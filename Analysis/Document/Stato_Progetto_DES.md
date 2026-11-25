# Stato del progetto DES — decisioni aperte e tarature da fare

> **Istantanea del 2026-11-24**, branch `analysis/dce-dcs-persistence`, commit `ed29b263`. Questo documento **invecchia in pochi
> giorni**: va riletto con la data in testa e aggiornato quando una decisione viene presa. Non fa parte della
> [Guida concettuale](Manuale_Motore_DES/Guida_Concettuale_DES.md), che lo cita soltanto (sezione 12.9).
> Fonte dei contenuti: Manuale DES, capitolo 9 (§9.1, §9.3, §9.4, §9.6) e memoria di progetto; nessun numero di questo
> documento è stato rieseguito oggi (suite e confronto sono quelli dichiarati nell'ultima sessione, sotto).
> Etichette: **[V]** verificato sul codice o con una prova rieseguibile; **[S]** stima dichiarata, senza fonte o non tarata;
> **[D]** decisione che spetta all'utente.

## 1. In una pagina

- **Il motore è completo nella struttura** (eventi, geometria, catena dello scontro, riproducibilità) e coperto da una
  suite di **4973 test** (OK, 7 saltati) e da una **fotografia di non regressione di 1219 esecuzioni** [V, ultima
  esecuzione del 2026-11-20: suite 4973 OK, confronto identico a 1219].
- **I numeri che lo alimentano sono in buona parte stime** dichiarate: nessuna taratura su dati reali o storici è stata
  fatta. Oggi il motore serve per **confronti relativi tra scelte, con repliche**, non per previsioni assolute (decisione
  dell'utente, 2026-11-19).
- **Non esiste ancora un collegamento di produzione** fra il motore e la campagna o DCS: il motore risolve sessioni
  sintetiche; il contratto di ingresso/uscita è lo stesso per una sessione giocata, ma manca l'adattatore DCS e manca chi
  chiama il ciclo di campagna.
- **Lavoro chiuso di recente**: permanenza nel volume (D-5) accesa e provata con i dati reali; probabilità di scoperta al
  bordo della portata ricalibrata a 0,2 e accesa (2026-11-20); manuale DES allineato al codice; guida concettuale scritta e
  verificata a campione.
- **Che cosa serve da te**: le decisioni della sezione 3 (accendere o no due regole spente, fonte per lo 0,2, passaggio del
  rilevamento fra sessioni, ordine di priorità del lavoro dati) e la prova dei diagrammi in Obsidian (sezione 5).

## 2. Interruttori delle regole: chi è acceso e chi no

Un **interruttore** è un'opzione nel codice che attiva o disattiva una regola; la regola nuova nasce con il comportamento
precedente come default e si accende solo con una decisione esplicita (accenderla cambia la fotografia di non regressione).

| Interruttore | Regola | Stato | Note |
|---|---|---|---|
| `D5_DWELL_TIME` | permanenza nel volume (D-5): un bersaglio che attraversa il volume per troppo poco tempo non viene scoperto | **ACCESO** dal 2026-11-18 | dati `dwell_time_s` per 53 modelli, 24 stime [S] |
| `PD_EDGE_RECALIBRATION` | probabilità di scoperta al bordo della portata a **0,2** (prima 0,5) | **ACCESO** dal 2026-11-20 | 0,2 è una **stima senza fonte** [S], scelta dell'utente; cambiate 716 esecuzioni su 1219 |
| `BI_AD_TARGET_RULE` | bersagli intercettabili dalle difese aeree (BI): un missile antiaereo non spara a ciò che non può intercettare | **SPENTO** | accenderlo cambia la fotografia **[D]** |
| `VA_ENGAGEMENT_ALTITUDE_BAND` | quota nel volume d'ingaggio (VA): l'ingaggio vale solo se il bersaglio è nella fascia di quota dell'arma | **SPENTO** | accenderlo cambia la fotografia **[D]** |
| `F7_WEAPON_POLICY`, `F7_TARGET_RULES`, `F7_AREA_FIRE`, `F8_IN_PROGRESS` | politica d'armi per missione, regole di bersaglio, fuoco su posizione, stato «in corso» | **ACCESI** | decisioni delle fasi F7/F8, 2026-10 |

Il rilevamento per passaggio nella portata propria (FP) non ha più interruttore dal 2026-11-13: è una regola sempre attiva.
Pendente: la **politica sugli interruttori** (criterio già scritto in memoria: si tengono solo se lo stato precedente è
un'alternativa valida, si eliminano se sostituiti) con una regola da scrivere in `AGENTS.md` **[D]**.

## 3. Decisioni aperte che spettano a te

| # | Decisione | Perché conta | Effetto | Prerequisito |
|---|---|---|---|---|
| 1 | **Accendere BI** | senza, un SAM può «sparare» a un bersaglio che non può intercettare (es. missile balistico) | cambia la fotografia (nuova da installare, solo tu) | L1 rivista e chiusa (n. 3): ora si può riaprire BI (S35 dipende da L1 e BI) |
| 2 | **Accendere VA** | senza, la fascia di quota dell'arma è ignorata | cambia la fotografia | dare portata e fascia alle armi di test (attività separata) |
| 3 | ~~**Rivedere L1**~~ | | **CHIUSA (2026-11-25)**: regola rivista ACCESA e senza interruttore (`Proposta_L1_Pulizia_Interruttore.md`, merge `bbaa61c1`); 6 esecuzioni cambiate all'accensione, fotografia nuova da 1219 installata (`79e500e9`), pulizia a confronto `IDENTICAL`, suite 4991 OK | nessuno |
| 4 | **Fonte per la Pd al bordo (0,2)** | oggi è il centro dell'intervallo che ti aspettavi, non un dato | restare a 0,2 con stima dichiarata, oppure una costante per sensore o la dipendenza dalla sezione radar del bersaglio (ipotesi rinviate) | una fonte (letteratura o prove) |
| 5 | **Passaggio del rilevamento fra sessioni** | oggi un bersaglio che attraversa due sessioni consecutive ha due estrazioni indipendenti: la legge non è additiva [V, sonde del 2026-11-19] | una memoria del passaggio sarebbe una Proposta separata con interruttore | nessuna regola proposta oggi |
| 6 | **D-5 nella scelta della rotta** | il pianificatore di rotta non «vede» la permanenza: la legge non accorcia le rotte | Proposta separata (attraversamento a corda limitata) | Proposta da scrivere |
| 7 | **Eliminare o tenere gli interruttori** `D5_DWELL_TIME`, `PD_EDGE_RECALIBRATION` | stato precedente valido come alternativa? | rimozione con fotografia nuova, decisa da te | criterio degli interruttori |
| 8 | **Chiamante di produzione del ciclo di campagna** (pianificatore / C2) | senza, il validatore e il conduttore di campagna girano solo nei test | Proposta di perimetro | gerarchia C2 (Fase 0 mai iniziata) |

## 4. Tarature e dati da fare (non sono decisioni di design)

| Tema | Stato | Note |
|---|---|---|
| **Fonti per le 24 stime di dwell** | registro dedicato `Registro_Dwell_Stimati.md` | 24 dei 43 modelli aggiunti dalla DW-9 sono stime [S]; vista e TVD (3,2 s) approssimati |
| **Fonti per i periodi di rivisita** | 24 stime | registro dedicato |
| **Soglia di rottura** (processo ATCAL) e dati di consumo d'emergenza | stime [S] | taratura da fare; regola WW2 per emergenze sotto 5 minuti |
| **Logistica (F8d)** | non fatta | consumo delle scorte del blocco e dipendenza di riarmo/riparazione dalle risorse della base; oggi rifornimento «senza logistica» con tempi stimati |
| **Orizzonte radar e curva portata-quota** | attività separate | senza orizzonte radar nel DES la legge di permanenza non accorcia le rotte |
| **Dati registri**: 22 o più incoerenze note (§9.6), metrica FP-9, costo del blocco B della pulizia FP | da chiudere | elenco in §9.6 del manuale |
| **Sensori fuori fotografia**: Shilka, Gepard, Osa, Tunguska, Roland, Kub, M163, Strela-1, Chaparral, M6, altri EWR e navi, E-2D, A-50 | non provati con i dwell reali | estendibile con la voce `detections` della fotografia, se vuoi |
| **Cueing EWR→SAM e reti di sensori** | non fatto | richiede la gerarchia C2 |
| **Revisione dei pianificatori satellite** (rotta, attacco): `MissionAsset.attack_profile` non collegato al motore | non fatto | oggi il motore legge solo l'arma designata, non quota né profilo |

## 5. Documentazione: cosa resta

1. **Prova dei 32 diagrammi Mermaid in Obsidian** — la fai tu. Il diagramma D15 è stato modificato e non è mai stato
   renderizzato.
2. **Guida concettuale**: per tua decisione del 2026-11-20 restano i riferimenti `[S/D]` e `[B 9.1]`/`[B 9.2]` (Manne,
   Ahuja: contenuto non letto); la bibliografia ha voci «non verificate» (ISBN Hughes 3a ed., Taylor 1983,
   DoDI 5000.61, Pd 0,5/0,9 come convenzione di portata radar).
3. **Manuale DES**: capitoli 1-3 e 5, e §4.35-§4.37, non riletti dopo gli ultimi cambi; i riferimenti `:riga` a
   `Session_Simulator.py` nel capitolo 6 sono ancora a `fa5fbf1e`.
4. **File di lavoro** `Guida_Concettuale_DES_ParteA/B/C/D.md`: da togliere o archiviare dopo la tua approvazione di questo
   documento.
5. **Nota wiki sulla rete multistrato** (logistica/militare): nessuna azione prima del tuo via.
6. Voci **39-41 di §9.6** (divergenze manuale/codice del 2026-11-20): corrette nel testo.

## 6. Come leggere questo documento

- Una voce **chiusa** non compare più: per lo storico, Manuale DES §9.4 e §9.6.
- «**Decisione**» significa che la scelta è tua e cambia il comportamento del motore; «**taratura**» significa che manca un
  dato o una fonte, non una scelta di design.
- Prima di una nuova delega a un agente OpenCode vale la regola di `CLAUDE.md`: proposta in una riga e conferma.
