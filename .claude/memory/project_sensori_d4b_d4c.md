---
name: project-sensori-d4b-d4c
description: "Proposta dati sensori D-4b (EWR) / D-4c (visivo ZSU-57-2, M163): decisioni prese 2026-11-04, blocco A fatto e unito, blocco B da eseguire con oc-developer"
metadata:
  node_type: memory
  type: project
  originSessionId: e63b0355-dc97-4348-a4fe-fe5ff556bb3d
  modified: 2026-11-04T19:15:17.880Z
---

## Stato (2026-11-04, branch `analysis/dce-dcs-persistence`, locale, NON pushato)
- Proposta `Analysis/Document/Proposta_Dati_Sensori_EWR_Visivo.md` (cb980bf8), scritta da des-planner. 17 decisioni dell'utente prese una per una (§3.1): tutte come raccomandato **tranne la 12** (reliability radar EWR = stima generica 45/4, non omessa).
- **Blocco A (D-4c) FATTO** da des-developer, commit `37816355` (merge fast-forward, branch `ai/cc-sensori-a` cancellato): campo `visual` nel registro, `Mobile.D4C_VISUAL_SENSOR` default True, scenario S31-VISUAL. Verificato dalla sessione principale: suite `Ran 4727`, OK skipped=7; confronto 989 identiche, 0 cambiate, 20 nuove S31-VISUAL; fotografia installata a 1009.
- **Blocco B (D-4b, 8 EWR) DA FARE**: esecutore scelto `oc-developer` (DeepSeek V4 Pro high), dopo A e non in parallelo. Esito atteso: suite 4742, confronto tutte identiche, 0 nuove. Passi: branch `ai/oc-sensori-b`, poi `/esegui` nella TUI di `oc` indicando il solo blocco B.
- Blocco C (siti fissi) rimandato: serve prima il modello di un'installazione fissa.

**Why:** gli EWR vanno esclusi dalla popolazione globale del combat score (G2) e i valori deboli (6 km visivo, 55Zh6, Freya, ecc.) sono dichiarati stime nel codice.
**How to apply:** prima di B verificare che il confronto non cambi con la `reliability` 45/4 sui radar (dubbio aperto dalla decisione 12: se cambia, fermarsi). Da aggiornare dopo: manuale DES (cap. 04/08/09/10), F4, Piano, nota in [[project-detection-interception-volumes]].

## Cose non ovvie
- Due agenti in parallelo sullo stesso checkout non vanno bene: un solo branch, `.ai-run/` condiviso (vedi regole in AGENTS.md).
- Le sonde di S31 danno valori diversi da quelli orientativi del planner (ZSU 150 colpi/0 perdite invece di 550/1): asserzioni qualitative passano, nulla ritoccato.
