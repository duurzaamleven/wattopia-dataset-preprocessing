# SPDX-License-Identifier: EUPL-1.2
"""Toetsen op het manifest: sha256, atomisch schrijven, contractversie, hervatten."""

import pandas as pd

from wattopia_preprocessing import manifest as M


def test_atomisch_schrijven_laat_geen_tmp_achter(tmp_path):
    pad = tmp_path / "sub" / "t.parquet"
    M.schrijf_parquet_atomisch(pad, pd.DataFrame({"a": [1, 2]}))
    assert pad.is_file() and not list(tmp_path.rglob("*.tmp"))
    assert pd.read_parquet(pad)["a"].tolist() == [1, 2]


def test_manifest_onthoudt_en_herkent_een_voltooid_onderdeel(tmp_path):
    pad = tmp_path / "t.parquet"
    M.schrijf_parquet_atomisch(pad, pd.DataFrame({"a": [1]}))
    m = M.Manifest(tmp_path)
    assert not m.is_voltooid("tabel", "t")
    regel = m.voeg_toe("tabel", "t", pad, rijen=1)
    assert regel.sha256 == M.sha256_van_bestand(pad) and regel.pad == "t.parquet"
    assert M.Manifest(tmp_path).is_voltooid("tabel", "t")  # ook na opnieuw laden
    pad.unlink()
    assert not M.Manifest(tmp_path).is_voltooid("tabel", "t")  # bestand weg: niet meer af


def test_andere_contractversie_telt_als_niet_voltooid(tmp_path):
    pad = tmp_path / "t.parquet"
    M.schrijf_parquet_atomisch(pad, pd.DataFrame({"a": [1]}))
    M.Manifest(tmp_path, contract="oud").voeg_toe("tabel", "t", pad, rijen=1)
    assert not M.Manifest(tmp_path, contract="nieuw").is_voltooid("tabel", "t")


def test_andere_bron_sha256_telt_als_niet_voltooid(tmp_path):
    pad = tmp_path / "t.parquet"
    M.schrijf_parquet_atomisch(pad, pd.DataFrame({"a": [1]}))
    m = M.Manifest(tmp_path)
    m.voeg_toe("werkboek", "w", pad, rijen=1, bron_sha256="aaa")
    assert m.is_voltooid("werkboek", "w", bron_sha256="aaa")
    assert not m.is_voltooid("werkboek", "w", bron_sha256="bbb")


def test_een_halve_manifestregel_wordt_overgeslagen(tmp_path):
    (tmp_path / "_manifest.jsonl").write_text('{"onderdeel": "tabel", "sleu\n', encoding="utf-8")
    assert M.Manifest(tmp_path).sleutels("tabel") == set()
