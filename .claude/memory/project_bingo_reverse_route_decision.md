---
name: project-bingo-reverse-route-decision
description: "Bingo aereo: F6-B2bis (rotta a ritroso, 1,2 x ritorno) FATTA e verificata 2026-10-15 (suite 4245 OK, fotografia 770), da committare come passo intermedio; poi NUOVO MODELLO G1-G5 deciso dall'utente (riserva = 5 min alla massima spinta, soglia = resto rotta + riserva, albero di decisione per trasferimento/combattimento, basi alternative entro 3 km dalla rotta)"
metadata:
  node_type: memory
  type: project
  originSessionId: 1e331bbd-207a-4b3c-b85b-2e41ee3532b4
  modified: 2026-10-15T16:46:33.008Z
---

## F6-B2bis (2026-10-15, osboxes): FATTA, verificata da me
Implementata dall'agente `des-developer` (Opus medium). Suite 4245 OK (7 skipped). Confronto con la fotografia: 722 esecuzioni identiche
+ 48 nuove S26-BINGO (8 seed x 6 varianti, compresa la nuova `reverse_off`).
- **Regola**: al bingo l'aereo ripercorre a ritroso i tratti in movimento, senza le soste. Il fabbisogno e' `BINGO_RETURN_FACTOR = 1,2` x
  il ritorno, al posto di `BINGO_RESERVE` 0,10, che resta solo per l'interruttore spento.
- **Missione ad anello**: ritorno = minimo fra ritroso e resto della rotta. "Stessa base" = stesso blocco base, oppure punti entro
  `AIR_BASE_AREA_RADIUS_M` 3 km.
- **Partenza in volo**: ritroso fino al punto di comparsa, poi diretto alla base piu' vicina.
- **Interruttore** `Session_Simulator.F6_BINGO_REVERSE_ROUTE`. Il bingo si calcola su `MA.airborne_legs` (missione intera).
- **Cambio rispetto a B2**: partenza da una base senza basi aeree nella sessione = bingo comunque, con atterraggio sul punto di partenza.
- **S26**: carburante portato a 0,28.
- **Decisione utente**: commit come PASSO INTERMEDIO. La regola 1,2 sara' sostituita, la meccanica di rientro a ritroso si riusa.

## NUOVO MODELLO DI BINGO (proposta dell'utente 2026-10-15, approvata) — piano G0-G5
- **Riserva** = carburante per 5 minuti alla MASSIMA spinta (`DISENGAGE_TIME` = 300 s, stima dell'utente: disimpegno da
  un'intercettazione e riposizionamento in rotta).
  - DATO SCELTO DALL'UTENTE: `speed_data['emergency']['consume']` del registro `Aircraft_Data` (presente nei 66 aerei), convertito in
    frazione del pieno con `Aircraft.fuel_capacity_kg`.
  - PRIMA va verificata l'unita' di `consume`, che non e' documentata: 4200 per un caccia, se sono kg/h, e' circa 1/6 del consumo reale
    in postbruciatore.
  - **VERIFICATO 2026-10-15 (agente G1)**: `consume` e' in kg/h (coerente su `sustained`), ma `emergency` corrisponde circa alla
    spinta MILITARE, non al postbruciatore: F-16 4500 contro circa 25.000 kg/h reali; anche `time` = 60' non e' plausibile.
  - **DECISO dall'utente (strada A)**: la riserva diventa "5 minuti alla massima spinta militare", dichiarata come stima non tarata.
    Valori: F-16C circa 12%, F-15C circa 8%, A-10C circa 5% del carburante interno.
  - Ripiego quando il dato manca: regime `'max'` del loadout.
  - ARRETRATO: correggere `emergency`/`time` nel registro con dati reali documentati, ed eventuale indicazione del postbruciatore.
- **Minimo di pianificazione**: carburante caricato > rotta intera + riserva. Si controlla nel validatore a priori.
- **Soglia di bingo in volo**: residuo < resto della rotta + riserva (si comincia a intaccare la riserva).
- **Classificazione delle missioni** (mia proposta, implicitamente accettata): per geometria. Trasferimento = LAND non sulla base di
  partenza; anello altrimenti.
- **Albero al bingo, trasferimento**: se il residuo basta a concludere, continua; altrimenti ritroso, se ci arriva; altrimenti base piu'
  vicina raggiungibile; altrimenti l'aereo e' PERSO e l'equipaggio NO (registrare "equipaggio recuperato" nell'esito, perche' l'equipaggio
  non e' modellato).
- **Albero al bingo, combattimento**:
  - caso A (missione non conclusa): base di partenza a ritroso, oppure base alternativa entro 3 km dalla rotta programmata, raggiunta
    seguendo la rotta verso di essa; si sceglie la piu' vicina raggiungibile;
  - caso B (attivita' conclusa, tratta di rientro): stessa regola del caso A (deciso dall'utente).
  - Generalizzazione: le basi candidate sono quelle entro 3 km dalla rotta, compresa quella di partenza, raggiunte lungo la rotta in
    avanti o a ritroso.
- **Perche'**: senza consumo in combattimento, con consumo deterministico, una missione fattibile non va MAI in bingo in volo. Servono
  G3 e G4.

## Regimi di spinta e durata dell'emergenza (precisazione dell'utente 2026-10-16)
- Regimi della manetta = registro `speed_data`: `sustained` (crociera/normal), `combat` (military), `emergency` (massima spinta
  possibile, per un tempo limitato dall'asset). Riserva G1 e consumo in ingaggio G3 usano `emergency` (i cui VALORI attuali sono
  pero' numericamente da spinta militare, strada A).
- Durata dell'emergenza: per i jet > 5-10 min; per gli aerei WW2 (non ancora nel registro) puo' essere < 5 min. Regola futura:
  emergency per min(`DISENGAGE_TIME`, `speed_data['emergency']['time']`), poi regime `combat` per il resto. Non implementata finche'
  `time` del registro non e' corretto (unita' ignota, 60 non plausibile). Il G3 calcola il consumo in ingaggio in un solo punto per
  poterla aggiungere.

**Piano**:
- **G0 FATTO**: `96942ca7`, pushato.
- **G1 FATTO**: `c1c0f576`, pushato. `Fuel_Model.DISENGAGE_TIME`, `disengagement_reserve[_with_source]`, `Aircraft.emergency_fuel_flow`,
  `Mission_Adapter.check_mission_fuel` (non chiamato da `run_session`). Suite 4262, fotografia 770 identiche. Piano §5 deviazione 17.
- **G2 APPROVATO 2026-10-16**: fotografia 794 installata (`e5465b31`). Era: COMMITTATO 2026-10-15 "da approvare": suite 4298 OK, confronto con la fotografia NON eseguito, baseline NON aggiornata (v.
  [[project-session-2026-10-15-summary]]). Soglia + albero, nuovo interruttore. DECISO dall'utente 2026-10-15:
  - trasferimento = task 'Transport' (categoria TRANSPORT); tutto il resto, AWACS e Tanker compresi, segue la regola di combattimento;
  - un'opzione di rientro e' raggiungibile se il residuo basta per il solo percorso: la riserva si puo' consumare;
  - G2 = funzione di decisione + applicazione SOLO alla partenza. Con consumo deterministico la soglia scatta al t0 o mai: gli aerei
    sotto il minimo non decollano. In volo la funzione si attivera' con G4;
  - default comunicati all'utente: senza base raggiungibile l'aereo punta alla base piu' vicina e valgono le regole F6-A; campo
    "equipaggio recuperato" nell'esito; costante 3 km.
- **G3 APPROVATO 2026-10-17** (ProArt P16): `--compare` ripetuto 802 = 372/422/8, fotografia 802 installata (`20f0e0db`).
  DECISO dall'utente 2026-10-17: esaurimento in ingaggio (contatore a zero, l'aereo prosegue) accettato fino al G4; il limite
  "un solo consumo d'ingaggio per sessione" (tutti gli scontri della forza in una componente) si risolve NEL G4 (prerequisito S27);
  la regola WW2 futura vale anche per la riserva G1 (stessa quantita'); etichetta 'engagement' in `FuelEvent.regime` confermata.
  Era COMMITTATO 2026-10-16 da approvare (v. [[project-session-2026-10-16-summary]]): consumo di 5 minuti alla massima spinta a ogni ingaggio, nell'istante dell'ingaggio, al posto della sovrastima attuale
  "tutto il movimento a 'max' se ha combattuto".
- **G4 PROPOSTA APPROVATA 2026-10-17**: `Analysis/Document/Proposta_G4_Ri_scheduling.md`. G4a = episodi d'ingaggio
  (finestre unite se condividono una forza e si sovrappongono entro `EPISODE_GAP` = 300 s; un `resolve_engagement` per
  episodio; RNG counter = ordinale degli episodi con lo stesso insieme di forze, quindi componenti a 1 episodio identiche;
  forza occupata fino al t_end del suo esito; contabilita' carburante in un passo finale; un consumo d'ingaggio per
  episodio; forza DISENGAGED passiva negli episodi successivi; tempra nuova per episodio). G4b = ri-pianificazione a fine
  episodio (residuo analitico, F6-A se a secco, `bingo_decision(time, fuel)`, ri-scheduling dei contatti futuri). Sonda:
  con 300 s 40/778 componenti a 2 episodi (S5 x36, Blue-AirWing+CSG x4). Due passi, interruttori `G4_EPISODES`/`G4_REPLAN`,
  confronti e approvazioni separati, `des-developer` Opus high.
- **G4a+G4b APPROVATI 2026-10-17** con l'uscita di scena senza basi (decisione utente: aereo comparso in volo senza
  basi del lato che deve rientrare dopo un episodio ripercorre la rotta fino al punto di comparsa ed esce di scena,
  `BINGO_EXIT`, `G4_OFF_SCENE_EXIT`); alla partenza (G2) restano le regole F6-A. Fotografia 878 installata, pushato.
- **G4** (dettaglio originale): ri-scheduling dopo l'ingaggio + piu' consumi d'ingaggio per sessione (limite noto P2/R4 di `Session_Simulator`: cancellare le finestre future dell'asset e
  ricalcolarle). Prima l'analisi dell'architettura; proposta Opus effort high.
- **G5**: S26 riscritto, nuovo S27, Piano §5, `F4_Differenze`, manuale.
- Agenti: `des-developer` Opus medium per G1-G3.

**How to apply:** ogni passo segue la procedura solita: interruttore, mia verifica con suite + `--compare`, approvazione dell'utente,
poi fotografia e commit. Restano da confermare le scelte B2 su cui l'utente non si e' espresso: validatore fuori da `run_session`, nessuna
salva dopo il bingo. Resta da decidere F6-B3 (S24-GLIDE con bingo di default) (v. [[project-session-2026-10-13-summary]]).
