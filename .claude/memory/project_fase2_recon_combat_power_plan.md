---
name: project-fase2-recon-combat-power-plan
description: "Fase 2 (fog-of-war combat-power estimation) — full plan produced by an Opus/high-effort Plan agent 2026-09-15, verified against real code, NOT YET IMPLEMENTED. 7 open design questions block start. Re-present this whole file at the next session before continuing."
metadata:
  node_type: memory
  type: project
  originSessionId: 68a4bcf0-0d82-4d78-95f3-8034f1d81a8d
  modified: 2026-09-15T16:38:24.611Z
---

# Fase 2 — piano di stima combat power fog-of-war — DA RIPRESENTARE INTEGRALMENTE ALLA PROSSIMA SESSIONE

**Stato: pianificazione completata, zero codice scritto.** Sessione 2026-09-15, dopo aver chiuso la normalizzazione `category`/`asset_type` ([[project_vehicle_asset_type_category_conflict]]). Il piano è stato prodotto da un agente Plan basato su Opus (effort alto), che ha verificato ogni riga di codice citata prima di scrivere il piano (non ha preso per buone le mie sintesi). Vedi anche il contesto generale in [[project_priority_calc_combat_power_redesign]].

**Istruzione per la prossima sessione**: ripresenta per intero questo file all'utente (stato, piano, domande aperte, considerazione dell'utente sulla dimensione) prima di riprendere il lavoro — non riassumere ulteriormente, l'utente ha chiesto esplicitamente il riepilogo completo.

## Premesse verificate (tutte confermate contro il codice reale)

- `Region.py:1128-1129`: la guardia `target_cp <= 0` produce già `combat_power_ratio = 0.1` per il ramo attacco (lati diversi) — un target senza combat power nota risulta già priorità bassa. Se lo stimatore fog-of-war ritorna 0.0 in assenza di visibilità, la policy "no-visibility → priorità bassa" ([[feedback_no_visibility_low_priority]]) si ottiene gratis, senza nuovo branching.
- `Region.py:1083-1088`: `_representative_combat_power` somma su tutti i task per ground/sea, prende un solo task per air — stand-in provvisorio, già segnalato come sbagliato in [[feedback_combat_power_action_selection]].
- `Region.py:797`: `get_recon_reports` usa `self.get_c2_efficiency(side=side)` — C2 del lato **osservato**, non dell'osservatore. Fix a una riga: `Utility.enemySide(side)`. `Utility.enemySide` esiste (`Utility.py:323`), ritorna `'Neutral'` per input non Blue/Red.
- `Context.TARGET_CLASSIFICATION` è inutilizzabile per la stima di combat power, e **peggio di quanto pensassi**: `tc.ARMORED` collassa `Armored`+`Tank`+`AAA`+`Artillery_Semovent` in un solo bucket; `tc.AIRCRAFT` collassa **tutti e nove** i valori di `Air_Asset_Type` insieme (Fighter efficacia 5.0 trattato come Transport 1.0); `get_target_classification` (`Context.py:1514-1522`) ritorna la **prima** chiave che matcha nell'ordine del dizionario, quindi `AAA` finisce sempre in `'Armored'`, mai in `'Air_Defense'`. **Bug preesistente indipendente da Fase 2, non corretto, da tenere presente per un intervento futuro separato.**
- `Block.py:601, 622-648`: `report['asset_summary']['operative']` è già `{asset_type: {dimensione: count}}`, grezzo, prima di qualunque collasso per classificazione — è questo il dato da leggere per la stima, **mai** passando da `get_target_report`/`TargetProfile`.
- `GROUND_COMBAT_EFFICACY`/`SEA_COMBAT_EFFICACY` hanno una voce `'Defense'` reale e distinta; `AIR_TASK` non ha alcun task `'Defense'` (è un elenco di ruoli missione: CAP, Strike, Intercept, SEAD, ...) e `AIR_COMBAT_EFFICACY` è piatta (nessuna azione). Per l'air la selezione Attack/Defense è quindi un no-op per costruzione, non una scelta.
- Nessun campo `users`/nazione in `Vehicle_Data.py`/`Ship_Data.py` (zero occorrenze); `Aircraft_Data.py` ce l'ha e lo incrocia con `Context.COALITIONS[side]` (`Aircraft_Data.py:1027,1051`).
- `_representative_combat_power` ha solo 2 chiamanti in produzione (entrambi dentro `_calculate_priority`, righe 1113 e 1125), nessuno nei test.
- Una presunta duplicazione di `_calc_surface_priority`/`_calc_air_priority` (righe 1308/1383) è risultata **falso allarme**: è testo morto dentro una docstring `""" superata """` (righe 1307-1436), non codice attivo.

## Scoperte nuove non previste dal design originale (v1/v2, 2026-09-11)

1. **Import circolare**: `Context.py` non importa nulla da `Asset/*`, mentre `Vehicle_Data.py`/`Ship_Data.py`/`Aircraft_Data.py` importano *da* `Context.py`. La tabella di calibrazione NON può stare in `Context.py`. Serve un **nuovo modulo**: `Context/Combat_Power_Estimation.py`.
2. **Campioni del registro scarsi/assenti**: `Motorized` e `Artillery_Fixed` hanno **zero** modelli in `Vehicle_Data._registry`, pur essendo chiavi di `GROUND_COMBAT_EFFICACY` — serve fallback obbligatorio a cascata: bucket `(asset_type, dimensione)` con soglia minima campioni → bucket `asset_type` → mediana globale della force → 0.0.
3. **Per l'air la dimensione è funzione pura dell'asset_type** (`classify_asset_dimension:306-315`: Fighter/Helicopter/Attacker→small, Fighter_Bomber/Recon→med, Bomber/Transport/Awacs/Heavy_Bomber→big) — includerla nel bucket per l'air non aggiunge segnale, solo frammentazione campionaria.
4. **Dispersione intra-bucket misurata alta** (es. Tank: range 0.154-1.000 attorno a mediana 0.432) — la stima non convergerà mai al ground-truth nemmeno con recon perfetta; i test non devono asserire uguaglianza tra i due percorsi, solo un intervallo di tolleranza.
5. **`Vehicle_Data.py` costa ~1.12s all'import** e oggi non è nella catena di import di `Region.py` (solo `Aircraft_Data` lo è). Import a livello di modulo raddoppierebbe il tempo della suite di test — **import lazy obbligatorio**, dentro le funzioni.
6. **I metodi di priorità sono `@lru_cache`d e la stima recon è stocastica** (`Block.get_recognition_report` pesca numeri casuali ad ogni chiamata, `Block.py:587-599`). Senza uno snapshot esplicito per sweep, lo stesso blocco nemico riceverebbe stime diverse a seconda di quale blocco amico lo valuta, e sweep successivi congelerebbero il primo risultato. Serve uno snapshot (`self._recon_cp_snapshot`) costruito una volta per ciclo con invalidazione cache esplicita.

## Piano in 5 fasi (indipendentemente committabili, ordine 1→2 prerequisito di 3)

**Fase 1** — fix C2 in `get_recon_reports` (`Region.py:797`, one-liner `Utility.enemySide(side)`). Rompe **una sola** asserzione: `Test_Region.py:856` (`assert_called_once_with(side="Red")` → `side="Blue"`).

**Fase 2** — selezione Attack/Defense in `_representative_combat_power`:
```python
_representative_combat_power(self, block, force, action: Optional[str] = None) -> float
```
- `force == 'air'` → ignora `action` (nessun task Defense esiste, tutti i task hanno lo stesso valore aggregato).
- `action is None` → comportamento legacy (somma su tutti i task), mantenuto per compatibilità.
- altrimenti → `breakdown.get(action, 0.0)`.

Tabella ruoli in `_calculate_priority`:
| Ramo | Blocco proprio | Target |
|---|---|---|
| attacco (lati diversi) | `'Attack'` | `'Defense'` |
| difesa (stesso lato) | `'Defense'` | `'Defense'` |

Il ramo difesa (Defense/Defense su entrambi, non Attack/Defense) è una **proposta dell'agente non ancora confermata dall'utente** — ragionamento: nel ramo difesa il blocco proprio assume una postura difensiva, e il valore rilevante dell'alleato protetto è quanto regge da solo (Defense), non la sua capacità offensiva.

Conseguenza da accettare esplicitamente (vedi Q3): il gate iniziale `combat_power <= 0 → return 0.0` (`Region.py:1114`) ora valuta un singolo task invece della somma — un blocco fatto solo di SAM/AAA/EWR (che hanno comunque combat_power 0 su ogni azione) non cambia comportamento; rischio pratico basso ma è un cambio di comportamento da segnalare nel commit.

**Fase 3** — nuovo modulo `Code/Dynamic_War_Manager/Source/Context/Combat_Power_Estimation.py`:
```python
DEFAULT_MIN_SAMPLES = 3

def estimated_model_score(asset_type, dimension, force, side=None, min_samples=DEFAULT_MIN_SAMPLES) -> float
def build_estimated_combat_power_table(force, action, *, side=None, efficiency=1.0, min_samples=DEFAULT_MIN_SAMPLES) -> Dict[Tuple[str, Optional[str]], float]
def estimate_combat_power_from_asset_summary(operative: Dict[str, Dict[str, int]], force, action, *, side=None, efficiency=1.0) -> float
```
- `_bucket_scores(force, side)` importa `Vehicle_Data`/`Ship_Data`/`Aircraft_Data` **lazy** dentro la funzione, mai a livello di modulo; `@lru_cache` su `(force, side)`.
- Bucket key da `Vehicle_Data.category`/`Ship_Data.category` (= vocabolario `asset_type`, verificato) + `Context.get_dimension(...)`. Per l'air, `category` nel registro è una **lista** di `Air_Asset_Type` — un modello contribuisce a ogni bucket elencato.
- Catena di fallback: `(asset_type, dimensione)` se n≥soglia → mediana; altrimenti `asset_type`-solo se non vuoto → mediana; altrimenti mediana globale della force (esclude SAM/AAA/EWR, punteggi quasi nulli che inquinerebbero il fallback); altrimenti 0.0. Per l'air, salta il primo livello (dimensione ridondante, vedi scoperta 3).
- `estimate_combat_power_from_asset_summary` è il punto d'ingresso da `Region`: itera `operative.items()` (formato grezzo, MAI l'output di `get_target_report`), usa `Context.combat_power_from_score` per bucket, somma; ritorna 0.0 per dict vuoto/tutto-zero (nessuna nuova logica no-visibility necessaria, si aggancia al gate esistente di `_calculate_priority`).

**Fase 4** — campo `users` (solo schema + wiring, popolamento dati **rimandato**):
- `Vehicle_Data.__init__`/`Ship_Data.__init__`: `users: Optional[List[str]] = None` → `self.users = users or []`, **keyword con default, in fondo alla firma** (non tocca le ~64+23 literal esistenti). Non imitare `Aircraft_Data` che ce l'ha posizionale obbligatorio.
- Filtro nell'estimatore mirror di `Aircraft_Data.py:1027`: `any(u in Context.COALITIONS[side] for u in model.users)` quando `side` è dato.
- **Fallback obbligatorio**: un modello con `users` vuoto/assente va **incluso** in ogni bucket per-lato (non escluso), altrimenti finché i dati non sono popolati ogni bucket per-lato risulta vuoto e degrada silenziosamente al fallback globale per ogni chiamata.
- **Il popolamento reale dei dati (~64 modelli Vehicle, ~23 Ship, ricerca via web per nazione/utilizzatore) resta esplicitamente un lavoro separato e successivo**, non parte di questa fase.

**Fase 5** — `use_recon` in `Region`:
```python
update_military_priorities(self, side, use_recon: bool = False) -> None
_calc_attack_priority(self, military_block, enemy_blocks, use_recon: bool = False) -> float
_calc_surface_priority(self, block, target_item, attack_route, weight, use_recon: bool = False) -> float
_calc_air_priority(self, block, target_block, weight, use_recon: bool = False) -> float
_calculate_priority(self, ..., use_recon: bool = False) -> float
```
- `_calc_defense_priority` **NON riceve `use_recon`** — il ramo difesa opera sempre su ground-truth (un lato conosce le proprie forze).
- Nuovi helper: `_build_recon_cp_snapshot(self, observed_side)` (uno sweep, `block_id → combat power stimata`), `_estimated_target_combat_power(self, report, force, action)`.
- Flusso: se `use_recon`, chiama `get_recon_reports(enemySide(side))` **una sola volta** per sweep, indicizza per `report['block_id']`, invalida cache priorità, poi in `_calculate_priority` sostituisce `target_cp` con lo snapshot per i target nemici (ramo attacco) quando `use_recon=True`; il blocco proprio resta **sempre** ground-truth.
- `_target_affinity` resta su ground-truth (`_target_profile_from_block`) — scelta di scope deliberata, vedi Q5.

## Impatto sui test

Rottura attesa: **una sola asserzione**, `Test_Region.py:856` (Fase 1). Tutto il resto (incluse le classi `TestTargetProfileFromBlock`, `TestTargetProfileFromReport`, `TestProfileToWeaponDistribution`, `TestTargetAffinity` — che devono restare **non toccate per design**, è la prova che il confine con `TargetProfile` tiene) passa invariato.

Nuovi test previsti (non ancora scritti): `Test_Combat_Power_Estimation.py` (nuovo file — fallback chain, tabella per azione, stima da asset_summary, coerenza-con-tolleranza vs ground-truth, filtro `users`); aggiunte a `Test_Region.py` (selezione azione in `_representative_combat_power`, ruoli Attack/Defense in `_calculate_priority`, `use_recon` end-to-end incluso il caso "nessuna visibilità → ratio 0.1", consistenza dello snapshot per sweep, C2 dell'osservatore corretto).

## 7 domande aperte (bloccano l'inizio implementazione)

- **Q1** — soglia minima campioni per il bucket `(asset_type, dimensione)`: l'agente raccomanda 3 con fallback ad `asset_type`-solo sotto soglia. **Vedi la considerazione dell'utente sotto — probabilmente risolve Q1 nel senso di NON usare affatto la dimensione nella calibrazione.**
- **Q2** — quale efficienza usare nella stima: `report['efficiency']` (spesso `None` se non rilevata — usarlo con fallback 1.0 rischia di sovrastimare un target proprio quando meno visibile, contro la policy no-visibility=bassa priorità) vs. sempre 1.0 fisso. Non decisa.
- **Q3** — il gate "combat power ≤0 → 0" sul blocco proprio: dopo la Fase 2 valuta una singola azione invece della somma, con effetto collaterale sui target logistici/civili per blocchi puramente SAM/AAA/EWR (rischio pratico basso ma reale). Va bene così?
- **Q4** — meccanismo snapshot: stash su `self` + invalidazione cache esplicita (più semplice) vs. parametro `recon_epoch` incrementale passato esplicitamente nei metodi cachati (più corretto, un parametro in più su 4 metodi). Non decisa.
- **Q5** — `_target_affinity` resta volutamente a ground-truth anche con `use_recon=True`? Esiste già `_target_profile_from_report`, oggi dead code senza chiamanti, che la userebbe — collegarla sarebbe economico ma non richiesto.
- **Q6** — la stima è "istantanea per ciclo" (coerente con la policy "non visto=basso") o serve un'intelligence che si accumula/decade nel tempo (cambia la forma dello snapshot, da `Dict` stateless a stato persistente)? L'agente ha implementato la prima ipotesi seguendo la policy dichiarata, da confermare.
- **Q7** — il lato `'Neutral'` (esiste in `COALITIONS` e come ritorno di `enemySide`): osservatore di prima classe o chiamata da considerare errore? Da verificare la tolleranza di `check_side` prima della Fase 1.

## Considerazione dell'utente (2026-09-15, dopo la presentazione del piano) — rilevante soprattutto per Q1

L'utente osserva, e ho verificato che è corretto: negli Asset `Vehicle`/`Ship`/`Aircraft`, `dimension` (big/med/small) è usata **esclusivamente** per valutare l'efficacia di un armamento contro una caratterizzazione del target basata su categoria (asset_type), dimensione, quantità e relativa distribuzione — funzioni verificate: `Vehicle_Data._weapon_target_effectiveness(target_type, target_dimension)` (`Vehicle_Data.py:669`), `Vehicle_Data._weapon_target_effectiveness_distribuition(target_type, target_dimension)` (`Vehicle_Data.py:721`), e gli equivalenti in `Aircraft_Loadouts.py`: `loadout_target_effectiveness(...)` (`:3800`) e `loadout_target_effectiveness_by_distribuition(...)` (`:3833`) — entrambi prendono `target_type`/`target_dimension` (o una distribuzione) come parametri per valutare quanto un armamento/loadout è efficace contro quel tipo di target.

**Implicazione che l'utente vuole venga portata nella prossima sessione**: se `dimension` appartiene concettualmente e sistematicamente al dominio "efficacia arma-vs-target" (già la logica di `_target_affinity`, deliberatamente separata da `_calculate_priority` per lo stesso motivo — vedi [[feedback_no_visibility_low_priority]]), allora i calcoli di **combat_power** (che rispondono a una domanda diversa: quanto è forte il target, non quale arma usare contro di esso) probabilmente non dovrebbero includere la dimensione nel bucket di calibrazione — userebbero solo `asset_type`. Questo tenderebbe a risolvere Q1 nel senso "niente split per dimensione", il che risolverebbe anche gran parte del problema di scarsità di campioni per bucket (scoperta 2/4 sopra), poiché i bucket `asset_type`-only hanno campioni molto più numerosi. **Non ancora deciso in modo definitivo — da confermare esplicitamente alla prossima sessione**, ma è l'argomento più forte finora a favore di questa scelta.

## Prossimi passi

1. Ripresentare questo file per intero (non solo un riassunto) all'inizio della prossima sessione.
2. Chiudere Q1 (probabilmente: niente dimensione nel bucket, solo `asset_type`, alla luce della considerazione sopra) e le altre 6 domande.
3. Solo dopo, iniziare l'implementazione Fase 1→5 in ordine, con suite di test eseguita dopo ogni fase.
