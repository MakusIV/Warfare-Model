# Revisione incrociata 3 di 3 — Coerenza fra le Proposte BI, VA e FP

**Revisore**: `oc-reviewer` (GLM 5.3), revisione indipendente in sola lettura (nessun codice, test,
documento o Proposta modificato; unico file scritto: questo rapporto).
**Oggetto**: coerenza fra `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (BI, *Bersagli
Intercettabili*, decisioni BI-1..BI-12 prese), `Proposta_Allineamento_Volumi_DES_Pianificatore.md`
(VA, *Volumi Allineati*, tutte le decisioni prese) e `Proposta_Finestre_Per_Passaggio_Portata_Propria.md`
(FP, *Finestre per Passaggio*, FP-1..FP-4 decise, FP-5 SOSPESA, FP-6..FP-10 aperte).
**Commit**: `94b391c9`, checkout `analysis/dce-dcs-persistence`, working tree pulito salvo i rapporti
di revisione non tracciati [V: `git status`]. **Data**: 2026-11-07.
**Ordine di esecuzione deciso** (BI-11, VA §2.8, BI §6.1:1089): BI blocchi 0-3 -> VA blocchi 1-2 ->
ripresa di FP-5 -> FP blocchi 1-2 -> estensione dei dwell a SAM/AAA. Gia' committati: D-5 blocchi A e B
(`8943b292`, `effb0dcf`, interruttore `D5_DWELL_TIME`, scenario S32-DWELL).

Acronimi alla prima comparsa: DES (*Discrete Event Simulation*), RNG (*Random Number Generator*),
CPA (*Closest Point of Approach*), R-INT (regola di *Intercettazione con tempo di Reazione*,
`Proposta_Intercettazione_Reazione.md`), SAM (*Surface-to-Air Missile*), AAA (*Anti-Aircraft
Artillery*), A2G (aria-superficie), FC (*fire control*, controllo del tiro), UNITS (tabella degli
scenari della fotografia in `Test/Scenario_Baseline.py`), ESITO (riepilogo di `tools/ai/verifica.sh`).
Legenda: [V] verificato leggendo (file:riga), [I] ipotesi, [S] stima.

Rinvii: le revisioni 1 e 2 (`Revisione_Incrociata_BI_oc-reviewer.md`,
`Revisione_Incrociata_VA_oc-reviewer.md`) esistono e sono state lette per intero: i loro punti NON sono
ripetuti qui (riferiti come rev.1 / rev.2).

---

## 1. Perimetro e metodo

Ho riletto con letture mirate le tre Proposte (BI 1152 righe, VA 1227, FP 1460): §0/§6-§6.1 di BI,
§2.8/§4.0/§6 di VA, §0/§2.6/§3/§4 di FP; il codice attuale (`Scenario_Baseline.py`, tag `event_id`,
nomi nuovi); i log locali `.ai-run/` (suite.log, confronto.log, sonde_passaggi/p0). Non ho eseguito
suite, confronto ne' sonde (divieto del compito). Non mi sono fidato dei rapporti dei planner: i numeri
chiave di P-0 sono stati confrontati con `.ai-run/sonde_passaggi/p0/stats.json`, la base con
`.ai-run/suite.log` e `.ai-run/confronto.log`.

## 2. Riconciliazione della base (premessa alla tabella unica)

- `.ai-run/suite.log` **locale** (4 novembre, quindi ai blocchi D-5): `Ran 4742 tests in 558.735s`,
  `OK (skipped=7)` [V `suite.log:17336-17338`]; `.ai-run/confronto.log` locale (4 novembre):
  `compared 1009 runs: IDENTICAL (474.2 s)` [V `confronto.log:1187`], nessuna esecuzione S32
  [V `confronto.log:1186`].
- La base `Ran 4795` con `compared 1029 runs: 20 difference lines` e' quella dei blocchi D-5 A+B
  (6 novembre, log su osboxes citati da FP §4.0.2 [V sul testo; log NON presente su questa macchina]):
  4742 + 53 test dei blocchi D-5 = 4795 [I sul 53, non misurabile qui]. Il dato e' del principale ed e'
  coerente con i log locali pre-D-5; accettato.
- Ordine di grandezza odierno: `grep -c "def test_"` sui file di test = **4718** metodi (somma manuale
  dei conteggi per file). NON e' il `Ran N` (che include test generati dinamicamente e `subTest`):
  non posso misurare il `Ran` di questo checkout senza eseguire la suite (vietato).

**I numeri delle tre Proposte quadrano fra loro** (dettaglio in §7.2): 6+21+15 = 42 (BI), 42+23+9 = 74
(VA), 74+20+14 = 108 (FP), 4795+108 = 4903. Le uniche parole stantie sono quelle di FP verso l'ordine
deciso (trovate 3 e 4 di §7.1).

## 3. Collisioni (punto B del compito)

### 3.1 Nomi di scenario e righe UNITS

- `S33-PASSES` (FP, 8 varianti x 5 semi = 40), `S34-BAND` (VA, 8 x 4 = 32), `S35-ADTGT` (BI,
  4 geometrie x 2 stati x 4 semi = 32): nomi distinti fra loro e da ogni unita' esistente S1..S32
  [V: grep su `Scenario_Baseline.py`, ultima riga `UNITS` = S32-DWELL a `:396`; nessuna occorrenza
  S33/S34/S35]. File di test distinti: `Test_Session_Scenarios_S33.py` (nuovo, FP §4.2.1),
  `Test_Session_Scenarios_S34.py`, `Test_Session_Scenarios_S35.py` [V BI:1082]. Nessuna collisione.
- Ordine finale atteso delle righe `UNITS`: ..., S30, S31, S32-DWELL, **S35-ADTGT** (BI:1024 "dopo S32,
  e dopo S33/S34 se gia' presenti"), **S34-BAND** (VA:1087-1090 "in coda, dopo S35-ADTGT della BI"),
  **S33-PASSES** (BI §6.1:1083 "in coda alle precedenti") — dichiarato esplicitamente da BI §6.1:
  "in coda, nell'ordine di esecuzione (l'ordine delle righe non segue il numero)". Coerente.
  **Ma** FP §4.2.2 (FP:1291) detta "In `UNITS`, dopo S32-DWELL (`:395-397`)": con l'ordine deciso
  (BI e VA gia' eseguite) quest'ancora inserirebbe S33-PASSES **fra** S32 e S35, contro la tabella di
  coordinamento BI §6.1 → trovata 4 (§7.1).

### 3.2 Interruttori, costanti, nomi

- Interruttori: `D5_DWELL_TIME` (esiste, `Engagement_Resolver.py:519-525` [V rev.2]),
  `BI_AD_TARGET_RULE`, `VA_ENGAGEMENT_ALTITUDE_BAND`, `FP_PER_PASS_DETECTION` — quattro nomi distinti
  [V rev.1 §1, rev.2 §2 e mio grep per i nomi FP]; default tutti `False` (retrocompatibili).
  Posizione dichiarata: BI "dopo `D5_DWELL_TIME`" (BI:1073), VA "subito dopo quello della BI"
  (BI:1073, VA §4.1.2 punto 1) — coerenti; FP "subito dopo `D5_DWELL_TIME = False` (`:525`)"
  (FP:750) metterebbe il proprio interruttore **prima** di quelli BI/VA, contro "in coda, nell'ordine
  di esecuzione" (BI:1073) → trovata 4.
- Costanti/nomi nuovi: BI (`AD_TARGET_DOMAINS`, `AD_SIZE_GATED_NAVAL`, `AD_DETECTABLE_DEFAULT`,
  `munition_class`, `intercept_domains_for`) liberi [V rev.1 §1]; VA (`altitude_intervals`,
  `intersect_intervals`, `accepts_keyword`, `ALTITUDES_KEYWORD`, `max_target_z`,
  `_altitudes_at`, `_band_of`, `_altitude_deferral`, `_own_intervals`) liberi [V rev.2 §2];
  FP (`pass_rng`, `pass_event_id`, `PASS_EVENT_TAG = 'detection_pass'`, `_detection_times`,
  `_own_intervals`/`_own_passes`/`_pass_cpa`/`_pass_detection_time`/`_detect_passes`,
  `FP_PER_PASS_DETECTION`, campi `Detection.pass_index/pass_count/pass_start/pass_end`) — grep su
  `Code/Dynamic_War_Manager/Source/**/*.py`: **zero occorrenze** [V]. Nessuna collisione.
- Tag degli `event_id` dell'RNG: esistenti `'engagement'` (`Session_Simulator.py:998-999`),
  `'temper'` (`TEMPER_EVENT_TAG`, `:798`; `temper_event_id`, `:1022-1023`), `'area_fire'`
  (`Area_Fire.py:131`) [V]; FP aggiunge `'detection_pass'` (FP:1018-1021, 1026-1036), distinto da
  tutti e tre; la chiave resta `(session_id, mission_id, event_id, counter)` [V
  `Session_Types.py:388-390`]; il test 17 di FP (FP:1139-1140) asserisce la distinzione. Nessuna
  collisione.

### 3.3 Campi `ShotSpec` (ordine e default) e `Detection`

- BI: campo **in coda** `intercept_domains: Optional[FrozenSet[str]] = None` (BI:931-933) [V rev.1 §1].
- VA: tre campi **in coda dopo `intercept_domains`** (VA:737; VA:574 corregge esplicitamente la prima
  stesura "dopo `stock_per_round`") — la composizione e' dichiarata identica da BI §6.1 (BI:1074) e
  VA §6: nessuna ambiguita' per l'esecutore, qualunque sia l'ordine. Con l'ordine deciso l'ordine
  finale sara': ..., `stock_per_round`, `intercept_domains`, `min_altitude`, `max_altitude`,
  `max_target_z`. Nessun campo FP nella `ShotSpec` [V BI:1074 e piano FP letto].
- FP aggiunge quattro campi (default `None`) alla classe `Detection` (FP:764-776): classe diversa
  dalla `ShotSpec`, nessuna interazione con BI/VA.

### 3.4 File toccati da piu' di un blocco

La tabella BI §6.1 (BI:1071-1084) e lo specchio VA §6 (VA:574-581) sono **coerenti fra loro** [V
confrontate riga per riga]. In particolare:

- `Engagement_Resolver.py`: BI filtra in `_on_resolve` (`:3350`), VA tocca `_range_entry`,
  `_schedule_next`, `_in_range_at`, `_call_fire_control`/`_fire_control`, FP tocca
  `_detect_direction`, `_exposure_time`, `_detection_time`, `_detection_time_of`, `_draw`,
  `resolve_engagement`, `Detection`: zone di riga disgiunte; i piani comandano la ricerca per nome
  dopo ogni esecuzione (VA §4.0.5; BI:845-846). `Fire_Control.py`: BI e VA estendono entrambe
  `shot_spec_for` con argomenti in coda (BI:1078) — composizione dichiarata. Nessun terzo tocca
  `make_registry_fire_control`/`restrict_by_policy` (solo VA, BI:1079).
- **`Test/Scenario_Fixtures.py`**: BI §6.1 (BI:1081) dice che VA non lo modifica: **verificato
  corretto**. VA usa `route_for` con la terza coordinata (gia' esistente, `Scenario_Fixtures.py:584`
  [V rev.2 §2]) e lascia le `SHOTS` di test senza portata ne' quote come **residuo dichiarato**
  (VA:922, VA:1192 "fire control di test non allineata"): nessun test VA richiede `SHOTS` con quote
  (i test 8-21 costruiscono specifiche a mano e S34 usa armi dei registri). BI non lo modifica
  (BI-8 (a), `SHOTS` invariate [V rev.1 §3]); FP non lo modifica (S33 vive in
  `Test_Session_Scenarios_S33.py` e importa `build`/`ZSU` da S32, FP:1321-1322) — coerente con
  il "—" di BI:1081.

## 4. Contraddizioni fra le tre Proposte (punto C del compito)

1. **FP-3 (a) contro la R-INT "vede il lancio" della BI** — l'interazione e' riconosciuta da entrambe:
   FP §2.6 (FP:462-513) sospende FP-5 proprio perche' con FP-3 (a) "traccia persa all'uscita" la scelta
   dell'istante di rilevamento per R-INT cambia senso (l'esempio FP:494-501 mostra che con l'opzione (a)
   un lancio fra due passaggi risulta "visto" tramite il rilevamento del primo passaggio, anche se la
   traccia e' persa: e' il motivo dell'opzione (d)); BI §6 (BI:1053) dichiara l'interazione e l'ordine
   (BI-11). **Il problema concreto** e' che il blocco 1 di FP (punto 10, FP:989-992) hardcodizza gia'
   l'opzione (a) — vedi trovata 2. Nota: BI §6.1:1086-1087 ("i conflitti sono di riga, non di logica")
   e la riga BI:1076 ("nessun conflitto" per `_detection_time_of`) sottovalutano la stessa interazione
   di logica (con entrambi gli interruttori accesi l'istante R-INT cambia): trovata 5.
2. **VA-6 `_own_intervals` (blocco 1 di FP) contro il piano FP** — **coerenti** [V]: FP implementa la
   decisione VA-6 (a) con la firma definitiva `_own_intervals(observer_id, target_id, own_range,
   radius=None)` (FP:835-836), raggio **invariato** ("nessuna moltiplicazione per un fattore",
   FP:982-983), unico punto di chiamata del volume proprio (FP:975-986), e il grep di verifica del
   punto 8-bis contempla "se la Proposta VA e' gia' eseguita, le sue funzioni d'ingaggio" (FP:985-986);
   il test 20 (FP:1142-1147) copre la decisione. L'unica stantia e' la firma `scale` in VA §2.3:
   rinvio a rev.2 (MINORE 6), non ripeto.
3. **La BI toglie agli A2G dei terrestri la maggior parte dei casi R-INT** — coerente e dichiarato in
   entrambe: FP §2.6 nota (FP:507-513) sospende FP-5 per questo motivo; FP §3 FP-5 (FP:680-692) conferma
   ("R-INT resterebbe per cruise/balistici e antinave contro le difese navali"); BI §6:1053 e BI-11 (a)
   (BI:785-787) registrano l'ordine "prima BI, poi FP-5 riproposta illustrando in dettaglio e con
   esempi". VA §2.8/VA:80 concorda sull'ordine. Nessuna delle parti decise di FP-1..FP-4 dipende da
   FP-5: P-0 misura `rint_last_not_earliest` 0 su tutte le 1029 esecuzioni [V
   `sonde_passaggi/p0/stats.json:18`], quindi la sospensione non tocca le attese dei blocchi.
4. **Presunzioni incrociate** — VA presuppone BI eseguita con controlli **verificabili per contenuto**
   (VA §4.0.2: `intercept_domains` presente, `BI_AD_TARGET_RULE` esistente, S35 in `UNITS`) e copre
   persino il caso "S33-PASSES se la FP fosse gia' eseguita" (VA:670-671): robusta a qualunque ordine.
   BI presuppone VA subito dopo e FP in coda (BI §6.1). **FP presuppone BI/VA non eseguite** (tranne
   una nota, FP:104, che copre solo i due `Ran`): precondizioni, esiti attesi e ancore di posizione
   assumono la base 4795 e UNITS/switch intatti → trovate 3 e 4.

## 5. Precondizioni per ogni blocco (punto D)

- **BI** (§5.0, BI:841-846): branch dedicato creato dal principale, `git status` pulito, nessun altro
  esecutore su `Engagement_Resolver.py`/`Fire_Control.py`; base `Ran B` **simbolica**, "letto
  dall'ESITO, mai stimato" (BI:1094) — precondizioni sufficienti e ordine-agnostiche. **Blocco 0 =
  ricerca dati con fonti, non lavoro dell'esecutore**: precondizione esplicita, esecuzione bloccata
  finche' l'utente non lo approva (BI:839-846, 848) [V rev.1 §4.1].
- **VA** (§4.0, VA:663-676): branch, tree pulito, `git stash list` vuota; BI eseguita (controlli per
  contenuto, VA §4.0.2); decisioni VA registrate; base annotata con confronto comprensivo delle nuove
  note; righe cercate **per nome** (VA §4.0.5). Sufficienti.
- **FP** (§4.0, FP:730-742): (1) D-5 blocco B committato — ancora verificabile oggi [V `git log`
  `effb0dcf`]; (2) base `Ran 4795` **stantia** per l'ordine deciso (sara' 4869 dopo BI+VA); (3) "le
  decisioni FP-1..FP-10 sono prese (al 2026-11-07: FP-1, FP-2 e FP-3 decise, FP-4..FP-10 ancora
  aperte)" — **insoddisfacibile oggi** (FP-5 sospesa, FP-6..10 aperte) e in contraddizione con §0, che
  FP-4 dichiara DECISA (FP:86): un esecutore diligente si ferma alla precondizione 3; (4) cattura di
  P-0 presente sulla macchina [V `ls .ai-run/sonde_passaggi/p0`: capture.json, log.txt, stats.json
  presenti sul ProArt]. **Manca la precondizione del branch dedicato** (BI §5.0.1 e VA §4.0.1 la
  hanno; resta comunque coperta da AGENTS.md) — trovata 6.
- **Dipendenze**: BI blocchi 1-3 richiedono il blocco 0 approvato; VA richiede BI eseguita; i blocchi
  FP richiedono la ripresa di FP-5 **e la decisione di FP-6** (trovata 1) prima di partire, come
  BI §6.1:1089 schedula ("ripresa di FP-5 -> FP blocchi 1-2").

## 6. Copertura dei test (parte "qa")

Conteggi coerenti con i piani: BI 6 / 21 / 15 [V rev.1 §4.3], VA 23 / 9 [V rev.2 §5], FP 20 / 14
[FP:102-104, §4.1.5 (FP:1076-1148), §4.2.1 (FP:1166)]. Priorita':

- **Alta** — percorso `earliest=True` integrato (R-INT con FP accesa): il test 13 (FP:1115-1117)
  collauda `_detection_times` isolata, ma nessun test collauda `_detection_time_of` con `pass_rng`
  dato dentro una risoluzione (cioe' l'effetto del punto 10 sulla regola R-INT della BI). Se il punto
  10 sopravvive alla ripresa di FP-5, serve un test d'integrazione del "lancio visto/non visto"
  (esecutore, nel blocco 1 aggiornato).
- **Media** — FP-6 (punto 8): il test 14 (FP:1130-1132) asserisce la nuova permanenza (100, non 180)
  **a FP spenta**, cioe' dà per decisa un'opzione oggi aperta; inoltre il ramo di ripiego
  `next(..., longest)` (passaggio che non contiene `t_cpa`, FP:966) non ha un test diretto (solo
  copertura indiretta). Da sistemare insieme alla decisione di FP-6 (trovata 1).
- **Media** — nessuna prova prevista che le esecuzioni nuove S34/S35 restino identiche con FP accesa
  (P-1 misura solo la fotografia, FP §4.3): probabilmente innocue [I: nessuna ha passaggi multipli],
  ma nessuna misura e' pianificata. Facoltativa.
- **Bassa** — rinvii a rev.2 §5 (rinvio in cascata, arma con fascia senza portata) e rev.1 §5 (casi
  limite censiti): non ripeto.
- Nota positiva: le asserzioni dei test FP sono forti e calcolate (istanti 50/290/170/300, Pd 0,9352,
  `places=6/9`, FP:1084-1085, 1099-1123), non del tipo "non solleva eccezioni"; il test 4 (stream
  dell'ingaggio identico nei due stati, FP:1096-1098) e' un buon test di determinismo.

## 7. ESITO

### 7.1 Problemi, ordinati per gravita'

**BLOCCANTE**

1. **Il blocco 1 di FP implementa FP-6 (ancora APERTA) con una modifica non dietro l'interruttore.**
   Prova: FP §4.1.1 punto 8 (FP:952-974) sostituisce il ramo con i tratti di `_exposure_time`
   **incondizionatamente** (permanenza = passaggio che contiene il CPA, mai la somma): nessun
   `if self.pass_rng is not None`; il commento nel codice cita FP-6 (FP:963-964). Ma FP-6 e' aperta
   (FP §4.0.3, FP:737-738; la riga §0 FP:88 non porta "DECISA") e la stessa docstring dell'interruttore
   del punto 2 promette "Spento: chiamata e **comportamento di prima**" (FP:758), che il punto 8 viola
   con D-5 accesa e FP spenta. Effetto: eseguito alla lettera, il blocco 1 cambia il comportamento
   della D-5 gia' committata senza decisione dell'utente e senza interruttore dedicato, in tensione con
   AGENTS.md ("ogni regola nuova sta dietro un interruttore il cui default riproduce il comportamento
   precedente"); l'estensione dei dwell a SAM/AAA (prevista DOPO i blocchi FP) si costruirebbe su una
   legge non decisa. Il confronto resta pulito solo per caso: la fotografia non esercita `_exposure_time`
   (D-5 spenta, FP:1155) e P-0 misura `multi` 0 su tutte le 1029 [V `p0/stats.json:7`], quindi nemmeno
   S32 cambia (FP:1160-1161). Correzione: chi pianifica la ripresa di FP-5 (o la sessione principale)
   porta FP-6 all'utente **prima** dei blocchi FP: o la si decide e si conferma il punto 8, oppure il
   punto 8 va messo dietro `FP_PER_PASS_DETECTION` (o dietro un interruttore dedicato), oppure tolto dal
   blocco 1 fino a decisione.

**IMPORTANTI**

2. **Il blocco 1 di FP presuppone FP-5 = (a), che e' SOSPESA.** Prova: punto 10 (FP:989-992):
   `self.detected_at = _detection_times(self.detections, earliest=self.pass_rng is not None)` — con
   l'interruttore FP acceso R-INT usa il **primo** rilevamento, che e' esattamente l'opzione (a) di
   FP-5; la docstring lo cita ("Con il rilevamento per passaggio (FP-5) il primo istante"). Ma FP-5 e'
   SOSPESA (FP:462-467: "le opzioni sotto restano tutte aperte", incluse (b), (c) e la (d) proposta
   dalla sessione principale proprio per coerenza con FP-3 (a)), e la ripresa e' schedulata **prima**
   dei blocchi (BI §6.1:1089). Effetto: se la ripresa scegliera' (b)/(c)/(d), il punto 10 sara' gia'
   scritto dalla parte sbagliata; il piano delle parti decise (blocchi) pre-decide una scelta aperta.
   Correzione: la ripresa di FP-5 decide esplicitamente e **riscrive il punto 10** di conseguenza
   (oppure il punto 10 resta con `earliest=False` fisso finche' FP-5 non e' decisa). Da: chi pianifica
   la ripresa.
3. **Precondizioni, titolo ed esiti attesi di FP sono calcolati sull'ordine "FP per prima", contro
   l'ordine deciso.** Prova: (i) §4.0.2 fissa la base `Ran 4795` (FP:734) che dopo BI+VA sara' 4869
   (la nota FP:104 copre solo i due numeri di suite, non la checklist §4.0); (ii) §4.0.3 richiede
   "le decisioni FP-1..FP-10 sono prese" e aggiunge "FP-4..FP-10 ancora aperte" (FP:737-738), mentre
   §0:86 dichiara FP-4 **DECISA** — il titolo del §4 (FP:725, "raccomandazioni FP-4..FP-10") e' stantio
   nello stesso modo; (iii) gli esiti attesi §4.1.6 (FP:1152-1153 "compared 1029 runs: 20 difference
   lines"), §4.2.4 (FP:1327-1328 "60 nuove ... compared 1069 runs: 60 difference lines") e §4.3
   (FP:1337-1339) non contano S35-ADTGT (32) e S34-BAND (32): con l'ordine deciso sara'
   `compared 1133 runs: 124 difference lines` dopo il blocco 2. Effetto: l'esecutore, che per piano e
   per AGENTS.md si ferma se una precondizione manca o il confronto differisce dall'atteso, si blocca
   due volte per motivi falsi (precondizione 3 insoddisfacibile; confronto "diverso dall'atteso").
   Correzione: la ripresa di FP-5 (che precede i blocchi) aggiorna §4.0, il titolo §4, §4.1.6, §4.2.4 e
   §4.3 con i numeri della tabella §7.2. Da: chi pianifica la ripresa.

**MINORI**

4. **Ancore di posizione di FP non riallineate a BI/VA.** Prova: interruttore "subito dopo
   `D5_DWELL_TIME = False` (`:525`)" (FP:750) e riga `UNITS` "dopo S32-DWELL (`:395-397`)"
   (FP:1291). Con BI e VA eseguite prima, la prima metterebbe `FP_PER_PASS_DETECTION` prima di
   `BI_AD_TARGET_RULE`/`VA_ENGAGEMENT_ALTITUDE_BAND` e la seconda inserirebbe S33-PASSES fra S32 e
   S35, contro la tabella di coordinamento BI §6.1 (BI:1073, 1083: "in coda, nell'ordine di
   esecuzione"). Effetto: solo consistenza/cosmetica (nessun effetto sugli esiti del confronto), ma
   due piani danno istruzioni contraddittorie per lo stesso punto. Correzione: l'esecutore FP segue la
   regola "in coda" di BI §6.1 (che e' il contratto di coordinamento); la ripresa corregge le due
   ancore nel testo.
5. **BI §6 dichiara "conflitti di riga, non di logica", ma il punto 10 di FP e' un'interazione di
   logica con la R-INT della BI.** Prova: BI:1086-1087 ("nessuna regola legge i campi delle altre") e
   BI:1076 ("nessun conflitto" per `_detection_time_of`): il punto 10 di FP cambia l'istante usato
   dalla regola "vede il lancio" della BI quando entrambi gli interruttori sono accesi. A default
   spenti nessun effetto; la ripresa di FP-5 coprira' la scelta. Correzione: una menzione esplicita
   nella ripresa di FP-5 (non serve toccare la BI). Da: chi pianifica la ripresa.
6. **FP §4.0 non richiede il branch dedicato** (BI §5.0.1 e VA §4.0.1 si'): resta coperto da AGENTS.md
   (l'esecutore controlla comunque `git branch --show-current`). Correzione: una riga in §4.0 nella
   ripresa. Da: chi pianifica la ripresa.

**Conferme** (cercate e NON trovate, perche' coerenti): nomi di scenario/interruttori/campi/tag senza
collisioni (§3); ordine UNITS dichiarato identico da BI §6.1 e VA §6; VA-6 implementata da FP con la
firma definitiva e il raggio invariato; il rinvio di FP-5 dopo la BI e' registrato in modo identico da
BI (BI-11, §6) e FP (§2.6); VA non modifica `Scenario_Fixtures.py` (BI:1081 corretto, §3.4).

### 7.2 Tabella unica dell'ordine di esecuzione (punto A)

B = `Ran` della suite **letto dall'ESITO all'avvio di ogni blocco, mai stimato** (regola di AGENTS.md
ribadita da BI:1094). Valori assoluti con base D-5 = 4795 [dato del principale; non riproducibile dai
log locali, v. §2]. Confronto = `compared N runs: D difference lines`; "0 DIFF/CHANGED" sempre
richiesto; le "1009 identiche" sono la fotografia attuale (S32/S33/S34/S35 restano fuori fino a
decisione dell'utente, AGENTS.md vieta di installare fotografia nuova).

| Passo | Base attesa (`Ran` prima) | `Ran` atteso dopo | Confronto atteso | Sonde da (ri)eseguire |
|---|---|---|---|---|
| base (dopo D-5 A+B, oggi) | — | 4795 | `compared 1029: 20` (tutte NEW S32-DWELL); 1009 identiche | B-0, V-0..V-2b, P-0 gia' eseguite (input) |
| BI blocco 0 (ricerca dati, non esecutore) | 4795 | 4795 | invariato | nessuna (solo fonti) |
| BI blocco 1 | 4795 | **4801** (B+6) | invariato (`compared 1029: 20`) | — |
| BI blocco 2 | 4801 | **4822** (B+27, +21) | invariato | **B-1** (BI accesa): cambiano solo le 6 S19AD `tor_rear` (BI:1100) |
| BI blocco 3 | 4822 | **4837** (B+42, +15) | `compared 1061: 52` (20 S32 + **32 NEW S35-ADTGT**) | — |
| VA blocco 1 (base VA = B+42) | 4837 | **4860** (B+65, +23) | invariato (52 righe NEW) | — |
| VA blocco 2 | 4860 | **4869** (B+74, +9) | `compared 1093: 84` (+ **32 NEW S34-BAND**) | sonda di geometria S34 (obbligatoria, con fermata); a fine VA: prova con VA accesa, atteso **1009 identiche** (VA:1122) |
| ripresa di FP-5 (proposta, nessun codice) | 4869 | 4869 | invariato | nessuna; aggiorna il piano FP (trovate 1-4) |
| FP blocco 1 | 4869 | **4889** (+20, "4815" del testo e' la base 4795) | invariato, 0 cambiate (`compared 1093: 84`) | **P-1** (FP accesa): da 0 a 44 cambiate, tutte `AFTER_PASS` [V: 44 elencate in `p0/stats.json:29-73` = 2+1+6+1+32+2]; verifica S32 vs cattura P-0: `compared 20 runs: IDENTICAL` (FP:1158-1161) |
| FP blocco 2 | 4889 | **4903** (+14, "4829" e' la base 4795) | `compared 1133: 124` (20 S32 + 32 S35 + 32 S34 + **40 NEW S33-PASSES**), 1009 identiche, 0 cambiate | — |
| estensione dei dwell a SAM/AAA | 4903 | fuori dai numeri delle tre Proposte (`Proposta_Dwell_Time_Rilevamento.md`) | da pianificare a parte | — |

Riconciliazione dei numeri citati dalle tre Proposte: BI "B+6/+27/+42" (BI:1099-1101) e "B+65/B+74"
(BI:1102-1103, = VA:1010 "Ran B+23" e VA:1116 "Ran B+32" con base dopo BI) **quadrano**; FP "Ran
4815/4829 su base 4795" con la nota "+20 e +34" (FP:104) **quadrano** in assoluto (4795+20, +14) e
con l'ordine deciso (4869+20=4889, +14=4903). Le uniche cifre stantie sono quelle di FP verso
l'ordine (trovata 3); i conteggi VA di BI §6.1 sono gia' riallineati [V BI:1102-1103 e VA:1116].

### 7.3 Cosa NON ho potuto verificare (limiti della revisione)

- **Suite, confronto e sonde non eseguiti** (vietato dal compito): ogni `Ran` atteso e ogni `compared`
  della tabella resta da provare all'esecuzione. In particolare la base `Ran 4795` non e' riproducibile
  dai log di questa macchina (`suite.log` locale del 4 novembre, pre-D-5: `Ran 4742` [V]); l'ho
  accettata come dato del principale, coerente con 4742 + 53 [I] test dei blocchi D-5 e con il [V]
  dichiarato da FP:734 su un log di osboxes che non ho.
- Il numero esatto di test aggiunti dai blocchi D-5 (53) e la differenza fra `Ran` (4795) e i metodi
  `def test_` contati oggi (4718, ~77: test dinamici) non sono misurabili senza eseguire la suite.
- Le sonde P-0/B-0/V-0..V-2b non sono state rieseguite: i numeri di P-0 citati sono stati confrontati
  con `.ai-run/sonde_passaggi/p0/stats.json` [V: `salvos` 28214, `multi` 0, `extra_draws` 0,
  `rint_last_not_earliest` 0, `inner_single_salvos_after_pass` 151, elenco AFTER_PASS = 44]; per B-0 e
  V-* mi appoggio alle verifiche fatte dalle revisioni 1 e 2 contro i loro log (non ripetute da me).
- Ho letto le tre Proposte per punti (§0, §2.6-2.8, §4, §6), non integralmente: le asserzioni di
  codice di BI e VA sono state verificate riga per riga dalle revisioni 1 e 2 (le cito come già
  verificate, non le ho ripetute); per FP ho verificato direttamente solo i punti a rischio di
  collisione/coerenza (nomi, tag, UNITS, punti 2/7/8/8-bis/10 del blocco 1, esiti attesi, precondizioni).
- Le geometrie di S33/S34/S35 e le attese qualitative dei loro test restano da provare all'esecuzione;
  non ho verificato i contenuti di `Proposta_Dwell_Time_Rilevamento.md` (estensione dei dwell, fuori
  perimetro delle tre Proposte).
- Non ho verificato che nessun altro scenario usi nomi di variante/asset in collisione con quelli
  dichiarati da S33 (FP:1315-1318) oltre al grep dei nomi di scenario: controllo di massima fatto, non
  esaustivo voce per voce.
