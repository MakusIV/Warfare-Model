# Proposta: scorta di munizioni per arma (A) e rotte d'attacco con quota di sgancio (B)

**Stato**: ANALISI E PROPOSTA (2026-09-26), in attesa delle decisioni dell'utente (§5). Nessun file
di codice modificato, nessun test scritto. Tre script di prova in sola lettura sono stati eseguiti
fuori dal repository, nella scratchpad di sessione (§3).
**Aggiornamento 2026-09-27 — Proposta B IMPLEMENTATA** (primo giro, senza l'entità `Mission`):
- decisioni: B1 fatta il 2026-09-26 (dati `release`); B2 tutte le missioni; B3 sostituita dalla D-8
  di `Proposta_Volumi_Rilevamento_Intercettazione.md` §4 (due liste di minacce, esposizione dopo il
  primo lancio possibile); B4 livellato/picchiata/cabrata con un solo modello balistico vettoriale;
  B5 direzione libera; B6 sì, subito; B7 fatta il 2026-09-26; drag selezionabile: `low_drag` se la
  quota ci sta, altrimenti `high_drag`;
- codice: `Logic/Weapon_Delivery.py` (balistica + `plan_attack_profile` + transiti opzionali con
  `RoutePlanner.calcCanonicalRoute`), `Command/Attack_Types.py` (`AttackProfile`, `ThreatExposure`),
  `Logic/Fire_Control.py` (B6: `max_range`/`time_of_flight` delle bombe dalla balistica),
  `Block/Military.air_defense_threats` (ora imposta `source_id`, per legare V_I e V_R dello stesso sito);
- scostamenti dal §2.4: le finestre del tratto d'attacco usano l'intervallo analitico
  `_segment_cylinder_interval` e non `route_threat_windows` (sympy, troppo lento per centinaia di
  candidati); spareggio aggiuntivo sull'azimut più vicino alla base; la geometria di picchiata/cabrata
  entra solo nella balistica, non nel tratto IP → sgancio (a quota costante);
- test: `Test/Test_Weapon_Delivery.py` + classe `TestFireControlBombRelease`; suite 3645 OK.

**Oggetto**: (A) verificare che il contatore aggregato `Mobile.ammunition` lasci sparare un asset con
armi che non ha più, e valutare una scorta compatibile con missione e bersaglio; (B) valutare un
pianificatore di profili d'attacco (quota e velocità di sgancio vincolate dalla finestra di rilascio
dell'arma e dalle minacce), per le missioni DCS e il suo legame con la portata mancante delle bombe
nel motore DES.
**Base**: `Analisi_Modello_Missione_Sessione.md` (stessa sessione), in particolare P1 (la Missione
non esiste come entità) e §2.4 (nessun bersaglio assegnato).
**Convenzione**: **[V]** = VERIFICATO leggendo il codice (con `file:riga`) o eseguendolo;
**[I]** = IPOTESI o conoscenza generale non verificata nel repository.
Percorsi di codice relativi a `Code/Dynamic_War_Manager/Source/`.

---

## 0. Sintesi e raccomandazioni

| Proposta | Verdetto | In una riga |
|---|---|---|
| **A** scorta compatibile | **Fattibile, da correggere nella forma** | Il problema è più grave di quanto ipotizzato. Il rimedio giusto non è "filtrare lo scalare al volo" ma sostituirlo con una **scorta per modello d'arma** (`{arma: quantità}`), consumata per arma. La scorta "compatibile" con bersaglio e missione diventa una vista derivata di quella. |
| **B** rotte d'attacco | **Fattibile, da approfondire nei dati** | Manca tutto il dato di rilascio delle bombe e manca il concetto stesso di profilo d'attacco. I mattoni geometrici però esistono già: minacce `ThreatAA`, esposizione temporale `threat_windows`, rotte canoniche, parametri `altitude`/`direction` del task DCS. Serve un **modulo di pianificazione nuovo, agnostico dal simulatore**, e una **funzione balistica unica** condivisa con il motore DES. |

### A: cosa succede oggi [V]

L'ipotesi dell'utente è **confermata e va oltre**. L'arma scelta non consuma mai la propria scorta:
`Fire_Control` è pura e memoizzata, quindi restituisce **sempre la stessa arma** per la stessa coppia
tiratore/bersaglio, e il risolutore scala sempre il contatore aggregato. L'aereo non passa a un'altra
arma dopo aver finito i Maverick. Continua a lanciare **Maverick fantasma** pagandoli con i colpi del
cannone, che la fire control non può nemmeno sparare (il cannone di bordo non è un'arma candidata).

Numeri misurati (§3, E-A1/E-A2):
- un A-10C `Maverick/Gun CAS` (4 AGM-65D a bordo) lancia **642 AGM-65D** in 321 salve;
- un F-16C `Strike` (4 Mk-83 a bordo) sgancia **523 Mk-83**, fino ad azzerare lo scalare.

Il difetto è **identico per `Vehicle` e `Ship`** (E-A3):
- un BMP-2 (500 colpi 2A42 + 4 Konkurs, scalare 504) sceglie sempre il 9M113 Konkurs contro i
  corazzati, quindi fino a 252 salve di ATGM;
- un T-72B (38 colpi 2A46M + 4 missili 99K120, scalare 42) spara 21 salve di ATGM invece di 2.

Il disegno proposto (§1.5) ha cinque punti:
1. scorta per arma su `Mobile`, con `ammunition` che resta come **somma derivata** per non rompere i
   lettori;
2. la fire control restituisce le armi adatte **in ordine di preferenza**, e il risolutore sceglie
   la prima con scorta;
3. `AmmunitionEvent` e `InterceptionEvent` acquistano un campo `weapon` opzionale;
4. la regola "SAM puro" (`Mobile.py:181-206`) diventa un caso particolare della condivisione per
   arma, quindi va eliminata e non estesa;
5. il filtro per **tipo di missione** è uno strato ROE separato, rimandato all'entità `Mission`
   (P1), perché oggi sull'asset non c'è né la missione né il bersaglio assegnato.

**Rapporto con la proposta SAM (D+B+F).** La scorta per arma è il **prerequisito** già dichiarato
da quel documento (§5.1, §6 "Prerequisito"). Non la sostituisce, la **completa** e ne rende precise
le regole: D (quale arma intercetta), B (riserva sul singolo tipo di missile), F (ordine di
consumo). Dettaglio in §1.4.

### B: cosa c'è e cosa manca [V]

- Le 32 bombe del registro **non hanno alcun campo** di portata, velocità, quota o finestra di
  rilascio.
- Il pianificatore `Air_Route_Manager.RoutePlanner` ha tre limiti per questo scopo:
  - fa solo **transito punto-punto**, a quota costante, aggirando o scavalcando i cilindri
    `ThreatAA`;
  - **esclude dal calcolo le minacce che contengono l'arrivo** (`Logic/Air_Route_Manager.py:780-781`),
    cioè proprio la difesa del bersaglio, che è la minaccia che decide la quota di sgancio;
  - non conosce arma, bersaglio, punto di sgancio né uscita.
- La metrica di esposizione temporale esiste già: `Contact_Scheduler.threat_windows`. Oggi però
  **nessun codice di produzione la usa**, solo i test.

**Raccomandazione netta sul legame con il DES (B.5)**:
- **una sola funzione balistica** (portata e tempo di caduta in funzione di quota, velocità e
  arma) e **un solo pianificatore di profilo d'attacco**, usati dagli esecutori DCS **e**
  virtuale;
- il DES ricava `max_range` e `time_of_flight` delle bombe dalla quota della missione, oggi da
  `position.z` dell'aereo;
- **non** due sottosistemi con logiche proprie: violerebbe il vincolo simulator-agnostic, perché
  la stessa missione avrebbe esiti "fisici" diversi a seconda dell'esecutore.

---

## 1. Proposta A: verifica del meccanismo di consumo

### 1.1 Da dove nasce lo scalare [V]

- **Decisione di progetto esplicita**: *"UN contatore AGGREGATO PER ASSET (non per arma installata,
  non per tipo di munizione)"* (`Asset/Mobile.py:88-122`, decisione R3 del 2026-09-23).
- **Veicoli e navi**: `Mobile.ammunition_from_registry` somma le quantità di `record.weapons` per
  tutti i tipi tranne quelli contati a unità (`MACHINE_GUNS`, `CIWS`) (`Asset/Mobile.py:749-810`,
  somma a `:786-803`).
- **Aerei**: `Aircraft.ammunition_from_registry` somma le quantità dei piloni che sono armi di
  `AIR_WEAPONS` **più `gun_rounds`** (`Asset/Aircraft.py:213-267`; cannone a `:262-265`). Il docstring
  lo dichiara: *"missili e colpi del cannone si sommano in un solo numero"* (`:225-227`). Assegnare
  il loadout ricalcola lo scalare (`:203-206`).
- **Consumo**: `Mobile.consume_ammunition(rounds)` decrementa lo scalare, senza alcun argomento
  d'arma (`Asset/Mobile.py:717-747`).
- **Verifica sui registri** (`Asset/Aircraft_Loadouts.py:1425` e `:1674`, eseguito):
  - F-16C Block 52d `Strike` = 2+2 Mk-83, 3+3 Mk-82, 1+1 AIM-9M, 511 colpi → **523**;
  - A-10C `Maverick/Gun CAS` = 4 AGM-65D, 2+2 Mk-82AIR, 1 AIM-9M, 1174 colpi → **1183**.

### 1.2 Quale arma, quale contatore [V]

1. **La fire control sceglie un'arma per nome** e la mette in `ShotSpec.weapon`:
   - candidate: `_candidate_weapons` (`Logic/Fire_Control.py:296-347`);
   - scelta per massima Pk: `select_weapon` (`:473-506`);
   - `ShotSpec(weapon=weapon.model, rounds=SALVO_ROUNDS[kind])` (`:537-541`).
2. **La scelta non dipende da alcuno stato di scorta.** È memoizzata per
   `(tiratore, chiavi bersaglio, dimensione, quote)` (`:592-603`), e il docstring la dichiara
   *"funzione PURA"* (`:101-107`). Stessa coppia significa stessa arma per tutta la sessione.
3. **Il risolutore legge solo lo scalare.** Lo stato ombra copia `asset.ammunition` in un intero
   (`Logic/Engagement_Resolver.py:1127-1142`; `_Shadow.ammunition`, `:899-907`). Tre punti lo usano:
   - condizione di stop: `shooter.ammunition <= 0` (`:1375`);
   - colpi della salva: `min(spec.rounds, shooter.ammunition)` (`:1450`);
   - decremento al lancio: `shooter.ammunition -= rounds` (`:1532-1533`).
4. **L'evento non porta l'arma.** `AmmunitionEvent(time, asset_id, rounds)` (`:387-400`), prodotto a
   `:1535`, applicato con `consume(event.rounds)` (`:1879-1882`). L'arma resta solo in `Salvo.spec` e
   nei `DamageEvent`.
5. **Il cannone di bordo non è sparabile**: *"Il cannone di bordo (`stores['gun_rounds']`) non ha un
   modello d'arma e non e' candidato"* (`Logic/Fire_Control.py:22-24`). `Aircraft_Data` non dichiara
   il modello del cannone (ricerca di `GAU-8`/`M61A1` in `Aircraft_Data.py`/`Aircraft_Loadouts.py`:
   nessun risultato), anche se `AIR_WEAPONS['CANNONS']` contiene `GAU-8/A` e `M61A1`. I 1174 colpi
   dell'A-10 sono quindi scorta **che nessuna arma può spendere, ma che paga i Maverick**.
6. Il modulo lo dichiara come limite: *"Non conta le munizioni per arma: la scorta e' il contatore
   aggregato di `Mobile`, e per le armi a raffica il risolutore consuma 1 unita' per raffica
   (sottostima dichiarata)"* (`Logic/Fire_Control.py:112-113`).

**Risposta alla domanda A.2.** La lettura dell'utente è corretta, con una correzione. Dopo 4
Maverick lo scalare passa da 1183 a 1179 e l'asset "ha ancora scorta", ma l'effetto è peggiore:
- l'A-10 **non smette di lanciare Maverick**, e non passa nemmeno a un'altra arma;
- ogni salva successiva è di nuovo `AGM-65D` × 2, pagata dallo scalare;
- si ferma solo quando lo scalare si azzera, oppure quando si chiude la finestra di contatto o
  finiscono i bersagli.

Nella prova E-A1 la finestra e i bersagli finiscono prima: 642 Maverick e scalare residuo 541.
Nella prova E-A2 l'F-16 azzera lo scalare con 523 Mk-83.

### 1.3 Vale anche per Vehicle e Ship? **Sì, identico** [V]

Registri reali (E-A3, letti da `Vehicle_Data`/`Ship_Data`):

| Modello | `record.weapons` | Scalare | Arma scelta contro corazzato | Salve possibili (reali) |
|---|---|---|---|---|
| BMP-2 | 2A42-30mm ×500, 9M113-Konkurs ×4, PKT ×1 (a unità) | 504 | 9M113-Konkurs (Pk 0,85×0,85) | 252 (2) |
| T-72B | 2A46M ×38, 99K120 ×4, PKT/NSVT (a unità) | 42 | 99K120 (Pk 0,95×0,9) | 21 (2) |
| M6-Linebacker | M242-25mm ×900, FIM-92 Stinger ×4 | 904 | n.d. | n.d. |
| 2K22-Tunguska | 2A38M ×1904, 9M311 ×8 | 1912 | n.d. | n.d. |
| USS Arleigh Burke IIa | SM-2ER ×74, ESSM ×16, Harpoon ×8, Tomahawk ×12, Mk-46 ×6, Mk-45 ×600, Phalanx ×1 (a unità) | 716 | n.d. | n.d. |

Per i veicoli il difetto è **mascherato**: la Pk dei missili anticarro è la più alta e le salve
restano poche rispetto alla durata di un ingaggio. Quando la sessione dura abbastanza, il carro
continua a lanciare 99K120 per altre 19 salve, invece di tornare al cannone come farebbe un carro
reale.

Esiste già un segnale del problema nel codice:
- la regola "SAM puro" (`Asset/Mobile.py:190-205`) nasce proprio dall'impossibilità di condividere
  il pool per arma: *"una scorta condivisa PER ARMA e' fuori dal modello aggregato attuale"*
  (`:202-203`). M6-Linebacker e Arleigh Burke restano a contatori indipendenti per questo;
- `Military.weapons_availability`, la scorta di **deposito** del blocco, è già
  `{tipo: {modello: quantità}}`, cioè per modello d'arma (`Block/Military.py:104, 119-129`). Il
  deposito è per arma, l'asset no: incoerenza di granularità.

### 1.4 Rapporto con la proposta SAM D+B+F (`Proposta_Regole_Allocazione_SAM.md`) [V + I]

- **Prerequisito dichiarato**: quel documento chiede di *"decidere prima le munizioni aggregate
  degli aerei"* (§5.1, §6) e ha dovuto **forzare a mano** la scorta degli A-10 a 4 per ottenere
  numeri sensati (§1.1). La scorta per arma chiude quel prerequisito. [V]
- **Ortogonale nella logica, complementare nei dati**:
  - D, B e F sono regole di **allocazione** (chi intercetta, quanto trattenere, in che ordine);
  - la scorta per arma è la **contabilità** su cui quelle regole operano. Nessuna delle due
    sostituisce l'altra. [V, lettura dei due disegni]
- Con la scorta per arma le tre regole diventano **più precise e più semplici** [I, da verificare
  in implementazione]:
  - **D (capacità dichiarata per arma)**: oggi l'idoneità a intercettare è dell'asset, a canali
    uguali per tutti. Per arma, un Tunguska intercetterebbe con il 9M311 e con i colpi 2A38M,
    ciascuno dalla propria scorta. Oggi le due componenti sono sommate in un solo contatore
    (8 + 1904//100 = 27, `Asset/Mobile.py:150-154`), che non sa quale si esaurisce per prima.
  - **Pool condiviso**: sparisce la regola a tre condizioni del "SAM puro"
    (`Asset/Mobile.py:190-205`). Ogni missile AD è **per costruzione** lo stesso oggetto per salva
    offensiva e intercettazione (stessa voce del dizionario); ogni cannone AD intercetta scalando
    `ROUNDS_PER_GUN_INTERCEPT` colpi dalla propria voce. M6-Linebacker (Stinger condivisi, M242
    separato) e Arleigh Burke (SM-2/ESSM condivisi, Harpoon/Mk-45 separati) diventano corretti.
    `interceptor_stock` diventa una somma derivata, non uno stato.
  - **B (riserva 50 %)** si applica al singolo missile AD, non a un totale che mescola colpi e
    missili.
  - **F (scorte dedicate prima dei pool condivisi)** diventa un ordine **dentro** l'asset (prima i
    cannoni AD, poi i missili) oltre che fra asset.

### 1.5 Disegno minimo proposto (NON implementato)

**Principio**: la scorta per arma è lo **stato primario**. "Scorta compatibile" (con bersaglio, con
missione) è una **vista** calcolata, non un secondo contatore da tenere allineato. Lo stesso principio
di `interceptor_stock` come vista di `ammunition` per i SAM puri (`Asset/Mobile.py:839-851`).

**Dati (`Asset/Mobile.py`)**
- `self._stores: Optional[Dict[str, int]]`, cioè `{modello_arma: quantità}`; None = non modellata
  (stessa semantica di oggi).
- `stores` (sola lettura, copia) e `stock_of(weapon) -> Optional[int]`.
- `ammunition` diventa una **vista**: `sum(stores.values())` se `_stores` non è None, altrimenti il
  vecchio `_ammunition` "anonimo".
  - Il setter `ammunition = n` resta per stub e test, e imposta un pool **anonimo** (`_stores =
    None`, `_ammunition = n`), usabile da qualunque arma: è il comportamento di oggi.
  - Così restano validi i test che forzano la scorta (`Test_Session_Scenarios_S10_S18.py:182-190`,
    `Test_Engagement_Resolver.py:612, 1689`) e quelli che leggono lo scalare
    (`Test_Aircraft.py:196-241`: 8 + 675 resta la somma).
- `consume_ammunition(rounds, weapon=None)`: con `weapon` presente in `_stores` scala quella voce;
  senza, scala il pool anonimo (oggi l'unico).
- `stores_from_registry()` / `load_stores_from_registry()` per Vehicle/Ship, con la stessa selezione
  di oggi (`Asset/Mobile.py:789-803`): esclusi i tipi contati a unità, voci sommate per modello.
- Scorta di intercettori come vista: Σ sulle armi AD (selezione di `_interceptor_registry_breakdown`,
  `:918-1000`) di `stock(missile)` e `stock(cannone) // ROUNDS_PER_GUN_INTERCEPT`.
  `consume_interceptor_stock` sceglie l'arma (ordine F: cannoni, poi missili). La regola "SAM puro"
  e `interceptor_shares_ammunition` (`:181-206`, `:829-837`, `:1023-1041`) si eliminano.

**Dati (`Asset/Aircraft.py`)**
- `stores_from_registry()` dal loadout assegnato, riusando `_pylons_to_weapons_dict`
  (`Logic/Air_Resources_Assigner.py:265-297`) con il filtro `get_weapon` già usato a
  `Asset/Aircraft.py:254-255` per scartare serbatoi e pod.
- Il cannone: **decisione utente** (§5, A2). Oggi `gun_rounds` non ha un modello. Due scelte:
  - aggiungere a `Aircraft_Data` il campo `gun` (es. A-10C → `GAU-8/A`, F-16C → `M61A1`, entrambi
    già in `AIR_WEAPONS['CANNONS']`), così il cannone diventa un'arma candidata con la propria voce;
  - oppure tenerlo fuori dalla scorta finché non lo si modella.
  In nessun caso deve pagare i missili.

**Fire control (`Logic/Fire_Control.py`)**
- `select_weapon` → `rank_weapons`: **tutte** le armi adatte, ordinate per `(-Pk, modello, tipo)`,
  cioè lo stesso ordine di oggi (`:501-504`), non solo la prima. Resta pura e memoizzabile.
- La callable restituisce `ShotSpec | Sequence[ShotSpec] | None`: una sequenza è l'ordine di
  preferenza. Estensione **retrocompatibile** del contratto (`Engagement_Resolver.py:24-26, 1431-1432`):
  una `ShotSpec` singola è una sequenza di un elemento, e le tabelle di test
  (`Scenario_Fixtures.make_fire_control`) non cambiano.
- Nuovo campo opzionale `ShotSpec.stock_per_round: int = 1`: le unità di scorta consumate da un
  colpo della salva. Per le armi a raffica vale `GUN_BURST_ROUNDS` (`:167-170`) e chiude la
  sottostima dichiarata a `:112-113`: oggi uno Shilka ha 2000 **raffiche**, non 2000 colpi.

**Risolutore (`Logic/Engagement_Resolver.py`)**
- `_Shadow` porta `stores` (copia) oltre al pool anonimo, e `ammunition` diventa la stessa vista
  (`:887-928`).
- `_schedule_next`:
  - lo stop di `:1375` diventa "nessuna scorta in nessuna arma";
  - dopo `self.fire_control(...)` (`:1424`) si prende la **prima opzione** la cui arma ha scorta
    nell'ombra (o il pool anonimo, se l'arma non ha voce);
  - `rounds = min(spec.rounds, stock // stock_per_round)` (`:1450`);
  - se nessuna opzione ha scorta, il candidato è esaurito, come per un `None`.
  La scelta resta deterministica: dipende dallo stato della coda, come la ripartizione del fuoco.
- `_on_launch` (`:1523-1535`): controllo e decremento **per arma**;
  `AmmunitionEvent(..., weapon=spec.weapon)`.
- `_on_resolve` (`:1598-1618`): l'intercettazione scala l'arma scelta e `InterceptionEvent`
  acquista `weapon`.
- `apply_engagement_result` (`:1879-1882`): `consume(event.rounds, weapon=event.weapon)`.
- `Command/Session_Types.py:196, 213-224`: `ammunition_consumed()` resta per asset, più
  `ammunition_consumed_by_weapon()`.

**Filtri di compatibilità (le due richieste dell'utente)**
- **(b) bersaglio**: è **già** fatto dalla fire control, per ogni coppia: dominio aria/superficie
  (`:36-46`), Pk > 0 (`:495-496`), inviluppo di quota (`:498-499`). Con la scorta per arma "le salve
  disponibili contro quel bersaglio" diventano una funzione di interrogazione esatta:
  `Σ_{armi adatte} stock // SALVO_ROUNDS`. Serve alla **pianificazione** (C2, `Air_Resources_Assigner`:
  "quante salve anticarro ha la formazione?"), non al risolutore, che consuma già l'arma giusta. Un
  **bersaglio assegnato** in senso stretto non esiste nel motore (`Analisi_Modello_Missione_Sessione.md`
  §2.4): arriverà con `Mission` (P1).
- **(a) tipo di missione**: è uno strato **ROE**, che restringe le armi candidate prima della scelta.
  Oggi non ha dove leggere la missione: sull'`Aircraft` c'è solo `assigned_loadout` (`Asset/Aircraft.py:168-171`).
  Serve anche una **tabella di corrispondenza**, perché il vocabolario dei task d'arma non coincide
  con quello dei task di missione (verificato su `AIR_WEAPONS`):
  - task d'arma: `A2A` (38 AAM), `Strike`, `SEAD`, `Anti_Ship`, `CAS` (solo 3 cannoni),
    `Pinpoint_Strike` (1 ASM);
  - task di missione (`AIR_TASK`, `Context/Context.py:413`): `CAP`/`Fighter_Sweep`/`Intercept`/
    `Escort`/`Recon`, `CAS`/`Strike`/`Pinpoint_Strike`/`SEAD`/`Anti_Ship`.

  Esempio: l'AGM-65D ha task `['Anti_Ship', 'Strike', 'SEAD']` e **non** `CAS`, eppure è l'arma della
  CAS dell'A-10. Proposta: `MISSION_WEAPON_TASKS` in `Context`, per esempio:
  - CAP/Sweep/Intercept/Escort → `{A2A}`;
  - CAS → `{Strike, CAS}`;
  - Pinpoint_Strike → `{Strike, Pinpoint_Strike}`;
  - SEAD → `{SEAD}`;
  - Anti_Ship → `{Anti_Ship}`;
  - più `{A2A}` in autodifesa quando il loadout ha `self_escort_capability` (campo già presente,
    `Asset/Aircraft_Loadouts.py:22`).

  Da introdurre **con** `Mission`, non prima. Per gli aerei, finché la missione non esiste, il loadout
  assegnato **è** già un filtro di missione: su 134 loadout, 97 mescolano tipi d'arma o armi e
  cannone, e sono il loro armamento dichiarato.

### 1.6 Rischi e impatti

- **Persistenza di campagna: nessuna migrazione, ma una lacuna** [V]. `Campaign_State._serialize_asset`
  (`Context/Campaign_State.py:453-489`) salva classe, modello, posizione, `state` (salute), payload e
  risorse: **né `ammunition`, né `interceptor_stock`, né carburante, né `assigned_loadout`** (nessuna
  occorrenza di `ammunition` nel file). Non ci sono snapshot da migrare. Quando la persistenza delle
  scorte verrà aggiunta, nel passaggio `mission_id` → `session_id` già deciso (wiki c2 `:46`), si
  salva direttamente il dizionario `stores`. Oggi una scorta consumata da un veicolo sopravvive fra
  sessioni solo nell'oggetto vivo, non nello snapshot.
- **Test da rivedere** [V, conteggio delle righe che citano `ammunition`]:

  | File | Righe | Cosa assume |
  |---|---|---|
  | `Test_Mobile.py` | 89 | pool condiviso del "SAM puro" (es. `:1599-1617`, Buk 1/1 → 0/0); da riscrivere per arma |
  | `Test_Engagement_Resolver.py` | 44 | stub con `ammunition` intero, restano validi col pool anonimo (`:51`); da rivedere `:1743-1757` (pool condiviso) |
  | `Test_Session_Scenarios_S10_S18.py` | 35 | esiti qualitativi dipendenti dal pool condiviso (S11) |
  | `Test_Aircraft.py` | 12 | somma 8 + 675: resta vera come vista |
  | `Test_Session_Simulator.py` | 11 | |
  | `Test_Session_Types.py` | 6 | |
  | `Test_Military.py` | 6 | |
  | `Test_Session_Scenarios.py` | 5 | |
  | `Test_Session_Validation.py` | 4 | |

  Gli **esiti** di S19 e della validazione cambieranno, perché gli aerei smettono di avere centinaia
  di Maverick. È il comportamento voluto, e va verificato solo qualitativamente.
- **Contratto della porta** [V + I]: l'estensione (`weapon` opzionale sugli eventi) va **verso** DCS,
  non contro:
  - il `world_state.payload` DCE è per pilone: `{gun, fuel, chaff, flare, ammo_type, pylons}`
    (`documentazione_dcs/ANALISI_DCE.md:372-376`) [V];
  - `Unit.getAmmo` restituisce la dotazione per arma (`documentazione_dcs/dcs_lua/Unit.md:329-333`
    [V]; il formato per arma è [I]).

  Con uno scalare l'adapter DCS dovrebbe **buttare via** quell'informazione.
  `ARCHITETTURA_CORE_AGNOSTICO.md:117-121` chiede un contratto sull'unione delle due sorgenti.
- **Rischio residuo non risolto dalla proposta** [V]: il **sovraffollamento sullo stesso bersaglio**
  (`Proposta_Regole_Allocazione_SAM.md` §5.2). L'A-10 lancia una salva ogni 1,5 s con 23 s di volo
  (E-A1: primo lancio a 1,5 s, ultimo a 510 s). Con 4 Maverick finirebbe tutta la scorta **sullo
  stesso carro** prima del primo impatto. Con la scorta per arma il difetto diventa più visibile,
  non più grave, e va chiuso a parte (le proprie salve in volo contano come copertura).
- **Criterio di scelta dell'arma** [V + I]: la massima Pk (`Logic/Fire_Control.py:473-506`) spende
  i missili migliori su bersagli leggeri: il Konkurs del BMP-2 è scelto anche contro un BTR-80.
  Con scorte per arma finite l'ordine di preferenza conta davvero. Un criterio di economia (Pk per
  costo: `cost` esiste nei registri) è una decisione utente (§5, A5).

---

## 2. Proposta B: rotte d'attacco e quota di sgancio

### 2.1 Cosa esiste oggi, con precisione [V]

**`ThreatAA` e la sua fabbrica** (`Logic/Air_Route_Manager.py`):
- **Geometria**: un **cilindro verticale per asset AD**, `Mobile.air_defense_volume()`
  (`Asset/Mobile.py:1276-1346`):
  - raggio = massima portata diretta fra le armi AD;
  - base = z dell'asset + minima `min_altitude`;
  - altezza = massima `max_altitude` meno minima `min_altitude`.
  È l'**unione** degli inviluppi delle armi AD dell'asset. La **quota è inclusa** come fascia
  verticale assoluta (`ThreatAA.min_altitude/max_altitude`, `:43-44`).
- **Non geometria**: `interception_speed` (velocità dell'arma), `min_detection_time` (tabella SAM
  ricercata), `min_fire_time` (placeholder dichiarato), e `danger_level` in [0, 1] da portata,
  tetto e reattività (`:122-251`, fabbrica `build_threat_aa` `:360-408`).
- **Chi costruisce le minacce**: solo Vehicle/Ship operativi di un blocco
  (`Military.air_defense_threats`, `Block/Military.py:551-577`). **I caccia nemici non sono
  minacce** per questo modello.

**`RoutePlanner.calcRoute`** (`:739-850`) è un pianificatore di **transito** da `start` a `end`:
- **esclude** le minacce che contengono `start` o `end` (`:780-781`, `excludeThreat` `:887-927`), e
  con `consider_aircraft_altitude_route` anche quelle la cui fascia non contiene la quota di rotta
  (`:783-787`, `:920`);
- **aggira** lateralmente con i punti tangenti di un cilindro allargato del 3 %
  (`_handle_threat_avoidance`, `:1631-1788`), oppure **cambia quota** sopra o sotto la fascia
  (`change_up`/`change_down`, `:1495-1629`; nuova quota `:1567`, `:1575`);
- in modalità `intersecate_threat` **attraversa** la minaccia su una corda di lunghezza massima
  `calcMaxLenghtCrossSegment` (`:70-98`, `:1204-1445`). Il pericolo del percorso è la somma dei
  `danger_level` degli archi di attraversamento (`:1415`), **non pesata sul tempo**;
- uscita canonica: `calcCanonicalRoute` → `DataType.Route` (`:854-885`), cioè la rotta che il
  motore DES consuma.

Cosa **non** fa: nessun concetto di arma, bersaglio, punto iniziale d'attacco (IP), punto di sgancio,
direzione d'attacco o uscita. Nessuna metrica di esposizione nel tempo. Stampa su stdout (`DEBUG =
True`, `:770`, `:836-846`).

**`Contact_Scheduler.threat_windows` / `route_threat_windows`** (`Logic/Contact_Scheduler.py:433-612`):
per una `DataType.Route` e un cilindro (o `ThreatAA`) restituisce le finestre `ThreatWindow`:
- `t_entry`/`t_exit`, `duration` = tempo di esposizione, punti d'ingresso e uscita,
  `danger_level` (`:140-169`);
- il docstring prevede il confronto di `duration` con `min_detection_time + min_fire_time`
  (`:143-146`).

**Nessun codice di produzione la chiama**: la ricerca di `threat_window` fuori da `Test/` trova solo
le definizioni. Né `Session_Simulator` né `Air_Route_Manager` la usano, e `Air_Route_Manager` usa la
propria `ThreatAA.edgeIntersect` (`:47-62`). La memoria di progetto va corretta su questo punto: il
cilindro `ThreatAA` è usato da `Air_Route_Manager`, `Military` e `Reaction_Profile`; `threat_windows`
da nessuno.

**Difetti incontrati durante la lettura** (fuori scope, da segnalare):
- `calcMaxLenghtCrossSegment` somma un raggio e una quota al quadrato:
  `c = -(self.cylinder.radius + aircraft_altitude * aircraft_altitude) / aircraft_speed` (`:74`), cioè
  metri più metri². Probabilmente l'intento era `sqrt(r² + h²)` o `r² + h²`. [V che la formula è
  dimensionalmente incoerente; I l'intento]
- L'esclusione delle minacce che contengono l'arrivo (`:781`) ha senso per un transito verso una
  base amica, ma è **sbagliata** per un bersaglio difeso: il SAM a 1 km dal bersaglio viene rimosso
  dal calcolo.

### 2.2 Dati di rilascio nel registro: **assenti** [V]

`AIR_WEAPONS['BOMBS']` contiene **32 voci** (13 `Bombs`, 12 `Cluster bombs`, 7 `Guided bombs`).
Chiavi presenti in tutte: `type, model, users, task, start_service, end_service, cost,
perc_efficiency_variability, efficiency, weapon_param_type`; `warhead` in 20, `weight` in 12.
**Nessuna** tra `range`, `speed`, `max_height`, quota/velocità minima o massima di rilascio, angolo
di picchiata, classe di resistenza (bassa/alta, frenata) o planata. Esempi:
- Mk-83 (`Asset/Aircraft_Weapon_Data.py:3696`), Mk-82 (`:3769`), GBU-12 (`:4059`);
- `WEAPON_PARAM['BOMBS']` pesa solo `warhead`/`weight` (`:62-63`).

Per confronto, gli ASM hanno `range` in tutte e 32 le voci, `max_speed` in tutte, `max_height` in 1
sola. L'unico dato di quota e velocità "d'impiego" è **del loadout, non dell'arma**: il blocco
`attack` (*"max-performance envelope during weapon employment"*, `Asset/Aircraft_Loadouts.py:23-24`),
per esempio A-10C CAS `speed 580` km/h, `reference_altitude 1000`, `altitude_min 30`,
`altitude_max 4000` m (`:1674` e seguenti). `Air_Resources_Assigner._check_mission_requirements` lo
confronta già con i requisiti `attack` di missione (`Logic/Air_Resources_Assigner.py:131-154`,
esempio `:811-815`). È il **punto di aggancio** per l'inviluppo dell'aereo. Manca quello dell'arma.

**Campi proposti** (per ogni voce di `BOMBS`, opzionali, unità coerenti con i loadout):
```python
'release': {
    'modes':        ['level', 'dive'],     # + 'loft' per il lancio in cabrata
    'min_altitude': 150,                   # m AGL: minimo di sicurezza (schegge, armamento spoletta)
    'max_altitude': 12000,                 # m
    'min_speed':    450, 'max_speed': 1100, # km/h
    'dive_angle':   (0, 45),               # gradi, per 'dive'
    'drag':         'low',                 # 'low' | 'high' (frenata: Mk-82AIR, Snakeye)
    'glide_ratio':  None,                  # solo bombe plananti/guidate
}
```
I valori sopra sono **segnaposto illustrativi** [I]. Vanno ricercati arma per arma con un prompt di
ricerca dati, come per B1 (`Proposta_Efficacia_Antiaerea.md`), e approvati.

### 2.3 Dove deve vivere la logica [V + I]

- **Non** in `Logic/Fire_Control.py`: è una fire control del risolutore, per coppia tiratore/bersaglio,
  pura, senza rotta. [V, docstring `:1-15`]
- **Non** dentro `RoutePlanner`, che è un pianificatore di transito con uno stato di lavoro privato
  (decisione Q1, `Logic/Route_Adapter.py`) e ha una semantica opposta sulle minacce all'arrivo (§2.1).
  Va **riusato** per l'ingresso e l'uscita, non esteso.
- **Nuovo modulo `Logic/Weapon_Delivery.py`**, stateless come il resto di `Logic/`, con due livelli:
  1. **fisica pura**: `release_envelope(weapon)`, `fall_time(h)`,
     `release_range(weapon, altitude, speed, mode)`. Nessuna dipendenza da rotte o minacce. È la
     parte condivisa con il DES (§2.5);
  2. **pianificazione**: `plan_attack_profile(aircraft_model, loadout, weapon, target_point, threats,
     constraints) -> AttackProfile`. Usa il livello 1, `ThreatAA` (via
     `Military.air_defense_threats` dei blocchi nemici vicini al bersaglio), `route_threat_windows`
     come metrica, e `RoutePlanner.calcCanonicalRoute` per i tratti base → IP e uscita → base.
- **Tipo di scambio `AttackProfile`** come **dato puro** in `Command/` (lo strato dei contratti,
  `Command/Command_Types.py:1-17`), accanto al futuro `Mission` (P1). Il profilo è un attributo della
  missione, non della rotta: `DataType.Waypoint` ha solo `point`, `name` e `obj_reference`
  (`DataType/Waypoint.py:12-18`), niente ruolo o azione.
- **Aggancio naturale** [V]: `Air_Resources_Assigner.get_aircraft_mission` sceglie già modello e
  loadout confrontando i requisiti `attack` (`Logic/Air_Resources_Assigner.py:757-817`), ma non
  produce una missione eseguibile. Il futuro `Session_Mission_Planner` (`Command/Command_Types.py:6`,
  non costruito) è il punto in cui modello e loadout scelti, bersaglio e minacce diventano
  `Mission(route, attack_profile)`.
- **Adapter DCS** [V, documentazione ingerita]: traduce `AttackProfile` nei parametri **già
  esistenti** dei task AI (`documentazione_dcs/dcs_lua/Controller.md:100-200`):
  - `AttackGroup`/`AttackUnit`/`Bombing` con `altitude` + `altitudeEnabled` (quota d'inizio attacco),
    `direction` + `directionEnabled` (azimut d'ingresso), `weaponType` (bitmask d'arma), `expend`,
    `attackQty`;
  - i waypoint vengono dalla rotta.

  La nota di `:157` è decisiva: *"If the altitude is too low or too high to use weapon aircraft/group
  will choose closest altitude"*. Se la quota pianificata è fuori dalla finestra dell'arma, **DCS la
  cambia in silenzio**, e l'analisi di esposizione del pianificatore non vale più. La validazione
  contro la finestra di rilascio va fatta **nel core**. In DCS il punto di sgancio lo calcola l'IA:
  il core deve fornire quota, direzione, arma e quantità, non un punto balistico esatto.

### 2.4 Modello minimo concreto (proposta)

```python
@dataclass(frozen=True)
class ThreatExposure:
    threat_id: str | None
    seconds: float             # durata della ThreatWindow
    effective_seconds: float   # max(0, seconds - (min_detection_time + min_fire_time))
    danger_level: float

@dataclass(frozen=True)
class AttackProfile:
    target_id: str | None; target_point: Point3D
    weapon: str; quantity: int; passes: int          # -> expend / attackQty DCS
    run_in_azimuth_deg: float                        # -> direction DCS (dal bersaglio verso l'attaccante)
    ip_point: Point3D; release_point: Point3D; egress_point: Point3D
    release_altitude_m: float; release_speed_kmh: float; release_mode: str
    release_slant_range_m: float; fall_time_s: float # -> DES (max_range / time_of_flight)
    exposure: tuple[ThreatExposure, ...]; feasible: bool; reason: str | None
```

Algoritmo (euristica deterministica, nessun RNG):
1. **Fascia ammessa** = inviluppo `attack` del loadout ∩ finestra `release` dell'arma, per quota e
   velocità. Vuota → `feasible=False` con il motivo. È il controllo che evita la correzione
   silenziosa di DCS.
2. **Quote candidate**: una griglia sulla fascia, più i **bordi delle fasce di minaccia** subito
   sopra il tetto e subito sotto la base di ogni `ThreatAA` che copre il bersaglio. Si riusano i
   margini 1,05/0,95 di `MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_*` (`Logic/Air_Route_Manager.py:28-29`).
3. **Direzioni candidate**: N azimut (es. 12), oppure una sola se il C2 la impone.
4. Per ogni coppia (quota, azimut):
   - distanza di sgancio `d = release_range(...)`;
   - tratto terminale IP → sgancio → uscita come `DataType.Route` (quota costante nel tratto, velocità
     sull'arco: `Edge.speed` esiste già);
   - esposizione con `route_threat_windows(route, threats)` su **tutte** le minacce, comprese quelle
     che contengono il bersaglio (correzione di §2.1).
5. **Scelta**:
   - la quota più bassa della fascia che resta **fuori da tutte** le fasce di minaccia sul tratto
     terminale (esposizione effettiva nulla);
   - se non esiste, la coppia che **minimizza Σ effective_seconds × danger_level**, cioè la regola
     dell'utente "minimizza il tempo di esposizione", pesata sul pericolo;
   - a parità, quota più bassa (precisione di sgancio, [I]), poi azimut minore (determinismo).
6. **Ingresso e uscita**: `RoutePlanner.calcCanonicalRoute(base → IP)` e `(uscita → base)` con le
   opzioni di cambio quota esistenti. La rotta completa è la concatenazione, e `AttackProfile` indica
   quale tratto è quello d'attacco.

**Balistica minima** del livello 1 [I, fisica elementare, da tarare]:
- rilascio livellato senza resistenza: `t = sqrt(2h/g)`, `R = v·t`;
- `drag` introduce un fattore < 1 sulla gittata (frenate molto minore), da registro;
- in picchiata la gittata si riduce con l'angolo;
- ordini di grandezza (vuoto): F-16 a 850 km/h da 3000 m → t ≈ 24,7 s, R ≈ 5,8 km; A-10 a 580 km/h
  da 1000 m → t ≈ 14,3 s, R ≈ 2,3 km.

Il `DEFAULT_TIME_OF_FLIGHT_S['bomb'] = 25` di `Logic/Fire_Control.py:154` è coerente solo con il
primo caso.

**Limiti dichiarati del modello** [V]:
- il cilindro è l'unione degli inviluppi dell'asset (`Asset/Mobile.py:1304-1335`): nessuna zona
  morta interna, nessun orizzonte radar né mascheramento del terreno. Il beneficio reale del volo
  basso contro i radar non è quindi rappresentato;
- la primitiva "orizzonte radar" è già prevista fra i futuri volumi d'ingaggio
  (`Logic/Engagement_Resolver.py:994-1001`), non ancora costruita.

### 2.5 Collegamento con la portata mancante del DES: **una fisica, un pianificatore, due esecutori**

**Raccomandazione netta: non due sottosistemi.** La funzione balistica del livello 1 è l'**unica**
fonte di gittata e tempo di caduta, per tre motivi:
- **Vincolo simulator-agnostic**: una stessa `Mission` deve poter essere eseguita da DCS o dal DES.
  Se il pianificatore sceglie 4000 m per stare sopra lo Shilka e il DES poi fa sganciare da
  qualunque distanza (oggi: `max_range=None`, verificato in E-A2), i due esecutori producono esiti
  fisicamente incoerenti per la stessa missione;
- il pianificatore d'attacco va quindi usato anche per le missioni virtuali: "per DCS" è solo
  l'adapter Lua;
- **Nel DES l'esposizione emerge da sola**: se la rotta virtuale segue il profilo pianificato, i SAM
  ingaggiano con le finestre di contatto alla quota scelta. La scelta di quota del pianificatore ha
  quindi effetto anche nella sessione virtuale, senza logica aggiuntiva.

Integrazione nel DES, in due passi:
1. **Subito, senza `Mission`**: per le bombe, `shot_spec_for` (`Logic/Fire_Control.py:509-541`)
   calcola:
   - `max_range = sqrt(R² + h²)`, cioè la distanza obliqua al rilascio, perché il controllo di
     portata del risolutore è una **sfera** 3D (`Logic/Engagement_Resolver.py:1006-1013`);
   - `time_of_flight = fall_time(h)`;

   con `h = shooter.position.z`, la quota che la fire control legge già (`:56-61`), e `v` =
   velocità `attack` del loadout. Resta pura e memoizzabile, perché `h` è già nella chiave di cache
   (`:592`). Con un rilascio livellato l'ingresso nella sfera coincide col punto di sgancio.
2. **Con `Mission`**: `h` e `v` dal `AttackProfile` della missione invece che da `position.z`.
   `position` non viene aggiornata durante la sessione (`:59-61`) e la quota della rotta può
   cambiare fra i waypoint.

Limite dichiarato: la sfera non ha una **distanza minima**. Un aereo rilevato tardi, già sopra il
bersaglio, sgancerebbe "a distanza zero". Accettabile come primo passo, correggibile con una fascia
(primitiva dei volumi già prevista).

---

## 3. Esperimenti di sola lettura

Script nella scratchpad di sessione (`expA.py`, `expV.py`, `bombs.py`, `tasks.py`), fuori dal
repository. Asset reali di `Test/Scenario_Fixtures`, `make_registry_fire_control()`, `run_session`
con dottrina ad oltranza (erosione e shock a 1,0), sessione di 3600 s. Nessun file del repository è
stato modificato.

| # | Configurazione | Risultato | Cosa dimostra |
|---|---|---|---|
| E-A1 | 1 A-10C `Maverick/Gun CAS` fermo a 1000 m, sensore 'ground' dichiarato 10 km, 3 km da 20 T-72B fermi | scalare iniziale **1183**; ShotSpec `AGM-65D`, `rounds=2`, `max_range=15000`; **321 salve, 642 colpi, tutti AGM-65D**; scalare finale 541; primo lancio 1,5 s, ultimo 510 s; 31 colpi a segno, 20 T-72 distrutti | Maverick fantasma pagati da cannone e AIM-9 (§1.2). Refire 1,5 s contro 23,4 s di volo: sovraffollamento sullo stesso bersaglio (§1.6) |
| E-A2 | Stesso schema, F-16C Block 52d `Strike` | scalare **523**; ShotSpec `Mk-83`, `max_range=None`, `time_of_flight=25`; **262 salve, 523 Mk-83**, scalare finale 0; 16 T-72 distrutti | Scorta azzerata con una sola arma di cui esistono 4 esemplari; nessun limite di portata sulle bombe (§2.5) |
| E-A3 | Registri e fire control per BMP-2 e T-72B contro M1A2 e BTR-80 | BMP-2 scalare 504, sceglie sempre 9M113-Konkurs; T-72B scalare 42, sceglie sempre 99K120; anche contro il BTR-80 | Stesso difetto su `Vehicle`; il criterio di massima Pk spende ATGM su bersagli leggeri (§1.3, §1.6) |
| E-B1 | Chiavi di `AIR_WEAPONS['BOMBS']`, vocabolario dei task d'arma e di missione | 32 bombe senza alcun campo di rilascio; task d'arma ≠ task di missione; 97 loadout su 134 misti | §2.2, §1.5 (a) |

---

## 4. Riepilogo delle correzioni alla memoria e ai documenti

- Memoria di progetto: `threat_windows` **non** è usato da `Air_Route_Manager`, che usa
  `ThreatAA.edgeIntersect`. Oggi non lo usa nessun codice di produzione (§2.1).
- `Fire_Control.py:112-113` e `10_Limiti_Estensioni_Divergenze.md:19-29` descrivono lo scalare come
  "sottostima". È anche una **sovrastima** di ordini di grandezza per le armi a scorta piccola
  (Maverick, ATGM), da riformulare quando si decide A.

---

## 5. Decisioni richieste all'utente

**Proposta A**, in ordine di blocco:
1. **A1**: adottare la scorta per modello d'arma come stato primario, con `ammunition` e
   `interceptor_stock` come viste derivate e la regola "SAM puro" rimossa? (Raccomandato.)
2. **A2**: il cannone di bordo degli aerei. Aggiungere il campo `gun` ad `Aircraft_Data` (ricerca
   dati per ~N modelli) perché sia un'arma candidata, oppure escluderlo dalla scorta per ora?
3. **A3**: `ShotSpec.stock_per_round` per le armi a raffica (consumo reale in colpi), accettando che
   cannoni AA e HMG si esauriscano ~50 volte prima di oggi?
4. **A4**: il filtro per tipo di missione (tabella `MISSION_WEAPON_TASKS` + autodifesa A2A con
   `self_escort_capability`) si fa **con** l'entità `Mission` (raccomandato) o prima, leggendo i
   `tasks` del loadout?
5. **A5**: il criterio di scelta dell'arma resta la massima Pk, o diventa un compromesso Pk/costo?
   Solo una decisione di principio: non blocca A1.
6. **A6**: la proposta SAM (D+B+F) va implementata **dopo** A1, riformulata per arma
   (raccomandato), o prima sullo scalare?

**Proposta B**:
1. **B1**: dati di rilascio per le 32 bombe (campi di §2.2): ricerca con prompt dedicato e
   approvazione, come per B1 antiaerea?
2. **B2**: il pianificatore d'attacco vale per **tutte** le missioni (DCS e virtuali, raccomandato)
   o solo per quelle DCS?
3. **B3**: metrica di esposizione: `Σ durata × danger_level` oppure con il tempo di reazione
   sottratto (`effective_seconds`, raccomandato, usa `min_detection_time`/`min_fire_time` già
   presenti)?
4. **B4**: profili ammessi: solo livellato, oppure anche picchiata e lancio in cabrata?
5. **B5**: direzione d'attacco libera (ottimizzata) o imposta dal C2 (es. dalla linea del fronte)?
6. **B6**: passo immediato sul DES: calcolare subito `max_range`/`time_of_flight` delle bombe da
   `position.z` e dalla velocità `attack` del loadout (§2.5 passo 1), prima di `Mission`?
7. **B7** (difetti fuori scope, §2.1): correggere `calcMaxLenghtCrossSegment` (formula
   dimensionalmente incoerente) e l'esclusione delle minacce all'arrivo per i tratti d'attacco?

---

## 6. Mappa d'impatto (proposta, non implementazione)

| Componente | Proposta A | Proposta B |
|---|---|---|
| `Asset/Mobile.py` | `_stores`, `stock_of`, `consume_ammunition(rounds, weapon)`, viste `ammunition`/`interceptor_stock`, rimozione "SAM puro" | nessuno |
| `Asset/Aircraft.py` | `stores_from_registry` dal loadout; cannone secondo A2 | nessuno |
| `Asset/Aircraft_Data.py` | campo `gun` (A2) | nessuno |
| `Asset/Aircraft_Weapon_Data.py` | nessuno | blocco `release` per le bombe (B1) |
| `Logic/Fire_Control.py` | `rank_weapons`, sequenza di ShotSpec, `stock_per_round` | bombe: `max_range`/`time_of_flight` da `Weapon_Delivery` (B6) |
| `Logic/Engagement_Resolver.py` | `_Shadow.stores`, scelta della prima opzione con scorta, consumo per arma, `weapon` sugli eventi | nessuno (la sfera di portata resta) |
| `Command/Session_Types.py` | `ammunition_consumed_by_weapon` | `Mission` + `AttackProfile` (con P1) |
| `Logic/Weapon_Delivery.py` (nuovo) | nessuno | balistica e `plan_attack_profile` |
| `Logic/Air_Route_Manager.py` | nessuno | riuso per ingresso e uscita; correzioni B7 |
| `Logic/Contact_Scheduler.py` | nessuno | `route_threat_windows` diventa il primo consumatore di produzione |
| `Context/Context.py` | `MISSION_WEAPON_TASKS` (A4) | nessuno |
| `Context/Campaign_State.py` | salvataggio di `stores` quando si aggiunge la persistenza delle scorte | salvataggio di `AttackProfile` con `Mission` |
| Adapter DCS (futuro) | `payload.pylons` / `getAmmo` → scorta per arma | `AttackProfile` → task `AttackGroup`/`Bombing` (`altitude`, `direction`, `weaponType`, `expend`, `attackQty`) |
