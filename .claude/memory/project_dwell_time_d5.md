---
name: project-dwell-time-d5
description: "D-5 opzione 2 (dwell_time_s, Pd dipendente dalla permanenza): Proposta in BOZZA sospesa il 2026-11-05, decisioni DW-1..DW-8 aperte, sonde S-2/S-3 da eseguire, rischio principale (effetto quasi nullo sulle rotte senza orizzonte radar nel DES)"
metadata:
  type: project
---

## Stato (2026-11-05, sessione sospesa su osboxes, ripresa possibile sul ProArt)
- Proposta `Analysis/Document/Proposta_Dwell_Time_Rilevamento.md` (des-planner Opus high, ~900 righe): **BOZZA**. Intestazione con "COMPLETO / MANCA". Completi: problema, alternative, decisioni DW-1..DW-8 con raccomandazione, piano blocco A (motore: ~170 righe di codice + ~330 di test, 31 test, scenario S32-DWELL 20 esecuzioni nuove) e blocco B (pianificatore: ~60 + ~110, 7 test), blocco C condizionato, rischi, documenti da aggiornare.
- Origine: scelta ESPLICITA dell'utente (opzione 2 della D-5 di `Proposta_Volumi_Rilevamento_Intercettazione.md`); il "se" non si riapre, la Proposta discute il "come". Nella Proposta d'origine e' stata aggiunta solo la riga di stato in §9 D-5.
- **Decisioni per l'utente (TUTTE aperte, raccomandazione del planner)**: DW-1 il dato e' il periodo di rivisita = 60/giri al minuto; DW-2 10 EWR con valore (regola "rotazione piu' veloce" sugli intervalli di fonte), 5 EWR senza dato restano senza valore; DW-3 legge `Pd = min(1, permanenza/dwell) x Pd(d)` (puo' solo ridurre la Pd attuale); DW-4 permanenza calcolata nel risolutore dai tratti, non tagliata all'inizio della finestra; DW-5 interruttore `Engagement_Resolver.D5_DWELL_TIME` spento di default; DW-6 nel pianificatore solo metriche coerenti (blocco B); DW-7 rimandare l'attraversamento a corda limitata nel pianificatore (blocco C); DW-8 S32-DWELL con 5 varianti x 4 semi.
- **Esito atteso**: suite `Ran 4788` dopo A e `Ran 4795` dopo B; confronto 1009 identiche + 20 nuove, con interruttore spento E acceso (S-1).

## Numeri gia' ottenuti (sonda S-1, letti)
- Legge accesa in memoria con i soli dati di fonte: `compared 1009 runs: IDENTICAL` (nessuno scenario della fotografia usa un EWR). Estrazioni di rilevamento 33 446 (tutte con i tratti), 29 024 con permanenza >= 5 minuti. Controfattuale (stesso dwell per tutti 2/6/10/30/60/120 s): rilevamenti persi 0/0/3/17/45/464 su 29 483.

## Rischio principale (da dire all'utente prima delle decisioni)
Con i periodi di fonte (6-60 s) la legge NON accorcia le rotte: la corda a Pd ridotta dentro un volume EWR e' 1,5-6 km e penetra di pochi metri (raggi 120-440 km). L'effetto che motiva la D-5 (rotte troppo lunghe se si aggira) richiede l'**orizzonte radar nel DES** (oggi assente) o accettare il rilevamento come costo: la DW-7 lo rende esplicito. La legge e' comunque corretta e utile per sensori lenti (SCR-270, vista), contatti radenti, radar SAM futuri.
Nel DES un EWR influisce solo sulla percezione (nessun cueing): S32 usa periodi dichiarati di TEST sulla ZSU (30 s e 600 s), non dati. Nessun chiamante del core usa `AVOID_DETECTION`.

## Come riprendere (primo passo)
1. `git pull`; se sul ProArt: venv della macchina (mai `python3` nudo), hook SessionStart.
2. Sonde: v. `Analysis/Document/Rapporti/Sonde_Dwell_D5/LEGGIMI.md` (copia versionata degli script e dell'esito S-1; `.ai-run/` e' fuori dal versionamento). Prima **S-3** (geometria di S32, pochi minuti, mai eseguita), poi **S-2** (dwell uniforme 10 s, ~19 min su osboxes, incompleta); mai in parallelo con suite o confronto. Riportare i numeri nel documento (des-planner via SendMessage/nuovo agente, e' il suo file; se S-3 non da' gli esiti attesi, ritoccare i test di §4.A.7).
3. Presentare le decisioni DW-1..DW-8 all'utente una per una (con la raccomandazione e il rischio principale sopra) e registrarle nella Proposta.
4. Poi esecuzione a blocchi: A (motore) a des-developer o oc-developer (proporre in una riga e attendere conferma), verifica con suite + confronto dalla sessione principale, poi B.
