# Proposta: overkill, salve su bersagli già condannati

> **Stato**: approvata e implementata il 2026-09-29 (decisioni al §7, implementazione al §8). Punto
> §5.2 di `Proposta_Regole_Allocazione_SAM.md` ("overkill dello stesso tiratore").

## 1. Il problema, misurato

Un tiratore continua a lanciare sullo stesso bersaglio a ogni `refire_interval` anche se ha già
salve in volo verso di esso, perché la ripartizione del fuoco (`_engaged_shooters`,
`Engagement_Resolver.py:1522`) esclude il tiratore che decide. Esempio del §5.2: un Tor mette 4
salve sullo stesso A-10 prima del primo impatto.

Misura del 2026-09-29: salve arrivate su un bersaglio **già distrutto**, divise per causa.

| scenario | salve | sprecate: il tiratore aveva già una sua salva in volo sul bersaglio | sprecate: un altro tiratore della stessa forza aveva una salva in volo | totale sprecate |
|---|---|---|---|---|
| S19 Tor avanzato (6 repliche) | 54 | 16 | 8 | 24 (44%) |
| S19 Strela sorvolo (6 repliche) | 72 | 8 | 24 | 32 (44%) |
| S19 Tor arretrato (6 repliche) | 48 | 0 | 11 | 11 (23%) |
| S1 con CAS (8 repliche) | 27 | 0 | 0 | 0 |

Due fatti:

1. Lo spreco fra **tiratori diversi** della stessa forza è grande quanto quello dello stesso
   tiratore (Strela sorvolo: 24 contro 8, sono i 4 A-10 sui 3 BMP). Una regola solo "per
   tiratore" risolve metà del problema.
2. La ripartizione attuale conta i **tiratori** impegnati, non quanto il bersaglio è già
   condannato: un bersaglio con una salva di 2 Maverick in volo (probabilità di distruzione
   ~0,94) vale "1 tiratore" come un bersaglio con un solo 9M37 in volo (~0,13).

## 2. Meccanismo attuale

`_schedule_next` sceglie, fra i bersagli ingaggiabili al primo istante utile, quello con meno
**altri** tiratori impegnati (lancio schedulato o salva in volo). Il tiratore che decide non conta
le proprie salve, e un bersaglio non è mai "abbastanza coperto": se è l'unico disponibile riceve
una salva a ogni ciclo di tiro finché la prima non arriva.

## 3. Opzioni

### A. Le proprie salve contano come copertura

Si toglie l'esclusione del tiratore che decide dal conteggio delle salve in volo. Il tiratore
preferisce un altro bersaglio, ma se ce n'è uno solo continua a sparargli. Risolve solo una parte
dello spreco dello stesso tiratore e niente di quello fra tiratori.

### B. Shoot-look-shoot per tiratore

Un tiratore non lancia su un bersaglio finché ha una sua salva in volo su di esso; se non ha altri
bersagli aspetta l'impatto e poi ridecide. Elimina lo spreco dello stesso tiratore, non quello fra
tiratori. Rigido: un SAM con probabilità bassa per missile non può più fare la dottrina reale
"due missili, poi guarda" (shoot-shoot-look).

### C. Soglia di distruzione attesa sul bersaglio (raccomandata)

Per ogni bersaglio si stima la probabilità che le salve già dirette contro di esso **dalla forza**
(in volo o schedulate) lo mettano fuori combattimento:

```
P_cov(T) = 1 − Π_s (1 − p_s)^(colpi_s)          p_s = accuracy × destroy_capacity della salva s
```

`p_s` è la probabilità di distruzione per colpo del modello di danno (`Damage_Model`,
esito KILL). Un bersaglio con `P_cov ≥ P_des` (dottrina, proposta 0,9) è **saturo**: nessun
tiratore della forza vi aggiunge salve.

- Un tiratore sceglie fra i bersagli non saturi, con le regole di oggi (primo istante utile,
  copertura, poi il resto).
- Se tutti i suoi bersagli sono saturi **aspetta**: ridecide al primo impatto previsto su uno di
  essi (evento `_DECIDE`, già usato dalla prelazione L3). Dopo l'impatto le salve risolte non
  contano più: se il bersaglio è sopravvissuto torna scoperto e si riprende a sparare.
- Esempi: una salva di 2 AGM-65D contro un BMP-2 (`p` = 0,75 per colpo) dà `P_cov` ≈ 0,94:
  una salva basta. Un 9M37 (`p` = 0,13) dà 0,13: lo Strela continua a lanciare
  (shoot-shoot-look) fino a saturare o a finire i missili. Un 9M38 (`p` = 0,5): due missili
  danno 0,75, tre 0,875, quattro 0,94.

Copre entrambe le cause dello spreco e produce da sé la dottrina "quante salve servono" in
funzione della letalità dell'arma. Non rende il tiro più lento quando serve davvero: le armi
poco letali continuano a sparare.

## 4. Dettagli da decidere con C

1. **Ambito**: forza intera (raccomandato, copre entrambe le cause) o solo il tiratore.
2. **`P_des`**: un valore unico per lato in `Context/Doctrine.py` (proposta 0,9), oppure per
   classe d'arma (per esempio più alto per i SAM, che difendono sé stessi).
3. **Lanciatori prioritari (regola L2)**: la dottrina dell'utente dà all'aereo che ha lanciato
   un'arma aria-superficie la priorità "per tempo e per numero di armi". Si può esentarlo dalla
   saturazione (tutti i tiratori a tiro gli sparano comunque) oppure applicargli una `P_des` più
   alta. Proposta: esenzione, per restare fedeli alla regola.
4. **Intercettazione**: le salve in volo possono essere intercettate, ma il tiratore non lo sa.
   Proposta: ignorarla nella stima (`P_cov` ottimistica), dichiarato; il bersaglio torna
   scoperto al primo impatto fallito.
5. **Colpi che danneggiano senza distruggere**: `p_s` conta solo l'esito KILL; un DAMAGE che
   porta la salute sotto 50 mette comunque fuori combattimento. Stima prudente (sottostima la
   copertura, quindi un po' di spreco resta), dichiarata.

## 5. Effetti attesi (da verificare, non misurati)

- S19: spreco molto ridotto in tutte le varianti; con il Tor avanzato il Tor spara meno missili
  per A-10 e ne conserva per gli altri bersagli.
- Scenari con un solo tiratore e un solo bersaglio: il tiratore aspetta l'impatto invece di
  sparare a raffica; la latenza di reazione (chi spara per primo) non cambia.
- Test esistenti sulla ripartizione del fuoco (`TestFireDistribution`) e sul consumo di scorte:
  alcuni conteggi di salve cambieranno.

## 6. Decisioni richieste

| # | domanda | proposta |
|---|---|---|
| O1 | Regola: A, B o C | C |
| O2 | Ambito della saturazione | forza intera |
| O3 | `P_des` e dove vive | 0,9, unica per lato in `Context/Doctrine.py` |
| O4 | Lanciatori prioritari (L2) | esenti dalla saturazione |
| O5 | Salve in volo possibili bersagli di intercettazione | ignorate nella stima |
| O6 | Tutti i bersagli saturi | il tiratore aspetta il primo impatto previsto e ridecide |

## 7. Decisioni dell'utente (2026-09-29)

O1 (regola C), O2 (forza intera), O4 (lanciatori esenti dalla saturazione), O5 (intercettazioni
ignorate), O6 (attesa del primo impatto): accettate come proposte. O3: `P_des` = 0,9 per lato in
`Context/Doctrine.py`, **più un tetto sulle salve: "due missili, poi guarda"**.

## 8. Implementazione

- `Context/Doctrine.py`: `DEFAULT_FIRE_DOCTRINE` per lato, `kill_probability_threshold` = 0,9 e
  `max_rounds_in_flight` = 2; `validate_fire_doctrine`, `get_fire_doctrine`. Un lato senza voce (o
  una chiave None) non ha la regola; `fire_doctrine={}` la disattiva per tutti.
- `Logic/Engagement_Resolver.py`: `_blocked` (tetto per tiratore e bersaglio, poi saturazione per
  la forza), `_coverage` (`P_cov` sulle salve in volo e sui lanci schedulati della forza),
  `_wait` (ridecisione al primo impatto previsto); ingresso `fire_doctrine`, passato anche da
  `Session_Simulator.run_session`.

Scelte d'implementazione:

- il **tetto** si conta in colpi (missili, o raffiche per i cannoni) in volo dallo stesso tiratore
  sullo stesso bersaglio; una salva non si spezza: con 0 colpi in volo parte intera anche se ne ha
  più del tetto (2 Maverick in una salva, poi si guarda);
- i **lanciatori prioritari** (L2) sono esenti dalla saturazione ma non dal tetto;
- l'**attesa** non accorcia mai il ciclo di tiro: la ridecisione avviene al più tardi fra il primo
  impatto previsto e il prossimo istante in cui il tiratore potrebbe sparare comunque.

Esiti misurati (salve sprecate su bersagli già distrutti):

| scenario | prima: salve / sprecate | dopo: salve / sprecate |
|---|---|---|
| S19 Tor avanzato | 54 / 24 | 32 / 0 |
| S19 Strela sorvolo | 72 / 32 | 25 / 0 |
| S19 Tor arretrato | 48 / 11 | 48 / 0 |
| S1 con CAS | 27 / 0 | 27 / 0 |

Effetti sui test:

- `TestDisengagementErosion`: le uccisioni passano da t = 2, 4, 6 a t = 2, 3, 4. Prima il lancio
  a t = 3 veniva deciso contro il bersaglio già condannato, poi annullato, e si perdeva un ciclo
  di tiro.
- S19, variante Strela in sorvolo: gli A-10C non sprecano più Maverick e con la stessa dotazione
  distruggono anche lo Strela da fuori portata, prima che spari. Perché il test verifichi ancora
  il caso d'origine (lo Strela conserva i missili per gli aerei), gli aerei attaccano solo i BMP,
  come nella variante con il Tor avanzato. Lo Strela ora ripartisce i missili su aerei diversi
  invece di tirarli tutti sullo stesso (6 A-10C abbattuti in 6 repliche, prima 7).
- Nuovi test: `Test_Engagement_Resolver.TestFireDoctrine` (7), `Test_Doctrine.TestFireDoctrine` (3).
