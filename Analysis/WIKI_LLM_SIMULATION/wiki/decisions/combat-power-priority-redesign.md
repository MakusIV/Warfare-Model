---
title: "Ridisegno combat power e calcolo priorità (fog-of-war)"
type: decision
tags: [architecture, dwm, combat-power, priority, fog-of-war, recon, vehicle, ship, aircraft]
created: 2026-09-18
updated: 2026-09-18
status: accepted
affects: ["[[context-state]]", "[[block]]", "[[asset-air]]", "[[asset-ground-naval]]"]
related: []
---

## Contesto

Il calcolo delle priorità militari di `Region` (`_calculate_priority`, usato per decidere quali bersagli attaccare/difendere) si basava su un `Military.combat_power()` rotto e su informazione di verità assoluta sui blocchi nemici, mentre il resto del sistema di reportistica (`Region.get_recon_reports()` / `Block.get_recognition_report()`) modella esplicitamente l'incertezza da ricognizione (fog-of-war). Un'analisi in due fasi (v1/v2, Opus high-effort) ha portato a un'iniziativa unica in più fasi: prima rendere reale il combat power per-modello di Vehicle/Ship/Aircraft (oggi quasi tutto rotto o mai eseguito), poi costruire su quella base una stima di combat power nemico compatibile col fog-of-war.

**Stato di partenza (bug preesistenti, non un problema di design):** `Vehicle_Data.get_vehicle_scores`/`get_aircraft_scores` avevano una validazione che confrontava l'intero argomento lista contro l'appartenenza a se stesso — sempre falsa, quindi **nessun Vehicle o Aircraft reale poteva mai essere costruito**. `Military.combat_power` non rispettava il contratto di `Mobile.combat_power(force, action)` (subscription su un metodo anziché un dict). `Vehicle`/`Ship` non esponevano `physical_characteristics`/`category`, quindi non comparivano mai in un `asset_summary` di ricognizione. `Ship`/`Aircraft.__init__` avevano un bug di costruzione (`self.speed = {...}` passava per un setter che non accetta quel kwarg) che rendeva impossibile costruire un'istanza reale di entrambe le classi.

## Decisione

**Fase 0/1 (combat power reale per-modello, 2026-09-11):** tutti i bug sopra sono stati corretti. È stata estratta una formula condivisa `Context.combat_power_from_score(category, score, efficacy_table, efficiency, ...)`, riusata da Vehicle (già esistente), Ship (nuova `SEA_COMBAT_EFFICACY`) e Aircraft. Per Aircraft è stato adottato un modello diverso da Vehicle/Ship su richiesta esplicita dell'utente: i task aerei (CAP, Intercept, Strike, SEAD, ...) sono ruoli di missione non mutuamente esclusivi (a differenza delle posture Attack/Defense/Retrait di terra/mare), quindi Aircraft ottiene **un valore aggregato unico** (`Aircraft_Data.combat_aggregate()`, somma del `max` per task su tutti i loadout disponibili, con normalizzazione log1p+min-max), replicato su tutti i task per rispettare il contratto esistente di `Mobile.combat_power(force, action)` senza modificarlo.

**Fase 2 (stima fog-of-war del combat power nemico, 2026-09-15/16):** nuovo modulo `Context/Combat_Power_Estimation.py` (esistenza e struttura verificate a HEAD: 210 righe, API `estimated_model_score`, `build_estimated_combat_power_table`, `estimate_combat_power_from_asset_summary`). Dato che un report di ricognizione può rivelare solo una coppia `(asset_type, dimensione)` — mai il modello esatto — la stima usa la **mediana calibrata** del punteggio combat reale dei modelli veri che ricadono in quel bucket, con la stessa formula `combat_power_from_score` del ground-truth (per non far divergere le due strade nel tempo), e un fallback a 3 livelli quando il campione è troppo piccolo (`min_samples=3`). SAM/AAA/EWR sono esclusi dalla mediana globale di fallback per motivo strutturale (hanno combat power zero per costruzione, non fanno parte della stessa popolazione), non per soglia quantitativa.

`use_recon: bool` è stato propagato end-to-end attraverso tutta la catena (`update_military_priorities` → `_calc_attack_priority` → `_calc_surface_priority`/`_calc_air_priority` → `_calculate_priority`): quando `True` e siamo nel ramo di attacco, il `target_cp` del bersaglio nemico viene sostituito dalla stima calcolata su `Region.get_recon_reports()` (una sola chiamata per sweep, mai dentro il loop di calcolo priorità); il blocco proprio e il ramo difesa restano **sempre** ground-truth, in ogni condizione — l'incertezza si applica solo a "cosa so del nemico", mai a "cosa so di me stesso o dei miei alleati".

Popolamento dati collaterale, con ricerca reale (non placeholder): campo `users: Optional[List[str]]` aggiunto a 64 modelli Vehicle e 23 Ship, per permettere un filtro `side` inclusivo (un modello senza `users` noti resta sempre incluso nella stima, mai escluso) sulla tabella di calibrazione. Aggiunta anche una dimensione fisica per-modello ad Aircraft (`physical_characteristics`, dati reali per tutti i 65 modelli, nuova `AIRCRAFT_SIZE_CATEGORY`), allineando Aircraft allo stesso schema già usato da Vehicle/Ship — prima la dimensione di un Aircraft dipendeva solo dal suo ruolo (`asset_type`), producendo classificazioni patologiche (es. un MiG-31 da 21820kg finiva nella stessa classe "small" di un MiG-15bis da 3635kg).

### No-visibility → priorità BASSA, non alta

Regola di design esplicita: un bersaglio senza un livello minimo di ricognizione/riconoscimento **non** deve essere trattato come segnale di alta incertezza/alto rischio (l'euristica ingenua "sconosciuto = pericoloso" è stata scartata). La logica adottata è opposta: l'assenza di sforzo di ricognizione su un bersaglio è essa stessa un segnale rivelato — significa che le risorse di ricognizione disponibili sono state spese su bersagli più importanti altrove. Un bersaglio non rilevato mappa quindi a **bassa priorità**, non va mai gonfiato come rischio sconosciuto. Questa regola si applica specificamente alla stima `target_cp` di Fase 2 (`_estimated_target_combat_power`/`estimate_combat_power_from_asset_summary`) — un `block_id` assente dallo snapshot di ricognizione vale `0.0`, non un ripiego al ground-truth.

**Esplicitamente esclusa da questa policy: `_target_affinity`** (ora `Tactical_Evaluation.target_affinity`, si veda [[air-priority-target-specific-loadout]]). Quel meccanismo risponde a una domanda diversa ("qual è il miglior loadout contro una composizione sconosciuta") dove il neutro (`1.0`, nessun bonus/malus) su bersaglio sconosciuto non è un giudizio di importanza ma una scelta di non-informazione — le due logiche non vanno confuse.

### Selezione dell'azione per il rapporto di combat power

Per calcolare il rapporto attacco/difesa in `_calculate_priority`, la scelta dell'azione (task) da passare a `Military.combat_power(force, action)` doveva essere risolta: un primo stand-in (Fase 0) sommava il combat power su **tutti** i task della force, diluendo il segnale. Decisione dell'utente: usare specificamente il task **'Attack'** per il ramo di attacco (non somma/media) — l'obiettivo è che il numero di attack-priority significhi qualcosa di leggibile: alta priorità = vantaggio di combat power chiaro sul bersaglio; bassa priorità = nessun vantaggio. Implementato in Fase 2 del piano fog-of-war: `_representative_combat_power(block, force, action)` usa `'Attack'` per il proprio blocco nel ramo di attacco, e per il bersaglio militare usa `max('Defense','Maintain')` su terra, solo `'Defense'` in mare, azione singola (nessuna scelta) per l'aria (che ha un solo aggregato).

L'utente ha inoltre espresso l'intenzione, non ancora implementata, di calcolare in futuro un **vettore di priorità per azione** (Attack/Defense/Maintain/Retrait), non solo Attack — questi valori diventerebbero input di un livello decisionale successivo che sceglie l'azione effettiva da assegnare a un blocco, usando anche contesto tattico/strategico non ancora modellato (disponibilità asset, orientamento di campagna, morale). Il 2026-09-17 questa idea è stata esplicitamente ricollegata al concetto di "indirizzo strategico" del design C2 (per-regione, per-dominio aria/terra/mare, Attack/Maintain/Defense/Retreat guidato da morale/perdite/produzione) — da implementare insieme a quel design, non separatamente.

## Motivazione

- Riusare/calibrare gli score reali per-modello già esistenti (`Vehicle_Data.get_vehicle_scores`) invece di inventare una tabella hand-authored separata — evita la divergenza fra due sistemi di scoring dello stesso concetto nel tempo.
- Aircraft trattato diversamente da Vehicle/Ship non per incoerenza ma perché i ruoli aerei sono realmente non-esclusivi (un loadout CAP serve sia offesa che difesa): forzare lo stesso schema Attack/Defense/Retrait avrebbe prodotto un modello falso.
- Mediana di bucket (non media, non tabella arbitraria) per la stima fog-of-war: garantisce matematicamente che la stima ricada nel range dei modelli veri del bucket, proprietà usata anche nei test di coerenza senza bisogno di tolleranze numeriche magiche.
- No-visibility→bassa priorità riflette un principio di dottrina reale (l'allocazione di ricognizione è essa stessa informazione), non solo una scelta tecnica di default.

## Conseguenze

- `Region.update_military_priorities(side, use_recon=True)` è la superficie pubblica che attiva l'intera catena fog-of-war end-to-end (verificato a HEAD: `Region.py`, firma `update_military_priorities(self, side: str, use_recon: bool = False)`).
- **`use_recon` ha default `False` ovunque e non è ancora abilitato da nessun chiamante di produzione**: verificato a HEAD che l'unico chiamante reale, `run_resource_management_cycle`, invoca `self.update_military_priorities(side=side)` senza passare `use_recon` — resta quindi sempre in modalità ground-truth in produzione. Attivarlo nel ciclo di simulazione reale è una decisione applicativa separata, non ancora presa.
- Bug preesistenti scoperti ma esplicitamente non corretti in questo lavoro (fuori scope, segnalati per il futuro): `Context.TARGET_CLASSIFICATION` classifica sempre `AAA` come `'Armored'` mai `'Air_Defense'` (duplicato nell'ordine del dizionario); `Air_Asset_Type.TRANSPORT` collide col vocabolario `SEA_MILITARY_CRAFT_ASSET`, per cui un C-130 può risultare classificato come nave; `Ship.loadAssetDataFromContext`/`Aircraft.loadAssetDataFromContext` hanno un bug di iterazione su dict piatto senza `.items()` (verificato a HEAD: `Ship.py:65`, `for k, v in asset_data[self.asset_type]:` — nessun `.items()`), non collegato al fog-of-war ma preesistente.
- Suite di test cresciuta da 2316 (inizio Fase 0) a 2516 OK/5 skipped al completamento delle 6 fasi del piano fog-of-war (2026-09-16).

## Fonti

- [[project_priority_calc_combat_power_redesign]] (Fase 0/1 — combat power reale Vehicle/Ship/Aircraft)
- [[project_fase2_recon_combat_power_plan]] (Fase 2 — stima fog-of-war, 6 fasi complete)
- [[feedback_no_visibility_low_priority]] (regola no-visibility → priorità bassa)
- [[feedback_combat_power_action_selection]] (selezione del task 'Attack', vettore di priorità per azione)
