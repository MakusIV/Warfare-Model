---
description: Esegue un piano approvato (Proposta_*.md) sul branch ai/oc-* corrente. Uso - /esegui Analysis/Document/Proposta_X.md
agent: oc-developer
---
Esegui il piano $ARGUMENTS seguendo AGENTS.md (flusso obbligatorio degli esecutori):
1. controlla con `git branch --show-current` di essere su un branch `ai/oc-*`, altrimenti fermati;
2. leggi tutto il piano e i file che cita;
3. implementa e scrivi i test previsti dal piano;
4. esegui `bash tools/ai/verifica.sh suite start` e poi `confronto start` (mai in parallelo), ripetendo `wait` fino all'ESITO;
5. se un esito non corrisponde a quello atteso dal piano e il piano non lo spiega, fermati e riferisci;
6. scrivi il rapporto in `Analysis/Document/Rapporti/` seguendo `TEMPLATE.md` e committa sul branch.
