---
name: project-virtual-session-engine-design
description: "Analisi delle due strategie proposte per il motore di esecuzione delle sessioni virtuali (tick a 1 ms vs risoluzione probabilistica) e architettura decisa: DES a coda eventi con scheduling analitico dei contatti. Documento in Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md, 2026-09-21."
metadata:
  type: project
---

**Stato 2026-09-21: analisi COMPLETATA e documentata. FASE 1 (cinematica) FATTA, non committata.**
Documento: `Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` (525 righe),
a fianco della proposta sorgente dell'utente `Architettura_esecuzione_sessioni_virtuali.txt`.
Entrambi ancora **non committati**. Nessun file di codice toccato.

## Verdetto sulle due strategie proposte dall'utente
- **Strategia 1 (tick da 1 ms, slot per asset)**: non utilizzabile come motore primario.
  2 h × 10.000 asset = 6,687e10 aggiornamenti → 3,2 h al pavimento assoluto di CPython (loop vuoto),
  **74 giorni** a costo Mesa reale (95,7 µs/agente-step), **3,6-21 anni** se il rilevamento è O(N)
  per asset. Inoltre il passo è dimensionato sul missile ipersonico, che il testo stesso esclude
  dalla simulazione a tick. E nessun simulatore entity-level reale lo fa: JTLS è time-stepped ma
  **aggregato** (btg/brigata, Lanchester); JCATS/BRAWLER/AFSIM/ESAMS sono **event-driven**.
  Incongruenza trovata nel testo: `4,21 / 0,1 = 43` usa un divisore che non è né lo slot (1,08e-7 s)
  né il ciclo (1,08e-3 s).
- **Da salvare della Strategia 1**: RIV/VAL/COM/ATT è l'OODA loop e i suoi ordini di grandezza sono
  corretti (Osa 26 s, S-300P 28 s, Tor 5-8 s, pilota 1-2 s, equipaggio carro ~31 s). Vanno conservate
  come **latenze di reazione schedulate come eventi futuri**, non come conteggi di cicli. Decidono
  **chi spara per primo**, che è proprio ciò la cui assenza fa fallire i modelli a rapporto di forze.
- **Strategia 2 (probabilistica)**: direzione giusta, ma **non dice quando e se due forze si
  incontrano** — è il buco più grave. Va colmato analiticamente (CPA/TCPA + intersezione
  rotta↔volume), non con un tick.

## Architettura decisa: DES con scheduling analitico dei contatti
Tempo in **secondi assoluti**, nessun tick globale. Quattro strati:
0. contratto `SessionOrder`/`SessionOutcome` puro dominio;
1. **scheduler dei contatti** (il pezzo mancante): rotta↔cilindro → intervalli temporali via
   `Route.travelTimeToEdge`; CPA/TCPA `t* = −(Δr·Δv)/|Δv|²` fra mobili; potatura gerarchica a
   livello Block prima delle coppie di asset (è ciò che evita l'O(N²));
2. **risolutore d'ingaggio**: Pd → latenza di reazione (chi spara primo) → ROE → Pk da
   `accuracy × destroy_capacity`; **modello a salva di Hughes** per i molti-contro-molti;
3. applicazione stato per-asset → `SessionOutcome` → `Campaign_State` in una passata.
Micro-passo fine (1-5 s) ammesso **solo dentro una finestra attiva**, mai globale.

## Decisioni dell'utente registrate
1. i 10.000 asset sono solo un **limite superiore teorico**;
2. sessione **riproducibile da seed** — e **l'ordine di risoluzione degli eventi fa parte del
   contratto**, salvare il solo seed non basta;
3. perdite e danni **per singolo asset**;
4. budget di calcolo fino a **minuti**.

## Avvertimento da non dimenticare
Lanchester non si valida su dati storici (9 test falliti, Ardenne/Kursk); la regola 3:1 versione RAND
usata da JICM azzecca solo il **19%** su 98 ingaggi storici — peggio del caso. Ricaduta diretta:
`Logic/Tactical_Evaluation.py:251 calcFightResult` è esattamente un modello a rapporto di forze con
coefficienti tabellati a mano → va tenuto come **fallback aggregato**, mai come risolutore primario.
Se servirà un livello aggregato, i coefficienti vanno stimati con un **ATCAL interno** (far girare il
risolutore fine offline), non inventati.

## FASE 1 — cinematica utilizzabile: FATTA 2026-09-21 (suite 2540 -> 2608 test, OK)
Sblocca precondizioni 1 e 2. Non committata.
- **Schema canonico `Mobile.speed`, tutto in m/s** (`SPEED_SCHEMA` in testa a `Asset/Mobile.py`):
  `{"nominal", "max", "off_road": {...} (solo Vehicle), "reference_altitude" (solo Aircraft)}`.
  Chiave canonica scelta: **`nominal`**, non `cruise` — `cruise` stava solo nel validatore, che
  non era mai stato eseguito con successo; `nominal` e' cio' che usano default, consumatori e test.
- **Fix del default mutabile**: `speed` nella firma di `Mobile.__init__` era un dict condiviso da
  tutte le istanze; ora `None` + `default_speed_profile()` che costruisce un oggetto nuovo.
- **Fix del setter**: non passa piu' da `checkParam` (che Vehicle/Ship/Aircraft sovrascrivono con
  firme senza `speed`) ma da `Mobile._validate_speed`. `checkParam` e' ora `@staticmethod` (le
  mancava `self`) e valida lo schema canonico.
- **Ponte registry -> istanza**: `Mobile.speed_profile_from_registry()` + `load_speed_from_registry()`,
  chiamati dai costruttori di Vehicle/Ship/Aircraft dopo `_model`. Dispatch **sul registry che
  risponde**, non su `isinstance` (piu' robusto e testabile). Conversioni: km/h, mph, nodi -> m/s
  (`Utility.kmh_2_meters_per_second` e `knots_2_meters_per_second`, nuove); per gli aerei IAS->TAS
  via `Utility.true_air_speed` (che restituisce sempre km/h). Ship: `max` = il piu' alto fra `max`
  e `flank`. Aircraft: `max` = il piu' alto fra `combat` ed `emergency`.
- **`Route.positionAtTime(t, speed=None)`**: la funzione posizione(t), interpolazione lineare
  sull'arco in percorrenza; oltre la durata totale restituisce l'ultimo waypoint; `None` se la
  velocita' non e' definita. Nuovo `Test/Test_Route.py` (20 test), che prima non esisteva.
- **`Military._speed_regime`** sostituisce la coppia `_get_nominal_speed`/`_get_max_speed`:
  None -> 0.0, cosi' i confronti `> 0` a valle non esplodono. `time_to_direct_line_attack` e'
  ora in **secondi** (la docstring diceva "hours" ma nessun calcolo convertiva) e funziona:
  verificato end-to-end, 10 km a 12.5 m/s -> 800 s (prima: divisione per zero).
- **Bug collaterale corretto**: `DataType/Route.py` creava il logger senza `.logger`, quindi ogni
  `logger.warning` sollevava AttributeError. Stesso difetto resta in Edge/Waypoint/Volume/Payload/
  Limes/Area/Threat/Event, dove pero' non ci sono call site.
- **Limite trovato, non risolto**: `Edge` costruisce una `Line2D` dalle proiezioni dei waypoint,
  quindi una salita verticale pura (stessa x,y) non e' rappresentabile — sympy rifiuta.

## Precondizioni bloccanti trovate nel codice (verificate riga per riga)
1. **`Asset/Mobile.py:345`**: `checkParam` definita senza `self` → il setter `speed` (`:97-100`)
   solleva sempre `TypeError`. Default mutabile a `:50`. `_speed` mai popolato dai registry.
   **Senza velocità non c'è posizione(t), quindi nessun contatto calcolabile: è IL blocco.**
2. `Block/Military.py:455-467` → `_get_nominal_speed`/`_get_max_speed` danno 0/None →
   `time_to_direct_line_attack` (`:363`) divide per zero.
3. Nessuna API di raggio di rilevamento: i dati radar/TVD esistono per ogni modello
   (`acquisition/tracking/engagement_range` per modo air/ground/sea, in km) ma nessuna classe li espone.
4. `ThreatAA` (`Logic/Air_Route_Manager.py:32`) mai costruito da `Mobile.air_defense_volume()`
   (`Asset/Mobile.py:208`) — è il ponte più economico da costruire.
5. Nessuna `apply_damage`: solo `asset.health = int` (`Asset/Asset.py:207-210`); "Destroyed" già a
   `health ≤ 15` (`DataType/State.py:178-198`).
6. `random` non seedato a livello di modulo (`Tactical_Evaluation.py:360-361`, `Structure.py:128`,
   `Utility.py:320`, DB armi).
7. **Tre modelli Route/Edge/Waypoint incompatibili**; `Air_Route_Manager` (l'unico generatore maturo)
   non produce `DataType.Route`, che è l'unico tipo che l'ecosistema consuma.
8. `DataType/Event.py:81-95` rotto (`self._type` mai assegnato), importato da 8 moduli, nessun test.
9. `Tactical_Evaluation.py:532-579 evaluateGroundRouteDangerLevel` rotta su 3 punti (concetto giusto).
10. **SAM/AAA/EWR hanno combat power ≡ 0** per costruzione (`Context/Context.py:502-507`).
11. `DataType/Threat.py` e `DataType/Volume.py` sono codice morto.

Fondamenta buone già pronte: `Cylinder.innerPoint`/`getIntersection` (404 righe di test),
`Route.travelTimeToEdge`, DB armi con `accuracy × destroy_capacity`, `Combat_Power_Estimation`,
`Tactical_Analysis`, `Military.time2attack`/`combat_range`/`air_defense_volume`.

## Roadmap (7 fasi, nel documento)
0 contratto+RNG → 1 cinematica (sblocca tutto) → 2 percezione → 3 `Logic/Contact_Scheduler.py` →
4 `Logic/Engagement_Resolver.py` + `Context/Reaction_Profile.py` → 5 danno per-asset →
6 `Logic/Session_Simulator.py` → 7 validazione + **test di agnosticismo**.

**How to apply:** qualunque lavoro sul motore di sessione parte da questo documento, non dal `.txt`
sorgente. Le Fasi 1 e 2 sono correzioni a codice esistente e vanno fatte per prime: senza di esse lo
Strato 1 non è scrivibile. V. [[project_c2_hierarchy_design]] per `Command/` e
[[feedback_core_simulator_agnostic]] per il vincolo che questo motore serve.
