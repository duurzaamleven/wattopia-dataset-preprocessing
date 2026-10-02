# Kwaliteit van de uitvoer

Dit rapport wordt door de pijplijn gegenereerd (`python -m wattopia_preprocessing`) en bevat alleen aggregaten: aantallen, aandelen en afwijkingspercentages. Het zegt iets over de **data en de verwerking**, niet over de prestaties van woningen of installaties. Waarden per woning staan niet in git; zie [`GEBRUIKSVOORWAARDEN.md`](../GEBRUIKSVOORWAARDEN.md).

Een vlag verandert geen waarde. In `woningen_jaar` staat de oorspronkelijke waarde onverkort naast de vlag; in `detail_5min` is een waarde die buiten het bereik valt `NaN` met een vlag, en houdt `detail_ruw` hem.

## 1. Jaartotalen

- `projecten`: 24 projecten. Waarden die niet in het keuzemenu staan: geen.
- `woningen_jaar`: 898 woningen (466 woningen in 2019, 432 woningen in 2020). Dubbele woningcodes: 0. Woningen met een projectcode die niet in `projecten` staat: 0.

### 1.1 Vulgraad

Een lege cel is "niet gerapporteerd", geen nul. De vulgraad is zeer ongelijk; een analyse die een kolom nodig heeft, hoort eerst te kijken hoeveel woningen hem hebben.

| kolom | gevuld | aandeel |
|---|---|---|
| `projectcode__str` | 898 | 100,0 % |
| `woningcode__str` | 898 | 100,0 % |
| `jaar_monitoring__0` | 898 | 100,0 % |
| `e_opwek__kWh_a_1` | 898 | 100,0 % |
| `e_opwekker_ruimte__kWh_a_1` | 54 | 6,0 % |
| `e_opwekker_tapwater__kWh_a_1` | 54 | 6,0 % |
| `e_opwekker_totaal__kWh_a_1` | 898 | 100,0 % |
| `q_ruimte__GJ_a_1` | 510 | 56,8 % |
| `q_tapwater__GJ_a_1` | 335 | 37,3 % |
| `q_totaal__GJ_a_1` | 257 | 28,6 % |
| `e_gebouw_overig__kWh_a_1` | 884 | 98,4 % |
| `e_beschikbaar_persoonlijk__kWh_a_1` | 884 | 98,4 % |
| `e_persoonlijk__kWh_a_1` | 868 | 96,7 % |
| `co2_stookseizoen__ppm` | 110 | 12,2 % |
| `rv_stookseizoen__pct` | 110 | 12,2 % |
| `gas_voor_renovatie__m3_a_1` | 30 | 3,3 % |
| `e_voor_renovatie__kWh_a_1` | 30 | 3,3 % |
| `ligging__cat` | 40 | 4,5 % |
| `e_bundel_beloofd__kWh_a_1` | 342 | 38,1 % |
| `e_netto_afname__kWh_a_1` | 389 | 43,3 % |
| `temp_woonkamer_stookseizoen__degC` | 112 | 12,5 % |
| `temp_setpoint_woonkamer_stookseizoen__degC` | 252 | 28,1 % |

### 1.2 Vlaggen op de woningen

De regel van elke vlag staat in [`datacatalogus.md`](datacatalogus.md). Een vergelijking is alleen toetsbaar als alle waarden erin gevuld zijn; het aandeel is genomen over de toetsbare woningen. Slaat een regel bij minstens 50 % van de toetsbare woningen aan, dan heet dat een **definitieverschil** en geen fout.

| vlag | aan | toetsbaar | aandeel van toetsbaar | oordeel |
|---|---|---|---|---|
| `negatieve_waarde__bool` | 1 | 898 | 0,11 % |  |
| `setpoint_nul__bool` | 3 | 898 | 0,33 % |  |
| `som_opwekker_klopt_niet__bool` | 0 | 54 | 0,00 % |  |
| `som_warmte_klopt_niet__bool` | 0 | 257 | 0,00 % |  |
| `balans_beschikbaar_klopt_niet__bool` | 54 | 884 | 6,11 % |  |

## 2. Detaildata van twee woningen

Lege tabbladen worden niet als tabel geschreven. Per woning: W_arnpivgi: sheet15; W_mkpiieku: ventilation, sheet15, air_sensor_kitchen, air_sensor_livingroom, air_sensor_bathroom, air_sensor_bedroom, virtualVentilation.

Het tabblad `summary` is een rekenblad met formules en wordt niet gelezen.

### 2.1 Woning W_arnpivgi: meetpunten

| meetpunt | metingen | bereik | mediane stap | stappen > 10 min | langste gat | dubbele tijdstempels |
|---|---|---|---|---|---|---|
| `HeatPump` | 104252 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 15 | 2.8 d | 0 |
| `energyHeatpump` | 104243 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 24 | 2.5 d | 0 |
| `energyBooster` | 104243 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 22 | 2.5 d | 0 |
| `energyImmersion` | 104244 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 24 | 2.5 d | 0 |
| `energyWtwReg` | 104243 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 24 | 2.5 d | 0 |
| `solar` | 104243 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 27 | 2.5 d | 0 |
| `smartMeter` | 78171 | 2019-04-01 13:44 tot 2019-12-31 23:00 UTC | 300 s | 12 | 2.8 d | 0 |
| `flowHeatSpaceHeating` | 104149 | 2018-12-31 23:04 tot 2019-12-31 23:00 UTC | 300 s | 58 | 2.8 d | 0 |
| `waterFlow` | 104130 | 2018-12-31 23:04 tot 2019-12-31 23:00 UTC | 300 s | 66 | 2.8 d | 0 |
| `ventilation` | 104255 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 21 | 2.5 d | 0 |
| `co2sensor` | 104242 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 23 | 2.5 d | 0 |
| `thermostat` | 103412 | 2018-12-31 23:04 tot 2019-12-31 22:57 UTC | 300 s | 11 | 2.8 d | 0 |
| `relay1` | 104244 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 25 | 2.5 d | 0 |
| `relay2` | 104245 | 2018-12-31 23:04 tot 2019-12-31 23:00 UTC | 300 s | 24 | 2.5 d | 0 |
| `relay24v` | 104247 | 2018-12-31 23:04 tot 2019-12-31 23:00 UTC | 300 s | 24 | 2.5 d | 0 |
| `immersion` | 104247 | 2018-12-31 23:04 tot 2019-12-31 23:00 UTC | 300 s | 29 | 2.5 d | 0 |

### 2.2 Woning W_mkpiieku: meetpunten

| meetpunt | metingen | bereik | mediane stap | stappen > 10 min | langste gat | dubbele tijdstempels |
|---|---|---|---|---|---|---|
| `HeatPump` | 103980 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 21 | 3.7 d | 0 |
| `energyHeatpump` | 103982 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 27 | 3.7 d | 0 |
| `energyBooster` | 103980 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 29 | 3.7 d | 0 |
| `energyImmersion` | 103978 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 29 | 3.7 d | 0 |
| `energyWtwReg` | 103982 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 28 | 3.7 d | 0 |
| `solar` | 103997 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 26 | 3.1 d | 0 |
| `smartMeter` | 40748 | 2019-08-08 12:39 tot 2019-12-31 23:00 UTC | 300 s | 10 | 3.8 d | 0 |
| `flowHeatSpaceHeating` | 94807 | 2019-02-01 13:35 tot 2019-12-31 22:55 UTC | 300 s | 40 | 3.8 d | 0 |
| `waterFlow` | 103866 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 65 | 3.8 d | 0 |
| `co2sensor` | 103983 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 27 | 3.7 d | 0 |
| `thermostat` | 85605 | 2018-12-31 23:04 tot 2019-10-29 12:18 UTC | 300 s | 11 | 3.7 d | 0 |
| `relay1` | 85737 | 2018-12-31 23:04 tot 2019-10-29 12:20 UTC | 300 s | 16 | 3.7 d | 0 |
| `relay2` | 85736 | 2018-12-31 23:04 tot 2019-10-29 12:20 UTC | 300 s | 17 | 3.7 d | 0 |
| `relay24v` | 85739 | 2018-12-31 23:04 tot 2019-10-29 12:20 UTC | 300 s | 20 | 3.7 d | 0 |
| `immersion` | 103986 | 2018-12-31 23:04 tot 2019-12-31 22:55 UTC | 300 s | 19 | 3.7 d | 0 |

## 3. Het raster van vijf minuten

De dekking is het aandeel intervallen waarvan beide grenzen geïnterpoleerd konden worden uit twee metingen die minder dan 15 minuten uit elkaar liggen. Daarbuiten is het vermogen `NaN`; er wordt niet over gaten geïnterpoleerd.

### Woning W_arnpivgi

| vermogenskolom | gedekt | teller daalt | met waarde |
|---|---|---|---|
| `p_warmtepomp__W` | 99,17 % | 0 | 99,17 % |
| `p_booster__W` | 99,17 % | 0 | 99,17 % |
| `p_vatelement__W` | 99,17 % | 0 | 99,17 % |
| `p_wtw__W` | 99,17 % | 0 | 99,17 % |
| `p_pv_opwek__W` | 99,17 % | 0 | 99,17 % |
| `p_net_afname__W` | 74,38 % | 0 | 74,38 % |
| `p_net_teruglevering__W` | 74,38 % | 0 | 74,38 % |
| `q_ruimte__W` | 99,04 % | 0 | 99,04 % |

| tabblad | intervallen met een steekproef |
|---|---|
| `HeatPump` | 98,9 % |
| `energyHeatpump` | 98,7 % |
| `energyBooster` | 98,9 % |
| `energyImmersion` | 98,9 % |
| `energyWtwReg` | 98,7 % |
| `solar` | 98,8 % |
| `smartMeter` | 74,2 % |
| `flowHeatSpaceHeating` | 98,9 % |
| `waterFlow` | 98,3 % |
| `ventilation` | 98,9 % |
| `co2sensor` | 99,0 % |
| `thermostat` | 98,2 % |
| `relay1` | 98,8 % |
| `relay2` | 98,9 % |
| `relay24v` | 98,9 % |
| `immersion` | 98,8 % |

### Woning W_mkpiieku

| vermogenskolom | gedekt | teller daalt | met waarde |
|---|---|---|---|
| `p_warmtepomp__W` | 98,94 % | 0 | 98,94 % |
| `p_booster__W` | 98,94 % | 0 | 98,94 % |
| `p_vatelement__W` | 98,94 % | 0 | 98,94 % |
| `p_wtw__W` | 98,94 % | 0 | 98,94 % |
| `p_pv_opwek__W` | 98,96 % | 0 | 98,96 % |
| `p_net_afname__W` | 38,79 % | 0 | 38,79 % |
| `p_net_teruglevering__W` | 38,79 % | 0 | 38,79 % |
| `q_ruimte__W` | 90,18 % | 0 | 90,18 % |

| tabblad | intervallen met een steekproef |
|---|---|
| `HeatPump` | 98,5 % |
| `energyHeatpump` | 97,8 % |
| `energyBooster` | 98,3 % |
| `energyImmersion` | 98,4 % |
| `energyWtwReg` | 98,4 % |
| `solar` | 98,0 % |
| `smartMeter` | 38,8 % |
| `flowHeatSpaceHeating` | 89,3 % |
| `waterFlow` | 98,4 % |
| `ventilation` | 0,0 % |
| `co2sensor` | 98,4 % |
| `thermostat` | 80,8 % |
| `relay1` | 81,1 % |
| `relay2` | 80,7 % |
| `relay24v` | 80,8 % |
| `immersion` | 97,4 % |

### 3.1 Sentinels in temperaturen

Een temperatuur buiten -40 tot 120 graden Celsius (en, voor kamertemperaturen en het setpoint daarvan, 0 of lager) is in `detail_5min` `NaN` met een vlag; de ruwe laag houdt de waarde. Aandeel van de gevulde ruwe metingen:

| woning | tabblad | kolom | aantal | aandeel |
|---|---|---|---|---|
| W_arnpivgi | `flowHeatSpaceHeating` | `temp_aanvoer__degC` | 1 | 0,001 % |
| W_arnpivgi | `thermostat` | `temp_thermostaat__degC` | 1 | 0,001 % |
| W_mkpiieku | `HeatPump` | `temp_ruimte_setpoint__degC` | 2 | 0,002 % |
| W_mkpiieku | `HeatPump` | `temp_ruimte__degC` | 2 | 0,002 % |
| W_mkpiieku | `thermostat` | `temp_thermostaat__degC` | 2 | 0,002 % |

## 4. Zelfcontrole tegen de jaartotalen

De twee detailwoningen staan ook in de jaartotalen. Vier grootheden uit de detaildata worden tegen het jaartotaal gelegd, op drie manieren:

- `reeks_delta`: eindstand min beginstand van de hele ruwe reeks. Het jaartotaal van Wattopia is vermoedelijk zo bepaald.
- `raster_som`: de som over de intervallen van `detail_5min`. Dit telt alleen de gedekte intervallen en mist dus de energie in gaten van meer dan 15 minuten, die niet wordt verdeeld of verzonnen. De afwijking is daarom negatief en ongeveer gelijk aan het aandeel van de energie dat in gaten viel.
- `raster_som_met_gaten`: `raster_som` plus de tellervoortgang in de niet-gedekte stukken, die wel in de teller staat maar niet aan een interval is toegerekend. Dit toetst de omrekening van teller naar vermogen in het raster.

Tolerantie 0,5 %. De run faalt als `reeks_delta` of `raster_som_met_gaten` daarbuiten valt; `raster_som` wordt gerapporteerd maar niet afgedwongen. Er staan hier alleen percentages.

| woning | grootheid | definitie | afwijking | oordeel |
|---|---|---|---|---|
| W_arnpivgi | e_opwekker_totaal | raster_som | -0,264 % | binnen (niet afgedwongen) |
| W_arnpivgi | e_opwekker_totaal | raster_som_met_gaten | +0,000 % | binnen |
| W_arnpivgi | e_opwekker_totaal | reeks_delta | +0,000 % | binnen |
| W_arnpivgi | q_ruimte | raster_som | -0,248 % | binnen (niet afgedwongen) |
| W_arnpivgi | q_ruimte | raster_som_met_gaten | +0,000 % | binnen |
| W_arnpivgi | q_ruimte | reeks_delta | +0,000 % | binnen |
| W_arnpivgi | e_opwek | raster_som | -1,308 % | buiten (niet afgedwongen) |
| W_arnpivgi | e_opwek | raster_som_met_gaten | +0,000 % | binnen |
| W_arnpivgi | e_opwek | reeks_delta | +0,000 % | binnen |
| W_arnpivgi | e_gebouw_overig | raster_som | -1,032 % | buiten (niet afgedwongen) |
| W_arnpivgi | e_gebouw_overig | raster_som_met_gaten | +0,000 % | binnen |
| W_arnpivgi | e_gebouw_overig | reeks_delta | +0,000 % | binnen |
| W_mkpiieku | e_opwekker_totaal | raster_som | -0,266 % | binnen (niet afgedwongen) |
| W_mkpiieku | e_opwekker_totaal | raster_som_met_gaten | +0,000 % | binnen |
| W_mkpiieku | e_opwekker_totaal | reeks_delta | +0,000 % | binnen |
| W_mkpiieku | q_ruimte | raster_som | -0,230 % | binnen (niet afgedwongen) |
| W_mkpiieku | q_ruimte | raster_som_met_gaten | +0,000 % | binnen |
| W_mkpiieku | q_ruimte | reeks_delta | +0,000 % | binnen |
| W_mkpiieku | e_opwek | raster_som | -1,749 % | buiten (niet afgedwongen) |
| W_mkpiieku | e_opwek | raster_som_met_gaten | +0,000 % | binnen |
| W_mkpiieku | e_opwek | reeks_delta | +0,000 % | binnen |
| W_mkpiieku | e_gebouw_overig | raster_som | -1,106 % | buiten (niet afgedwongen) |
| W_mkpiieku | e_gebouw_overig | raster_som_met_gaten | +0,000 % | binnen |
| W_mkpiieku | e_gebouw_overig | reeks_delta | +0,000 % | binnen |
