---
name: feedback-interruttori-criterio
description: "Criterio dell'utente (2026-11-08) per tenere o eliminare gli interruttori del motore; analisi mirata di tutti gli interruttori da fare dopo FP"
metadata:
  type: feedback
---

- **Criterio**: un interruttore si tiene solo se lo stato precedente e' una **alternativa valida** (due modelli entrambi legittimi); si **elimina** se la soluzione nuova sostituisce una soluzione sbagliata o superata. La criticita' dei DATI (stime, taratura) NON e' un motivo per tenere un interruttore: e' un'altra questione dalla correttezza della logica.
- **Why:** l'utente ha osservato che le combinazioni di interruttori (es. FP spenta + D-5 accesa) sono stati che nel modello voluto non dovrebbero esistere, ma costringono a descriverli, testarli e confrontarli (esempio: il rilievo bloccante della revisione su FP-6). La fotografia e i test non devono "trascinare" stati che la logica scarta.
- **Rimozione**: accettato (2026-11-08) che ogni rimozione comporti una nuova fotografia, decisa dall'utente dopo aver letto le esecuzioni cambiate (sonda come P-1); mai installata da un agente. Una rimozione per volta, blocchi piccoli.
- **How to apply:** (1) concludere FP (decisioni FP-7..FP-10, FP-5) con interruttori dichiarati TEMPORANEI e criterio di rimozione scritto nella Proposta; niente test sulle combinazioni scartate; (2) poi **analisi mirata di tutti gli interruttori** (censimento in sola lettura con agente Opus high: default, chi li accende, test/scenari/fotografia che ne dipendono, classificazione alternativa-valida vs sostituita) e discussione con l'utente; (3) proporre il testo aggiornato della regola di AGENTS.md ("interruttore temporaneo con criterio di rimozione"; AGENTS.md e' dell'utente). Conteggio iniziale: 19 costanti booleane di modulo (15 in Session_Simulator), piu' i parametri di costruttore (use_recon...). Vedi [[project-session-2026-11-07-summary]].
