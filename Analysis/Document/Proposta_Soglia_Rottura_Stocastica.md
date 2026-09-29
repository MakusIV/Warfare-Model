# Proposta: soglia di rottura stocastica, modulata da morale e stima della forza avversaria

*2026-09-29 — risolve il difetto §5.3 di `Proposta_Regole_Allocazione_SAM.md` (disingaggio alla
prima perdita per forze piccole). Scelta di partenza dell'utente: opzione D (soglia casuale per
forza), estesa con morale e stima della forza d'attacco. Nessuna modifica al codice finché le
decisioni del §8 non sono prese.*

## 1. Il problema, misurato

Oggi (`Context/Doctrine.py`, `Engagement_Resolver._check_doctrine`) una forza rompe il contatto se
`erosione ≥ 0,30` (perdite cumulate / organico impegnato) oppure se `shock ≥ 0,20` (perdite di una
sola salva / organico impegnato). Soglie fisse, uguali per tutti, deterministiche.

Con *n* mezzi la perdita minima è 1/*n*: per forze piccole la soglia è un interruttore.

| mezzi | lo shock scatta alla… | l'erosione scatta alla… |
|---|---|---|
| 1-2 | 1ª perdita | 1ª perdita |
| 3 | 1ª | 1ª |
| 4-5 | 1ª | 2ª |
| 6 | 2ª nella stessa salva | 2ª |
| 10 | 2ª nella stessa salva | 3ª |

Misura su S1 (8 repliche, 2026-09-29):

- **senza CAS**: Blue-Armor (5 mezzi) si disingaggia per *shock* alla **prima perdita** in 7/8
  repliche — lo scontro corazzato si decide con un carro;
- **con CAS**: Red-Line (6 mezzi) si ritira per *erosione* alla 2ª perdita in 6/8 repliche (2/6 =
  0,33), per erosione + shock nelle altre 2; Blue non subisce danni.

Il difetto non è solo la granularità: la stessa soglia vale per una compagnia fresca e motivata e
per una logorata, per chi vede un nemico inferiore e per chi è colpito da un nemico che non vede e
non può colpire. La letteratura sulle soglie di rottura (Helmbold, v. wiki
[[lanchester-models]]) le tratta come una **distribuzione**, non un valore: forze analoghe cedono a
livelli di perdita molto diversi.

## 2. Cosa esiste già nel codice

### 2.1 Morale — esiste ma non è utilizzabile così com'è

`Block.morale` (`Block/Block.py:435`) = `evaluateMorale(mean_success_ratio, efficiency)`
(`Utility/Utility.py:854`, logica fuzzy scikit-fuzzy). Problemi verificati:

1. **Nessuno alimenta il dato**: `State.total_success_ratio` somma `success_count/total_count` per
   task, ma nessun modulo registra gli esiti delle missioni (il TODO in `Context/Region.py:761` lo
   dichiara). Oggi vale sempre 0.
2. **"Sconosciuto" diventa "morale nullo"**: con success_ratio 0 la proprietà restituisce `0.0`, che
   un consumatore leggerebbe come forza demoralizzata al massimo.
3. **Funzioni di appartenenza fuori scala**: `kd` ha universo [0, 1] ma `M` e `H` sono definite su
   [0,75 … 2] e [1,25 … 10]; un success_ratio in [0, 1] non raggiunge mai `H`.
4. **Costo**: il sistema fuzzy viene ricostruito a ogni chiamata; va bene per una valutazione di
   campagna, non per un ingresso ripetuto del risolutore.

Conclusione: il risolutore deve ricevere il morale **come ingresso** (un numero in [0, 1] o None =
sconosciuto → neutro), non leggere `Block.morale`. Aggiustare `Block.morale` e alimentarlo con gli
esiti degli ingaggi (v. §7) è lavoro di campagna, separato.

### 2.2 Stima della forza avversaria — due fonti disponibili

1. **Dentro l'ingaggio**: il risolutore registra i `Detection` (osservatore, bersaglio, istante).
   In ogni istante *t* si sa quali asset nemici una forza ha visto: è la percezione "dal campo", già
   coerente con la nebbia di guerra (C).
2. **Prima dell'ingaggio**: `Context/Combat_Power_Estimation.py` stima la combat power di un blocco
   osservato dalla ricognizione (`asset_summary` per tipo/dimensione) — è la stima "d'intelligence"
   che un C2 avrebbe prima del contatto. Oggi il risolutore non la riceve.

Vincolo noto: la combat power è per dimensione (terra/aria/mare) e SAM/AAA/EWR valgono 0 per
definizione (`Military.air_defense_power()` è una dimensione separata). Un rapporto di forze in
combat power fra una colonna corazzata e due A-10 non è ben definito oggi.

### 2.3 Casualità

`SessionOrder.rng(mission_id, event_id, counter)` genera flussi derivati. Le estrazioni della
soglia possono venire da un flusso **separato** (es. `counter=1`): così non spostano la sequenza
di rilevamenti e danni, e gli esiti degli scenari cambiano solo dove cambia davvero il disingaggio.

## 3. Modello proposto

### 3.1 Tempra estratta una volta, soglia ricalcolata a ogni perdita

All'inizio dell'ingaggio ogni forza che può disingaggiarsi estrae **una volta** un quantile
`u ∈ (0, 1)` — la sua "tempra" in questo scontro. A ogni perdita la soglia di rottura è

```
B(t) = logistic( logit(μ_eff(t)) + σ · Φ⁻¹(u) )
μ_eff(t) = clamp( μ · M(morale) · R(t) · P(postura),  μ_min, μ_max )
```

e la forza si disingaggia se `erosione(t) ≥ B(t)`.

- `μ` è la mediana dottrinale (oggi 0,30), `σ` la dispersione (in scala logit). La
  distribuzione logit-normale sta in (0, 1), si calcola con la sola libreria standard
  (`statistics.NormalDist`) e ha mediana esattamente `μ`.
- `u` fisso e `μ_eff` variabile: la tempra dell'unità non cambia durante lo scontro, cambia la
  situazione percepita. Se il rapporto di forze percepito peggiora, la soglia scende e la forza può
  rompere alla stessa perdita a cui prima reggeva.

**Perché un'estrazione sola e non un "test di morale" a ogni perdita** (stile wargame): con un test
per evento la probabilità di rottura dipenderebbe da quanti eventi-perdita ci sono, quindi da
`salvo_window` e dalla granularità delle salve — un parametro numerico deciderebbe il morale.
Con un'estrazione sola la rottura dipende solo da quante perdite e in che situazione.

Effetto con `μ = 0,30`, senza modificatori (probabilità di aver rotto entro la *k*-esima perdita):

| mezzi | σ = 0,5: 1ª / 2ª / 3ª | σ = 0,7: 1ª / 2ª / 3ª |
|---|---|---|
| 2 | 0,95 / 1 / 1 | 0,89 / 1 / 1 |
| 3 | 0,62 / 1 / 1 | 0,59 / 0,99 / 1 |
| 4 | 0,31 / 0,95 / 1 | 0,36 / 0,89 / 1 |
| 5 | 0,14 / 0,81 / 0,99 | 0,22 / 0,74 / 0,96 |
| 6 | 0,06 / 0,62 / 0,95 | 0,14 / 0,59 / 0,89 |
| 10 | 0,00 / 0,14 / 0,50 | 0,03 / 0,22 / 0,50 |

(σ = 0,5 → deviazione standard ≈ 0,10, 90% delle soglie fra 0,16 e 0,49; σ = 0,7 → ≈ 0,14, fra
0,12 e 0,58.) Le forze di 1-3 mezzi restano fragili: è voluto — una coppia di aerei che perde il
gregario rientra, una sezione di 3 carri che ne perde uno è dimezzata come potenza.

### 3.2 Morale `M`

```
M(m) = 1 + α · (2m − 1)          m ∈ [0, 1], m = None → 0,5 (neutro, M = 1)
```

Con `α = 0,3`: morale massimo alza la mediana del 30% (0,30 → 0,39), minimo la abbassa del 30%
(→ 0,21). Il morale entra come **ingresso** del risolutore (`morale_for: force → Optional[float]`,
stesso schema di `reaction_profile_for`), default None per tutti: finché la campagna non lo
alimenta, il modello si comporta come se fosse neutro, **mai** come se fosse zero.

### 3.3 Rapporto di forze percepito `R(t)`

```
ρ(t) = forza propria operativa(t) / forza nemica percepita(t)
R(t) = clamp( ρ(t)^β, R_min, R_max )        es. β = 0,5, R ∈ [0,6 ; 1,5]
forza nemica percepita(t) = max( stima a priori, asset nemici rilevati entro t )
```

- **Forza propria**: asset propri ancora operativi (la forza sa quanto ha perso).
- **Forza nemica percepita**: il massimo fra la stima con cui la forza entra nello scontro (ingresso
  opzionale `enemy_estimate_for`, dal C2 / `Combat_Power_Estimation`) e ciò che ha rilevato durante
  lo scontro. I nemici distrutti restano contati come "visti" (conservativo: una forza non sa con
  certezza di averli distrutti — rivedibile).
- **Metrica**: vedi decisione D4. Proposta di partenza: **conteggio degli asset combattenti**
  (esclusi logistica/trasporti), uguale per entrambi i lati. Non misura la qualità, ma è definito
  fra domini diversi; la combat power per dimensione ha oggi il problema del §2.2.
- Se la forza non ha rilevato nessun nemico e non ha stima, `R = 1` (neutro).
- `β = 0,5`: rapporto 4:1 a favore → mediana ×1,5 (limite); 1:4 contro → ×0,6 (limite).

### 3.4 Fuoco senza risposta (opzionale, decisione D5)

Una forza che subisce perdite da tiratori che **non ha rilevato** (o non può ingaggiare) cede prima
di una che risponde al fuoco. È esattamente S1 con CAS: Red-Line perde mezzi per Maverick lanciati
da A-10 fuori portata di Shilka e Strela.

```
U(t) = 1 − γ · (perdite causate da tiratori non rilevati / perdite totali)      es. γ = 0,3
```

moltiplicato dentro `μ_eff`. Il dato c'è già: ogni `DamageEvent` ha `source_id`, i `Detection`
dicono chi ha visto chi.

### 3.5 Postura `P` (opzionale, decisione D6)

Difesa su posizione (forza ferma per tutto l'ingaggio) `P = 1,2`, altrimenti `P = 1`. È il fattore
"postura" dei modelli di Helmbold. Il risolutore sa già se una forza si muove (tratti di rotta). Il
valore 1,2 è una stima dichiarata, non un dato.

### 3.6 Shock

Lo shock resta come seconda condizione ma cambia in due punti:

1. **minimo assoluto**: scatta solo se la salva ha tolto almeno `shock_min_losses` mezzi (default 2)
   — un colpo improvviso che rompe una forza è, per definizione, più della perdita minima possibile;
2. **stessa tempra**: soglia `S(t) = k_shock · B(t)` con `k_shock = 2/3` (oggi 0,20 / 0,30). Il
   vincolo `shock ≤ erosione` è garantito dalla costruzione, non più da una validazione.

Con `salvo_window = 0` lo shock diventa raro (servono due perdite simultanee): è coerente con il suo
significato, ma rende più urgente la taratura di `salvo_window` (punto aperto di modello).

## 4. Dove vive

| elemento | dove |
|---|---|
| `μ`, `σ`, `α`, `β`, limiti di `R`, `γ`, `P`, `k_shock`, `shock_min_losses`, `μ_min/μ_max` | `Context/Doctrine.py`, per lato (sostituiscono `erosion`/`shock`; stessa politica: stesse soglie per i tre lati salvo asimmetria dichiarata) |
| morale di ogni forza | ingresso `morale_for` di `resolve_engagement` (default None → neutro) |
| stima a priori della forza nemica | ingresso `enemy_estimate_for` (default None) |
| quantile `u` | flusso casuale separato (`rng` dedicato, es. `SessionOrder.rng(..., counter=1)`) |
| valutazione | `Engagement_Resolver._check_doctrine`, a ogni risoluzione di salva con perdite |
| spiegazione | `ForceOutcome`: `u`, soglia finale `B`, morale usato, `ρ` finale, motivo |

Compatibilità: `σ = 0`, `α = 0`, `β = 0`, `γ = 0`, `P = 1`, `shock_min_losses = 1` riproducono
esattamente le soglie fisse di oggi. Serve come test di non regressione e come modalità
deterministica per i test unitari.

## 5. Effetti attesi (da verificare, non misurati)

- **S1 senza CAS**: Blue-Armor (5 mezzi, in movimento, 5 contro 6 → `R ≈ 0,91`) rompe alla prima
  perdita in circa 1 replica su 6-7 invece di 7 su 8; lo scontro corazzato si svolge.
- **S1 con CAS**: Red-Line (6 mezzi, ferma → `P = 1,2`, ma colpita da A-10 non ingaggiabili → `U`
  < 1) continua a ritirarsi spesso alla 2ª-3ª perdita. È l'esito plausibile discusso il
  2026-09-29: il test che lo vieta (`test_both_sides_take_damage`) va probabilmente riscritto
  come distribuzione di esiti, non come vincolo.
- **Tutti gli scenari**: le asserzioni del tipo "esito X in ogni replica" sulla rottura diventano
  asserzioni su frequenze; il numero di repliche di alcuni scenari potrebbe dover crescere.

## 6. Cosa non fa

- Non introduce coefficienti da fonti non validate: `μ = 0,30` resta la stima di partenza
  dichiarata, `σ`, `α`, `β`, `γ`, `P` sono stime dichiarate da ricalibrare con ATCAL.
- Non modella la rottura parziale (una parte della forza cede, l'altra resiste): il disingaggio
  resta per forza intera (decisione P1 del 2026-09-23).
- Non modella il contagio fra forze dello stesso lato (una forza che vede ritirarsi quella accanto)
  né il legame C2: appartiene alla Fase 0 della gerarchia C2.

## 7. Morale nella campagna (fuori scope, da decidere dopo)

Il morale ha senso solo se ha una memoria: gli esiti degli ingaggi (HELD / DISENGAGED / DESTROYED,
perdite inflitte e subite) devono alimentare `State.success_ratio`, e `Block.morale` va corretto
(§2.1: funzioni di appartenenza, None invece di 0, costo). È il pezzo che collega questa proposta
al C2 regionale ("orientamento guidato da morale", [[c2-hierarchy-design]]).

## 8. Decisioni richieste

| # | domanda | proposta |
|---|---|---|
| D1 | Tempra estratta una volta per forza per ingaggio, oppure test di morale a ogni perdita? | una volta (§3.1) |
| D2 | Distribuzione e dispersione | logit-normale, mediana 0,30, σ = 0,5 |
| D3 | Morale: ingresso del risolutore con None = neutro, peso `α` | sì, `α = 0,3` |
| D4 | Metrica del rapporto di forze percepito | conteggio asset combattenti; combat power quando il problema fra domini sarà risolto |
| D5 | Fattore "fuoco senza risposta" | sì, `γ = 0,3` |
| D6 | Fattore postura (difesa ferma) | sì, `P = 1,2` |
| D7 | Shock con minimo 2 perdite e soglia `2/3 · B(t)` | sì |
| D8 | Flusso casuale separato per la tempra | sì |
| D9 | Correggere `Block.morale` e alimentarlo dagli esiti adesso o dopo | dopo (§7) |

## 9. Piano di implementazione (dopo le decisioni)

1. `Context/Doctrine.py`: nuova tabella dei parametri di rottura con validazione; modalità
   deterministica (§4) per compatibilità.
2. `Engagement_Resolver`: estrazione di `u`, calcolo di `ρ(t)`, `U(t)`, `P`; nuovo
   `_check_doctrine`; ingressi `morale_for`, `enemy_estimate_for`, `breakpoint_rng`; campi in
   `ForceOutcome`.
3. `Session_Simulator`: passaggio del flusso separato e degli ingressi.
4. Test unitari a geometria e perdite controllate (ogni fattore da solo, modalità deterministica =
   soglie di oggi); rimisura S1-S19 e riscrittura delle asserzioni sulla rottura come frequenze.
5. Documentazione: questa proposta (§ implementazione), commento in `Doctrine.py`, manuale DES.

## 10. Decisioni dell'utente (2026-09-29)

**Approvate come proposte**: D1 (tempra estratta una volta), D2 (logit-normale, mediana 0,30,
σ = 0,5), D3 (morale in ingresso, None = neutro, `α = 0,3`), D5 (fuoco senza risposta, `γ = 0,3`),
D6 (postura, `P = 1,2`), D7 (shock con minimo 2 perdite e soglia `2/3 · B(t)`), D8 (flusso casuale
separato), D9 (`Block.morale` dopo).

**D4 respinta nella forma proposta** (conteggio puro): contare un Kub come un Buk non distingue
difese aeree di capacità molto diversa, e la potenza di SAM e AAA non è definita nella combat
power. Richiesta: un **fattore moltiplicativo di efficacia difensiva** per ogni asset di difesa
aerea (SAM e AAA), da una tabella che consideri sia la **potenza distruttiva contro un singolo
aereo** sia la **capacità distruttiva sul numero di aerei nemici presenti nella zona
d'intercettazione**. Proposta nel §11.

## 11. D4 rivista: efficacia difensiva antiaerea

### 11.1 Grandezza: aerei abbattuti attesi durante un attraversamento della zona

Per ogni asset di difesa aerea *i* e per un numero *N* di aerei nemici nella sua zona
d'intercettazione:

```
E_i(N) = N · ( 1 − (1 − p_i)^(K_i / N) )
```

- `p_i` — **potenza contro un singolo aereo**: probabilità che un ingaggio abbatta l'aereo,
  `accuracy × destroy_capacity` dell'arma antiaerea migliore dell'asset contro la classe di
  bersaglio di riferimento (registro d'arma, righe "Aircraft*" introdotte con B1). Per i cannoni
  un ingaggio è una raffica (`GUN_BURST_ROUNDS = 50`, come in `Fire_Control`).
- `K_i` — **ingaggi possibili** mentre un aereo attraversa la zona:
  `K_i = min( c_i · n_cicli , colpi_i )`, dove
  - `c_i` = canali di fuoco (`Mobile.engagement_channels('air')`, `multi_target_capacity`,
    default 1);
  - `n_cicli` = ingaggi successivi possibili nel tempo di esposizione
    `T = 2 R / v_rif` (attraversamento lungo il diametro della zona a velocità di
    riferimento): il primo dopo `acquisizione + sequenza di lancio + tempo di volo` (tempi di
    `Air_Route_Manager.threat_reaction_times`, tempo di volo a metà portata), i successivi
    ogni `sequenza di lancio + tempo di volo` (o durata della raffica per i cannoni);
  - `colpi_i` = missili a bordo, o raffiche per i cannoni: **la scorta corrente**, non quella
    di dotazione (un Buk che ha sparato tutti i missili vale 0).
- La formula distribuisce i `K_i` ingaggi in modo uniforme sugli `N` aerei; ogni aereo si
  abbatte una volta sola. Per `N = 1` vale `1 − (1 − p)^K` (quanto è letale contro un aereo
  solo); per `N` grande tende a `≈ K · p` (quanti aerei può abbattere al massimo): sono le
  due componenti chieste, in una sola funzione.

### 11.2 Bozza di tabella (dai registri, riferimento A-10 = `Aircraft_Attacker` med, 200 m/s)

Calcolata il 2026-09-29 con i dati dei registri così come sono, scorta piena, un asset isolato:

| asset | arma | p | canali | colpi | portata | cicli | K | E(1) | E(2) | E(4) | E(8) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MIM-115 Roland | Roland | 0,33 | 2 | 10 | 6,3 km | 5 | 10 | 0,98 | 1,73 | 2,53 | 3,15 |
| 2K22 Tunguska | 9M311 (+ 2A38M nel modulo) | 0,33 | 2 | 8 | 8 km | 11 | 8 | 0,96 | 1,60 | 2,20 | 2,64 |
| 9K331 Tor | 9M331 | 0,33 | 4 | 8 | 12 km | 12 | 8 | 0,96 | 1,60 | 2,20 | 2,64 |
| 9K37 Buk | 9M38 | 0,50 | 1 | 4 | 35 km | 12 | 4 | 0,93 | 1,49 | 1,98 | 2,31 |
| S-300PS | 5V55R | 0,50 | 6 | 4 | 75 km | 28 | 4 | 0,93 | 1,49 | 1,98 | 2,31 |
| 9A33 Osa | 9M33 | 0,33 | 2 | 6 | 10 km | 6 | 6 | 0,91 | 1,40 | 1,81 | 2,08 |
| **2K12 Kub** | 3M9 | 0,33 | 1 | 3 | 24 km | 8 | 3 | 0,70 | 0,90 | 1,04 | 1,12 |
| 9K35 Strela-10 | 9M37 | 0,13 | 1 | 8 | 5 km | 6 | 6 | 0,55 | 0,66 | 0,73 | 0,77 |
| ZSU-23-4 Shilka | AZP-23 | 0,03 | 1 | 40 raffiche | 2,5 km | 22 | 22 | 0,49 | 0,57 | 0,62 | 0,64 |
| Strela-1 9P31 | 9M31 | 0,13 | 1 | 4 | 4,2 km | 5 | 4 | 0,42 | 0,47 | 0,50 | 0,52 |
| MIM-72G Chaparral | MIM-72 | 0,13 | 1 | 4 | 9 km | 7 | 4 | 0,42 | 0,47 | 0,50 | 0,52 |
| M6 Linebacker | Stinger | 0,13 | 1 | 4 | 4,8 km | 4 | 4 | 0,42 | 0,47 | 0,50 | 0,52 |
| Flakpanzer Gepard | KDA 35 mm | 0,03 | 1 | 13 raffiche | 4 km | 13 | 13 | 0,33 | 0,36 | 0,38 | 0,39 |
| ZSU-57-2 | S-68 57 mm | 0,07 | 1 | 6 raffiche | 4 km | 3 | 3 | 0,21 | 0,22 | 0,23 | 0,23 |
| M163 VADS | M61 20 mm | 0,03 | 1 | 42 raffiche | 1,2 km | 7 | 7 | 0,19 | 0,20 | 0,21 | 0,21 |

Kub contro Buk: contro un aereo solo 0,70 contro 0,93, contro quattro aerei 1,04 contro 1,98.

Cosa la bozza rivela sui dati (da sapere prima di approvare):

1. **`p` è per classe d'efficienza, non per sistema**: Kub, Osa, Tor, Roland, Tunguska sono tutti
   `_EFF_SAM_MERAD` (0,33); le differenze fra loro vengono solo da canali, scorta, portata e tempi.
   Se serve distinguere di più (es. Kub SARH anni '60 contro Tor), la via è un fattore di
   generazione/guida sulla classe, non numeri inventati per singolo sistema.
2. **La scorta per asset domina la saturazione**: il Tor ha 4 canali ma 8 missili, lo S-300PS 6
   canali ma 4 missili per lanciatore. Nel registro un S-300PS è un lanciatore, non una batteria:
   una batteria è più asset (e le loro `E` si sommano, §11.3).
3. **I canali dei radar Buk/Kub valgono 1** (un bersaglio per TELAR/radar, corretto per 9S35 e 1S91).
4. **Esposizione**: l'attraversamento lungo il diametro favorisce le zone grandi; un aereo che
   attacca da fuori zona (stand-off) ha esposizione nulla, ma quello è già geometria del
   risolutore (L1, portate), non efficacia: la tabella misura la capacità potenziale.

### 11.3 Uso nel rapporto di forze percepito `R(t)`

La minaccia rilevante dipende dal **dominio della forza che valuta**:

- **Forza aerea** (tutti aerei), `N` aerei operativi:
  ```
  minaccia(t) = Σ_i E_i(N)   sugli asset AD nemici rilevati entro t (scorta corrente)
              + caccia nemici rilevati (peso 1 ciascuno)
  ρ(t) = N / (κ · minaccia(t))            κ = 2
  ```
  Le zone sovrapposte si sommano (stima prudente per chi attacca). `κ = 2`: una difesa che
  si aspetta di abbattere metà della formazione la "bilancia" (`ρ = 1`, neutro); una che si
  aspetta di abbatterla tutta dà `ρ = 0,5`. Stima dichiarata.
  Esempi con 2 A-10: Strela-10 → `ρ = 1,5`; Kub → `ρ = 1,1`; Buk → `ρ = 0,67`;
  Buk + Kub + Shilka → `ρ = 0,34` (`R` al limite inferiore 0,6).
- **Forza terrestre o navale**: conteggio degli asset nemici rilevati che possono colpire bersagli
  di superficie, peso 1 ciascuno (mezzi da combattimento, aerei d'attacco, cannoni AAA con
  impiego terrestre come Shilka o Tunguska); **peso 0 per i SAM puri**, che non minacciano una
  forza terrestre. Stessa regola per la forza propria, così che il rapporto sia omogeneo.

Il fattore di efficacia AD entra quindi solo dove conta: quando a valutare è chi deve volare
dentro la zona.

### 11.4 Dove vive

- `Context/Air_Defense_Efficacy.py` (nuovo): `air_defense_efficacy(asset, n_aircraft, *,
  stock=None)` → `E_i(N)`, con i parametri di riferimento (classe bersaglio, `v_rif`) come
  costanti dichiarate; letture difensive (modello ignoto → None, mai eccezioni per dati mancanti).
- Tabella di **correzione per modello** opzionale (vuota di default), per quando un sistema
  specifico va distinto dalla sua classe: i valori calcolati restano la base.
- `κ` in `Context/Doctrine.py` con gli altri parametri di rottura.
- Le navi con difesa aerea (registro `Ship_Weapon_Data`) entrano con la stessa formula; nella
  bozza sono escluse perché il calcolo di prova leggeva solo `Vehicle_Data`.

### 11.5 Decisioni aperte su D4

| # | domanda | proposta |
|---|---|---|
| D4a | Grandezza: aerei abbattuti attesi `E_i(N)` (§11.1) | sì |
| D4b | Riferimento: A-10 (`Aircraft_Attacker` med), 200 m/s, attraversamento lungo il diametro | sì; in seguito la classe dell'aereo che valuta, quando serve |
| D4c | Tabella calcolata dai registri + correzioni opzionali per modello, non tabella a mano | sì |
| D4d | Scala del rapporto per le forze aeree, `κ = 2` | sì |
| D4e | Forze terrestri/navali: conteggio, SAM puri a peso 0 | sì |

## 12. Implementazione (2026-09-29)

Tutte le decisioni D1-D9 e D4a-D4e implementate.

| file | cosa |
|---|---|
| `Context/Doctrine.py` | chiavi facoltative della soglia di rottura (`dispersion`, `morale_weight`, `force_ratio_exponent`, `force_ratio_bounds`, `air_force_ratio_scale`, `unanswered_fire_weight`, `defensive_posture_factor`, `shock_min_losses`, `median_bounds`), valori neutri `DISENGAGEMENT_NEUTRAL`, `disengagement_parameter`, validazione; la tabella di default dichiara tutti i parametri della proposta |
| `Context/Air_Defense_Efficacy.py` (nuovo) | `air_defense_profile`, `expected_kills`, `air_defense_efficacy` (E(N)), `surface_threat_weight`, `air_threat_weight`, correzioni per modello `EFFICACY_CORRECTIONS` (vuota) |
| `Logic/Engagement_Resolver.py` | tempra per forza dal flusso `breakpoint_rng`, `seen_by` (primo rilevamento per forza), `loss_shooters` (chi ha tolto ogni asset), `_breakpoint`/`_perceived_ratio`/`_unanswered_fraction`/`_stationary`; `_check_doctrine` con B(t) e minimo di perdite per lo shock; ingressi `breakpoint_rng`, `morale_for`, `enemy_estimate_for`; `ForceOutcome` con `temper`, `breakpoint`, `morale`, `force_ratio`, `unanswered_fraction` |
| `Logic/Session_Simulator.py` | `temper_event_id`, flusso della tempra `order.rng(event_id=temper_event_id(...))`, `run_session(morale_for=..., enemy_estimate_for=...)` |

Scelte d'implementazione non esplicite nella proposta (da rivedere se non convincono):

- **Compatibilità**: una tabella con le sole `erosion`/`shock` è la soglia fissa di prima (le chiavi
  facoltative assenti valgono neutre); `erosion = 1` resta "ad oltranza", senza modulazione.
- **Senza flusso dedicato** (chiamata diretta a `resolve_engagement` senza `breakpoint_rng`) la
  tempra non si estrae: soglia alla mediana, modulata dagli altri fattori.
- **B(t) si ricalcola a ogni risoluzione di salva** contro la forza (non solo quando ci sono perdite):
  una forza può rompere quando il quadro percepito peggiora, alla salva successiva.
- **Nemici percepiti**: i distrutti sono esclusi (la distruzione si vede), i danneggiati restano.
- **Forza aerea** = tutti gli asset impegnati sono aerei; altrimenti superficie. Una forza di sola
  difesa aerea (peso di superficie 0) ha rapporto non definito, quindi neutro.
- **Armi di uno stesso asset** (missili + cannoni del Tunguska) combinate come indipendenti, ciascuna
  con i propri canali: approssimazione per eccesso.
- **Fuoco senza risposta**: "non rilevato" dalla forza entro l'istante della perdita; la capacità di
  ingaggiare il tiratore non è considerata.

Esiti misurati (8 repliche S1, 6 repliche S5):

- **S1 senza CAS**: Blue-Armor rompe alla 1ª perdita in 3/8 repliche (prima 7/8), sempre sotto fuoco
  d'artiglieria non rilevato e con tempra bassa; nelle altre lo scontro prosegue.
- **S1 con CAS**: Red-Line si ritira in 8/8 repliche fra la 1ª e la 3ª perdita, sempre con fuoco senza
  risposta = 1 (gli A-10 non sono rilevati da Red).
- **S5 dottrina di default**: 4 formazioni di F-15E si fermano al primo strato, 2 proseguono fino al
  Buk (prima: tutte ferme alla prima perdita). Gli F-15E non rilevano quasi mai i SAM (i loro sensori
  non hanno il modo 'ground'), quindi il fuoco senza risposta pesa sempre: è un limite dei dati sensore,
  da tenere presente quando si modellerà l'avviso radar (RWR).

Test: `Test_Air_Defense_Efficacy` (nuovo, 15), `Test_Doctrine.TestBreakpointParameters` (6),
`Test_Engagement_Resolver.TestStochasticBreakpoint` (13) e `TestAirForceRatio` (1),
`Test_Session_Simulator` (flusso della tempra). Scenari aggiornati: S10 verifica il meccanismo con le
soglie fisse (`FIXED_THRESHOLDS`) più un caso DISPERSIONE con la dottrina di default; S5 verifica la
distribuzione degli esiti invece di "sempre fermi al primo strato"; docstring di S1 aggiornato.
