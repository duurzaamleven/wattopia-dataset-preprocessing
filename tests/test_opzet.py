# SPDX-License-Identifier: EUPL-1.2
"""Toetsen op de opzet: de data blijft buiten git, en het pakket is te controleren op compleetheid."""

import subprocess
from pathlib import Path

import wattopia_preprocessing as wp

ROOT = Path(__file__).resolve().parents[1]


def test_ontbrekende_bestanden_op_een_lege_map(tmp_path):
    assert wp.ontbrekende_bestanden(tmp_path) == list(wp.VERWACHTE_BESTANDEN)


def test_een_compleet_pakket_mist_niets(tmp_path):
    for naam in wp.VERWACHTE_BESTANDEN:
        (tmp_path / naam).write_text("")
    assert wp.ontbrekende_bestanden(tmp_path) == []


def test_data_en_brondata_staan_in_gitignore():
    """De dataset mag niet worden doorgestuurd; git mag hem dus nooit oppakken."""
    for pad in ("data/raw/pakket.zip", "data/processed/tabel.parquet",
                "ergens/Detaildata woning_x.xlsx", "RVO_Woningprestaties_Datapakketje_2022.zip"):
        uit = subprocess.run(["git", "check-ignore", "-q", pad], cwd=ROOT)
        assert uit.returncode == 0, f"{pad} wordt niet genegeerd"
