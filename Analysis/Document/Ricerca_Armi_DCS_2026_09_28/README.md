# Armi DCS mancanti — ricerca del 2026-09-28

Fonte dell'elenco: `../bombe_missili_russi.pdf` (schermate del menu armi dell'editor DCS).
Confronto con `AIR_WEAPONS` fatto a mano sul registro reale. Ricerca fatta da tre agenti Haiku, uno per
gruppo (`Ricerca_AAM.md`, `Ricerca_ASM.md`, `Ricerca_Bombe.md`), con fonte e confidenza per campo
(A primaria o due fonti concordi, M una fonte secondaria, B stima o analogia). `cost` ed `efficiency`
sono sempre stime B per analogia con voci già nel registro.

## Inserite in `Asset/Aircraft_Weapon_Data.py`
- **MISSILES_AAM (4)**: PL-12, PL-5EII, PL-8A, PL-8B.
- **MISSILES_ASM (12)**: Kh-29TE, Kh-31A, Kh-31P, Kh-35, Kh-41, Kh-65, Kh-555, Kh-59M, LD-10, KD-63,
  KD-63B, KD-20.
- **BOMBS (23)**: KAB-500Kr-OD, KAB-500S, KAB-1500Kr, KAB-1500LG-Pr, KAB-1500LG-Pr-E, LS-6, LS-6-100,
  LS-6-250, OFAB-100-120, OFAB-100-120 TU, OFAB-100-110TU, OFAB-250-270, ODAB-500PM, Mk-84 AIR GP HD,
  Mk-84 AIR TP HD, e 8 varianti RBK come voci separate (decisione utente 2026-09-28).
- Per ogni ASM e bomba, la riga di `_WEAPON_PARAM_TYPE`.

## Correzioni della revisione (NON presenti nei rapporti degli agenti)
- **Kh-22**: non inserito, è l'arma già registrata come `Kh-22N`. **Kh-58U**: non inserito, i dati
  di `Kh-58` (250 km) sono già quelli del Kh-58U.
- **Kh-41**: testata 320 kg (P-270 Moskit), non 150.
- **KD-20** (CJ-10 aviolanciato, H-6K): l'agente non l'ha trovato. Voce ricavata da KD-63 con
  range 1500 km, 240 m/s, testata 500 kg, servizio 2015, cost come Kh-55: **tutto B/M, da verificare**.
- **Bombe guidate e non guidate**: le classi di `efficiency` mancanti (Hard, ship, Airbase, Port,
  Shipyard, Farp, Stronghold, secondo il caso) sono copiate dalla voce modello (KAB-500L, FAB-100,
  FAB-250M54, FAB-500M62, Mk-84); il commento sopra ogni voce le elenca. Stima B.
- **LS-6, LS-6-100, LS-6-250**: bomba **planante** (famiglia Leishi-6), non a caduta libera. `release`
  riscritto nella forma "dispenser planante" di BK-90: solo level, 1000-12000 m, `standoff_range_km`
  (10, 60). Stima B.
- **Mk-84 AIR GP HD / TP HD**: coda BSU-50 AIR, quindi `drag: 'selectable'` come Mk-82AIR:
  finestra low_drag = quella della Mk-84, high_drag = quella proposta dall'agente.

## Escluse
P-500, P-700, RGM-84D (navali), IRIS-T-SL (terrestre), KG600 (pod), P-50T e IAB-500 (esercitazione
e imitazione), LTF 5b (siluro: il registro non ha una categoria), submunizioni PTAB-* (contenuto dei
dispenser), PK-3 (non identificato con certezza).
