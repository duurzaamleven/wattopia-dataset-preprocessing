"""De pijplijn: ruw pakket naar getypeerde Parquet-tabellen (zie ``ontwerp-preprocessing.md``).

Volgorde van een run:

1. De detailwerkboeken naar ``interim/<woning>/<meetpunt>.parquet`` (traag; wordt overgeslagen als de
   sha256 van het werkboek gelijk is aan die in het manifest).
2. ``projecten`` en ``woningen_jaar`` uit het werkboek met jaartotalen.
3. ``detail_ruw/<meetpunt>.parquet``: per tabblad beide woningen onder elkaar.
4. Per woning ``detail_5min``, dan ``detail_kwartier``; er staat steeds maar één woning volledig in
   het geheugen.
5. ``controle_jaartotalen``; de run faalt als de afwijking de tolerantie overschrijdt.
6. ``docs/data-quality.md``, ``docs/datacatalogus.md`` en ``datapackage.json``.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import RAW_DIR, kolommen as K, lezers, tabellen, tijd, toetsen
from .manifest import (INTERIM_VERSIE, Manifest, schrijf_arrow_atomisch, schrijf_tekst_atomisch,
                       sha256_van_bestand)

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
JAARTOTALEN_BESTAND = "Woningprestaties 2022-07-22 ANON.xlsx"
DETAIL_PATROON = re.compile(r"^Detaildata woning_(?P<code>[A-Za-z0-9]+)\.xlsx$")
TABBLADEN_BESTAND = "_tabbladen.json"


@dataclass
class Resultaat:
    rijen: dict[str, int] = field(default_factory=dict)
    werkboeken_gelezen: list[str] = field(default_factory=list)
    werkboeken_overgeslagen: list[str] = field(default_factory=list)
    statistieken: dict = field(default_factory=dict)
    controle: pd.DataFrame | None = None


def vind_detailwerkboeken(raw_dir: Path) -> dict[str, Path]:
    """``{woningcode: pad}`` voor elk ``Detaildata woning_<code>.xlsx``; de code in het werkboek met
    jaartotalen is ``W_<code>``."""
    gevonden = {}
    for pad in sorted(Path(raw_dir).glob("Detaildata woning_*.xlsx")):
        m = DETAIL_PATROON.match(pad.name)
        if m:
            gevonden[f"W_{m.group('code')}"] = pad
    return gevonden


# --------------------------------------------------------------------------------------------
# stap 1: de tussenstap
# --------------------------------------------------------------------------------------------

def leg_interim_aan(woningcode: str, werkboek: Path, interim_dir: Path, manifest: Manifest,
                    opnieuw: bool = False) -> bool:
    """Lees één detailwerkboek naar ``interim/<woning>/<meetpunt>.parquet`` (bronkolommen en
    bronwaarden). Geeft ``True`` als het werkboek gelezen is, ``False`` als het manifest zei dat het
    al klaar was (zelfde sha256, tussenbestanden aanwezig)."""
    sha = sha256_van_bestand(werkboek)
    if not opnieuw and manifest.is_voltooid("werkboek", woningcode, bron_sha256=sha):
        regel = manifest.regel("werkboek", woningcode)
        meta = json.loads((manifest.map / regel.pad).read_text(encoding="utf-8"))
        if all((manifest.map / woningcode / f"{naam}.parquet").is_file() for naam in meta["tabbladen"]):
            log.info("Werkboek %s ongewijzigd (sha256 gelijk); niet opnieuw gelezen", werkboek.name)
            return False
    doel = Path(interim_dir) / woningcode
    doel.mkdir(parents=True, exist_ok=True)
    for oud in doel.glob("*.parquet"):
        oud.unlink()  # geen tabbladen uit een eerdere versie laten staan
    tabbladen: dict[str, int] = {}
    leeg: list[str] = []
    for naam, df in lezers.lees_detailwerkboek(werkboek):
        if df is None:
            leeg.append(naam)
            log.info("%s: tabblad %s is leeg", woningcode, naam)
            continue
        tmp = doel / f"{naam}.parquet.tmp"
        df.to_parquet(tmp, index=False, compression="zstd")
        tmp.replace(doel / f"{naam}.parquet")
        tabbladen[naam] = len(df)
        log.info("%s: tabblad %s, %d rijen", woningcode, naam, len(df))
    meta_pad = doel / TABBLADEN_BESTAND
    schrijf_tekst_atomisch(meta_pad, json.dumps({"tabbladen": tabbladen, "leeg": leeg},
                                                ensure_ascii=False, indent=2))
    manifest.voeg_toe("werkboek", woningcode, meta_pad, rijen=sum(tabbladen.values()), bron_sha256=sha)
    return True


def _tabbladen(woningcode: str, interim_dir: Path) -> tuple[list[str], list[str]]:
    meta = json.loads((Path(interim_dir) / woningcode / TABBLADEN_BESTAND).read_text(encoding="utf-8"))
    return list(meta["tabbladen"]), list(meta["leeg"])


def _lees_ruw(woningcode: str, meetpunt: str, interim_dir: Path) -> pd.DataFrame:
    bron = pd.read_parquet(Path(interim_dir) / woningcode / f"{meetpunt}.parquet")
    return tabellen.bouw_detail_ruw(meetpunt, bron, woningcode)


# --------------------------------------------------------------------------------------------
# statistieken voor het kwaliteitsrapport (alleen aggregaten)
# --------------------------------------------------------------------------------------------

def _vulgraad(df: pd.DataFrame, kolommen: list[K.Kolom]) -> list[dict]:
    return [{"kolom": k.naam, "gevuld": int(df[k.naam].notna().sum()), "van": int(len(df))} for k in kolommen]


def _sentinels_ruw(meetpunt: str, ruw: pd.DataFrame) -> dict[str, dict]:
    uit = {}
    for k in K.DETAIL_MEETPUNTEN[meetpunt]:
        if not K.is_temperatuur(k):
            continue
        v = ruw[k.naam].to_numpy(dtype="float64")
        gevuld = ~np.isnan(v)
        buiten = (v < K.TEMP_MIN_DEGC) | (v > K.TEMP_MAX_DEGC)
        kamer = (meetpunt, k.naam) in K.TEMP_KAMER
        if kamer:
            buiten |= v <= K.TEMP_KAMER_ONDERGRENS_DEGC
        uit[k.naam] = {"gevuld": int(gevuld.sum()), "buiten_bereik": int(buiten.sum()), "kamer": kamer,
                       "min": float(np.nanmin(v)) if gevuld.any() else None,
                       "max": float(np.nanmax(v)) if gevuld.any() else None}
    return uit


# --------------------------------------------------------------------------------------------
# de run
# --------------------------------------------------------------------------------------------

def draai(raw_dir: Path = RAW_DIR, uit_dir: Path | None = None, interim_dir: Path | None = None,
          docs_dir: Path | None = None, datapackage_pad: Path | None = None,
          schrijf_docs: bool = True, opnieuw_lezen: bool = False,
          raster: pd.DatetimeIndex | None = None) -> Resultaat:
    raw_dir = Path(raw_dir)
    uit_dir = Path(uit_dir) if uit_dir else raw_dir.parent / "processed"
    interim_dir = Path(interim_dir) if interim_dir else raw_dir.parent / "interim"
    docs_dir = Path(docs_dir) if docs_dir else REPO_ROOT / "docs"
    datapackage_pad = Path(datapackage_pad) if datapackage_pad else REPO_ROOT / "datapackage.json"

    jaartotalen_pad = raw_dir / JAARTOTALEN_BESTAND
    if not jaartotalen_pad.is_file():
        raise FileNotFoundError(f"{JAARTOTALEN_BESTAND} staat niet in {raw_dir}; zie GEBRUIKSVOORWAARDEN.md")
    werkboeken = vind_detailwerkboeken(raw_dir)
    res = Resultaat()
    stat: dict = {"detail": {}, "lege_tabbladen": {}}
    res.statistieken = stat

    # 1. tussenstap
    manifest_interim = Manifest(interim_dir, contract=INTERIM_VERSIE)
    for code, pad in werkboeken.items():
        gelezen = leg_interim_aan(code, pad, interim_dir, manifest_interim, opnieuw=opnieuw_lezen)
        (res.werkboeken_gelezen if gelezen else res.werkboeken_overgeslagen).append(code)

    manifest = Manifest(uit_dir)

    def schrijf(naam: str, df: pd.DataFrame) -> None:
        tabel = tabellen.naar_arrow(df, K.tabel_kolommen(naam))
        pad = uit_dir / f"{naam}.parquet"
        schrijf_arrow_atomisch(pad, tabel)
        manifest.voeg_toe("tabel", naam, pad, rijen=len(df))
        res.rijen[naam] = len(df)
        log.info("Geschreven: %s (%d rijen)", naam, len(df))

    # 2. jaartotalen
    jt = lezers.lees_jaartotalen(jaartotalen_pad)
    projecten = tabellen.bouw_projecten(jt)
    woningen = tabellen.bouw_woningen(jt)
    schrijf("projecten", projecten)
    schrijf("woningen_jaar", woningen)
    stat["projecten"] = {"rijen": len(projecten), "vulgraad": _vulgraad(projecten, K.tabel_kolommen("projecten")),
                         "buiten_keuzemenu": {k.naam: int(projecten[k.naam].sum()) for k in K.PROJECTEN_VLAGGEN}}
    stat["woningen"] = {
        "rijen": len(woningen), "vulgraad": _vulgraad(woningen, K.WONINGEN),
        "vlaggen": {k.naam: {"aan": int(woningen[k.naam].fillna(False).sum()), "toetsbaar": int(woningen[k.naam].notna().sum())}
                    for k in K.WONINGEN_VLAGGEN},
        "jaren": {int(j): int(n) for j, n in woningen["jaar_monitoring__0"].value_counts().sort_index().items()},
        "projecten_zonder_projectrij": int((~woningen["projectcode__str"].isin(projecten["projectcode__str"])).sum()),
        "dubbele_woningcodes": int(woningen["woningcode__str"].duplicated().sum()),
    }

    # 3. detail_ruw, per meetpunt beide woningen onder elkaar
    meetpunten: list[str] = []
    for code in werkboeken:
        tabs, leeg = _tabbladen(code, interim_dir)
        stat["lege_tabbladen"][code] = leeg
        for m in tabs:
            if m not in meetpunten:
                meetpunten.append(m)
    meetpunten.sort(key=lambda m: list(K.DETAIL_MEETPUNTEN).index(m) if m in K.DETAIL_MEETPUNTEN else 999)
    for m in meetpunten:
        delen = []
        for code in werkboeken:
            if m in _tabbladen(code, interim_dir)[0]:
                ruw = _lees_ruw(code, m, interim_dir)
                stat["detail"].setdefault(code, {"gaten": {}, "sentinels": {}})
                stat["detail"][code]["gaten"][m] = toetsen.gatstatistiek(ruw["timestamp_bron__s"].to_numpy())
                stat["detail"][code]["sentinels"][m] = _sentinels_ruw(m, ruw)
                delen.append(ruw)
        schrijf(f"detail_ruw/{m}", pd.concat(delen, ignore_index=True))
        del delen

    # 4. detail_5min en detail_kwartier, per woning
    raster = tijd.jaarraster() if raster is None else raster
    vijf_delen, kwartier_delen = [], []
    totalen: dict[str, dict] = {}
    for code in werkboeken:
        tabs, _ = _tabbladen(code, interim_dir)
        ruw = {m: _lees_ruw(code, m, interim_dir) for m in tabs}
        vijf = tabellen.bouw_detail_5min(code, ruw, raster)
        totalen[code] = toetsen.totalen_uit_detail(ruw, vijf, tijd.rastergrenzen_s(raster))
        del ruw
        vijf_delen.append(vijf)
        kwartier_delen.append(tabellen.bouw_detail_kwartier(vijf))
        stat["detail"].setdefault(code, {"gaten": {}, "sentinels": {}})
        stat["detail"][code]["raster"] = _rasterstatistiek(vijf)
    schrijf("detail_5min", pd.concat(vijf_delen, ignore_index=True))
    del vijf_delen
    schrijf("detail_kwartier", pd.concat(kwartier_delen, ignore_index=True))
    del kwartier_delen

    # 5. zelfcontrole
    controle = toetsen.bouw_controle(totalen, woningen)
    schrijf("controle_jaartotalen", controle)
    res.controle = controle

    # 6. documenten
    if schrijf_docs:
        from . import datapackage, kwaliteitsrapport
        schrijf_tekst_atomisch(Path(docs_dir) / "data-quality.md", kwaliteitsrapport.schrijf_rapport(stat, controle))
        schrijf_tekst_atomisch(Path(docs_dir) / "datacatalogus.md", datapackage.schrijf_datacatalogus(meetpunten, res.rijen))
        datapackage.schrijf_datapackage(datapackage_pad, meetpunten)

    toetsen.eis_controle(controle)
    return res


def _rasterstatistiek(vijf: pd.DataFrame) -> dict:
    n = len(vijf)
    tellers = {}
    for t in K.TELLERS:
        stam = t.naam.rpartition("__")[0]
        tellers[t.naam] = {
            "gedekt": int(vijf[f"{stam}_gedekt__bool"].sum()),
            "daalt": int(vijf[f"{stam}_teller_daalt__bool"].sum()),
            "met_waarde": int(vijf[t.naam].notna().sum()),
        }
    bereik = {c: int(vijf[c].sum()) for c in vijf.columns if c.endswith("_buiten_bereik__bool")}
    steekproeven = {}
    gezien = set()
    for meetpunt, _ in K.steekproef_kolommen():
        if meetpunt in gezien:
            continue
        gezien.add(meetpunt)
        steekproeven[meetpunt] = int(vijf[K.tijdstip_steekproef_naam(meetpunt)].notna().sum())
    return {"intervallen": n, "tellers": tellers, "buiten_bereik": bereik, "met_steekproef": steekproeven}


# --------------------------------------------------------------------------------------------
# opdrachtregel
# --------------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m wattopia_preprocessing", description=__doc__.split("\n")[0])
    p.add_argument("--raw", type=Path, default=RAW_DIR, help="map met het uitgepakte pakket (standaard data/raw)")
    p.add_argument("--uit", type=Path, default=None, help="uitvoermap (standaard data/processed naast --raw)")
    p.add_argument("--interim", type=Path, default=None, help="map voor de tussenstap (standaard data/interim naast --raw)")
    p.add_argument("--geen-docs", action="store_true", help="schrijf docs/ en datapackage.json niet")
    p.add_argument("--opnieuw-lezen", action="store_true", help="lees de werkboeken opnieuw, ook als de sha256 gelijk is")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        res = draai(args.raw, args.uit, args.interim, schrijf_docs=not args.geen_docs, opnieuw_lezen=args.opnieuw_lezen)
    except toetsen.ControleFout as fout:
        log.error("%s", fout)
        return 2
    log.info("Klaar. Werkboeken gelezen: %s; overgeslagen: %s",
             res.werkboeken_gelezen or "geen", res.werkboeken_overgeslagen or "geen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
