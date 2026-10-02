# Ontwerp: preprocessing van de Wattopia-dataset Woningprestaties

Wat deze pijplijn doet: het pakket van 22 juli 2022 (één werkboek met jaartotalen, twee werkboeken
met tijdreeksen) naar getypeerde, herleidbare Parquet-tabellen, met de kolomvertaling, de
tijdbehandeling, de eenheden en de aannames die daarbij horen. **Dit is geen analyse.** Er wordt
niets geconcludeerd over de prestaties van woningen of installaties.

De afspraken met de dataleveranciers bepalen twee ontwerpregels (zie
[`GEBRUIKSVOORWAARDEN.md`](GEBRUIKSVOORWAARDEN.md)): **niets stil vervangen of weggooien** ("de gegevens
worden niet gemanipuleerd"), en **opnieuw te draaien op een nieuwere versie** (een leverancier kan zijn
toestemming intrekken).

## 1. De brondata, zoals ze werkelijk zijn

Alles hieronder is nagekeken in de bestanden zelf, niet overgenomen uit het codeboek.

### 1.1 `Woningprestaties 2022-07-22 ANON.xlsx`: jaartotalen

Drie tabbladen.

- **`Projectdata`**: 24 projecten, 29 kolommen. **Drie kopregels**: rij 1 de groep
  (`PROJECTIDENTIFICATIE`, `ALGEMENE GEGEVENS`, `SCHIL`, `INSTALLATIES`), rij 2 de kolomnaam, rij 3 het
  type of de eenheid (`aantal`, `keuze`, `ja/nee`, `tekst`). Data vanaf rij 4.
- **`Monitoringdata`**: **898 woningen**, 22 kolommen, ook drie kopregels; rij 3 is hier de eenheid
  (`kWh_e / jaar`, `GJ / jaar`, `ppm`, `percentage`, `m3 / jaar`, `graden C`, `hoek / tussen`). Geen
  dubbele woningcodes; elke projectcode staat ook in `Projectdata`. Jaartal monitoring: 466 woningen
  2019, 432 woningen 2020. Woningen per project van 1 tot 129 (mediaan 15,5).
- **`keuzemenu`**: de toegestane waarden per keuzekolom. Dient als validatielijst.

Vulgraad is zeer ongelijk. Van de 898 woningen hebben er 898 een opwek en een totaal van de
warmteopwekker, maar 54 een aparte meting voor ruimteverwarming en tapwater, 510 geleverde warmte
voor ruimteverwarming, 30 een verbruik vóór renovatie, 112 een woonkamertemperatuur. Lege cellen zijn
"niet gerapporteerd", geen nul.

Opvallende waarden die als vlag gevonden moeten worden, niet gecorrigeerd:

- geleverde warmte voor tapwater **−0,000189 GJ** (één woning);
- setpoint woonkamer **0 °C**;
- *Beschikbaar voor persoonlijk gebruik* negatief tot −4.250 kWh (kan kloppen: meer verbruik dan opwek);
- *Gebruikte energie voor overige gebouwgebonden functies* tot 9.050 kWh (onwaarschijnlijk hoog).

### 1.2 `Detaildata woning_arnpivgi.xlsx` en `Detaildata woning_mkpiieku.xlsx`: tijdreeksen

Twee woningen uit project `MNGDU2HNKK`, **beide ook aanwezig in de jaartotalen** als `W_arnpivgi` en
`W_mkpiieku` (jaar 2019). Per meetpunt een tabblad, met een kolom `Timestamp` en een tot zestien
waardenkolommen. Het eerste tabblad, `summary`, is een rekenblad van Wattopia met Excel-formules en
geen meetdata.

| tabblad | kolommen (naast `Timestamp`) | woning 1 | woning 2 |
|---|---|---|---|
| `HeatPump` | `booster_status`, `dhw_prohibit`, `error_code` (tekst), `firmware_version`, `flow_temp`, `force_dhw`, `heating_prohibit`, `holiday`, `op_mode`, `outdoor_temp`, `return_temp`, `room_target_temp`, `room_temp`, `system_status`, `target_temp`, `temp` | 104.252 rijen | 103.980 |
| `energyHeatpump` | `power`, `total_energy_in` | 104.243 | 103.982 |
| `energyBooster` | `power`, `total_energy_in` | 104.243 | 103.980 |
| `energyImmersion` | `power`, `total_energy_in` | overal 0 | overal 0 |
| `energyWtwReg` | `power`, `total_energy_in` | 104.243 | 103.982 |
| `solar` | `power`, `total_energy_in`, `total_energy_out` | 104.243 | 103.997 |
| `smartMeter` | `energy_in_low`, `energy_in_norm`, `energy_out_low`, `energy_out_norm`, `power`, `total_energy_in`, `total_energy_out` | vanaf 1 april | vanaf 8 augustus |
| `flowHeatSpaceHeating` | `flow_temp`, `return_temp`, `total_energyGJ`, `volume_out` | 104.149 | vanaf 1 februari |
| `waterFlow` | `ambient_temp`, `min_flow_temp`, `volume_out` | 104.130 | 103.866 |
| `ventilation` | `error_code`, `exhaust_flow`, `filter`, `outdoor_temp`, `room_temp`, `supply_flow` | 104.255 | **leeg** |
| `co2sensor` | `co2`, `humidity`, `temp`, `voc` | 104.242 | 103.983 |
| `thermostat` | `temp` | 103.412 | tot 29 oktober |
| `relay1`, `relay2`, `relay24v`, `immersion` | `status` | overal 0 | overal 0, deels tot 29 oktober |
| `sheet15`, `air_sensor_*` (4), `virtualVentilation` | | leeg | leeg |

**Tijd.** `Timestamp` is Unix-tijd in seconden (UTC). De reeksen lopen van 2018-12-31 23:04 tot
2019-12-31 23:00 UTC, dus het **kalenderjaar 2019 in lokale tijd**. De stap is in de mediaan 300 s,
met spreiding (p1 tot p99: 280 tot 320 s) en per meetpunt een eigen fase: de tijdstempels liggen
ongeveer 260 tot 285 s na een veelvoud van 300 s, behalve bij de slimme meter (0 tot 1 s). Gaten tot
ongeveer 3,8 dagen; per meetpunt 10 tot 66 stappen van meer dan 10 minuten. Geen dubbele tijdstempels.

**Eenheden.** Het codeboek licht de detaildata niet toe ("niet bewerkt en wordt hier ook niet nader
toegelicht"). De eenheden zijn daarom **afgeleid en vervolgens getoetst tegen de jaartotalen**, en dat
sluit tot op een paar honderdste procent:

| grootheid | afgeleid uit | woning 1 | jaartotaal | woning 2 | jaartotaal |
|---|---|---:|---:|---:|---:|
| totaal warmteopwekker | Δ `energyHeatpump.total_energy_in` + Δ `energyBooster.total_energy_in` | 1.428,7 + 79,8 = 1.508,5 kWh | 1.508,67 | 2.313 + 76,6 = 2.389,6 kWh | 2.390,17 |
| geleverde warmte ruimteverwarming | Δ `flowHeatSpaceHeating.total_energyGJ` | 14,12 GJ | 14,115 | 15,97 GJ | 15,971 |
| opgewekte energie | Δ `solar.total_energy_out` | 8.119 kWh | 8.119,23 | 7.218 kWh | 7.221,11 |
| overige gebouwgebonden | Δ `energyWtwReg.total_energy_in` | 269,35 kWh | 269,35 | 224,0 kWh | 224,05 |

Daarmee staat vast: tellers `total_energy_*` en `energy_*` in **kWh**, `total_energyGJ` in **GJ**,
`power` in **W** (het gemiddelde van `power` en de afgeleide van de teller verschillen minder dan 1 %).
"Totaal gebruikte energie door de warmteopwekker" is **warmtepomp plus booster**; de booster is het
elektrische bijverwarmingselement (`booster_status` 0 of 1, `power` tot ongeveer 2 kW).

Nog **onzeker** en dus als aanname te labelen:

- `solar.power` is negatief bij opwek (minimum ongeveer −7,5 kW) en `smartMeter.power` positief bij
  afname en negatief bij teruglevering. Tekenconventie per meetpunt vastleggen, niet omdraaien.
- `volume_out` in `waterFlow` loopt in een jaar maar van 1,2 naar 4,3 (woning 1); als dat m³ tapwater
  is, is het onwaarschijnlijk weinig. **Eenheid onbekend**, zo opnemen.
- `volume_out` in `flowHeatSpaceHeating` (716 naar 2.754): vermoedelijk m³ circulatiewater. Onzeker.
- `op_mode`, `system_status`, `error_code`: codes van de fabrikant, betekenis onbekend.
- Sentinelwaarden: `thermostat.temp` tot −100 en −20 °C, `HeatPump.room_temp` en `room_target_temp`
  0 °C, `flowHeatSpaceHeating.flow_temp` tot 192 °C. Vlaggen, niet weghalen.

## 2. Ontwerpprincipes

1. **Twee lagen: ruw en afgeleid.** De ruwe laag is een getrouwe, getypeerde kopie van wat er staat
   (andere kolomnamen en types, geen andere waarden). De afgeleide laag rekent (rasters, vermogens uit
   tellers, kwartieren) en zet vlaggen. Een waarde die in de afgeleide laag ongeldig is, wordt daar
   `NaN` **mét** een vlag; de ruwe laag houdt hem.
2. **Niets verzinnen.** Geen interpolatie over gaten langer dan het raster; geen opvulling van
   ontbrekende jaartotalen; geen afleiding van een kolom die de bron niet heeft (bijvoorbeeld geen
   tapwaterwarmte uit `waterFlow`).
3. **Lokale tijd in de uitvoer.** Elke tijdkolom tz-aware in `Europe/Amsterdam`, intern UTC; zelfde
   conventie als de andere preprocessing-repo's voor KITE-datasets. Intervallen zijn
   **begin-gelabeld**: `tijdstip_start` is het begin van het interval.
4. **`physiquant__unit`-namen.** Jaartotalen als `__kWh_a_1` en `__GJ_a_1`; tellers met `_cum`;
   vermogens `__W`; temperaturen `__degC`; vlaggen `__bool`; categorieën `__cat`; tekst `__str`.
5. **Zelfcontrole.** De afgeleide jaartotalen van de twee detailwoningen worden in elke run tegen de
   jaartotalen gelegd (§1.2). Een afwijking van meer dan 0,5 % is een fout in de pijplijn, en de run
   faalt.

## 3. Wat er uit komt

In `data/processed/` (gitignored), Parquet met zstd:

| tabel | korrel | rijen | inhoud |
|---|---|---:|---|
| `projecten` | project | 24 | de kolommen van `Projectdata`, getypeerd |
| `woningen_jaar` | woning | 898 | de kolommen van `Monitoringdata`, getypeerd, plus vlaggen |
| `detail_ruw/<meetpunt>.parquet` | meting | ~100.000 per woning | per tabblad, beide woningen, getrouwe kopie |
| `detail_5min` | woning × 5 min | ~2 × 105.120 | gemeenschappelijk raster, vermogens uit tellers, steekproeven, vlaggen |
| `detail_kwartier` | woning × kwartier | ~2 × 35.040 | uit `detail_5min`, voor afnemers die op kwartierbasis rekenen |
| `controle_jaartotalen` | woning × grootheid | 2 × 4 | detail tegenover jaartotaal, met afwijking en oordeel |
| `_manifest.jsonl` | | | per tabel pad, sha256, rijen, contractversie |

Daarnaast, gegenereerd door de pijplijn: `docs/data-quality.md` (vulgraad, vlaggen, gaten, de
zelfcontrole), `docs/datacatalogus.md` en `datapackage.json` (Frictionless), zoals bij de andere
preprocessing-repo's.

## 4. Kolomvertaling

### 4.1 `projecten`

| bron | uitvoer | type |
|---|---|---|
| Projectcode | `projectcode__str` | str |
| Monitoringdata | `woningen_met_monitoring__0` | int |
| KNMI Weerstation | `knmi_station__str` | str |
| Bouwjaar afgerond | `bouwjaar_afgerond__0` | int |
| Renovatiejaar afgerond | `renovatiejaar_afgerond__0` | int |
| Gebruiksoppervlak afgerond | `gebruiksoppervlak_afgerond__m2` | int |
| Woningtypologie | `woningtypologie__cat` | cat |
| EPV | `epv__bool` | bool |
| Actieve koeling | `actieve_koeling__bool` | bool |
| Netto warmtevraag na renovatie | `netto_warmtevraag_klasse__cat` | cat |
| Luchtdichtheid | `luchtdichtheid_qv10_klasse__cat` | cat |
| Spouwmuurisolatie, Gevelisolatie binnen-/buitenzijde, Dakisolatie binnen-/buitenzijde, Vloerisolatie, Nieuwe/Bestaande kozijnen met tenminste hr++ glas, Kierdichting | `spouwmuurisolatie__bool`, `gevelisolatie_binnen__bool`, `gevelisolatie_buiten__bool`, `dakisolatie_binnen__bool`, `dakisolatie_buiten__bool`, `vloerisolatie__bool`, `kozijnen_nieuw_hrpp__bool`, `kozijnen_bestaand_hrpp__bool`, `kierdichting__bool` | bool |
| Bijzonderheden schil | `bijzonderheden_schil__str` | str |
| Individueel of collectief | `opwekking_collectief__cat` | cat |
| Warmteopwekker | `warmteopwekker__cat` | cat |
| Bron van de warmteopwekker | `bron_warmteopwekker__cat` | cat |
| Afgiftesysteem | `afgiftesysteem__cat` | cat |
| Ventilatiesysteem | `ventilatiesysteem__cat` | cat |
| Elektrische opwekking | `elektrische_opwekking__cat` | cat |
| Kookinstallatie | `kookinstallatie__cat` | cat |
| Bijzonderheden installaties | `bijzonderheden_installaties__str` | str |

`ja`/`nee` naar `True`/`False`, leeg naar `<NA>`. Een keuzewaarde die niet in `keuzemenu` staat, blijft
staan en krijgt `<kolom>_buiten_keuzemenu__bool`. Let op aanhalingstekens: het werkboek gebruikt ’ en
‘ door elkaar (`jaren ’60` tegen `jaren ‘60`). Vergelijk met het keuzemenu na normalisatie van die
twee tekens, maar schrijf de oorspronkelijke tekst weg.

### 4.2 `woningen_jaar`

| bron | uitvoer |
|---|---|
| PROJECTCODE, WONINGCODE, JAARTAL MONITORING | `projectcode__str`, `woningcode__str`, `jaar_monitoring__0` |
| Opgewekte energie | `e_opwek__kWh_a_1` |
| Gebruikte energie voor ruimteverwarming / warm tapwater / Totaal | `e_opwekker_ruimte__kWh_a_1`, `e_opwekker_tapwater__kWh_a_1`, `e_opwekker_totaal__kWh_a_1` |
| Geleverde warmte voor ruimteverwarming / warm tapwater / Totaal | `q_ruimte__GJ_a_1`, `q_tapwater__GJ_a_1`, `q_totaal__GJ_a_1` |
| Gebruikte energie voor overige gebouwgebonden functies | `e_gebouw_overig__kWh_a_1` |
| Beschikbaar voor persoonlijk gebruik | `e_beschikbaar_persoonlijk__kWh_a_1` |
| Daadwerkelijk persoonlijk gebruik | `e_persoonlijk__kWh_a_1` |
| Luchtkwaliteit [CO2] / [%RV] | `co2_stookseizoen__ppm`, `rv_stookseizoen__pct` |
| Gasverbruik / Elektragebruik voor renovatie | `gas_voor_renovatie__m3_a_1`, `e_voor_renovatie__kWh_a_1` |
| Ligging woning | `ligging__cat` |
| Beloofde bundel voor huishoudelijk gebruik | `e_bundel_beloofd__kWh_a_1` |
| Netto afname grid | `e_netto_afname__kWh_a_1` |
| Temperatuur woonkamer / Setpoint | `temp_woonkamer_stookseizoen__degC`, `temp_setpoint_woonkamer_stookseizoen__degC` |

Geen omrekening van GJ naar kWh in de tabel; dat is één factor (277,78 kWh per GJ) en hoort bij de
afnemer. De eenheid staat in de naam.

**Vlaggen** (`__bool`, één per regel, de regel in de datacatalogus):

- `negatieve_waarde__bool`: een energie- of warmtegrootheid kleiner dan 0, behalve
  `e_beschikbaar_persoonlijk` en `e_netto_afname` (die mogen negatief zijn);
- `setpoint_nul__bool`: setpoint 0 °C;
- `som_opwekker_klopt_niet__bool`: als ruimte, tapwater en totaal alle drie gevuld zijn en het totaal
  meer dan 1 % afwijkt van de som; idem `som_warmte_klopt_niet__bool` voor de warmte;
- `balans_beschikbaar_klopt_niet__bool`: als opwek, totaal opwekker en overig gebouw gevuld zijn en
  *beschikbaar* meer dan 1 % (en meer dan 10 kWh) afwijkt van opwek min totaal opwekker min overig.

Eerst nagaan op de data hoe vaak elke regel aanslaat, en een regel die bij de helft van de woningen
aanslaat niet als fout maar als **definitieverschil** rapporteren.

### 4.3 `detail_ruw/<meetpunt>.parquet`

Eén bestand per tabblad (behalve `summary` en de lege tabbladen), beide woningen onder elkaar:
`woningcode__str`, `tijdstip` (tz-aware, `Europe/Amsterdam`, uit `Timestamp`), `timestamp_bron__s`
(de oorspronkelijke Unix-seconden, int64), daarna de bronkolommen met een eenheid in de naam:
`power` naar `p__W`, `total_energy_in` naar `e_in_cum__kWh`, `total_energy_out` naar
`e_uit_cum__kWh`, `energy_in_low`/`_norm` naar `e_in_laag_cum__kWh`/`e_in_normaal_cum__kWh` (idem
uit), `total_energyGJ` naar `q_cum__GJ`, temperaturen naar `temp_<naam>__degC`, `volume_out` naar
`volume_uit_cum__onbekend` (zie §1.2), statussen naar `<naam>__cat` of `__bool` als ze alleen 0 en 1
kennen, `error_code` naar `foutcode__str`. Lege tabbladen worden niet geschreven maar wel gemeld in
`docs/data-quality.md`.

### 4.4 `detail_5min` en `detail_kwartier`

Een gemeenschappelijk raster per woning: 5 minuten, begin-gelabeld, lokaal kalenderjaar 2019
(2019-01-01 00:00 tot 2020-01-01 00:00 `Europe/Amsterdam`).

- **Energie uit tellers.** Per teller de stand **lineair geïnterpoleerd op de intervalgrenzen**, maar
  alleen als de twee omringende metingen minder dan 15 minuten uit elkaar liggen. Het gemiddelde
  vermogen over het interval is dan Δstand / Δt. Zo wordt elke kWh precies één keer toegerekend en
  tellen de intervallen op tot het jaartotaal. Kolommen: `p_warmtepomp__W`, `p_booster__W`,
  `p_vatelement__W`, `p_wtw__W`, `p_pv_opwek__W`, `p_net_afname__W`, `p_net_teruglevering__W`,
  `q_ruimte__W` (uit GJ). Een teller die daalt, geeft een vlag (`<kolom>_teller_daalt__bool`) en
  `NaN` voor dat interval.
- **Momentane waarden** (temperaturen, statussen, `power`): de laatste meting **binnen** het interval,
  als steekproef, met het tijdstip ervan in `<groep>_tijdstip_steekproef`; geen middeling. Dat maakt
  het verschil tussen een intervalgemiddelde en een steekproef zichtbaar in de naam: `_steekproef`.
- **Dekking**: per teller `<kolom>_gedekt__bool` (de interpolatie was mogelijk).
- **Sentinels**: temperaturen buiten −40 tot 120 °C (en kamertemperatuur 0 °C) worden `NaN` met
  `<kolom>_buiten_bereik__bool`; de ruwe laag houdt de waarde.

`detail_kwartier` telt drie opeenvolgende intervallen van vijf minuten op tot een kwartier: gemiddeld
vermogen alleen als alle drie gedekt zijn, anders `NaN` met `<kolom>_onvolledig__bool`; steekproeven
van het laatste interval.

### 4.5 `controle_jaartotalen`

Voor `W_arnpivgi` en `W_mkpiieku`: `e_opwekker_totaal` (warmtepomp plus booster), `q_ruimte`,
`e_opwek` (PV) en `e_gebouw_overig` (WTW), uit `detail_5min` opgeteld tegenover `woningen_jaar`. Kolommen:
`woningcode__str`, `grootheid__str`, `uit_detail`, `uit_jaartotaal`, `eenheid__str`,
`afwijking__pct`, `binnen_tolerantie__bool`. Tolerantie 0,5 %. Faalt er een, dan stopt de run met een
foutmelding; dat is een fout in de pijplijn, niet in de data.

Let op het randeffect: de tellers beginnen een paar minuten vóór en eindigen een paar minuten na de
jaargrens. Het jaartotaal van Wattopia is vermoedelijk eindstand min beginstand van de hele reeks. De
controle gebruikt daarom **ook** die definitie (Δ over de ruwe reeks) naast de som over het raster, en
rapporteert beide.

## 5. Hervatbaarheid, manifest en contractversie

Het pakket is klein (78 MB uitgepakt, waarvan bijna alles de twee detailwerkboeken). Inlezen met
`openpyxl` in `read_only` duurt een paar minuten; daarom:

- per detailwerkboek eerst een tussenstap `data/interim/<woning>/<meetpunt>.parquet` (de ruwe laag per
  woning), met in het manifest de sha256 van het bronbestand; bij een volgende run wordt een werkboek
  niet opnieuw gelezen als de sha256 gelijk is;
- elke tabel eerst naar `<pad>.tmp` en dan atomisch hernoemd;
- `_manifest.jsonl` met per tabel pad, sha256, rijen en `UITVOER_CONTRACT_VERSIE`;
- `UITVOER_CONTRACT_VERSIE` omhoog bij elke wijziging aan vorm of betekenis van de uitvoer.

## 6. Pakketstructuur

Naar het model van de preprocessing-repo voor DACS-HW:

| module | doet |
|---|---|
| `lezers.py` | werkboeken lezen: jaartotalen met drie kopregels, detailtabbladen per meetpunt |
| `kolommen.py` | de vertaaltabellen van §4 als data, niet als code verspreid |
| `tijd.py` | Unix-seconden naar UTC en lokaal, het 5-minutenraster, de interpolatie van tellers |
| `tabellen.py` | de uitvoertabellen opbouwen |
| `toetsen.py` | de vlaggen en de zelfcontrole |
| `manifest.py` | manifest, sha256, atomisch schrijven, contractversie |
| `kwaliteitsrapport.py` | `docs/data-quality.md` schrijven |
| `datapackage.py` | `datapackage.json` en `docs/datacatalogus.md` uit dezelfde kolomdefinities |
| `pijplijn.py`, `__main__.py` | `python -m wattopia_preprocessing [--raw data/raw] [--uit data/processed]` |

## 7. Toetsen

Met kleine synthetische invoer in `tests/` (nooit de echte data in de repo):

- de drie kopregels van de jaartotalen; lege cellen blijven leeg;
- `ja`/`nee` naar bool; keuzewaarden met ’ en ‘ tegen het keuzemenu;
- Unix-seconden naar lokale tijd rond een zomertijdwissel;
- tellerinterpolatie: een reeks met jitter en een gat van meer dan 15 minuten; som van de
  intervallen gelijk aan Δstand over het gedekte deel; geen interpolatie over het gat;
- steekproef is de laatste meting binnen het interval, niet een gemiddelde;
- een dalende teller geeft een vlag en `NaN`;
- sentinels worden `NaN` met vlag in de afgeleide laag, en blijven staan in de ruwe laag;
- de zelfcontrole faalt bij een afwijking boven de tolerantie;
- manifest: een tweede run met dezelfde invoer leest de werkboeken niet opnieuw;
- de bestaande toets dat `data/` en brondata gitignored zijn.

Plus één toets die alleen draait als `data/raw/` er staat (`@pytest.mark.echte_data`, standaard
overgeslagen): de vorm van de echte uitvoer (rijen, kolommen) en de zelfcontrole.

## 8. Wat deze pijplijn niet doet

- **Geen koppeling met weerdata**, ook al noemt `Projectdata` een KNMI-station. Dat is een stap voor
  de afnemer; het station is geen locatie, maar bij een kleine set wel een aanwijzing over de
  regio, en die hoort niet in een gedeelde tabel met woningkenmerken.
- **Geen afleiding van tapwaterwarmte, COP of SCOP.** Dat zijn analyses.
- **Geen correctie van de tekenconventie** van `solar.power` en `smartMeter.power`; wel twee
  afgeleide, positieve kolommen voor afname en teruglevering uit de tellers.
- **Geen gebruik van `summary`**: het is een rekenblad, geen meting.

## 9. Afwijkingen bij de implementatie

De pijplijn is gedraaid op het echte pakket. Waar de data een aanname uit dit ontwerp tegensprak, is het
ontwerp hierboven ongewijzigd gelaten en staat hier wat de data liet zien en wat er is gedaan.

### 9.1 De som over het raster haalt het jaartotaal niet (§4.5)

- **Ontwerp.** "Zo wordt elke kWh precies één keer toegerekend en tellen de intervallen op tot het
  jaartotaal." De controle legt de som over het raster en de Δ over de ruwe reeks naast het jaartotaal, met
  een tolerantie van 0,5 % voor beide; een afwijking is een fout in de pijplijn.
- **Data.** De Δ over de ruwe reeks (`reeks_delta`) valt op alle acht posten op 0,000 % van het jaartotaal,
  dus eenheden, definitie en randeffect kloppen. De som over de intervallen (`raster_som`) blijft daar
  structureel onder: -0,26 % en -0,27 % (warmtepomp plus booster), -0,25 % en -0,23 % (warmte
  ruimteverwarming), -1,31 % en -1,75 % (zonnepanelen), -1,03 % en -1,11 % (WTW-regeling), voor
  respectievelijk W_arnpivgi en W_mkpiieku. Oorzaak: er wordt niet over gaten van meer dan 15 minuten
  geïnterpoleerd (§4.4), en per tabblad zijn er 10 tot 66 stappen van meer dan 10 minuten, de langste gaten
  2,5 tot 3,8 dagen. De teller loopt in zo'n gat gewoon door; die energie
  staat in geen enkel interval. Het raster dekt 99,17 % (W_arnpivgi) en 98,94 % (W_mkpiieku) van de
  intervallen voor de elektriciteitstellers van de warmtepomp. Het verlies bij de zonnepanelen en de
  WTW-regeling (1,0 tot 1,7 %) is groter dan het aandeel niet-gedekte intervallen (0,8 tot 1,1 %); de
  oorzaak daarvan is niet nagegaan.
- **Gedaan.** Een derde definitie toegevoegd, `raster_som_met_gaten`: `raster_som` plus de tellervoortgang in
  de niet-gedekte stukken. Die toetst de omrekening van teller naar vermogen in het raster (de factoren
  3,6e6 en 1e9, de duur van 300 s) zonder energie in gaten te verzinnen of te verdelen. De run faalt op
  `reeks_delta` en `raster_som_met_gaten` (beide binnen 0,5 %: alle 16 posten op 0,000 %). `raster_som` staat
  in de tabel en in `docs/data-quality.md`, met de aantekening "niet afgedwongen", zodat de gatenfout
  zichtbaar blijft. `controle_jaartotalen` heeft daardoor een kolom `definitie__str` en 24 in plaats van
  8 rijen. Een afnemer die over het raster sommeert, moet weten dat de intervallen de energie in gaten
  missen.

### 9.2 Sentinels in de thermostaat liggen binnen het bereik van -40 tot 120 °C (§1.2 en §4.4)

- **Ontwerp.** Temperaturen buiten -40 tot 120 °C zijn sentinels, en voor de kamertemperatuur ook exact
  0 °C. §1.2 noemt voor `thermostat.temp` waarden "tot -100 en -20 °C".
- **Data.** De thermostaat van W_arnpivgi heeft 1 meting van -100 °C, die van W_mkpiieku 2 metingen van
  -20 °C (van respectievelijk 103.412 en 85.605). -100 valt buiten het bereik; -20 niet, en blijft zonder
  extra regel als temperatuur staan. De warmtepomp van W_mkpiieku heeft 2 metingen met `room_temp` en
  `room_target_temp` exact 0 °C. In `flowHeatSpaceHeating.flow_temp` van W_arnpivgi staat 1 meting van 192,3 °C.
- **Gedaan.** Voor kamertemperaturen en het setpoint daarvan (`HeatPump` ruimte en setpoint, `thermostat`,
  `ventilation` ruimte, `co2sensor` ruimte) is "exact 0" verruimd naar "0 of lager"; de rest van het
  bereik is zoals in het ontwerp. Een kamertemperatuur van 0 °C of lager komt in een woning niet voor.
  De ruwe laag houdt alle waarden. De vlag slaat aan op 2 metingen van W_arnpivgi (1 thermostaat, 1
  aanvoertemperatuur van de warmtemeter) en 6 van W_mkpiieku (2 ruimtetemperatuur, 2 setpoint, 2 thermostaat).
  Buitentemperaturen zijn niet beperkt: 0 °C is daar een
  gewone waarde (486 en 905 metingen).

### 9.3 Aanhalingstekens in het keuzemenu bleken niet uiteen te lopen (§4.1)

- **Ontwerp.** Het werkboek gebruikt ’ en ‘ door elkaar; vergelijk met het keuzemenu na normalisatie.
- **Data.** Alle 236 ingevulde waarden in de keuzekolommen van `Projectdata` staan letterlijk in het `keuzemenu`, met én
  zonder normalisatie. De vlagkolommen `<kolom>_buiten_keuzemenu__bool` zijn daardoor altijd onwaar.
- **Gedaan.** De normalisatie en de vlagkolommen zijn gebleven, voor een volgende versie van het pakket; de
  oorspronkelijke tekst wordt altijd weggeschreven.

### 9.4 Kleine vormafwijkingen

- **Tussenstap en manifest (§5).** Het manifest van de tussenstap staat in `data/interim/_manifest.jsonl`
  en niet in dat van `data/processed/`, met de sha256 van het bronbestand in de regel van elk werkboek.
  Beide manifesten gebruiken dezelfde klasse. De tabellen in `data/processed/` worden in elke run opnieuw
  gebouwd (dat kost ongeveer drie minuten); alleen de werkboeken, die tientallen minuten kosten, worden
  op sha256 overgeslagen.
- **Inlezen.** Het inlezen van een detailwerkboek met `openpyxl` duurde op deze machine ongeveer 40 minuten
  per werkboek (twee werkboeken parallel, de machine ook voor andere dingen in gebruik; ruwweg honderd
  seconden per tabblad van ongeveer 100.000 rijen), veel meer dan de "paar minuten" uit §5.
- **Kolomnamen in `detail_5min`.** De dekkings- en dalingsvlaggen heten `<vermogenskolom zonder eenheid>_gedekt__bool`
  en `..._teller_daalt__bool`, bijvoorbeeld `p_warmtepomp_gedekt__bool`. Steekproefkolommen heten
  `<tabbladnaam in kleine letters>_<naam>_steekproef__<eenheid>`, met `<tabbladnaam>_tijdstip_steekproef` voor het tijdstip.
- **Vlagregels van `woningen_jaar` (§4.2).** De drie vergelijkingen (`som_*`, `balans_*`) zijn leeg (`<NA>`)
  als ze niet toetsbaar zijn, en niet onwaar. De waarden zelf blijven in `woningen_jaar` staan; de
  `NaN`-bij-vlag-regel uit §2 geldt voor `detail_5min`.
