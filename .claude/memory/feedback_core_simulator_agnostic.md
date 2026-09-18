---
name: feedback-core-simulator-agnostic
description: Vincolo architetturale dichiarato dall'utente il 2026-09-18 — il core Python di Warfare-Model deve essere indifferente al simulatore e deve poter gestire una campagna con sole sessioni sintetiche
metadata:
  type: feedback
---

L'utente ha dichiarato il 2026-09-18 il vincolo architetturale portante di Warfare-Model:

> Un **core Python** che modella **tutti** gli aspetti del modello, integrato al simulatore
> tramite **moduli di interfaccia**. Il simulatore **può essere diverso da DCS**. L'architettura
> del core deve essere **indifferente** rispetto al simulatore, e deve consentire in linea
> teorica di gestire una campagna **esclusivamente con sessioni sintetiche**.

**Why:** DCE (il progetto LUA analizzato) è il controesempio: non ha un core: `oob_ground`
replica letteralmente la struttura del file `mission` del `.miz`, `targetlist` usa coordinate
mappa DCS, `DC_Weather` scrive direttamente `mission.weather`, e **non esiste alcun modello di
combattimento** — DCS *è* il risolutore. Tolto DCS, DCE non produce nulla. Warfare-Model parte
meglio (`Combat_Power_Estimation`, `Tactical_Evaluation`, `Strategical_Evaluation` sono
l'embrione di un risolutore proprio) ma il rischio di contaminazione è alto perché tutta
l'analisi DCS svolta finora è, per natura, materiale da adapter.

**How to apply:**
- Test operativo di agnosticismo: **cancellando l'adapter DCS la campagna deve continuare a
  girare**. Se qualcosa si rompe, era nel posto sbagliato.
- Nel core mai: `lupa`/`zipfile`/`minizip`; ID del simulatore (`unitId`, `groupId`,
  `airdromeId`, `DictKey_*`); stringhe di tipo DCS (`"MiG-21Bis"`); unità del simulatore;
  `timer.getTime()`/model time.
- Definire per primo il contratto delle porte `SessionOrder` (core→sessione) e
  `SessionOutcome` (sessione→core), dimensionato sull'**unione** di ciò che DCS e il
  risolutore sintetico sanno produrre, con i campi non universali opzionali e con la
  **provenienza dichiarata** per campo (`measured`/`derived`/`estimated`) — coerente con la
  distinzione osservato/stimato già introdotta in [[project-fase2-recon-combat-power-plan]].
- **Ordine di lavoro (controintuitivo):** 1) contratto porte; 2) `SyntheticResolver` nel core
  anche rozzo; 3) far girare una campagna intera **senza simulatore**; 4) **solo dopo**
  l'adapter DCS, obbligato a produrre lo stesso `SessionOutcome`. Invertendo l'ordine il
  contratto nasce modellato su DCS e l'agnosticismo è perso in partenza.
- Il pezzo davvero mancante è la **risoluzione dell'ingaggio** (+ consumo munizioni/carburante):
  non esiste in Warfare-Model né in DCE.
- **Warehouse**: l'utente ha precisato che **DCE non le usa**. Nell'ottica agnostica è la
  scelta giusta — il magazzino è un concetto di dominio. Le warehouse DCS (scriptabili da
  2.8.8) vanno trattate come **proiezione** dell'adapter, mai come rappresentazione del core.
- Dati di riferimento ingeriti: separare **fisica reale e dottrina → core** (inviluppi SAM,
  `acquire_time`, tipo contromisura, `site_layout`, `sead_priority`, anni di servizio,
  tassonomie) da **rappresentazione DCS → adapter** (HARM code, simboli RWR, nomi di tipo,
  cloud preset, ICAO/TACAN). Un sito SAM è un **gruppo di asset eterogenei**, non un asset
  singolo.

Documento completo: `Analysis/Document/documentazione_dcs/ARCHITETTURA_CORE_AGNOSTICO.md`.
Rileggere con questa lente [[project-dce-analysis]], in particolare la tabella di
corrispondenze §7.2 di `ANALISI_DCE.md`, che accosta strutture DCS a moduli di dominio.
