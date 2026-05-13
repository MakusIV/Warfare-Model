---
name: UML Generation Workflow
description: Procedura e convenzioni per generare diagrammi UML dei moduli del progetto
type: project
---

## Workflow UML Diagrams

**Strumento:** PlantUML con jar in `/home/marco/.vscode/extensions/jebbs.plantuml-2.18.1/plantuml.jar`
**Renderer:** `java -jar <plantuml.jar> -tpng -o <output_dir> <source.plantuml>`

### Struttura file
- **Sorgenti PlantUML:** `/home/marco/Sviluppo/Warfare-Model/Analysis/UML/<ModuleName>.plantuml`
- **Output PNG:** `/home/marco/Sviluppo/Warfare-Model/out/Analysis/UML/<ModuleName>/`
- Ogni file `.plantuml` contiene più blocchi `@startuml ... @enduml`, ognuno genera un PNG separato.

### Tipi di diagrammi usati per moduli Python
Per ogni modulo, generare i seguenti diagrammi:

| Tipo | Nome file PNG | Contenuto |
|---|---|---|
| Component Diagram | `<Module>.Component.png` | Dipendenze esterne del modulo (import, libs) |
| Class Diagram | `<Module>.<Topic>.png` | Strutture dati / architettura interna (es. FuzzyLogic) |
| Activity Diagram | `<functionName>.png` | Uno per funzione complessa, algoritmo step-by-step |
| Sequence Diagram | `<functionName>.png` | Per funzioni che orchestrano chiamate ad altre funzioni |

### Moduli già documentati con UML
- `Tactical_Evaluation.py` → `Analysis/UML/Tactical_Evaluation.plantuml` (2026-03-16)
  - 8 diagrammi: Component, FuzzyLogic, 5 Activity, 1 Sequence

### Convenzioni stile PlantUML
```
skinparam ActivityBackgroundColor #D9E8FF
skinparam ActivityBorderColor #336699
skinparam ArrowColor #336699
skinparam backgroundColor #FEFEFE
```
- Usare `autonumber` nei sequence diagram
- Usare `partition` per raggruppare passi logici negli activity diagram

**Why:** Il team riutilizzerà questa procedura per documentare altri moduli del progetto.
**How to apply:** Quando si chiede di generare UML per un nuovo modulo, seguire questo workflow esatto (stessa struttura cartelle, stessi tipi di diagrammi, stesso stile).
