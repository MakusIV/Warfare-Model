"""Ricevitori d'allarme radar (RWR) degli aerei del registro: che cosa riconoscono e quando.

Richiesta dell'utente (2026-09-29, `Analysis/Document/Proposta_Soglia_Rottura_Stocastica.md` §5):
il fuoco senza risposta di una forza aerea va valutato con l'RWR di ogni aereo illuminato. Il
registro `Aircraft_Data` nomina l'RWR solo per alcuni aerei (campo `avionics`); qui il dato e'
completo e strutturato. Fonti: campo `avionics` del registro, decisioni dell'utente del
2026-09-29 e ricerca `Analysis/Document/Ricerca_RWR_2026_09_29.md`.

## Schema di una voce

* `rwr`: nome del sistema (None = nessun RWR).
* `classes`: le CLASSI di minaccia SAM che il sistema distingue, ciascuna un insieme di categorie
  (`VSHORAD`, `SHORAD`, `MRSAM`, `LRSAM`). Una classe con piu' categorie = il sistema non le
  separa (SPO-15: VSHORAD e SHORAD insieme). L'unione delle classi sono le categorie che l'RWR
  riconosce come minaccia SAM; vuota = nessun riconoscimento (solo allarme generico, o nessun RWR).
* `modes`: modalita' del radar nemico che il sistema rileva: `search` (ricerca/acquisizione),
  `track` (tracciamento/aggancio), `guidance` (guida del missile). Decide QUANDO la minaccia e'
  percepita (v. `Context/Air_Defense_Efficacy.rwr_perception`).
* `sectors`: settori di direzione (4, 8), None = direzione precisa (strobe).
* `ewr`: se riconosce i radar di scoperta (EWR) come classe a parte.
* `confidence`: alta / media / bassa.

## Famiglie (decisioni dell'utente, 2026-09-29)

* **SPO-10 Sirena-3**: direzione approssimativa su 4 quadranti; riconoscimento su due soli livelli
  (SAM o EWR); rileva solo il tracciamento.
* **SPO-15 Beryoza** (anche L, LE, LM): direzione su 8 settori; tre classi SAM (VSHORAD-SHORAD,
  MRSAM, LRSAM); distingue ricerca, tracciamento e guida del missile. Rileva il radar dello Shilka
  (verificato dall'utente in DCS con il Su-25).
* **Sistemi digitali** (AN/ALR-46/56/67/69, ALQ-161, SERVAL/SPIRALE, L-150 Pastel/SPO-32, BKO-1
  Baykal, ESM di bordo): ogni categoria separata, tutte le modalita', direzione precisa.
* **AN/ALR-45** (F-14A, A-4E): riconosce la classe AAA ma non distingue i SAM fra loro (manuale
  Heatblur del modulo F-14): due classi, VSHORAD e "SAM" generico.
* **Solo allarme** (Sirena-2, radarvarnare del Viggen): nessun riconoscimento.
"""

from typing import Dict, FrozenSet, Optional, Tuple

VSHORAD = 'VSHORAD'
SHORAD = 'SHORAD'
MRSAM = 'MRSAM'
LRSAM = 'LRSAM'
ALL = frozenset((VSHORAD, SHORAD, MRSAM, LRSAM))
NONE: FrozenSet[str] = frozenset()

SEARCH = 'search'
TRACK = 'track'
GUIDANCE = 'guidance'
RWR_MODES = (SEARCH, TRACK, GUIDANCE)

_ALL_MODES = frozenset(RWR_MODES)


def _family(rwr, classes, modes, sectors, ewr):
    return {'rwr': rwr, 'classes': tuple(frozenset(c) for c in classes), 'modes': frozenset(modes),
            'sectors': sectors, 'ewr': ewr}


def _digital(rwr):
    """Sistema digitale: ogni categoria separata, tutte le modalita', direzione precisa."""
    return _family(rwr, [(VSHORAD,), (SHORAD,), (MRSAM,), (LRSAM,)], _ALL_MODES, None, True)


def _spo15(rwr='SPO-15 Beryoza'):
    return _family(rwr, [(VSHORAD, SHORAD), (MRSAM,), (LRSAM,)], _ALL_MODES, 8, True)


def _spo10(rwr='SPO-10 Sirena-3'):
    return _family(rwr, [(VSHORAD, SHORAD, MRSAM, LRSAM)], (TRACK,), 4, True)


def _alr45(rwr='AN/ALR-45'):
    return _family(rwr, [(VSHORAD,), (SHORAD, MRSAM, LRSAM)], _ALL_MODES, None, True)


def _warning_only(rwr):
    return _family(rwr, [], (TRACK,), None, False)


def _none():
    return _family(None, [], (), None, False)


def _entry(family, confidence):
    entry = dict(family)
    entry['confidence'] = confidence
    return entry


AIRCRAFT_RWR: Dict[str, dict] = {
    # ── caccia e attacco occidentali ──
    'A-10A Thunderbolt II':    _entry(_digital('AN/ALR-69'), 'alta'),
    'A-10C Thunderbolt II':    _entry(_digital('AN/ALR-69A'), 'alta'),
    'A-10C II Thunderbolt II': _entry(_digital('AN/ALR-69A'), 'alta'),
    'A-4E Skyhawk':            _entry(_alr45(), 'media'),        # registro: AN/ALR-45
    'AJ/ASJ 37 Viggen':        _entry(_warning_only('radarvarnare'), 'media'),
    'F-117 Nighthawk':         _entry(_none(), 'alta'),          # utente: nessun RWR (bassa osservabilita')
    'F-14A Tomcat':            _entry(_alr45(), 'alta'),
    'F-14B Tomcat':            _entry(_digital('AN/ALR-67'), 'alta'),
    'F-15C Eagle':             _entry(_digital('AN/ALR-56C'), 'alta'),
    'F-15E Strike Eagle':      _entry(_digital('AN/ALR-56C'), 'alta'),
    'F-16A Fighting Falcon':   _entry(_digital('AN/ALR-69'), 'alta'),
    'F-16A MLU':               _entry(_digital('AN/ALR-69A'), 'alta'),
    'F-16C Block 52d':         _entry(_digital('AN/ALR-69A'), 'alta'),
    'F-16CM Block 50':         _entry(_digital('AN/ALR-69A'), 'alta'),
    'F-4E Phantom II':         _entry(_digital('AN/ALR-46'), 'alta'),
    'F-5E Tiger II':           _entry(_digital('AN/ALR-46'), 'alta'),
    'F-86E Sabre':             _entry(_none(), 'alta'),
    'F/A-18A Hornet':          _entry(_digital('AN/ALR-67'), 'alta'),
    'F/A-18C Hornet':          _entry(_digital('AN/ALR-67(V)2'), 'alta'),
    'F/A-18C Lot 20':          _entry(_digital('AN/ALR-67(V)3'), 'alta'),
    'Mirage 2000C':            _entry(_digital('SERVAL/SPIRALE'), 'alta'),
    # ── caccia e attacco sovietici/russi ──
    'MiG-15bis':               _entry(_none(), 'alta'),
    'MiG-19P':                 _entry(_warning_only('Sirena-2'), 'alta'),
    'MiG-21bis':               _entry(_spo10('SPO-10 Sirena-3'), 'alta'),
    'MiG-23MLD':               _entry(_spo15(), 'alta'),
    'MiG-25PD':                _entry(_spo15(), 'alta'),
    'MiG-25RB':                _entry(_spo15(), 'alta'),     # utente
    'MiG-27K':                 _entry(_spo15(), 'alta'),
    'MiG-29A':                 _entry(_spo15('SPO-15LM Beryoza'), 'alta'),
    'MiG-29S':                 _entry(_spo15('SPO-15LM Beryoza'), 'alta'),
    'MiG-31':                  _entry(_spo15(), 'alta'),
    'Su-17M4':                 _entry(_spo15('SPO-15LE Beryoza'), 'alta'),
    'Su-24M':                  _entry(_spo15(), 'alta'),
    'Su-24MR':                 _entry(_spo15(), 'alta'),
    'Su-25':                   _entry(_spo15('SPO-15LM Beryoza'), 'alta'),
    'Su-25T':                  _entry(_digital('L-150 Pastel'), 'alta'),
    'Su-25TM':                 _entry(_digital('L-150 Pastel'), 'alta'),
    'Su-27':                   _entry(_spo15('SPO-15LM Beryoza'), 'alta'),
    'Su-30':                   _entry(_digital('SPO-32 Pastel'), 'alta'),
    'Su-33':                   _entry(_spo15('SPO-15LM Beryoza'), 'alta'),
    'Su-34':                   _entry(_digital('L-150 Pastel'), 'alta'),
    # ── bombardieri ──
    'A-20G Havoc':             _entry(_none(), 'alta'),
    'B-1B Lancer':             _entry(_digital('AN/ALQ-161'), 'alta'),
    'B-52H Stratofortress':    _entry(_digital('AN/ALR-46'), 'alta'),
    'Tu-160':                  _entry(_digital('BKO-1 Baykal (Baikal-3)'), 'media'),   # utente: equivalenza
    'Tu-22M':                  _entry(_spo15(), 'alta'),
    'Tu-95MS':                 _entry(_digital('L-150 Pastel'), 'media'),   # utente; registro allineato
    'Tu-142':                  _entry(_spo15(), 'alta'),                    # utente
    # ── AEW, pattugliamento, ricognizione (ESM di bordo) ──
    'A-50':                    _entry(_digital('ESM di bordo'), 'media'),
    'E-2D Advanced Hawkeye':   _entry(_digital('AN/ALQ-217 (ESM)'), 'alta'),
    'E-3A Sentry':             _entry(_digital('ESM di bordo'), 'media'),
    'S-3B Viking':             _entry(_digital('AN/ALR-76 (ESM)'), 'alta'),
    'S-3B Viking Tanker':      _entry(_digital('AN/ALR-76 (ESM)'), 'alta'),
    'An-30M':                  _entry(_none(), 'media'),
    # ── trasporto e rifornimento ──
    'An-26B':                  _entry(_none(), 'media'),
    'C-130 Hercules':          _entry(_digital('AN/ALR-69'), 'media'),
    'C-17A Globemaster III':   _entry(_digital('AN/ALR-69A'), 'media'),
    'Il-76MD':                 _entry(_spo10('SPO-10 Sirena-3'), 'alta'),   # utente
    'Il-78M':                  _entry(_spo15(), 'alta'),                    # utente
    'KC-130':                  _entry(_digital('AN/ALR-69(V)'), 'alta'),   # utente
    'KC-135 MPRS':             _entry(_none(), 'alta'),
    'KC-135 Stratotanker':     _entry(_none(), 'alta'),
    'Yak-40':                  _entry(_none(), 'alta'),
    # ── droni ──
    'MQ-1 Predator':           _entry(_none(), 'alta'),
    'MQ-9 Reaper':             _entry(_none(), 'media'),   # pod AN/ALR-69A(V) opzionale, non di serie
}


def rwr_entry(model: Optional[str]) -> Optional[dict]:
    """La voce del modello, o None se il modello non e' nella tabella (trattato come senza RWR)."""
    return AIRCRAFT_RWR.get(model) if isinstance(model, str) else None


def rwr_categories(model: Optional[str]) -> FrozenSet[str]:
    """Categorie SAM che l'RWR del modello riconosce (unione delle classi); vuoto se nessuna."""
    entry = rwr_entry(model)

    if entry is None:
        return NONE

    return frozenset().union(*entry['classes']) if entry['classes'] else NONE


def rwr_modes(model: Optional[str]) -> FrozenSet[str]:
    """Modalita' del radar nemico che l'RWR del modello rileva; vuoto se nessun RWR."""
    entry = rwr_entry(model)

    return frozenset(entry['modes']) if entry is not None else frozenset()


def rwr_classes(model: Optional[str]) -> Tuple[FrozenSet[str], ...]:
    """Classi SAM distinte dall'RWR del modello."""
    entry = rwr_entry(model)

    return tuple(entry['classes']) if entry is not None else ()
