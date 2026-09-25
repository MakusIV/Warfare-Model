---
name: project-session-2026-09-25-summary
description: "Sessione 2026-09-25 (ProArt P16, dopo pull da osboxes): nebbia di guerra (attività C) FATTA committata e pushata (suite 3478 OK); due documenti di analisi committati (gerarchia militare Armata/Divisione/Brigata, proposta regole SAM); aperti: 9 decisioni Fase 0 gerarchia, scelta regole SAM (D+B+F raccomandato), munizioni aggregate aerei, bombe senza portata"
metadata:
  type: project
  originSessionId: c7ec8f1d-1962-40ab-914c-52c324594d92
  modified: 2026-09-25T22:09:22.688Z
---

**Macchina**: ProArt P16 (WSL2), dopo pull dalla sessione precedente su osboxes. Suite eseguita con
`.direnv/python-3.12/bin/python3`. Tre agenti `des-developer`/generici (Opus, effort medio salvo
uno) lanciati in parallelo, tutti conclusi con successo, nessun commit fatto da loro (per
convenzione di progetto, commit solo su richiesta esplicita — fatti a fine sessione dalla sessione
principale).

## 1. Nebbia di guerra (Attività C del piano) — FATTA, committata e pushata
Commit `388e6ea3`. Nuovi costruttori in `Logic/Engagement_Resolver.py` (motore invariato):
`recon_detection_factor_fn`/`combine_detection_factors` (fattore per-lato sui blocchi visti,
niente RNG consumato) e `region_recon_detection_factor(region, observer_side, ...)` (istantanea
pre-sessione, stessa ricetta di `update_military_priorities`:
`Tactical_Analysis.build_recon_cp_snapshot(region.get_recon_reports(enemySide(side)))`).

**Decisione utente presa in sessione**: `unseen_factor` modulato da `Military.get_recon_efficiency()`
dell'osservatore (non costante fissa). Formula (stima dichiarata, da ricalibrare):
`unseen = unseen_factor + (seen_factor - unseen_factor) × RECON_EFFICIENCY_FOG_RELIEF × e`, con
`UNSEEN_DETECTION_FACTOR = 0.5` e `RECON_EFFICIENCY_FOG_RELIEF = 0.5`. Aggregazione su più `Military`
dello stesso lato nella regione: **il massimo**, non la media (basta un buon sensore per illuminare
l'area; la media esistente `Region.get_region_recon_efficiency` misura invece quanto la ricognizione
è diffusa — tenuta intatta, caso d'uso diverso). Verificato su S9 con una `Region` vera: tasso di
rilevamento Blue 0.948 (visto) → 0.726 (ricognizione buona) → 0.496 (non visto, ricognizione nulla).
Suite: 3478 test OK (skipped=5), +34 dalla baseline 3444.

**Limiti noti, non corretti (fuori perimetro)**:
- Bug in `Region.get_blocks_by_criteria`: con `category='Military'` scarta le `Military` reali la cui
  `category` non è esattamente `'Military'` (le fixture hanno `category=''`) — impatta anche
  `update_military_priorities` e le metriche di regione esistenti. Da decidere se/come correggere,
  tocca altri chiamanti.
- La nebbia è "debole" con la ricetta attuale: `get_recognition_report` produce sempre un report con
  `block_id` per ogni `Military` nemica della regione; "non visto" oggi scatta solo per blocco fuori
  regione/non militare/categoria non mappata/asset senza blocco, non per un criterio più stringente
  (es. `position is None` nel report). Scelta deliberata per restare fedele alla ricetta esistente di
  `update_military_priorities`; un criterio più forte è un'estensione futura.
- `get_recognition_report` usa `random` globale ma solo nella costruzione dell'istantanea
  pre-sessione, fuori dal percorso del motore — non tocca l'RNG di sessione, documentato.

## 2. Analisi gerarchia unità militari (Armata/Corpo/Divisione/Brigata/Battaglione/Compagnia)
Commit `30774603`. Fonte: documento caricato dall'utente
`Analysis/Document/Forze.Armate.Mondiali.1960-1980.docx` (export Gemini, struttura + competenze
funzionali per livello, per ~19 paesi, periodo 1960-1980). Analisi completa in
`Analysis/Document/Analisi_Gerarchia_Unita_Militari.md`.

**Dubbio dell'utente**: se `Military` = Armata, i suoi asset non possono rappresentare i singoli
mezzi di Divisioni/Brigate/Battaglioni; forse serve una gerarchia di classi C2 per Armata/Divisione/
Brigata/Battaglione con logica di autonomia/dipendenza decisionale.

**Raccomandazione dell'agente (Opus, effort alto)**: sì ma minimale, no a una classe per livello
storico.
1. `Military` resta l'unità atomica (compagnia/batteria/plotone/sito SAM = un gruppo DCS) — vincolato
   anche dal motore DES: le soglie di disingaggio (0.30/0.20) sono per forza intera, un `Military`
   grande quanto una Divisione si ritirerebbe tutto dopo il 30% di perdite in un solo ingaggio.
2. Una sola classe nuova, `Formation`, in `Command/`, NON sottoclasse di `Block` — ricorsiva, con il
   livello storico (Divisione/Brigata/...) come attributo, non come sottoclasse. Un livello
   intermedio obbligatorio, un secondo opzionale.
3. Base comune `C2_Node` per `C2_Manager`/`C2_Region_Manager`/`Formation` — protocollo proponi/approva
   generico per ogni coppia figlio→padre (v. [[project_c2_hierarchy_design]]).
4. Autonomia decisionale come dato (tabella per lato/livello in `Doctrine.py`, sul modello delle
   soglie di disingaggio), non come sottoclasse — permette asimmetria NATO/Patto di Varsavia.
5. Criterio per quali livelli modellare: l'orizzonte decisionale. Il C2 gira solo fra una sessione e
   l'altra, quindi Battaglione/Compagnia non hanno nodi decisionali propri — il Battaglione diventa
   una missione temporanea del pianificatore di sessione.

**Punto critico sulla scala**: limite teorico del DES ~10.000 asset totali = circa un Corpo d'Armata
per lato con un asset per mezzo reale (la campagna DCE di riferimento ha ~900 unità in 429 gruppi).
Un "C2 di scenario = Gruppo d'Armate" con asset 1:1 non è rappresentabile: servirebbero asset
aggregati, un progetto separato fuori da questa proposta.

**Compatibilità**: l'ipotesi utente (C2 regionale = Corpo, C2 di scenario = Gruppo d'Armate) è
compatibile col design C2 già concordato ([[project_c2_hierarchy_design]]) e lo generalizza — va
decisa PRIMA di scrivere `C2_Manager.py`/`C2_Region_Manager.py` (non ancora esistenti).

Il documento contiene un piano a 7 fasi con una **Fase 0 di 9 decisioni utente** (le principali: scala
dello scenario, numero di livelli intermedi, significato di `Region`, latenza delle proposte, regola
di riarmo) più un'alternativa minima senza classi nuove. Nessuna di queste 9 decisioni è ancora
presa — da fare all'inizio della prossima sessione che riprende questo filone.

**Bug trovati, non corretti**: `Block/Military.py:463` chiama `is_helibase()` che non esiste (può
sollevare `AttributeError` in certi casi); `MILITARY_CATEGORY` mescola livelli gerarchici e tipi di
installazione, commento in `Context.py:437-447` non coincide col documento storico; lo scenario di
test S17 usa i nomi dei livelli come semplici moltiplicatori di taglia (1-6).

## 3. Proposta regole allocazione munizioni SAM (Compito 2, rimandato dalla sessione precedente)
Commit `395a6e84`. Problema: i SAM puri (`interceptor_shares_ammunition=True`) esauriscono le
munizioni intercettando salve non dirette a sé e restano vuoti quando il lanciatore arriva a portata
di tiro diretto — emerso dopo il controllo di portata (commit `15350cc5`).

**Riprodotto** con script deterministico (scratchpad, non nel repo): seed `repro-strela-1`, 4 A-10
con 4 Maverick ciascuno, disingaggio disattivato, Strela-10 a ~1 km da 3 BMP-2. 16 Maverick lanciati
da ~16 km contro i BMP; lo Strela intercetta 1/evento, scorta 8→0 in ~25s, rileva gli A-10 solo dopo;
quando questi entrano nei suoi 5 km (~50s più tardi) spara 0 salve. Media su 30 seed: le
intercettazioni salvano 0.04 BMP e costano 1.2 A-10 abbattuti su 4.

**Causa** (`Logic/Engagement_Resolver.py`, `_on_resolve`): intercetta a livello di forza TUTTI i
colpi intercettabili nella finestra, qualunque sia il bersaglio designato, senza controllo di
distanza/rilevamento, senza riserva né priorità. `salvo_interceptors` tratta ogni asset di difesa
aerea come intercettore con Pk=1.

**Perché non si vedeva nello scenario di default**: mascherato da due difetti indipendenti — l'A-10
ha munizioni aggregate abnormi (1183 totali, 128 Maverick) e Red si disingaggia alla prima perdita
(soglia di shock 0.20 superata subito).

**Regole valutate**: A) autodifesa (SAM intercetta solo colpi diretti a sé) — intervento minimo
immediato; B) riserva 50% (stima) per il tiro diretto; C) priorità al lanciatore entro T — efficace
ma usa informazioni che il difensore non avrebbe realisticamente; D) capacità antimissile dichiarata
nei registri (task `Anti_Missile` già esiste per le armi navali, manca per quelle terrestri); E)
nessuna modifica; F) accessoria, consumare prima le scorte dedicate poi i pool condivisi.

**Raccomandazione dell'agente**: D+B+F, con A come intervento minimo subito applicabile. **Segnala
esplicitamente che va chiusa PRIMA la questione delle munizioni aggregate degli aerei** (vedi sotto)
prima di implementare, perché altrimenti il test di verifica resta falsato dallo stesso artefatto
che ha mascherato il problema.

## Decisioni utente ancora aperte per la prossima sessione, in ordine di blocco
1. **Munizioni aggregate aerei** e **bombe senza portata** (ereditate dalla sessione 2026-09-24,
   ora confermate bloccanti anche per le regole SAM) — vanno chiuse per prime.
2. **Scelta regole SAM**: D+B+F raccomandato, o solo A come intervento minimo, o altro.
3. **Fase 0 gerarchia militare**: 9 decisioni in `Analisi_Gerarchia_Unita_Militari.md` (scala
   scenario, numero livelli intermedi, significato `Region`, latenza proposte, regola di riarmo, +4
   altre) prima di scrivere `Command/Formation.py`/`Command/C2_Node.py`.
4. Bug `Region.get_blocks_by_criteria` con `category='Military'` — se/come correggere, impatta
   chiamanti esistenti.
5. Bug `Military.is_helibase()` mancante (`Block/Military.py:463`) — se/come correggere.

**Non ancora affrontato**: capitolo aggiuntivo del manuale DES su attività B (fire control)/C (nebbia
di guerra) — punto 4 della sequenza del piano originale, rimasto indietro rispetto a C.

## Lezione di processo
Tre agenti lanciati in parallelo su file/moduli non sovrapposti (`Engagement_Resolver.py` per due di
loro, ma uno solo scrittura codice — l'analisi SAM ha scritto solo in scratchpad) hanno funzionato
senza conflitti. L'utente ha scelto sempre effort medio per Opus quando gli è stato chiesto
esplicitamente (costo), coerente con [[project_session_2026_09_24_summary]].
