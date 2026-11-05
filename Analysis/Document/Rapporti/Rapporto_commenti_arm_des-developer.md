# Rapporto commenti Air_Route_Manager — des-developer

- **Agente / modello**: `des-developer` / Claude Sonnet 5.5
- **Branch**: `ai/cc-commenti-arm` · **piano eseguito**: compito diretto (nessuna Proposta), solo commenti/docstring
- **Data**: 2026-11-05

## 1. Esito in una riga
Completato: solo commenti/docstring corretti in `Air_Route_Manager.py`, nessun codice eseguibile toccato.

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Logic/Air_Route_Manager.py` | 4 punti di commento/docstring (v. sotto); diff: 7 inserzioni, 4 cancellazioni, tutte righe `#` o docstring |

Punti corretti:
1. Commento sopra `SENSOR_HEIGHT_VEHICLE_M`: `antenna_height` ora dichiarata nei dizionari `radar`/`TVD`/`visual`; oggi la dichiara solo il record SCR-270 (EWR, 16,8 m, DEDOTTO da fonte, antenna alzata a 55 ft), gli altri usano le stime per classe.
   Verifica: `grep -n antenna_height Vehicle_Data.py Ship_Data.py` -> un'unica occorrenza di chiave (`Vehicle_Data.py:4655`, piu' il commento a :4653); nessuna in `Ship_Data.py`. Nessun record `visual` la dichiara.
2. Riga EWR dello stesso blocco: "nessun record EWR oggi" sostituito. Conteggio `grep -c "^    'category': 'EWR',"` in `Vehicle_Data.py` = 8: SCR-270, FuMG-80-Freya, P-12-Yenisei, P-18-Terek, P-37-Mech, 1L13-Nebo-SV, 55Zh6-Nebo, AN-TPS-43. I 20 m restano STIMA per i 7 senza `antenna_height`.
3. Docstring di `sensor_antenna_height`: `('radar'/'TVD'/'visual')`.
4. Commento a riga ~624 (fabbrica DetectionThreat): "(`radar`/`TVD` -> capabilities['air'] ..." -> aggiunto `visual` (il ciclo di `build_detection_threat` a riga ~761 itera su `('radar', 'TVD', 'visual')`). Non era nell'elenco del compito, ma era reso impreciso da D-4c.

## 3. Scostamenti dal piano
Nessuno. Unica aggiunta rispetto all'elenco: punto 4 sopra (stessa natura, falso per D-4c).

## 4. Scelte minori prese
Formulazione dei commenti; indicati i 7 nomi degli EWR senza dato e il totale 8 nel commento (per evitare che il conteggio diventi di nuovo ambiguo).

## 5. Costanti stimate
Nessuna nuova. `SENSOR_HEIGHT_EWR_M = 20.0` resta una stima dichiarata (ora esplicitamente riferita ai 7 EWR senza dato).

## 6. Verifiche eseguite
- Diff: solo righe di commento/docstring (verificato filtrando le righe `+/-` non `#` e non docstring: nessuna).
- Interprete: `python3` di sistema (nessun `.direnv` ne' `venv` su questa macchina).
- `Test_Threat_AA_Factory`: `Ran 58 tests` · `OK`
- `Test_Air_Route_Manager`: `Ran 81 tests in 200.598s` · `OK` (lento su questa macchina)
- Suite completa e confronto con la fotografia NON eseguiti: modifica di soli commenti, nessun effetto sul comportamento.

## 7. Limiti noti e dubbi per la sessione principale
Commenti con "oggi"/"nessun" lasciati perche' ancora veri:
- riga ~86 "`volume` e' oggi sempre un Cylinder" (vero);
- riga ~204 "valore che il pianificatore usa oggi" per `ready_delay_s` (non toccato da D-4b/D-4c);
- riga ~209 "secondo passo non ancora implementato" (non correlato);
- riga ~201, 283, 334, 349, 381, 422, 546, 579-580, 744-746, 815, 1051, 1091-1100, 1405, 1496-1500, 1726, 2161: "nessun..." su temi non legati ai sensori EWR/visivo, oppure gia' coerenti (es. 746 cita gia' ZSU-57-2/M163 con `D4C_VISUAL_SENSOR` spento; 295 e 638-647 citano gia' `visual`).

## 8. Stato git
`git status --short`: ` M .../Air_Route_Manager.py`, `?? .../Rapporto_commenti_arm_des-developer.md`, `?? Analysis/Document/Untitled 1.odt` (preesistente). `git stash list`: vuota. Nessun commit fatto.
