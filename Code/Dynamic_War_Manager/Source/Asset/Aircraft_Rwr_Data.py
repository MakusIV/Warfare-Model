"""Ricevitori d'allarme radar (RWR) degli aerei del registro: quali categorie di SAM identificano.

Richiesta dell'utente (2026-09-29, `Analysis/Document/Proposta_Soglia_Rottura_Stocastica.md`
§13): il fuoco senza risposta di una forza aerea va valutato tenendo conto degli aerei che hanno
un RWR in grado di identificare la categoria del SAM che li illumina. Il registro
`Aircraft_Data` non ha questo dato (compare solo nel nome di qualche suite avionica): e' qui,
in una tabella separata, perche' e' una proposta da verificare voce per voce.

Categorie (`Context/Air_Defense_Efficacy.SAM_CATEGORIES`): VSHORAD, SHORAD, MRSAM, LRSAM. Un RWR
"identifica" una categoria se riconosce i radar di tiro/acquisizione dei sistemi di quella
categoria come minaccia di quel tipo (simbolo o classe sul display), non se da' solo un allarme
generico di illuminazione (Sirena, radarvarnare del Viggen): questi ultimi non identificano nulla.

VALORI: PROPOSTA DA VERIFICARE (conoscenza generale, riferimento DCS), con un grado di fiducia
per voce. Un aereo assente dalla tabella = dato mancante, trattato come "nessun RWR".
"""

from typing import Dict, FrozenSet, Optional

VSHORAD = 'VSHORAD'
SHORAD = 'SHORAD'
MRSAM = 'MRSAM'
LRSAM = 'LRSAM'
ALL = frozenset((VSHORAD, SHORAD, MRSAM, LRSAM))
NONE: FrozenSet[str] = frozenset()

# model -> {'rwr': nome del sistema | None, 'identifies': categorie, 'confidence': alta|media|bassa}
AIRCRAFT_RWR: Dict[str, dict] = {
    # ── caccia e attacco occidentali ──
    'A-10A Thunderbolt II':    {'rwr': 'AN/ALR-69', 'identifies': ALL, 'confidence': 'alta'},
    'A-10C Thunderbolt II':    {'rwr': 'AN/ALR-69', 'identifies': ALL, 'confidence': 'alta'},
    'A-10C II Thunderbolt II': {'rwr': 'AN/ALR-69', 'identifies': ALL, 'confidence': 'alta'},
    'A-4E Skyhawk':            {'rwr': 'AN/APR-25', 'identifies': ALL, 'confidence': 'bassa'},
    'AJ/ASJ 37 Viggen':        {'rwr': 'KA radarvarnare', 'identifies': NONE, 'confidence': 'media'},
    'F-117 Nighthawk':         {'rwr': 'RWR (non specificato)', 'identifies': ALL, 'confidence': 'media'},
    'F-14A Tomcat':            {'rwr': 'AN/ALR-45', 'identifies': ALL, 'confidence': 'alta'},
    'F-14B Tomcat':            {'rwr': 'AN/ALR-67', 'identifies': ALL, 'confidence': 'alta'},
    'F-15C Eagle':             {'rwr': 'AN/ALR-56C', 'identifies': ALL, 'confidence': 'alta'},
    'F-15E Strike Eagle':      {'rwr': 'AN/ALR-56C', 'identifies': ALL, 'confidence': 'alta'},
    'F-16A Fighting Falcon':   {'rwr': 'AN/ALR-69', 'identifies': ALL, 'confidence': 'alta'},
    'F-16A MLU':               {'rwr': 'AN/ALR-69', 'identifies': ALL, 'confidence': 'alta'},
    'F-16C Block 52d':         {'rwr': 'AN/ALR-56M', 'identifies': ALL, 'confidence': 'alta'},
    'F-16CM Block 50':         {'rwr': 'AN/ALR-56M', 'identifies': ALL, 'confidence': 'alta'},
    'F-4E Phantom II':         {'rwr': 'AN/ALR-46', 'identifies': ALL, 'confidence': 'alta'},
    'F-5E Tiger II':           {'rwr': 'AN/ALR-87', 'identifies': ALL, 'confidence': 'alta'},
    'F-86E Sabre':             {'rwr': None, 'identifies': NONE, 'confidence': 'alta'},
    'F/A-18A Hornet':          {'rwr': 'AN/ALR-67', 'identifies': ALL, 'confidence': 'alta'},
    'F/A-18C Hornet':          {'rwr': 'AN/ALR-67', 'identifies': ALL, 'confidence': 'alta'},
    'F/A-18C Lot 20':          {'rwr': 'AN/ALR-67', 'identifies': ALL, 'confidence': 'alta'},
    'Mirage 2000C':            {'rwr': 'Serval', 'identifies': ALL, 'confidence': 'alta'},
    # ── caccia e attacco sovietici/russi ──
    'MiG-15bis':               {'rwr': None, 'identifies': NONE, 'confidence': 'alta'},
    'MiG-19P':                 {'rwr': 'Sirena-2', 'identifies': NONE, 'confidence': 'alta'},
    'MiG-21bis':               {'rwr': 'SPO-3 Sirena-3', 'identifies': NONE, 'confidence': 'alta'},
    'MiG-23MLD':               {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'media'},
    'MiG-25PD':                {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'media'},
    'MiG-25RB':                {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'bassa'},
    'MiG-27K':                 {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'media'},
    'MiG-29A':                 {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'alta'},
    'MiG-29S':                 {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'alta'},
    'MiG-31':                  {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'media'},
    'Su-17M4':                 {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'media'},
    'Su-24M':                  {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'media'},
    'Su-24MR':                 {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'media'},
    'Su-25':                   {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'alta'},
    'Su-25T':                  {'rwr': 'L-150 Pastel', 'identifies': ALL, 'confidence': 'alta'},
    'Su-25TM':                 {'rwr': 'L-150 Pastel', 'identifies': ALL, 'confidence': 'media'},
    'Su-27':                   {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'alta'},
    'Su-30':                   {'rwr': 'L-150 Pastel', 'identifies': ALL, 'confidence': 'media'},
    'Su-33':                   {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'alta'},
    'Su-34':                   {'rwr': 'L-150 Pastel', 'identifies': ALL, 'confidence': 'media'},
    # ── bombardieri ──
    'A-20G Havoc':             {'rwr': None, 'identifies': NONE, 'confidence': 'alta'},
    'B-1B Lancer':             {'rwr': 'AN/ALQ-161', 'identifies': ALL, 'confidence': 'alta'},
    'B-52H Stratofortress':    {'rwr': 'AN/ALR-46', 'identifies': ALL, 'confidence': 'alta'},
    'Tu-160':                  {'rwr': 'Baikal (ESM)', 'identifies': ALL, 'confidence': 'media'},
    'Tu-22M':                  {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'bassa'},
    'Tu-95MS':                 {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'bassa'},
    'Tu-142':                  {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'bassa'},
    # ── AEW, pattugliamento, ricognizione (ESM di bordo) ──
    'A-50':                    {'rwr': 'ESM di bordo', 'identifies': ALL, 'confidence': 'media'},
    'E-2D Advanced Hawkeye':   {'rwr': 'AN/ALQ-217 (ESM)', 'identifies': ALL, 'confidence': 'alta'},
    'E-3A Sentry':             {'rwr': 'ESM di bordo', 'identifies': ALL, 'confidence': 'media'},
    'S-3B Viking':             {'rwr': 'AN/ALR-76 (ESM)', 'identifies': ALL, 'confidence': 'media'},
    'S-3B Viking Tanker':      {'rwr': 'AN/ALR-76 (ESM)', 'identifies': ALL, 'confidence': 'media'},
    'An-30M':                  {'rwr': None, 'identifies': NONE, 'confidence': 'media'},
    # ── trasporto e rifornimento ──
    'An-26B':                  {'rwr': None, 'identifies': NONE, 'confidence': 'media'},
    'C-130 Hercules':          {'rwr': 'AN/ALR-69', 'identifies': ALL, 'confidence': 'media'},
    'C-17A Globemaster III':   {'rwr': None, 'identifies': NONE, 'confidence': 'bassa'},
    'Il-76MD':                 {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'bassa'},
    'Il-78M':                  {'rwr': 'SPO-15 Beryoza', 'identifies': ALL, 'confidence': 'bassa'},
    'KC-130':                  {'rwr': 'AN/ALR-69', 'identifies': ALL, 'confidence': 'bassa'},
    'KC-135 MPRS':             {'rwr': None, 'identifies': NONE, 'confidence': 'media'},
    'KC-135 Stratotanker':     {'rwr': None, 'identifies': NONE, 'confidence': 'media'},
    'Yak-40':                  {'rwr': None, 'identifies': NONE, 'confidence': 'alta'},
    # ── droni ──
    'MQ-1 Predator':           {'rwr': None, 'identifies': NONE, 'confidence': 'alta'},
    'MQ-9 Reaper':             {'rwr': None, 'identifies': NONE, 'confidence': 'alta'},
}


def rwr_categories(model: Optional[str]) -> FrozenSet[str]:
    """Categorie di SAM che l'RWR del modello identifica; vuoto se nessun RWR o modello ignoto."""
    entry = AIRCRAFT_RWR.get(model) if isinstance(model, str) else None

    return frozenset(entry['identifies']) if entry is not None else NONE
