---
name: project-session-2026-10-16-summary
description: "Sessione 2026-10-16 (osboxes) CHIUSA: G2 verificato/approvato, fotografia 794 installata (e5465b31); G3 (consumo carburante in ingaggio) implementato e committato DA APPROVARE, fotografia NON installata; alla ripresa: --compare G3, 4 decisioni utente, installazione fotografia; poi G4"
metadata:
  node_type: memory
  type: project
  originSessionId: 6aed8959-ec4b-4e9c-8447-de1ec3948927
  modified: 2026-10-16T15:21:11.160Z
---

**STATO AL 2026-10-16 (chiusura su osboxes)**: branch `analysis/dce-dcs-persistence`, tutto pushato. Prossima sessione su un'ALTRA
macchina: `git pull`, interprete della macchina (v. [[feedback-venv]]). Suite e `--compare` MAI in parallelo.

## Fatto in sessione
1. **G2 verificato e approvato**: `--compare` 794 (762 identiche, 8 cambiate S26 'bingo', 24 nuove; 'reserve_off' identiche alle
   vecchie 'bingo'); l'utente ha approvato anche le 7 scelte dell'agente. Fotografia 794 installata, commit `e5465b31`.
2. **Precisazione dell'utente sui regimi di spinta** (cruise/combat-military/emergency, durata limitata dell'emergenza, WW2 < 5 min):
   registrata in [[project-bingo-reverse-route-decision]].
3. **G3 implementato** (agente `des-developer` Opus medium), committato come "da approvare", fotografia NON installata:
   - `Fuel_Model`: `ENGAGEMENT_REGIME` = 'engagement', `engagement_fuel[_with_source]` (unico punto, delega a
     `disengagement_reserve_with_source`), `build_engagement_fuel_event` (FuelEvent istantaneo, limitato al disponibile);
   - `Session_Simulator`: interruttore `G3_ENGAGEMENT_FUEL` (True), `_engagement_instants` (partecipa = tiratore / bersaglio di salva /
     intercettore, istante = primo `t_launch` o intercettazione); aerei di missione in volo: movimento sempre a crociera + consumo
     d'ingaggio; terra/mare invariati; aerei a terra niente consumo;
   - esaurimento in ingaggio: solo il contatore a zero, l'aereo prosegue (nessun ri-scheduling, G4);
   - S26 + variante 'engagement_fuel_off' (identica alle vecchie 'none'); Piano §5 deviazione 19; sezione G3 in `F4_Differenze`.
   - **Verificato da me**: suite **4321 OK (7 skipped)**; confronto 802 = 372 identiche, 422 cambiate (SOLO voci carburante, controllato
     chiave per chiave), 8 nuove. Quasi tutti gli scenari aerei con meno carburante (-0,013..-0,167: un ingaggio ~0,05-0,12 del pieno,
     pareggio con la vecchia sovrastima a ~350 km di rotta per F-16C); piu' carburante in S5 (950 km, +0,045) e S22-AIR 'parked';
     S26 'transfer_continue' finisce a 0,0 con rotta completata (limite pre-G4).

## DA FARE ALLA RIPRESA (riproporre all'utente questo piano)
1. **Rifare il `--compare` del G3** sulla nuova macchina (la cattura in scratchpad e' persa): atteso 802 esecuzioni, 372/422/8.
2. **Chiedere all'utente** (domande gia' formulate, l'utente ha chiuso prima di rispondere):
   - approvazione G3 + installazione fotografia 802;
   - esaurimento in ingaggio: accettare fino al G4 (mia raccomandazione) o anticipare ora planata/perdita F6-A;
   - un solo consumo d'ingaggio per sessione (tutti gli scontri della forza in una componente): risolverlo nel G4 (raccomandato),
     prerequisito di S27 del G5 con due intercettazioni;
   - regola WW2 futura: anche la riserva G1 la segue (raccomandato: si', stessa quantita');
   - (default che terrei) etichetta 'engagement' in `FuelEvent.regime`.
3. Installare la fotografia (`--capture` in scratchpad, `--against`, copia), commit.
4. **G4**: ri-scheduling dopo l'ingaggio (analisi dell'architettura prima, proposta Opus effort high).
5. **G5**: S27, manuale.
6. Aperti invariati: F6-B3 S24-GLIDE, conferma validatore fuori da `run_session`, F7, F8, F9, arretrato (registro
   `emergency`/`time`, `testCalcFightResult`, Fase 0 C2, rotte -> mappe). File non tracciato `Analysis/Document/Untitled 1.odt`
   dell'utente: mai toccato.
