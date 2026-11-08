---
name: project-bi-blocco3-punti-aperti
description: BI blocco 3 (S35-ADTGT) non eseguibile finche' non sono decisi P-1..P-7 (BI §5.4.1); P-1 decisa (Rezky); revisione di L1 rinviata
metadata:
  type: project
---

Il 2026-11-08 le sonde del planner (commit 551f774b) hanno mostrato che il blocco 3 BI e' in contraddizione col codice: Burke (V_I 240 km) + regola L1 = nessuna intercettazione navale; l'asserzione 2 (piu' danni ai BMP) e' falsa (distrutti in ogni caso, cambiano Maverick lanciati 14->8 e perdite Blue). Precondizione 5 di BI §5.0 vieta l'esecuzione finche' P-1..P-7 sono APERTI. Esecutore previsto: oc-developer (scelta dell'utente), branch `ai/oc-bi-blocco3` da creare dopo le decisioni.

**Decise (2026-11-08):**
- **P-1 = (a)**: nave `'FF 1135M Rezky'` (V_I 12 km, intercettore AK-630) per entrambe le varianti navali; nomi delle varianti invariati.
- **L1 non si cambia ora**: l'utente ritiene L1 da rivedere ("dopo"), ma e' una sua decisione del 2026-09-28 (Proposta_Regole_Allocazione_SAM §7.7 Q2: colpi lanciati dentro V_I non si intercettano mai). Rivedere in una Proposta separata dopo FP; S35 si rivede insieme alla fotografia. L'utente confondeva L1 con R-INT (rilevamento/tempo di reazione), che e' un'altra regola.

- **P-2 = (a)**: sensore `sea` dichiarato nello scenario con `F.Unit(..., sensors={'sea': 20_000})`, 20 km VALORE DI TEST [S] (l'A-10C non ha sensore marittimo a registro; il numero non entra nelle asserzioni).
- **P-3 = (a)**: asserzione 2 sostituita da 'meno AGM-65D lanciati a regola accesa che spenta, per seme' (sonda: 14 -> 8); NON verificato che valga per ogni seme: fermata dell'esecutore se non regge, legata a P-6.
- **P-4 = (b)**: 15 test (12 asserzioni + 3 premesse non vacue: lanci AGM-65D, Kh-59, AGM-84A in ogni variante), suite attesa 4844 [S].
- **P-5 = (a)**: `land_cruise` = configurazione della sonda S-b fissata nella Proposta (2 Su-34 'Anti-Ship' da (-150 km,0,6000 m) fino a x=-60 km e ritorno, missione Strike, Kh-59, `Oil_Tank` (category 'Farp') in (0,0) ristretto con `Target.asset_ids`, ROE only_designated, Buk a 1 km dal deposito nella stessa forza; risultato [V]: 4 Kh-59, 2 intercettazioni, identici off/on).
- **P-6 = raccomandazioni**: asserzioni 3 e 4 PER SEME, 9 sul TOTALE dei 4 semi (fermata se 3/4 non reggono in un seme); asserzione 11 = (b): `interception_events == ()` nelle sole varianti con domini vuoti (`land_tactical_on`, `naval_maverick_on`), come TestS19AdTargetRule :275.

- **P-7 = confermato**: `SEEDS = [f'S35-ADTGT-{index}' for index in range(4)]`, chiavi `S35-ADTGT/S35-ADTGT-<i>/<variante>`.

**TUTTE LE DECISIONI P-1..P-7 PRESE (2026-11-08).**

**STATO INTERROTTO (limite d'uso):** il des-planner (agentId a8db9f84b43203a3f, fermato con TaskStop) stava riscrivendo BI §5.4/§5.0 con le decisioni; la Proposta BI ha MODIFICHE PARZIALI (committate come WIP il 2026-11-08 sera) (§5 e §5.0 riscritti a meta', non verificate). Per riprendere: SendMessage al planner (o nuovo des-planner) con il compito '.ai-run/compito_planner_BI_blocco3_decisioni.txt', rileggere il diff parziale (`git diff Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`), completare §5.4.1->'Decisioni', §5.0 (togliere la precondizione 5), §6.1, §8; poi commit, branch `ai/oc-bi-blocco3`, compito per oc-developer (V4 Pro 0813), suite/confronto lanciati dal principale.

**Why:** evitare uno scenario su regola contestata; criterio utente sugli interruttori (vedi [[feedback-interruttori-criterio]]).
**How to apply:** presentare un punto per volta (vedi [[feedback-presentazione-decisioni]]); dopo P-1..P-7 far aggiornare §5.4 al des-planner, committare, poi creare il branch e preparare il compito per oc-developer.
