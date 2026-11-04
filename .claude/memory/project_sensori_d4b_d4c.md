---
name: project-sensori-d4b-d4c
description: "Proposta dati sensori D-4b (EWR) / D-4c (visivo ZSU-57-2, M163): decisioni prese 2026-11-04, blocchi A e B fatti, verificati e uniti (suite 4742, fotografia 1009); restano documenti e push"
metadata:
  node_type: memory
  type: project
  originSessionId: e63b0355-dc97-4348-a4fe-fe5ff556bb3d
  modified: 2026-11-04T19:15:17.880Z
---

## Stato (2026-11-04, branch `analysis/dce-dcs-persistence`, pushato a fine sessione; prossime attivita' in [[project-session-2026-11-04-summary]])
- Proposta `Analysis/Document/Proposta_Dati_Sensori_EWR_Visivo.md` (cb980bf8), scritta da des-planner. 17 decisioni dell'utente prese una per una (§3.1): tutte come raccomandato **tranne la 12** (reliability radar EWR = stima generica 45/4, non omessa).
- **Blocco A (D-4c) FATTO** da des-developer, commit `37816355` (merge fast-forward, branch `ai/cc-sensori-a` cancellato): campo `visual` nel registro, `Mobile.D4C_VISUAL_SENSOR` default True, scenario S31-VISUAL. Verificato dalla sessione principale: suite `Ran 4727`, OK skipped=7; confronto 989 identiche, 0 cambiate, 20 nuove S31-VISUAL; fotografia installata a 1009.
- **Blocco B (D-4b, 8 EWR) FATTO** da oc-developer (modello effettivo `deepseek/deepseek-v4-pro-0813`), commit `cbc75634` (merge fast-forward, branch `ai/oc-sensori-b` cancellato): 8 record EWR, G2 (EWR fuori dal combat score globale, con saturazione in [0,1]), `Test_EWR_Data`. Verificato dalla sessione principale: suite `Ran 4742`, OK skipped=7; confronto 1009 identiche, 0 cambiate, 0 nuove (il dubbio sulla reliability 45/4 e' chiuso: nessun effetto). Costo reale 0,678 $ dal CSV Activity (fornitore StreamLake per tutte le 126 richieste, cache 97,3%), uguale alla TUI; la somma dei `cost` di `oc export` (2,03 $) e' un conteggio errato, non usarla. Registrato in `Costi_Deleghe.md`.
- Blocco C (siti fissi) rimandato: serve prima il modello di un'installazione fissa.

**Why:** gli EWR vanno esclusi dalla popolazione globale del combat score (G2) e i valori deboli (6 km visivo, 55Zh6, Freya, ecc.) sono dichiarati stime nel codice.
**How to apply:** restano da fare (non scritti): manuale DES (cap. 04/08/09/10) a des-manual-writer, `F4_Differenze_Scenari.md`, Piano, nota di stato nella Proposta d'origine, nota in [[project-detection-interception-volumes]]; push su richiesta dell'utente; blocco C (siti fissi) solo dopo la scelta del modello. Vedi anche [[feedback-opencode-no-upgrade-beta]].

## Cose non ovvie
- Due agenti in parallelo sullo stesso checkout non vanno bene: un solo branch, `.ai-run/` condiviso (vedi regole in AGENTS.md).
- Le sonde di S31 danno valori diversi da quelli orientativi del planner (ZSU 150 colpi/0 perdite invece di 550/1): asserzioni qualitative passano, nulla ritoccato.
