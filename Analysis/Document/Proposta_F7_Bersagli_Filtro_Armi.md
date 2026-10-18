# Proposta F7: bersagli espliciti della missione e filtro delle armi per missione

**Stato**: PROPOSTA (2026-10-18), da approvare. È la proposta di dettaglio prevista dalla domanda Q3 del
`Piano_Implementazione_Missione.md` (Fase 7, righe 190-205; riga F7-F9 della tabella §5).
**Base**: HEAD `a784a9e7`, suite 4385 OK, fotografia `Test/baseline/scenario_baseline.json` di 918 esecuzioni.
**Convenzioni**: [V] verificato sul codice; [S] misurato con una sonda di sola lettura (§1.5); [I] ipotesi;
**STIMA** = costante non tarata, da dichiarare come tale nel codice.
I percorsi sono relativi a `Code/Dynamic_War_Manager/Source/`.

---

## 0. Sintesi

- **Oggi la missione non decide né chi si ingaggia né con quale arma.** Il risolutore sceglie il bersaglio fra
  i nemici rilevati con il round-robin; la fire control sceglie l'arma per coppia (tiratore, bersaglio) dal
  loadout assegnato, senza conoscere la missione. Bersaglio, ROE, loadout di missione e `AttackProfile` sono
  validati ma non letti dal motore. Unica eccezione: il bersaglio ASSET/GROUP per il criterio
  `target_destroyed` della F6-B1.
- **Raccomandazione**: dividere la F7 in due passi.
  - **F7a: regole d'ingaggio di missione**, su due strati.
    - (W) Politica d'armi per tipo di missione: un involucro statico della fire control, che conosce i
      registri.
    - (T) Regole di bersaglio nel risolutore: bersaglio designato, ROE a 5/3 livelli già presenti nel dominio,
      armi designate e riservate. Sono una struttura per asset, come `ActivityCriteria`.
  - **F7b: fuoco su posizione** (la "salva su area" di Q3): un evento di sessione nuovo, separato dal
    risolutore.
- **Fotografia** (sonda [S], con le raccomandazioni): la F7a lascia identiche tutte le 918 esecuzioni.
  - Le 24 esecuzioni di S19AD restano identiche anche dopo la migrazione dei filtri di test (`ifv_only`,
    `maverick_only`) alle missioni.
  - Si aggiungono le esecuzioni nuove di S28.
  - Le alternative non raccomandate cambiano 28 esecuzioni (restrizione di classe anche per le armi di test)
    oppure fino a 50 (ROE di default restrittivo per l'attacco).
  - La F7b aggiunge solo esecuzioni nuove (S29).

---

## 1. Problema e comportamento attuale

### 1.1 Chi si ingaggia [V]

`Logic/Engagement_Resolver._EngagementRun._schedule_next` (`Logic/Engagement_Resolver.py:2012-2199`) procede
così:
- **candidati** = nemici rilevati, operativi e in finestra;
- **priorità L2** ai lanciatori aria-superficie contro la forza (`:2137-2144`);
- **dottrina di tiro** (saturazione e tetto di colpi);
- **round-robin**: primo istante utile, poi copertura, poi id.

La fire control che restituisce `None` vale "questo tiratore non ingaggia questo bersaglio" (`:2168-2174`,
commento "ROE o arma inadatta").

Nel motore **non esiste un bersaglio assegnato**: ogni nemico rilevato è un candidato con lo stesso peso.
L'unico punto d'ingresso della fire control nel risolutore è `_EngagementRun._fire_control(shooter, target, time)`
(`:2293-2319`). Lo usano anche il controllo di portata L2 `_in_range_at` (`:2325-2343`). Il metodo conosce
l'istante e quindi può conoscere la posizione del bersaglio (`_position_at`, `:2578`).

### 1.2 Con quale arma [V]

`Logic/Fire_Control.make_registry_fire_control` (`:740-810`):
- **armi candidate**: i piloni del loadout ASSEGNATO all'aereo (`Aircraft.assigned_loadout`,
  `Asset/Aircraft.py:171`) più il cannone di bordo; per veicoli e navi le armi del registro;
- **filtri**: dominio aria/superficie (`AIR_ONLY_TASKS`, `:189`), Pk > 0, quota;
- **ordine**: Pk/costo^0,5.

Il modulo lo dichiara: "nessun filtro per tipo di missione (A4)" (`:29`) e "filtro ROE per tipo di missione
rimandato all'entità `Mission`, decisione A4" (`:159-160`).

### 1.3 Cosa porta la missione e cosa ne legge il motore [V]

| Campo (`Command/Mission_Types.py`) | Letto da | Uso oggi |
|---|---|---|
| `Mission.mission_type` | `Mission_Adapter.final_posture` (`:1556`), `is_transfer_mission` (`:1222`) | postura finale aerea, albero di bingo G2 |
| `Mission.target` (`Target`, `:429-518`) | `Session_Simulator._mission_target_ids` (`:1599-1630`) | solo `target_destroyed` per ASSET/GROUP; POINT/AREA danno un warning "not representable before F7" (`:1610-1613`) |
| `Mission.rules.roe` (`AIR_ROE` 5 livelli, `SURFACE_ROE` 3, `:226-231`; default `weapon_free`, `:254-261`) | nessuno | — |
| `MissionAsset.loadout` (`:690-693`) | nessuno | il motore usa `Aircraft.assigned_loadout`; nessun controllo di coerenza (le fixture copiano l'uno nell'altro, `Test/Scenario_Fixtures.py:722-725`) |
| `MissionAsset.attack_profile` (`AttackProfile.weapon/target_id/quantity`, `Command/Attack_Types.py`) | nessuno in sessione | — |
| `EndCriteria.winchester` | F6-B1 | categorie di registro (`Fire_Control.weapon_category`) |

### 1.4 Sostituti nei test [V]

- **S19AD** (`Test/Test_Session_Scenarios_S19_Air_Defence.py`) ha due filtri di test.
  - `maverick_only` (`:62-74`) lascia all'A-10C le sole opzioni AGM-65D, perché con il criterio Pk/costo
    sceglierebbe la Mk-82AIR.
  - `ifv_only` (`:77-85`) fa attaccare agli aerei solo i BMP-2, non la difesa aerea.
  - Il docstring li dichiara "le veci del filtro per tipo di missione (A4)".
  - Le missioni dichiarano già `CAS` e `group_target('Red-Line')` (`:107`).
- **Scenari a tabella**: la fire control di test `Scenario_Fixtures.make_fire_control` (`:843-881`) usa
  ruoli imposti ('strike' = "solo aria-suolo non-AD", 'sead', 'fighter', `:768-790`) come sostituto del tipo
  di missione. Le armi sono `test:*`, che non esistono nei registri.
- Il docstring di `missions_for` dice che bersaglio e tipo sono "non ancora usato dal motore, F7"
  (`Test/Scenario_Fixtures.py:673-674`).

### 1.5 Misure (sonda [S])

La sonda è uno script fuori dal repository. Avvolge `run_session` e la fire control in memoria, esegue
`Scenario_Baseline.capture()` sulle 918 esecuzioni e confronta il risultato con la fotografia. Nessun file del
progetto è stato modificato.

**Censimento (fire control invariata)**: 918 identiche. Le chiamate alla fire control sono 37 412; quelle con
esito non nullo sono 33 373. Delle chiamate non nulle di un asset di missione con bersaglio ASSET/GROUP, 548 sono
dirette a nemici di superficie NON designati e 87 a nemici aerei non designati. Sono i "bersagli d'opportunità"
di oggi. Il conteggio comprende la scorta, il cui bersaglio è la missione protetta: per lei ogni nemico è fuori
dalla designazione.

| Variante ipotetica | Esecuzioni cambiate | Dove |
|---|---|---|
| (a) politica d'armi della §2.4, solo per armi dei registri | **0** | 40 chiamate filtrate in S19, tutte della scorta F-16C (cannone contro suolo, mai a portata da 3000 m) |
| (b) come (a), ma restrizione di CLASSE anche per le armi `test:*` | **28** | S16 x4 (missione `Anti_Ship` contro le strutture del porto); S25-WIN x24 (Strike rosso senza `self_escort` che oggi spara allo sweep) |
| (c) `only_designated` di default per le missioni ATTACK con bersaglio ASSET/GROUP | **50** | ORC-twofronts 9, S15 6, S18 6, S21R 6, S25-TGT 19, S6 4 |

### 1.6 Vocabolario d'arma nei registri [V]

| Registro | Categorie e task |
|---|---|
| Aria | MISSILES_AAM 42 (`A2A`); MISSILES_ASM 44 (`Strike`, `SEAD`, `Anti_Ship`, `Pinpoint_Strike` in combinazioni); BOMBS 54 (`Strike`, `Anti_Ship`); ROCKETS 12 (`Anti_Ship`+`Strike`); CANNONS 15 (`Strike`, 3 anche `CAS`); MACHINE_GUNS 2 (`Strike`) |
| Terra | `Anti_Tank`, `Infantry_Support`, `Artillery`, `Anti_Air`, `Anti_Missile` |
| Mare | `Anti_Air`, `Anti_Missile`, `Anti_Ballistic`, `Anti_Ship`, `Anti_Submarine`, `Land_Attack`, `Naval_Gunfire_Support` |

Il vocabolario dei task d'arma non coincide con quello dei tipi di missione:
- l'AGM-65D ha `Anti_Ship`, `SEAD` e `Strike`, ma non `CAS`;
- la Mk-82AIR ha `Strike`.

Quindi il filtro per tipo di missione non basta a far preferire il Maverick alla bomba in una CAS: serve
un'**arma designata** (§2.5).

Sui loadout aria-suolo con missili aria-aria [V]:
- 55 dichiarano `self_escort_capability` True;
- 5 lo dichiarano False pur avendo l'AIM-9M: sono tutti dell'A-10C, tra cui 'Maverick/Gun CAS' (anomalia di
  dato, decisione 8).

### 1.7 Cosa non si può esprimere oggi

1. Uno Strike attacca il primo nemico che rileva, non il suo bersaglio.
2. Una CAP può mitragliare a terra: è un effetto collaterale della decisione A2 (cannone candidato).
3. Una SEAD tira AGM-65 ai carri; una missione Anti_Ship attacca bersagli terrestri.
4. Un'arma non si può riservare al bersaglio, e manca la regola d'autodifesa aria-aria per i cacciabombardieri.
5. Le ROE dichiarate (`only_designated`, `return_fire`, `weapon_hold`) non hanno effetto.
6. Bersagli POINT/AREA/ZONE: nessun significato in ingaggio e `target_destroyed` non rappresentabile.
7. Manca il fuoco su coordinate stimate. L'artiglieria spara solo a ciò che ha rilevato, quindi "il punto dove
   i blu erano" (N3.e) non si rappresenta.

---

## 2. Definizioni proposte

### 2.1 Bersaglio designato

Per ogni asset di missione, l'insieme dei NEMICI (lato diverso da quello della missione) che corrispondono al
`Target` della sua missione:

| Forma | Designati |
|---|---|
| ASSET | l'asset `target_id`, se nemico |
| GROUP | se `target_id` è un blocco, i suoi asset; se è una missione, gli asset di quella missione; se è un asset, l'asset stesso. Con il nuovo campo facoltativo `asset_ids` (decisione 9) solo quel sottoinsieme. Sempre filtrati ai soli nemici |
| POINT/AREA/ZONE | **designazione geometrica**: nemico la cui posizione orizzontale, all'istante del tiro, è entro il raggio efficace dal centro. Raggio efficace = `radius_m` (POINT senza raggio: `TARGET_POINT_RADIUS_M`, STIMA, decisione 11) + `uncertainty_m` se la provenienza è ESTIMATED |
| NONE | nessuno |

Un GROUP amico non designa nessuno: è il caso della scorta (`Escort`, S18 e S19, bersaglio = la missione
protetta) e delle categorie TRANSPORT e POSITIONING. Un messaggio `info` lo registra (decisione 16).

**Nebbia di guerra**:
- la designazione per id NON dà il rilevamento, niente cueing (come nella deviazione 7 del Piano): si spara
  solo a un designato già rilevato dal tiratore;
- la designazione geometrica usa la posizione vera di un bersaglio GIÀ rilevato, quindi non aggiunge
  informazione;
- la posizione stimata della missione definisce solo l'area.

Il fuoco su posizioni non osservate è la F7b.

### 2.2 Opportunità e minacce

- **Bersaglio d'opportunità**: nemico rilevato e non designato.
- **Ostile** (per `return_fire`): un asset nemico che ha lanciato almeno una salva contro il dominio di
  coordinamento del tiratore. È la generalizzazione di `launchers_against` (`Engagement_Resolver.py:1484`),
  che oggi registra solo i lanci aria-superficie.

### 2.3 ROE (vocabolario già nel dominio, `Mission_Types.py:226-231`)

| ROE | Designati | Opportunità | Aerei nemici per missioni aria-suolo (autodifesa, §2.4) | Intercettazione delle salve |
|---|---|---|---|---|
| `weapon_free` (default) | sì | sì, **senza le armi riservate** (§2.5) | sì | sì |
| `priority_designated` (solo aria) | sì, **prima** degli altri | sì, senza le armi riservate | sì | sì |
| `only_designated` (solo aria) | sì | **no** | sì (esenzione d'autodifesa) | sì |
| `return_fire` | solo se ostili | solo se ostili | solo se ostili | sì |
| `weapon_hold` | no | no | no | **sì** (atto difensivo, decisione 3) |

Note:
- **Priorità**: è un livello nuovo nella scelta del bersaglio, DOPO la priorità L2 ai lanciatori (autodifesa
  delle forze di superficie) e PRIMA del round-robin. Fra i candidati utili, se ce n'è almeno uno designato,
  la scelta si fa solo fra i designati, con le stesse regole di prima. Un designato non ancora rilevato non
  blocca il tiro sulle opportunità.
- **Terra e mare**: hanno solo `weapon_free`, `return_fire` e `weapon_hold`.

### 2.4 Politica d'armi per tipo di missione (strato W; tabella `Context.MISSION_WEAPON_POLICY`)

**Classe del bersaglio** (`Fire_Control.target_class`):
- `air`: aereo in volo;
- `ship`: `Ship`;
- `air_defence`: `Vehicle` con `isSAM`, `isAAA` o `isEWR` (decisione 6);
- `surface`: ogni altro bersaglio di superficie, compresi gli aerei a terra della F4c.

**Regola per classe**:
- `ANY`: tutte le opzioni della fire control;
- `SELF_DEFENCE`: tutte le opzioni solo se il loadout ha `self_escort_capability`, altrimenti nessuna;
- un insieme di task: solo le armi con almeno un task dell'insieme;
- assente: classe non ingaggiabile.

| Tipo di missione aereo | air | air_defence | ship | surface |
|---|---|---|---|---|
| CAP, Fighter_Sweep, Intercept, Escort | ANY | — | — | — |
| CAS | SELF_DEFENCE | {CAS, Strike} | {CAS, Strike} | {CAS, Strike} |
| Strike | SELF_DEFENCE | {Strike} | {Strike} | {Strike} |
| Pinpoint_Strike | SELF_DEFENCE | {Pinpoint_Strike, Strike} | {Pinpoint_Strike, Strike} | {Pinpoint_Strike, Strike} |
| SEAD | SELF_DEFENCE | {SEAD} | — | — |
| Anti_Ship | SELF_DEFENCE | — | {Anti_Ship} | — |
| Recon, AWACS, Tanker, Transport | SELF_DEFENCE | — | — | — |

- **Terra e mare**: nella F7a nessuna restrizione d'arma, valgono solo le ROE. Le chiavi di dominio esistono
  con il valore `None`, che significa "nessun vincolo", pronte per una tabella futura (Fire_Support,
  Shore_Bombardment, decisione 5).
- **Armi assenti dai registri** (`test:*`, `weapon` None): nessun vincolo né di task né di classe. È la stessa
  politica "non modellato = nessun vincolo" di munizioni e carburante (decisione 7).

### 2.5 Armi designate e riservate (strato T)

Nuovo campo `MissionAsset.weapons: Tuple[str, ...]` (decisione 10): le armi da usare sul bersaglio designato.
Se c'è `attack_profile` e `weapons` è vuoto, vale `(attack_profile.weapon,)`.
- **Su un designato**: solo le opzioni con l'arma fra quelle designate, nessun ripiego. Con le armi designate
  esaurite il tiratore non ingaggia il designato, come in DCS con `weaponType`.
- **Su un non designato**: le armi designate sono **riservate**, cioè escluse, sotto ogni ROE.

### 2.6 Interazioni

- **F6-B1**:
  - `target_destroyed` resta per ASSET/GROUP e rispetta `asset_ids`; per POINT/AREA/ZONE resta non
    rappresentabile (decisione 12);
  - `winchester` invariato: una politica d'armi può rendere inutilizzabili armi del criterio, che non si
    esaurirebbero (limite, §7).
- **Bingo G1-G4**: dal bingo e dal disingaggio l'asset resta passivo (`ActivityCriteria.until`, invariato).
  Meno salve vuol dire meno partecipazioni, quindi meno consumi d'ingaggio G3 e meno ri-pianificazioni G4b.
  Sono effetti solo dove il filtro cambia una scelta.
- **Dominio di coordinamento** (F4b+): saturazione e ripartizione invariate; la priorità ai designati è per
  asset.
- **Simulator-agnostic**: tutti i valori sono di dominio (ROE, task dei registri, id). L'adapter DCS tradurrà:
  - ROE in opzione ROE;
  - armi designate in `weaponType`;
  - designati in AttackGroup/AttackUnit;
  - fuoco su posizione in FireAtPoint/Bombing.

  Nessun riferimento a DCS nel nucleo; cancellando l'adapter la F7 funziona uguale.

---

## 3. Alternative

### A. Dove applicare le regole

| | Pro | Contro |
|---|---|---|
| A1 Solo involucro della fire control (il Piano originale, stile `ifv_only`) | risolutore intatto | niente priorità (la fire control è per coppia, non sceglie fra bersagli); niente designazione geometrica (non conosce l'istante e `position` è statica, `Fire_Control.py:62-66`); niente `return_fire` |
| A2 Tutto nel risolutore, che legge la missione | un solo punto | rompe la regola "il risolutore non legge la missione" (`ActivityCriteria`, `:673-710`); il risolutore non conosce i registri |
| **A3 (R)** Due strati: W (statico, involucro in `Fire_Control`, conosce i registri) + T (dinamico, `TargetRules` per asset nel risolutore, costruite dalla sessione) | ogni strato dove ha i dati; T senza regole = codice di prima | due meccanismi da documentare |

### B. ROE di default

- **B1 (R)**: `weapon_free` invariato, confermato dall'utente il 2026-10-05. Le novità dello strato T si
  attivano dichiarando ROE o armi; fotografia identica per costruzione.
- **B2**: default per categoria, per esempio ATTACK con bersaglio a `priority_designated` (o
  `only_designated`). È più vicino a DCS (AttackGroup), ma cambia fino a 50 esecuzioni [S] e la conferma del
  2026-10-05.

### C. Filtro d'armi

- **C1 (R)**: tabella per tipo di missione (§2.4) più armi designate (§2.5).
- **C2**: i `tasks` del loadout come filtro (l'A4 "prima della Missione"). Scartata: il loadout è già il
  filtro di fatto, e non distingue il bersaglio né l'autodifesa.

### D. Fuoco su posizione (Q3)

- **D1 (R)**: nuovo evento di sessione analitico, modulo `Logic/Area_Fire.py` (§6).
- **D2**: pseudo-asset fermo nel punto stimato, dentro il risolutore. Riusa salve e intercettazione, ma
  richiede finestre di contatto e rilevamento fittizi e tocca il cuore del risolutore.
- **D3**: rimandare. La F7a copre solo la designazione geometrica di bersagli già rilevati, e il criterio del
  Piano ("artiglieria su posizione stimata superata colpisce solo chi c'è") resta aperto.

### E. Il sottoinsieme di S19AD (solo i BMP-2 del blocco)

- **E1 (R)**: `Target.asset_ids` per GROUP.
- **E2**: missione rossa fittizia con i soli BMP-2. Cambia le forze d'ingaggio rosse, gli `event_id` e quindi
  le estrazioni.
- **E3**: lasciare il filtro di test.

---

## 4. Decisioni aperte per l'utente

1. **Scomposizione**: F7a (regole d'ingaggio) e poi F7b (fuoco su posizione), ognuna con interruttore,
   confronto e approvazione separati. (R: sì.)
2. **Architettura a due strati** A3: politica d'armi come involucro della fire control più `TargetRules` nel
   risolutore. (R: sì.)
3. **Semantica delle ROE** della tabella §2.3, in particolare:
   - l'intercettazione resta anche con `weapon_hold`;
   - l'autodifesa aria-aria resta anche con `only_designated`.

   (R: sì a entrambe.)
4. **ROE di default**: (R) B1, `weapon_free` invariato; oppure B2.
5. **Tabella `MISSION_WEAPON_POLICY`** della §2.4. Va confermata riga per riga, in particolare:
   - CAS e Strike contro le navi;
   - Recon, AWACS, Tanker e Transport con sola autodifesa;
   - terra e mare senza restrizioni nella F7a.
6. **Classe `air_defence`**: (R) `Vehicle` con `isSAM`/`isAAA`/`isEWR`. Le navi con SAM restano `ship`.
7. **Armi assenti dai registri**: (R) nessun vincolo (0 esecuzioni cambiate). L'alternativa (restrizione di
   classe anche per le armi di test) cambia 28 esecuzioni (S16 x4, S25-WIN x24). In quel caso S16 dovrebbe
   passare a `Strike`, e la postura finale dei suoi aerei cambierebbe ('Anti_Ship' -> 'Strike').
8. **Autodifesa e dati**: fonte `self_escort_capability` del loadout (R). I 5 loadout dell'A-10C con AIM-9M e
   il flag False vanno corretti nel registro? Senza correzione l'A-10C non tira mai l'AIM-9 in una missione
   aria-suolo. (R: correzione dei dati a parte, dopo una verifica dell'utente; la F7a non tocca i registri.)
9. **`Target.asset_ids`** per GROUP (E1). (R: sì.)
10. **Armi designate**: nuovo `MissionAsset.weapons`, con `AttackProfile.weapon` come implicito. Sul
    designato nessun ripiego; sul non designato riservate sotto ogni ROE. (R: sì.)
11. **POINT senza raggio**: `TARGET_POINT_RADIUS_M` = 500 m (STIMA). Va confermato anche che l'incertezza
    ESTIMATED si somma al raggio. (R: sì.)
12. **`target_destroyed`** per POINT/AREA/ZONE: (R) resta non rappresentabile (warning invariato). Una
    definizione possibile, "tutti i nemici nell'area all'ETA del punto ATTACK distrutti", va decisa a parte.
13. **Coerenza di `MissionAsset.loadout`** con `Aircraft.assigned_loadout`: (R) `ValueError` in
    `_check_missions`, perché il motore usa il secondo e la politica d'armi deve leggere lo stesso loadout.
    Alternative: warning, oppure applicare il loadout di missione all'asset.
14. **Memoria di `return_fire`**: (R) per sessione. La sessione passa al risolutore gli ostili degli episodi
    già risolti.
15. **F7b** (§6), da confermare punto per punto:
    - (a) solo terra e mare (artiglieria, fuoco navale); l'aereo che bombarda un punto resta fuori;
    - (b) raggio letale STIMA dal calibro (0,25 m/mm, ripiego 25 m);
    - (c) dispersione minima 50 m (STIMA);
    - (d) niente fuoco amico (solo i nemici del tiratore);
    - (e) nessuna intercettazione (escluse le armi `missile`);
    - (f) un solo evento all'impatto;
    - (g) nessun effetto dottrinale (shock, disingaggio) sul lato colpito.
16. **Scorta**: (R) nella F7a il bersaglio amico non designa nessuno, e la scorta è `weapon_free` contro gli
    aerei. La "protezione del gruppo scortato" (ingaggiare chi minaccia il gruppo) resta una funzionalità
    futura.

---

## 5. Piano di intervento: F7a (regole d'ingaggio di missione)

### 5.1 Interruttori (`Logic/Session_Simulator.py`, accanto a `G4_OFF_SCENE_EXIT`, `:799`)

- `F7_WEAPON_POLICY = True`. Spento: nessun involucro, la fire control iniettata com'è.
- `F7_TARGET_RULES = True`. Spento: nessuna `TargetRules` passata al risolutore.
- Indipendenti fra loro. Spenti entrambi: comportamento esattamente precedente, anche con missioni che
  dichiarano ROE e armi.
- Le validazioni nuove di `Mission_Types` (decisioni 9 e 10) e il controllo del loadout (decisione 13) NON
  dipendono dagli interruttori.

### 5.2 File e funzioni

**`Context/Context.py`** (vicino a `MISSION_TYPE_CATEGORY`, `:515`):
- costanti `TARGET_CLASS_AIR = 'air'`, `TARGET_CLASS_AIR_DEFENCE = 'air_defence'`, `TARGET_CLASS_SHIP = 'ship'`,
  `TARGET_CLASS_SURFACE = 'surface'`, `TARGET_CLASSES`;
- regole `WEAPON_RULE_ANY = 'any'`, `WEAPON_RULE_SELF_DEFENCE = 'self_defence'`;
- `MISSION_WEAPON_POLICY: Dict[str, Optional[Dict[str, Dict[str, object]]]]`: per l'aria
  `{mission_type: {classe: 'any' | 'self_defence' | frozenset(task)}}` (classe assente = non ingaggiabile),
  per `'ground'` e `'sea'` il valore `None`;
- `mission_weapon_policy(domain, mission_type) -> Optional[Mapping]`: valida il tipo con
  `_check_mission_type` e restituisce None se nessun vincolo.

**`Command/Mission_Types.py`**:
- `Target.asset_ids: Tuple[str, ...] = ()`:
  - ammesso solo con `kind` GROUP;
  - id di dominio non vuoti e distinti (`_as_tuple`, `_check_domain_id`);
  - docstring: sottoinsieme esplicito del gruppo.
- `MissionAsset.weapons: Tuple[str, ...] = ()`:
  - id distinti, tutti i domini;
  - se ci sono sia `weapons` sia `attack_profile`, `attack_profile.weapon` deve essere in `weapons`
    (`ValueError`);
  - nuova proprietà `designated_weapons -> Tuple[str, ...]`, che vale `weapons`, oppure
    `(attack_profile.weapon,)`, oppure `()`.

**`Logic/Fire_Control.py`**:
- `target_class(target, grounded: bool = False) -> str`: classi della §2.4;
  `type(target).__name__` come nel resto del modulo; `isEWR` letto con `getattr` (default False).
- `weapon_tasks(domain: str, model) -> Optional[FrozenSet[str]]`:
  - task del modello nel registro del dominio ('air', 'ground', 'sea'), con la stessa ricerca di
    `weapon_category`;
  - None se il modello non è a registro.
- `@dataclass(frozen=True) class WeaponPolicy`:
  - campi `mission_id: str`, `domain: str`, `rules: Mapping[str, object]` (immutabile), `self_escort: bool`;
  - metodo `allows(weapon: Optional[str], target_class: str) -> bool`:
    - arma assente dal registro: True;
    - classe assente: False;
    - `'any'`: True;
    - `'self_defence'`: `self_escort`;
    - insieme di task: intersezione non vuota.
- `restrict_by_policy(fire_control, policy_of: Mapping[str, WeaponPolicy]) -> Callable`:
  - involucro puro con la stessa firma della base; dichiara `target_grounded` solo se
    `ER.accepts_target_grounded(fire_control)`, così l'introspezione del risolutore resta la stessa;
  - tiratore senza politica (`_domain_id(shooter)` non in `policy_of`): risultato della base invariato
    (STESSO oggetto);
  - altrimenti filtra le opzioni con `allows(spec.weapon, target_class(target, grounded))`;
  - tutte tenute: lo stesso oggetto restituito dalla base, così la memoizzazione e l'identità non cambiano;
  - nessuna tenuta: None; alcune tenute: tupla delle tenute, nello stesso ordine;
  - una `ShotSpec` singola si tratta come una sequenza di un elemento e, se tenuta, si restituisce com'era.
- Docstring: aggiornare il punto 1 (`:29`) e "Cosa NON fa" (`:159-160`) con il rimando alla F7a.

**`Logic/Engagement_Resolver.py`**:
- Costanti `ROE_WEAPON_FREE`, `ROE_PRIORITY_DESIGNATED`, `ROE_ONLY_DESIGNATED`, `ROE_RETURN_FIRE`,
  `ROE_WEAPON_HOLD`: le stringhe di dominio di `Mission_Types`, ripetute qui per non importare `Command`, come
  `_TIME_EPS`. Un test ne verifica l'uguaglianza.
- `@dataclass(frozen=True) class TargetRules`, i cui campi sono:
  - `roe: str = ROE_WEAPON_FREE`;
  - `designated_ids: FrozenSet[str] = frozenset()`;
  - `designated_area: Optional[Tuple[float, float, float]] = None`, cioè (x, y, raggio efficace) orizzontali;
  - `designated_weapons: FrozenSet[str] = frozenset()`;
  - `air_self_defence: bool = False`, l'esenzione d'autodifesa aerea di `only_designated`;
  - `known_hostile_ids: FrozenSet[str] = frozenset()`, gli ostili degli episodi precedenti;
  - validazione in `__post_init__` (ROE fra le cinque, raggio > 0).
- `resolve_engagement(..., target_rules: Optional[Mapping[str, TargetRules]] = None)`, in coda ai parametri
  keyword: None o vuoto vale "comportamento precedente"; arriva a `_EngagementRun.__init__`.
- Nuovo stato `self.hostile_by_domain: Dict[str, set]`. In `_on_launch` (`:2481`), per ogni salva lanciata,
  aggiungere `shooter_id` a `hostile_by_domain[self.domain_of[target_force_id]]`. Va fatto all'istante del
  lancio, prima di ogni nuova decisione.
- `_is_designated(shooter_id, target, time) -> bool`:
  - `target.id` in `designated_ids`;
  - oppure, con un'area, la posizione `_position_at(target, time)` ha distanza orizzontale ≤ raggio;
  - posizione ignota: non designato.
- `_is_hostile(shooter, target_id) -> bool`: `target_id` in `known_hostile_ids` oppure in
  `hostile_by_domain[self.domain_of[shooter.force_id]]`.
- In `_fire_control` (`:2293`), dopo la chiamata attuale e se esistono regole per il tiratore, applicare la
  funzione pura di modulo `apply_target_rules(rules, result, designated: bool, hostile: bool, air_target: bool)`:
  - `weapon_hold`: None;
  - `return_fire` e target non ostile: None;
  - `only_designated`, target non designato e non (`air_target` e `air_self_defence`): None;
  - target designato con `designated_weapons`: solo quelle opzioni (nessuna: None);
  - target non designato: tolte le opzioni con arma in `designated_weapons`;
  - stessa normalizzazione delle opzioni di `_options`.

  `air_target` = bersaglio aereo e non a terra all'istante (`self.grounded.at`).
- In `_schedule_next`, sostituire `pool = priority or viable` (`:2144`) con:
  `pool = priority or self._designated_first(shooter, viable) or viable`.
  - `_designated_first` restituisce gli elementi di `viable` il cui bersaglio è designato a `t_fire`, solo se
    la ROE del tiratore è `priority_designated`; altrimenti una lista vuota.
  - Il resto (dottrina, `t_first`, chiave di scelta) invariato.
- Docstring del modulo, punto 3 (`:24`), e una sezione "Regole di bersaglio di missione (F7a)".

**`Logic/Mission_Adapter.py`**:
- `TARGET_POINT_RADIUS_M = 500.0`, STIMA (decisione 11).
- `designated_targets(mission, blocks, mission_of, assets, side) -> Tuple[FrozenSet[str], Optional[Tuple[float, float, float]]]`:
  - forme della §2.1;
  - filtro ai nemici: `getattr(blocks[owner_block], 'side')` diverso da `side`;
  - `asset_ids` rispettato;
  - gruppo amico o id sconosciuto: insieme vuoto con un `info`/`warning`;
  - POINT/AREA/ZONE: `(x, y, raggio efficace)` da `target.position`.
- `weapon_policies(missions, assets) -> Dict[str, FC.WeaponPolicy]`:
  - per ogni asset di missione con `mission_weapon_policy` non None;
  - `self_escort` da `AIRCRAFT_LOADOUTS[asset._model][asset.assigned_loadout]['self_escort_capability']`,
    False se manca.
  - Mission_Adapter oggi non importa Fire_Control: l'import è nuovo, e Fire_Control non importa
    Mission_Adapter, quindi non nasce un ciclo. Da verificare con la suite.
- `target_rules(missions, blocks, mission_of, assets, side_of) -> Dict[str, ER.TargetRules]`. Crea una regola
  SOLO per gli asset la cui missione ha una ROE diversa da `weapon_free` OPPURE armi designate non vuote:
  senza, nessuna voce, quindi il risolutore è identico. Il campo `air_self_defence` vale True se la politica
  della missione ha `'self_defence'` per la classe `air`.

**`Logic/Session_Simulator.py`** (`run_session`):
- in `_check_missions` (`:1797`), per ogni `MissionAsset` aereo con `loadout` non None diverso da
  `assigned_loadout` dell'asset: `ValueError` (decisione 13);
- dopo la costruzione di `assets_by_id`:
  - con `F7_WEAPON_POLICY`, `policies = MA.weapon_policies(...)`; se non vuoto,
    `fire_control = FC.restrict_by_policy(fire_control, policies)`. Va fatto PRIMA di ogni uso: lo usano tutti
    gli episodi e la ri-pianificazione.
  - con `F7_TARGET_RULES`, `rules = MA.target_rules(...)`.
- in `engage` (`:2449`), se `rules` non è vuoto, `extra['target_rules']` = le regole, con `known_hostile_ids`
  aggiornati (`dataclasses.replace`). Gli ostili si accumulano per dominio di coordinamento dai
  `result.salvos` degli episodi già risolti (`shooter_id` per `coordination[target_force_id]`). Le chiavi
  degli asset che non compaiono nella componente sono innocue.
- docstring: sezione "`fire_control`" (`:434-443`) e una sezione "Regole d'ingaggio di missione (F7a)".

### 5.3 Effetti sugli altri moduli e sui chiamanti

- **`run_session`**: firma invariata. I chiamanti in produzione e nei test (`Scenario_Fixtures.run`, S11,
  `Test_Session_Simulator`) non cambiano.
- **`resolve_engagement`**: un keyword nuovo e facoltativo. I chiamanti diretti nei test del risolutore non
  cambiano.
- **`Fire_Control`**: funzioni nuove, `make_registry_fire_control` invariata.
  `Test_Session_Scenarios_S19.py:164` chiama la fire control dei registri direttamente, fuori dalla
  sessione: non tocca l'involucro.
- **`_mission_target_ids`** (F6-B1): resta, con un solo cambio, il rispetto di `asset_ids` per GROUP (nuovo
  campo, nessun uso oggi). Non filtra per lato, per non cambiare S25-TGT.
- **`Air_Resources_Assigner` e `Aircraft_Data`**: non toccati.

### 5.4 Vincoli

- **RNG**: nessuna estrazione nuova e nessuno stream nuovo. Un filtro che cambia una scelta sposta le
  estrazioni successive dello stesso ingaggio (atteso, solo dove la scelta cambia).
- **Nomi stabili**: nessun cambio di `session_id`, ordine o varianti negli scenari esistenti. S19AD mantiene i
  nomi delle varianti (`strela_overflight_ifv_only`, ..., `Test/Scenario_Baseline.py:269`) anche senza filtri
  di test.
- **Costanti**: `TARGET_POINT_RADIUS_M` = 500 m (STIMA). La tabella `MISSION_WEAPON_POLICY` è una scelta di
  progetto, non un dato tarato: va dichiarata come tale.
- **Nessuna dipendenza da DCS.**

### 5.5 Test unitari

- **`Test_Context`**:
  - ogni tipo aereo di `MISSION_TYPES['air']` ha una voce;
  - le classi sono in `TARGET_CLASSES`;
  - ogni task usato esiste in almeno un'arma di `AIR_WEAPONS`;
  - terra e mare valgono None.
- **`Test_Mission_Types`**:
  - `asset_ids` solo con GROUP, distinti;
  - `weapons` distinti;
  - incoerenza fra `weapons` e `attack_profile.weapon` rifiutata;
  - `designated_weapons` nei tre casi.
- **`Test_Fire_Control`** (con la fire control dei registri):
  - F-15C 'Eagle Sweep' in CAP contro BMP-2: None;
  - contro un aereo: invariato (stesso oggetto).
  - A-10C 'Maverick/Gun CAS' in CAS contro BMP-2: AGM-65D, Mk-82AIR e cannone tenuti.
  - F-16C 'SEAD':
    - contro BMP-2: None;
    - contro un SAM: le opzioni con task SEAD.
  - Anti_Ship contro un carro: None.
  - Contro un aereo:
    - F-16C 'Strike' (self_escort True): AIM-9M tenuto;
    - A-10C (False): None.
  - Arma `test:*`: invariata.
  - `target_grounded` inoltrato solo se la base lo accetta (`accepts_target_grounded` sull'involucro).
  - Tiratore senza politica: stesso oggetto.
  - `target_class` per aereo in volo, aereo a terra, nave, SAM, AAA, carro.
- **`Test_Engagement_Resolver`** (geometria controllata, fire control a tabella):
  - `target_rules=None` e `{}` danno un `EngagementResult` uguale a quello di prima, campo per campo;
  - `only_designated`: nessuna salva su un non designato, salve sul designato;
  - esenzione `air_self_defence` contro un aereo;
  - `priority_designated`: con designato e opportunità entrambi utili, il primo lancio è sul designato;
    designato non rilevato: tiro sull'opportunità;
  - armi designate: sul designato solo quell'arma; arma esaurita, nessun tiro sul designato; sul non designato
    l'arma designata non è mai usata;
  - `weapon_hold`: nessuna salva, intercettazioni presenti;
  - `return_fire`: nessuna salva prima di essere bersaglio, salva sul tiratore ostile dopo; `known_hostile_ids`
    abilita subito;
  - designazione geometrica: un bersaglio che esce dall'area non è più designato, a un istante successivo;
  - `apply_target_rules` come funzione pura;
  - costanti ROE uguali a quelle di `Mission_Types`.
- **`Test_Mission_Adapter`**:
  - `designated_targets` per ASSET, GROUP-blocco, GROUP-missione, `asset_ids`;
  - gruppo amico vuoto;
  - POINT con e senza raggio, ESTIMATED con l'incertezza;
  - `target_rules` non crea voci con `weapon_free` e senza armi;
  - `weapon_policies`, con `self_escort` dal loadout.
- **`Test_Session_Simulator`**:
  - loadout di missione incoerente: `ValueError`;
  - con i due interruttori spenti, una missione con `only_designated` produce l'esito di `weapon_free`;
  - un `return_fire` vede gli ostili di un episodio precedente.

### 5.6 Scenari

**S19AD, migrazione** (Fatto quando del Piano: "S19 senza filtro di test dà lo stesso esito di prima"):
- togliere `maverick_only_fire_control` e `ifv_only`: la fire control diventa `make_registry_fire_control()`;
- missioni CAS con `MissionAsset.weapons=('AGM-65D',)`, costruite con un parametro nuovo e facoltativo
  `weapons` di `F.missions_for`, che lo applica a tutti gli asset; il default `()` lascia invariati gli altri
  scenari;
- varianti `_ifv_only`: `Target(kind=GROUP, target_id='Red-Line', asset_ids=<id dei 3 BMP-2>,
  provenance=OBSERVED, observed_at=0.0)` e `MissionRules(roe='only_designated')`, con un parametro nuovo
  `rules` di `F.missions_for`;
- docstring aggiornato;
- asserzioni invariate;
- nuovo test: nessuna arma diversa da AGM-65D lanciata dagli A-10C e, nelle varianti `_ifv_only`, nessuna salva
  degli A-10C su `ad0`.

**S28, nuovo** (`Test/Test_Session_Scenarios_S28.py`):
- fire control dei registri;
- dottrina ad oltranza (`BOTH_HOLD`) per isolare le regole dal disingaggio;
- 4 seed per variante;
- geometria da tarare dallo sviluppatore perché ogni premessa sia NON vacua. Se una premessa non si ottiene,
  ci si ferma e lo si riporta, senza ritoccare le regole.

| Unità | Varianti (in quest'ordine) | Composizione | Asserzioni |
|---|---|---|---|
| S28-ROE | `free`, `priority`, `only`, `hold`, `rules_off` | 2 F-16C Block 52d 'Strike' (Mk-82, Mk-83, AIM-9M), 3000 m; Red-Column (3 BMP-2) sulla rotta prima di Red-Depot (3 BMP-2), bersaglio GROUP 'Red-Depot'; `priority` con `weapons=('Mk-82',)`; `rules_off` = `only` con `F7_TARGET_RULES` spento | `free`: almeno una salva su Red-Column (premessa); `only`: zero salve su Red-Column e almeno una su Red-Depot; `priority`: nessuna Mk-82 su Red-Column, almeno una Mk-82 su Red-Depot; `hold`: zero eventi di munizioni Blue; `rules_off` uguale a `free` evento per evento |
| S28-CLASS | `cap_low`, `cap_low_off`, `sead`, `sead_off`, `self_defence`, `self_defence_off` | `cap_low`: F-15C 'Eagle Sweep' in CAP a 300 m sopra 3 BMP-2; `sead`: F-16C 'SEAD' (AGM-88) contro Red-AD (BMP-2 + un SAM con radar a registro); `self_defence`: F-16C 'Strike' e A-10C 'Maverick/Gun CAS' in missioni Strike/CAS incrociati da 2 MiG-29S 'CAP'; `*_off` = `F7_WEAPON_POLICY` spento | `cap_low_off`: almeno una salva di cannone su un BMP-2 (premessa); `cap_low`: nessuna salva Blue su bersagli di superficie; `sead`: nessuna salva su BMP-2, almeno una sul SAM; `sead_off`: almeno una salva su BMP-2; `self_defence`: almeno un AIM-9M dell'F-16C sui MiG (aggregato sui seed), nessuna salva dell'A-10C sui MiG; `self_defence_off`: almeno una salva dell'A-10C sui MiG (premessa) |
| S28-ZONE | `zone_only`, `zone_free` | F-15C 'Eagle Sweep' in CAP con bersaglio ZONE di raggio 20 km; 2 MiG-29S, uno attraverso la zona e uno fuori zona ma a portata; `zone_only` con `only_designated` | `zone_free`: salve su entrambi (premessa); `zone_only`: nessuna salva sul MiG fuori zona, almeno una su quello in zona |

- In `Test/Scenario_Baseline.py` aggiungere in coda tre voci `UNITS` con `_by_occurrence` e i nomi di variante
  della tabella: 13 varianti x 4 seed = **52 esecuzioni nuove**.
- Aggiornare il docstring di `missions_for` (`Scenario_Fixtures.py:673-674`): bersaglio, ROE e armi sono
  usati dalla F7a.

### 5.7 Esito atteso del confronto con la fotografia (F7a, con le raccomandazioni)

- **918 esecuzioni IDENTICHE**:
  - politica d'armi: sonda (a), 0 cambiate;
  - nessuna missione esistente dichiara ROE o armi, quindi nessuna `TargetRules`;
  - nessun controllo nuovo scatta, perché le fixture copiano il loadout.
- Comprese le **24 di S19AD** dopo la migrazione. La spiegazione:
  - `maverick_only` diventa le armi designate su un bersaglio che designa tutto Red-Line;
  - `ifv_only` diventa `only_designated` sui 3 BMP-2;
  - entrambi passano per lo stesso `None` o per la stessa tupla filtrata, nello stesso punto del risolutore.

  Se una delle 24 cambia, è un errore della migrazione: va spiegato prima di procedere.
- **52 esecuzioni NUOVE** (S28); fotografia da rigenerare a **970** dopo l'approvazione.
- Con scelte diverse:
  - decisione 7 alternativa: +28 cambiate (S16 x4, S25-WIN x24);
  - decisione 4 = B2: fino a 50 cambiate (ORC-twofronts 9, S15 6, S18 6, S21R 6, S25-TGT 19, S6 4; misurate con
    `only_designated`, che è un limite superiore della variante `priority_designated`).

  Ogni differenza va attribuita in `F4_Differenze_Scenari.md`.

### 5.8 Documenti da aggiornare

- **`Piano_Implementazione_Missione.md`**:
  - §5, riga F7: F7a FATTA;
  - nuova deviazione 23, con le decisioni 1-14 e 16 come prese;
  - Fase 7 (righe 190-205): rimando a questo documento;
  - ultimo punto aperto (`:429`): "bersaglio, regole letti dalla F7a".
- **`F4_Differenze_Scenari.md`**: sezione "F7a", con il cambio, l'esito del confronto, le scelte, le costanti
  stimate, i limiti e i test.
- **Manuale DES**, a cura di `des-manual-writer`, dopo il lavoro in corso sul bingo:
  - capitolo 05 (risolutore): `TargetRules`, priorità, `return_fire`;
  - capitolo 07 (orchestratore): involucro e interruttori;
  - capitolo 10: limiti.
- **Memorie**: `project_ammunition_per_weapon_stock.md` (A4 chiusa dalla F7a),
  `project_mission_structure_decisions.md`.

---

## 6. Piano di intervento: F7b (fuoco su posizione)

Da avviare dopo l'approvazione della F7a e delle decisioni del punto 15.

### 6.1 Regola

**Missione di fuoco**: una missione di terra o di mare con bersaglio POINT o AREA e un'azione
`MissionAction(kind=TASK, name='Fire_At_Point', params={'rounds': int ≥ 1, 'weapon': str (facoltativo)}, start=...)`
su un suo waypoint. La condizione d'avvio è pre-calcolabile ed esiste già (`StartCondition`).

Per ogni asset della missione:
- **istante di tiro** `t_f`: l'arrivo al waypoint (`MA.waypoint_times(movement)[indice]`), poi la condizione:
  - ON_ARRIVAL: l'arrivo;
  - AT_TIME: max(arrivo, `time`);
  - AFTER_DURATION: arrivo + `duration_s`.
- **Condizioni**, altrimenti nessun tiro (con log) e esito di missione invariato:
  - l'asset è vivo e non passivo a `t_f`: non disingaggiato, non a fine attività, non a secco;
  - un'arma è utilizzabile (sotto);
  - il punto mirato è entro la portata indiretta (o massima) dell'arma, in orizzontale dalla posizione a `t_f`.
- **Arma**:
  - `params['weapon']`, se presente;
  - altrimenti la prima delle armi dell'asset con task `Artillery` / `Naval_Gunfire_Support` / `Land_Attack`
    (ordine `_candidate_weapons`) che ha scorta e portata.

  Le armi `missile` sono escluse nella prima versione (15e).
- **Colpi**: min(`rounds`, scorta // `stock_per_round`). Impatto a `t_i = t_f + time_of_flight` (stessa formula
  di `shot_spec_for`).
- **Punto mirato** = `target.position` (stimato, N3.e). Raggio di dispersione
  `R = max(radius_m or 0, uncertainty_m or 0 se ESTIMATED, AREA_FIRE_MIN_DISPERSION_M)`.
- **Effetto a `t_i`**:
  - per ogni colpo, nell'ordine, 2 estrazioni per il punto d'impatto uniforme nel disco
    (raggio `R·sqrt(u1)`, angolo `2π·u2`);
  - per ogni nemico del tiratore non distrutto, in ordine di id, la cui posizione a `t_i`
    (`CS.position_on_legs` sui tratti di presenza della sessione, oppure la posizione statica) dista in
    orizzontale ≤ `r_l` dal punto d'impatto: 1 estrazione e `DM.resolve_hit(1.0, destroy_capacity, draw)`;
  - `destroy_capacity` viene dalla riga del template dell'arma per la classe del bersaglio, con la stessa catena
    `target_key` / `_cell` della fire control;
  - Pk zero: nessun effetto.
- **Raggio letale** `r_l` = `AREA_FIRE_LETHAL_RADIUS_PER_MM` (0,25 m/mm, STIMA) x `caliber` del registro;
  ripiego `AREA_FIRE_LETHAL_RADIUS_M` = 25 m (STIMA).

### 6.2 File

- **`Logic/Area_Fire.py`** (nuovo, puro):
  - costanti STIMA: `AREA_FIRE_MIN_DISPERSION_M` = 50, `AREA_FIRE_LETHAL_RADIUS_PER_MM` = 0,25,
    `AREA_FIRE_LETHAL_RADIUS_M` = 25;
  - `@dataclass(frozen=True) FireOrder(mission_id, asset_id, waypoint_index, action_index, t_fire, aim_x, aim_y, dispersion_m, rounds, weapon)`;
  - `fire_orders(mission, movement, asset) -> List[FireOrder]`;
  - `area_fire_event_id(order) -> str`, che vale `'area_fire|<mission_id>|<asset_id>|<wp>|<action>'`;
  - `resolve_area_fire(order, shooter, enemies, positions_at, rng, provenance) -> ER.EngagementResult`, con
    `forces=()`, `t_start=t_f`, `t_end=t_i`, gli `AmmunitionEvent` all'istante `t_f` e i `DamageEvent` a `t_i`.
- **`Logic/Fire_Control.py`**: `area_fire_weapon(shooter, distance_m, weapon=None)` e `area_fire_pk(weapon, target)`.
- **`Command/Mission_Types.py`**: costante `FIRE_AT_POINT_ACTION = 'Fire_At_Point'`. Validazione:
  - l'azione richiede una missione di terra o di mare con bersaglio POINT o AREA;
  - `rounds` intero ≥ 1.
- **`Logic/Session_Simulator.py`**:
  - interruttore `F7_AREA_FIRE = True`; spento, le azioni sono ignorate con un warning, come prima;
  - nuovo tipo di evento in coda `AREA_FIRE_EVENT` all'istante `t_i`. A parità d'istante l'ordine è
    ENGAGEMENT < AREA_FIRE < MOVEMENT, poi l'id;
  - risolto con `order.rng(mission_id=mission_id, event_id=area_fire_event_id(...), counter=0)`. È il primo uso
    dello slot `mission_id` di `Session_Rng`, corretto perché il tiro appartiene a una sola missione;
  - esito applicato subito (`ER.apply_engagement_result` sul blocco del tiratore e sui blocchi colpiti);
  - risultato aggiunto a `results`/`resolved` in ordine di tempo;
  - le distruzioni entrano in `_known_destructions` e quindi negli episodi successivi.
- Verificare che `apply_engagement_result` e `assemble_session_outcome` accettino `forces=()`. Se no, ci si
  ferma e lo si riporta.

### 6.3 Test e scenari

- **`Test_Area_Fire`**:
  - nessuno nel disco, nessun danno;
  - bersaglio fermo nel punto, danni (aggregato su 200 seed contro la frequenza attesa);
  - bersaglio uscito dall'area, nessuna estrazione di danno;
  - estrazioni deterministiche per lo stesso stream;
  - scorta limitante;
  - fuori portata, nessun tiro;
  - asset passivo, nessun tiro.
- **S29-AREA** (nuovo):
  - Red-Art (1 2S19-Msta), missione `Fire_Support` con un breve tratto DEPARTURE -> OBJECTIVE e l'azione
    AT_TIME 600 s su un POINT ESTIMATED (`estimated_at` = -1800, `uncertainty_m` = 200), posto dove era
    Blue-Col;
  - Blue-Col (4 veicoli) a 3 km dal punto all'impatto, Blue-Stay (2 veicoli) fermi nel punto;
  - varianti `stale` (descritta), `on_target` (Blue-Col ancora nel punto), `switch_off`;
  - 4 seed per variante: **12 esecuzioni nuove**;
  - asserzioni:
    - `stale`: nessun `DamageEvent` su Blue-Col, almeno uno su Blue-Stay (aggregato);
    - `on_target`: almeno uno su Blue-Col;
    - `switch_off`: nessun danno da Red-Art.

### 6.4 Esito atteso del confronto (F7b)

- 970 esecuzioni identiche: nessuno scenario esistente dichiara `Fire_At_Point`, e gli stream di ingaggio e di
  tempra non cambiano.
- 12 nuove; fotografia a **982**.

### 6.5 Documenti

- Piano §5: riga F7b e deviazione 24;
- `F4_Differenze_Scenari.md`: sezione "F7b";
- manuale: capitolo 07 (nuovo evento di coda) e capitolo 10 (limiti);
- `EndCriteria`, docstring: POINT/AREA.

---

## 7. Rischi e limiti

- **Priorità solo locale**: `priority_designated` agisce fra i candidati UTILI di un tiratore. Un designato
  non ancora rilevato non trattiene il tiro sulle opportunità, e per riservare le armi va dichiarata l'arma
  (§2.5).
- **Designazione geometrica approssimata**: si valuta all'istante di decisione, non all'impatto. Un bersaglio
  che esce dall'area dopo il lancio riceve comunque la salva (payload congelato, R4).
- **`return_fire`**: conosce le salve, non il solo rilevamento (un radar che illumina non è ostile). Tra
  episodi la memoria passa per la sessione.
- **Winchester e politica d'armi**: un'arma esclusa dalla politica per tutti i bersagli possibili non si
  esaurisce mai. Il criterio su quella categoria allora non scatta: va dichiarato, non corretto.
- **Dati**:
  - `self_escort_capability` dell'A-10C (decisione 8);
  - task dei registri non uniformi: il cannone ha `Strike` e non `A2A`, ma contro gli aerei decidono le righe
    del template, non i task;
  - nessun task `CAS` sull'AGM-65D.
- **Scorta**: senza "protezione del gruppo" la scorta ingaggia ogni aereo nemico rilevato, come oggi.
- **Terra e mare**: nessuna restrizione d'arma per tipo di missione nella F7a; un `Supply` con
  `weapon_free` combatte come un `Attack`.
- **F7b** (modello volutamente semplice, tutte STIME):
  - dispersione uniforme;
  - letalità a soglia;
  - niente fuoco amico, niente intercettazione;
  - niente effetti dottrinali sul colpito;
  - aerei esclusi;
  - un solo evento all'impatto, per cui un bersaglio distrutto da un altro episodio fra `t_f` e `t_i` è già
    distrutto all'impatto (corretto). La scorta però è consumata a `t_i` nell'ordine di applicazione, anche se
    l'evento porta l'istante `t_f`.
- **Dimensione stimata**:
  - F7a circa 600-800 righe di codice e 500-700 di test (S28 compreso): una sessione di `des-developer`;
  - F7b circa 350-450 righe di codice e 300 di test (S29 compreso): una sessione.
