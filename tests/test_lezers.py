"""Toetsen op de lezers: drie kopregels, lege cellen, detailtabbladen."""

import numpy as np
import openpyxl
import pandas as pd

from wattopia_preprocessing import lezers


def test_drie_kopregels_en_lege_cellen_blijven_leeg():
    rijen = [
        ("GROEP A", None, "GROEP B"),
        ("code", "waarde", "andere"),
        (None, "kWh_e / jaar", "graden C"),
        ("x1", 1.5, None),
        ("x2", None, 20.0),
        (None, None, None),  # volledig lege rij
    ]
    df, groepen, eenheden = lezers.lees_gegroepeerd_blad(rijen, sleutelkolom="code")
    assert list(df.columns) == ["code", "waarde", "andere"]
    assert len(df) == 2
    assert groepen == {"code": "GROEP A", "waarde": "GROEP A", "andere": "GROEP B"}  # groepsnaam doorgetrokken
    assert eenheden["waarde"] == "kWh_e / jaar" and eenheden["code"] == ""
    assert df["waarde"].iloc[0] == 1.5 and np.isnan(df["waarde"].iloc[1])  # leeg is niet nul
    assert np.isnan(df["andere"].iloc[0]) and df["andere"].iloc[1] == 20.0


def test_rijen_zonder_sleutel_worden_overgeslagen():
    rijen = [(None, None), ("code", "w"), (None, None), ("a", 1), (None, 5)]
    df, _, _ = lezers.lees_gegroepeerd_blad(rijen, sleutelkolom="code")
    assert list(df["code"]) == ["a"]


def test_jaartotalen_uit_een_werkboek(pakket):
    jt = lezers.lees_jaartotalen(pakket / "Woningprestaties 2022-07-22 ANON.xlsx")
    assert len(jt.projectdata) == 1 and len(jt.monitoringdata) == 3
    assert "Woningtypologie" in jt.keuzemenu
    assert jt.eenheden["Monitoringdata"]["Opgewekte energie"] == "kWh_e / jaar"


def test_detailwerkboek_slaat_het_rekenblad_over_en_meldt_lege_tabbladen(pakket):
    bladen = dict(lezers.lees_detailwerkboek(pakket / "Detaildata woning_aaaaaaaa.xlsx"))
    assert "summary" not in bladen
    assert bladen["sheet15"] is None
    assert bladen["energyHeatpump"].shape == (577, 3)
    assert bladen["energyHeatpump"]["Timestamp"].dtype == "int64"


def test_detailkolom_met_tekst_blijft_tekst_en_getallen_blijven_getallen(tmp_path):
    pad = tmp_path / "x.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "HeatPump"
    ws.append(["Timestamp", "error_code", "temp", "leeg"])
    ws.append([1546300800, "E1", 20.5, None])
    ws.append([1546301100, None, None, None])
    wb.save(pad)
    df = dict(lezers.lees_detailwerkboek(pad))["HeatPump"]
    assert df["error_code"].iloc[0] == "E1" and pd.isna(df["error_code"].iloc[1])
    assert df["temp"].iloc[0] == 20.5 and np.isnan(df["temp"].iloc[1])
    assert df["leeg"].isna().all()
    assert isinstance(df, pd.DataFrame)
