---
title: "Gerarchia unità militari: Military resta atomico, una sola classe Formation"
type: decision
tags: [architecture, dwm, c2, command-control, military-hierarchy]
created: 2026-09-25
updated: 2026-09-25
status: proposed
affects: ["[[block]]", "[[command]]"]
related: ["[[c2-hierarchy-design]]", "[[virtual-session-engine-des]]", "[[risolutore-ingaggio-salva-fase4]]"]
---

## Contesto

L'utente ha caricato `Analysis/Document/Forze.Armate.Mondiali.1960-1980.docx` (struttura e
competenze funzionali per livello — Gruppo d'Armate/Fronte, Armata, Corpo d'Armata, Divisione,
Brigata, Battaglione, Compagnia — per ~19 paesi, periodo 1960-1980) e ha posto un dubbio
architetturale: se `Military` (v. [[block]]) rappresenta un'Armata, i suoi asset non possono
rappresentare i singoli mezzi di Divisioni/Brigate/Battaglioni; forse serve una gerarchia di classi
C2 esplicite per Armata/Divisione/Brigata/Battaglione, con logica di autonomia/dipendenza
decisionale, e il C2 regionale/globale già concordato in [[c2-hierarchy-design]] potrebbe
mappare su Corpo d'Armata/Gruppo di Armate.

## Decisione (proposta, non ancora presa dall'utente)

**Sì a una gerarchia esplicita, ma minimale — non una classe per ogni livello storico.**

1. **`Military` resta l'unità atomica** (compagnia, batteria, plotone o sito SAM — un gruppo DCS).
   Non solo per fedeltà di rappresentazione: il motore DES vincola questa scelta indipendentemente,
   perché le soglie di disingaggio (v. [[risolutore-ingaggio-salva-fase4]] R2, 0.30/0.20) si
   applicano per **forza intera**. Un `Military` grande quanto una Divisione si ritirerebbe per
   intero dopo il 30% di perdite in un singolo ingaggio — un artefatto del motore, non del modello
   storico.
2. **Una sola classe nuova, `Formation`**, in `Command/` (non sottoclasse di `Block`) —
   **ricorsiva**: il livello storico (Divisione, Brigata, ...) è un **attributo**, non una
   sottoclasse dedicata. Un livello intermedio obbligatorio fra `Military` e il C2 regionale, un
   secondo livello opzionale.
3. **Base comune `C2_Node`** condivisa da `C2_Manager`, `C2_Region_Manager` (entrambi già
   concordati in [[c2-hierarchy-design]], non ancora costruiti) e `Formation`: il protocollo
   proponi/approva già previsto fra C2 regionale e globale diventa **generico** per ogni coppia
   figlio→padre della gerarchia, non solo per i due livelli C2 originari.
4. **L'autonomia decisionale è un dato, non una sottoclasse**: una tabella per lato/livello in
   `Context/Doctrine.py`, sul modello delle soglie di disingaggio già esistenti — permette anche
   asimmetria NATO/Patto di Varsavia (es. l'URSS storicamente priva di livello Corpo d'Armata
   intermedio, v. il documento sorgente).
5. **Criterio per decidere quali livelli modellare: l'orizzonte decisionale**, non la fedeltà
   storica in sé. Il ciclo C2 gira solo fra una sessione e l'altra (v. [[c2-hierarchy-design]] §
   modello sessioni), quindi Battaglione/Compagnia — il cui orizzonte è ore/minuti secondo il
   documento sorgente — non possono avere nodi decisionali propri: il Battaglione diventa una
   **missione temporanea** del pianificatore di sessione, non un nodo persistente della gerarchia.

### Punto critico sulla scala

Il limite teorico del motore DES è **~10.000 asset totali** ([[virtual-session-engine-des]] §
vincoli utente) — circa un Corpo d'Armata per lato con un asset per mezzo reale (la campagna DCE di
riferimento ha ~900 unità in 429 gruppi, v. [[core-simulator-agnostic]]). Un "C2 di scenario =
Gruppo d'Armate" con asset 1:1 **non è rappresentabile** entro questo limite: richiederebbe asset
aggregati (un asset che rappresenta statisticamente un reparto più grande), un progetto separato,
fuori dal perimetro di questa proposta.

### Compatibilità con il design C2 esistente

L'ipotesi dell'utente (C2 regionale = Corpo d'Armata, C2 di scenario = Gruppo di Armate) **è
compatibile** con [[c2-hierarchy-design]] e lo **generalizza** — non lo contraddice. Va decisa
**prima** di scrivere `Command/C2_Manager.py`/`Command/C2_Region_Manager.py` (non ancora esistenti,
v. [[command]]), perché la base comune `C2_Node` (punto 3 sopra) va progettata insieme a questi due,
non aggiunta dopo.

## Motivazione

Il criterio guida è lo stesso già applicato al resto del motore DES: non importare complessità che
il motore non può sostenere (scala, soglie per-forza-intera) né che il ciclo C2 a grana di sessione
può effettivamente consumare (orizzonte decisionale). Una classe per livello storico
moltiplicherebbe le classi senza aggiungere capacità decisionale distinta ai livelli che il C2
non visita mai (Battaglione, Compagnia).

## Conseguenze

**Se accettata**: nuovo `Command/Formation.py` (ricorsivo, attributo di livello storico), nuovo
`Command/C2_Node.py` (base comune), estensione di `Context/Doctrine.py` con la tabella di autonomia
per lato/livello. Non tocca il motore DES (`Engagement_Resolver`, `Contact_Scheduler`,
`Fire_Control`) né `Military`/`Block`.

**Se respinta o rimandata**: `C2_Manager`/`C2_Region_Manager` vengono costruiti come già concordato
in [[c2-hierarchy-design]], senza livello `Formation` intermedio; l'ipotesi Corpo/Gruppo di Armate
resta un'analogia concettuale, non un vincolo implementato.

**Fase 0 — decisioni utente richieste prima di scrivere codice** (9 punti nel documento completo,
principali):
1. Scala effettiva dello scenario di riferimento (vincola se/quanto serve `Formation`).
2. Numero di livelli intermedi da modellare (uno obbligatorio, un secondo opzionale — quali).
3. Significato di `Region` rispetto a `Formation` (area geografica vs. unità organica — restano
   concetti distinti?).
4. Latenza delle proposte nel protocollo proponi/approva generalizzato.
5. Regola di riarmo/rifornimento a livello `Formation` (rispetto a quanto già deciso per
   `Theater_Session_Manager` in [[c2-hierarchy-design]]).
6-9. Altri punti minori, dettagliati nel documento completo.

Il documento propone anche un'**alternativa minima senza classi nuove** (arricchire `Military`/
`MILITARY_CATEGORY` con pochi attributi) per il caso in cui la Fase 0 concluda che la gerarchia
completa non è necessaria.

**Bug trovati durante l'analisi, non corretti**: `MILITARY_CATEGORY` (`Context/Context.py`)
mescola livelli gerarchici e tipi di installazione nella stessa enumerazione, in modo non coerente
col documento storico — v. [[block]] per `is_helibase()` mancante, bug distinto ma nello stesso
file.

## Fonti

- `.claude/memory/project_session_2026_09_25_summary.md` (memoria di origine)
- `Analysis/Document/Analisi_Gerarchia_Unita_Militari.md` (documento di analisi completo, piano a
  7 fasi con Fase 0 di 9 decisioni)
- `Analysis/Document/Forze.Armate.Mondiali.1960-1980.docx` (fonte storica caricata dall'utente)
- [[c2-hierarchy-design]] — design C2 esistente che questa proposta generalizza
- [[virtual-session-engine-des]] — vincoli di scala e soglie per-forza-intera del motore DES
