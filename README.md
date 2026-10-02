# wattopia-dataset-preprocessing

Van de ruwe monitoringdata **Woningprestaties** (Wattopia, Out of Harm's Way en RVO, 2022) naar
getypeerde, herleidbare Parquet-tabellen. De preprocessing staat op zichzelf: wat hier uit komt is
bruikbaar voor iedereen die met deze dataset werkt, ongeacht welke analyse erop volgt. Bij Milieu
Centraal is dat een simulatiemodel dat de tabellen afneemt, maar deze repo veronderstelt dat niet.

> **Lees eerst [`GEBRUIKSVOORWAARDEN.md`](GEBRUIKSVOORWAARDEN.md).** De dataset mag alleen worden
> gebruikt voor onderzoek naar de energetische prestaties van woningen, mag niet worden doorgestuurd
> (aanvragen via KITE), en een dataleverancier kan zijn toestemming intrekken.

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

## Stand

Alleen het **juridisch kader** en de opzet staan er. Er is nog geen pijplijn; het ontwerp daarvan
volgt in `ontwerp-preprocessing.md`, naar het model van de andere preprocessing-repo's voor
KITE-datasets: ruw, gestandaardiseerd, afgeleid, met een kwaliteitsrapport, een datacatalogus en een
`datapackage.json`.

Eerste vragen voor het ontwerp:

1. **Tijdstempels** in de detaildata zijn Unix-seconden met een paar seconden spreiding per
   meetpunt (bijvoorbeeld `1546297478`, `1546297480`). Uitlijnen op een vast raster van vijf minuten
   is een keuze die vastgelegd moet worden.
2. **Tellers en vermogens** staan naast elkaar (`power` en `total_energy_in`). Welke van de twee is
   de bron van een gemiddeld vermogen per interval?
3. **Formules in de werkbladen** (het tabblad *summary* bevat Excel-formules): die horen niet in de
   uitvoer; alleen de meetwaarden.
4. **De jaartotalen** hebben een kopregel over twee rijen (groepsnaam en kolomnaam).

## Beginnen

```
pip install -e ".[dev]"
pytest -q
```

Zet het pakket uitgepakt in `data/raw/` (zie [`GEBRUIKSVOORWAARDEN.md`](GEBRUIKSVOORWAARDEN.md) voor
waar je het aanvraagt).

## Documenten

| document | waarover |
|---|---|
| [`GEBRUIKSVOORWAARDEN.md`](GEBRUIKSVOORWAARDEN.md) | de afspraken met de dataleveranciers, intrekking, bronvermelding, en hoe je de dataset verkrijgt |
| [`LICENSE.md`](LICENSE.md) | de licentie van de **code** (nog te besluiten) |
| [`CLAUDE.md`](CLAUDE.md) | werkafspraken voor deze repo |
