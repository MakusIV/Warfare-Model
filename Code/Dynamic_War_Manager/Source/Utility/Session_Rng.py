"""RNG di sessione seedato: l'unica sorgente di casualita' del motore di sessioni virtuali.

Disciplina trasversale dell'architettura DES (§6 di
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md`):

    "RNG di sessione seedato da (session_id, mission_id, event_id, contatore). Ogni
    estrazione stocastica passa da li'. L'ordine di risoluzione degli eventi fa parte del
    contratto — salvare solo il seed non basta, perche' un PRNG riproduce la stessa
    sequenza solo a parita' di ordine delle chiamate."

Era la "Fase 0" della roadmap, mai fatta: finora ogni chiamante costruiva il proprio
`random.Random(seed)` con un seed scelto a mano. Questo modulo fissa COME si ottiene il seed.

## Contratto
1. **Seed = funzione pura della chiave** `(session_id, mission_id, event_id, counter)`,
   tutti valori di DOMINIO (mai un id del simulatore, v. il vincolo simulator-agnostic).
2. **Stabile fra processi, macchine e versioni di Python.** NON si usa `hash()`: per le
   stringhe e' randomizzato per processo (PYTHONHASHSEED) e non e' garantito fra versioni.
   Si usa SHA-256 su una codifica canonica (JSON con i tipi preservati: `"1"` e `1` sono
   chiavi diverse, `None` e' distinto da `"None"`), troncato a SEED_BITS bit.
   `random.Random(int)` e' a sua volta stabile: il seeding da intero e il Mersenne Twister
   di `random()` non dipendono da hash di processo.
3. **Una chiave, uno stream.** Ogni valore di `counter` apre uno stream diverso: un evento
   che deve fare piu' estrazioni indipendenti da quelle di un altro evento usa un `counter`
   diverso, invece di condividere un solo generatore il cui stato dipenderebbe dall'ordine
   in cui gli eventi lo interrogano. Resta vero che DENTRO uno stream l'ordine delle
   estrazioni fa parte del contratto (es. quello documentato in Engagement_Resolver).
4. **Mai `random` di modulo**: ogni funzione restituisce un'istanza esplicita, da passare
   come `rng` a chi la consuma (`Engagement_Resolver.resolve_engagement` richiede un
   oggetto con `.random()` in [0, 1), che `random.Random` soddisfa).

## Cosa NON fa
- Non assegna i `mission_id`/`event_id` ne' incrementa i contatori: e' compito di chi
  ordina gli eventi (l'orchestratore della Fase 6), che e' anche chi garantisce l'ordine.
- Nessun componente LLM, in nessuna forma.
"""

import hashlib
import json
import random
from typing import Optional, Union

# Bit del seed: 64 bastano a rendere trascurabili le collisioni fra le chiavi di una campagna
# (paradosso del compleanno ~ 2^32 chiavi per una collisione probabile) e restano un intero
# che `random.Random` accetta senza costi.
SEED_BITS = 64

# Versione della codifica canonica: entra nell'hash, cosi' un cambio futuro della codifica
# produce seed diversi IN MODO DICHIARATO invece di riprodurre in silenzio sequenze diverse
# sotto la stessa etichetta.
SEED_SCHEME = 'warfare-model/session-rng/v1'

DomainKey = Union[str, int]


def _check_key(label: str, value, optional: bool) -> None:
    if value is None:
        if optional:
            return
        raise TypeError(f"{label} is required")

    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise TypeError(f"{label} must be a str or an int{' or None' if optional else ''}, "
                        f"got {type(value).__name__}")

    if isinstance(value, str) and not value:
        raise ValueError(f"{label} must be a non-empty string")


def session_seed(session_id: DomainKey, mission_id: Optional[DomainKey] = None,
                 event_id: Optional[DomainKey] = None, counter: int = 0) -> int:
    """Seed intero deterministico per la chiave `(session_id, mission_id, event_id, counter)`.

    Args:
        session_id: id di dominio della sessione (obbligatorio).
        mission_id/event_id: id di dominio di missione ed evento; None = estrazione di
            livello superiore (es. di sessione), distinta da qualunque id valorizzato.
        counter: intero >= 0, per aprire piu' stream indipendenti sulla stessa chiave.

    Returns:
        int in [0, 2**SEED_BITS).

    Raises:
        TypeError/ValueError: chiave non str/int (bool escluso), stringa vuota, counter
            negativo. Un seed costruito da una chiave malformata e' un errore di
            programmazione, non un dato mancante.
    """
    _check_key('session_id', session_id, optional=False)
    _check_key('mission_id', mission_id, optional=True)
    _check_key('event_id', event_id, optional=True)

    if isinstance(counter, bool) or not isinstance(counter, int):
        raise TypeError(f"counter must be an int, got {type(counter).__name__}")

    if counter < 0:
        raise ValueError(f"counter must be non-negative, got {counter}")

    canonical = json.dumps([SEED_SCHEME, session_id, mission_id, event_id, counter],
                           ensure_ascii=True, separators=(',', ':'))
    digest = hashlib.sha256(canonical.encode('ascii')).digest()

    return int.from_bytes(digest[:SEED_BITS // 8], 'big')


def session_rng(session_id: DomainKey, mission_id: Optional[DomainKey] = None,
                event_id: Optional[DomainKey] = None, counter: int = 0) -> random.Random:
    """Un `random.Random` nuovo, seedato da `session_seed(...)`: pronto per `resolve_engagement(rng=...)`.

    Ogni chiamata restituisce un'istanza NUOVA posizionata all'inizio dello stream: due
    chiamate con la stessa chiave producono la stessa sequenza, e consumare l'una non
    avanza l'altra.
    """
    return random.Random(session_seed(session_id, mission_id, event_id, counter))
