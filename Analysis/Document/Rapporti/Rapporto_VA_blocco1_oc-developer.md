# Rapporto VA blocco 1 — oc-developer

- **Agente / modello**: `oc-developer` / `openrouter/deepseek/deepseek-v4-pro-0813`
- **Branch**: `ai/oc-va-blocco1` · **piano eseguito**: `Analysis/Document/Proposta_Allineamento_Volumi_DES_Pianificatore.md` — SOLO il blocco 1 (§4.0 precondizioni e §4.1; NON il blocco 2 §4.2)
- **Data**: 2026-11-10

## 1. Esito in una riga

Completato (blocco 1). Implementate le tre primitive/cambi di codice e i 23 test previsti dal piano (§4.1.6), tutti
verdi nei test singoli. **Suite e confronto NON eseguiti**: per istruzione del compito li lancia la sessione principale
("Fermati dopo il rapporto: suite e confronto li lancia la sessione principale").

## 2. File toccati

| File | Cosa e' cambiato |
|---|---|
| `Logic/Contact_Scheduler.py` | Nuove primitive della Attivita' D dopo `_merge_intervals`: `altitude_intervals` (fascia di quota, relativa o assoluta) e `intersect_intervals` (intersezione di liste ordinate di intervalli). Nessuna costante nuova. |
| `Logic/Engagement_Resolver.py` | Interruttore `VA_ENGAGEMENT_ALTITUDE_BAND = False` (dopo `BI_AD_TARGET_RULE`); tre campi in coda a `ShotSpec` (`min_altitude`, `max_altitude`, `max_target_z`) + validazione; sezione "Quota nel volume d'ingaggio" nella docstring del modulo; `engagement_intervals(..., band=None)`; introspezione `accepts_keyword`/`accepts_altitudes` (da `accepts_target_grounded`); `_EngagementRun.__init__` (`self.altitude_band`, `self.fire_control_knows_altitudes`, annotazione `range_cache`); `_call_fire_control`/`_fire_control` con `altitudes`; `_range_entry(..., band=None)`; metodi nuovi `_band_of`, `_altitudes_at`, `_altitude_deferral`; chiamanti `_schedule_next` e `_in_range_at` aggiornati (fascia + rinvio VA-2.1). |
| `Logic/Fire_Control.py` | `make_registry_fire_control` accetta `altitudes`; `shot_spec_for` valorizza `min_altitude`/`max_altitude` (superficie) e `max_target_z` (aria); `restrict_by_policy` a quattro varianti (nessuna / solo `target_grounded` / solo `altitudes` / entrambe); docstring "Quota" e della fabbrica aggiornate. |
| `Test/Test_Contact_Scheduler.py` | Classi `TestAltitudeIntervals` (5 test) e `TestIntersectIntervals` (2 test). |
| `Test/Test_Engagement_Resolver.py` | Classe `TestEngagementAltitude` (14 test, punti 8-21 del piano). |
| `Test/Test_Fire_Control.py` | Classe `TestAltitudeBand` (2 test, punti 22-23 del piano). |

## 3. Scostamenti dal piano

Nessuno. Verificate le precondizioni §4.0: branch `ai/oc-va-blocco1`; la Proposta BI e' gia' integrata (`ShotSpec` ha
`intercept_domains` in coda, `BI_AD_TARGET_RULE` esiste, `Scenario_Baseline.UNITS` ha gia' S35-ADTGT); le decisioni
VA-1..VA-8/VA-2.1/VA-8r sono registrate nella riga di stato del piano. Le firme citate dal piano sono state cercate per
nome e coincidono. Unica nota: nel working tree ci sono due file untracked NON miei
(`Analysis/Document/In DCS l'asset FPS-117 ... Cerca con Google.md` e `Analysis/Document/Untitled 1.odt`): li lascio
fuori dal commit.

## 4. Scelte minori prese

- **Annotazione di `range_cache`**: il piano (§4.1.2 punto 10) lascia la scelta all'esecutore. Ho usato
  `Dict[tuple, List[Tuple[float, float]]]` (chiave larga: la chiave e' una tupla a 3 elementi senza `band`, a 4 con
  `band`), invece di un `Union` piu' preciso, per non aggiungere import.
- **Patch dell'interruttore nei test**: ho usato `patch.object(ER, 'VA_ENGAGEMENT_ALTITUDE_BAND', ...)` invece della
  forma letterale `patch.object(sys.modules[ER.__name__], ...)`: e' lo stesso oggetto modulo, ed e' la convenzione gia'
  usata nel progetto (es. `Test_Session_Scenarios_S35` con `BI_AD_TARGET_RULE`). Evita di aggiungere `import sys`.
- **Geometrie dei test**: per i casi "quota" ho scelto geometrie a calcolo a mano (bersaglio in verticale sopra il
  tiratore 0→2000 m in 100 s; discesa 8000→0 m; quota di volo costante), piu' semplici della base di `TestWeaponRange`.
  Il rinvio del test 20 usa l'istante 37.5 s (la mia geometria) invece del "t = 120 s" indicativo del piano.
- **Test 18 white-box**: per verificare `_in_range_at` ("rinvio non e' 'a portata adesso' e candidato non modificato")
  costruisco `ER._EngagementRun` direttamente (come fanno i test RWR/dottrina esistenti del file) e chiamo il metodo
  privato, invece di montare l'intera macchina L2/L3.
- **Test 23**: i quattro punti (i)-(iv) del piano sono in un unico metodo `test_registry_fire_control_altitudes`
  (conteggio totale 23 test rispettato).

## 5. Costanti stimate

Nessuna. La fascia e il tetto vengono dagli stessi campi di registro che `in_altitude_envelope` legge; quote e posizioni
dei test sono geometria di test dichiarata.

## 6. Verifiche eseguite (copiare le righe dell'ESITO, non riassumerle)

**Suite e confronto NON eseguiti** (per istruzione del compito: li lancia la sessione principale). Test singoli eseguiti
dalla root del repo con `python3 -m unittest <modulo>` (stesso interprete di `tools/ai/verifica.sh`):

- `Code.Dynamic_War_Manager.Source.Test.Test_Contact_Scheduler` → `Ran 119 tests in 1.718s` · `OK` (7 nuovi: 5+2)
- `Code.Dynamic_War_Manager.Source.Test.Test_Engagement_Resolver` → `Ran 346 tests in 1.817s` · `OK` (14 nuovi)
- `Code.Dynamic_War_Manager.Source.Test.Test_Fire_Control` → `Ran 111 tests in 0.615s` · `OK` (2 nuovi)
- `Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S19_Air_Defence` → `Ran 12 tests in 17.901s` · `OK`
  (smoke test del percorso sessione + `restrict_by_policy` + fire control dei registri)

Totale test nuovi: **7 + 14 + 2 = 23**, coerente con l'atteso `Ran B + 23` del piano (§4.1.7). Tutti i file Python
modificati compilano (`py_compile.compile(..., doraise=True)` senza errori).

## 7. Limiti noti e dubbi per la sessione principale

- La previsione del piano (VA spento = codice di prima, 1009 esecuzioni identiche; acceso = attese 1009 identiche, regola
  visibile solo in S34-BAND) non e' stata verificata qui: resta alla suite/confronto della sessione principale, come da
  compito.
- Il blocco 2 (§4.2, scenario S34-BAND) non e' in questo compito: nessuna voce nuova in `Scenario_Baseline.UNITS`.
- I due file untracked in `Analysis/Document/` non sono miei e non sono stati committati.
- Nessun interruttore e' stato acceso da me: `VA_ENGAGEMENT_ALTITUDE_BAND` resta `False` (default riproduce il
  comportamento precedente).

## 8. Stato git

`git status --short`:

```
 M Code/Dynamic_War_Manager/Source/Logic/Contact_Scheduler.py
 M Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py
 M Code/Dynamic_War_Manager/Source/Logic/Fire_Control.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Contact_Scheduler.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Engagement_Resolver.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Fire_Control.py
?? "Analysis/Document/In DCS l'asset FPS-117 ... Cerca con Google.md"
?? "Analysis/Document/Untitled 1.odt"
```

`git log --oneline -5` (prima del commit):

```
d7813251 BI blocco 4: documenti (manuale DES cap. 4/9/atlante 11a ...)
6386aac8 Memoria: branch mergiati cancellati
9021a89a Fine sessione 2026-11-08: memoria per la ripresa da osboxes ...
b5c53f46 Memoria e costi: BI blocco 3 mergiato ...
fa6bc1d8 Merge ai/oc-bi-blocco3: BI blocco 3 ...
```
