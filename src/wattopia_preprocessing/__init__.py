# SPDX-License-Identifier: EUPL-1.2
"""Preprocessing van de Wattopia-dataset Woningprestaties (Wattopia, Out of Harm's Way en RVO, 2022).

Nog geen pijplijn; zie README.md voor de stand en de eerste ontwerpvragen.
"""

from pathlib import Path

#: Waar het uitgepakte pakket hoort te staan (gitignored, zie GEBRUIKSVOORWAARDEN.md).
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

#: De bestanden die het pakket van 22 juli 2022 bevat.
VERWACHTE_BESTANDEN = (
    "Woningprestaties 2022-07-22 ANON.xlsx",
    "Codeboek 2022-07-22.pdf",
    "Detaildata woning_arnpivgi.xlsx",
    "Detaildata woning_mkpiieku.xlsx",
    "Instructies over delen met anderen v2.txt",
    "Presentatie RVO Voorbeeldprojecten 2022 incl verslag.pdf",
)


def ontbrekende_bestanden(raw_dir: Path = RAW_DIR) -> list[str]:
    """Welke verwachte bestanden er niet in `raw_dir` staan; leeg als het pakket compleet is."""
    return [naam for naam in VERWACHTE_BESTANDEN if not (Path(raw_dir) / naam).exists()]
