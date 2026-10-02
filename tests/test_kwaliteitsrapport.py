"""Toetsen op het kwaliteitsrapport: opmaak en het oordeel over vlaggen."""

import pandas as pd

from wattopia_preprocessing import kwaliteitsrapport as R


def test_percentages_en_getallen_met_een_komma_en_zonder_negatieve_nul():
    assert R._pct(1, 8) == "12,5 %" and R._pct(0, 0) == "n.v.t."
    assert R._getal(-1e-9) == "+0,000 %" and R._getal(-1.3) == "-1,300 %" and R._getal(float("nan")) == "n.v.t."


def test_een_tabel_heeft_een_kopregel_en_een_scheidingsregel():
    t = R._tabel(["a", "b"], [[1, 2]])
    assert t.splitlines() == ["| a | b |", "|---|---|", "| 1 | 2 |"]


def test_datum_is_utc():
    assert R._datum(1546300800) == "2019-01-01 00:00" and R._datum(None) == "n.v.t."


def test_vlag_bij_de_helft_van_de_toetsbare_woningen_heet_definitieverschil():
    stat = {
        "projecten": {"rijen": 1, "buiten_keuzemenu": {}},
        "woningen": {"rijen": 10, "vulgraad": [], "jaren": {2019: 10}, "dubbele_woningcodes": 0,
                     "projecten_zonder_projectrij": 0,
                     "vlaggen": {"negatieve_waarde__bool": {"aan": 0, "toetsbaar": 10},
                                 "setpoint_nul__bool": {"aan": 0, "toetsbaar": 10},
                                 "som_opwekker_klopt_niet__bool": {"aan": 0, "toetsbaar": 4},
                                 "som_warmte_klopt_niet__bool": {"aan": 0, "toetsbaar": 4},
                                 "balans_beschikbaar_klopt_niet__bool": {"aan": 3, "toetsbaar": 6}}},
        "lege_tabbladen": {}, "detail": {},
    }
    tekst = R.schrijf_rapport(stat, pd.DataFrame(columns=["woningcode__str", "grootheid__str", "definitie__str",
                                                          "afwijking__pct", "binnen_tolerantie__bool"]))
    regel = next(r for r in tekst.splitlines() if r.startswith("| `balans_beschikbaar"))
    assert "definitieverschil" in regel
    assert "definitieverschil" not in next(r for r in tekst.splitlines() if r.startswith("| `som_opwekker"))
