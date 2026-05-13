---
name: Pattern mixin per test base class
description: Le classi base di test non devono ereditare da unittest.TestCase per evitare discovery automatica
type: feedback
---

Le classi base condivise di test (es. `_ScenarioTestBase`) NON devono ereditare da `unittest.TestCase`. Usare pattern mixin: solo le sottoclassi concrete ereditano da entrambi.

```python
class _ScenarioTestBase:  # NO unittest.TestCase qui
    _CFG = {}
    def test_something(self): ...

class TestConcreteScenario(_ScenarioTestBase, unittest.TestCase):
    _CFG = _SCENARIO_CONFIGS[0]
```

**Why:** Python `unittest` discovery trova e istanzia anche le classi base, causando `KeyError` su `_CFG = {}` vuoto.
**How to apply:** Ogni volta che si crea una classe base di test con dati di configurazione variabili, usare il pattern mixin.
