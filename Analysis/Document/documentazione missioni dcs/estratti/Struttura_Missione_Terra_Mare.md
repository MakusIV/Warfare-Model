# Missione di prova terra/mare (`ground_sea_mission.miz`)

Missione creata dall'utente nel Mission Editor (2026-10-05). Serve a verificare come DCS assegna
compiti e bersagli ai gruppi **terrestri** e **navali**: carri e artiglieria per i veicoli; bersagli
terrestri e navali per le navi. Analizzata caricando `mission` con `lupa` e percorrendo le tabelle.
Tutti i numeri sono **misurati sul file**; le interpretazioni non verificate sono marcate **[I]**.

Riferimento per il formato generale del `.miz`: `Struttura_File_MIZ.md` (missione DCE). Le
differenze di formato sono in §6.

---

## 1. Contenuto

| Voce | Valore |
|---|---|
| file nello zip | `mission` (50 KB), `options`, `warehouses`, `theatre` (= `Caucasus`), `l10n/DEFAULT/dictionary`, `mapResource` |
| `version` | 23 |
| data, ora di inizio | 21/6/2016, `start_time` = 28800 s (08:00) |
| moduli richiesti | `WWII Armour and Technics` (per l'oggetto `Sandbox`) |
| trigger, obiettivi, zone | **nessuno**: tutto il comportamento sta nelle rotte e nei task ai waypoint |
| meteo | 20 °C, QNH 760 mmHg, nubi `Preset2` base 2500 m, visibilità 80 km, vento nullo |

## 2. Gruppi

| Gruppo | Lato | Cat. | Unità | WP | Rotta | Velocità | Arrivo ultimo WP |
|---|---|---|---|---:|---|---|---|
| Ground-1 | blu | vehicle | LAV-25, 2× M-2 Bradley, M1130, 3× M-1 Abrams | 4 | 11,5 km, **On Road** | 20 km/h | 2095 s |
| Ground-5 | blu | vehicle | 3× M2A1-105 (obice trainato) | 3 | 5,3 km, Off Road | 3,6 km/h | 5302 s |
| Naval-1 | blu | ship | 3× USS Arleigh Burke IIa | 4 | 31,6 km | 50 km/h | 2273 s |
| Ground-2 | rosso | vehicle | 4× T-90M | 4 | 9,2 km, Off Road | 20 km/h | 1650 s |
| Ground-3 | rosso | vehicle | 5× SAU Akatsia (2S3, semovente) | 3 | 4,3 km, Off Road | 20 km/h | 779 s |
| Ground-4 | rosso | vehicle | 1× Sandbox (postazione fissa) | 1 | — | — | — |
| Naval-2 | rosso | ship | 4× REZKY | 3 | 19,0 km | 50 km/h | 1368 s |

Tutti i gruppi hanno `start_time = 0`, `lateActivation` assente e skill `Average`. Il campo `task` di
gruppo è `Ground Nothing` per i veicoli e assente per le navi: anche qui **non porta significato**.

## 3. Compiti ai waypoint (il dato che interessava)

| Gruppo | WP | Istante | Azioni in ordine | Bersaglio | Distanza di tiro |
|---|---|---|---|---|---|
| Ground-1 (carri blu) | 3 | 2095 s | 1. `FireAtPoint`, 2. `Hold` | punto a **77 m** dal `Sandbox` rosso | 4,27 km |
| Ground-5 (artiglieria blu) | 2 | 5302 s | `FireAtPoint` | punto a 255 m dal `Sandbox` rosso | 9,91 km |
| Ground-2 (carri rossi) | 3 | 1650 s | 1. `Hold`, 2. **`AttackGroup` → Ground-1** | gruppo di carri blu | 2,44 km dal bersaglio in quell'istante |
| Ground-3 (artiglieria rossa) | 2 | 779 s | `FireAtPoint` | punto dove **stavano** i blu all'inizio (566 m dal WP0 di Ground-1, 880 m da quello di Ground-5) | 14,11 km |
| Naval-1 (navi blu) | 3 | 2273 s | `FireAtPoint` | punto a terra, a più di 21 km da ogni unità rossa (bersaglio fisso) | 8,00 km |
| Naval-2 (navi rosse) | 2 | 1368 s | **`AttackGroup` → Naval-1** | gruppo navale blu | 4,51 km dal bersaglio in quell'istante |

**Conferme rispetto al manuale del 2020** (che per i veicoli non documentava un task di attacco a
un gruppo):

1. **I veicoli possono ricevere un gruppo bersaglio** (`AttackGroup`): la supposizione dell'utente
   era corretta.
2. **Le navi attaccano sia bersagli navali** (`AttackGroup` su un gruppo navale) **sia bersagli a
   terra** (`FireAtPoint` su un punto).
3. **Anche i carri usano `FireAtPoint`** (tiro su un punto, qui su una postazione), non solo
   l'artiglieria.

Osservazione sull'artiglieria rossa: spara a 779 s sul punto dove i blu erano all'inizio. In
quell'istante Ground-5 ne è a 1,45 km e Ground-1 a 4,57 km. Un `FireAtPoint` è un bersaglio
**di posizione, fissato in pianificazione**: se il bersaglio si muove, il colpo cade dove era.
`AttackGroup` invece insegue il gruppo.

## 4. Schema dei task

### 4.1 `FireAtPoint` (veicoli e navi)

| Chiave | Valori osservati | Significato |
|---|---|---|
| `x`, `y` | m | punto bersaglio (x verso nord, y verso est) |
| `zoneRadius` | 0 | raggio dell'area di tiro in m (0 = sul punto) [M parte 4] |
| `expendQtyEnabled`, `expendQty` | false, 1 | limite al numero di colpi ("Rounds expend"); disattivato = nessun limite [M parte 4] |
| `weaponType` | 52613349374 (veicoli), 805339120 (navi) | maschera di bit delle armi ammesse; i valori differiscono per categoria. Non decodificata: probabilmente il default "Auto" [I] |
| `alt_type` | 1 | riferimento di quota del punto [I] |
| `counterbattaryRadius` | 0 | **non presente nel manuale del 2020**: raggio per il tiro di controbatteria [I] |
| `templateId` | `''` | template di schieramento (vuoto) |

### 4.2 `AttackGroup` (veicoli e navi)

| Chiave | Valori osservati | Significato |
|---|---|---|
| `groupId` | 1 (Ground-1), 7 (Naval-1) | gruppo bersaglio |
| `weaponType` | 52613349374 (veicoli), 56908316670 (navi) | come sopra |
| `expend` | `Auto` | quantità per passaggio (come l'aereo) |
| `attackQtyLimit`, `attackQty` | false, 1 | numero massimo di attacchi |
| `groupAttack` | false | tutto il gruppo sullo stesso bersaglio |
| `directionEnabled`, `direction` | false, 0 | direzione d'attacco |
| `altitudeEnabled`, `altitude` | false, quota del WP | quota d'attacco (senza effetto per veicoli e navi [I]) |
| `counterbattaryRadius` | 0 (solo veicoli) | v. sopra |

`AttackGroup` ha per veicoli e navi **gli stessi parametri del task aereo**. Il modello di dominio
può quindi usare un unico compito "attacca gruppo" per tutti e tre i domini, con parametri non
pertinenti ignorati.

### 4.3 Altri elementi

- `Hold` (veicoli): sospende il movimento. Nel gruppo blu viene **dopo** il tiro, nel gruppo rosso
  **prima** dell'attacco. L'ordine delle azioni al waypoint è significativo.
- `EPLRS` (Ground-2, WP0, `auto = true`): azione automatica di datalink inserita dall'editor.
- Campo `tasks` di gruppo (Ground-2: `Hold`): è la lista delle azioni attivabili da trigger
  (Triggered Actions). Qui nessun trigger la usa.

## 5. Rotte

- **Ogni waypoint ha un `ETA` calcolato**. Solo il WP0 ha `ETA_locked = true` (istante di partenza);
  tutti hanno `speed_locked = true`: velocità imposte, tempi derivati.
- `speed` in m/s per tratto (5,56 = 20 km/h; 13,89 = 50 km/h; 1 = 3,6 km/h). Il WP0 ha velocità 0.
- `alt` dei waypoint terrestri = quota del terreno (5-37 m, `BARO`); per le navi 0.
- `action`: `Off Road`/`On Road` per i veicoli (Ground-1 è l'unico su strada dal WP1), `Turning
  Point` per le navi; `type` sempre `Turning Point`.
- Il tiro avviene **all'arrivo al waypoint** che porta l'azione: il waypoint fa da **posizione di
  tiro** e l'ETA da **istante di inizio** del compito.

## 6. Differenze di formato rispetto alla missione DCE

| Punto | DCE (`Struttura_File_MIZ.md`) | Questa missione |
|---|---|---|
| `version` | 19 | 23 |
| voce `theatre` nello zip | assente | **presente** (`Caucasus`) |
| unità veicolo | — | campi `playerCanDrive`, `coldAtStart` |
| frequenza nave | — | `frequency` = 127500000 (Hz), `modulation` = 0 (AM) |
| task terrestri | solo `Ground Nothing` con 1 waypoint | rotte a 3-4 punti, `FireAtPoint`, `AttackGroup`, `Hold` |

## 7. Rilevanza per Warfare-Model (livello di dominio)

1. **Bersaglio esplicito anche per terra e mare.** La missione terrestre e quella navale devono poter
   portare un bersaglio, come quella aerea. I tipi di bersaglio sono gli stessi nei tre domini:
   - **gruppo/asset** (bersaglio mobile, inseguito);
   - **punto o area** (bersaglio di posizione, con raggio).
2. **Un bersaglio di posizione invecchia.** Il punto è fissato in pianificazione con l'informazione
   disponibile in quel momento, e l'artiglieria rossa colpisce dove i blu *erano*. È coerente con la
   nebbia di guerra (C): la missione deve registrare **su quale conoscenza** è stato scelto il
   bersaglio (asset osservato o posizione stimata, con istante).
3. **Posizione di tiro e istante di tiro sono dati della missione.** Il compito è legato a un
   waypoint: la posizione è quella del waypoint, l'istante è la sua ETA. Per il fuoco indiretto è
   l'analogo dell'`AttackProfile` aereo. Va verificata la fattibilità contro la gittata dell'arma
   (qui 14,1 km per il 2S3, 9,9 km per l'M2A1-105) [gittate da verificare sui registri d'arma].
4. **Sequenze di azioni.** "Tira e poi fermati", "fermati e poi attacca": l'ordine è un dato.
5. **Quantità di colpi** (con limite opzionale) e **raggio dell'area**: parametri del fuoco
   indiretto da tenere nel dominio. Si collegano a `Weapon_Stores` (consumo) e alla dispersione.
6. **Il tipo di missione resta assente in DCS** per terra e mare (`Ground Nothing`). Nel nostro
   modello va dichiarato: Attack/Defense/Maintain/Retrait più eventuali compiti specifici, come il
   fuoco di supporto.
