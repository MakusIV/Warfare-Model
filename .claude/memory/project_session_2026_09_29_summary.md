---
name: project-session-2026-09-29-summary
description: "Sessione 2026-09-29 (osboxes/VM) CHIUSA: soglia di rottura stocastica, efficacia antiaerea E(N), puntamento condiviso, RWR per classi/modalità, classificazione SAM, overkill (dottrina di tiro); suite 3735 OK; tutto committato e pushato; prossima sessione su ProArt P16"
metadata:
  node_type: memory
  type: project
  originSessionId: c96aae50-d207-4afc-a001-15c7352ab468
  modified: 2026-09-29T16:54:37.521Z
---

**Macchina**: osboxes (VM), branch `analysis/dce-dcs-persistence`. Sessione chiusa con tutto
committato e pushato. **Prossima sessione sull'Asus ProArt P16 (WSL2)**: fare `git pull` a inizio
sessione; lì python è in `.direnv/python-3.12/bin/python3` (v. [[feedback-venv]]). Suite: 3735 OK
(5 skipped), ~14 min sulla VM. Comando dalla root:
`python -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_*.py"`.

## STATO DI FATTO (tutto implementato, testato, pushato)

1. **Soglia di rottura stocastica** (difetto §5.3 disingaggio alla prima perdita) —
   `Analysis/Document/Proposta_Soglia_Rottura_Stocastica.md` (documento finale, §1-11). Tempra per
   forza (logit-normale, mediana 0,30, σ 0,5, flusso separato `temper_event_id`), morale in ingresso
   (None = neutro), rapporto di forze percepito, fuoco senza risposta, postura, shock con minimo 2
   perdite. Tabella con sole erosion/shock = soglie fisse di prima.
2. **Efficacia antiaerea E(N)** (`Context/Air_Defense_Efficacy.py`): aerei abbattuti attesi;
   armi dello stesso sistema di puntamento ripartiscono il tempo-canale (Tunguska: radar condiviso;
   nave: direttore SAM condiviso, CIWS a parte); minaccia percepita su scorta di DOTAZIONE stimata.
3. **Categorie SAM**: fonte primaria `classificazione_sam_1950_2000.md` (dell'utente) per sistema
   missilistico (`SAM_WEAPON_CATEGORY`), ripiego ruolo/portata.
4. **RWR** (`Asset/Aircraft_Rwr_Data.py`, 65 aerei): classi distinte, modalità (ricerca/
   tracciamento/guida), settori, EWR. SPO-15 rileva lo Shilka (verificato dall'utente in DCS);
   SPO-10 = 4 quadranti, "SAM" generico, solo tracciamento (percepisce al lancio); SPO-15 = 8
   settori, 3 classi. Ricerca Sonnet in `Analysis/Document/Ricerca_RWR_2026_09_29.md` (decisioni
   utente prevalenti). Tu-95MS: `avionics` allineato a L-150 Pastel.
5. **Overkill** (§5.2) — `Analysis/Document/Proposta_Overkill_Tiro.md`: `Doctrine.DEFAULT_FIRE_DOCTRINE`
   (saturazione del bersaglio per la forza a P_cov ≥ 0,9; tetto "due missili, poi guarda" per
   tiratore; lanciatori L2 esenti dalla saturazione; attesa al primo impatto, mai prima del
   prossimo istante di tiro). Salve sprecate → 0 negli scenari S19/S1.

## PROSSIME ATTIVITÀ (in ordine, da proporre all'utente)

1. **Intercettazione senza tempo di reazione** (§5.4 di `Proposta_Regole_Allocazione_SAM.md`):
   l'intercettazione è istantanea e non richiede di aver rilevato il colpo in arrivo. Legarla a
   rilevamento del colpo + tempo di reazione dell'intercettore (con nebbia di guerra C).
2. **Uso di direzione (settori) e granularità delle classi RWR**: registrati in
   `Aircraft_Rwr_Data` ma il modello li ignora (percezione sì/no, minaccia con la E(N) del sistema
   specifico).
3. **A4 — filtro armi per missione**: legato all'entità `Mission` e alle 6 decisioni di
   `Analisi_Modello_Missione_Sessione.md` (S19 usa ancora il filtro di test `ifv_only`/"solo Maverick").
4. **Dettagli del calcolo rotte**, poi **modulo mappe** (v. [[project-map-module-plan]]), poi volumi
   con terreno. Il .docx sulle mappe non è ancora letto (volutamente).
5. Residui volumi: D-4b/c, D-5 opz. 2, D-7 seconda parte, D-8.
6. **Fase 0 gerarchia C2** (la più vecchia; anche legame C2 fra unità AD e contagio del disingaggio).
7. D9: correggere `Block.morale` (success_ratio mai alimentato, MF fuzzy fuori scala) e alimentarlo
   dagli esiti degli ingaggi.
8. Bug noti non corretti: `get_blocks_by_criteria`, `Military.is_helibase` mancante.
9. **Manuale DES** da aggiornare (soglia di rottura, Air_Defense_Efficacy, RWR, dottrina di tiro,
   A6) con `des-manual-writer`, verificando i riferimenti file:riga.

## Lezioni della sessione
- Un agente di ricerca va fatto con Sonnet (non Haiku) passando lo schema esatto e la tabella da
  verificare; le sue conclusioni da fonti deboli vanno filtrate (SPO-15/Shilka: la ricerca diceva il
  contrario di quanto l'utente ha verificato in DCS).
- Un'attesa che ridecide a un istante fisso deve rispettare il proprio ciclo di tiro, altrimenti con
  tempo di volo nullo si ha un ciclo infinito allo stesso istante.
- `pkill -f` con un pattern che compare nella propria riga di comando uccide anche la shell corrente.
- File dell'utente non tracciato da non committare: `Analysis/Document/Untitled 1.odt`. Il .docx
  `Documentazione e Guida Mappe DCS World.docx` è stato aggiunto al repository (4dbf9479).
