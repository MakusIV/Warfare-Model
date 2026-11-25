# Sonde del blocco 4 della revisione L1 (2026-11-25)

Eseguite sul codice `a1559ad9` (interruttore `L1_IMMEDIATE_TARGET_RULE` spento nel codice, acceso in memoria dalla sonda).

Dopo la pulizia (`Proposta_L1_Pulizia_Interruttore.md`, 2026-11-25, merge `bbaa61c1`):
- `probe_l1.py` **non e' piu' eseguibile**: chiama `_may_intercept_volume`, `_may_intercept_revised` e `_interception_zone`,
  eliminati (`AttributeError`);
- `suite_l1_on.py` gira, ma l'assegnazione di `L1_IMMEDIATE_TARGET_RULE` non ha piu' effetto (il simbolo non esiste).

Sono documenti storici: i loro risultati stanno in `../L1_Esecuzioni_Cambiate.md`. Per rieseguirle serve il codice di un
commit fino a `170f4e0b` nel checkout principale (mai in un git worktree).
