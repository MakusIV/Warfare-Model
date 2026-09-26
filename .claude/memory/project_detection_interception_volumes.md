---
name: project-detection-interception-volumes
description: "Volumi di rilevamento e intercettazione distinti nel pianificatore rotte (Air_Route_Manager) — D-1..D-7 implementate 2026-09-26 (commit 815dc35f); D-4b/c, D-5 opzione 2, D-8 ancora da fare"
metadata:
  type: project
  originSessionId: b183e431-8211-4d82-bd56-aecf65301f45
  modified: 2026-09-26T21:38:40.854Z
---

**Problema risolto**: `Mobile.air_defense_volume()` costruiva da sempre UN SOLO `Cylinder` per asset
di difesa aerea, esplicitamente "the engagement envelope" (portata dell'arma) — nessun volume di
rilevamento distinto basato sulle prestazioni del sensore di scoperta, anche se questi dati esistono
già nei registri (SA-6 verificato: `acquisition_range` 75 km, `tracking_range` 28 km, portata arma
24 km — mai usati dal pianificatore). Origine della richiesta: l'utente ha specificato che rilevamento
e intercettazione dipendono da sistemi (radar di scoperta vs radar/sistema di guida) spesso distinti,
e che alcuni SAM hanno prestazioni diverse per i due, richiedendo due volumi geometrici separati per lo
stesso sito. Dettaglio completo in `Analysis/Document/Proposta_Volumi_Rilevamento_Intercettazione.md`.

**Design e implementazione** (commit `815dc35f`): base comune `AirThreat`; `ThreatAA` (intercettazione,
stesso costruttore di prima, `acquisition_time` al posto di `min_detection_time` con alias,
`calcMaxLenghtCrossSegmentInterception` rinominata con alias — quest'ultima corretta in un commit
precedente, `199e0cdf`, formula dimensionalmente incoerente riscritta da zero con un modello fisico
esplicito); `DetectionThreat` nuova (`danger_level=0`, raggio limitato dall'orizzonte radar in funzione
di quota e altezza d'antenna, formula standard dell'orizzonte radio). `calcRoute` riceve `ThreatMode`
{`AVOID`, `CROSS_UNINTERCEPTED`, `AVOID_DETECTION`} (il vecchio `intersecate_threat` resta alias) e una
lista separata di minacce di rilevamento.

**Decisione di design importante da ricordare**: `AVOID_DETECTION` aggira il rilevamento ma attraversa
l'intercettazione con la stessa corda limitata di `CROSS_UNINTERCEPTED` quando serve — **non deve mai
assumere per costruzione** che evitare il rilevamento eviti automaticamente l'intercettazione, anche
se per i SAM tipici (sensore/lanciatore co-locati, rilevamento > intercettazione, volumi annidati) è
quasi sempre vero — va sempre verificato sui valori dichiarati caso per caso (rilevante soprattutto per
future reti EWR non co-locate col lanciatore). "Un sensore che vede = rilevato" non richiede logica di
unione: il ciclo di evitamento valuta già ogni volume indipendentemente, anche se annidato in un altro.

Metriche di rotta separate dal pericolo di intercettazione: `detection_exposure_s`,
`first_detection_time_s`, `warning_time_s`, `max_detection_probability` (replica la formula
`detection_probability` del risolutore DES come metrica di pianificazione, senza toccarla).

**Fuori scope in questo intervento, ancora da fare**:
- **D-4b**: ricerca dati EWR (confermato dall'utente: da WWII a Guerra Fredda, non solo Guerra Fredda).
- **D-4c**: ricerca dati sensore visivo di ripiego per ZSU-57-2/M163 (oggi senza sensore radar).
- **D-5 opzione 2** (scelta esplicita dell'utente, non ancora implementata): introdurre `dwell_time_s`
  per sensore e rendere la Pd del risolutore DES dipendente dal tempo di permanenza, non solo dalla
  distanza minima — l'utente ha scelto questa opzione più impegnativa (cambia la legge del motore, non
  solo il pianificatore) motivandola esplicitamente: l'aggiramento puro allungherebbe troppo le rotte
  rispetto ai parametri di missione, e annullare missioni per l'impossibilità di evitare il rilevamento
  sarebbe eccessivo in un contesto Guerra Fredda. **Nota bene per quando si implementa**: tocca
  `Engagement_Resolver.detection_probability`, non solo `Air_Route_Manager.py`.
- **D-7 seconda parte**: reti di sensori/cueing EWR→SAM sinergiche (l'utente ha menzionato l'analogo
  DCS: script Lua runtime per network SAM interconnessi) — esplicitamente rimandata alla Fase 0 della
  gerarchia militare (`Formation`/`C2_Node`), con un dubbio dichiarato dall'utente sull'efficienza di
  comunicazione in epoca WWII lasciato a discrezione futura, non deciso ora.
- **D-8**: aggiornare la firma della Proposta B (rotte d'attacco/quota di sgancio,
  [[project_ammunition_per_weapon_stock]] è il suo prerequisito gemello sul lato dati) per accettare le
  due liste di minacce — da fare insieme all'implementazione di quella proposta, non prima.

**Manuale DES**: NON aggiornato per questo commit — il commit `59be4379` (manuale) è ancorato solo a
`1d0c1127` (Proposta A), scritto apposta per non documentare lavoro in corso instabile. Il capitolo 4
§4.16 e il capitolo 9 §9.1/§9.3 vanno riletti e aggiornati di nuovo per riflettere sia A2 (cannone) sia
questa proposta.
