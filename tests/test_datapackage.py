"""Toetsen op datapackage.json en de datacatalogus: dezelfde bron als de uitvoer."""

import re

import pytest

from wattopia_preprocessing import datapackage as D
from wattopia_preprocessing import kolommen as K


def test_elke_kolom_van_elke_tabel_staat_in_het_datapackage_en_omgekeerd():
    pakket = D.bouw_datapackage()
    per_naam = {r["name"]: r for r in pakket["resources"]}
    for tabel in D.resource_namen():
        velden = [f["name"] for f in per_naam[D._resource_naam(tabel)]["schema"]["fields"]]
        assert velden == [k.naam for k in K.tabel_kolommen(tabel)], tabel


def test_primaire_sleutel_bestaat_als_veld():
    for r in D.bouw_datapackage()["resources"]:
        velden = {f["name"] for f in r["schema"]["fields"]}
        assert set(r["schema"]["primaryKey"]) <= velden, r["name"]


def test_kolomnamen_volgen_de_physiquant_unit_conventie():
    """Elke kolomnaam eindigt op een dubbele underscore plus eenheid, of is een tijdkolom, een
    sleutel of een tijdstip van een steekproef."""
    # uit_detail en uit_jaartotaal hebben de eenheid in de kolom eenheid__str (ontwerp §4.5)
    uitzonderingen = {"tijdstip", "tijdstip_start", "uit_detail", "uit_jaartotaal"}
    for tabel in D.resource_namen():
        for k in K.tabel_kolommen(tabel):
            if k.naam in uitzonderingen or k.naam.endswith("_tijdstip_steekproef"):
                continue
            assert re.search(r"__[A-Za-z0-9_]+$", k.naam), f"{tabel}.{k.naam}"
            assert k.beschrijving, f"{tabel}.{k.naam} heeft geen beschrijving"


def test_vlaggen_hebben_het_type_bool_en_cumulatieve_standen_dragen_cum():
    for tabel in D.resource_namen():
        for k in K.tabel_kolommen(tabel):
            if k.naam.endswith("__bool"):
                assert k.type == "bool", k.naam
            if k.bron in ("total_energy_in", "total_energy_out", "total_energyGJ", "energy_in_low", "energy_in_norm",
                          "energy_out_low", "energy_out_norm"):
                assert "_cum__" in k.naam, k.naam
            if k.naam.startswith("p_") and tabel in ("detail_5min", "detail_kwartier"):
                assert "_cum" not in k.naam  # een gemiddeld vermogen is geen meterstand


def test_datacatalogus_noemt_elke_tabel_en_elke_kolom():
    tekst = D.schrijf_datacatalogus()
    for tabel in D.resource_namen():
        assert f"`{tabel}`" in tekst
        for k in K.tabel_kolommen(tabel):
            assert f"`{k.naam}`" in tekst
    assert chr(0x2014) not in tekst


def test_datapackage_voldoet_aan_de_frictionless_specificatie():
    frictionless = pytest.importorskip("frictionless")
    beschrijving = D.bouw_datapackage()
    pakket = frictionless.Package.from_descriptor(beschrijving)  # faalt op een ongeldige beschrijving
    assert [r.name for r in pakket.resources] == [r["name"] for r in beschrijving["resources"]]
