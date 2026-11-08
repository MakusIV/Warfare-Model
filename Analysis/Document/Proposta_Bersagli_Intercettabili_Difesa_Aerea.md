# Proposta: quali colpi una difesa aerea puo' considerare bersagli (BI) — piano di revisione del DES

**Stato: scelte utente registrate il 2026-11-07. TUTTE le decisioni BI-1..BI-12 prese** dall'utente il 2026-11-07
(§4): tutte come raccomandato, tranne **BI-6 = (a) con il Maverick (famiglia AGM-65) fisso "piccolo"** (`ad_detectable`
False contro ogni difesa, criterio esteso agli altri missili della stessa taglia) e **BI-9 confermata dopo la
spiegazione di W1** (§3.2); **BI-11**: prima si esegue questa Proposta, poi si ripropone FP-5 con esempi (superata: FP-5 decisa il 2026-11-08,
opzione (d); §4, BI-11); **BI-12 =
(a)**: il criterio di dimensione vale **solo per le difese navali**, per le terrestri contano solo le categorie
(cruise/balistici) (§4.12, limite dichiarato [S]). Lo scenario nuovo e' rinominato **S35-ADTGT** (S34
e' gia' riservato a `S34-BAND` della Proposta VA, §5.4). Sonda di sola lettura **B-0 eseguita** il 2026-11-07 sul
ProArt (§1.8). Nessun file di codice o di test
modificato; scritti solo questo documento, lo script e il LEGGIMI della sonda in
`Analysis/Document/Rapporti/Sonde_Bersagli_Intercettabili/` e due ritocchi a
`Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (allora FP-4 decisa, FP-5 sospesa; dal 2026-11-08 tutte le
decisioni FP-1..FP-10 sono prese, FP-5 = (d), e la Proposta FP e' riscritta e riletta, commit `8c440dba`, non ancora
eseguita).
- **Blocco 0 (ricerca dati) ESEGUITO e approvato il 2026-11-07**: `Proposta_Dati_Bersagli_Intercettabili.md` (decisioni
  D1-D6 di quel documento; metro del Maverick: diametro <= 304,8 mm **e** massa <= 304 kg, lunghezza esclusa; valori
  per il blocco 1 nel suo §10.2). Allineati qui §2.2, §2.3, §2.5, BI-2 e BI-7 (note), §5.0-§5.2 (test 5), §6.1, §7,
  §8; nessuna decisione BI-1..BI-12 cambiata.
- **Blocchi 1 e 2 ESEGUITI e mergiati** (merge `a74d7505` e `4803424b`, `des-developer`; suite 4829).
- **Blocco 3 (2026-11-08)**: riferimenti di §5.0, §5.4, §5.5 riverificati sul checkout dopo il merge `4803424b`; la
  verifica aveva trovato due attese contraddette dal codice e cinque parametri non fissati (P-1..P-7). **L'utente li ha
  decisi tutti il 2026-11-08** (§5.4.1): nave delle varianti navali = `FF 1135M Rezky` (P-1 (a)), sensore `sea`
  dichiarato di test sull'A-10C (P-2 (a)), asserzione 2 = "meno AGM-65D lanciati da acceso" (P-3 (a)), 15 test (P-4
  (b)), `land_cruise` = configurazione della sonda S-b (P-5 (a)), granularita' per seme/totale e asserzione 11 (P-6),
  nomi dei seed (P-7). §5.4 e' riscritto di conseguenza con il **file di test completo** (§5.4.3), gia' eseguito
  dall'analista fuori dal repo sul checkout attuale: 15 test OK, 32 chiavi della fotografia corrette [V]. **Il blocco 3 e'
  eseguibile.**
- **Esecutore previsto**: blocchi 1-2 `des-developer` (eseguiti); **blocco 3 `oc-developer`** (DeepSeek V4 Pro,
  OpenCode; scelta dell'utente del 2026-11-08), sul branch `ai/oc-bi-blocco3`: il blocco 3 non tocca il motore, solo un
  file di test nuovo e una riga (piu' la docstring) di `Scenario_Baseline`. L'esecutore segue §5 cosi' com'e'; se il
  codice reale non corrisponde (righe, firme, esiti) si ferma e riferisce. Il blocco 0 (ricerca dati) **non** e'
  dell'esecutore: e' una ricerca con fonti (§5.1).

**Convenzioni**: **[V]** = verificato leggendo il codice (`file:riga`, checkout del 2026-11-07, HEAD `b20e39cf` piu' il
working tree) o eseguendolo; **[I]** = ipotesi o conoscenza generale, **non** verificata nel repository ne' su fonti in
questa sessione; **[S]** = stima o scelta di progetto, mai dato tarato. Percorsi di codice relativi a
`Code/Dynamic_War_Manager/Source/`. Sonde **B-0, B-1**; decisioni **BI-1, BI-2, ...**.

## Regola dell'utente (2026-11-07, vincolante; riportata nella sostanza)

Una difesa antiaerea (SAM o AAA) puo' considerare un **missile** come bersaglio **solo** se:
1. appartiene alle categorie dei missili **BALISTICI** e/o **CRUISE**, **indipendentemente da chi lo lancia** (aerei, navi,
   postazioni, veicoli terrestri), e/o
2. le sue **dimensioni** sono tali da poter essere rilevato dai sensori della difesa: traccia radar (RCS) comparabile a
   quella di un aereo, di un missile cruise o di un missile balistico.

I missili che non rientrano in queste categorie **non** sono bersagli. Quindi:
- **tutti** i missili **A2G** (aria-superficie) lanciati da cacciabombardieri e aerei d'attacco sono **esclusi** dai
  bersagli dei SAM/AAA **terrestri**;
- i missili **A2S** (aria-nave) **devono** essere bersagli dei sistemi antiaerei **navali** se le loro dimensioni sono
  compatibili con i sensori navali (riferimento: un missile balistico/cruise di dati noti);
- **tutte le bombe e tutti i razzi** non possono essere bersagli dei sistemi di difesa aerea terrestri e navali;
- il riferimento di dimensione "rilevabile" e' un missile balistico/cruise la cui rilevabilita' per un sistema
  antiaereo di prestazioni medie sia nota.

## Glossario delle sigle

| Sigla | Significato | Fonte / verifica |
|---|---|---|
| DES | *Discrete Event Simulation*: il motore delle sessioni virtuali, a coda di eventi | `Logic/Session_Simulator.py`, `Logic/Engagement_Resolver.py:1-64` [V] |
| AD | *Air Defence*: difesa aerea (SAM, AAA, CIWS) | uso del codice, es. "armi AD" `Logic/Engagement_Resolver.py:179` [V] |
| SAM | *Surface-to-Air Missile*: missile superficie-aria (es. Tor, Buk, SM-2) | [I] |
| AAA | *Anti-Aircraft Artillery*: cannoni contraerei (es. Gepard, Shilka) | [I] |
| CIWS | *Close-In Weapon System*: cannone navale antimissile a tiro rapidissimo (Phalanx, AK-630, Type-730) | `Asset/Ship_Weapon_Data.py`, categoria `CIWS` [V] |
| A2G / A2S / A2A | arma aria-suolo / aria-nave / aria-aria | uso dell'utente; nei registri: `MISSILES_ASM` con task `Strike`/`SEAD`/`Anti_Ship`, `MISSILES_AAM` con task `A2A` [V, §1.5] |
| ASM / AAM | *Air-to-Surface Missile* / *Air-to-Air Missile*: le due categorie di missili aerei del registro | `Asset/Aircraft_Weapon_Data.py`, `AIR_WEAPONS` [V] |
| ATGM | *Anti-Tank Guided Missile*: missile anticarro (Kornet, TOW, Hellfire) | registro terrestre `MISSILES` con task `Anti_Tank` [V] |
| ARM | *Anti-Radiation Missile*: missile antiradar (AGM-88 HARM, Kh-58, Kh-31P) | registro aereo, task `SEAD` [V] |
| MLRS / C-RAM | lanciarazzi multiplo / *Counter Rocket, Artillery and Mortar* (difesa contro razzi e proietti) | [I] |
| RCS | *Radar Cross Section*: superficie equivalente radar [m^2], quanto un oggetto "si vede" al radar | **nessun campo nei registri** [V, §1.5] |
| Pd / Pk | probabilita' di rilevamento / di distruzione | `Logic/Engagement_Resolver.py:14-20` [V] |
| V_I | volume d'intercettazione di un asset AD: cilindro di `Mobile.air_defense_volume` | `Logic/Engagement_Resolver.py:3142-3160` [V] |
| Regola D | intercetta munizioni solo un'arma AD con task `Anti_Missile` | `Asset/Mobile.py:203-208`, `:1112-1117` [V] |
| Regola F | ordine di consumo: prima gli intercettori a soli cannoni, poi per id | `Logic/Engagement_Resolver.py:2052` [V] |
| L1 | un colpo lanciato **dentro** il V_I dell'intercettore non si intercetta mai | `_may_intercept`, `Logic/Engagement_Resolver.py:3162-3185` [V] |
| L2 / L3 | priorita' di bersaglio e prelazione sul lanciatore di armi aria-superficie | `Logic/Engagement_Resolver.py:3106-3110`, `:2886` [V] |
| R-INT | intercettazione solo con traccia del colpo e tempo di reagire; "lancio visto" se l'intercettore aveva gia' rilevato il lanciatore | `_in_time`, `Logic/Engagement_Resolver.py:3250-3274` [V] |
| R1 / Hughes | saturazione per salva: i primi N colpi intercettabili sono fermati, il resto arriva al danno (modello a salve di Hughes) | `Logic/Engagement_Resolver.py:32-55`, `Block/Military.py:717-771` [V] |
| FP / FP-5 | `Proposta_Finestre_Per_Passaggio_Portata_Propria.md`; FP-5 = istante di rilevamento usato da R-INT (allora SOSPESA; DECISA il 2026-11-08, opzione (d)) | quel documento, §2.6 |
| D-5 | Pd dipendente dalla permanenza nel volume, interruttore `D5_DWELL_TIME` (spento) | `Logic/Engagement_Resolver.py:522-529` [V 2026-11-08, dopo il merge `4803424b`] |
| VA | `Proposta_Allineamento_Volumi_DES_Pianificatore.md` (sfera del DES contro cilindro del pianificatore) | quel documento |
| BI | questa Proposta: "bersagli intercettabili"; decisioni BI-1..BI-12, sonde B-0/B-1 | questo documento |

**Ruoli** (usati in tutte le tabelle delle decisioni):

| Ruolo | Che cos'e' | Esempio fisso usato sotto |
|---|---|---|
| **lanciatore** | chi spara il colpo (aereo, nave, veicolo) | un A-10C con AGM-65D Maverick |
| **colpo** | il missile/bomba/razzo in volo, candidato a essere intercettato | 2 Maverick di una salva (`SALVO_ROUNDS['missile'] = 2`, `Logic/Fire_Control.py:240` [V]) |
| **bersaglio dell'attacco** | l'unita' contro cui e' lanciato il colpo | un BMP-2 della forza Red |
| **intercettore** | asset AD della forza (o del dominio di coordinamento) del bersaglio dell'attacco che puo' fermare il colpo | un Tor (9K331) della stessa forza, arma 9M331 con task `Anti_Missile` |
| **osservatore** | chi rileva; per R-INT e' lo stesso intercettore (rilevamento per asset) | il Tor |
| **bersaglio del rilevamento** | chi viene rilevato; per R-INT e' il **lanciatore** (se il Tor ha gia' rilevato l'A-10C, "vede il lancio") | l'A-10C |

---

## 0. Sintesi

**Oggi** [V] ogni missile (di qualunque registro: SAM, AAM, ASM, ATGM, antinave) e ogni bomba guidata e' "intercettabile"
(`Logic/Fire_Control.py:763-768`); bombe a caduta libera, razzi, cannoni e siluri no. Intercettano solo veicoli e navi
con un'arma `Anti_Missile` (regola D). Nessun campo dei registri dice "balistico" o "cruise", nessuno da' l'RCS; i
missili aerei non hanno nemmeno diametro o lunghezza. Il motore quindi fa fermare a un Tor i Maverick degli A-10C
(S19AD `tor_rear`), cosa che la regola nuova esclude.

| Tema | Decisione dell'utente (2026-11-07) | Effetto sulla fotografia |
|---|---|---|
| Criterio (BI-1) | **categoria della munizione**, con un flag di **dimensione compatibile** (`ad_detectable`) per le difese navali | — |
| Missili piccoli (BI-6) | uso A2S (aria-nave): bersaglio dei navali ogni missile `ad_detectable`; **Maverick (AGM-65D/K, RB-75T) fisso `ad_detectable` False** contro ogni difesa; gli altri missili della stessa taglia valutati con lo stesso metro (blocco 0) | — |
| Dove si decide (BI-9) | la **fire control** (chi conosce l'arma) dichiara in `ShotSpec` i domini AD che possono intercettare il colpo (`intercept_domains`); il **risolutore** filtra l'intercettore per dominio (terrestre/navale), dietro l'interruttore `Engagement_Resolver.BI_AD_TARGET_RULE = False` | spento: **1009 identiche** |
| Terrestre/navale (BI-5) | per **classe dell'intercettore** (`Ship` = navale, ogni altro = terrestre) | — |
| Armi non a registro (BI-8) | comportamento precedente (`test:*`, `weapon=None`) | — |
| Acceso (sonda B-1 dopo il blocco 2) | cambiano solo le esecuzioni in cui un colpo **escluso** e' stato fermato | **6** (S19AD `tor_rear`, semi 0-5) con BI-8 (a); **8** (piu' S2 `sead` 0 e 6) con BI-8 (b) |
| Scenario (BI-10) | **S35-ADTGT** nuovo (S34 e' di VA): terrestre con Maverick, terrestre con cruise, navale con antinave, **navale con Maverick (caso "non fermato")**, interruttore spento/acceso: 4 x 2 x 4 semi; nave delle varianti navali `FF 1135M Rezky` (P-1 del 2026-11-08, §5.4.1) | **+32 nuove** |
| Ordine (BI-11) | prima questa Proposta, poi ripresa di FP-5 con esempi (superata: FP-5 decisa il 2026-11-08, (d); ordine attuale BI blocchi 3-4 -> VA blocchi 1-2 -> FP blocchi 1-2); ordine dei file con VA e FP in §6 | — |

**Esito della sonda B-0** (§1.8, numeri letti dal log): 1029 esecuzioni, confronto invariato (0 DIFF); 397 colpi
fermati in **16** esecuzioni (S6 4, S16 4, S19AD 6, S2 2); l'unico missile **dei registri** fermato e' l'AGM-65D (36
colpi, Tor, S19AD `tor_rear`); gli altri sono armi della tabella di test (`test:anti_ship` 351 colpi fermati da una nave,
`test:anti_radiation` 10 da un Buk). Nessun AAM, SAM, ATGM, bomba guidata o razzo fermato.

**Dimensione stimata** [S] (aggiornata dopo le scelte): blocco 0 ricerca dati (nessun codice; eseguito); blocco 1 ~110 righe di
dati nei registri (classe, flag, dimensioni di supporto dove trovate) + ~90 di test (6 test); blocco 2 ~120 righe di
codice + ~320 di test (circa 21 test; eseguito: 28); blocco 3 ~290 righe di test (**15 test**, file completo in §5.4.3)
+ 3 righe della tabella della fotografia e ~6 di docstring, **32 esecuzioni nuove**; blocco 4 documenti.

---

## 1. Problema e comportamento attuale

### 1.1 La catena d'intercettazione oggi [V]

Per ogni evento-salva contro una forza (`_on_resolve`, `Logic/Engagement_Resolver.py:3276-3420`):
1. si contano i colpi intercettabili, `interceptable = sum(s.rounds ... if s.spec.interceptable)` (`:3291`);
2. gli intercettori sono quelli di **tutte** le forze del dominio di coordinamento della forza colpita
   (`self.domain_interceptors.get(domain, [])`, `:3300-3301`), costruiti da `_interceptors_of` (`:2033-2054`) a
   partire da `salvo_interceptors()` della forza;
3. disponibilita' per intercettore = `min(canali, scorta)` (`:3325-3334`): Hughes/R1, un canale ferma un colpo per
   evento (Pk dell'intercettore = 1 per canale, ipotesi dichiarata ottimistica, `Block/Military.py:752-756`);
4. ciclo per salva nell'ordine (impatto, salva) (`:3338-3358`): una salva con `spec.interceptable` False e' saltata
   (`:3339-3340`); per ogni intercettore nell'ordine F si richiede canale libero, **L1** (`_may_intercept`) e **R-INT**
   (`_in_time`) (`:3350`), poi `take = min(liberi, residui)`;
5. ogni intercettazione consuma la scorta dell'intercettore e produce un `InterceptionEvent` per arma
   (`:3373-3382`; tipo a `:748-779`); i colpi non fermati arrivano al danno, un'estrazione RNG per colpo (`:3384-3407`).

Nessuna estrazione casuale nelle fasi 1-5 tranne il danno: L1 e R-INT sono deterministici
(`Proposta_Intercettazione_Reazione.md` §7 Q2).

### 1.2 Chi decide che un colpo e' "intercettabile": la fire control [V]

- `ShotSpec.interceptable` (`Logic/Engagement_Resolver.py:597-599`, campo `:614`, default False): "La decide chi conosce
  l'arma (il chiamante), non il risolutore".
- La fire control dei registri lo calcola in `shot_spec_for` (`Logic/Fire_Control.py:763-768`) dal solo **genere**
  dell'arma (`kind`):

      if kind == 'missile':  interceptable = True
      elif kind == 'bomb':   interceptable = weapon.data.get('type') == 'Guided bombs'
      else:                  interceptable = False

- `kind` viene dalla categoria del registro (`_KIND_BY_TYPE`, `Logic/Fire_Control.py:301-310`; assegnato a
  `_Weapon.kind`, `:365`):

| Registro (dominio del lanciatore) | Categoria | `kind` | Intercettabile oggi |
|---|---|---|---|
| terrestre (`GROUND_WEAPONS`) | `MISSILES` (ATGM **e** SAM) | missile | **si'** |
| terrestre | `ROCKETS` (Grad, Uragan, Smerch, MLRS 227 mm) | rocket | no |
| terrestre | `CANNONS`, `AUTO_CANNONS`, `AA_CANNONS`, `ARTILLERY`, `MORTARS`, `MACHINE_GUNS`, `GRENADE_LAUNCHERS` | gun | no |
| navale (`SHIP_WEAPONS`) | `MISSILES_SAM`, `MISSILES_ASM` (antinave, Tomahawk) | missile | **si'** |
| navale | `MISSILES_TORPEDO` | torpedo | no |
| navale | `GUNS`, `CIWS` | gun | no |
| aereo (`AIR_WEAPONS`) | `MISSILES_AAM`, `MISSILES_ASM` (ogni A2G, ARM, antinave, cruise) | missile | **si'** |
| aereo | `BOMBS` con `type == 'Guided bombs'` (GBU-10/12/16/24/27, KAB-500/1500, LS-6) | bomb | **si'** |
| aereo | `BOMBS` `type` 'Bombs' o 'Cluster bombs' | bomb | no |
| aereo | `ROCKETS`, `CANNONS`, `MACHINE_GUNS` | rocket / gun | no |

  Docstring coerente: `Logic/Fire_Control.py:129-131`. Le "difese di salva" sono SAM/cannoni AA "che non intercettano
  un siluro".
- **Fire control di test** (`Test/Scenario_Fixtures.py:800-827`): `test:agm` (aria-superficie), `test:anti_radiation`
  e `test:anti_ship` hanno `interceptable=True`; `test:bomb` False; le altre (fuoco diretto, artiglieria, SAM, AAA, AAM)
  il default False. Usate dalla tabella di riferimento (`:832-849`) degli scenari S1-S18. Queste armi **non** sono nei
  registri.

**Risposte alle domande del compito** [V]: una **bomba** a caduta libera no, una **bomba guidata** si'; un **razzo**
no (aereo o MLRS); un **cannoncino** no (proietti e raffiche: `kind` 'gun'); un **ATGM** si'; un **AAM** o un **SAM**
si' (ma un aereo non ha mai intercettori, §1.3: lo diventano solo se il dominio del bersaglio contiene veicoli o navi
con armi `Anti_Missile`); un **siluro** no.

### 1.3 Chi intercetta: regola D [V]

- `Military.salvo_interceptors` (`Block/Military.py:652-715`): solo asset `Vehicle` o `Ship` operativi (`:682-685`) con
  `interceptor_capability()` True; capacita' None (modello ignoto, stub) ricade sulla vecchia regola "esiste una
  `ThreatAA`" (`:693-696`). Gli aerei **non** intercettano mai.
- `Mobile.interceptor_weapons_from_registry` (`Asset/Mobile.py:1059-1129`): tipi `AA_CANNONS`/`MISSILES` per i veicoli,
  `MISSILES_SAM`/`CIWS` per le navi (`:199-201`), con quote e task `Anti_Air` **e** `Anti_Missile` (`:1112-1117`).
- Armi con `Anti_Missile` (eseguendo i registri il 2026-11-07): terrestri 9M311 e 2A38M (Tunguska), 9M331 (Tor), 9M38
  (Buk), 5V55R (S-300PS), Oerlikon-KDA-35mm (Gepard); navali ESSM, Sea Sparrow, SM-2, SM-2ER, SA-N-9, S-300F, HHQ-7,
  HHQ-9, HHQ-16 e i CIWS Phalanx, AK-630, Type-730. Coincide con `Proposta_Dati_Anti_Missile.md` §1-§2.
- La regola D dice **chi puo'** intercettare; la regola nuova dice **che cosa** si puo' intercettare. Sono ortogonali:
  la regola nuova non tocca D.

### 1.4 Contabilita' delle scorte e degli eventi [V]

- La scorta di intercettori e' una **vista** sulle voci AD della scorta per arma (`Asset/Mobile.py:160-194`): 1 missile
  = 1 intercettazione; un cannone AD spende `ROUNDS_PER_GUN_INTERCEPT` = 100 colpi (stima dichiarata,
  `Asset/Weapon_Stores.py:58-68`). Un missile AD speso per intercettare e' lo stesso delle salve offensive.
- `InterceptionEvent` (`Logic/Engagement_Resolver.py:748-779`): intercettore, numero di intercettazioni, forza difesa,
  salve dell'evento, arma. `SalvoResolution.interceptable_rounds` (`:694-721`) conta i colpi con `spec.interceptable`.
- La fotografia (`Test/Scenario_Baseline.py:499-598`) registra eventi e conteggi di intercettazione (`:560`,
  `:566-567`, `:577-578`), danni, munizioni e scorte finali; **non** registra `SalvoResolution` ne'
  `interceptable_rounds`. Conseguenza usata dalla sonda: un'esecuzione cambia **se e solo se** almeno un colpo che la
  regola esclude e' stato **fermato** (una salva esclusa che non ha preso canali non sposta l'allocazione delle altre:
  il ciclo di `:3344-3355` non tocca `used` se `take` non avviene).

### 1.5 Registri: classificazione e dimensioni disponibili [V, eseguendo i registri il 2026-11-07]

Campi presenti (unione sulle voci della categoria):

| Categoria | N | Campi utili alla regola | Manca |
|---|---|---|---|
| aereo `MISSILES_ASM` | 44 | `type` 'ASM' (tutti), `task` (Anti_Ship 29, Strike 27, SEAD 22, Pinpoint_Strike 1), `max_speed`, `range`, `warhead` [kg], `seeker`, `weapon_param_type` (precisione/effetto) | **classe** (cruise/balistico/tattico), **diametro, lunghezza, peso, RCS** |
| aereo `MISSILES_AAM` | 42 | `type` 'AAM', `task` A2A | dimensioni, RCS |
| aereo `BOMBS` | 54 | `type` 'Bombs' 20 / 'Guided bombs' 15 / 'Cluster bombs' 19, `weight` (solo cluster), `warhead` | (non servono: mai bersagli) |
| aereo `ROCKETS` | 12 | `caliber` [mm] | (non servono) |
| aereo `CANNONS` | 15 | **2 voci con `type` 'Rockets'** (UPK-23, Gsh-23L: sono cannoni) — anomalia del registro, ininfluente qui (`kind` dalla categoria) | — |
| terrestre `MISSILES` | 26 | `task` (Anti_Tank 15, Anti_Air 11, Anti_Missile 4), `caliber` [mm, diametro: es. 9M38 400, 5V55R 508] | classe, lunghezza, RCS; **nessun missile balistico o cruise terrestre** nel registro |
| terrestre `ROCKETS` | 4 | `caliber` 122-300 mm, task Artillery | — |
| navale `MISSILES_ASM` | 8 | `task` (Anti_Ship 8, Land_Attack 1 = Tomahawk), `caliber` [mm] (Harpoon 343, Tomahawk 519, Granit 850, Moskit 760, Vulkan 880, YJ-12 500, YJ-18 540, YJ-83 360), `speed`, `guidance` | classe, lunghezza, RCS |
| navale `MISSILES_SAM` | 12 | `task` (Anti_Missile 9, Anti_Ballistic 2), `caliber` | — |

- **Nessun campo `rcs`**, **nessuna classe "ballistic"/"cruise"** in nessun registro (ricerca `rcs|RCS|cruise|ballistic`
  sui tre registri: solo commenti e la tabella descrittiva `Asset/Aircraft_Weapon_Data.py:108-143`, che chiama
  "Missili strike/anti-nave" Kh-101 e AGM-84A). Il task `Anti_Ballistic` esiste solo come capacita' degli
  **intercettori** navali S-300F e HHQ-9.
- **Nessun missile balistico** e **nessun cruise lanciato da terra** nei registri: la parte "balistici" della regola non
  ha oggi nessuna arma a cui applicarsi (la regola va scritta per il futuro, non e' provabile sulla fotografia).
- Il `caliber` dei missili terrestri e navali e' plausibilmente il diametro in mm [I: i valori coincidono con i
  diametri noti, es. Harpoon 343 mm, ma il registro non lo dichiara].
- Anomalia: **Mistral** (MANPADS aria-aria) e' fra gli `MISSILES_ASM` aerei con task Strike/Anti_Ship [V]; per la regola
  e' comunque escluso (tattico, piccolo). Da segnalare al manutentore dei registri, non si corregge qui.

Lanciatori dei missili aerei nei loadout (eseguendo `AIRCRAFT_LOADOUTS`, 2026-11-07) [V]: AGM-65D/K solo A-10C
(Attacker); AGM-88 F-15E, F-16, F/A-18C (Fighter_Bomber); Kh-58 Su-24M (Bomber), Su-25TM, Su-30, Su-34; **Kh-59** Su-30,
Su-34 (Fighter_Bomber) **e** Tu-160 (Heavy_Bomber); Kh-55 Tu-95MS; Kh-101 Tu-160; Kh-22N Tu-22M; AGM-84A F/A-18 e
S-3B; RB-15F Viggen. Senza lanciatore nei loadout: Kh-59M, KD-63/63B, KD-20, Kh-555, Kh-65, Kh-35, Kh-41, Kormoran,
Sea Eagle, RB-04E e altri (elenco nella sonda di appoggio, non versionata).

### 1.6 Il pianificatore non modella l'intercettazione delle munizioni [V]

Ricerca di `intercept` in `Logic/`: fuori dal risolutore il termine compare solo per l'intercettazione degli **aerei**
(`ThreatAA.interception_speed`, `Logic/Air_Route_Manager.py:144-256`) e per la priorita' tattica
(`Logic/Tactical_Evaluation.py:552-868`). `Weapon_Delivery` e `Air_Resources_Assigner` non stimano la sopravvivenza dei
colpi. La regola nuova e' quindi **solo DES**: nessun cambio al pianificatore, nessun disallineamento nuovo.

### 1.7 Cosa dice oggi il manuale [V]

- `Manuale_Motore_DES/05_Strato2_Risolutore_Ingaggio.md:179` e `:900`: `interceptable` True per "missili, bombe
  guidate"; `§4.24` (`:1612-1736`): regole D, F, L1, L2, L3 e la regola dell'utente del 2026-09-28 "sono bersagli
  legittimi **solo** le armi autonome lanciate a distanza considerevole" (`:1620-1622`), con le "bombe plananti" fra le
  armi autonome (`:1626-1627`); diagramma D24 (`:1720-1736`).
- `10_Limiti_Estensioni_Divergenze.md:282`: R-INT con "RCS del colpo non modellata".
- Da cambiare con la regola (blocco 4): §4.24 (nuova sottosezione "Che cosa e' un bersaglio", regola dell'utente
  2026-11-07, che **restringe** la regola 2 del 2026-09-28), tabella `ShotSpec` (campo nuovo), D24 (nodo nuovo prima di
  L1), capitolo 9 (limiti: classificazione stimata, nessun balistico a registro, dimensione come flag).

**Contrasto con le regole precedenti da far confermare** (BI-4): la regola dell'utente del 2026-09-28
(`Proposta_Regole_Allocazione_SAM.md:308-311`) e la decisione Q6 (`:407-408`, `:435`) mettevano **missili, droni e
bombe plananti** fra i bersagli legittimi; `Proposta_Dati_Anti_Missile.md:19` motiva il Tor come "progettato contro ...
bombe guidate e plananti" (fonti [T1][T2] di quel documento). La regola nuova esclude **tutte** le bombe.

### 1.8 Sonda B-0 (sola lettura) — ESEGUITA il 2026-11-07 sul ProArt

Script versionato: `Analysis/Document/Rapporti/Sonde_Bersagli_Intercettabili/probe_intercepts.py` (istruzioni, tempi e
riassunti in `LEGGIMI.md` e `b0/` della stessa cartella). Avvolge `_EngagementRun._on_resolve` **senza cambiarne il
comportamento**: legge le variabili locali al ritorno (`ordered`, `stopped`, `available`, `interceptors`) con un
profilatore, ricostruisce l'attribuzione colpo -> intercettore ripercorrendo il ciclo con le cache gia' riempite dal
motore (nessuna chiamata che estragga numeri), controlla che la ricostruzione coincida con il motore, e riesegue il
confronto con la fotografia ignorando la propria voce. Tempo: ~8 minuti sul ProArt (13:19:51-13:28:02).

**Esito (2026-11-07, ProArt)** [V: `.ai-run/sonde_bersagli/b0/log.txt`, copia in `Sonde_Bersagli_Intercettabili/b0/`]:

    compared 1029 runs: 20 difference lines (487.6 s)        -> tutte NEW S32-DWELL, 0 righe DIFF
    PROBE_RC 1
    RUNS 1029 (in fotografia 1009, nuove 20)
    TOTALS {"interceptable_rounds": 2847, "interceptable_rounds_facing_interceptors": 615, "replay_mismatch": 0,
            "resolutions": 23721, "resolutions_with_interceptors": 308, "stopped_rounds": 397}
    RUNS_WITH_STOPS 16 (in fotografia 16)
    UNITS_WITH_STOPS {"S16": 4, "S19AD": 6, "S2": 2, "S6": 4}
    CHANGED[unmodelled_as_before] 6 (in fotografia 6) UNITS {"S19AD": 6}
    CHANGED[by_role] 8 (in fotografia 8) UNITS {"S19AD": 6, "S2": 2}

Colpi fermati per arma e intercettore (totale 397):

| Colpi fermati | Lanciatore | Arma | Bersaglio | Intercettore | Esecuzioni | Con R-BI |
|---|---|---|---|---|---|---|
| 302 | nave | `test:anti_ship` (tabella di test) | nave | FSG 1241.1MP Molniya | S6-0..3 (80, 62, 80, 80) | ammessi in ogni variante (antinave contro navale) |
| 49 | aereo (Fighter) | `test:anti_ship` | nave | Molniya | S16-0..3 (6, 19, 15, 9) | ammessi |
| 36 | A-10C (Attacker) | **AGM-65D** (registro) | veicolo | **Tor** | S19AD `tor_rear`, semi 0-5 (6 ciascuno) | **esclusi** |
| 10 | aereo (Fighter) | `test:anti_radiation` | veicolo | Buk | S2-0-sead (3), S2-6-sead (7) | esclusi solo con BI-8 (b) |

Letture:
- **Esecuzioni che cambierebbero con l'interruttore acceso**: **6** con BI-8 (a) (le 6 `S19AD/S19-<0..5>/tor_rear`), **8**
  con BI-8 (b) (in piu' `S2/S2-0-sead` e `S2/S2-6-sead`). Tutte le altre 1001 (o 1003) esecuzioni della fotografia e le
  20 di S32 restano identiche anche accese (criterio di §1.4). Gli scenari dipendenti da A2G intercettati sono quindi
  **uno** con armi di registro (S19AD `tor_rear`) e **uno** con armi di test (S2 `sead`, solo se le armi di test seguono la
  regola).
- **Nessuna** intercettazione di AAM, SAM, ATGM, bombe guidate o razzi nella fotografia: i casi limite di §2.3 non vi
  compaiono (non sono nemmeno fra i colpi intercettabili arrivati su forze con intercettori: `FACING` contiene solo
  AGM-65D, `test:agm`, `test:anti_radiation`, `test:anti_ship`).
- I `test:agm` arrivati su forze con intercettori (72 colpi) non sono mai fermati: R-INT li respinge (righe
  `RINT ... geometry|late` e `seen|late`).
- **R-INT nei casi che restano**: i 351 colpi antinave fermati passano quasi tutti dal percorso **geometrico** (151 + 31
  valutazioni `geometry|ok`, 1 `seen|ok`): l'intercettore navale non "vede il lancio", scopre il colpo. Nei Maverick di
  S19AD invece prevale il lancio visto (14 `seen|ok`, 4 `geometry|ok`). Con R-BI accesa, quindi, la parte "lancio visto"
  di R-INT (quella toccata da FP-5) non e' esercitata da nessuna esecuzione della fotografia.
- `replay_mismatch` 0: la misura coincide con l'allocazione del motore.
- Le intercettazioni navali sono del **Molniya** (FSG 1241.1MP), la cui arma `Anti_Missile` e' il CIWS AK-630 (il SA-N-4
  non ha il task, §1.3) [V: registro del Molniya = P-270 x4, SA-N-4 x16, AK-176 x300, AK-630 x2; l'attribuzione per arma
  non e' nel riassunto della sonda].

---

## 2. La regola tradotta in regole operative

### 2.1 Regole operative proposte (R-BI)

Per un colpo `c` (della salva `s`) e un intercettore `i` (gia' selezionato dalla regola D):

- **R-BI-1 (classe della munizione).** Ogni arma del registro ha una **classe di munizione**: `ballistic`, `cruise`,
  `anti_ship`, `arm`, `tactical` (missili aria-superficie tattici), `atgm`, `sam`, `aam`, `guided_bomb`, `bomb`,
  `rocket`, `gun`, `torpedo`. Per bombe, razzi, cannoni, siluri, SAM, AAM e ATGM la classe si **deriva** da categoria e
  task del registro (nessun dato nuovo); per i missili aria-superficie e navali (`MISSILES_ASM`, 44 + 8 voci) e'
  **dichiarata** nel registro (dato nuovo, blocco 1).
- **R-BI-2 (dimensione).** Ogni missile puo' dichiarare `ad_detectable` (True/False): dimensione/RCS (*Radar Cross
  Section*, traccia radar) compatibile con i sensori AD (*Air Defence*, difesa aerea) rispetto al riferimento (BI-7).
  Assente: default per classe (BI-7). **Decisione BI-6 dell'utente**: la famiglia Maverick (AGM-65D, AGM-65K e RB-75T,
  versione svedese del Maverick [I]) ha `ad_detectable` **fisso False**, dichiarato esplicitamente nel registro, in ogni
  contesto (contro difese terrestri e navali); ogni altro missile di taglia pari o minore e' valutato con lo stesso metro
  (§2.5, "metro del Maverick").
- **R-BI-3 (domini AD ammessi).** Dalla classe (e dal flag) si ricava l'insieme dei domini AD che possono considerare
  il colpo un bersaglio:

| Classe | Terrestre | Navale | Nota |
|---|---|---|---|
| `ballistic` | si' | si' | lettera della regola |
| `cruise` | si' | si' | "indipendentemente da chi lo lancia" (BI-2 per i cruise dei cacciabombardieri) |
| `anti_ship` | no (non spara a terra) | **si' se `ad_detectable`** | regola A2S |
| `arm` | **no** | si' se `ad_detectable` (BI-3, BI-6) | A2G dei cacciabombardieri |
| `tactical` (Maverick, Kh-25/29, Hellfire...) | **no** | si' se `ad_detectable` (BI-6); **Maverick mai** (flag fisso False) | A2G; contro navi e' un uso A2S |
| `atgm`, `sam`, `aam` | no | no | piccoli, non balistici ne' cruise |
| `guided_bomb`, `bomb` | no | no | "tutte le bombe" (BI-4) |
| `rocket`, `gun`, `torpedo` | no | no | "tutti i razzi"; cannoni e siluri gia' oggi no |

- **R-BI-4 (filtro nel risolutore).** Con l'interruttore acceso, `i` puo' fermare `c` solo se il dominio di `i`
  (BI-5: `Ship` -> navale, altrimenti terrestre) e' fra quelli ammessi. Il controllo si aggiunge a L1 e R-INT, che non
  cambiano. Spento: nessun filtro (oggi).
- **R-BI-5 (dato mancante).** Arma non a registro (`test:*`, `weapon=None`) o fire control che non dichiara i domini:
  comportamento precedente (vale solo `interceptable`), BI-8.

### 2.2 Tabella armi -> classe -> intercettabile (classificazione PROPOSTA [S], da confermare con la ricerca, blocco 0)

**Aereo `MISSILES_ASM` (44)** — classe dichiarata nel registro:

| Classe proposta | Modelli | Terrestre | Navale | Zona d'ombra |
|---|---|---|---|---|
| `cruise` (lanciati da bombardieri) | Kh-55, Kh-101, Kh-555, Kh-65, KD-20; **KD-63, KD-63B** (solo dal bombardiere H-6 secondo GlobalSecurity, fonte unica; nessun lanciatore nei loadout [V]) | si' | si' | correzione del 2026-11-07 (Proposta dati, decisione D3.2 (a)): KD-63/KD-63B non sono lanciabili da cacciabombardieri |
| `cruise` **tattici** (anche da cacciabombardieri) | Kh-59, Kh-59M | si' (BI-2 (a)) / no (BI-2 (b)) | si' | **BI-2**: il caso vero e' il Kh-59, portato da Su-30/Su-34 e da Tu-160 [V §1.5]; il Kh-59M non ha lanciatori nei loadout [V] |
| `anti_ship` | AGM-84A, RB-04E, RB-15, RB-15F, Kormoran, Sea Eagle, Kh-22N, Kh-31A, Kh-35, Kh-41 | — | si' se `ad_detectable` | dimensione (BI-7); molti sono "cruise antinave" [I] |
| `arm` | AGM-45, AGM-88, Kh-58, Kh-25MP, Kh-25MPU, Kh-31P, LD-10 | **no** | se `ad_detectable` | **BI-3**; candidati "piccoli" con il metro del Maverick [I]: AGM-45 (Shrike), Kh-25MP/MPU; zona grigia [I]: AGM-88, Kh-58, Kh-31P, LD-10 |
| `tactical`, famiglia Maverick | AGM-65D, AGM-65K, RB-75T | **no** | **no** (`ad_detectable` fisso False, BI-6) | decisione dell'utente: "piccolo", in ogni contesto |
| `tactical`, candidati "piccoli" (ipotesi [I]/[S], da confermare con fonti nel blocco 0) | AGM-114 (Hellfire), BGM-71D (TOW), 9M114 (Shturm [I]), 9M120 e 9M120-F (Ataka [I]), Hot-3, Mistral, Kh-25ML, Kh-25MR, Kh-66, RB-05A, RB-05E | **no** | atteso **no** (taglia pari o minore del Maverick [I]), se le fonti lo confermano | il nome tra parentesi e' conoscenza generale; Brimstone, Vikhr e APKWS **non sono nei registri** [V: ricerca del 2026-11-07] (l'APKWS sarebbe comunque un razzo, mai bersaglio) |
| `tactical`, zona grigia | Kh-29L, Kh-29T, Kh-29TE | **no** | se `ad_detectable` (BI-6) | Kh-29 piu' grande del Maverick [I] (diametro ~380 mm [I]): puo' risultare True; v. incoerenza I-1 (§4.13) |

**Navale `MISSILES_ASM` (8)**: Tomahawk `cruise` (Land_Attack + Anti_Ship) -> terrestre e navale si'; Harpoon, Granit,
Moskit, Vulkan, YJ-12, YJ-18, YJ-83 `anti_ship` -> navale si' (con `ad_detectable`, presunto vero, BI-7).

**Esito del blocco 0** (2026-11-07, `Proposta_Dati_Bersagli_Intercettabili.md` §1, §5 e §10.2; prevale sulle ipotesi
della tabella sopra, che resta come traccia): classi confermate dalle fonti per tutte le 52 voci; il **Mistral** resta
`tactical` con `ad_detectable` False (anomalia del registro, decisione D2 (a) della Proposta dati); il **Kh-22N** resta
`anti_ship` (D3.1 (a)). Flag: **32 True, 20 False**. Kh-29L/T/TE, Kh-58 e Kh-31P superano l'Harpoon in diametro e
massa: `ad_detectable` **True** (D3.3 (a)); AGM-45, Kh-25ML, Kh-25MR, Kh-66, LD-10 e i candidati "piccoli" (AGM-114,
BGM-71D, 9M114, 9M120, 9M120-F, Hot-3, Mistral) **False**; in **zona grigia**, approvate dall'utente voce per voce,
AGM-88, Kh-25MP, Kh-25MPU, RB-05A, RB-05E (**False**) e il Kormoran sul bordo alto (**True**). I nomi comuni Shturm,
Ataka e Shrike sono confermati dalle fonti (bozza L2 e L4 della ricerca).

**Derivate, senza dato nuovo**: AAM aerei -> `aam`; SAM terrestri (task Anti_Air) e navali -> `sam`; ATGM terrestri
(task Anti_Tank) -> `atgm`; `BOMBS` -> `guided_bomb`/`bomb` dal `type`; `ROCKETS` aerei e terrestri -> `rocket`; armi a
canna -> `gun`; siluri -> `torpedo`. Tutte non bersagli.

### 2.3 Casi limite (richiesti dal compito)

| Caso | Oggi | Con R-BI | Note |
|---|---|---|---|
| ARM (AGM-88, Kh-58) contro un SAM terrestre | intercettabile da Tor/Buk/S-300 | **escluso** (A2G di cacciabombardiere) | nella realta' alcune difese ingaggiano gli ARM [I]; BI-3 |
| bomba guidata (GBU-12, KAB-500) | intercettabile | **esclusa** | BI-4 |
| bomba planante (LS-6; JDAM-ER non a registro) | intercettabile (`Guided bombs`) | **esclusa** | BI-4; contrasto con la regola del 2026-09-28 |
| SLAM-ER (AGM-84H), Storm Shadow, Taurus | **non a registro** [V] | sarebbero `cruise` (BI-2) | SLAM-ER e' un missile, non una bomba [I] |
| antinave da aereo (Harpoon AGM-84A, Exocet non a registro) contro nave | intercettabile | **si'** (navale, se `ad_detectable`) | regola A2S |
| antinave da nave (RGM-84, P-270) contro nave | intercettabile | **si'** | `anti_ship` navale |
| antinave lanciato da terra (batteria costiera) | nessuna batteria costiera con missili nel registro terrestre [V] | come sopra (classe del missile) | — |
| antinave da bombardiere contro bersaglio terrestre (es. Kh-22N del Tu-22M) | intercettabile | **non intercettabile da nessuno** (classe `anti_ship` non bersaglio delle difese terrestri, R-BI-3) | [I] la regola dell'utente esclude l'A2G (aria-superficie) solo per cacciabombardieri/aerei d'attacco e ammetterebbe un cruise da bombardiere. Nessun caso nella fotografia (sonda B-0). Il blocco 0 deve classificare il Kh-22N: se `cruise`, e' bersaglio dei terrestri. Nessuna decisione nuova. **Esito del blocco 0** (2026-11-07): Kh-22N `anti_ship` (Proposta dati, D3.1 (a)); il caso non puo' accadere con i registri attuali, perche' il Kh-22N ha solo la riga di efficacia `ship` e la fire control non lo usa mai contro un bersaglio terrestre [V, Proposta dati §2.2]. |
| Tomahawk da nave contro terra | intercettabile | **si'** (cruise, terrestre e navale) | — |
| cruise lanciato da terra | non a registro [V] | `cruise` | — |
| razzi MLRS (Grad, Smerch) | non intercettabili | non intercettabili | C-RAM non modellato; la regola dice mai |
| artiglieria, mortai | non intercettabili | non intercettabili | idem |
| cannoni AA (Gepard, 2A38M, CIWS) come **intercettori** | intercettano missili e bombe guidate | intercettano solo le classi ammesse | la regola riguarda il colpo, non l'arma che intercetta |
| cannoni AA contro **colpi** di cannone | no (`kind` gun) | no | — |
| difese navali contro A2S | intercettano ogni missile | solo classi ammesse e `ad_detectable` | BI-6, BI-7 |
| Maverick contro una nave (A-10C contro Arleigh Burke) | intercettabile | **mai** (flag fisso False, BI-6) | caso di prova "non fermato" di S35 (in S35 la nave e' la `FF 1135M Rezky`, non il Burke: P-1, §5.4.1) |
| ATGM (Kornet da BMP, Hellfire da elicottero) contro una forza con Tor | intercettabile | **escluso** | — |
| AAM o SAM contro un aereo di un dominio con navi/veicoli `Anti_Missile` | intercettabile in teoria (difesa di dominio, `:3293-3301`) | **escluso** | B-0: non succede in nessuna esecuzione (§1.8) |
| droni / munizioni circuitanti | non a registro come munizioni [V] | con R-BI-2 (dimensione) sarebbero bersagli | fuori perimetro |

### 2.4 "Terrestre" e "navale" (BI-5) e il dominio del bersaglio dell'attacco

Il colpo e' lanciato contro un bersaglio dell'attacco U; lo intercetta un asset del **dominio** di U (stessa forza, o
altra forza dello stesso blocco/Operazione, F4b++, `Logic/Engagement_Resolver.py:204-243`). Di norma intercettore e
bersaglio sono dello stesso dominio fisico (un Tor difende i BMP, un Arleigh Burke difende sé e il gruppo). Il caso
misto e' la **difesa di dominio**: una nave dello stesso blocco/Operazione che difende truppe costiere, o un Tor a terra
che difende un trasporto navale in porto. Le due letture divergono solo li' (BI-5).

### 2.5 Riferimento di dimensione/RCS: dati mancanti e come ottenerli (BI-7)

- **Nessun dato nel repository**: ne' RCS ne' dimensioni dei missili aerei (§1.5). I diametri dei missili navali e
  terrestri ci sono (`caliber`), le lunghezze no.
- La regola chiede un **riferimento**: "un missile balistico/cruise la cui rilevabilita' per un sistema antiaereo con
  prestazioni medie sia nota". Candidati [I, nessuna fonte consultata in questa sessione]: Harpoon (antinave subsonico,
  diametro a registro 343 mm), Tomahawk (cruise subsonico, 519 mm a registro), uno Scud (balistico tattico, non a
  registro). **Nessun valore di RCS e' riportato qui**: valori pubblicati per i missili sono spesso stime di seconda
  mano; vanno cercati con fonte e confidenza (A/M/B come in `Proposta_Dati_Anti_Missile.md`).
- Strada raccomandata (BI-7 (a)): la ricerca dati (blocco 0) produce, per ciascuno dei 52 `MISSILES_ASM` (44 aerei + 8
  navali), **classe** e **flag `ad_detectable`** (dimensione compatibile si'/no rispetto al riferimento), con fonte,
  confidenza e motivazione; dove esistono, diametro, lunghezza e peso [con fonte] come dati di supporto. Nessuna
  soglia numerica nel codice.
- Ogni valore entra nei registri con il commento `# STIMA [S]: <fonte/assunzione>`.
- **Metro del Maverick e coerenza con il riferimento Harpoon** (decisione BI-6, 2026-11-07). Due ancore, documentate
  con fonte nel blocco 0 (`Proposta_Dati_Bersagli_Intercettabili.md` §3 e §5, decisioni D1 = R1-K, cioe' metro
  sull'inviluppo della famiglia Maverick, e D4.1 (a) del 2026-11-07):
  - ancora **bassa** = famiglia Maverick fissata False dall'utente (AGM-65D, AGM-65K, RB-75T), presa come **inviluppo**:
    diametro **304,8 mm** (FAS, *Federation of American Scientists*: "1 foot") e massa **304 kg**
    (designation-systems, colonna AGM-65F/G, la cellula del K; i 306 kg di Wikipedia per il K non sono verificati con
    fonte primaria e non si usano); `ad_detectable` False in ogni contesto;
  - ancora **alta** = riferimento rilevabile (BI-7 (a): Harpoon aviolanciato AGM-84A, diametro **343 mm** (anche a
    registro navale [V]) e massa **515,25 kg** (FAS)): `ad_detectable` True.
  Regola di coerenza [S]: (1) un missile con diametro <= 304,8 mm **e** massa <= 304 kg (**non maggiore** del Maverick)
  e' False, senza eccezioni; (2) un missile con diametro >= 343 mm **e** massa >= 515,25 kg (**non minore**
  dell'Harpoon) e' True; (3) i missili fra le due ancore sono la **zona grigia**, approvata dall'utente voce per voce:
  esito AGM-88, Kh-25MP, Kh-25MPU, RB-05A, RB-05E (False) e Kormoran (True, 340 mm < 343). La **lunghezza e' esclusa**
  dal metro (AGM-45, Kh-25, RB-05 e AGM-88 sono piu' lunghi del Maverick ma piu' stretti; le lunghezze sono anche i dati
  piu' discordi). Cosi' nessun missile di taglia analoga al Maverick puo' risultare True per un errore di trascrizione:
  il blocco 1 scrive nel registro anche le dimensioni di supporto trovate (`diameter_mm`, `mass_kg`, con fonte; nessun
  `length_m`) e un test verifica le regole (1) e (2) su tutte le voci che le hanno e congela l'elenco delle voci grigie
  approvate (§5.2, test 5). Nessuna soglia numerica nel codice di produzione: le ancore stanno nel test e nel documento
  dati.
- Estensione futura, fuori perimetro: scalare il raggio di scoperta del colpo in R-INT con l'RCS (oggi il colpo e' visto
  come un aereo, `Proposta_Intercettazione_Reazione.md:66-67`; la decisione Q2 del 2026-09-30 prevedeva gia' "ridurre il
  raggio contro i colpi" quando ci sara' un dato, `:97-99`).

---

## 3. Alternative

### 3.1 Criterio di ammissibilita' (BI-1)

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| **C+F: categoria + flag di dimensione** | classe di munizione (R-BI-1) e flag `ad_detectable` per i missili | segue la struttura della regola (categoria, poi dimensione); un campo enumerato e un booleano, verificabili da fonti; nessuna soglia numerica inventata | la dimensione e' binaria: nessuna gradazione (la Pd del colpo resta quella di un aereo) |
| C: sola categoria | classe; per i navali `anti_ship` sempre ammessi | dati minimi | non distingue un antinave piccolo da uno grande; non realizza "se le dimensioni sono compatibili" |
| R: solo RCS numerico | `rcs_m2` per missile e soglia `>= RCS_rif` | uniforme | RCS dei missili poco documentati [I]; due costanti stimate (valori e soglia); escluderebbe un balistico piccolo che la regola ammette per categoria |
| C+R: categoria + RCS numerico | come C+F ma con `rcs_m2` e soglia | gradazione possibile in futuro (raggio di scoperta in R-INT) | come R per i dati; piu' costanti stimate |
| C+D: categoria + dimensioni fisiche come proxy | diametro/lunghezza a registro e soglia derivata dal riferimento | dimensioni fisiche ben documentate [I] | la relazione dimensione-RCS dipende da forma e materiali [I]; soglia stimata; sensibile (es. Maverick 305 mm contro Harpoon 343 mm [I per il Maverick]) |

**Raccomandazione: C+F.** Fa quello che la regola chiede con i dati piu' verificabili; le dimensioni fisiche, se la
ricerca le trova, entrano come supporto della decisione sul flag, non come soglia nel codice. C+R resta l'evoluzione
naturale se servira' una Pd del colpo.

### 3.2 Dove mettere la regola (BI-9)

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| **W1: domini nella `ShotSpec` + filtro nel risolutore** | la fire control (che conosce l'arma) calcola `intercept_domains: Optional[FrozenSet[str]]` (es. `{'land','naval'}`, `{'naval'}`, `frozenset()`; None = non dichiarato); il risolutore, con l'interruttore acceso, ammette `i` solo se il suo dominio e' nell'insieme | rispetta il contratto "la decide chi conosce l'arma" (`:597-599`); il risolutore resta indifferente ai registri; un solo punto per la tabella di §2.1 (fire control); il filtro per intercettore realizza la distinzione terrestre/navale | un campo nuovo in `ShotSpec` (additivo, default None) |
| W2: la fire control mette `interceptable=False` | nessun campo nuovo | minima | non puo' esprimere "solo navali": un Harpoon e' bersaglio di una nave ma (in teoria) non di un Tor |
| W3: il risolutore legge i registri per nome d'arma | nessun campo nuovo | — | il risolutore importerebbe i registri (oggi non lo fa: `Logic/Engagement_Resolver.py` riceve tutto dalla fire control); rompe il contratto; le armi `test:*` resterebbero senza classe |
| W4: tabella nel risolutore, classe nella `ShotSpec` | `munition_class` nella `ShotSpec`, tabella classe->domini nel risolutore | la regola dell'utente e' visibile nel risolutore | la tabella sta lontano dai dati; il flag `ad_detectable` dovrebbe viaggiare anch'esso |

**Raccomandazione: W1**, con la tabella classe->domini in `Logic/Fire_Control.py` (costante `AD_TARGET_DOMAINS`) e il
dominio dell'intercettore calcolato nel risolutore. **DECISA e CONFERMATA dall'utente il 2026-11-07** (BI-9 (a)), dopo
la spiegazione qui sotto.

#### 3.2.1 Che cos'e' W1, spiegato per esteso

"W1".."W4" sono solo le etichette delle quattro opzioni della tabella; la W sta probabilmente per *Where*, "dove" [I:
etichetta scelta nella prima stesura, senza significato tecnico]. La domanda e': **in quale modulo del DES (*Discrete
Event Simulation*, il motore delle sessioni virtuali) si scrive la regola dell'utente?**

I due moduli coinvolti e il loro ruolo oggi [V]:

| Modulo | Ruolo | Che cosa sa | Che cosa non sa |
|---|---|---|---|
| **fire control** (`Logic/Fire_Control.py`, "controllo del tiro") | dato un tiratore e un bersaglio, sceglie l'arma e prepara la **`ShotSpec`** (*shot specification*, la "scheda del colpo": precisione, distruttivita', colpi per salva, tempo di volo, portata, e oggi il booleano `interceptable`) | legge i **registri d'arma** (`AIR_WEAPONS`, `GROUND_WEAPONS`, `SHIP_WEAPONS`): categoria, task, tipo, dati | non sa chi difendera' il bersaglio ne' dove sara' l'intercettore |
| **risolutore** (`Logic/Engagement_Resolver.py`) | svolge l'ingaggio nel tempo: rilevamenti, lanci, salve in volo; all'impatto decide **chi ferma che cosa** (Hughes/R1, regole L1 e R-INT) | conosce gli intercettori, le loro posizioni, scorte e canali, gli istanti | **non legge i registri** (riceve tutto dalla `ShotSpec`; il contratto e' scritto in `:597-599`: "la decide chi conosce l'arma, non il risolutore") |

La regola dell'utente ha **due meta'**: una dipende solo dall'**arma** (e' un cruise? e' un Maverick? e' una bomba?),
l'altra dipende dall'**intercettore** (e' una difesa terrestre o navale?). Nessuno dei due moduli, da solo, ha entrambe
le informazioni. W1 le divide cosi':
1. la **fire control**, che conosce l'arma, aggiunge alla `ShotSpec` un campo nuovo `intercept_domains`: l'insieme dei
   domini di difesa aerea che possono considerare quel colpo un bersaglio, `{'land','naval'}` (terrestre e navale),
   `{'naval'}` (solo navale) oppure l'insieme vuoto (nessuno). Lo calcola dalla classe della munizione e dal flag
   `ad_detectable` del registro (tabella di §2.1);
2. il **risolutore**, che conosce l'intercettore, al momento di assegnare i colpi calcola il dominio
   dell'intercettore (`Ship` = `'naval'`, ogni altro = `'land'`, BI-5) e lo **ammette** solo se quel dominio sta
   nell'insieme. Poi applica L1 e R-INT come oggi. Con l'interruttore `BI_AD_TARGET_RULE` spento questo controllo non
   si fa: comportamento di oggi.

**Esempio** (stessa salva di 2 colpi, due intercettori possibili: un Tor terrestre e un Arleigh Burke navale, entrambi
nel dominio del bersaglio):

| Colpo (lanciatore) | Classe e flag (registro) | `intercept_domains` (fire control) | Tor (`'land'`) | Arleigh Burke (`'naval'`) |
|---|---|---|---|---|
| AGM-65D Maverick (A-10C) | `tactical`, `ad_detectable` False fisso (BI-6) | `frozenset()` | non ammesso | non ammesso |
| AGM-84A Harpoon (F/A-18C) | `anti_ship`, `ad_detectable` True [S] | `{'naval'}` | non ammesso | ammesso (poi L1, R-INT) |
| Kh-59 (Su-34) | `cruise` (BI-2 (a)) | `{'land','naval'}` | ammesso (poi L1, R-INT) | ammesso |

**Perche' le altre opzioni sono scartate.**
- **W2** (la fire control mette `interceptable=False` per i colpi esclusi): un solo booleano non puo' dire "si' per la
  nave, no per il Tor"; l'Harpoon dovrebbe essere o intercettabile da tutti o da nessuno. La distinzione
  terrestre/navale, che la regola dell'utente richiede, andrebbe persa.
- **W3** (il risolutore legge i registri cercando l'arma per nome): il risolutore dovrebbe importare i tre registri,
  cosa che oggi non fa; si romperebbe il contratto "la decide chi conosce l'arma"; le armi di test (`test:*`), che non
  sono nei registri, resterebbero senza classe; due moduli interpreterebbero gli stessi dati.
- **W4** (la `ShotSpec` porta la classe, la tabella classe->domini sta nel risolutore): funzionerebbe, ma la tabella
  della regola starebbe lontano dai dati che la alimentano e la `ShotSpec` dovrebbe portare anche il flag
  `ad_detectable` (due campi invece di uno); il risolutore dovrebbe conoscere le classi di munizione, che sono un
  concetto dei registri.
W1 e' l'unica che tiene la parte "arma" dove sono i dati d'arma e la parte "intercettore" dove sono gli intercettori,
con un solo campo nuovo (default None = non dichiarato, quindi ogni `ShotSpec` esistente resta valida).

### 3.3 Interruttore e significato di spento/acceso

- `Engagement_Resolver.BI_AD_TARGET_RULE = False`, letto **una volta** all'inizio della run (`_EngagementRun.__init__`,
  attributo `self.ad_target_rule`), quindi valido anche per le chiamate dirette a `resolve_engagement` e sostituibile nei
  test con `patch.object(ER, 'BI_AD_TARGET_RULE', True)`.
- La fire control valorizza `intercept_domains` **sempre** (e' un dato dell'arma, come `interceptable`): niente cache
  della fire control dipendente da un interruttore (`make_registry_fire_control` memoizza per chiave di tiratore e
  bersaglio, `Logic/Fire_Control.py:172-179` docstring).
- **Spento** = oggi: ogni missile e ogni bomba guidata e' fermabile da qualunque intercettore `Anti_Missile` (Tor che
  ferma Maverick, nave che ferma qualunque missile). Fotografia: 1009 identiche.
- **Acceso** = R-BI: Maverick, ARM, ATGM, bombe guidate non sono piu' fermati dalle difese terrestri; restano cruise,
  balistici e, per le navi, gli antinave e i missili `ad_detectable`. Cambiano solo le esecuzioni elencate da B-0 come
  `CHANGED` (§1.8).
- **RNG**: il filtro non estrae nulla. Cambia solo **chi** e' fermato; dove cambia, cambia il numero di colpi che
  arrivano al danno e quindi le estrazioni di danno successive dello stesso ingaggio (come per L1 e R-INT).

### 3.4 Effetti su R-INT, L1, Hughes, scorte, L2/L3

| Pezzo | Effetto con l'interruttore acceso |
|---|---|
| L1 (`_may_intercept`) | invariata; valutata solo sui colpi ammessi (il filtro va **prima** nell'`if` di `:3350`, cosi' le cache di L1/R-INT non si riempiono per coppie inutili; nessun effetto sugli esiti) |
| R-INT (`_in_time`) | invariata nel meccanismo; resta in uso per cruise, balistici e, sui navali, antinave/`ad_detectable`. Il caso tipico di oggi (Tor contro Maverick, `Proposta_Intercettazione_Reazione.md:116-121`) sparisce |
| Hughes/R1, canali | invariati; i canali non sono piu' spesi su colpi esclusi: piu' capacita' per quelli ammessi |
| scorte di intercettori | meno `InterceptionEvent`; i missili AD risparmiati restano per le salve offensive (stessa voce, A1) |
| `SalvoResolution.interceptable_rounds` | con l'interruttore acceso conta i colpi con `interceptable` **e** `intercept_domains` non vuoto (o None); spento: come oggi (BI-9) |
| L2/L3 (priorita' e prelazione sul lanciatore) | invariate (`:3106-3110` non leggono `interceptable`): diventano la sola risposta AD contro un attacco A2G, coerente con la regola 1 del 2026-09-28 |
| fine di attivita' (F6-B1, armi AD consumate) | scatta meno spesso (meno intercettazioni) |
| regola D | invariata |
| pianificatore, adapter DCS | invariati (§1.6); core indifferente al simulatore: nessun riferimento all'adapter |

---

## 4. Decisioni per l'utente (una per volta)

Ogni decisione ha la tabella dei ruoli dell'esempio fisso (§Glossario) adattata al caso. "Fermato" = intercettato
dalla regola R1 (consuma un canale e una unita' di scorta dell'intercettore).

### BI-1 — Criterio di ammissibilita'

| Ruolo | Esempio |
|---|---|
| lanciatore | F/A-18C |
| colpo | 2 AGM-84A Harpoon |
| bersaglio dell'attacco | un Arleigh Burke |
| intercettore / osservatore | lo stesso Arleigh Burke (SM-2, ESSM, Phalanx) |
| bersaglio del rilevamento | l'F/A-18C |

Opzioni (§3.1): **C+F** (raccomandata), C, R, C+R, C+D. Esempio: con C+F il Harpoon ha classe `anti_ship` e
`ad_detectable` True (riferimento rilevabile, BI-7) -> il Burke puo' fermarne fino a min(canali, scorta); un Maverick
lanciato contro lo stesso Burke ha classe `tactical` e `ad_detectable` **fisso False** (decisione BI-6): passa sempre.
Con C il Maverick passerebbe comunque (classe non `anti_ship`) e ogni antinave sarebbe ammesso senza guardare la
dimensione.

scelta utente: raccomandata

**DECISA dall'utente il 2026-11-07: C+F** (categoria della munizione + flag `ad_detectable`).

### BI-2 — Cruise tattici lanciati da cacciabombardieri (Kh-59/59M, KD-63/63B; in futuro Storm Shadow, SLAM-ER, Taurus)

| Ruolo | Esempio |
|---|---|
| lanciatore | Su-34 (Fighter_Bomber) |
| colpo | 2 Kh-59 (portata 90 km a registro) |
| bersaglio dell'attacco | un deposito della forza Blue |
| intercettore / osservatore | un Buk (9M38, V_I ~35 km) della stessa forza |
| bersaglio del rilevamento | il Su-34 |

Le due frasi della regola si contraddicono qui: "cruise indipendentemente da chi li lancia" contro "tutti gli A2G dei
cacciabombardieri esclusi". (a) **la categoria vince**: il Kh-59 e' `cruise`, il Buk puo' fermarlo se lanciato fuori
dal suo V_I (lancio a 80 km: si'). (b) **il lanciatore vince**: escluso per le difese terrestri. Raccomandazione **(a)**
[S]: la prima frase e' la regola, la seconda ne e' la conseguenza ("percio'") per i missili A2G tipici (Maverick,
Kh-25, Kh-29), che non sono cruise. Con (b) il codice dovrebbe leggere anche la classe del lanciatore (dato
`Air_Asset_Type`, lista di categorie per aereo, §1.5): piu' complesso.

scelta utente: raccomandata

**DECISA dall'utente il 2026-11-07: (a), la categoria vince** (Kh-59, Kh-59M, KD-63, KD-63B `cruise`, bersagli anche
delle difese terrestri). Incoerenza segnalata: I-1 (§4.13). Nota del blocco 0 (Proposta dati, D3.2 (a)): KD-63 e
KD-63B sono lanciati solo dal bombardiere H-6, non da cacciabombardieri; restano `cruise` per la categoria; il caso di
cruise da cacciabombardiere e' il Kh-59.

### BI-3 — Missili antiradiazione (ARM)

| Ruolo | Esempio |
|---|---|
| lanciatore | F-16CM Block 50 |
| colpo | 2 AGM-88 HARM |
| bersaglio dell'attacco | il radar/lanciatore di un S-300PS |
| intercettore / osservatore | lo stesso S-300PS (5V55R, `Anti_Missile`) e un Tor della forza |
| bersaglio del rilevamento | l'F-16 |

(a) **esclusi per le difese terrestri** (lettera della regola: A2G di cacciabombardiere), raccomandata; (b) bersagli
anche dei terrestri, come classe a parte (nella realta' alcuni sistemi li ingaggiano [I]). Con (a) gli HARM lanciati a
80 km fuori dal V_I arrivano sempre; con (b) il Tor e l'S-300 ne fermano fino a min(canali, scorta).

scelta utente: raccomandata

**DECISA dall'utente il 2026-11-07: (a)**, ARM (*Anti-Radiation Missile*, missile antiradar) esclusi per le difese
terrestri; per le navali vale il flag `ad_detectable` (BI-6).


### BI-4 — Bombe guidate e plananti

| Ruolo | Esempio |
|---|---|
| lanciatore | A-10C |
| colpo | 2 GBU-12 |
| bersaglio dell'attacco | un BMP-2 |
| intercettore / osservatore | un Tor |
| bersaglio del rilevamento | l'A-10C |

La regola dice "tutte le bombe mai". Conferma richiesta perche' **restringe** la regola del 2026-09-28 (bombe plananti
fra le armi autonome bersaglio legittimo) e la motivazione del task `Anti_Missile` del Tor (§1.7). (a) **mai**
(raccomandata, lettera della regola); (b) le sole plananti a lungo raggio (LS-6 a registro [V]) trattate come cruise.
Oggi il Tor ferma le GBU-12 (bombe guidate intercettabili); con (a) mai.

scelta utente: raccomandata

**DECISA dall'utente il 2026-11-07: (a), mai** (tutte le bombe, comprese guidate e plananti): restringe la regola del
2026-09-28; i documenti precedenti ricevono una nota di rimando (blocco 4).

### BI-5 — Che cosa e' "terrestre" e "navale"

| Ruolo | Esempio |
|---|---|
| lanciatore | A-10C |
| colpo | 2 Kh-29T (tattico, grande [I]) |
| bersaglio dell'attacco | una compagnia di carri sulla costa |
| intercettore / osservatore | un Arleigh Burke dello stesso blocco/Operazione (difesa di dominio) |
| bersaglio del rilevamento | l'A-10C |

(a) **per classe dell'intercettore** (Ship = navale), raccomandata: il Burke applica le regole navali (se il Kh-29 e'
`ad_detectable` lo puo' fermare); (b) per dominio del **bersaglio dell'attacco**: carri = terrestre, nessuno ferma il
Kh-29. (a) e' piu' semplice (un'informazione dell'intercettore, gia' nello stato ombra) e lega il criterio di
dimensione ai sensori che devono vedere il colpo, che sono quelli dell'intercettore.

scelta utente: raccomandata

**DECISA dall'utente il 2026-11-07: (a), per classe dell'intercettore.**

### BI-6 — Missili tattici e ARM contro le difese navali

| Ruolo | Esempio |
|---|---|
| lanciatore | Su-25T |
| colpo | 2 Kh-29T, oppure 2 AGM-65D da un A-10C |
| bersaglio dell'attacco | una corvetta |
| intercettore / osservatore | la stessa corvetta (SA-N-9, AK-630) |
| bersaglio del rilevamento | il Su-25T / l'A-10C |

"A2S" puo' voler dire la **classe** (missile antinave) o l'**uso** (missile lanciato contro una nave). (a) **uso**:
ogni missile con `ad_detectable` True e' bersaglio dei navali (raccomandata: criterio di dimensione generale per i
navali); (b) solo la classe `anti_ship` con `ad_detectable`; (c) solo la classe `anti_ship`, senza dimensione. Con (a)
il Kh-29 (se la ricerca lo dichiara compatibile) e' fermabile, il Maverick no (fisso piccolo, decisione dell'utente);
con (b) e (c) nessuno dei due.

scelta utente: (a) con Maverick considerato piccolo (applica questa considerazione in modo da garantire la coerenza pur le altre situazioni di utilizzo)

**DECISA dall'utente il 2026-11-07: (a) "uso", con il Maverick fisso "piccolo"** (interpretazione confermata
dall'utente):
- la famiglia Maverick (AGM-65D, AGM-65K, RB-75T) e' un missile piccolo **non rilevabile da nessuna difesa aerea**,
  terrestre o navale: `ad_detectable` e' scritto **False** nel registro per queste tre voci, con il commento
  "decisione dell'utente BI-6 del 2026-11-07", e non dipende dalla ricerca dati;
- lo stesso criterio vale per gli altri missili della stessa taglia: la ricerca (blocco 0) li valuta con il "metro del
  Maverick" (§2.5): taglia pari o minore -> False obbligatorio; taglia pari o maggiore dell'Harpoon -> True; in mezzo
  zona grigia, approvata voce per voce. I candidati "piccoli" dei registri (§2.2: Hellfire, TOW, Shturm, Ataka, HOT-3,
  Mistral, Kh-25, Kh-66, RB-05, Shrike) sono **ipotesi** [I]/[S], non fatti;
- conseguenze sul piano: blocco 1 (flag esplicito e test di coerenza, §5.2), blocco 2 (test "Maverick contro nave ->
  nessun dominio", §5.3.5), scenario S35 (variante navale con Maverick: caso di prova "non fermato", §5.4).
- Contro le difese terrestri il Maverick era gia' escluso dalla classe (`tactical`, BI-3/corollario dell'utente): il
  flag fisso rende la regola **uguale nei due domini** per questa famiglia.
- Incoerenza nuova: I-1 (§4.13).

### BI-7 — Riferimento di dimensione e valore di default del flag

| Ruolo | Esempio |
|---|---|
| lanciatore | F/A-18C |
| colpo | 2 AGM-84A Harpoon (riferimento) e 2 AGM-65D Maverick |
| bersaglio dell'attacco | un Arleigh Burke |
| intercettore / osservatore | l'Arleigh Burke |
| bersaglio del rilevamento | l'F/A-18C |

(a) **flag `ad_detectable` per missile**, deciso dalla ricerca rispetto a un riferimento scelto dall'utente
(raccomandato: Harpoon per gli antinave/cruise subsonici, un balistico tattico se si aggiungeranno i balistici), con
default se manca il dato: `anti_ship` e `cruise` True, `arm`/`tactical` False [S]; (b) soglia numerica sull'RCS [S]
(`AD_DETECTABLE_RCS_M2`, nessun valore noto oggi); (c) soglia sul diametro [S]. Esempio della sensibilita' di (c)
(scritto prima della decisione BI-6, **non piu' valido**: con una soglia di 300 mm il Maverick, 305 mm [I], sarebbe
stato ammesso, cosa che BI-6 ora vieta).

scelta utente: raccomandata

**DECISA dall'utente il 2026-11-07: (a), flag per missile**, con la decisione BI-6 come vincolo. Come si garantisce la
coerenza fra il flag e il riferimento (dettaglio in §2.5):
- il flag non viene da una soglia nel codice ma da due **ancore** documentate: Maverick (False, fissato dall'utente) e
  Harpoon (True, riferimento rilevabile); i missili non maggiori del Maverick sono False, quelli non minori
  dell'Harpoon True, gli altri sono zona grigia approvata voce per voce;
- per evitare che un missile di taglia analoga al Maverick risulti True, il blocco 1 registra le dimensioni di supporto
  trovate dalla ricerca (`diameter_mm`, `mass_kg`, con fonte) e un **test di coerenza** fallisce se un missile True ha
  diametro e massa entrambi non maggiori di quelli del Maverick, o se un missile False ha diametro e massa entrambi non
  minori di quelli dell'Harpoon (§5.2, test 5);
- default quando manca il dato: `anti_ship` e `cruise` True, `arm`/`tactical` False [S] (invariato).
Esempio: Hellfire (AGM-114, piu' piccolo del Maverick [I]) -> False per la regola (1); RGM-84 Harpoon navale -> True per
la regola (2); Kh-29T (diametro ~380 mm [I], massa maggiore del Maverick [I]) -> zona grigia, proposta della ricerca.
Esito del blocco 0 (Proposta dati §5): Hellfire 180 mm / 45,7 kg -> False obbligatorio; Kh-29T 380 mm / 685 kg, sopra
l'Harpoon -> True obbligatorio; ancore e regole definitive in §2.5.

### BI-8 — Armi non a registro (`test:*`) e fire control a tabella

| Ruolo | Esempio |
|---|---|
| lanciatore | un aereo di ruolo 'strike' della tabella di riferimento |
| colpo | `test:agm` (interceptable=True, `Test/Scenario_Fixtures.py:813-814`) |
| bersaglio dell'attacco | un'unita' di ruolo 'ground' |
| intercettore / osservatore | un asset della forza con capacita' None (stub) o `Anti_Missile` |
| bersaglio del rilevamento | l'aereo |

(a) **comportamento precedente** (raccomandata): `intercept_domains` None -> nessun filtro; gli scenari S1-S18 a tabella
non cambiano nemmeno con l'interruttore acceso, salvo quelli che usano la fire control dei registri; (b) le `SHOTS` di
test dichiarano i domini per ruolo (`agm`/`arm` -> vuoto, `asm` -> navale): gli scenari a tabella con intercettazioni
di test escluse cambierebbero con l'interruttore acceso. B-0 (§1.8): con (a) cambiano 6 esecuzioni (S19AD `tor_rear`),
con (b) 8 (in piu' S2-0-sead e S2-6-sead, 10 `test:anti_radiation` fermati da un Buk); i `test:anti_ship` di S6/S16 sono
ammessi in entrambe (antinave contro navale). (a) tiene gli scenari a tabella fuori dalla regola, (b) li rende coerenti
con essa: entrambe difendibili; (a) e' raccomandata perche' le armi di test non hanno dati di dimensione.

scelta utente: raccomandata

**DECISA dall'utente il 2026-11-07: (a), comportamento precedente** per le armi non a registro: con l'interruttore
acceso cambiano le 6 esecuzioni S19AD `tor_rear` (sonda B-0).

### BI-9 — Interruttore e punto d'aggancio

| Ruolo | Esempio |
|---|---|
| lanciatore | A-10C |
| colpo | 2 AGM-65D |
| bersaglio dell'attacco | BMP-2 |
| intercettore / osservatore | Tor |
| bersaglio del rilevamento | A-10C |

(a) **W1 + `Engagement_Resolver.BI_AD_TARGET_RULE = False`** letto all'inizio della run (raccomandata, §3.2-§3.3);
(b) W2 (la fire control spegne `interceptable` se l'interruttore e' acceso: niente distinzione navale); (c) parametro
passato da `Session_Simulator` solo se acceso (schema della D-5): inutile qui perche' non serve nessun dato di sessione
e nessuno stream. Esempio: spento, il Tor ferma i Maverick di S19AD `tor_rear` come oggi; acceso, mai.

nota utente: spiega meglio cos'è W1?

**Risposta (2026-11-07)**: spiegazione estesa in §3.2.1 (ruoli di fire control e risolutore, campo
`intercept_domains`, esempio Maverick/Harpoon/Kh-59 contro Tor e Arleigh Burke, motivi dello scarto di W2/W3/W4).
**DECISA e CONFERMATA dall'utente il 2026-11-07, dopo la spiegazione: (a) W1 + `Engagement_Resolver.BI_AD_TARGET_RULE
= False`.**

### BI-10 — Scenario

| Ruolo | Esempio (variante `land_tactical`) |
|---|---|
| lanciatore | 4 A-10C con AGM-65D (geometria di S19AD `tor_rear`) |
| colpo | Maverick |
| bersaglio dell'attacco | 3 BMP-2 |
| intercettore / osservatore | Tor arretrato |
| bersaglio del rilevamento | gli A-10C |

(a) **S34-ADTGT** (nome della prima stesura; ora S35-ADTGT con 4 geometrie, v. decisione sotto), 3 geometrie x interruttore spento/acceso x 4 semi = **24 esecuzioni nuove** (raccomandata, §5.4):
`land_tactical_off/on` (Maverick contro Tor), `land_cruise_off/on` (Kh-59 da Su-34 contro un deposito difeso da un Buk:
dipende da BI-2), `naval_off/on` (AGM-84A da F/A-18C contro un Arleigh Burke); (b) nessuno scenario nuovo, solo test
unitari e la sonda B-1. Senza scenario la regola non sarebbe provata in sessione con i registri veri (la fotografia ha
solo il caso Maverick, §1.8).

scelta utente: raccomandata

**DECISA dall'utente il 2026-11-07: (a)**, con due adattamenti dopo le altre scelte: (i) nome **S35-ADTGT** e file
`Test_Session_Scenarios_S35.py`, perche' S34 (`S34-BAND`, `Test_Session_Scenarios_S34.py`) e' gia' riservato dal piano
della Proposta VA (`Proposta_Allineamento_Volumi_DES_Pianificatore.md` §4.2) e S33 da FP; (ii) **quarta geometria**
`naval_maverick_off/on` (A-10C con AGM-65D contro un Arleigh Burke: caso di prova "non fermato" della decisione BI-6).
Totale **4 geometrie x 2 x 4 semi = 32 esecuzioni nuove** (§5.4).
*Nota (2026-11-08)*: nelle due varianti navali la nave e' la `FF 1135M Rezky` e non l'Arleigh Burke (decisione P-1 (a),
§5.4.1): con il V_I di 240 km del Burke la regola L1 vieta ogni intercettazione dei lanci da aereo; i nomi delle
varianti non cambiano.

### BI-11 — Ordine dei lavori e FP-5

(a) **prima questa Proposta, poi la ripresa di FP-5** (raccomandata, §6): FP-5 riguarda solo R-INT, e la regola nuova
toglie a R-INT il caso tipico (A2G contro difese terrestri); (b) FP completa prima (FP-5 decisa con (a) o (d) senza
sapere quali colpi restano intercettabili). Le altre Proposte (D-5 blocchi fatti, FP blocchi 1-2, VA) sono indipendenti
nel codice (§6).

scelta utente: esegui questa proposta e poi riproponi la FP-5 illustrandone in dettaglio e con esempi le scelte possibili   

**DECISA dall'utente il 2026-11-07: (a).** Ordine registrato: (1) esecuzione di questa Proposta (blocchi 0-4); (2)
ripresa di FP-5 in `Proposta_Finestre_Per_Passaggio_Portata_Propria.md`, riproposta con le opzioni (a)-(d) illustrate in
dettaglio e con esempi, alla luce di quali colpi restano intercettabili. FP-5 resta SOSPESA fino ad allora. Ordine dei
file rispetto a VA e FP: §6.

*Nota a margine (2026-11-08): superata: FP-5 decisa il 2026-11-08 (opzione (d)), prima della fine di questa Proposta;
non c'e' piu' una ripresa di FP-5. Ordine di esecuzione attuale: BI blocchi 3-4 -> VA blocchi 1-2 -> FP blocchi 1-2
(BI blocchi 0-2 gia' eseguiti e mergiati), §6.1.*

### 4.12 BI-12 — Il criterio di dimensione vale anche per le difese terrestri? (NUOVA 2026-11-07, DECISA: (a))

| Ruolo | Esempio |
|---|---|
| lanciatore | Su-34 |
| colpo | 2 Kh-29T (tattico, diametro ~380 mm [I]), oppure 2 Kh-58 (ARM, grande [I]) |
| bersaglio dell'attacco | un deposito della forza Blue |
| intercettore / osservatore | un Buk (terrestre) e, nello stesso dominio, una corvetta (navale) |
| bersaglio del rilevamento | il Su-34 |

Nasce dalle scelte BI-2 (a), BI-3 (a) e BI-6 (a) (incoerenza I-1, §4.13). La regola dell'utente ammette un missile se
e' balistico/cruise **e/o** se ha dimensioni rilevabili; il corollario esclude **tutti** gli A2G (aria-suolo) dei
cacciabombardieri dalle difese terrestri. Oggi il piano applica la dimensione **solo** ai navali. (a) **lasciare cosi'**
(lettera del corollario): il Kh-29T, se `ad_detectable` True, e' fermabile dalla corvetta ma mai dal Buk; il Kh-59, di
taglia simile [I], e' fermabile dal Buk perche' `cruise`. (b) **dimensione anche per i terrestri** per le classi
`tactical` e `arm`: il Buk puo' fermare il Kh-29T e il Kh-58 se `ad_detectable` True; il Maverick resta escluso ovunque
(BI-6). Raccomandazione **(a)** [S]: e' la lettera del corollario dato dall'utente e non cambia l'esito della sonda
B-0; (b) e' piu' coerente con la clausola "e/o dimensioni" e costa una riga in `intercept_domains_for` (aggiungere
`'land'` quando il flag e' vero). La scelta non cambia la fotografia in nessuna delle due opzioni (nella fotografia
nessun Kh-29 o ARM di registro e' fermato, §1.8); cambia solo la variante `land_cruise` di S35 se si usasse un Kh-29.

scelta utente: raccomandata

**DECISA dall'utente il 2026-11-07: (a).** Il flag `ad_detectable` vale **solo per le difese navali**; per le difese
terrestri contano solo le categorie (`cruise`, `ballistic`). Kh-29 e Kh-58 (e ogni `tactical`/`arm`) non sono quindi
bersagli delle difese terrestri anche se di taglia simile al Kh-59 [I]. **Limite dichiarato, scelta di progetto [S]**:
da riportare nel capitolo 9 del manuale (`10_Limiti_Estensioni_Divergenze.md`, blocco 4) e nel commento di
`AD_SIZE_GATED_NAVAL` in `Logic/Fire_Control.py` (§5.3.1). Nessun cambio al piano: era la raccomandazione gia'
implementata (stessi test, righe ed esecuzioni).

### 4.13 Incoerenze segnalate dopo le scelte (2026-11-07)

- **I-1 (dimensione e dominio).** Con BI-2 (a) un Kh-59 (cruise tattico, portato da Su-30/Su-34) e' bersaglio del Buk;
  con BI-3 (a) e il corollario un Kh-29 o un Kh-58 (A2G di taglia comparabile [I]) non lo e', anche se con BI-6 (a) la
  stessa arma puo' essere `ad_detectable` True e quindi fermabile da una nave. Lo stesso missile "si vede" dai sensori
  navali e "non si vede" da quelli terrestri. Non e' un errore del piano: discende dal corollario. **Accettata
  dall'utente con BI-12 (a) il 2026-11-07**: limite dichiarato [S].
- **I-2 (Maverick e regola "e/o dimensioni").** Il Maverick e' escluso per scelta dell'utente, non per un dato: se la
  ricerca trovasse un missile di taglia analoga ma classificato `anti_ship` (es. un antinave leggero [I]), la regola (1)
  del metro del Maverick lo renderebbe False anche contro le navi. E' voluto (coerenza di taglia), ma va saputo: la
  classe `anti_ship` non basta da sola a renderlo bersaglio.
- **I-3 (nomi di scenario).** S34 era riservato da VA (`S34-BAND`): rinominato S35-ADTGT (BI-10).
- **I-4 (bombe plananti e Tor).** BI-4 (a) contraddice la motivazione del task `Anti_Missile` del Tor
  (`Proposta_Dati_Anti_Missile.md:19`); il task resta (regola D invariata), cambia solo che cosa il Tor puo' fermare.

---

## 5. Piano di revisione (decisioni dell'utente del 2026-11-07: BI-1 C+F, BI-2 (a), BI-3 (a), BI-4 (a), BI-5 (a), BI-6 (a) con Maverick fisso piccolo, BI-7 (a), BI-8 (a), BI-9 (a) W1, BI-10 (a) come S35, BI-11 (a), BI-12 (a))

Tutte le decisioni sono prese e il blocco 0 (dati) e' eseguito e approvato (2026-11-07): il piano e' eseguibile dal
blocco 1. Blocchi 1 e 2 eseguiti e mergiati il 2026-11-08; i punti P-1..P-7 del blocco 3 decisi dall'utente il
2026-11-08 (§5.4.1): **il blocco 3 e' eseguibile** (esecutore `oc-developer`).

### 5.0 Precondizioni (l'esecutore le verifica e si ferma se mancano)
1. Branch dedicato creato dalla sessione principale (blocco 3: **`ai/oc-bi-blocco3`**, controllo con
   `git branch --show-current`); `git status` pulito; nessun altro esecutore al lavoro su
   `Logic/Engagement_Resolver.py` o `Logic/Fire_Control.py` (§6).
2. Il blocco 0 (dati) consegnato e approvato dall'utente (le decisioni BI-1..BI-12 sono registrate in §4): **fatto il
   2026-11-07**, `Proposta_Dati_Bersagli_Intercettabili.md` con le decisioni D1-D6 prese; l'esecutore controlla che il
   suo stato dica "DECISO".
3. Righe citate ancora valide (riverificate il 2026-11-08 sul checkout dopo il merge `4803424b`, HEAD `c69ff954`;
   prima del blocco 2 erano `Logic/Fire_Control.py:763-768`, `Logic/Engagement_Resolver.py:614`, `:3291`, `:3350`):
   `Logic/Fire_Control.py:837-842` (calcolo di `interceptable`) [V], `Logic/Engagement_Resolver.py:635` (campo
   `intercept_domains`) [V], `:3333-3337` (conteggio dei colpi intercettabili) [V], `:3396-3397` (filtro con
   `_admissible`) [V]. Se sono slittate per l'esecuzione di FP o VA, cercare i punti per contenuto e riferire.
4. **Solo blocco 3** (aggiunta del 2026-11-08): i simboli dei blocchi 1-2 su cui il blocco 3 poggia esistono con questi
   nomi e firme (elenco con righe in §5.4.2, "Cosa il blocco 3 usa dai blocchi 1-2"); `Test/Test_Session_Scenarios_S33.py`,
   `_S34.py`, `_S35.py` **non** esistono [V]; la tupla `Scenario_Baseline.UNITS` termina con S32-DWELL
   (`Test/Scenario_Baseline.py:395-397`, chiusura `:398`) [V]; la suite di partenza da' `Ran 4829` `OK (skipped=7)` [V,
   `.ai-run/suite.log` del 2026-11-08 e `Rapporti/Rapporto_BI_blocco2_des-developer.md:41`]. Se uno di questi fatti non
   vale, fermarsi e riferire.
5. **Solo blocco 3**: esistono i simboli dei test e dei registri che il file nuovo importa o usa (elenco in §5.4.2,
   "Cosa il file nuovo usa dal repo"); controllo con `grep -n`, nessuna modifica. Se uno manca o ha un'altra firma,
   fermarsi e riferire.

### 5.1 Blocco 0 — ricerca dati (non codice; `oc-writer` o sessione principale con l'utente) — ESEGUITO

**Eseguito e approvato il 2026-11-07**: ricerca di `oc-researcher` in sette lotti (L1-L7, 0,196 $) e ricerca mirata M1
(0,371 $), verifiche della sessione principale, decisioni D1-D6 dell'utente; prodotto
`Analysis/Document/Proposta_Dati_Bersagli_Intercettabili.md`, valori per il blocco 1 nel suo §10.2. Il testo sotto e'
il mandato originale, lasciato come traccia; i punti 1-5 sono coperti da quel documento (§3, §5, §4, §6, §4 in fondo).

Prodotto: `Analysis/Document/Proposta_Dati_Bersagli_Intercettabili.md` (stile `Proposta_Dati_Anti_Missile.md`): per
ciascuno dei 44 `MISSILES_ASM` aerei e degli 8 navali: classe (§2.2), `ad_detectable`, diametro/lunghezza/massa se
trovati, fonte, confidenza A/M/B (fonte primaria o due concordi / una secondaria / stima), motivazione. Nessun valore
inventato: senza fonte la voce resta al default di classe, dichiarato [S]. Da approvare dall'utente. Contenuto
obbligatorio dopo la decisione BI-6:
1. **le due ancore** con fonte: dimensioni del Maverick (AGM-65, ancora bassa, False per decisione dell'utente) e
   dell'Harpoon (ancora alta, True; diametro 343 mm gia' a registro navale [V], lunghezza e massa da fonte);
2. **tabella del metro del Maverick**: per ogni missile `tactical` e `arm` (e per ogni `anti_ship` sospetto di essere
   piccolo) diametro e massa con fonte e il confronto con le due ancore: "non maggiore del Maverick" -> False
   obbligatorio; "non minore dell'Harpoon" -> True; altrimenti **zona grigia** con proposta motivata;
3. l'elenco dei **candidati piccoli** di §2.2 (AGM-114, BGM-71D, 9M114, 9M120, 9M120-F, Hot-3, Mistral, Kh-25ML/MR/MP/MPU,
   Kh-66, RB-05A/E, AGM-45) trattato come **ipotesi** da confermare o smentire con fonti, non come fatto; i nomi
   comuni fra parentesi (Shturm, Ataka, Shrike) vanno verificati;
4. la **zona grigia** (atteso [I]: Kh-29L/T/TE, Kh-58, AGM-88, Kh-31P, LD-10) presentata all'utente voce per voce;
5. una nota sui missili citati dall'utente ma **assenti dai registri** (Brimstone, Vikhr, APKWS [V]): nessuna voce da
   creare in questa Proposta.

Nota [I] (caso limite M1, §2.3): un antinave lanciato da un **bombardiere** contro un bersaglio **terrestre** (es.
Kh-22N del Tu-22M) non e' intercettabile da nessuno con la classe `anti_ship` (non bersaglio delle difese terrestri,
tabella R-BI-3). La regola dell'utente esclude l'A2G (aria-superficie) solo per cacciabombardieri/aerei d'attacco e
ammetterebbe un cruise da bombardiere: il blocco 0 deve quindi **classificare il Kh-22N** (se `cruise`, diventa
bersaglio dei terrestri). Nessuna decisione nuova. **Esito**: `anti_ship` (Proposta dati, D3.1 (a)); il Kh-22N ha solo
la riga di efficacia `ship` [V], quindi non e' mai lanciato contro bersagli terrestri e il caso non si presenta con i
registri attuali. Anomalia di designazione (per tre fonti in inglese la "N" e' la versione nucleare) segnalata in
Proposta dati §7, IR-21 (incoerenza di registro n. 21), da non correggere nel blocco 1.

### 5.2 Blocco 1 — dati nei registri

- `Asset/Aircraft_Weapon_Data.py` (`AIR_WEAPONS['MISSILES_ASM']`, 44 voci) e `Asset/Ship_Weapon_Data.py`
  (`SHIP_WEAPONS['MISSILES_ASM']`, 8 voci): campo nuovo `'munition_class'` (str, uno di `'cruise'`, `'anti_ship'`,
  `'arm'`, `'tactical'`, piu' `'ballistic'` per il futuro) e, dove il blocco 0 lo da', `'ad_detectable'` (bool), ogni
  voce con commento `# STIMA [S]: <fonte>`. Commento di testa che rimanda a questa Proposta e al documento dati. Valori:
  tabella del §10.2 di `Proposta_Dati_Bersagli_Intercettabili.md` (52 voci, tutte con classe e flag; regole di
  scrittura nel suo §10.1).
- **Famiglia Maverick** (AGM-65D, AGM-65K, RB-75T in `AIR_WEAPONS['MISSILES_ASM']`): `'ad_detectable': False` scritto
  sempre, con il commento `# decisione dell'utente BI-6 (2026-11-07): Maverick piccolo, non rilevabile da nessuna
  difesa aerea` (non `STIMA`: e' una decisione, non un dato).
- **Dimensioni di supporto** dove il blocco 0 le ha trovate con fonte: `'diameter_mm'` (44 voci) e `'mass_kg'` (46
  voci) sulle stesse voci, commento con la fonte e con l'altro valore se le fonti discordano; **nessun `'length_m'`**
  (lunghezza esclusa dal metro, Proposta dati D1). Servono al test di coerenza, non al motore.
- Nessun altro registro cambia (classi derivate, R-BI-1).
- Verifica prima di scrivere: che gli scorer (`get_missiles_score` e simili, `Asset/Aircraft_Weapon_Data.py:441-537`;
  `Asset/Ship_Weapon_Data.py:793-812`) non iterino su tutte le chiavi della voce (un campo nuovo li romperebbe). Se lo
  fanno, fermarsi e riferire.
- Test (6, nei file esistenti `Test/Test_Aircraft_Weapon_Data.py` e `Test/Test_Ship_Weapon_Data.py`):
  1. ogni voce `MISSILES_ASM` ha `munition_class` in `{'ballistic','cruise','anti_ship','arm','tactical'}`;
  2. `ad_detectable`, `diameter_mm`, `mass_kg`, se presenti, sono rispettivamente bool e numeri positivi;
  3. le classi delle voci elencate in §2.2 sono quelle approvate (tabella del blocco 0, Proposta dati §10.2);
  4. AGM-65D, AGM-65K e RB-75T hanno `ad_detectable` **presente e False** (decisione BI-6);
  5. **coerenza col metro del Maverick** (Proposta dati §5 e §10.1; sta in `Test/Test_Aircraft_Weapon_Data.py` e legge
     sia `AIR_WEAPONS['MISSILES_ASM']` sia `SHIP_WEAPONS['MISSILES_ASM']`): costanti del test con la fonte
     `D_M = 304.8` (FAS, *Federation of American Scientists*), `M_M = 304` (designation-systems, AGM-65F/G),
     `D_H = 343` (FAS), `M_H = 515.25` (FAS) e
     `GREY_ZONE_APPROVED = {'AGM-88': False, 'Kh-25MP': False, 'Kh-25MPU': False, 'RB-05A': False, 'RB-05E': False,
     'Kormoran': True}` (voci in zona grigia approvate dall'utente il 2026-11-07). Sulle voci con **entrambe** le
     dimensioni: (1) nessuna voce con `ad_detectable` True ha `diameter_mm <= D_M` e `mass_kg <= M_M`; (2) nessuna voce
     con `ad_detectable` False ha `diameter_mm >= D_H` e `mass_kg >= M_H`; (3b) l'insieme delle voci che non soddisfano
     ne' la condizione di (1) ne' quella di (2) (zona grigia) e' esattamente `{'AGM-88', 'Kh-25MP', 'Kh-25MPU',
     'RB-05A', 'Kormoran'}`. Inoltre (3a) ogni voce di `GREY_ZONE_APPROVED` esiste nel registro aereo e ha
     `ad_detectable` presente e uguale al valore approvato (anche RB-05E, che non ha dimensioni). Le voci senza la coppia
     (8: RB-75T, 9M120-F, RB-05E, Kh-555, Kh-65, KD-20, KD-63B, YJ-18) sono saltate da (1), (2) e (3b). Le voci grigie
     non sono eccezioni alle regole (1) e (2), che non le riguardano: l'asserzione (3) serve a congelare l'approvazione
     dell'utente (un True scritto per errore sull'AGM-88 farebbe fallire il test) e a segnalare ogni voce che entra o
     esce dalla zona grigia per un valore cambiato. Esito atteso con i valori del §10.2: 44 voci con la coppia, 13 False
     obbligatorie, 26 True obbligatorie, 5 in zona grigia; il test passa;
  6. punteggi invariati: `get_weapon_score` di tre missili (AGM-65D, Kh-55, RGM-84-Harpoon) identico a prima (valore
     letto prima della modifica e inserito nel test).
- Esito atteso: suite +6 test, tutti OK; confronto **1009 identiche** (la fire control non legge ancora i campi).

### 5.3 Blocco 2 — fire control e risolutore

#### 5.3.1 `Logic/Fire_Control.py`
- Costanti (scelte di progetto [S], la tabella di §2.1):

      # Regola dell'utente del 2026-11-07 (Proposta_Bersagli_Intercettabili_Difesa_Aerea.md): domini di difesa aerea che
      # possono considerare un colpo un BERSAGLIO, per classe di munizione. 'land' = intercettore non navale, 'naval' =
      # nave. Le classi 'anti_ship', 'arm', 'tactical' sono ammesse dai navali solo se il missile e' `ad_detectable`.
      # Il criterio di dimensione vale SOLO per i navali (decisione BI-12 (a), scelta di progetto [S]): per le difese
      # terrestri contano solo le classi 'cruise' e 'ballistic' (Kh-29/Kh-58 mai bersagli dei terrestri).
      AD_LAND, AD_NAVAL = 'land', 'naval'
      AD_TARGET_DOMAINS = {'ballistic': {AD_LAND, AD_NAVAL}, 'cruise': {AD_LAND, AD_NAVAL}}
      AD_SIZE_GATED_NAVAL = frozenset({'anti_ship', 'arm', 'tactical'})
      # Default di `ad_detectable` quando il registro non lo dichiara (STIMA [S], BI-7).
      AD_DETECTABLE_DEFAULT = {'cruise': True, 'ballistic': True, 'anti_ship': True, 'arm': False, 'tactical': False}

- `munition_class(weapon: _Weapon) -> Optional[str]`: `data['munition_class']` se presente; altrimenti derivata:
  `kind` 'bomb' -> `'guided_bomb'` se `type == 'Guided bombs'` altrimenti `'bomb'`; 'rocket' -> `'rocket'`; 'gun' ->
  `'gun'`; 'torpedo' -> `'torpedo'`; 'missile': aereo `MISSILES_AAM` -> `'aam'`; terrestre con task `Anti_Tank` ->
  `'atgm'`; con task `Anti_Air` (terrestre o `MISSILES_SAM` navale) -> `'sam'`; altrimenti None (non classificato).
- `intercept_domains_for(weapon: _Weapon) -> Optional[FrozenSet[str]]`: None se la classe e' None; altrimenti
  `AD_TARGET_DOMAINS.get(classe, set())` piu' `AD_NAVAL` se la classe e' in `AD_SIZE_GATED_NAVAL` e
  `data.get('ad_detectable', AD_DETECTABLE_DEFAULT[classe])` e' vero; restituisce un `frozenset`.
- `shot_spec_for` (`:745-790`): passa `intercept_domains=intercept_domains_for(weapon)` alla `ShotSpec`. `interceptable`
  invariato (riga `:763-768` intatta).
- Docstring del modulo, punto "`interceptable`" (`:129-131`): aggiungere `intercept_domains`.

#### 5.3.2 `Logic/Engagement_Resolver.py`
- Interruttore, accanto a `D5_DWELL_TIME` (`:519-525`):

      # Bersagli intercettabili (Proposta_Bersagli_Intercettabili_Difesa_Aerea.md), interruttore dedicato:
      #   * `BI_AD_TARGET_RULE` (SPENTO): un intercettore ferma un colpo solo se il suo dominio ('land' | 'naval') e' fra
      #     gli `intercept_domains` della ShotSpec (None = non dichiarato: nessun vincolo). Letto all'inizio di ogni run.
      #     Spento: nessun filtro, come prima. Nessuna estrazione in piu' ne' in ordine diverso in nessuno dei due stati.
      BI_AD_TARGET_RULE = False

- `ShotSpec`: campo nuovo **in coda** `intercept_domains: Optional[FrozenSet[str]] = None` (docstring: domini AD che
  possono considerare il colpo un bersaglio; None = non dichiarato). `__post_init__`: None oppure frozenset di stringhe
  in `{'land','naval'}`, altrimenti `ValueError`. Il campo e' in coda: le costruzioni posizionali esistenti non cambiano.
- `_EngagementRun.__init__`: `self.ad_target_rule = BI_AD_TARGET_RULE`.
- `_ad_domain(self, shadow) -> str`: `'naval'` se `validate_class(shadow.asset, 'Ship')`, altrimenti `'land'`
  (memoizzato per id come `zone_cache`).
- `_admissible(self, shadow, salvo) -> bool`: True se `not self.ad_target_rule` o `salvo.spec.intercept_domains is None`;
  altrimenti `self._ad_domain(shadow) in salvo.spec.intercept_domains`.
- `_on_resolve`: (i) `:3350` diventa
  `if free <= 0 or not self._admissible(shadow, salvo) or not self._may_intercept(shadow, salvo) or not self._in_time(shadow, salvo):`
  (il filtro prima di L1/R-INT); (ii) `:3291`: con `self.ad_target_rule` acceso si contano solo le salve con
  `interceptable` e `intercept_domains` None o non vuoto; spento come oggi.
- Docstring del modulo, punto 4 della catena (`:32-55`): una frase sulla regola e l'interruttore.

#### 5.3.3 Effetti sui chiamanti [V sulle ricerche del 2026-11-07]
- `ShotSpec(` e' costruita in produzione solo da `Logic/Fire_Control.py:786`; nei test in 8 file (§1.2 e ricerca:
  `Test_Session_Scenarios_S25.py`, `Test_Aircraft.py`, `Test_Session_Rng.py`, `Scenario_Fixtures.py`,
  `Test_Engagement_Resolver.py`, `Test_Session_Types.py`, `Test_Fire_Control.py`, `Test_Session_Simulator.py`): tutte
  per nome di campo, nessuna da cambiare (campo nuovo con default).
- `restrict_by_policy` (`Logic/Fire_Control.py`, F7a) filtra le opzioni senza ricostruirle: da verificare dall'esecutore
  che non usi `dataclasses.replace` con un elenco di campi esplicito (se si', riferire).
- `Area_Fire` non usa `ShotSpec` per l'intercettazione (nessuna intercettazione nel fuoco su posizione,
  `Manuale_Motore_DES/10_Limiti_Estensioni_Divergenze.md:502`).
- Fotografia: `Scenario_Baseline.summarize_run` non registra le `ShotSpec`: nessuna voce nuova.
- Adapter DCS: nessun riferimento.

#### 5.3.4 Vincoli
- RNG: nessuna estrazione nuova; a interruttore spento il codice percorso e' identico salvo la chiamata a `_admissible`
  che restituisce True senza effetti.
- Nessuna costante tarata: le tre tabelle di 5.3.1 sono scelte di progetto [S] dichiarate nel commento.
- Nomi stabili: nessuna unita' o variante della fotografia toccata in questo blocco.

#### 5.3.5 Test del blocco 2 (circa 21; eseguito: 28)
`Test/Test_Fire_Control.py` (circa 10, nuova classe `TestInterceptDomains`):
1. AGM-65D (A-10C contro BMP-2) -> `intercept_domains == frozenset()` (tactical, flag fisso False);
1bis. AGM-65D (A-10C contro un Arleigh Burke, uso A2S) -> `frozenset()`: il Maverick non e' bersaglio nemmeno delle
   difese navali (decisione BI-6); stesso esito per AGM-65K;
2. Kh-55 e Kh-101 -> `{'land','naval'}`; 3. Kh-59 -> `{'land','naval'}` (BI-2 (a));
4. AGM-84A -> `{'naval'}`; 5. AGM-88 -> `frozenset()`;
6. RGM-84-Harpoon da nave -> `{'naval'}`; BGM-109-Tomahawk -> `{'land','naval'}`;
7. GBU-12 e Mk-82 -> `frozenset()`; razzo Hydra-70 e cannone GAU-8/A -> `frozenset()`;
8. SAM 9M38 contro un aereo e AAM -> `frozenset()`; ATGM 9M35 Kornet -> `frozenset()`;
9. `interceptable` invariato su tutti i casi precedenti (stessi valori dei test esistenti `:205`, `:226`, `:304`, `:492`).

`Test/Test_Engagement_Resolver.py` (circa 9, nuova classe `TestAirDefenceTargetRule`, stub come
`TestLauncherInsideInterceptionZone` `:1664`, tempi di volo realistici come `TestInterceptionReaction` `:1741`):
1. interruttore spento, `intercept_domains=frozenset()`: il colpo e' fermato come oggi;
2. acceso, `frozenset()`: nessuna intercettazione, nessun `InterceptionEvent`, tutti i colpi al danno;
3. acceso, `{'naval'}`, intercettore stub non nave: non fermato; intercettore `Ship`: fermato;
4. acceso, `{'land','naval'}`: fermato da entrambi;
5. acceso, `intercept_domains=None`: fermato come oggi (BI-8 (a));
6. acceso: L1 e R-INT si applicano ancora ai colpi ammessi (lancio dentro V_I non fermato);
7. acceso: stesso numero di estrazioni RNG (contatore sul `rng` come nei test R-INT esistenti) quando nessun colpo
   ammesso cambia;
8. acceso: `SalvoResolution.interceptable_rounds` esclude i colpi con domini vuoti;
9. `ShotSpec(intercept_domains={'air'})` -> `ValueError`; `frozenset({'land'})` accettato.

`Test/Test_Session_Simulator.py` o un test di sessione (circa 2): con la fire control dei registri e l'interruttore
acceso, nessun `InterceptionEvent` da un Tor contro AGM-65D in una sessione minima; spento, almeno uno.

#### 5.3.6 Esito atteso del blocco 2
- Suite: base + circa 21 test, tutti OK (numero esatto dall'ESITO). (Eseguito: 28; 4801 -> 4829.)
- Confronto con la fotografia: **1009 identiche** (interruttore spento); le esecuzioni nuove gia' presenti fuori dalla
  fotografia (S32-DWELL, ed eventualmente S33) identiche a prima.
- **Sonda B-1** (`probe_switch_on.py`, da scrivere dall'esecutore sul modello di
  `Rapporti/Sonde_Finestre_Passaggio/probe_switch_on.py`, solo dopo il blocco 2): accende `BI_AD_TARGET_RULE` in memoria
  e riesegue il confronto. Atteso: cambiano **esattamente** le 6 esecuzioni `CHANGED[unmodelled_as_before]` di B-0
  (`S19AD/S19-<0..5>/tor_rear`, §1.8), nessun'altra; in ciascuna, zero `InterceptionEvent` del Tor e piu' colpi al danno.
  Le 351 intercettazioni antinave di S6/S16 restano identiche. Una differenza fuori elenco = fermarsi e riferire.

### 5.4 Blocco 3 — scenario S35-ADTGT (esecutore `oc-developer`, branch `ai/oc-bi-blocco3`)

**Riferimenti riverificati il 2026-11-08** sul checkout dopo il merge `4803424b` (blocchi 0-2 eseguiti), HEAD `dd07fd16`
(il codice del motore e dei test e' quello di `c69ff954`: i commit successivi toccano solo documenti e memoria):
[V] = letto o eseguito in quella data. Le decisioni dell'utente sui punti P-1..P-7 sono in §5.4.1; la sonda **S-e**
(file di test definitivo di §5.4.3 eseguito dall'analista **fuori dal repo**, da una cartella temporanea, sul checkout
attuale) ne misura l'esito: **15 test OK, 32 sessioni (8 per seed), cattura simulata della fotografia con 32 chiavi
corrette e nessun errore** [V].

**Che cosa scrive il blocco 3** (e nient'altro):
1. `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S35.py`, **nuovo**, con il contenuto **esatto** di
   §5.4.3 (da copiare tale e quale: e' gia' stato eseguito, non va riprogettato);
2. `Code/Dynamic_War_Manager/Source/Test/Scenario_Baseline.py`: una riga di commento e una tupla in coda a `UNITS` e
   una sezione di docstring, testo esatto in §5.4.4;
3. il rapporto `Analysis/Document/Rapporti/Rapporto_BI_blocco3_oc-developer.md` (modello `Rapporti/TEMPLATE.md`).

Il blocco 3 **non** tocca il motore ne' i registri: nessun interruttore nuovo (usa `BI_AD_TARGET_RULE`, default `False`
invariato), nessuna estrazione RNG aggiunta o riordinata, nessuna costante del motore. Unica costante nuova: il sensore
`sea` di 20 km dell'A-10C, **VALORE DI TEST [S]** dichiarato nel test (P-2), non un dato. Il core resta indifferente al
simulatore (nessun import dell'adapter DCS).

Nome: **S35**, non S34: `S34-BAND` e `Test/Test_Session_Scenarios_S34.py` sono gia' nel piano della Proposta VA
(`Proposta_Allineamento_Volumi_DES_Pianificatore.md` §4.2), S33-PASSES in quello della FP. Se uno dei due non verra'
eseguito, il numero resta comunque S35 (nomi stabili, nessun riuso). Oggi nessuno dei tre file di test esiste [V].

#### 5.4.1 Decisioni del 2026-11-08 (ex punti aperti)

Evidenza: sonde di sola lettura del 2026-11-08 sul ProArt, con il motore del checkout (script nella cartella temporanea
della sessione, non nel repo; nessun file del repo modificato). Le sonde S-a..S-d sono quelle che hanno portato alle
decisioni; la S-e misura il file definitivo.
- **S-a** [V] (`land_tactical`, la chiamata di S19AD `:144`, session_id `S35-ADTGT-0..3`): spento 14 AGM-65D lanciati, 6
  intercettazioni del Tor, 3 BMP-2 distrutti in ogni seed; acceso 8 AGM-65D, 0 intercettazioni, 3 BMP-2 distrutti in ogni
  seed; perdite Blue spento 1/1/0/1, acceso 2/4/4/3; Tor distrutto in tutti gli 8 casi.
- **S-b** [V] (`land_cruise`, seed `P-0`): 2 Su-34 'Anti-Ship' da (-150 km, 0, 6000 m), rotta fino a x = -60 km e
  ritorno, missione Strike, `weapons=('Kh-59',)`, bersaglio un `Oil_Tank` (`category='Farp'`) in (0, 0) ristretto con
  `Target.asset_ids` e ROE `only_designated`, Buk a 1 km dal deposito nella stessa forza: spento e acceso identici, 4
  Kh-59 lanciati, 2 intercettazioni.
- **S-c** [V] (navale con l'Arleigh Burke, nave a x = 60 km, seed `P-0`): F/A-18C 'Anti-Ship', missione Anti_Ship: 2
  AGM-84A lanciati, **0 intercettazioni** spento e acceso (regola L1: V_I del Burke 240 km); A-10C, missione CAS:
  **nessun** Maverick lanciato (anche con un sensore `sea` dichiarato di 20 km), la nave spara ESSM.
- **S-d** [V] (navale con la `'FF 1135M Rezky'`, nave a x = 60 km, prefisso `ddg`, seed `P-0`): F/A-18C: 4 AGM-84A, 4
  intercettazioni spento e acceso (identici); A-10C con sensore `sea` dichiarato di 20 km: spento 4 AGM-65D e 2
  intercettazioni, acceso 2 AGM-65D e 0 intercettazioni, un colpo al danno sulla nave; A-10C senza sensore dichiarato:
  nessun lancio.
- **S-e** [V] (file definitivo di §5.4.3, seed `S35-ADTGT-0..3`, nave con prefisso `ff`): stessi numeri di S-a, S-b e
  S-d **in ogni seed**; dettaglio e distanze di lancio nella tabella "Misure della sonda S-e" in §5.4.3.
- V_I delle navi con un'arma `Anti_Missile` (`Mobile.air_defense_volume`, `Asset/Mobile.py:1396`: per le navi contano
  solo le `MISSILES_SAM`) [V, sonda]: Arleigh Burke IIa e CG-65 240 km; Type 052C 200 km; Moskva, Piotr Velikiy,
  Kuznetsov 150 km; FFG-46 74 km; Type 054A 70 km; CVN-70..75 50 km; Forrestal e Tarawa 19 km; Neustrashimy 15 km;
  Type 052B e Type 071 13 km; Rezky, Grisha, Molniya 12 km.

Decisioni:
- **P-1 — Nave delle varianti navali. DECISA dall'utente il 2026-11-08: (a)** la `'FF 1135M Rezky'` per **entrambe**
  le varianti navali (`naval_*` con AGM-84A e `naval_maverick_*`), al posto dell'Arleigh Burke; i nomi delle varianti
  non cambiano. Fatti [V]: `Asset/Ship_Data.py:1095-1135` (modello `:1098`; armi `:1114-1120`: `MISSILES_SAM`
  `SA-N-4-Gecko`, `CIWS` `AK-630`); `SA-N-4-Gecko` portata 12 km, quote 10-6000 m, task `['Anti_Air']`
  (`Asset/Ship_Weapon_Data.py:1123-1137`) -> V_I raggio 12 000 m, fascia relativa 10-6000 m [V, sonda S-e:
  `_interception_zone` = (12000.0, 10.0, 6000.0)]; `AK-630` task `['Anti_Missile', 'Anti_Air']`
  (`Asset/Ship_Weapon_Data.py:1571-1585`): e' l'unico intercettore (regola D). Lanci misurati in S-e: AGM-84A a 49,9 e
  23,3 km dalla nave, Maverick al primo lancio a 14,7 km (12,2 km nel seed 2), tutti **fuori** dai 12 km; il secondo
  lancio di Maverick in `naval_maverick_off` parte da dentro (11,05 km; 8,6 km nel seed 2) e non e' intercettabile (L1):
  le 2 intercettazioni sono quelle della prima salva. *Motivo*: unica scelta che rende possibili le asserzioni 6, 7 e 10
  con lanci da aereo e una sola nave. *Scartate*: (b) due navi diverse (piu' parti mobili, nessun vantaggio misurato);
  (c) tenere il Burke cambiando le attese (le varianti navali non mostrerebbero piu' la regola); (d) lancio sotto i 15 m
  della base del V_I (artificioso). **L1 non cambia in questo blocco**: e' una decisione dell'utente del 2026-09-28
  (`Proposta_Regole_Allocazione_SAM.md` §7.7 `:413`, Q2 `:417`) che l'utente rivedra' in una Proposta separata; se L1
  cambiera', S35 (con S19AD) andra' rivisto insieme alla fotografia.
- **P-2 — Sensore `sea` dell'A-10C. DECISA dall'utente il 2026-11-08: (a)** sensore dichiarato nello scenario,
  `F.Unit(..., sensors={'sea': DECLARED_SEA_RANGE_M})` con `DECLARED_SEA_RANGE_M = 20_000.0`, come `VISUAL` di S19AD
  (`Test/Test_Session_Scenarios_S19_Air_Defence.py:49`); costante dichiarata **VALORE DI TEST [S]** nel codice e nel
  rapporto (non e' un dato dell'A-10C; il numero non entra nelle asserzioni). Fatti [V]: `declare_sensor`
  (`Test/Scenario_Fixtures.py:271-303`) accetta i modi di `DETECTION_MODES = ('ground', 'air', 'sea')`
  (`Asset/Mobile.py:82`); `Unit.sensors` `Test/Scenario_Fixtures.py:504`. *Motivo*: il registro dell'A-10C non ha
  sensore marittimo (`detection_range('sea')` None) e senza sensore l'A-10C non lancia (S-d). *Scartata*: (b) un altro
  aereo con Maverick e sensore marittimo a registro (non cercato; cambierebbe il lanciatore del caso BI-6).
- **P-3 — Asserzione 2. DECISA dall'utente il 2026-11-08: (a)** "in `land_tactical_on` si lanciano **meno** AGM-65D che
  in `land_tactical_off`, **per seme**" (S-a ed S-e: 14 -> 8 in ogni seed). *Motivo*: e' l'effetto diretto della regola
  (nessun Maverick e' piu' fermato, ne servono meno); "piu' danni ai BMP" e' falsa (3 BMP-2 distrutti in tutti i casi).
  *Scartate*: (b) BMP distrutti `_on` >= `_off` (vera ma vacua: uguaglianza); (c) perdite Blue `_on` >= `_off` (non
  effetto diretto); (d) geometria nuova con meno attaccanti (da misurare). **Regola di fermata**: se in un seed
  l'asserzione non regge, l'esecutore si ferma e riferisce i numeri per seed (Maverick lanciati spento/acceso), **senza**
  cambiare l'asserzione.
- **P-4 — Numero di test. DECISA dall'utente il 2026-11-08: (b)** 15 test = 12 asserzioni + 3 premesse non vacue (in
  ogni variante interessata si lanciano AGM-65D, Kh-59, AGM-84A), sul modello di `test_mavericks_are_launched` di S19AD
  (`:148-154`). `Ran` atteso della suite: 4829 + 15 = **4844** (B + 49 con B = 4795 di §6.1) [V sulla sonda S-e per i 15
  test; il totale della suite si legge dall'ESITO]. Elenco dei 15 metodi in §5.4.3. *Motivo*: premesse esplicite (un
  test "0 intercettazioni" e' vacuo se non parte nessun colpo), coerente con §6.1. *Scartate*: (a) 12 test senza
  premesse; (c) numero libero all'esecutore.
- **P-5 — Costruzione di `land_cruise`. DECISA dall'utente il 2026-11-08: (a)** la configurazione della sonda S-b,
  scritta per intero in `build_land_cruise` (§5.4.3): forza `Red-Depot` (`F.make_force`, `GROUND_UNIT` di default) con
  `Red-Depot/tank0` = `make_structure(..., (0, 0), category='Farp', asset_type='Oil_Tank')` e `Red-Depot/sam0` =
  `make_vehicle(..., '9K37-Buk', (1000, 0))`; forza `Blue-STR` di 2 Su-34 `loadout='Anti-Ship'` (2 Kh-59 + 2 R-73,
  `Asset/Aircraft_Loadouts.py:3417-3431`) da (-150 km, 0, 6000 m), passo (0, 500 m), prefisso `str`; rotta
  `[(-60 km, 0), (-150 km, 0)]`; missione `Strike`, `weapons=('Kh-59',)`, bersaglio `Target(GROUP 'Red-Depot',
  asset_ids=('Red-Depot/tank0',))`, ROE `only_designated`. Esito [V, S-b ed S-e]: 4 Kh-59 e 2 intercettazioni del Buk,
  identici spento e acceso, in ogni seed; lancio a 90,8 km dal Buk (fuori dal V_I di 35 km). *Motivo*: configurazione
  gia' misurata, nessuna scelta lasciata all'esecutore. *Scartata*: (b) costruzione libera entro i vincoli.
- **P-6 — Per seme o in totale, e asserzione 11. DECISA dall'utente il 2026-11-08**: asserzioni 3 e 4 **per seme**;
  asserzione 9 sul **totale** dei 4 semi; asserzione 11 = **(b)**: `outcome.interception_events == ()` nelle sole
  varianti in cui tutte le salve offensive hanno domini vuoti (`land_tactical_on`, `naval_maverick_on`), per seme, come
  `TestS19AdTargetRule` (`:275`). Le asserzioni 1 e 8 erano gia' "in ogni seme"; 5 e 7 confrontano per seme. Per le
  asserzioni 6 e 10, rese possibili da P-1 e non coperte dal testo della decisione, il piano applica la stessa logica
  (scelta di coerenza dell'analista, segnalata all'utente): **6 per seme** (come la 4: un missile ammesso fermato da una
  difesa), **10 sul totale** (come la 9: stessa geometria Maverick-nave, e nel seed 2 il primo lancio e' a soli ~200 m
  fuori dal V_I); entrambe reggono comunque in ogni seed [V, S-e]. **Regola di fermata**: se la 3 o la 4 non reggono in
  un seed, fermarsi e riferire i numeri per seed. *Motivo*: le asserzioni "positive" sul caso ammesso valgono in ogni
  seed misurato; il totale solo dove l'evento e' raro. *Scartata* per la 11: (a) spia sugli `EngagementResult` (fallisce
  con gruppi di armi miste e aggiunge codice).
- **P-7 — Nomi dei seed. DECISA dall'utente il 2026-11-08**: `SEEDS = [f'S35-ADTGT-{index}' for index in range(4)]`
  (modello S32 `:45-46`), chiavi della fotografia `S35-ADTGT/S35-ADTGT-<i>/<variante>`. *Motivo*: nomi stabili gia'
  usati dalle sonde S-a ed S-e. *Scartate*: nessuna alternativa proposta.

#### 5.4.2 Riferimenti [V] e vincoli

**Cosa il blocco 3 usa dai blocchi 1-2** (esistono con questi nomi e firme [V]; il blocco 3 non li modifica):
- `Logic/Engagement_Resolver.py`: `BI_AD_TARGET_RULE = False` `:535` (commento `:531-534`); `AD_DOMAINS =
  frozenset({'land', 'naval'})` `:538`; `ShotSpec.intercept_domains: Optional[FrozenSet[str]] = None` `:635`
  (validazione `:668-671`); `_EngagementRun.__init__` copia l'interruttore in `self.ad_target_rule` `:1833`, quindi
  l'interruttore va sostituito **attorno all'intera sessione** (prima della costruzione del run), come fa
  `TestS19AdTargetRule` e come fa `run_variant` di §5.4.3; `_ad_domain(self, shadow) -> str` `:3189-3194`;
  `_admissible(self, shadow, salvo) -> bool` `:3196-3202`; `_may_intercept` (regola L1) `:3204-3227`; conteggio dei
  colpi intercettabili `:3333-3337`; filtro `:3396-3397`.
- `Logic/Fire_Control.py`: `AD_LAND, AD_NAVAL` `:293`, `AD_TARGET_DOMAINS` `:294`, `AD_SIZE_GATED_NAVAL` `:295`,
  `AD_DETECTABLE_DEFAULT` `:297`; `munition_class` `:761-796`; `intercept_domains_for` `:799-816`; `shot_spec_for`
  `:819-865`; `make_registry_fire_control(altitude_filter=True, memoize=True)` `:881`.
- Registri: AGM-65D `munition_class` `'tactical'`, `ad_detectable` False (`Asset/Aircraft_Weapon_Data.py:2546-2550`),
  portata 15 km; Kh-59 `'cruise'`, True (`:3477-3481`), portata 90 km; AGM-84A `'anti_ship'`, True (`:2256-2260`). Domini
  prodotti dalla fire control dei registri [V, sonda]: AGM-65D `frozenset()`, Kh-59 `{'land', 'naval'}`, AGM-84A
  `{'naval'}`.

**Cosa il file nuovo usa dal repo** (precondizione 5 di §5.0; controllo con `grep -n`, righe [V] su HEAD `dd07fd16`):

| Simbolo | Dove | Controllo |
|---|---|---|
| `MissionRules`, `Target`, `TargetKind`, `TargetProvenance` | `Command/Mission_Types.py:876`, `:455`, `:91`, `:101` | `grep -n "^class " .../Command/Mission_Types.py` |
| `Engagement_Resolver as ER`, `ER.BI_AD_TARGET_RULE` | `Logic/Engagement_Resolver.py:535` | `grep -n "^BI_AD_TARGET_RULE" ...` |
| `make_registry_fire_control` | `Logic/Fire_Control.py:881` | `grep -n "def make_registry_fire_control" ...` |
| `F.LoggerSilencer`, `F.Unit`, `F.build_force`, `F.make_force`, `F.add_assets`, `F.make_structure`, `F.make_vehicle`, `F.group_target`, `F.missions_for`, `F.run`, `F.AIR_UNIT`, `F.NAVAL_UNIT` | `Test/Scenario_Fixtures.py:216`, `:484-505`, `:508-536`, `:410`, `:425`, `:468-481`, `:350`, `:623`, `:710-715`, `:944-950`, `:256`, `:257` | `grep -n "^def \|^class \|^AIR_UNIT\|^NAVAL_UNIT" .../Scenario_Fixtures.py` |
| `BOTH_HOLD` | `Test/Test_Session_Scenarios_S10_S18.py:110` | `grep -n "^BOTH_HOLD" ...` |
| `DURATION`, `MAVERICK`, `OVERFLIGHT`, `TOR_REAR_X`, `run_variant(session_id, defence_model, defence_x, defence_y, attackers, points, targets_ifv_only=False, runner=F.run)` | `Test/Test_Session_Scenarios_S19_Air_Defence.py:51`, `:50`, `:55`, `:60`, `:81-99` | `grep -n "^DURATION\|^MAVERICK\|^OVERFLIGHT\|^TOR_REAR_X\|^def run_variant" ...` |
| modello `'FF 1135M Rezky'` | `Asset/Ship_Data.py:1098` | `grep -n "FF 1135M Rezky" .../Asset/Ship_Data.py` |
| modelli `'Su-34'` (loadout `'Anti-Ship'`), `'F/A-18C Hornet'` (`'Anti-Ship'`), `'A-10C Thunderbolt II'` (`'Maverick/Gun CAS'`) | `Asset/Aircraft_Loadouts.py:3380` e `:3417`, `:673`, `:1674` | `grep -n '"Anti-Ship"\|"Maverick/Gun CAS"' .../Aircraft_Loadouts.py` |
| modelli `'9K37-Buk'`, `'9K331-Tor'` | `Asset/Vehicle_Data.py:4472`, `:4297` | `grep -n "'9K37-Buk'\|'9K331-Tor'" .../Asset/Vehicle_Data.py` |

Il file nuovo importa da S19AD solo costanti e la funzione `run_variant` (rinominata `s19_run_variant`), **non** il
modulo ne' le sue classi: `unittest` non raccoglie due volte i test di S19AD.

**Vincoli dalla fotografia** [V]:
- `Scenario_Baseline.capture` registra OGNI `run_session` eseguita nel `setUpClass` dell'unita'
  (`Test/Scenario_Baseline.py:602-614` registratore, `:648-702` cattura) e la nomina per **occorrenza del session_id**
  nell'unita' (`_by_occurrence` `:227-232`; oltre l'ottava occorrenza il nome diventa `#8`, `#9`, ...). Quindi: per ogni
  seed **esattamente 8** sessioni con lo **stesso** `session_id`, nell'ordine dei nomi della riga `UNITS` (= ordine di
  `VARIANT_SPEC`); nessun'altra `run_session` nel `setUpClass`. La replica per il determinismo (asserzione 12) sta in un
  **metodo di test**: i metodi delle classi di scenario non sono eseguiti dalla fotografia (`:20-25`). Sonda S-e [V]:
  `run_session` chiamata 8 volte per ciascuno dei 4 seed; cattura simulata (unita' S35 sola, in memoria) -> 32 chiavi
  `S35-ADTGT/S35-ADTGT-<i>/<variante>`, nessuna `#`, `errors` vuoto.
- `verifica.sh confronto` usa `--summary --quiet` (`tools/ai/verifica.sh:26-28`): le righe `NEW` non sono stampate ne' nel
  log ne' nell'ESITO; il totale `difference lines` conta una riga per esecuzione NEW (`Test/Scenario_Baseline.py:801`,
  `:948`), quindi l'exit code del confronto e' **1** anche quando tutto e' come atteso. Formato verificato sull'ultimo
  confronto (`.ai-run/confronto.log` del 2026-11-08: `compared 1029 runs: 20 difference lines`; nella cattura
  `grep -cE '^  "S32-DWELL/' .ai-run/confronto_capture.json` -> `20`) [V].
- Politica d'armi F7a (`Context/Context.py:662-683`) [V]: il Kh-59 sul deposito richiede CAS, Strike o Pinpoint_Strike
  (si usa Strike); l'AGM-84A sulla nave richiede `Anti_Ship`; l'AGM-65D sulla nave e' ammesso con CAS (come S19AD).

#### 5.4.3 Il file di test (contenuto completo, da copiare)

Percorso: `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S35.py`. Contenuto esatto (274 righe; eseguito
dall'analista nella sonda S-e: `Ran 15 tests ... OK`, ~9 s):

```python
"""Scenario S35 del motore di sessioni virtuali: quali colpi una difesa aerea puo' considerare bersagli (BI).

Riproduzione di `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (blocco 3, decisioni BI-1..BI-12
del 2026-11-07 e P-1..P-7 del 2026-11-08). Con l'interruttore `Engagement_Resolver.BI_AD_TARGET_RULE` acceso un
intercettore ferma un colpo solo se il suo dominio ('land' | 'naval') e' fra gli `intercept_domains` della ShotSpec
(dichiarati dalla fire control dei registri); spento, nessun filtro, come prima. Esito QUALITATIVO (relazioni fra
varianti), mai un numero calibrato.

## S35-ADTGT (`TestS35AirDefenceTargets`)

Quattro geometrie, ciascuna con l'interruttore spento (`_off`) e acceso (`_on`), 4 seed (nomi stabili nella fotografia,
nell'ordine; stesso `session_id` per le 8 varianti di un seed). Fire control dei registri, `BOTH_HOLD`, 1800 s.

  * `land_tactical`: 4 A-10C con AGM-65D contro 3 BMP-2 e un Tor arretrato (V_I 12 km), la variante `tor_rear` di
    S19AD. Acceso: il Tor non ferma piu' i Maverick (classe 'tactical').
  * `land_cruise`: 2 Su-34 'Anti-Ship' con Kh-59 designato (missione Strike) contro un deposito `Oil_Tank` e un Buk a
    1 km (V_I 35 km). Il cruise resta bersaglio delle difese terrestri: acceso = spento.
  * `naval`: 2 F/A-18C 'Anti-Ship' con AGM-84A (missione Anti_Ship) contro una FF 1135M Rezky (V_I 12 km, AK-630 con
    task 'Anti_Missile'). L'antinave resta bersaglio delle difese navali: acceso = spento.
  * `naval_maverick`: 2 A-10C con AGM-65D designato (missione CAS, sensore `sea` dichiarato di test) contro la stessa
    Rezky. Acceso: la nave non ferma piu' i Maverick (`ad_detectable` fisso False).

La Rezky e non l'Arleigh Burke (decisione P-1 del 2026-11-08): con il V_I di 240 km del Burke la regola L1 vieta ogni
intercettazione dei lanci da aereo. Il sensore `sea` di 20 km dell'A-10C e' un VALORE DI TEST [S] (P-2), non un dato:
senza, l'A-10C non rileva la nave e non lancia.
"""

import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import MissionRules, Target, TargetKind, TargetProvenance
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18 import BOTH_HOLD
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S19_Air_Defence import (
    DURATION, MAVERICK, OVERFLIGHT, TOR_REAR_X, run_variant as s19_run_variant)

SEEDS_PER_SCENARIO = 4
SEEDS = [f'S35-ADTGT-{index}' for index in range(SEEDS_PER_SCENARIO)]
# variante -> (geometria, interruttore BI_AD_TARGET_RULE); l'ordine e' quello dei nomi nella riga di Scenario_Baseline.
VARIANT_SPEC = {
    'land_tactical_off': ('land_tactical', False),
    'land_tactical_on': ('land_tactical', True),
    'land_cruise_off': ('land_cruise', False),
    'land_cruise_on': ('land_cruise', True),
    'naval_off': ('naval', False),
    'naval_on': ('naval', True),
    'naval_maverick_off': ('naval_maverick', False),
    'naval_maverick_on': ('naval_maverick', True),
}
VARIANTS = tuple(VARIANT_SPEC)

KH59 = 'Kh-59'
HARPOON = 'AGM-84A'
TOR = 'Red-Line/ad0'            # Tor di S19AD (`build`, prefisso 'ad')
DEPOT_TANK = 'Red-Depot/tank0'
BUK = 'Red-Depot/sam0'
SHIP_MODEL = 'FF 1135M Rezky'   # V_I 12 km (SA-N-4), intercettore AK-630 (task 'Anti_Missile')
SHIP = 'Red-Navy/ff0'
SHIP_X = 60_000.0

# Sensore marittimo DICHIARATO DI TEST dell'A-10C [m]: VALORE DI TEST [S], non un dato del registro (che non ne ha);
# serve solo a far rilevare la nave entro la portata del Maverick (15 km). Non entra in nessuna asserzione.
DECLARED_SEA_RANGE_M = 20_000.0

# land_cruise: 2 Su-34 a 6000 m da x = -150 km, virata a x = -60 km e ritorno (lancio dei Kh-59 a ~90 km dal Buk,
# fuori dai suoi 35 km).
CRUISE_ORIGIN = (-150_000.0, 0.0, 6_000.0)
CRUISE_POINTS = [(-60_000.0, 0.0), (-150_000.0, 0.0)]
# naval / naval_maverick: partenza a x = -40 km, 3000 m, sorvolo della nave fino a x = +80 km.
NAVAL_ORIGIN = (-40_000.0, 0.0, 3_000.0)
NAVAL_POINTS = [(SHIP_X + 20_000.0, 0.0)]


def build_land_cruise(session_id: str):
    """`land_cruise`: Su-34 con Kh-59 contro un deposito difeso da un Buk della stessa forza.

    Bersaglio ristretto al deposito (`Target.asset_ids`) con ROE `only_designated`: i Su-34 non attaccano il Buk.
    Restituisce `(deposito, attaccanti, outcome)`.
    """
    depot = F.make_force('Red-Depot', 'Red')
    F.add_assets(depot, [
        F.make_structure(depot, DEPOT_TANK, (0.0, 0.0), category='Farp', asset_type='Oil_Tank'),
        F.make_vehicle(depot, BUK, '9K37-Buk', (1_000.0, 0.0))])
    strike = F.build_force('Blue-STR', 'Blue', [
        F.Unit('aircraft', 'Su-34', 2, origin=CRUISE_ORIGIN, step=(0.0, 500.0), prefix='str',
               loadout='Anti-Ship')], mil_category=F.AIR_UNIT)
    target = Target(kind=TargetKind.GROUP, target_id='Red-Depot', asset_ids=(DEPOT_TANK,),
                    provenance=TargetProvenance.OBSERVED, observed_at=0.0)
    missions = F.missions_for(strike, CRUISE_POINTS, mission_type='Strike', target=target, weapons=(KH59,),
                              rules=MissionRules(roe='only_designated'))
    outcome = F.run(session_id, [strike], [depot], make_registry_fire_control(), duration=DURATION,
                    missions=missions, thresholds=BOTH_HOLD)
    return depot, strike, outcome


def build_naval(session_id: str, weapon: str):
    """`naval` (`weapon` = AGM-84A: 2 F/A-18C, missione Anti_Ship) o `naval_maverick` (`weapon` = AGM-65D: 2 A-10C
    con sensore `sea` dichiarato di test, missione CAS, arma designata) contro la Rezky. Restituisce
    `(nave, attaccanti, outcome)`."""
    navy = F.build_force('Red-Navy', 'Red', [
        F.Unit('ship', SHIP_MODEL, 1, origin=(SHIP_X, 0.0), prefix='ff')], mil_category=F.NAVAL_UNIT)

    if weapon == HARPOON:
        attackers = F.build_force('Blue-AS', 'Blue', [
            F.Unit('aircraft', 'F/A-18C Hornet', 2, origin=NAVAL_ORIGIN, step=(0.0, 500.0), prefix='as',
                   loadout='Anti-Ship')], mil_category=F.AIR_UNIT)
        missions = F.missions_for(attackers, NAVAL_POINTS, mission_type='Anti_Ship',
                                  target=F.group_target('Red-Navy'))
    else:
        attackers = F.build_force('Blue-CAS', 'Blue', [
            F.Unit('aircraft', 'A-10C Thunderbolt II', 2, origin=NAVAL_ORIGIN, step=(0.0, 500.0), prefix='cas',
                   loadout='Maverick/Gun CAS', sensors={'sea': DECLARED_SEA_RANGE_M})], mil_category=F.AIR_UNIT)
        missions = F.missions_for(attackers, NAVAL_POINTS, mission_type='CAS', target=F.group_target('Red-Navy'),
                                  weapons=(MAVERICK,))

    outcome = F.run(session_id, [attackers], [navy], make_registry_fire_control(), duration=DURATION,
                    missions=missions, thresholds=BOTH_HOLD)
    return navy, attackers, outcome


def run_variant(session_id: str, variant: str):
    """Una sessione della variante: `(blocco difeso, attaccanti, outcome)`. L'interruttore e' sostituito attorno
    all'intera esecuzione (il run lo copia alla costruzione, `_EngagementRun.__init__`)."""
    geometry, switch = VARIANT_SPEC[variant]

    with patch.object(ER, 'BI_AD_TARGET_RULE', switch):
        if geometry == 'land_tactical':
            return s19_run_variant(session_id, '9K331-Tor', TOR_REAR_X, 300.0, 4, OVERFLIGHT)

        if geometry == 'land_cruise':
            return build_land_cruise(session_id)

        return build_naval(session_id, HARPOON if geometry == 'naval' else MAVERICK)


def _interceptions(outcome, asset_id: str) -> int:
    return sum(e.interceptions for e in outcome.interception_events if e.asset_id == asset_id)


def _launched(outcome, weapon: str) -> int:
    return sum(e.rounds for e in outcome.ammunition_events if e.weapon == weapon)


def _events(outcome):
    """Munizioni, danni e intercettazioni con i loro istanti: la storia confrontata fra varianti e repliche."""
    return ([(e.time, e.asset_id, e.weapon, e.rounds) for e in outcome.ammunition_events],
            [(e.time, e.target_id, e.source_id, e.weapon, e.outcome, e.health_after) for e in outcome.damage_events],
            [(e.time, e.asset_id, e.interceptions, e.force_id, e.weapon) for e in outcome.interception_events])


class TestS35AirDefenceTargets(F.LoggerSilencer, unittest.TestCase):
    """S35-ADTGT: con la regola BI accesa una difesa ferma solo i colpi del proprio dominio."""

    SEEDS = SEEDS
    VARIANTS = VARIANTS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        # Ciclo esterno sui seed, interno sulle varianti: stesso `session_id` per le 8 varianti di un seed
        # (la fotografia numera le esecuzioni per occorrenza del session_id nell'unita'). Nessun'altra sessione qui.
        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(run_variant(session_id, variant))

    def _outcomes(self, variant: str):
        return [outcome for _, _, outcome in self.runs[variant]]

    # ── premesse non vacue (P-4 (b)) ──

    def test_premise_mavericks_are_launched(self):
        """Premessa: gli AGM-65D sono lanciati in ogni variante che li usa (totale sui seed)."""
        for variant in ('land_tactical_off', 'land_tactical_on', 'naval_maverick_off', 'naval_maverick_on'):
            with self.subTest(variant=variant):
                self.assertGreater(sum(_launched(o, MAVERICK) for o in self._outcomes(variant)), 0)

    def test_premise_kh59_are_launched(self):
        """Premessa: i Kh-59 sono lanciati in `land_cruise_off/_on` (totale sui seed)."""
        for variant in ('land_cruise_off', 'land_cruise_on'):
            with self.subTest(variant=variant):
                self.assertGreater(sum(_launched(o, KH59) for o in self._outcomes(variant)), 0)

    def test_premise_harpoons_are_launched(self):
        """Premessa: gli AGM-84A sono lanciati in `naval_off/_on` (totale sui seed)."""
        for variant in ('naval_off', 'naval_on'):
            with self.subTest(variant=variant):
                self.assertGreater(sum(_launched(o, HARPOON) for o in self._outcomes(variant)), 0)

    # ── asserzioni 1-12 ──

    def test_land_tactical_on_the_tor_never_intercepts(self):
        """1. Acceso: il Tor (difesa terrestre) non ferma gli AGM-65D (classe 'tactical'), in ogni seed."""
        for seed, outcome in zip(self.SEEDS, self._outcomes('land_tactical_on')):
            with self.subTest(session=seed):
                self.assertEqual(_interceptions(outcome, TOR), 0)

    def test_land_tactical_on_launches_fewer_mavericks(self):
        """2. Acceso si lanciano MENO AGM-65D che spento, per seed (nessuno e' piu' fermato: ne servono meno)."""
        for seed, off, on in zip(self.SEEDS, self._outcomes('land_tactical_off'), self._outcomes('land_tactical_on')):
            with self.subTest(session=seed):
                self.assertLess(_launched(on, MAVERICK), _launched(off, MAVERICK))

    def test_land_tactical_off_the_tor_intercepts(self):
        """3. Spento: il Tor ferma AGM-65D (comportamento precedente, come S19AD `tor_rear`), in ogni seed."""
        for seed, outcome in zip(self.SEEDS, self._outcomes('land_tactical_off')):
            with self.subTest(session=seed):
                self.assertGreater(_interceptions(outcome, TOR), 0)

    def test_land_cruise_on_the_buk_intercepts_the_kh59(self):
        """4. Acceso: il Buk ferma i Kh-59 (classe 'cruise', bersaglio di ogni difesa), in ogni seed."""
        for seed, outcome in zip(self.SEEDS, self._outcomes('land_cruise_on')):
            with self.subTest(session=seed):
                self.assertGreater(_interceptions(outcome, BUK), 0)

    def test_land_cruise_switch_changes_nothing(self):
        """5. Il cruise e' ammesso in entrambi gli stati: stessa storia (munizioni, danni, intercettazioni),
        per seed."""
        for seed, off, on in zip(self.SEEDS, self._outcomes('land_cruise_off'), self._outcomes('land_cruise_on')):
            with self.subTest(session=seed):
                self.assertEqual(_events(on), _events(off))

    def test_naval_on_the_ship_intercepts_the_harpoons(self):
        """6. Acceso: la Rezky ferma gli AGM-84A (classe 'anti_ship', bersaglio navale), in ogni seed."""
        for seed, outcome in zip(self.SEEDS, self._outcomes('naval_on')):
            with self.subTest(session=seed):
                self.assertGreater(_interceptions(outcome, SHIP), 0)

    def test_naval_switch_changes_nothing(self):
        """7. L'antinave e' ammesso in entrambi gli stati: stessa storia, per seed."""
        for seed, off, on in zip(self.SEEDS, self._outcomes('naval_off'), self._outcomes('naval_on')):
            with self.subTest(session=seed):
                self.assertEqual(_events(on), _events(off))

    def test_naval_maverick_on_the_ship_never_intercepts(self):
        """8. Acceso: la nave non ferma gli AGM-65D (Maverick fisso `ad_detectable` False, BI-6), in ogni seed."""
        for seed, outcome in zip(self.SEEDS, self._outcomes('naval_maverick_on')):
            with self.subTest(session=seed):
                self.assertEqual(_interceptions(outcome, SHIP), 0)

    def test_naval_maverick_on_hits_reach_the_ship(self):
        """9. Acceso: almeno un AGM-65D arriva al danno sulla nave (totale sui seed)."""
        hits = sum(1 for outcome in self._outcomes('naval_maverick_on') for e in outcome.damage_events
                   if e.target_id == SHIP and e.weapon == MAVERICK)
        self.assertGreater(hits, 0)

    def test_naval_maverick_off_the_ship_intercepts(self):
        """10. Spento: la nave ferma AGM-65D (comportamento precedente: e' la differenza che la variante mostra),
        totale sui seed."""
        self.assertGreater(sum(_interceptions(o, SHIP) for o in self._outcomes('naval_maverick_off')), 0)

    def test_on_variants_with_excluded_shots_have_no_interception_event(self):
        """11. Nelle varianti accese in cui tutte le salve offensive hanno domini vuoti nessun InterceptionEvent
        (come TestS19AdTargetRule), per seed."""
        for variant in ('land_tactical_on', 'naval_maverick_on'):
            for seed, outcome in zip(self.SEEDS, self._outcomes(variant)):
                with self.subTest(variant=variant, session=seed):
                    self.assertEqual(outcome.interception_events, ())

    def test_runs_are_deterministic(self):
        """12. Determinismo: ogni variante di ogni seed, rieseguita, ripete la stessa storia. In un metodo di test,
        non in `setUpClass`: la fotografia esegue solo `setUpClass` e non deve vedere le repliche."""
        for index, seed in enumerate(self.SEEDS):
            for variant in self.VARIANTS:
                with self.subTest(variant=variant, session=seed):
                    _, _, replica = run_variant(seed, variant)
                    self.assertEqual(_events(replica), _events(self.runs[variant][index][2]))


if __name__ == '__main__':
    unittest.main()
```

**I 15 test** (nomi dei metodi; "asserzione n" = numerazione storica del piano; misure [V] dalla sonda S-e):

| # | Metodo | Asserzione | Atteso (corpo) | Granularita' | Misura S-e |
|---|---|---|---|---|---|
| 1 | `test_premise_mavericks_are_launched` | premessa | AGM-65D lanciati > 0 in `land_tactical_off`, `land_tactical_on`, `naval_maverick_off`, `naval_maverick_on` | totale per variante (subTest) | 56 / 32 / 16 / 8 |
| 2 | `test_premise_kh59_are_launched` | premessa | Kh-59 lanciati > 0 in `land_cruise_off`, `land_cruise_on` | totale per variante | 16 / 16 |
| 3 | `test_premise_harpoons_are_launched` | premessa | AGM-84A lanciati > 0 in `naval_off`, `naval_on` | totale per variante | 16 / 16 |
| 4 | `test_land_tactical_on_the_tor_never_intercepts` | 1 | intercettazioni del Tor (`Red-Line/ad0`) == 0 in `land_tactical_on` | per seme | 0 in ogni seed |
| 5 | `test_land_tactical_on_launches_fewer_mavericks` | 2 (P-3) | AGM-65D lanciati `_on` < `_off` | per seme | 8 < 14 in ogni seed |
| 6 | `test_land_tactical_off_the_tor_intercepts` | 3 | intercettazioni del Tor > 0 in `land_tactical_off` | per seme | 6 in ogni seed |
| 7 | `test_land_cruise_on_the_buk_intercepts_the_kh59` | 4 | intercettazioni del Buk (`Red-Depot/sam0`) > 0 in `land_cruise_on` | per seme | 2 in ogni seed |
| 8 | `test_land_cruise_switch_changes_nothing` | 5 | `_events(on) == _events(off)` (munizioni, danni, intercettazioni con istanti) | per seme | identici |
| 9 | `test_naval_on_the_ship_intercepts_the_harpoons` | 6 | intercettazioni della nave (`Red-Navy/ff0`) > 0 in `naval_on` | per seme | 4 in ogni seed (AK-630) |
| 10 | `test_naval_switch_changes_nothing` | 7 | `_events(on) == _events(off)` per `naval` | per seme | identici |
| 11 | `test_naval_maverick_on_the_ship_never_intercepts` | 8 | intercettazioni della nave == 0 in `naval_maverick_on` | per seme | 0 in ogni seed |
| 12 | `test_naval_maverick_on_hits_reach_the_ship` | 9 | `DamageEvent` sulla nave con `weapon == 'AGM-65D'` > 0 in `naval_maverick_on` | totale sui 4 semi | 4 (1 per seed, esito `kill`) |
| 13 | `test_naval_maverick_off_the_ship_intercepts` | 10 | intercettazioni della nave > 0 in `naval_maverick_off` | totale sui 4 semi | 8 (2 per seed) |
| 14 | `test_on_variants_with_excluded_shots_have_no_interception_event` | 11 (P-6 (b)) | `outcome.interception_events == ()` in `land_tactical_on` e `naval_maverick_on` | per seme | `()` in ogni seed |
| 15 | `test_runs_are_deterministic` | 12 | per ogni seed e variante, `run_variant` rieseguita da' gli stessi `_events` della corsa del `setUpClass` | per seme e variante | identici (32 repliche) |

Totale: 3 premesse + 12 asserzioni = **15** metodi, coerente con P-4 e con la riga "BI blocco 3" di §6.1 (B + 49 =
4795 + 49 = 4829 + 15 = **4844**).

**Misure della sonda S-e** [V] (file di §5.4.3, seed `S35-ADTGT-0..3`; "per seed" = uguale nei 4 seed salvo dove
indicato):

| Variante | Lanciati (per seed) | Intercettazioni (per seed) | Altro |
|---|---|---|---|
| `land_tactical_off` | 14 AGM-65D | Tor 6 (9M331) | lanci a ~17,7 km dal Tor (V_I 12 km); 3 BMP-2 e Tor distrutti |
| `land_tactical_on` | 8 AGM-65D | 0, `interception_events == ()` | 3 BMP-2 e Tor distrutti; il Tor spara 8 9M331 agli A-10C |
| `land_cruise_off` / `_on` | 4 Kh-59 (2 per Su-34) | Buk 2 (9M38), identiche | lancio a 90,8 km dal Buk (V_I 35 km), t = 228,1 s |
| `naval_off` / `_on` | 4 AGM-84A | Rezky 4 (AK-630), identiche | lanci a 49,9 e 23,3 km dalla nave (V_I 12 km) |
| `naval_maverick_off` | 4 AGM-65D | Rezky 2 (AK-630) | 1o lancio a 14,7 km (seed 2: 12,2 km), fuori; 2o a 11,05 km (seed 2: 8,6 km), dentro: non intercettabile (L1); 1 `kill` sulla nave |
| `naval_maverick_on` | 2 AGM-65D | 0, `interception_events == ()` | 1o lancio a 14,7 km (seed 2: 12,2 km); 1 `kill` sulla nave |

Le distanze di lancio sono quelle del risolutore (`_may_intercept`: posizione del lanciatore e dell'intercettore a
`t_launch`) e coincidono con la formula di S19AD (`launch_distances`, `:102-115`: x = x0 + v t sulla rotta rettilinea).
Il vincolo della decisione P-1 (lancio dei Maverick oltre i 12 km) e' quindi rispettato **in ogni seed**, ma nel seed 2
con un margine di ~200 m (§7).

#### 5.4.4 `Test/Scenario_Baseline.py`: riga di `UNITS` e docstring (testo esatto)

1. In `UNITS`, dopo la tupla di S32-DWELL (`:396-397`) e **prima** della `)` di chiusura (`:398`), queste quattro righe
   (indentazione di 4 spazi come le precedenti; formato della tupla `:263-265`, `None` = si esegue `setUpClass`):

```python
    # ── S35 (BI: bersagli intercettabili dalle difese aeree, BI_AD_TARGET_RULE) — in coda, nomi stabili ──
    ('S35-ADTGT', 'Test_Session_Scenarios_S35', 'TestS35AirDefenceTargets', None,
     _by_occurrence('land_tactical_off', 'land_tactical_on', 'land_cruise_off', 'land_cruise_on',
                    'naval_off', 'naval_on', 'naval_maverick_off', 'naval_maverick_on')),
```

2. Nella docstring del modulo, dopo la sezione `## Permanenza nel volume dopo la D-5` (`:176-181`) e prima di
   `## Uso (dalla root del repo, con l'interprete della macchina)` (`:183`), una riga vuota e questa sezione (stile di
   quella della D-5; nessun backslash, la docstring non e' raw):

```text
## Bersagli intercettabili dopo la BI

La BI (`Engagement_Resolver.BI_AD_TARGET_RULE`, SPENTO; `ShotSpec.intercept_domains` dichiarati dalla fire control
dei registri, `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`) non cambia le esecuzioni esistenti (interruttore
spento). Aggiunge in coda l'unita' S35-ADTGT (8 varianti, 4 seed): 32 esecuzioni nuove; nessuna voce nuova nel
riassunto.
```

Nomi stabili: unita' `S35-ADTGT`, classe `TestS35AirDefenceTargets`, varianti nell'ordine sopra, seed `S35-ADTGT-0..3`.
Asset: `Red-Line/ad0` (Tor) e `Blue-CAS/cas0..3` da S19AD; `Red-Depot/tank0`, `Red-Depot/sam0`, `Blue-STR/str0..1`;
`Red-Navy/ff0`, `Blue-AS/as0..1`, `Blue-CAS/cas0..1`.

#### 5.4.5 Esito atteso, verifiche e regole di fermata

Numeri da leggere nell'ESITO, mai stimati. `<python>` = l'interprete stampato da `verifica.sh` nell'ESITO (sul ProArt
`.direnv/python-3.12/bin/python3`).
- Compilazione: `<python> -c "import py_compile; py_compile.compile('Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S35.py', doraise=True)"`
  e lo stesso per `Scenario_Baseline.py`.
- Test singolo, dalla root del repo: `<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S35`
  -> `Ran 15 tests`, `OK` [V, sonda S-e].
- Suite (`bash tools/ai/verifica.sh suite start`, poi `... suite wait` fino a `ESITO`): `Ran 4844 tests`,
  `OK (skipped=7)` (base 4829 [V] + 15).
- Confronto, solo dopo la fine della suite (`bash tools/ai/verifica.sh confronto start`, poi `... confronto wait`):
  `UNCHANGED (1009)` e `compared 1061 runs: 52 difference lines` (1029 + 32 esecuzioni; 20 NEW S32-DWELL + 32 NEW
  S35-ADTGT = 52 righe, 0 DIFF), exit code **1** (atteso, v. §5.4.2). Poiche' 1009 + 52 = 1061, quei due numeri insieme
  escludono ogni DIFF. Controllo delle chiavi nuove sulla cattura salvata, con comandi consentiti a `oc-developer`:
  `grep -cE '^  "S35-ADTGT/' .ai-run/confronto_capture.json` -> `32`;
  `grep -E '^  "S35-ADTGT/' .ai-run/confronto_capture.json` -> solo chiavi `S35-ADTGT/S35-ADTGT-<i>/<variante>` con le 8
  varianti per ciascuno dei 4 seed, nessuna `#`; `grep -cE '^  "S32-DWELL/' .ai-run/confronto_capture.json` -> `20`.
- Esecuzioni identiche: le 1009 della fotografia (il blocco 3 non tocca il motore). Esecuzioni cambiate: nessuna.
  Esecuzioni nuove: 20 S32-DWELL (gia' fuori dalla fotografia) e 32 S35-ADTGT. Nessuna fotografia nuova si installa.
- Rapporto `Rapporti/Rapporto_BI_blocco3_oc-developer.md`: numeri letti dagli ESITI; la costante
  `DECLARED_SEA_RANGE_M = 20 000 m` dichiarata **VALORE DI TEST [S]**; scelte minori (nessuna attesa).

**Fermarsi e riferire** (senza cambiare asserzioni, geometrie, costanti o codice del motore; regola dei due fallimenti
dell'agente):
- un simbolo di §5.4.2 non esiste o ha un'altra firma (precondizioni 4-5 di §5.0);
- la **asserzione 2** (test 5) fallisce in un seed: riferire per seed i Maverick lanciati spento/acceso (P-3);
- la **3 o la 4** (test 6 e 7) falliscono in un seed: riferire per seed le intercettazioni del Tor/Buk (P-6);
- un'asserzione su una variante `_off` fallisce perche' la variante non produce lanci o intercettazioni, o un test
  qualunque fallisce: il file e' gia' stato eseguito con esito OK sul checkout `dd07fd16`, quindi un fallimento indica
  un codice diverso da quello misurato (riferire `git log --oneline -5` e il messaggio);
- `Ran` diverso da 4844 o `UNCHANGED` diverso da 1009, `compared` diverso da 1061 o righe diverse da 52; una chiave S35
  con `#` o un numero di chiavi S35 diverso da 32.

### 5.5 Blocco 4 — documenti (sessione principale e `des-manual-writer`)
(Righe dei documenti riverificate il 2026-11-08 [V].)
- `Manuale_Motore_DES/05_Strato2_Risolutore_Ingaggio.md`: tabella dei campi di `ShotSpec` (`:172-182`, ultima riga
  `stock_per_round` `:182`: aggiungere `intercept_domains`), campi derivati della fire control (sezione `:887`, punto
  `interceptable` `:900`), §4.24 (`:1612`; sottosezione nuova e nota sulla regola del 2026-09-28 ristretta), D24
  (didascalia `:1720`; nodo `_admissible`); atlante `11a_Atlante_Risolutore.md:1308` (riga di `ShotSpec` nella tabella
  dei simboli: campo nuovo).
- `10_Limiti_Estensioni_Divergenze.md`: classificazione stimata, nessun balistico a registro, dimensione binaria, R-INT
  senza RCS (`:282`); **limite BI-12 (a) [S]**: il criterio di dimensione vale solo per le difese navali, quindi
  Kh-29/Kh-58 (e ogni `tactical`/`arm`) non sono mai bersagli delle difese terrestri anche se di taglia simile al
  Kh-59, che lo e' perche' `cruise`.
- `F4_Differenze_Scenari.md`: esito di B-1 e sezione S35-ADTGT (32 esecuzioni nuove; nave Rezky e sensore `sea` di test
  dell'A-10C come costante stimata [S]; decisioni P-1..P-7 di §5.4.1; limite: S35 dipende da L1, da rivedere se L1
  cambia).
- `Proposta_Finestre_Per_Passaggio_Portata_Propria.md`: nessun intervento (voce superata: FP-5 decisa il 2026-11-08,
  opzione (d), e Proposta FP gia' riscritta; non c'e' piu' una riproposta di FP-5 dopo il blocco 3).
- `Piano_Implementazione_Missione.md` §5 (`:275`, "Stato di avanzamento e deviazioni dal piano"): riga di avanzamento.
- `Proposta_Dati_Anti_Missile.md` e `Proposta_Regole_Allocazione_SAM.md`: nota di rimando (la regola 2 del 2026-09-28 e'
  ristretta dalla BI).

---

## 6. Interazioni e ordine rispetto alle altre Proposte

| Proposta | Interazione | Ordine raccomandato |
|---|---|---|
| FP (finestre per passaggio) | FP-5 (istante di rilevamento per R-INT) perde il caso tipico: con R-BI accesa un A2G non e' piu' fermato da un SAM terrestre; R-INT resta per cruise/balistici e antinave (navali). L'opzione (d) di FP-5 (legata al passaggio) resta la coerente con FP-3 (a) ma diventa marginale. Il codice delle due regole e' disgiunto (FP: rilevamento e candidati; BI: filtro in `_on_resolve`); entrambe toccano `Logic/Engagement_Resolver.py` (conflitti di riga possibili, non di logica) | decisione BI-11: prima la BI, poi FP-5 riproposta (superata: FP-5 decisa il 2026-11-08, (d)); FP blocco 1 dopo la BI e la VA (§6.1) |
| D-5 (dwell) | nessuna: la D-5 non tocca R-INT (`Logic/Engagement_Resolver.py:163`, "nessun dwell sul tracciamento dei colpi") | indipendente |
| VA (sfera contro cilindro, decisioni prese) | VA cambia il volume d'ingaggio delle armi al lancio (fascia/tetto nel tempo, quote all'istante con `altitudes`), non L1 ne' R-INT; logica indipendente dalla BI, ma stessi file (`Engagement_Resolver.py`, `Fire_Control.py`, `ShotSpec`, `UNITS`) | **dopo la BI** (BI-11 e VA §2.8); conflitti di riga in §6.1 |
| Regole SAM / Dati Anti_Missile | la BI restringe la regola 2 del 2026-09-28; D, F, L1-L3 invariate | documenti aggiornati al blocco 4 |

Sonda B-0 e fotografia: B-0 dice che oggi la regola tocca solo il caso Maverick-Tor (§1.8); quindi l'accensione
futura del default richiederebbe una fotografia nuova solo per quelle esecuzioni, su decisione esplicita dell'utente.

### 6.1 Conflitti di file con VA e FP e ordine dei lavori (riallineata il 2026-11-07 alla Proposta VA decisa)

Stato delle altre Proposte [V sui documenti]: **VA** (`Proposta_Allineamento_Volumi_DES_Pianificatore.md`) ha tutte le
decisioni prese (VA-1 sfera ∩ fascia; VA-2 (d), filtro di quota ricalcolato alla quota dell'istante di tiro con la
keyword `altitudes` della fire control, rilevata per introspezione, e rinvio VA-2.1 (i); VA-3 (b) tetto assoluto
`max_target_z` per le armi d'aereo; VA-6 (a); VA-7 interruttore `VA_ENGAGEMENT_ALTITUDE_BAND`; scenario S34-BAND a 8
varianti) e fissa gia' l'ordine **BI -> VA** (VA §2.8, precondizione 2 di VA §4.0); **FP** ha tutte le decisioni
FP-1..FP-10 prese (FP-5 = (d), decisa il 2026-11-08: BI-11 superata) e la Proposta riscritta e riletta (commit
`8c440dba`), non ancora eseguita.

Punti di contatto [V sui piani scritti: VA §4.1.2-§4.1.4, §4.2, §6; FP §4.1-§4.2; BI blocchi 0-2 eseguiti e mergiati
(merge `4803424b`), BI blocchi 3-4, VA e FP non eseguiti; righe del codice ricontrollate il 2026-11-08 sul checkout
dopo il merge `4803424b`]:

| File / punto | BI | VA (volumi allineati) | FP (finestre per passaggio) | Come si compongono |
|---|---|---|---|---|
| `Logic/Engagement_Resolver.py`, interruttori dopo `D5_DWELL_TIME` (`:522-529`; `BI_AD_TARGET_RULE` gia' presente a `:531-535`) | `BI_AD_TARGET_RULE` | `VA_ENGAGEMENT_ALTITUDE_BAND`, subito dopo quello della BI (VA §4.1.2 punto 1) | `FP_PER_PASS_DETECTION` | in coda, nell'ordine di esecuzione |
| `ShotSpec` (`:599-671`), campi in coda | `intercept_domains` (dopo `stock_per_round`) | `min_altitude`, `max_altitude`, `max_target_z`, **in coda dopo `intercept_domains`** (VA §4.1.2 punto 2) | — | BI prima; validazioni nello stesso ordine |
| `_EngagementRun.__init__` | `self.ad_target_rule` | `self.altitude_band`, `self.fire_control_knows_altitudes` | `pass_rng` e passaggi | righe vicine, indipendenti |
| `_on_resolve` (`:3318`, filtro a `:3396`) | filtro `_admissible` | — | — (FP-5 tocca `_detection_time_of` `:3229-3235` / `_in_time`) | nessun conflitto |
| `_call_fire_control`, `_fire_control`, `_schedule_next`, `_in_range_at`, `_range_entry`, introspezione | — | quote all'istante, rinvio, fascia/tetto nel tempo (**nuova schedulazione**) | `_detect_direction`, fine del candidato | VA e FP sulle stesse funzioni di schedulazione: FP dopo VA |
| `Logic/Fire_Control.py` `shot_spec_for` (`:819-865`) | `intercept_domains=intercept_domains_for(weapon)` | tre argomenti di quota | — | stesso costruttore: argomenti in coda, BI prima |
| `Logic/Fire_Control.py` `make_registry_fire_control` (protocollo `altitudes`, chiave di memoizzazione con le quote dell'istante), `restrict_by_policy` (quattro varianti per introspezione), docstring "Quota" | — (la BI non li tocca: `intercept_domains` si calcola in `shot_spec_for`) | **si'** (VA §4.1.3 punti 1, 3, 4); `in_altitude_envelope`, `rank_weapons` invariati | — | solo VA; **correzione della stesura precedente**, che diceva "Fire_Control invariato per VA" |
| `Logic/Fire_Control.py` costanti e funzioni nuove | `AD_TARGET_DOMAINS`, `AD_SIZE_GATED_NAVAL`, `AD_DETECTABLE_DEFAULT`, `munition_class`, `intercept_domains_for` | — | — | solo BI |
| `Test/Scenario_Fixtures.py` | non modificato (BI-8 (a): `SHOTS` invariate) | il testo del piano VA usa `route_for` con la terza coordinata (`:584`) e lascia `SHOTS` senza quote (§4.1.4); **nessuna modifica esplicita** trovata nel piano [V sul testo; da ricontrollare se il piano VA cambia] | — | nessun conflitto atteso |
| scenari | **S35-ADTGT** (`Test_Session_Scenarios_S35.py`, 32 esecuzioni) | **S34-BAND** (`Test_Session_Scenarios_S34.py`, 8 varianti x 4 = 32) | **S33-PASSES** (`Test_Session_Scenarios_S33.py`, 4 varianti x 5 semi = 20 esecuzioni, 13 test; FP §4.0.2) | file distinti |
| `Scenario_Baseline.UNITS` e docstring | riga S35-ADTGT dopo S32 | riga S34-BAND **dopo S35-ADTGT** (VA §4.2.2), nessuna rinumerazione | S33-PASSES in coda alle precedenti | in coda, nell'ordine di esecuzione (l'ordine delle righe non segue il numero) |
| docstring del modulo del risolutore | punto 4 della catena | sezione "Quota nel volume d'ingaggio" | sezione FP | sezioni distinte |

I conflitti sono **di riga** (stesse zone di testo), non di logica: nessuna regola legge i campi delle altre (un colpo
con `intercept_domains` e quote e' trattato da VA al lancio e dalla BI all'impatto).

**Ordine** (BI-11 e VA §2.8; FP-5 decisa il 2026-11-08, nessuna ripresa): **BI blocchi 3-4 -> VA blocchi 1-2 -> FP
blocchi 1-2 -> estensione dei dwell a SAM/AAA**; BI blocchi 0-2 gia' eseguiti e mergiati (blocco 0 il 2026-11-07,
blocchi 1-2 il 2026-11-08, merge `a74d7505` e `4803424b`). Mai due esecutori insieme su `Logic/Engagement_Resolver.py`
o `Logic/Fire_Control.py`. Ogni piano successivo rilegge le righe citate (precondizioni gia' scritte nei tre piani).

**Suite e confronto lungo la sequenza** (B = `Ran` della suite sul checkout di partenza, letto dall'ESITO, mai stimato):

| Dopo | Suite | Confronto (oltre alle 1009 identiche, 0 DIFF) |
|---|---|---|
| base | `Ran B` (B = 4795 [V], `Rapporti/Rapporto_BI_blocco1_des-developer.md:43`) | NEW: 20 S32-DWELL |
| BI blocco 1 | `B + 6` = 4801 [V] | invariato |
| BI blocco 2 | `B + 34` = 4829 [V] (eseguito: 28 test, non i "circa 21" del piano; `Rapporti/Rapporto_BI_blocco2_des-developer.md:41`) | invariato; sonda B-1 (interruttore BI acceso): cambiano solo le 6 S19AD `tor_rear` [V] |
| BI blocco 3 | `B + 49` = 4844 [S] (15 test, P-4 (b) di §5.4.1, elenco in §5.4.3; il modulo da solo: `Ran 15` OK [V, sonda S-e]) | NEW: + 32 S35-ADTGT; `UNCHANGED (1009)`, `compared 1061 runs: 52 difference lines` [S; chiavi e numero di sessioni V sulla cattura simulata S-e] |
| VA blocco 1 (base VA = `B + 49` [S]) | `B + 72` [S] (23 test, VA §4.1.7; ~4867) | invariato (20 S32 + 32 S35 NEW) |
| VA blocco 2 | `B + 81` [S] (9 test, VA §4.2.4: `Ran B_VA + 32` complessivi; ~4876) | NEW: + 32 S34-BAND |
| FP blocco 1 (base FP = `B_FP`, letta dall'ESITO dopo VA blocco 2) | `B_FP + 30` (30 test, FP §4.0.1) | invariato (20 S32 + 32 S35 + 32 S34 NEW) |
| FP blocco 2 | `B_FP + 43` (13 test di S33, FP §4.0.1) | NEW: + 20 S33-PASSES (4 varianti x 5 semi); totale `compared 1113 runs: 104 difference lines` |

I conteggi della BI non cambiano con l'ordine BI -> VA (la BI viene prima); quelli della VA partono da `B + 49` [S], quelli
della FP da `B_FP` (valori ~4844, ~4867, ~4876 coerenti con FP §4.0.1). Le
esecuzioni S35 non dipendono dall'interruttore VA (spento di default): restano identiche alla loro cattura dopo VA,
come VA §2.8 si aspetta. Se l'utente invertisse l'ordine (VA prima), `intercept_domains` andrebbe in coda dopo i campi
di VA, `shot_spec_for` e gli interruttori si comporrebbero all'inverso e le base di suite si scambierebbero: nessun
altro effetto sulla logica.

---

## 7. Rischi e limiti

- **Classificazione stimata**: classi e flag sono scelte con fonte ma non tarate; errori di classe spostano interi
  scenari (un Kh-59 `tactical` invece di `cruise` cambia `land_cruise`).
- **Contraddizione interna della regola** (BI-2) e **contrasto con la regola del 2026-09-28** (BI-4): risolte dalle
  scelte dell'utente del 2026-11-07 (categoria vince; tutte le bombe mai); resta l'incoerenza I-1 fra dimensione e
  dominio terrestre, accettata dall'utente come limite [S] (BI-12 (a)): Kh-29/Kh-58 mai bersagli delle difese
  terrestri, il Kh-59 si'.
- **Metro del Maverick**: la coerenza dei flag dipende dalle dimensioni di supporto trovate dalla ricerca; voci senza
  diametro o massa sfuggono al test di coerenza (restano al default di classe [S]): sono 8 (Proposta dati §10.2). Le
  voci vicine ai confini (AGM-65K a 304 kg, RB-05A a 305 kg, Kormoran a 340 mm) dipendono dal valore scelto fra fonti
  discordi con la regola D4.2 (a) della Proposta dati.
- **Balistici assenti**: la parte "balistici" e' scritta ma non provabile in sessione finche' i registri non avranno un
  missile balistico.
- **Dimensione binaria**: nessuna Pd del colpo; R-INT continua a vedere un colpo ammesso come un aereo (ottimistico per
  la difesa).
- **Tempo di volo dei cruise a lunga portata**: `time_of_flight = 0.5 x portata / velocita'` (`Logic/Fire_Control.py:226-228`,
  `:773-774`) da' tempi enormi per Kh-55/Kh-101 (ordine di 5000-11000 s con i dati del registro [calcolo]); R-INT li
  vede sempre "in tempo". Limite precedente, reso piu' visibile dalla regola (motivo per usare Kh-59 in S35).
- **Difesa di dominio mista** (navi che difendono truppe a terra): dipende da BI-5.
- **Armi `test:*`**: con BI-8 (a) gli scenari a tabella non vedono mai la regola.
- **Conflitti di file** con FP e VA su `Logic/Engagement_Resolver.py` (§6).
- **S35 dipende da L1** (regola dell'utente del 2026-09-28, `Proposta_Regole_Allocazione_SAM.md` §7.7 Q2): le varianti
  navali funzionano solo perche' la Rezky ha un V_I di 12 km, minore della distanza di lancio. L1 non si tocca in questo
  blocco; se l'utente la cambiera' (Proposta separata), S35 (come S19AD) andra' rivisto insieme alla fotografia.
- **Margine stretto in `naval_maverick`**: nel seed `S35-ADTGT-2` il primo Maverick parte a ~12,2 km dalla nave, ~200 m
  fuori dal V_I [V, sonda S-e]; una modifica futura che sposti di qualche secondo il lancio (VA, FP, rilevamento)
  potrebbe portarlo dentro: in quel seed `naval_maverick_off` avrebbe 0 intercettazioni. Per questo l'asserzione 10 e'
  sul totale dei semi (§5.4.1, P-6); le chiavi S35 cambierebbero comunque nella fotografia.
- **Sensore `sea` dell'A-10C**: 20 km e' un VALORE DI TEST [S] (P-2), non un dato; le distanze di lancio dei Maverick
  sulla nave dipendono da esso (portata del Maverick 15 km, rilevamento a 20 km).

## 8. Cosa non ho potuto verificare

- **Nessun valore di RCS, diametro, lunghezza o peso dei missili aerei** e' stato cercato o verificato in questa
  sessione (nessuna ricerca su fonti esterne): i confronti di dimensione dell'esempio di BI-7 (Maverick 305 mm, Kh-29
  380 mm) sono conoscenza generale [I]. **Superato dal blocco 0** (2026-11-07): dimensioni con fonte, confidenza e
  livello di verifica in `Proposta_Dati_Bersagli_Intercettabili.md`; nessuna RCS pubblicata per nessuna delle 52 voci.
- La classificazione di §2.2 (cruise/anti_ship/arm/tactical) e' una proposta [S] su conoscenza generale [I], non su
  fonti; Kh-59/KD-63 come cruise, Kh-29 come "grande", Mistral come anomalia del registro sono da confermare.
  **Confermata dal blocco 0** (esito in §2.2), con il Mistral `tactical` per decisione dell'utente.
- Che il `caliber` dei missili sia il diametro [I].
- Che gli scorer dei registri ignorino un campo stringa nuovo (§5.2: l'esecutore lo verifica).
- Che `restrict_by_policy` non ricostruisca le `ShotSpec` per campi espliciti (§5.3.3).
- Il comportamento dell'IA di DCS contro missili in arrivo (gia' segnalato in `Proposta_Dati_Anti_Missile.md:101-103`).
- Le geometrie di S35 non sono state costruite ne' misurate: le asserzioni di §5.4 sono attese qualitative [I]; in
  particolare che l'Arleigh Burke fermi oggi (interruttore spento) i Maverick di `naval_maverick_off`. **Aggiornamento
  del 2026-11-08**: sonde di sola lettura (§5.4.1, S-a..S-d) hanno smentito quest'ultima attesa (con il V_I di 240 km del
  Burke la regola L1 vieta ogni intercettazione) e l'asserzione "piu' danni ai BMP". **Decisioni del 2026-11-08**
  (P-1..P-7, §5.4.1): ora la nave delle varianti navali e' la `FF 1135M Rezky` (V_I 12 km), l'asserzione 2 e' "meno
  Maverick lanciati da acceso", e le geometrie definitive sono **misurate** (sonda S-e, §5.4.3: 15 test OK, 32 chiavi
  della fotografia corrette, in cattura simulata). Restano non verificati la suite completa e il confronto reale con
  il file nel repo (li esegue l'esecutore).
- Le dimensioni del Maverick, dell'Harpoon (salvo il diametro a registro), del Kh-29 e dei candidati "piccoli", e i
  nomi comuni Shturm/Ataka/Shrike: conoscenza generale [I], da verificare nel blocco 0. **Verificati nel blocco 0**
  (ancore e Kh-29 riletti dalla sessione principale; candidati "piccoli" e nomi comuni dalle bozze della ricerca).
- Il numero esatto di test della suite attuale non e' stato riletto (la suite non e' stata eseguita in questa sessione:
  solo la sonda B-0).
- Verificato invece [V]: righe di codice citate (lette il 2026-11-07), statistiche dei registri e lanciatori dei
  loadout (eseguendo i registri), esito della sonda B-0 (§1.8).
