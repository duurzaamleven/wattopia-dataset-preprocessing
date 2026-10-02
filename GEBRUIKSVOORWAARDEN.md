# Gebruiksvoorwaarden van de Wattopia-dataset

Deze repository verwerkt de dataset **Woningprestaties: monitoringdata van bestaande woningen**,
verzameld door Wattopia en Out of Harm's Way in opdracht van RVO, en verspreid via het KITE-portaal
van RVO onder de titel *Monitoringdata Energieprestaties Wattopia*. De ruwe dataset staat **niet** in
deze git-repo (`data/` is gitignored) en wordt niet door of via deze repo verspreid.

## Wat de dataset zelf zegt

### Uit het codeboek (`Codeboek 2022-07-22.pdf`, auteur Marten Witkamp)

> *"Met de dataleveranciers is het volgende afgesproken, waar gebruikers van de data zich aan
> dienen te houden:*
>
> *Wat gebeurt er met de gegevens die verzameld worden?*
> *De gegevens worden gebruikt voor onderzoek naar de energetische (en waar mogelijk ook andere)
> prestaties van woningen.*
>
> *Wat wordt niet gedaan met de gegevens die verzameld worden?*
> *De gegevens worden niet gemanipuleerd.*
> *De gegevens worden niet verkocht aan derden.*
> *De gegevens worden niet zonder aanvullende toestemming gebruikt voor andere doelstellingen."*

> *"Recht op intrekken toestemming. Door gegevens op te sturen, gaan partijen akkoord met het
> hierboven beschreven gebruik. Indien partijen daar op een later tijdstip anders over denken, kan
> dat akkoord worden ingetrokken. De betreffende gegevens kunnen dan niet uit al gepubliceerd
> onderzoek worden verwijderd. Toekomstig gebruik van de gegevens wordt hiermee echter wel
> voorkomen. RVO houdt om die reden bij welke partijen de dataset opvragen, om hen te kunnen
> informeren over eventuele intrekkingen van toestemming."*

**Bronvermelding**, zoals het codeboek die voorschrijft:

> RVO, Wattopia, Out of Harm's Way, "Woningprestaties - Monitoringdata van bestaande woningen",
> 2022, opvraagbaar via info@woningprestaties.nl

### Uit `Instructies over delen met anderen v2.txt`

> *"Gelieve deze dataset niet zelf door te sturen naar anderen. Iedereen die deze dataset graag wil
> hebben, kan die aanvragen via KITE. De reden hiervoor is dat we graag met gebruikers willen kunnen
> communiceren over eventuele updates en verbeteringen van de dataset."*

### Van de KITE-pagina *Monitoringdata Energieprestaties Wattopia*

Gelezen op 02-10-2026 (de pagina vraagt een inlog bij Kennisdelen RVO; een kopie staat lokaal in
`data/raw/`). Onder **Licentie**:

> *"Openbare data, te gebruiken onder voorwaarde van **vermelding van het doel/gebruik van de data
> aan Wattopia** (zie contact). Check voor de volledigheid ook de gebruiksvoorwaarden in de
> instructies (onderdeel van het datapakket in de download)."*

Verder op die pagina: auteurs Marten Witkamp en Harmke Bekkema, versie juli 2022, contact
marten@wattopia.nl, en een downloadlink `https://wattopia.nl/download/RVO_Woningprestaties_Datapakketje_2022.zip`.
De pagina zegt ook dat er **geen werk is besteed aan het opschonen of analyseren** van de data, dat
het pakket destijds naar 78 mensen is gestuurd, en dat de feedback vooral de vijfminutendata van de
twee voorbeeldwoningen nuttig vond, met de kanttekening dat daar meer metadata bij zou moeten.

### Hoe die drie zich tot elkaar verhouden

- **Meldplicht.** Het doel en het gebruik moeten aan Wattopia worden gemeld. Dat staat alleen op de
  KITE-pagina, niet in het pakket.
- **"Openbare data" en "niet doorsturen".** De KITE-pagina noemt de set openbaar, met een openbare
  downloadlink; de instructie in het pakket vraagt hem niet zelf door te sturen. Die twee zijn te
  verenigen: de set is voor iedereen te halen, maar via de bron, zodat Wattopia en RVO weten wie hem
  gebruikt en bij een intrekking iedereen kunnen bereiken. Deze repo verspreidt hem dus niet.
- **Doelbinding en intrekking** uit het codeboek blijven gelden.

## Wat dit betekent voor deze repo

1. **De ruwe data en alle afgeleide tabellen per woning blijven lokaal.** Ze staan in `data/`, en
   die map gaat nooit in git. Wie de dataset wil gebruiken, vraagt hem aan via KITE.
2. **Doelbinding.** De verwerking dient onderzoek naar de energetische prestaties van woningen.
   Een ander doel vraagt aanvullende toestemming van de dataleveranciers (via Wattopia of RVO).
3. **"Niet gemanipuleerd".** Omzetten naar een ander formaat, eenheden harmoniseren en
   kwaliteitsvlaggen toevoegen veranderen de meetwaarden niet. Waarden worden nooit stil vervangen
   of verwijderd; een correctie of uitsluiting is altijd een **vlag naast** de oorspronkelijke
   waarde, met de regel erbij. Zo blijft de oorspronkelijke waarde altijd terug te vinden.
4. **Intrekking.** Een dataleverancier kan zijn toestemming intrekken. De pijplijn moet daarom
   opnieuw te draaien zijn op een nieuwere versie van de dataset, en geen projecten of woningen
   bewaren die daar niet meer in staan.
5. **Herleidbaarheid.** Het codeboek beschrijft hoe de data is geanonimiseerd (willekeurige codes,
   afgeronde bouwjaren en oppervlakken, verhulde projectgrootte, willekeurige volgorde). Deze repo
   koppelt geen gegevens die die anonimisering ongedaan kunnen maken, zoals kaart- of adresgegevens.
6. **Melden vóór gebruik.** Wie de dataset gebruikt, meldt het doel en het gebruik aan Wattopia
   (marten@wattopia.nl). Een analyse die op deze uitvoer draait, doet dat ook.
7. **Publiceren van uitkomsten** (aggregaten, conclusies) mag binnen het doel, met de
   bronvermelding hierboven.

## Hoe je de dataset verkrijgt

Via het KITE-portaal van RVO, pagina *Monitoringdata Energieprestaties Wattopia*, die doorlinkt naar
`https://wattopia.nl/download/RVO_Woningprestaties_Datapakketje_2022.zip`. Het pakket hoort na het
uitpakken in `data/raw/`. Meld daarbij het doel aan Wattopia (zie boven).
