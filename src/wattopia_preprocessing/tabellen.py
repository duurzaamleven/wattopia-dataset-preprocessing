"""De uitvoertabellen opbouwen (ontwerp §3 en §4).

Twee lagen: de ruwe laag (``bouw_projecten``, ``bouw_woningen``, ``bouw_detail_ruw``) is een getrouwe,
getypeerde kopie met nieuwe kolomnamen en geen andere waarden; de afgeleide laag
(``bouw_detail_5min``, ``bouw_detail_kwartier``) rekent en zet vlaggen. Een waarde die in de afgeleide
laag ongeldig is, wordt daar ``NaN`` mét een vlag; de ruwe laag houdt hem.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pyarrow as pa

from . import kolommen as K
from . import tijd as T
from .lezers import Jaartotalen, TIJDKOLOM_BRON
from .toetsen import vlaggen_woningen

# --------------------------------------------------------------------------------------------
# schema's
# --------------------------------------------------------------------------------------------

_ARROW = {
    "str": pa.string(),
    "cat": pa.string(),
    "int": pa.int64(),
    "float": pa.float64(),
    "bool": pa.bool_(),
    "tijd": pa.timestamp("us", tz=K.TIJDZONE),
}


def schema_van(kolommen: list[K.Kolom]) -> pa.Schema:
    return pa.schema([pa.field(k.naam, _ARROW[k.type]) for k in kolommen])


def naar_arrow(df: pd.DataFrame, kolommen: list[K.Kolom]) -> pa.Table:
    """``df`` naar een ``pyarrow.Table`` met precies het schema van ``kolommen``; een kolom die
    ontbreekt of extra is, is een fout."""
    verwacht = [k.naam for k in kolommen]
    if list(df.columns) != verwacht:
        ontbreekt = [n for n in verwacht if n not in df.columns]
        extra = [n for n in df.columns if n not in verwacht]
        raise ValueError(f"Kolommen wijken af van de definitie; ontbreekt: {ontbreekt}, extra: {extra}")
    return pa.Table.from_pandas(df, schema=schema_van(kolommen), preserve_index=False, safe=True)


# --------------------------------------------------------------------------------------------
# typeren
# --------------------------------------------------------------------------------------------

_AANHALINGSTEKENS = str.maketrans({"’": "'", "‘": "'", "´": "'", "`": "'"})


def normaliseer_tekst(waarde: str) -> str:
    """Vergelijkvorm voor het keuzemenu: de aanhalingstekens ’ en ‘ (het werkboek gebruikt ze door
    elkaar) worden gelijkgetrokken; de oorspronkelijke tekst wordt elders weggeschreven."""
    return waarde.translate(_AANHALINGSTEKENS).strip()


def _naar_bool(reeks: pd.Series, kolom: str) -> pd.Series:
    kaart = {"ja": True, "nee": False}
    uit = []
    for w in reeks:
        if w is None or (isinstance(w, float) and np.isnan(w)):
            uit.append(pd.NA)
            continue
        sleutel = str(w).strip().lower()
        if sleutel not in kaart:
            raise ValueError(f"Kolom {kolom}: waarde {w!r} is geen ja of nee (zie ontwerp §4.1)")
        uit.append(kaart[sleutel])
    return pd.Series(uit, index=reeks.index, dtype="boolean")


def _typeer(reeks: pd.Series, type_: str, kolom: str) -> pd.Series:
    if type_ == "int":
        return pd.to_numeric(reeks).astype("Int64")
    if type_ == "float":
        return pd.to_numeric(reeks).astype("float64")
    if type_ in ("str", "cat"):
        return reeks.astype("string")
    if type_ == "bool":
        return _naar_bool(reeks, kolom)
    raise ValueError(type_)


# --------------------------------------------------------------------------------------------
# projecten en woningen_jaar
# --------------------------------------------------------------------------------------------

def bouw_projecten(jt: Jaartotalen) -> pd.DataFrame:
    bron = jt.projectdata
    uit = pd.DataFrame(index=bron.index)
    for k in K.PROJECTEN:
        if k.bron not in bron.columns:
            raise ValueError(f"Kolom {k.bron!r} ontbreekt in Projectdata")
        uit[k.naam] = _typeer(bron[k.bron], k.type, k.naam)
    # vlag per keuzekolom, op de genormaliseerde tekst
    menu = {naam: {normaliseer_tekst(w) for w in waarden} for naam, waarden in jt.keuzemenu.items()}
    kolommen = K.tabel_kolommen("projecten")
    for k in K.PROJECTEN:
        if not k.menu:
            continue
        toegestaan = menu[k.menu]
        waarden = uit[k.naam]
        buiten = waarden.notna() & ~waarden.fillna("").map(lambda w: normaliseer_tekst(w) in toegestaan).astype(bool)
        uit[K.buiten_keuzemenu_naam(k.naam)] = buiten.astype(bool)
    return uit[[k.naam for k in kolommen]]


#: Eenheid in het werkboek (kopregel 3) per eenheid in de uitvoernaam; een afwijking is een fout,
#: want dan is de bron anders dan het ontwerp aanneemt.
_VERWACHTE_BRONEENHEID = {
    "kWh_a_1": "kWh_e / jaar", "GJ_a_1": "GJ / jaar", "ppm": "ppm", "pct": "percentage",
    "m3_a_1": "m3 / jaar", "degC": "graden C",
}


def bouw_woningen(jt: Jaartotalen) -> pd.DataFrame:
    bron = jt.monitoringdata
    eenheden = jt.eenheden.get("Monitoringdata", {})
    uit = pd.DataFrame(index=bron.index)
    for k in K.WONINGEN:
        if k.bron not in bron.columns:
            raise ValueError(f"Kolom {k.bron!r} ontbreekt in Monitoringdata")
        eenheid = K.stam_en_eenheid(k.naam)[1]
        if eenheid in _VERWACHTE_BRONEENHEID and eenheden.get(k.bron, "") != _VERWACHTE_BRONEENHEID[eenheid]:
            raise ValueError(
                f"Kolom {k.bron!r}: eenheid in het werkboek is {eenheden.get(k.bron)!r}, "
                f"het ontwerp verwacht {_VERWACHTE_BRONEENHEID[eenheid]!r}")
        uit[k.naam] = _typeer(bron[k.bron], k.type, k.naam)
    vlaggen = vlaggen_woningen(uit)
    for naam in vlaggen.columns:
        uit[naam] = vlaggen[naam]
    return uit[[k.naam for k in K.tabel_kolommen("woningen_jaar")]]


# --------------------------------------------------------------------------------------------
# detail_ruw
# --------------------------------------------------------------------------------------------

def _typeer_detail(reeks: pd.Series, k: K.Kolom, meetpunt: str) -> pd.Series:
    if k.type == "float":
        return reeks.astype("float64")
    if k.type == "bool":
        waarden = pd.to_numeric(reeks, errors="coerce")
        vreemd = waarden.dropna()[~waarden.dropna().isin([0, 1])]
        if len(vreemd):
            raise ValueError(f"{meetpunt}.{k.bron} kent naast 0 en 1 ook {sorted(vreemd.unique())[:5]}; "
                             "zie ontwerp §4.3 (statussen met meer dan 0 en 1 horen bij __cat)")
        return waarden.astype("Int64").astype("boolean")
    if k.type == "cat":
        if pd.api.types.is_float_dtype(reeks) or pd.api.types.is_integer_dtype(reeks):
            if reeks.dropna().ne(reeks.dropna().round()).any():
                raise ValueError(f"{meetpunt}.{k.bron}: een code met een fractie, geen categorie")
            return reeks.astype("Int64").astype("string")
        return reeks.astype("string")
    if k.type == "str":
        if pd.api.types.is_float_dtype(reeks) or pd.api.types.is_integer_dtype(reeks):
            if pd.api.types.is_float_dtype(reeks) and reeks.dropna().ne(reeks.dropna().round()).any():
                return reeks.astype("string")
            return reeks.astype("Int64").astype("string")
        return reeks.astype("string")
    raise ValueError(k.type)


def bouw_detail_ruw(meetpunt: str, bron: pd.DataFrame, woningcode: str) -> pd.DataFrame:
    """Het tabblad ``meetpunt`` van één woning, met de nieuwe kolomnamen en types. De waarden zijn
    die van de bron."""
    definitie = K.DETAIL_MEETPUNTEN[meetpunt]
    bekend = {k.bron for k in definitie} | {TIJDKOLOM_BRON}
    onbekend = [c for c in bron.columns if c not in bekend]
    if onbekend:
        raise ValueError(f"Tabblad {meetpunt}: kolommen {onbekend} staan niet in kolommen.DETAIL_MEETPUNTEN")
    seconden = bron[TIJDKOLOM_BRON].astype("int64").to_numpy()
    uit = pd.DataFrame({
        "woningcode__str": pd.Series([woningcode] * len(bron), dtype="string"),
        "tijdstip": T.unix_naar_lokaal(seconden),
        "timestamp_bron__s": seconden,
    })
    for k in definitie:
        if k.bron in bron.columns:
            uit[k.naam] = _typeer_detail(bron[k.bron].reset_index(drop=True), k, meetpunt)
        else:
            uit[k.naam] = _leeg_als(k.type, len(bron))
    return uit


# --------------------------------------------------------------------------------------------
# detail_5min
# --------------------------------------------------------------------------------------------

_FACTOR_NAAR_JOULE = {"kWh": 3.6e6, "GJ": 1e9}


def _leeg_als(type_: str, n: int) -> pd.Series:
    if type_ == "float":
        return pd.Series(np.full(n, np.nan))
    if type_ == "bool":
        return pd.Series([pd.NA] * n, dtype="boolean")
    return pd.Series([pd.NA] * n, dtype="string")


def bouw_detail_5min(woningcode: str, ruw: dict[str, pd.DataFrame],
                     raster: pd.DatetimeIndex | None = None) -> pd.DataFrame:
    """Het 5-minutenraster van één woning (ontwerp §4.4). ``ruw`` bevat de ruwe tabbladen
    (resultaat van :func:`bouw_detail_ruw`); een ontbrekend tabblad geeft lege kolommen."""
    raster = T.jaarraster() if raster is None else raster
    grenzen = T.rastergrenzen_s(raster)
    n = len(raster)
    ruw = {m: d.sort_values("timestamp_bron__s", kind="stable").reset_index(drop=True) for m, d in ruw.items()}

    kolommen: dict[str, pd.Series | np.ndarray] = {
        "woningcode__str": pd.Series([woningcode] * n, dtype="string"),
        "tijdstip_start": raster,
    }
    vermogens, gedekt_vlaggen, daalt_vlaggen = {}, {}, {}
    for t in K.TELLERS:
        stam = t.naam.rpartition("__")[0]
        d = ruw.get(t.meetpunt)
        if d is None or d[t.teller].notna().sum() < 2:
            vermogens[t.naam] = np.full(n, np.nan)
            gedekt_vlaggen[stam] = np.zeros(n, dtype=bool)
            daalt_vlaggen[stam] = np.zeros(n, dtype=bool)
            continue
        stand, gedekt = T.interpoleer_teller(d["timestamp_bron__s"].to_numpy(), d[t.teller].to_numpy(), grenzen)
        p, interval_gedekt, daalt = T.vermogen_uit_stand(stand, gedekt, _FACTOR_NAAR_JOULE[t.eenheid_teller])
        vermogens[t.naam] = p
        gedekt_vlaggen[stam] = interval_gedekt
        daalt_vlaggen[stam] = daalt
    for t in K.TELLERS:
        kolommen[t.naam] = vermogens[t.naam]
    for t in K.TELLERS:
        stam = t.naam.rpartition("__")[0]
        kolommen[f"{stam}_gedekt__bool"] = gedekt_vlaggen[stam]
        kolommen[f"{stam}_teller_daalt__bool"] = daalt_vlaggen[stam]

    idx_per_meetpunt: dict[str, np.ndarray] = {}
    gezien: set[str] = set()
    for meetpunt, k in K.steekproef_kolommen():
        d = ruw.get(meetpunt)
        if meetpunt not in gezien:
            gezien.add(meetpunt)
            if d is None:
                idx_per_meetpunt[meetpunt] = np.full(n, -1)
                kolommen[K.tijdstip_steekproef_naam(meetpunt)] = pd.Series(pd.NaT, index=range(n), dtype=f"datetime64[us, {K.TIJDZONE}]")
            else:
                idx = T.steekproef_laatste_binnen(d["timestamp_bron__s"].to_numpy(), grenzen)
                idx_per_meetpunt[meetpunt] = idx
                sec = np.where(idx >= 0, d["timestamp_bron__s"].to_numpy()[np.clip(idx, 0, None)], np.nan)
                kolommen[K.tijdstip_steekproef_naam(meetpunt)] = (
                    pd.to_datetime(pd.Series(sec), unit="s", utc=True).dt.tz_convert(K.TIJDZONE).dt.as_unit("us"))
        naam = K.steekproef_naam(meetpunt, k.naam)
        if d is None:
            waarden = _leeg_als(k.type, n)
        else:
            idx = idx_per_meetpunt[meetpunt]
            waarden = d[k.naam].take(np.clip(idx, 0, None)).reset_index(drop=True)
            if (idx < 0).any():
                waarden = waarden.copy()
                waarden[idx < 0] = np.nan if k.type == "float" else pd.NA
        if K.is_temperatuur(k):
            v = waarden.to_numpy(dtype="float64")
            buiten = (v < K.TEMP_MIN_DEGC) | (v > K.TEMP_MAX_DEGC)
            if (meetpunt, k.naam) in K.TEMP_KAMER:
                buiten |= v <= K.TEMP_KAMER_ONDERGRENS_DEGC
            kolommen[naam] = np.where(buiten, np.nan, v)
            kolommen[K.buiten_bereik_naam(naam)] = buiten
        else:
            kolommen[naam] = waarden
    uit = pd.DataFrame({k: (v.to_numpy() if isinstance(v, pd.Series) and v.dtype == "float64" else v)
                        for k, v in kolommen.items()})
    return uit[[k.naam for k in K.detail_5min_kolommen()]]


# --------------------------------------------------------------------------------------------
# detail_kwartier
# --------------------------------------------------------------------------------------------

def bouw_detail_kwartier(vijf: pd.DataFrame) -> pd.DataFrame:
    """Drie opeenvolgende intervallen van vijf minuten tot een kwartier (ontwerp §4.4)."""
    if len(vijf) % 3:
        raise ValueError("Het aantal intervallen van vijf minuten is geen veelvoud van drie")
    if vijf["tijdstip_start"].iloc[0].minute % 15:
        raise ValueError("Het raster begint niet op een heel kwartier")
    uit: dict[str, pd.Series | np.ndarray] = {}
    uit["woningcode__str"] = vijf["woningcode__str"].iloc[::3].reset_index(drop=True)
    uit["tijdstip_start"] = vijf["tijdstip_start"].iloc[::3].reset_index(drop=True)
    for t in K.TELLERS:
        stam = t.naam.rpartition("__")[0]
        blok = vijf[t.naam].to_numpy().reshape(-1, 3)
        volledig = ~np.isnan(blok).any(axis=1)
        gemiddeld = np.full(len(blok), np.nan)
        gemiddeld[volledig] = blok[volledig].mean(axis=1)
        uit[t.naam] = gemiddeld
        uit[f"{stam}_onvolledig__bool"] = ~volledig
    for k in K.detail_kwartier_kolommen():
        if k.naam in uit or k.naam.endswith("_onvolledig__bool"):
            continue
        uit[k.naam] = vijf[k.naam].iloc[2::3].reset_index(drop=True)
    kolommen = K.tabel_kolommen("detail_kwartier")
    return pd.DataFrame(uit)[[k.naam for k in kolommen]]
