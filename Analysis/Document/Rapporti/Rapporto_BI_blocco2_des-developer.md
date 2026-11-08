# Rapporto BI blocco 2 — des-developer

- **Agente / modello**: `des-developer` / Claude Sonnet 5.5
- **Branch**: `ai/des-bi-blocco2` · **piano eseguito**: `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` §5.3 (5.3.1-5.3.6)
- **Data**: 2026-11-08

## 1. Esito in una riga
Completato, nessuno scostamento di design. Suite 4829 OK; confronto a interruttore spento 1009 identiche + 20 nuove (S32-DWELL); sonda B-1 come atteso (cambiano esattamente le 6 esecuzioni `S19AD/S19-<0..5>/tor_rear`).

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Logic/Fire_Control.py` | costanti `AD_LAND`, `AD_NAVAL`, `AD_TARGET_DOMAINS`, `AD_SIZE_GATED_NAVAL`, `AD_DETECTABLE_DEFAULT` (dopo `KNOT_MS`); funzioni `munition_class(weapon)` e `intercept_domains_for(weapon)`; `shot_spec_for` passa `intercept_domains=intercept_domains_for(weapon)` (calcolo di `interceptable` intatto); docstring del modulo (punto `intercept_domains`) |
| `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py` | interruttore `BI_AD_TARGET_RULE = False` (accanto a `D5_DWELL_TIME`) e costante `AD_DOMAINS`; campo `ShotSpec.intercept_domains: Optional[FrozenSet[str]] = None` in coda, con validazione in `__post_init__`; `_EngagementRun.__init__`: `ad_target_rule`, `ad_domain_cache`; metodi `_ad_domain`, `_admissible`; `_on_resolve`: conteggio `interceptable_rounds` e condizione del ciclo di allocazione; docstring del modulo (punto 4) |
| `Code/Dynamic_War_Manager/Source/Test/Test_Fire_Control.py` | nuova classe `TestInterceptDomains` (14 test) |
| `Code/Dynamic_War_Manager/Source/Test/Test_Engagement_Resolver.py` | nuove classe stub `Ship` e `TestAirDefenceTargetRule` (12 test) |
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S19_Air_Defence.py` | nuova classe `TestS19AdTargetRule` (2 test di sessione); import di `patch` e di `Engagement_Resolver as ER` |
| `Analysis/Document/Rapporti/Sonde_Bersagli_Intercettabili/probe_switch_on.py` | sonda B-1 (nuova) |
| `Analysis/Document/Rapporti/Sonde_Bersagli_Intercettabili/b1/esito.txt` | riepilogo dell'uscita della sonda (nuovo, come `b0/esito.txt`) |
| `Analysis/Document/Rapporti/Sonde_Bersagli_Intercettabili/LEGGIMI.md` | solo la riga B-1 della tabella: da "da scrivere" a "eseguita" |
| `Analysis/Document/Rapporti/Rapporto_BI_blocco2_des-developer.md` | questo rapporto |

## 3. Scostamenti dal piano
Nessuno. Precondizioni verificate: branch `ai/des-bi-blocco2` con `git status` pulito; `Proposta_Dati_Bersagli_Intercettabili.md` con stato "DECISO dall'utente il 2026-11-07"; righe citate coincidenti (`Fire_Control.py:763-768` calcolo di `interceptable`, `:786` unica `ShotSpec(` di produzione; `Engagement_Resolver.py` `D5_DWELL_TIME` a `:525`, campo `interceptable` a `:614`, conteggio `interceptable_rounds` a `:3291`, condizione a `:3350`); `restrict_by_policy` non usa `dataclasses.replace`: filtra le opzioni senza ricostruirle (5.3.3 soddisfatto).

## 4. Scelte minori prese
- `AD_DOMAINS = frozenset({'land','naval'})` nel risolutore (il piano dice "in `{'land','naval'}'" senza nominare la costante); la validazione di `ShotSpec` richiede un `frozenset` (un `set` semplice come `{'land'}` viene rifiutato con `ValueError`, coerente con "None oppure frozenset").
- `munition_class`: un valore dichiarato non stringa e' ignorato e si passa alla derivazione; per `kind` 'missile' la derivazione e': `MISSILES_AAM` -> 'aam'; dominio 'ground' con `Anti_Tank` -> 'atgm'; `Anti_Air` o `MISSILES_SAM` -> 'sam'; altrimenti None. Effetto sui registri veri: nessuna arma resta senza classe (verificato con un test che percorre i tre registri).
- `intercept_domains_for` usa `bool(data.get('ad_detectable', AD_DETECTABLE_DEFAULT[classe]))`.
- Cache del dominio degli intercettori: dizionario `ad_domain_cache` nella run (analogo a `zone_cache`).
- La condizione di allocazione e' andata a capo con `\` per rispettare la lunghezza di riga del file.
- Test: piu' di quelli stimati dal piano (28 invece di ~21): in `TestInterceptDomains` ho separato i casi del piano in test distinti, aggiunto la copertura di tutte le armi dei registri (`test_every_registry_weapon_has_a_class_and_a_frozenset`), il caso `None` (arma non classificabile), il flag/default `ad_detectable` e `munition_class` derivata; in `TestAirDefenceTargetRule` ho aggiunto il caso `{'land'}` solo terrestri, R-INT con tempo di volo nullo e il default dell'interruttore. Stub di nave: classe `Ship` (il risolutore riconosce le navi per nome di classe).
- Test di sessione: nuova classe `TestS19AdTargetRule` nel file di S19AD (sessione `S19-0`, Tor arretrato, interruttore acceso con `patch.object(ER, 'BI_AD_TARGET_RULE', True)`), sul modello di `TestS19MissionRulesReplaceTheTestFilters` che non e' eseguita dalla fotografia; `Test_Session_Simulator.py` non e' stato toccato.
- La sonda stampa anche un'analisi post-confronto (righe `B1_*`) oltre al confronto `--summary`; il riepilogo e' copiato in `b1/esito.txt`. Ho aggiornato la riga B-1 di `LEGGIMI.md` (non e' un `Proposta_*.md`).

## 5. Costanti stimate
Nessuna costante tarata. Le tre tabelle `AD_TARGET_DOMAINS`, `AD_SIZE_GATED_NAVAL`, `AD_DETECTABLE_DEFAULT` sono scelte di progetto [S] dichiarate nel commento (default di `ad_detectable` = STIMA [S], BI-7); nel codice sono gia' etichettate come tali. Sui registri veri i default non sono usati: tutte le 52 voci `MISSILES_ASM` dichiarano `munition_class` e `ad_detectable` (blocco 1).

## 6. Verifiche eseguite
- Test singoli (interprete `.direnv/python-3.12/bin/python3`): `Test_Fire_Control` Ran 109 OK; `Test_Engagement_Resolver` Ran 332 OK; `Test_Session_Scenarios_S19_Air_Defence` Ran 12 OK; `Test_Session_Simulator` Ran 167 OK.
- Suite (`bash tools/ai/verifica.sh suite`): `ESITO suite: exit code 0 · interprete .direnv/python-3.12/bin/python3` · `Ran 4829 tests in 580.712s` · `OK (skipped=7)`. 4829 = 4801 + 28 nuovi (14 + 12 + 2).
- Confronto con la fotografia, interruttore SPENTO (`verifica.sh confronto`): `UNCHANGED (1009)` · `compared 1029 runs: 20 difference lines (492.3 s)`. Controllato sulle catture: le 20 esecuzioni nuove sono tutte `S32-DWELL`, 0 esecuzioni cambiate, 0 mancanti. Come atteso dal piano (1009 identiche; le 20 NEW S32-DWELL non sono nella fotografia versionata).
- Sonda B-1 (`PYTHONPATH=. .direnv/python-3.12/bin/python3 Analysis/Document/Rapporti/Sonde_Bersagli_Intercettabili/probe_switch_on.py .ai-run/sonde_bersagli/b1`), interruttore acceso in memoria; non scrive nel repository:
  - `compared 1029 runs: 152 difference lines (490.5 s)` · `PROBE_RC 1` (atteso: le NEW contano come differenze);
  - `B1_CHANGED_KEYS 6`, `B1_EXPECTED_SET OK`: cambiano ESATTAMENTE `S19AD/S19-0..5/tor_rear`, nessun'altra; `B1_NEW_KEYS 20 ['S32-DWELL']`;
  - eventi di intercettazione 3 -> 0 in ognuna (nessun `InterceptionEvent` del Tor, `B1_TOR_ZERO True`); eventi di danno: S19-0 6->12, S19-1 5->11, S19-2 6->11, S19-3 5->11, S19-4 6->10, S19-5 6->8 (`B1_MORE_DAMAGE True`);
  - `B1_ANTISHIP_RUNS 8 rounds_stopped 351`, `B1_ANTISHIP_IDENTICAL True`: le 351 intercettazioni antinave di S6/S16 sono identiche.
  Uscita completa in `.ai-run/sonde_bersagli/b1/log.txt` (non versionata), riepilogo in `Sonde_Bersagli_Intercettabili/b1/esito.txt`.

## 7. Limiti noti e dubbi per la sessione principale
- Il numero dei test nuovi (28) supera il "circa 21" del piano; nessun test e' stato rimosso o indebolito.
- Con la regola accesa, `SalvoResolution.capacity` (somma delle disponibilita') non e' filtrata per dominio, come per il piano (si conta solo `interceptable_rounds`); non toccato.
- La sonda B-1 verifica le esecuzioni della fotografia con la fire control dei registri; la classificazione dei missili nei registri e' quella del blocco 1 (non rivalutata).
- Non verificato: manuale DES e documenti (blocco 4), scenario S35 (blocco 3): fuori dal compito.

## 8. Stato git
Vedere l'output riportato nel messaggio finale (`git status --short` e `git log --oneline -5` dopo il commit).
