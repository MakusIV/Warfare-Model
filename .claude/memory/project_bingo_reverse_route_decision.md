---
name: project-bingo-reverse-route-decision
description: "Bingo aereo: F6-B2bis (rotta a ritroso, 1,2 x ritorno) FATTA e verificata 2026-10-15 (suite 4245 OK, fotografia 770), da committare come passo intermedio; poi NUOVO MODELLO G1-G5 deciso dall'utente (riserva = 5 min alla massima spinta, soglia = resto rotta + riserva, albero di decisione per trasferimento/combattimento, basi alternative entro 3 km dalla rotta)"
metadata:
  node_type: memory
  type: project
  originSessionId: 1e331bbd-207a-4b3c-b85b-2e41ee3532b4
  modified: 2026-10-15T14:07:14.471Z
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

**Piano**:
- **G0**: commit della B2bis con la fotografia 770.
- **G1**: riserva + validatore.
- **G2**: soglia + albero, con nuovo interruttore.
- **G3**: consumo di 5 minuti alla massima spinta a ogni ingaggio, nell'istante dell'ingaggio, al posto della sovrastima attuale
  "tutto il movimento a 'max' se ha combattuto".
- **G4**: ri-scheduling dopo l'ingaggio (limite noto P2/R4 di `Session_Simulator`: cancellare le finestre future dell'asset e
  ricalcolarle). Prima l'analisi dell'architettura; proposta Opus effort high.
- **G5**: S26 riscritto, nuovo S27, Piano §5, `F4_Differenze`, manuale.
- Agenti: `des-developer` Opus medium per G1-G3.

**How to apply:** ogni passo segue la procedura solita: interruttore, mia verifica con suite + `--compare`, approvazione dell'utente,
poi fotografia e commit. Restano da confermare le scelte B2 su cui l'utente non si e' espresso: validatore fuori da `run_session`, nessuna
salva dopo il bingo. Resta da decidere F6-B3 (S24-GLIDE con bingo di default) (v. [[project-session-2026-10-13-summary]]).
