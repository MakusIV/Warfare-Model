---
name: project-session-2026-09-26-summary
description: "Sessione 2026-09-26 (ProArt P16): risolto il bug delle munizioni aggregate (scorta per modello d'arma, Proposta A completa A1/A2/A3/A5), dati di rilascio bombe + volumi rilevamento/intercettazione distinti (prerequisiti Proposta B), 8 commit e push fatti (suite 3597 OK); aperti: Proposta B non implementata, A4/A6, D4 KGBU sospesa in attesa verifica DCS dell'utente, Fase 0 gerarchia militare mai toccata"
metadata:
  type: project
  originSessionId: b183e431-8211-4d82-bd56-aecf65301f45
  modified: 2026-09-26T21:37:15.481Z
---

**Macchina**: ProArt P16 (WSL2), branch `analysis/dce-dcs-persistence`. Suite eseguita con
`.direnv/python-3.12/bin/python3`. Sessione lunghissima e molto densa: partita dal punto 1 lasciato
aperto dalla sessione 2026-09-25 (munizioni aggregate aerei + bombe senza portata) ed è arrivata a
implementare due proposte complete più i loro prerequisiti dati. **8 commit fatti e pushati.**

## Diagnosi iniziale (verificata nel codice, non solo ipotizzata)
`Mobile.ammunition` era un solo intero che sommava armi eterogenee (bombe+missili+colpi cannone) del
loadout/registro. `Fire_Control.py` scelto un'arma specifica per nome, ma il risolutore consumava
sempre lo stesso scalare aggregato — e siccome `Fire_Control` è pura/memoizzata (stessa arma sempre
per la stessa coppia tiratore/bersaglio), l'arma scelta non calava mai la propria scorta reale.
Misurato con numeri concreti: un A-10C con 4 Maverick reali ne lanciava **642**; un F-16C con 4 Mk-83
ne sganciava **523**; un BMP-2 con 4 Konkurs ne lanciava **252**. Bug NON di moltiplicazione per
squadrone (verificato: `Unit(model, count, ...)` in `Scenario_Fixtures.py` crea istanze indipendenti
corrette) — il difetto era nel consumo, non nel conteggio iniziale.

## Lavoro fatto, in ordine, con commit (tutti su `analysis/dce-dcs-persistence`, pushati)
1. `199e0cdf` + `a8642cc9` — **Air_Route_Manager.py**: 4 bug corretti (formula
   `calcMaxLenghtCrossSegment`/ora `...Interception` dimensionalmente incoerente, riscritta da zero
   con un modello fisico esplicito; minaccia sul bersaglio non più esclusa a priori ma "accettata"
   sul tratto terminale non evitabile, per decisione utente esplicita; side-effect del debug flag in
   `_handle_threat_avoidance`; bug for+remove in `PathCollection.get_best_path` che saltava percorsi
   fuori portata).
2. `e0bb8cb4` — 3 anomalie dati nel registro bombe corrette con ricerca (GBU-27 warhead
   429→250 kg BLU-109; BetAB-500 92→76 kg; RBK-250AO riga Armored corretta a profilo frammentazione).
3. `1d0c1127` — **[[project_ammunition_per_weapon_stock]] Proposta A completa** (A1/A3/A5): nuovo
   `Asset/Weapon_Stores.py`, funzioni pure condivise fra asset reale e stato ombra del risolutore.
   `_stores: {arma: quantità}` stato primario, `ammunition`/`interceptor_stock` viste calcolate.
   Regola "SAM puro" eliminata (non serve più con la scorta per arma). `ShotSpec.stock_per_round` per
   armi a raffica. Criterio scelta arma: Pk/costo (`score = Pk / costo^0.5`), non solo Pk massima.
   Risultati scenario cambiati e attesi: A-10 preferisce Mk-82AIR a Maverick (più economico); S1 non dà
   più vittoria netta all'attaccante; S16 alzato a `STRIKE_SIZE=16` perché con munizioni reali un raid
   di 4 F/A-18C veniva assorbito interamente.
4. `4ddbb089` — Dati `release` (finestra di rilascio: quota/velocità/angolo/resistenza) scritti per
   29/32 bombe, da `Proposta_Dati_Rilascio_Bombe.md` (D1-D3, D5). 3 KGBU sospese (D4).
5. `8bd69727` — **A2**: cannone di bordo diventato arma candidata vera. Campo `gun` su 37 modelli
   aereo in `Aircraft_Data.py`, associazione aereo→cannone (13 cannoni già completamente modellati nel
   registro, mancava solo il collegamento). Comportamento cambiato: un aereo in CAP può ora impegnare
   un bersaglio terrestre col cannone.
6. `815dc35f` — **[[project_detection_interception_volumes]] Volumi rilevamento/intercettazione
   distinti** (D-1...D-7 di 10): nuovo `DetectionThreat` accanto a `ThreatAA`, con raggio limitato
   dall'orizzonte radar (formula standard, quota+altezza antenna). `ThreatMode`
   {AVOID, CROSS_UNINTERCEPTED, AVOID_DETECTION} in `calcRoute`. Metriche di rotta separate
   (`detection_exposure_s`, `warning_time_s`, ecc.), pericolo di rilevamento NON sommato al pericolo
   di intercettazione.
7. `59be4379` — manuale DES aggiornato (ancorato a `1d0c1127`, non al lavoro parallelo in corso al
   momento) + i 4 documenti di analisi/proposta della sessione.

## Documenti prodotti (in `Analysis/Document/`, tutti committati)
- `Analisi_Modello_Missione_Sessione.md` — verifica della regola utente "una missione per asset per
  sessione, mai ripetuta, rientro-per-rifornire = missione nuova" contro il motore DES: coerente nel
  nucleo, 7 problemi trovati (P1 "Missione" non esiste come entità, P2 fine missione solo geometrica,
  P3 "fine attività" oggi vuol dire "sparisce", P4 carburante non vincola nulla/rifornimento assente,
  P5 durata sessione unica, P6/P7 minori). 6 decisioni utente NON ancora prese (§6 del documento).
- `Proposta_Dati_Rilascio_Bombe.md` — ricerca dati per 32 bombe, D1-D5 tutte chiuse (D4 sospesa).
- `Proposta_Munizioni_Compatibili_e_Rotte_Attacco.md` — Proposta A (implementata) e Proposta B (NON
  implementata), con mappa d'impatto completa per B.
- `Proposta_Volumi_Rilevamento_Intercettazione.md` — D-1...D-10, D-1...D-7 implementate, D-4b/c/D-5
  seconda opzione/D-8 fuori scope per questo giro.

## Decisioni utente rilevanti prese in sessione (da ricordare per coerenza futura)
- **Missioni**: una sessione = al più una missione per asset (mai ripetuta), rifornimento in volo
  dentro la missione, rientro a terra per rifornire = fine missione + missione nuova successiva.
  Verificata: coerente nel nucleo col motore, ma richiede l'entità `Mission` (non esiste) per essere
  vincolo reale — vedi 6 decisioni aperte nel documento dedicato.
- **Rotte d'attacco/minacce**: una minaccia non evitabile in prossimità del target va accettata (non
  deve bloccare l'attacco), anche se il pericolo lì supera quello tollerato altrove sulla rotta —
  principio già applicato nel fix Bug2 di Air_Route_Manager e riconfermato per il design dei volumi.
  Direzione d'attacco: libera/ottimizzata dall'algoritmo (non imposta dal C2, per ora). Profili di
  sgancio: tutti e tre ammessi (livellato/picchiata/cabrata), anche se solo il livellato ha oggi una
  formula balistica pronta.
- **AVOID_DETECTION**: aggira il rilevamento ma attraversa l'intercettazione con corda limitata se
  necessario — MAI assumere che evitare il rilevamento eviti automaticamente l'intercettazione anche
  se per i SAM tipici (sensore/lanciatore co-locati) è quasi sempre vero: verificare sempre sui valori
  dichiarati.
- **Criterio scelta arma**: compromesso Pk/costo (non solo Pk massima) — principio confermato, formula
  esatta lasciata a discrezione dell'agente implementatore (dichiarata, ricalibrabile).

## APERTO per la prossima sessione, in ordine di blocco
1. **Proposta B (rotte d'attacco/quota di sgancio)**: entrambi i prerequisiti sono pronti (dati
   `release` scritti, volumi rilevamento/intercettazione implementati) — può partire subito.
   Richiederà anche l'aggiornamento della sua firma per accettare le due liste di minacce (D-8 della
   proposta volumi, non ancora fatto).
2. **D4 sospesa**: le tre voci KGBU-2AO/2PTAB/96r (probabile KMGU-2 mal identificato) — l'utente deve
   verificare la documentazione DCS prima di decidere il flag `dispenser` e se KGBU-96r è un doppione
   da eliminare.
3. **A4** (filtro missione/bersaglio) e **A6** (revisione proposta SAM D+B+F sopra la scorta per arma)
   — entrambe rimandate esplicitamente, A4 dipende dall'entità `Mission` (non esiste).
4. **D-4b/c della proposta volumi**: ricerca dati EWR (da WWII a Guerra Fredda, confermato dall'utente)
   e sensore visivo di ripiego per ZSU-57-2/M163.
5. **D-5 seconda opzione**: `dwell_time_s` per sensore + Pd del DES dipendente dal tempo di permanenza
   (non solo distanza) — l'utente ha scelto questa opzione più impegnativa (cambia la legge del
   risolutore) motivandola con l'eccesso di missioni annullate che l'aggiramento puro comporterebbe.
6. **Le 6 decisioni di `Analisi_Modello_Missione_Sessione.md`** (§6): presenza a fine missione,
   criteri di fine missione ammessi, unità della missione (per asset o per gruppo), durata/
   sovrapposizione sessioni, rifornimento in volo, turnaround/pool di prontezza.
7. **Manuale DES**: la sezione su Fire_Control/candidati del tiratore (cap. 4 §4.16, cap. 9 §9.1/§9.3)
   va aggiornata di nuovo per riflettere A2 (cannone) e i volumi rilevamento/intercettazione — il
   commit `59be4379` è ancorato solo a `1d0c1127`, non ai commit successivi.
8. **Fase 0 gerarchia militare** (9 decisioni, da sessioni precedenti) — non toccata in questa
   sessione, resta la più vecchia decisione in sospeso del progetto.
9. Anomalia dati non risolta: AJ/ASJ 37 Viggen ha 150 `gun_rounds` nel loadout ma nessun cannone
   interno assegnato (Oerlikon-KCA è della variante JA 37, non della AJ 37) — lasciato senza `gun`
   deliberatamente piuttosto che assegnare un'arma sbagliata.

## Lezione di processo (nuova, importante)
Fino a 4 agenti `des-developer`/generici lanciati in parallelo su file non sovrapposti hanno
funzionato bene anche in una sessione molto lunga — ma un agente (manuale DES) ha rilevato da solo
lavoro concorrente non ancora committato di altri due agenti e si è correttamente ancorato all'ultimo
commit (`git show HEAD:...`) invece di documentare uno stato instabile: comportamento corretto da
riconoscere e replicare. Un agente ha anche usato `git stash`/`pop` per confrontare vecchio/nuovo
comportamento durante l'implementazione — è tornato tutto a posto (verificato da questa sessione con
`git stash list` vuoto), ma è un'operazione rischiosa da non incoraggiare esplicitamente in futuri
prompt se evitabile. Sempre verificare `git status`/suite indipendentemente dal report dell'agente
prima di committare, specialmente con più agenti paralleli sullo stesso checkout.
