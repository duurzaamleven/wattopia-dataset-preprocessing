# SPDX-License-Identifier: EUPL-1.2
"""De echte data: draait alleen als ``data/raw/`` het pakket heeft en ``pytest -m echte_data`` wordt
gegeven (standaard overgeslagen, zie ``addopts`` in pyproject.toml). Gebruikt ``data/processed/`` als
dat er al staat, anders draait de pijplijn eerst (dat leest de werkboeken, wat minuten duurt)."""

import pandas as pd
import pytest

import wattopia_preprocessing as wp
from wattopia_preprocessing import kolommen as K
from wattopia_preprocessing import pijplijn, toetsen

pytestmark = [
    pytest.mark.echte_data,
    pytest.mark.skipif(bool(wp.ontbrekende_bestanden()), reason="het pakket staat niet in data/raw/"),
]


@pytest.fixture(scope="module")
def uit():
    map_ = wp.RAW_DIR.parent / "processed"
    if not (map_ / "controle_jaartotalen.parquet").is_file():
        pijplijn.draai(wp.RAW_DIR, map_, schrijf_docs=False)
    return map_


def test_vorm_van_de_echte_uitvoer(uit):
    projecten = pd.read_parquet(uit / "projecten.parquet")
    woningen = pd.read_parquet(uit / "woningen_jaar.parquet")
    assert len(projecten) == 24 and len(woningen) == 898
    assert woningen["woningcode__str"].is_unique
    assert woningen["projectcode__str"].isin(projecten["projectcode__str"]).all()
    assert woningen["jaar_monitoring__0"].value_counts().to_dict() == {2019: 466, 2020: 432}
    for naam in ("detail_5min", "detail_kwartier", "controle_jaartotalen"):
        df = pd.read_parquet(uit / f"{naam}.parquet")
        assert list(df.columns) == [k.naam for k in K.tabel_kolommen(naam)]
    vijf = pd.read_parquet(uit / "detail_5min.parquet")
    assert len(vijf) == 2 * 365 * 288
    assert len(pd.read_parquet(uit / "detail_kwartier.parquet")) == 2 * 365 * 96


def test_zelfcontrole_op_de_echte_data(uit):
    c = pd.read_parquet(uit / "controle_jaartotalen.parquet")
    vereist = c[c["definitie__str"].isin(toetsen.VEREISTE_DEFINITIES)]
    assert len(c) == 24
    assert vereist["binnen_tolerantie__bool"].all(), c[["woningcode__str", "grootheid__str", "definitie__str", "afwijking__pct"]]
