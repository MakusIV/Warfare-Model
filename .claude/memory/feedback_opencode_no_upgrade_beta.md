---
name: feedback-opencode-no-upgrade-beta
description: "Decisione dell'utente 2026-11-04: non aggiornare OpenCode alla 2.x finche' non e' dichiarata stabile; si resta sulla 1.19.5"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e63b0355-dc97-4348-a4fe-fe5ff556bb3d
  modified: 2026-11-04T19:46:01.840Z
---

L'utente ha deciso (2026-11-04) di **non** fare l'upgrade major di OpenCode (avviso nella TUI) finche' la 2.x non e' la versione definitiva: la guida ufficiale `opencode.ai/v2/docs/migrate-v1` la chiama ancora "beta". ProArt resta su 1.19.5 (osboxes risulta 1.19.3 nei documenti).

**Why:** la guida non ha rollback, l'installer v2 sostituisce il binario v1, e non e' documentato cosa succede a `OPENCODE_CONFIG` (routing fornitori per costo in `bin/oc`) e a `OPENCODE_DISABLE_CLAUDE_CODE_*`. In v2 `external_directory` e' permesso di default (in v1 chiedeva) e `permission` diventa `permissions`: puo' indebolire i limiti degli agenti.

**How to apply:** non proporre l'upgrade a una 2.x beta e non toccare OpenCode durante un'esecuzione. Quando la v2 sara' stabile: copiare prima `~/.opencode/bin/opencode` e `~/.config/opencode`, provare su una macchina sola con `01_verifica_opencode.sh`, `oc debug agent`, un `oc run` che mostri il fornitore reale dal CSV Activity e una prova di scrittura fuori dal repo; poi riallineare l'altra macchina. Vedi [[project-opencode-costi-misurati]].
