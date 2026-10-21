# Warfare-Model Project Memory

Indice compatto (2026-10-21). Descrizioni estese e sessioni precedenti al 2026-10-13: [archivio_indice_dettagliato.md](archivio_indice_dettagliato.md).

## Start here
- [Sessione 2026-10-21 ProArt (ai-multimodel) — CHIUSA, pushato: ruoli multi-agente ridefiniti, prove U4 4/4, osboxes pronta](project_session_2026_10_21_multillm_summary.md) — voci 11 e 23 del manuale chiuse dal Piano allineato; ora si assegnano gli esecutori F8
- [Sessione 2026-10-21 ProArt — CHIUSA, pushato: manuale DES a dcedc541, Proposta F8 decisa (17-27)](project_session_2026_10_21_summary.md) — F8d logistica non fatta; esecutori F8 da assegnare dopo la ridefinizione dei ruoli multi-agente; Game_PC/Ollama verificato
- [Sessione 2026-10-20 osboxes — CHIUSA: F7b approvata, fotografia 982, suite 4555](project_session_2026_10_20_summary.md) — fuoco su posizione (Area_Fire, S29); hooksPath corretto; OpenCode NON installato su osboxes (da fare da ProArt, progetto ai-multimodel); main invariato
- [Sessione 2026-10-19 ProArt — CHIUSA, pushato: sistema multi-LLM (OpenCode) integrato, pilota riuscito](project_session_2026_10_19_summary.md) — AGENTS.md/CLAUDE.md, oc-developer come alternativa a des-developer; suite 4490, fotografia 970; prossimo F7b
- [Sessione 2026-10-18 ProArt — CHIUSA, pushato](project_session_2026_10_18_summary.md) — G5, F7a, A-10C; fotografia 970, suite 4490; prossimo F7b (decisione 15), pulizia doc, F6-B3, F8
- [Sessione 2026-10-17 ProArt — CHIUSA](project_session_2026_10_17_summary.md) — G3, G4a/b, uscita di scena; fotografia 878
- [Sessione 2026-10-16 osboxes — CHIUSA](project_session_2026_10_16_summary.md) — G2 approvato, fotografia 794
- [Sessione 2026-10-15 osboxes — CHIUSA](project_session_2026_10_15_summary.md) — F6-B2bis, G1, G2
- [Sessione 2026-10-13 osboxes — CHIUSA](project_session_2026_10_13_summary.md) — F6-B2; aperti F6-B3 S24-GLIDE, F7, F8, F9
- Sessioni precedenti (2026-05-05 … 2026-10-11): vedi archivio

## Piani e decisioni di design
- [Bingo G0-G5](project_bingo_reverse_route_decision.md) — riserva 5 min spinta MILITARE, soglia = resto rotta + riserva, basi alternative
- [Struttura Missione D1-D6/N1-N3, piano F0-F9](project_mission_structure_decisions.md) — Operazione ⊃ Missione; F0-F6 fatte
- [Motore DES sessioni virtuali](project_virtual_session_engine_design.md) — DES a coda eventi, contatti analitici CPA/TCPA; completo 2026-09-23
- [Modello di rotta unico](project_route_model_unification_plan.md) — DataType.Route/Edge/Waypoint; Route_Adapter è la frontiera
- [Gerarchia C2](project_c2_hierarchy_design.md) — C2 globale+regionale per lato; TASK 1 fatto, Fase 0/TASK 2 mai iniziati
- [Modulo mappe — FUTURO](project_map_module_plan.md) — servizio orografico comune; fonte docx non ancora letta
- [Scorta munizioni per arma](project_ammunition_per_weapon_stock.md) — A1/A2/A3/A5 fatte, A4/A6 aperte
- [Volumi rilevamento/intercettazione](project_detection_interception_volumes.md) — D-1..D-7 fatte; non assumere mai evitare rilevamento = evitare intercettazione
- [Analisi DCE](project_dce_analysis.md) — DCE gira fuori da DCS; .miz unica interfaccia di scrittura
- [Modello temporale DCS vs sintetico (storico)](project_campaign_temporal_model_dcs_vs_synthetic.md) — superato dal design C2
- [Refactor Region tattico/strategico](project_region_tactical_refactor_plan.md) — completo 2026-09-16
- [Fase 2 combat power con nebbia di guerra](project_fase2_recon_combat_power_plan.md) — completa; use_recon default False
- [Fase 2 decisioni di design](project_fase2_design_decisions.md) — tutte chiuse (#6, #7 rinviate)
- [Redesign combat power/priorità](project_priority_calc_combat_power_redesign.md) — Fase 0+1 fatte
- [Priorità aria: loadout per bersaglio](project_air_priority_target_specific_loadout.md) — completo, pushato
- [Vehicle/Ship/Aircraft asset_type vs category](project_vehicle_asset_type_category_conflict.md) — risolto 2026-09-15

## Progetto e ambiente
- [Moduli chiave e percorsi](project_key_modules.md)
- [Ambiente e macchine](project_dev_environment.md) — 3 macchine, hook SessionStart su allineamento con origin
- [Worktree: falsi esiti nei test](project_worktree_pythonpath_test_gotcha.md) — testare sempre dal checkout principale
- [Audit moduli](project_module_audit.md) — Fase 1 completa 2026-08-21
- [Test_Air_Route_Manager — risolto](project_test_air_route_manager_mismatches.md)
- [LoggerClass cwd — risolto](project_loggerclass_cwd_fix.md)
- [Block.get_recon_efficiency rimosso](project_block_get_recon_efficiency_removed.md)
- [Region dead code — risolto](project_region_unattributed_dead_code_removal.md)
- [Analysis/ e Obsidian](project_analysis_symlink_decision.md) — Obsidian nativo su ProArt
- [WIKI_LLM_SIMULATION fusa in Analysis/](project_wiki_llm_simulation_merge.md)
- [Rinomina_Campaign_State.py — NON cancellare](project_rinomina_campaign_state.md)

## Fatti di sottosistema
- [Aircraft_Data / Loadouts](project_aircraft_data_facts.md) · [Ship_Weapon_Data](project_ship_weapon_scoring.md) · [Air_Resources_Assigner](project_mra_state.md)
- [Campaign_State](project_campaign_persistence.md) · [Mobile/Military 2026-05-22](project_asset_military_2026_05_22.md) · [UML](project_uml_generation.md)

## Riferimenti esterni
- [WIKI_LLM_SIMULATION](reference_wiki_llm_simulation.md) — per questioni concettuali
- [Sabin, Simulating War](reference_philip_sabin_simulating_war.md) — Force/Space/Time/Command, Igo-Ugo

## Feedback (come lavorare qui)
- [Modelli e sforzi](feedback_model_effort_delegation.md) — principale Sonnet high, des-planner Opus high; esecuzione: des-developer (Claude) o oc-developer (OpenCode), a scelta; proporre e attendere conferma
- [Agenti paralleli + verifica pre-commit](feedback_parallel_agents_verification.md) — verificare sempre di persona
- [Core indifferente al simulatore](feedback_core_simulator_agnostic.md) — VINCOLO: la campagna gira senza adapter DCS
- [Nessuna visibilità → priorità BASSA](feedback_no_visibility_low_priority.md)
- [Combat power: selezione per azione](feedback_combat_power_action_selection.md)
- [venv per macchina](feedback_venv.md) — mai `python3` nudo
- [Classi base dei test](feedback_test_base_class.md) · [Pattern dei test](feedback_test_patterns.md) · [Import circolari](feedback_circular_import_workaround.md)
