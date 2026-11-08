# Rapporto BI blocco 3 — oc-developer

- **Agente / modello**: `oc-developer` / `openrouter/deepseek/deepseek-v4-pro-0813`
- **Branch**: `ai/oc-bi-blocco3` · **piano eseguito**: `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (§5.0 e §5.4)
- **Data**: 2026-11-08

## 1. Esito in una riga
Completato. Scenario S35-ADTGT scritto tale e quale §5.4.3, righe aggiunte a `Scenario_Baseline.py` come da
§5.4.4, 15 test OK, suite `Ran 4844 · OK (skipped=7)`, confronto `UNCHANGED (1009) · compared 1061 runs: 52
difference lines` (exit code 1 atteso): tutti i numeri coincidono con quelli del piano.

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S35.py` | nuovo: copia esatta (274 righe) del blocco Python di §5.4.3 |
| `Code/Dynamic_War_Manager/Source/Test/Scenario_Baseline.py` | in coda a `UNITS` la tupla S35-ADTGT (§5.4.4 punto 1) e la sezione di docstring "Bersagli intercettabili dopo la BI" (§5.4.4 punto 2) |
| `Analysis/Document/Rapporti/Rapporto_BI_blocco3_oc-developer.md` | questo rapporto |

## 3. Scostamenti dal piano
Nessuno. Il motore, i registri e la Proposta non sono stati toccati.

Osservazione (fuori dal mio intervento): durante la sessione il file `requirements.txt` e' risultato modificato
nel working tree (aggiunta del pacchetto `pymupdf4llm`, `mtime` 20:50). **Non** e' una modifica mia (nessuno dei
miei comandi lo scrive) e **non** l'ho committata: il commit comprende solo i tre file del blocco 3. La segnalo
perche' lo stato `git status --short` non e' piu' pulito per causa esterna.

## 4. Scelte minori prese
Nessuna: il file di test e' stato copiato tale e quale (§5.4.3) e le righe di `Scenario_Baseline.py` inserite con
il testo esatto di §5.4.4, senza variazioni di nomi, costanti, geometrie o asserzioni.

## 5. Costanti stimate
`DECLARED_SEA_RANGE_M = 20_000.0` nel file di test (§5.4.3): **VALORE DI TEST [S]**, sensore marittimo dichiarato
dell'A-10C, non un dato del registro (che non ne ha); serve solo a far rilevare la nave entro la portata del
Maverick (15 km) e non entra in nessuna asserzione (decisione P-2).

## 6. Verifiche eseguite (copiare le righe dell'ESITO, non riassumerle)
- Compilazione (interprete `.direnv/python-3.12/bin/python3`): `py_compile` su
  `Test_Session_Scenarios_S35.py` e `Scenario_Baseline.py`, nessun errore.
- Test singolo: `.direnv/python-3.12/bin/python3 -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S35`
  -> `Ran 15 tests in 9.072s` · `OK`.
- Suite: `Ran 4844 tests in 564.205s` · `OK (skipped=7)`.
- Confronto (exit code 1, atteso per le esecuzioni nuove): `UNCHANGED (1009)` ·
  `compared 1061 runs: 52 difference lines (474.4 s)`.
- Chiavi sulla cattura `.ai-run/confronto_capture.json`:
  `grep -cE '^  "S35-ADTGT/'` -> `32`; `grep -cE '^  "S32-DWELL/'` -> `20`; nessuna chiave `S35-ADTGT/` con `#`
  (32 chiavi, tutte `S35-ADTGT/S35-ADTGT-<i>/<variante>` per le 8 varianti e i 4 seed).

Confronto con l'esito atteso dal piano (§5.4.5): tutti i numeri coincidono (15 test OK; Ran 4844; OK skipped=7;
UNCHANGED 1009; compared 1061 / 52 difference lines; 32 chiavi S35 + 20 S32-DWELL; 1009 + 52 = 1061, quindi 0 DIFF).

## 7. Limiti noti e dubbi per la sessione principale
- L'asserzione 2 (per seed) regge in tutti e 4 i seed: 8 AGM-65D lanciati in `land_tactical_on`, 14 in
  `land_tactical_off` (come da sonda S-e). Le asserzioni 3 e 4 (per seed) reggono: Tor 6 intercettazioni in
  `land_tactical_off`, Buk 2 intercettazioni in `land_cruise_on`, in ogni seed.
- Non ho toccato il blocco 4 (documenti) ne' il motore ne' i registri, come richiesto.
- La modifica di `requirements.txt` (vedi §3) non e' mia e resta non committata: da verificare a chi appartiene.

## 8. Stato git
`git status --short`:
```
 M Code/Dynamic_War_Manager/Source/Test/Scenario_Baseline.py
 M requirements.txt
?? Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S35.py
```
(la `M` su `requirements.txt` non e' mia e non viene committata; il rapporto e' stato aggiunto al commit).

`git log --oneline -5`:
```
47cfba62 Proposta BI: blocco 3 completato con le decisioni P-1..P-7 (file di test S35 completo e provato: 15 test OK; Rezky; esecutore oc-developer)
dd07fd16 Stato a fine sessione 2026-11-08: memoria (stato di fatto, attivita' da concludere e successive), bozze di ricerca dwell D1-D4, Proposta BI blocco 3 (WIP: decisioni P-1..P-7 prese, riscrittura di 5.4/5.0 da completare)
6b744f12 Memoria: BI blocco 3, decisioni P-1..P-7 prese (Rezky, sensore 20 km, nuova asserzione 2, 15 test, S-b, per seme, seed), revisione di L1 rinviata; lavoro del planner interrotto per limite d'uso
551f774b Proposta BI: blocco 3 riallineato al codice attuale; sonde di sola lettura mostrano contraddizioni (Burke e L1, asserzione 2) e 7 punti P-1..P-7 APERTI in 5.4.1; precondizione 5 vieta l'esecuzione finche' non sono decisi
c69ff954 Proposte FP/BI/VA: correzioni dalla rilettura incrociata di FP (verdetto: pronto per l'esecutore), stati superati aggiornati, conteggi B+N riallineati (blocco 2 BI = 28 test, 4829), riferimenti di riga della VA ricontrollati; costi D2 e reviewer
```