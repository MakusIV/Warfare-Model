# Le 116 esecuzioni nuove della serie S36 (permanenza breve con i dwell reali)

Totale: 116 esecuzioni, 360 righe di `Detection`.

Estratte il 2026-11-18 da `.ai-run/confronto_capture.json` (cattura del confronto completo: 1103 esecuzioni identiche alla fotografia + **116 NEW**, 0 cambiate, 0 mancanti; suite `Ran 4961`, `OK (skipped=7)`). La fotografia nuova da 1219 **non e' installata**: la installa solo l'utente, dopo aver letto queste righe. Spiegazione delle unita' e delle geometrie: `Proposta_Scenari_S34_Permanenza_Breve.md` e `F4_Differenze_Scenari.md`, sezione S36.

## Come leggere le tabelle

Ogni esecuzione (`unita'/seme/variante`) registra le `Detection` del risolutore nella voce `detections` del riassunto (solo per le cinque unita' S36). Una riga = un'occasione di rilevamento. Colonne (campi `DETECTION_FIELDS`):

- **osservatore -> bersaglio**; **portata** [m] del sensore; **CPA** [m] = distanza minima del passaggio (v. sotto); **Pd** = probabilita' di rilevamento dopo la legge D-5; **estraz.** = numero estratto dall'RNG di sessione; **rilev.** = `estraz. < Pd`; **istante** [s] del rilevamento;
- **perman.** [s] = tempo del bersaglio nella portata dell'osservatore; **dwell** [s] = periodo di rivisita letto dal registro (o dichiarato di test per gli estremi di banda); `g = min(1, perman./dwell)` e' il fattore che moltiplica la Pd;
- **pass.** = indice del passaggio / numero di passaggi (vuoto = un solo passaggio o unione); **inizio/fine** [s] del passaggio.

**Rilevamento con dwell > permanenza (g < 1): e' atteso, non un'anomalia.** La legge D-5 e' probabilistica, non una soglia: `Pd = min(1, perman./dwell) x Pd(d_cpa)` (`Engagement_Resolver.D5_DWELL_TIME`). Il dwell e' il periodo di rivisita del sensore; se il bersaglio resta nel volume meno di un periodo, il fascio puo' o non puo' passarvi sopra, e `perman./dwell` e' la probabilita' che almeno un passaggio cada nella finestra (ipotesi: fase della scansione casuale e uniforme, non modellata ne' verificata su dati). Con g < 1 la Pd scende ma resta > 0, quindi un'estrazione bassa da' comunque **si** (es. `S36-BAND-3`: estrazione 0,0725 con g = 0,5-0,705 -> si; `S36-GRAZE-0/band_min` e `/on`, `casA0`: estrazione 0,0044 -> si). Viceversa con g = 1 un **no** e' solo sfortuna al sorteggio (es. `BAND-0/buk_min` si, `BAND-1/buk_min` no: stessa Pd 0,5, estrazioni diverse). Per leggere una riga si guardano insieme `g`, `Pd` ed `estraz.`; la colonna **rilev.** e' l'esito effettivo del confronto estraz. < Pd. Una regola a soglia netta (nessun rilevamento con perman. < dwell) sarebbe una regola nuova del motore, con interruttore e Proposta separata.

Le righe senza permanenza ne' dwell sono il verso opposto (l'A-10C o l'AWACS come osservatore del sensore, che non dichiara dwell): non sono la legge D-5. `CPA` = Closest Point of Approach, distanza minima fra osservatore e bersaglio lungo le traiettorie.

## S36-BAND (48 esecuzioni)

| Esecuzione              | osservatore -> bersaglio       | portata | CPA     | Pd       | estraz.  | rilev. | istante | perman. | dwell | g        | pass. | inizio | fine |
| ----------------------- | ------------------------------ | ------- | ------- | -------- | -------- | ------ | ------- | ------- | ----- | -------- | ----- | ------ | ---- |
| S36-BAND-0/buk_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.259981 | no     |         |         |       |          |       |        |      |
| S36-BAND-0/buk_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.112504 | 0.466523 | no     |         | 4.5     | 20    | 0.225    |       |        |      |
| S36-BAND-0/buk_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.259981 | no     |         |         |       |          |       |        |      |
| S36-BAND-0/buk_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.500017 | 0.466523 | si     | 126.321 | 4.5     | 4.3   | 1        |       |        |      |
| S36-BAND-0/ffg46_max    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.125    | 0.259981 | no     |         | 2.5     | 10    | 0.25     |       |        |      |
| S36-BAND-0/ffg46_min    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.25     | 0.259981 | no     |         | 2.5     | 5     | 0.5      |       |        |      |
| S36-BAND-0/p37_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.259981 | no     |         |         |       |          |       |        |      |
| S36-BAND-0/p37_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.176251 | 0.466523 | no     |         | 7.05    | 20    | 0.3525   |       |        |      |
| S36-BAND-0/p37_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.259981 | no     |         |         |       |          |       |        |      |
| S36-BAND-0/p37_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.352503 | 0.466523 | no     |         | 7.05    | 10    | 0.705    |       |        |      |
| S36-BAND-0/s300_max     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.259981 | no     |         |         |       |          |       |        |      |
| S36-BAND-0/s300_max     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.250005 | 0.466523 | no     |         | 6       | 12    | 0.5      |       |        |      |
| S36-BAND-0/s300_min     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.259981 | no     |         |         |       |          |       |        |      |
| S36-BAND-0/s300_min     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.50001  | 0.466523 | si     | 125.571 | 6       | 5     | 1        |       |        |      |
| S36-BAND-0/strela10_max | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.259981 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-0/strela10_max | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.133375 | 0.466523 | no     |         | 1.6     | 6     | 0.266667 |       |        |      |
| S36-BAND-0/strela10_min | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.259981 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-0/strela10_min | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.457284 | 0.466523 | no     |         | 1.6     | 1.75  | 0.914286 |       |        |      |
| S36-BAND-0/tor_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.259981 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-0/tor_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.250011 | 0.466523 | no     |         | 1.5     | 3     | 0.5      |       |        |      |
| S36-BAND-0/tor_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.259981 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-0/tor_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.500022 | 0.466523 | si     | 127.821 | 1.5     | 1     | 1        |       |        |      |
| S36-BAND-1/buk_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.410326 | no     |         |         |       |          |       |        |      |
| S36-BAND-1/buk_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.112504 | 0.746018 | no     |         | 4.5     | 20    | 0.225    |       |        |      |
| S36-BAND-1/buk_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.410326 | no     |         |         |       |          |       |        |      |
| S36-BAND-1/buk_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.500017 | 0.746018 | no     |         | 4.5     | 4.3   | 1        |       |        |      |
| S36-BAND-1/ffg46_max    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.125    | 0.410326 | no     |         | 2.5     | 10    | 0.25     |       |        |      |
| S36-BAND-1/ffg46_min    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.25     | 0.410326 | no     |         | 2.5     | 5     | 0.5      |       |        |      |
| S36-BAND-1/p37_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.410326 | no     |         |         |       |          |       |        |      |
| S36-BAND-1/p37_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.176251 | 0.746018 | no     |         | 7.05    | 20    | 0.3525   |       |        |      |
| S36-BAND-1/p37_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.410326 | no     |         |         |       |          |       |        |      |
| S36-BAND-1/p37_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.352503 | 0.746018 | no     |         | 7.05    | 10    | 0.705    |       |        |      |
| S36-BAND-1/s300_max     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.410326 | no     |         |         |       |          |       |        |      |
| S36-BAND-1/s300_max     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.250005 | 0.746018 | no     |         | 6       | 12    | 0.5      |       |        |      |
| S36-BAND-1/s300_min     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.410326 | no     |         |         |       |          |       |        |      |
| S36-BAND-1/s300_min     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.50001  | 0.746018 | no     |         | 6       | 5     | 1        |       |        |      |
| S36-BAND-1/strela10_max | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.410326 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-1/strela10_max | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.133375 | 0.746018 | no     |         | 1.6     | 6     | 0.266667 |       |        |      |
| S36-BAND-1/strela10_min | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.410326 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-1/strela10_min | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.457284 | 0.746018 | no     |         | 1.6     | 1.75  | 0.914286 |       |        |      |
| S36-BAND-1/tor_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.410326 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-1/tor_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.250011 | 0.746018 | no     |         | 1.5     | 3     | 0.5      |       |        |      |
| S36-BAND-1/tor_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.410326 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-1/tor_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.500022 | 0.746018 | no     |         | 1.5     | 1     | 1        |       |        |      |
| S36-BAND-2/buk_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.347676 | no     |         |         |       |          |       |        |      |
| S36-BAND-2/buk_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.112504 | 0.541666 | no     |         | 4.5     | 20    | 0.225    |       |        |      |
| S36-BAND-2/buk_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.347676 | no     |         |         |       |          |       |        |      |
| S36-BAND-2/buk_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.500017 | 0.541666 | no     |         | 4.5     | 4.3   | 1        |       |        |      |
| S36-BAND-2/ffg46_max    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.125    | 0.347676 | no     |         | 2.5     | 10    | 0.25     |       |        |      |
| S36-BAND-2/ffg46_min    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.25     | 0.347676 | no     |         | 2.5     | 5     | 0.5      |       |        |      |
| S36-BAND-2/p37_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.347676 | no     |         |         |       |          |       |        |      |
| S36-BAND-2/p37_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.176251 | 0.541666 | no     |         | 7.05    | 20    | 0.3525   |       |        |      |
| S36-BAND-2/p37_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.347676 | no     |         |         |       |          |       |        |      |
| S36-BAND-2/p37_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.352503 | 0.541666 | no     |         | 7.05    | 10    | 0.705    |       |        |      |
| S36-BAND-2/s300_max     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.347676 | no     |         |         |       |          |       |        |      |
| S36-BAND-2/s300_max     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.250005 | 0.541666 | no     |         | 6       | 12    | 0.5      |       |        |      |
| S36-BAND-2/s300_min     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.347676 | no     |         |         |       |          |       |        |      |
| S36-BAND-2/s300_min     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.50001  | 0.541666 | no     |         | 6       | 5     | 1        |       |        |      |
| S36-BAND-2/strela10_max | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.347676 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-2/strela10_max | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.133375 | 0.541666 | no     |         | 1.6     | 6     | 0.266667 |       |        |      |
| S36-BAND-2/strela10_min | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.347676 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-2/strela10_min | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.457284 | 0.541666 | no     |         | 1.6     | 1.75  | 0.914286 |       |        |      |
| S36-BAND-2/tor_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.347676 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-2/tor_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.250011 | 0.541666 | no     |         | 1.5     | 3     | 0.5      |       |        |      |
| S36-BAND-2/tor_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.347676 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-2/tor_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.500022 | 0.541666 | no     |         | 1.5     | 1     | 1        |       |        |      |
| S36-BAND-3/buk_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.292312 | no     |         |         |       |          |       |        |      |
| S36-BAND-3/buk_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.112504 | 0.072547 | si     | 126.321 | 4.5     | 20    | 0.225    |       |        |      |
| S36-BAND-3/buk_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.292312 | no     |         |         |       |          |       |        |      |
| S36-BAND-3/buk_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.500017 | 0.072547 | si     | 126.321 | 4.5     | 4.3   | 1        |       |        |      |
| S36-BAND-3/ffg46_max    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.125    | 0.292312 | no     |         | 2.5     | 10    | 0.25     |       |        |      |
| S36-BAND-3/ffg46_min    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.25     | 0.292312 | no     |         | 2.5     | 5     | 0.5      |       |        |      |
| S36-BAND-3/p37_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.292312 | no     |         |         |       |          |       |        |      |
| S36-BAND-3/p37_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.176251 | 0.072547 | si     | 125.046 | 7.05    | 20    | 0.3525   |       |        |      |
| S36-BAND-3/p37_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.292312 | no     |         |         |       |          |       |        |      |
| S36-BAND-3/p37_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.352503 | 0.072547 | si     | 125.046 | 7.05    | 10    | 0.705    |       |        |      |
| S36-BAND-3/s300_max     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.292312 | no     |         |         |       |          |       |        |      |
| S36-BAND-3/s300_max     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.250005 | 0.072547 | si     | 125.571 | 6       | 12    | 0.5      |       |        |      |
| S36-BAND-3/s300_min     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.292312 | no     |         |         |       |          |       |        |      |
| S36-BAND-3/s300_min     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.50001  | 0.072547 | si     | 125.571 | 6       | 5     | 1        |       |        |      |
| S36-BAND-3/strela10_max | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.292312 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-3/strela10_max | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.133375 | 0.072547 | si     | 127.771 | 1.6     | 6     | 0.266667 |       |        |      |
| S36-BAND-3/strela10_min | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.292312 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-3/strela10_min | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.457284 | 0.072547 | si     | 127.771 | 1.6     | 1.75  | 0.914286 |       |        |      |
| S36-BAND-3/tor_max      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.292312 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-3/tor_max      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.250011 | 0.072547 | si     | 127.821 | 1.5     | 3     | 0.5      |       |        |      |
| S36-BAND-3/tor_min      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.292312 | si     | 0       |         |       |          |       |        |      |
| S36-BAND-3/tor_min      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.500022 | 0.072547 | si     | 127.821 | 1.5     | 1     | 1        |       |        |      |

## S36-CUT (8 esecuzioni)

| Esecuzione    | osservatore -> bersaglio        | portata | CPA     | Pd       | estraz.  | rilev. | istante | perman. | dwell | g      | pass. | inizio | fine |
| ------------- | ------------------------------- | ------- | ------- | -------- | -------- | ------ | ------- | ------- | ----- | ------ | ----- | ------ | ---- |
| S36-CUT-0/off | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5865.8  | 0.999986 | 0.244263 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-0/off | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5865.8  | 0.543255 | 0.106571 | si     | 119     |         |       |        |       |        |      |
| S36-CUT-0/off | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5600.72 | 0.999988 | 0.257775 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-0/off | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5600.72 | 0.620388 | 0.549288 | si     | 118.146 |         |       |        |       |        |      |
| S36-CUT-0/off | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 4717.41 | 0.999994 | 0.281494 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-0/off | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 4717.41 | 0.808936 | 0.167512 | si     | 110     |         |       |        |       |        |      |
| S36-CUT-0/on  | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5865.8  | 0.999986 | 0.244263 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-0/on  | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5865.8  | 0.169767 | 0.106571 | si     | 119     | 1       | 3.2   | 0.3125 |       |        |      |
| S36-CUT-0/on  | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5600.72 | 0.999988 | 0.257775 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-0/on  | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5600.72 | 0.581614 | 0.549288 | si     | 119.067 | 3       | 3.2   | 0.9375 |       |        |      |
| S36-CUT-0/on  | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 4717.41 | 0.999994 | 0.281494 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-0/on  | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 4717.41 | 0.808936 | 0.167512 | si     | 110     | 10      | 3.2   | 1      |       |        |      |
| S36-CUT-1/off | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5865.8  | 0.999986 | 0.953288 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-1/off | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5865.8  | 0.543255 | 0.715424 | no     |         |         |       |        |       |        |      |
| S36-CUT-1/off | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5600.72 | 0.999988 | 0.631439 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-1/off | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5600.72 | 0.620388 | 0.026312 | si     | 117     |         |       |        |       |        |      |
| S36-CUT-1/off | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 4717.41 | 0.999994 | 0.408484 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-1/off | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 4717.41 | 0.808936 | 0.69959  | si     | 115.453 |         |       |        |       |        |      |
| S36-CUT-1/on  | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5865.8  | 0.999986 | 0.953288 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-1/on  | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5865.8  | 0.169767 | 0.715424 | no     |         | 1       | 3.2   | 0.3125 |       |        |      |
| S36-CUT-1/on  | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5600.72 | 0.999988 | 0.631439 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-1/on  | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5600.72 | 0.581614 | 0.026312 | si     | 117     | 3       | 3.2   | 0.9375 |       |        |      |
| S36-CUT-1/on  | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 4717.41 | 0.999994 | 0.408484 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-1/on  | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 4717.41 | 0.808936 | 0.69959  | si     | 115.453 | 10      | 3.2   | 1      |       |        |      |
| S36-CUT-2/off | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5865.8  | 0.999986 | 0.483627 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-2/off | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5865.8  | 0.543255 | 0.13384  | si     | 119     |         |       |        |       |        |      |
| S36-CUT-2/off | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5600.72 | 0.999988 | 0.130538 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-2/off | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5600.72 | 0.620388 | 0.809292 | no     |         |         |       |        |       |        |      |
| S36-CUT-2/off | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 4717.41 | 0.999994 | 0.451253 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-2/off | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 4717.41 | 0.808936 | 0.243098 | si     | 110     |         |       |        |       |        |      |
| S36-CUT-2/on  | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5865.8  | 0.999986 | 0.483627 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-2/on  | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5865.8  | 0.169767 | 0.13384  | si     | 119     | 1       | 3.2   | 0.3125 |       |        |      |
| S36-CUT-2/on  | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5600.72 | 0.999988 | 0.130538 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-2/on  | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5600.72 | 0.581614 | 0.809292 | no     |         | 3       | 3.2   | 0.9375 |       |        |      |
| S36-CUT-2/on  | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 4717.41 | 0.999994 | 0.451253 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-2/on  | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 4717.41 | 0.808936 | 0.243098 | si     | 110     | 10      | 3.2   | 1      |       |        |      |
| S36-CUT-3/off | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5865.8  | 0.999986 | 0.313691 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-3/off | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5865.8  | 0.543255 | 0.785269 | no     |         |         |       |        |       |        |      |
| S36-CUT-3/off | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5600.72 | 0.999988 | 0.078415 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-3/off | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5600.72 | 0.620388 | 0.316395 | si     | 117     |         |       |        |       |        |      |
| S36-CUT-3/off | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 4717.41 | 0.999994 | 0.574226 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-3/off | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 4717.41 | 0.808936 | 0.444709 | si     | 110     |         |       |        |       |        |      |
| S36-CUT-3/on  | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5865.8  | 0.999986 | 0.313691 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-3/on  | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5865.8  | 0.169767 | 0.785269 | no     |         | 1       | 3.2   | 0.3125 |       |        |      |
| S36-CUT-3/on  | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5600.72 | 0.999988 | 0.078415 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-3/on  | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5600.72 | 0.581614 | 0.316395 | si     | 117     | 3       | 3.2   | 0.9375 |       |        |      |
| S36-CUT-3/on  | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 4717.41 | 0.999994 | 0.574226 | si     | 0       |         |       |        |       |        |      |
| S36-CUT-3/on  | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 4717.41 | 0.808936 | 0.444709 | si     | 110     | 10      | 3.2   | 1      |       |        |      |

## S36-FAMILIES (28 esecuzioni)

| Esecuzione              | osservatore -> bersaglio       | portata | CPA     | Pd       | estraz.  | rilev. | istante | perman. | dwell | g   | pass. | inizio | fine |
| ----------------------- | ------------------------------ | ------- | ------- | -------- | -------- | ------ | ------- | ------- | ----- | --- | ----- | ------ | ---- |
| S36-FAMILIES-0/buk      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.73118  | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-0/buk      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.250008 | 0.602441 | no     |         | 4.5     | 9     | 0.5 |       |        |      |
| S36-FAMILIES-0/e3a      | Blue-AEW/obs0 -> Red-Air/tgt0  | 400000  | 399998  | 0.250004 | 0.736305 | no     |         | 5       | 10    | 0.5 |       |        |      |
| S36-FAMILIES-0/e3a      | Red-Air/tgt0 -> Blue-AEW/obs0  | 80000   | 399998  | 0        | 0.938062 | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-0/ffg46    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.25     | 0.73118  | no     |         | 2.5     | 5     | 0.5 |       |        |      |
| S36-FAMILIES-0/p37      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.73118  | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-0/p37      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.250002 | 0.602441 | no     |         | 7.05    | 14.1  | 0.5 |       |        |      |
| S36-FAMILIES-0/s300     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.73118  | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-0/s300     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.250005 | 0.602441 | no     |         | 6       | 12    | 0.5 |       |        |      |
| S36-FAMILIES-0/strela10 | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.73118  | si     | 0       |         |       |     |       |        |      |
| S36-FAMILIES-0/strela10 | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.250077 | 0.602441 | no     |         | 1.6     | 3.2   | 0.5 |       |        |      |
| S36-FAMILIES-0/tor      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.73118  | si     | 0       |         |       |     |       |        |      |
| S36-FAMILIES-0/tor      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.250011 | 0.602441 | no     |         | 1.5     | 3     | 0.5 |       |        |      |
| S36-FAMILIES-1/buk      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.669092 | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-1/buk      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.250008 | 0.267076 | no     |         | 4.5     | 9     | 0.5 |       |        |      |
| S36-FAMILIES-1/e3a      | Blue-AEW/obs0 -> Red-Air/tgt0  | 400000  | 399998  | 0.250004 | 0.583182 | no     |         | 5       | 10    | 0.5 |       |        |      |
| S36-FAMILIES-1/e3a      | Red-Air/tgt0 -> Blue-AEW/obs0  | 80000   | 399998  | 0        | 0.227845 | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-1/ffg46    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.25     | 0.669092 | no     |         | 2.5     | 5     | 0.5 |       |        |      |
| S36-FAMILIES-1/p37      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.669092 | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-1/p37      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.250002 | 0.267076 | no     |         | 7.05    | 14.1  | 0.5 |       |        |      |
| S36-FAMILIES-1/s300     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.669092 | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-1/s300     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.250005 | 0.267076 | no     |         | 6       | 12    | 0.5 |       |        |      |
| S36-FAMILIES-1/strela10 | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.669092 | si     | 0       |         |       |     |       |        |      |
| S36-FAMILIES-1/strela10 | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.250077 | 0.267076 | no     |         | 1.6     | 3.2   | 0.5 |       |        |      |
| S36-FAMILIES-1/tor      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.669092 | si     | 0       |         |       |     |       |        |      |
| S36-FAMILIES-1/tor      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.250011 | 0.267076 | no     |         | 1.5     | 3     | 0.5 |       |        |      |
| S36-FAMILIES-2/buk      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.38071  | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-2/buk      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.250008 | 0.521011 | no     |         | 4.5     | 9     | 0.5 |       |        |      |
| S36-FAMILIES-2/e3a      | Blue-AEW/obs0 -> Red-Air/tgt0  | 400000  | 399998  | 0.250004 | 0.218937 | si     | 197.5   | 5       | 10    | 0.5 |       |        |      |
| S36-FAMILIES-2/e3a      | Red-Air/tgt0 -> Blue-AEW/obs0  | 80000   | 399998  | 0        | 0.742975 | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-2/ffg46    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.25     | 0.38071  | no     |         | 2.5     | 5     | 0.5 |       |        |      |
| S36-FAMILIES-2/p37      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.38071  | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-2/p37      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.250002 | 0.521011 | no     |         | 7.05    | 14.1  | 0.5 |       |        |      |
| S36-FAMILIES-2/s300     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.38071  | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-2/s300     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.250005 | 0.521011 | no     |         | 6       | 12    | 0.5 |       |        |      |
| S36-FAMILIES-2/strela10 | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.38071  | si     | 0       |         |       |     |       |        |      |
| S36-FAMILIES-2/strela10 | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.250077 | 0.521011 | no     |         | 1.6     | 3.2   | 0.5 |       |        |      |
| S36-FAMILIES-2/tor      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.38071  | si     | 0       |         |       |     |       |        |      |
| S36-FAMILIES-2/tor      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.250011 | 0.521011 | no     |         | 1.5     | 3     | 0.5 |       |        |      |
| S36-FAMILIES-3/buk      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 84999.3 | 0        | 0.94859  | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-3/buk      | Red-Line/obs0 -> Blue-CAS/cas0 | 85000   | 84999.3 | 0.250008 | 0.990993 | no     |         | 4.5     | 9     | 0.5 |       |        |      |
| S36-FAMILIES-3/e3a      | Blue-AEW/obs0 -> Red-Air/tgt0  | 400000  | 399998  | 0.250004 | 0.187028 | si     | 197.5   | 5       | 10    | 0.5 |       |        |      |
| S36-FAMILIES-3/e3a      | Red-Air/tgt0 -> Blue-AEW/obs0  | 80000   | 399998  | 0        | 0.238207 | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-3/ffg46    | Red-Line/obs0 -> Blue-CAS/cas0 | 350000  | 350000  | 0.25     | 0.94859  | no     |         | 2.5     | 5     | 0.5 |       |        |      |
| S36-FAMILIES-3/p37      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 279999  | 0        | 0.94859  | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-3/p37      | Red-Line/obs0 -> Blue-CAS/cas0 | 280000  | 279999  | 0.250002 | 0.990993 | no     |         | 7.05    | 14.1  | 0.5 |       |        |      |
| S36-FAMILIES-3/s300     | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 149999  | 0        | 0.94859  | no     |         |         |       |     |       |        |      |
| S36-FAMILIES-3/s300     | Red-Line/obs0 -> Blue-CAS/cas0 | 150000  | 149999  | 0.250005 | 0.990993 | no     |         | 6       | 12    | 0.5 |       |        |      |
| S36-FAMILIES-3/strela10 | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 9999.23 | 0.999878 | 0.94859  | si     | 0       |         |       |     |       |        |      |
| S36-FAMILIES-3/strela10 | Red-Line/obs0 -> Blue-CAS/cas0 | 10000   | 9999.23 | 0.250077 | 0.990993 | no     |         | 1.6     | 3.2   | 0.5 |       |        |      |
| S36-FAMILIES-3/tor      | Blue-CAS/cas0 -> Red-Line/obs0 | 80000   | 24999.7 | 0.995232 | 0.94859  | si     | 0       |         |       |     |       |        |      |
| S36-FAMILIES-3/tor      | Red-Line/obs0 -> Blue-CAS/cas0 | 25000   | 24999.7 | 0.250011 | 0.990993 | no     |         | 1.5     | 3     | 0.5 |       |        |      |

## S36-GRAZE (16 esecuzioni)

| Esecuzione           | osservatore -> bersaglio        | portata | CPA     | Pd       | estraz.  | rilev. | istante | perman. | dwell | g        | pass. | inizio | fine |
| -------------------- | ------------------------------- | ------- | ------- | -------- | -------- | ------ | ------- | ------- | ----- | -------- | ----- | ------ | ---- |
| S36-GRAZE-0/band_max | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.963558 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/band_max | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.133448 | 0.004447 | si     | 256.343 | 1.6     | 6     | 0.266667 |       |        |      |
| S36-GRAZE-0/band_max | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.32566  | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/band_max | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.240669 | 0.432789 | no     |         | 2.88    | 6     | 0.48     |       |        |      |
| S36-GRAZE-0/band_max | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.648817 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/band_max | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.294554 | 0.659254 | no     |         | 3.52    | 6     | 0.586667 |       |        |      |
| S36-GRAZE-0/band_max | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.115436 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/band_max | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.712609 | no     |         | 6.4     | 6     | 1        |       |        |      |
| S36-GRAZE-0/band_min | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.963558 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/band_min | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.457536 | 0.004447 | si     | 256.343 | 1.6     | 1.75  | 0.914286 |       |        |      |
| S36-GRAZE-0/band_min | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.32566  | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/band_min | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.501393 | 0.432789 | si     | 255.703 | 2.88    | 1.75  | 1        |       |        |      |
| S36-GRAZE-0/band_min | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.648817 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/band_min | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.659254 | no     |         | 3.52    | 1.75  | 1        |       |        |      |
| S36-GRAZE-0/band_min | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.115436 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/band_min | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.712609 | no     |         | 6.4     | 1.75  | 1        |       |        |      |
| S36-GRAZE-0/off      | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.963558 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/off      | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.50043  | 0.004447 | si     | 256.343 |         |       |          |       |        |      |
| S36-GRAZE-0/off      | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.32566  | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/off      | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.501393 | 0.432789 | si     | 255.703 |         |       |          |       |        |      |
| S36-GRAZE-0/off      | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.648817 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/off      | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.659254 | no     |         |         |       |          |       |        |      |
| S36-GRAZE-0/off      | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.115436 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/off      | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.712609 | no     |         |         |       |          |       |        |      |
| S36-GRAZE-0/on       | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.963558 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/on       | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.250215 | 0.004447 | si     | 256.343 | 1.6     | 3.2   | 0.5      |       |        |      |
| S36-GRAZE-0/on       | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.32566  | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/on       | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.451254 | 0.432789 | si     | 255.703 | 2.88    | 3.2   | 0.9      |       |        |      |
| S36-GRAZE-0/on       | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.648817 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/on       | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.659254 | no     |         | 3.52    | 3.2   | 1        |       |        |      |
| S36-GRAZE-0/on       | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.115436 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-0/on       | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.712609 | no     |         | 6.4     | 3.2   | 1        |       |        |      |
| S36-GRAZE-1/band_max | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.45953  | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/band_max | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.133448 | 0.378597 | no     |         | 1.6     | 6     | 0.266667 |       |        |      |
| S36-GRAZE-1/band_max | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.693601 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/band_max | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.240669 | 0.328331 | no     |         | 2.88    | 6     | 0.48     |       |        |      |
| S36-GRAZE-1/band_max | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.151199 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/band_max | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.294554 | 0.058029 | si     | 255.383 | 3.52    | 6     | 0.586667 |       |        |      |
| S36-GRAZE-1/band_max | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.564183 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/band_max | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.903962 | no     |         | 6.4     | 6     | 1        |       |        |      |
| S36-GRAZE-1/band_min | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.45953  | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/band_min | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.457536 | 0.378597 | si     | 256.343 | 1.6     | 1.75  | 0.914286 |       |        |      |
| S36-GRAZE-1/band_min | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.693601 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/band_min | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.501393 | 0.328331 | si     | 255.703 | 2.88    | 1.75  | 1        |       |        |      |
| S36-GRAZE-1/band_min | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.151199 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/band_min | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.058029 | si     | 255.383 | 3.52    | 1.75  | 1        |       |        |      |
| S36-GRAZE-1/band_min | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.564183 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/band_min | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.903962 | no     |         | 6.4     | 1.75  | 1        |       |        |      |
| S36-GRAZE-1/off      | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.45953  | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/off      | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.50043  | 0.378597 | si     | 256.343 |         |       |          |       |        |      |
| S36-GRAZE-1/off      | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.693601 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/off      | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.501393 | 0.328331 | si     | 255.703 |         |       |          |       |        |      |
| S36-GRAZE-1/off      | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.151199 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/off      | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.058029 | si     | 255.383 |         |       |          |       |        |      |
| S36-GRAZE-1/off      | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.564183 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/off      | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.903962 | no     |         |         |       |          |       |        |      |
| S36-GRAZE-1/on       | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.45953  | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/on       | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.250215 | 0.378597 | no     |         | 1.6     | 3.2   | 0.5      |       |        |      |
| S36-GRAZE-1/on       | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.693601 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/on       | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.451254 | 0.328331 | si     | 255.703 | 2.88    | 3.2   | 0.9      |       |        |      |
| S36-GRAZE-1/on       | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.151199 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/on       | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.058029 | si     | 255.383 | 3.52    | 3.2   | 1        |       |        |      |
| S36-GRAZE-1/on       | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.564183 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-1/on       | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.903962 | no     |         | 6.4     | 3.2   | 1        |       |        |      |
| S36-GRAZE-2/band_max | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.592471 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/band_max | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.133448 | 0.998711 | no     |         | 1.6     | 6     | 0.266667 |       |        |      |
| S36-GRAZE-2/band_max | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.838105 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/band_max | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.240669 | 0.50758  | no     |         | 2.88    | 6     | 0.48     |       |        |      |
| S36-GRAZE-2/band_max | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.037694 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/band_max | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.294554 | 0.454095 | no     |         | 3.52    | 6     | 0.586667 |       |        |      |
| S36-GRAZE-2/band_max | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.794459 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/band_max | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.09289  | si     | 253.943 | 6.4     | 6     | 1        |       |        |      |
| S36-GRAZE-2/band_min | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.592471 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/band_min | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.457536 | 0.998711 | no     |         | 1.6     | 1.75  | 0.914286 |       |        |      |
| S36-GRAZE-2/band_min | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.838105 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/band_min | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.501393 | 0.50758  | no     |         | 2.88    | 1.75  | 1        |       |        |      |
| S36-GRAZE-2/band_min | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.037694 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/band_min | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.454095 | si     | 255.383 | 3.52    | 1.75  | 1        |       |        |      |
| S36-GRAZE-2/band_min | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.794459 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/band_min | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.09289  | si     | 253.943 | 6.4     | 1.75  | 1        |       |        |      |
| S36-GRAZE-2/off      | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.592471 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/off      | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.50043  | 0.998711 | no     |         |         |       |          |       |        |      |
| S36-GRAZE-2/off      | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.838105 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/off      | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.501393 | 0.50758  | no     |         |         |       |          |       |        |      |
| S36-GRAZE-2/off      | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.037694 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/off      | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.454095 | si     | 255.383 |         |       |          |       |        |      |
| S36-GRAZE-2/off      | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.794459 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/off      | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.09289  | si     | 253.943 |         |       |          |       |        |      |
| S36-GRAZE-2/on       | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.592471 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/on       | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.250215 | 0.998711 | no     |         | 1.6     | 3.2   | 0.5      |       |        |      |
| S36-GRAZE-2/on       | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.838105 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/on       | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.451254 | 0.50758  | no     |         | 2.88    | 3.2   | 0.9      |       |        |      |
| S36-GRAZE-2/on       | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.037694 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/on       | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.454095 | si     | 255.383 | 3.52    | 3.2   | 1        |       |        |      |
| S36-GRAZE-2/on       | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.794459 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-2/on       | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.09289  | si     | 253.943 | 6.4     | 3.2   | 1        |       |        |      |
| S36-GRAZE-3/band_max | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.562909 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/band_max | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.133448 | 0.843351 | no     |         | 1.6     | 6     | 0.266667 |       |        |      |
| S36-GRAZE-3/band_max | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.543745 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/band_max | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.240669 | 0.578597 | no     |         | 2.88    | 6     | 0.48     |       |        |      |
| S36-GRAZE-3/band_max | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.763238 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/band_max | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.294554 | 0.720493 | no     |         | 3.52    | 6     | 0.586667 |       |        |      |
| S36-GRAZE-3/band_max | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.594852 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/band_max | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.286202 | si     | 253.943 | 6.4     | 6     | 1        |       |        |      |
| S36-GRAZE-3/band_min | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.562909 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/band_min | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.457536 | 0.843351 | no     |         | 1.6     | 1.75  | 0.914286 |       |        |      |
| S36-GRAZE-3/band_min | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.543745 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/band_min | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.501393 | 0.578597 | no     |         | 2.88    | 1.75  | 1        |       |        |      |
| S36-GRAZE-3/band_min | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.763238 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/band_min | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.720493 | no     |         | 3.52    | 1.75  | 1        |       |        |      |
| S36-GRAZE-3/band_min | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.594852 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/band_min | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.286202 | si     | 253.943 | 6.4     | 1.75  | 1        |       |        |      |
| S36-GRAZE-3/off      | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.562909 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/off      | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.50043  | 0.843351 | no     |         |         |       |          |       |        |      |
| S36-GRAZE-3/off      | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.543745 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/off      | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.501393 | 0.578597 | no     |         |         |       |          |       |        |      |
| S36-GRAZE-3/off      | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.763238 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/off      | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.720493 | no     |         |         |       |          |       |        |      |
| S36-GRAZE-3/off      | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.594852 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/off      | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.286202 | si     | 253.943 |         |       |          |       |        |      |
| S36-GRAZE-3/on       | Blue-CAS/casA0 -> Red-Line/obs0 | 80000   | 5998.71 | 0.999984 | 0.562909 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/on       | Red-Line/obs0 -> Blue-CAS/casA0 | 6000    | 5998.71 | 0.250215 | 0.843351 | no     |         | 1.6     | 3.2   | 0.5      |       |        |      |
| S36-GRAZE-3/on       | Blue-CAS/casB0 -> Red-Line/obs0 | 80000   | 5995.82 | 0.999984 | 0.543745 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/on       | Red-Line/obs0 -> Blue-CAS/casB0 | 6000    | 5995.82 | 0.451254 | 0.578597 | no     |         | 2.88    | 3.2   | 0.9      |       |        |      |
| S36-GRAZE-3/on       | Blue-CAS/casC0 -> Red-Line/obs0 | 80000   | 5993.75 | 0.999984 | 0.763238 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/on       | Red-Line/obs0 -> Blue-CAS/casC0 | 6000    | 5993.75 | 0.50208  | 0.720493 | no     |         | 3.52    | 3.2   | 1        |       |        |      |
| S36-GRAZE-3/on       | Blue-CAS/casD0 -> Red-Line/obs0 | 80000   | 5979.32 | 0.999984 | 0.594852 | si     | 0       |         |       |          |       |        |      |
| S36-GRAZE-3/on       | Red-Line/obs0 -> Blue-CAS/casD0 | 6000    | 5979.32 | 0.506859 | 0.286202 | si     | 253.943 | 6.4     | 3.2   | 1        |       |        |      |

## S36-PASSES (16 esecuzioni)

| Esecuzione | osservatore -> bersaglio | portata | CPA | Pd | estraz. | rilev. | istante | perman. | dwell | g | pass. | inizio | fine |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S36-PASSES-0/join_off | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.593705 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-0/join_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.678256 | no |  |  |  |  | 0/2 | 128.071 | 129.071 |
| S36-PASSES-0/join_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.030783 | si | 130.071 |  |  |  | 1/2 | 130.071 | 131.071 |
| S36-PASSES-0/join_on | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.593705 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-0/join_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.468908 | 0.678256 | no |  | 3 | 3.2 | 0.9375 |  |  |  |
| S36-PASSES-0/split_off | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.593705 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-0/split_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.678256 | no |  |  |  |  | 0/2 | 128.071 | 129.071 |
| S36-PASSES-0/split_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.030783 | si | 134.071 |  |  |  | 1/2 | 134.071 | 135.071 |
| S36-PASSES-0/split_on | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.593705 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-0/split_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.156303 | 0.678256 | no |  | 1 | 3.2 | 0.3125 | 0/2 | 128.071 | 129.071 |
| S36-PASSES-0/split_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.156303 | 0.030783 | si | 134.071 | 1 | 3.2 | 0.3125 | 1/2 | 134.071 | 135.071 |
| S36-PASSES-1/join_off | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.730633 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-1/join_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.229612 | si | 128.071 |  |  |  | 0/2 | 128.071 | 129.071 |
| S36-PASSES-1/join_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.531807 | no |  |  |  |  | 1/2 | 130.071 | 131.071 |
| S36-PASSES-1/join_on | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.730633 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-1/join_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.468908 | 0.229612 | si | 128.071 | 3 | 3.2 | 0.9375 |  |  |  |
| S36-PASSES-1/split_off | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.730633 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-1/split_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.229612 | si | 128.071 |  |  |  | 0/2 | 128.071 | 129.071 |
| S36-PASSES-1/split_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.531807 | no |  |  |  |  | 1/2 | 134.071 | 135.071 |
| S36-PASSES-1/split_on | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.730633 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-1/split_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.156303 | 0.229612 | no |  | 1 | 3.2 | 0.3125 | 0/2 | 128.071 | 129.071 |
| S36-PASSES-1/split_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.156303 | 0.531807 | no |  | 1 | 3.2 | 0.3125 | 1/2 | 134.071 | 135.071 |
| S36-PASSES-2/join_off | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.276834 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-2/join_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.060952 | si | 128.071 |  |  |  | 0/2 | 128.071 | 129.071 |
| S36-PASSES-2/join_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.60542 | no |  |  |  |  | 1/2 | 130.071 | 131.071 |
| S36-PASSES-2/join_on | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.276834 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-2/join_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.468908 | 0.060952 | si | 128.071 | 3 | 3.2 | 0.9375 |  |  |  |
| S36-PASSES-2/split_off | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.276834 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-2/split_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.060952 | si | 128.071 |  |  |  | 0/2 | 128.071 | 129.071 |
| S36-PASSES-2/split_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.60542 | no |  |  |  |  | 1/2 | 134.071 | 135.071 |
| S36-PASSES-2/split_on | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.276834 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-2/split_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.156303 | 0.060952 | si | 128.071 | 1 | 3.2 | 0.3125 | 0/2 | 128.071 | 129.071 |
| S36-PASSES-2/split_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.156303 | 0.60542 | no |  | 1 | 3.2 | 0.3125 | 1/2 | 134.071 | 135.071 |
| S36-PASSES-3/join_off | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.668871 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-3/join_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.626416 | no |  |  |  |  | 0/2 | 128.071 | 129.071 |
| S36-PASSES-3/join_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.295008 | si | 130.071 |  |  |  | 1/2 | 130.071 | 131.071 |
| S36-PASSES-3/join_on | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.668871 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-3/join_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.468908 | 0.626416 | no |  | 3 | 3.2 | 0.9375 |  |  |  |
| S36-PASSES-3/split_off | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.668871 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-3/split_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.626416 | no |  |  |  |  | 0/2 | 128.071 | 129.071 |
| S36-PASSES-3/split_off | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.500168 | 0.295008 | si | 134.071 |  |  |  | 1/2 | 134.071 | 135.071 |
| S36-PASSES-3/split_on | Blue-CAS/cas0 -> Red-Line/obs0 | 80000 | 5999.5 | 0.999984 | 0.668871 | si | 0 |  |  |  |  |  |  |
| S36-PASSES-3/split_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.156303 | 0.626416 | no |  | 1 | 3.2 | 0.3125 | 0/2 | 128.071 | 129.071 |
| S36-PASSES-3/split_on | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999.5 | 0.156303 | 0.295008 | no |  | 1 | 3.2 | 0.3125 | 1/2 | 134.071 | 135.071 |

