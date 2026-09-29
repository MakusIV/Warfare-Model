# Soglia di rottura stocastica, efficacia antiaerea e RWR

> **Stato**: approvata e implementata il 2026-09-29 (decisioni al §10). Risolve il difetto §5.3 di
> `Proposta_Regole_Allocazione_SAM.md`: disingaggio alla prima perdita per le forze piccole.
> Scelta di partenza dell'utente: opzione D (soglia casuale per forza), estesa con morale, stima
> della forza avversaria, efficacia della difesa aerea e RWR. I dati RWR del §5 seguono il registro,
> le decisioni dell'utente e la ricerca `Ricerca_RWR_2026_09_29.md`.

## 1. Il problema, misurato

Fino al 2026-09-29 (`Context/Doctrine.py`, `Engagement_Resolver._check_doctrine`) una forza
rompeva il contatto se l'**erosione** (perdite cumulate / organico impegnato) raggiungeva 0,30
oppure se lo **shock** (perdite di una sola salva / organico impegnato) raggiungeva 0,20. Erano
soglie fisse, uguali per tutti, deterministiche.

Con *n* mezzi la perdita minima è 1/*n*: per le forze piccole la soglia è un interruttore.

| mezzi | lo shock scatta alla… | l'erosione scatta alla… |
|---|---|---|
| 1-2 | 1ª perdita | 1ª perdita |
| 3 | 1ª perdita | 1ª perdita |
| 4-5 | 1ª perdita | 2ª perdita |
| 6 | 2ª perdita nella stessa salva | 2ª perdita |
| 10 | 2ª perdita nella stessa salva | 3ª perdita |

Misura su S1, 8 repliche:

- **senza CAS**: Blue-Armor (5 mezzi) si disingaggiava per shock alla **prima perdita** in 7
  repliche su 8, quindi lo scontro corazzato si decideva con un carro;
- **con CAS**: Red-Line (6 mezzi) si ritirava per erosione alla 2ª perdita (2/6 = 0,33) in 6
  repliche su 8 e per erosione + shock nelle altre 2; Blue non subiva danni.

Il difetto non è solo la granularità. La stessa soglia valeva per una compagnia fresca e per una
logorata, per chi vede un nemico inferiore e per chi è colpito da un nemico che non vede e non
può colpire. La letteratura sulle soglie di rottura (Helmbold, v. wiki [[lanchester-models]]) le
tratta come una **distribuzione**, non come un valore: forze analoghe cedono a livelli di perdita
molto diversi.

## 2. Cosa esisteva nel codice

### 2.1 Morale: esiste, ma non è utilizzabile

`Block.morale` (`Block/Block.py:435`) vale `evaluateMorale(mean_success_ratio, efficiency)`
(`Utility/Utility.py:854`, logica fuzzy con scikit-fuzzy). Problemi verificati:

1. **Nessuno alimenta il dato**: `State.total_success_ratio` somma `success_count / total_count`
   per task, ma nessun modulo registra gli esiti delle missioni (lo dichiara il TODO in
   `Context/Region.py:761`). Oggi vale sempre 0.
2. **"Sconosciuto" diventa "morale nullo"**: con success_ratio 0 la proprietà restituisce `0.0`,
   che un consumatore leggerebbe come forza demoralizzata al massimo.
3. **Funzioni di appartenenza fuori scala**: `kd` ha universo [0, 1], ma `M` e `H` sono definite
   su [0,75; 2] e [1,25; 10]: un success_ratio in [0, 1] non raggiunge mai `H`.
4. **Costo**: il sistema fuzzy viene ricostruito a ogni chiamata. Va bene per una valutazione di
   campagna, non per un ingresso ripetuto del risolutore.

Per questo il risolutore riceve il morale **come ingresso** (un numero in [0, 1], oppure None =
sconosciuto, quindi neutro) e non legge `Block.morale`. Correggerlo e alimentarlo con gli esiti
degli ingaggi è lavoro di campagna (§9).

### 2.2 Stima della forza avversaria: due fonti

1. **Dentro l'ingaggio**: il risolutore registra i `Detection` (osservatore, bersaglio, istante),
   quindi in ogni istante *t* si sa quali asset nemici una forza ha visto. È la percezione "dal
   campo", coerente con la nebbia di guerra (C).
2. **Prima dell'ingaggio**: `Context/Combat_Power_Estimation.py` stima la combat power di un blocco
   osservato dalla ricognizione. È la stima "d'intelligence" che un C2 ha prima del contatto.

Vincolo: la combat power è per dimensione (terra/aria/mare) e SAM/AAA/EWR valgono 0 per
definizione (`Military.air_defense_power()` è una grandezza separata). Un rapporto di forze in
combat power fra una colonna corazzata e due A-10 non è definito: da qui il §4.

### 2.3 Casualità

`SessionOrder.rng(mission_id, event_id, counter)` genera flussi derivati. La tempra viene da un
flusso **separato**, con `event_id = temper_event_id(*forze)` (stesse forze dell'ingaggio, tag
diverso): le estrazioni di rilevamento e di danno non si spostano, e gli esiti cambiano solo dove
cambia davvero il disingaggio.

## 3. Modello della soglia di rottura

### 3.1 Tempra estratta una volta, soglia ricalcolata a ogni salva

All'inizio dell'ingaggio ogni forza che può disingaggiarsi estrae **una volta** un quantile
`u ∈ (0, 1)`: la sua "tempra" in questo scontro. A ogni salva risolta contro la forza la soglia
di rottura vale

```
B(t)     = logistic( logit(μ_eff(t)) + σ · Φ⁻¹(u) )
μ_eff(t) = clamp( μ · M(morale) · R(t) · U(t) · P,  μ_min, μ_max )
```

e la forza si disingaggia se `erosione(t) ≥ B(t)`.

- `μ` è la mediana dottrinale (0,30) e `σ` la dispersione in scala logit. La distribuzione
  logit-normale sta in (0, 1), si calcola con la sola libreria standard (`statistics.NormalDist`)
  e ha mediana esattamente `μ`.
- `u` è fisso, `μ_eff` varia: la tempra dell'unità non cambia durante lo scontro, cambia la
  situazione percepita. Se il rapporto di forze percepito peggiora, la soglia scende e la forza
  può rompere alla stessa perdita a cui prima reggeva, alla salva successiva.
- Limiti `μ_min`, `μ_max` = 0,05 e 0,95 (`median_bounds`).

**Perché un'estrazione sola e non un "test di morale" a ogni perdita** (stile wargame): con un test
per evento la probabilità di rottura dipenderebbe da quanti eventi-perdita ci sono, quindi da
`salvo_window` e dalla granularità delle salve: un parametro numerico deciderebbe il morale. Con
un'estrazione sola la rottura dipende solo da quante perdite e in che situazione.

Effetto con `μ = 0,30` e fattori neutri (probabilità di aver rotto entro la *k*-esima perdita):

| mezzi | σ = 0,5: 1ª / 2ª / 3ª | σ = 0,7: 1ª / 2ª / 3ª |
|---|---|---|
| 2 | 0,95 / 1 / 1 | 0,89 / 1 / 1 |
| 3 | 0,62 / 1 / 1 | 0,59 / 0,99 / 1 |
| 4 | 0,31 / 0,95 / 1 | 0,36 / 0,89 / 1 |
| 5 | 0,14 / 0,81 / 0,99 | 0,22 / 0,74 / 0,96 |
| 6 | 0,06 / 0,62 / 0,95 | 0,14 / 0,59 / 0,89 |
| 10 | 0,00 / 0,14 / 0,50 | 0,03 / 0,22 / 0,50 |

Con σ = 0,5 la deviazione standard è circa 0,10 e il 90% delle soglie cade fra 0,16 e 0,49; con
σ = 0,7 è circa 0,14, fra 0,12 e 0,58. Le forze di 1-3 mezzi restano fragili, ed è voluto: una
coppia di aerei che perde il gregario rientra, una sezione di 3 carri che ne perde uno ha perso
un terzo della potenza.

### 3.2 Morale `M`

```
M(m) = 1 + α · (2m − 1)          m ∈ [0, 1];  m = None → neutro (M = 1)
```

Con `α = 0,3` il morale massimo alza la mediana del 30% (0,30 → 0,39), il minimo la abbassa del
30% (→ 0,21). Il morale entra come ingresso del risolutore (`morale_for: force → Optional[float]`,
stesso schema di `reaction_profile_for`), di default None per tutte le forze: finché la campagna
non lo alimenta, il modello si comporta come se fosse neutro, **mai** come se fosse zero.

### 3.3 Rapporto di forze percepito `R(t)`

```
ρ(t) = forza propria operativa(t) / forza nemica percepita(t)
R(t) = clamp( ρ(t)^β, R_min, R_max )          β = 0,5;  R ∈ [0,6; 1,5]
forza nemica percepita(t) = max( stima a priori, nemici percepiti entro t )
```

- **Forza propria**: asset propri ancora operativi (la forza sa quanto ha perso).
- **Nemici percepiti**: quelli rilevati dai sensori della forza entro *t* e, per le forze aeree,
  quelli identificati dall'RWR (§5). I nemici distrutti sono esclusi (la distruzione si vede),
  quelli danneggiati restano.
- **Stima a priori**: ingresso opzionale `enemy_estimate_for`, dal C2 o da
  `Combat_Power_Estimation`, nella stessa misura del rapporto.
- **Misura**: dipende dal dominio della forza che valuta (§4.3).
- Se il rapporto non è definito (nessun nemico percepito né stimato, oppure forza propria di peso
  nullo) `R = 1`, neutro.
- Con `β = 0,5`: un rapporto 4:1 a favore dà ×1,5 (limite), 1:4 contro dà ×0,6 (limite).

### 3.4 Fuoco senza risposta `U(t)`

Una forza che subisce perdite da tiratori che **non ha percepito** cede prima di una che sa chi la
colpisce. È il caso di S1 con CAS: Red-Line perde mezzi per Maverick lanciati da A-10 fuori
portata di Shilka e Strela, e non rilevati.

```
U(t) = 1 − γ · (perdite causate da tiratori non percepiti / perdite totali)      γ = 0,3
```

Il dato c'è già: ogni perdita registra il tiratore (`loss_shooters`) e i rilevamenti dicono chi
ha visto chi. Per le forze aeree conta anche l'RWR (§5).

### 3.5 Postura `P`

Difesa su posizione (tutti i tratti di rotta della forza fermi) `P = 1,2`, altrimenti `P = 1`. È
il fattore "postura" dei modelli di Helmbold; 1,2 è una stima dichiarata, non un dato.

### 3.6 Shock

Lo shock resta come seconda condizione, con due cambiamenti:

1. **minimo assoluto**: scatta solo se la salva ha tolto almeno `shock_min_losses` mezzi
   (default 2). Un colpo improvviso che rompe una forza è, per definizione, più della perdita
   minima possibile;
2. **stessa tempra**: soglia `S(t) = (shock / erosion) · B(t)`, cioè 2/3 · B(t) con i valori di
   default. Il vincolo `shock ≤ erosione` resta garantito dalla validazione della dottrina.

Con `salvo_window = 0` lo shock diventa raro (servono due perdite simultanee). È coerente con il
suo significato, ma rende più urgente la taratura di `salvo_window`, punto aperto di modello.

## 4. Efficacia difensiva antiaerea (D4 rivista)

### 4.1 Grandezza: aerei abbattuti attesi durante l'attraversamento della zona

Per ogni asset di difesa aerea e per *N* aerei nemici nella sua zona d'intercettazione:

```
E(N) = N · ( 1 − Π_w (1 − p_w)^(K_w / N) )
```

- `p_w` — **potenza contro un singolo aereo** dell'arma *w*: probabilità che un ingaggio abbatta
  l'aereo, `accuracy × destroy_capacity` contro la classe di bersaglio di riferimento (righe
  "Aircraft*" dei registri d'arma, introdotte con B1). Per i cannoni un ingaggio è una raffica
  (`GUN_BURST_ROUNDS = 50`, come in `Fire_Control`).
- `K_w` — **ingaggi possibili** mentre un aereo attraversa la zona: il minimo fra il tempo di
  puntamento disponibile (canali × cicli, ripartito come al §4.2) e la scorta
  (`scorta_w // colpi per ingaggio`).
  - canali: `Mobile.engagement_channels('air')` (`multi_target_capacity`), default 1;
  - cicli: ingaggi successivi possibili nel tempo di esposizione `T = 2R / v_rif`
    (attraversamento lungo il diametro della zona a 200 m/s). Il primo dopo acquisizione +
    sequenza di lancio + tempo di volo a metà portata (`Air_Route_Manager.threat_reaction_times`),
    i successivi ogni sequenza di lancio + tempo di volo, o ogni durata di raffica per i cannoni;
  - scorta: quella passata dal chiamante, altrimenti la dotazione del registro. Nel rapporto di
    forze percepito si usa **sempre la dotazione stimata** (§4.3): chi osserva un sistema non sa
    quanti missili gli restano.
- Gli ingaggi sono distribuiti in modo uniforme sugli *N* aerei e ogni aereo si abbatte una volta
  sola. Per `N = 1` vale `1 − (1 − p)^K`, la letalità contro un aereo solo; per *N* grande tende a
  circa `Σ K_w · p_w`, quanti aerei il sistema può abbattere al massimo. Le due componenti chieste
  stanno in una sola funzione.

### 4.2 Sistema di puntamento condiviso

Le armi guidate dallo **stesso** sistema di puntamento non si sommano come indipendenti: si
ripartiscono il tempo dei suoi canali. Dentro un sistema si impiega prima l'arma più letale,
finché ha scorta; il tempo-canale che resta passa all'arma successiva. Sistemi diversi dello
stesso asset restano indipendenti fra loro.

| asset | sistema di puntamento | canali |
|---|---|---|
| veicolo con radar aria | radar di tiro: tutte le armi a comando radio, SARH, SACLOS e i cannoni (Tunguska: 9M311 e 2A38M sotto lo stesso radar) | `multi_target_capacity` |
| veicolo, arma a guida autonoma (IR) o cannone senza radar | l'arma stessa | 1 |
| nave, SAM | direttore di tiro della nave, condiviso da tutti i SAM | `multi_target_capacity` della nave |
| nave, CIWS | radar proprio del CIWS, uno per tipo | numero di impianti |

### 4.3 Uso nel rapporto di forze

La minaccia rilevante dipende dal **dominio della forza che valuta**.

- **Forza aerea** (tutti gli asset impegnati sono aerei), con *N* aerei operativi:

  ```
  minaccia(t) = Σ E_i(N)   sugli asset AD nemici percepiti entro t (scorta di dotazione stimata)
              + caccia nemici percepiti (peso 1 ciascuno)
  ρ(t) = N / (κ · minaccia(t))            κ = 2
  ```

  Le zone sovrapposte si sommano (stima prudente per chi attacca). Con `κ = 2` una difesa che si
  aspetta di abbattere metà della formazione la "bilancia" (`ρ = 1`, neutro); una che si aspetta
  di abbatterla tutta dà `ρ = 0,5`. Stima dichiarata. Esempi con 2 A-10: Strela-10 → `ρ = 1,5`;
  Kub → `ρ = 1,1`; Buk → `ρ = 0,67`; Buk + Kub + Shilka → `ρ = 0,34` (`R` al limite di 0,6).
- **Forza terrestre o navale**: conteggio degli asset che possono colpire bersagli di superficie,
  peso 1 ciascuno (mezzi da combattimento, aerei non da trasporto/ricognizione/AWACS, cannoni AAA
  con impiego terrestre come Shilka e Tunguska); **peso 0 per i SAM puri**, che non minacciano una
  forza terrestre. La stessa regola vale per la forza propria, così che il rapporto sia omogeneo.

L'efficacia antiaerea entra quindi solo dove conta: quando a valutare è chi deve volare dentro la
zona.

### 4.4 Tabella (dai registri; riferimento A-10 = `Aircraft_Attacker` med, 200 m/s)

Calcolata con `Context/Air_Defense_Efficacy.py`, scorta piena, un asset isolato.

| asset | armi (sistema di puntamento) | p | canali | E(1) | E(2) | E(4) | E(8) |
|---|---|---|---|---|---|---|---|
| 2K22 Tunguska | 9M311 + 2A38M (radar) | 0,33 / 0,03 | 2 | 0,99 | 1,77 | 2,66 | 3,36 |
| MIM-115 Roland | Roland (radar) | 0,33 | 2 | 0,98 | 1,73 | 2,53 | 3,15 |
| 9K331 Tor | 9M331 (radar) | 0,33 | 4 | 0,96 | 1,60 | 2,20 | 2,64 |
| 9K37 Buk | 9M38 (radar) | 0,50 | 1 | 0,93 | 1,49 | 1,98 | 2,31 |
| S-300PS | 5V55R (radar) | 0,50 | 6 | 0,93 | 1,49 | 1,98 | 2,31 |
| 9A33 Osa | 9M33 (radar) | 0,33 | 2 | 0,91 | 1,40 | 1,81 | 2,08 |
| **2K12 Kub** | 3M9 (radar) | 0,33 | 1 | 0,70 | 0,90 | 1,04 | 1,12 |
| 9K35 Strela-10 | 9M37 (IR, autonomo) | 0,13 | 1 | 0,55 | 0,66 | 0,73 | 0,77 |
| ZSU-23-4 Shilka | AZP-23 (radar) | 0,03 | 1 | 0,49 | 0,57 | 0,62 | 0,64 |
| Strela-1 9P31 | 9M31 (IR, autonomo) | 0,13 | 1 | 0,42 | 0,47 | 0,50 | 0,52 |
| MIM-72G Chaparral | MIM-72 (IR, autonomo) | 0,13 | 1 | 0,42 | 0,47 | 0,50 | 0,52 |
| M6 Linebacker | Stinger (IR, autonomo) | 0,13 | 1 | 0,42 | 0,47 | 0,50 | 0,52 |
| Flakpanzer Gepard | KDA 35 mm (radar) | 0,03 | 1 | 0,33 | 0,36 | 0,38 | 0,39 |
| ZSU-57-2 | S-68 57 mm (ottico) | 0,07 | 1 | 0,21 | 0,22 | 0,23 | 0,23 |
| M163 VADS | M61 20 mm (ottico) | 0,03 | 1 | 0,19 | 0,20 | 0,21 | 0,21 |
| FFG-46 | SM-1 (direttore) + Phalanx | 0,51 / 0,07 | 8 / 1 | 1,00 | 2,00 | 3,99 | 7,69 |
| Type 052B | HHQ-7 (direttore) + Type 730 | 0,35 / 0,07 | 10 / 2 | 1,00 | 1,93 | 3,27 | 4,59 |
| CV-59 Forrestal | Sea Sparrow (direttore) + Phalanx | 0,35 / 0,07 | 8 / 2 | 0,98 | 1,74 | 2,56 | 3,19 |

Kub contro Buk: contro un aereo solo 0,70 contro 0,93, contro quattro aerei 1,04 contro 1,98.
Gli incrociatori e i caccia con SAM a lungo raggio (CG-65, Arleigh Burke, Kuznetsov, Piotr
Velikiy) saturano: E(N) = N fino a 8 aerei.

Cosa la tabella rivela sui dati:

1. **`p` è per classe d'efficienza, non per sistema**: Kub, Osa, Tor, Roland e Tunguska sono tutti
   `_EFF_SAM_MERAD` (0,33); le differenze fra loro vengono solo da canali, scorta, portata e tempi.
   Per distinguere di più la via è `EFFICACY_CORRECTIONS` (correzione per modello), non numeri
   inventati per singolo sistema.
2. **La scorta per asset domina la saturazione**: il Tor ha 4 canali ma 8 missili, l'S-300PS 6
   canali ma 4 missili per lanciatore. Nel registro un S-300PS è un lanciatore, non una batteria:
   una batteria è fatta di più asset, e le loro E si sommano (§4.3).
3. **I canali dei radar di Buk e Kub valgono 1**: un bersaglio per TELAR/radar, corretto per 9S35
   e 1S91.
4. **Tunguska**: il valore non cambia rispetto alla somma indipendente, perché i missili (8) si
   esauriscono in poco più di un terzo del tempo-canale e le raffiche dei cannoni sono limitate
   dalla scorta, non dal tempo. La ripartizione pesa quando il tempo è il vincolo (test dedicato).
5. **Esposizione**: l'attraversamento lungo il diametro favorisce le zone grandi. Un aereo che
   attacca da fuori zona (stand-off) ha esposizione nulla, ma quella è già geometria del
   risolutore (L1, portate), non efficacia: la tabella misura la capacità potenziale.

## 5. RWR: fuoco senza risposta e percezione delle forze aeree

### 5.1 Regola

Un asset di difesa aerea che **emette** (ha un radar aria) e illumina un aereo è percepito dalla
forza di quell'aereo se l'RWR di quell'aereo **riconosce la sua categoria SAM**, cioè se la
categoria sta in una delle classi che l'RWR distingue (§5.3). Basta la classe: un RWR che dice
solo "SAM" (SPO-10) riconosce comunque la minaccia. La valutazione è fatta su ogni aereo
illuminato, con il suo RWR; la percezione vale per la sua forza (la formazione).

**Quando** la minaccia è percepita dipende dalle modalità radar che l'RWR rileva:

- l'RWR rileva la **ricerca** (SPO-15, sistemi digitali): dall'istante in cui il radar del sistema
  rileva l'aereo;
- l'RWR rileva solo **tracciamento o guida** (SPO-10): dal lancio contro l'aereo, che il
  tracciamento precede (approssimazione dichiarata).

Da quell'istante l'asset conta nella minaccia percepita (§4.3) e rende "con risposta" le perdite
che causa (§3.4).

Un sistema che non emette (cercatore IR, puntamento ottico: Strela-1, Strela-10, Chaparral,
Linebacker, ZSU-57-2, VADS) non accende nessun RWR e resta non percepito finché i sensori della
forza non lo vedono.

### 5.2 Categorie SAM

Fonte primaria: `classificazione_sam_1950_2000.md` (classificazione per sistema missilistico,
fornita dall'utente), in `Air_Defense_Efficacy.SAM_WEAPON_CATEGORY`. Un asset prende la categoria
più alta fra quelle dei suoi missili elencati. Per le armi che il documento non elenca vale il
ripiego: `roles` del veicolo, o portata del SAM a portata maggiore per le navi.

| categoria | sistemi dal documento | ripiego |
|---|---|---|
| VSHORAD | Stinger (M6 Linebacker) | veicoli `AAA` (Shilka, Gepard, ZSU-57-2, VADS); navi con solo CIWS |
| SHORAD | Strela-1, Strela-10, Osa, Tor, Chaparral, Roland; HHQ-7; SA-N-4 e SA-N-9 (varianti navali di Osa e Tor) | veicoli `SHORAD` (Tunguska: `AAA` + `SHORAD`, vince la più alta); navi < 30 km |
| MRSAM | Kub, Buk | veicoli `MERAD`; navi 30-100 km (ESSM, SM-1, HHQ-16) |
| LRSAM | S-300PS; HHQ-9; S-300F (variante navale) | veicoli `LORAD`; navi ≥ 100 km (SM-2ER) |

Le varianti navali sono ricondotte al sistema terrestre da cui derivano: è una derivazione, non
un dato del documento. Le soglie di portata delle navi sono una stima dichiarata. Rispetto alla
classificazione per ruolo cambia solo l'M6 Linebacker (SHORAD → VSHORAD), senza effetti sull'RWR:
lo Stinger non emette.

### 5.3 Dati RWR

`Asset/Aircraft_Rwr_Data.py`, una voce per ciascuno dei 65 aerei del registro. Fonti: il campo
`avionics` del registro (dove nomina l'RWR), le decisioni dell'utente del 2026-09-29 e la ricerca
`Ricerca_RWR_2026_09_29.md` (con fonti web; dove diverge prevalgono le decisioni dell'utente).
Ogni voce dichiara:

- `classes`: le classi di minaccia SAM che il sistema distingue; una classe con più categorie
  significa che il sistema non le separa;
- `modes`: le modalità del radar nemico rilevate (ricerca, tracciamento, guida del missile);
- `sectors`: settori di direzione (4, 8, oppure direzione precisa);
- `ewr`: se riconosce i radar di scoperta come classe a parte;
- `confidence`: alta, media o bassa.

| famiglia | classi SAM | modalità | direzione | aerei |
|---|---|---|---|---|
| sistemi digitali (ALR-46/56/67/69, ALQ-161, SERVAL/SPIRALE, L-150 Pastel/SPO-32, BKO-1 Baykal, ESM) | VSHORAD, SHORAD, MRSAM, LRSAM separate | ricerca, tracciamento, guida | precisa | A-10A/C, F-4E, F-5E, F-14B, F-15C/E, F-16 (tutti), F/A-18 (tutti), Mirage 2000C, B-1B, B-52H, Su-25T/TM, Su-30, Su-34, Tu-95MS, Tu-160, E-2D, E-3A, A-50, S-3B, C-130, KC-130, C-17A |
| SPO-15 Beryoza (L, LE, LM) | VSHORAD-SHORAD, MRSAM, LRSAM | ricerca, tracciamento, guida | 8 settori | MiG-23MLD, MiG-25PD/RB, MiG-27K, MiG-29A/S, MiG-31, Su-17M4, Su-24M/MR, Su-25, Su-27, Su-33, Tu-22M, Tu-142, Il-78M |
| AN/ALR-45 | VSHORAD; SAM generico | ricerca, tracciamento, guida | precisa | F-14A, A-4E |
| SPO-10 Sirena-3 | SAM generico (più EWR) | solo tracciamento | 4 quadranti | MiG-21bis, Il-76MD |
| solo allarme (Sirena-2, radarvarnare) | nessuna | — | — | MiG-19P, AJS-37 Viggen |
| nessun RWR | nessuna | — | — | F-117, F-86E, MiG-15bis, A-20G, Yak-40, An-26B, An-30M, KC-135 (2), MQ-1, MQ-9 |

Note:

- l'SPO-15 rileva il radar dello Shilka: verificato dall'utente in DCS con il Su-25 (la ricerca
  proponeva il contrario, sulla base di una banda di frequenza da fonte debole);
- Tu-95MS: la ricerca indica l'L-150 Pastel, adottato; il campo `avionics` del registro dice ancora
  SPO-15;
- Tu-160: il "Baikal-3 EW" del registro è considerato equivalente alla suite BKO-1 Baykal;
- A-4E: il registro indica AN/ALR-45, adottato (la ricerca parlava dell'APR-25 del modulo DCS);
- la **direzione** (settori) e la **granularità delle classi** sono registrate ma non ancora usate
  dal modello: la percezione è sì/no e la minaccia usa la E(N) del sistema specifico (§8).

## 6. Dove vive

| elemento | dove |
|---|---|
| `μ` (`erosion`), `shock`, `σ` (`dispersion`), `α` (`morale_weight`), `β` (`force_ratio_exponent`), limiti di `R` (`force_ratio_bounds`), `κ` (`air_force_ratio_scale`), `γ` (`unanswered_fire_weight`), `P` (`defensive_posture_factor`), `shock_min_losses`, `μ_min/μ_max` (`median_bounds`) | `Context/Doctrine.py`, per lato; stessi valori per i tre lati salvo asimmetria dichiarata |
| morale di ogni forza | ingresso `morale_for` di `resolve_engagement` e `run_session` (default None → neutro) |
| stima a priori della forza nemica | ingresso `enemy_estimate_for` (default None) |
| tempra `u` | flusso `breakpoint_rng`; in sessione `SessionOrder.rng(event_id=temper_event_id(...))` |
| valutazione | `Engagement_Resolver._check_doctrine` / `_breakpoint`, a ogni salva risolta contro la forza |
| efficacia antiaerea, pesi di minaccia, categorie SAM, RWR | `Context/Air_Defense_Efficacy.py` |
| dati RWR | `Asset/Aircraft_Rwr_Data.py` |
| spiegazione | `ForceOutcome`: `temper`, `breakpoint`, `morale`, `force_ratio`, `unanswered_fraction` |

**Compatibilità**: le chiavi oltre `erosion` e `shock` sono facoltative. Una tabella che dichiara
solo quelle due riproduce esattamente le soglie fisse precedenti (modalità deterministica, usata
dai test e dagli scenari "ad oltranza"); `erosion = 1` resta "combatte fino all'annientamento",
senza modulazione. La tabella di default dichiara tutti i parametri.

## 7. Esiti misurati (2026-09-29)

| scenario | prima | dopo |
|---|---|---|
| S1 senza CAS (Blue-Armor, 5 carri) | rottura alla 1ª perdita in 7 repliche su 8 | 3 su 8, sempre sotto artiglieria non rilevata e con tempra bassa |
| S1 con CAS (Red-Line) | ritirata in 8 su 8 | ritirata in 8 su 8, fra la 1ª e la 3ª perdita, sempre sotto fuoco senza risposta (gli A-10 non sono rilevati) |
| S5 (4 F-15E, dottrina di default) | sempre fermi al 1° strato | 4 fermi al 1° strato, 2 arrivano al Buk |

Con l'RWR gli F-15E (ALR-56C) identificano S-300 e Buk: in S5 il fuoco senza risposta passa da 1
a 0 in tutte le repliche. Con la minaccia calcolata sulla scorta di dotazione stimata il rapporto
percepito è sempre definito (fra 0,34 e 0,84) e la ripartizione degli esiti resta 4 contro 2.

## 8. Limiti e cosa non fa

- **Coefficienti**: nessuno da fonti non validate. `μ = 0,30` è la stima di partenza dichiarata;
  `σ`, `α`, `β`, `κ`, `γ`, `P` sono stime dichiarate da ricalibrare con ATCAL.
- **Rottura parziale**: non modellata (una parte della forza cede, l'altra resiste). Il
  disingaggio resta per forza intera (decisione P1 del 2026-09-23).
- **Contagio e C2**: non modella il contagio fra forze dello stesso lato (una forza che vede
  ritirarsi quella accanto) né il legame C2; appartengono alla Fase 0 della gerarchia C2.
- **Scorta nella minaccia percepita**: si usa la dotazione di registro, una stima e non un dato
  certo. Un SAM che ha sparato tutto continua a pesare come se fosse carico, perché chi lo osserva
  non può saperlo (decisione dell'utente, 2026-09-29).
- **RWR e sistema specifico**: l'RWR riconosce una classe, ma la minaccia usa la E(N) del sistema
  specifico. Gli RWR digitali hanno librerie per sistema; SPO-15 e SPO-10 no. Direzione (settori)
  e granularità delle classi sono nei dati ma non ancora nel modello.
- **Fuoco senza risposta**: conta solo la percezione del tiratore, non la capacità di ingaggiarlo.
- **Sensori degli aerei**: nessun modo 'ground' nei registri, quindi senza RWR un aereo non
  percepisce mai i SAM.

## 9. Morale nella campagna (fuori scope, da decidere dopo)

Il morale ha senso solo se ha una memoria. Gli esiti degli ingaggi (HELD / DISENGAGED / DESTROYED,
perdite inflitte e subite) devono alimentare `State.success_ratio`, e `Block.morale` va corretto
(§2.1: funzioni di appartenenza, None invece di 0, costo). È il pezzo che collega questa proposta
al C2 regionale ("orientamento guidato da morale", [[c2-hierarchy-design]]).

## 10. Decisioni dell'utente (2026-09-29)

| # | decisione | esito |
|---|---|---|
| D1 | Tempra estratta una volta per forza e per ingaggio | approvata |
| D2 | Logit-normale, mediana 0,30, σ = 0,5 | approvata |
| D3 | Morale come ingresso, None = neutro, α = 0,3 | approvata |
| D4 | Rapporto di forze a conteggio puro | **respinta**: un Kub non vale un Buk, e la potenza di SAM e AAA non è definita nella combat power |
| D4a | Efficacia antiaerea come aerei abbattuti attesi E(N) (§4.1) | approvata |
| D4b | Riferimento A-10 (`Aircraft_Attacker` med), 200 m/s, attraversamento lungo il diametro | approvata |
| D4c | Tabella calcolata dai registri + correzioni opzionali per modello | approvata |
| D4d | Scala del rapporto per le forze aeree κ = 2 | approvata |
| D4e | Forze terrestri/navali: conteggio con SAM puri a peso 0 | approvata |
| D5 | Fuoco senza risposta, γ = 0,3 | approvata |
| D6 | Postura, P = 1,2 | approvata |
| D7 | Shock con minimo 2 perdite e soglia 2/3 · B(t) | approvata |
| D8 | Flusso casuale separato per la tempra | approvata |
| D9 | Correggere `Block.morale` più avanti (§9) | approvata |
| — | Armi dello stesso sistema di puntamento non indipendenti (§4.2) | richiesta dell'utente, implementata |
| — | Fuoco senza risposta valutato con l'RWR di ogni aereo, per categoria SAM (§5) | richiesta dell'utente, implementata |
| — | Minaccia percepita sulla scorta di dotazione stimata, non su quella residua (§4.3) | richiesta dell'utente, implementata |
| — | Classificazione SAM per sistema missilistico da `classificazione_sam_1950_2000.md` (§5.2) | richiesta dell'utente, implementata |
| — | Dati RWR: SPO-15 rileva lo Shilka; SPO-10 e SPO-15 come al §5.3; RWR di Il-76MD, MiG-25RB, Il-78M, Tu-142, Tu-160, F-117, KC-130, Mirage 2000C; proposte della ricerca su F-14A, C-17A, Tu-95MS, Viggen | decisioni dell'utente, implementate |

## 11. Implementazione e test

| file | cosa |
|---|---|
| `Context/Doctrine.py` | chiavi facoltative della soglia di rottura, valori neutri `DISENGAGEMENT_NEUTRAL`, `disengagement_parameter`, validazione |
| `Context/Air_Defense_Efficacy.py` (nuovo) | `air_defense_profile`, `expected_kills`, `air_defense_efficacy`, sistema di puntamento (`_director`), `surface_threat_weight`, `air_threat_weight`, `SAM_WEAPON_CATEGORY`, `sam_category`, `emits_radar`, `rwr_identifies`, `rwr_perception`, `EFFICACY_CORRECTIONS` |
| `Asset/Aircraft_Rwr_Data.py` (nuovo) | `AIRCRAFT_RWR` (classi, modalità, settori, EWR, fiducia), `rwr_entry`, `rwr_categories`, `rwr_modes`, `rwr_classes` |
| `Logic/Engagement_Resolver.py` | tempra, `seen_by` (percezione: sensori e RWR), `loss_shooters`, `_breakpoint`, `_perceived_ratio`, `_unanswered_fraction`, `_stationary`; `_check_doctrine` con B(t) e minimo di perdite per lo shock; ingressi `breakpoint_rng`, `morale_for`, `enemy_estimate_for`; nuovi campi di `ForceOutcome` |
| `Logic/Session_Simulator.py` | `temper_event_id`, flusso della tempra, `run_session(morale_for=..., enemy_estimate_for=...)` |

Test: `Test_Air_Defense_Efficacy` (nuovo: efficacia, sistema di puntamento, categorie SAM, RWR,
completezza della tabella RWR), `Test_Doctrine.TestBreakpointParameters`,
`Test_Engagement_Resolver` (`TestStochasticBreakpoint`, `TestAirForceRatio`, `TestRwrPerception`),
`Test_Session_Simulator` (flusso della tempra). Scenari: S10 verifica il meccanismo con le soglie
fisse (`FIXED_THRESHOLDS`) più un caso DISPERSIONE con la dottrina di default; S5 verifica la
distribuzione degli esiti; il docstring di S1 descrive la ritirata di Red con il nuovo modello.
