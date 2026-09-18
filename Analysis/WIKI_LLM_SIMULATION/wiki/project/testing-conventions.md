---
title: "Convenzioni di testing"
type: project-module
tags: [testing, unittest, convenzioni, architecture, dwm]
created: 2026-09-18
updated: 2026-09-18
code_paths: [Code/Dynamic_War_Manager/Source/Test/]
related_decisions: []
related: ["[[datatype]]", "[[utility-manager]]"]
---

## Scopo

Questa pagina non deriva da un file sorgente, ma da un insieme di lezioni operative accumulate nella memoria di progetto (`.claude/memory/feedback_*.md`, `.claude/memory/project_*.md`) su come scrivere ed eseguire test in questo repository senza incorrere in falsi positivi/negativi. Non esisteva un audit equivalente prima d'ora: è contenuto nuovo per il wiki, non una revisione di una pagina precedente. Lo scopo è dare a un futuro contributore (umano o agente) una checklist concreta prima di scrivere o eseguire test in questo progetto.

## Convenzioni obbligatorie

### 1. Le classi base di test non devono ereditare da `unittest.TestCase`

Quando si crea una classe base condivisa per parametrizzare più scenari di test (es. `_ScenarioTestBase` con un attributo di configurazione `_CFG`), la classe base **non deve** ereditare da `unittest.TestCase`. Solo le sottoclassi concrete devono farlo, ereditando da entrambe:

```python
class _ScenarioTestBase:  # NO unittest.TestCase qui
    _CFG = {}
    def test_something(self): ...

class TestConcreteScenario(_ScenarioTestBase, unittest.TestCase):
    _CFG = _SCENARIO_CONFIGS[0]
```

**Perché**: il meccanismo di discovery di `unittest` trova e istanzia anche le classi base se ereditano da `TestCase`, causando `KeyError` (o simili) su un `_CFG = {}` vuoto mai pensato per essere eseguito direttamente.

### 2. Workaround per l'import circolare Aircraft/Vehicle/Ship

Esiste un import circolare irrisolto: `Aircraft.py → Aircraft_Data → Aircraft_Loadouts → Aircraft_Weapon_Data → Aircraft.py`. Anche `Vehicle.py` e `Ship.py` lo attivano (via `Ground_Weapon_Data → Aircraft`). Non è possibile importare direttamente `Vehicle`, `Ship` o `Aircraft` in un file di test — l'import fallisce o si blocca a metà inizializzazione.

Due pattern di workaround validati, entrambi in uso nel repository:

1. **Stub class** (usato in `Test_Military.py`): creare uno stub a livello di modulo con `_Vehicle = type('Vehicle', (), {})`, poi assegnare `mock.__class__ = _Vehicle` sui mock. `Utility.validate_class(mock, "Vehicle")` verifica il nome nella MRO, quindi funziona anche con classi stub. Nota collegata: il setter `Block.assets` valida `isinstance(v, Asset)` — per aggirarlo nei test si assegna direttamente `block._assets = {...}` invece di `block.assets = {...}`.
2. **Pre-iniezione in `sys.modules`** (usato in `Test_Mobile.py`, più radicale): iniettare l'intera catena di import di `Aircraft` in `sys.modules` come `MagicMock` **prima** che qualunque import reale venga eseguito. Include moduli fake per `Vehicle_Data` (`_vd_mod.Vehicle_Data = _FakeVehicleData`, con `_registry = {}`) e `Ground_Weapon_Data` (`_gwd_mod.GROUND_WEAPONS = _FAKE_GW`, dizionario mutabile). `Ship_Data`/`Ship_Weapon_Data` possono invece essere importati direttamente (nessuna dipendenza circolare lì). In questo scenario, `assertIsInstance(cyl, Cylinder)` fallisce per via del doppio percorso di modulo: usare `type(cyl).__name__ == 'Cylinder'` al suo posto.

**Implicazione da tenere a mente**: entrambi i pattern significano che le suite "verdi" per queste classi non esercitano mai la catena di import realmente completa — un bug di import può restare nascosto a lungo (è già successo: un path di import errato non è stato rilevato per molto tempo proprio a causa di questo).

### 3. Mocking del logger, timing delle patch, convenzioni CLI

- Mock del logger: `patch("Code.Dynamic_War_Manager.Source.Asset.XXX.logger", MagicMock())`.
- Per i test sui punteggi di combattimento, mockare anche `Aircraft_Weapon_Data.logger` e `Aircraft_Loadouts.logger`.
- Se il mock deve avere effetto dopo che l'import è già avvenuto, usare `p = patch(...); p.start()` invece di `with patch(...):` (il context manager arriva troppo tardi in quei casi).
- I file `Test_*.py` espongono un menu interattivo di default, con flag `--tests-only` e `--tables-only`; non tutti i file implementano `--tests-only` (es. `Test_Ship_Weapon_Data.py`) — in quel caso usare `python -m unittest discover` mirato al file.
- Pattern di invocazione tipico per un singolo file: `python Code/Dynamic_War_Manager/Source/Test/Test_XXX.py --tests-only`.
- `Test_Aircraft_Data.py` espone `_all_loggers_mocked()` che mocka in un colpo solo `_LOGGER_PATH`, `_LOADOUTS_LOGGER_PATH`, `_GWD_LOGGER_PATH`, `_AWD_LOGGER_PATH`.

### 4. Convenzione di import: sempre il path assoluto completo

Ogni modulo sotto `Code/Dynamic_War_Manager/Source/` deve importare con il path completo:

```python
from Code.Dynamic_War_Manager.Source.X.Y import Z
```

**Mai** la forma abbreviata `from Dynamic_War_Manager.Source...` (path incompleto): causa `ModuleNotFoundError` quando il processo viene lanciato dalla root del repository. Questa convenzione non è solo stilistica — vedi il punto 6 sotto per come la sua violazione (o anche solo la sua coesistenza con import relativi interni) può produrre risultati di test silenziosamente sbagliati.

Per lanciare l'intera suite in modo affidabile:

```
python -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_*.py"
```

da eseguire dalla root del repository.

## Trappola critica: eseguire i test dentro un git worktree collegato dà risultati FALSI

Questo è il punto più importante e meno intuitivo di questa pagina — va letto per intero da qualunque agente (o persona) che lavori dentro `.claude/worktrees/<nome>/...` su questo progetto.

### Sintomo

Un test che dovrebbe passare, dato il codice realmente presente su disco nel worktree, fallisce invece con un errore che corrisponde alla logica **vecchia**, pre-modifica (vecchio formato del messaggio di log, vecchio tipo di eccezione) — come se il file appena modificato non venisse mai caricato. Aggiungere una `print()` in cima alla funzione modificata non produce nulla nell'output del test, anche se la funzione viene sicuramente raggiunta (la riga di log dell'eccezione che solleva compare comunque).

### Causa radice

Il codebase usa import assoluti ovunque, del tipo `from Code.Dynamic_War_Manager.Source.Context.Campaign_State import CampaignState` (vedi punto 4 sopra), **insieme** a import in stile relativo usati all'interno dell'albero `Source/` stesso, del tipo `from Context.Campaign_State import CampaignState`. La variabile d'ambiente `PYTHONPATH` della shell è impostata in modo fisso su `/home/marco/Sviluppo/Warfare-Model/Code:/home/marco/Sviluppo/Warfare-Model` — cioè sul **checkout principale**, non su un worktree qualsiasi.

Questo permette a Python di risolvere lo **stesso modulo fisico sotto due nomi puntati diversi**:
- `Context.Campaign_State` — trovato tramite la working directory corrente (dentro qualunque worktree si stia eseguendo);
- `Code.Dynamic_War_Manager.Source.Context.Campaign_State` — trovato tramite `PYTHONPATH`, che punta **sempre al checkout principale**, indipendentemente da quale worktree si stiano davvero eseguendo i test.

Questi diventano due voci separate in `sys.modules`, ciascuna con propri oggetti classe. Il modulo che vince — cioè quello effettivamente usato a runtime da un terzo modulo già importato — dipende da quale dei due percorsi è stato raggiunto per primo. Il risultato: un test eseguito dentro un worktree può finire per esercitare silenziosamente il codice **stantio del checkout principale** invece delle modifiche del worktree.

### Come riconoscerlo

Controllare il nome del logger in una riga di log WARNING/ERROR sollevata dal codice sospetto: un nome completamente qualificato come `Code.Dynamic_War_Manager.Source.Context.Campaign_State` (invece della forma breve `Context.Campaign_State`) è il segnale. In alternativa, confrontare direttamente i due file (`<worktree>/Code/.../X.py` vs `/home/marco/Sviluppo/Warfare-Model/Code/.../X.py`): se sono diversi e il test si comporta come la versione del checkout principale, è confermato.

### Come risolverlo

Non fidarsi mai di un'esecuzione di test lanciata da dentro `.claude/worktrees/<agente>/...` su questo progetto come verità di base. Due opzioni:

- **(a)** Applicare le modifiche del worktree su un branch nel **checkout principale** (`/home/marco/Sviluppo/Warfare-Model`, dove `PYTHONPATH` e cwd coincidono) ed eseguire lì la suite. Metodo effettivamente usato in produzione: estrarre il diff con `git diff`, applicarlo con `git apply` su un branch nuovo nel checkout principale, poi lanciare la suite piena lì.
- **(b)** Sovrascrivere `PYTHONPATH` in modo che punti al worktree prima di eseguire i test al suo interno.

Questa non è una particolarità di un modulo specifico: la combinazione di import assoluti + `PYTHONPATH` fisso è una caratteristica **dell'intero progetto**, quindi la trappola può colpire qualunque lavoro futuro lasciato in un `.claude/worktrees/*` su una qualunque delle 3 macchine di sviluppo.

## Copertura test — quadro sintetico (per contesto, non normativo)

Alcuni package hanno copertura solida e matura (`DataType.State`: 67 test, `DataType.Payload`: 7 test, `DataType.Cylinder`: 15 test — vedi [[datatype]]); altri hanno 0% di copertura nonostante siano infrastruttura usata ovunque (`Utility/LoggerClass.py`, `Utility/Utility.py`, `Manager.py` — vedi [[utility-manager]]). Prima di introdurre nuove funzionalità in un modulo a copertura zero, vale la pena considerare se il primo passo utile non sia proprio un test minimo di baseline (anche solo per documentare via test il comportamento — corretto o rotto — attuale).

## Decisioni architetturali rilevanti

Questa pagina descrive un processo (come si scrivono/eseguono i test), non una decisione architetturale sul dominio applicativo — non ci sono decisioni di `wiki/decisions/` direttamente collegate. La trappola PYTHONPATH/worktree documentata sopra è una caratteristica strutturale dell'ambiente di sviluppo, non una scelta di design del software applicativo.

## Note

- Le convenzioni di questa pagina si applicano sia a lavoro umano che ad agenti automatici (Claude Code o altri) che scrivono o eseguono test in questo repository.
- Se in futuro il progetto elimina la coesistenza di import assoluti/relativi descritta sopra (unificando tutto sotto `Code.Dynamic_War_Manager.Source...`), la trappola worktree/PYTHONPATH scompare da sola — ma finché coesistono entrambi gli stili, resta un rischio concreto ad ogni sessione di lavoro in un worktree.
