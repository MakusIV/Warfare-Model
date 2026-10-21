# Warfare-Model — regole comuni a tutti gli agenti

Valgono per **ogni** agente che lavora in questo repo: Claude Code (che le importa da `CLAUDE.md`) e
OpenCode con qualunque modello, cloud o locale. Scrivi in italiano; commenti e docstring nello stile e
nella lingua del codice circostante.

## Il progetto
- Codice Python in `Code/Dynamic_War_Manager/Source/` (motore DES di sessioni virtuali, registri d'arma e
  asset, logica tattica/strategica, pianificatori); test in `Code/Dynamic_War_Manager/Source/Test/`.
- Documenti in `Analysis/Document/`: i piani di intervento sono i file `Proposta_*.md`.
- Repo pubblico su GitHub, usato da piu' macchine (ProArt P16, VM osboxes) sincronizzate con git.

## Verifiche: sempre con `tools/ai/verifica.sh`
Suite completa e confronto con la "fotografia" girano in background, **mai in parallelo tra loro**
(suite ~10 minuti sul ProArt; sulla VM osboxes suite ~21 e confronto ~17); ogni chiamata dura al
massimo ~2 minuti. Ripeti `wait` finche' non compare `ESITO`:
```
bash tools/ai/verifica.sh suite start        bash tools/ai/verifica.sh suite wait
bash tools/ai/verifica.sh confronto start    bash tools/ai/verifica.sh confronto wait
```
Lo script sceglie da solo l'interprete Python della macchina. Un solo file di test, dalla root del repo:
`<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_<Nome>` (`<python>` = quello che
`verifica.sh` stampa nell'esito). Riporta i numeri letti dall'ESITO (`Ran N tests`, `OK`/`FAILED`), mai
stimati. **Non installare mai una fotografia nuova** (`Test/baseline/scenario_baseline.json`).
L'ESITO del confronto mostra solo il riepilogo (righe accorciate): l'elenco completo delle esecuzioni
identiche/cambiate/nuove e' in `.ai-run/confronto.log` (cercalo con `grep -E '^(CHANGED|NEW)'`).

## Regole tecniche vincolanti
- **Mai lavorare in un git worktree**: import assoluti + PYTHONPATH fanno eseguire ai test il codice del
  checkout principale, con esiti falsi. Lavora nel checkout principale.
- Import sempre con il percorso completo: `from Code.Dynamic_War_Manager.Source.X.Y import Z`.
- **Determinismo**: nel motore DES solo l'RNG di sessione (`Utility/Session_Rng.py`), mai il modulo
  `random` globale; non cambiare l'ordine delle estrazioni se il piano non lo dice.
- Ogni regola nuova del motore sta dietro un interruttore il cui default riproduce il comportamento
  precedente.
- **Core indifferente al simulatore**: il codice del core non dipende dall'adapter DCS (cancellando
  l'adapter la campagna deve girare con sole sessioni sintetiche).
- **Mai spacciare valori inventati per dati tarati**: ogni costante stimata e' dichiarata come stima, nel
  codice (commento) e nel rapporto.
- Test: le classi base condivise NON ereditano da `unittest.TestCase`; il logger si mocka come negli altri
  `Test_*.py`, es. `patch("Code.Dynamic_War_Manager.Source.Asset.XXX.logger", MagicMock())`.

## Proprieta' dei file (chi puo' scrivere cosa)
| File | Scrive | Gli altri agenti |
|---|---|---|
| `.claude/` (memoria di Claude, agenti, hook), `CLAUDE.md` | solo Claude Code con modello Claude | leggono solo se il compito lo cita |
| `AGENTS.md`, `.opencode/`, `opencode.json`, `.githooks/`, `tools/ai/` | l'utente (o Claude su sua richiesta) | sola lettura |
| `Analysis/Document/Proposta_*.md` | l'agente che pianifica (`des-planner` o `oc-planner`) | sola lettura: e' il contratto |
| `Analysis/Document/Rapporti/` | ogni agente il proprio file: `Rapporto_*` (esecutori), `Revisione_*` (`oc-reviewer`), `Diagnosi_*` (`oc-debugger`) | — |
| `Analysis/Document/Bozze/` | `oc-writer` (bozze, poi integrate da `des-manual-writer` o dalla sessione principale) | — |
| `Analysis/Document/Manuale_Motore_DES/` | `des-manual-writer` | sola lettura |
| codice e test | l'esecutore, **solo sul proprio branch** | — |

## Agenti OpenCode del progetto (`.opencode/agents/`)
| Agente | Modello predefinito | Scrive | Committa | Comando |
|---|---|---|---|---|
| `oc-planner` | DeepSeek V4 Pro high | solo `Proposta_*.md` | no | `/piano <richiesta>` |
| `oc-developer` | DeepSeek V4 Pro high | codice, test, rapporto | si', solo `ai/*` | `/esegui <Proposta>` |
| `oc-reviewer` | GLM 5.3 high | solo `Revisione_*.md` | no | `/rivedi <branch> <Proposta>` |
| `oc-debugger` | DeepSeek V4 Pro high | solo `Diagnosi_*.md` | no | `/diagnosi <sintomo>` |
| `oc-writer` | DeepSeek V4.1 Flash high | bozze e documenti `.md` non riservati, rapporto | si', solo `ai/*` | `/bozza <tema>` |
| `oc-helper` | Qwen3.8 27B locale (Game_PC) | su conferma | no | — |

L'agente globale `oc-ui-developer` e' disattivato in questo progetto (`opencode.json`).

Lo stato del progetto (decisioni, avanzamento, memoria) lo aggiorna **solo** la sessione principale di
Claude, dopo aver verificato il lavoro: un agente esecutore non scrive mai "fatto/approvato" altrove che
nel proprio rapporto.

## Agenti esecutori non-Claude (OpenCode): flusso obbligatorio
1. Lavori sul branch `ai/oc-<tema>` gia' creato dalla sessione principale. Controlla con
   `git branch --show-current`; se sei su un altro branch, fermati e dillo.
2. Segui il piano `Proposta_*.md` indicato nel compito. Non prendere decisioni di design che il piano non
   prende. Se il codice reale non corrisponde al piano (funzione inesistente, firma diversa, test che
   falliscono per una ragione non spiegata, confronto diverso dall'atteso), **fermati e riferisci** cosa
   hai trovato, dove, e le alternative che vedi.
3. Scelte minori non coperte dal piano (nomi locali, struttura interna di un test) sono tue: elencale.
4. Esegui suite e confronto con `tools/ai/verifica.sh`.
5. Scrivi `Analysis/Document/Rapporti/Rapporto_<tema>_<agente>.md` seguendo `Rapporti/TEMPLATE.md`.
6. Committa codice, test e rapporto sul tuo branch. Il trailer `AI-Agent:` lo aggiunge l'hook
   `commit-msg`; non scriverlo tu.

Comandi bash per gli agenti OpenCode: sono consentiti solo quelli elencati nel proprio agente, **tutti gli altri
sono vietati** (ricevi l'errore "a rule which prevents you..."): ripiega su un comando consentito invece di fermarti.
Usa comandi semplici, uno per volta (`grep`, `rg`, `git log -1 <hash>`, `git show`, `cat`, `sed -n`, `ls`, `wc`,
`bash tools/ai/verifica.sh ...`), niente cicli `for`/`while` o pipeline complesse.

Vietato agli esecutori: `git push`, `git stash`, `git reset --hard`, `git checkout`/`switch` di altri
branch, `git config`, installare pacchetti, modificare i file riservati sopra (un hook git rifiuta il
commit), dichiarare test eseguiti che non hai eseguito.
