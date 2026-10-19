# SPDX-License-Identifier: EUPL-1.2
"""Tijd: Unix-seconden naar lokale tijd, het 5-minutenraster en de interpolatie van tellers.

Conventie (ontwerp §2): elke tijdkolom in de uitvoer is tz-aware ``Europe/Amsterdam``, intern UTC;
intervallen zijn **begin-gelabeld**. Rekenen gebeurt op Unix-seconden (``float64``), zodat een
zomertijdwissel geen rol speelt.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .kolommen import MAX_INTERPOLATIEGAT_S, RASTERJAAR, STAP_S, TIJDZONE


def unix_naar_lokaal(seconden) -> pd.DatetimeIndex:
    """Unix-seconden (UTC) naar een tz-aware ``DatetimeIndex`` in ``Europe/Amsterdam``."""
    s = pd.Series(np.asarray(seconden, dtype="int64"))
    return pd.DatetimeIndex(pd.to_datetime(s, unit="s", utc=True).dt.tz_convert(TIJDZONE))


def lokaal_naar_unix(tijden: pd.DatetimeIndex) -> np.ndarray:
    """Tz-aware tijdstippen naar Unix-seconden (``int64``)."""
    return (tijden.tz_convert("UTC").as_unit("s").asi8).astype("int64")


def jaarraster(jaar: int = RASTERJAAR) -> pd.DatetimeIndex:
    """De begin-gelabelde intervalstarts van vijf minuten van het lokale kalenderjaar: van
    ``jaar-01-01 00:00`` tot (exclusief) ``jaar+1-01-01 00:00`` ``Europe/Amsterdam``. Vijf minuten is
    een vaste duur, dus de zomertijdwissels in het voorjaar en het najaar heffen elkaar op: een jaar
    van 365 dagen heeft 105.120 intervallen, en de lokale tijdstippen slaan een uur over of herhalen
    een uur zoals de klok dat doet."""
    start = pd.Timestamp(f"{jaar}-01-01", tz=TIJDZONE)
    einde = pd.Timestamp(f"{jaar + 1}-01-01", tz=TIJDZONE)
    return pd.date_range(start, einde, freq=f"{STAP_S}s", inclusive="left")


def rastergrenzen_s(raster: pd.DatetimeIndex) -> np.ndarray:
    """Unix-seconden van de intervalgrenzen: de starts plus het einde van het laatste interval."""
    starts = lokaal_naar_unix(raster)
    return np.append(starts, starts[-1] + STAP_S)


def interpoleer_teller(t_s: np.ndarray, stand: np.ndarray, grenzen_s: np.ndarray,
                       max_gat_s: int = MAX_INTERPOLATIEGAT_S) -> tuple[np.ndarray, np.ndarray]:
    """Tellerstand lineair geïnterpoleerd op de ``grenzen_s``.

    Een grens is **gedekt** als er een meting op of vóór en een op of na de grens bestaat en die
    twee minder dan ``max_gat_s`` seconden uit elkaar liggen (ontwerp §4.4). Daarbuiten blijft de
    stand ``NaN``: er wordt niet over gaten geïnterpoleerd en niet buiten de reeks geëxtrapoleerd.
    Metingen zonder tellerstand (``NaN``) tellen niet mee.

    ``t_s`` moet oplopend zijn. Geeft ``(stand_op_grens, gedekt)``.
    """
    t = np.asarray(t_s, dtype="float64")
    y = np.asarray(stand, dtype="float64")
    geldig = ~np.isnan(y)
    t, y = t[geldig], y[geldig]
    grenzen = np.asarray(grenzen_s, dtype="float64")
    uit = np.full(len(grenzen), np.nan)
    gedekt = np.zeros(len(grenzen), dtype=bool)
    if len(t) < 2:
        return uit, gedekt

    rechts = np.searchsorted(t, grenzen, side="left")  # eerste meting op of na de grens
    heeft_rechts = rechts < len(t)
    i1 = np.minimum(rechts, len(t) - 1)
    # De meting op of vóór de grens: de rechter zelf als die precies op de grens ligt.
    precies = heeft_rechts & (t[i1] == grenzen)
    i0 = np.clip(np.where(precies, rechts, rechts - 1), 0, len(t) - 1)
    heeft_beide = heeft_rechts & (precies | (rechts >= 1))
    afstand = t[i1] - t[i0]
    ok = heeft_beide & (afstand < max_gat_s)
    # Op een grens die precies op een meting valt, is de afstand 0: neem de gemeten stand.
    gelijk = ok & (afstand == 0)
    teller = ok & ~gelijk
    uit[gelijk] = y[i0[gelijk]]
    frac = (grenzen[teller] - t[i0[teller]]) / afstand[teller]
    uit[teller] = y[i0[teller]] + frac * (y[i1[teller]] - y[i0[teller]])
    gedekt[ok] = True
    return uit, gedekt


def vermogen_uit_stand(stand_op_grens: np.ndarray, gedekt: np.ndarray, factor_naar_w: float
                       ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Gemiddeld vermogen per interval uit de standen op de grenzen: ``Δstand * factor / STAP_S``.

    ``factor_naar_w`` zet een eenheid van de teller om in joule (3,6e6 voor kWh, 1e9 voor GJ).
    Geeft ``(vermogen_W, interval_gedekt, teller_daalt)``. Een interval is gedekt als beide
    grenzen gedekt zijn; daalt de teller, dan is het vermogen ``NaN`` en ``teller_daalt`` waar.
    """
    delta = np.diff(stand_op_grens)
    interval_gedekt = gedekt[:-1] & gedekt[1:]
    daalt = interval_gedekt & (delta < 0)
    vermogen = np.where(interval_gedekt & ~daalt, delta * factor_naar_w / STAP_S, np.nan)
    return vermogen, interval_gedekt, daalt


def steekproef_laatste_binnen(t_s: np.ndarray, grenzen_s: np.ndarray) -> np.ndarray:
    """Per interval ``[grens_i, grens_i+1)`` de index van de **laatste meting binnen het interval**,
    of ``-1`` als er geen is. Geen middeling: het is een steekproef (ontwerp §4.4)."""
    t = np.asarray(t_s, dtype="float64")
    grenzen = np.asarray(grenzen_s, dtype="float64")
    idx = np.searchsorted(t, grenzen[1:], side="left") - 1  # laatste meting strikt vóór het einde
    geldig = (idx >= 0) & (t[np.clip(idx, 0, max(len(t) - 1, 0))] >= grenzen[:-1]) if len(t) else np.zeros(len(idx), bool)
    return np.where(geldig, idx, -1)
