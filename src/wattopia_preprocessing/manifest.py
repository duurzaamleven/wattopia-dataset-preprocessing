"""Hervatbaarheid: ``_manifest.jsonl``, atomisch schrijven en de contractversie.

Het inlezen van de twee detailwerkboeken met ``openpyxl`` duurt tientallen minuten; de rest van de
pijplijn is een kwestie van een minuut of twee. Daarom twee manifesten met hetzelfde mechanisme:

- ``data/interim/_manifest.jsonl``: per detailwerkboek de sha256 van het **bronbestand**. Is die bij
  een volgende run gelijk, en staan de tussenbestanden er nog, dan wordt het werkboek niet opnieuw
  gelezen (:meth:`Manifest.is_voltooid` met ``bron_sha256``).
- ``data/processed/_manifest.jsonl``: per uitvoertabel pad, sha256, rijen en contractversie.

Elke tabel wordt eerst naar ``<pad>.tmp`` geschreven en pas daarna atomisch hernoemd
(:func:`schrijf_parquet_atomisch`). Pas ná die hernoeming volgt de manifestregel.

``UITVOER_CONTRACT_VERSIE`` hoort omhoog bij elke wijziging aan de vorm of betekenis van de
uitvoer: kolomnamen, eenheden, tijdzone, vlagregels. ``INTERIM_VERSIE`` hoort omhoog bij een
wijziging aan de manier waarop een werkboek wordt ingelezen; dan worden de werkboeken opnieuw gelezen.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

log = logging.getLogger(__name__)

#: Versie van het uitvoercontract.
UITVOER_CONTRACT_VERSIE = "2026-10-02-eerste-pijplijn"

#: Versie van de tussenstap (het inlezen van de werkboeken).
INTERIM_VERSIE = "1"

MANIFEST_BESTANDSNAAM = "_manifest.jsonl"


@dataclass
class ManifestRegel:
    onderdeel: str
    sleutel: str
    pad: str
    sha256: str
    rijen: int
    contract: str = UITVOER_CONTRACT_VERSIE
    #: sha256 van het bronbestand waaruit dit onderdeel is opgebouwd (alleen voor de tussenstap)
    bron_sha256: str = ""
    voltooid_op: str = ""

    def __post_init__(self) -> None:
        if not self.voltooid_op:
            self.voltooid_op = datetime.now(timezone.utc).isoformat()


def sha256_van_bestand(pad: Path, leesblok: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with Path(pad).open("rb") as f:
        while True:
            blok = f.read(leesblok)
            if not blok:
                break
            h.update(blok)
    return h.hexdigest()


def schrijf_parquet_atomisch(pad: Path, df: pd.DataFrame, compressie: str = "zstd") -> None:
    """Schrijf ``df`` naar ``pad`` via ``<pad>.tmp`` en hernoem daarna."""
    pad = Path(pad)
    pad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pad.with_suffix(pad.suffix + ".tmp")
    df.to_parquet(tmp, index=False, compression=compressie)
    tmp.replace(pad)


def schrijf_arrow_atomisch(pad: Path, tabel: pa.Table, compressie: str = "zstd") -> None:
    """Als :func:`schrijf_parquet_atomisch`, voor een ``pyarrow.Table`` met een expliciet schema, zodat
    elk Parquet-type (met name de tz-aware tijdkolommen) precies het gedeclareerde schema volgt."""
    pad = Path(pad)
    pad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pad.with_suffix(pad.suffix + ".tmp")
    pq.write_table(tabel, tmp, compression=compressie)
    tmp.replace(pad)


def schrijf_tekst_atomisch(pad: Path, tekst: str) -> None:
    pad = Path(pad)
    pad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pad.with_suffix(pad.suffix + ".tmp")
    tmp.write_text(tekst, encoding="utf-8", newline="\n")
    tmp.replace(pad)


class Manifest:
    """Lees- en schrijftoegang tot ``<map>/_manifest.jsonl``."""

    def __init__(self, map_: Path, contract: str = UITVOER_CONTRACT_VERSIE):
        self.map = Path(map_)
        self.pad = self.map / MANIFEST_BESTANDSNAAM
        self.contract = contract
        self._regels: dict[tuple[str, str], ManifestRegel] = {}
        self._laad()

    def _laad(self) -> None:
        if not self.pad.is_file():
            return
        with self.pad.open(encoding="utf-8") as f:
            for regel in f:
                regel = regel.strip()
                if not regel:
                    continue
                try:
                    post = json.loads(regel)
                    self._regels[(post["onderdeel"], post["sleutel"])] = ManifestRegel(**post)
                except (json.JSONDecodeError, KeyError, TypeError):
                    log.warning("Onvolledige of onbekende manifestregel overgeslagen in %s", self.pad)

    def regel(self, onderdeel: str, sleutel: str) -> ManifestRegel | None:
        return self._regels.get((onderdeel, sleutel))

    def is_voltooid(self, onderdeel: str, sleutel: str, bron_sha256: str | None = None) -> bool:
        """True als het manifest dit onderdeel als af beschouwt, met de huidige contractversie, het
        bestand nog bestaat en (als opgegeven) de bron dezelfde sha256 heeft."""
        regel = self._regels.get((onderdeel, sleutel))
        if regel is None or regel.contract != self.contract:
            return False
        if bron_sha256 is not None and regel.bron_sha256 != bron_sha256:
            return False
        return (self.map / regel.pad).is_file()

    def voeg_toe(self, onderdeel: str, sleutel: str, pad: Path, rijen: int,
                 bron_sha256: str = "") -> ManifestRegel:
        regel = ManifestRegel(
            onderdeel=onderdeel, sleutel=sleutel,
            pad=Path(pad).relative_to(self.map).as_posix(),
            sha256=sha256_van_bestand(pad), rijen=rijen,
            contract=self.contract, bron_sha256=bron_sha256,
        )
        self._regels[(onderdeel, sleutel)] = regel
        self.pad.parent.mkdir(parents=True, exist_ok=True)
        with self.pad.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(regel), ensure_ascii=False) + "\n")
        return regel

    def sleutels(self, onderdeel: str) -> set[str]:
        return {s for (o, s) in self._regels if o == onderdeel}
