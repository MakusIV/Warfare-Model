# Proposta: pulizia dell'interruttore FP (`Engagement_Resolver.FP_PER_PASS_DETECTION`)

**Stato: piano pronto, 3 decisioni per l'utente (§3) con raccomandazione; il piano di §4 implementa le
raccomandazioni.** Se l'utente sceglie un'alternativa diversa, chi pianifica aggiorna §4 prima dell'esecuzione.

- Origine: Proposta FP (`Proposta_Finestre_Per_Passaggio_Portata_Propria.md`) §2.8 (FP-7, interruttore TEMPORANEO) e
  §4.3 punto 3; criterio dell'utente del 2026-11-08 (un interruttore si elimina se lo stato precedente non e' un'alternativa
  valida ma una soluzione superata); decisione dell'utente del 2026-11-12: interruttore acceso e fotografia nuova a 1113
  esecuzioni installata.
- **Esecutore**: `oc-developer` (DeepSeek V4 Pro) sul branch `ai/oc-fp-pulizia`, a blocchi (§4.2-§4.5). Alternativa:
  `des-developer`. L'esecutore segue il piano cosi' com'e'; se il codice reale non corrisponde (righe, firme, esiti), si
  ferma e riferisce.
- **Nessun file di codice o di test modificato da questo documento.** Le sonde di §1.6 sono state eseguite in memoria
  (patch a tempo di esecuzione in uno script fuori dal repo), senza toccare file.

**Convenzioni**: **[V]** = verificato sul checkout del 2026-11-12 (branch `analysis/dce-dcs-persistence`, `04cf4411`)
leggendo il codice o eseguendo una sonda di sola lettura; **[I]** = ipotesi o deduzione non eseguita; **[S]** = stima o
scelta di chi pianifica. Percorsi di codice relativi a `Code/Dynamic_War_Manager/Source/`. "Test n" = numerazione della
Proposta FP §4.1.5 (test 1-30) e §4.2.1 (test S33 1-13).

**Sigle**: FP = rilevamento per passaggio nella portata propria (Proposta FP); FP-2 (O3) = stream separato `pass_rng`
per i passaggi dal secondo in poi; FP-3 (a) = candidato al tiro valido fino alla fine del passaggio; FP-5 (d) = R-INT
"vede il lancio" solo con un rilevamento nel passaggio che contiene il lancio; FP-6 (a) = permanenza D-5 di un passaggio,
mai la somma; FP-10 (c) = unione dei passaggi separati da un'uscita <= dwell; D-5 = Pd dipendente dalla permanenza
(`D5_DWELL_TIME`, spento); R-INT = regola dell'intercettazione con tempo di reazione; S33 = scenario S33-PASSES;
"fotografia" = `Test/baseline/scenario_baseline.json`.

---

## 0. Sintesi

| Cosa | Esito |
|---|---|
| Interruttore `FP_PER_PASS_DETECTION` | eliminato con il suo commento; nessun nuovo interruttore |
| `_detect_direction` | i passaggi si calcolano sempre quando ci sono i tratti; tolto il ramo `if self.pass_rng is not None` |
| `pass_rng` mancante in una direzione a >= 2 passaggi | `ValueError` (errore di chiamata, non un ripiego): decisione U-2, raccomandata |
| `_detection_time_of` | solo FP-5 (d) piu' il ripiego senza tratti; `at` diventa obbligatorio |
| `_exposure_time` (FP-6) | resta solo il ripiego SENZA tratti; il ramo con i tratti (scelta "passaggio che contiene `t_cpa`, in subordine il piu' lungo") e' codice morto e si toglie; 0 passaggi = permanenza 0, come oggi |
| `Session_Simulator.engage` | passa sempre `pass_rng`, nella stessa posizione di oggi |
| S33 | tolte le varianti `off` e `cas_off` (decisione U-1, raccomandata): 13 -> 11 test, 20 -> 10 esecuzioni |
| Suite | `Ran 4914` (da 4919: -5 test, §4.7) |
| Confronto con la fotografia di 1113 | `UNCHANGED (1103)`, nessuna `CHANGED`, `compared 1103 runs: 10 difference lines` = le 10 `MISSING` di S33 `off`/`cas_off`; nessun cambio di comportamento sulle esecuzioni che restano |
| Fotografia nuova (1103) | **solo l'utente** la installa, dopo la verifica finale (decisione U-3) |

**Dimensione stimata** [S]: ~250 righe toccate in tutto (risolutore ~40 di codice, quasi tutte tolte, e ~60 di docstring;
orchestratore ~10; test ~180, fra cui S33 ~90), 4 blocchi piccoli piu' la verifica finale.

---

## 1. Problema e comportamento attuale

### 1.1 Stato di partenza [V]

- `Logic/Engagement_Resolver.py:626` `FP_PER_PASS_DETECTION = True` (commento `:610-625`, ACCESO dal 2026-11-12,
  "TEMPORANEO ... si elimina, con il ramo spento, in un blocco di pulizia dopo la fotografia nuova installata
  dall'utente"). La fotografia nuova (1113 esecuzioni, regola accesa) e' installata: la condizione e' soddisfatta.
- Il risolutore NON legge la costante: la regola e' attiva se e solo se `pass_rng` non e' None (FP-7 (a)). La legge solo
  `Logic/Session_Simulator.py:2794-2797` (`if ER.FP_PER_PASS_DETECTION: extra['pass_rng'] = order.rng(...)`).
- Rami "spento" nel risolutore (gli unici due `pass_rng is None` / `is not None`):
  - `_detect_direction`, `Logic/Engagement_Resolver.py:2340` `if self.pass_rng is not None:` (passaggi, FP-3 (a), permanenza
    del passaggio); fuori dal ramo: estrazione unica per finestra e direzione, permanenza da `_exposure_time`.
  - `_detection_time_of`, `:3748` `if self.pass_rng is None or at is None or key not in self.own_passes_of:` (regola
    precedente "ultimo rilevamento in ordine di lista").
- `_exposure_time`, `:2479-2516`: ramo con i tratti `:2496-2508` (FP-6 (a): passaggio che contiene `t_cpa`, in subordine il
  piu' lungo, `:2505-2506`); ramo senza tratti `:2510-2516`. Unico chiamante: `_detect_direction:2367`.
- `_detect_passes`, `:2592-2642`: estrazione `self._draw() if index == 0 else self._draw(self.pass_rng)` (`:2613`).
- `resolve_engagement`, `:4333-4513`: parametro `pass_rng=None` (`:4352`), docstring `:4434-4441` ("None (default) = un'estrazione
  per finestra e direzione, comportamento precedente"), validazione del tipo `:4479-4480`.
- Testi che descrivono l'interruttore o lo stato spento: docstring del modulo `:53-54` (R-INT), `:182-185` (D-5,
  permanenza), `:197-223` (sezione FP, che a `:223` dice ancora "Fino ad allora il default resta spento", superato),
  `:475-477` (ordine delle estrazioni); commenti `:2034-2036` (`__init__`), `:2341-2343` (`_detect_direction`);
  `Logic/Session_Simulator.py:735-738` (sezione FP del docstring), `:804-805` (`PASS_EVENT_TAG`), `:2795-2796`.

### 1.2 Chiamanti di `resolve_engagement` e di `_EngagementRun` [V, grep]

- Produzione: **solo** `Logic/Session_Simulator.py:2799`. Nessun altro modulo del core ne' l'adapter DCS.
- Test: `Test_Engagement_Resolver.py` (101 chiamate), `Test_Aircraft.py` (3 + un `_EngagementRun` a `:345`),
  `Test_Session_Rng.py:196`, `Test_Session_Types.py:285`, `Test_Session_Simulator.py:465`, `Test_Fire_Control.py:526`,
  `Test_Mission_Adapter.py:605` (`_EngagementRun` diretto).
- `_detection_time_of`: unico chiamante di produzione `_in_time` (`:3831`), sempre con `at=salvo.t_launch`; nei test
  sempre con `at` (`Test_Engagement_Resolver.py:4462-4475`).
- `_exposure_time`: unico chiamante `_detect_direction:2367`; citato per nome nel test 20 (`:4330`) e nel docstring di
  `Test_Session_Scenarios_S32.py:8`.

### 1.3 Chi dipende dalla costante [V, grep su `FP_PER_PASS_DETECTION`]

| File | Righe | Uso |
|---|---|---|
| `Logic/Engagement_Resolver.py` | 197, 612, 626, 2034, 2341, 4441 | costante, commenti, docstring |
| `Logic/Session_Simulator.py` | 736, 805, 2794-2795 | lettura e docstring |
| `Test/Test_Engagement_Resolver.py` | 4014 | test 1 `test_switch_is_on_by_default` |
| `Test/Test_Session_Simulator.py` | 270, 286, 295, 1041, 2331 | test 15, 16 e due test di stream con `patch.object(ER, 'FP_PER_PASS_DETECTION', False)` |
| `Test/Test_Session_Scenarios_S33.py` | 6, 49, 111, 347, 360, 369 | `patch.object` per variante e test 13 |
| `Test/Test_Session_Scenarios_S26.py` | 511 | solo docstring (nessun patch) |
| `Test/Scenario_Baseline.py` | 198 | solo docstring |
| `Analysis/Document/Rapporti/Sonde_Finestre_Passaggio/probe_switch_on.py` | — | sonda storica P-1: dopo la pulizia non e' piu' eseguibile (§6) |

Le tre unita' della fotografia che vengono da `Test_Session_Simulator` (`ORC-*`, `Scenario_Baseline.py:328-344`) non
includono i test che spengono la FP: la fotografia non dipende da quei patch [V].

### 1.4 Perche' il ramo "spento" e' superato

Per il criterio dell'utente la regola FP sostituisce una soluzione superata (una sola estrazione per finestra con piu'
passaggi nel volume minore, candidato valido fuori dal volume, R-INT con l'ultimo rilevamento in lista): lo stato spento
non e' un'alternativa valida, quindi interruttore e ramo si eliminano. Restano, perche' NON sono lo stato spento ma il
limite di FP-1 (B-R, passaggi calcolati dai tratti): il **ripiego senza tratti** (chiamate dirette senza `legs`: un'estrazione
per finestra e direzione, candidato fino a `window.t_end`, permanenza da `_exposure_time`, R-INT con l'ultimo rilevamento),
gia' dichiarato in Proposta FP §5.2.

### 1.5 Il ramo con i tratti di `_exposure_time` e' gia' morto [V, lettura del codice]

Con la regola sempre attiva, `_exposure_time` e' chiamata (`:2367`) solo se `pass_exposure` e' None, cioe' se
`_own_passes` restituisce None (nessun tratto: ramo senza tratti) oppure `[]` (tratti, ma nessun passaggio che tocca la
finestra). Nel secondo caso il ramo con i tratti restituisce sempre **0.0**: `_own_passes` (`:2546-2568`) e il ramo
(`:2497-2498`) filtrano gli STESSI intervalli di `_own_intervals(..., own_range)` con lo STESSO criterio di contatto; l'unione
FP-10 (`_join_passes`) produce solo sovrainsiemi, quindi se nessun passaggio unito tocca la finestra nessun intervallo non
unito la tocca e `touching` e' vuoto (`:2500-2501`). La scelta FP-6 (a) "passaggio che contiene `t_cpa`, in subordine il piu'
lungo" (`:2505-2506`) serviva solo a FP spenta (Proposta FP §2.7: "con FP acceso ogni occasione ha la permanenza del
proprio passaggio"): si toglie. Per una direzione con i tratti la permanenza e' quella del passaggio (1 passaggio), di
ciascun passaggio (>= 2, `_detect_passes`) o 0 (nessun passaggio), identica a oggi in ogni caso.

### 1.6 Sonde di sola lettura (2026-11-12, ProArt) [V]

Script nello scratchpad (fuori dal repo) che sostituisce in memoria, in `_EngagementRun.__init__`, un `pass_rng` None con
una sentinella: emula "FP sempre attiva" su TUTTE le chiamate dirette, senza modificare file.

| Sonda | Moduli | Esito |
|---|---|---|
| S-A "flusso": sentinella = `random.Random(12345)` | `Test_Engagement_Resolver`, `Test_Aircraft`, `Test_Session_Rng`, `Test_Session_Types`, `Test_Fire_Control`, `Test_Mission_Adapter` (724 test, 2,8 s) | 8 fallimenti, tutti test FP/D-5 che provano lo stato spento: test 2, 7, 8, 14, 18, 20, 21, 23. Nessun altro test cambia esito: FP-3 (a) e FP-5 (d) applicati anche alle chiamate dirette con tratti non toccano nient'altro |
| S-B "errore": sentinella con `random()` che solleva | stessi moduli | sentinella chiamata 4 volte, solo nei test 2, 4, 7, 8 (geometria comune a due passaggi senza `pass_rng`); test 14, 18, 20, 21, 23 falliscono per asserzione. Nessuna chiamata diretta fuori dai test FP ha una direzione a >= 2 passaggi senza `pass_rng` |
| S-B su `Test_Session_Simulator` | 170 test, 6,4 s | 0 fallimenti, sentinella mai chiamata |

Dalla fotografia installata (lettura del JSON) [V]: in tutti e 5 i semi di S33 la ZSU spara sia in `on` (200 colpi) sia
in `cas_on` (300 colpi): una premessa "la ZSU spara" sulle varianti accese non e' vacua.

### 1.7 Discrepanze trovate fra memoria/piani e codice

1. **Conteggio delle "meta' senza `pass_rng`"**: la memoria e la Proposta FP §4.3 parlano di test 1, 2, 15 "e le meta'
   senza `pass_rng` degli altri". Le sonde (§1.6) mostrano che solo i test 2, 4, 7, 8, 14, 18, 20, 21, 23 cambiano
   esito; i test 10, 19, 22 hanno una meta' senza `pass_rng` ma restano veri (direzioni a un passaggio o senza tratti).
2. **`_exposure_time`**: la Proposta FP §4.3 dice che il ramo con i tratti "diventa il solo ripiego per le direzioni a zero
   passaggi e si semplifica". In realta' in quel caso restituisce sempre 0 (§1.5): la logica FP-6 del ramo e' morta e si
   toglie del tutto.
3. **Confronto atteso**: il compito parla di "1009 UNCHANGED piu' le invariate"; 1009 era il numero della fotografia
   precedente. Con la fotografia di 1113 installata il 2026-11-12 l'atteso e' `UNCHANGED (1103)` (1113 - 10 tolte).
   Inoltre il confronto di `verifica.sh` usa `--summary`, che **non stampa** le righe `MISSING`: le 10 esecuzioni tolte si
   vedono solo nel conteggio `10 difference lines` e con il comando di §4.6 (senza `--summary`).
4. **Nomi della fotografia**: la Proposta FP §4.3 dice "nomi della fotografia da aggiornare con la fotografia nuova". Con le
   etichette per occorrenza di `Scenario_Baseline` (`_by_occurrence`, `:249-254`) basta cambiare la tupla dei nomi in
   `('on', 'cas_on')`: le chiavi `S33-PASSES/S33-PASSES-k/on` e `/cas_on` restano identiche; spariscono solo le 10 chiavi
   tolte.
5. Testi gia' superati nel codice: `Engagement_Resolver.py:223` "Fino ad allora il default resta spento" e
   `Test_Engagement_Resolver.py:3990` "l'interruttore spento di default" (la costante e' True). Si correggono qui.
6. La memoria dice che nella suite dopo l'accensione c'erano "3 test espliciti con FP False": confermato
   (`Test_Session_Simulator.py:285`, `:1041`, `:2331`); il terzo e il secondo NON sono nella fotografia (§1.3).
7. `_ScriptedRng` dei test (`Test_Engagement_Resolver.py:78-88`) restituisce 0.5 quando la lista e' esaurita (non
   solleva): i test che contano le estrazioni devono asserire `calls`, come fanno gia'.
8. La conferma che la fotografia di 1113 sia identica al codice attuale (`UNCHANGED (1113)`, `IDENTICAL`) e' in corso da
   parte della sessione principale (la memoria la dava come non ancora eseguita): e' la precondizione P-2 (§4.1).

---

## 2. Alternative e raccomandazioni

### 2.1 Varianti `off`/`cas_off` di S33 (decisione U-1)

| Opzione | Contenuto | Effetto sul confronto | Pro | Contro |
|---|---|---|---|---|
| **(a) toglierle** | S33 a 2 varianti (`on`, `cas_on`) x 5 semi = 10 esecuzioni; tolti i test S33 2 e 8, riscritti 3, 5, 9, 12, 13 | 10 `MISSING`, le altre 1103 identiche | lo stato "FP spenta" non esiste piu': lo scenario prova solo la configurazione reale; nomi `on`/`cas_on` stabili | in sessione la FP a passaggi multipli e' provata solo con la D-5 accesa (la D-5 spenta resta ai test unitari 3, 27) |
| (b) tenerle, come "D-5 spenta" | `off`/`cas_off` = FP sempre attiva, D-5 spenta, nessun dwell | 10 `CHANGED` | copertura in sessione della configurazione di default (D-5 spenta) | con g = 1 e senza unione la D-5 non cambia nulla (Proposta FP §2.9): le 10 esecuzioni diventerebbero copie di `on`/`cas_on` nella fotografia; nome `off` fuorviante |
| (c) come (b) ma rinominate (`d5_off`, `cas_d5_off`) | nomi chiari | 10 `MISSING` + 10 `NEW` | nomi coerenti | stessa ridondanza di (b), piu' righe nella fotografia |

**Raccomandazione: (a).** Le varianti erano "stato precedente contro configurazione finale"; lo stato precedente non c'e'
piu' e le alternative (b)/(c) produrrebbero esecuzioni uguali a quelle accese. La D-5 spenta con passaggi multipli resta
coperta dai test unitari (`test_with_pass_rng_one_draw_per_pass`, `test_passes_stay_apart_with_the_dwell_law_off`);
l'eventuale interesse per S33 a D-5 spenta va nell'analisi mirata degli interruttori (la D-5 ha il suo).

### 2.2 Chiamata diretta con tratti e una direzione a >= 2 passaggi senza `pass_rng` (decisione U-2)

Dopo la pulizia i passaggi si calcolano sempre quando ci sono i tratti. Un chiamante diretto che passa `legs` ma non
`pass_rng` (default None, ~100 chiamate di test) puo' trovarsi con una direzione a due passaggi: da dove vengono le
estrazioni dal secondo passaggio in poi?

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| **P1 `ValueError`** | `pass_rng` resta facoltativo; `_detect_passes` solleva `ValueError` prima di ogni estrazione se `pass_rng` e' None | nessuna seconda modalita' d'ordine; lo stream `rng` resta quello del contratto (FP-2 O3); sonda S-B: **nessuna** chiamata fuori dai test FP la incontra; la sessione passa sempre lo stream | errore a tempo di esecuzione (durante la fase di rilevamento, prima di ogni evento), non all'ingresso |
| P2 estrazioni in linea da `rng` | senza `pass_rng` i passaggi dal secondo in poi estraggono da `rng` | nessun errore | due ordini delle estrazioni a seconda dell'argomento: e' l'opzione O1 scartata dall'utente per FP-2, reintrodotta di nascosto |
| P3 `pass_rng` obbligatorio con `legs` | `TypeError` all'ingresso se `legs` e' dato senza `pass_rng` | errore immediato | decine di chiamate di test da modificare per nulla (sonde: nessuna ha piu' passaggi) |
| P4 estrazione unica per finestra senza `pass_rng` | il vecchio comportamento per quel solo caso | nessun errore | e' il ramo "spento" che la pulizia deve togliere |

**Raccomandazione: P1.** E' una validazione d'argomento (le eccezioni del risolutore restano "per gli argomenti fuori
dominio", docstring del modulo `:480-482`), non uno stato alternativo; FP-3 (a) e FP-5 (d) valgono anche senza `pass_rng`
(servono solo i tratti). **Conseguenza dichiarata**: dopo la pulizia una chiamata diretta con i tratti e un solo passaggio
per direzione applica FP-3 (a) e FP-5 (d) anche senza `pass_rng` (oggi no): le sonde mostrano che cambia solo l'esito dei
test FP che provano lo stato spento (riscritti in §4.4).

### 2.3 Allineamento della fotografia dopo la pulizia (decisione U-3)

Con U-1 (a) la fotografia di 1113 contiene 10 esecuzioni che il codice non produce piu': ogni confronto termina con
`10 difference lines` ed exit code 1 finche' l'utente non installa una fotografia di 1103 esecuzioni.

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| **(i) copia della cattura del confronto finale** | dopo la verifica di §4.6, l'utente copia `.ai-run/confronto_capture.json` (salvata da `verifica.sh confronto` con `--save`, stessa funzione `dump` della `--capture`) su `Test/baseline/scenario_baseline.json` | e' la cattura del codice finale; nessuna esecuzione in piu' (~8-17 min risparmiati) | va controllato prima che la cattura non abbia errori di unita' (§4.6) |
| (ii) cattura nuova | `Scenario_Baseline --capture` dall'utente | procedura gia' usata il 2026-11-12 | ~20 min in piu' (ProArt ~8-10, osboxes ~20) |
| (iii) togliere 10 chiavi dal JSON | modifica a mano/script | immediata | non e' una cattura del codice: sconsigliata |

**Raccomandazione: (i)** [S], con la verifica di §4.6. In ogni caso **solo l'utente** installa (AGENTS.md); l'esecutore
non tocca la fotografia.

### 2.4 Scelte di chi pianifica (non di modello, dichiarate)

1. **`at` obbligatorio in `_detection_time_of`**: nessun chiamante passa `at` None (§1.2); il ripiego resta legato alla
   sola mancanza dei tratti (`key not in self.own_passes_of`).
2. **`_exposure_time` ridotta al ripiego senza tratti**, con firma `_exposure_time(self, window, own_range, other_range)`;
   la permanenza "0 passaggi = 0" diventa esplicita in `_detect_direction` (§1.5, comportamento identico).
3. **Posizione della creazione di `pass_rng` in `engage` invariata** (prima degli stream d'ingaggio e di tempra): l'ordine
   delle chiamate a `order.rng` non cambia (rilevante solo per i test che spiano `SessionOrder.rng`; `order.rng` e' una
   funzione pura, `Command/Session_Types.py:388-390`).
4. **Test 1 tolto senza sostituto** (non si prova l'assenza di una costante).
5. **Nomi di classi di test**: `TestPerPassDetectionSwitch` diventa `TestPerPassDetectionStream` (nessuna unita' della
   fotografia la cita).
6. **`run_variant` di S33** restituisce ancora una terna; il terzo elemento diventa la lista delle coppie
   `(copia dello stream d'ingaggio, copia di pass_rng)` per ingaggio, cosi' le altre letture `(_, results, _)` non cambiano.
   Le copie salvate si estraggono sempre da una `copy.deepcopy` (oggi il test S33 10 consuma la copia condivisa della classe).
7. **Ordine dei blocchi**: S33 prima (smette di toccare la costante), poi l'orchestratore, poi il risolutore; ogni blocco
   lascia la suite verde.

---

## 3. Decisioni per l'utente

1. **U-1 — varianti `off`/`cas_off` di S33**: (a) toglierle [raccomandata], (b) tenerle come "D-5 spenta", (c) come (b)
   rinominate. Motivo della raccomandazione: §2.1 (lo stato precedente non esiste; (b)/(c) sarebbero copie di `on`/`cas_on`).
2. **U-2 — `pass_rng` mancante con una direzione a >= 2 passaggi**: P1 `ValueError` [raccomandata], P2 estrazioni in linea,
   P3 obbligatorio con i tratti. Motivo: §2.2 (nessuna modalita' d'ordine nascosta; nessuna chiamata reale la incontra).
3. **U-3 — installazione della fotografia di 1103 esecuzioni (solo dall'utente)**: (i) copia della cattura del confronto
   finale [raccomandata], (ii) cattura nuova, (iii) potatura del JSON [sconsigliata]. Motivo: §2.3.

---

## 4. Piano di intervento (opzioni raccomandate: U-1 (a), U-2 P1)

### 4.1 Precondizioni (la sessione principale le verifica; l'esecutore si ferma se mancano)

- **P-1**: branch `ai/oc-fp-pulizia` creato dalla sessione principale dal branch di lavoro (`git branch --show-current`).
- **P-2**: confronto con la fotografia installata = `UNCHANGED (1113)` e `compared 1113 runs: IDENTICAL` (quello in corso
  ora). Se non e' cosi', la pulizia non parte: prima si spiega la differenza.
- **P-3**: base della suite `Ran 4919` (l'unico fallimento noto ammesso e' il test di tempo
  `TestS17HierarchicalScaleSweep.test_every_size_runs_within_a_loose_bound`, rumore della macchina, non della FP).
- **P-4**: le righe citate qui corrispondono al codice (ricerca per nome se spostate di poche righe; se una funzione o un
  ramo non c'e', fermarsi).

### 4.2 Blocco A — S33 e tabella della fotografia (solo test)

**File**: `Test/Test_Session_Scenarios_S33.py` (tutto il file, 389 righe), `Test/Scenario_Baseline.py:196-203` e
`:428-430`.

`Test_Session_Scenarios_S33.py`:
1. Docstring del modulo (`:1-29`): S33 prova la configurazione finale: FP (sempre attiva) e D-5 accesa con il dwell della
   ZSU 2 s [S]; **due** varianti, 5 semi; tabella con le sole righe `on` (rientro) e `cas_on` (CAS); togliere ogni
   riferimento a `FP_PER_PASS_DETECTION` e allo "stato precedente"; una frase: "Le varianti `off` e `cas_off` (FP e D-5
   spente) sono state tolte con l'interruttore FP (Proposta_FP_Pulizia_Interruttore.md)".
2. `VARIANT_SPEC` (`:49-55`) -> `{'on': 'reentry', 'cas_on': 'cas'}` (variante -> geometria); commento `:49` aggiornato
   ("variante -> geometria; in ogni variante D-5 accesa e dwell ZSU_DWELL_S sulla ZSU"). `VARIANTS = tuple(VARIANT_SPEC)`
   invariato. Commento di `ZSU_DWELL_S` (`:69-72`): "Dichiarato sulla ZSU in ogni variante".
3. `run_variant` (`:88-128`): `geometry = VARIANT_SPEC[variant]`; nessun patch di `FP_PER_PASS_DETECTION`; un solo
   `with patch.object(ER_MODULE, 'D5_DWELL_TIME', True):` attorno a costruzione forze ed esecuzione (come oggi);
   `F.declare_dwell(red.assets[ZSU], {'air': ZSU_DWELL_S})` incondizionato. La spia salva PRIMA dell'esecuzione
   `(copy.deepcopy(args[4]), copy.deepcopy(kwargs['pass_rng']))` (stream d'ingaggio = quinto argomento posizionale,
   `Session_Simulator.py:2799-2800`; `pass_rng` sempre presente, `Session_Simulator.py:2794-2797` con il default True)
   e, se il risultato non e' None, accoda risultato e coppia. Ritorno `(outcome, captured, streams)`; docstring aggiornata.
4. Test (13 -> 11; i nomi non elencati restano come sono):
   - **tolti**: `test_switch_off_one_draw_per_window` (S33 2), `test_cas_switch_off_one_draw_per_aircraft` (S33 8).
   - `test_the_engagement_stream_is_unchanged` (S33 3) -> **`test_first_passes_draw_from_the_engagement_stream`**: per ogni
     seme di `on` e ogni coppia `(result, (engagement, _))`: `first = [d.draw for d in result.detections if d.pass_index
     in (None, 0)]`; `assertTrue(first)`; `stream = copy.deepcopy(engagement)`; `assertEqual(first, [stream.random() for _
     in first])`. Docstring: FP-2 (O3), le estrazioni dei primi passaggi sono, nell'ordine delle `Detection`, le prime
     uscite dello stream dell'ingaggio (la fase di rilevamento e' la prima del risolutore, `Engagement_Resolver.py:4277-4278`).
   - `test_premise_the_zsu_fires_without_the_switch` (S33 5) -> **`test_premise_the_zsu_fires`**: per ciascuna variante di
     `VARIANTS`, somma dei `rounds` della ZSU negli `ammunition_events` su tutti i semi `> 0` (subTest per variante). Rende
     non vacui i test S33 4 e 11 [V: fotografia, 200 colpi in `on` e 300 in `cas_on` in ogni seme].
   - `test_cas_first_pass_keeps_the_engagement_stream` (S33 9) -> **`test_cas_first_passes_draw_from_the_engagement_stream`**:
     come il nuovo S33 3 su `cas_on` (un aiuto locale comune ai due e' una scelta minore).
   - `test_cas_second_pass_draws_from_the_pass_stream` (S33 10): itera `for result, (_, pass_stream) in zip(results,
     streams)`; `assertIsNotNone(pass_stream)` al posto di `if stream is None: continue`; estrae da
     `copy.deepcopy(pass_stream)`. Asserzioni invariate.
   - `test_d5_reads_the_dwell_and_leaves_the_probability_unchanged` (S33 12): togliere il secondo ciclo su `('off',
     'cas_off')` (`:335-341`); il primo ciclo itera `for variant in VARIANTS`. Docstring senza "a D-5 spenta".
   - `test_variant_switches_are_scoped` (S33 13): `probe` registra `(ER_MODULE.D5_DWELL_TIME,
     args[2][0].assets[ZSU].detection_dwell_time('air'))`; atteso `(True, ZSU_DWELL_S)` per ogni variante di `VARIANTS`;
     `before = ER.D5_DWELL_TIME` e, dopo l'eccezione, `assertEqual(ER.D5_DWELL_TIME, before)`. Docstring: "La D-5 e'
     sostituita soltanto durante la variante ...".
   - commenti di sezione (`:165`, `:220`, `:308`): "geometria di rientro, `on`", "geometria CAS, `cas_on`", "D-5".

`Scenario_Baseline.py`:
5. `:428-430`: `('S33-PASSES', 'Test_Session_Scenarios_S33', 'TestS33DetectionPerPass', None, _by_occurrence('on', 'cas_on'))`;
   commento `:428`: "S33 (FP: un'occasione di rilevamento per passaggio nel volume proprio; dal blocco di pulizia FP solo
   le varianti accese) — in coda, nomi stabili".
6. Docstring `:196-203` ("Rilevamento per passaggio dopo la FP"): la regola e' senza interruttore dal blocco di pulizia
   (`Proposta_FP_Pulizia_Interruttore.md`); la fotografia di 1113 del 2026-11-12 la include gia'; l'unita' S33-PASSES ha
   ora 2 varianti (rientro e CAS, FP e D-5 accese, dwell della ZSU 2 s, stima; 5 seed) = 10 esecuzioni: le 10 `off`/`cas_off`
   sono tolte e risultano `MISSING` finche' l'utente non installa la fotografia nuova.

**Vincoli**: nessun file di `Logic/` toccato; la costante `FP_PER_PASS_DETECTION` esiste ancora (default True) ma S33 non
la nomina piu'. Ordine dei cicli in `setUpClass` (`:161-163`: semi esterni, varianti interne) invariato: con due varianti
l'occorrenza 0 = `on`, 1 = `cas_on`, quindi le chiavi restano `S33-PASSES/S33-PASSES-k/on` e `/cas_on`.

**Verifica dell'esecutore**: `<python> -m py_compile` dei due file; `<python> -m unittest
Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S33` -> **`Ran 11`, `OK`**.

**Verifica parziale della sessione principale** (dalla root del repo):

    <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \
        --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json --only '^S33-PASSES/'

Atteso: esattamente 10 righe `MISSING S33-PASSES/S33-PASSES-{0..4}/{off,cas_off}`, nessuna `DIFF`/`NEW`/`ERROR`;
`compared 10 runs: 10 difference lines`. Una `DIFF` su `on`/`cas_on` = fermarsi (stato globale che dipendeva dalle varianti
tolte [I, non atteso]).

### 4.3 Blocco B — orchestratore (`Session_Simulator` e i suoi test)

**File**: `Logic/Session_Simulator.py:735-738`, `:804-806`, `:2794-2797`; `Test/Test_Session_Simulator.py:269-310`,
`:451-470`, `:1035-1048`, `:2326-2339`.

`Session_Simulator.py`:
1. `:2794-2797`: togliere `if ER.FP_PER_PASS_DETECTION:`; la riga `extra['pass_rng'] = order.rng(mission_id=None,
   event_id=pass_event_id(*force_ids), counter=counter)` resta **nella stessa posizione** (dopo il blocco D-5, prima della
   chiamata a `ER.resolve_engagement`), con il commento: "FP: un'occasione di rilevamento per passaggio nel volume proprio
   (v. Engagement_Resolver, "Rilevamento per passaggio"): stream separato dei passaggi dal secondo in poi, con lo stesso
   `counter` dell'episodio."
2. `:735-738` (sezione "Rilevamento per passaggio (FP)" del docstring): "`engage` passa sempre a `resolve_engagement` lo
   stream separato `pass_rng = order.rng(mission_id=None, event_id=pass_event_id(*forze), counter=ordinale dell'episodio)`,
   da cui il risolutore estrae i passaggi dal secondo in poi di una direzione con piu' passaggi nel volume proprio. Regola
   senza interruttore dal blocco di pulizia (Proposta_FP_Pulizia_Interruttore.md)."
3. `:804-805` (commento di `PASS_EVENT_TAG`): togliere "Engagement_Resolver.FP_PER_PASS_DETECTION"; "(FP, v.
   Engagement_Resolver "Rilevamento per passaggio")".

`Test_Session_Simulator.py`:
4. Classe `TestPerPassDetectionSwitch` (`:269`) -> `TestPerPassDetectionStream`, docstring "FP: `Session_Simulator.engage`
   passa sempre lo stream `pass_rng` al risolutore."
   - **tolto** `test_switch_off_passes_no_pass_rng` (`:285-292`, test 15);
   - `test_switch_on_passes_the_pass_stream` (`:294-301`, test 16) -> **`test_engage_always_passes_the_pass_stream`**: senza
     `patch.object`; `calls = self._resolver_calls()`; `assertTrue(calls)`; per ogni chiamata
     `assertTrue(callable(kwargs['pass_rng'].random))`;
   - `test_pass_event_id_is_distinct_and_order_free` invariato.
5. `test_engagement_uses_the_documented_stream` (`:451-470`): aggiungere alla chiamata manuale
   `pass_rng=order.rng(mission_id=None, event_id=SS.pass_event_id('M-south', red3[1].id))` e alla docstring "e lo stream
   dei passaggi order.rng(None, pass_event_id, 0)". Asserzioni invariate (con un solo passaggio per direzione la chiamata
   e' quella di oggi; sonda S-B: nessuna direzione multi in questo modulo).
6. `test_rng_streams_are_keyed_by_mission_ids` (`:1035-1048`): togliere `patch.object(ER, 'FP_PER_PASS_DETECTION', False)`
   e il commento "Solo gli stream dell'ingaggio e della tempra..."; docstring "Ogni stream d'ingaggio (di tempra e dei
   passaggi)"; insieme atteso di **6** chiavi: le 4 di oggi piu' `('detection_pass', 'M-north', 'Red-East')` e
   `('detection_pass', 'M-south', 'Red-West')`. Asserzione su `mission_id is None` invariata.
7. `test_same_forces_counter_is_the_ordinal` (`:2326-2339`): togliere il patch FP e il commento; docstring "per
   l'ingaggio, la tempra e i passaggi"; lista attesa (ordine delle chiamate, punto 1 e scelta 3 di §2.4):
   `[(('detection_pass', 'M-b1', 'Red'), 0), (('engagement', 'M-b1', 'Red'), 0), (('temper', 'M-b1', 'Red'), 0),
   (('detection_pass', 'M-b1', 'Red'), 1), (('engagement', 'M-b1', 'Red'), 1), (('temper', 'M-b1', 'Red'), 1)]`.
   [I: dedotto da `Session_Simulator.py:2794-2810`; se la lista reale e' diversa, fermarsi e riferire.]

**Vincoli**: nessuna estrazione nuova ne' spostata (lo stream dei passaggi era gia' creato con il default True);
`Engagement_Resolver.py` non si tocca in questo blocco.

**Verifica dell'esecutore**: `py_compile`; `<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Simulator`
-> **`Ran 169`, `OK`** (170 - 1).

**Verifica parziale della sessione principale**:

    <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \
        --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json --only '^(ORC-[a-z]+|S26-BINGO)/'

Atteso: `compared 113 runs: IDENTICAL` [V: 113 chiavi della fotografia corrispondono all'espressione].

### 4.4 Blocco C1 — risolutore: codice e test

**File**: `Logic/Engagement_Resolver.py:610-626`, `:2318-2401` (`_detect_direction`), `:2479-2516` (`_exposure_time`),
`:2592-2613` (`_detect_passes`), `:3734-3758` (`_detection_time_of`), `:4333-4513` (`resolve_engagement`: docstring di
`pass_rng` e `Raises`); `Test/Test_Engagement_Resolver.py:3987-4476` (classe `TestDetectionPerPass`) e `:4631-4657` (due
test di `TestDwellTimeInTheResolver`).

`Engagement_Resolver.py`:
1. **Costante**: togliere `FP_PER_PASS_DETECTION = True` (`:626`) e il suo commento (`:610-625`).
2. **`_detect_direction`** (`:2333-2369`): sostituire il blocco da `exposure = None` (`:2333`) a
   `factor = factor * dwell_factor(exposure, dwell)` (`:2369`) con:

   ```python
        exposure = None
        # D-5 (D5_DWELL_TIME, v. docstring del modulo): periodo di rivisita del sensore; None senza lettore (interruttore
        # spento) o senza dato. Nessuna estrazione: numero e ordine delle estrazioni restano quelli di prima.
        dwell = self._dwell_of(window, observer, target)
        candidate_end = window.t_end
        pass_exposure = None
        # FP (v. "Rilevamento per passaggio" nel docstring del modulo): passaggi del bersaglio nel volume proprio dentro la
        # finestra, uniti se separati da un'uscita <= dwell (FP-10). Con >= 2 passaggi un'estrazione per passaggio; con 0 o
        # 1 passaggio l'estrazione unica. None senza i tratti di entrambi (chiamate dirette): ripiego senza tratti.
        passes = self._own_passes(window, observer.id, target.id, own_range, dwell)

        if passes is not None:
            # FP-5 (d): passaggi della coppia, per la regola R-INT (`_detection_time_of`).
            self.own_passes_of.setdefault((observer.id, target.id), []).extend(
                (start, end) for _, _, start, end in passes)

            if len(passes) >= 2:
                self._detect_passes(window, observer, target, own_range, factor, dwell, passes)
                return

            # Nessun passaggio che tocca la finestra: permanenza nulla (FP-6; prima la dava `_exposure_time`, sempre 0).
            pass_exposure = 0.0

            if passes:
                _, hi, start, end = passes[0]
                # D-5: permanenza dell'unico passaggio (unito, FP-10), come in `_detect_passes`.
                pass_exposure = max(0.0, min(end, window.t_end) - start)

                # FP-3 (a): all'uscita dal volume proprio la traccia e' persa. Per l'osservatore con la portata MINORE il
                # candidato al tiro vale fino alla fine del passaggio (ritagliata alla finestra). Portata maggiore o
                # uguale (il passaggio coincide con la finestra): fine della finestra.
                if other_range is not None and other_range > 0 and own_range < other_range:
                    candidate_end = hi

        if dwell is not None:
            exposure = self._exposure_time(window, own_range, other_range) if pass_exposure is None else pass_exposure
            factor = factor * dwell_factor(exposure, dwell)
   ```
   Il resto della funzione (`:2371-2401`) non cambia. Equivalenza con oggi a regola accesa: identica per 1 e >= 2
   passaggi; per 0 passaggi 0.0 come il ramo con i tratti di oggi (§1.5); senza tratti `_exposure_time` come oggi.
3. **`_exposure_time`** (`:2479-2516`): nuova firma `def _exposure_time(self, window, own_range: float,
   other_range: Optional[float]) -> float:`; corpo = solo il ramo senza tratti di oggi (`:2510-2516`); togliere le letture
   di `legs_observer/legs_target` e il ramo `:2496-2508`. Docstring: "Permanenza [s] per la legge D-5 nel RIPIEGO SENZA
   TRATTI (chiamate dirette senza `legs`): `t_end - t_start` se la portata propria e' la maggiore (o l'altra e' None);
   altrimenti l'intervallo reciproco `t_mutual_end - t_mutual_start` se esiste; altrimenti 0 (stesso criterio di
   `_detection_time`). Con i tratti la permanenza e' quella del passaggio (`_detect_direction`, `_detect_passes`; FP-6:
   mai la somma). Nessuna estrazione."
4. **`_detect_passes`** (`:2592-2601`): prima di `count = len(passes)` aggiungere

   ```python
        if self.pass_rng is None:
            raise ValueError(f"pass_rng is required: {observer.id!r} -> {target.id!r} has {len(passes)} passes in its own "
                             f"volume within the window [{window.t_start}, {window.t_end}] (resolve_engagement(pass_rng=...))")
   ```
   e in docstring: "Senza `pass_rng` (chiamata diretta che non lo passa) `ValueError` prima di ogni estrazione: e' un errore
   di chiamata, non un ripiego (Proposta_FP_Pulizia_Interruttore.md, U-2)." `:2613` invariata.
5. **`_detection_time_of`** (`:3734-3758`): firma `def _detection_time_of(self, observer_id: str, target_id: str, at: float)
   -> Optional[float]:`; condizione `:3748` -> `if key not in self.own_passes_of:`. Docstring: "Istante in cui `observer_id`
   ha rilevato `target_id`, per la regola R-INT valutata all'istante `at` (il lancio); None = non rilevato. FP-5 (d): il
   rilevamento NEL passaggio dell'osservatore che contiene `at` (`_detection_time_in_pass`); None se nessun passaggio lo
   contiene. Ripiego senza tratti (passaggi della coppia non calcolati, chiamate dirette senza `legs`): l'ULTIMO rilevamento
   in ordine di lista, la regola precedente. Nessuna estrazione."
6. **`resolve_engagement`**: docstring di `pass_rng` (`:4434-4441`) -> "flusso casuale SEPARATO (oggetto con `.random()`)
   per il rilevamento per passaggio (FP, v. "Rilevamento per passaggio"): con i tratti (`legs`) una direzione con >= 2
   passaggi nel volume proprio dentro una finestra ha un'estrazione per passaggio, la prima dallo stream `rng` nella
   posizione dell'estrazione unica, le altre da questo. Necessario solo in quel caso (altrimenti mai estratto); None con una
   direzione a >= 2 passaggi = `ValueError`. FP-3 (a), FP-5 (d) e l'unione FP-10 valgono con i tratti, con o senza questo
   stream. In sessione lo passa sempre Session_Simulator (`pass_event_id`)."; in `Raises/ValueError` aggiungere "`pass_rng`
   mancante con una direzione a >= 2 passaggi nel volume proprio".

`Test_Engagement_Resolver.py` (373 -> **371** test):
7. **tolto** `test_switch_is_on_by_default` (`:4012-4014`, test 1).
8. `test_without_pass_rng_one_draw_per_window` (`:4083-4097`, test 2) -> **`test_multi_pass_direction_requires_pass_rng`**:
   `rng = _ScriptedRng([0.3, 0.6])`; `with self.assertRaises(ValueError) as ctx: self._resolve(rng)`;
   `assertIn('pass_rng', str(ctx.exception))`; `assertEqual(rng.calls, 0)` (la direzione di `b1` e' la prima, il controllo
   precede ogni estrazione); poi `with self.assertRaises(ValueError): ER.resolve_engagement(*self._forces(), [self.WINDOW],
   lambda s, t: None, _ScriptedRng([0.3, 0.6]), legs=self.LEGS)`.
9. `test_the_engagement_stream_is_unchanged` (`:4120-4132`, test 4) -> **`test_first_pass_draws_from_the_engagement_stream`**:
   `rng = _ScriptedRng([0.3, 0.6])`, `pass_rng = _ScriptedRng([0.7])`, `result = self._resolve(rng, pass_rng=pass_rng)`;
   `assertEqual([(d.observer_id, d.pass_index, d.draw) for d in result.detections], [('b1', 0, 0.3), ('b1', 1, 0.7),
   ('r1', None, 0.6)])`; `rng.calls == 2`; `pass_rng.calls == 1`.
10. `test_the_second_pass_is_a_new_occasion` (`:4150-4163`, test 7): togliere la meta' senza `pass_rng` (`:4154-4156`); dopo
    `on`, `assertEqual([d.detected for d in on.detections if d.observer_id == 'b1'], [False, True])` (0.95 >= 0.9 nel
    primo passaggio; 0.1 < 0.9352 x 0.9 nel secondo); salva di `b1` a 300.0 invariata.
11. `test_a_pass_candidate_ends_with_its_pass` (`:4165-4177`, test 8): togliere la meta' senza `pass_rng` (`:4169-4173`);
    tenere `on` con le sue asserzioni e aggiungere: `b1 = [d for d in on.detections if d.observer_id == 'b1']`,
    `assertEqual([d.detected for d in b1], [True, False])`, `assertAlmostEqual(b1[0].time, 50.0, places=6)` (premessa: il
    primo passaggio rileva, ma t_ready 170 > fine del passaggio 150).
12. `test_single_pass_candidate_ends_with_the_pass` (`:4245-4275`, test 18): profilo lento: **anche senza `pass_rng`**
    nessuna salva di `b1` (`assertEqual([...], [])` al posto di "una salva a 170"); con `pass_rng` invariato
    (`on_rng.calls == 0`); profilo veloce invariato (60.0 in entrambi). Commento `:4252`: "FP-3 (a) vale con i tratti, con
    o senza `pass_rng`: il passaggio e' [50, 150]".
13. `test_own_intervals_is_the_single_volume_call` (`:4300-4336`, test 20): parti (i), (ii) e riferimenti invariati; nella
    parte con la spia: la prima risoluzione (pass_rng, dwell 125) aggiunge `assertNotIn('_exposure_time', callers)`; la
    seconda (`self._resolve(_ScriptedRng([0.3, 0.6]), dwell=400.0)`, senza `pass_rng`: con dwell 400 i due passaggi si
    uniscono, FP-10, quindi un passaggio solo e nessun errore) asserisce `assertIn('_own_passes', callers)`,
    `assertIn('_detection_time', callers)`, `assertNotIn('_pass_detection_time', callers)`,
    `assertNotIn('_exposure_time', callers)`. Uguaglianze finali con le risoluzioni senza spia invariate.
14. `test_rint_launch_seen_only_inside_its_pass` (`:4440-4444`, test 21): attesi `(100_000.0, 1.5, None) -> 0`,
    `(100_000.0, 1.5, _ScriptedRng([])) -> 0`, `(50_000.0, 3.0, None) -> 3`, `(50_000.0, 3.0, _ScriptedRng([])) -> 3`
    (FP-5 (d) vale con i tratti, con o senza `pass_rng`); docstring di `_rint_intercepted` invariata.
15. Docstring della classe `TestDetectionPerPass` (`:3987-3993`): togliere "l'interruttore spento di default" e i
    riferimenti ai sotto-blocchi; "Rilevamento per passaggio (FP, senza interruttore dal blocco di pulizia): funzioni
    pure, passaggi, stream, FP-3 (a), FP-5 (d), FP-10."
16. `TestDwellTimeInTheResolver`: `test_exposure_is_the_pass_containing_the_cpa` (`:4631-4640`, test 14) ->
    **`test_exposure_without_a_pass_is_zero`**: tratti `{'b1': [Leg(0.0, 200.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))],
    'r1': [Leg(0.0, 200.0, (-10000.0, 6000.0, 0.0), (10000.0, 6000.0, 0.0))]}`, finestra `ContactWindow('b1', 'r1',
    t_start=0.0, t_end=200.0, t_cpa=100.0, distance_cpa=6000.0, range_a=5000.0, range_b=20000.0, t_mutual_start=None,
    t_mutual_end=None)`, `self._run([window], _ScriptedRng([0.0, 0.9]), dwell=400.0, legs=legs, fire=lambda s, t: None)`;
    la `Detection` di `b1`: `exposure_s == 0.0`, `dwell_time_s == 400.0`, `probability == 0.0`, `detected` False,
    `pass_index` None. Docstring: "Con i tratti e nessun passaggio nel volume proprio (bersaglio sempre a 6 km, portata 5 km)
    la permanenza e' 0 (FP-6)." [I: vero anche sul codice di oggi; l'esecutore puo' eseguirlo prima della modifica come
    controllo.]
17. **tolto** `test_exposure_falls_back_to_the_longest_pass` (`:4642-4657`, test 23): prova solo il ripiego FP-6 a FP
    spenta, codice tolto al punto 3.

Restano **invariati** (veri prima e dopo, sonde §1.6): test 3, 5, 6, 9, 10, 11, 12, 13, 19, 22, 24-30 e i test di
`TestDwellTimeInTheResolver` diversi da 14 e 23.

**Vincoli**: nessuna estrazione nuova ne' spostata (il controllo del punto 4 precede ogni estrazione; lo stream `rng` resta
"prima di tutto il rilevamento nell'ordine canonico, poi il danno"); solo RNG iniettati; nessun nuovo interruttore.
Comportamento in sessione identico a oggi (la sessione passa sempre `pass_rng`, quindi percorre gia' oggi il ramo
acceso); cambiano solo le chiamate dirette con i tratti senza `pass_rng` (FP-3 (a) e FP-5 (d) ora valgono; `ValueError`
con >= 2 passaggi).

**Verifica dell'esecutore**: `py_compile`; `<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Engagement_Resolver`
-> **`Ran 371`, `OK`**; poi, uno per volta: `Test_Session_Simulator` (`Ran 169 OK`), `Test_Session_Scenarios_S33`
(`Ran 11 OK`), `Test_Fire_Control`, `Test_Aircraft`, `Test_Mission_Adapter`, `Test_Session_Rng`, `Test_Session_Types`
(`OK`, stesso numero di test di prima), `Test_Session_Scenarios_S32` (`OK`).

**Verifica parziale della sessione principale** (scenari delle 44 `AFTER_PASS`, D-5, R-INT, S33):

    <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \
        --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json \
        --only '^(S13|S14|S19AD|S21|S24-ORBIT|S26-BINGO|S28-CLASS|S32-DWELL|S33-PASSES|S35-ADTGT)/'

Atteso: `compared 258 runs: 10 difference lines`, le 10 righe = le stesse `MISSING` di S33 del blocco A, nessuna `DIFF`
[V: 268 chiavi della fotografia corrispondono, meno le 10 tolte].

### 4.5 Blocco C2 — testi (docstring e commenti, nessun comportamento)

**File**: `Logic/Engagement_Resolver.py:53-54`, `:182-185`, `:197-223`, `:475-477`, `:2034-2039`;
`Test/Test_Session_Scenarios_S26.py:506-515`; `Test/Test_Session_Scenarios_S32.py:8`.

1. `:53-54` (R-INT): "Con i tratti delle rotte (rilevamento per passaggio, FP-5 (d)) 'aveva gia' rilevato il lanciatore'
   vale solo per un rilevamento nel passaggio che contiene il lancio."
2. `:182-185` (D-5, "Permanenza"): "dai tratti delle rotte: la permanenza del passaggio in portata PROPRIA a cui
   l'estrazione appartiene (`_own_passes`, unito se separato da uscite <= dwell, FP-10), mai la somma (FP-6,
   Proposta_Finestre_Per_Passaggio_Portata_Propria.md); 0 se nessun passaggio tocca la finestra. NON e' tagliata ..." (il
   seguito invariato); "Senza tratti (chiamate dirette, `_exposure_time`): ..." invariato.
3. `:197-223`, titolo "## Rilevamento per passaggio nella portata propria (FP)"; primo capoverso: "...; regola senza
   interruttore dal blocco di pulizia (Proposta_FP_Pulizia_Interruttore.md: l'interruttore temporaneo
   `FP_PER_PASS_DETECTION`, acceso il 2026-11-12, e' stato eliminato con il ramo della regola precedente)". Punto FP-2:
   "... i passaggi dal secondo in poi estraggono da un flusso separato `pass_rng` (iniettato dal chiamante; in sessione
   sempre). Una direzione con >= 2 passaggi senza `pass_rng` e' un errore di chiamata (`ValueError`)." Punto FP-6: "con la
   D-5 accesa ogni estrazione usa la permanenza del proprio passaggio (unito, FP-10), mai la somma; nessun passaggio = 0."
   Punto FP-10: "solo con la D-5 accesa e il dwell dichiarato". Capoverso "Ripiego senza tratti": "i passaggi non si
   calcolano: un'estrazione per finestra e direzione, candidato fino alla fine della finestra, permanenza D-5 di
   `_exposure_time`, R-INT con l'ultimo rilevamento in lista (limite di B-R, Proposta FP §5.2)". Togliere il capoverso
   "Temporaneo ..." (`:221-223`).
4. `:475-477`: "... (invariato dalla D-5 e dal rilevamento per passaggio: i passaggi dal secondo in poi estraggono dallo
   stream separato `pass_rng`, nell'ordine canonico seguito dall'indice del passaggio, e lo stream `rng` resta identico)".
5. `:2034-2036` (`__init__`): "# FP (v. "Rilevamento per passaggio" nel docstring del modulo): stream separato dei passaggi
   dal secondo in poi; None ammesso solo se nessuna direzione ha >= 2 passaggi (altrimenti ValueError in `_detect_passes`).
   Passaggi `(start, end)` (uniti, FP-10) ..." (seguito invariato).
6. `Test_Session_Scenarios_S26.py:510-511`: "Con la FP accesa (dal 2026-11-12, `Engagement_Resolver.FP_PER_PASS_DETECTION`)"
   -> "Con il rilevamento per passaggio (FP, dal 2026-11-12; Proposta_Finestre_Per_Passaggio_Portata_Propria.md)". Nessun
   altro cambio nel file.
7. `Test_Session_Scenarios_S32.py:8`: "(`_EngagementRun._exposure_time`)" -> "(la permanenza del passaggio, calcolata dai
   tratti in `_EngagementRun._detect_direction`)".
8. Controllo finale di questo blocco: `grep -rn "FP_PER_PASS_DETECTION" Code/` -> **nessuna riga**.

**Verifica dell'esecutore**: `py_compile` dei tre file; `Test_Engagement_Resolver` (`Ran 371 OK`),
`Test_Session_Scenarios_S26` (`OK`, 16 test), `Test_Session_Scenarios_S32` (`OK`). Nessun confronto parziale: solo testi.

### 4.6 Verifica finale (esecutore con `tools/ai/verifica.sh`, poi la sessione principale)

Esecutore, mai in parallelo, ripetendo `wait` fino a `ESITO`:

    bash tools/ai/verifica.sh suite start        # poi: bash tools/ai/verifica.sh suite wait
    bash tools/ai/verifica.sh confronto start    # poi: bash tools/ai/verifica.sh confronto wait

Attesi:
- Suite: **`Ran 4914`**, `OK (skipped=7)` (§4.7). Un fallimento del solo test di tempo
  `TestS17HierarchicalScaleSweep.test_every_size_runs_within_a_loose_bound` va riportato com'e' (rumore noto), non
  corretto.
- Confronto (riepilogo `--summary`): **`UNCHANGED (1103)`**, **nessuna riga `CHANGED`**, **`compared 1103 runs: 10 difference
  lines`**, exit code **1** (atteso: le differenze sono le 10 `MISSING`, che `--summary` non stampa).

Sessione principale (secondi, nessuna esecuzione):

    <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \
        --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json \
        --against .ai-run/confronto_capture.json | grep -E '^(MISSING|NEW|DIFF|ERROR)'

Atteso: **esattamente 10 righe**, tutte `MISSING S33-PASSES/S33-PASSES-k/off` o `/cas_off` (k = 0..4); nessuna `NEW`,
`DIFF`, `ERROR`. Poi l'utente decide l'installazione (U-3).

### 4.7 Conteggio dei test (da `Ran 4919`)

Colonna "Prima" [V: conteggio del caricatore di `unittest` senza esecuzione, 2026-11-12; `Test_Session_Scenarios_S26` = 16,
invariato]. Il totale 4919 e' quello dell'ultima suite (memoria del 2026-11-12), da riconfermare con P-3.

| Modulo | Prima | Dopo | Differenza |
|---|---|---|---|
| `Test_Engagement_Resolver` | 373 | 371 | -2 (test 1 e 23 tolti; 2 e 14 riscritti con nome nuovo) |
| `Test_Session_Simulator` | 170 | 169 | -1 (test 15 tolto) |
| `Test_Session_Scenarios_S33` | 13 | 11 | -2 (S33 2 e 8 tolti) |
| **Suite** | **4919** | **4914** | **-5** |

### 4.8 Esito atteso del confronto con la fotografia di 1113 esecuzioni

| Gruppo | Esecuzioni | Esito | Perche' |
|---|---|---|---|
| Tutte le unita' tranne S33 | 1093 | identiche | la sessione percorreva gia' il ramo acceso (`pass_rng` sempre passato con il default True); per 0/1/>=2 passaggi il calcolo e' lo stesso (§1.5); nessuna estrazione cambiata |
| S33 `on`, `cas_on` | 10 | identiche | stessa configurazione (FP attiva, D-5 accesa, dwell 2 s) e stessi nomi (`_by_occurrence('on', 'cas_on')`) |
| S33 `off`, `cas_off` | 10 | `MISSING` (ammesse) | varianti tolte (U-1 (a)) |
| Nuove | 0 | — | nessuna |

Con U-1 (b) le 10 di `off`/`cas_off` sarebbero `CHANGED`; con U-1 (c) 10 `MISSING` + 10 `NEW`: in quei casi §4.2 va
riscritto prima dell'esecuzione.

### 4.9 Scelte minori lasciate all'esecutore (da elencare nel rapporto)

Testo esatto dei commenti e delle docstring entro il contenuto indicato; un aiuto locale comune ai test S33 3 e 9;
nomi delle variabili locali dei test; posizione del controllo di `pass_rng` dentro `_detect_passes` purche' prima di ogni
estrazione.

### 4.10 Compito per `oc-developer` (indicazioni per la sessione principale)

Un compito per blocco (A, B, C1, C2), con solo le righe pertinenti di questo piano, comandi consentiti (`python3 -m
unittest`, `py_compile`, `verifica.sh` solo nel blocco finale), commit dei soli file del blocco sul branch
`ai/oc-fp-pulizia`; il confronto parziale `--only` lo esegue la sessione principale dopo ogni blocco (l'agente non ha il
permesso). Rapporto unico `Rapporti/Rapporto_FP_Pulizia_oc-developer.md` (TEMPLATE) a fine lavoro.

---

## 5. Rischi e limiti

- **Chiamanti diretti esterni con tratti e piu' passaggi**: ora `ValueError` senza `pass_rng` (U-2). Nel repo nessuno (sonda
  S-B); un modulo futuro che chiama `resolve_engagement` con `legs` deve passare uno stream separato (documentato nella
  docstring di `resolve_engagement`).
- **FP-3 (a) e FP-5 (d) nelle chiamate dirette con tratti**: prima valevano solo con `pass_rng`; ora sempre. Sonda S-A: nessun
  test fuori da quelli FP cambia esito.
- **S33 dopo U-1 (a)**: in sessione la FP a passaggi multipli e' esercitata solo con la D-5 accesa (g = 1, nessuna unione);
  D-5 spenta, unione effettiva e g < 1 restano ai test unitari (come gia' dichiarato in Proposta FP §5.1).
- **Stato globale fra varianti di S33** [I, non atteso]: se togliere `off`/`cas_off` cambiasse una variante rimasta (cache
  riscaldate dalle esecuzioni tolte), la verifica parziale del blocco A lo mostra come `DIFF`: fermarsi.
- **Fotografia non allineata finche' l'utente non installa** (U-3): ogni confronto mostra `10 difference lines` ed exit
  code 1; nel frattempo va letto come atteso.
- **Sonda storica P-1** (`Rapporti/Sonde_Finestre_Passaggio/probe_switch_on.py`) e Proposta FP: citano la costante; restano
  come documenti storici (non si eseguono piu' sul codice nuovo).
- **Test di tempo S17** su macchine cariche: puo' fallire per rumore, indipendente da questo lavoro.
- Limiti di modello invariati (Proposta FP §5.2): ripiego senza tratti, finestre e pianificatore con la tolleranza numerica,
  metrica del pianificatore per attraversamento.

---

## 6. Documenti da aggiornare (sessione principale, non l'esecutore)

- **`Proposta_Finestre_Per_Passaggio_Portata_Propria.md`**: §4.3 punto 3 -> "eseguito il 2026-11-xx (Proposta_FP_Pulizia_
  Interruttore.md): suite `Ran 4914`, confronto `UNCHANGED (1103)` + 10 `MISSING`; fotografia di 1103 installata
  dall'utente il ..."; §2.8 (FP-7) e §0 (riga dell'interruttore): nota "interruttore eliminato"; §2.7 (FP-6): la scelta
  "passaggio che contiene `t_cpa`, in subordine il piu' lungo" valeva solo a FP spenta ed e' stata tolta; §5.2 "Senza
  tratti": aggiungere che con i tratti e >= 2 passaggi `pass_rng` e' obbligatorio (`ValueError`).
- **`F4_Differenze_Scenari.md`**, sezione FP (`:2741-2772`): titolo "(interruttore eliminato il 2026-11-xx)"; "Stato" ->
  pulizia eseguita; nuova sottosezione "Pulizia dell'interruttore": 0 esecuzioni cambiate, S33 da 20 a 10 (tolte
  `off`/`cas_off`, 10 `MISSING` fino alla fotografia nuova), fotografia di 1103 installata dall'utente; il paragrafo
  "S33-PASSES (20 esecuzioni nuove)" resta come storico con una riga che rimanda alla pulizia.
- **`Piano_Implementazione_Missione.md`** §5 (righe fuori dalla numerazione F, come D-4b/D-4c a `:310`): oggi non c'e' una riga
  FP (ne' D-5, BI, VA); aggiungere almeno la riga FP con stato "fatta e senza interruttore", commit, numeri.
- **Manuale DES** (`des-manual-writer`; il manuale non descrive ancora ne' FP ne' D-5): scrivere direttamente lo stato
  finale, senza interruttore:
  - cap. 4 (`05_Strato2_Risolutore_Ingaggio.md`): un'estrazione per passaggio nel volume proprio (sempre, con i tratti),
    `pass_rng` necessario per direzioni a >= 2 passaggi (`ValueError` altrimenti), FP-3 (a), FP-4, FP-5 (d), permanenza
    D-5 del passaggio (0 senza passaggi), FP-10; ripiego senza tratti;
  - cap. 6 (`07_Orchestratore_Session_Simulator.md`): tre stream per episodio (`detection_pass`, `engagement`, `temper`,
    stesso `counter`), `pass_event_id`;
  - cap. 8 (`09_Validazione.md`): S33-PASSES a 2 varianti x 5 semi = 10 esecuzioni;
  - cap. 9 (`10_Limiti_Estensioni_Divergenze.md`): "una sola estrazione per finestra con piu' passaggi nel volume minore"
    come limite **storico** superato; limiti di Proposta FP §5.2;
  - atlante `11a_Atlante_Risolutore.md`: nessuna costante FP; `_exposure_time(window, own_range, other_range)` (solo
    ripiego senza tratti); `_detection_time_of(observer, target, at)` con `at` obbligatorio; sequenza di
    `_detect_direction` di §4.4 punto 2.
- **`Rapporti/Sonde_Finestre_Passaggio/LEGGIMI.md`**: una riga "dopo la pulizia (2026-11-xx) `probe_switch_on.py` non e'
  piu' eseguibile: la costante non esiste; documento storico".
- **Memoria** (solo la sessione principale): interruttore FP eliminato, numeri della verifica, fotografia di 1103 (quando
  installata), analisi mirata degli interruttori come passo successivo.
