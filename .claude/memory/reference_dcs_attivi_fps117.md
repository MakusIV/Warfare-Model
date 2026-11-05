---
name: reference-dcs-attivi-fps117
description: "Classificazione in DCS dell'FPS-117 e degli asset 'attivi' diversi da vehicle/ship/aircraft: cosa e' confermato dal repo, cosa del documento Google AI e' dubbio, cosa resta da verificare nell'editor (2026-11-05)"
metadata:
  type: reference
---

Fonte: `Analysis/Document/In DCS l'asset FPS-117 è un componente attivo ... - Cerca con Google.md` (output di Google AI Mode, NON fonte primaria) letto il 2026-11-05 e confrontato con le fonti del repo.

**Confermato (repo):**
- L'FPS-117 esiste in DCS come unita' EWR attiva (anche con cupola); la variante di oggetto statico e' passiva (`documentazione_dcs/dcs_lua/StaticObject.md`: "just a passive variant of Unit"). Lo script DCE `ATO_ThreatEvaluation.lua:1215` lo riconosce con `unit.type == "FPS-117"`, classe "EWR".
- `Unit.Category` (`dcs_lua/Unit.md`) = AIRPLANE, HELICOPTER, GROUND_UNIT, SHIP, STRUCTURE; `Object.Category` include anche STATIC, SCENERY, BASE (aeroporti/FARP, `Airbase.md`). DCE legge le unita' EWR dai gruppi `vehicle` della missione (`DC_Prune.lua:62`, `ATO_ThreatEvaluation.lua:1560-1602`).
- Quindi un sito fisso attivo come l'FPS-117 e' una `GROUND_UNIT` (gruppo `vehicle` del .miz): la scelta del blocco C D-4b (`Vehicle` immobile + `fixed_site`, [[project-sensori-d4b-d4c]]) e' coerente con DCS e l'adapter e' banale. "Attivo" in DCS dipende da sensori/armi, non dalla mobilita'.

**Dubbio nel documento Google (non usare come dato):** la frase "non e' Vehicle ma `Ground Crew`" non trova riscontro (nessuna fonte del repo, e lo stesso testo lo mette in Air Defence); il secondo elenco ("altri attivi") mescola categorie: fanteria = GROUND_UNIT, SAM Hawk/S-75/S-125 = unita' terrestri, FARP/aeroporti = oggetti base con servizi (non unita'), bunker/postazioni costiere = statici passivi o armi attive a seconda del tipo.

**Discrepanza di portata:** DCE usa 461 km (`range = 461000`) per l'FPS-117 e 330 km per l'1L13; il nostro registro ha 330 km per l'FPS-117 (Lockheed, Pd 80 % su 1 m2) mentre i 461 km corrispondono ai 250 nmi strumentali della scheda Wikipedia. Sono due definizioni di portata, non un errore; la portata effettiva in DCS e' sconosciuta.

**Aperto:** verificare nell'editor DCS (o in un .miz reale) la categoria esatta dell'FPS-117 (si attende GROUND_UNIT / gruppo `vehicle`, sottogruppo Air Defence). Fatto reale solo dall'utente.

**Decisione 2026-11-05:** solo registrare; nessuna tassonomia degli "attivi" da pianificare ora (i casi veri fuori da Vehicle/Ship/Aircraft sono poche strutture armate e le basi; `Military.air_detection_threats` filtra solo Vehicle/Ship: da riaprire solo se servono strutture armate attive).
**How to apply:** per classificare un asset DCS come attivo guardare sensori/armi del registro, non la classe; non fidarsi del documento Google per le categorie dell'editor.
