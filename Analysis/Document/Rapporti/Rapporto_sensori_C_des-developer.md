# Rapporto sensori C (siti EWR fissi) — des-developer

- **Agente / modello**: `des-developer` / Claude Sonnet 5.5
- **Branch**: `ai/cc-sensori-c` · **piano eseguito**: `Analysis/Document/Proposta_Dati_Sensori_EWR_Siti_Fissi.md` §4 (C.1-C.8)
- **Data**: 2026-11-05

## 1. Esito in una riga
Completato, nessuno scostamento dal piano. Suite `Ran 4757`, OK (skipped=7); confronto 1009 identiche, 0 cambiate, 0 nuove. Nulla committato.

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py` | C.1: argomento `fixed_site: bool = False` in coda a `__init__`, validazione `ValueError` prima della registrazione, attributo `self.fixed_site`. C.2: `_ewr_support_fields` con terzo ramo `'fixed'` (rami `'mobile'`/`'semi_mobile'` identici nei valori). C.3: 7 record (`AN_FPS117_data`, `Chain_Home_data`, `AMES_Type7_data`, `AMES_Type80_data`, `Wassermann_data`, `Mammut_data`, `P14_Lena_data`) dopo `AN_TPS43_data` e registrazione dopo `Vehicle_Data(**AN_TPS43_data)` |
| `Code/Dynamic_War_Manager/Source/Logic/Air_Route_Manager.py` | C.4: solo commento sopra `SENSOR_HEIGHT_*` (+1 riga: 11 righe cambiate, nessun codice) |
| `Code/Dynamic_War_Manager/Source/Test/Test_Vehicle_Data.py` | C.5: `test_all_vehicles_speed_eval_positive` salta i record con `fixed_site` (3 righe aggiunte) |
| `Code/Dynamic_War_Manager/Source/Test/Test_EWR_Data.py` | C.6: docstring di modulo, import, costanti `FIXED_SITE_*`, 3 classi nuove con 15 test |

## 3. Scostamenti dal piano
Nessuno. Controllato sul diff (`git diff -U0`): nei rami `'mobile'` e `'semi_mobile'` di `_ewr_support_fields` valori invariati
(dimensioni, costo, `range`, velocita'; `consume` 0.4/0.55/0.7 ora letto dalla tupla `consumes` con gli stessi valori).
`test_range_is_positive_number` non toccato. Nessun codice del motore modificato.

## 4. Scelte minori prese
- Anagrafica C.3-a: commenti brevi accanto ai campi (testo mio, secondo le note del piano); in AN-FPS-117 il commento su
  `constructor` e `model`; in P-14-Lena la nota 1RL113/5N84A e 731/~2000 sta nel commento di testa del sensore.
- Chain-Home: aggiunta nel commento del sensore la nota "fascio su 150 gradi, omnidirezionale (limite)" (dal §5.2 punto 3 del piano).
- `_ewr_support_fields`: variabile locale `consumes` e `fields` (come nel testo del piano).
- Test: messaggi `msg=` nei subTest, ordine delle asserzioni dentro i test; nei test 3 e 8 il ciclo salta/ramifica con
  `continue`/`if` dentro `subTest`; il test 7 verifica anche che il profilo sia quello atteso (`FIXED_SITE_PROFILES`) oltre alla
  coerenza; il test 15 (sessione) controlla `ammunition_events` e `fuel_events`. I 15 test sono: 10 + 1 + 4 come da C.6.
- Messaggio della `ValueError`: `fixed_site must be a bool, got: 'yes'` (come nel piano).

## 5. Costanti stimate
Tutte dichiarate nel codice (commento) e qui:
- `_ewr_support_fields('fixed')` [S]: dimensioni 30x10x20 m, 50 t (classe 'big'); costo 10.0 M$ (non consumato dal motore);
  `consume` (0, 0, 0); **`range` = 1 km SEGNAPOSTO di schema, non autonomia**. Velocita' 0 nei tre regimi: dato vero, non stima.
- `reliability` 45/4 [S] dei 6 siti diversi dall'FPS-117 (decisione 12); `communication.reliability` 45/3 [S] come per gli altri EWR.
- `acquisition_range`: Mammut 300 km e P-14 400 km = FONTE DEBOLE trattata come STIMA (bersaglio non qualificato); gli altri di fonte
  con confidenza media (FPS-117 media-alta); Wassermann e Type 7 a 6000/6100 m, non 10 000.
- `antenna_height` DEDOTTE (limiti superiori): Chain-Home 73 m, Wassermann 37 m, Type 80 11,4 m. Gli altri 4 siti usano il default EWR 20 m [S] (`SENSOR_HEIGHT_EWR_M`).
- FPS-117 `reliability` 2000/0.75: da fonte (limiti: ">2000 h", "<45 min" = 0.75 h, conversione dedotta), decisione C-2.

## 6. Verifiche eseguite
- `python3 -m unittest Code.Dynamic_War_Manager.Source.Test.Test_EWR_Data`: `Ran 30 tests` · `OK` (15 preesistenti + 15 nuovi)
- `python3 -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Vehicle_Data`: `Ran 168 tests` · `OK`
- Suite: `ESITO suite: exit code 0 · interprete python3` — `Ran 4757 tests in 1231.551s` — `OK (skipped=7)`. Come atteso (4742 + 15).
- Confronto: `ESITO confronto: exit code 0 · interprete python3` — `compared 1009 runs: IDENTICAL (957.6 s)`; `UNCHANGED (1009)`;
  `grep -cE '^(CHANGED|NEW)' .ai-run/confronto.log` = 0. Come atteso: 1009 identiche, 0 cambiate, 0 nuove. Nessuna fotografia installata.

## 7. Limiti noti e dubbi per la sessione principale
Quelli di §5.2 della Proposta, invariati: immobilita' non imposta dal motore (C-4); il DES non ha orizzonte radar (portate 300-400 km
applicate anche ai radenti, costo di calcolo non misurato); copertura angolare omnidirezionale; torri non rappresentate; siti WWII senza
latenza di plotting; fuori dal catalogo RWR; nessun cueing; score di categoria EWR spostati per gli 8 mobili (nessun consumatore);
migrazione a `Structure` richiede codice oltre ai dati. Documenti da aggiornare dopo: elenco in fondo alla Proposta (non toccati).

## 8. Stato git
`git status --short`:
```
 M Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py
 M Code/Dynamic_War_Manager/Source/Logic/Air_Route_Manager.py
 M Code/Dynamic_War_Manager/Source/Test/Test_EWR_Data.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Vehicle_Data.py
?? "Analysis/Document/Untitled 1.odt"    (preesistente, non mio)
?? Analysis/Document/Rapporti/Rapporto_sensori_C_des-developer.md
```
`git stash list`: vuota. `git log --oneline -3`: 7264b028, 3594dda1, 17280694 (nessun commit nuovo).
