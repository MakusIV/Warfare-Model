# Proposta: difetto 26, i record di prontezza degli asset assenti dalla sessione

**Stato**: DA DECIDERE (decisioni aperte in §3). Nessun codice modificato.
**Base**: HEAD `630689f9` del branch `analysis/dce-dcs-persistence` (F0-F9 fatte; suite 4701 OK, 7 skipped; fotografia 986).
**Fonti**: manuale DES, capitolo 10 §9.6 voci 24-27 (`Manuale_Motore_DES/10_Limiti_Estensioni_Divergenze.md:950-967`);
capitolo 7 §6.26 (`07_Orchestratore_Session_Simulator.md:1818-1873`); `Proposta_F8_Sessione_Campagna.md` §4.4 (`:728-794`) e §4.6;
`Piano_Implementazione_Missione.md` deviazione 25 (`:502-511`) e riga F9 (`:309`).
**Convenzioni**: [V] verificato leggendo il codice (`file:riga`); [S] misurato con una sonda in sola lettura (script nella
cartella temporanea della sessione, fuori dal repository: sostituisce le funzioni in memoria, non scrive nulla nel repo).
**Numerazione delle decisioni**: locale a questo documento (D26-1 ... D26-6), per non confonderla con le decisioni 17-27 della F8.

---

## 0. Sintesi

Il difetto c'e' ed e' descritto bene dal manuale: `readiness_after_session` costruisce la nuova mappa di prontezza solo dagli
asset passati e `record_session` la consegna a `CampaignLedger.with_readiness`, che **sostituisce** la mappa. Il record di un asset
assente dalle forze della sessione si perde. Le conseguenze misurate [S]: l'asset assente torna **impiegabile prima del tempo**
(il validatore accetta una missione che dovrebbe rifiutare con `ASSET_NOT_READY`) e la sua riparazione **ricomincia da capo**.

Raccomandazione: correggere nell'origine. `readiness_after_session` parte dai record degli asset non passati e ci aggiunge quelli
calcolati per gli asset passati. `with_readiness` resta una sostituzione, perche' `apply_campaign_processes` ha bisogno proprio di
questo. Non serve un interruttore: e' la correzione di un contratto gia' deciso, fuori dal motore. Con la correzione nessuna
esecuzione della fotografia cambia (verificato con una sonda su S30).

C'e' poi un **difetto collegato** che il manuale non segnala, in `apply_campaign_processes` (§1.4). Un processo che si conclude
mentre l'asset e' assente viene buttato via con un warning, senza essere applicato. L'asset torna quindi danneggiato e senza riarmo,
e la riparazione riparte. Correggerlo e' raccomandato (D26-3), ma cambia una regola scritta nella F8 (§4.4): la scelta e'
dell'utente.

---

## 1. Problema e comportamento attuale

### 1.1 Il codice corrisponde alla descrizione [V]

- `Logic/Readiness.py:168-169`, firma:
  `readiness_after_session(ledger: CampaignLedger, order: SessionOrder, outcome: SessionOutcome, assets: Mapping[str, object]) -> Dict[str, ReadyRecord]`.
- Docstring `:170-172`: "La nuova mappa di prontezza dopo la sessione ... I record degli asset non presenti in `assets` restano nel
  registro (non sono qui)".
- `:174` `readiness: Dict[str, ReadyRecord] = {}`: la mappa parte vuota.
- `:185` `for asset_id in sorted(assets):`: si scorrono solo gli asset passati. `:187` legge `previous = ledger.readiness.get(asset_id)`
  solo per loro.
- `:249` `return readiness`: dentro ci sono solo gli asset passati.
- `:252-259` `record_session(...)` e' l'**unico chiamante** e fa
  `ledger.with_session(...).with_readiness(readiness_after_session(ledger, order, outcome, assets))`.
- `Command/Campaign_Types.py:341-345` `with_readiness(self, readiness)`, "Registro con la mappa di prontezza SOSTITUITA":
  `CampaignLedger(rules=..., sessions=..., readiness=readiness)`.

Il docstring `:170-172` e la Proposta F8 §4.4 (`Proposta_F8_Sessione_Campagna.md:794`: "I record degli asset non presenti in `assets`
restano (forze non passate a questa sessione)") promettono quindi una cosa che il codice non fa.

### 1.2 Chiamanti e usi [V]

| Dove | Uso |
|---|---|
| `Logic/Session_Campaign.py:136` | `assets = _assets_of(forces_a, forces_b)`: tutti gli asset delle forze **di quella sessione**, di entrambi i lati (`:43-59`) |
| `Logic/Session_Campaign.py:139` | `Readiness.apply_campaign_processes(ledger, assets, order.t_start)` (passo 1) |
| `Logic/Session_Campaign.py:142-143` | `Session_Validator.check_session(..., ledger=ledger, ...)` (passo 2: `ASSET_NOT_READY` a `Session_Validator.py:149-157`, tramite `ledger.is_ready`) |
| `Logic/Session_Campaign.py:153` | `Readiness.record_session(ledger, order, outcome, assets)` (passo 5) |
| `Logic/Readiness.py:321` | `apply_campaign_processes` restituisce `ledger.with_readiness(remaining)`: qui la **sostituzione serve** (i record conclusi vanno tolti) |
| `Command/Campaign_Types.py:319-322` | `is_ready`: nessun record = pronto. Per questo un record perso rende l'asset impiegabile |
| Test | `Test_Readiness.py` (8 chiamate dirette a `readiness_after_session` e 2 a `record_session`, `:200-283`), `Test_Campaign_Types.py:259-265` (`test_with_readiness_replaces`), `Test_Session_Campaign.py:142-167`, `Test_Session_Scenarios_S30.py` (via `run_campaign_session`) |

Fuori dai test non c'e' nessun chiamante di produzione: `Session_Campaign` e `CampaignState` sono usati solo da scenari e test
(deviazione 25, "Limiti"). `Context/Campaign_State.py:241-259` salva e legge il registro come dizionario e non dipende dalla
correzione.

### 1.3 Perche' S30 non lo vede [V]

`TestS30CampaignSequence.setUpClass` (`Test_Session_Scenarios_S30.py:207-268`) passa a tutte e quattro le sessioni le stesse
forze `cls.forces_a`/`cls.forces_b`. Ogni asset con un record e' quindi sempre in `assets`. `Test_Readiness` non ha nessun caso
con un record di un asset non passato: `test_absent_asset_dropped_with_warning` (`:321-325`) riguarda `apply_campaign_processes`.

### 1.4 Difetto collegato in `apply_campaign_processes` [V]

`Logic/Readiness.py:298-307`. Se un record e' concluso (`ready_at <= t + eps`) e l'asset non c'e' (`assets.get(asset_id)` e' None),
il record viene tolto con un warning e **nessun processo viene applicato** (niente salute a 100, niente riarmo). E' la regola
decisa nella F8 (§4.4, `Proposta_F8_Sessione_Campagna.md:762`: "asset assente -> record tolto con un warning") ed e' coperta da
`test_absent_asset_dropped_with_warning`. Ha pero' lo stesso effetto del difetto 26, cioe' "record perso perche' la forza non era
nella sessione":
- l'asset torna in una sessione successiva senza record, quindi risulta pronto, ma ha ancora la salute e il carburante di prima;
- alla fine di quella sessione la regola 2 di `readiness_after_session` (`:201-209`: `previous` None e `repair_s > 0`) apre un
  **nuovo** record di riparazione da `end_nominal`. La riparazione ricomincia e il tempo gia' passato e' perso.

Una volta corretto il difetto 26, questo e' l'unico caso in cui un asset assente perde ancora il suo processo.

### 1.5 Misure [S]

Due sonde, entrambe fuori dal repository e senza scritture nel repo:
(a) si sostituisce in memoria `Readiness.readiness_after_session` con la versione corretta dell'alternativa A (§2) e, nella
variante "keep", anche `apply_campaign_processes` con la versione dell'alternativa 3b;
(b) si esegue la sequenza dello scenario proposto in §4.3 (S30-ABSENT) e `setUpClass` di S30-CAMPAIGN.

**S30-CAMPAIGN**: con la correzione A, i 4 registri (`to_dict()`) e le 4 fotografie degli asset (posizione, carburante, salute) sono
**identici byte per byte** a quelli di oggi. Registri di oggi: dopo la sessione 1 `mbt0` 22 254,5 s, `mbt1` 41 760 s, `f0`/`f1`
11 550,9 s; dopo la sessione 4 resta solo `mbt0` a 44 509,1 s.

**S30-ABSENT** (sessione 1 in [0, 7200] con `Blue-Mech`; sessione 2 senza `Blue-Mech` da `t2 = max(last_end, ready_at(mbt0))`
= 22 254,5 s; sessione 3 di nuovo con `Blue-Mech` da `t3 = max(last_end, ready_at(mbt1))`):

| Grandezza | Oggi | Con A | Con A + 3b ("keep") |
|---|---|---|---|
| registro dopo la sessione 1 | `mbt0` 22 254,5; `mbt1` 41 760 | uguale | uguale |
| registro dopo la sessione 2 | **vuoto** | `mbt1` 41 760 | `mbt0` 22 254,5 (concluso, conservato); `mbt1` 41 760 |
| ordine a `last_end` = 29 454,5 s con una missione per `mbt1` | **accettato** | `ASSET_NOT_READY` per `mbt1` | `ASSET_NOT_READY` per `mbt1` |
| inizio della sessione 3 | 29 454,5 (record di `mbt1` perso) | 41 760 | 41 760 |
| salute di `mbt1` dopo la sessione 3 | **60** | 100 | 100 |
| registro dopo la sessione 3 | `mbt1` 71 214,5 (**riparazione ripartita** da 36 654,5) | vuoto | vuoto |
| carburante di `mbt0` dopo la sessione 3 | 0,97653 (pieno meno il consumo della sessione 1) | 0,97653 (processo perso nella sessione 2, §1.4) | **1,0** (rifornito al ritorno) |

Con la correzione (A e A+3b) i file `Test_Readiness`, `Test_Session_Campaign`, `Test_Session_Scenarios_S30`, `Test_Campaign_Types` e
`Test_Session_Validator` (108 test) passano tutti. Con 3b fallisce, come atteso, solo `test_absent_asset_dropped_with_warning`, da
riscrivere (§4.2).

I numeri dipendono dai tempi attuali di `Context.py:1013-1038`: `GROUND_TURNAROUND_S` = 21 600 s e `REPAIR_TIME_FULL_S['ground']`
= 86 400 s, il primo dichiarato STIMA DI PROGETTO e il secondo ricavato dalla ricerca F8-R ma con confidenza bassa. I test non li
scrivono a mano: li calcolano dal registro e dalle costanti, e controllano le precondizioni con un messaggio esplicito.

---

## 2. Alternative

### A. `readiness_after_session` parte dai record degli asset non passati (RACCOMANDATA)

La mappa iniziale (`:174`) e' `{id: record for id, record in ledger.readiness.items() if id not in assets}`. Il resto della funzione
non cambia: scrive solo chiavi di `assets`, quindi non sovrascrive mai un record conservato.

- Pro: il codice fa quello che dice il docstring ("la nuova mappa"), senza toccare tipi e API. `record_session` e
  `with_readiness` restano come sono. Nessun test esistente cambia, perche' tutti usano registri vuoti o con chiavi in `assets`
  (verificato [S]). Il gestore di un asset passato resta l'unico che decide il suo record: un asset **distrutto e passato** perde
  il record (regola 1) anche se ne aveva uno.
- Contro: la funzione restituisce anche record che non ha calcolato. Va scritto nel docstring.

### B. `with_readiness` unisce invece di sostituire

- Contro decisivo: `apply_campaign_processes` (`:321`) usa `with_readiness(remaining)` proprio per **togliere** i record
  conclusi. Con un'unione resterebbero, e i processi verrebbero riapplicati a ogni sessione. Anche `test_with_readiness_replaces`
  (`Test_Campaign_Types.py:259`) andrebbe invertito. Servirebbe un parametro `replace=True`, cioe' due semantiche nello stesso
  metodo. Inoltre un'unione semplice (`dict.update`) terrebbe il record di un asset distrutto e passato, contro la regola 1.
- Scartata.

### C. L'unione la fa `record_session`

`record_session` fa `with_readiness({**assenti, **readiness_after_session(...)})` e `readiness_after_session` resta "mappa degli asset
passati".
- Pro: lo stesso risultato di A, e la funzione pura restituisce solo cio' che calcola.
- Contro: il docstring e il nome di `readiness_after_session` ("la nuova mappa") vanno cambiati, e la Proposta F8 §4.4 parla di
  questa funzione. Ogni chiamante futuro dovrebbe ricordarsi di unire, e un pianificatore che chiamasse direttamente
  `readiness_after_session` per una previsione otterrebbe una mappa parziale senza accorgersene.
- Possibile, ma meno robusta di A.

### D. Metodo nuovo `CampaignLedger.with_readiness_for(asset_ids, readiness)`

Sostituisce solo le voci degli id dati e lascia le altre.
- Pro: la semantica e' esplicita nel tipo.
- Contro: un'API in piu' per un solo chiamante, e `readiness_after_session` dovrebbe comunque cambiare docstring come in C. Nessun
  vantaggio pratico su A.

### Interruttore (D26-2)

AGENTS.md chiede un interruttore per "ogni regola nuova del motore". Qui non serve, per tre motivi:
1. non e' una regola nuova ma l'allineamento del codice a un contratto gia' deciso (docstring `:170-172`, Proposta F8 §4.4);
2. non e' nel motore: `Readiness` sta fuori da `run_session`, e la Proposta F8 §4.6 lo dice esplicitamente ("Validatore,
   prontezza e posizioni non sono regole del motore: sono funzioni nuove fuori da `run_session`");
3. un interruttore con default "comportamento precedente" lascerebbe il difetto attivo per default.
Nessuna esecuzione della fotografia cambia (§1.5) e non ci sono chiamanti di produzione.

Alternativa possibile: `Readiness.KEEP_ABSENT_READINESS_RECORDS: bool = False`, con il vecchio comportamento a False. Sconsigliata
per il motivo 3.

### Il difetto collegato (D26-3)

- **3a, lasciare com'e'**: il record concluso di un asset assente si toglie con un warning. Va dichiarato come limite: chi torna
  dopo la fine del suo processo torna con lo stato di prima e la riparazione riparte.
- **3b, conservare (RACCOMANDATA)**: nessun warning e nessuna modifica dell'asset. Il processo si applica alla prima sessione in cui
  l'asset e' di nuovo presente. Il record e' concluso (`ready_at <= t`), quindi `is_ready` e' gia' True e il validatore non
  rifiuta nulla. Pro: elimina il secondo modo di perdere un processo e completa la correzione del difetto 26 nel caso "assente
  quando il processo finisce". Contro: cambia una regola scritta nella F8. Il record di un asset tolto dalla campagna (un id che non
  ricompare piu') resta nel registro per sempre: e' innocuo per il validatore, ma il registro cresce. Chi legge lo stato di un
  asset assente (per esempio in un'istantanea di `CampaignState`) vede salute e carburante vecchi finche' l'asset non torna.
- **3c, conservare dietro un interruttore** `Readiness.KEEP_ABSENT_CONCLUDED_RECORDS: bool = False` (False = 3a). Rispetta la
  lettera di AGENTS.md, ma `Readiness` non e' il motore (motivo 2 sopra) e lascia il limite attivo per default.

---

## 3. Decisioni aperte per l'utente

1. **D26-1, dove correggere**: A (`readiness_after_session` parte dai record degli asset assenti), C (`record_session` unisce) o
   D (metodo nuovo nel registro). **Raccomandata A.**
2. **D26-2, interruttore per la correzione**: nessuno (raccomandato, motivi in §2) oppure
   `Readiness.KEEP_ABSENT_READINESS_RECORDS` con default False (difetto attivo per default).
3. **D26-3, record concluso di un asset assente in `apply_campaign_processes`**: 3a lasciare (limite dichiarato), **3b
   conservare senza interruttore (raccomandata)**, 3c conservare dietro `KEEP_ABSENT_CONCLUDED_RECORDS` = False.
4. **D26-4, fotografia**: registrare il nuovo scenario S30-ABSENT in `Scenario_Baseline.UNITS` (**raccomandato**: tutte le classi di
   scenario lo sono, e la fotografia protegge lo stato degli asset della sessione 3; 3 esecuzioni nuove, fotografia 989 installata
   dalla sessione principale dopo l'approvazione) oppure non registrarlo (986 identiche, nessuna nuova).
5. **D26-5, pulizia documentale (§6)**: i docstring del codice nello stesso branch, con un commit separato (**raccomandato**),
   oppure in un branch a parte. I documenti di progetto restano comunque alla sessione principale (Piano, F4), a `des-planner`
   (nota nella Proposta F8) e a `des-manual-writer` (manuale).
6. **D26-6, esecutore**: `oc-developer` (raccomandato, §7) o `des-developer`.

> La sessione principale scrive qui le scelte (data, D26-1...D26-6) prima della delega. Il piano in §4 e' scritto per le opzioni
> raccomandate. Le parti che dipendono da D26-3 e D26-4 sono marcate **[se 3b]**, **[se 3a]** e **[se D26-4 = registrare]**.

**Scelte dell'utente (2026-10-29)**: D26-1 = A; D26-2 = nessun interruttore; D26-3 = 3b (conservare); D26-4 = registrare
S30-ABSENT (la fotografia 989 la installa la sessione principale); D26-5 = stesso branch, commit separato; D26-6 = **`des-developer`**
(Sonnet high) invece di `oc-developer`. Branch: `ai/cc-difetto26`. `des-developer` non committa: i commit li fa la sessione
principale (commit 1 = §4.1-§4.5 con i test; commit 2 = §6.1; commit 3 = rapporto).

---

## 4. Piano di intervento (opzioni raccomandate)

### 4.0 Ordine dei passi (per l'esecutore)

0. `git branch --show-current` deve essere `ai/oc-difetto26` (o `ai/cc-difetto26` per `des-developer`), creato dalla sessione
   principale. Se non lo e', fermati.
1. **Prima i test** (§4.3). Esegui i tre file (§4.4, comando) **senza** la correzione e scrivi nel rapporto quali test falliscono:
   devono essere esattamente quelli della colonna "prima" in §4.4.
2. Correzione A in `Logic/Readiness.py` (§4.1); **[se 3b]** anche §4.2.
3. Riesegui i tre file: tutti verdi. Riesegui anche `Test_Campaign_Types` e `Test_Session_Validator`: invariati.
4. **[se D26-4 = registrare]** la riga in `Scenario_Baseline.UNITS` (§4.5).
5. Commit 1: "Difetto 26: ...".
6. **[se D26-5 = stesso branch]** la pulizia dei docstring del codice (§6.1), commit 2 separato.
7. `bash tools/ai/verifica.sh suite start`, poi `wait` fino all'ESITO; dopo, `confronto start` e `wait`. Mai in parallelo.
8. Scrivi il rapporto `Analysis/Document/Rapporti/Rapporto_difetto26_<agente>.md` (`Rapporti/TEMPLATE.md`) e committalo.

### 4.1 `Logic/Readiness.py`: correzione A

**`readiness_after_session`** (`:168-249`). La firma non cambia.
- Sostituisci `:174` (`readiness: Dict[str, ReadyRecord] = {}`) con:
  ```python
      # I record degli asset non passati (forze assenti da questa sessione) restano com'erano:
      # il ciclo qui sotto scrive solo chiavi di `assets` (difetto 26).
      readiness: Dict[str, ReadyRecord] = {asset_id: record
                                           for asset_id, record in ledger.readiness.items()
                                           if asset_id not in assets}
  ```
- Il ciclo `:185-247` non cambia. In particolare il ramo "distrutto" (`:189-191`, `continue`) continua a NON scrivere il record:
  il record precedente di un asset distrutto e passato sparisce, come oggi.
- Docstring `:170-172`, nuovo testo:
  ```
  """La nuova mappa di prontezza dopo la sessione (regola nel docstring del modulo).

  I record degli asset NON presenti in `assets` (forze non passate a questa sessione) sono
  riportati tali e quali; per gli asset presenti decide solo la regola (un asset distrutto
  perde il suo record anche se ne aveva uno).
  """
  ```
- Docstring del modulo, sezione "Regola di `readiness_after_session`" (`:16-19`): aggiungi in coda la frase "I record degli asset
  non passati alla sessione restano nel registro com'erano (difetto 26)."
- `record_session` (`:252-259`): il codice non cambia. Nel docstring aggiungi "La prontezza degli asset non passati resta quella del
  registro."

**RNG e determinismo**: nessuna estrazione, nessun uso di `random`. La mappa e' ordinata da `_check_readiness_map`
(`Campaign_Types.py:273`), quindi l'ordine di inserimento non conta.
**Core indifferente al simulatore**: nessun import nuovo.
**Costanti**: nessuna nuova.

### 4.2 [se 3b] `Logic/Readiness.py`: `apply_campaign_processes` conserva il record concluso di un asset assente

`:298-307`. Sostituisci il ramo `if asset is None:` con:
```python
        if asset is None:
            # Asset non passato (forza assente da questa sessione): il record resta e il processo
            # sara' applicato alla prima sessione in cui l'asset tornera' (difetto 26).
            logger.debug(f"apply_campaign_processes: asset {asset_id!r} is absent; keeping its "
                         f"concluded readiness record until it returns")
            continue
```
Nuovo docstring (`:286-292`):
"Processi di campagna fra sessioni (D4.d) conclusi entro `t`. Per ogni record con `ready_at <= t + eps`, in ordine di id: asset
assente -> record CONSERVATO, applicato quando l'asset torna (difetto 26); asset distrutto -> record tolto; `record.repair` ->
`asset.health = 100`; `record.rearm` -> riarmo e rifornimento (`_rearm_and_refuel`); record tolto. Restituisce il registro con i
record non conclusi e quelli conclusi di asset assenti. IDEMPOTENTE (riapplicarlo con lo stesso registro e lo stesso `t` lascia
gli asset nello stesso stato)."

`Logic/Session_Campaign.py`: il codice non cambia. Nel docstring di `run_campaign_session` (`:115`), dopo
`(1) Readiness.apply_campaign_processes(ledger, assets, order.t_start)`, aggiungi "(i processi conclusi di asset assenti restano
nel registro fino al loro ritorno)".

[se 3a] Nessuna modifica di `apply_campaign_processes`. Il limite va dichiarato nel docstring del modulo, sezione "Regola":
"Un processo che si conclude mentre l'asset e' assente e' tolto senza essere applicato (warning): l'asset torna con lo stato di
prima e la riparazione riparte (limite dichiarato, difetto 26 / D26-3)."

### 4.3 Test

Logger mockati come gia' fanno i file (classe `_Base` in `Test_Readiness.py:47-59` e in `Test_Session_Campaign.py`;
`F.LoggerSilencer` per lo scenario). Nessuna classe base nuova.

**`Test/Test_Readiness.py`, classe `TestReadinessAfterSession`** (`:192`), tre test nuovi in coda:
1. `test_absent_asset_record_is_kept`: `prev = ReadyRecord('ghost', 9000.0, 1000.0, 8000.0, 0.0)`;
   `ledger = CampaignLedger(readiness={'ghost': prev})`;
   `ready = R.readiness_after_session(ledger, _order(asset_ids=('ac0',)), _outcome(movement_ends={'ac0': 3000.0}), self.assets)`.
   Asserzioni: `assertIn('ghost', ready)`, `assertEqual(ready['ghost'], prev)`, `assertIn('ac0', ready)`.
2. `test_destroyed_present_asset_previous_record_removed`: `self.v0.health = 0`;
   `ledger = CampaignLedger(readiness={'v0': ReadyRecord('v0', 9000.0, 1000.0, 8000.0, 0.0)})`;
   `ready = R.readiness_after_session(ledger, _order(), _outcome(), self.assets)`; `assertNotIn('v0', ready)`. E' un test di guardia
   contro un'unione ingenua: passa gia' oggi.
3. `test_record_session_keeps_absent_asset_record`: stesso `prev` di 1; `new = R.record_session(ledger, _order(), _outcome(), self.assets)`;
   `assertEqual(new.readiness['ghost'], prev)` (preceduto da `assertIn('ghost', new.readiness)`) e `assertEqual(new.last_end, 3600.0)`.

**[se 3b] `Test/Test_Readiness.py`, classe `TestApplyCampaignProcesses`** (`:286`):
4. **Riscrivi** `test_absent_asset_dropped_with_warning` (`:321-325`) come `test_absent_asset_record_kept`:
   `record = ReadyRecord('ghost', 1000.0, 0.0, 1000.0, 0.0)`; `new = R.apply_campaign_processes(CampaignLedger(readiness={'ghost': record}), self.assets, 1000.0)`;
   `assertEqual(new.readiness['ghost'], record)`; `self._readiness_logger.warning.assert_not_called()`.
5. Nuovo `test_absent_concluded_record_applied_when_asset_returns`: `self.v0.health = 60`;
   `ledger = CampaignLedger(readiness={'v0': ReadyRecord('v0', 1000.0, 0.0, 0.0, 1000.0)})`;
   `kept = R.apply_campaign_processes(ledger, {'ac0': self.ac0}, 2000.0)`: `assertEqual(self.v0.health, 60)`,
   `assertIn('v0', kept.readiness)`. Poi `done = R.apply_campaign_processes(kept, self.assets, 3000.0)`:
   `assertEqual(self.v0.health, 100)`, `assertIsNone(done.ready_at('v0'))`.

[se 3a] `test_absent_asset_dropped_with_warning` non cambia; 4 e 5 non si scrivono.

**`Test/Test_Session_Campaign.py`, classe `TestRunCampaignSession`** (`:127`), un test nuovo in coda:
6. `test_absent_force_keeps_readiness_record`: `record = ReadyRecord('ghost', 10000.0, 0.0, 10000.0, 0.0)`;
   `order = SessionOrder('S', t_start=0.0, t_end=3600.0, missions=())`;
   `fake_outcome = SessionOutcome(session_id='S', t_start=0.0, t_end=3600.0)`; con
   `patch.object(SS, 'run_session', return_value=fake_outcome)`:
   `_, new_ledger = SC.run_campaign_session(CampaignLedger(readiness={'ghost': record}), order, [self.block], [], lambda shooter, target: None)`.
   Asserzioni: `assertIn('ghost', new_ledger.readiness)`, `assertEqual(new_ledger.readiness['ghost'], record)`.

**Scenario nuovo S30-ABSENT in `Test/Test_Session_Scenarios_S30.py`**, classe `TestS30AbsentForce(F.LoggerSilencer, unittest.TestCase)`,
dopo `TestS30CampaignSequence` (prima di `if __name__ == '__main__':`). Usa le funzioni del modulo `_build_forces`,
`_movement_mission`, `_snapshot_of` senza cambiarle. Nessun contatto (Red-Depot a 300 km, ala parcheggiata senza missione):
**nessuna estrazione RNG**.

Costanti nuove in testa al modulo, accanto a `S1, S2, S3, S4` (`:92`):
```python
A1, A2, A3 = 'S30-ABSENT-1', 'S30-ABSENT-2', 'S30-ABSENT-3'
```
Funzione nuova accanto a `_movement_mission` (`:136-141`):
```python
def _mbt1_movement_mission(mech, dest_x: float) -> Mission:
    """Missione 'Movement' (POSITIONING) del solo `mbt1` verso (dest_x, MECH_Y) (offset di formazione di
    `routes_for`): serve solo a provare che l'ordine e' rifiutato (`ASSET_NOT_READY`)."""
    target = Target(kind=TargetKind.POINT, position=Point3D(dest_x, MECH_Y, 0.0))
    mission, = F.missions_for(mech, [(dest_x, MECH_Y)], mission_type='Movement', target=target,
                              only=[MBT1])
    return mission
```
`setUpClass` (scritto per esteso: gli istanti vengono dal registro e non sono scritti a mano):
```python
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.rules = SessionRules()
        cls.base, cls.wing, cls.mech, cls.red = _build_forces()
        with_mech = [cls.base, cls.wing, cls.mech]
        without_mech = [cls.base, cls.wing]
        cls.forces_b = [cls.red]
        cls.fire_control = F.make_fire_control()
        all_forces = with_mech + cls.forces_b

        cls.outcomes, cls.ledgers, cls.checkpoints = {}, {}, {}
        ledger = CampaignLedger()

        # Sessione 1: Blue-Mech presente; mbt0 in missione (turnaround), mbt1 gia' danneggiato (riparazione).
        t1_start, t1_end = cls.rules.window(0.0)
        order1 = SessionOrder(A1, t_start=t1_start, t_end=t1_end,
                              missions=(_movement_mission(cls.mech, FIRST_DEST_X),))
        outcome1, ledger = Session_Campaign.run_campaign_session(
            ledger, order1, with_mech, cls.forces_b, cls.fire_control)
        cls.outcomes[A1], cls.ledgers[A1] = outcome1, ledger
        cls.checkpoints[A1] = _snapshot_of(all_forces)

        # Sessione 2: Blue-Mech ASSENTE, dalla fine del turnaround di mbt0 (processo concluso
        # mentre la forza e' assente); la riparazione di mbt1 e' ancora in corso.
        cls.t2 = max(ledger.last_end, ledger.ready_at(MBT0))
        t2_start, t2_end = cls.rules.window(cls.t2)
        order2 = SessionOrder(A2, t_start=t2_start, t_end=t2_end, missions=())
        outcome2, ledger = Session_Campaign.run_campaign_session(
            ledger, order2, without_mech, cls.forces_b, cls.fire_control)
        cls.outcomes[A2], cls.ledgers[A2] = outcome2, ledger
        cls.checkpoints[A2] = _snapshot_of(all_forces)

        # Sessione 3: Blue-Mech di nuovo presente, alla fine prevista della riparazione di mbt1
        # (senza il suo record, prima della correzione, si ripiega sulla fine della sessione 2).
        ready_mbt1 = ledger.ready_at(MBT1)
        cls.t3 = ledger.last_end if ready_mbt1 is None else max(ledger.last_end, ready_mbt1)
        t3_start, t3_end = cls.rules.window(cls.t3)
        order3 = SessionOrder(A3, t_start=t3_start, t_end=t3_end, missions=())
        outcome3, ledger = Session_Campaign.run_campaign_session(
            ledger, order3, with_mech, cls.forces_b, cls.fire_control)
        cls.outcomes[A3], cls.ledgers[A3] = outcome3, ledger
        cls.checkpoints[A3] = _snapshot_of(all_forces)
```
Test della classe:
7. `test_absent_force_keeps_pending_record`. Premessa: `assertNotIn(MBT1, self.outcomes[A2].postures)` (la forza non e' nella
   sessione 2). Poi `assertIn(MBT1, self.ledgers[A2].readiness)` e
   `assertEqual(self.ledgers[A2].readiness[MBT1], self.ledgers[A1].readiness[MBT1])` (record identico: non e' ripartito ne' esteso).
8. `test_absent_asset_still_not_ready`. Precondizione con messaggio:
   `assertGreater(self.ledgers[A1].ready_at(MBT1), self.ledgers[A2].last_end, "precondizione: mbt1 e' ancora in riparazione alla fine della sessione 2 con i tempi di Context; se non lo fosse va rivista la sequenza di S30-ABSENT")`.
   Poi, su forze ricostruite: `base, wing, mech, red = _build_forces()`;
   `order = SessionOrder('S30-ABSENT-NOT-READY', t_start=self.ledgers[A2].last_end, t_end=self.ledgers[A2].last_end + self.rules.default_duration_s, missions=(_mbt1_movement_mission(mech, FIRST_DEST_X),))`;
   `with self.assertRaises(SessionValidationError) as raised: Session_Campaign.run_campaign_session(self.ledgers[A2], order, [base, wing, mech], [red], F.make_fire_control())`;
   esiste una violazione con `code is ViolationCode.ASSET_NOT_READY` e `asset_id == MBT1` (stesso schema di
   `test_not_ready_asset_is_rejected`, `:301-307`). Questa sessione e' dentro un metodo di test, quindi la fotografia non la
   registra.
9. `test_repair_continues_across_absence`: `assertAlmostEqual(self.t3, self.ledgers[A1].ready_at(MBT1), delta=1e-6)` (la sessione 3
   parte alla fine della riparazione registrata nella sessione 1); salute di `mbt1` 60 in `checkpoints[A1]` e `checkpoints[A2]`, 100
   in `checkpoints[A3]`; `assertNotIn(MBT1, self.ledgers[A3].readiness)` (la riparazione non e' ripartita).
10. `test_concluded_process_of_absent_asset`. Precondizione: `assertLessEqual(self.ledgers[A1].ready_at(MBT0), self.t2 + 1e-9)`
    (il turnaround di `mbt0` finisce mentre la forza e' assente). `consumed_1 = self.outcomes[A1].fuel_consumed().get(MBT0, 0.0)`;
    `assertGreater(consumed_1, 0.0)`.
    - **[se 3b]**: `assertEqual(self.ledgers[A2].readiness[MBT0], self.ledgers[A1].readiness[MBT0])` (conservato);
      `assertAlmostEqual(self.checkpoints[A2][MBT0]['fuel'], FUEL_FULL - consumed_1, delta=1e-9)` (non ancora rifornito);
      `assertAlmostEqual(self.checkpoints[A3][MBT0]['fuel'], FUEL_FULL, delta=1e-9)` (rifornito al ritorno);
      `assertNotIn(MBT0, self.ledgers[A3].readiness)`.
    - **[se 3a]**: `assertNotIn(MBT0, self.ledgers[A2].readiness)` (tolto senza essere applicato) e
      `assertAlmostEqual(self.checkpoints[A3][MBT0]['fuel'], FUEL_FULL - consumed_1, delta=1e-9)`. Docstring del test: "limite
      dichiarato (D26-3 = 3a)".

Docstring della classe: "S30-ABSENT: una forza assente da una sessione conserva i propri record di prontezza (difetto 26)."
Docstring del modulo: aggiungi prima della sezione "`Scenario_Baseline.UNITS`" (`:46`) la sezione:
```
## S30-ABSENT (`TestS30AbsentForce`, difetto 26)

Stesse forze di S30-CAMPAIGN, una sola missione (`mbt0` verso (10 km, -20 km)), tre sessioni:
  1. `S30-ABSENT-1` in `[0, 7200]` con `Blue-Mech`: turnaround di `mbt0`, riparazione di `mbt1`.
  2. `S30-ABSENT-2` SENZA `Blue-Mech`, da `max(last_end, ready_at('mbt0'))`: il record di `mbt1`
     resta identico; `mbt1` resta non impiegabile (`ASSET_NOT_READY`) alla fine della sessione.
     [3b] il record concluso di `mbt0` resta e il rifornimento arriva al ritorno.
     [3a] il record concluso di `mbt0` e' tolto senza effetto (limite dichiarato).
  3. `S30-ABSENT-3` di nuovo con `Blue-Mech`, da `max(last_end, ready_at('mbt1'))`: `mbt1` riparato
     (salute 100) e fuori dal registro.
Nessun contatto e nessuna estrazione RNG.
```
Togli dalla sezione la riga [3a] o [3b] che non si applica.
Se D26-4 = registrare, aggiungi alla sezione "`Scenario_Baseline.UNITS`" del docstring la riga
"`('S30-ABSENT', 'Test_Session_Scenarios_S30', 'TestS30AbsentForce', None, _single_or_index)`: tre esecuzioni nuove
(`S30-ABSENT/S30-ABSENT-1..3`)".

Import: `Mission`, `Target`, `TargetKind`, `Point3D`, `FUEL_FULL`, `SessionValidationError`, `ViolationCode`, `CampaignLedger`,
`SessionRules` e `SessionOrder` sono gia' importati nel modulo (`:53-83`). Non servono import nuovi.

### 4.4 Esiti attesi dei test (prima e dopo la correzione)

Comando per un file, dalla root del repo:
`<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Readiness` (e `.Test_Session_Campaign`,
`.Test_Session_Scenarios_S30`), con `<python>` = l'interprete che `verifica.sh` stampa nell'ESITO.

| Test | Prima (test nuovi, codice vecchio) | Dopo |
|---|---|---|
| 1 `test_absent_asset_record_is_kept` | FAIL | OK |
| 2 `test_destroyed_present_asset_previous_record_removed` | OK (guardia) | OK |
| 3 `test_record_session_keeps_absent_asset_record` | FAIL | OK |
| 4 [3b] `test_absent_asset_record_kept` (riscritto) | FAIL | OK |
| 5 [3b] `test_absent_concluded_record_applied_when_asset_returns` | FAIL | OK |
| 6 `test_absent_force_keeps_readiness_record` | FAIL | OK |
| 7 `test_absent_force_keeps_pending_record` | FAIL | OK |
| 8 `test_absent_asset_still_not_ready` | FAIL (l'ordine e' accettato) | OK |
| 9 `test_repair_continues_across_absence` | FAIL (`t3` = 29 454,5 invece di 41 760; salute 60) | OK |
| 10 `test_concluded_process_of_absent_asset` | [3b] FAIL; [3a] OK (documenta il limite) | OK |
| tutti i test esistenti dei tre file | OK | OK |

I valori fra parentesi vengono dalla sonda [S] (§1.5). Se un test della colonna "prima" non fallisce come indicato, o fallisce per
un altro motivo (per esempio un errore in `setUpClass`), fermati e riferisci.

**Suite** (dall'ESITO di `verifica.sh`, base 4701 OK, 7 skipped):
- [se 3b]: **4710 OK (7 skipped)**. Test nuovi: 1, 2, 3, 5, 6, 7, 8, 9, 10 = 9. Il 4 sostituisce un test esistente.
- [se 3a]: **4709 OK (7 skipped)**. Test nuovi: 1, 2, 3, 6, 7, 8, 9, 10 = 8.

### 4.5 [se D26-4 = registrare] `Test/Scenario_Baseline.py`

In coda a `UNITS`, dopo la voce S30-CAMPAIGN (`:373-375`) e prima della `)` di chiusura:
```python
    # ── S30-ABSENT (difetto 26: una forza assente conserva i record di prontezza) — in coda ──
    ('S30-ABSENT', 'Test_Session_Scenarios_S30', 'TestS30AbsentForce', None,
     _single_or_index),
```
Nomi stabili: `S30-ABSENT/S30-ABSENT-1`, `S30-ABSENT/S30-ABSENT-2`, `S30-ABSENT/S30-ABSENT-3` (un `session_id` per sessione,
nessuna variante). Le chiavi esistenti non cambiano.

### 4.6 Vincoli

- **RNG**: nessuna estrazione nuova e l'ordine di quelle esistenti non cambia (`Readiness` non usa numeri casuali, S30-ABSENT non ha
  contatti). Mai il modulo `random`.
- **Interruttori**: nessuno (D26-2; per 3b anche D26-3). Se l'utente sceglie 3c: costante di modulo
  `Readiness.KEEP_ABSENT_CONCLUDED_RECORDS: bool = False`, con il ramo di §4.2 eseguito solo se True e quello di oggi (`del` e
  warning) se False. In quel caso il test 4 diventa `test_absent_asset_record_kept_with_switch`
  (`patch.object(R, 'KEEP_ABSENT_CONCLUDED_RECORDS', True)`), `test_absent_asset_dropped_with_warning` resta, e nel test 10 vale il
  ramo [3a]. Suite: 4710.
- **Core indifferente al simulatore**: si toccano solo `Logic/Readiness.py` (core, nessun import nuovo) e i test.
- **Costanti**: nessuna nuova. I test calcolano tutto dal registro e da `Context` (tempi F8-R, in parte STIME dichiarate nei commenti
  di `Context.py:1013-1038`).
- **Nomi**: nessun nome esistente della fotografia cambia. S30-CAMPAIGN non si tocca (`setUpClass` e test invariati).
- **Import**: sempre con il percorso completo.
- **File che non si toccano**: `Command/Campaign_Types.py` (`with_readiness` resta una sostituzione, e
  `test_with_readiness_replaces` resta), `Logic/Session_Campaign.py` (solo docstring, [se 3b]), `Logic/Session_Validator.py`.

### 4.7 Esito atteso del confronto con la fotografia (`Test/baseline/scenario_baseline.json`, 986 esecuzioni)

| Caso | Identiche | Cambiate | Nuove | Perche' |
|---|---|---|---|---|
| D26-4 = registrare | **986** | **0** | **3** (`S30-ABSENT/S30-ABSENT-1..3`) | `run_session` non cambia; S30-CAMPAIGN ha registri e stato degli asset identici [S], quindi anche i suoi istanti `t3`/`t4`; le 3 nuove sono le sessioni di `TestS30AbsentForce.setUpClass` |
| D26-4 = non registrare | **986** | **0** | **0** | come sopra; la classe nuova non e' in `UNITS` |

Un'esecuzione CAMBIATA qualsiasi, in particolare `S30-CAMPAIGN/S30-CAMPAIGN-1..4`, non e' attesa: l'esecutore si ferma e
riferisce (elenco in `.ai-run/confronto.log`, `grep -E '^(CHANGED|NEW)'`). La fotografia **non** va installata dall'esecutore. Se
D26-4 = registrare, la installa la sessione principale dopo l'approvazione (989 esecuzioni). Il contenuto delle 3 esecuzioni nuove
dipende da D26-3 (il carburante di `mbt0` nella sessione 3), e la fotografia installata fissa la scelta fatta.

### 4.8 Documenti da aggiornare (dopo la verifica, non dall'esecutore salvo dove indicato)

- **Rapporto** (esecutore): elenco dei test che falliscono prima della correzione (§4.4), numeri dell'ESITO della suite e del
  confronto, scelte minori.
- `Piano_Implementazione_Missione.md` (sessione principale): riga F9 (`:309`), dove la voce 26 dice "DIFETTO APERTO": diventa
  "corretto (commit ..., Proposta_Difetto26_Readiness_Ledger.md)". Deviazione 25, "Limiti" (`:509-510`): con 3a, aggiungere il
  limite del processo concluso di un asset assente. Eventuale riga nuova "Difetto 26" nella tabella §5.
- `F4_Differenze_Scenari.md` (sessione principale): sotto "F8" (`:2588`), un paragrafo "Difetto 26" con commit, suite, confronto
  (986 identiche + 3 nuove o 0) e la descrizione di S30-ABSENT.
- `Proposta_F8_Sessione_Campagna.md` (proprieta' del pianificatore: una nota datata, a cura di `des-planner` o della sessione
  principale, senza riscrivere il contratto): a §4.4 `:794` "realizzato solo dopo il difetto 26"; [se 3b] a `:762` "asset assente:
  dal difetto 26 il record resta".
- Manuale DES (`des-manual-writer`): capitolo 7 §6.26 (`07_Orchestratore_Session_Simulator.md:1818-1824` regola,
  `:1820` `apply_campaign_processes`, `:1870-1873` la "divergenza trovata" da togliere); capitolo 9 (`09_Validazione.md:793`
  S30-ABSENT, `:808` conteggio di `Test_Readiness`, `:822` "nessun test copre" da togliere); capitolo 10 §9.6 voce 26 -> CHIUSA
  (`10_Limiti_Estensioni_Divergenze.md:959-963`).

---

## 5. Rischi e limiti

| Rischio / limite | Mitigazione o dichiarazione |
|---|---|
| Un asset tolto dalla campagna (id che non ricompare piu') lascia il record nel registro per sempre (A, e con 3b anche i record conclusi) | innocuo per validatore e `ready_assets`, che guardano solo gli asset passati; registro piccolo (un record per asset); da dichiarare nel docstring. Una pulizia esplicita ("asset ritirato") sarebbe una funzione nuova, fuori da questo intervento |
| Con 3a: un processo che finisce mentre l'asset e' assente e' perso, e la riparazione riparte al ritorno | limite dichiarato nel docstring, nel test 10 e nel Piano; motivo della raccomandazione 3b |
| Con 3b: lo stato di un asset assente (salute, carburante) resta vecchio finche' l'asset non torna, anche se il registro lo da' gia' pronto | coerente con "i processi si applicano agli asset presenti"; da scrivere nel docstring di `apply_campaign_processes` |
| La correzione dipende dall'identita' degli id di dominio fra sessioni | come tutto il registro (F8): se un asset cambia id, il suo record resta orfano |
| Le precondizioni di S30-ABSENT dipendono dai tempi di `Context` (turnaround a terra 6 h STIMA, riparazione 24 h) | precondizioni con un messaggio esplicito nei test 8 e 10; istanti calcolati dal registro |
| Nessun chiamante di produzione: la correzione si vede solo negli scenari | come tutta la F8c (deviazione 25); il futuro `Theater_Session_Manager` passera' sottoinsiemi di forze, ed e' proprio il caso corretto qui |
| "Il test deve fallire prima della correzione" si controlla solo se l'esecutore esegue i test prima del codice | passo 1 di §4.0 e colonna "prima" di §4.4, da riportare nel rapporto; la sessione principale puo' rifarlo durante la verifica (§7) |

---

## 6. Facoltativo, sezione separata: pulizia dei testi "STIME da sostituire con F8-R" e docstring di `CampaignState`

Voci 24, 25 e 27 del capitolo 10 §9.6 del manuale. Punti verificati sul codice e sui documenti il 2026-10-29. Sono **solo testo**:
nessun effetto su suite e confronto.

### 6.1 Nel codice (puo' farlo l'esecutore, nello stesso branch, commit separato)

| # | Dove | Testo attuale | Testo nuovo |
|---|---|---|---|
| P1 | `Logic/Readiness.py:12-14` (docstring del modulo, "## Tempi") | "STIME DI PROGETTO, dichiarate tali nel codice, da sostituire con la ricerca F8-R (commit di soli dati)" | "I tempi di turnaround e riparazione sono in `Context/Context` (`AIR_TURNAROUND_S`, `GROUND_TURNAROUND_S`, `SEA_TURNAROUND_S`, `REPAIR_TIME_FULL_S`): valori della ricerca F8-R del 2026-10-23 (`Analysis/Document/Ricerca_Turnaround_Riparazione.md`), ordini di grandezza e non dati tarati; dove la ricerca non ha trovato una fonte il valore resta una STIMA DI PROGETTO, come dice il commento in `Context`." |
| P2 | `Test/Test_Session_Scenarios_S30.py:4-7` (docstring del modulo) | "Le uniche novita' numeriche sono le STIME di progetto della tabella di turnaround/riparazione (`Context/Context`, §4.4, sostituite dalla ricerca F8-R) e le posizioni ..." | "Le uniche novita' numeriche sono i tempi di turnaround/riparazione di `Context/Context` (ricerca F8-R, in parte STIME DI PROGETTO dichiarate nei commenti) e le posizioni ..." |
| P3 | `Test/Test_Session_Scenarios_S30.py:291` (docstring di `test_not_ready_asset_is_rejected`) | "(precondizione: `ready_at('mbt0') > t2` con le stime di §4.4)" | "(precondizione: `ready_at('mbt0') > t2` con i tempi di `Context`)" |
| P4 | `Test/Test_Session_Scenarios_S30.py:294-295` (messaggio dell'asserzione) | "precondizione del piano: con le stime di §4.4 mbt0 non e' pronto a t2; se la ricerca F8-R la rendesse falsa va allungata la rotta della sessione 1" | "precondizione del piano: con i tempi di `Context` mbt0 non e' pronto a t2; se un cambio dei tempi la rendesse falsa va allungata la rotta della sessione 1" |
| P5 | `Test/Test_Readiness.py:4-6` (docstring del modulo) | "ricalcolati dalle costanti STIMATE dichiarate in `Context`" | "ricalcolati dalle costanti di `Context` (ricerca F8-R, in parte STIME dichiarate)" |
| P6 | `Test/Test_Context.py:1441` (docstring di `TestReadinessTables`) | "Tabelle di prontezza della F8 (D6.b-d): STIME di progetto in `Context` (§4.4)." | "Tabelle di prontezza della F8 (D6.b-d) in `Context`: valori della ricerca F8-R, in parte STIME di progetto (v. commenti)." |
| P7 | `Context/Campaign_State.py:29-102` (struttura interna nel docstring della classe) | non c'e' la chiave `ledger` | sotto `mission_id: {`, dopo `"regions": {...}`, aggiungere la riga `"ledger": dict   # optional: CampaignLedger.to_dict() (add_ledger, F8)` (in inglese, come il resto del docstring) |
| P8 | `Context/Campaign_State.py:104-108` ("Write API") | mancano i metodi del registro | aggiungere `add_ledger(mission_id, ledger)  — campaign ledger dict (CampaignLedger.to_dict(), F8)` |
| P9 | `Context/Campaign_State.py:110-118` ("Read API") | idem | aggiungere `get_ledger(mission_id)  → Optional[Dict]` |
| P10 | `Context/Campaign_State.py:122` ("Restore API") | `restore(mission_id, regions)   — applies snapshot ...` | `restore(mission_id, regions, restore_position=False)   — applies snapshot to live Region / Block / Asset objects (position only with restore_position=True, F8)` |

`Readiness.py:121` ("lineare, STIMA") resta: il modello lineare e' una stima, indipendente dalla ricerca.
`Context.py:1013-1038` e' gia' corretto e non si tocca.

### 6.2 Nei documenti (non dall'esecutore)

| # | Dove | Cosa | Chi |
|---|---|---|---|
| P11 | `Piano_Implementazione_Missione.md:306` (riga F8c) e `:507` (deviazione 25, "tabelle STIMATE, da sostituire con la ricerca F8-R") | "tabelle in `Context` (STIME di progetto, poi valori della ricerca F8-R applicati in `dc53af99`)" | sessione principale |
| P12 | `Piano_Implementazione_Missione.md:510` (deviazione 25, "Limiti: costanti di tempo STIMATE") | "costanti di tempo da ricerca F8-R, in parte STIME (non dati tarati)" | sessione principale |
| P13 | `F4_Differenze_Scenari.md:2607` ("tutte le tabelle ... sono STIME DI PROGETTO") | aggiungere "fino a F8-R: dal `dc53af99` i valori vengono dalla ricerca (`Ricerca_Turnaround_Riparazione.md`), in parte ancora stime" | sessione principale |
| P14 | `Proposta_F8_Sessione_Campagna.md:5` ("F8-R rinviata") e tabella §4.4 `:708-726` (i valori prima della ricerca) | una nota datata in testa al documento e sopra la tabella: "F8-R fatta e applicata il 2026-10-23 (`dc53af99`): i valori in vigore sono in `Context.py:1013-1038`; la tabella e' quella del contratto F8c". Il contratto non si riscrive | `des-planner` o sessione principale |
| P15 | Manuale, capitolo 10 §9.6 voci 24, 25 e 27 | chiudere dopo P1-P14 | `des-manual-writer` |

Nota: l'intestazione del Piano (riga 3) e la riga F9 (`:309`) non dicono piu' "F8-R in attesa", quindi della voce 24 resta solo P14.

### 6.3 Stesso branch o separato

Conviene lo **stesso branch, con un commit separato** (D26-5) per P1-P10. Due dei file (`Readiness.py` e
`Test_Session_Scenarios_S30.py`) sono gia' toccati dalla correzione: un secondo branch sugli stessi file creerebbe solo conflitti.
Il rischio e' nullo (solo docstring e il testo di un messaggio di asserzione) e i numeri attesi di suite e confronto non cambiano.
P11-P15 seguono il flusso di sempre: li fa la sessione principale dopo la verifica (Piano, F4, nota nella Proposta F8), e il
manuale `des-manual-writer`, insieme all'aggiornamento del manuale per il difetto 26 (§4.8).

---

## 7. Esecutore consigliato

**`oc-developer`** (DeepSeek V4 Pro), in una sola seduta.
- Dimensione: circa 10-15 righe di codice in `Readiness.py` (piu' circa 10 con 3b), circa 160-200 righe di test (8-9 test, di cui una
  classe di scenario con `setUpClass` scritta per esteso qui), 3 righe in `Scenario_Baseline`, circa 30 righe di docstring (§6.1).
- Rischio basso: nessuna modifica del motore, nessuna estrazione RNG, esito del confronto noto in anticipo (identiche + nuove) e
  verificato con una sonda; tutte le decisioni sono scritte nel piano. Il solo punto delicato, `setUpClass` dello scenario con gli
  istanti presi dal registro, e' dato per esteso.
- Costo: una seduta e' molto meno della F8c (3 blocchi). Il limite di 120 passi e' sufficiente se suite e confronto girano con
  `verifica.sh` come da AGENTS.md.
- `des-developer` (Sonnet) e' un'alternativa equivalente se si preferisce non fare il giro di verifica OpenCode (modello effettivo,
  CSV OpenRouter, costi) per un intervento cosi' piccolo.

Verifica della sessione principale: oltre alla procedura di CLAUDE.md, rieseguire i tre file di test con il solo
`Logic/Readiness.py` del commit base e controllare che i test falliscano come in §4.4. Si fa nel checkout principale, mai in un
worktree e senza `git stash`, che alla verifica deve restare vuota:
`git show <base>:Code/Dynamic_War_Manager/Source/Logic/Readiness.py > Code/Dynamic_War_Manager/Source/Logic/Readiness.py`, poi i
tre file di test, poi `git checkout -- Code/Dynamic_War_Manager/Source/Logic/Readiness.py` e `git status` pulito.
