# Proposta G4 — ri-pianificazione dopo l'ingaggio (nuovo modello di bingo)

Data: 2026-10-17 (ProArt P16). Stato: **APPROVATA dall'utente 2026-10-17** (decisioni in §4). Base: HEAD `ed97eccb` (G3 approvato, fotografia 802).

## 1. Il problema

Due limiti dichiarati dal G3, che l'utente ha deciso di risolvere entrambi nel G4 (2026-10-17):

1. **Nessuna ri-pianificazione dopo l'ingaggio.** In `run_session` tutto cio' che riguarda il movimento e' calcolato
   A MONTE, prima dello scheduler, alla crociera: tratti, bingo (valutato una sola volta, all'inizio dei tratti, G2),
   esaurimento (F6-A), programma a terra. Il consumo d'ingaggio del G3 arriva DOPO, nella sola contabilita': un aereo
   che dopo un ingaggio e' sotto la soglia di bingo prosegue la rotta, e uno che finisce il carburante in ingaggio ha
   il contatore a zero ma vola e combatte (S26 `transfer_continue`: rotta completata a carburante 0,0).
2. **Un solo consumo d'ingaggio per sessione.** Ogni forza sta in UNA componente connessa per sessione, risolta con
   UNA chiamata a `resolve_engagement` che copre tutta la sessione ("deliberatamente conservativa rispetto al tempo",
   docstring di `Session_Simulator`). X contro A al mattino e contro B la sera e' un solo ingaggio: un solo consumo.

I due problemi hanno la stessa radice: **l'ingaggio non e' un evento nel tempo ma un blocco unico per la sessione.**
Non si puo' ri-pianificare "dopo l'ingaggio" se l'ingaggio dura quanto la sessione.

## 2. Fatti verificati nel codice (2026-10-17)

- `Engagement_Resolver` non legge il carburante (nessuna occorrenza di `fuel`): la contabilita' del carburante si puo'
  spostare in fondo alla sessione senza cambiare nulla degli ingaggi.
- `Fuel_Model.bingo_decision(asset, legs, bases, rule, transfer, time=, fuel=)` e' gia' generale: istante e residuo
  qualunque (scritta cosi' dal G2 per il G4).
- Con consumo deterministico alla crociera residuo e resto della rotta calano insieme (G2): la soglia puo' essere
  attraversata SOLO quando il residuo scende a scatti, cioe' ai consumi d'ingaggio. Valutare il bingo dopo ogni
  ingaggio e' quindi **esatto**, non un'approssimazione per campionamento.
- `Fuel_Model.fuel_exhaustion` legge `asset.fuel` corrente: serve un parametro `fuel` (residuo) per ricalcolare
  l'esaurimento da un istante qualunque senza mutare l'asset.
- `ActivityCriteria.damage_threshold` e' relativo alla salute "all'ingresso nella run, che in sessione e' quella
  d'inizio sessione: un asset sta in una sola run": con piu' episodi va passata la salute d'inizio sessione.
- Il risolutore disingaggia per forza (`broken_forces`) DENTRO la run; fra run diverse non c'e' memoria.
- `SessionOrder.rng(..., counter=0)`: il contatore e' "libero per un futuro re-ingaggio" (docstring), pensato per questo.

**Misura d'impatto (sonda sugli scenari della fotografia, 778 componenti risolte):** componenti le cui finestre
formano piu' gruppi separati nel tempo (finestre unite se condividono una forza e si sovrappongono):

| intervallo di fusione | componenti con >1 episodio | massimo episodi | dove |
|---|---|---|---|
| 0 s   | 58 | 3 | S5 (36), M-raid (8), Blue-Strike+Sweep (8), Blue-AirWing+CSG (4), M-stable (2) |
| 300 s | 40 | 2 | S5 (36: strati L1 e L2 a [556-1648] e [2206-3490] s), Blue-AirWing+CSG (4) |

Le altre ~740 componenti sono gia' un episodio solo.

## 3. Proposta: due passi, ciascuno con il proprio interruttore e il proprio confronto

### G4a — Episodi d'ingaggio (interruttore `G4_EPISODES`)

**Episodio** = gruppo di finestre di contatto legate, direttamente o per tramite di altre, perche' **condividono una
forza** (missione) **e si sovrappongono nel tempo entro `EPISODE_GAP`**; le forze dello stesso dominio di
coordinamento restano unite (come oggi), ma solo se le loro finestre si sovrappongono entro lo stesso intervallo.
La componente connessa di oggi e' l'unione dei suoi episodi.

- **Coda eventi**: un ENGAGEMENT per episodio, all'istante della sua prima finestra, in ordine di tempo; ogni
  episodio e' risolto con UNA `resolve_engagement` sulle sole sue finestre e il suo esito e' applicato subito (danno,
  munizioni), quindi l'episodio successivo della stessa forza parte dallo stato gia' consumato: e' la concatenazione
  che `assemble_session_outcome` gia' prevede ("health_before/after concatenabili se il primo esito e' applicato prima
  di risolvere il secondo").
- **Forza occupata**: una forza e' impegnata dal primo istante del suo episodio fino al `t_end` del suo esito
  (salve in volo comprese); le sue finestre successive sono ritagliate per partire non prima. Impedisce che due
  episodi leggano lo stesso asset sullo stesso intervallo (il difetto che le componenti connesse avevano risolto).
- **RNG**: `event_id` = quello di oggi (insieme delle forze), `counter` = ordinale degli episodi con lo STESSO
  insieme di forze (0 per il primo). Stessa regola per lo stream della tempra. **Una componente di un solo episodio
  ha esattamente lo stream di oggi**: le ~740 componenti non coinvolte restano identiche bit per bit.
- **Consumo d'ingaggio**: uno per episodio a cui l'aereo partecipa (il codice G3 conta gia' "un consumo per esito
  d'ingaggio"): risolve il limite 2.
- **Contabilita' del carburante**: spostata in un passo finale dopo tutti gli episodi (stessi `FuelEvent` per tratto e
  d'ingaggio, nello stesso ordine di tempo); a G4a da sola l'esito del carburante e' quello di oggi salvo i consumi in
  piu' degli episodi multipli. Serve a G4b, dove i tratti definitivi si conoscono solo alla fine.
- **Soglia di danno**: la sessione passa al risolutore la salute d'inizio sessione come riferimento.
- **Spento**: la componente connessa di oggi, esattamente come prima.

Effetto atteso sul confronto: cambiano SOLO le esecuzioni con componenti a piu' episodi (S5, Blue-AirWing+CSG con
300 s; anche M-raid, Blue-Strike+Sweep, M-stable con 0 s): stream RNG diversi per il secondo episodio, un consumo
d'ingaggio in piu', storia del secondo episodio diversa.

### G4b — Ri-pianificazione dopo l'episodio (interruttore `G4_REPLAN`)

Alla fine di ogni episodio (istante `t_r` = `t_end` dell'esito), per ogni aereo di MISSIONE in volo, non distrutto, che
vi ha consumato:

1. **Residuo a `t_r`** calcolato analiticamente: carburante d'inizio sessione − fabbisogno dei tratti che consumano fino
   a `t_r` (alla crociera, `leg_fuel_demand` ritagliato) − consumi d'ingaggio fino a `t_r`. Nuova funzione in
   `Fuel_Model` (es. `fuel_at`), stessa aritmetica della contabilita' (verificabile con un test di coerenza).
2. **Esaurimento in ingaggio** (residuo 0): le regole della F6-A dal punto in cui l'aereo si trova a `t_r` (planata
   sulla base raggiungibile, altrimenti perso con l'equipaggio recuperato). Sostituisce la soluzione minima del G3.
3. **Bingo**: `bingo_decision(..., time=t_r, fuel=residuo)` sui tratti della missione intera. Se l'aereo rientra:
   `BingoEnd` da `t_r` con la meccanica del G2 (`_return_end`, `_legs_after_bingo`: rotta di rientro, nessuna salva
   offensiva da `t_r`, a terra `parking_cold` sulla base raggiunta, esito BINGO, ABORTED(BINGO)). Qui le basi
   alternative entro 3 km dalla rotta contano davvero (al G2, all'inizio dei tratti, non potevano vincere).
4. **Esaurimento sui nuovi tratti**: `fuel_exhaustion` da `t_r` con il residuo (nuovo parametro `fuel`).
5. **Ri-scheduling**: tratti di presenza, tratti di movimento e programma a terra dell'aereo sostituiti da `t_r` in
   poi; `schedule_contacts` rieseguito con i tratti aggiornati; delle nuove finestre si tengono quelle degli aerei
   ri-pianificati che finiscono dopo `t_r` (ritagliate a `t_r` e alle forze occupate); le finestre non ancora risolte
   di quegli aerei sono scartate; gli episodi NON ancora risolti sono ricostruiti (stessa regola, stesso ordine
   deterministico). Gli episodi gia' risolti non cambiano: la storia prima di `t_r` e' fissata (causalita').

Il ciclo termina: ogni ri-pianificazione avviene a un istante non anteriore all'episodio estratto e gli episodi sono
estratti in ordine di tempo. Terra e mare: nessun consumo d'ingaggio, quindi nessuna ri-pianificazione (invariati).
**Spento**: G4a da sola.

Effetto atteso sul confronto: gli scenari aerei con poco carburante dopo l'ingaggio (S26 in primo luogo:
`transfer_continue` non finisce piu' a 0,0 con la rotta completata) e, piu' in generale, ogni aereo che dopo un
consumo d'ingaggio e' sotto il resto della rotta + riserva.

### Limiti dichiarati (proposti)

- La decisione e' presa alla FINE dell'episodio, non a meta': l'episodio e' risolto in blocco con i tratti di prima.
  La riserva di disimpegno (5 minuti) e' proprio il carburante di quella coda.
- Forza occupata: un aereo ri-pianificato che incontrerebbe una forza impegnata in un episodio gia' risolto e ancora
  in corso la incontra solo dopo la fine di quell'episodio.
- Solo il carburante ri-pianifica: un aereo danneggiato oltre la soglia continua passivo sulla rotta (F6-B1, invariato).

## 4. Decisioni (DECISE dall'utente il 2026-10-17: tutte le raccomandazioni)

Esito: `EPISODE_GAP` = 300 s; forza disingaggiata PASSIVA negli episodi successivi; tempra NUOVA per episodio;
due passi G4a e G4b con interruttori, confronti e approvazioni separati.


1. **Intervallo di fusione degli episodi `EPISODE_GAP`.** Raccomandato **300 s** (= `DISENGAGE_TIME`: ritrovare il
   contatto entro i 5 minuti del disimpegno e' lo stesso combattimento). Alternativa: 0 s, sovrapposizione stretta
   (piu' episodi: M-raid, Blue-Strike+Sweep, M-stable si spezzano).
2. **Forza disingaggiata (DISENGAGED) negli episodi successivi della stessa sessione.** Raccomandato: **passiva**
   (nessuna salva offensiva per il resto della sessione, resta bersaglio e intercettore, come dopo il bingo; il DES non
   la ri-instrada). Alternativa: combatte di nuovo nell'episodio successivo (nessuna memoria del disingaggio).
3. **Tempra (soglia di rottura) per episodio.** Raccomandato: **nuova estrazione per episodio** (`counter` = ordinale,
   coerente con "ingaggio diverso"). Alternativa: una sola tempra per forza nella sessione.
4. **Due passi G4a/G4b** con interruttori, confronti e approvazioni separati (raccomandato), oppure un passo unico.

Agente proposto per l'implementazione: `des-developer` Opus, sforzo **high** (cambia la coda eventi della sessione),
un passo alla volta, verifica (suite + `--compare`) fatta da me prima del commit.
