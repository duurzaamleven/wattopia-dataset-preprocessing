"""De vlaggen op de jaartotalen en de zelfcontrole van de detaildata tegen de jaartotalen.

Een vlag verandert nooit een waarde; zij staat ernaast, met de regel erbij (``kolommen.py`` bevat de
beschrijving van elke regel, ``docs/datacatalogus.md`` herhaalt die).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import kolommen as K
from . import tijd as T

#: Relatieve afwijking waarboven een som of balans als "klopt niet" geldt (ontwerp §4.2).
SOM_TOLERANTIE = 0.01
#: Absolute ondergrens voor de balans van beschikbaar voor persoonlijk gebruik, in kWh.
BALANS_ONDERGRENS_KWH = 10.0
#: Een stap tussen twee metingen van meer dan dit aantal seconden telt als gat in de kwaliteit.
GAT_GRENS_S = 600


class ControleFout(RuntimeError):
    """De zelfcontrole tegen de jaartotalen faalt: een fout in de pijplijn, niet in de data."""


def _som_klopt_niet(delen: list[pd.Series], totaal: pd.Series) -> pd.Series:
    """Nullable boolean: totaal wijkt meer dan 1 % af van de som van ``delen``; ``NA`` als een van
    de waarden ontbreekt."""
    alles = pd.concat(delen + [totaal], axis=1)
    toetsbaar = alles.notna().all(axis=1)
    som = sum(delen)
    verschil = (totaal - som).abs()
    grens = SOM_TOLERANTIE * som.abs()
    afwijkt = (verschil > grens) & ~((som == 0) & (totaal == 0))
    return pd.Series(np.where(toetsbaar, afwijkt, pd.NA), index=totaal.index, dtype="boolean")


def vlaggen_woningen(w: pd.DataFrame) -> pd.DataFrame:
    """De vlaggen van ``woningen_jaar`` (ontwerp §4.2), als ``DataFrame`` met alleen de vlagkolommen.

    ``negatieve_waarde__bool`` en ``setpoint_nul__bool`` zijn waar of onwaar; de drie vergelijkingen
    zijn leeg als ze niet toetsbaar zijn (een van de waarden ontbreekt)."""
    negatief = pd.concat([(w[c] < 0).fillna(False) for c in K.ENERGIE_GROOTHEDEN_NIET_NEGATIEF], axis=1).any(axis=1)
    uit = pd.DataFrame(index=w.index)
    uit["negatieve_waarde__bool"] = negatief.astype(bool)
    uit["setpoint_nul__bool"] = (w["temp_setpoint_woonkamer_stookseizoen__degC"] == 0).fillna(False).astype(bool)
    uit["som_opwekker_klopt_niet__bool"] = _som_klopt_niet(
        [w["e_opwekker_ruimte__kWh_a_1"], w["e_opwekker_tapwater__kWh_a_1"]], w["e_opwekker_totaal__kWh_a_1"])
    uit["som_warmte_klopt_niet__bool"] = _som_klopt_niet(
        [w["q_ruimte__GJ_a_1"], w["q_tapwater__GJ_a_1"]], w["q_totaal__GJ_a_1"])
    verwacht = w["e_opwek__kWh_a_1"] - w["e_opwekker_totaal__kWh_a_1"] - w["e_gebouw_overig__kWh_a_1"]
    verschil = (w["e_beschikbaar_persoonlijk__kWh_a_1"] - verwacht).abs()
    toetsbaar = pd.concat([w["e_opwek__kWh_a_1"], w["e_opwekker_totaal__kWh_a_1"],
                           w["e_gebouw_overig__kWh_a_1"], w["e_beschikbaar_persoonlijk__kWh_a_1"]], axis=1).notna().all(axis=1)
    afwijkt = (verschil > SOM_TOLERANTIE * verwacht.abs()) & (verschil > BALANS_ONDERGRENS_KWH)
    uit["balans_beschikbaar_klopt_niet__bool"] = pd.Series(
        np.where(toetsbaar, afwijkt, pd.NA), index=w.index, dtype="boolean")
    return uit[[k.naam for k in K.WONINGEN_VLAGGEN]]


# --------------------------------------------------------------------------------------------
# zelfcontrole (ontwerp §4.5)
# --------------------------------------------------------------------------------------------

#: grootheid -> (eenheid, [(meetpunt, tellerkolom in detail_ruw, vermogenskolom in detail_5min)])
CONTROLE_BRONNEN: dict[str, tuple[str, list[tuple[str, str, str]]]] = {
    "e_opwekker_totaal": ("kWh", [("energyHeatpump", "e_in_cum__kWh", "p_warmtepomp__W"),
                                  ("energyBooster", "e_in_cum__kWh", "p_booster__W")]),
    "q_ruimte": ("GJ", [("flowHeatSpaceHeating", "q_cum__GJ", "q_ruimte__W")]),
    "e_opwek": ("kWh", [("solar", "e_uit_cum__kWh", "p_pv_opwek__W")]),
    "e_gebouw_overig": ("kWh", [("energyWtwReg", "e_in_cum__kWh", "p_wtw__W")]),
}
_JOULE_PER_EENHEID = {"kWh": 3.6e6, "GJ": 1e9}
DEFINITIES = ("raster_som", "raster_som_met_gaten", "reeks_delta")
#: De definities waarop de run moet slagen. ``raster_som`` alleen telt de gedekte intervallen en mist
#: dus per constructie de energie in gaten van meer dan 15 minuten; zij wordt gerapporteerd maar niet
#: afgedwongen (ontwerp §9, afwijking 1).
VEREISTE_DEFINITIES = ("raster_som_met_gaten", "reeks_delta")


def _teller_boekhouding(d: pd.DataFrame, teller: str, grenzen_s: np.ndarray) -> tuple[float, float] | None:
    """``(Δ over de ruwe reeks, tellervoortgang die niet aan een interval is toegerekend)`` voor één
    teller, in de eenheid van de teller. De tweede is de voortgang tussen de eerste en laatste gedekte
    grens min de som over de intervallen met een vermogen; dat zijn de gaten (geen dekking) en de
    dalende stukken. ``None`` als de teller minder dan twee standen heeft."""
    d = d.sort_values("timestamp_bron__s", kind="stable")
    standen = d[teller].dropna()
    if len(standen) < 2:
        return None
    delta_reeks = float(standen.iloc[-1] - standen.iloc[0])
    stand, gedekt = T.interpoleer_teller(d["timestamp_bron__s"].to_numpy(), d[teller].to_numpy(), grenzen_s)
    idx = np.flatnonzero(gedekt)
    if len(idx) < 2:
        return delta_reeks, 0.0
    voortgang = float(stand[idx[-1]] - stand[idx[0]])
    delta = np.diff(stand)
    interval_gedekt = gedekt[:-1] & gedekt[1:]
    toegerekend = float(delta[interval_gedekt & (delta >= 0)].sum())
    return delta_reeks, voortgang - toegerekend


def totalen_uit_detail(ruw: dict[str, pd.DataFrame], vijf: pd.DataFrame,
                       grenzen_s: np.ndarray | None = None) -> dict[tuple[str, str], tuple[float, str]]:
    """``{(grootheid, definitie): (waarde, eenheid)}`` voor één woning, volgens ontwerp §4.5:

    - ``raster_som``: som van vermogen maal duur over de intervallen van ``detail_5min``;
    - ``raster_som_met_gaten``: ``raster_som`` plus de tellervoortgang die niet aan een interval is
      toegerekend (gaten van meer dan 15 minuten). Dit toetst de omrekening in het raster zonder dat de
      energie in gaten verloren gaat of wordt verzonnen;
    - ``reeks_delta``: laatste min eerste tellerstand van de hele ruwe reeks.
    """
    grenzen_s = T.rastergrenzen_s(pd.DatetimeIndex(vijf["tijdstip_start"])) if grenzen_s is None else grenzen_s
    uit: dict[tuple[str, str], tuple[float, str]] = {}
    for grootheid, (eenheid, bronnen) in CONTROLE_BRONNEN.items():
        som = delta = onttrokken = 0.0
        compleet = True
        for meetpunt, teller, p_kolom in bronnen:
            som += float(np.nansum(vijf[p_kolom].to_numpy())) * K.STAP_S / _JOULE_PER_EENHEID[eenheid]
            d = ruw.get(meetpunt)
            boekhouding = None if d is None else _teller_boekhouding(d, teller, grenzen_s)
            if boekhouding is None:
                compleet = False
                continue
            delta += boekhouding[0]
            onttrokken += boekhouding[1]
        nan = np.nan
        uit[(grootheid, "raster_som")] = (som if compleet else nan, eenheid)
        uit[(grootheid, "raster_som_met_gaten")] = (som + onttrokken if compleet else nan, eenheid)
        uit[(grootheid, "reeks_delta")] = (delta if compleet else nan, eenheid)
    return uit


def bouw_controle(totalen: dict[str, dict[tuple[str, str], tuple[float, str]]],
                  woningen: pd.DataFrame) -> pd.DataFrame:
    """De tabel ``controle_jaartotalen``. ``totalen`` is per woningcode het resultaat van
    :func:`totalen_uit_detail`; ``woningen`` is ``woningen_jaar``."""
    rijen = []
    for woningcode, per_post in totalen.items():
        rij_jaar = woningen[woningen["woningcode__str"] == woningcode]
        for grootheid, jaarkolom in K.CONTROLE_GROOTHEDEN.items():
            jaar = float(rij_jaar[jaarkolom].iloc[0]) if len(rij_jaar) else np.nan
            for definitie in DEFINITIES:
                waarde, eenheid = per_post[(grootheid, definitie)]
                if np.isnan(jaar) or np.isnan(waarde) or jaar == 0:
                    afwijking = np.nan
                else:
                    afwijking = (waarde - jaar) / jaar * 100.0
                rijen.append({
                    "woningcode__str": woningcode, "grootheid__str": grootheid, "definitie__str": definitie,
                    "uit_detail": waarde, "uit_jaartotaal": jaar, "eenheid__str": eenheid,
                    "afwijking__pct": afwijking,
                    "binnen_tolerantie__bool": bool(not np.isnan(afwijking) and abs(afwijking) <= K.TOLERANTIE_PCT),
                })
    df = pd.DataFrame(rijen)
    df["woningcode__str"] = df["woningcode__str"].astype("string")
    for c in ("grootheid__str", "definitie__str", "eenheid__str"):
        df[c] = df[c].astype("string")
    return df[[k.naam for k in K.CONTROLE]]


def eis_controle(controle: pd.DataFrame, definities: tuple[str, ...] = VEREISTE_DEFINITIES) -> None:
    """Faalt met :class:`ControleFout` als een vereiste rij buiten de tolerantie valt."""
    slecht = controle[controle["definitie__str"].isin(definities) & ~controle["binnen_tolerantie__bool"]]
    if len(slecht):
        regels = [f"{r.woningcode__str} {r.grootheid__str} ({r.definitie__str}): "
                  f"afwijking {r.afwijking__pct:+.3f} %" for r in slecht.itertuples()]
        raise ControleFout(
            f"Zelfcontrole tegen de jaartotalen faalt (tolerantie {K.TOLERANTIE_PCT} %): "
            + "; ".join(regels) + ". Dit wijst op een fout in de pijplijn (eenheid, definitie of randeffect).")


# --------------------------------------------------------------------------------------------
# kwaliteitsstatistieken per tabblad (voor docs/data-quality.md)
# --------------------------------------------------------------------------------------------

def gatstatistiek(timestamp_s: np.ndarray) -> dict:
    """Aantal metingen, bereik, mediane stap en gaten van een reeks Unix-seconden."""
    t = np.sort(np.asarray(timestamp_s, dtype="float64"))
    if len(t) < 2:
        return {"rijen": int(len(t)), "eerste": None, "laatste": None, "mediaan_stap_s": None,
                "stappen_boven_10min": 0, "langste_gat_s": None, "dubbele_tijdstempels": 0}
    stap = np.diff(t)
    return {
        "rijen": int(len(t)),
        "eerste": int(t[0]), "laatste": int(t[-1]),
        "mediaan_stap_s": float(np.median(stap)),
        "stappen_boven_10min": int((stap > GAT_GRENS_S).sum()),
        "langste_gat_s": float(stap.max()),
        "dubbele_tijdstempels": int((stap == 0).sum()),
    }
