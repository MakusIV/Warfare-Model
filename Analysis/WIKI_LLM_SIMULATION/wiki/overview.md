---
title: "Panoramica — Modelli di Simulazione Bellica"
type: overview
tags: [campaign-model, combat-simulation, wargame, warfare-model]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]", "[[source-simulation-techniques-past-conflicts]]"]
---

# Panoramica del Dominio

> Questo documento rappresenta la sintesi evoluta di tutta la conoscenza accumulata nel wiki. Viene aggiornato da Claude dopo ogni ingestione significativa.

---

## Dominio di Ricerca

Questa base di conoscenza copre la **modellazione e simulazione di conflitti militari**, con focus su:

1. **Modelli di campagna militare** (Theater/Campaign Level Models): sistemi che simulano operazioni militari su scala operativa o strategica, considerando logistica, forze, territorio e dinamiche di combattimento.

2. **Tecniche di simulazione dei conflitti**: metodologie matematiche e computazionali usate per rappresentare il combattimento — da modelli Lanchester alle simulazioni ad agenti.

3. **Sviluppo del Warfare-Model**: progetto in corso che implementa un Dynamic War Manager (DWM) per il simulatore DCS (Digital Combat Simulator), con gestione dinamica di risorse aeree, navali e terrestri.

---

## Progetto Warfare-Model

Il progetto principale a cui questo wiki fa riferimento è situato in:
`/home/marco/Sviluppo/Warfare-Model/`

### Architettura Attuale
- **Dynamic War Manager (DWM)**: motore centrale di gestione della campagna
- **Persistence Layer**: gestione dati DCS (missioni, unità, waypoint)
- **Resource Manager**: assegnazione e gestione risorse militari
- **Componenti**: Aircraft, Ship, Vehicle, Ground Units con relative armi

### Classi/Moduli Chiave
- `Manager.py` — orchestratore principale
- `Resource_Manager.py` — gestione risorse
- `Air_Resources_Assigner.py` — assegnazione risorse aeree
- `Military_Resources_Assigner.py` — assegnazione risorse militari generali

### Domande di Ricerca Aperte
*(Da aggiornare man mano che si ingeriscono fonti)*
- Come modellare al meglio l'interazione aria-terra nelle campagne dinamiche?
- Quali metriche (MOE/MOP) sono più appropriate per valutare lo stato della campagna?
- Come integrare simulazioni Monte Carlo per la valutazione degli esiti tattici?

---

## Stato della Conoscenza

| Area | Fonti | Copertura | Note |
|------|-------|-----------|------|
| Campaign Models | 1 | Buona | TLC (RAND 1994) — prototipo prossima generazione |
| Combat Simulation Techniques | 2 | Buona | TLC (computazionale) + Sabin (manuale/accademico) |
| Ground Attrition (CADEM) | 1 | Buona | Metodologia CADEM dettagliata |
| Air Warfare (SAM, A-A, A-G) | 1 | Media | Processo TLC descritto, dati da TAC BRAWLER/RJARS/JMEM |
| Adaptive Resource Allocation | 1 | Buona | Algoritmo SAGE descritto |
| Historical Conflict Modelling | 1 | Media | Sabin: wargaming accademico, comparative dynamic modelling |
| Wargame Design Theory | 1 | Buona | Anti-hindsight, 3 ruoli simulazione, dialettica Clausewitz |
| Agent-Based Models | 0 | Nessuna | Da acquisire fonti specifiche |

---

## Tesi in Evoluzione

Dopo le prime due ingestioni emergono le seguenti tesi di sintesi:

1. **La struttura game board è fondamentale**: la scelta tra piston/griglia/generalizzata determina cosa il modello può e non può rappresentare. La rete generalizzata del TLC è l'evoluzione naturale verso cui punta anche il DWM (Route/Area/Region).

2. **La simulazione stocastica è necessaria per l'analisi robusta**: i modelli deterministici danno false certezze. Gli esiti del combattimento sono intrinsecamente stocastici e devono essere trattati come tali. Sabin rafforza questo argomento: l'anti-hindsight richiede esiti incerti anche in simulazioni operative.

3. **L'allocazione adattiva delle risorse è il cuore del C²**: i modelli con script fissi non possono valutare il valore dei sistemi C⁴I. SAGE rappresenta un approccio concreto già implementato nel 1994 — direttamente applicabile ad `Air_Resources_Assigner.py`.

4. **La cross-resolution è necessaria ma difficile**: nessun approccio di aggregazione è teoricamente perfetto; la coerenza è approssimata. Il costo in dati e risorse è elevato.

5. **La validazione tramite "refighting" è il metodo sistematico per il DWM**: il comparative dynamic modelling di Sabin — variare assunzioni e confrontare con esiti noti — è esattamente il metodo da applicare a `tactical_evaluation_results.csv` per calibrare i parametri del DWM. Questa convergenza tra approccio storico (Sabin) e calibrazione computazionale (CADEM) è un risultato non ovvio.

6. **Wargame manuale e campaign model computazionale sono complementari, non alternativi**: risolvono lo stesso problema (dialettica tra volontà opposte) con diversi trade-off di fedeltà, velocità e scopo. Il DWM si colloca nel quadrante computazionale-analitico, ma deve mantenere la dimensione di agency tramite le missioni DCS.

---

## Lacune da Colmare

- Fonti sui modelli Lanchester (classici e moderni)
- Letteratura su modelli ad agenti per conflitti (MANA, ISAAC, ecc.)
- Standard NATO/militari per simulazione (DSEEP, HLA/RPR FOM)
- Documentazione DCS sull'architettura di missione e hook disponibili
- Letteratura su ottimizzazione per resource allocation in warfare (MILP, reinforcement learning)
- Fonti sull'algoritmo SAGE originale (TAC SAGE predecessore di RAND)

---

## Risorse Esterne Raccomandate

*(Da espandere)*
- [Military Operations Research Society (MORS)](https://www.mors.org)
- [Journal of Defense Modeling and Simulation](https://journals.sagepub.com/home/jdm)
- [Simulation Interoperability Standards Organization (SISO)](https://www.sisostandards.org)
