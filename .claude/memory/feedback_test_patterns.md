---
name: feedback-test-patterns
description: "Conventions for writing/running tests in this project — logger mocking, patch timing, CLI flags, PDF table generation"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 54069b25-fc3b-495d-81bb-9efd11133381
  modified: 2026-08-16T16:08:16.214Z
---

- Logger mock: `patch("Code.Dynamic_War_Manager.Source.Asset.XXX.logger", MagicMock())`
- Per combat score test: mock anche `Aircraft_Weapon_Data.logger` e `Aircraft_Loadouts.logger`
- Se il mock serve dopo l'import: usare `p = patch(...); p.start()` invece di `with patch(...)`
- Menu dei file Test_*.py: interactive (default), `--tests-only`, `--tables-only` flags (non tutti i file implementano `--tests-only`, es. `Test_Ship_Weapon_Data.py` — usare `python -m unittest discover` in quel caso)
- PDF: matplotlib + PdfPages (one page per category), RdYlGn heatmap colormap
- Comando tipico: `python Code/Dynamic_War_Manager/Source/Test/Test_XXX.py --tests-only`
- `_all_loggers_mocked()` in Test_Aircraft_Data: mocka `_LOGGER_PATH`, `_LOADOUTS_LOGGER_PATH`, `_GWD_LOGGER_PATH`, `_AWD_LOGGER_PATH`
- Base class per i test: NON deve ereditare da `unittest.TestCase`, vedi [[feedback_test_base_class]]
- Circular import Aircraft/Vehicle/Ship: vedi [[feedback_circular_import_workaround]]

**Import path convention (fixed 2026-08-16):** tutti i moduli sotto `Code/Dynamic_War_Manager/Source/` devono importare con il path completo `from Code.Dynamic_War_Manager.Source.X.Y import Z` — mai `from Dynamic_War_Manager.Source...` (path incompleto, causava `ModuleNotFoundError` quando eseguito da repo root). Per lanciare l'intera suite in modo affidabile: `python -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_*.py"` da repo root. Vedi [[project_module_audit]].
