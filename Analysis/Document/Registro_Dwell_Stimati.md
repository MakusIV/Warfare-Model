# Registro dei dwell stimati da aggiornare (D-5, DW-9 rivista)

Creato il 2026-11-18 (blocco 1 della Proposta); le date delle righe sono quelle delle decisioni (2026-11-17).

Periodi di rivisita (`dwell_time_s`, funzione di RICERCA) dei registri che NON sono dati di fonte verificati.
Origine: `Proposta_Dwell_Estensione_DW9.md` (decisioni DW9-1..DW9-9). Copia per i test: costanti `DWELL_S`/
`DWELL_ESTIMATED`/`NO_DWELL` di `Code/Dynamic_War_Manager/Source/Test/Test_Dwell_Data.py` (vanno aggiornate insieme).
Valore FISSO per sensore (nessuna dipendenza da distanza, modo o carico del radar: rinvio dichiarato, Proposta §3.4).
Intervalli di fonte: regime normale se citato, altrimenti valore centrale (media geometrica degli estremi del periodo);
la "banda di incertezza" e' l'intervallo di fonte o degli analoghi. Etichette: FONTE NON VERIFICATA [S] |
FONTE DEBOLE [S] | STIMA PER CONFRONTO [S] | FONTE, interpretazione/attribuzione [S].
Per chiudere una riga: fonte leggibile -> etichetta FONTE nel commento del registro, riga tolta da qui e da
`DWELL_ESTIMATED`; valore o banda cambiati -> registro, test, questo file e sonda S-4.

| Record | Sensore (funzione di ricerca) | Valore [s] | Banda di incertezza [s] | Etichetta | Base | Che cosa serve per chiuderla | Data |
|---|---|---|---|---|---|---|---|
| ZSU-23-4-Shilka | radar (1RL33, ricerca) | 7.3 | 3-18 | FONTE di variante, valore centrale, attribuzione [S] | manuale 1RL33M3 (ZSU-23-4M): circolare 18 s, accelerata 8-6 s, settore 3-10 s; centrale (DW9-3) | dato del 1RL33 base (1965) e del suo regime normale | 2026-11-17 |
| 2K22-Tunguska | radar (1RL144) | 1.82 | 1.0-4.0 | STIMA PER CONFRONTO [S] | 9A33-Osa Land Roll, 33 giri/min (analoghi: Gepard 1 s, Pantsir 2-4 s) | giri/min del 1RL144 (manuale 2S6) | 2026-11-17 |
| 9K37-Buk | radar (ricerca 9S18) | 9.0 | 4.3-20 | FONTE NON VERIFICATA [S], valore centrale | GlobalSecurity 9s18.htm (403), circolare 4,5-18 s; 3-14 giri/min radartutorial via ricerca | frase di fonte leggibile (GlobalSecurity, Jane's) | 2026-11-17 |
| S-300PS | radar (ricerca 5N64S) | 12.0 | 5-12 | STIMA PER CONFRONTO [S] | 64N6/64N6E, rotazione ogni 12 s regolare (GlobalSecurity non verificato; P1: 6/12 giri/min) | giri/min del 5N64S | 2026-11-17 |
| Strela-1-9P31 | TVD (vista del servente) | 3.2 | 1.75-6.0 | STIMA PER CONFRONTO [S], valore centrale, APPROSSIMAZIONE L1 | Poe 1974, passata del settore 1,75-6,00 s | legge cumulativa (Koopman) o tempo di scoperta misurato | 2026-11-17 |
| MIM-72G-Chaparral | TVD (vista del servente) | 3.2 | 1.75-6.0 | idem | idem | idem | 2026-11-17 |
| 9K35-Strela-10 | TVD (vista del servente) | 3.2 | 1.75-6.0 | idem | idem | idem | 2026-11-17 |
| M6-Linebacker | TVD (vista del servente) | 3.2 | 1.75-6.0 | idem | idem | idem; cueing radar non modellato | 2026-11-17 |
| ZSU-57-2 | visual | 3.2 | 1.75-6.0 | idem | idem | idem | 2026-11-17 |
| M163-VADS | visual | 3.2 | 1.75-6.0 | idem | idem | idem | 2026-11-17 |
| FuMG-80-Freya | radar | 60.0 | 30-60 | STIMA PER CONFRONTO [S] | SCR-270, 1 giro/min (analogo alternativo AMES Type 7, 30 s dopo DW9-10) | velocita' di rotazione del Freya | 2026-11-17 |
| Wassermann | radar | 60.0 | 30-60 | STIMA PER CONFRONTO [S] | SCR-270, 1 giro/min (analogo alternativo AMES Type 7, 30 s dopo DW9-10) | velocita' di rotazione del Wassermann | 2026-11-17 |
| AN-FPS-117 | radar | 10.0 | — | STIMA PER CONFRONTO [S] | AN-TPS-43, 6 giri/min | giri/min dell'AN/FPS-117 da fonte leggibile | 2026-11-17 |
| CV-59 USS Forrestal | radar (AN/SPS-43) | 5.0 | 5-10 | STIMA PER CONFRONTO [S] | AN/SPS-49 | giri/min dell'AN/SPS-43 | 2026-11-17 |
| USS Arleigh Burke IIa | radar (AN/SPY-1D) | 5.0 | 5-60 | FONTE DEBOLE [S] | infobox "1 (orizzonte), 12 (sopra l'orizzonte) scan/min" | periodo di volume search dichiarato | 2026-11-17 |
| Type 052B Guangzhou-class | radar (Type 381) | 7.1 | 5-10 | STIMA PER CONFRONTO [S] | Fregat-MA (valore centrale) | giri/min del Type 381 | 2026-11-17 |
| Type 052C | radar (Type 346) | 5.0 | 5-60 | STIMA PER CONFRONTO [S] | AN/SPY-1 | periodo di rivisita del Type 346 | 2026-11-17 |
| CG-65 | radar (AN/SPY-1A) | 5.0 | 5-60 | FONTE DEBOLE [S] | infobox "1 (orizzonte), 12 (sopra l'orizzonte) scan/min" | periodo di volume search dichiarato | 2026-11-17 |
| FF 1135M Rezky | radar (Head Net-C) | 7.1 | 5-10 | STIMA PER CONFRONTO [S] | Head Net-A (MR-310), 6/12 giri/min, valore centrale | giri/min dell'MR-310U | 2026-11-17 |
| Type 054A | radar (Type 382) | 2.0 | 2-10 | FONTE DEBOLE [S] | forum, ~30 giri/min (alternativa Fregat MAE-3 7,1 s) | fonte tecnica | 2026-11-17 |
| FFL 1124.4 Grisha | radar (MR-302 Strut Curve) | 7.1 | 5-10 | STIMA PER CONFRONTO [S] | Head Net-A (valore centrale) | giri/min dell'MR-302 | 2026-11-17 |
| FSG 1241.1MP Molniya | radar (record con Band Stand, radar di tiro) | 7.1 | 5-10 | STIMA PER CONFRONTO [S] | Head Net-A (valore centrale) | radar di ricerca della corvetta e suoi giri/min | 2026-11-17 |
| LHA-1 Tarawa | radar (AN/SPS-52) | 5.0 | 5-10 | STIMA PER CONFRONTO [S] | AN/SPS-49 | giri/min dell'AN/SPS-52 | 2026-11-17 |
| A-50 | radar (Shmel) | 10.0 | — | FONTE DEBOLE [S] | divulgativo "circa sei giri al minuto" | seconda fonte o fonte tecnica | 2026-11-17 |
| AMES-Type-80 | radar | 15.0 | 10-15 | FONTE, interpretazione [S] (regime base letto come normale) | "4 giri/min (fino a 6)" | fonte che dica il regime normale | 2026-11-17 |

**Valori di fonte scelti con la regola del valore centrale** (stima per scelta di regola dentro un intervallo di
fonte, NON per mancanza di dato; si chiudono con una fonte che citi il regime normale):

| Record | Sensore | Valore [s] | Banda di incertezza [s] | Intervallo di fonte | Data |
|---|---|---|---|---|---|
| 2K12-Kub | radar (1S11) | 3.5 | 3-4 | 15 o 20 giri/min (radartutorial) | 2026-11-17 |
| CV 1143.5 Admiral Kuznetsov | radar (Fregat-MA) | 7.1 | 5-10 | 12 o 6 giri/min | 2026-11-17 |
| FFG 11540 Neustrashimy | radar (Fregat-MA) | 7.1 | 5-10 | 12 o 6 giri/min | 2026-11-17 |
| CGN 1144.2 Piotr Velikiy | radar (Fregat-MA; Top Pair) | 7.1 | 5-20 | 12 o 6 giri/min; Top Pair 3-12 | 2026-11-17 |
| CG 1164 Moskva | radar (MR-800 Top Pair) | 10.0 | 5-20 | 3-12 giri/min | 2026-11-17 |
| P-37-Mech | radar | 14.1 | 10-20 | 3-6 giri/min (DW9-10; era 10 s con DW-2) | 2026-11-17 |
| 1L13-Nebo-SV | radar | 14.1 | 10-20 | 3-6 giri/min (DW9-10; era 10 s) | 2026-11-17 |
| AMES-Type-7 | radar | 30.0 | 7.5-120 | 0,5-8 giri/min (DW9-10; era 7,5 s) | 2026-11-17 |
| P-14-Lena | radar | 17.3 | 10-30 | 2-6 giri/min (DW9-10; era 10 s) | 2026-11-17 |

Fonti discordanti: P-12-Yenisei 6.0, banda 6-30 (fonte principale [W-P12] 10 giri/min, scelta dell'utente; [AC-P12]
2-6 giri/min solo nella banda); si chiude con una fonte che risolva la discordanza.

Bande degli altri valori di fonte (regime normale citato): 9K331-Tor 3.0 (1-3, "main mode", testo GlobalSecurity
incollato dall'utente); CVN-70..75 e FFG-46 5.0 (5-10, default 12 giri/min). Gli altri valori di fonte sono valori
unici.

Senza valore (motivo): Chain-Home (illuminazione continua); Mammut (schiera fissa, cadenza non data, nessun analogo);
Type 093 (sonar passivo). Aerei non AWACS: esclusi per decisione dell'utente.

Rinviato (non e' una stima da chiudere, e' un modello da fare): dwell dipendente da distanza, modo e carico del radar,
insieme all'orizzonte radar nel DES e a una legge cumulativa (Koopman/esponenziale); riferimento qualitativo
`Dinamica dei Tempi di Aggiornamento Radar - Google Gemini.md`.
