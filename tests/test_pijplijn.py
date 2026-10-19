# SPDX-License-Identifier: EUPL-1.2
"""Toetsen op de pijplijn als geheel, op het synthetische pakket."""

import json

import numpy as np
import pandas as pd
import pytest

from wattopia_preprocessing import kolommen as K
from wattopia_preprocessing import lezers, pijplijn, toetsen

from .conftest import AANTAL, WONINGEN, kort_raster, schrijf_jaartotalen, verwachte_totalen


import shutil

from .conftest import schrijf_detailwerkboek


def _draai(raw, **kw):
    basis = raw.parent
    return pijplijn.draai(raw, basis / "processed", basis / "interim", docs_dir=basis / "docs",
                          datapackage_pad=basis / "datapackage.json", raster=kort_raster(), **kw)


@pytest.fixture(scope="module")
def eerste(pakket):
    """Een run op het synthetische pakket; de toetsen hieronder lezen de uitkomst. Elke run kost
    enkele tientallen seconden aan bestandstoegang, dus de tabellen worden maar één keer gebouwd."""
    return pakket, _draai(pakket)


def _kopie(raw, tmp_path):
    """Een kopie van het hele pakket met de uitvoer en de tussenstap van de eerste run."""
    doel = tmp_path / "kopie"
    shutil.copytree(raw.parent.parent, doel)
    return doel / "data" / "raw"


def test_pijplijn_schrijft_alle_tabellen_met_het_verwachte_aantal_rijen(eerste):
    raw, res = eerste
    uit = raw.parent / "processed"
    assert res.rijen["projecten"] == 1 and res.rijen["woningen_jaar"] == 3
    assert res.rijen["detail_5min"] == 2 * AANTAL and res.rijen["detail_kwartier"] == 2 * AANTAL // 3
    assert res.rijen["controle_jaartotalen"] == 2 * 4 * 3
    assert res.rijen["detail_ruw/energyHeatpump"] == 2 * (AANTAL + 1)
    assert not (uit / "detail_ruw" / "sheet15.parquet").exists()  # leeg tabblad niet geschreven
    assert not list(uit.rglob("*.tmp"))
    for naam in res.rijen:
        assert (uit / f"{naam}.parquet").is_file()
        assert list(pd.read_parquet(uit / f"{naam}.parquet").columns) == [k.naam for k in K.tabel_kolommen(naam)]


def test_zelfcontrole_slaagt_op_het_synthetische_pakket(eerste):
    _, res = eerste
    c = res.controle
    assert c["binnen_tolerantie__bool"].all()
    assert (c["afwijking__pct"].abs() < 1e-9).all()
    for code, factor in WONINGEN.items():
        rij = c[(c.woningcode__str == code) & (c.grootheid__str == "e_opwek") & (c.definitie__str == "raster_som")]
        assert np.isclose(rij["uit_detail"].iloc[0], verwachte_totalen(factor)["e_opwek"])


def test_zelfcontrole_laat_de_run_falen_bij_een_afwijkend_jaartotaal(eerste, tmp_path):
    raw = _kopie(eerste[0], tmp_path)
    schrijf_jaartotalen(raw / "Woningprestaties 2022-07-22 ANON.xlsx", afwijking_pct=2.0)
    with pytest.raises(toetsen.ControleFout, match="e_opwek"):
        _draai(raw)
    # de tabellen zijn wel geschreven, zodat de oorzaak na te gaan is
    assert (raw.parent / "processed" / "controle_jaartotalen.parquet").is_file()


def test_tweede_run_leest_de_werkboeken_niet_opnieuw(eerste, monkeypatch):
    raw, eerste_res = eerste
    assert sorted(eerste_res.werkboeken_gelezen) == sorted(WONINGEN) and not eerste_res.werkboeken_overgeslagen

    def mag_niet(*a, **k):
        raise AssertionError("werkboek opnieuw gelezen")

    monkeypatch.setattr(lezers, "lees_detailwerkboek", mag_niet)
    tweede = _draai(raw)
    assert tweede.werkboeken_gelezen == [] and sorted(tweede.werkboeken_overgeslagen) == sorted(WONINGEN)
    assert tweede.rijen == eerste_res.rijen


def test_een_gewijzigd_werkboek_wordt_wel_opnieuw_gelezen(eerste, tmp_path):
    raw = _kopie(eerste[0], tmp_path)
    schrijf_detailwerkboek(raw / "Detaildata woning_aaaaaaaa.xlsx", 1.0000001)  # andere inhoud, andere sha256
    tweede = _draai(raw)
    assert tweede.werkboeken_gelezen == ["W_aaaaaaaa"] and tweede.werkboeken_overgeslagen == ["W_bbbbbbbb"]


def test_documenten_worden_gegenereerd_en_bevatten_geen_em_dash_of_waarden_per_woning(eerste):
    raw, res = eerste
    basis = raw.parent
    for pad in (basis / "docs" / "data-quality.md", basis / "docs" / "datacatalogus.md", basis / "datapackage.json"):
        tekst = pad.read_text(encoding="utf-8")
        assert chr(0x2014) not in tekst, pad
        assert len(tekst) > 500
    dq = (basis / "docs" / "data-quality.md").read_text(encoding="utf-8")
    assert "Zelfcontrole" in dq and "raster_som" in dq and "reeks_delta" in dq
    # geen absolute jaartotalen van de woningen in het rapport
    for code, factor in WONINGEN.items():
        for waarde in verwachte_totalen(factor).values():
            assert f"{waarde:.2f}" not in dq
    pakket_json = json.loads((basis / "datapackage.json").read_text(encoding="utf-8"))
    assert {r["name"] for r in pakket_json["resources"]} >= {"projecten", "woningen_jaar", "detail_5min"}
    assert res.statistieken["woningen"]["rijen"] == 3


def test_ontbrekend_jaartotalenwerkboek_geeft_een_duidelijke_fout(tmp_path):
    (tmp_path / "raw").mkdir()
    with pytest.raises(FileNotFoundError, match="GEBRUIKSVOORWAARDEN"):
        pijplijn.draai(tmp_path / "raw", tmp_path / "uit", tmp_path / "interim")
