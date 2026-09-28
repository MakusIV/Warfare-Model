---
name: project-session-2026-09-28-summary
description: "Sessione 2026-09-28 (ProArt P16): D4 KMGU-2 CHIUSA (suite 3646 OK, non committata), A6 riprogettata come D+F+L con regole dottrinali dell'utente e APPROVATA (non implementata), ricerca armi DCS mancanti fatta da Haiku ma inaffidabile"
metadata:
  node_type: memory
  type: project
  originSessionId: 9bc0955f-e706-4f76-bae5-8515dde95b83
  modified: 2026-09-28T13:38:09.375Z
---

**Macchina**: ProArt P16 (WSL2), branch `analysis/dce-dcs-persistence`. L'auto mode ha avuto
il classificatore guasto per tutta la sessione; l'utente è passato ad "accept edits on".

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

## Armi DCS mancanti — ricerca Haiku NON utilizzabile così com'è
Fonte: `Analysis/Document/bombe_missili_russi.pdf` (7 schermate del menu armi DCS, anche armi cinesi).
Il rapporto Haiku (scratchpad, effimero) ha sbagliato il confronto (dava come mancanti Kh-101, Kh-25*,
Kh-29L/T, che ci sono), ha usato uno schema inventato ("ship", "seeker", "reliability", senza tutte
le classi di `efficiency` né la tabella precision/power né `release`) e ha numeri errati (Kh-41 2500
m/s). Lezione: a Haiku va dato lo schema esatto e la lista già confrontata; i numeri vanno verificati
uno per uno. Il confronto corretto l'ho fatto io (v. la risposta della sessione): circa 4 AAM cinesi,
circa 14 ASM, circa 23 bombe (incluse le varianti RBK, che nel registro sono voci distinte come
RBK-500AO/PTAB).
