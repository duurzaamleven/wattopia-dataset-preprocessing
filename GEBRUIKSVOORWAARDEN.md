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

De KITE-pagina zelf was bij het opzetten van deze repo niet zonder inlog te lezen; of daar
aanvullende voorwaarden staan (zoals een meldplicht of een licentie), is **nog niet nagekeken**.

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
6. **Publiceren van uitkomsten** (aggregaten, conclusies) mag binnen het doel, met de
   bronvermelding hierboven. Of er een meldplicht is zoals bij andere KITE-datasets, staat nog open
   (zie boven).

## Hoe je de dataset verkrijgt

Aanvragen via het KITE-portaal van RVO, pagina *Monitoringdata Energieprestaties Wattopia*. Het
pakket heet `RVO_Woningprestaties_Datapakketje_2022.zip` en hoort na het uitpakken in `data/raw/`.
