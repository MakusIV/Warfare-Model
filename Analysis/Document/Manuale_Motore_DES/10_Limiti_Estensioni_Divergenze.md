# Capitolo 9 — Limiti noti, punti di estensione, divergenze codice/wiki

## 9.1 Limiti noti (dichiarati nel codice, non difetti nascosti)

Raccolti dai "Cosa NON fa" dei singoli moduli, già citati nei capitoli precedenti; qui riuniti
per avere un solo punto di riferimento.

### Selezione dell'arma dai registri — non fatta

`fire_control` è sempre **iniettata** dal chiamante (`Logic/Engagement_Resolver.py:131-133`): il
risolutore non seleziona mai un'arma da `Ground_Weapon_Data`/`Ship_Weapon_Data`/loadout aerei, e
non modula la Pk con la posizione nell'inviluppo di tiro. È il pezzo su cui, in parallelo alla
stesura di questo manuale, sta lavorando un altro filone di sviluppo (`Asset/Ground_Weapon_Data.py`,
`Asset/Ship_Weapon_Data.py`, `Context/Context.py`, nuovo `Logic/Fire_Control.py`) — non descritto
qui (v. l'introduzione del manuale). Negli scenari di validazione (capitolo 8) il ruolo è coperto
da `Scenario_Fixtures.make_fire_control`, dichiarato esplicitamente come tabella di ruoli non
calibrata, non come sostituto di una selezione reale.

### Fog-of-war reale non collegato

Il fog-of-war del progetto vive in `Context/Region`/`Logic/Tactical_Analysis`/
`Logic/Tactical_Evaluation` (`recon_cp_snapshot`, `use_recon`, la policy "non visto → priorità
bassa" di `feedback_no_visibility_low_priority`) ed è una nozione **informativa** di livello C2:
decide le priorità di targeting a partire da ciò che la ricognizione ha confermato. Il motore di
sessione (`Session_Simulator`, `Engagement_Resolver`) **non ha oggi nessun aggancio** a quel
sistema: non riceve uno snapshot di ricognizione e non conosce priorità
(`Test/Test_Session_Scenarios.py`, docstring di `TestS9PartialFogOfWar`). Le due nozioni di
"visibilità" — geometrica (nel raggio di un sensore, ciò che `Contact_Scheduler` calcola) e
informativa (confermata dal C2) — non sono quindi ancora collegate. Lo scenario S9 esercita solo
il punto di iniezione geometrico (`detection_factor`), non l'informazione C2; è un gap
**documentato, non aggirato** (v. capitolo 8, §8.4).

### Re-scheduling delle finestre di contatto dopo un cambio di rotta — rimandato

Se un asset cambia rotta durante una finestra di contatto già calcolata dallo scheduler (Fase 3),
la finestra andrebbe invalidata e ricalcolata: questo meccanismo **non esiste**, perché finora
nessun consumatore modifica una rotta dopo che le finestre sono state prodotte
(`Logic/Engagement_Resolver.py:108-110`, R4 seconda parte). Concretamente, una forza che si
disingaggia è solo **segnalata** nell'esito (`ForceOutcome.outcome = DISENGAGED`); il nuovo
instradamento e il ricalcolo delle finestre spettano a un livello superiore (C2/campagna), non
ancora costruito. V. §9.2 per la divergenza fra questo comportamento e il testo originale della
decisione che lo ha proposto.

### La Pd non distingue radar da ottico

`weather_detection_factor` applica un fattore di degradazione **unico** a qualunque sensore
abbia prodotto la portata della finestra di contatto, perché la finestra stessa non porta
l'informazione "quale sensore" (`Logic/Engagement_Resolver.py:536-541`). Un radar non dovrebbe
subire la stessa degradazione notturna di un sensore ottico, ma oggi la subisce comunque, con un
compromesso pesato verso il radar. La discriminazione per tipo di sensore richiede che la
finestra di contatto porti anche il sensore che l'ha prodotta — un cambiamento nello strato 1.

### Altri limiti dichiarati, minori

- **Ripartizione del fuoco**: round-robin locale per tiratore (`_schedule_next`,
  `Logic/Engagement_Resolver.py:992-1030`), non un'assegnazione ottima arma-bersaglio (nessun
  WTA, nessun peso per valore del bersaglio o per Pk della coppia).
- **`salvo_window` di default 0.0**: solo impatti simultanei formano un evento-salva; la finestra
  giusta per raggruppare impatti ravvicinati è un punto aperto di modello, da decidere con la
  taratura (`Logic/Engagement_Resolver.py:1397-1400`).
- **Nessun movimento fisico fra sessioni**: `run_session` non aggiorna `asset.position` a fine
  rotta; una campagna che concatena sessioni vede le forze ripartire dalle posizioni iniziali a
  ogni sessione, a meno che il chiamante non aggiorni le posizioni da sé
  (`Test/Test_Session_Validation.py:259-261`, v. capitolo 8, §8.3).
- **Carburante esaurito a metà rotta**: l'asset non viene fermato sulla rotta né i contatti già
  calcolati vengono ricorretti; l'informazione (`FuelEvent.exhausted`) è nell'esito, e la userà
  un livello superiore (capitolo 6, §6.5).
- **`calcFightResult` (fallback aggregato a rapporto di forze) resta invariato**: nessuna delle 7
  fasi lo ha toccato, per scelta esplicita (wiki `decisions/soglie-disingaggio-e-attrito-aggregato`
  §P2); se mai verrà riscritto, il bersaglio dichiarato è una forma eterogenea a matrice di
  letalità incrociata con coefficienti solo da ATCAL interno, mai da tabelle a mano.
- **Sensori 'ground' assenti nei registri** per carri/corazzati/artiglieria e per le navi (v.
  capitolo 8, §8.1): senza un'iniezione esplicita, due forze terrestri non si vedono mai. Non è
  un bug del motore, è un dato mancante nei registri d'arma che nessun chiamante di produzione
  compensa ancora.
- **Nessun rifornimento nel motore**: né di munizioni né di carburante. È dichiarato materia del
  ciclo di campagna in entrambi i moduli (`Logic/Fuel_Model.py:31-32`, wiki
  `decisions/risolutore-ingaggio-salva-fase4` §R3).

## 9.2 Divergenze fra il codice e la wiki di progetto

Verificate confrontando il codice a HEAD con i tre documenti indicati come fonte
(`Analysis/WIKI_LLM_SIMULATION/wiki/decisions/virtual-session-engine-des.md`,
`risolutore-ingaggio-salva-fase4.md`, `soglie-disingaggio-e-attrito-aggregato.md`). Il codice
prevale; qui si segnala dove il testo della wiki, letto alla lettera, descrive un comportamento
diverso da quello implementato.

### D1 — Re-scheduling dopo disingaggio: la proposta originale (P1) descrive un comportamento non implementato

Il corpo della decisione P1 in `soglie-disingaggio-e-attrito-aggregato.md` (§"P1 — Soglia di
disingaggio come esito di ingaggio di prima classe") dice testualmente: *"al superamento,
l'ingaggio termina con esito `DISENGAGED` distinto da `DESTROYED`, e **la forza che si
disingaggia rientra nello scheduler dei contatti con una nuova rotta** (non sparisce)"*.

Il codice implementato non fa questo: `Logic/Engagement_Resolver.py:108-110` dichiara
esplicitamente che il "re-scheduling dopo spostamento fisico" (di cui il rientro nello scheduler
con una nuova rotta è un caso) è la **seconda parte di R4, rimandata** — non Fase 4. Una forza
`DISENGAGED` è oggi **solo segnalata** nel `ForceOutcome`: nessun codice la re-instrada né
ricalcola le finestre di contatto per lei. Questo non è un'incoerenza nascosta: il blocco di
stato in cima a `soglie-disingaggio-e-attrito-aggregato.md` (`status: accepted`, aggiornato
2026-09-23) e il blocco equivalente in `risolutore-ingaggio-salva-fase4.md` §"Punti aperti —
RISOLTI" registrano correttamente che "R4: re-scheduling ora o rimandato → **rimandato** ...al
primo consumatore reale". Il corpo originale della proposta P1, però, non è stato riscritto per
riflettere questa decisione successiva, e un lettore che si fermasse al solo corpo della sezione
P1 (senza leggere fino ai blocchi di stato/punti aperti) si farebbe un'idea sbagliata del
comportamento attuale. Vale quindi la correzione: **oggi il rientro nello scheduler non esiste**,
coerentemente con quanto descritto in questo manuale al capitolo 4, §4.9 e qui sopra in §9.1.

### D2 — Nessun'altra divergenza sostanziale trovata

Il resto dei tre documenti (decisioni Q1-Q3, R1-R4 prima parte, P1 negli esiti/soglie, P3) è
coerente con il codice a HEAD punto per punto, per quanto verificato nella stesura di questo
manuale: soglie di dottrina in `Context/Doctrine.py` come dichiarato; saturazione con funzione
dedicata (`Military.salvo_interception_capacity`, distinta da `air_defense_power`) come
dichiarato in R1; munizioni per asset senza rifornimento nel motore come dichiarato in R3;
congelamento del payload come dichiarato in R4 prima parte; batteria S1-S18 con la stessa regola
dichiarata in P3 (composizione e domanda, mai numeri precalcolati).

## 9.3 Punti di estensione (dove agganciare sviluppi futuri)

Riassunto operativo per chi estenderà il motore, con il punto esatto del codice:

| Estensione | Punto di aggancio |
|---|---|
| Selezione arma dai registri | Sostituire la `fire_control` iniettata con una funzione reale che consulta `Ground_Weapon_Data`/`Ship_Weapon_Data`/`Aircraft.assigned_loadout`; firma invariata `(shooter, target) -> ShotSpec \| None` (`Logic/Engagement_Resolver.py:1358-1366`). |
| Fog-of-war reale | Comporre `detection_factor` con l'informazione di `recon_cp_snapshot`/`use_recon` (`Context/Region`), sullo stesso punto di iniezione già usato dal meteo (`weather_detection_factor_fn`, `Logic/Engagement_Resolver.py:574-588`). |
| Re-scheduling dopo disingaggio | Livello C2/campagna: leggere `ForceOutcome.outcome == DISENGAGED` dal `SessionOutcome`, decidere una nuova rotta, e far ripartire `Contact_Scheduler.schedule_contacts` per quella forza in una sessione successiva (non dentro `resolve_engagement`, che è a stato ombra e non muta rotte). |
| Pd per tipo di sensore | La finestra di contatto (`ContactWindow`) dovrebbe portare il sensore che l'ha prodotta, non solo la portata; `detection_factor` potrebbe allora distinguere radar da ottico (`Logic/Contact_Scheduler.py:188-223`, `Logic/Engagement_Resolver.py:536-541`). |
| Assegnazione ottima arma-bersaglio | Sostituire la regola greedy round-robin di `_schedule_next` (`Logic/Engagement_Resolver.py:992-1030`) con un algoritmo di weapon-target assignment, mantenendo l'invariante del payload congelato (R4 prima parte). |
| Movimento fisico persistente fra sessioni | Far scrivere a `run_session` (o a un futuro `Theater_Session_Manager`) la posizione finale di ogni asset mobile a fine sessione, oggi non aggiornata (`Logic/Session_Simulator.py`, v. capitolo 6 §6.5 e capitolo 8 §8.3). |
| Rifornimento (munizioni/carburante) | Materia esplicitamente del ciclo di campagna, non del motore DES: da costruire come passo separato che precede una nuova `SessionOrder`, consumando `Mobile.load_ammunition_from_registry`/`load_fuel_from_registry` o equivalenti. |

## 9.4 Stato del motore a questo commit

Le 7 fasi della roadmap (contratto+RNG, cinematica, percezione, scheduler dei contatti,
risolutore d'ingaggio, applicazione dello stato/carburante, orchestratore, validazione — 7 fasi
enumerate nella wiki, con la cinematica e la percezione assorbite nelle precondizioni delle fasi
successive) sono **complete**: non c'è un "prossimo passo obbligatorio" per il motore DES in sé.
I seguiti possibili sono esattamente quelli elencati in §9.3, nell'ordine di priorità indicato
dalla wiki di progetto: selezione arma dai registri (in corso in parallelo a questo manuale),
collegamento del fog-of-war reale, e — oggetto di questo stesso documento — il manuale che si
sta leggendo.
