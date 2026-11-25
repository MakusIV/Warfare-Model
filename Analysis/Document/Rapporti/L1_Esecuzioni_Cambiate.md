# L1 rivista — esecuzioni cambiate con l'interruttore acceso (blocco 4, sonda)

Data: 2026-11-25. Autore: sessione principale (Claude). Branch `ai/des-l1-revisione`, codice dei blocchi 1-3 a `a1559ad9`
(interruttore `L1_IMMEDIATE_TARGET_RULE` SPENTO nel codice; la sonda lo accende solo in memoria).
Piano: `Proposta_Revisione_L1_Lanciatore_Bersaglio.md` §4.4. Script: `Sonde_L1_Revisione/probe_l1.py` e `suite_l1_on.py`
(dalle Appendici A e B). Log: `.ai-run/l1_on.log`, `l1_on_cmp.log`, `l1_suite_on.log`, `l1_on.json(.rows.json)`.

## 1. Esito (tutto conforme all'atteso della Proposta, §4.8 stato "acceso")

| Verifica | Atteso | Misurato |
|---|---|---|
| Cattura con interruttore acceso | 1219 esecuzioni, 0 errori | 1219 esecuzioni, 0 errori |
| Coppie (intercettore, salva) valutate | 414 | 414 (S2 46, S6 113, S11 30, S16 152, S19AD 19, S35-ADTGT 54) |
| Coppie escluse dalla regola del 2026-09-28 | 14 | 14 |
| Coppie escluse dalla regola rivista | 0 | **0** |
| Confronto con la fotografia | 6 CHANGED, 1213 identiche, 0 NEW, 0 MISSING | 6 CHANGED, 1213 identiche, 0 NEW, 0 MISSING (le stesse 6 nominate) |
| Suite con interruttore acceso in memoria | falliscono solo `test_switch_is_off_by_default` e `test_forward_tor_engages_launchers_inside_its_zone` (S19-4) | `Ran 5005`, `FAILED (failures=2)`: esattamente questi due |

Non e' stata rieseguita la sonda con l'interruttore spento (la suite e il confronto a interruttore spento erano gia'
IDENTICAL a 1219, e la sonda a `off` e' una verifica "minima" della spia). Il fatto che le 6 cambiate coincidano con le
6 della sonda con L1 spenta del tutto (2026-11-24, S16/S19AD/S35) e' coerente con "la regola rivista non esclude mai",
ma l'identita' dei valori non e' stata ricontrollata riga per riga in questa sessione.

## 2. Le 6 esecuzioni cambiate (prima = fotografia, dopo = interruttore acceso)

| Esecuzione | Cosa cambia |
|---|---|
| `S16/S16-3` | Red-Port: esito `destroyed` -> `held`; intercettazioni 34 -> 44; distrutti 5 -> 3; eventi di danno 20 -> 15 |
| `S19AD/S19-4/tor_forward_ifv_only` | Red-Line (Tor): intercettazioni 0 -> 2; colpi 8 -> 6; distrutti 2 -> 1; eventi di danno 10 -> 6 |
| `S35-ADTGT/S35-ADTGT-0/naval_maverick_off` | Red-Navy: `destroyed` -> `held`; intercettazioni 2 -> 6; distrutti 1 -> 0; colpi Blue-CAS 4 -> 6; eventi di danno 5 -> 4 |
| `S35-ADTGT/S35-ADTGT-1/naval_maverick_off` | Red-Navy: `destroyed` -> `held`; intercettazioni 2 -> 6; distrutti 1 -> 0; colpi Blue-CAS 4 -> 6; eventi di danno 6 -> 4 |
| `S35-ADTGT/S35-ADTGT-2/naval_maverick_off` | Red-Navy: `destroyed` -> `held`; intercettazioni 0 -> 4; distrutti 1 -> 0; colpi Red-Navy 6 -> 8; colpi Blue-CAS 2 -> 4 |
| `S35-ADTGT/S35-ADTGT-3/naval_maverick_off` | Red-Navy: `destroyed` -> `held`; intercettazioni 2 -> 4; distrutti 1 -> 0; eventi di danno 5 -> 4 |

In tutte e 6 la direzione e' una sola: piu' intercettazioni, meno perdite della forza difesa. Nessuna esecuzione peggiora
per il difensore.

## 3. Coppie escluse oggi (regola del 2026-09-28) e con la regola rivista

Le 14 coppie escluse oggi (tutte con R-INT che avrebbe permesso di intercettare, `r_int_ok = True`):

| Unita' | Intercettore | Lanciatore, arma | Coppie | Lanciatore "bersaglio immediato"? | Zona dell'arma contiene il lancio? |
|---|---|---|---|---|---|
| S16 | Molniya (FSG 1241.1MP) | Blue-Naval-Strike (5 lanciatori fa*), `test:anti_ship` | 6 | no | no: zona dell'AK-630 = 4 km, 0-3000 m; lanci a 2,3-10,7 km orizzontali e 6000 m di quota relativa (oltre il tetto dell'arma; V_I di oggi 12 km, 10-6000 m) |
| S19AD | Tor (9K331) | Blue-CAS/cas1, AGM-65D | 1 | no (non rilevato al lancio) | si': 9,7 km e 3000 m, dentro la zona 12 km, 10-6000 m |
| S35-ADTGT | Rezky (FF 1135M) | Blue-CAS/cas0 (4) e cas1 (3), AGM-65D | 7 | si' (rilevato e a portata) | no: lanci a 7,1-11,1 km, fuori dai 4 km dell'AK-630 |

Con la regola rivista: **0 coppie escluse**, perche' nessuna delle 14 soddisfa insieme le due condizioni: 6 (S16) sono
fuori zona e non bersaglio immediato, 1 (S19AD) e' dentro la zona ma il lanciatore non e' bersaglio immediato, 7 (S35) sono
bersaglio immediato ma fuori zona. Quindi il ramo "lanciatore bersaglio immediato dentro la zona dell'arma = non si
intercetta" non e' esercitato da nessuna esecuzione fotografata: resta provato solo dai test unitari e di scenario fuori
dalla fotografia (blocchi 2-3; Proposta §1.5 L-2, Q-L1-4).

## 4. Suite con interruttore acceso

Falliti (2, attesi):
1. `Test_Engagement_Resolver.TestL1ImmediateTarget.test_switch_is_off_by_default` — per costruzione (verifica il default).
2. `Test_Session_Scenarios_S19_Air_Defence.TestS19AirDefenceAllocation.test_forward_tor_engages_launchers_inside_its_zone`
   (seme `S19-4`, `Test_Session_Scenarios_S19_Air_Defence.py:212`: atteso 0 intercettazioni del Tor, ora 2) — da
   riscrivere all'accensione come da §4.5 punto 3 della Proposta.

Nessun altro test fallisce: le fissature a interruttore spento dei blocchi 2-3 reggono.

## 5. Cosa serve per l'accensione (blocco 5, SOLO su decisione esplicita dell'utente)

Una riga (`L1_IMMEDIATE_TARGET_RULE = True`), il rinomino/inversione del test sul default, la riscrittura del test del
Tor (§4.5 punto 3) e i ritocchi ai docstring (§4.5 punto 4). Poi suite e confronto completi (atteso §4.8: 6 CHANGED);
la fotografia nuova la installa solo l'utente. Il blocco 6 (eliminare l'interruttore) va ripianificato.
