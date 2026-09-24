# Piano: manuale del motore DES + scelta arma dai registri + nebbia di guerra

## Contesto
Il motore delle sessioni virtuali (DES, 7 fasi) è completo e la suite è verde (3371 OK, 5 saltati, verificata su osboxes il 2026-09-24). Restano tre attività:
1. **Manuale** Markdown con diagrammi sull'architettura del motore. Da scrivere in parallelo agli sviluppi.
2. **Scelta arma dai registri**: oggi `fire_control(shooter, target) -> ShotSpec | None` esiste solo come tabella a ruoli di test (`Test/Scenario_Fixtures.py:528-652`).
3. **Nebbia di guerra reale** collegata a `detection_factor` (gap S9). Si fa dopo la 2.

Scelte dell'utente:
- manuale con Sonnet 5, sforzo alto;
- sviluppi delegati a un agente Opus 5.5, sforzo medio, con verifica mia (rilettura del codice + suite completa);
- efficacia antiaerea ricavata aggiornando le tabelle dei registri con la classificazione degli aerei proposta dall'utente;
- ricognizione presa come istantanea fissata prima della sessione.

## Passo 0 — Definizioni di agente del progetto
Lo sforzo di un sottoagente si imposta solo dalla definizione in `.claude/agents/*.md`. Prima di scriverle, verifico il nome esatto del campo dello sforzo nel frontmatter (documentazione di Claude Code).
- `.claude/agents/des-manual-writer.md`: `model: sonnet`, sforzo alto. Strumenti: Read, Grep, Glob, Bash (sola lettura), Write limitato alla cartella del manuale.
- `.claude/agents/des-developer.md`: `model: opus`, sforzo medio. Strumenti completi.

Nel prompt di entrambi vanno le regole del progetto:
- **niente worktree**: i test in un worktree danno falsi esiti;
- **interprete**: `python3` di sistema su osboxes;
- **comando della suite**: `python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_*.py"` dalla root;
- **import**: path completi `from Code.Dynamic_War_Manager.Source...`;
- **mai valori inventati spacciati per tarati**: le stime vanno dichiarate come tali.

## Attività A — Manuale (agente des-manual-writer, in background)
- Destinazione: `Analysis/Document/Manuale_Motore_DES/`. Contiene `Manuale_Motore_DES.md` e un eventuale file per ogni capitolo.
- Diagrammi in **Mermaid** dentro il Markdown: si vedono in Obsidian e su GitHub. Su questa macchina non ci sono né Java né PlantUML, quindi niente PNG.
- Contenuto minimo (dalla memoria di progetto):
  - i 4 strati: contratto `Command/Session_Types.py`, `Logic/Contact_Scheduler.py`, `Logic/Engagement_Resolver.py`, applicazione dello stato + `Logic/Fuel_Model.py`;
  - l'orchestratore `Logic/Session_Simulator.py` e il flusso dei dati;
  - un diagramma di sequenza della coda eventi (heapq, regola di parità);
  - diagrammi delle classi dei tipi di dominio (`ContactWindow`, `ShotSpec`, `Salvo`, `Detection`, `EngagementResult`, `SessionOrder`/`SessionOutcome`);
  - RNG seedato (`Utility/Session_Rng.py`), le soglie di disingaggio in `Context/Doctrine.py`, `Context/Reaction_Profile.py`;
  - il perché delle scelte: DES invece del tick, modello a salva di Hughes, RNG seedato;
  - la batteria di validazione S1-S18.
- Fonti: il codice al commit `f61aa2b7` più le pagine wiki `Analysis/WIKI_LLM_SIMULATION/wiki/decisions/virtual-session-engine-des.md` e `risolutore-ingaggio-salva-fase4.md`.
- Le aggiunte delle attività B e C diventano un breve capitolo aggiuntivo, da scrivere dopo che si sono stabilizzate.
- Verifica mia: controllo a campione i diagrammi contro il codice (nomi di classi, campi, ordine delle chiamate).

## Attività B — Scelta arma dai registri (agente des-developer, prima)

### B1. Classificazione degli aerei come bersaglio (proposta, poi decisione dell'utente)
- Nuove classi di bersaglio aereo nei modelli di efficacia:
  - `Ground_Weapon_Data.py`: `_EFF_SAM_SHORAD/MERAD/LORAD` (oggi hanno bersagli terrestri inadatti), `_EFF_AA_CANNON`, `_EFF_AA_CANNON_57MM`, `AMMO_TARGET_EFFECTIVENESS`;
  - `Ship_Weapon_Data.py`: SAM e `CIWS`, con lo stesso principio.
- Regola dell'utente per la resistenza (`destroy_capacity`):
  - **Attacker** (per esempio A-10, Su-25) = righe di `Armored`, se non emergono incongruenze a parità di arma; altrimenti `Soft`;
  - **Fighter / Fighter_Bomber** (per esempio F-16) sono meno resistenti dell'attacker. Vanno distinti bene dall'attacker in base a `Air_Asset_Type` (`Context/Context.py:717`) e al campo `category` di `Aircraft_Data`;
  - **Bomber / Heavy_Bomber**: resistenza minore o uguale a quella del fighter.
- Nota da sottoporre all'utente: la `accuracy` delle righe Soft/Armored dei SAM è pensata per bersagli a terra (per esempio 0.1). Per gli aerei serve una `accuracy` propria, che per i bombardieri, più grandi e meno manovrabili, deve essere più alta.
- Classi non coperte dalla regola: Helicopter, Awacs, Recon, Transport. L'agente propone come mapparle.
- **Consegna intermedia**: una tabella di valori proposti con motivazione. **Nessuna scrittura nei registri prima dell'approvazione dell'utente.**
- Aggancio: estendere `Context.get_target_classification` / `get_weapon_target_class` (`Context/Context.py:1550`, `:1615`) perché un bersaglio `Aircraft` porti alla sua sottoclasse. Se `category` ha più voci, vince la più resistente.

### B2. Nuovo `Logic/Fire_Control.py`
- `make_registry_fire_control(...) -> Callable[[shooter, target], ShotSpec | None]`. Il contratto `ShotSpec` e la firma di `fire_control` non cambiano; il motore (`Engagement_Resolver`, `Session_Simulator`) non viene toccato.
- Selezione dell'arma:
  - candidate: per i veicoli `record.weapons` di `Vehicle_Data._registry` o `Ship_Data._registry`, per gli aerei i piloni di `Aircraft.assigned_loadout`;
  - filtro sulle armi adatte al bersaglio, riusando la logica di `Mobile.air_defense_volume` / `combat_range` (`Asset/Mobile.py:1276`, `:1348`);
  - chiave del bersaglio: `get_weapon_target_class(get_target_classification(...))` + `Context.classify_asset_dimension`;
  - si sceglie l'arma con il valore di accuracy × destroy_capacity più alto.
- **Deterministico**: si legge `efficiency[class][dim]` direttamente. Non si usa `get_weapon_score_single_target`, che usa il `random` globale (`Ground_Weapon_Data.py:1378`).
- Campi derivati per categoria, con costanti dichiarate come stime:
  - `interceptable` = True per i missili e le bombe guidate;
  - `time_of_flight` = portata tipica / `speed`, quando disponibile;
  - `rounds` e `cycle_time` da `fire_rate` per i cannoni, e con una salva dottrinale di default per i missili;
  - `weapon` = il nome del modello.
- Si ritorna `None` se nessuna arma è adatta.
- Limite dichiarato: senza la distanza la Pk non dipende dalla posizione nell'inviluppo. Resta invariato.
- Test: `Test/Test_Fire_Control.py`, con selezione per veicolo, nave e aereo, antiaerea contro Attacker/Fighter/Bomber, caso `None` e determinismo. Più uno scenario in `Test_Session_Scenarios*.py` che fa girare `run_session` con il fire control dei registri. La tabella a ruoli delle fixture resta invariata.

## Attività C — Nebbia di guerra (agente des-developer, dopo B)
- In `Logic/Engagement_Resolver.py`, accanto a `meteo_detection_factor` (:591), solo funzioni costruttrici (niente modifiche al motore):
  - `recon_detection_factor_fn(seen_block_ids, *, observer_side, unseen_factor, seen_factor=1.0)`: fattore ridotto se `target.block.id` non è tra quelli visti. Si applica solo agli osservatori del lato dato e non consuma l'RNG. Ricorre ad `Asset.block` (`Asset/Asset.py:374`).
  - `combine_detection_factors(*fns)`: prodotto dei fattori, sempre in [0,1], per usare insieme meteo e ricognizione.
- Costruttore lato Region, per esempio `region_recon_detection_factor(region, observer_side)`, che scatta l'istantanea una volta prima della sessione. La ricetta è `Tactical_Analysis.build_recon_cp_snapshot(region.get_recon_reports(enemy))` (`Logic/Tactical_Analysis.py:54`, `Context/Region.py:826`), come fa già `update_military_priorities`.
- Costante dichiarata: `unseen_factor`. È da decidere con l'utente se modularla anche con `Military.get_recon_efficiency()` dell'osservatore.
- S9 (`Test/Test_Session_Scenarios.py:773-866`): si aggiunge un caso con una Region vera e l'istantanea al posto della lambda. Il test esistente resta.

## Attività D — Volumi di rilevamento/ingaggio generici (accettata 2026-09-24, dopo C)
- Oggi `run_session` usa solo una sfera (distanza 3D ≤ portata di rilevamento, `Contact_Scheduler.range_intervals`); il cilindro `ThreatAA` è usato solo da `Air_Route_Manager` e da `threat_windows` (non chiamato dalla sessione).
- Interfaccia "volume": intervalli di permanenza su un tratto a moto relativo rettilineo uniforme. Primitive: sfera, cilindro verticale, fascia di quota, cono (cono di silenzio / campo visivo), orizzonte radar. Combinatori: unione, intersezione, differenza di intervalli.
- Il volume diventa `detection_volume` / `engagement_volume` per asset e per arma. La sfera `max_range` del controllo di portata è il primo caso particolare.
- Prima una proposta di progetto da far approvare all'utente, poi l'implementazione.

## Sequenza ed esecuzione
1. Passo 0, poi A in background insieme a B1 (proposta dei valori).
2. Presento all'utente la tabella B1 e raccolgo la decisione. Poi B2, seguita dalla mia verifica: rilettura dei file nuovi e suite completa.
3. C, seguita dalla mia verifica.
4. Capitolo aggiuntivo del manuale su B e C, poi la mia verifica del manuale.
5. Commit separati per attività su `analysis/dce-dcs-persistence`, solo quando l'utente li chiede. Il push solo su richiesta.
6. Aggiornamento della memoria di progetto (motore DES, recap della sessione).

## Verifica
- Suite completa dalla root con `python3` di sistema: 3371 test più quelli nuovi, tutti OK. Il riepilogo di unittest va letto dal log completo, non da `tail` in pipe.
- Scenario end-to-end: `run_session` con `make_registry_fire_control` e con meteo e ricognizione combinati. Deve dare esiti riproducibili con lo stesso seed.
- Manuale: nomi e campi nei diagrammi confrontati con il codice. I blocchi Mermaid devono essere sintatticamente validi.
