# Proposta: volumi distinti di rilevamento e di intercettazione per la pianificazione di rotta

**Stato**: ANALISI E PROPOSTA (2026-09-26), in attesa delle decisioni dell'utente (§9). Nessun file di
codice modificato, nessun test scritto. Due script di prova in sola lettura sono stati eseguiti fuori dal
repository, nella scratchpad di sessione (§7).
**Oggetto**: il requisito dell'utente di separare il volume in cui un aereo può essere **RILEVATO**
(sensore di scoperta, dedicato o sottosistema di un SAM, eventualmente in rete) dal volume in cui può
essere **INTERCETTATO** (l'intercettore parte solo quando la guida può ingaggiare), e l'uso dei due volumi
nelle tre modalità del pianificatore di rotta aereo: aggirare, attraversare senza essere intercettati,
attraversare senza essere rilevati.
**Base**: `Proposta_Munizioni_Compatibili_e_Rotte_Attacco.md` (Proposta B), il fix non committato di
`ThreatAA.calcMaxLenghtCrossSegment` e delle minacce terminali (`git diff`, stessa sessione),
`Piano_Lavori_2026_09_24.md` §"Attività D" (volumi generici, già accettata dall'utente).
**Convenzione**: **[V]** = VERIFICATO leggendo il codice (con `file:riga`) o eseguendolo;
**[I]** = IPOTESI o conoscenza generale non verificata nel repository.
Percorsi di codice relativi a `Code/Dynamic_War_Manager/Source/`. Le righe di
`Logic/Air_Route_Manager.py` sono quelle della copia di lavoro **con** il fix non committato.

---

## 0. Sintesi e raccomandazioni

| Domanda | Verdetto | In una riga |
|---|---|---|
| (a) Un solo volume per asset AD, d'intercettazione? | **Sì** [V] | `ThreatAA` è costruito solo dal cilindro delle **armi** (`Mobile.air_defense_volume`). Nessun sensore vi entra. |
| (b) Nei registri manca il dato del sensore di scoperta? | **No, c'è: premessa da correggere** [V] | Ogni record ha `radar`/`TVD` con `acquisition_range` (scoperta) distinta da `tracking_range`/`engagement_range` (guida). `Mobile.detection_range()` lo espone già. Il pianificatore di rotta non lo legge. |
| (c) Esiste un sensore di rete (EWR) che rileva senza intercettare? | **No** [V] | Nessun record EWR nei registri. Nessun meccanismo di passaggio del dato fra siti, né nel pianificatore né nel DES. La nebbia di guerra è un'altra cosa. |
| Il DES distingue già rilevamento e ingaggio? | **Sì, con due sfere** [V] | Rileva con la portata del sensore (`_detect`), spara con la portata dell'arma (`_range_entry`). Quello indietro è il **pianificatore**, non il motore. |
| Il fix appena scritto resta valido? | **Sì, come modello d'intercettazione** [V] | Resta corretto. Diventa il caso "sito già pronto all'ingresso", con un parametro di ritardo opzionale e docstring rivista (§6). |
| Proposta B va aggiornata? | **Sì, subito, nella firma** [V] | La sua `effective_seconds` contraddice l'ipotesi del fix: i due documenti della stessa sessione fanno partire il cronometro in punti diversi (§4). |

**Raccomandazione principale.** Non creare un secondo sistema di volumi per il pianificatore. La proposta
è l'**anticipo della Attività D** (volumi di rilevamento e ingaggio per asset e per arma, già accettata il
2026-09-24) sul lato pianificatore, in tre passi:
1. **Due tipi di minaccia con una base comune** (`AirThreat`):
   - `ThreatAA` resta il tipo d'**intercettazione**, senza cambiare comportamento;
   - nuovo `DetectionThreat`, costruito da `Mobile.detection_range('air')`;
   - entrambi portano un `source_id` che lega i due volumi dello stesso sito.
2. **Il pianificatore riceve due liste e una modalità esplicita** (`AVOID`, `CROSS_UNINTERCEPTED`,
   `AVOID_DETECTION`). `intersecate_threat` resta come alias retrocompatibile.
3. **L'orizzonte radar** è il pezzo che produce l'effetto fisico richiesto: rilevamento difficile in
   quota, più facile da evitare a bassa quota. Entra come raggio di rilevamento che dipende dalla quota
   del bersaglio. Nel primo passo è un cilindro costruito **alla quota di rotta**; con D diventa un solido
   di rotazione vero.

Resta **fuori perimetro** la rete di sensori, cioè un EWR che passa la traccia a un SAM lontano: dipende
dalla gerarchia C2 ancora da decidere. Qui si predispone solo il punto d'aggancio (§2.6).
**Dentro perimetro**, invece, il sito sensore puro. Il sensore senza armi ottiene il suo
`DetectionThreat` senza codice dedicato, perché la fabbrica lo costruisce da `detection_range`
(§2.6 livello 1). Mancano però i dati: oggi nel registro non c'è nessun EWR.

**"Attraversare senza essere rilevati" non ha un equivalente di `calcMaxLenghtCrossSegment`** con i dati
attuali. La legge di rilevamento del DES dipende solo dalla distanza, non dal tempo di permanenza. Vale
0,5 già sul bordo del volume, quindi qualunque ingresso comporta Pd ≥ 0,5 (§3.3). La modalità si
implementa quindi come **aggiramento dei volumi di rilevamento**, più una metrica di rischio. La corda
massima "non rilevata" richiede un dato nuovo, il tempo di permanenza del sensore. È una decisione
separata (D-5).

---

## 1. Verifica: cosa esiste e cosa manca

### 1.1 (a) Un solo volume per asset AD, d'intercettazione nella sostanza [V]

- **Solo armi.** `Mobile.air_defense_volume()` (`Asset/Mobile.py:1276-1346`) legge solo le armi AD del
  record:
  - veicoli: `AA_CANNONS`/`MISSILES` con quote e task `Anti_Air` (`:1300-1322`);
  - navi: `MISSILES_SAM` (`:1301-1304`);
  - raggio = massima `range.direct` (`:1328-1331`), base = z sito + `min_altitude` minima, altezza fino
    alla `max_altitude` massima (`:1340-1346`).

  Il docstring dice *"engagement envelope"* (`:1277`). **Nessun campo `radar`/`TVD` viene letto.**
- **La fabbrica avvolge quel cilindro.** `build_threat_aa` (`Logic/Air_Route_Manager.py:393-441`) ci
  aggiunge:
  - `interception_speed`: la velocità massima fra le armi AD (`_air_defense_weapons`, `:287-360`);
  - `min_detection_time`/`min_fire_time` (`threat_reaction_times`, `:363-390`);
  - `danger_level` (`:432-435`).

  Un asset produce **un** `ThreatAA`, oppure `None` se non ha armi AD (`:350-352`, `:416-419`).
- **Il blocco raccoglie solo quelli.** `Military.air_defense_threats()` (`Block/Military.py:551-577`)
  prende un `ThreatAA` per ogni Vehicle/Ship operativo con armi AD. `Military.air_defense_power()`
  (`:579-616`) aggrega i loro `danger_level`.

Il nome generico `ThreatAA` e il campo `min_detection_time` fanno pensare che il tipo rappresenti anche il
rilevamento. Non è così: **la geometria è solo quella dell'arma**, e `min_detection_time` è una
**latenza**, non un volume (§1.4).

### 1.2 (b) Dati del sensore nei registri: **esistono** [V]. La premessa va corretta

I sensori non stanno in `Ground_Weapon_Data.py`/`Ship_Weapon_Data.py`, che hanno solo il campo `guide`
(tipo di guida: `IR`, `SARH`, `Radio_Command`, `SACLOS`, `Active_Radar`, per esempio
`Asset/Ground_Weapon_Data.py:2683-2697`). Stanno nei record del **mezzo**:

```python
record.radar['capabilities']['air'] = (True, {'tracking_range': km, 'acquisition_range': km,
                                              'engagement_range': km, 'multi_target_capacity': n})
```

La forma è documentata in `Asset/Mobile.py:58-85`. Esempio: SA-6, `Asset/Vehicle_Data.py:4381-4389`,
radar 1S91 Straight Flush con `acquisition_range 75`, `tracking_range 28`, `engagement_range 28`.
È esattamente la distinzione dell'utente:
- `acquisition_range` = **scoperta**;
- `tracking_range`/`engagement_range` = **guida**.

Lo stesso dizionario radar la esprime anche per i sistemi con radar di scoperta e di tiro distinti,
fusi in un solo record (Tunguska `'1RL144 Search + 1A26 Track'`: 18 / 13 / 10 km).

**Il ponte esiste già**:
- `Mobile.detection_range(mode, sensor, range_type)` (`Asset/Mobile.py:1451-1527`) restituisce la portata
  in metri, di default `acquisition_range`, massima fra radar e TVD;
- `Military.detection_range` (`Block/Military.py:719-749`) la aggrega per blocco;
- oggi la consumano il DES (`Contact_Scheduler.mutual_detection_ranges`, `Logic/Contact_Scheduler.py:851-886`)
  e la potatura dei blocchi (`block_reach`, `:1044-1085`);
- **nessuno la collega a `air_defense_volume` né ad `Air_Route_Manager`**.

Confronto misurato su tutti i record AD dei registri (E-1, §7). Portate in km, modo `air`:

| Sistema | Arma (portata, guida) | Scoperta (`acquisition`) | Guida (`engagement`) |
|---|---|---|---|
| 2K12-Kub (SA-6) | 3M9 24, SARH | 75 | 28 |
| 9K37-Buk (SA-11) | 9M38 35, SARH | 85 | 45 |
| S-300PS (SA-10) | 5V55R 75, SARH | 150 (30N6 Flap Lid) | 90 |
| 9A33-Osa / 9K331-Tor | 10 / 12, comando | 30 / 25 | 15 / 15 |
| Strela-1, Strela-10, Chaparral, Linebacker | 4,2-9, IR | solo TVD 8-12 | — |
| ZSU-23-4 / Gepard | cannone 2,5 / 4 | 20 / 15 | 8 / 12 |
| **ZSU-57-2, M163-VADS** | cannone 4 / 1,2 | **nessun sensore** (`radar: False`, `TVD: False`) | — |
| 22 navi con SAM | 12-240 | 130-550 | 60-350; **`None` per 9 navi: 6 CVN, Forrestal, Tarawa, Type 071** |

Conseguenze verificate:
- **Scoperta ≥ arma in tutti i sistemi dotati di sensore.** L'ipotesi del fix ("portata radar > portata
  arma", `Logic/Air_Route_Manager.py:88-89`) è quindi **vera sui dati, ma solo in quota**. A bassa quota
  la smentisce l'orizzonte radar (§2.5), che nessun codice modella.
- **Guida ≥ arma ovunque sia dichiarata** (uguale per il Type 052C, 200/200). L'intersezione "arma ∩ guida"
  richiesta dall'utente ("l'intercettore parte solo quando la guida può ingaggiare") oggi **coincide
  numericamente con il solo volume dell'arma**. Introdurla non cambia alcun risultato attuale, ma rende
  corretto il modello quando entreranno dati diversi.
- **Mancano**:
  - la fascia di quota del **sensore** (copertura min/max): esiste solo quella delle armi;
  - l'altezza d'antenna, necessaria per l'orizzonte radar;
  - qualunque tempo di permanenza, periodo di scansione o Pd del sensore;
  - i sensori di 2 AAA e la guida di 9 navi.
- **Record monolitici.** Un record `Vehicle_Data` è un **sistema intero**: il radar del record S-300PS è
  il 30N6 di tiro, senza il 64N6 di scoperta. La tassonomia `Context.AIR_DEFENSE_ASSET`
  (`Context/Context.py:749-775`) prevede invece componenti di sito separati: `Search_Radar`,
  `Track_Radar`, `Search_&_Track_Radar`, `Launcher`, `Command_&_Control`. Anche la tabella SAM ingerita li
  separa: colonne `search_radar_1/2`, `track_radar`, `site_layout` "6L + TR + C2 + SR"
  (`Analysis/Document/documentazione_dcs/estratti/sam_threat_table.csv`). Registro per sistema e tassonomia
  per componente **non sono allineati**. Per questa proposta basta il livello sistema (§2.3); il livello
  componente riguarda la gerarchia militare e il SEAD (§2.6).

### 1.3 (c) Sensore di rete / EWR: **assente** [V]. Nebbia di guerra: **sistema distinto**

- **Nessun record EWR.** Nei 64 `Vehicle_Data(**...)` registrati, la ricerca di `'category': 'EWR'` non
  trova nulla. La categoria esiste solo in `Context` (`Context/Context.py:479`, `:776-782`) e in
  `Vehicle.isEWR` (`Asset/Vehicle.py:298-299`).
- **Un EWR non produrrebbe comunque minacce.** Senza armi AD, `air_defense_volume` restituisce `None`
  (`Asset/Mobile.py:1336-1338`) e così `_air_defense_weapons` (`Logic/Air_Route_Manager.py:350-352`).
  L'EWR sparisce dalla pianificazione di rotta.
- **Il modello del sensore puro esiste già, per gli AWACS.** E-3A e A-50 dichiarano
  `engagement_range: 0` (`Asset/Aircraft_Data.py:3314`, e il record E-3A da `:2061`), che
  `_sensor_range_km` tratta come "nessuna guida" (`Asset/Mobile.py:1447-1449`). È il modello dati di un
  sensore che rileva senza guidare: un EWR terrestre si descrive **con la stessa forma**, senza campi
  nuovi.
- **Nessun passaggio del dato fra siti.** Nel DES ogni osservatore rileva con la **propria** portata
  (`_detect_direction`, `Logic/Engagement_Resolver.py:1231-1261`, `own_range`). Il candidato al tiro
  nasce solo per l'osservatore stesso (`self.candidates.setdefault(observer.id, ...)`, `:1253`). Un EWR
  nel DES rileva e registra un `Detection`, ma non abilita nessun tiratore.
- **La nebbia di guerra è un meccanismo diverso.**
  - `Military.get_recon_efficiency` (`Block/Military.py:498-512`) è la mediana di `efficiency` degli asset
    con ruolo `Reconnaissance`.
  - `recon_detection_factor_fn` / `region_recon_detection_factor`
    (`Logic/Engagement_Resolver.py:687-724`, `:837-881`) moltiplicano la **Pd** del DES per i bersagli dei
    blocchi non visti in un'**istantanea di ricognizione presa prima della sessione**.

  È conoscenza **strategica pregressa**, a livello di schieramento, senza geometria e senza tempo. Il
  rilevamento di questa proposta è invece **fisico e istantaneo**: un sensore, un volume, una rotta. Non
  devono convergere nella stessa funzione. Si **compongono**: nel DES il fattore di ricognizione continua a
  modulare la Pd dentro il volume di rilevamento (`combine_detection_factors`, `:727-761`). Nel
  pianificatore potrà in futuro decidere **quali** minacce di rilevamento il pianificatore conosce, perché
  si pianifica solo contro i siti noti. Questo è fuori perimetro [I].

### 1.4 Incongruenze trovate [V]

1. **Il DES ha due volumi, il pianificatore uno.**
   - DES: rilevamento = sfera di raggio `detection_range` (`_detect`, `Logic/Engagement_Resolver.py:1210-1261`);
     tiro = sfera di raggio `max_range` dell'arma (`_range_entry`, `:1455-1488`), dopo `t_ready = t_detect +
     profilo.total` (`:1250`).
   - Pianificatore: un solo cilindro d'arma.

   Lo **stesso sito** ha quindi due geometrie diverse:
   - nel pianificatore, un cilindro con fascia di quota;
   - nel DES, sfere senza fascia.

   La Attività D nasce per unificarle (`Engagement_Resolver.py:992-1001`).
2. **`min_detection_time` non è un tempo di rilevamento.** Viene da `acquire_time` della tabella SAM,
   descritto come *"latenza di reazione — quanto tempo serve al sistema per ingaggiare"*
   (`documentazione_dcs/estratti/README.md:29`). Il DES lo usa come RIV, cioè latenza **dopo** il contatto
   (`Context/Reaction_Profile.py:239-257`). È il tempo di **acquisizione**, dall'istante del contatto alla
   traccia utile. Usarlo come "tempo di permanenza prima di essere visti" sarebbe un abuso semantico (§3.3).
3. **La Proposta B e il fix fanno partire il cronometro in punti diversi** (dettaglio §4):
   - B: rilevamento all'ingresso nel volume d'arma;
   - fix: rilevamento prima dell'ingresso.

---

## 2. Progetto della distinzione a due volumi

### 2.1 Definizioni

- **Volume di rilevamento** V_R(s): dove il sensore s vede un bersaglio aereo. Raggio orizzontale
  `r_R(z) = min(acquisition_range, orizzonte_radar(h_antenna, z))` per i radar, `acquisition_range` del TVD
  per gli ottici/IR. Fascia di quota del sensore (dato mancante, §2.2).
- **Volume d'intercettazione** V_I(a, g): dove l'arma a, **guidata da g**, può essere lanciata con
  successo. Raggio = `min(range.direct dell'arma, engagement_range della guida)`, fascia = quote dell'arma.
  La guida g dipende dal campo `guide` dell'arma:
  - `SARH`/`Radio_Command`/`SACLOS`: radar o ottica di tiro del sistema, cioè `engagement_range`;
  - `IR`: autoguida dell'arma, quindi il limite è l'arma stessa;
  - `Active_Radar`: autoguida terminale, quindi arma.

  [I per la regola di guida; V che i dati esistono.]
- **Prontezza del sito**: istante in cui il sito può lanciare,
  `t_ready = t_contatto + acquisition_time` (l'attuale `min_detection_time`), dove `t_contatto` è l'ingresso
  in V_R del sensore **proprio**, o in futuro di un sensore di rete (§2.6).
  **Lancio** = `max(t_ingresso in V_I, t_ready) + min_fire_time`.

  È **la stessa regola del DES** (`t_ready = time + profile.total`, `Logic/Engagement_Resolver.py:1250`,
  poi `_range_entry`). Il pianificatore e l'esecutore virtuale hanno così una sola fisica, come già
  raccomandato per la balistica in Proposta B §2.5.

### 2.2 Dati: presenti, derivabili, mancanti

| Grandezza | Stato | Fonte / proposta |
|---|---|---|
| Portata di scoperta | **presente** [V] | `acquisition_range` via `Mobile.detection_range('air')` |
| Portata di guida | **presente** [V] per tutti i sistemi terrestri guidati da radar; **assente** per 9 navi | `engagement_range`; se `None` → portata dell'arma |
| Tipo di guida dell'arma | **presente** [V] | `guide` in `Ground_Weapon_Data`; `guidance`/`guide` navali da verificare arma per arma |
| Latenza di acquisizione e di lancio | **presente come stima** [V] | `SAM_REACTION_TABLE`, `LAUNCH_SEQUENCE_TIME_S` (`Logic/Air_Route_Manager.py:191-242`) |
| Altezza d'antenna | **mancante** | default dichiarati per classe [I]: ~5 m radar su veicolo, ~20 m radar su palo/EWR, ~20-40 m nave; poi dato di registro opzionale `radar['antenna_height']` |
| Fascia di quota del sensore | **mancante** | default: 0 → tetto di riferimento (`DANGER_LEVEL_REFERENCE_CEILING_M`, 25 km); il limite basso lo fa l'orizzonte |
| Tempo di permanenza / periodo di scansione | **mancante** | serve solo per l'attraversamento "non rilevato" a corda limitata (D-5) |
| Sensori di ZSU-57-2 e M163 | **mancanti** | ripiego visivo dichiarato, come fanno le fixture di test (`Test/Scenario_Fixtures.py:189-246`), oppure ricerca dati |
| Record EWR (1L13, 55Zh6, P-19, P-37, …) | **mancanti** | ricerca dati; forma identica agli AWACS (`engagement_range: 0`) |

### 2.3 Tipi proposti (disegno, non implementazione)

```python
class AirThreat:                       # base comune: cio' che il pianificatore usa oggi di ThreatAA
    volume                             # oggi un Cylinder; con D l'interfaccia volume (§5)
    cylinder                           # alias di volume finche' esiste solo Cylinder (Contact_Scheduler._cylinder_of lo legge)
    min_altitude: float; max_altitude: float
    danger_level: float                # 0.0 per il puro rilevamento (§3.5)
    source_id: str | None              # asset che la genera: lega V_R e V_I dello stesso sito
    def innerPoint(p) -> bool; def edgeIntersect(edge) -> (bool, Segment3D | None)

class ThreatAA(AirThreat):             # INTERCETTAZIONE: la classe di oggi, stesso costruttore
    interception_speed; min_fire_time
    min_detection_time                 # = acquisition_time (latenza), nome da rivedere (D-6)
    def calcMaxLenghtCrossSegment(v_a, h, t_inv, ready_delay_s=0.0)   # §6

class DetectionThreat(AirThreat):      # RILEVAMENTO: nuova
    sensor: str                        # 'radar' | 'TVD'
    acquisition_range: float           # portata nominale, prima dell'orizzonte
    reference_altitude: float          # quota alla quale e' stato calcolato il raggio (§2.5)
```

**Fabbrica.** `build_air_defense_threats(asset, route_altitude) -> (DetectionThreat | None, ThreatAA | None)`
accanto a `build_threat_aa`, che resta invariata.
- La parte di rilevamento usa `asset.detection_range('air')`.
- Se il raggio di guida è minore di quello d'arma, la parte d'intercettazione applica `min(arma, guida)` al
  cilindro. Con i dati di oggi il caso non si presenta (§1.2).

**Blocco.**
- Nuovo `Military.air_detection_threats(route_altitude)` accanto ad `air_defense_threats()`, che resta
  invariato.
- `air_defense_power()` deve continuare a leggere **solo** le minacce d'intercettazione: un EWR non è
  potenza di fuoco antiaerea.

**Perché non basta un campo `kind` su `ThreatAA`.** I due tipi hanno parametri disgiunti:
- l'intercettazione ha velocità dell'intercettore e sequenza di lancio;
- il rilevamento ha sensore, portata nominale e quota di riferimento.

Inoltre `excludeThreat` controlla già il tipo (`isinstance(threat, ThreatAA)`,
`Logic/Air_Route_Manager.py:945-946`): con una base comune il controllo passa ad `AirThreat` e il
pianificatore resta tipizzato.

**Esempio SA-6** (una batteria 2K12-Kub a quota 0, bersaglio a 250 m/s):
- V_R: raggio `min(75 km, orizzonte(5 m, z))`; a 30 m di quota ≈ 31,8 km, da ~300 m in su 75 km;
- V_I: raggio `min(24, 28) = 24 km`, fascia 100-14 000 m (dall'arma 3M9);
- a 50 m di quota l'aereo è **sotto** V_I, dove non può essere intercettato, ma **dentro** V_R, entro
  ~38 km: è visto e non colpito. È il caso che oggi il pianificatore non sa rappresentare.

### 2.4 Numeri: cosa cambia quando i volumi sono due (E-2, §7)

Corda massima attraversabile, formula del fix, aereo a 250 m/s, inversione 10 s, antenna 5 m [I]:

| Sito | Quota | Raggio di rilevamento | Ritardo di prontezza | Corda oggi | Corda a due volumi |
|---|---|---|---|---|---|
| S-300PS (75 km) | 30 m | 31,8 km | 175,9 s | **8,0 km** | **46,3 km** |
| S-300PS | 100 m | 50,4 km | 101,3 s | 8,0 km | 30,1 km |
| S-300PS | 1000 m | 139,5 km | 0 | 8,0 km | 8,0 km |
| 2K12-Kub (24 km) | 30 m | 31,8 km | 0 | 5,4 km | 5,4 km |

Letture:
- a media quota i due modelli coincidono: il fix resta esatto;
- a bassa quota contro un SAM a lungo raggio il fix è **molto conservativo**, perché ipotizza di vedere un
  aereo che l'orizzonte nasconde;
- l'antenna di 5 m è una scelta di test: il vero S-300 usa il 76N6 su palo proprio per questo, e il
  registro non lo contiene [I].

### 2.5 L'orizzonte radar: il pezzo che produce l'effetto richiesto

Formula standard, terra con raggio 4/3 [I, conoscenza generale]:
`d_km ≈ 4,12 · (√h_antenna_m + √h_bersaglio_m)`.

| Quota bersaglio | Antenna 5 m | Antenna 20 m |
|---|---|---|
| 30 m | 31,8 km | 41,0 km |
| 100 m | 50,4 km | 59,6 km |
| 1000 m | 139,5 km | 148,7 km |
| 5000 m | 300,5 km | 309,8 km |

**Guerra Fredda.** Un EWR da 300 km vede un aereo a 5000 m su tutta la portata, e a 30 m solo entro
~41 km. È esattamente il "molto difficile a quote medio-alte, più facile a bassa quota" dell'utente.
**WWII.** Stessa fisica, con portate nominali minori e sensori ottici/visivi (TVD) che dipendono da
meteo e luce. Il fattore meteo esiste già nel DES (`weather_detection_factor`,
`Logic/Engagement_Resolver.py:583-631`), il pianificatore non lo usa ancora [V].

**Forma geometrica.** V_R di un radar **non è un cilindro**: è un solido di rotazione il cui raggio cresce
con la quota, `r(z) = min(R_acq, d(h_a, z))`. Nel pianificatore attuale però una chiamata a `calcRoute`
vola a **quota costante** (`aircraft_altitude_route`), salvo `change_up`/`change_down`. Primo passo
compatibile con il solo `Cylinder`:
- costruire V_R **alla quota di rotta**: raggio `r(z_rotta)`, fascia `[0, tetto]`;
- registrare `reference_altitude` sulla minaccia;
- nelle modalità che usano V_R, **vietare il cambio di quota** o ricostruire V_R alla nuova quota.

Il solido vero arriva con D (§5). Mascheramento del terreno: **fuori perimetro**. Il core non ha un
modello del terreno [V: nessun riferimento in `Logic/`, `Utility/`, `DataType/`].

### 2.6 Il sito EWR puro: quanto è grande, e dove sta il confine

Tre livelli, di costo crescente:

| Livello | Contenuto | Perimetro |
|---|---|---|
| 1. Sensore puro come `DetectionThreat` | Ogni asset con `detection_range('air')` e senza armi AD produce solo V_R. La fabbrica lo fa già se parte da `detection_range` e non dalle armi. Nessun codice dedicato all'EWR. | **Dentro** |
| 2. Dati EWR | Record `Vehicle_Data` per 1L13 / 55Zh6 / P-19 / P-37 (e Chain Home / Freya per WWII), stessa forma degli AWACS (`engagement_range: 0`). Ricerca dati con prompt dedicato. | **Dentro, come dati**: decisione D-4 |
| 3. Rete di sensori (cueing) | Un contatto di un sensore di rete rende pronto un SAM lontano dopo una latenza di collegamento: `t_ready = min(proprio, rete + latenza) + acquisizione`. Richiede: chi è collegato a chi (C2 del lato, `communication_range` dei record, `Asset/Vehicle_Data.py:4392-4396`), latenza di rete, stato del collegamento (C2 distrutto = rete spezzata). Tocca il DES (`_detect` crea candidati solo per l'osservatore) e la gerarchia militare (`Formation`/`C2_Node`, Fase 0 con 9 decisioni aperte). | **Fuori**: attività successiva alla Fase 0 della gerarchia |

**Punto d'aggancio del livello 3.** Il parametro `ready_delay_s` della corda d'intercettazione (§6) e il
`source_id` delle minacce. Con la rete, il ritardo si calcola dal primo ingresso in **qualunque** V_R
della rete, invece che in quello del sito. Per la modalità "non rilevato" la rete non cambia nulla:
essere visti da chiunque del lato nemico è già "rilevato" [I, scelta di modello: D-7].

---

## 3. Integrazione con il pianificatore di rotta

### 3.1 Come tratta oggi un `ThreatAA` [V]

`RoutePlanner.calcRoute` (`Logic/Air_Route_Manager.py:772-896`), su **una sola lista** `threats_`:

1. **Esclusioni** (`:812-826`):
   - le minacce che contengono `start` (`excludeThreat`, `:933-973`);
   - le minacce terminali, che contengono `end`: vengono estratte e il loro pericolo si riapplica a
     posteriori (fix non committato: `extractTerminalThreats` `:975-995`, `applyTerminalThreatsDanger`
     `:997-1034`);
   - con `consider_aircraft_altitude_route`, le minacce la cui fascia non contiene la quota di rotta
     (`:822-826`, `:966`).
2. **Ramo `intersecate_threat=False`**, cioè `calcPathWithoutThreat` (`:1097-1181`):
   - prima minaccia intersecata (`firstThreatIntersected`, `:1036-1067`);
   - poi `_handle_threat_avoidance` (`:1554-1895`): cambio di quota sopra/sotto la fascia se autorizzato
     (`:1603-1736`), altrimenti aggiramento sui punti esterni di un cilindro allargato del 3 %
     (`:1739-1895`).
3. **Ramo `intersecate_threat=True`**, cioè `calcPathWithThreat` (`:1183-1309`):
   - con intersezione **completa**, cioè due punti sulla superficie laterale: `calcMaxLenghtCrossSegment`
     (`:1280-1282`) e `_handle_threat_crossing` (`:1311-1552`), corda di sicurezza, `danger` sull'arco di
     attraversamento (`:1522`), minaccia rimossa (`:1524`);
   - **qualunque altra intersezione** (estremo interno, ingresso dall'alto o dal basso) restituisce
     `False` (`:1308-1309`) e **non ripiega sull'aggiramento**.
4. **Scelta**: `get_best_path` (`:719-735`) minimizza la coppia `(total_danger, total_length)`.

Quindi: **un tipo di volume, due modalità** (aggira oppure attraversa), scelte con un flag booleano.

### 3.2 Nuova firma (proposta)

```python
class ThreatMode(Enum):
    AVOID               = 'avoid'                # aggira V_I (oggi: intersecate_threat=False)
    CROSS_UNINTERCEPTED = 'cross_unintercepted'  # attraversa V_I con corda di sicurezza (oggi: True)
    AVOID_DETECTION     = 'avoid_detection'      # aggira V_R (nuovo)

def calcRoute(self, start, end, threats_: list[ThreatAA], ...,
              intersecate_threat: bool = False,                          # alias retrocompatibile
              mode: ThreatMode | None = None,                            # prevale su intersecate_threat
              detection_threats: list[DetectionThreat] | None = None) -> Route
```

| Modalità | Volumi di ricerca | Volumi solo per metrica | Motore di ricerca riusato |
|---|---|---|---|
| `AVOID` | V_I | V_R (tempo di preavviso, §3.5) | `calcPathWithoutThreat`, invariato |
| `CROSS_UNINTERCEPTED` | V_I | V_R (ritardo di prontezza, §6) | `calcPathWithThreat`, invariato salvo `ready_delay_s` |
| `AVOID_DETECTION` | V_R alla quota di rotta | V_I (pericolo residuo se la ricerca fallisce) | `calcPathWithoutThreat` su `detection_threats` |

- **Le tre funzioni di ricerca non cambiano algoritmo.** Cambia solo **quale lista** ricevono. È il punto
  forte del disegno: il path-finding esistente (e i suoi test) lavora già su "una lista di volumi con
  `innerPoint`/`edgeIntersect`/`min_altitude`/`max_altitude`/`danger_level`".
- **Combinazioni** ("evita il rilevamento dove puoi, altrimenti attraversa senza essere intercettato"):
  restano una **strategia del chiamante**, cioè più chiamate e confronto dei risultati. Lo suggerisce già
  la nota del codice sulla doppia esecuzione (`:795-801`). Il chiamante naturale è il futuro pianificatore
  di missione (Proposta B, `Session_Mission_Planner`).
- **Minacce terminali in `AVOID_DETECTION`.** Il bersaglio sta quasi sempre dentro un V_R. Stesso
  trattamento del fix, cioè estrazione, ma la metrica non è `danger`: è il **tempo di preavviso** (§3.5).
  La modalità ottimizza il transito, non l'arrivo non visto, che di norma è impossibile.

### 3.3 Esiste un "calcMaxLenghtCrossSegment" per il rilevamento? **Non con i dati attuali** [V + I]

- La **legge di rilevamento del DES** è `Pd(d) = f · (1 − 0,5 · (d/R)⁴)` per `d ≤ R`, e 0 fuori
  (`detection_probability`, `Logic/Engagement_Resolver.py:519-546`; `PD_AT_ACQUISITION_RANGE = 0.5`,
  `:200`). Dipende solo dalla **distanza al punto di massimo avvicinamento**, non dal tempo passato dentro
  il volume. Sul bordo vale già `0,5·f`. **Qualunque corda dentro V_R ha Pd ≥ 0,5·f**, quindi con la stessa
  fisica del DES "attraversare senza essere visti" equivale ad "aggirare V_R". Una corda massima
  indipendente dal tempo non esiste.
- **`min_detection_time` non può fare da tempo di permanenza**: è latenza di acquisizione (§1.4 punto 2).
  Usarlo come "si resta invisibili per N secondi" sarebbe incoerente con il DES, che lo usa **dopo** il
  contatto.
- Un modello a corda limitata richiede un **dato nuovo**. Esempi:
  - `dwell_time_s` per sensore, cioè periodo di scansione × colpi necessari alla conferma della traccia
    [I: ordini di grandezza 10-20 s per un EWR a rotazione lenta, 1-3 s per un radar di tiro];
  - `L_max_R = v_a · dwell_time_s`, senza inversione: non si deve uscire prima di un intercettore, solo
    prima della conferma.

  Il DES andrebbe riallineato con una Pd dipendente dalla permanenza, altrimenti pianificatore ed
  esecutore divergono. È un cambio di legge nel risolutore: decisione D-5.
- **Raccomandazione.** `AVOID_DETECTION` nasce come aggiramento puro. Come **metrica**, non come vincolo,
  si riporta la Pd massima lungo ogni tratto dentro un V_R, calcolata con la **stessa**
  `detection_probability` del DES e con `d` = distanza minima dal sensore. Serve al chiamante per scegliere
  fra le alternative quando l'aggiramento totale fallisce.

### 3.4 Prontezza nell'attraversamento d'intercettazione

In `CROSS_UNINTERCEPTED` il pianificatore conosce gli archi già posati del percorso
(`current_path.edges`). Da questi può calcolare quando la rotta è entrata nel V_R dello **stesso**
`source_id`, e quindi `ready_delay_s = max(0, t_contatto + acquisition_time − t_ingresso_V_I)`.

**Primo passo**: `ready_delay_s = 0`, cioè il comportamento del fix. È conservativo per chi attacca
(§2.4), quindi sicuro. **Secondo passo**: calcolo dal percorso. Il vantaggio è grande solo a bassa quota
contro SAM a lungo raggio (tabella §2.4).

### 3.5 Metriche di percorso: non mescolare pericolo e rilevamento

Oggi `Path.total_danger` è la somma dei `danger_level` degli archi (`Logic/Air_Route_Manager.py:624-628`).
Il rilevamento **non è un pericolo commensurabile**: un EWR non abbatte nessuno. Proposta:
- `DetectionThreat.danger_level = 0.0`, così `air_defense_power` e `total_danger` restano invariati per
  costruzione;
- nuovi attributi del `Path`:
  - `detection_exposure_s`: tempo totale dentro volumi V_R, dal tempo di percorrenza degli archi;
  - `first_detection_time_s`;
  - `warning_time_s`: da primo rilevamento ad arrivo, la grandezza tattica che il volo basso minimizza;
- chiave di `get_best_path` configurabile per modalità. Per `AVOID_DETECTION`:
  `(detection_exposure_s, total_danger, total_length)`. Per le altre resta quella attuale. Decisione D-3.

### 3.6 Limiti noti che la modalità a rilevamento rende visibili [V]

- **Cambio di quota.** `change_up`/`change_down` usano la fascia piatta `min_altitude/max_altitude`
  (`:1603`, `:1674`, `:1682`). Su un V_R con orizzonte:
  - il limite inferiore è ~0: non si passa "sotto" un radar vicino;
  - scendere **restringe** il raggio invece di evitare il volume.

  In `AVOID_DETECTION` il cambio di quota va disabilitato finché V_R è costruito alla sola quota di rotta
  (§2.5).
- **Attraversamento incompleto.** `calcPathWithThreat` fallisce su intersezioni non laterali
  (`:1308-1309`). Per V_I resta com'è: non è introdotto da questa proposta.
- **Deviazioni proporzionali al raggio.** L'aggiramento usa `threat.cylinder.radius` per spostamenti e
  punti laterali (`:1445`, `:1460`, `:1739`, `:1785`, `:1808`). Con V_R da 300 km, le deviazioni di
  1,5 × raggio portano fuori dalla portata dell'aereo: il limite `aircraft_range_max` le scarterà
  (`checkPathOverlimits`, `:1069-1094`). È comportamento corretto, ma va detto all'utente: contro una rete
  EWR in quota **l'aggiramento spesso non esiste**, e il risultato atteso è "nessuna rotta". Da lì il
  chiamante scende di quota o passa ad `AVOID`.

---

## 4. Collegamento con la Proposta B: **sì, va aggiornata, nella firma e in B3**

**L'incoerenza** [V, lettura dei due testi]. Proposta B §2.4 definisce
`effective_seconds = max(0, seconds − (min_detection_time + min_fire_time))`, e in B3 la raccomanda. È
l'ipotesi "il sito comincia a reagire quando entro nel **volume d'arma**". Il fix di
`calcMaxLenghtCrossSegment` ipotizza l'opposto: "il sito mi ha già acquisito prima che entrassi"
(`Logic/Air_Route_Manager.py:88-89`). Due documenti della stessa sessione, due cronometri diversi per la
stessa minaccia:
- il pianificatore di transito sarebbe conservativo;
- il pianificatore d'attacco sarebbe ottimista.

Proprio sul tratto terminale, dove il bersaglio difeso sta sempre dentro un V_R.

**Raccomandazione netta.**
1. `plan_attack_profile(..., threats, detection_threats, ...)`: le **due liste** dal primo giorno, nella
   firma. Costa zero e impedisce che B nasca sulla semantica indifferenziata.
2. **B3 riformulata** con la regola unica di §2.1:
   - `t_lancio = max(t_ingresso V_I, t_contatto V_R + acquisition_time) + min_fire_time`;
   - `effective_seconds = max(0, t_uscita V_I − t_lancio)`.

   Senza V_R, cioè nel primo passo, `t_contatto = −∞` e quindi `effective_seconds = seconds − min_fire_time`:
   coerente con il fix, non con la B3 attuale.
3. **`ThreatExposure` acquista `detected_at_s` e `warning_time_s`**. Il preavviso al difensore è **il**
   parametro che una quota di sgancio bassa compra, e senza V_R la Proposta B non lo vede.
4. `route_threat_windows` funziona già con un `DetectionThreat` che esponga `.cylinder`
   (`_cylinder_of`, `Logic/Contact_Scheduler.py:415-417`): nessuna modifica al `Contact_Scheduler`
   nel primo passo.

---

## 5. Estensione futura a volumi non cilindrici: dove sta l'aggancio

- **Il confine vero è già dichiarato: la Attività D** (`Piano_Lavori_2026_09_24.md:82-86`). Interfaccia
  "volume" che restituisce **intervalli di permanenza** su un tratto a moto rettilineo uniforme. Primitive:
  sfera, cilindro, fascia di quota, cono, orizzonte radar. Combinatori: unione, intersezione, differenza.
  Destinazione: `detection_volume`/`engagement_volume` per asset e per arma. Questa proposta **ne è il
  lato pianificatore**, e non deve introdurre una seconda astrazione. `AirThreat.volume` diventa quel tipo.
- **Nel pianificatore l'accoppiamento a `Cylinder` è localizzato** [V]:
  - `ThreatAA.edgeIntersect`/`innerPoint` (`:47-68`) sono già una facciata;
  - le dipendenze dirette dalla forma sono una decina di accessi a `threat.cylinder.radius/center` e ai suoi metodi
    specifici:
    - `find_chord_coordinates` (`:1383-1389`);
    - costruzione di punti laterali (`:1445`, `:1460`, `:1780-1808`);
    - `getIntersection` (`:1610`), `innerPoint` (`:1619`);
    - `Cylinder(...)` allargato (`:1739`), `pointOfCirconference` (`:1747`);
  - la formula della corda (`:100-101`).
- **La primitiva di cui il pianificatore ha bisogno è la sezione orizzontale**, non il solido intero.
  Esiste già in embrione: `Cylinder._get_circle_at_z(z) -> (centro, raggio)`
  (`DataType/Cylinder.py:107-114`). Ogni **solido di rotazione** ha una sezione circolare a ogni quota: il
  cilindro, il cono, la semisfera (esiste `DataType/Hemisphere.py`, non usato), l'orizzonte radar.
  Proposta d'interfaccia minima da chiedere a D: `section_at(z) -> (center2d, radius) | None` più
  `altitude_band() -> (z_min, z_max)`. Il pianificatore sostituisce `threat.cylinder.radius` con
  `threat.volume.section_at(z_rotta).radius`, e **l'algoritmo di aggiramento non cambia**, perché lavora
  già su cerchi alla quota dell'arco.
- **Composizioni.** Un'unione di volumi dello stesso sito (per esempio il cono di silenzio sottratto, o
  radar su pali diversi) si rappresenta nel pianificatore come **più minacce con lo stesso `source_id`**:
  il path-finding gestisce già liste di minacce sovrapposte. La differenza (cono di silenzio sopra il sito)
  non si esprime con le sole sezioni circolari, perché la sezione diventa una corona. Va rimandata a D, e
  per la rotta ha poco valore pratico [I].
- **Cosa questa proposta NON deve fare** per non ostacolare D:
  - non aggiungere altri accessi diretti a `.cylinder` fuori da `AirThreat`;
  - non codificare l'orizzonte dentro `Cylinder`: il raggio alla quota di rotta si calcola nella fabbrica,
    e il `Cylinder` resta un contenitore geometrico puro;
  - tenere `cylinder` come **alias** di `volume` finché `Contact_Scheduler._cylinder_of` lo legge.

---

## 6. Impatto sul lavoro non committato

**`calcMaxLenghtCrossSegment`** (`Logic/Air_Route_Manager.py:70-131`): **resta corretto come modello
d'intercettazione**. La sostanza non cambia.
- La fisica (intercettore dal sito, avvicinamento radiale peggiore, quota relativa, inversione che consuma
  il tempo) è indipendente da come si è stati rilevati. Il rilevamento entra **solo** nell'istante di
  lancio.
- **Modifica necessaria all'arrivo di V_R**: un parametro opzionale `ready_delay_s = 0.0`, con
  `x0 = R − v_a·(min_fire_time + ready_delay_s)` e `t* = ready_delay_s + min_fire_time + lm/v_i`.
  L'equivalenza è verificata: E-2 la ottiene passando `min_fire_time + ritardo` alla formula attuale, che
  dà i numeri di §2.4. Default 0 = comportamento e test attuali invariati.
- **Docstring da riscrivere** (`:88-89`). L'argomento "portata radar > portata arma" è vero sui dati in
  quota (§1.2) ma falso a bassa quota (§2.5). Va sostituito con l'ipotesi esplicita: "sito pronto
  all'ingresso nel volume d'intercettazione (`ready_delay_s = 0`): conservativo per chi attacca".
- **Nome**: rinomina **facoltativa**, per esempio `calcMaxUninterceptedChord`, con alias del vecchio nome
  per non toccare i test. Non necessaria (D-6).
- **Semantica di lancio coerente con il DES** [V]:
  - planner: lancio quando il bersaglio **entra** nel volume;
  - DES: `_range_entry` spara al primo istante in portata.

  Nessuno dei due modella il lancio anticipato sul punto d'intercettazione predetto (lancio **prima**
  dell'ingresso contro un bersaglio che si avvicina). Il limite è comune e va dichiarato una volta sola,
  in D [I sull'entità dell'effetto: dell'ordine del tempo di volo del missile].

**`extractTerminalThreats` / `applyTerminalThreatsDanger`** (`:975-1034`): **corretti, nessuna modifica
sostanziale**.
- Sono generici su "volume con `innerPoint`/`edgeIntersect`/`danger_level`" e funzionano identici su V_R.
- Con `danger_level = 0` di un `DetectionThreat` non sporcano `total_danger`.
- L'unica aggiunta è altrove: la metrica di preavviso (§3.5) per i V_R terminali.
- `extractTerminalThreats` va chiamato **per lista**, una volta su V_I e una su V_R.

**Test del fix**: nessuno si rompe.
- `test_cross_formula_*` restano validi con `ready_delay_s = 0`.
- `test_terminal_threat_*` restano validi perché il pianificatore di default riceve solo V_I.

**Raccomandazione**: committare il fix così com'è, con la sola docstring corretta (§6 punto 3). Il resto
arriva con l'implementazione di questa proposta.

---

## 7. Esperimenti di sola lettura

Script nella scratchpad di sessione (`sensors_vs_weapons.py`, `cross_delay.py`), fuori dal repository,
eseguiti con `.direnv/python-3.12/bin/python3`. Nessun file del repository modificato.

| # | Configurazione | Risultato | Cosa dimostra |
|---|---|---|---|
| E-1 | Per ogni record `Vehicle_Data`/`Ship_Data` con armi AD: portata arma (stessa selezione di `air_defense_volume`), `guide`, e `acquisition`/`tracking`/`engagement_range` del radar e `acquisition_range` del TVD in modo `air` (`Mobile._sensor_range_km`) | 15 veicoli e 22 navi. Scoperta ≥ arma in tutti i sistemi con sensore; guida ≥ arma dove dichiarata; ZSU-57-2 e M163 senza sensori; 9 navi con `engagement_range` `None` | §1.2: i dati di scoperta e di guida esistono già e sono coerenti |
| E-2 | `ThreatAA` reale, `calcMaxLenghtCrossSegment` del fix; ritardo di prontezza emulato come `min_fire_time + ritardo`, con il ritardo calcolato dall'orizzonte radar (antenna 5 m) su avvicinamento radiale; S-300PS e 2K12-Kub, 250 m/s, inversione 10 s | tabella §2.4: identico in quota, S-300PS a 30 m da 8,0 a 46,3 km | §2.4, §6: il fix è il caso limite corretto e conservativo |

---

## 8. Difetti incontrati durante la lettura (fuori scope, da segnalare)

1. **`get_best_path` rimuove da una lista mentre la scorre** (`Logic/Air_Route_Manager.py:727-729`). Un
   percorso troppo lungo subito dopo un altro troppo lungo non viene scartato, e può essere scelto come
   migliore. [V lettura; I sulla frequenza pratica]
2. **Comportamento che dipende dal flag di debug** in `_handle_threat_avoidance`:
   `if not valid_lateral_movement_ext_p1 and debug: ext_p1 = None` (`:1792-1794`, simmetrico `:1816-1818`).
   Con `debug=False` un punto esterno rimasto dentro un'altra minaccia **non** viene scartato. [V]
3. **`Vehicle.isEWR`** confronta `asset_type` con `'EWR'` (`Asset/Vehicle.py:298-299`). Il resto della
   tassonomia usa lo stesso bucket (`Context.py:776`), quindi è coerente. Non è verificabile su un record
   reale perché nessun EWR esiste nel registro (§1.3). [V l'assenza; I il resto]
4. `DataType/Threat.py` e `DataType/Volume.py` sono abbozzi non funzionanti: `Threat.__init__` usa
   `General` e `obj` non definiti (`:22-31`), `Volume.inside` restituisce sempre `False` (`:57-75`).
   Sono importati da `Asset/Aircraft.py:16-17`. **Non vanno scambiati** per l'interfaccia volume di D:
   meglio un modulo nuovo, e questi rimossi o riscritti quando D parte. [V]

---

## 9. Decisioni richieste all'utente

In ordine di blocco:
1. **D-1 Perimetro e sequenza**: questa proposta si fa come **anticipo della Attività D** sul lato
   pianificatore (tipi `AirThreat`/`DetectionThreat` ora, forme non cilindriche con D), oppure si aspetta D
   e si fa tutto insieme? (Raccomandato: anticipo, perché il primo passo usa solo `Cylinder`.)
2. **D-2 Modalità**: adottare `ThreatMode` {`AVOID`, `CROSS_UNINTERCEPTED`, `AVOID_DETECTION`} con
   `intersecate_threat` come alias retrocompatibile? Le combinazioni restano al chiamante? (Raccomandato.)
3. **D-3 Metriche**: `DetectionThreat.danger_level = 0` e metriche separate `detection_exposure_s` /
   `warning_time_s`, con chiave di scelta del percorso per modalità? Oppure un peso di rilevamento sommato
   al pericolo?
4. **D-4 Dati**:
   - (a) altezza d'antenna: default per classe dichiarati ora, dato di registro poi?
   - (b) record EWR (e WWII) con ricerca dati dedicata?
   - (c) sensore visivo di ripiego per ZSU-57-2 e M163?
5. **D-5 "Non rilevato" a corda limitata**: si accetta che `AVOID_DETECTION` sia aggiramento puro più la
   metrica Pd? Oppure si introduce `dwell_time_s` per sensore **e** una Pd dipendente dalla permanenza nel
   DES? La seconda cambia la legge del risolutore.
6. **D-6 Nomi**:
   - rinominare `min_detection_time` in `acquisition_time`, con alias e aggiornamento di
     `Reaction_Profile`?
   - rinominare `calcMaxLenghtCrossSegment`, con alias?
7. **D-7 Rete di sensori**: confermare che il cueing EWR → SAM è **fuori perimetro** e segue la Fase 0
   della gerarchia militare (`Formation`/`C2_Node`)? Per la modalità "non rilevato", essere visti da un
   qualunque sensore nemico conta come rilevato?
8. **D-8 Proposta B**: adottare le due liste nella firma di `plan_attack_profile` e la B3 riformulata di
   §4? Questo sostituisce la raccomandazione B3 del documento precedente.
9. **D-9 Fix non committato**: committarlo subito con la sola docstring corretta (§6), lasciando
   `ready_delay_s` all'implementazione di questa proposta? (Raccomandato.)
10. **D-10 Difetti di §8** (1 e 2): correggerli in un commit separato prima di toccare il pianificatore?

---

## 10. Mappa d'impatto (proposta, non implementazione)

| Componente | Primo passo (solo `Cylinder`) | Con Attività D |
|---|---|---|
| `Logic/Air_Route_Manager.py` | `AirThreat` base, `DetectionThreat`, `build_air_defense_threats`, orizzonte radar nella fabbrica, `ThreatMode`, `detection_threats` in `calcRoute`, `ready_delay_s`, metriche di `Path`, controllo di tipo su `AirThreat` | accessi a `.cylinder` → `volume.section_at(z)` |
| `Asset/Mobile.py` | nessuna modifica: `detection_range` esiste; eventuale `min(arma, guida)` in `air_defense_volume` o nella fabbrica | `detection_volume`/`engagement_volume` |
| `Block/Military.py` | `air_detection_threats(route_altitude)`; `air_defense_power` invariata | idem |
| `Asset/Vehicle_Data.py`, `Ship_Data.py` | (D-4) `antenna_height` opzionale, record EWR, sensori AAA | — |
| `Logic/Contact_Scheduler.py` | nessuno (`_cylinder_of` legge l'alias `cylinder`) | intervalli dal volume |
| `Logic/Engagement_Resolver.py` | nessuno | V_R/V_I al posto delle due sfere; (D-5) Pd con permanenza |
| `Context/Reaction_Profile.py` | solo se D-6 rinomina `min_detection_time` | — |
| Proposta B (`Weapon_Delivery`, non costruito) | due liste nella firma, B3 riformulata, `warning_time_s` | — |
| `DataType/Threat.py`, `Volume.py` | nessuno | sostituiti dall'interfaccia di D |
