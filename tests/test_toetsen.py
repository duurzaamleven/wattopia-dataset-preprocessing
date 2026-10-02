"""Toetsen op de vlaggen en de zelfcontrole."""

import numpy as np
import pandas as pd
import pytest

from wattopia_preprocessing import kolommen as K
from wattopia_preprocessing import toetsen


def _woningen(**waarden):
    basis = {k.naam: [np.nan] for k in K.WONINGEN if k.type == "float"}
    basis.update({k: [v] for k, v in waarden.items()})
    return pd.DataFrame(basis)


def test_negatieve_waarde_vlag_slaat_niet_aan_voor_beschikbaar_en_netto_afname():
    w = _woningen(e_beschikbaar_persoonlijk__kWh_a_1=-4250.0, e_netto_afname__kWh_a_1=-5000.0)
    assert not toetsen.vlaggen_woningen(w)["negatieve_waarde__bool"].iloc[0]
    w = _woningen(q_tapwater__GJ_a_1=-0.000189)
    assert toetsen.vlaggen_woningen(w)["negatieve_waarde__bool"].iloc[0]


def test_setpoint_nul():
    assert toetsen.vlaggen_woningen(_woningen(temp_setpoint_woonkamer_stookseizoen__degC=0.0))["setpoint_nul__bool"].iloc[0]
    assert not toetsen.vlaggen_woningen(_woningen())["setpoint_nul__bool"].iloc[0]  # leeg is geen nul


def test_som_opwekker_alleen_als_alle_drie_gevuld_zijn():
    w = _woningen(e_opwekker_ruimte__kWh_a_1=600.0, e_opwekker_tapwater__kWh_a_1=400.0,
                  e_opwekker_totaal__kWh_a_1=1005.0)
    assert not toetsen.vlaggen_woningen(w)["som_opwekker_klopt_niet__bool"].iloc[0]  # 0,5 % verschil
    w["e_opwekker_totaal__kWh_a_1"] = 1100.0
    assert toetsen.vlaggen_woningen(w)["som_opwekker_klopt_niet__bool"].iloc[0]
    w["e_opwekker_tapwater__kWh_a_1"] = np.nan
    assert pd.isna(toetsen.vlaggen_woningen(w)["som_opwekker_klopt_niet__bool"].iloc[0])  # niet toetsbaar


def test_balans_beschikbaar_heeft_een_relatieve_en_een_absolute_drempel():
    basis = dict(e_opwek__kWh_a_1=8000.0, e_opwekker_totaal__kWh_a_1=1500.0, e_gebouw_overig__kWh_a_1=270.0)
    verwacht = 8000.0 - 1500.0 - 270.0
    assert not toetsen.vlaggen_woningen(_woningen(e_beschikbaar_persoonlijk__kWh_a_1=verwacht + 5, **basis))[
        "balans_beschikbaar_klopt_niet__bool"].iloc[0]  # onder 10 kWh
    assert toetsen.vlaggen_woningen(_woningen(e_beschikbaar_persoonlijk__kWh_a_1=verwacht + 500, **basis))[
        "balans_beschikbaar_klopt_niet__bool"].iloc[0]
    assert pd.isna(toetsen.vlaggen_woningen(_woningen(e_beschikbaar_persoonlijk__kWh_a_1=1.0))[
        "balans_beschikbaar_klopt_niet__bool"].iloc[0])


def _controle(afwijking_pct):
    totalen = {"W_a": {(g, d): (100.0 * (1 + afwijking_pct / 100), e)
                       for g, (e, _) in toetsen.CONTROLE_BRONNEN.items() for d in toetsen.DEFINITIES}}
    woningen = pd.DataFrame({"woningcode__str": ["W_a"],
                             **{kol: [100.0] for kol in K.CONTROLE_GROOTHEDEN.values()}})
    return toetsen.bouw_controle(totalen, woningen)


def test_zelfcontrole_slaagt_binnen_de_tolerantie():
    c = _controle(0.3)
    assert len(c) == 12 and c["binnen_tolerantie__bool"].all()
    assert np.allclose(c["afwijking__pct"], 0.3)
    toetsen.eis_controle(c)


def test_zelfcontrole_faalt_boven_de_tolerantie():
    c = _controle(0.6)
    assert not c["binnen_tolerantie__bool"].any()
    with pytest.raises(toetsen.ControleFout, match="0.5 %"):
        toetsen.eis_controle(c)


def test_zelfcontrole_faalt_als_het_jaartotaal_ontbreekt():
    c = _controle(0.0)
    i = c.index[c["definitie__str"] == "reeks_delta"][0]
    c.loc[i, "afwijking__pct"] = np.nan
    c.loc[i, "binnen_tolerantie__bool"] = False
    with pytest.raises(toetsen.ControleFout):
        toetsen.eis_controle(c)


def test_gatstatistiek():
    s = toetsen.gatstatistiek(np.array([0, 300, 600, 2400, 2700]))
    assert s["rijen"] == 5 and s["stappen_boven_10min"] == 1 and s["langste_gat_s"] == 1800.0
    assert s["dubbele_tijdstempels"] == 0


def test_raster_som_mist_de_gaten_maar_raster_som_met_gaten_en_reeks_delta_niet():
    from wattopia_preprocessing import tabellen

    from .conftest import AANTAL, START_S, kort_raster
    t = START_S + 300 * np.arange(AANTAL + 1)
    bron = pd.DataFrame({"Timestamp": t, "power": 1200.0, "total_energy_in": 0.1 * np.arange(AANTAL + 1)})
    bron = bron[~bron.index.isin(range(100, 110))].reset_index(drop=True)  # gat van 50 minuten
    ruw = {"energyHeatpump": tabellen.bouw_detail_ruw("energyHeatpump", bron, "W_x"),
           "energyBooster": tabellen.bouw_detail_ruw("energyBooster", bron, "W_x")}
    vijf = tabellen.bouw_detail_5min("W_x", ruw, kort_raster())
    # alleen de heatpump-bronnen van e_opwekker_totaal zijn gevuld; de andere grootheden zijn niet compleet
    totalen = toetsen.totalen_uit_detail(ruw, vijf)
    raster, _ = totalen[("e_opwekker_totaal", "raster_som")]
    met_gaten, _ = totalen[("e_opwekker_totaal", "raster_som_met_gaten")]
    reeks, _ = totalen[("e_opwekker_totaal", "reeks_delta")]
    assert np.isclose(reeks, 2 * 0.1 * AANTAL)
    assert raster < reeks * 0.99  # de gedekte intervallen missen de energie in het gat
    assert np.isclose(met_gaten, reeks)  # de tellervoortgang in het gat wordt er weer bij opgeteld
    assert np.isnan(totalen[("e_opwek", "reeks_delta")][0])  # zonder tabblad solar niet te controleren


def test_raster_som_wordt_gerapporteerd_maar_niet_afgedwongen():
    c = _controle(0.0)
    c.loc[c["definitie__str"] == "raster_som", ["afwijking__pct", "binnen_tolerantie__bool"]] = [-1.3, False]
    toetsen.eis_controle(c)  # slaagt: alleen raster_som is buiten de tolerantie
    c.loc[c["definitie__str"] == "raster_som_met_gaten", "binnen_tolerantie__bool"] = False
    with pytest.raises(toetsen.ControleFout):
        toetsen.eis_controle(c)
