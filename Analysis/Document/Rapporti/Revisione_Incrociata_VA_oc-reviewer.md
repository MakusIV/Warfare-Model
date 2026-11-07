# Revisione incrociata 2 di 3 — Proposta VA (Volumi Allineati)

Autore: `oc-reviewer` (revisione indipendente, sola lettura). Data: 2026-11-07.
Commit di lavoro: `94b391c9` (checkout principale, working tree pulito salvo i rapporti di revisione
BI e VA, non tracciati). **Non** eseguiti suite, confronto ne' sonde, come da compito.
Documento revisionato: `Analysis/Document/Proposta_Allineamento_Volumi_DES_Pianificatore.md`
(1227 righe), letto per intero. Contesto: `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (BI,
*Bersagli Intercettabili*), `Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (FP, *Finestre per
Passaggio*), `AGENTS.md`. Acronimi alla prima comparsa: DES (*Discrete Event Simulation*), VA
(*Volumi Allineati*), AAM (*Air-to-Air Missile*), RNG (*Random Number Generator*), CPA (*Closest Point
of Approach*), FC (*fire control*, controllo del tiro), SAM/AAA (missili/artiglieria contraerea).

Legenda: [V] verificato leggendo (file:riga); [I] ipotesi; [S] stima.

---

## 1. Perimetro e metodo

Ho riletto una per una le citazioni di codice del §1 e del piano §4 sui file reali del checkout, i
valori dei registri d'arma citati, lo script della sonda e i suoi esiti locali (`.ai-run/`), le
 strutture di test di S19/S32 e `Scenario_Baseline`, e le tabelle di conflitto BI/FP. Non mi sono
fidato dei rapporti dei planner: ogni numero citato nella §1.7 e' stato confrontato con i log
`.ai-run/sonde_volumi/v1/log.txt`, `v2/log.txt`, `v2b/log.txt`.

## 2. Riferimenti di codice verificati (domanda B: OK/NO + riga)

| Citazione nella Proposta | Esito | Codice reale [V] |
|---|---|---|
| `Fire_Control.py` `in_altitude_envelope` (~:628-655) | **OK** | `:628-656`: aria `target_z <= max_height_m` (:636-638), senza tetto `abs(Δz) <= air_range_m` (:640-643), fascia relativa `min_alt <= z_t - z_s <= max_alt` (:650-651), nessun dato → `relative <= air_range_m` (:653-656); quota ignota → True (:633-634) |
| Memoizzazione (~:862-869: chiave come descritta?) | **OK** | `:860` `cache_key = (shooter_key, keys, dimension, is_air, shooter_z, target_z)`; lettura quote `:858-859` (`_z(shooter)`/`_z(target)` solo `if is_air or bomber`). §1.2 (:130) la cita semplificata, §4.1.3.1 la riporta esatta |
| `make_registry_fire_control` | **OK** | `:806` (`altitude_filter=True` di default), interna `fire_control(shooter, target, target_grounded=False)` `:838`, accetta `target_grounded` |
| `restrict_by_policy` (esiste? come dichiara le keyword?) | **OK** | `:926-981`: dichiara `target_grounded` solo se la base la accetta (`ER.accepts_target_grounded` :971); 2 varianti odierne (:972, :978); le 4 varianti del piano §4.1.3.3 estendono lo schema senza contraddirlo |
| Precedente `target_grounded` (introspezione) | **OK** | `Engagement_Resolver.py:1669` keyword, `:1672-1691` `accepts_target_grounded` (firma o `**kwargs`); la generalizzazione `accepts_keyword` (§4.1.2.5) e' un cambio di nome del corpo attuale, fattibile senza alterare i risultati |
| `ShotSpec` (~:587-650) | **OK** | `:586-648`; validazione `max_range` `:641-644` (dove il piano aggiunge le sue); campi nuovi in coda con default None → nessun costruttore esistente si rompe |
| `_range_entry` (~:2984-3017) | **OK** | `:2984-3017`: chiave `(shooter_id, target_id, float(max_range))` :2994, ciclo multi-intervallo :3010-3015, ripiego `engagement_intervals_without_legs` :3003, chiamata a 3 argomenti :3001 (la spia del test 13 resta verde) |
| `engagement_intervals` | **OK** | `:1708-1715` (delega a `range_intervals`); attributo sostituibile `:1832`; usata solo da `_range_entry` e dai test (`Test_Engagement_Resolver.py:2009-2030`, valore `[(70.0, 100.0)]` a :2025 = attesa del test 9) |
| `_schedule_next` (~:2541-2558) | **OK** | `:2533` scelta con `_first_with_stock(_fire_control(...))`, `:2535-2539` ramo `choice is None` (esaurito), `:2549` `_range_entry`, `:2556` `not_before` |
| `_in_range_at` (~:2866-2884) | **OK** | `:2866-2884`: `:2872` `_first_with_stock(_fire_control(...))`, `:2883` `_range_entry`, `:2884` `<= t_fire + TIME_EPS` |
| `_call_fire_control` / `_fire_control` | **OK** | `:2834-2860` / `:2819-2832` (il piano dice :2835-2860: scarto 1 riga); `fire_control_knows_grounded` lazy :2850-2851, modello replicato da `fire_control_knows_altitudes` |
| `Contact_Scheduler.range_intervals` (~:873) | **OK** | `:874-935`; caso a breakpoint unico `:903-907` (stessa forma che il piano richiede per `altitude_intervals`); `_merge_intervals` `:938-952`; `TIME_EPS` `:92` (1e-9); `VELOCITY_EPS` `:98` = soglia su |Δv|², il piano dice bene di non riusarla (§4.1.1) |
| Chiamate a `range_intervals` nel risolutore | **OK, 2** [V] | `Engagement_Resolver.py:2206` (`_detection_time`) e `:2238` (`_exposure_time`), piu' la delega `:1715` dentro `engagement_intervals`: coerente con §2.3 ("oggi 2, con FP 4") |
| Nomi nuovi (`altitude_intervals`, `intersect_intervals`, `accepts_keyword`, `accepts_altitudes`, `ALTITUDES_KEYWORD`, `max_target_z`, `VA_ENGAGEMENT_ALTITUDE_BAND`, `_altitudes_at`, `_band_of`, `_altitude_deferral`, `_own_intervals`) | **OK, nessuna collisione** [V] | `grep -rn` su `Source/*.py`: zero occorrenze; `_own_intervals` non esiste ancora (FP non eseguita, coerente con lo stato) |
| `position_on_legs` gia' importata nel risolutore | **OK** [V] | `Engagement_Resolver.py:468` |
| Registra AAM: `max_height` | **OK** [V] | `Aircraft_Weapon_Data.py`: AIM-9B :1242, AIM-9P :1267, AIM-9P5 :1292, AIM-9L :1317, AIM-9M :1342 (tutte 18 km), AIM-9X :1367 (25), AIM-54 :1001-1082 (24,8), R-73 :1644 (20), R-530EM :1443 (20), PL-12 :1983 (21), R-37 :1954 (30): intervallo 18-30 km come da §2.6; conversione km→m `Fire_Control.py:373-374`; **nessuna** `min_altitude` nei record AAM (le `min_altitude` del file sono solo nelle finestre `release` delle bombe, da :5219) |
| SAM terrestri/navali citati | **OK** [V] | `Ground_Weapon_Data.py`: 9M33-SAM :2603 (10 000 m, 25-5000 "m AGL" :2612-2613), 3M9-SAM :2683 (24 000 m, 100-14 000 :2692-2693), S-68-57mm :2254, AZP-23-23mm :2270; `Ship_Weapon_Data.py:1050-1051` (RIM-162-ESSM 15-15 000 "m AGL"); `Vehicle_Data.py:4123` (9A33-Osa), radar aria 30 km `:4144`; 26 s di reazione Osa `Context/Reaction_Profile.py:168` |
| `_Weapon.domain` per il navale | **OK** [V] | `Fire_Control.py:497` (dominio `'ship'`), :429: la condizione del piano `weapon.domain in ('ground', 'ship')` (§4.1.3.2) e' corretta; l'attibuto `min_alt`/`max_alt`/`max_height_m` usato dal piano esiste (:371-374) |
| Strutture di test citate | **OK** [V] | `Scenario_Fixtures.py`: SHOTS :802-826 (senza `max_range` ne' quote), "non calibrati" :800-801, `route_for` con terza coordinata :584; `Test_Session_Scenarios_S19_Air_Defence.build` :69-76 (A-10C a (-40 000, 0, 3000), passo (0,500), 'Maverick/Gun CAS'), `IFV_IDS` :66, `VISUAL` :47, `MAVERICK` :48, `DURATION` :49; S32: `SEEDS` 4 :46, `VARIANT_SPEC` :48, `ER_MODULE` :43, `patch.object(ER_MODULE, 'D5_DWELL_TIME', ...)` :95; `Scenario_Baseline.py`: `_by_occurrence` :227, `UNITS` :265; `Session_Simulator.py:2282` unico avvolgimento `restrict_by_policy`; `Area_Fire` usa `plan_shot` (:202, :259); `Ground_Weapon_Data` `GROUND_WEAPONS['MISSILES']` :2336 (il test 22 puo' leggere il record 9M33 dal registro) |
| VA-6 (a) scritta nel blocco 1 della FP | **OK** [V] | `Proposta_Finestre_Per_Passaggio...md`: titolo righe 10-12, firma `_own_intervals(observer_id, target_id, own_range, radius=None)` :835-836 (raggio invariato, non fattore), punto 8-bis :975-986, test 20 :1142-1145: identica a quanto dichiarato in VA §2.3/§3 (VA-6) |

## 3. Fedelta' alle regole dell'utente (domanda A)

- **VA-1 [V]**: la regola R3 dell'utente ("nel DES la portata e' 3D ma va distinta dalla quota
  massima; sfera ∩ fascia relativa al tiratore; cilindri nel pianificatore come prima
  approssimazione") e' realizzata pari pari: sfera ∩ fascia relativa (§2.1), pianificatore col suo
  cilindro invariato dichiarato involucro conservativo (VA-4 (a), §2.2 — la contensione geometrica
  sfera∩fascia ⊆ cilindro e' corretta); i raggi orizzontali campionati di §2.1 sono esatti
  (SA-6 a 10 km: 21,82 km; Osa a 6 km: 8,00 km; ZSU-57-2 1,41x). Nessuna costante nuova.
- **VA-2 (d), coerenza dei due meccanismi [V]**: non ci sono contraddizioni. La disuguaglianza e'
  una sola (`in_altitude_envelope`, `Fire_Control.py:628-656`), valutata dalla FC (fire control)
  all'istante della decisione con le quote dei tratti passate per introspezione (`altitudes`), e dal
  risolutore nel tempo sugli stessi dati di registro copiati nella `ShotSpec`. Casi limite:
  (i) FC sceglie l'arma ma l'ingresso in sfera ∩ fascia e' piu' tardi → `not_before` con il
  meccanismo di portata esistente (:2556); (ii) mai in sfera ∩ fascia → esaurito (`:2552`), coerente
  con la regola; (iii) FC nessuna arma per quota → rinvio VA-2.1; (iv) bordo/arrotondamento →
  scelta immediata `(None, (spec, colpi))` del rinvio. Residuo non dichiarato: arma con fascia ma
  `max_range = None` (v. §6, MINORE 1). Il protocollo `altitudes` e' la generalizzazione pulita di
  `target_grounded` (`Engagement_Resolver.py:1669-1691`); la FC dei registri userebbe `altitudes`
  solo `if is_air or bomber` come oggi (`Fire_Control.py:858-859`), quindi le coppie
  superficie-superficie non cambiano neanche di chiave di cache.
- **VA-2.1 (i), rinvio ben definito [V]**: trigger (FC None a `t_fire`, bersaglio aereo in volo,
  tratti e keyword dichiarati), richiamo con `altitudes=(None, None)` (nessun filtro di quota:
  politica dichiarata in `Fire_Control.py:90-92`), ingresso per opzione con scorta in ordine di
  preferenza (scorta come `_first_with_stock` :2965-2982), minimo → `not_before`, scelta immediata al
  bordo. La mutazione del candidato e' solo in `_schedule_next` (giusto: `not_before` e' il meccanismo
  esistente per la portata), mentre `_in_range_at` non muta (rinvio non e' "a portata adesso").
  Ho verificato **tutti** i punti di esaurimento del risolutore (:2467 bersaglio sparito, :2476
  finestra chiusa, :2538 FC-None — l'unico toccato dal rinvio, :2552 mai in portata, :3061
  annullamento al lancio): la copertura del rinvio e' completa, nessun altro ramo decide per None
  della FC. Nessun rischio di ciclo: il rinvio va a un istante > `t_fire` (o sceglie subito), e a
  `t_next` l'ingresso della stessa opzione e' `<= t_next + TIME_EPS` (chiusura del bordo).
- **VA-3 (b) [V]**: tetto **assoluto** `max_target_z` [m] dalle stesse due convenzioni della FC
  (`max_height` km → m :373-374; confronto `target_z <= max_height_m` :636-638), **nessuna quota
  minima** perche' il registro AAM non l'ha (verificato: nessuna `min_altitude` nei record AAM).
  Coerente fra istante (FC) e tempo (risolutore, `relative=False`).
- **VA-5/VA-6/VA-7 [V]**: separazione ingaggio/rilevamento rispettata (il piano tocca solo
  `_range_entry` e la FC, non `_detection_time`/`_exposure_time`); VA-6 (a) gia' scritta nella FP
  con la firma dichiarata; interruttore `VA_ENGAGEMENT_ALTITUDE_BAND = False` a imitazione di
  `D5_DWELL_TIME` (:519-525), letto alla costruzione della run (i test lo patchano sul modulo come
  S32 :95): con l'interruttore spento i quattro percorsi nuovi (`_altitudes_at`, `_band_of`,
  `_altitude_deferral`, keyword `altitudes`) restituiscono tutti il comportamento di oggi
  (chiamate, chiavi e istanti identici): ho seguito ciascun percorso sul codice e concordo.
- **VA-8r [V]**: 8 varianti x 4 semi = 32; `late_descend` e' effettivamente l'unica geometria che
  distingue VA-2.1 (i) da (ii) (l'ho verificato sui calcoli di §4.2.1: sfera 10 km/fascia 25-5000,
  ingresso a ~8,3 km orizzontali a quota ~4150 m, discesa sotto i 5000 m a x = -10 km: corretto);
  `descend` non richiede rinvio (sotto i 5000 m gia' a ~34 km dal sito, prima del rilevamento a
  30 km): corretto.

## 4. Le sonde (domanda C)

- `Analysis/Document/Rapporti/Sonde_Allineamento_Volumi/probe_altitude.py` **esiste** (631 righe,
  versionato nel commit `94b391c9`), docstring e contatori corrispondono alle descrizioni di §1.7
  [V].
- La Proposta indica **dove** sono stati ottenuti gli esiti e **come ripeterli** (§1.7: comando
  completo, ~11 minuti, uscite in `.ai-run/sonde_volumi/{v0,v1,v2,v2b}`, dichiarate "fuori dal
  versionamento") [V].
- Ho confrontato i numeri citati con i log locali **senso per senso**: `compared 1029 runs: 20
  difference lines`, `PROBE_RC 1`, 0 righe DIFF/CHANGED (v2), 1258 ingaggi, FC di test 191+941=1132
  e dei registri 12+114=126, 28 214/7 489 salve, 252/242 con arma del registro, `sw_above_max` 0 /
  `sw_below_min` 0, 6 977 con `ShotSpec` di test, 1 510 salve con cilindro (523 sopra: ZSU-23-4 504,
  Strela-10 16, Tunguska 3; 0 sotto; 1 238 oltre il raggio, ripartizione identica), 42 esecuzioni
  sopra il tetto (2+6+6+6+6+16), 162 fuori dal cilindro, 362 candidati/48 esclusi/0+0, 978/0
  controlli fascia, 90/0 tetto, 3 091 chiamate FC/0 differenze/0 quote di sgancio, 48 rinvii in 14
  esecuzioni (S19 4 x 5, S21R 6 x 2, S31 `vads_high` 4 x 4), 353/353 chiavi, V-2b `fc_air_defer` 48
  e `fc_air_defer_entry` 0. **Tutti coincidenti** [V].
- Nota: l'esito grezzo non e' versionato (solo la tabella della Proposta e lo script lo sono); e'
  ripetibile col comando documentato. V. §6, MINORE 5.

## 5. Copertura dei test (parte "qa")

**Conteggi** [V]: blocco 1 = 5 (TestAltitudeIntervals) + 2 (TestIntersectIntervals) + 14
(TestEngagementAltitude, n. 8-21) + 2 (Test_Fire_Control, n. 22-23) = **23**; blocco 2 = **9**;
suite attese `Ran B+23` e `Ran B+32` (23+9=32) coerenti; 8 varianti x 4 semi = 32 esecuzioni;
dimensione ~215 + ~680 righe [S] interna coerente (~60+110+45 e ~420+260).

Punti di forza: le attese sono quasi tutte calcolabili a mano e lo sono davvero (25,0/75,0;
[(70,0, 100,0)] confermato dal test esistente :2025; t = 120 s del rinvio; `salvo.spec.weapon`;
`max_target_z == 18000.0` dal registro). I test 13-14-17 coprono i tre ripiegati a interruttore
spento/senza keyword/senza tratti; il test 19 copre la regressione "piu' armi" che aveva fatto
scartare la VA-2 (c); i test 20-21 coprono il rinvio riuscito e impossibile; il test 23 copre le
quattro varianti di `restrict_by_policy`; il test 8-9 della S34 (determinismo, stream identico in
`level`) sono forti.

Lacune e suggerimenti, con priorita':

- **Media** — rinvio ripetuto: se all'istante del rinvio la scorta dell'arma d'ingresso e' nel
  frattempo consumata, la decisione differisce di nuovo (termina per costruzione, ma nessun test
  copre due rinvii in cascata). Suggerimento: un test con una FC spia che restituisce None alla
  seconda chiamata con le quote e un'arma alla terza (esecutore, nel blocco 1).
- **Media** — arma con fascia ma `max_range = None`: nessun test ne copre il comportamento (con VA
  acceso la fascia e' verificata solo all'istante, non nel tempo). Se il caso e' ritenuto in
  perimetro, un test esplicito + dichiarazione al §5.2 (esecutore/planner).
- **Bassa** — `altitude_intervals` con `relative=False` e `z_min` dato non e' mai usata dal
  risolutore (solo `(None, max_target_z)`): ramo della primitiva senza test dedicato; utile per la
  Attivita' D futura (esecutore).
- **Bassa** — nessun test diretto che a VA spento le chiavi della cache della FC siano le stesse di
  oggi (il test 23(i) copre il caso `altitudes=None`); il confronto con 1009 identiche lo copre a
  posteriori (non serve altro).

## 6. Problemi trovati (ordinati per gravita')

**BLOCCANTI**: nessuno.

**IMPORTANTI**: nessuno.

**MINORI**:

1. **Fascia senza portata, asimmetria non dichiarata** — `Proposta...md` §4.1.3.2/§4.1.2.10: una
   `ShotSpec` con fascia (o tetto) ma `max_range = None` non riceve alcun controllo nel tempo (il
   rinvio stesso salta le opzioni senza `max_range`, §4.1.2.12 "si salta se `spec.max_range` e'
   None"): la "una sola disuguaglianza, due istanti" vale solo all'istante (FC). Scenario: arma del
   registro con `min_altitude`/`max_altitude` ma senza `range` [I: frequenza non verificata]. Non e'
   una regressione (meglio del filtro statico), ma e' un residuo che il §5.2 non dichiara.
   Correzione suggerita: dichiararlo in §5.2 (o popolare la fascia solo con `max_range` presente) —
   chi pianifica la VA (sessione principale), prima o durante l'esecuzione.
2. **Annotazione `range_cache` non aggiornata** — `Engagement_Resolver.py:1833` dichiara
   `Dict[Tuple[str, str, float], ...]`; con la chiave allargata a `band` (§4.1.2.10) l'annotazione
   va estesa. Il piano non lo dice: scelta minore per l'esecutore, da elencare nel rapporto.
3. **§2.8 stille' "BI-12 aperta"** — `Proposta...md:559` contro lo stato reale della BI
   ("TUTTE le decisioni BI-1..BI-12 prese", `Proposta_Bersagli...md:3`, BI-12 (a) a `:790`).
   Documentale, senza effetto sul piano (la precondizione §4.0.2 e' "BI eseguita", non "BI-12
   chiusa"). Chi pianifica la BI o la sessione principale.
4. **§2.8/§6 chiedono un aggiornamento della BI §6.1 gia' fatto** — `Proposta...md:580` e `:1222-1224`
   dicono che la tabella BI §6.1 "dice ancora invariato per VA"; la riga reale e' gia' stata corretta
   (`Proposta_Bersagli...md:1079`: "correzione della stesura precedente"). Nessun lavoro richiesto;
   togliere o aggiornare le due frasi (chi pianifica).
5. **Esito delle sonde non versionato** — i numeri V-0..V-2b esistono solo nella Proposta e nei log
   locali `.ai-run/sonde_volumi/` (fuori dal versionamento, dichiarato). Ripetibili col comando di
   §1.7 (~11 min), ma un revisore senza la macchina che li ha prodotti non puo' verificarli.
   Suggerimento: trascrivere le righe `TOTALS`/`SWITCH` in un esito versionato accanto alla sonda
   (sessione principale, costo nullo).
6. **§2.3 mostra ancora la firma `scale`** — il blocco di codice `Proposta...md:404-410` presenta
   `_own_intervals(..., scale: float = 1.0)`, mentre la decisione (:421-422) e la FP (:835) usano
   `radius=None`. La decisione prevale e la FP e' corretta, ma un lettore frettoloso del §2.3
   potrebbe implementare la variante sbagliata: riferimento esplicito alla firma finale gia' presente
   nella frase successiva (chi pianifica, ritocco).

## 7. Completezza per l'esecutore (domanda D)

- **Niente da indovinare**: interruttore, campi, primitive, introspezione, `_altitudes_at`,
  `_band_of`, `_call_fire_control`/`_fire_control`, `_range_entry` e chiamanti, rinvio (con corpo
  specificato riga per riga e blocco di inserimento in `_schedule_next`), `make_registry_fire_control`,
  `shot_spec_for`, `restrict_by_policy`, docstring, test, scenario S34 con geometria e condizioni di
  arresto della sonda di geometria (§4.2.1, in grassetto), voci `UNITS` e ordine delle varianti
  (vincolo §4.2.3 verificato: l'ordine del blocco `VARIANT_SPEC` e di `_by_occurrence` coincidono).
- Ho controllato le firme/membri usati dal corpo del rinvio: `self._options` (:2947),
  `engagement_intervals_without_legs` (:1718), `self.grounded.at` (in uso a :2847),
  `validate_class` (importato :472), `shooter.available` (in `_first_with_stock` :2972): tutti
  esistenti [V].
- **Rischi gia' dichiarati nel piano** e confermati plausibili: crescita della memoizzazione in
  campagna (V-2: 353 chiavi sulla fotografia; non misurato in campagna, §5.1), quota di sgancio
  delle bombe alla quota dell'istante (§4.1.3.1, V-2: 0 differenze sulla fotografia), percorso nuovo
  del rinvio (§5.1, test 20-21), "prima arma con scorta" senza ripiego (§5.2), fire control di test
  non allineata (§5.2, fuori perimetro).
- **Attese non calcolabili?** nessuna trovata: le attese numeriche dei test derivano tutte da
  geometrie esplicite o dal registro; le soglie "almeno 3 semi su 4" derivano dal calcolo
  probabilistico del rilevamento (u <= ~0,96, marcato [I]/[S] dove serve) e sono salvaguardate dalla
  sonda di geometria obbligatoria con fermata.
- Geometria S34 ricontrollata: 9,54 km orizzontali a 3000 m e 8,0 km a 6000 m (sfera 10 km),
  ingresso `late_descend` a x ≈ -8,3 km quota ≈ 4150 m, sotto i 5000 m a x = -10 km, decisione Osa
  sopra i 5000 m per rilevamenti oltre ~16 km: tutti corretti [V sul registro, calcolo].

## 8. Verdetto

**Pronto per l'esecutore** (dopo la precondizione BI, §4.0.2). Nessun problema bloccante o
importante: tutte le righe citate esistono e corrispondono, i sei problemi minori sono
documentali o casi limite dichiarabili senza toccare il disegno. Il piano rispetta i vincoli di
`AGENTS.md`: interruttore con default retrocompatibile (percorsi a spento verificati identici),
nessuna estrazione RNG (Random Number Generator) nuova o spostata (i percorsi nuovi non chiamano
`_draw`; un tiro tolto/rimandato cambia solo le estrazioni successive di danno, come dichiarato),
nessuna costante inventata spacciata per tarata (quote e posizioni di S34 dichiarate "geometria di
test"; le stime del §4.2.1 sono marcate [I]/[S]), core indipendente dall'adapter DCS (nessun import
nuovo oltre `Contact_Scheduler`, gia' usato), import completi nel piano (`altitude_intervals` e
`intersect_intervals` accanto a `range_intervals`, §4.1.2.4).

## 9. Cosa NON ho controllato

- Suite, confronto e sonde: non eseguiti (divieto del compito). La veridicita' dei numeri V-0..V-2b
  e' stata verificata solo contro i log locali preesistenti di `.ai-run/sonde_volumi/`, non
  rieseguendo la sonda.
- Claim di ricerca del planner non ripetuti da me: "nessun chiamante di produzione usa oggi
  `calcRoute` o `plan_attack_profile`" (§1.1); "nessun modulo di `Logic/` legge
  `altitude_reference='AGL'`" e "nessun modulo modella il terreno" (§1.4); "`threat_windows`/
  `route_threat_windows` non chiamati dalla sessione" (§1.8); "nessun test confronta per uguaglianza
  una `ShotSpec` della fire control con una costruita a mano" e "`summarize_run` registra `weapon`,
  non la `ShotSpec`" (§4.1.4); righe citate di `Mobile.py:392`/`:1396`, `Mission_Types.py`,
  `Weapon_Delivery.py`, `DataType/Cylinder.py`, `DataType/Hemisphere.py`, `Air_Route_Manager.py`
  (oltre `:103-104`), `Piano_Lavori_2026_09_24.md`, manuale DES.
- Volumi [km³] di §2.1 non ricalcolati integralmente (solo i raggi orizzontali campionati); la
  qualita' dei `max_height` AAM rispetto a fonti esterne (dichiarata non verificata anche dalla
  Proposta); la velocita' dell'A-10C [I] e la formula del raggio estratto di §4.2.1 non verificate
  sul codice (salvate dalla sonda di geometria obbligatoria).
- Record di armi SHORAD citati in §2.1 (Chaparral, Tunguska, Strela-10) non riaperti nel registro.
- L'effettiva esistenza di armi del registro con fascia ma senza portata (MINORE 1: frequenza [I]).
- L'esecuzione della FP e della BI (non ancora fatte): le precondizioni §4.0.2 restano da
  verificare all'esecutore al momento del suo avvio.
