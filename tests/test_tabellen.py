# SPDX-License-Identifier: EUPL-1.2
"""Toetsen op het bouwen van de tabellen: typeren, vlaggen, ruwe tegenover afgeleide laag."""

import numpy as np
import pandas as pd
import pytest

from wattopia_preprocessing import kolommen as K
from wattopia_preprocessing import lezers, tabellen
from wattopia_preprocessing import tijd as T

from .conftest import AANTAL, START_S, kort_raster


def test_ja_nee_wordt_bool_en_leeg_wordt_na():
    uit = tabellen._naar_bool(pd.Series(["ja", "nee", None, "Ja "]), "x")
    assert uit.tolist() == [True, False, pd.NA, True]
    with pytest.raises(ValueError):
        tabellen._naar_bool(pd.Series(["misschien"]), "x")


def test_aanhalingstekens_worden_gelijkgetrokken_maar_de_tekst_blijft(pakket):
    jt = lezers.lees_jaartotalen(pakket / "Woningprestaties 2022-07-22 ANON.xlsx")
    p = tabellen.bouw_projecten(jt)
    # het werkboek heeft ’60 in de projectdata en ‘60 in het keuzemenu: binnen het menu
    assert not p["woningtypologie_buiten_keuzemenu__bool"].iloc[0]
    assert p["woningtypologie__cat"].iloc[0] == "Grondgebonden jaren ’60"  # oorspronkelijke tekst
    # een waarde die niet in het menu staat blijft staan en krijgt een vlag
    assert p["afgiftesysteem_buiten_keuzemenu__bool"].iloc[0]
    assert p["afgiftesysteem__cat"].iloc[0] == "Een afgiftesysteem dat niet bestaat"
    assert p["epv__bool"].iloc[0] is True or p["epv__bool"].iloc[0] == True  # noqa: E712
    assert list(p.columns) == [k.naam for k in K.tabel_kolommen("projecten")]


def test_woningen_vlaggen_en_lege_cellen(pakket):
    jt = lezers.lees_jaartotalen(pakket / "Woningprestaties 2022-07-22 ANON.xlsx")
    w = tabellen.bouw_woningen(jt)
    assert len(w) == 3
    assert w["setpoint_nul__bool"].tolist() == [True, True, False]  # setpoint 0 in de eerste twee
    assert w["e_opwekker_ruimte__kWh_a_1"].isna().all()  # niet gerapporteerd, geen nul
    # niet toetsbaar zonder alle waarden: leeg, niet onwaar
    assert w["som_opwekker_klopt_niet__bool"].isna().all()
    assert w["balans_beschikbaar_klopt_niet__bool"].isna().tolist() == [False, False, True]
    assert w["negatieve_waarde__bool"].tolist() == [False, False, False]  # beschikbaar mag negatief zijn


def test_werkboek_met_andere_eenheid_dan_het_ontwerp_faalt(pakket):
    jt = lezers.lees_jaartotalen(pakket / "Woningprestaties 2022-07-22 ANON.xlsx")
    jt.eenheden["Monitoringdata"]["Opgewekte energie"] = "MWh / jaar"
    with pytest.raises(ValueError, match="eenheid"):
        tabellen.bouw_woningen(jt)


def _ruw(naam, bron, code="W_x"):
    return tabellen.bouw_detail_ruw(naam, bron, code)


def _heatpump(aantal=AANTAL + 1, **kolommen):
    t = START_S + 300 * np.arange(aantal)
    df = pd.DataFrame({"Timestamp": t, "booster_status": 0, "error_code": None, "firmware_version": "1",
                       "flow_temp": 35.0, "op_mode": 3, "room_temp": 21.0, "temp": 40.0})
    for k, v in kolommen.items():
        df[k] = v
    return df


def test_ruwe_laag_houdt_sentinels_en_tijd_in_lokale_tijd():
    bron = _heatpump()
    bron.loc[10, "flow_temp"] = -100.0
    bron.loc[20, "room_temp"] = 0.0
    ruw = _ruw("HeatPump", bron)
    assert ruw["temp_aanvoer__degC"].iloc[10] == -100.0 and ruw["temp_ruimte__degC"].iloc[20] == 0.0
    assert str(ruw["tijdstip"].dt.tz) == "Europe/Amsterdam"
    assert ruw["timestamp_bron__s"].iloc[0] == START_S
    assert ruw["booster_status__bool"].dtype == "boolean"
    assert ruw["op_mode__cat"].iloc[0] == "3"
    assert list(ruw.columns) == [k.naam for k in K.detail_ruw_kolommen("HeatPump")]


def test_een_status_met_meer_dan_nul_en_een_wordt_geen_bool():
    with pytest.raises(ValueError, match="0 en 1"):
        _ruw("HeatPump", _heatpump(booster_status=2))


def test_een_onbekende_bronkolom_is_een_fout():
    with pytest.raises(ValueError, match="staan niet in"):
        _ruw("HeatPump", _heatpump(nieuwe_kolom=1.0))


def _teller(stap, aantal=AANTAL + 1, kolom="total_energy_in"):
    t = START_S + 300 * np.arange(aantal)
    return pd.DataFrame({"Timestamp": t, "power": stap * 12000, kolom: stap * np.arange(aantal)})


def test_sentinels_worden_nan_met_vlag_in_de_afgeleide_laag_en_blijven_in_de_ruwe():
    bron = _heatpump()
    bron.loc[10, "flow_temp"] = -100.0
    bron.loc[20, "room_temp"] = 0.0
    ruw = {"HeatPump": _ruw("HeatPump", bron)}
    vijf = tabellen.bouw_detail_5min("W_x", ruw, kort_raster())
    flow, vlag = "heatpump_temp_aanvoer_steekproef__degC", "heatpump_temp_aanvoer_steekproef_buiten_bereik__bool"
    assert np.isnan(vijf[flow].iloc[10]) and vijf[vlag].iloc[10]  # meting 10 valt in interval 10
    assert vijf[flow].iloc[9] == 35.0 and not vijf[vlag].iloc[9]
    kamer = "heatpump_temp_ruimte_steekproef__degC"
    assert np.isnan(vijf[kamer].iloc[20]) and vijf["heatpump_temp_ruimte_steekproef_buiten_bereik__bool"].iloc[20]
    assert vijf["heatpump_temp_ruimte_steekproef_buiten_bereik__bool"].sum() == 1
    assert vijf[vlag].sum() == 1
    # de ruwe laag houdt beide waarden
    assert ruw["HeatPump"]["temp_aanvoer__degC"].iloc[10] == -100.0


def test_thermostaat_met_min_twintig_en_min_honderd_is_een_sentinel():
    """Het ontwerp noemt alleen het bereik van -40 tot 120 graden; de thermostaat heeft ook -20 en -100."""
    t = START_S + 300 * np.arange(AANTAL + 1)
    temp = np.full(AANTAL + 1, 20.0)
    temp[5], temp[6], temp[7] = -20.0, -100.0, 0.0
    ruw = {"thermostat": _ruw("thermostat", pd.DataFrame({"Timestamp": t, "temp": temp}))}
    vijf = tabellen.bouw_detail_5min("W_x", ruw, kort_raster())
    vlag = "thermostat_temp_thermostaat_steekproef_buiten_bereik__bool"
    assert vijf[vlag].iloc[[5, 6, 7]].all() and vijf[vlag].sum() == 3
    assert vijf["thermostat_temp_thermostaat_steekproef__degC"].iloc[[5, 6, 7]].isna().all()
    assert ruw["thermostat"]["temp_thermostaat__degC"].iloc[5] == -20.0  # de ruwe laag houdt de waarde


def test_steekproef_is_de_laatste_meting_met_het_tijdstip_ervan():
    bron = _heatpump(aantal=10)
    bron["Timestamp"] = [START_S + s for s in (0, 100, 200, 310, 400, 590, 600, 900, 1000, 1190)]
    bron["room_temp"] = np.arange(10) + 10.0
    vijf = tabellen.bouw_detail_5min("W_x", {"HeatPump": _ruw("HeatPump", bron)}, kort_raster())
    # interval 0 [0, 300): metingen op 0, 100, 200; laatste = 200 (waarde 12), geen gemiddelde (11)
    assert vijf["heatpump_temp_ruimte_steekproef__degC"].iloc[0] == 12.0
    assert vijf["heatpump_tijdstip_steekproef"].iloc[0] == pd.Timestamp(START_S + 200, unit="s", tz="UTC").tz_convert(K.TIJDZONE)
    # interval 1 [300, 600): 310, 400, 590; laatste = 590 (waarde 15)
    assert vijf["heatpump_temp_ruimte_steekproef__degC"].iloc[1] == 15.0
    # na de laatste meting (1190) is er niets meer
    assert vijf["heatpump_tijdstip_steekproef"].iloc[4:].isna().all()


def test_een_ontbrekend_tabblad_geeft_lege_kolommen():
    vijf = tabellen.bouw_detail_5min("W_x", {}, kort_raster())
    assert vijf["p_warmtepomp__W"].isna().all() and not vijf["p_warmtepomp_gedekt__bool"].any()
    assert vijf["ventilation_tijdstip_steekproef"].isna().all()
    assert list(vijf.columns) == [k.naam for k in K.detail_5min_kolommen()]


def test_vermogen_uit_teller_en_dekking_in_het_raster():
    ruw = {"energyHeatpump": _ruw("energyHeatpump", _teller(0.1))}
    vijf = tabellen.bouw_detail_5min("W_x", ruw, kort_raster())
    assert np.allclose(vijf["p_warmtepomp__W"], 0.1 * 12000)  # 0,1 kWh per 5 min is 1200 W
    assert vijf["p_warmtepomp_gedekt__bool"].all()
    assert not vijf["p_warmtepomp_teller_daalt__bool"].any()
    assert vijf["p_booster__W"].isna().all()


def test_gat_in_de_teller_geeft_geen_vermogen_en_geen_interpolatie():
    bron = _teller(0.1)
    bron = bron[~bron.index.isin(range(100, 110))].reset_index(drop=True)  # 50 minuten zonder metingen
    vijf = tabellen.bouw_detail_5min("W_x", {"energyHeatpump": _ruw("energyHeatpump", bron)}, kort_raster())
    p = vijf["p_warmtepomp__W"]
    # de grenzen 100 tot en met 109 liggen in het gat; de intervallen 99 tot en met 109 raken het
    assert p.iloc[99:110].isna().all() and not vijf["p_warmtepomp_gedekt__bool"].iloc[99:110].any()
    # buiten het gat: normaal
    assert np.allclose(p.iloc[:99], 1200) and np.allclose(p.iloc[110:], 1200)
    # som over de intervallen is Δstand van het gedekte deel, geen extra energie uit het gat
    kwh = np.nansum(p) * 300 / 3.6e6
    assert np.isclose(kwh, 0.1 * (AANTAL - 11))  # 576 intervallen minus de 11 die het gat raken


def test_dalende_teller_in_het_raster():
    bron = _teller(0.1)
    bron.loc[200:, "total_energy_in"] -= 5.0  # de teller springt terug
    vijf = tabellen.bouw_detail_5min("W_x", {"energyHeatpump": _ruw("energyHeatpump", bron)}, kort_raster())
    assert vijf["p_warmtepomp_teller_daalt__bool"].sum() == 1
    assert vijf["p_warmtepomp__W"].isna().sum() == 1


def test_kwartier_is_alleen_gevuld_als_alle_drie_intervallen_gedekt_zijn():
    bron = _teller(0.1)
    bron = bron[~bron.index.isin([30, 31, 32, 33])].reset_index(drop=True)  # 20 minuten gat
    ruw = {"energyHeatpump": _ruw("energyHeatpump", bron), "HeatPump": _ruw("HeatPump", _heatpump())}
    vijf = tabellen.bouw_detail_5min("W_x", ruw, kort_raster())
    kw = tabellen.bouw_detail_kwartier(vijf)
    assert len(kw) == AANTAL // 3
    ontbreekt = kw["p_warmtepomp__W"].isna()
    assert (kw["p_warmtepomp_onvolledig__bool"] == ontbreekt).all()
    assert ontbreekt.sum() > 0 and not ontbreekt.all()
    assert np.allclose(kw["p_warmtepomp__W"].dropna(), 1200)
    # steekproeven komen van het laatste interval van het kwartier
    assert kw["tijdstip_start"].iloc[1] - kw["tijdstip_start"].iloc[0] == pd.Timedelta(minutes=15)
    assert kw["heatpump_tijdstip_steekproef"].iloc[0] == vijf["heatpump_tijdstip_steekproef"].iloc[2]
    assert list(kw.columns) == [k.naam for k in K.detail_kwartier_kolommen()]


def test_arrow_schema_volgt_de_kolomdefinitie():
    vijf = tabellen.bouw_detail_5min("W_x", {}, kort_raster())
    tabel = tabellen.naar_arrow(vijf, K.tabel_kolommen("detail_5min"))
    assert str(tabel.schema.field("tijdstip_start").type) == "timestamp[us, tz=Europe/Amsterdam]"
    assert tabel.num_rows == AANTAL


def test_jaarraster_en_zomertijd_in_de_uitvoer():
    r = T.jaarraster()
    assert str(r.tz) == "Europe/Amsterdam" and len(r) % 3 == 0
