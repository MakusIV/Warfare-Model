# Proposta: allocazione dei missili dei SAM puri fra intercettazione e tiro offensivo

**Stato**: PROPOSTA, in attesa di scelta dell'utente (2026-09-25). Nessun file del motore modificato.
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
3. **Disingaggio alla prima perdita**: con 4 asset, una perdita dà shock 0.25 ≥ 0.20, e la forza rompe
   il contatto al primo impatto. Per forze piccole la soglia di shock è quasi un interruttore.
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
