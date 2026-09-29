# Proposta: allocazione dei missili dei SAM puri fra intercettazione e tiro offensivo

**Stato**: PROPOSTA, in attesa di scelta dell'utente (2026-09-25). Nessun file del motore modificato.
**Revisione 2026-09-28 (A6)**: l'utente ha dato due regole di dottrina che sostituiscono B e
riprendono C in forma non onnisciente. La proposta corrente è il **§7 (D + F + L)**; i §4-§6 restano
come storia della decisione.
**Costanti**: le poche costanti introdotte dalle regole qui sotto sono **stime non tarate** e vanno
marcate come tali anche nei commenti del codice.

Contesto: dopo il controllo di portata (`ShotSpec.max_range`, commit `15350cc5`) un SAM a corto
raggio non spara più a un aereo fuori portata, e aspetta. Nel frattempo intercetta le salve in arrivo
sulla sua forza, e per un **SAM puro** (`Mobile.interceptor_shares_ammunition`) ogni intercettazione
consuma un missile del pool unico. Il risultato è uno Strela-10 che finisce i missili sui Maverick
diretti ad altri asset e resta a secco quando gli A-10 arrivano a tiro.

## 1. Riproduzione (numeri)

Script deterministico in scratchpad (effimero, non nel repo): `repro_strela.py` e `proto_rules.py`.
Si appoggiano ad asset reali (`Test/Scenario_Fixtures`), a `Logic/Fire_Control.make_registry_fire_control`
e a `run_session`. Il motore non viene toccato: gli script leggono salve e risoluzioni avvolgendo
`ER.resolve_engagement`.

**Scenario.** Red-Line (Red, ferma): 3 BMP-2 in (0, 0), (0, 300), (0, 600), più 1 9K35-Strela-10 in
(1000, −300), cioè a circa 1 km dai BMP. Blue-CAS: N A-10C con loadout `Maverick/Gun CAS`, a 3000 m di
quota, in volo da x = −40 km verso x = +20 km (sorvolo). Il Maverick (AGM-65D) ha portata 15 km; lo
Strela (9M37) 5 km, con 8 missili e scorta condivisa (`ammo 8, interceptor_stock 8, shared True`).
Seed: session_id `repro-strela-1`.

### 1.1 Caso pulito: 4 A-10, 4 Maverick ciascuno, disingaggio disattivato

Due parametri di disturbo sono neutralizzati solo dentro lo script (v. §1.2):
- `ammunition` degli A-10 forzata a 4, i Maverick veri del loadout;
- tabella dottrinale senza Red/Blue, quindi si combatte fino all'annientamento.

| t [s] | Evento |
|---|---|
| 162.7–164.3 | 4 A-10 lanciano 8 salve × 2 AGM-65D (16 missili) da 15.8–16.1 km dallo Strela. Bersagli: ifv0 ×3, ifv1 ×2, ifv2 ×3. **Nessuna salva sullo Strela.** |
| 186.1–187.8 | 8 eventi-salva sulla forza Red, capacità 1 ciascuno: lo Strela intercetta 1 Maverick per evento, **8 intercettazioni, scorta 8 → 0 a t = 187.8** |
| 202.8–224.4 | Lo Strela *rileva* i 4 A-10 (sensore aria 10 km), cioè dopo aver già speso tutti i missili |
| 238.0–240.7 | Gli A-10 entrano nei 5 km dello Strela. **Salve dello Strela: 0** |

Esito: Red perde 3 BMP su 3 (lo Strela è illeso), Blue perde 0 A-10 su 4.

Media su 30 seed (`repro-strela-1…30`), sorvolo:

| A-10 | Intercettazioni Strela | Salve Strela | Perdite Red (su 4) | Perdite Blue |
|---|---|---|---|---|
| 2 | 4.00 | 2.00 | 2.47 | 0.70 / 2 |
| 4 | 8.00 | 0.00 | 2.93 | 0.00 / 4 |
| 4, **senza** intercettazioni del SAM puro (regola A, §4) | 0 | 4.00 | 2.97 | 1.20 / 4 |

Le 8 intercettazioni salvano in media **0.04 BMP**. Ogni salva è di 2 Maverick e lo Strela ne ferma 1,
quindi l'altro colpisce con Pk 0.75 e il BMP muore comunque. In cambio gli A-10 **non subiscono più
perdite**: con gli 8 missili ancora a bordo lo Strela ne avrebbe abbattuti 1.2 in media.

### 1.2 Caso "motore così com'è" (1 A-10, munizioni e dottrina di default)

- L'A-10 ha `ammunition = 1183`: 4 AGM-65D, 4 Mk-82, 1 AIM-9 **più 1174 colpi del cannone**
  (aggregazione del loadout). Spara una salva ogni 1.5 s: **16 salve (32 Maverick) su ifv0**, tutte
  prima del primo impatto (da t = 162.7 a 185.2).
- Lo Strela intercetta 1 Maverick per salva fino a esaurimento: 8 intercettazioni, **scorta 0 a
  t = 196.6**. Tutte difendono ifv0, nessuna difende lo Strela stesso.
- Red **si disingaggia già a t = 186.1**: la prima perdita dà shock 1/4 = 0.25, sopra la soglia di
  0.20 (`Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS`). Da quel momento la forza non lancia più nulla,
  quindi lo Strela non avrebbe sparato neppure con i missili ancora a bordo.

Col disingaggio disattivato e le munizioni native, l'A-10 lancia 64 salve (128 Maverick) e distrugge
tutta la forza Red, Strela compreso.

**Conferma.** Il problema segnalato è reale e riproducibile: un SAM puro spende l'intero pool per
intercettare colpi diretti ad altri asset, senza aver ancora rilevato i lanciatori, e resta senza
missili quando questi entrano a tiro. Nello scenario di default è però **mascherato da due difetti
indipendenti** (munizioni aggregate dell'aereo, disingaggio alla prima perdita), elencati al §5.
L'osservazione sul Buk che spende missili in tiro offensivo non è stata riprodotta qui: è il
comportamento atteso e non fa parte del problema.

## 2. Meccanismo attuale (dal codice)

Le righe si riferiscono al commit `757baaac`.

1. **Chi intercetta.** `Military.salvo_interceptors` (`Block/Military.py:618-663`) restituisce ogni
   Vehicle/Ship operativo per cui esiste una `ThreatAA`, cioè **ogni asset di difesa aerea**, con i
   canali di `engagement_channels('air')` o `DEFAULT_INTERCEPTION_CHANNELS = 1` (`Military.py:51`).
   Nessun requisito di capacità antimissile: uno Strela-10 IR vale quanto un Tor. Il risolutore copia
   l'elenco in `_interceptors_of` (`Logic/Engagement_Resolver.py:939-957`), ordinato per id.
2. **Quali colpi.** `_on_resolve` (`Engagement_Resolver.py:1329-1418`) lavora sull'evento-salva
   **della forza**, non del singolo asset. Somma i colpi intercettabili di tutte le salve del
   gruppo, qualunque sia il `target_id` (`:1344`), e confronta il totale con la capacità **dell'intera
   forza** (`_capacity`, `:1316-1327`; stessa formula di `Military.salvo_interception_capacity`,
   `Military.py:665-717`). **Risposta alla domanda 1: sì, tutti i colpi intercettabili, qualunque sia
   il bersaglio designato.** Non c'è alcun controllo geometrico (distanza intercettore–bersaglio del
   colpo) né di rilevamento: né il colpo né il suo lanciatore devono essere stati visti.
3. **Chi paga.** Il loop `:1352-1375` consuma i canali degli intercettori **in ordine di id**. Per un
   SAM puro `interceptor_stock` è una vista di `ammunition` (`_Shadow`, `:644-685`; attivazione in
   `_build_forces`, `:894-899`; regola in `Asset/Mobile.py:181-206`), quindi ogni intercettazione è un
   missile offensivo in meno. **Risposta alla domanda 2: sì, e per costruzione.** È la formulazione a
   "salva di Hughes" (R1): la difesa è un termine della forza bersaglio (y, z = missili intercettati
   per salva), non del singolo asset. Il pool unico (decisione 2026-09-23) ha poi trasformato questa
   proprietà in un consumo della capacità offensiva, e il controllo di portata ha reso visibile la
   conseguenza: prima lo Strela sparava all'A-10 appena rilevato, a qualunque distanza, e il pool si
   esauriva nell'altro verso.
4. **Erosione a valle.** `_on_launch` (`:1280-1287`) annulla un lancio già schedulato se nel frattempo
   le intercettazioni hanno eroso il pool: è il caso previsto e documentato, non un errore.
5. **Riserve o priorità.** **Risposta alla domanda 3: nessuna.** Non esiste una logica di riserva,
   né una priorità per il lanciatore, né una distinzione fra autodifesa e difesa d'area. L'unico
   limite è `min(canali, scorta)`.
6. **Canali per evento, non per unità di tempo.** Con `salvo_window = 0`, il default di
   `SessionOrder` (`Command/Session_Types.py:110`), ogni impatto separato da più di `TIME_EPS` è un
   evento a sé e la capacità si rigenera
   (`test_capacity_refreshes_between_separate_salvo_events`, comportamento voluto). Il limite di un
   canale dello Strela quindi non frena il ritmo delle intercettazioni: lo frena solo la scorta.

## 3. Criteri di valutazione

- **Determinismo / RNG**: nessuna delle regole estrae numeri casuali. L'intercettazione resta un
  contatore (R1) e l'ordine delle estrazioni del danno non cambia.
- **Contratto pubblico**: `ShotSpec`, `SalvoResolution`, `InterceptionEvent`, la firma di
  `resolve_engagement` e `Military.salvo_interceptors` devono restare invariati, se possibile.
- **DES**: niente stato previsionale; tutto ciò che è decidibile all'istante dell'evento `_RESOLVE`.
- **Nebbia di guerra (C, prossima)**: una regola che usa informazioni che il difensore non ha (rotta
  futura del nemico, lanciatore non rilevato) andrà rifatta con la nebbia.

## 4. Regole alternative

I numeri di A, B e C vengono da un **prototipo in memoria** (`proto_rules.py`, monkeypatch di
`_on_resolve` solo nel processo dello script). Con la regola base il prototipo riproduce il motore
esattamente, su tutte le varianti. Sorvolo = rotta di §1; standoff = gli A-10 virano a x = −11 km e non
entrano mai nei 5 km dello Strela. Media su 30 seed, 4 Maverick per A-10.

| Regola | 2 A-10 sorvolo: interc. / salve Strela / perdite Red / perdite Blue | 4 A-10 sorvolo | 4 A-10 standoff |
|---|---|---|---|
| Base (oggi) | 4 / 2.0 / 2.47 / 0.70 | 8 / 0 / 2.93 / 0.00 | 8 / 0 / 2.93 / 0 (residuo 0) |
| A. Autodifesa | 0 / 3.9 / 2.83 / 1.50 | 0 / 4 / 2.97 / 1.20 | 0 / 0 / 2.97 / 0 (residuo 8) |
| B. Riserva 50 % | 4 / 2.0 / 2.47 / 0.70 | 4 / 2 / 2.93 / 0.67 | 4 / 0 / 2.93 / 0 (residuo 4) |
| C. Priorità al lanciatore (T = 120 s, geometria esatta) | = A | = A | = Base |
| D. Capacità dichiarata (Strela non intercetta) | = A | = A | = A |

### A. Autodifesa per i SAM puri

**Regola.** Un intercettore con pool condiviso intercetta solo i colpi il cui `target_id` è lui
stesso. Gli intercettori a contatori distinti (cannoni AA, sistemi misti, navi con SAM + cannoni)
continuano a fare difesa d'area come oggi.

- **Pro**: una riga di condizione; nessuna costante; nessuna informazione nascosta al difensore;
  risolve completamente il caso Strela (8 missili conservati, 1.2 A-10 abbattuti su 4).
- **Contro**: toglie la difesa d'area a **tutti** i SAM puri, compresi quelli nati per farla (Buk,
  S-300, e le portaerei con Sea Sparrow + Phalanx, che il registro classifica come SAM puri). In
  standoff lo Strela resta con 8 missili inutilizzati mentre i BMP muoiono: plausibile per uno
  Strela, sbagliato per un sistema d'area.
- **Costo**: `_on_resolve`, dove l'allocazione diventa **per salva** invece che per totale della
  forza, perché l'idoneità dipende dal bersaglio del colpo. `_capacity` diventa un tetto superiore e
  `SalvoResolution.capacity` va ridocumentata (il campo resta). In
  `Military.salvo_interception_capacity` cambia la docstring: è la capacità massima, non quella
  garantita. Test da aggiornare: `Test_Engagement_Resolver`
  (`test_pure_sam_interceptions_draw_on_its_missiles`, `test_pure_sam_offensive_fire_reduces_...`,
  dove il colpo è diretto a `r1` e non all'intercettore) e i conteggi di S10-S18.
- **Rischio**: basso.

### B. Riserva per il tiro offensivo

**Regola.** Un SAM puro intercetta colpi diretti **ad altri** solo finché la scorta resta sopra
`ceil(f × scorta iniziale)`. L'autodifesa è sempre ammessa, fino all'ultimo missile.

- **Pro**: conserva la difesa d'area; una sola costante; nessuna informazione nascosta; deterministica.
- **Contro**: è una mezza misura. Con 4 A-10 lo Strela conserva 4 missili (2 salve) e abbatte 0.67
  A-10; con 2 A-10 **non cambia nulla**, perché la soglia coincide esattamente col consumo. Il valore
  di f è arbitrario: una stessa f non va bene per uno Strela e per un S-300.
- **Costante stimata**: `INTERCEPT_RESERVE_FRACTION = 0.5`, da dichiarare come stima (eventualmente
  per classe SAM_Small/Medium/Big).
- **Costo**: come A, più la scorta iniziale nello stato ombra (un campo in `_Shadow`, letto in
  `_build_forces`; oggi `shadow.asset.interceptor_stock` è ancora quello iniziale durante la run, ma
  è meglio non dipendere da questo dettaglio).
- **Rischio**: basso.

### C. Priorità al lanciatore

**Regola.** Un SAM puro non intercetta un colpo diretto ad altri se **il lanciatore di quel colpo**
entrerà nella sua portata (`fire_control(sam, lanciatore).max_range`) entro T secondi: il missile
viene conservato per il tiro diretto. Il calcolo è analitico, con
`engagement_intervals(legs[sam], legs[lanciatore], max_range)`, lo stesso già usato dal controllo di
portata.

- **Pro**: è il comportamento tatticamente migliore. Nel sorvolo si comporta come A, in standoff
  come oggi (lo Strela intercetta, perché i lanciatori non verranno mai a tiro).
- **Contro**:
  - **Onniscienza**: usa la rotta *futura* del nemico, che il difensore non conosce. Lo Strela non
    ha nemmeno rilevato gli A-10 all'istante delle intercettazioni (rilevamento a t = 202–224, contro
    intercettazioni a 186–188).
  - La versione corretta, che considera solo i lanciatori già rilevati, **non fa niente nel caso
    riprodotto**, per la ragione appena detta.
  - Ogni intercettazione chiama la fire control.
  - Introduce una previsione nel DES, anche se calcolata all'istante.
  - Da rifare con la nebbia di guerra.
- **Costante stimata**: `LAUNCHER_PRIORITY_HORIZON_S` (prototipo: 120 s).
- **Costo**: `_on_resolve`, più accesso a `fire_control` e `legs` in fase di risoluzione (sono già
  attributi della run). Nessun cambio di contratto.
- **Rischio**: medio (la semantica della previsione, e il conflitto con la nebbia di guerra).

### D. Capacità di intercettazione dichiarata dai registri (causa radice)

**Regola.** Intercetta munizioni in arrivo solo un asset che ha almeno un'arma AD dichiarata capace
di farlo. Oggi `Military.salvo_interceptors` prende **ogni** asset con `ThreatAA` e gli attribuisce
Pk = 1 per canale. Uno Strela-10 (9M37, IR) o uno Stinger non sono sistemi antimunizioni: non
ingaggiano un Maverick in volo. Tor, Pantsir, Tunguska e, in parte, Buk/S-300/Patriot sì.

- **Dati**: `Ship_Weapon_Data` ha già il task `'Anti_Missile'` su ESSM, Sea Sparrow, SM-2/SM-2ER,
  SA-N-9, S-300F, HHQ-7/9/16, Phalanx, AK-630 e Type-730 (12 armi). `Ground_Weapon_Data` non ha il task
  (`Context.GROUND_WEAPON_TASK` contiene solo Anti_Tank/Anti_Air/Artillery/Infantry_Support): va
  aggiunto e assegnato arma per arma, con una proposta di dati da far approvare, come B1.
- **Pro**: corregge la causa, non il sintomo; nessuna costante di comportamento, solo dati di
  registro; nessuna informazione nascosta; deterministica; contratto invariato (cambia solo *chi*
  compare in `salvo_interceptors`, e lo stesso insieme serve a `salvo_interception_capacity`). Nel
  caso Strela dà lo stesso esito di A.
- **Contro**:
  - Richiede un lavoro sui dati (enum `GROUND_WEAPON_TASK`, task su circa 16 armi terrestri
    Anti_Air, decisione sui cannoni AA: uno Shilka intercetta un Maverick?).
  - Scenari e test che oggi fanno intercettare Strela e Shilka cambiano esito (S10-S18, validazione).
  - **Da sola non risolve** il problema generale per un SAM puro che *è* anche intercettore: un Buk
    continuerebbe a spendere i 4 missili sui Maverick diretti ad altri.
- **Costo**: `Context.GROUND_WEAPON_TASK`, `Ground_Weapon_Data` (task), `Military.salvo_interceptors`
  (filtro, con un helper condiviso con `Mobile.interceptor_stock_from_registry` per non duplicare la
  selezione), docstring in `Mobile.py` (blocco ROUNDS_PER_GUN_INTERCEPT/SCORTA CONDIVISA). Il
  risolutore non si tocca.
- **Rischio**: medio (cambia la popolazione degli intercettori in tutti gli scenari).

### E. Nessuna modifica (dottrina di scenario)

Il comportamento attuale è coerente con la sua specifica (R1 di Hughes, difesa di forza, pool unico)
e si può correggere solo componendo gli scenari: niente Strela da soli in prima linea, SHORAD in una
forza separata dalle forze manovranti.

- **Pro**: costo zero.
- **Contro**: il difetto resta per qualunque composizione realistica. La composizione S1 di
  riferimento (`combined_arms_scenario`) mette proprio uno Strela e uno Shilka nella stessa forza dei
  BMP. Inoltre scarica sull'autore di scenario un problema del modello.
- Da escludere, salvo come stato transitorio.

### Accessoria F. Ordine di consumo degli intercettori

Oggi i canali si consumano in ordine di id (`_interceptors_of`, `Military.salvo_interceptors`): un
Buk con id minore dello Shilka brucia i suoi missili prima dei 20 "intercettori" a cannone dello
Shilka. Proposta: chiave di ordinamento `(shared_pool, id)`, così che si consumino prima le scorte
dedicate (cannoni, sistemi misti) e poi i pool condivisi. L'ordine resta deterministico, costa due
righe e non introduce costanti. Si abbina a qualunque delle regole sopra.

## 5. Difetti indipendenti emersi (fuori scope, da decidere a parte)

1. **Munizioni aggregate degli aerei**: `ammunition` dell'A-10 = 1183, perché include i colpi del
   cannone. L'aereo lancia 128 Maverick da un loadout che ne ha 4. È già fra le decisioni utente
   aperte e **va chiuso prima di tarare qualunque regola di questo documento**.
2. **Overkill dello stesso tiratore**: `_engaged_shooters` (`Engagement_Resolver.py:1067-1085`)
   esclude il tiratore che decide, quindi l'A-10 mette 16 salve sullo stesso BMP prima del primo
   impatto (refire 1.5 s, tempo di volo 23 s). Le proprie salve in volo dovrebbero contare come
   copertura (tiro "shoot-look-shoot").
   **Risolto 2026-09-29**: saturazione del bersaglio per la forza (P_cov ≥ 0,9) e tetto "due
   missili, poi guarda" per tiratore. V. `Proposta_Overkill_Tiro.md`.
3. **Disingaggio alla prima perdita**: con 4 asset, una perdita dà shock 0.25 ≥ 0.20, e la forza rompe
   il contatto al primo impatto. Per forze piccole la soglia di shock è quasi un interruttore.
   **Risolto 2026-09-29**: soglia di rottura stocastica modulata da morale, rapporto di forze
   percepito (efficacia antiaerea per le forze aeree), fuoco senza risposta e postura; shock con
   minimo 2 perdite. V. `Proposta_Soglia_Rottura_Stocastica.md`.
4. **Intercettazione senza rilevamento**: né il colpo né il lanciatore devono essere stati rilevati
   dall'intercettore. Ne terrà conto la nebbia di guerra (C).
5. **Canali rigenerati per evento** (§2, punto 6): con `salvo_window = 0` il limite di canali non frena
   un flusso di salve piccole. È un comportamento voluto e testato, ma rende la scorta l'unico
   vincolo reale.

## 6. Raccomandazione

**Adottare D + B + F, in quest'ordine di valore. Se si vuole un solo intervento subito, A.**

- **D** è la correzione giusta del caso segnalato: lo Strela-10 non deve essere un intercettore di
  munizioni, e il modello oggi gli dà Pk = 1 per canale contro un Maverick. È un lavoro di dati con
  proposta da approvare (stile B1). Non tocca il risolutore e non introduce costanti di comportamento.
- **B** (riserva, con autodifesa sempre ammessa) copre i SAM puri che restano intercettori dopo D
  (Buk, S-300, Tor, portaerei), senza togliere loro la difesa d'area come farebbe A. Una sola costante
  stimata, eventualmente per classe.
- **F** costa due righe e rende più sensato l'ordine di consumo in ogni caso.
- **A** è l'alternativa minima se D richiede troppo lavoro sui dati adesso: risolve completamente il
  caso Strela, a costo di togliere la difesa d'area anche ai SAM puri d'area. È reversibile quando
  arriva D.
- **C** è da scartare ora: ha il comportamento migliore sulla carta, ma poggia su informazioni che
  il difensore non ha, e nella versione "solo lanciatori rilevati" non risolve il caso riprodotto.
  Si può riprendere dopo la nebbia di guerra, sopra D + B.

**Prerequisito**: decidere prima le munizioni aggregate degli aerei (§5.1). Con 128 Maverick per
A-10 nessuna regola di allocazione del difensore produce numeri sensati, e i confronti del §4 hanno
dovuto forzare a mano la scorta a 4.

Quando una regola viene implementata, lo scenario del §1.1 (4 A-10, sorvolo e standoff) va
trasformato in uno scenario di test persistente in `Test_Session_Scenarios_*`, con esito qualitativo
(lo Strela conserva missili e spara agli A-10), non numerico.

---

## 7. Revisione 2026-09-28 (A6): D + F + L, sopra la scorta per arma

**Stato**: APPROVATA il 2026-09-28 (decisioni al §7.7). TUTTI I PASSI FATTI il 2026-09-28: dati `Anti_Missile` e D + F (`Proposta_Dati_Anti_Missile.md` §6), scenario persistente S19 (§7.8), L1 (§7.9), L2 + L3 (§7.10).

### 7.1 Regole di dottrina date dall'utente

1. **Priorità al lanciatore.** La difesa aerea (SAM e AAA) dà la **massima priorità, di tempo e di
   numero di armi impiegate**, all'intercettazione del velivolo che ha lanciato un'arma A2G, se il
   velivolo è entro il raggio d'intercettazione della difesa.
2. **Armi autonome come bersaglio.** Sono bersagli legittimi della difesa aerea **solo** le armi
   autonome (missili, droni, bombe plananti) lanciate a distanza considerevole dalle zone
   d'intercettazione, e solo se il sistema che intercetta (missile, cannone, puntamento) è in grado
   di intercettarle e colpirle.

### 7.2 Cosa cambia rispetto alla raccomandazione del §6 [V + I]

Prerequisito ormai chiuso: la scorta per arma (A1, commit `1d0c1127`) ha eliminato le munizioni
aggregate e la regola "SAM puro". Nel codice attuale (verificato il 2026-09-28) il difetto dello
Strela resta, perché:
- `Military.salvo_interceptors` seleziona ancora **ogni** asset con `ThreatAA`, con Pk = 1 per canale;
- `Engagement_Resolver._on_resolve` confronta ancora il **totale** dei colpi intercettabili della
  forza con la capacità della forza, senza guardare né chi ha lanciato né da dove;
- la scelta del bersaglio (`_schedule_next`, chiave `(coperture, t_fire, t_ready, target_id)`) è un
  round-robin: nessuna priorità per chi sta attaccando.

| Regola | §6 (2026-09-25) | §7 (ora) | Motivo |
|---|---|---|---|
| **D**, capacità dichiarata | per asset | **per arma** (`Anti_Missile`) | scorta per arma: il Tunguska intercetta col 9M311 e col 2A38M, lo Strela col 9M37 no. È la condizione "il sistema è in grado di intercettare" della regola 2 |
| **B**, riserva 50 % | adottata | **eliminata** | superata dalla regola 2: un'arma lanciata dentro la zona non si intercetta (si spara al lanciatore); una lanciata da fuori, da un lanciatore che non entrerà mai a tiro, è esattamente dove conviene spendere i missili. La riserva non ha più un caso d'uso, e sparisce la sua costante arbitraria |
| **C**, priorità al lanciatore | scartata (onnisciente: rotta futura del nemico) | **ripresa come L**, senza previsione | la regola 1 guarda dove il lanciatore **è** (all'istante del lancio e della decisione), non dove andrà: nessuna informazione nascosta, nessuna costante di orizzonte |
| **F**, ordine di consumo | fra asset | dentro l'asset **già fatto** (cannoni, poi missili: `Weapon_Stores.interceptor_order`); resta l'ordine fra asset | invariato nello spirito |

### 7.3 Regola L: dettaglio

**L1 — Idoneità di un colpo all'intercettazione** (per intercettore *i*, con arma AD *w*). Un colpo
della salva *s* è intercettabile da *i* con *w* solo se valgono tutte e tre:
- (a) **arma autonoma**: `s.spec.interceptable` (già oggi: missili e bombe guidate; proiettili,
  razzi non guidati, bombe a caduta libera e siluri no). Droni: nessun drone è oggi nei registri come
  munizione, entrerebbero dallo stesso flag;
- (b) **capacità (D)**: *w* dichiara il task `Anti_Missile`;
- (c) **lancio da fuori zona**: il punto di lancio `P_L` (posizione del lanciatore a `s.t_launch`,
  ricavata dai tratti di rotta già in `self.legs`) è **fuori dal volume d'intercettazione V_I** di *i*
  (lo stesso volume dichiarato di `Proposta_Volumi_Rilevamento_Intercettazione.md`, già usato dal
  pianificatore delle rotte: una sola definizione di "zona d'intercettazione" in tutto il modello).
  Soglia a margine zero: "fuori da V_I" e basta, nessuna costante "distanza considerevole".

Se (c) è falsa, il colpo **non** si intercetta e il lanciatore diventa un bersaglio prioritario (L2).

**L2 — Priorità di bersaglio (numero di armi).** Nella scelta del bersaglio di un tiratore AD, un
candidato che **ha lanciato un'arma A2G contro la forza del tiratore** ed è entro la portata del
tiratore passa davanti a ogni altro. La chiave di `_schedule_next` acquista un primo elemento di priorità, e
per i bersagli prioritari la copertura (`_engaged_shooters`) **non** disperde più il fuoco: tutti gli
AD a portata si concentrano sul lanciatore (è il "massimo numero di armi"). La dimensione della salva
resta quella della fire control (nessuna nuova costante).

**L3 — Priorità di tempo (prelazione).** Quando una forza subisce il lancio di una salva A2G, i suoi
tiratori AD che hanno il lanciatore a portata **ridecidono subito**: un lancio già schedulato su un
bersaglio non prioritario viene annullato (contatore di generazione sul lancio schedulato, stesso
schema di annullamento già usato in `_on_launch`), e il nuovo tiro rispetta comunque i tempi di
reazione del profilo (`min_fire_time`), che non si saltano.

**Nebbia di guerra.** Il lanciatore è bersaglio prioritario solo se è un **candidato** del tiratore,
cioè già rilevato: il lancio non rivela da solo il lanciatore (decisione Q5 sotto). Con V_I di
norma dentro la portata dei sensori, il caso tipico (lanciatore a tiro) è già rilevato.

### 7.4 Esiti attesi (da verificare con la riproduzione, non ancora misurati)

| Caso | Oggi | Con D + F + L |
|---|---|---|
| 4 A-10 contro Strela-10 (V_I 5 km), Maverick lanciati a ~16 km, sorvolo | lo Strela spende 8 missili sui Maverick, 0 salve sugli A-10 | Maverick lanciati fuori zona ma 9M37 non `Anti_Missile` → nessuna intercettazione; A-10 a 5 km → bersagli prioritari, lo Strela spara i suoi 8 missili sugli A-10 |
| stesso, standoff (A-10 mai sotto i 5 km) | 8 intercettazioni | 0 intercettazioni, 0 salve: lo Strela conserva gli 8 missili (plausibile per uno SHORAD IR) |
| Buk (V_I ~30 km) nella stessa forza, A-10 a 16 km | il Buk spende missili sui Maverick | Maverick lanciati **dentro** V_I del Buk → non intercettati dal Buk; A-10 bersaglio prioritario del Buk |
| Kh-59 lanciato a 100 km su una forza con Buk/Tor | intercettazione | lancio fuori zona e arma capace → intercettazione legittima; il lanciatore non è raggiungibile |

Nota: dopo A5 l'A-10 preferisce la Mk-82AIR al Maverick. Prima di tarare qualunque cosa la
riproduzione del §1.1 va rifatta sul motore attuale, e diventa lo scenario di test persistente.

### 7.5 Mappa d'impatto

| Componente | Modifica |
|---|---|
| `Context.GROUND_WEAPON_TASK` | + `Anti_Missile` |
| `Asset/Ground_Weapon_Data.py` | task `Anti_Missile` sulle armi idonee fra le 16 Anti_Air (S-68, AZP-23, M61, Oerlikon-KDA, 2A38M; 9M311, 9M31, MIM-72, 9M33, 9M37, Roland, 9M331, FIM-92, 3M9, 9M38, 5V55R): **proposta di dati con fonti da approvare**, stile B1 |
| `Asset/Ship_Weapon_Data.py` | già 12 armi `Anti_Missile`; da verificare le navi con armi Anti_Air senza il task, che smetterebbero di intercettare |
| `Asset/Mobile.interceptor_weapons_from_registry` | filtro `Anti_Missile`: punto unico, capacità e scorta degli intercettori lo seguono |
| `Block/Military.salvo_interceptors` | seleziona gli asset con almeno un'arma intercettrice (non più "ogni ThreatAA"); ordine F fra asset: prima gli intercettori a soli cannoni, poi per id |
| `Logic/Engagement_Resolver._on_resolve` | allocazione **per salva** con l'idoneità L1; `_capacity` diventa un tetto, `SalvoResolution.capacity` ridocumentata (campo invariato) |
| `Logic/Engagement_Resolver` (`Salvo`, `_schedule_next`, `_on_launch`) | `Salvo.launch_position` (campo opzionale, additivo); chiave di priorità L2; prelazione L3 |
| Test | `Test_Engagement_Resolver` (intercettazioni dei SAM), S10-S18 (esiti), nuovo scenario Strela/Buk persistente |

Contratto pubblico: `ShotSpec`, `InterceptionEvent`, `resolve_engagement` invariati; `Salvo` e
`SalvoResolution` cambiano solo in modo additivo o nella documentazione. Nessuna estrazione casuale
nuova: il determinismo non cambia.

### 7.6 Decisioni richieste

- **Q1 — Zona per intercettore o per forza?** (c) si valuta sul V_I **del singolo intercettore**
  (raccomandato: un Tor lontano dal lanciatore intercetta anche se il Buk della stessa forza ha il
  lanciatore a tiro) o sull'unione dei V_I della forza (la difesa come sistema unico)?
- **Q2 — Colpi lanciati dentro la zona**: mai intercettati (lettura letterale della regola 2,
  raccomandata), oppure intercettabili con la capacità che avanza dopo aver servito il lanciatore?
- **Q3 — "Numero di armi"**: concentrazione di tutti gli AD a portata sul lanciatore con la salva
  normale (raccomandato, nessuna costante), oppure anche salva maggiorata (es. 2 missili, tiro
  "shoot-shoot") con una costante stimata?
- **Q4 — Prelazione L3**: sì (raccomandato: è la "priorità di tempo"), o solo priorità alla
  prossima decisione naturale del tiratore (più semplice, meno fedele)?
- **Q5 — Rilevamento del lanciatore**: il lanciatore deve essere già rilevato (raccomandato, coerente
  con la nebbia di guerra), o il lancio lo rivela automaticamente alla forza bersaglio?
- **Q6 — Granularità di D**: un solo task `Anti_Missile` per tutte le armi autonome (raccomandato
  ora), o capacità distinte per classe (missile da crociera, ASM, bomba planante, drone)?

Ordine di lavoro proposto: (1) proposta di dati `Anti_Missile` da approvare; (2) D + F (filtro e
ordinamento); (3) riproduzione aggiornata come test persistente; (4) L1 nel risolutore; (5) L2 + L3.

### 7.7 Decisioni dell'utente (2026-09-28)

**APPROVATA**: D + F + L, con l'ordine di lavoro del §7.6.
- **Q1**: zona valutata sul V_I del **singolo intercettore**.
- **Q2**: i colpi lanciati dentro la zona **non si intercettano mai**.
- **Q3**: concentrazione sul lanciatore con la salva normale, **con una precisazione**: in presenza di
  più aerei nemici, una difesa fatta di più unità indipendenti deve **distribuire** il lavoro
  d'intercettazione fra i lanciatori, e la distribuzione **richiede tempo** (valutazione e
  assegnazione). Conseguenze sul disegno di L2/L3:
  - L2 diventa: la **classe di priorità** è il primo elemento della chiave di `_schedule_next`, e
    **dentro** la classe prioritaria resta la copertura (`_engaged_shooters`). Con un solo lanciatore
    a tiro tutti gli AD ci si concentrano (nessun altro bersaglio prioritario); con più lanciatori il
    round-robin esistente li ripartisce. Non si disattiva più la copertura per i bersagli
    prioritari, come proposto al §7.3.
  - L3: la ridecisione dopo un lancio nemico non è istantanea. Al tempo di reazione del tiratore si
    somma un **tempo di valutazione e assegnazione** del lavoro fra unità. Va dichiarato come stima,
    e verificato prima di introdurre una costante nuova: se i profili di reazione esistenti
    (`Reaction_Profile`, fasi rilevamento → decisione → fuoco) coprono già questa fase, la si
    riusa. Dipende anche dal legame C2 fra le unità: unità indipendenti senza rete comune sono più
    lente di una batteria integrata. Da tenere coerente con la Fase 0 della gerarchia C2.
- **Q4**: prelazione L3 **sì** (con il tempo di assegnazione di Q3).
- **Q5**: il lanciatore deve essere **già rilevato**.
- **Q6**: **un solo** task `Anti_Missile`.

### 7.8 Passo 3: scenario persistente S19 (2026-09-28)

`Test/Test_Session_Scenarios_S19_Air_Defence.py`: 3 BMP-2 + una difesa, 1-4 A-10C con i soli
AGM-65D (il criterio Pk/costo preferirebbe la Mk-82AIR, non intercettabile: il filtro fa le veci di
A4), dottrina ad oltranza. Esiti qualitativi verificati sul motore attuale (D + F):

| Variante | Esito |
|---|---|
| Strela-10, sorvolo | 0 intercettazioni; lo Strela spara i suoi missili sugli A-10C e ne abbatte |
| Strela-10, standoff | 0 intercettazioni, 0 lanci: lo Strela conserva gli 8 missili |
| Tor arretrato (lanci a 15-19 km, fuori dai 12 km) | intercetta: bersagli legittimi per L1 |
| Tor avanzato, A-10C solo sui BMP (lanci a ~9,5 km, dentro) | spara ai lanciatori, 0 intercettazioni |

**Scoperta**: nell'ultimo caso il motore rispetta già la regola L, ma **per tempistica e non per
costruzione**. Il lanciatore entra nei 12 km prima che i suoi Maverick arrivino, e il Tor spende gli
8 missili su di lui. Inoltre la portata del Maverick (15 km) supera la zona del Tor (12 km): un Tor
raggiungibile viene attaccato da fuori zona, e le sue intercettazioni sono legittime. Il caso che
solo L1 distingue (intercettore con scorta in avanzo e lancio da dentro la zona) non si ottiene in
modo stabile negli scenari: sarà un test unitario a geometria controllata del risolutore (passo 4).
Una misura su 16 seed ha trovato un solo caso di intercettazione *prima* del tiro del Tor, dovuta al
fatto che l'intercettazione non richiede tempo di reazione (§5.4): è materia di L3 e della nebbia di
guerra, non di L1.

### 7.9 Passo 4: L1 nel risolutore (2026-09-28)

`Engagement_Resolver._on_resolve` alloca le intercettazioni **per salva**: salve nell'ordine
(impatto, salva), intercettori nell'ordine F, ognuno fino a min(canali, scorta) per evento. Un
intercettore può fermare i colpi di una salva solo se il punto di lancio (posizione del lanciatore
all'istante `t_launch`, dai tratti di rotta o dalla posizione ferma) è fuori dal suo V_I
(`Mobile.air_defense_volume`, cilindro: raggio orizzontale e fascia di quota; il bordo conta come
dentro). Senza volume o senza posizioni la regola non si applica (dato mancante = non modellato).
Senza vincoli il risultato coincide con l'allocazione sul totale di prima: nessuno scenario
esistente ha cambiato esito. `SalvoResolution.capacity` è ora un tetto.

Test: `Test_Engagement_Resolver.TestLauncherInsideInterceptionZone` (7 casi a geometria controllata:
fuori zona, dentro, bordo, sopra il tetto, zona per intercettore (Q1), senza dato, colpi non
intercettabili). Suite 3663 OK.

### 7.10 Passo 5: L2 + L3 nel risolutore (2026-09-28)

- **L2** (`_schedule_next`): se fra i candidati ci sono aerei che hanno lanciato armi aria-superficie
  contro la forza del tiratore e sono a portata al loro istante di tiro, si sceglie solo fra loro,
  con la copertura esistente: più lanciatori vengono ripartiti fra le difese, uno solo le concentra.
  La salva resta quella della fire control (Q3, nessuna costante).
- **L3** (`_register_launcher`, `_on_decide`): alla prima salva aria-superficie di un aereo contro
  una forza, i tiratori di quella forza che lo hanno a portata e non sono già su un lanciatore
  annullano il lancio programmato (contatore di generazione) e **ridecidono dopo il proprio
  `refire_interval`** (VAL + COM + ATT del profilo di reazione): è il tempo di valutazione e
  assegnazione chiesto al Q3, senza costanti nuove. La decisione è presa alla fine di quel tempo,
  con i lanciatori noti allora: nella prima stesura si ridecideva subito, e due lanciatori
  simultanei finivano entrambi sotto il fuoco delle stesse difese invece di essere ripartiti (un
  test lo ha mostrato).
- Q5: il lanciatore dev'essere un candidato del tiratore, cioè già rilevato.
- Test: `Test_Engagement_Resolver.TestLauncherPriority` (premessa senza lanciatori, prelazione del
  primo tiro, priorità sulle decisioni successive, concentrazione su un lanciatore, ripartizione su
  due). Nessuno scenario esistente ha cambiato esito qualitativo. Suite 3668 OK.
- Limite: il legame C2 fra le unità (una batteria integrata assegna più in fretta di unità
  indipendenti) non è modellato: ogni tiratore usa il proprio profilo. Da riprendere con la Fase 0
  della gerarchia C2.
