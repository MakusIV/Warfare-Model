# Proposta: intercettazione con rilevamento del colpo e tempo di reazione

Difetto §5.4 di `Proposta_Regole_Allocazione_SAM.md` ("intercettazione senza rilevamento"), stato
al commit `d6b4b4b6`.

## 1. Il difetto (dal codice)

`Engagement_Resolver._on_resolve` ferma un colpo intercettabile se l'intercettore:

- è operativo, ha canali e scorta liberi nell'evento;
- soddisfa la regola L1 (`_may_intercept`): il punto di lancio è fuori dal suo V_I.

Non si chiede **né** che l'intercettore abbia rilevato il colpo o il lanciatore, **né** che abbia
avuto il tempo di reagire. Un Tor che non ha ancora finito il proprio ciclo RIV+VAL+COM+ATT sul
lanciatore (5-8 s) ferma comunque un Maverick che arriva: nella misura su 16 seed di S19 un caso di
intercettazione *precede* il primo tiro del Tor. Con `time_of_flight = 0` si intercetta un colpo
che non ha mai volato.

## 2. Regola proposta (R-INT)

Un intercettore `I` può fermare i colpi della salva `S` (lanciata da `L` all'istante `t_L`, impatto
a `t_I`) solo se, **oltre a L1**:

    t_traccia(I, S) + τ(I, S) ≤ t_I

**t_traccia**: istante in cui `I` ha una traccia del colpo.

- **Lancio osservato**: se `I` ha già rilevato `L` a `t_L` (una `Detection` di `I` su `L` con
  `time ≤ t_L`), vede partire il colpo: `t_traccia = t_L`.
- **Altrimenti, geometria**: il colpo vola in linea retta a velocità costante dal punto di lancio
  (posizione di `L` a `t_L`) alla posizione del bersaglio a `t_I`. `t_traccia` è il primo istante
  in cui entra nel raggio di rilevamento aereo di `I` (`detection_range('air')`), con `I` fermo
  nella posizione di `t_L`. Se non ci entra mai, `I` non lo vede e non può fermarlo.

**τ**: tempo di reazione dell'intercettore, dal suo profilo `ReactionProfile`, senza costanti nuove.

- lancio osservato → `refire_interval` (VAL+COM+ATT): la traccia del lanciatore c'è già, il colpo
  nasce da lì;
- colpo scoperto dalla geometria → `total` (RIV+VAL+COM+ATT): una traccia nuova.

Il rilevamento geometrico è **deterministico**, senza estrazione. Il flusso RNG resta identico:
le estrazioni di rilevamento e di danno di tutti gli scenari non cambiano, e ogni differenza di
esito si deve alla regola.

L'intercettore che non soddisfa R-INT è saltato come oggi quello escluso da L1: il colpo passa al
successivo nell'ordine F.

## 3. Dato mancante (stessa politica di L1, scorte, carburante)

| Manca | Comportamento |
|---|---|
| posizioni (lanciatore, bersaglio, intercettore) e nessun lancio osservato | nessun vincolo geometrico: `t_traccia = t_L` |
| `detection_range('air')` dell'intercettore | idem |
| profilo di reazione | c'è sempre (profilo di ripiego del modulo) |

Il vincolo di tempo `t_traccia + τ ≤ t_I` resta **sempre** attivo. Con `time_of_flight = 0` non si
intercetta nulla, ed è corretto. I test del risolutore che oggi intercettano con tempo di volo nullo
vanno aggiornati con un tempo di volo realistico (19 occorrenze in `Test_Engagement_Resolver.py`,
3 in `Scenario_Fixtures.py`).

## 4. Semplificazioni dichiarate

1. **Tempo di volo dell'intercettore trascurato**: il vincolo è sull'istante di lancio
   dell'intercettore, non sul punto d'incontro. Richiederebbe la `fire_control`
   dell'intercettore contro un colpo, che non esiste. È ottimistico per la difesa.
2. **RCS del colpo non modellata**: il colpo è visto alla portata aerea dell'intercettore come un
   aereo. Anche questo è ottimistico per la difesa, da ridurre quando ci sarà un dato.
3. **Traiettoria rettilinea a velocità costante**: nessun profilo di volo né pop-up; una bomba
   plana in linea retta.
4. **Rilevamento per asset, non per forza**: la traccia del lanciatore ottenuta da un altro asset
   della stessa forza non basta (nessun collegamento dati). La condivisione è materia della Fase 0
   della gerarchia C2, come per L3.

## 5. Decisioni richieste

- **Q1**: τ differenziato (lancio osservato → VAL+COM+ATT; scoperto → totale) oppure sempre il
  totale? *Raccomandato: differenziato.*
- **Q2**: rilevamento del colpo deterministico (geometria) oppure con estrazione Pd come per gli
  asset? L'estrazione cambia il flusso RNG di ogni scenario con intercettazioni. *Raccomandato:
  deterministico.*
- **Q3**: rilevamento per asset oppure per forza (quadro condiviso)? *Raccomandato: per asset,
  fino alla Fase 0 C2.*

## 6. Impatto sul codice

- `Engagement_Resolver`: indice `(osservatore, bersaglio) → istante di rilevamento`; nuovo
  `_in_time(shadow, salvo)` accanto a `_may_intercept`, memoizzato sulla stessa chiave;
  docstring del modulo (punto 4 della catena).
- Test: nuova classe `TestInterceptionReaction` a geometria controllata (lancio osservato /
  non osservato, colpo che non entra nel raggio, τ appena sufficiente e insufficiente, dato
  mancante, tempo di volo nullo); aggiornamento dei test esistenti con tempo di volo nullo.
- Scenari: misura di S19 e degli scenari con intercettazioni prima/dopo.

## 7. Decisioni dell'utente (2026-09-30)

- **Q1**: τ differenziato (lancio osservato → VAL+COM+ATT; colpo scoperto → RIV+VAL+COM+ATT).
- **Q2**: rilevamento del colpo deterministico. Una Pd sul colpo, se servirà, andrà su un flusso RNG
  separato e solo quando ci sarà un dato sulla visibilità radar dei missili; anche allora basterà
  ridurre il raggio contro i colpi.
- **Q3**: rilevamento per asset, fino alla Fase 0 della gerarchia C2.

Senza posizioni o senza raggio aereo, e senza lancio osservato, vale `t_traccia = t_L` con
τ = totale: "lancio osservato" dipende solo da una `Detection` dell'intercettore sul lanciatore.

## 8. Implementazione (2026-09-30)

- `Engagement_Resolver._in_time` (memoizzato per intercettore e salva), `_round_track_time`
  (ingresso del segmento lancio→impatto nella sfera del raggio aereo, soluzione analitica),
  `_air_detection_range`, `_detection_time_of`; chiamato in `_on_resolve` accanto a
  `_may_intercept`. Docstring del modulo, punto 4 della catena.
- Test: `Test_Engagement_Resolver.TestInterceptionReaction` (8 casi: lancio osservato, lancio non
  osservato, colpo scoperto a metà volo, colpo mai nel raggio, tempo di volo nullo, dato mancante,
  passaggio all'intercettore successivo, nessuna estrazione aggiunta). I 19 test esistenti che
  intercettavano con tempo di volo nullo usano ora `REACTION_TOF = 20 s`; il test multi-fronte
  usa 1 s di volo con lanci osservati (tempi di risoluzione spostati di 1 s).
- **Misura S19** (16 seed, con e senza la regola): esiti identici. Tor arretrato 96
  intercettazioni, 32 missili offensivi; Tor avanzato 0 intercettazioni, 128 missili offensivi.
  Il Tor ha in traccia gli A-10C molto prima dei lanci (radar di 25 km): vede partire i Maverick e
  reagisce in pochi secondi contro circa 20 s di volo. Il caso del 2026-09-28 (intercettazione prima
  del primo tiro del Tor) non si ripresenta con la dottrina di tiro del 2026-09-29. La regola incide
  sui lanci non osservati, sui colpi fuori dalla copertura radar e sui tempi di volo brevi.
