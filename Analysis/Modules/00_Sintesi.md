# Sintesi — Audit dei moduli (2026-08-16)

## Come leggere questo documento

Questo è il documento di sintesi prodotto dopo l'analisi approfondita di tutti gli 11 sottosistemi del Dynamic War Manager (documenti `01_...md`–`11_...md` in questa cartella). Non ripete il dettaglio — per quello vedi i singoli documenti — ma **riorganizza tutti i problemi trovati per leva d'intervento**: quali fix sbloccano di più con il minor rischio, quali richiedono una decisione di design dell'utente prima di poter essere affrontati, e quale roadmap complessiva ne consegue.

**Metodo usato**: 11 subagenti paralleli hanno letto il codice sorgente completo (non solo i test) ed eseguito realmente la suite di test (`python -m unittest discover`) e, dove possibile, istanziato direttamente le classi per verificare i bug empiricamente, non solo per lettura statica. Ogni affermazione sotto è verificata, non dedotta.

## Il quadro d'insieme, in una frase

**La maggior parte dei test unitari passa non perché il codice funzioni, ma perché i test aggirano sistematicamente la costruzione reale degli oggetti con mock/stub** — e quando si prova a costruire gli oggetti veri (`Vehicle()`, `Ship()`, `Structure()`, `Manager()`, un blocco `Production`/`Storage`/`Transport`/`Urban`, un `Edge` di `DataType`, un `Threat`, un `Limes`...) quasi nessuno si istanzia con i parametri di default. Il progetto è meno maturo di quanto il tasso di successo dei test suggerisca, ma i problemi sono in larga parte **meccanici e localizzati** (parametri mancanti, refusi, import sbagliati), non architetturali — con un paio di eccezioni importanti (il layer decisionale e il layer Lua↔DCS, vedi sotto).

## Blocchi ad alta leva (fix meccanici, sbloccano molto, rischio quasi nullo)

Questi sono i fix da fare per primi: ciascuno richiede da 1 a poche righe, è già verificato empiricamente, e sblocca test/moduli oggi completamente inutilizzabili.

| #   | Fix                                                                                          | File:riga                                                   | Sblocca                                                                                                                                              | Verificato                         |     |
| --- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | --- |
| 1   | Rimuovere import morto `Aircraft`                                                            | `Aircraft_Weapon_Data.py:5`                                 | L'intera catena `Aircraft_Data`/`Aircraft_Loadouts`/`Aircraft_Weapon_Data` (3 file di test, 655 metodi `test_*` scritti)                             | Sì, empiricamente in copia isolata |     |
| 2   | Rimuovere import morto `Aircraft`                                                            | `Ground_Weapon_Data.py:5`                                   | `Vehicle`/`Vehicle_Data`/`Ground_Weapon_Data` (3 file di test)                                                                                       | Sì, punto di aggancio confermato   |     |
| 3   | `Sea_Asset_Type.FAST_ATTACK` → `.CORVETTE`                                                   | `Initial_Context.py:101`, `Actual_Context.py:70`            | Import di entrambi i moduli (oggi `AttributeError` certo)                                                                                            | Sì                                 |     |
| 4   | `Vehicle_Data.get_vehicle_scores`: validazione per-elemento invece di `scores not in SCORES` | `Vehicle_Data.py:4646`                                      | Ogni istanziazione di `Vehicle` con modello valido (oggi `ValueError` sistematico) — pattern corretto già presente in `Ship_Data.py:1505` da copiare | Sì, logica inequivocabile          |     |
| 5   | `Logger(..., class_name='')` → nome reale                                                    | `Tactical_Evaluation.py:42`, `Strategical_Evaluation.py:28` | Import di entrambi i moduli                                                                                                                          | Sì                                 |     |
| 6   | `GROUND_Military_VEHICLE_ASSET` → `GROUND_MILITARY_VEHICLE_ASSET`                            | `Strategical_Evaluation.py:17`                              | Import del modulo (a monte del fix #5 per questo file)                                                                                               | Sì                                 |     |
| 7   | `Block                                                                                       | None` con `Block` modulo non classe + `List` non importato  | `Scenario_Manager.py:10,29`                                                                                                                          | Import del modulo                  | Sì  |

**Nota**: i fix #1/#2 (import morti) sono la causa **diretta** del blocco totale del sottosistema Asset-Air e di metà di Asset-Ground-Naval — non sono workaround, sono la vera causa radice, confermata rimuovendo la riga in una copia isolata del repository. Non serve alcun refactoring architetturale per il ciclo di import: bastano due righe.

## Blocchi ad alta leva ma più profondi (richiedono più cura, ancora meccanici)

| # | Problema | File | Impatto | Nota |
|---|---|---|---|---|
| 8 | `Mobile.checkParam`/`checkParamDCS` definiti senza `self` esplicito, firma incompatibile con l'override nelle sottoclassi | `Mobile.py:345-358,360` | **Nessuna istanza di `Vehicle`/`Ship`/`Aircraft` è costruibile con i parametri di default oggi** (`TypeError` in `__init__`) | Il bug singolo più impattante dell'intero progetto: blocca la costruzione di ogni asset mobile, a prescindere dal ciclo di import |
| 9 | `Structure.__init__` passa argomenti posizionali disallineati a `super().__init__()`, più `super.checkParam` senza parentesi | `Structure.py:46,55` | `Structure` non istanziabile in nessuna configurazione | Nessuna sottoclasse concreta la usa oggi — priorità bassa finché non si decide se resta in roadmap (vedi decisioni aperte) |
| 10 | `Production`/`Storage`/`Transport`/`Urban.__init__`: `super().__init__()` con troppi argomenti posizionali + `self.checkParam()` mai esistito | 4 file, `Block/` | L'intero layer economico dei blocchi (produzione, stoccaggio, trasporto, città) non istanziabile | Codice fermo da >1 anno, va riscritto seguendo il pattern di `Military.py`, non solo "corretto" |
| 11 | `DataType/Edge.py.__init__`: `self.calcLenght(self)` (refuso di `calcLength`, + `self` extra) | `Edge.py:32-33` | Nessun `DataType.Edge` reale esiste mai in memoria, nonostante sia il tipo dichiarato per `Route.edges`/`Region._routes` | Bug indipendente dalla `Edge` locale di `Air_Route_Manager.py` (quella funziona, sono due classi diverse con lo stesso nome — vedi decisioni aperte) |
| 12 | `checkParam` senza `self`/`@staticmethod` + controllo `check_results[1]` invece di `[0]` (validazione sempre inerte) | `Edge.py`, `Waypoint.py`, `Area.py` | Validazione dei parametri di fatto disattivata in 3 classi — pattern copiato 3 volte | Da correggere in un solo passaggio, stesso identico bug |
| 13 | `Limes()` solleva `AttributeError` anche senza argomenti | `Limes.py:24` | Blocca anche `Manager.py` (che le passa una stringa invece di un `Dict`) | Nessun test la esercita |

## Il layer decisionale (Logic/) non è collegato — gap più rilevante rispetto all'obiettivo di progetto

L'obiettivo dichiarato del progetto è un motore che "analizza la situazione... e decide azioni... in particolare tattico e strategico". Oggi:

- **`Scenario_Manager.py`, `Strategical_Evaluation.py`, `Tactical_Evaluation.py`, `Air_Resources_Assigner.py` non si importano mai a vicenda** (verificato via grep incrociato) — non esiste alcuna pipeline scenario→strategia→tattica→allocazione nel codice, solo nell'intento.
- Di questi 4, **3 non sono nemmeno importabili oggi**, ciascuno per un bug locale distinto e indipendente dal ciclo di import Asset-Air (righe 5-7 della tabella sopra) — quindi anche dopo aver risolto tutto il resto, questi moduli restano stub concettuali:
  - `Strategical_Evaluation.py`: **0% di logica funzionante**, solo funzioni `pass` + uno schizzo di design (`ConflictGraph`/`PrioritySystem`) che non compila.
  - `Scenario_Manager.py` (classe `CommandControl`): scheletro con qualche CRUD funzionante ma bacato, sezioni core (lettura/scrittura dati DCS, valutazione missione) tutte `pass`. Concettualmente un doppione parziale di `Region`/`Military`, mai completato.
  - `Tactical_Evaluation.py`: l'unico dei tre con logica reale (fuzzy logic per azione tattica/accuratezza ricognizione/risultato scontro, aderente all'UML) — ma una funzione chiave (`evaluateGroundRouteDangerLevel`) presuppone un'API su `Military` (`time2attack`, `is_airbase`, `artilleryInRange`) mai implementata, segno che è stata scritta prima del refactoring di `Block`/`Military`.
- **`Air_Resources_Assigner.py`** è il più maturo (logica completa, 196 test scritti) ma oggi bloccato solo dal ciclo di import Asset-Air (fix #1/#2 sopra lo sbloccano).

**Conseguenza pratica**: anche risolvendo tutti i bug meccanici elencati sopra, il DWM non avrebbe ancora un vero "cervello" decisionale collegato — quello va in gran parte **scritto da zero**, non solo corretto. `Tactical_Evaluation.py` è la base più solida da cui ripartire.

## Il layer di integrazione DCS/Lua non esiste

Dallo schizzo in `Analysis/Document/WM_Software_Structure.pdf`: DCS scambia `mission_param`/`mission_result` con moduli Lua, che dialogano con un modulo Python intermedio, che alimenta il DWM.

**Verificato**: `mission_param`/`mission_result` hanno **zero occorrenze** in tutto il codice sorgente. `Context.DCS_DATA_DIRECTORY` (path Windows hardcoded) non è mai letto/scritto da nessuno. `Manager.py` (il candidato più naturale per essere il DWM) e `Scenario_Manager.CommandControl` (l'altro candidato) sono entrambi orfani — nessuno dei due è importato da alcun altro modulo, e **`Manager('QualunqueRegione')` non si istanzia nemmeno** (`TypeError` da `Limes(stringa)` invece di `Limes(Dict)`). `Asset.dcs_unit_data`/`Mobile.checkParamDCS` sono punti di validazione pronti a ricevere dati DCS già convertiti in dict Python, ma non esiste alcun parser Lua→Python a monte che produca quei dict.

**Conseguenza pratica**: questo è puro lavoro da **costruire ex novo**, non da correggere. È l'altro grande pezzo mancante rispetto all'obiettivo di progetto, insieme al layer decisionale sopra.

## Decisioni di design che servono da te prima di poter procedere

Questi problemi non hanno un fix meccanico ovvio — richiedono una scelta:

**Stato (aggiornato 2026-08-21 — Fase 2 chiusa, dettaglio completo in `.claude/memory/project_fase2_design_decisions.md`):**

1. **`Structure.py` resta in roadmap?** ✅ **DECISO: resta in roadmap, va sviluppata.** Non istanziabile, non usata da alcuna sottoclasse concreta, zero test. Ambito non ancora specificato — da definire quando affrontata in Fase 3.
2. **`Production`/`Storage`/`Transport`/`Urban.py` (layer economico dei Block): riscrivere seguendo `Military.py` come modello?** ✅ **DECISO: sì, riscrivere seguendo Military.py.** Modello confermato dall'utente e verificato contro il codice: ogni `Block` possiede un `Resource_Manager` (componente costruito in `Block.__init__`) che lo rende nodo di una rete client/server di scambio risorse (`Payload`: `goods`/`energy`/`hr`/`hc`/`hs`/`hb`), con consumo interno (`resources_to_self_consume`) e magazzino (`warehouse`) propri; `Military`/`Production`/`Transport`/`Urban` si distinguono per ruolo (combattimento, produzione, trasporto, contesto urbano/produzione hr). Gap concreto trovato: i costruttori attuali di `Production`/`Storage`/`Transport`/`Urban` hanno ancora un parametro `block: Block` ridondante (residuo pre-refactor) e `acp`/`rcp`/`payload` assenti in `Military.__init__` — la riscrittura deve anche allineare le firme.
3. **Route/Edge/Waypoint: tre implementazioni incompatibili** (`DataType`, `Air_Route_Manager.py` locale, `Ground_Route_Manager.py` locale) senza alcun ponte. ✅ **DECISO ED ESEGUITO (commit `60335b5e`, 2026-08-21): `DataType.Route`/`Edge`/`Waypoint` canonico per terra.** `Air_Route_Manager.py` resta con le sue classi locali (già funzionanti, 22/22 test, non alimentano comunque `Region`). Motivazione: `Region.add_route`/`get_route`/`get_shortest_route`/`get_safest_route` e `Tactical_Evaluation.evaluateGroundRouteDangerLevel` dipendono strutturalmente da `DataType.Route`/`Edge` — non erano isole morte, semplicemente non avevano mai funzionato. Sistemati tutti i bug meccanici che lo impedivano (molti di più dei 2 originariamente stimati — dettaglio completo in `.claude/memory/project_fase2_design_decisions.md`): refusi di nomi metodo, `checkParam` non `@staticmethod` su sia `Edge` che `Waypoint` (disallineava tutti gli argomenti), indicizzazione sbagliata sul risultato di validazione, `Line3D` chiamata con `Waypoint` invece di `Point3D`, bug in `Waypoint.point2d`, `Military.time_to_ground_intercept`/`time2attack` con default rotti, guardia logica sbagliata, ramo mancante per basi navali. Verificato end-to-end costruendo oggetti reali (non mock): `Waypoint → Edge → Route → Military.time2attack → time_to_ground_intercept → Route.travelTime()`. `Ground_Route_Manager.py` (ha già proprie classi locali `Waypoint`/`Edge`/`NavigationGraph`, oltre a Dijkstra) dovrà produrre in uscita — o convertire a fine calcolo — oggetti `DataType.Route`/`Edge` per poter alimentare `Region.add_route` e sbloccare la catena di priorità militare: lavoro di sviluppo non ancora iniziato (Fase 3). `Tactical_Evaluation.evaluateGroundRouteDangerLevel` resta sostanzialmente non implementata oltre il fix del singolo bug meccanico trovato (`Route.edges` → `route.edges.items()`) — marcata `# da testare` nel codice stesso, chiama metodi/attributi inesistenti (`v_base.efficiency`, `is_airbase`, `artilleryInRange`), non è mai stata una vera implementazione: completarla è lavoro di Fase 3, non un fix meccanico.
4. **Geometria delle minacce: `Threat`/`Sphere`/`Hemisphere`/`Volume` vs `Cylinder`.** ✅ **DECISO: `Cylinder` è il modello attuale.** Geometria più realistica (via `Volume`) trattata come upgrade futuro, non nel lavoro corrente. `Threat`/`Sphere`/`Hemisphere`/`Volume` restano deprecate per ora (non eliminate).
5. **`Military.intelligence()`: implementare o eliminare `Region.get_region_intelligence_efficiency()`?** ✅ **RISOLTO (commit `7a5fa679`, 2026-08-21).** `Military.get_c2_efficiency()` confermato come unica metrica; `Region.get_region_intelligence_efficiency()` e i suoi 2 test eliminati (nessun chiamante in produzione).
6. **`Manager.py` vs `Scenario_Manager.CommandControl`: chi è il vero orchestratore DWM?** ⏸️ **SOSPESO** su richiesta esplicita dell'utente — non ancora deciso.
7. **`Coalition.py`** — ⏸️ **SOSPESO** su richiesta esplicita dell'utente (già rimandato anche nella pulizia dei file morti del 2026-08-16).
8. **`Classi.py`** (in `DataType/`) — ✅ **DECISO ED ESEGUITO: eliminato** (nessun riferimento nel codice, verificato prima della cancellazione).
9. **`visualizer.py`** — ✅ **DECISO ED ESEGUITO: aggiornato, non rimosso.** Serviva all'utente per definire visivamente i parametri degli scenari di `Test_Air_Route_Manager.py`. Riscritto per lavorare con gli oggetti reali (`ThreatAA`/`Cylinder`/`Route` di `Air_Route_Manager`) invece delle classi giocattolo isolate che aveva prima; selezione del backend matplotlib resa robusta (fallback automatico se l'ambiente non ha un backend interattivo disponibile, come nel caso di questa sessione dove tkinter/Qt non sono installati). Verificato end-to-end con uno scenario reale (minaccia + rotta calcolata da `RoutePlanner.calcRoute`), rendering corretto.

## Debito minore (basso rischio, bassa urgenza — pulizia quando si tocca il file comunque)

- Bug matematici in `Utility.py`: `indicated_air_speed()` usa `^` (XOR) invece di `**` (potenza) → risultati privi di senso; `calcVectorDiff`/`calcVectorSum`/`calcScalProd` hanno indici sbagliati sulla componente z/y. Nessuna di queste funzioni è oggi usata in produzione da un percorso testato, ma vanno corrette prima che lo diventino.
- `Region.get_sorted_priority_blocks()` muta in-place una lista `@lru_cache`, corrompendo la cache per chiamate successive.
- UML disallineati dal codice: `Military.plantuml` (segna `air_defense`/`combat_range`/`combat_state` come stub, sono già implementati); `Mobile.plantuml` (mostra `fire_range`/`attackRange`/`airDefense` mai più esistenti). Nessun UML esiste per `Ship`/`Structure`/`Logistic_Lines` (parzialmente) — quest'ultimo però riflette fedelmente codice comunque rotto.
- Fixture di test disallineate (fix a costo quasi zero, nessun rischio): `Test_Resource_Manager.MockBlock` manca `.name` (12 test); `Test_Air_Route_Manager` ha `Edge`/`ThreatAA` istanziate con argomenti mancanti (26 test, bug è nel test non nel codice di produzione).
- Numerosi import morti/inutilizzati sparsi (`heapq` in `Military.py`, `Payload` in `Block.py`, `setName`/`setId`/`mean_point`/`validate_class`/`defaultdict` in `Resource_Manager.py`, `skfuzzy`/`numpy` in `Air_Resources_Assigner.py`, ecc.) — utile un passaggio di lint (`pyflakes`) una volta sbloccati gli import.
- `Logistic_Lines.py` (gestione rifornimenti tra Block) non funzionale e non collegato a nulla — 6 bug strutturali distinti, nessun test. Rilevante perché il vero motore di rifornimento sembra essere `Component/Resource_Manager.py` (quello sì maturo, solo bloccato da un test fixture da una riga).

## Roadmap proposta

**Fase 1 — Sblocco meccanico (poche ore, rischio quasi nullo).** I 13 fix della prima e seconda tabella sopra, in quest'ordine: prima i due import morti (#1, #2 — sbloccano il maggior numero di test in assoluto), poi FAST_ATTACK/Logger/import-typo/Block|None (#3, #5, #6, #7 — sbloccano il resto di Context-Foundation e Logic/), poi `Vehicle_Data.get_vehicle_scores` (#4) e `Mobile.checkParam` (#8 — sblocca la costruzione reale di asset). A questo punto quasi tutta la suite test gira per davvero, non su mock, e diventa possibile scrivere test di integrazione reali per la prima volta.

**Fase 2 — Decisioni di design (conversazione con te, non codice).** Le 9 domande della sezione sopra. Il loro esito determina la forma del lavoro successivo (riscrivere vs. rimuovere vs. deprecare).

**Fase 3 — Costruzione del layer mancante (il vero "sviluppo nuovo").** Il pezzo più grande: collegare `Scenario_Manager`/`Strategical_Evaluation`/`Tactical_Evaluation`/`Air_Resources_Assigner` in una pipeline reale, e costruire il layer di scambio dati Lua↔DCS (che oggi non esiste). Qui si concentra la vera nuova ingegneria, non manutenzione.

**Fase 4 — Pulizia debito minore.** Bug matematici, UML disallineati, fixture di test, import morti, lint.

## Indice dei documenti per sottosistema

| Doc | Sottosistema | Stato sintetico |
|---|---|---|
| [01_Asset_Air.md](01_Asset_Air.md) | Aircraft, Aircraft_Data, Aircraft_Loadouts, Aircraft_Weapon_Data | Logica di dominio solida, bloccato al 100% da 2 import morti |
| [02_Asset_Ground_Naval.md](02_Asset_Ground_Naval.md) | Vehicle, Ship + dati/armi | Metà navale verde (298 test OK), metà terrestre bloccata dall'import + bug di validazione |
| [03_Asset_Base.md](03_Asset_Base.md) | Asset, Mobile, Structure | Bug bloccante di costruzione (`checkParam`) per tutte le sottoclassi; `Structure` non istanziabile |
| [04_Context_Foundation.md](04_Context_Foundation.md) | Context, Initial/Actual_Context, Logistic_Lines | `Context.py` solido (145 test OK); resto non importabile o non funzionale |
| [05_Context_State.md](05_Context_State.md) | Region, Campaign_State, Target_Status_History | Solido (202/203 test OK); 1 test drift + 1 bug cache reale |
| [06_Block.md](06_Block.md) | Block, Military, Production/Storage/Transport/Urban | `Block`/`Military` solidi (178 test OK) con bug residui; 4 sottotipi economici non istanziabili |
| [07_Logic_Routing.md](07_Logic_Routing.md) | Air/Ground_Route_Manager | Algoritmo funzionante e testato (30/30 core), ma isolato dal resto del sistema |
| [08_Logic_Decision.md](08_Logic_Decision.md) | Scenario_Manager, Strategical/Tactical_Evaluation, Air_Resources_Assigner | Il gap più grande: 3/4 moduli non importabili, nessuna pipeline collegata |
| [09_Component.md](09_Component.md) | Resource_Manager | Logica completa e coerente, bloccato da 1 riga di fixture test |
| [10_DataType.md](10_DataType.md) | Area, Cylinder, Edge, Event, Route, State, ecc. | Eterogeneo: `State`/`Payload`/`Cylinder` solidi, `Edge`/`Limes`/`Threat`/`Volume` rotti |
| [11_Utility_Manager.md](11_Utility_Manager.md) | Utility, LoggerClass, visualizer, Manager | `Manager.py` (candidato nucleo DWM) non istanziabile, orfano; layer Lua↔DCS assente |
