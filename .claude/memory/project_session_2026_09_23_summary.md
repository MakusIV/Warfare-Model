---
name: project-session-2026-09-23-summary
description: "Recap sessione 2026-09-23: git pull di 15 commit rimasti indietro (lavoro fatto il 22/9 sulla VM Oracle VirtualBox), poi decisione dell'utente sulle 3 proposte pendenti (soglie di disingaggio, LLM locale, modello a salva Fase 4). Implementazione della Fase 4 delegata a un agente Opus effort alto, in corso."
metadata:
  node_type: memory
  type: project
  originSessionId: 4f24ae57-a1fd-4207-aa69-d0ba0c8c5df1
  modified: 2026-09-23T13:04:53.524Z
---

**Promemoria multi-macchina**: l'utente lavora su almeno 3 macchine (VM Oracle VirtualBox Ubuntu,
Asus ProArt P16, e questa). Il repo puo' avere commit avanti che questa sessione non vede finche'
non si fa `git fetch`+merge esplicito — **fallo sempre a inizio sessione**, non fidarti della
memoria per lo stato del branch. V. [[project_dev_environment]].

## Cosa e' successo in questa sessione

1. L'utente ha chiesto un riassunto di stato; la memoria era ferma al 21/9. L'utente ha segnalato
   che il locale era indietro rispetto a origin (lavoro fatto il 22/9 sulla VM). `git fetch` ha
   confermato: locale indietro di **15 commit** su `analysis/dce-dcs-persistence`. Fast-forward
   eseguito, nessun conflitto (working tree locale era pulito).
2. Il pull ha portato: Fase 2 del motore DES (percezione), le 3 questioni del §9 chiuse (Route
   unico, contratto danno, SAM/AAA/EWR dimensione separata), Fase 3 (`Contact_Scheduler.py`),
   ingestione Lanchester (S1-S11) e Hughes/salvo model, con **3 pagine wiki `status: proposed`**
   che richiedevano decisione dell'utente. Dettaglio completo gia' in
   [[project_session_2026_09_22_summary]] e [[project_virtual_session_engine_design]] (che si sono
   auto-aggiornate su disco dopo il pull, via il sync hook memoria<->repo).
3. **Le 3 proposte sono state discusse e decise** (v. sotto). Aggiornate le pagine wiki
   corrispondenti (`status: accepted`/`proposed` rimandata) + `index.md` + `log.md` in
   `Analysis/WIKI_LLM_SIMULATION/wiki/`.
4. L'utente ha chiesto esplicitamente di usare **Opus, effort alto** per lo sviluppo che segue
   (Fase 4). V. [[feedback_opus_high_effort_for_dev]] se esiste, altrimenti trattare come
   preferenza valida per questa fase di lavoro.

## Le 3 decisioni prese (2026-09-23)

### 1. Soglie di disingaggio (P1) + batteria S1-S11 (P3) — ACCETTATE
- La soglia di disingaggio (sia erosione cumulata P1 sia shock da salva R2, v. sotto) vive in
  **`Context/Doctrine.py`** come parametro dottrinale **di lato** (non C2 per-sessione, non profilo
  d'asset).
- Il disingaggio scatta **per forza intera**, non per singolo asset (nonostante il vincolo di
  progetto sia "perdite per singolo asset" — sono due granularita' diverse, decise
  indipendentemente).
- `Logic/Tactical_Evaluation.calcFightResult` **non viene toccato** per ora (default raccomandato,
  accettato senza obiezioni): resta il fallback aggregato cosi' com'e' fino a dopo la Fase 4.
- Gli scenari **S1-S11 sono confermati batteria ufficiale**, ma **solo per la Fase 7** — nessun test
  anticipato durante la Fase 4.
- P2 (bersaglio futuro per un eventuale riscrittura di `calcFightResult`, matrice CADEM +
  coefficienti solo da ATCAL interno) resta una nota di orientamento, nessuna azione richiesta ora.

### 2. Ruolo dell'LLM locale nel motore — RIMANDATA (non rifiutata, non accettata)
Risposta dell'utente testuale: *"Per il momento non consideriamo LLM nel motore"*. Interpretato
come rimando dell'intera domanda, non come rifiuto di R2 (che sarebbe stato comunque l'esito
raccomandato): **nessuna delle 4 opzioni (R1 regola generale, R2 esclusioni, R3 debrief narrativo,
R4 uso offline in progettazione) e' stata formalizzata**, R3 non entra nemmeno nel backlog a
priorita' bassa. La pagina wiki resta `status: proposed` con una nota di aggiornamento, non
`superseded`. **Impatto pratico su Fase 4: nessuno** — `Engagement_Resolver.py` nasce comunque in
forma chiusa, perche' era gia' il comportamento di riferimento anche prima di questa proposta.

### 3. Modello a salva per la Fase 4 (da Hughes) — R1-R4 ACCETTATE INTEGRALMENTE
- **R1 (saturazione difensiva per-salva)**: la capacita' di intercettazione vive in una **nuova
  funzione dedicata** su `Military` (non un riuso di `Military.air_defense_power()` con scala
  diversa) — decisione esplicita per tenere separati i due concetti (potenza AD aggregata vs
  saturazione per singolo evento-salva). Il valore numerico **non va inventato**: stessa disciplina
  di P2, calibrazione futura via ATCAL interno o dichiarazione utente.
- **R2 (soglia di shock da salva)**: stessa sede (`Context/Doctrine.py`) e stessa granularita' (per
  forza intera) della soglia P1 — le due soglie devono restare coerenti, come richiesto dal
  documento originale.
- **R3 (scorte munizioni per asset — precondizione nuova, non nelle 11 originarie)**: granularita'
  **per asset** (un contatore aggregato, non per arma installata ne' per tipo di munizione).
  **Il rifornimento e' esplicitamente fuori dallo scope Fase 4/5**: e' materia del ciclo di
  campagna piu' ampio (es. quando un asset rientra in una base) — possibile punto di contatto con
  `Rinomina_Campaign_State.py` (riservato, v. [[project_rinomina_campaign_state]]).
- **R4 (congelamento payload + re-scheduling)**: il congelamento del payload all'istante di fuoco
  (niente ricalcolo retroattivo di una salva gia' in volo se il lanciatore viene distrutto dopo) e'
  **adottato subito** come vincolo di design di `Engagement_Resolver.py`. Il re-scheduling delle
  finestre di contatto dopo un cambio di rotta a ingaggio in corso resta **rimandato** (default
  raccomandato, accettato senza obiezioni) al primo consumatore reale — probabilmente un ordine di
  ritirata C2 — e riguarda lo strato 1 (`Contact_Scheduler.py`), non la Fase 4.

## Stato pagine wiki dopo questa sessione
Aggiornate in `Analysis/WIKI_LLM_SIMULATION/wiki/decisions/`:
`soglie-disingaggio-e-attrito-aggregato.md` (proposed→accepted), `risolutore-ingaggio-salva-fase4.md`
(proposed→accepted), `llm-locale-ruolo-e-confini.md` (resta proposed, nota di rimando aggiunta).
Piu' `wiki/index.md` (tabella decisioni + data) e `wiki/log.md` (nuova voce). **Non ancora
committato su git** al momento in cui questa memoria viene scritta.

## Fase 4 — FATTA e verificata (stesso giorno, 2026-09-23)
Implementazione delegata a un agente Opus (effort alto, richiesta esplicita dell'utente) con tutti
e 4 i vincoli di design sopra. Dettaglio completo, file per file, in
[[project_virtual_session_engine_design]] (sezione "FASE 4"). Questa sessione ha **verificato** il
lavoro (non solo fidandosi del report dell'agente): riletto per intero `Engagement_Resolver.py` +
le sezioni nuove di `Doctrine.py`/`Military.py`, e **rieseguita indipendentemente** la suite
completa con `.direnv/python-3.12/bin/python3` (non `venv/bin/python3`, Python 3.14 senza
dipendenze su questa macchina) — **3002 test, OK (skipped=5)**, stesso numero dichiarato
dall'agente. Qualita' del codice alta, coerente con le 4 decisioni.

**11 punti aperti di calibrazione**, lasciati con l'opzione piu' conservativa: v. la lista completa
in [[project_virtual_session_engine_design]]. Nessuno blocca l'uso del risolutore ne' e' stato
ancora sottoposto all'utente.

**Anche registrato in questa sessione** (messaggio dell'utente durante l'implementazione Fase 4,
non legato al codice): cadenza confermata di **6 sessioni virtuali** dopo ogni sessione DCS, e
riarmo/aggiornamento stato dopo OGNI sessione prima della successiva — v.
[[project_c2_hierarchy_design]], nessun impatto sul codice di Fase 4.

**Stato git**: nulla e' stato committato. Il working tree contiene: Fase 4 (codice + test),
tutti gli aggiornamenti alle 3 pagine wiki decisions + index.md + log.md, e le memorie di questa
sessione. Da decidere con l'utente se/come suddividere in commit.

**How to apply**: se la sessione che legge questa memoria trova `Logic/Engagement_Resolver.py`
assente, qualcuno ha fatto un `git reset`/checkout distruttivo dopo questa sessione — verificare
con l'utente prima di rifare il lavoro da zero. Se il file esiste, la Fase 4 e' fatta: passare
alla Fase 5 o ai punti aperti, non richiedere di nuovo le 3 decisioni originarie (sono chiuse).

## Decisioni sui punti aperti di Fase 4 (stesso giorno, 2026-09-23)
Presentati tutti gli 11 punti aperti all'utente. Decisioni:
- **Ripartizione fuoco fra tiratori**: passare a round-robin semplice (era: nessun coordinamento).
- **`salvo_window`**: lasciare 0 (raccomandato).
- **Munizioni aerei**: derivarle ORA dal loadout assegnato (era: raccomandato lasciarle illimitate,
  l'utente ha preferito farlo subito nonostante non esista ancora un concetto di "loadout assegnato
  all'istanza Aircraft" — l'agente di follow-up deve introdurlo).
- **Ordine dei colpi intercettati**: lasciare com'e' (raccomandato).
- **Pd degradata da meteo/notte**: collegarla ORA a `Logic/Meteo_Analysis` (era: raccomandato
  rimandare, l'utente ha preferito farlo subito).
- **Soglia P1 a conteggio minimo per categoria critica**: non implementare, solo frazione
  (raccomandato).
- Gli altri 5 punti (selezione arma dai registri, denominatore soglie, `interceptable` per-arma,
  interpretazione shoot-look-shoot, conflitto potenziale su `Doctrine.py` al merge con
  `feature/c2-doctrine-per-side-fase-a`) non richiedevano una decisione oggi — sono lavoro di fase
  successiva o scelte gia' coerenti.

**Secondo agente Opus (effort alto) lanciato** per implementare le 3 decisioni che richiedono
codice (round-robin, munizioni aerei da loadout, Pd-meteo). V. quando torna per l'esito: se questa
memoria non e' stata ancora aggiornata con un esito, il lavoro e' probabilmente ancora in corso o
la sessione si e' interrotta prima di verificarlo — controllare `git status`/`git diff` su
`Engagement_Resolver.py`, `Mobile.py`, `Aircraft.py` prima di rilanciare da zero.

**Commit fatto**: `44bc6950` su `analysis/dce-dcs-persistence`, un commit unico come richiesto
(Fase 4 + le 3 rifiniture + wiki + memoria), **non pushato**. Suite finale verificata due volte
indipendentemente da questa sessione (non solo dai report degli agenti): **3027 test, OK
(skipped=5)**, con `.direnv/python-3.12/bin/python3` (non `venv/bin/python3`, Python 3.14 senza
dipendenze su questa macchina).

**Rifiniture consegnate dal secondo agente**: round-robin per la ripartizione del fuoco fra
tiratori convergenti (`Engagement_Resolver._engaged_shooters`/`_schedule_next`, greedy locale,
mai fa aspettare un tiratore pronto); `Aircraft.assigned_loadout` (nuovo, non esisteva alcun
concetto di "loadout di questo volo" su un'istanza) + `ammunition_from_registry()` override che
somma pylon (esclusi serbatoi/pod) + gun_rounds; degradazione della Pd da meteo/notte
(`weather_detection_factor`/`meteo_detection_factor` in `Engagement_Resolver.py`, NIGHT=0.7,
ADVERSE_WEATHER=0.8, dichiarati come stime, si moltiplicano).

**4 note dell'agente, verificate e accettate senza ulteriore azione** (nessuna blocca nulla):
assegnare un loadout "riarma" l'aereo sovrascrivendo consumi precedenti — deviazione dichiarata
dalla regola "il setter delle munizioni serve solo a inizializzazione/persistenza" di `Mobile`,
ma coerente con la decisione di riarmo-a-inizio-sessione gia' registrata in
[[project_c2_hierarchy_design]]; il contatore aggregato mescola munizioni cannone e missili (675
colpi cannone + 8 missili in un solo numero) — stesso limite gia' presente per i veicoli
terrestri (cannone + ATGM), non nuovo; i pod di razzi contano "1" per pylon (quantita' letterale
dai registri, potrebbe sotto-contare i razzi effettivi in un pod); la Pd non distingue sensori
radar/ottici nella degradazione meteo (limite dichiarato, `ContactWindow` non porta il tipo di
sensore).

**Prossimo passo**: Fase 5 (applicazione danno/consumi in un'unica passata, assemblaggio verso un
futuro `SessionOutcome`) — non ancora iniziata.
