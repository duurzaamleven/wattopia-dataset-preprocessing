"""De vertaaltabellen van ontwerp §4 als data: bronkolom naar uitvoerkolom, type en beschrijving.

Alles wat een kolom beschrijft staat hier, op één plek. ``tabellen.py`` bouwt eruit de tabellen en de
Arrow-schema's, ``datapackage.py`` en de datacatalogus lezen er de beschrijvingen uit, en een toets
borgt dat de uitvoer precies deze kolommen heeft.

Typen: ``str``, ``int``, ``float``, ``bool``, ``cat`` (tekst uit een keuzelijst of een code van de
fabrikant), ``tijd`` (tz-aware, ``Europe/Amsterdam``).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Kolom:
    naam: str
    type: str
    beschrijving: str
    #: naam in de bron (leeg voor kolommen die de pijplijn zelf toevoegt)
    bron: str = ""
    #: kolom van het tabblad ``keuzemenu`` waartegen de waarden worden gecontroleerd
    menu: str = ""


# --------------------------------------------------------------------------------------------
# projecten (ontwerp §4.1)
# --------------------------------------------------------------------------------------------

PROJECTEN: list[Kolom] = [
    Kolom("projectcode__str", "str", "Willekeurige projectcode uit de anonimisering.", "Projectcode"),
    Kolom("woningen_met_monitoring__0", "int", "Aantal woningen in het project met monitoringdata (verhuld, zie codeboek).", "Monitoringdata"),
    Kolom("knmi_station__str", "str", "KNMI-weerstation dat bij het project hoort; geen locatie van de woning.", "KNMI Weerstation"),
    Kolom("bouwjaar_afgerond__0", "int", "Bouwjaar, afgerond door de anonimisering.", "Bouwjaar afgerond"),
    Kolom("renovatiejaar_afgerond__0", "int", "Renovatiejaar, afgerond door de anonimisering.", "Renovatiejaar afgerond"),
    Kolom("gebruiksoppervlak_afgerond__m2", "int", "Gebruiksoppervlak, afgerond door de anonimisering.", "Gebruiksoppervlak afgerond"),
    Kolom("woningtypologie__cat", "cat", "Woningtypologie volgens het keuzemenu.", "Woningtypologie", "Woningtypologie"),
    Kolom("epv__bool", "bool", "Energieprestatievergoeding (ja/nee).", "EPV"),
    Kolom("actieve_koeling__bool", "bool", "Actieve koeling aanwezig (ja/nee).", "Actieve koeling"),
    Kolom("netto_warmtevraag_klasse__cat", "cat", "Klasse van de netto warmtevraag na renovatie.", "Netto warmtevraag na renovatie", "Netto warmtevraag na renovatie"),
    Kolom("luchtdichtheid_qv10_klasse__cat", "cat", "Klasse van de luchtdichtheid (qv;10).", "Luchtdichtheid", "Luchtdichtheid"),
    Kolom("spouwmuurisolatie__bool", "bool", "Spouwmuurisolatie (ja/nee).", "Spouwmuurisolatie"),
    Kolom("gevelisolatie_binnen__bool", "bool", "Gevelisolatie aan de binnenzijde (ja/nee).", "Gevelisolatie binnenzijde"),
    Kolom("gevelisolatie_buiten__bool", "bool", "Gevelisolatie aan de buitenzijde (ja/nee).", "Gevelisolatie buitenzijde"),
    Kolom("dakisolatie_binnen__bool", "bool", "Dakisolatie aan de binnenzijde (ja/nee).", "Dakisolatie binnenzijde"),
    Kolom("dakisolatie_buiten__bool", "bool", "Dakisolatie aan de buitenzijde (ja/nee).", "Dakisolatie buitenzijde"),
    Kolom("vloerisolatie__bool", "bool", "Vloerisolatie (ja/nee).", "Vloerisolatie"),
    Kolom("kozijnen_nieuw_hrpp__bool", "bool", "Nieuwe kozijnen met tenminste HR++-glas (ja/nee).", "Nieuwe kozijnen met tenminste hr++ glas"),
    Kolom("kozijnen_bestaand_hrpp__bool", "bool", "Bestaande kozijnen met tenminste HR++-glas (ja/nee).", "Bestaande kozijnen met tenminste hr++ glas"),
    Kolom("kierdichting__bool", "bool", "Kierdichting (ja/nee).", "Kierdichting"),
    Kolom("bijzonderheden_schil__str", "str", "Vrije tekst over de schil.", "Bijzonderheden schil"),
    Kolom("opwekking_collectief__cat", "cat", "Individuele of collectieve opwekking.", "Individueel of collectief", "Individueel of collectief"),
    Kolom("warmteopwekker__cat", "cat", "Type warmteopwekker.", "Warmteopwekker", "Warmteopwekker"),
    Kolom("bron_warmteopwekker__cat", "cat", "Bron van de warmteopwekker.", "Bron van de warmteopwekker", "Bron van de warmteopwekker"),
    Kolom("afgiftesysteem__cat", "cat", "Afgiftesysteem.", "Afgiftesysteem", "Afgiftesysteem"),
    Kolom("ventilatiesysteem__cat", "cat", "Ventilatiesysteem.", "Ventilatiesysteem", "Ventilatiesysteem"),
    Kolom("elektrische_opwekking__cat", "cat", "Elektrische opwekking (kolom Energieopweksysteem in het keuzemenu).", "Elektrische opwekking", "Energieopweksysteem"),
    Kolom("kookinstallatie__cat", "cat", "Kookinstallatie.", "Kookinstallatie", "Kookinstallatie"),
    Kolom("bijzonderheden_installaties__str", "str", "Vrije tekst over de installaties.", "Bijzonderheden installaties"),
]

#: Kolomnaam waarmee de vlag "waarde staat niet in het keuzemenu" heet.
def buiten_keuzemenu_naam(kolom: str) -> str:
    stam = kolom.rsplit("__", 1)[0]
    return f"{stam}_buiten_keuzemenu__bool"


PROJECTEN_VLAGGEN: list[Kolom] = [
    Kolom(buiten_keuzemenu_naam(k.naam), "bool",
          f"Waarde van {k.naam} staat niet in het keuzemenu (kolom {k.menu}), na normalisatie van de "
          "aanhalingstekens; de oorspronkelijke tekst is behouden.")
    for k in PROJECTEN if k.menu
]

# --------------------------------------------------------------------------------------------
# woningen_jaar (ontwerp §4.2)
# --------------------------------------------------------------------------------------------

WONINGEN: list[Kolom] = [
    Kolom("projectcode__str", "str", "Willekeurige projectcode; verwijst naar projecten.", "PROJECTCODE"),
    Kolom("woningcode__str", "str", "Willekeurige woningcode uit de anonimisering.", "WONINGCODE"),
    Kolom("jaar_monitoring__0", "int", "Kalenderjaar van de monitoring.", "JAARTAL MONITORING"),
    Kolom("e_opwek__kWh_a_1", "float", "Opgewekte energie (zonnepanelen).", "Opgewekte energie"),
    Kolom("e_opwekker_ruimte__kWh_a_1", "float", "Elektriciteit voor ruimteverwarming door de warmteopwekker(s).", "Gebruikte energie voor ruimteverwarming"),
    Kolom("e_opwekker_tapwater__kWh_a_1", "float", "Elektriciteit voor warm tapwater door de warmteopwekker(s).", "Gebruikte energie voor warm tapwater"),
    Kolom("e_opwekker_totaal__kWh_a_1", "float", "Totaal gebruikte elektriciteit door de warmteopwekker(s); in de detaildata warmtepomp plus booster.", "Totaal gebruikte energie door de warmteopwekker(s)"),
    Kolom("q_ruimte__GJ_a_1", "float", "Geleverde warmte voor ruimteverwarming.", "Geleverde warmte voor ruimteverwarming"),
    Kolom("q_tapwater__GJ_a_1", "float", "Geleverde warmte voor warm tapwater.", "Geleverde warmte voor warm tapwater"),
    Kolom("q_totaal__GJ_a_1", "float", "Totaal geleverde warmte.", "Totaal geleverde warmte"),
    Kolom("e_gebouw_overig__kWh_a_1", "float", "Elektriciteit voor overige gebouwgebonden functies (in de detaildata de WTW-regeling).", "Gebruikte energie voor overige gebouwgebonden functies"),
    Kolom("e_beschikbaar_persoonlijk__kWh_a_1", "float", "Elektriciteit beschikbaar voor persoonlijk gebruik; mag negatief zijn.", "Beschikbaar voor persoonlijk gebruik"),
    Kolom("e_persoonlijk__kWh_a_1", "float", "Daadwerkelijk persoonlijk elektriciteitsgebruik.", "Daadwerkelijk persoonlijk gebruik"),
    Kolom("co2_stookseizoen__ppm", "float", "Luchtkwaliteit, CO2 in het stookseizoen.", "Luchtkwaliteit [CO2]"),
    Kolom("rv_stookseizoen__pct", "float", "Luchtkwaliteit, relatieve vochtigheid in het stookseizoen.", "Luchtkwaliteit [%RV]"),
    Kolom("gas_voor_renovatie__m3_a_1", "float", "Gasverbruik voor de renovatie.", "Gasverbruik voor renovatie"),
    Kolom("e_voor_renovatie__kWh_a_1", "float", "Elektriciteitsgebruik voor de renovatie.", "Elektragebruik voor renovatie"),
    Kolom("ligging__cat", "cat", "Ligging van de woning (hoek of tussen).", "Ligging woning"),
    Kolom("e_bundel_beloofd__kWh_a_1", "float", "Beloofde bundel voor huishoudelijk gebruik.", "Beloofde bundel voor huishoudelijk gebruik"),
    Kolom("e_netto_afname__kWh_a_1", "float", "Netto afname van het net; mag negatief zijn.", "Netto afname grid"),
    Kolom("temp_woonkamer_stookseizoen__degC", "float", "Gemeten temperatuur in de woonkamer in het stookseizoen.", "Temperatuur woonkamer"),
    Kolom("temp_setpoint_woonkamer_stookseizoen__degC", "float", "Ingesteld setpoint van de woonkamer in het stookseizoen.", "Setpoint temperatuur woonkamer"),
]

#: Grootheden waarvoor een negatieve waarde verdacht is (ontwerp §4.2).
ENERGIE_GROOTHEDEN_NIET_NEGATIEF: list[str] = [
    k.naam for k in WONINGEN
    if (k.naam.endswith("__kWh_a_1") or k.naam.endswith("__GJ_a_1"))
    and k.naam not in ("e_beschikbaar_persoonlijk__kWh_a_1", "e_netto_afname__kWh_a_1")
]

WONINGEN_VLAGGEN: list[Kolom] = [
    Kolom("negatieve_waarde__bool", "bool",
          "Regel: een energie- of warmtegrootheid (kWh of GJ per jaar) is kleiner dan 0, behalve "
          "e_beschikbaar_persoonlijk en e_netto_afname, die negatief mogen zijn."),
    Kolom("setpoint_nul__bool", "bool", "Regel: het setpoint van de woonkamer is 0 graden Celsius."),
    Kolom("som_opwekker_klopt_niet__bool", "bool",
          "Regel: ruimte, tapwater en totaal van de warmteopwekker zijn alle drie gevuld en het totaal "
          "wijkt meer dan 1 % af van de som. Leeg als niet alle drie gevuld zijn."),
    Kolom("som_warmte_klopt_niet__bool", "bool",
          "Regel: geleverde warmte voor ruimte, tapwater en totaal zijn alle drie gevuld en het totaal "
          "wijkt meer dan 1 % af van de som. Leeg als niet alle drie gevuld zijn."),
    Kolom("balans_beschikbaar_klopt_niet__bool", "bool",
          "Regel: opwek, totaal opwekker en overig gebouwgebonden zijn gevuld, en beschikbaar voor "
          "persoonlijk gebruik wijkt meer dan 1 % (en meer dan 10 kWh) af van opwek min totaal opwekker "
          "min overig. Leeg als een van de drie ontbreekt. Een afwijking is een definitieverschil of "
          "een meetfout; de pijplijn beslist dat niet."),
]

# --------------------------------------------------------------------------------------------
# detail_ruw (ontwerp §4.3): per meetpunt de bronkolommen met hun nieuwe naam
# --------------------------------------------------------------------------------------------

DETAIL_VOORKOP: list[Kolom] = [
    Kolom("woningcode__str", "str", "Woningcode (W_ plus de code uit de bestandsnaam)."),
    Kolom("tijdstip", "tijd", "Tijdstip van de meting, tz-aware Europe/Amsterdam, uit Timestamp."),
    Kolom("timestamp_bron__s", "int", "Oorspronkelijke Unix-seconden (UTC) uit de bron.", "Timestamp"),
]

_ENERGIE_TELLER = [
    Kolom("p__W", "float", "Vermogen op het meetmoment (teken zoals in de bron).", "power"),
    Kolom("e_in_cum__kWh", "float", "Meterstand van de energie, kWh (eenheid afgeleid en getoetst tegen de jaartotalen).", "total_energy_in"),
]

DETAIL_MEETPUNTEN: dict[str, list[Kolom]] = {
    "HeatPump": [
        Kolom("booster_status__bool", "bool", "Status van de booster (bijverwarming), 0 of 1.", "booster_status"),
        Kolom("dhw_verboden__bool", "bool", "Warm tapwater geblokkeerd, 0 of 1.", "dhw_prohibit"),
        Kolom("foutcode__str", "str", "Foutcode van de fabrikant, betekenis onbekend.", "error_code"),
        Kolom("firmware_versie__str", "str", "Firmwareversie van de warmtepomp.", "firmware_version"),
        Kolom("temp_aanvoer__degC", "float", "Aanvoertemperatuur.", "flow_temp"),
        Kolom("dhw_geforceerd__bool", "bool", "Warm tapwater geforceerd, 0 of 1.", "force_dhw"),
        Kolom("verwarming_verboden__bool", "bool", "Verwarming geblokkeerd, 0 of 1.", "heating_prohibit"),
        Kolom("vakantie__bool", "bool", "Vakantiestand, 0 of 1.", "holiday"),
        Kolom("op_mode__cat", "cat", "Bedrijfsmodus, code van de fabrikant, betekenis onbekend.", "op_mode"),
        Kolom("temp_buiten__degC", "float", "Buitentemperatuur zoals de warmtepomp die meet.", "outdoor_temp"),
        Kolom("temp_retour__degC", "float", "Retourtemperatuur.", "return_temp"),
        Kolom("temp_ruimte_setpoint__degC", "float", "Gewenste ruimtetemperatuur (room_target_temp).", "room_target_temp"),
        Kolom("temp_ruimte__degC", "float", "Ruimtetemperatuur zoals de warmtepomp die meet.", "room_temp"),
        Kolom("system_status__cat", "cat", "Systeemstatus, code van de fabrikant, betekenis onbekend.", "system_status"),
        Kolom("temp_doel__degC", "float", "Doeltemperatuur (target_temp).", "target_temp"),
        Kolom("temp_ongespecificeerd__degC", "float", "Kolom temp van de bron; welke temperatuur dit is, is niet toegelicht.", "temp"),
    ],
    "energyHeatpump": list(_ENERGIE_TELLER),
    "energyBooster": list(_ENERGIE_TELLER),
    "energyImmersion": list(_ENERGIE_TELLER),
    "energyWtwReg": list(_ENERGIE_TELLER),
    "solar": [
        Kolom("p__W", "float", "Vermogen; negatief bij opwek (tekenconventie van de bron, niet omgedraaid).", "power"),
        Kolom("e_in_cum__kWh", "float", "Meterstand ingaande energie, kWh.", "total_energy_in"),
        Kolom("e_uit_cum__kWh", "float", "Meterstand opgewekte energie, kWh.", "total_energy_out"),
    ],
    "smartMeter": [
        Kolom("e_in_laag_cum__kWh", "float", "Meterstand afname laag tarief, kWh.", "energy_in_low"),
        Kolom("e_in_normaal_cum__kWh", "float", "Meterstand afname normaal tarief, kWh.", "energy_in_norm"),
        Kolom("e_uit_laag_cum__kWh", "float", "Meterstand teruglevering laag tarief, kWh.", "energy_out_low"),
        Kolom("e_uit_normaal_cum__kWh", "float", "Meterstand teruglevering normaal tarief, kWh.", "energy_out_norm"),
        Kolom("p__W", "float", "Vermogen; positief bij afname, negatief bij teruglevering (tekenconventie van de bron).", "power"),
        Kolom("e_in_cum__kWh", "float", "Meterstand totale afname, kWh.", "total_energy_in"),
        Kolom("e_uit_cum__kWh", "float", "Meterstand totale teruglevering, kWh.", "total_energy_out"),
    ],
    "flowHeatSpaceHeating": [
        Kolom("temp_aanvoer__degC", "float", "Aanvoertemperatuur van de warmtemeter.", "flow_temp"),
        Kolom("temp_retour__degC", "float", "Retourtemperatuur van de warmtemeter.", "return_temp"),
        Kolom("q_cum__GJ", "float", "Meterstand geleverde warmte, GJ.", "total_energyGJ"),
        Kolom("volume_uit_cum__m3", "float", "Meterstand van het circulatiewater van de ruimteverwarming, m3 (resolutie 1 liter). Eenheid afgeleid: warmte, temperatuurverschil en volume sluiten op rho*c*V*dT (ontwerp §9.5).", "volume_out"),
    ],
    "waterFlow": [
        Kolom("temp_omgeving__degC", "float", "Omgevingstemperatuur (ambient_temp).", "ambient_temp"),
        Kolom("temp_stroom_min__degC", "float", "Minimale stroomtemperatuur (min_flow_temp).", "min_flow_temp"),
        Kolom("volume_uit_cum__m3", "float", "Meterstand van het warme tapwater, m3 (resolutie 1 liter); vermoedelijk gemeten aan de koudwaterinlaat van het vat. Eenheid afgeleid uit het dagritme en de warmtebalans in de zomer, niet in de bron gedocumenteerd; of de meter al het warme water meet, is niet vast te stellen (ontwerp §9.5).", "volume_out"),
    ],
    "ventilation": [
        Kolom("foutcode__str", "str", "Foutcode van de ventilatie-unit.", "error_code"),
        Kolom("debiet_afvoer__onbekend", "float", "Afvoerdebiet; eenheid onbekend.", "exhaust_flow"),
        Kolom("filter__cat", "cat", "Filterstatus, code van de fabrikant.", "filter"),
        Kolom("temp_buiten__degC", "float", "Buitentemperatuur zoals de ventilatie-unit die meet.", "outdoor_temp"),
        Kolom("temp_ruimte__degC", "float", "Ruimtetemperatuur zoals de ventilatie-unit die meet.", "room_temp"),
        Kolom("debiet_toevoer__onbekend", "float", "Toevoerdebiet; eenheid onbekend.", "supply_flow"),
    ],
    "co2sensor": [
        Kolom("co2__ppm", "float", "CO2-concentratie (eenheid niet toegelicht in de bron; ppm aangenomen).", "co2"),
        Kolom("rv__pct", "float", "Relatieve vochtigheid.", "humidity"),
        Kolom("temp_ruimte__degC", "float", "Ruimtetemperatuur van de CO2-sensor.", "temp"),
        Kolom("voc__onbekend", "float", "VOC-waarde van de sensor; eenheid onbekend en niet in de bron gedocumenteerd. Waarschijnlijkst een dimensieloze luchtkwaliteitsindex (ondergrens 1,0, resolutie 0,1); niet als concentratie gebruiken (ontwerp §9.5).", "voc"),
    ],
    "thermostat": [
        Kolom("temp_thermostaat__degC", "float", "Temperatuur zoals de thermostaat die meet.", "temp"),
    ],
    "relay1": [Kolom("status__bool", "bool", "Relaisstatus, 0 of 1.", "status")],
    "relay2": [Kolom("status__bool", "bool", "Relaisstatus, 0 of 1.", "status")],
    "relay24v": [Kolom("status__bool", "bool", "Relaisstatus, 0 of 1.", "status")],
    "immersion": [Kolom("status__bool", "bool", "Status van het element in het vat, 0 of 1.", "status")],
}


def stam_en_eenheid(naam: str) -> tuple[str, str]:
    """``temp_aanvoer__degC`` naar ``("temp_aanvoer", "degC")``."""
    stam, _, eenheid = naam.rpartition("__")
    return stam, eenheid


def detail_ruw_kolommen(meetpunt: str) -> list[Kolom]:
    """Alle kolommen van ``detail_ruw/<meetpunt>.parquet``. Een tabblad dat in ``DETAIL_MEETPUNTEN``
    ontbreekt, is een fout: voeg het daar toe met naam, type en beschrijving."""
    if meetpunt not in DETAIL_MEETPUNTEN:
        raise KeyError(f"Tabblad {meetpunt!r} staat niet in kolommen.DETAIL_MEETPUNTEN")
    return DETAIL_VOORKOP + DETAIL_MEETPUNTEN[meetpunt]


# --------------------------------------------------------------------------------------------
# detail_5min en detail_kwartier (ontwerp §4.4)
# --------------------------------------------------------------------------------------------

#: Tijdzone van alle tijdkolommen in de uitvoer.
TIJDZONE = "Europe/Amsterdam"
#: Het kalenderjaar van het raster; beide woningen hebben monitoring in dit jaar.
RASTERJAAR = 2019
STAP_S = 300
#: Maximale afstand tussen twee metingen waartussen een tellerstand mag worden geïnterpoleerd.
MAX_INTERPOLATIEGAT_S = 900
#: Temperaturen buiten dit bereik zijn sentinels (ontwerp §4.4).
TEMP_MIN_DEGC = -40.0
TEMP_MAX_DEGC = 120.0
#: Kamertemperaturen (en het setpoint daarvan): hier is ook een waarde van 0 graden Celsius of lager een
#: sentinel. Het ontwerp (§1.2 en §4.4) noemt alleen exact 0 voor de warmtepomp; de data bevat ook -20 en
#: -100 in de thermostaat (zie ontwerp §9, afwijking 2).
TEMP_KAMER: set[tuple[str, str]] = {
    ("HeatPump", "temp_ruimte__degC"),
    ("HeatPump", "temp_ruimte_setpoint__degC"),
    ("thermostat", "temp_thermostaat__degC"),
    ("ventilation", "temp_ruimte__degC"),
    ("co2sensor", "temp_ruimte__degC"),
}
TEMP_KAMER_ONDERGRENS_DEGC = 0.0


@dataclass(frozen=True)
class Teller:
    """Een vermogenskolom die uit een tellerstand wordt afgeleid."""

    naam: str
    meetpunt: str
    teller: str
    eenheid_teller: str  # kWh of GJ
    beschrijving: str


TELLERS: list[Teller] = [
    Teller("p_warmtepomp__W", "energyHeatpump", "e_in_cum__kWh", "kWh", "Gemiddeld elektrisch vermogen van de warmtepomp over het interval."),
    Teller("p_booster__W", "energyBooster", "e_in_cum__kWh", "kWh", "Gemiddeld elektrisch vermogen van de booster (elektrische bijverwarming)."),
    Teller("p_vatelement__W", "energyImmersion", "e_in_cum__kWh", "kWh", "Gemiddeld elektrisch vermogen van het element in het vat."),
    Teller("p_wtw__W", "energyWtwReg", "e_in_cum__kWh", "kWh", "Gemiddeld elektrisch vermogen van de WTW-regeling (overige gebouwgebonden)."),
    Teller("p_pv_opwek__W", "solar", "e_uit_cum__kWh", "kWh", "Gemiddeld opgewekt vermogen van de zonnepanelen, positief (uit total_energy_out)."),
    Teller("p_net_afname__W", "smartMeter", "e_in_cum__kWh", "kWh", "Gemiddeld vermogen afgenomen van het net, positief."),
    Teller("p_net_teruglevering__W", "smartMeter", "e_uit_cum__kWh", "kWh", "Gemiddeld vermogen teruggeleverd aan het net, positief."),
    Teller("q_ruimte__W", "flowHeatSpaceHeating", "q_cum__GJ", "GJ", "Gemiddeld thermisch vermogen geleverd voor ruimteverwarming (uit GJ)."),
]
_TELLER_KOLOMMEN = {(t.meetpunt, t.teller) for t in TELLERS}


def groepnaam(meetpunt: str) -> str:
    """Voorvoegsel van de steekproefkolommen: de tabbladnaam in kleine letters."""
    return meetpunt.lower()


def steekproef_naam(meetpunt: str, kolom: str) -> str:
    stam, eenheid = stam_en_eenheid(kolom)
    return f"{groepnaam(meetpunt)}_{stam}_steekproef__{eenheid}"


def steekproef_kolommen() -> list[tuple[str, Kolom]]:
    """``(meetpunt, kolom)`` voor elke kolom die als steekproef in ``detail_5min`` komt: alle
    kolommen behalve de tellers waaruit een vermogen wordt afgeleid, en behalve de meterstanden van
    de slimme meter per tarief."""
    uit = []
    for meetpunt, kolommen in DETAIL_MEETPUNTEN.items():
        for k in kolommen:
            if (meetpunt, k.naam) in _TELLER_KOLOMMEN:
                continue
            if meetpunt == "smartMeter" and k.naam.startswith(("e_in_laag", "e_in_normaal", "e_uit_laag", "e_uit_normaal")):
                continue
            uit.append((meetpunt, k))
    return uit


def is_temperatuur(kolom: Kolom) -> bool:
    return kolom.naam.endswith("__degC")


def buiten_bereik_naam(steekproefnaam: str) -> str:
    return steekproefnaam.rpartition("__")[0] + "_buiten_bereik__bool"


def tijdstip_steekproef_naam(meetpunt: str) -> str:
    return f"{groepnaam(meetpunt)}_tijdstip_steekproef"


def detail_5min_kolommen() -> list[Kolom]:
    kolommen = [
        Kolom("woningcode__str", "str", "Woningcode (W_ plus de code uit de bestandsnaam)."),
        Kolom("tijdstip_start", "tijd", "Begin van het interval [tijdstip_start, tijdstip_start + 5 min), tz-aware Europe/Amsterdam."),
    ]
    for t in TELLERS:
        kolommen.append(Kolom(t.naam, "float", t.beschrijving + " Δstand / Δt tussen de intervalgrenzen; leeg als niet gedekt of als de teller daalt."))
    for t in TELLERS:
        stam = t.naam.rpartition("__")[0]
        kolommen.append(Kolom(f"{stam}_gedekt__bool", "bool",
                              f"De tellerstand van {t.meetpunt}.{t.teller} kon op beide grenzen van het interval worden geïnterpoleerd "
                              "(omringende metingen minder dan 15 minuten uit elkaar)."))
        kolommen.append(Kolom(f"{stam}_teller_daalt__bool", "bool",
                              f"De tellerstand van {t.meetpunt}.{t.teller} daalt in dit interval; het vermogen is dan leeg."))
    gezien = set()
    for meetpunt, k in steekproef_kolommen():
        if meetpunt not in gezien:
            gezien.add(meetpunt)
            kolommen.append(Kolom(tijdstip_steekproef_naam(meetpunt), "tijd",
                                  f"Tijdstip van de laatste meting van tabblad {meetpunt} binnen het interval; leeg als er geen was."))
        naam = steekproef_naam(meetpunt, k.naam)
        kolommen.append(Kolom(naam, k.type if k.type != "str" else "str",
                              f"Steekproef (laatste meting binnen het interval, geen gemiddelde) van {meetpunt}.{k.bron}. {k.beschrijving}"))
        if is_temperatuur(k):
            kamer = (meetpunt, k.naam) in TEMP_KAMER
            kolommen.append(Kolom(buiten_bereik_naam(naam), "bool",
                                  f"De ruwe waarde van {naam} lag buiten {TEMP_MIN_DEGC:g} tot {TEMP_MAX_DEGC:g} graden Celsius"
                                  + (f" of was {TEMP_KAMER_ONDERGRENS_DEGC:g} of lager (kamertemperatuur)" if kamer else "")
                                  + "; de waarde is dan leeg, de ruwe laag houdt hem."))
    return kolommen


def detail_kwartier_kolommen() -> list[Kolom]:
    kolommen = [
        Kolom("woningcode__str", "str", "Woningcode (W_ plus de code uit de bestandsnaam)."),
        Kolom("tijdstip_start", "tijd", "Begin van het kwartier [tijdstip_start, tijdstip_start + 15 min), tz-aware Europe/Amsterdam."),
    ]
    for t in TELLERS:
        kolommen.append(Kolom(t.naam, "float", t.beschrijving + " Gemiddelde van drie intervallen van vijf minuten; alleen als alle drie gedekt zijn."))
    for t in TELLERS:
        stam = t.naam.rpartition("__")[0]
        kolommen.append(Kolom(f"{stam}_onvolledig__bool", "bool",
                              "Minstens een van de drie intervallen van vijf minuten had geen vermogen (niet gedekt of dalende teller); "
                              "het kwartiergemiddelde is dan leeg."))
    for k in detail_5min_kolommen()[2 + 3 * len(TELLERS):]:
        kolommen.append(Kolom(k.naam, k.type, k.beschrijving.replace("interval", "laatste interval van het kwartier", 1)
                              if k.naam.endswith("_buiten_bereik__bool") else k.beschrijving + " Van het laatste interval van het kwartier."))
    return kolommen


# --------------------------------------------------------------------------------------------
# controle_jaartotalen (ontwerp §4.5)
# --------------------------------------------------------------------------------------------

CONTROLE: list[Kolom] = [
    Kolom("woningcode__str", "str", "Woningcode van een van de twee detailwoningen."),
    Kolom("grootheid__str", "str", "Gecontroleerde grootheid: e_opwekker_totaal, q_ruimte, e_opwek of e_gebouw_overig."),
    Kolom("definitie__str", "str",
          "raster_som: som van de intervallen in detail_5min (alleen de gedekte intervallen, dus zonder de energie in gaten); "
          "raster_som_met_gaten: raster_som plus de tellervoortgang in de niet-gedekte stukken, die niet aan intervallen "
          "wordt toegerekend; reeks_delta: eindstand min beginstand van de hele ruwe reeks."),
    Kolom("uit_detail", "float", "Waarde afgeleid uit de detaildata."),
    Kolom("uit_jaartotaal", "float", "Waarde in het werkboek met jaartotalen."),
    Kolom("eenheid__str", "str", "Eenheid van beide waarden (kWh of GJ)."),
    Kolom("afwijking__pct", "float", "Afwijking van uit_detail ten opzichte van uit_jaartotaal, in procenten."),
    Kolom("binnen_tolerantie__bool", "bool", "De absolute afwijking is hoogstens 0,5 %."),
]

#: Grootheid naar (kolom in woningen_jaar, bron van de tellers)
CONTROLE_GROOTHEDEN: dict[str, str] = {
    "e_opwekker_totaal": "e_opwekker_totaal__kWh_a_1",
    "q_ruimte": "q_ruimte__GJ_a_1",
    "e_opwek": "e_opwek__kWh_a_1",
    "e_gebouw_overig": "e_gebouw_overig__kWh_a_1",
}
TOLERANTIE_PCT = 0.5

def tabel_kolommen(naam: str) -> list[Kolom]:
    """Alle kolommen van een uitvoertabel, in volgorde."""
    if naam == "projecten":
        uit: list[Kolom] = []
        for k in PROJECTEN:
            uit.append(k)
            if k.menu:
                uit.append(next(v for v in PROJECTEN_VLAGGEN if v.naam == buiten_keuzemenu_naam(k.naam)))
        return uit
    if naam == "woningen_jaar":
        return WONINGEN + WONINGEN_VLAGGEN
    if naam == "detail_5min":
        return detail_5min_kolommen()
    if naam == "detail_kwartier":
        return detail_kwartier_kolommen()
    if naam == "controle_jaartotalen":
        return CONTROLE
    if naam.startswith("detail_ruw/"):
        return detail_ruw_kolommen(naam.split("/", 1)[1])
    raise KeyError(naam)
