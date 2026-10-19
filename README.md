# wattopia-dataset-preprocessing

Van de ruwe monitoringdata **Woningprestaties** (Wattopia, Out of Harm's Way en RVO, 2022) naar
getypeerde, herleidbare Parquet-tabellen. De preprocessing staat op zichzelf: wat hier uit komt is
bruikbaar voor iedereen die met deze dataset werkt, ongeacht welke analyse erop volgt. Bij Kenniscentrum Duurzaam
Leven is dat een simulatiemodel dat de tabellen afneemt, maar deze repo veronderstelt dat niet.

> **Lees eerst [`GEBRUIKSVOORWAARDEN.md`](GEBRUIKSVOORWAARDEN.md).** De dataset is openbaar te halen,
> maar het doel en het gebruik moeten aan Wattopia worden gemeld; hij mag alleen worden gebruikt
> voor onderzoek naar de energetische prestaties van woningen, niet zelf worden doorgestuurd, en een
> dataleverancier kan zijn toestemming intrekken.

## Wat dit is

Woningen die in de periode 2019 tot 2022 zijn gerenoveerd naar of richting aardgasvrij, met
monitoringdata die woningcorporaties, bouwbedrijven en monitoringleveranciers om niet hebben gedeeld.
Het pakket (`RVO_Woningprestaties_Datapakketje_2022.zip`, codeboek van 22 juli 2022) bevat:

| bestand | inhoud |
|---|---|
| `Woningprestaties 2022-07-22 ANON.xlsx` | **jaartotalen**: tabblad *Projectdata* (24 projecten: typologie, schil, installaties) en *Monitoringdata* (898 woningen: opwek, elektriciteit en warmte voor ruimteverwarming en tapwater, overig gebouwgebonden, persoonlijk gebruik, binnenklimaat, gas- en elektriciteitsverbruik vóór renovatie) |
| `Detaildata woning_arnpivgi.xlsx`, `Detaildata woning_mkpiieku.xlsx` | **tijdreeksen van twee woningen**, per vijf minuten, per meetpunt een tabblad: warmtepomp, booster, element in het vat, slimme meter, zonnepanelen, ventilatie, thermostaat, CO₂, aanvoer en retour |
| `Codeboek 2022-07-22.pdf` | definities per variabele, anonimisering, datakwaliteit, uitsluitingscriteria en de afspraken over gebruik |
| `Presentatie RVO Voorbeeldprojecten 2022 incl verslag.pdf` | presentatie en verslag van de projecten |
| `Instructies over delen met anderen v2.txt` | het verzoek de dataset niet door te sturen |

Elke woning heeft minstens één aaneengesloten jaar monitoring (meestal een kalenderjaar). Volgens
het codeboek is niet na te gaan of warmtemetingen in- of exclusief stilstandsverliezen zijn
opgegeven, en is de kwaliteit van de meters onbekend.

**Tijd.** Elke tijdkolom in de uitvoer is tz-aware `Europe/Amsterdam`; intern wordt in UTC
gerekend, en intervallen zijn begin-gelabeld. De bron is Unix-tijd, en dat die werkelijk UTC is (en
niet de lokale kloktijd), is op de data gecontroleerd: de zon staat het hele jaar op hetzelfde
UTC-tijdstip hoog, en rond de zomertijdwissels ontbreekt of verdubbelt geen uur (ontwerp §9.6).

## Stand

De pijplijn bestaat en draait op het volledige pakket. Het ontwerp staat in
[`ontwerp-preprocessing.md`](ontwerp-preprocessing.md); wat de echte data anders liet zien dan het ontwerp
aannam, staat in sectie 9 daarvan.

**Wat eruit komt** (in `data/processed/`, gitignored, Parquet met zstd):

| tabel | rijen | inhoud |
|---|---:|---|
| `projecten` | 24 | typologie, schil en installaties per project |
| `woningen_jaar` | 898 | jaartotalen per woning, met vlaggen |
| `detail_ruw/<meetpunt>.parquet` | 104.000 tot 208.000 | per tabblad een getrouwe, getypeerde kopie voor beide detailwoningen |
| `detail_5min` | 210.240 | twee woningen op een raster van vijf minuten over 2019 |
| `detail_kwartier` | 70.080 | idem per kwartier |
| `controle_jaartotalen` | 24 | de jaartotalen uit de detaildata tegenover die uit de jaartotalen |

Daarnaast schrijft de pijplijn `docs/data-quality.md` (vulgraad, vlaggen, gaten, dekking en de zelfcontrole,
alleen aggregaten), `docs/datacatalogus.md` en `datapackage.json` (Frictionless). Alles komt uit dezelfde
kolomdefinities in `src/wattopia_preprocessing/kolommen.py`.

**Draaien.** `python -m wattopia_preprocessing [--raw data/raw] [--uit data/processed]`. De eerste run leest de
twee detailwerkboeken met `openpyxl` en dat duurt lang (orde van een uur voor beide); de bladen gaan naar
`data/interim/`. Elke volgende run slaat een werkboek over zolang de sha256 van het bronbestand gelijk is
aan die in `data/interim/_manifest.jsonl`, en is in een paar minuten klaar. `--opnieuw-lezen` dwingt het
inlezen af. De run faalt als de zelfcontrole tegen de jaartotalen buiten de tolerantie van 0,5 % valt.

**Wat de zelfcontrole zegt.** De eindstand min de beginstand van de tellers valt op alle gecontroleerde
posten van beide woningen op 0,000 % van het jaartotaal. De som over de intervallen van vijf minuten blijft
daaronder, omdat er niet over gaten van meer dan 15 minuten wordt geïnterpoleerd; wie over het raster
sommeert, mist de energie in die gaten (zie `docs/data-quality.md` en ontwerp §9.1).

**Wat nog openstaat.**

- De eenheid van `volume_out`, de debieten van de ventilatie en `voc` is onbekend en staat zo in de namen
  (`__onbekend`); de betekenis van de codes van de fabrikant (`op_mode`, `system_status`, `error_code`) ook.
- De tekenconventie van `solar.power` en `smartMeter.power` is overgenomen, niet omgedraaid.
- Geen koppeling met weerdata en geen afleiding van tapwaterwarmte, COP of SCOP; dat is werk voor de afnemer.

## Beginnen

```
pip install -e ".[dev]"
pytest -q                  # synthetische invoer; de toets op de echte data staat standaard uit
pytest -m echte_data       # idem op data/raw/ en data/processed/ (traag als die nog niet bestaat)
```

Zet het pakket uitgepakt in `data/raw/`. Waar je het haalt en wat je moet melden, staat in
[`GEBRUIKSVOORWAARDEN.md`](GEBRUIKSVOORWAARDEN.md).

## Documenten

| document | waarover |
|---|---|
| [`ontwerp-preprocessing.md`](ontwerp-preprocessing.md) | het ontwerp van de pijplijn, met in §9 de afwijkingen bij de implementatie |
| [`docs/data-quality.md`](docs/data-quality.md) | vulgraad, vlaggen, gaten, dekking en zelfcontrole van de laatste run |
| [`docs/datacatalogus.md`](docs/datacatalogus.md) | elke tabel en kolom, met type, bron en beschrijving |
| [`GEBRUIKSVOORWAARDEN.md`](GEBRUIKSVOORWAARDEN.md) | de afspraken met de dataleveranciers, intrekking, bronvermelding, en hoe je de dataset verkrijgt |
| [`LICENSE`](LICENSE) | de licentie van de **code**: `EUPL-1.2` |
| [`CLAUDE.md`](CLAUDE.md) | werkafspraken voor deze repo |

## Licentie

De **code** in deze repository valt onder de European Union Public Licence 1.2 (`EUPL-1.2`), zie
[`LICENSE`](LICENSE). Kenniscentrum Duurzaam Leven heeft daartoe op 19-10-2026 besloten.

Copyright © 2026 Kenniscentrum Duurzaam Leven, Stichting Milieu Centraal

De licentie gaat over de code, niet over de data. De ruwe dataset staat niet in deze repository en
wordt er ook niet via verspreid. Voor de data, en voor alles wat per woning uit de data volgt, gelden
de afspraken met de dataleveranciers: alleen voor onderzoek naar de energetische prestaties van
woningen, niet doorsturen, niet manipuleren, niet verkopen, en een recht op intrekken van
toestemming. Het doel en het gebruik meld je aan Wattopia. Zie
[`GEBRUIKSVOORWAARDEN.md`](GEBRUIKSVOORWAARDEN.md).
