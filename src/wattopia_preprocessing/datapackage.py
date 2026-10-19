# SPDX-License-Identifier: EUPL-1.2
"""``datapackage.json`` (Frictionless Data Package) en ``docs/datacatalogus.md``, beide uit dezelfde
kolomdefinities in ``kolommen.py``.

Er is dus één bron van waarheid: een kolom die in de uitvoer komt, staat in ``kolommen.py`` met naam,
type en beschrijving, en komt vanzelf in het datapackage en de catalogus. ``datapackage.json`` staat in de
repo-root; de paden verwijzen naar ``data/processed/``, dat lokaal blijft (zie ``GEBRUIKSVOORWAARDEN.md``).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import kolommen as K
from .manifest import UITVOER_CONTRACT_VERSIE

DATAPACKAGE_BESTANDSNAAM = "datapackage.json"
STANDAARD_DATAPACKAGE_PAD = Path(__file__).resolve().parents[2] / DATAPACKAGE_BESTANDSNAAM
UITVOER_MAP = "data/processed"

#: Herkomst van het pakket, zodat de sha256's vastliggen (CLAUDE.md, punt 6).
PAKKET_ZIP = "RVO_Woningprestaties_Datapakketje_2022.zip"
PAKKET_URL = "https://wattopia.nl/download/RVO_Woningprestaties_Datapakketje_2022.zip"
PAKKET_SHA256 = "42ac03254c4d3cbb349655a32e3258c535c0db5dba3704353f567e2157d4e86a"
PAKKET_OMVANG__B = 69_243_717
BRONBESTANDEN: dict[str, str] = {
    "Woningprestaties 2022-07-22 ANON.xlsx": "141a82b767c8a5a1e8288fbe9d5eaeb6e982b2c4e75977b577708ce644291a13",
    "Detaildata woning_arnpivgi.xlsx": "2fa913d91c9107596339cb508cbfe74097f7e81f17953cd7c2f2368be3ddb9a1",
    "Detaildata woning_mkpiieku.xlsx": "71b72ec906a3bdbe354adbd950facce28dfd93fb5da9de06b3bc7afa5faecdf6",
}
KITE_PAGINA_URL = "https://kennisdelen.rvo.nl/groups/view/1434df6b-d9c4-4d87-8c73-36834399abeb/kite"
BRONVERMELDING = ("RVO, Wattopia, Out of Harm's Way, \"Woningprestaties - Monitoringdata van bestaande "
                  "woningen\", 2022, opvraagbaar via info@woningprestaties.nl")

_FRICTIONLESS_TYPE = {"str": "string", "cat": "string", "int": "integer", "float": "number",
                      "bool": "boolean", "tijd": "datetime"}

_TITELS = {
    "projecten": ("Projecten", "Eén rij per project: typologie, schil en installaties (tabblad Projectdata)."),
    "woningen_jaar": ("Jaartotalen per woning", "Eén rij per woning: energie, warmte, binnenklimaat en gebruik over een jaar "
                      "(tabblad Monitoringdata), met vlaggen."),
    "detail_5min": ("Twee woningen per vijf minuten", "Gemeenschappelijk raster van vijf minuten over kalenderjaar "
                    "2019, met vermogens uit tellers, steekproeven en vlaggen."),
    "detail_kwartier": ("Twee woningen per kwartier", "Drie intervallen van vijf minuten opgeteld tot een kwartier."),
    "controle_jaartotalen": ("Zelfcontrole", "De jaartotalen uit de detaildata tegenover die in de jaartotalen."),
}

_SLEUTELS = {
    "projecten": ["projectcode__str"],
    "woningen_jaar": ["woningcode__str"],
    "detail_5min": ["woningcode__str", "tijdstip_start"],
    "detail_kwartier": ["woningcode__str", "tijdstip_start"],
    "controle_jaartotalen": ["woningcode__str", "grootheid__str", "definitie__str"],
}

_KORRELS = {
    "projecten": "project", "woningen_jaar": "woning", "detail_5min": "woning x 5 minuten",
    "detail_kwartier": "woning x kwartier", "controle_jaartotalen": "woning x grootheid x definitie",
}


def resource_namen(meetpunten: list[str] | None = None) -> list[str]:
    """De tabellen in volgorde van de uitvoer. ``meetpunten`` zijn de tabbladen waarvoor een
    ``detail_ruw``-bestand bestaat (standaard alle bekende)."""
    meetpunten = list(K.DETAIL_MEETPUNTEN) if meetpunten is None else meetpunten
    return (["projecten", "woningen_jaar"] + [f"detail_ruw/{m}" for m in meetpunten]
            + ["detail_5min", "detail_kwartier", "controle_jaartotalen"])


def _resource_naam(tabel: str) -> str:
    return tabel.replace("detail_ruw/", "detail_ruw_").lower()


def _titel(tabel: str) -> tuple[str, str]:
    if tabel.startswith("detail_ruw/"):
        m = tabel.split("/", 1)[1]
        return (f"Ruwe metingen: {m}", f"Getrouwe kopie van tabblad {m} van beide detailwoningen, met nieuwe "
                "kolomnamen en types en tijd in lokale tijd; geen andere waarden.")
    return _TITELS[tabel]


def _sleutel(tabel: str) -> list[str]:
    return ["woningcode__str", "timestamp_bron__s"] if tabel.startswith("detail_ruw/") else _SLEUTELS[tabel]


def _resource(tabel: str) -> dict:
    titel, beschrijving = _titel(tabel)
    return {
        "name": _resource_naam(tabel),
        "title": titel,
        "description": beschrijving,
        "format": "parquet",
        "mediatype": "application/vnd.apache.parquet",
        "path": f"{UITVOER_MAP}/{tabel}.parquet",
        "schema": {
            "fields": [{"name": k.naam, "type": _FRICTIONLESS_TYPE[k.type], "description": k.beschrijving}
                       for k in K.tabel_kolommen(tabel)],
            "primaryKey": _sleutel(tabel),
        },
    }


def bouw_datapackage(meetpunten: list[str] | None = None, contract_versie: str = UITVOER_CONTRACT_VERSIE) -> dict:
    return {
        "name": "wattopia-woningprestaties-processed",
        "title": "Woningprestaties: voorbewerkte monitoringdata (getypeerde Parquet-tabellen)",
        "description": (
            "Voorbewerkte monitoringdata Woningprestaties (Wattopia, Out of Harm's Way en RVO, 2022): "
            "jaartotalen van 898 woningen en vijfminutendata van twee woningen. Deze repo is niet de data-"
            "eigenaar; zie GEBRUIKSVOORWAARDEN.md voor de voorwaarden, de meldplicht en de herkomst, en "
            "docs/datacatalogus.md voor de beschrijving van elke tabel. De uitvoer in data/processed/ staat "
            "niet in git. Gegenereerd door wattopia_preprocessing.datapackage."
        ),
        "version": contract_versie,
        "licenses": [{
            "name": "andere",
            "title": ("Geen open licentie in de zin van een licentietekst. De KITE-pagina noemt de data openbaar, "
                      "onder voorwaarde van vermelding van het doel en gebruik aan Wattopia; het codeboek zegt dat "
                      "de gegevens niet worden gemanipuleerd, niet worden verkocht en niet zonder toestemming voor "
                      "andere doelen worden gebruikt; de instructies vragen de dataset niet zelf door te sturen. "
                      "Zie GEBRUIKSVOORWAARDEN.md."),
            "path": "GEBRUIKSVOORWAARDEN.md",
        }],
        "sources": [
            {"title": "Monitoringdata Energieprestaties Wattopia, KITE (Kennisdelen RVO)", "path": KITE_PAGINA_URL},
            {"title": f"{PAKKET_ZIP} (codeboek van 22 juli 2022)", "path": PAKKET_URL,
             "sha256": PAKKET_SHA256, "bytes": PAKKET_OMVANG__B},
            *[{"title": naam, "sha256": sha} for naam, sha in BRONBESTANDEN.items()],
        ],
        "contributors": [
            {"title": "Wattopia", "role": "author"},
            {"title": "Out of Harm's Way", "role": "author"},
            {"title": "RVO", "role": "publisher"},
        ],
        "keywords": ["woningprestaties", "monitoring", "warmtepomp", "tijdreeksen"],
        "resources": [_resource(t) for t in resource_namen(meetpunten)],
        "x-bronvermelding": BRONVERMELDING,
    }


def schrijf_datapackage(pad: Path, meetpunten: list[str] | None = None) -> None:
    from .manifest import schrijf_tekst_atomisch
    schrijf_tekst_atomisch(Path(pad), json.dumps(bouw_datapackage(meetpunten), ensure_ascii=False, indent=2) + "\n")


# --------------------------------------------------------------------------------------------
# datacatalogus
# --------------------------------------------------------------------------------------------

_AANNAMEN = [
    "**Eenheden van de tellers** (`total_energy_*`, `energy_*` in kWh, `total_energyGJ` in GJ, `power` in W) zijn "
    "afgeleid en getoetst tegen de jaartotalen; het codeboek licht de detaildata niet toe.",
    "**Tekenconventie.** `solar.power` is negatief bij opwek en `smartMeter.power` positief bij afname en negatief "
    "bij teruglevering. Dat is niet omgedraaid; `p_pv_opwek`, `p_net_afname` en `p_net_teruglevering` komen uit de "
    "tellers en zijn positief.",
    "**Eenheid onbekend** (kolomnaam eindigt op `__onbekend`): `volume_out`, de debieten van de ventilatie en `voc`.",
    "**Codes van de fabrikant** (`op_mode`, `system_status`, `error_code`, `filter`): betekenis onbekend.",
    "**Totaal gebruikte energie door de warmteopwekker** is warmtepomp plus booster (het elektrische "
    "bijverwarmingselement).",
    "**Momentane waarden** (temperaturen, statussen, `power`) in `detail_5min` zijn de laatste meting binnen het "
    "interval, een steekproef en geen gemiddelde; de naam eindigt daarom op `_steekproef`.",
    "**Intervallen** zijn begin-gelabeld; alle tijdkolommen zijn tz-aware in `Europe/Amsterdam`.",
]


def schrijf_datacatalogus(meetpunten: list[str] | None = None, rijen: dict[str, int] | None = None) -> str:
    r: list[str] = ["# Datacatalogus\n"]
    r.append("Wordt door de pijplijn gegenereerd uit `kolommen.py`, net als `datapackage.json`. De uitvoer staat in "
             "`data/processed/` en niet in git; zie [`GEBRUIKSVOORWAARDEN.md`](../GEBRUIKSVOORWAARDEN.md). Bronvermelding: "
             f"{BRONVERMELDING}.\n")
    r.append("Namen volgen de conventie `physiquant__unit`: de eenheid staat na een dubbele underscore "
             "(`temp_aanvoer__degC`). `_cum` is een meterstand op een moment; zonder `_cum` is het een gemiddelde "
             "over het interval of een jaartotaal. `__bool` is een vlag of ja/nee, `__cat` een categorie, `__str` tekst, "
             "`__0` een telling zonder eenheid.\n")
    r.append("## Aannames en onzekerheden\n")
    r += [f"- {a}" for a in _AANNAMEN]
    r.append("")
    tabellen_lijst = resource_namen(meetpunten)
    r.append("## Tabellen\n")
    for t in tabellen_lijst:
        titel, beschrijving = _titel(t)
        r.append(f"### `{t}`\n")
        r.append(f"{beschrijving}")
        regel = f"Pad: `{UITVOER_MAP}/{t}.parquet`."
        if t in _KORRELS:
            regel += f" Korrel: {_KORRELS[t]}."
        if rijen and t in rijen:
            regel += f" Rijen: {rijen[t]:,}.".replace(",", ".")
        r.append(regel + "\n")
        kolommen = K.tabel_kolommen(t)
        r.append("| kolom | type | bron | beschrijving |")
        r.append("|---|---|---|---|")
        for k in kolommen:
            r.append(f"| `{k.naam}` | {_FRICTIONLESS_TYPE[k.type]} | {('`' + k.bron + '`') if k.bron else ''} | "
                     f"{k.beschrijving.replace('|', '/')} |")
        r.append("")
    return "\n".join(r) + "\n"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--pad", type=Path, default=STANDAARD_DATAPACKAGE_PAD)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    schrijf_datapackage(args.pad)
    print(f"Geschreven: {args.pad}")


if __name__ == "__main__":
    main()
