# Revisione incrociata 1 di 3 — Proposta BI (Bersagli Intercettabili)

**Revisore**: `oc-reviewer` (GLM 5.3), revisione indipendente in sola lettura.
**Oggetto**: `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (BI, decisioni BI-1..BI-12 tutte DECISE).
**Commit**: 94b391c9, checkout `analysis/dce-dcs-persistence`, working tree pulito [V: `git status` nullo].
**Data**: 2026-11-07. Acronimi: DES (*Discrete Event Simulation*), SAM (*Surface-to-Air Missile*), AAA (*Anti-Aircraft Artillery*), RCS (*Radar Cross Section*), A2G/A2S (aria-superficie / aria-nave), ARM (*Anti-Radiation Missile*), ATGM (*Anti-Tank Guided Missile*).

> Rapporto in costruzione: aggiornato dopo ogni gruppo di controlli. Le sezioni incomplete sono marcate.

## 1. Stato dei controlli sul codice (punto B del compito)

| Aff ermazione della Proposta | Esito | Riscontro (file:riga) |
|---|---|---|
| `shot_spec_for` classifica da `kind`: missile sempre True, bomba solo se `type == 'Guided bombs'`, altro False | **OK** | `Logic/Fire_Control.py:763-768` [V letto] |
| `shot_spec_for` estesa `:745-790` | **OK** | `Logic/Fire_Control.py:745-790` [V letto] |
| `salvo_interceptors`: solo `Vehicle`/`Ship` operativi; capacita' None ricade su `build_threat_aa`; aerei mai | **OK** | `Block/Military.py:652-715`, filtro a `:682-685`, fallback `:693-696` [V letto] |
| `ShotSpec` campi/ordine/default (`interceptable` default False a `:614`; `stock_per_round` in coda `:617`; campo nuovo in coda possibile) | **OK** | `Logic/Engagement_Resolver.py:587-650` [V letto]; docstring "la decide chi conosce l'arma" a `:597-599` [V] |
| `_may_intercept` = regola L1, lancio dentro il volume d'intercettazione non si intercetta | **OK** | `Logic/Engagement_Resolver.py:3162-3185` (`allowed = not (dentro)` a `:3181`) [V letto] |
| `_in_time` = R-INT (traccia + tau <= impatto; lancio visto solo se il lanciatore era gia' rilevato) | **OK** | `Logic/Engagement_Resolver.py:3250-3274` [V letto] |
| `_on_resolve`: conteggio intercettabili a `:3291`, filtro `free <= 0 / L1 / R-INT` a `:3350` | **OK** | `Logic/Engagement_Resolver.py:3291`, `:3350` [V letto]; l'inserimento di `_admissible` proposto in §5.3.2 combacia con la riga `:3350` reale |
| Nomi nuovi (`BI_AD_TARGET_RULE`, `AD_TARGET_DOMAINS`, `AD_SIZE_GATED_NAVAL`, `AD_DETECTABLE_DEFAULT`, `munition_class`, `intercept_domains`, `ad_detectable`, `ad_target_rule`, `_ad_domain`, `_admissible`) liberi | **OK** | grep su `Code/Dynamic_War_Manager/Source/**.py`: nessuna occorrenza [V]; unica vicinanza `test_bad_target_rules_argument_raises` (`Test/Test_Engagement_Resolver.py:3689`), non collisione |
| Registri aerei senza `diameter_mm`/`mass_kg`/`length_m`/`rcs` | **OK** | grep su `Asset/**.py`: nessun campo con questi nomi [V] |
| Voci citate esistono nei registri | **OK** | AGM-65D `Aircraft_Weapon_Data.py:2499`; AGM-65K `:2569`; RB-75T `:2409`; Kh-59 `:3375` (portata 90 km a `:3384`); Kh-59M `:4467`; Kh-29T `:3728`; Kh-29L/Kh-29TE presenti; KD-63 `:4677`; KD-63B `:4858`; AGM-84A `:2239`; AGM-88/AGM-45/Kh-58/Kh-25MP/MPU/Kh-31P/LD-10 presenti; Mistral `:3032` (l'anomalia dichiarata §1.5 e' vera); RGM-84-Harpoon `Ship_Weapon_Data.py:1240`; BGM-109-Tomahawk `:1254` [V] |
| AGM-65D con riga `ship` a Pk > 0 (per la variante `naval_maverick` di S35) | **OK** | `Aircraft_Weapon_Data.py:2562-2566` (`"ship"`: accuracy 1, destroy_capacity 0.6/0.8/1) [V letto]; task include `Anti_Ship` (`:2503`) |

Campi della voce AGM-65D [V letti, `:2499-2568`]: `type`, `model`, `users`, `task`, `start_service`, `end_service`, `cost`, `warhead` (57 kg), `range` (15), `max_speed` (320 m/s), `perc_efficiency_variability`, `efficiency`. **Nessun campo RCS/diametro/lunghezza/peso**: l'affermazione "nessun campo RCS/diametro nei registri aerei" e' verificata [V].

## 2. Sonda B-0 (punto C): i numeri della Proposta coincidono con i file

Confronto fra §1.8 della Proposta e `Sonde_Bersagli_Intercettabili/b0/` (esito.txt, stats.json,
esecuzioni_con_intercettazioni.txt) e `LEGGIMI.md`. **Tutti i numeri citati coincidono** [V]:

| Numero citato nella Proposta (§1.8 / §0) | Valore nei file | Esito |
|---|---|---|
| 1029 esecuzioni, 1009 in fotografia, 20 nuove, 0 DIFF | `esito.txt:21-23` (20 righe NEW S32-DWELL a `:1-20`, nessun DIFF) | **OK** |
| 397 colpi fermati in 16 esecuzioni | `esito.txt:24-25` (TOTALS `stopped_rounds` 397; RUNS_WITH_STOPS 16), `stats.json:7,12` | **OK** |
| S6 4, S16 4, S19AD 6, S2 2 esecuzioni con fermati | `esito.txt:26` = `stats.json:10-15` | **OK** |
| AGM-65D 36 colpi fermati dal Tor in S19AD `tor_rear`, semi 0-5, 6 ciascuno | `esito.txt:31` (STOPPED 36), `esito.txt:53-58` (6 per seme), `stats.json:18,49-77` | **OK** |
| `test:anti_ship` 351 colpi fermati da una nave | 302 (`esito.txt:29`) + 49 aereo (`:30`) = 351; per seme S6 80/62/80/80, S16 6/19/15/9 = `esecuzioni_con_intercettazioni.txt:1-4,13-16` | **OK** |
| `test:anti_radiation` 10 fermati da un Buk (S2-0-sead 3, S2-6-sead 7) | `esito.txt:32`, `esito.txt:65-66` | **OK** |
| 6 esecuzioni cambiano con BI-8 (a), 8 con BI-8 (b) | `CHANGED[unmodelled_as_before] 6` (`esito.txt:27`), `CHANGED[by_role] 8` (`:28`, dettaglio `:59-66`) | **OK** |
| `test:agm` 72 colpi su forze con intercettori, mai fermati | FACING 12+32+28 = 72 (`stats.json:23-25`); nessun STOPPED con `test:agm` (`esito.txt:29-32`) | **OK** |
| FACING contiene solo AGM-65D, `test:agm`, `test:anti_radiation`, `test:anti_ship` | `stats.json:22-30`: esattamente quelle 4 armi | **OK** |
| Maverick: 14 `seen|ok`, 4 `geometry|ok` | `esito.txt:46,50` | **OK** |
| Antinave: 151+31 `geometry|ok`, 1 `seen|ok` | `esito.txt:40,43,51` | **OK** |
| `replay_mismatch` 0 | `esito.txt:24`, `stats.json:8` | **OK** |
| Tempi: ~8 minuti (13:19:51-13:28:02), confronto 487.6 s | `LEGGIMI.md:28`, `esito.txt:21` | **OK** |

Unico numero non riscontrabile nei file: l'attribuzione dei fermati del Molniya all'arma AK-630
(§1.8:299-301). La Proposta stessa lo dichiara ("l'attribuzione per arma non e' nel riassunto della
sonda") con il registro del Molniya citato [V planner, non verificato da me]. Onesto, non un errore.

Verdetto sezione: la sonda B-0 e' veritiera; i numeri della Proposta sono letti dai file, non stimati.

## 3. Fedelta' alle regole dell'utente (punto A)

Riferimento vincolante (R2/R4/R1/BI-12 del compito). Per ogni decisione: cosa dice la Proposta
(Proposta = `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`, righe da `grep -n`/lettura) e se
realizza la regola dell'utente o una scorciatoia.

### 3.1 Decisioni BI-1..BI-12

| Decisione | Realizza la regola? | Analisi (righe Proposta) |
|---|---|---|
| BI-1 C+F (`:541-559`) | **SI'** | Categoria + flag `ad_detectable`: struttura identica a R2 (categorie balistico/cruise, poi dimensione). La parte "dimensione" ha effetto solo sui navali (BI-12, decisa): corrisponde al testo dell'utente. |
| BI-2 (a) (`:561-581`) | **SI', con contraddizione esplicitata** | La contraddizione interna della regola (cruise "indipendentemente da chi li lancia" vs "tutti gli A2G dei cacciabombardieri esclusi") e' messa nero su bianco a `:571-576` e risolta dall'utente: la categoria vince, Kh-59/59M/KD-63/63B `cruise` bersagli anche dei terrestri. Incoerenza I-1 dichiarata (`:822-826`). Nessuna scorciatoia: coincide con la regola data nel compito ("Kh-59 cruise si'"). |
| BI-3 (a) (`:583-600`) | **SI'** | ARM esclusi dai terrestri (lettera del corollario A2G); per i navali vale il flag (coerente con BI-6 "uso"). |
| BI-4 (a) (`:603-621`) | **SI', restringe dichiarata** | "Tutte le bombe mai, comprese plananti": realizza la regola nuova e **restringe** quella del 2026-09-28 (bombe plananti fra i bersagli legittimi, citata a `:248-251` con file:riga). Il contrasto e la motivazione del Tor sono dichiarati (I-4 `:832-833`) e il blocco 4 prevede la nota di rimando (`:1044-1045`). Scelta dell'utente, non scorciatoia. |
| BI-5 (a) (`:623-640`) | **SI'** | Ship = navale, altro = terrestre: realizza R4 (i sensori che devono vedere il colpo sono dell'intercettore); il caso misto (difesa di dominio) e' spiegato (`:386-392`). |
| BI-6 (a) (`:642-673`) | **SI'** | "Uso" A2S: ogni missile `ad_detectable` bersaglio dei navali; Maverick (AGM-65D/K, RB-75T) `ad_detectable` **fisso False** "in ogni contesto, contro difese terrestri e navali" (`:662-664`), con il "metro del Maverick" (ancore Maverick/Harpoon, `:408-420`) che realizza "stessa coerenza per le altre situazioni d'uso". Esattamente la regola dell'utente. Ho verificato che i candidati "piccoli" citati (Hellfire, TOW, Shturm, Ataka, Hot-3, Kh-25, Kh-66, RB-05) sono davvero nel registro aereo (`Aircraft_Weapon_Data.py:158,166,168,181-186`), quindi la via "classe dichiarata" e' percorribile [V]. |
| BI-7 (a) (`:675-705`) | **SI', con [S] dichiarato** | Flag per missile, nessuna soglia numerica nel codice (le ancore stanno nei test e nel documento dati, `:419-420`); default `anti_ship`/`cruise` True, `arm`/`tactical` False marcato [S] (`:687`, `:909`). Vedi MINORE M2 sotto sul default True. |
| BI-8 (a) (`:707-728`) | **DEVIAZIONE DICHIARATA** | Le armi `test:*` non seguono la regola (`intercept_domains` None = nessun filtro anche acceso): un `test:anti_radiation` continuera' a essere fermato da un Buk (10 colpi, S2 `sead`) anche con l'interruttore acceso, contro la lettera di R2. La Proposta lo quantifica (6 vs 8 esecuzioni, `:720-722`), lo motiva (armi di test senza dati di dimensione) e l'utente ha deciso (a). Non e' una scorciatoia nascosta: e' una scelta censita. Valori `interceptable` delle armi di test verificati [V: `Scenario_Fixtures.py:814,816,818` True; `:826` bomb False]. |
| BI-9 (a) (`:730-750`) | **SI'** | W1 + `BI_AD_TARGET_RULE = False` (default retrocompatibile, AGENTS.md); il filtro si aggiunge prima di L1/R-INT che non cambiano (`:524`, `:939-942`): R4, L1 e R1 restano intatte. Nessuna estrazione RNG nuova (`:517-518`, `:957-959`). |
| BI-10 (a) (`:752-774`) | **SI'** | S35-ADTGT, 4 geometrie x 2 x 4 = 32; la quarta geometria (`naval_maverick`) prova proprio il caso "Maverick mai" della BI-6. |
| BI-11 (a) (`:776-788`) | **SI'** | Ordine dei lavori; FP-5 (*finestre per passaggio*, opzione sospesa) riproposta dopo. |
| BI-12 (a) (`:790-818`) | **SI'** | Dimensione solo per i navali; i terrestri solo per categoria (Kh-59 cruise si', Kh-29/Kh-58 mai). Esattamente il testo dell'utente; limite I-1 dichiarato [S] (`:813-818`, `:1117-1120`). |

### 3.2 Blocchi 0-4

- **Blocco 0** (`:848-865`): ricerca con fonti per i 52 `MISSILES_ASM` (44 aerei + 8 navali), ancore Maverick/Harpoon, zona grigia approvata voce per voce, candidati piccoli trattati come ipotesi. Realizza R2 ("dimensioni compatibili", Harpoon ancora) senza inventare valori; "nessun valore inventato" e' esplicito (`:852-853`).
- **Blocco 1** (`:867-893`): `munition_class` + `ad_detectable` nei registri, Maverick fisso False con commento "decisione, non STIMA" (`:873-875`), dimensioni di supporto e test di coerenza del metro (test 5, `:887-890`). Fedele a BI-1/BI-6/BI-7.
- **Blocco 2** (`:895-1000`): le tre tabelle (`:905-909`) coincidono con R-BI-3 (`:325-334`) e BI-12 (nessun 'land' per `tactical`/`arm`); campo `intercept_domains` in coda con default None e validazione (`:931-933`); filtro `_admissible` prima di L1/R-INT a `:3350` [V riga reale]; conteggio `:3291` condizionato all'interruttore (`:941-942`). Fedele.
- **Blocco 3** (`:1001-1031`): S35 con fire control dei registri (armi vere, non `test:*`), asserzioni qualitative con istruzione "riferire invece di cambiare" se una variante non produce intercettazioni (`:1029-1031`). Fedele; attese non calcolabili dichiarate [I] (`:1145-1146`).
- **Blocco 4** (`:1033-1045`): manuale, limiti (incluso il limite BI-12), nota di rimando alle regole precedenti ristrette. Fedele.

### 3.3 Contraddizioni interne cercate (compito A)

1. **BI-2 vs "tutti gli A2G esclusi"**: esplicitata dalla Proposta stessa (`:571-576`) e risolta
   dall'utente; incoerenza I-1 censita (`:822-826`). Non nascosta. [V]
2. **BI-4 vs regola del 2026-09-28**: esplicitata (`:248-251`, `:613-616`, I-4 `:832-833`); il
   blocco 4 aggiorna i documenti vecchi. Non nascosta. [V]
3. **BI-8 vs regola**: deviazione censita con numeri della sonda (v. tabella BI-8). [V]
4. **BI-12 vs "e/o dimensioni"**: la clausola dimensione non vale per i terrestri (un Kh-29 grande
   sfugge ai terrestri che fermano il Kh-59): e' I-1, dichiarato e accettato. [V]
5. **Nuova, trovata da me (MINORE M1)**: la classe `anti_ship` esclude ogni difesa terrestre
   ("non spara a terra", tabella R-BI-3 `:329`), ma un antinave lanciato da **bombardiere** contro
   un bersaglio **terrestre** (es. Kh-22N da Tu-22M) resterebbe non intercettabile da nessuno,
   mentre la regola dell'utente esclude gli A2G solo per "cacciabombardieri/aerei d'attacco" e
   ammetterebbe un cruise da bombardiere. Nessun caso in fotografia (B-0) e classificazione [S]
   soggetta al blocco 0 (Kh-22N potrebbe risultare `cruise`): rischio residuo basso, ma il caso
   limite manca in §2.3. Correzione: una riga in §2.3 o una nota per il blocco 0.
6. **Nuova, trovata da me (MINORE M2)**: default `AD_DETECTABLE_DEFAULT['anti_ship'] = True`
   (`:909`) ammette come bersaglio navale un antinave senza dati dimensionali, presuma di
   compatibilita' che la regola condiziona alle dimensioni. Il test di coerenza lo corregge solo
   se il blocco 1 registra diametro e massa; le voci senza dimensioni sfuggono (limiti dichiarati
   `:1121-1122`). Gia' censito dalla Proposta come limite: lo segnalo per completezza.
7. **Coerenza incrociata verificata**: le classi derivate senza dato nuovo (`:359-361`) coprono
   AAM/SAM/ATGM/bombe/razzi/cannoni/siluri, tutti esclusi da R-BI-3 (`:332-334`): nessun missile
   "civettato" dentro per effetto collaterale. La famiglia Maverick ha flag esplicito che
   prevale sul default (`:318-321` vs `:909`). [V]

## 4. Completezza per l'esecutore (punto D)

### 4.1 Punti dove l'esecutore deve indovinare (tutti dichiarati o risolti da questa revisione)

| Punto | Dove sta nella Proposta | Gravita' |
|---|---|---|
| Loadout Kh-59 per la variante `land_cruise` di S35 ("da scegliere fra quelli esistenti; se nessuno porta i soli Kh-59, filtro d'arma designata della F7a come in S19AD") | `:1010-1012` | bassa: la regola di fallback e' data; scelta minore coperta da AGENTS.md ("scelte minori sono tue: elencale") |
| Geometrie di S35 da costruire e misurare; attese qualitative [I]; se una variante non produce intercettazioni nemmeno `_off`, **riferire** invece di cambiare le asserzioni | `:1018-1031`, `:1145-1146` | bassa: istruzione di arresto esplicita (regola di AGENTS.md) |
| Scorer dei registri con campo nuovo ("verifica prima di scrivere... se lo fanno, fermarsi e riferire") | `:879-881` | **nulla da indovinare: verificato da me** [V: `get_missiles_score` (`Aircraft_Weapon_Data.py:441-537`) e `get_weapon_score` (`:765-798`) leggono campi per nome, mai iterano su tutte le chiavi] |
| `restrict_by_policy` non ricostruisca le `ShotSpec` per campi espliciti | `:950-951`, `:1143` | **nulla da indovinare: verificato da me** [V: `Logic/Fire_Control.py:926-970` filtra con `policy.allows(option.weapon, tclass)`, nessuna ricostruzione; il campo nuovo con default non crea problemi] |
| Righe citate slittate per FP/VA: "cercare i punti per contenuto e riferire" | `:845-846` | bassa: ho ricontrollato le righe chiave oggi: `Fire_Control.py:763-768`, `Engagement_Resolver.py:614,3291,3350` tutte valide [V §1 del rapporto] |
| Il blocco 0 (ricerca dati dei 52 missili aria-superficie) **non e' dell'esecutore**: precondizione esplicita, esecuzione bloccata finche' non e' approvato | `:839-846`, `:848` | nessuna ambiguita' |

### 4.2 Dati mancanti, valori [S], test con attese non calcolabili

- Dati mancanti (nessuno dei quali a carico dell'esecutore): classe e flag dei 52 `MISSILES_ASM`
  (blocco 0, `:848-865`); dimensioni Maverick/Harpoon con fonte (ancore, `:855-856`); geometrie
  S35 (`:1145-1146`). Tutti censiti in §8 "Cosa non ho potuto verificare" (`:1134-1150`): onesto.
- Valori [S] da dichiarare: le tre tabelle di `Fire_Control` (`:898-909`, commenti `[S]` previsti),
  il default di `ad_detectable` (`:909`), le ancore nel test 5 del blocco 1 ("scritti come costanti
  del test con la fonte", `:887-888`), la classificazione §2.2 [S]. Il Maverick e' marcato
  "decisione, non STIMA" (`:873-875`): corretto rispetto ad AGENTS.md ("mai spacciare valori
  inventati per dati tarati").
- Test con attese non calcolabili: le asserzioni numeriche di S35 (quante intercettazioni per seme)
  NON sono pretese: le attese sono qualitative (>0, =0, "uguali per seme tra _off e _on", `:1018-1023`),
  con determinismo per seme. Le attese forti (32 NEW, 6 CHANGED in B-1) derivano dalla sonda B-0,
  che ho verificato coincidere con i file [V §2]. Il test 6 del blocco 1 chiede di leggere i
  punteggi **prima** della modifica e inserirli nel test: procedura deterministica, riproducibile.
- La suite base non e' mai dichiarata come numero (solo `Ran B` simbolico, "letto dall'ESITO, mai
  stimato", `:1094`): scelta coerente con AGENTS.md; con base D-5 = **4795** [dato del principale]
  i valori attesi assoluti sarebbero 4801 (blocco 1), 4816 (blocco 2), ~4830 (blocco 3): nessun
  numero nel documento li contraddice.

### 4.3 Coerenza dei conteggi dentro il documento [V, riletto]

- Blocco 1: 6 test (`:882`); blocco 2: ~21 = 10 Fire_Control (`:964-973`, con "1bis") + 9 risolutore
  (`:975-986`) + 2 sessione (`:988-989`); blocco 3: ~15 (`:107`). Somme cumulative §6.1: B+27 (21+6),
  B+42 (+15) (`:1099-1101`): coerenti fra loro e con §0 (`:106-108`).
- S35: 4 geometrie x 2 stati x 4 semi = 32, identico in BI-10 (`:774`), §0 (`:97`) ed esito atteso
  (`:1027-1028`). Il "24" a `:762` e' il conteggio della prima stesura a 3 geometrie, esplicitamente
  aggiornato dalla decisione: non e' un errore, e' la storia della scelta.
- "1009 identiche" con interruttore spento (`:93`, `:893`, `:993`): coerente con la sonda (1029
  esecuzioni - 20 nuove S32 = 1009 della fotografia) [V §2].
- Append di S35 in `Scenario_Baseline.UNITS` "in coda, dopo S32" (`:1024-1026`): verificato che
  S32-DWELL e' oggi l'ultima riga e che S33/S34 non esistono ancora [V: `Scenario_Baseline.py:396`,
  grep S33/S34 senza occorrenze]: l'istruzione "dopo S33/S34 se gia' presenti" copre il caso.

## 5. ESITO

### 5.1 Problemi trovati, ordinati per gravita'

**BLOCCANTI**: nessuno.

**IMPORTANTI**: nessuno.

**MINORI**:

1. **M1 — caso limite mancante: `anti_ship` da bombardiere contro bersaglio terrestre.** Con la
   tabella R-BI-3 (`Proposta:329`) un missile classe `anti_ship` non e' bersaglio di nessuna
   difesa terrestre ("non spara a terra"); ma la regola dell'utente esclude gli A2G solo per
   cacciabombardieri/aerei d'attacco, e un Kh-22N (Tu-22M, bombardiere) contro terra sarebbe
   un cruise bersaglio legittimo dei terrestri. Scenario: nessun caso in fotografia (B-0 [V §2]),
   S35 non lo copre. Correzione suggerita: una riga in §2.3 o una nota al blocco 0 (la
   classificazione e' [S] e il blocco 0 puo' classificare il Kh-22N `cruise`). Da: `des-planner`
   o sessione principale, in fase di blocco 0; non ferma l'esecutore.
2. **M2 — default `anti_ship` True senza dati dimensionali** (`Proposta:909`): presume la
   compatibilita' che R2 subordina alle dimensioni; il test di coerenza (`:887-890`) corregge solo
   le voci con diametro e massa registrati. Gia' censito come limite (`:1121-1122`): nessuna
   azione necessaria oltre alla consapevolezza; eventualmente il blocco 0 puo' insistere sul
   cercare le dimensioni degli antinave.
3. **M3 — attribuzione per arma delle intercettazioni del Molniya non misurata dalla sonda**
   (`Proposta:299-301`): l'affermazione "l'arma e' il CIWS AK-630" e' inferita dal registro, non
   dalla sonda. Nessun impatto sul piano (B-1 guardera' gli `InterceptionEvent` per arma).
   Nessuna azione.

### 5.2 Verdetto

**PRONTO PER L'ESECUTORE.** Le decisioni BI-1..BI-12 realizzano le regole dell'utente; le
contraddizioni interne alla regola (BI-2, BI-4) e la deviazione censita (BI-8) sono state messe
nero su bianco e risolte dall'utente, non appianate dal planner; i numeri della sonda B-0 citati
nel documento coincidono con i file [V §2]; le righe di codice citate esistono e sono come
descritte [V §1]; i nomi nuovi non collidono [V]; le due verifiche lasciate all'esecutore
(scorer, `restrict_by_policy`) sono state svolte da questa revisione con esito OK, quindi
l'esecutore le ritrovera' confermate. Precondizione operativa: il blocco 0 deve essere approvato
prima di iniziare (`Proposta:839-846`), come il piano stesso stabilisce.

### 5.3 Cosa NON ho controllato (limiti della revisione)

- Non ho eseguito suite ne' confronto (vietato dal compito): la bonta' delle attese "1009
  identiche", "32 NEW" e "B+27/B+42" resta da provare all'esecuzione; ho verificato solo la
  coerenza interna dei conteggi e la corrispondenza con la sonda.
- Non ho verificato i documenti citati ma non letti: `Proposta_Regole_Allocazione_SAM.md:308-311,
  407-408, 435`, `Proposta_Dati_Anti_Missile.md:19`, le righe del manuale
  (`05_Strato2_Risolutore_Ingaggio.md:179,900,1620-1736`, `10_Limiti_Estensioni_Divergenze.md:282`),
  l'atlante `11a:1308`, e i contenuti delle Proposte VA/FP (solo citati in §6.1, non riletti).
- Non ho verificato il registro del Molniya (SA-N-4 senza task `Anti_Missile`, AK-630 si') [I],
  i loadout Kh-59 su Su-30/Su-34 [I, dichiarati [V] dal planner che ha eseguito i registri], e le
  statistiche aggregate di §1.5 (conteggi 44/42/54/26/8/12): le voci specifiche che servono al
  piano (AGM-65D/K, RB-75T, Kh-59/59M, Kh-29L/T/TE, KD-63/63B, AGM-84A, AGM-88, Kh-58, candidati
  piccoli, RGM-84, BGM-109) le ho invece verificate una per una [V §1].
- Non ho verificato `Scenario_Baseline.summarize_run` (citata per "non registra le ShotSpec")
  ne' `Weapon_Stores.py:58-68` (`ROUNDS_PER_GUN_INTERCEPT`): asserzioni [V] del planner lasciate
  al verdetto della suite dell'esecutore.
- Non ho verificato riga per riga `probe_intercepts.py` (che la sonda non alteri il motore): mi
  fido dell'esito confrontato (0 DIFF su 1029) e del `replay_mismatch` 0 [V: esito.txt].
- La classificazione delle armi di §2.2 (cruise/anti_ship/arm/tactical) e' una proposta [S] su
  conoscenza generale: NON verificabile in questa sede (e' il lavoro del blocco 0); ho verificato
  solo che le armi citate esistano nei registri e che i task dichiarati non contraddicano la
  proposta (es. AGM-65D task `Anti_Ship`/`Strike`/`SEAD` [V: `Aircraft_Weapon_Data.py:2503`]).
