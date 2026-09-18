---
name: project-session-2026-09-18-summary
description: Recap sessione 2026-09-18 — analisi completa DCE/DCS, ingestione documentazione asset, e il vincolo architetturale del core simulator-agnostic
metadata:
  type: project
---

Sessione interamente di **analisi e documentazione**, nessuna modifica al codice di
Warfare-Model. Tutto il prodotto sta in `Analysis/Document/documentazione_dcs/`.

## Cosa è stato fatto

1. **Analisi del Dynamic Campaign Engine** (DCE di MBot, ScriptsMod NG 20.47.105) →
   `ANALISI_DCE.md` (~1650 righe). V. [[project-dce-analysis]] per le conclusioni.
2. **Report di auto-verifica** sulla persistenza DCS e sulle API Lua →
   `COMPRENSIONE_PERSISTENZA_DCS.md`, con etichette di fonte
   (`[CODICE]`/`[DATI]`/`[DOC-LOC]`/`[WEB]`/`[INFER]`) e una Parte 3 esplicita sui confini
   della conoscenza.
3. **Analisi empirica di un `debrief.log` reale** fornito dall'utente (DCS 2.9.29.27468
   build 559) — ha ribaltato la conclusione iniziale: il debrief nativo è molto più ricco del
   log custom di DCE. Dettagli in [[project-dce-analysis]].
4. **Ingestione documentazione asset** → `estratti/` con `sam_threat_table.csv` (23 sistemi
   SAM: inviluppi, acquire_time, contromisure, priorità SEAD, site layout) e
   `vehicles_overview.json` (tassonomie + anno di servizio).
5. **Nota architetturale** → `ARCHITETTURA_CORE_AGNOSTICO.md`, dal vincolo dichiarato
   dall'utente. V. [[feedback-core-simulator-agnostic]] — è la cosa più importante emersa.

## Stato dei documenti

| File | Righe | Contenuto |
|---|---|---|
| `ANALISI_DCE.md` | ~1650 | analisi codice DCE + Appendice A (riferimento piattaforma DCS) |
| `COMPRENSIONE_PERSISTENZA_DCS.md` | ~490 | auto-verifica, con confini di conoscenza dichiarati |
| `ARCHITETTURA_CORE_AGNOSTICO.md` | ~250 | dove passa la linea core/adapter |
| `estratti/README.md` + 2 file dati | — | dati di riferimento con affidabilità per fonte |

## Cosa ho sbagliato e corretto in corso d'opera

Due affermazioni date per buone e poi smentite (entrambe corrette nei documenti e in
[[project-dce-analysis]]):
- "i warehouse non sono accessibili via scripting" — **falso**, lo sono da DCS 2.8.8;
- "il debrief.log non basta" — **ridimensionato**: i limiti reali sono due (niente scenery,
  formato degenere in MP), non quattro.

Lezione: le fonti web secondarie sulla piattaforma DCS sono spesso datate; **il file reale
vince sempre** (più volte i `.miz` e i log dell'utente hanno smentito `pydcs` e le wiki).

## Aperto / prossimi passi

- **Campione multiplayer del `debrief.log`** — l'utente ha detto che proverà a fornirlo. È
  l'unico tassello mancante sulla persistenza: le fonti dicono che in MP il formato degenera
  in righe testuali non-Lua.
- **Non analizzati**: `ATO_Generator.lua`, `ATO_FlightPlan.lua`, `ATO_RouteGenerator.lua`,
  `DC_LoadoutsAssignment.lua`, `DC_Briefing.lua` (~630 KB) — i corrispettivi di
  `Air_Resources_Assigner` + `Air_Route_Manager`. È il materiale più utile rimasto.
  Anche `db_firepower.lua` (318 KB) e `db_loadouts.lua` (331 KB).
- **Decisioni lasciate aperte all'utente** sul meteo (v. [[project-dce-analysis]]): dove vive
  lo stato sinottico, seed o snapshot per la riproducibilità, e la soglia di
  `adverse_weather` — che deve pesare **nebbia/visibilità, non densità nuvole**, perché in
  DCS le nuvole non bloccano la LOS dell'IA mentre nebbia e polvere sì.
- **`lupa` non è installato nel venv** pur essendo in `requirements.txt`:
  `DCS_Data_Management.py` oggi non è importabile.
- Segnalati ma non approfonditi: `Context/Coalition.py` e `Persistence/Source/Coalition.py`
  coesistono (due `Coalition` in due strati); `Persistence/` mescola persistenza di dominio e
  traduzione verso DCS.

## Nota sul commit

Su scelta dell'utente sono stati versionati i deliverable, i sorgenti testuali analizzati
(`.lua`/`.bat`/`.log`), i `.miz` e la SAM guide (~21 MB). Esclusi via `.gitignore`: PDF di
terze parti, `Overview Vehicles.pptx` (46 MB), `caucasus-freq_gross.png` (21 MB) e le
`Images/` della campagna DCE (86 MB) — materiale riscaricabile, 235 MB risparmiati.
