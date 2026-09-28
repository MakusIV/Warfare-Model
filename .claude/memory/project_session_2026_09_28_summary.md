---
name: project-session-2026-09-28-summary
description: "Sessione 2026-09-28 (ProArt P16): D4 KMGU-2 chiusa, 39 armi DCS inserite in AIR_WEAPONS, A6 COMPLETA (D Anti_Missile + CIWS, F, L1 lancio fuori zona, L2 priorità ai lanciatori, L3 prelazione), scenario S19; suite 3668 OK; tutto committato e pushato"
metadata:
  node_type: memory
  type: project
  originSessionId: 9bc0955f-e706-4f76-bae5-8515dde95b83
  modified: 2026-09-28T18:43:04.247Z
---

**Macchina**: ProArt P16 (WSL2), branch `analysis/dce-dcs-persistence`. L'auto mode ha avuto
il classificatore guasto per tutta la sessione; l'utente è passato ad "accept edits on".

## STATO FINALE (fine sessione) — tutto committato e pushato
Commit della sessione: `89f1aa34` D4+A6 riprogettata, `0df5ddf9` armi DCS, `37ca477e` A6 passi 1-2,
`aedd7fa5` S19, `24a43d10` L1, commit finale L2+L3 (+ memoria). Suite **3668 OK** (5 skipped).
Documenti di riferimento: `Proposta_Regole_Allocazione_SAM.md` §7 (§7.7 decisioni, §7.8-7.10
implementazione), `Proposta_Dati_Anti_Missile.md`, `Ricerca_Armi_DCS_2026_09_28/README.md`.

## PROSSIMI PASSI (in ordine di blocco, da proporre all'utente)
1. **Disingaggio alla prima perdita per forze piccole** (proposta SAM §5.3): con 4-6 asset una
   perdita dà shock >= 0,20 e la forza rompe il contatto. Con la regola D è diventato evidente in S1
   con CAS (Red si ritira prima dello scontro coi blindati; test rilassato). Va deciso prima di tarare
   altro: soglia di shock dipendente dalla dimensione della forza? minimo di perdite assolute?
2. **Overkill dello stesso tiratore** (§5.2): `_engaged_shooters` esclude il tiratore che decide, un
   Tor mette 4 salve sullo stesso A-10 prima del primo impatto (visto nelle misure di S19).
3. **Intercettazione senza tempo di reazione** (§5.4): l'intercettazione è istantanea e non richiede
   rilevamento del colpo; con la nebbia di guerra.
4. **A4** (filtro armi per missione) resta legato all'entità `Mission` (6 decisioni di
   `Analisi_Modello_Missione_Sessione.md`); S19 usa un filtro "solo Maverick" di test al suo posto.
5. Residui volumi: D-4b/c, D-5 opz. 2, D-7 seconda parte, D-8.
6. **Fase 0 gerarchia C2** (la più vecchia in sospeso), che dovrà anche modellare il legame C2 fra
   unità di difesa aerea (limite di L3: ogni tiratore usa il proprio refire_interval).
7. Bug noti non corretti: `get_blocks_by_criteria`, `Military.is_helibase` mancante.
8. Manuale DES da aggiornare (A6: Anti_Missile, CIWS, L1/L2/L3, S19; armi nuove) — con
   `des-manual-writer`, verificando poi i riferimenti file:riga.

## D4 — FATTA (non committata al momento della scrittura)
L'utente ha verificato in DCS: nessuna arma "KGBU"; il dispenser è il **KMG-2F/2B** (KMGU-2), resta sul
pilone. `KGBU-2AO`/`KGBU-2PTAB` → `KMGU-2AO`/`KMGU-2PTAB`, `KGBU-96r` eliminata (doppione), weight 525,
`"dispenser": True` a livello di voce, `release` solo level 30-1000 m / 500-1100 km/h / drag high. Nessuna
logica dedicata: con drag high da 200 m la gittata è ~0,7 km (sorvolo). BOMBS ora 31 voci, tutte con
`release`. Test aggiornati (Test_Aircraft_Weapon_Data, Test_Weapon_Delivery, Test_Fire_Control), suite
**3646 OK**. Aggiornati anche `Proposta_Dati_Rilascio_Bombe.md` e i riferimenti KGBU nel manuale DES.

## A6 — APPROVATA, da implementare (`Proposta_Regole_Allocazione_SAM.md` §7, decisioni §7.7)
Regole dottrinali dell'utente: (1) la difesa aerea dà priorità massima, per tempo e per numero di armi,
all'aereo che ha lanciato un'arma A2G se è entro il raggio d'intercettazione; (2) sono bersagli leciti
solo le armi autonome (missili, droni, bombe plananti) lanciate da FUORI dalla zona d'intercettazione,
e solo se l'arma intercettrice è capace. Ne esce **D + F + L**: B (riserva 50%) eliminata, C ripresa
come L senza previsione della rotta. Q1: zona = V_I del singolo intercettore; Q2: colpi lanciati dentro
la zona mai intercettati; Q3: la classe di priorità è il primo elemento della chiave di `_schedule_next`,
ma DENTRO la classe resta la copertura (più aerei nemici → le unità indipendenti si ripartiscono il
lavoro) + un tempo di valutazione e assegnazione (riusare Reaction_Profile se basta, legame con la
Fase 0 C2); Q4: prelazione sì; Q5: il lanciatore deve essere già rilevato; Q6: un solo task
`Anti_Missile`. Ordine: (1) proposta di dati `Anti_Missile` sulle 16 armi Anti_Air terrestri, (2) D+F,
(3) riproduzione Strela/Buk come test persistente, (4) L1 nel risolutore, (5) L2+L3.

## A6 passo 5 (L2 + L3) — FATTO, A6 COMPLETA; suite 3668 OK, non committato al momento della scrittura
Passo 4 committato (`24a43d10`). L2 in `_schedule_next` (lanciatori A2G contro la mia forza, a portata,
passano davanti; copertura invariata fra loro). L3: `_register_launcher` al primo lancio A2G di un
aereo → generazione++ (annulla il lancio programmato) + evento `_DECIDE` a t + refire_interval
(`_on_decide`). Lezione: la prima stesura ridecideva SUBITO e due lanciatori simultanei non venivano
ripartiti — il tempo di valutazione deve precedere la decisione, non solo il tiro. Test
`TestLauncherPriority` (5). Limite: legame C2 fra unità non modellato (Fase 0 C2).
Aperti dopo A6: difetto disingaggio alla prima perdita (§5.3, ora più visibile in S1), overkill dello
stesso tiratore (§5.2), intercettazione senza tempo di reazione (§5.4).

## A6 passo 4 (L1) — FATTO, suite 3663 OK, non committato al momento della scrittura
Passo 3 committato (`aedd7fa5`). `Engagement_Resolver._on_resolve` ora alloca PER SALVA:
`_may_intercept` (punto di lancio a t_launch fuori dal cilindro `air_defense_volume` dell'intercettore,
posizioni da `position_on_legs`), `_interception_zone` e cache per run. Senza vincoli = identico a
prima (nessuno scenario cambiato). Test `TestLauncherInsideInterceptionZone` (7). Resta passo 5:
L2 (priorità di bersaglio ai lanciatori a tiro, dentro la classe resta la copertura) + L3
(prelazione con tempo di valutazione/assegnazione), v. proposta §7.7 Q3/Q4.

## A6 passo 3 — FATTO (S19), suite 3656 OK, non committato al momento della scrittura
Passi 1-2 committati (`37ca477e`). Nuovo `Test/Test_Session_Scenarios_S19_Air_Defence.py`: Strela
sorvolo/standoff, Tor arretrato (intercetta, lanci fuori zona), Tor avanzato con A-10 solo sui BMP
(spara ai lanciatori, 0 intercettazioni). Scoperta: il motore rispetta già L per TEMPISTICA (il
lanciatore entra nella zona prima dell'impatto) e il Maverick (15 km) supera la zona del Tor (12 km),
quindi il caso che solo L1 distingue non è stabile negli scenari → al passo 4 serve un test UNITARIO
a geometria controllata in Test_Engagement_Resolver. Errore mio evitato: avevo scritto un
expectedFailure su un caso che in realtà era un lancio da FUORI zona (misurare le distanze, non
stimarle). Documentato in `Proposta_Regole_Allocazione_SAM.md` §7.8.

## A6 passi 1-2 (dati Anti_Missile + D + F) — FATTI, suite 3650 OK (non committati al momento della scrittura)
Armi committate (`0df5ddf9`). `Proposta_Dati_Anti_Missile.md` approvata (D-AM1 Osa/Stinger NO,
D-AM2 CIWS navali intercettori con quote + `rounds_per_mount`, D-AM3 9M311 = M1). Anti_Missile su
Tor, Buk, S-300PS, Tunguska (missile+cannone), Gepard. `Mobile.interceptor_capability()` (True/False/
None), `INTERCEPTOR_TASK`, scorta CIWS = impianti x rounds_per_mount, `WS.interceptor_rank` (ordine F
fra asset, anche nel risolutore). Esiti cambiati: S13 senza intercettori; S11 difesa → Gepard+Tor (per
non far saltare in silenzio i test sulle scorte d'intercettazione); S1 con CAS: Red si disingaggia
prima dello scontro coi blindati (regola D + difetto §5.3 disingaggio alla prima perdita, ora più
visibile — da discutere). Prossimo: passo 3 (riproduzione Strela/Buk come test), 4 (L1), 5 (L2+L3).

## Armi DCS mancanti — INSERITE (seconda ricerca, non committate al momento della scrittura)
D4 + A6 committate (`89f1aa34`, memoria `697a031d`, nessun push). Poi seconda ricerca Haiku a tre gruppi
con lo schema esatto → 4 AAM, 12 ASM, 23 bombe inserite in `Aircraft_Weapon_Data.py` (+ righe
`_WEAPON_PARAM_TYPE`), suite **3647 OK**. Correzioni mie documentate in
`Analysis/Document/Ricerca_Armi_DCS_2026_09_28/README.md` (Kh-22/Kh-58U non inseriti perché alias,
Kh-41 320 kg, KD-20 ricostruito, classi efficiency ereditate dal modello, LS-6 planante con standoff
(10, 60), Mk-84 AIR drag selezionabile). Test: SELECTABLE +Mk-84 AIR, nuovo GLIDE_STANDOFF (LS-6).

## Armi DCS mancanti — prima ricerca Haiku NON utilizzabile così com'è
Fonte: `Analysis/Document/bombe_missili_russi.pdf` (7 schermate del menu armi DCS, anche armi cinesi).
Il rapporto Haiku (scratchpad, effimero) ha sbagliato il confronto (dava come mancanti Kh-101, Kh-25*,
Kh-29L/T, che ci sono), ha usato uno schema inventato ("ship", "seeker", "reliability", senza tutte
le classi di `efficiency` né la tabella precision/power né `release`) e ha numeri errati (Kh-41 2500
m/s). Lezione: a Haiku va dato lo schema esatto e la lista già confrontata; i numeri vanno verificati
uno per uno. Il confronto corretto l'ho fatto io (v. la risposta della sessione): circa 4 AAM cinesi,
circa 14 ASM, circa 23 bombe (incluse le varianti RBK, che nel registro sono voci distinte come
RBK-500AO/PTAB).
