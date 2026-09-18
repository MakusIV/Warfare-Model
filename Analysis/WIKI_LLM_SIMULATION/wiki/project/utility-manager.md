---
title: "Utility e Manager"
type: project-module
tags: [package-python, utility, logging, entry-point, architecture, dwm]
created: 2026-09-18
updated: 2026-09-18
code_paths: [Code/Dynamic_War_Manager/Source/Utility/, Code/Dynamic_War_Manager/Source/Manager.py]
related_decisions: ["[[c2-hierarchy-design]]"]
related: ["[[datatype]]", "[[logic-routing]]"]
---

## Scopo

Questo sottosistema raggruppa due categorie di codice molto diverse per maturità:

1. **Utility trasversali** (`Utility/LoggerClass.py`, `Utility/Utility.py`, `Utility/visualizer.py`): funzioni di supporto generiche (logging, geometria, fuzzy logic, conversioni di unità, validazione di tipo) usate — o pensate per essere usate — da tutti gli altri sottosistemi. Infrastruttura, non logica di dominio.
2. **`Manager.py`**, alla radice di `Source/`: il candidato storico per essere il "DWM" (Dynamic War Manager) descritto nello schizzo architetturale (`Analysis/Document/WM_Software_Structure.pdf`) — il nucleo che dovrebbe ricevere `mission_param` da DCS, aggiornare lo stato della campagna, e produrre `mission_result`.

Questa pagina **supera** il vecchio audit una-tantum `Analysis/Modules/11_Utility_Manager.md` (2026-08-16). Rispetto ad allora: **`LoggerClass.py` ha ricevuto un fix reale e verificato** (bug del path di log dipendente da `os.getcwd()`, corretto 2026-08-25); **`visualizer.py` è passato da prototipo isolato a strumento di debug attivamente documentato** (anche se ancora non importato da alcun modulo di produzione); **`Manager.py` resta invariato e non funzionante**, come già rilevato.

## File inclusi

- `Code/Dynamic_War_Manager/Source/Utility/LoggerClass.py` (63 righe) — classe `Logger`, wrapper su `logging` standard
- `Code/Dynamic_War_Manager/Source/Utility/Utility.py` (~1127 righe) — funzioni di supporto generiche: geometria 2D/3D con `sympy`, fuzzy logic con `scikit-fuzzy`, conversioni di unità aeronautiche, validazione, hashing/naming
- `Code/Dynamic_War_Manager/Source/Utility/visualizer.py` (~210+ righe) — modulo di plotting 2D/3D con `matplotlib` per debug visivo di minacce (`ThreatAA`/`Cylinder`) e rotte (`Route`) di `Air_Route_Manager`
- `Code/Dynamic_War_Manager/Source/Manager.py` (106 righe) — classe `Manager`, unico file alla radice di `Source/` oltre a `__init__.py`

Non esiste ancora alcun file di test per nessuno dei quattro moduli (confermato di nuovo: nessun `Test_Manager.py`, `Test_Utility.py`, `Test_LoggerClass.py`, `Test_visualizer.py` in `Code/Dynamic_War_Manager/Source/Test/`).

## Utility — funzioni principali

### `LoggerClass.py` — bug del path di log RISOLTO

A differenza del vecchio audit, il bug per cui il file di log veniva risolto come `os.getcwd()/logs` (crash se il processo veniva lanciato con una working directory diversa dalla root del repo) **è stato corretto**. Il codice attuale:

```python
self._repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
self._log_dir = os.path.join(self._repo_root, 'logs')
os.makedirs(self._log_dir, exist_ok=True)
self._log_fname = os.path.join(self._log_dir, 'log_' + self._class_name + '.log')
```

ancora `Logger(module_name, class_name, set_consolle_log_level=WARNING, set_file_log_level=DEBUG, name=None)`: wrapper su `logging.getLogger(module_name)` con due handler (console + file), pattern d'uso invariato: `logger = Logger(module_name=__name__, class_name='NomeClasse').logger`.

Bug/rischi ancora presenti, non toccati dal fix:
- Ogni chiamata a `Logger(...)` esegue `logging.basicConfig(level=DEBUG)` e crea nuovi handler aggiunti al logger nominato — istanziare più `Logger` con lo stesso `module_name` (import ripetuti/reload) accumula handler duplicati, con conseguente duplicazione dei messaggi in console/file. Nessun `Test_LoggerClass.py` verifica questo comportamento.
- Se `class_name` non corrisponde alla classe/modulo reale che istanzia il logger (vedi `Manager.py` sotto, dove `class_name='Region'`), i log finiscono nel file sbagliato — rischio strutturale del pattern, non del modulo in sé.

### `Utility.py`

Invariato rispetto al vecchio audit — nessuna delle funzioni elencate qui sotto è stata toccata dal fix del 2026-08-25 (quel fix ha riguardato solo la risoluzione della directory di log, stesso pattern applicato in parallelo anche qui per la cartella `logs/` usata da `Utility.py`, non le funzioni geometriche/di conversione):

- **Naming/ID**: `setId(name, id=None)`, `setName(name)`.
- **Validazione**: `validate_class(obj, class_name) -> bool` — verifica via MRO, meccanismo standard nel progetto per aggirare gli import circolari (vedi [[testing-conventions]]). `checkEventType(_type)` referenzia `EVENT_TYPE`, mai definita/importata in questo file → `NameError` se invocata. `check_side(side)`, `enemySide(side)`.
- **Geometria 2D/3D** (`sympy`): `calcVectorDiff`/`calcVectorSum` hanno ancora la componente `z` errata (usano l'indice `1` invece di `2`); `calcScalProd` ha ancora il secondo termine errato (`vect1[1]*vect2[2]` invece di `vect1[1]*vect2[1]`). Nessuna di queste funzioni ha test associati.
- **Fuzzy logic** (`scikit-fuzzy`): `calc_Production_Target_Priority`, `calc_Storage_Target_Priority`, `calc_Transport_Line_Target_Priority`, `calc_Threat_Level`, `evaluateMorale` — validati storicamente fuori dal repository (notebook Jupyter non incluso).
- **Conversioni aeronautiche**: `indicated_air_speed` ha ancora il bug `10^-6`/`10^-3` (XOR bit a bit invece di elevamento a potenza, `**`) — risultato numerico privo di senso fisico per qualunque input. `true_air_speed()` non ha lo stesso bug.
- **Varie**: `getClassName(obj)`, `get_sub_string(id_str, chiave)`.

### `visualizer.py` — da prototipo isolato a strumento di debug attivo (ma ancora non integrato in produzione)

Cambiamento rilevante rispetto al vecchio audit: il file ha ora un docstring esplicito che ne dichiara lo scopo — *"Utility di debug per la visualizzazione 2D/3D delle minacce (ThreatAA/Cylinder) e delle rotte (Route) calcolate da Air_Route_Manager. Serve per definire/verificare a colpo d'occhio gli scenari usati nei test (vedi Test_Air_Route_Manager.py) prima di scriverli."* — quindi non più uno script sperimentale anonimo, ma uno strumento di supporto alla scrittura dei test di `Air_Route_Manager`.

Altre differenze verificate rispetto al vecchio audit:
- **La doppia implementazione di `Cylinder` segnalata nel vecchio audit non c'è più**: la funzione `_cylinder_geometry(cylinder, ...)` estrae la geometria di plotting **da un vero `DataType.Cylinder`** (accede a `cylinder.bottom_center`, `cylinder.radius`, `cylinder.height`), non da una classe `Cylinder` locale duplicata.
- **Gestione robusta del backend matplotlib**: invece di un `matplotlib.use('TkAgg')` fisso (che rendeva l'import fragile in ambienti headless/CI), il modulo ora prova in sequenza `TkAgg`, `Qt5Agg`, `QtAgg`, `Agg`, verificando ciascuno creando e chiudendo davvero una figura di prova (non solo chiamando `matplotlib.use()`, che può "riuscire" silenziosamente e fallire solo alla prima creazione reale di una figura).
- Il vecchio workaround `os.chdir()` nel blocco `__main__` (aggiunto per aggirare il bug di `LoggerClass`/`Utility.py` risolto a valle) **è stato rimosso** in quanto ridondante dopo il fix del 2026-08-25.
- **Resta non importato da alcun modulo di produzione** — la classe `Space.add_route(route)` esiste come metodo di supporto al plotting, semanticamente non correlato a `Region.add_route()` (facile falso positivo se si cerca `add_route` col grep, vedi [[datatype]]).

## Manager.py — analisi del nucleo DWM (invariato)

Rivalutato integralmente il 2026-09-18: **nessuna riga di `Manager.py` risulta cambiata** rispetto al vecchio audit. Tutti i bug bloccanti restano presenti:

- `Manager('TestRegion')` continua a sollevare immediatamente `TypeError: Bad Arg: points must be a Dict:{ 'name': str, 'position': Point2D }`, perché `self._limes = Limes(self._region)` (riga 28) passa una stringa al costruttore di `Limes`, che si aspetta un `Dict` di punti. `_initialize_blocks()` non viene mai raggiunto.
- **Riga 16**: `logger = Logger(module_name=__name__, class_name='Region')` — `class_name` è ancora `'Region'`, non `'Manager'` (copia-incolla da `Region.py` mai corretto). I log di `Manager` finiscono ancora in `logs/log_Region.log`.
- **Righe 57-59**: `_is_valid_block(block)` confronta ancora `block.__class__.__name__ == 'Block'` letteralmente — nessuno dei blocchi reali creati da `_initialize_blocks()` (`Military`, `Production`, `Storage`, `Transport`, `Urban`, tutte sottoclassi di `Block`) supererebbe questa validazione.
- **Righe 97-106**: `__repr__`/`__str__` referenziano ancora attributi che `Manager` non possiede (`self._name`, `self._description`, `self._side`, `self._clients`, `self._server`, `self._warehouse`, copiati da `Region.py`); `__repr__` restituisce ancora una tupla di stringhe invece di una singola stringa.
- `Manager` resta **non importato da nessun altro modulo del progetto** (verificato di nuovo con grep ricorsivo).

### Nota di roadmap: `Manager.py` candidato al rename/eliminazione per liberare `C2_Manager`

È stata presa (ma non ancora eseguita nel codice) una decisione architetturale che riguarda direttamente questo file: la gerarchia C2 a due livelli descritta in [[c2-hierarchy-design]] introduce un modulo `C2_Manager` (globale, uno per side) e un `C2_Region_Manager` (uno per coppia side/regione) come nuovo nucleo di comando/controllo. Poiché `Manager.py` è oggi **orfano, non istanziabile e non funzionante** — e il nome "Manager" è quello naturale per il nuovo componente — la direzione concordata è di rinominare o eliminare l'attuale `Manager.py` per liberare il nome `C2_Manager`, invece di continuare a evolverlo verso l'orchestratore end-to-end originariamente previsto. Questo lavoro non è ancora iniziato: `Manager.py` esiste ancora, identico, alla data di questa pagina. Per il disegno completo della gerarchia C2 vedi [[c2-hierarchy-design]] (non duplicato qui).

### Layer Lua↔Python / mission_param / mission_result: gap invariato

Nessun cambiamento rilevato rispetto al vecchio audit:
- `mission_param`/`mission_result`: nessuna occorrenza in tutto il codice sorgente.
- `Context.py`: `DCS_DATA_DIRECTORY` resta un placeholder hardcoded per Windows, mai letto né scritto altrove.
- `Logic/Scenario_Manager.py` (classe `CommandControl`, nome file non corrispondente): resta un abbozzo con sezioni core a `pass`, bug bloccanti (`NameError` su `Region` non importata, `AttributeError` su `self._events` mai inizializzato), non importato da nessuno.
- `Asset/Asset.py` (`dcs_unit_data`, `_validate_dcs_data`) e `Asset/Mobile.py` (`checkParamDCS`, ancora con accessi diretti `data["campo"]` senza `.get()`) restano i punti di validazione dati "già pronti" più vicini a un adattatore Lua→Python, senza che nessun parser Lua reale esista.

## Stato attuale

| Modulo | Stato | Note |
|---|---|---|
| `LoggerClass.py` | Funzionante, usato ovunque | **Fix del path di log verificato** (2026-08-25, commit `9a7342a1`); rischio residuo di handler duplicati su import ripetuti; nessun test dedicato |
| `Utility.py` | Parzialmente funzionante | Bug matematici invariati (`calcVectorDiff`/`calcVectorSum`/`calcScalProd`/`indicated_air_speed`), nessun test |
| `visualizer.py` | Strumento di debug dichiarato, non integrato in produzione | Non più prototipo anonimo: docstring esplicito, usa `DataType.Cylinder` reale, backend matplotlib robusto; ancora non importato da alcun modulo che non sia sé stesso |
| `Manager.py` | Non funzionante / orfano, invariato | Non si istanzia; non importato da nessuno; candidato a rename/eliminazione per liberare `C2_Manager` (vedi [[c2-hierarchy-design]]) |
| `Logic/Scenario_Manager.py` (`CommandControl`) | Abbozzo puro, invariato | Bug bloccanti; sezioni "core" `pass`; non importato da nessuno |

Copertura test: **0%** per tutti i moduli di questo sottosistema, invariato rispetto al vecchio audit.

## Decisioni architetturali rilevanti

- [[c2-hierarchy-design]] — introduce `C2_Manager`/`C2_Region_Manager` come nuovo nucleo di comando/controllo a due livelli; impatta direttamente il destino di `Manager.py` (rename/eliminazione pianificati, non ancora eseguiti). Vedi la sezione dedicata sopra per il dettaglio locale a questo sottosistema; il disegno completo della gerarchia C2 vive nella pagina della decisione, non qui.

## Note

- Il fix di `LoggerClass.py` è stato applicato in coppia con un fix identico in `Utility.py` per la stessa risoluzione `os.getcwd()`-dipendente della cartella `logs/` — entrambi ancorati a `__file__`, quattro livelli sopra `Code/Dynamic_War_Manager/Source/Utility/`, quindi portabili identicamente su ogni clone del repository.
- Il fix ha reso ridondante e quindi rimosso il workaround `os.chdir()` che `visualizer.py` usava nel proprio blocco `__main__` per aggirare lo stesso bug.
- Import path convention del progetto (`from Code.Dynamic_War_Manager.Source.X.Y import Z`, mai la forma abbreviata `from Dynamic_War_Manager.Source...`) — vedi [[testing-conventions]] per il dettaglio e per il motivo per cui violarla è particolarmente insidioso in questo progetto.
