# Rapporto BI blocco 1 — des-developer

- **Agente / modello**: `des-developer` / Claude Sonnet 5.5
- **Branch**: `ai/des-bi-blocco1` · **piano eseguito**: `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` §5.2 (valori: `Analysis/Document/Proposta_Dati_Bersagli_Intercettabili.md` §10.1-§10.2)
- **Data**: 2026-11-07

## 1. Esito in una riga
Completato; suite OK (4801 test, +6); confronto con la fotografia: 1009 identiche, 0 cambiate, ma **20 esecuzioni NUOVE** (S32-DWELL) non attese dal piano e **non dovute a questo blocco** (v. §6 e §7).

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py` | 44 voci di `AIR_WEAPONS['MISSILES_ASM']`: campi `munition_class`, `ad_detectable`, e dove il §10.2 li da' `diameter_mm`, `mass_kg`, ciascuno con commento (`# STIMA [S]: ...`); Maverick (AGM-65D, AGM-65K, RB-75T) con il commento della decisione BI-6; commento di testa sopra `'MISSILES_ASM'`. Solo righe aggiunte (~175). |
| `Code/Dynamic_War_Manager/Source/Asset/Ship_Weapon_Data.py` | Come sopra per le 8 voci di `SHIP_WEAPONS['MISSILES_ASM']` (`diameter_mm` accanto a `caliber`, che non e' stato toccato); commento di testa. Solo righe aggiunte (~36). |
| `Code/Dynamic_War_Manager/Source/Test/Test_Aircraft_Weapon_Data.py` | Nuova classe `TestAdTargetFields` con i 6 test del §5.2; import di `SHIP_WEAPONS` e `get_weapon_score` navale (alias `get_ship_weapon_score`). |
| `Analysis/Document/Rapporti/Rapporto_BI_blocco1_des-developer.md` | questo rapporto |

Nessun file di logica toccato (`Logic/Fire_Control.py`, `Logic/Engagement_Resolver.py` e altro invariati).

## 3. Scostamenti dal piano
Nessuno sul codice. Precondizioni verificate: (1) stato "DECISO" in testa alla Proposta dati: si'; (2) gli scorer iterano sulle chiavi di `WEAPON_PARAM`, non su quelle della voce (`get_missiles_score` usa `weapon.get(param_name)` per `param_name` in `WEAPON_PARAM[...]`; `get_asm_score` navale `weapon[p]` per `p` in `WEAPON_PARAM['MISSILES_ASM']`): un campo nuovo non li tocca; (3) 44 voci aeree e 8 navali, tutte le 52 del §10.2 presenti con lo stesso nome. Righe di fire control del §5.0 punto 3 non verificate: il blocco 1 non le tocca.

Una differenza di conteggio da segnalare, non un errore del piano: il confronto con la fotografia ha 20 esecuzioni NUOVE (S32-DWELL), v. §6.

## 4. Scelte minori prese
- Tutti e 6 i test stanno in `Test_Aircraft_Weapon_Data.py` (classe `TestAdTargetFields`); `Test_Ship_Weapon_Data.py` NON e' toccato. Il piano parla di "file esistenti" (plurale) ma dei 6 test uno solo (il 6) riguarda anche un'arma navale e il test 5 sta per piano nel file aereo; i test 1-3 iterano su entrambi i registri. Cosi' il totale resta 6.
- Test 6: il valore navale e' `get_weapon_score('MISSILES_ASM', 'RGM-84-Harpoon')` (la firma navale ha due argomenti; l'Harpoon non e' nel registro aereo). Valori letti PRIMA della modifica: AGM-65D `1.416515714285714`, Kh-55 `103.14253968253968`, RGM-84-Harpoon `0.2600272727272727`; confronto con `assertEqual` esatto.
- Test 3 congela anche l'insieme delle chiavi dei due registri (una voce nuova senza classe approvata fa fallire il test); il test 1 controlla anche 44 e 8 voci.
- Test 2: i numeri non possono essere `bool` (`bool` e' sottoclasse di `int`).
- Test 5: le asserzioni (1) e (2) hanno un `subTest` per voce; (3a) e (3b) come da piano; controllato `len(pairs) == 44`.
- Posizione dei campi: subito dopo la riga `"model"` di ogni voce; commento di testa sopra `'MISSILES_ASM'` (in `Ship_Weapon_Data.py` dopo la riga separatrice `# ───`).
- Commenti: classe `# STIMA [S]: classe approvata, <Proposta dati> §10.2` (con nota per Mistral D2 (a), Kh-22N D3.1 (a), KD-63/KD-63B D3.2 (a)); flag con esito del metro (F!/T!), zona grigia con riferimento al paragrafo §6.x, `default di classe` per le voci senza coppia; dimensioni con la fonte della tabella (separate per diametro e massa dove il §10.2 lo permette; per Kh-25MR, Kh-66 ecc. la stessa stringa di fonte e' ripetuta su entrambe le righe, perche' la tabella da' una fonte sola).
- Applicato con uno script (non versionato) dalla tabella del §10.2; verificati a mano i totali: 32 True e 20 False, 44 `diameter_mm`, 46 `mass_kg`, classi 10 cruise / 17 anti_ship / 7 arm / 18 tactical, 44 voci con la coppia = 13 F! + 26 T! + 5 ZG (AGM-88, Kh-25MP, Kh-25MPU, RB-05A, Kormoran).
- Voci senza dato (celle "—"): `diameter_mm`/`mass_kg` non scritti (8 voci senza coppia; Kh-65 e RB-75T hanno solo la massa); al loro posto un commento `# diameter_mm e mass_kg non scritti: ...` dove mancano entrambi.

## 5. Costanti stimate
- Tutti i valori dei 4 campi sono stime di progetto [S] su dati di fonti aperte (non dati tarati), dichiarate come `# STIMA [S]` accanto a ogni campo e nel commento di testa; sono i valori del §10.2 della Proposta dati (decisi dall'utente il 2026-11-07), non scelti da me. Fanno eccezione i `ad_detectable` della famiglia Maverick, commentati come decisione BI-6.
- Costanti del test 5: `D_M = 304.8`, `M_M = 304`, `D_H = 343`, `M_H = 515.25`, `GREY_ZONE_APPROVED` (6 voci): stime [S] con fonte, come da piano (Proposta dati §5.1); dichiarate come tali nel test.
- Nessuna costante inventata da me.

## 6. Verifiche eseguite (righe dell'ESITO)
- File di test singoli (interprete `.direnv/python-3.12/bin/python3`): `TestAdTargetFields` `Ran 6 tests` `OK`; `Test_Aircraft_Weapon_Data` `Ran 291 tests` `OK`; `Test_Ship_Weapon_Data` `Ran 155 tests` `OK`.
- Suite completa (`tools/ai/verifica.sh suite`): `ESITO suite: exit code 0 · interprete .direnv/python-3.12/bin/python3`, `Ran 4801 tests in 560.797s`, `OK (skipped=7)`. Atteso dal piano: 4795 + 6 = 4801. La base era 4795 (4801 - 6; non misurata a parte prima delle modifiche).
- Confronto (`tools/ai/verifica.sh confronto`): `ESITO confronto: exit code 1`; `UNCHANGED (1009): ...`; `compared 1029 runs: 20 difference lines`. **Diverso dall'atteso** (`compared 1009`, nessuna nuova): ho confrontato a mano `Test/baseline/scenario_baseline.json` con la cattura (`.ai-run/confronto_capture.json`): 1009 esecuzioni nella fotografia, 1029 nella cattura, **0 cambiate**, nessuna solo-nella-fotografia, **20 solo-nella-cattura**, tutte `S32-DWELL/S32-DWELL-{0,1,2,3}/{ewr_off,ewr_on,long,off,short}`. Lo scenario S32-DWELL e' definito in `Test/Scenario_Baseline.py` e `Test/Test_Session_Scenarios_S32.py` gia' al commit di partenza (`git grep S32-DWELL HEAD`), la fotografia versionata non lo contiene: le 20 esecuzioni sono NUOVE rispetto alla fotografia indipendentemente da questo blocco (che modifica solo dati non letti). Non ho installato la fotografia nuova. Non ho rieseguito il confronto sul commit di partenza per escluderlo sperimentalmente (richiederebbe stash/checkout, vietati).

## 7. Limiti noti e dubbi per la sessione principale
- **Esito del confronto diverso dall'atteso** (1029 compare contro 1009 attese): vedi §6. Le 1009 esecuzioni della fotografia sono identiche; le 20 nuove sono S32-DWELL, la cui fotografia non e' ancora stata aggiornata (decisione dell'utente/sessione principale, non mia). Se si vuole il "compared 1009" stretto, serve prima rigenerare la fotografia con S32-DWELL o verificare l'atteso con i numeri dell'ESITO attuale.
- Mixed-source: le stringhe di fonte per voce riprendono la colonna del §10.2 senza distinguere diametro e massa dove la tabella non lo fa (Kh-25MR, Kh-66, Kh-25ML ecc.); l'ho distinto solo dove il testo della Proposta dati lo diceva (AGM-65D/K, AGM-114, RB-05A, Kormoran, Kh-22N).
- Nessun valore verificato su fonti esterne da me: tutti dal §10.2; i limiti sul livello di verifica ("agente"/"principale") sono quelli della Proposta dati §2.
- Non verificato: i punti di `Logic/Fire_Control.py:763-768`, `Engagement_Resolver.py:614/3291/3350` (precondizione 3 del §5.0): non servono a questo blocco, che non li tocca.

## 8. Stato git
Vedi il messaggio di consegna (aggiornato dopo il commit).
