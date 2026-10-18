---
name: project-map-module-plan
description: "Modulo di gestione mappe (futuro): base per volumi di rilevamento/minaccia con morfologia del terreno e per il calcolo rotte; fonte Analysis/Document/Documentazione e Guida Mappe DCS World.docx; da fare DOPO la definizione dei dettagli del calcolo rotte; 2026-10-18: perimetro esteso a servizio comune (DES, adapter simulatori, logica tattica/strategica, pianificatore missioni)"
metadata:
  node_type: memory
  type: project
  originSessionId: c96aae50-d207-4afc-a001-15c7352ab468
  modified: 2026-09-29T13:06:24.372Z
---

Dichiarato dall'utente il 2026-09-29. Il documento `Analysis/Document/Documentazione e Guida Mappe DCS World.docx`
(fornito dall'utente, tracciato in git dal 2026-09-29, commit 4dbf9479) contiene le informazioni per realizzare un
**modulo di gestione delle mappe**. Il modulo darà le funzionalità di base per due moduli successivi:
1. volumi **effettivi** di rilevamento e/o minaccia che tengano conto della **morfologia del terreno**
   (oggi i volumi sono geometrici: cilindri + orizzonte radar, v. [[project-detection-interception-volumes]]);
2. il **calcolo delle rotte**.

**Why:** i volumi puramente geometrici ignorano il mascheramento del terreno, che decide rilevamento e
minaccia reali.

**How to apply:** NON iniziare il modulo mappe prima che siano definiti con l'utente i dettagli del
calcolo delle rotte: l'ordine è 1) dettagli rotte, 2) modulo mappe, 3) volumi con terreno e rotte.
Il documento .docx non è ancora stato letto (l'utente ha chiesto di leggerlo solo quando si arriverà
a quel lavoro).

## Perimetro esteso (utente, 2026-10-18)
Sara' un lavoro dedicato: un modulo che gestisce informazioni **orografiche, topografiche e altro** delle mappe
come servizio COMUNE a tutto il sistema, non solo al DES: DES, adapter/API verso DCS e altri simulatori (vincolo
[[feedback-core-simulator-agnostic]]: interfaccia indifferente al simulatore, i formati DCS dietro un adapter),
logica tattica e strategica, pianificatore delle missioni e delle rotte.
Stato del DES verificato il 2026-10-18 (motivo della richiesta): portata, rilevamento e limiti di quota usano gia'
la distanza 3D su `position.z`, ma non esistono modello del terreno, quota del suolo in (x,y), aggiornamento della z
lungo il movimento ne' linea di vista; nelle fixture degli scenari z = 0 di default (`Test/Scenario_Fixtures.py`).
