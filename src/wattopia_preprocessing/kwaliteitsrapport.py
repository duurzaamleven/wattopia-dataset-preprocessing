# SPDX-License-Identifier: EUPL-1.2
"""``docs/data-quality.md``: het kwaliteitsrapport van een run.

Het rapport bevat alleen **aggregaten**: vulgraad, hoe vaak een vlag aanslaat, gaten, dekking en de
afwijkingspercentages van de zelfcontrole. Het bevat geen waarden per woning; die blijven lokaal
(zie ``GEBRUIKSVOORWAARDEN.md``).
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from . import kolommen as K

#: Een regel die bij minstens dit aandeel van de toetsbare woningen aanslaat, is waarschijnlijk geen
#: fout in de data maar een verschil in definitie (ontwerp §4.2).
DEFINITIEVERSCHIL_AANDEEL = 0.5


def _pct(n: int, van: int, decimalen: int = 1) -> str:
    return "n.v.t." if van == 0 else f"{100.0 * n / van:.{decimalen}f} %".replace(".", ",")


def _getal(x: float, decimalen: int = 3) -> str:
    if x is None or pd.isna(x):
        return "n.v.t."
    x = 0.0 if round(x, decimalen) == 0 else x  # geen "-0,000 %"
    return f"{x:+.{decimalen}f} %".replace(".", ",")


def _tabel(kop: list[str], rijen: list[list[str]]) -> str:
    regels = ["| " + " | ".join(kop) + " |", "|" + "|".join("---" for _ in kop) + "|"]
    regels += ["| " + " | ".join(str(c) for c in r) + " |" for r in rijen]
    return "\n".join(regels)


def _datum(unix_s: int | None) -> str:
    return "n.v.t." if unix_s is None else datetime.fromtimestamp(unix_s, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def schrijf_rapport(stat: dict, controle: pd.DataFrame) -> str:
    w = stat["woningen"]
    r: list[str] = []
    r.append("# Kwaliteit van de uitvoer\n")
    r.append("Dit rapport wordt door de pijplijn gegenereerd (`python -m wattopia_preprocessing`) en bevat alleen "
             "aggregaten: aantallen, aandelen en afwijkingspercentages. Het zegt iets over de **data en de "
             "verwerking**, niet over de prestaties van woningen of installaties. Waarden per woning staan "
             "niet in git; zie [`GEBRUIKSVOORWAARDEN.md`](../GEBRUIKSVOORWAARDEN.md).\n")
    r.append("Een vlag verandert geen waarde. In `woningen_jaar` staat de oorspronkelijke waarde onverkort naast "
             "de vlag; in `detail_5min` is een waarde die buiten het bereik valt `NaN` met een vlag, en houdt "
             "`detail_ruw` hem.\n")

    # ---- jaartotalen
    r.append("## 1. Jaartotalen\n")
    p = stat["projecten"]
    r.append(f"- `projecten`: {p['rijen']} projecten. Waarden die niet in het keuzemenu staan: "
             + (", ".join(f"{k.replace('_buiten_keuzemenu__bool', '')} ({n})" for k, n in p["buiten_keuzemenu"].items() if n)
                or "geen") + ".")
    jaren = ", ".join(f"{n} woningen in {j}" for j, n in w["jaren"].items())
    r.append(f"- `woningen_jaar`: {w['rijen']} woningen ({jaren}). Dubbele woningcodes: {w['dubbele_woningcodes']}. "
             f"Woningen met een projectcode die niet in `projecten` staat: {w['projecten_zonder_projectrij']}.\n")

    r.append("### 1.1 Vulgraad\n")
    r.append("Een lege cel is \"niet gerapporteerd\", geen nul. De vulgraad is zeer ongelijk; een analyse die een "
             "kolom nodig heeft, hoort eerst te kijken hoeveel woningen hem hebben.\n")
    r.append(_tabel(["kolom", "gevuld", "aandeel"],
                    [[f"`{v['kolom']}`", v["gevuld"], _pct(v["gevuld"], v["van"])] for v in w["vulgraad"]]) + "\n")

    r.append("### 1.2 Vlaggen op de woningen\n")
    r.append("De regel van elke vlag staat in [`datacatalogus.md`](datacatalogus.md). Een vergelijking is alleen "
             "toetsbaar als alle waarden erin gevuld zijn; het aandeel is genomen over de toetsbare woningen. "
             f"Slaat een regel bij minstens {int(DEFINITIEVERSCHIL_AANDEEL * 100)} % van de toetsbare woningen aan, dan "
             "heet dat een **definitieverschil** en geen fout.\n")
    rijen = []
    for k in K.WONINGEN_VLAGGEN:
        v = w["vlaggen"][k.naam]
        toetsbaar_kolom = k.naam in ("som_opwekker_klopt_niet__bool", "som_warmte_klopt_niet__bool",
                                     "balans_beschikbaar_klopt_niet__bool")
        van = v["toetsbaar"] if toetsbaar_kolom else w["rijen"]
        oordeel = ("definitieverschil" if van and v["aan"] / van >= DEFINITIEVERSCHIL_AANDEEL and toetsbaar_kolom
                   else "")
        rijen.append([f"`{k.naam}`", v["aan"], v["toetsbaar"] if toetsbaar_kolom else w["rijen"],
                      _pct(v["aan"], van, 2), oordeel])
    r.append(_tabel(["vlag", "aan", "toetsbaar", "aandeel van toetsbaar", "oordeel"], rijen) + "\n")

    # ---- detail
    r.append("## 2. Detaildata van twee woningen\n")
    lege = stat["lege_tabbladen"]
    r.append("Lege tabbladen worden niet als tabel geschreven. Per woning: "
             + "; ".join(f"{code}: {', '.join(l) if l else 'geen'}" for code, l in lege.items()) + ".\n")
    r.append("Het tabblad `summary` is een rekenblad met formules en wordt niet gelezen.\n")
    for code, d in stat["detail"].items():
        r.append(f"### 2.{list(stat['detail']).index(code) + 1} Woning {code}: meetpunten\n")
        rijen = []
        for m, g in d["gaten"].items():
            rijen.append([f"`{m}`", g["rijen"], f"{_datum(g['eerste'])} tot {_datum(g['laatste'])} UTC",
                          "n.v.t." if g["mediaan_stap_s"] is None else f"{g['mediaan_stap_s']:.0f} s",
                          g["stappen_boven_10min"],
                          "n.v.t." if g["langste_gat_s"] is None else f"{g['langste_gat_s'] / 86400:.1f} d",
                          g["dubbele_tijdstempels"]])
        r.append(_tabel(["meetpunt", "metingen", "bereik", "mediane stap", "stappen > 10 min", "langste gat",
                         "dubbele tijdstempels"], rijen) + "\n")

    r.append("## 3. Het raster van vijf minuten\n")
    r.append("De dekking is het aandeel intervallen waarvan beide grenzen geïnterpoleerd konden worden uit twee "
             "metingen die minder dan 15 minuten uit elkaar liggen. Daarbuiten is het vermogen `NaN`; er wordt "
             "niet over gaten geïnterpoleerd.\n")
    for code, d in stat["detail"].items():
        ras = d["raster"]
        n = ras["intervallen"]
        r.append(f"### Woning {code}\n")
        r.append(_tabel(["vermogenskolom", "gedekt", "teller daalt", "met waarde"],
                        [[f"`{k}`", _pct(v["gedekt"], n, 2), v["daalt"], _pct(v["met_waarde"], n, 2)]
                         for k, v in ras["tellers"].items()]) + "\n")
        r.append(_tabel(["tabblad", "intervallen met een steekproef"],
                        [[f"`{m}`", _pct(v, n, 1)] for m, v in ras["met_steekproef"].items()]) + "\n")

    r.append("### 3.1 Sentinels in temperaturen\n")
    r.append(f"Een temperatuur buiten {K.TEMP_MIN_DEGC:g} tot {K.TEMP_MAX_DEGC:g} graden Celsius (en, voor "
             f"kamertemperaturen en het setpoint daarvan, {K.TEMP_KAMER_ONDERGRENS_DEGC:g} of lager) is in `detail_5min` `NaN` met een "
             "vlag; de ruwe laag houdt de waarde. Aandeel van de gevulde ruwe metingen:\n")
    rijen = []
    for code, d in stat["detail"].items():
        for m, kol in d["sentinels"].items():
            for naam, v in kol.items():
                if v["buiten_bereik"]:
                    rijen.append([code, f"`{m}`", f"`{naam}`", v["buiten_bereik"], _pct(v["buiten_bereik"], v["gevuld"], 3)])
    r.append((_tabel(["woning", "tabblad", "kolom", "aantal", "aandeel"], rijen) if rijen else "Geen.") + "\n")

    # ---- zelfcontrole
    r.append("## 4. Zelfcontrole tegen de jaartotalen\n")
    r.append("De twee detailwoningen staan ook in de jaartotalen. Vier grootheden uit de detaildata worden tegen het "
             "jaartotaal gelegd, op drie manieren:\n")
    r.append("- `reeks_delta`: eindstand min beginstand van de hele ruwe reeks. Het jaartotaal van Wattopia is "
             "vermoedelijk zo bepaald.")
    r.append("- `raster_som`: de som over de intervallen van `detail_5min`. Dit telt alleen de gedekte intervallen en "
             "mist dus de energie in gaten van meer dan 15 minuten, die niet wordt verdeeld of verzonnen. De "
             "afwijking is daarom negatief en ongeveer gelijk aan het aandeel van de energie dat in gaten viel.")
    r.append("- `raster_som_met_gaten`: `raster_som` plus de tellervoortgang in de niet-gedekte stukken, die wel in de "
             "teller staat maar niet aan een interval is toegerekend. Dit toetst de omrekening van teller naar "
             "vermogen in het raster.\n")
    r.append(f"Tolerantie {str(K.TOLERANTIE_PCT).replace('.', ',')} %. De run faalt als `reeks_delta` of `raster_som_met_gaten` daarbuiten valt; "
             "`raster_som` wordt gerapporteerd maar niet afgedwongen. Er staan hier alleen percentages.\n")
    rijen = []
    for rij in controle.itertuples():
        rijen.append([rij.woningcode__str, rij.grootheid__str, rij.definitie__str, _getal(rij.afwijking__pct),
                      ("binnen" if rij.binnen_tolerantie__bool else "buiten")
                      + (" (niet afgedwongen)" if rij.definitie__str == "raster_som" else "")])
    r.append(_tabel(["woning", "grootheid", "definitie", "afwijking", "oordeel"], rijen) + "\n")
    return "\n".join(r)
