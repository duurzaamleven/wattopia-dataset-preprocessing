# Werkafspraken voor deze repo

Preprocessing van de monitoringdata **Woningprestaties** (Wattopia, Out of Harm's Way en RVO): van
het ruwe pakket (jaartotalen van 898 woningen en tijdreeksen van twee woningen, in Excel) naar
getypeerde, herleidbare Parquet-tabellen, met een kwaliteitsrapport. Het is **geen analyse**; hier
wordt niets geconcludeerd over de prestaties van woningen of installaties.

Begin met [`README.md`](README.md) en [`GEBRUIKSVOORWAARDEN.md`](GEBRUIKSVOORWAARDEN.md).

## Draaien

```bash
pip install -e ".[dev]"
pytest -q
```

## Zes dingen die niet ter discussie staan

1. **Nederlands.** README's, commentaar, docstrings en variabelenamen. Geen em dash; gebruik een
   puntkomma, punt of komma.
2. **`physiquant__unit`-naamgeving.** De eenheid staat in de naam na een dubbele underscore
   (`temp_aanvoer__degC`). `_cum` betekent een meterstand op een moment; zonder `_cum` is het een
   gemiddelde over het interval. Conventie: <https://github.com/energietransitie/physiquant__unit>.
3. **Deze repo staat op zichzelf.** Hij kan gedeeld of publiek worden en moet bruikbaar zijn voor
   iedereen die met deze dataset werkt. Verwijs dus **niet** naar de afnemende repo van Milieu
   Centraal, niet bij naam en niet met een link; schrijf "de afnemende repo" of "de afnemende
   simulatie".
4. **De ruwe data blijft buiten git.** `data/` is gitignored, en de dataset mag niet worden
   doorgestuurd. Zie [`GEBRUIKSVOORWAARDEN.md`](GEBRUIKSVOORWAARDEN.md) vóór je iets publiceert of
   deelt.
5. **Niets stil vervangen of weggooien.** De dataleveranciers hebben afgesproken dat de gegevens
   "niet gemanipuleerd" worden. Een correctie of uitsluiting is daarom altijd een vlag naast de
   oorspronkelijke waarde, met de regel erbij.
6. **Getallen zonder herkomst zijn schuld.** Neem je een waarde over, leg dan vast wélke bron, welke
   versie en welk peiljaar, niet alleen het getal.

## Schrijf voor iemand die er nog niet was

Een datum hoort in de tekst als hij **iets vastlegt**: wanneer een meting is gedaan, wanneer een
bron is opgehaald. Hij hoort er **niet** in als hij nieuws meldt. Zeg wat er **is**; wat er wás
staat in de git-geschiedenis.

## Commits

Nederlandstalige commitboodschappen die uitleggen **waarom**, niet alleen wat. Eén onderwerp per
commit.
