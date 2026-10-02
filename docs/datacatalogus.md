# Datacatalogus

Wordt door de pijplijn gegenereerd uit `kolommen.py`, net als `datapackage.json`. De uitvoer staat in `data/processed/` en niet in git; zie [`GEBRUIKSVOORWAARDEN.md`](../GEBRUIKSVOORWAARDEN.md). Bronvermelding: RVO, Wattopia, Out of Harm's Way, "Woningprestaties - Monitoringdata van bestaande woningen", 2022, opvraagbaar via info@woningprestaties.nl.

Namen volgen de conventie `physiquant__unit`: de eenheid staat na een dubbele underscore (`temp_aanvoer__degC`). `_cum` is een meterstand op een moment; zonder `_cum` is het een gemiddelde over het interval of een jaartotaal. `__bool` is een vlag of ja/nee, `__cat` een categorie, `__str` tekst, `__0` een telling zonder eenheid.

## Aannames en onzekerheden

- **Eenheden van de tellers** (`total_energy_*`, `energy_*` in kWh, `total_energyGJ` in GJ, `power` in W) zijn afgeleid en getoetst tegen de jaartotalen; het codeboek licht de detaildata niet toe.
- **Tekenconventie.** `solar.power` is negatief bij opwek en `smartMeter.power` positief bij afname en negatief bij teruglevering. Dat is niet omgedraaid; `p_pv_opwek`, `p_net_afname` en `p_net_teruglevering` komen uit de tellers en zijn positief.
- **Eenheid onbekend** (kolomnaam eindigt op `__onbekend`): `volume_out`, de debieten van de ventilatie en `voc`.
- **Codes van de fabrikant** (`op_mode`, `system_status`, `error_code`, `filter`): betekenis onbekend.
- **Totaal gebruikte energie door de warmteopwekker** is warmtepomp plus booster (het elektrische bijverwarmingselement).
- **Momentane waarden** (temperaturen, statussen, `power`) in `detail_5min` zijn de laatste meting binnen het interval, een steekproef en geen gemiddelde; de naam eindigt daarom op `_steekproef`.
- **Intervallen** zijn begin-gelabeld; alle tijdkolommen zijn tz-aware in `Europe/Amsterdam`.

## Tabellen

### `projecten`

Eén rij per project: typologie, schil en installaties (tabblad Projectdata).
Pad: `data/processed/projecten.parquet`. Korrel: project. Rijen: 24.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `projectcode__str` | string | `Projectcode` | Willekeurige projectcode uit de anonimisering. |
| `woningen_met_monitoring__0` | integer | `Monitoringdata` | Aantal woningen in het project met monitoringdata (verhuld, zie codeboek). |
| `knmi_station__str` | string | `KNMI Weerstation` | KNMI-weerstation dat bij het project hoort; geen locatie van de woning. |
| `bouwjaar_afgerond__0` | integer | `Bouwjaar afgerond` | Bouwjaar, afgerond door de anonimisering. |
| `renovatiejaar_afgerond__0` | integer | `Renovatiejaar afgerond` | Renovatiejaar, afgerond door de anonimisering. |
| `gebruiksoppervlak_afgerond__m2` | integer | `Gebruiksoppervlak afgerond` | Gebruiksoppervlak, afgerond door de anonimisering. |
| `woningtypologie__cat` | string | `Woningtypologie` | Woningtypologie volgens het keuzemenu. |
| `woningtypologie_buiten_keuzemenu__bool` | boolean |  | Waarde van woningtypologie__cat staat niet in het keuzemenu (kolom Woningtypologie), na normalisatie van de aanhalingstekens; de oorspronkelijke tekst is behouden. |
| `epv__bool` | boolean | `EPV` | Energieprestatievergoeding (ja/nee). |
| `actieve_koeling__bool` | boolean | `Actieve koeling` | Actieve koeling aanwezig (ja/nee). |
| `netto_warmtevraag_klasse__cat` | string | `Netto warmtevraag na renovatie` | Klasse van de netto warmtevraag na renovatie. |
| `netto_warmtevraag_klasse_buiten_keuzemenu__bool` | boolean |  | Waarde van netto_warmtevraag_klasse__cat staat niet in het keuzemenu (kolom Netto warmtevraag na renovatie), na normalisatie van de aanhalingstekens; de oorspronkelijke tekst is behouden. |
| `luchtdichtheid_qv10_klasse__cat` | string | `Luchtdichtheid` | Klasse van de luchtdichtheid (qv;10). |
| `luchtdichtheid_qv10_klasse_buiten_keuzemenu__bool` | boolean |  | Waarde van luchtdichtheid_qv10_klasse__cat staat niet in het keuzemenu (kolom Luchtdichtheid), na normalisatie van de aanhalingstekens; de oorspronkelijke tekst is behouden. |
| `spouwmuurisolatie__bool` | boolean | `Spouwmuurisolatie` | Spouwmuurisolatie (ja/nee). |
| `gevelisolatie_binnen__bool` | boolean | `Gevelisolatie binnenzijde` | Gevelisolatie aan de binnenzijde (ja/nee). |
| `gevelisolatie_buiten__bool` | boolean | `Gevelisolatie buitenzijde` | Gevelisolatie aan de buitenzijde (ja/nee). |
| `dakisolatie_binnen__bool` | boolean | `Dakisolatie binnenzijde` | Dakisolatie aan de binnenzijde (ja/nee). |
| `dakisolatie_buiten__bool` | boolean | `Dakisolatie buitenzijde` | Dakisolatie aan de buitenzijde (ja/nee). |
| `vloerisolatie__bool` | boolean | `Vloerisolatie` | Vloerisolatie (ja/nee). |
| `kozijnen_nieuw_hrpp__bool` | boolean | `Nieuwe kozijnen met tenminste hr++ glas` | Nieuwe kozijnen met tenminste HR++-glas (ja/nee). |
| `kozijnen_bestaand_hrpp__bool` | boolean | `Bestaande kozijnen met tenminste hr++ glas` | Bestaande kozijnen met tenminste HR++-glas (ja/nee). |
| `kierdichting__bool` | boolean | `Kierdichting` | Kierdichting (ja/nee). |
| `bijzonderheden_schil__str` | string | `Bijzonderheden schil` | Vrije tekst over de schil. |
| `opwekking_collectief__cat` | string | `Individueel of collectief` | Individuele of collectieve opwekking. |
| `opwekking_collectief_buiten_keuzemenu__bool` | boolean |  | Waarde van opwekking_collectief__cat staat niet in het keuzemenu (kolom Individueel of collectief), na normalisatie van de aanhalingstekens; de oorspronkelijke tekst is behouden. |
| `warmteopwekker__cat` | string | `Warmteopwekker` | Type warmteopwekker. |
| `warmteopwekker_buiten_keuzemenu__bool` | boolean |  | Waarde van warmteopwekker__cat staat niet in het keuzemenu (kolom Warmteopwekker), na normalisatie van de aanhalingstekens; de oorspronkelijke tekst is behouden. |
| `bron_warmteopwekker__cat` | string | `Bron van de warmteopwekker` | Bron van de warmteopwekker. |
| `bron_warmteopwekker_buiten_keuzemenu__bool` | boolean |  | Waarde van bron_warmteopwekker__cat staat niet in het keuzemenu (kolom Bron van de warmteopwekker), na normalisatie van de aanhalingstekens; de oorspronkelijke tekst is behouden. |
| `afgiftesysteem__cat` | string | `Afgiftesysteem` | Afgiftesysteem. |
| `afgiftesysteem_buiten_keuzemenu__bool` | boolean |  | Waarde van afgiftesysteem__cat staat niet in het keuzemenu (kolom Afgiftesysteem), na normalisatie van de aanhalingstekens; de oorspronkelijke tekst is behouden. |
| `ventilatiesysteem__cat` | string | `Ventilatiesysteem` | Ventilatiesysteem. |
| `ventilatiesysteem_buiten_keuzemenu__bool` | boolean |  | Waarde van ventilatiesysteem__cat staat niet in het keuzemenu (kolom Ventilatiesysteem), na normalisatie van de aanhalingstekens; de oorspronkelijke tekst is behouden. |
| `elektrische_opwekking__cat` | string | `Elektrische opwekking` | Elektrische opwekking (kolom Energieopweksysteem in het keuzemenu). |
| `elektrische_opwekking_buiten_keuzemenu__bool` | boolean |  | Waarde van elektrische_opwekking__cat staat niet in het keuzemenu (kolom Energieopweksysteem), na normalisatie van de aanhalingstekens; de oorspronkelijke tekst is behouden. |
| `kookinstallatie__cat` | string | `Kookinstallatie` | Kookinstallatie. |
| `kookinstallatie_buiten_keuzemenu__bool` | boolean |  | Waarde van kookinstallatie__cat staat niet in het keuzemenu (kolom Kookinstallatie), na normalisatie van de aanhalingstekens; de oorspronkelijke tekst is behouden. |
| `bijzonderheden_installaties__str` | string | `Bijzonderheden installaties` | Vrije tekst over de installaties. |

### `woningen_jaar`

Eén rij per woning: energie, warmte, binnenklimaat en gebruik over een jaar (tabblad Monitoringdata), met vlaggen.
Pad: `data/processed/woningen_jaar.parquet`. Korrel: woning. Rijen: 898.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `projectcode__str` | string | `PROJECTCODE` | Willekeurige projectcode; verwijst naar projecten. |
| `woningcode__str` | string | `WONINGCODE` | Willekeurige woningcode uit de anonimisering. |
| `jaar_monitoring__0` | integer | `JAARTAL MONITORING` | Kalenderjaar van de monitoring. |
| `e_opwek__kWh_a_1` | number | `Opgewekte energie` | Opgewekte energie (zonnepanelen). |
| `e_opwekker_ruimte__kWh_a_1` | number | `Gebruikte energie voor ruimteverwarming` | Elektriciteit voor ruimteverwarming door de warmteopwekker(s). |
| `e_opwekker_tapwater__kWh_a_1` | number | `Gebruikte energie voor warm tapwater` | Elektriciteit voor warm tapwater door de warmteopwekker(s). |
| `e_opwekker_totaal__kWh_a_1` | number | `Totaal gebruikte energie door de warmteopwekker(s)` | Totaal gebruikte elektriciteit door de warmteopwekker(s); in de detaildata warmtepomp plus booster. |
| `q_ruimte__GJ_a_1` | number | `Geleverde warmte voor ruimteverwarming` | Geleverde warmte voor ruimteverwarming. |
| `q_tapwater__GJ_a_1` | number | `Geleverde warmte voor warm tapwater` | Geleverde warmte voor warm tapwater. |
| `q_totaal__GJ_a_1` | number | `Totaal geleverde warmte` | Totaal geleverde warmte. |
| `e_gebouw_overig__kWh_a_1` | number | `Gebruikte energie voor overige gebouwgebonden functies` | Elektriciteit voor overige gebouwgebonden functies (in de detaildata de WTW-regeling). |
| `e_beschikbaar_persoonlijk__kWh_a_1` | number | `Beschikbaar voor persoonlijk gebruik` | Elektriciteit beschikbaar voor persoonlijk gebruik; mag negatief zijn. |
| `e_persoonlijk__kWh_a_1` | number | `Daadwerkelijk persoonlijk gebruik` | Daadwerkelijk persoonlijk elektriciteitsgebruik. |
| `co2_stookseizoen__ppm` | number | `Luchtkwaliteit [CO2]` | Luchtkwaliteit, CO2 in het stookseizoen. |
| `rv_stookseizoen__pct` | number | `Luchtkwaliteit [%RV]` | Luchtkwaliteit, relatieve vochtigheid in het stookseizoen. |
| `gas_voor_renovatie__m3_a_1` | number | `Gasverbruik voor renovatie` | Gasverbruik voor de renovatie. |
| `e_voor_renovatie__kWh_a_1` | number | `Elektragebruik voor renovatie` | Elektriciteitsgebruik voor de renovatie. |
| `ligging__cat` | string | `Ligging woning` | Ligging van de woning (hoek of tussen). |
| `e_bundel_beloofd__kWh_a_1` | number | `Beloofde bundel voor huishoudelijk gebruik` | Beloofde bundel voor huishoudelijk gebruik. |
| `e_netto_afname__kWh_a_1` | number | `Netto afname grid` | Netto afname van het net; mag negatief zijn. |
| `temp_woonkamer_stookseizoen__degC` | number | `Temperatuur woonkamer` | Gemeten temperatuur in de woonkamer in het stookseizoen. |
| `temp_setpoint_woonkamer_stookseizoen__degC` | number | `Setpoint temperatuur woonkamer` | Ingesteld setpoint van de woonkamer in het stookseizoen. |
| `negatieve_waarde__bool` | boolean |  | Regel: een energie- of warmtegrootheid (kWh of GJ per jaar) is kleiner dan 0, behalve e_beschikbaar_persoonlijk en e_netto_afname, die negatief mogen zijn. |
| `setpoint_nul__bool` | boolean |  | Regel: het setpoint van de woonkamer is 0 graden Celsius. |
| `som_opwekker_klopt_niet__bool` | boolean |  | Regel: ruimte, tapwater en totaal van de warmteopwekker zijn alle drie gevuld en het totaal wijkt meer dan 1 % af van de som. Leeg als niet alle drie gevuld zijn. |
| `som_warmte_klopt_niet__bool` | boolean |  | Regel: geleverde warmte voor ruimte, tapwater en totaal zijn alle drie gevuld en het totaal wijkt meer dan 1 % af van de som. Leeg als niet alle drie gevuld zijn. |
| `balans_beschikbaar_klopt_niet__bool` | boolean |  | Regel: opwek, totaal opwekker en overig gebouwgebonden zijn gevuld, en beschikbaar voor persoonlijk gebruik wijkt meer dan 1 % (en meer dan 10 kWh) af van opwek min totaal opwekker min overig. Leeg als een van de drie ontbreekt. Een afwijking is een definitieverschil of een meetfout; de pijplijn beslist dat niet. |

### `detail_ruw/HeatPump`

Getrouwe kopie van tabblad HeatPump van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/HeatPump.parquet`. Rijen: 208.232.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `booster_status__bool` | boolean | `booster_status` | Status van de booster (bijverwarming), 0 of 1. |
| `dhw_verboden__bool` | boolean | `dhw_prohibit` | Warm tapwater geblokkeerd, 0 of 1. |
| `foutcode__str` | string | `error_code` | Foutcode van de fabrikant, betekenis onbekend. |
| `firmware_versie__str` | string | `firmware_version` | Firmwareversie van de warmtepomp. |
| `temp_aanvoer__degC` | number | `flow_temp` | Aanvoertemperatuur. |
| `dhw_geforceerd__bool` | boolean | `force_dhw` | Warm tapwater geforceerd, 0 of 1. |
| `verwarming_verboden__bool` | boolean | `heating_prohibit` | Verwarming geblokkeerd, 0 of 1. |
| `vakantie__bool` | boolean | `holiday` | Vakantiestand, 0 of 1. |
| `op_mode__cat` | string | `op_mode` | Bedrijfsmodus, code van de fabrikant, betekenis onbekend. |
| `temp_buiten__degC` | number | `outdoor_temp` | Buitentemperatuur zoals de warmtepomp die meet. |
| `temp_retour__degC` | number | `return_temp` | Retourtemperatuur. |
| `temp_ruimte_setpoint__degC` | number | `room_target_temp` | Gewenste ruimtetemperatuur (room_target_temp). |
| `temp_ruimte__degC` | number | `room_temp` | Ruimtetemperatuur zoals de warmtepomp die meet. |
| `system_status__cat` | string | `system_status` | Systeemstatus, code van de fabrikant, betekenis onbekend. |
| `temp_doel__degC` | number | `target_temp` | Doeltemperatuur (target_temp). |
| `temp_ongespecificeerd__degC` | number | `temp` | Kolom temp van de bron; welke temperatuur dit is, is niet toegelicht. |

### `detail_ruw/energyHeatpump`

Getrouwe kopie van tabblad energyHeatpump van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/energyHeatpump.parquet`. Rijen: 208.225.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `p__W` | number | `power` | Vermogen op het meetmoment (teken zoals in de bron). |
| `e_in_cum__kWh` | number | `total_energy_in` | Meterstand van de energie, kWh (eenheid afgeleid en getoetst tegen de jaartotalen). |

### `detail_ruw/energyBooster`

Getrouwe kopie van tabblad energyBooster van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/energyBooster.parquet`. Rijen: 208.223.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `p__W` | number | `power` | Vermogen op het meetmoment (teken zoals in de bron). |
| `e_in_cum__kWh` | number | `total_energy_in` | Meterstand van de energie, kWh (eenheid afgeleid en getoetst tegen de jaartotalen). |

### `detail_ruw/energyImmersion`

Getrouwe kopie van tabblad energyImmersion van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/energyImmersion.parquet`. Rijen: 208.222.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `p__W` | number | `power` | Vermogen op het meetmoment (teken zoals in de bron). |
| `e_in_cum__kWh` | number | `total_energy_in` | Meterstand van de energie, kWh (eenheid afgeleid en getoetst tegen de jaartotalen). |

### `detail_ruw/energyWtwReg`

Getrouwe kopie van tabblad energyWtwReg van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/energyWtwReg.parquet`. Rijen: 208.225.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `p__W` | number | `power` | Vermogen op het meetmoment (teken zoals in de bron). |
| `e_in_cum__kWh` | number | `total_energy_in` | Meterstand van de energie, kWh (eenheid afgeleid en getoetst tegen de jaartotalen). |

### `detail_ruw/solar`

Getrouwe kopie van tabblad solar van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/solar.parquet`. Rijen: 208.240.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `p__W` | number | `power` | Vermogen; negatief bij opwek (tekenconventie van de bron, niet omgedraaid). |
| `e_in_cum__kWh` | number | `total_energy_in` | Meterstand ingaande energie, kWh. |
| `e_uit_cum__kWh` | number | `total_energy_out` | Meterstand opgewekte energie, kWh. |

### `detail_ruw/smartMeter`

Getrouwe kopie van tabblad smartMeter van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/smartMeter.parquet`. Rijen: 118.919.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `e_in_laag_cum__kWh` | number | `energy_in_low` | Meterstand afname laag tarief, kWh. |
| `e_in_normaal_cum__kWh` | number | `energy_in_norm` | Meterstand afname normaal tarief, kWh. |
| `e_uit_laag_cum__kWh` | number | `energy_out_low` | Meterstand teruglevering laag tarief, kWh. |
| `e_uit_normaal_cum__kWh` | number | `energy_out_norm` | Meterstand teruglevering normaal tarief, kWh. |
| `p__W` | number | `power` | Vermogen; positief bij afname, negatief bij teruglevering (tekenconventie van de bron). |
| `e_in_cum__kWh` | number | `total_energy_in` | Meterstand totale afname, kWh. |
| `e_uit_cum__kWh` | number | `total_energy_out` | Meterstand totale teruglevering, kWh. |

### `detail_ruw/flowHeatSpaceHeating`

Getrouwe kopie van tabblad flowHeatSpaceHeating van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/flowHeatSpaceHeating.parquet`. Rijen: 198.956.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `temp_aanvoer__degC` | number | `flow_temp` | Aanvoertemperatuur van de warmtemeter. |
| `temp_retour__degC` | number | `return_temp` | Retourtemperatuur van de warmtemeter. |
| `q_cum__GJ` | number | `total_energyGJ` | Meterstand geleverde warmte, GJ. |
| `volume_uit_cum__onbekend` | number | `volume_out` | Meterstand volume; eenheid onbekend (vermoedelijk m3 circulatiewater). |

### `detail_ruw/waterFlow`

Getrouwe kopie van tabblad waterFlow van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/waterFlow.parquet`. Rijen: 207.996.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `temp_omgeving__degC` | number | `ambient_temp` | Omgevingstemperatuur (ambient_temp). |
| `temp_stroom_min__degC` | number | `min_flow_temp` | Minimale stroomtemperatuur (min_flow_temp). |
| `volume_uit_cum__onbekend` | number | `volume_out` | Meterstand volume; eenheid onbekend. |

### `detail_ruw/ventilation`

Getrouwe kopie van tabblad ventilation van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/ventilation.parquet`. Rijen: 104.255.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `foutcode__str` | string | `error_code` | Foutcode van de ventilatie-unit. |
| `debiet_afvoer__onbekend` | number | `exhaust_flow` | Afvoerdebiet; eenheid onbekend. |
| `filter__cat` | string | `filter` | Filterstatus, code van de fabrikant. |
| `temp_buiten__degC` | number | `outdoor_temp` | Buitentemperatuur zoals de ventilatie-unit die meet. |
| `temp_ruimte__degC` | number | `room_temp` | Ruimtetemperatuur zoals de ventilatie-unit die meet. |
| `debiet_toevoer__onbekend` | number | `supply_flow` | Toevoerdebiet; eenheid onbekend. |

### `detail_ruw/co2sensor`

Getrouwe kopie van tabblad co2sensor van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/co2sensor.parquet`. Rijen: 208.225.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `co2__ppm` | number | `co2` | CO2-concentratie (eenheid niet toegelicht in de bron; ppm aangenomen). |
| `rv__pct` | number | `humidity` | Relatieve vochtigheid. |
| `temp_ruimte__degC` | number | `temp` | Ruimtetemperatuur van de CO2-sensor. |
| `voc__onbekend` | number | `voc` | VOC-waarde; eenheid onbekend. |

### `detail_ruw/thermostat`

Getrouwe kopie van tabblad thermostat van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/thermostat.parquet`. Rijen: 189.017.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `temp_thermostaat__degC` | number | `temp` | Temperatuur zoals de thermostaat die meet. |

### `detail_ruw/relay1`

Getrouwe kopie van tabblad relay1 van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/relay1.parquet`. Rijen: 189.981.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `status__bool` | boolean | `status` | Relaisstatus, 0 of 1. |

### `detail_ruw/relay2`

Getrouwe kopie van tabblad relay2 van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/relay2.parquet`. Rijen: 189.981.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `status__bool` | boolean | `status` | Relaisstatus, 0 of 1. |

### `detail_ruw/relay24v`

Getrouwe kopie van tabblad relay24v van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/relay24v.parquet`. Rijen: 189.986.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `status__bool` | boolean | `status` | Relaisstatus, 0 of 1. |

### `detail_ruw/immersion`

Getrouwe kopie van tabblad immersion van beide detailwoningen, met nieuwe kolomnamen en types en tijd in lokale tijd; geen andere waarden.
Pad: `data/processed/detail_ruw/immersion.parquet`. Rijen: 208.233.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip` | datetime |  | Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp. |
| `timestamp_bron__s` | integer | `Timestamp` | Oorspronkelijke Unix-seconden (UTC) uit de bron. |
| `status__bool` | boolean | `status` | Status van het element in het vat, 0 of 1. |

### `detail_5min`

Gemeenschappelijk raster van vijf minuten over kalenderjaar 2019, met vermogens uit tellers, steekproeven en vlaggen.
Pad: `data/processed/detail_5min.parquet`. Korrel: woning x 5 minuten. Rijen: 210.240.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip_start` | datetime |  | Begin van het interval [tijdstip_start, tijdstip_start + 5 min), tz-aware Europe/Amsterdam. |
| `p_warmtepomp__W` | number |  | Gemiddeld elektrisch vermogen van de warmtepomp over het interval. Δstand / Δt tussen de intervalgrenzen; leeg als niet gedekt of als de teller daalt. |
| `p_booster__W` | number |  | Gemiddeld elektrisch vermogen van de booster (elektrische bijverwarming). Δstand / Δt tussen de intervalgrenzen; leeg als niet gedekt of als de teller daalt. |
| `p_vatelement__W` | number |  | Gemiddeld elektrisch vermogen van het element in het vat. Δstand / Δt tussen de intervalgrenzen; leeg als niet gedekt of als de teller daalt. |
| `p_wtw__W` | number |  | Gemiddeld elektrisch vermogen van de WTW-regeling (overige gebouwgebonden). Δstand / Δt tussen de intervalgrenzen; leeg als niet gedekt of als de teller daalt. |
| `p_pv_opwek__W` | number |  | Gemiddeld opgewekt vermogen van de zonnepanelen, positief (uit total_energy_out). Δstand / Δt tussen de intervalgrenzen; leeg als niet gedekt of als de teller daalt. |
| `p_net_afname__W` | number |  | Gemiddeld vermogen afgenomen van het net, positief. Δstand / Δt tussen de intervalgrenzen; leeg als niet gedekt of als de teller daalt. |
| `p_net_teruglevering__W` | number |  | Gemiddeld vermogen teruggeleverd aan het net, positief. Δstand / Δt tussen de intervalgrenzen; leeg als niet gedekt of als de teller daalt. |
| `q_ruimte__W` | number |  | Gemiddeld thermisch vermogen geleverd voor ruimteverwarming (uit GJ). Δstand / Δt tussen de intervalgrenzen; leeg als niet gedekt of als de teller daalt. |
| `p_warmtepomp_gedekt__bool` | boolean |  | De tellerstand van energyHeatpump.e_in_cum__kWh kon op beide grenzen van het interval worden geïnterpoleerd (omringende metingen minder dan 15 minuten uit elkaar). |
| `p_warmtepomp_teller_daalt__bool` | boolean |  | De tellerstand van energyHeatpump.e_in_cum__kWh daalt in dit interval; het vermogen is dan leeg. |
| `p_booster_gedekt__bool` | boolean |  | De tellerstand van energyBooster.e_in_cum__kWh kon op beide grenzen van het interval worden geïnterpoleerd (omringende metingen minder dan 15 minuten uit elkaar). |
| `p_booster_teller_daalt__bool` | boolean |  | De tellerstand van energyBooster.e_in_cum__kWh daalt in dit interval; het vermogen is dan leeg. |
| `p_vatelement_gedekt__bool` | boolean |  | De tellerstand van energyImmersion.e_in_cum__kWh kon op beide grenzen van het interval worden geïnterpoleerd (omringende metingen minder dan 15 minuten uit elkaar). |
| `p_vatelement_teller_daalt__bool` | boolean |  | De tellerstand van energyImmersion.e_in_cum__kWh daalt in dit interval; het vermogen is dan leeg. |
| `p_wtw_gedekt__bool` | boolean |  | De tellerstand van energyWtwReg.e_in_cum__kWh kon op beide grenzen van het interval worden geïnterpoleerd (omringende metingen minder dan 15 minuten uit elkaar). |
| `p_wtw_teller_daalt__bool` | boolean |  | De tellerstand van energyWtwReg.e_in_cum__kWh daalt in dit interval; het vermogen is dan leeg. |
| `p_pv_opwek_gedekt__bool` | boolean |  | De tellerstand van solar.e_uit_cum__kWh kon op beide grenzen van het interval worden geïnterpoleerd (omringende metingen minder dan 15 minuten uit elkaar). |
| `p_pv_opwek_teller_daalt__bool` | boolean |  | De tellerstand van solar.e_uit_cum__kWh daalt in dit interval; het vermogen is dan leeg. |
| `p_net_afname_gedekt__bool` | boolean |  | De tellerstand van smartMeter.e_in_cum__kWh kon op beide grenzen van het interval worden geïnterpoleerd (omringende metingen minder dan 15 minuten uit elkaar). |
| `p_net_afname_teller_daalt__bool` | boolean |  | De tellerstand van smartMeter.e_in_cum__kWh daalt in dit interval; het vermogen is dan leeg. |
| `p_net_teruglevering_gedekt__bool` | boolean |  | De tellerstand van smartMeter.e_uit_cum__kWh kon op beide grenzen van het interval worden geïnterpoleerd (omringende metingen minder dan 15 minuten uit elkaar). |
| `p_net_teruglevering_teller_daalt__bool` | boolean |  | De tellerstand van smartMeter.e_uit_cum__kWh daalt in dit interval; het vermogen is dan leeg. |
| `q_ruimte_gedekt__bool` | boolean |  | De tellerstand van flowHeatSpaceHeating.q_cum__GJ kon op beide grenzen van het interval worden geïnterpoleerd (omringende metingen minder dan 15 minuten uit elkaar). |
| `q_ruimte_teller_daalt__bool` | boolean |  | De tellerstand van flowHeatSpaceHeating.q_cum__GJ daalt in dit interval; het vermogen is dan leeg. |
| `heatpump_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad HeatPump binnen het interval; leeg als er geen was. |
| `heatpump_booster_status_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.booster_status. Status van de booster (bijverwarming), 0 of 1. |
| `heatpump_dhw_verboden_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.dhw_prohibit. Warm tapwater geblokkeerd, 0 of 1. |
| `heatpump_foutcode_steekproef__str` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.error_code. Foutcode van de fabrikant, betekenis onbekend. |
| `heatpump_firmware_versie_steekproef__str` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.firmware_version. Firmwareversie van de warmtepomp. |
| `heatpump_temp_aanvoer_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.flow_temp. Aanvoertemperatuur. |
| `heatpump_temp_aanvoer_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_aanvoer_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_dhw_geforceerd_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.force_dhw. Warm tapwater geforceerd, 0 of 1. |
| `heatpump_verwarming_verboden_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.heating_prohibit. Verwarming geblokkeerd, 0 of 1. |
| `heatpump_vakantie_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.holiday. Vakantiestand, 0 of 1. |
| `heatpump_op_mode_steekproef__cat` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.op_mode. Bedrijfsmodus, code van de fabrikant, betekenis onbekend. |
| `heatpump_temp_buiten_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.outdoor_temp. Buitentemperatuur zoals de warmtepomp die meet. |
| `heatpump_temp_buiten_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_buiten_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_temp_retour_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.return_temp. Retourtemperatuur. |
| `heatpump_temp_retour_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_retour_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_temp_ruimte_setpoint_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.room_target_temp. Gewenste ruimtetemperatuur (room_target_temp). |
| `heatpump_temp_ruimte_setpoint_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_ruimte_setpoint_steekproef__degC lag buiten -40 tot 120 graden Celsius of was 0 of lager (kamertemperatuur); de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_temp_ruimte_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.room_temp. Ruimtetemperatuur zoals de warmtepomp die meet. |
| `heatpump_temp_ruimte_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_ruimte_steekproef__degC lag buiten -40 tot 120 graden Celsius of was 0 of lager (kamertemperatuur); de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_system_status_steekproef__cat` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.system_status. Systeemstatus, code van de fabrikant, betekenis onbekend. |
| `heatpump_temp_doel_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.target_temp. Doeltemperatuur (target_temp). |
| `heatpump_temp_doel_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_doel_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_temp_ongespecificeerd_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.temp. Kolom temp van de bron; welke temperatuur dit is, is niet toegelicht. |
| `heatpump_temp_ongespecificeerd_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_ongespecificeerd_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `energyheatpump_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad energyHeatpump binnen het interval; leeg als er geen was. |
| `energyheatpump_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van energyHeatpump.power. Vermogen op het meetmoment (teken zoals in de bron). |
| `energybooster_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad energyBooster binnen het interval; leeg als er geen was. |
| `energybooster_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van energyBooster.power. Vermogen op het meetmoment (teken zoals in de bron). |
| `energyimmersion_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad energyImmersion binnen het interval; leeg als er geen was. |
| `energyimmersion_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van energyImmersion.power. Vermogen op het meetmoment (teken zoals in de bron). |
| `energywtwreg_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad energyWtwReg binnen het interval; leeg als er geen was. |
| `energywtwreg_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van energyWtwReg.power. Vermogen op het meetmoment (teken zoals in de bron). |
| `solar_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad solar binnen het interval; leeg als er geen was. |
| `solar_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van solar.power. Vermogen; negatief bij opwek (tekenconventie van de bron, niet omgedraaid). |
| `solar_e_in_cum_steekproef__kWh` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van solar.total_energy_in. Meterstand ingaande energie, kWh. |
| `smartmeter_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad smartMeter binnen het interval; leeg als er geen was. |
| `smartmeter_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van smartMeter.power. Vermogen; positief bij afname, negatief bij teruglevering (tekenconventie van de bron). |
| `flowheatspaceheating_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad flowHeatSpaceHeating binnen het interval; leeg als er geen was. |
| `flowheatspaceheating_temp_aanvoer_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van flowHeatSpaceHeating.flow_temp. Aanvoertemperatuur van de warmtemeter. |
| `flowheatspaceheating_temp_aanvoer_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van flowheatspaceheating_temp_aanvoer_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `flowheatspaceheating_temp_retour_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van flowHeatSpaceHeating.return_temp. Retourtemperatuur van de warmtemeter. |
| `flowheatspaceheating_temp_retour_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van flowheatspaceheating_temp_retour_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `flowheatspaceheating_volume_uit_cum_steekproef__onbekend` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van flowHeatSpaceHeating.volume_out. Meterstand volume; eenheid onbekend (vermoedelijk m3 circulatiewater). |
| `waterflow_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad waterFlow binnen het interval; leeg als er geen was. |
| `waterflow_temp_omgeving_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van waterFlow.ambient_temp. Omgevingstemperatuur (ambient_temp). |
| `waterflow_temp_omgeving_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van waterflow_temp_omgeving_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `waterflow_temp_stroom_min_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van waterFlow.min_flow_temp. Minimale stroomtemperatuur (min_flow_temp). |
| `waterflow_temp_stroom_min_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van waterflow_temp_stroom_min_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `waterflow_volume_uit_cum_steekproef__onbekend` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van waterFlow.volume_out. Meterstand volume; eenheid onbekend. |
| `ventilation_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad ventilation binnen het interval; leeg als er geen was. |
| `ventilation_foutcode_steekproef__str` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.error_code. Foutcode van de ventilatie-unit. |
| `ventilation_debiet_afvoer_steekproef__onbekend` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.exhaust_flow. Afvoerdebiet; eenheid onbekend. |
| `ventilation_filter_steekproef__cat` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.filter. Filterstatus, code van de fabrikant. |
| `ventilation_temp_buiten_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.outdoor_temp. Buitentemperatuur zoals de ventilatie-unit die meet. |
| `ventilation_temp_buiten_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van ventilation_temp_buiten_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `ventilation_temp_ruimte_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.room_temp. Ruimtetemperatuur zoals de ventilatie-unit die meet. |
| `ventilation_temp_ruimte_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van ventilation_temp_ruimte_steekproef__degC lag buiten -40 tot 120 graden Celsius of was 0 of lager (kamertemperatuur); de waarde is dan leeg, de ruwe laag houdt hem. |
| `ventilation_debiet_toevoer_steekproef__onbekend` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.supply_flow. Toevoerdebiet; eenheid onbekend. |
| `co2sensor_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad co2sensor binnen het interval; leeg als er geen was. |
| `co2sensor_co2_steekproef__ppm` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van co2sensor.co2. CO2-concentratie (eenheid niet toegelicht in de bron; ppm aangenomen). |
| `co2sensor_rv_steekproef__pct` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van co2sensor.humidity. Relatieve vochtigheid. |
| `co2sensor_temp_ruimte_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van co2sensor.temp. Ruimtetemperatuur van de CO2-sensor. |
| `co2sensor_temp_ruimte_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van co2sensor_temp_ruimte_steekproef__degC lag buiten -40 tot 120 graden Celsius of was 0 of lager (kamertemperatuur); de waarde is dan leeg, de ruwe laag houdt hem. |
| `co2sensor_voc_steekproef__onbekend` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van co2sensor.voc. VOC-waarde; eenheid onbekend. |
| `thermostat_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad thermostat binnen het interval; leeg als er geen was. |
| `thermostat_temp_thermostaat_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van thermostat.temp. Temperatuur zoals de thermostaat die meet. |
| `thermostat_temp_thermostaat_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van thermostat_temp_thermostaat_steekproef__degC lag buiten -40 tot 120 graden Celsius of was 0 of lager (kamertemperatuur); de waarde is dan leeg, de ruwe laag houdt hem. |
| `relay1_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad relay1 binnen het interval; leeg als er geen was. |
| `relay1_status_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van relay1.status. Relaisstatus, 0 of 1. |
| `relay2_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad relay2 binnen het interval; leeg als er geen was. |
| `relay2_status_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van relay2.status. Relaisstatus, 0 of 1. |
| `relay24v_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad relay24v binnen het interval; leeg als er geen was. |
| `relay24v_status_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van relay24v.status. Relaisstatus, 0 of 1. |
| `immersion_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad immersion binnen het interval; leeg als er geen was. |
| `immersion_status_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van immersion.status. Status van het element in het vat, 0 of 1. |

### `detail_kwartier`

Drie intervallen van vijf minuten opgeteld tot een kwartier.
Pad: `data/processed/detail_kwartier.parquet`. Korrel: woning x kwartier. Rijen: 70.080.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode (W_ plus de code uit de bestandsnaam). |
| `tijdstip_start` | datetime |  | Begin van het kwartier [tijdstip_start, tijdstip_start + 15 min), tz-aware Europe/Amsterdam. |
| `p_warmtepomp__W` | number |  | Gemiddeld elektrisch vermogen van de warmtepomp over het interval. Gemiddelde van drie intervallen van vijf minuten; alleen als alle drie gedekt zijn. |
| `p_booster__W` | number |  | Gemiddeld elektrisch vermogen van de booster (elektrische bijverwarming). Gemiddelde van drie intervallen van vijf minuten; alleen als alle drie gedekt zijn. |
| `p_vatelement__W` | number |  | Gemiddeld elektrisch vermogen van het element in het vat. Gemiddelde van drie intervallen van vijf minuten; alleen als alle drie gedekt zijn. |
| `p_wtw__W` | number |  | Gemiddeld elektrisch vermogen van de WTW-regeling (overige gebouwgebonden). Gemiddelde van drie intervallen van vijf minuten; alleen als alle drie gedekt zijn. |
| `p_pv_opwek__W` | number |  | Gemiddeld opgewekt vermogen van de zonnepanelen, positief (uit total_energy_out). Gemiddelde van drie intervallen van vijf minuten; alleen als alle drie gedekt zijn. |
| `p_net_afname__W` | number |  | Gemiddeld vermogen afgenomen van het net, positief. Gemiddelde van drie intervallen van vijf minuten; alleen als alle drie gedekt zijn. |
| `p_net_teruglevering__W` | number |  | Gemiddeld vermogen teruggeleverd aan het net, positief. Gemiddelde van drie intervallen van vijf minuten; alleen als alle drie gedekt zijn. |
| `q_ruimte__W` | number |  | Gemiddeld thermisch vermogen geleverd voor ruimteverwarming (uit GJ). Gemiddelde van drie intervallen van vijf minuten; alleen als alle drie gedekt zijn. |
| `p_warmtepomp_onvolledig__bool` | boolean |  | Minstens een van de drie intervallen van vijf minuten had geen vermogen (niet gedekt of dalende teller); het kwartiergemiddelde is dan leeg. |
| `p_booster_onvolledig__bool` | boolean |  | Minstens een van de drie intervallen van vijf minuten had geen vermogen (niet gedekt of dalende teller); het kwartiergemiddelde is dan leeg. |
| `p_vatelement_onvolledig__bool` | boolean |  | Minstens een van de drie intervallen van vijf minuten had geen vermogen (niet gedekt of dalende teller); het kwartiergemiddelde is dan leeg. |
| `p_wtw_onvolledig__bool` | boolean |  | Minstens een van de drie intervallen van vijf minuten had geen vermogen (niet gedekt of dalende teller); het kwartiergemiddelde is dan leeg. |
| `p_pv_opwek_onvolledig__bool` | boolean |  | Minstens een van de drie intervallen van vijf minuten had geen vermogen (niet gedekt of dalende teller); het kwartiergemiddelde is dan leeg. |
| `p_net_afname_onvolledig__bool` | boolean |  | Minstens een van de drie intervallen van vijf minuten had geen vermogen (niet gedekt of dalende teller); het kwartiergemiddelde is dan leeg. |
| `p_net_teruglevering_onvolledig__bool` | boolean |  | Minstens een van de drie intervallen van vijf minuten had geen vermogen (niet gedekt of dalende teller); het kwartiergemiddelde is dan leeg. |
| `q_ruimte_onvolledig__bool` | boolean |  | Minstens een van de drie intervallen van vijf minuten had geen vermogen (niet gedekt of dalende teller); het kwartiergemiddelde is dan leeg. |
| `heatpump_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad HeatPump binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `heatpump_booster_status_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.booster_status. Status van de booster (bijverwarming), 0 of 1. Van het laatste interval van het kwartier. |
| `heatpump_dhw_verboden_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.dhw_prohibit. Warm tapwater geblokkeerd, 0 of 1. Van het laatste interval van het kwartier. |
| `heatpump_foutcode_steekproef__str` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.error_code. Foutcode van de fabrikant, betekenis onbekend. Van het laatste interval van het kwartier. |
| `heatpump_firmware_versie_steekproef__str` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.firmware_version. Firmwareversie van de warmtepomp. Van het laatste interval van het kwartier. |
| `heatpump_temp_aanvoer_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.flow_temp. Aanvoertemperatuur. Van het laatste interval van het kwartier. |
| `heatpump_temp_aanvoer_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_aanvoer_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_dhw_geforceerd_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.force_dhw. Warm tapwater geforceerd, 0 of 1. Van het laatste interval van het kwartier. |
| `heatpump_verwarming_verboden_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.heating_prohibit. Verwarming geblokkeerd, 0 of 1. Van het laatste interval van het kwartier. |
| `heatpump_vakantie_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.holiday. Vakantiestand, 0 of 1. Van het laatste interval van het kwartier. |
| `heatpump_op_mode_steekproef__cat` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.op_mode. Bedrijfsmodus, code van de fabrikant, betekenis onbekend. Van het laatste interval van het kwartier. |
| `heatpump_temp_buiten_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.outdoor_temp. Buitentemperatuur zoals de warmtepomp die meet. Van het laatste interval van het kwartier. |
| `heatpump_temp_buiten_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_buiten_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_temp_retour_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.return_temp. Retourtemperatuur. Van het laatste interval van het kwartier. |
| `heatpump_temp_retour_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_retour_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_temp_ruimte_setpoint_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.room_target_temp. Gewenste ruimtetemperatuur (room_target_temp). Van het laatste interval van het kwartier. |
| `heatpump_temp_ruimte_setpoint_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_ruimte_setpoint_steekproef__degC lag buiten -40 tot 120 graden Celsius of was 0 of lager (kamertemperatuur); de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_temp_ruimte_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.room_temp. Ruimtetemperatuur zoals de warmtepomp die meet. Van het laatste interval van het kwartier. |
| `heatpump_temp_ruimte_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_ruimte_steekproef__degC lag buiten -40 tot 120 graden Celsius of was 0 of lager (kamertemperatuur); de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_system_status_steekproef__cat` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.system_status. Systeemstatus, code van de fabrikant, betekenis onbekend. Van het laatste interval van het kwartier. |
| `heatpump_temp_doel_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.target_temp. Doeltemperatuur (target_temp). Van het laatste interval van het kwartier. |
| `heatpump_temp_doel_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_doel_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `heatpump_temp_ongespecificeerd_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van HeatPump.temp. Kolom temp van de bron; welke temperatuur dit is, is niet toegelicht. Van het laatste interval van het kwartier. |
| `heatpump_temp_ongespecificeerd_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van heatpump_temp_ongespecificeerd_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `energyheatpump_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad energyHeatpump binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `energyheatpump_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van energyHeatpump.power. Vermogen op het meetmoment (teken zoals in de bron). Van het laatste interval van het kwartier. |
| `energybooster_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad energyBooster binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `energybooster_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van energyBooster.power. Vermogen op het meetmoment (teken zoals in de bron). Van het laatste interval van het kwartier. |
| `energyimmersion_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad energyImmersion binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `energyimmersion_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van energyImmersion.power. Vermogen op het meetmoment (teken zoals in de bron). Van het laatste interval van het kwartier. |
| `energywtwreg_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad energyWtwReg binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `energywtwreg_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van energyWtwReg.power. Vermogen op het meetmoment (teken zoals in de bron). Van het laatste interval van het kwartier. |
| `solar_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad solar binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `solar_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van solar.power. Vermogen; negatief bij opwek (tekenconventie van de bron, niet omgedraaid). Van het laatste interval van het kwartier. |
| `solar_e_in_cum_steekproef__kWh` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van solar.total_energy_in. Meterstand ingaande energie, kWh. Van het laatste interval van het kwartier. |
| `smartmeter_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad smartMeter binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `smartmeter_p_steekproef__W` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van smartMeter.power. Vermogen; positief bij afname, negatief bij teruglevering (tekenconventie van de bron). Van het laatste interval van het kwartier. |
| `flowheatspaceheating_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad flowHeatSpaceHeating binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `flowheatspaceheating_temp_aanvoer_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van flowHeatSpaceHeating.flow_temp. Aanvoertemperatuur van de warmtemeter. Van het laatste interval van het kwartier. |
| `flowheatspaceheating_temp_aanvoer_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van flowheatspaceheating_temp_aanvoer_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `flowheatspaceheating_temp_retour_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van flowHeatSpaceHeating.return_temp. Retourtemperatuur van de warmtemeter. Van het laatste interval van het kwartier. |
| `flowheatspaceheating_temp_retour_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van flowheatspaceheating_temp_retour_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `flowheatspaceheating_volume_uit_cum_steekproef__onbekend` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van flowHeatSpaceHeating.volume_out. Meterstand volume; eenheid onbekend (vermoedelijk m3 circulatiewater). Van het laatste interval van het kwartier. |
| `waterflow_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad waterFlow binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `waterflow_temp_omgeving_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van waterFlow.ambient_temp. Omgevingstemperatuur (ambient_temp). Van het laatste interval van het kwartier. |
| `waterflow_temp_omgeving_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van waterflow_temp_omgeving_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `waterflow_temp_stroom_min_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van waterFlow.min_flow_temp. Minimale stroomtemperatuur (min_flow_temp). Van het laatste interval van het kwartier. |
| `waterflow_temp_stroom_min_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van waterflow_temp_stroom_min_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `waterflow_volume_uit_cum_steekproef__onbekend` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van waterFlow.volume_out. Meterstand volume; eenheid onbekend. Van het laatste interval van het kwartier. |
| `ventilation_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad ventilation binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `ventilation_foutcode_steekproef__str` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.error_code. Foutcode van de ventilatie-unit. Van het laatste interval van het kwartier. |
| `ventilation_debiet_afvoer_steekproef__onbekend` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.exhaust_flow. Afvoerdebiet; eenheid onbekend. Van het laatste interval van het kwartier. |
| `ventilation_filter_steekproef__cat` | string |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.filter. Filterstatus, code van de fabrikant. Van het laatste interval van het kwartier. |
| `ventilation_temp_buiten_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.outdoor_temp. Buitentemperatuur zoals de ventilatie-unit die meet. Van het laatste interval van het kwartier. |
| `ventilation_temp_buiten_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van ventilation_temp_buiten_steekproef__degC lag buiten -40 tot 120 graden Celsius; de waarde is dan leeg, de ruwe laag houdt hem. |
| `ventilation_temp_ruimte_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.room_temp. Ruimtetemperatuur zoals de ventilatie-unit die meet. Van het laatste interval van het kwartier. |
| `ventilation_temp_ruimte_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van ventilation_temp_ruimte_steekproef__degC lag buiten -40 tot 120 graden Celsius of was 0 of lager (kamertemperatuur); de waarde is dan leeg, de ruwe laag houdt hem. |
| `ventilation_debiet_toevoer_steekproef__onbekend` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van ventilation.supply_flow. Toevoerdebiet; eenheid onbekend. Van het laatste interval van het kwartier. |
| `co2sensor_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad co2sensor binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `co2sensor_co2_steekproef__ppm` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van co2sensor.co2. CO2-concentratie (eenheid niet toegelicht in de bron; ppm aangenomen). Van het laatste interval van het kwartier. |
| `co2sensor_rv_steekproef__pct` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van co2sensor.humidity. Relatieve vochtigheid. Van het laatste interval van het kwartier. |
| `co2sensor_temp_ruimte_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van co2sensor.temp. Ruimtetemperatuur van de CO2-sensor. Van het laatste interval van het kwartier. |
| `co2sensor_temp_ruimte_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van co2sensor_temp_ruimte_steekproef__degC lag buiten -40 tot 120 graden Celsius of was 0 of lager (kamertemperatuur); de waarde is dan leeg, de ruwe laag houdt hem. |
| `co2sensor_voc_steekproef__onbekend` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van co2sensor.voc. VOC-waarde; eenheid onbekend. Van het laatste interval van het kwartier. |
| `thermostat_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad thermostat binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `thermostat_temp_thermostaat_steekproef__degC` | number |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van thermostat.temp. Temperatuur zoals de thermostaat die meet. Van het laatste interval van het kwartier. |
| `thermostat_temp_thermostaat_steekproef_buiten_bereik__bool` | boolean |  | De ruwe waarde van thermostat_temp_thermostaat_steekproef__degC lag buiten -40 tot 120 graden Celsius of was 0 of lager (kamertemperatuur); de waarde is dan leeg, de ruwe laag houdt hem. |
| `relay1_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad relay1 binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `relay1_status_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van relay1.status. Relaisstatus, 0 of 1. Van het laatste interval van het kwartier. |
| `relay2_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad relay2 binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `relay2_status_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van relay2.status. Relaisstatus, 0 of 1. Van het laatste interval van het kwartier. |
| `relay24v_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad relay24v binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `relay24v_status_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van relay24v.status. Relaisstatus, 0 of 1. Van het laatste interval van het kwartier. |
| `immersion_tijdstip_steekproef` | datetime |  | Tijdstip van de laatste meting van tabblad immersion binnen het interval; leeg als er geen was. Van het laatste interval van het kwartier. |
| `immersion_status_steekproef__bool` | boolean |  | Steekproef (laatste meting binnen het interval, geen gemiddelde) van immersion.status. Status van het element in het vat, 0 of 1. Van het laatste interval van het kwartier. |

### `controle_jaartotalen`

De jaartotalen uit de detaildata tegenover die in de jaartotalen.
Pad: `data/processed/controle_jaartotalen.parquet`. Korrel: woning x grootheid x definitie. Rijen: 24.

| kolom | type | bron | beschrijving |
|---|---|---|---|
| `woningcode__str` | string |  | Woningcode van een van de twee detailwoningen. |
| `grootheid__str` | string |  | Gecontroleerde grootheid: e_opwekker_totaal, q_ruimte, e_opwek of e_gebouw_overig. |
| `definitie__str` | string |  | raster_som: som van de intervallen in detail_5min (alleen de gedekte intervallen, dus zonder de energie in gaten); raster_som_met_gaten: raster_som plus de tellervoortgang in de niet-gedekte stukken, die niet aan intervallen wordt toegerekend; reeks_delta: eindstand min beginstand van de hele ruwe reeks. |
| `uit_detail` | number |  | Waarde afgeleid uit de detaildata. |
| `uit_jaartotaal` | number |  | Waarde in het werkboek met jaartotalen. |
| `eenheid__str` | string |  | Eenheid van beide waarden (kWh of GJ). |
| `afwijking__pct` | number |  | Afwijking van uit_detail ten opzichte van uit_jaartotaal, in procenten. |
| `binnen_tolerantie__bool` | boolean |  | De absolute afwijking is hoogstens 0,5 %. |

