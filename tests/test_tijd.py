"""Toetsen op de tijd: lokale tijd, het raster, tellerinterpolatie en steekproeven."""

import numpy as np
import pandas as pd

from wattopia_preprocessing import tijd as T


def test_unix_naar_lokale_tijd_rond_de_zomertijdwissel():
    # 31 maart 2019: om 01:00 UTC gaat de klok van 02:00 naar 03:00 (CET naar CEST)
    s = pd.Timestamp("2019-03-31 00:59:00", tz="UTC").timestamp()
    lokaal = T.unix_naar_lokaal([s, s + 60, s + 3600])
    assert [t.strftime("%H:%M %z") for t in lokaal] == ["01:59 +0100", "03:00 +0200", "03:59 +0200"]
    assert str(lokaal.tz) == "Europe/Amsterdam"


def test_unix_naar_lokale_tijd_rond_de_wintertijdwissel():
    s = pd.Timestamp("2019-10-27 00:30:00", tz="UTC").timestamp()  # 02:30 CEST
    lokaal = T.unix_naar_lokaal([s, s + 3600])
    assert [t.strftime("%H:%M %z") for t in lokaal] == ["02:30 +0200", "02:30 +0100"]


def test_jaarraster_2019_is_een_volledig_lokaal_jaar_van_vijf_minuten():
    r = T.jaarraster(2019)
    assert len(r) == 365 * 288
    assert r[0] == pd.Timestamp("2019-01-01 00:00", tz="Europe/Amsterdam")
    assert r[-1] == pd.Timestamp("2019-12-31 23:55", tz="Europe/Amsterdam")
    assert (np.diff(T.lokaal_naar_unix(r)) == 300).all()  # vaste duur, ook over de zomertijdwissels
    assert len(T.rastergrenzen_s(r)) == len(r) + 1


def test_interpolatie_met_jitter_en_een_gat():
    # metingen met jitter rond 300 s; een gat van 30 minuten tussen 1500 en 3300
    t = np.array([0, 295, 600, 905, 1200, 1500, 3300, 3600, 3900, 4200], dtype=float)
    stand = t / 100.0  # 0,01 per seconde
    grenzen = np.arange(0, 4201, 300, dtype=float)
    uit, gedekt = T.interpoleer_teller(t, stand, grenzen)
    # lineair, dus de interpolatie geeft de exacte stand daar waar er gedekt is
    assert np.allclose(uit[gedekt], grenzen[gedekt] / 100.0)
    # grenzen binnen het gat (1800 tot 3000) zijn niet gedekt: geen interpolatie over meer dan 15 minuten
    in_gat = (grenzen > 1500) & (grenzen < 3300)
    assert not gedekt[in_gat].any() and np.isnan(uit[in_gat]).all()
    assert gedekt[grenzen <= 1500].all() and gedekt[grenzen >= 3300].all()


def test_som_van_de_intervallen_is_delta_stand_over_het_gedekte_deel():
    t = np.array([0, 295, 600, 905, 1200, 1500, 3300, 3600, 3900, 4200], dtype=float)
    stand = np.cumsum(np.r_[0, np.diff(t) * 0.5])  # 0,5 kWh per seconde, zo ontstaat een teller
    grenzen = np.arange(0, 4201, 300, dtype=float)
    uit, gedekt = T.interpoleer_teller(t, stand, grenzen)
    p, interval_gedekt, daalt = T.vermogen_uit_stand(uit, gedekt, 3.6e6)
    assert not daalt.any()
    energie_kwh = np.nansum(p) * 300 / 3.6e6
    verwacht = (uit[gedekt][-1] - uit[gedekt][0])  # eindstand min beginstand, maar zonder het gat
    gat = uit[(grenzen == 3300)][0] - uit[(grenzen == 1500)][0]
    assert np.isclose(energie_kwh, verwacht - gat)
    assert np.isnan(p[interval_gedekt == False]).all()  # noqa: E712


def test_een_dalende_teller_geeft_een_vlag_en_nan():
    t = np.arange(0, 1801, 300, dtype=float)
    stand = np.array([10, 11, 12, 5, 6, 7, 8], dtype=float)  # daalt tussen 900 en 1200
    uit, gedekt = T.interpoleer_teller(t, stand, t)
    p, interval_gedekt, daalt = T.vermogen_uit_stand(uit, gedekt, 3.6e6)
    assert daalt.tolist() == [False, False, True, False, False, False]
    assert np.isnan(p[2]) and not np.isnan(p[1])


def test_geen_extrapolatie_buiten_de_reeks():
    t = np.array([300.0, 600.0, 900.0])
    uit, gedekt = T.interpoleer_teller(t, np.array([1.0, 2.0, 3.0]), np.array([0.0, 300.0, 900.0, 1200.0]))
    assert gedekt.tolist() == [False, True, True, False]


def test_nan_in_de_teller_telt_niet_mee():
    t = np.arange(0, 1201, 300, dtype=float)
    stand = np.array([0.0, np.nan, 2.0, 3.0, 4.0])
    uit, gedekt = T.interpoleer_teller(t, stand, t)
    assert gedekt.all()  # 0 en 600 liggen 10 minuten uit elkaar: nog binnen 15 minuten
    assert uit[1] == 1.0


def test_steekproef_is_de_laatste_meting_binnen_het_interval_niet_een_gemiddelde():
    t = np.array([10, 100, 290, 310, 590, 1000], dtype=float)
    grenzen = np.array([0, 300, 600, 900, 1200], dtype=float)
    idx = T.steekproef_laatste_binnen(t, grenzen)
    assert idx.tolist() == [2, 4, -1, 5]  # 290; 590; niets in [600, 900); 1000
