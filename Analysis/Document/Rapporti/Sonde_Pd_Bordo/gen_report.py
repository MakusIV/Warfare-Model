"""Genera le sezioni 1-5 del rapporto R1 (Proposta_Pd_Bordo_Portata.md, PB-4) da report.json della sonda.

uso (dalla root del repo): python3 gen_report.py <report.json> > sezioni_1_5.md
Sola lettura: nessun file del repository modificato.
"""
import json
import sys
from collections import Counter

report = json.load(open(sys.argv[1], encoding='utf-8'))
fam, counts, det = report['family'], report['family_counts'], report['detections']
outcome_by_family = Counter(key.split('/')[0] for key in report['outcome_changed'])

print('## 1. Esecuzioni cambiate per famiglia di scenari\n')
print(f"Interruttore `PD_EDGE_RECALIBRATION` acceso in memoria, Pd al bordo {report['edge_now']} (prima "
      f"{report['edge_before']}). Riferimento: fotografia da 1219. Esecuzioni: {report['runs']}; **cambiate "
      f"{report['changed']}**, invariate {report['unchanged']}, nuove {len(report['new'])}, mancanti "
      f"{len(report['missing'])}, errori {len(report['errors'])}.\n")
print('Voci del riassunto che cambiano (numero di esecuzioni): ' +
      ', '.join(f'`{k}` {v}' for k, v in sorted(report['keys_changed'].items(), key=lambda kv: -kv[1])) + '.\n')
print('| Famiglia | Cambiate / totali | Esito di forza cambiato | Salve prima -> dopo | Distruzioni prima -> dopo |')
print('|---|---|---|---|---|')
for family in sorted(fam):
    changed, total = fam[family]
    row = counts.get(family, {})
    print(f"| {family} | {changed} / {total} | {outcome_by_family.get(family, 0)} | "
          f"{row.get('salvos_before', 0)} -> {row.get('salvos_after', 0)} | "
          f"{row.get('destroyed_events_before', 0)} -> {row.get('destroyed_events_after', 0)} |")

tot = Counter()
for row in counts.values():
    tot.update(row)
print(f"| **Totale** | **{report['changed']} / {report['runs']}** | **{len(report['outcome_changed'])}** | "
      f"**{tot['salvos_before']} -> {tot['salvos_after']}** | "
      f"**{tot['destroyed_events_before']} -> {tot['destroyed_events_after']}** |\n")
print('Salve e distruzioni sono sommate sulle sole esecuzioni cambiate (le invariate hanno gli stessi valori).\n')

print('## 2. Esecuzioni con esito di forza cambiato\n')
print(f"{len(report['outcome_changed'])} esecuzioni (`force_outcomes` diverso dalla fotografia):\n")
for key in sorted(report['outcome_changed']):
    print(f'- `{key}`')
print()

print('## 3. Rilevamenti a parita\' di estrazione (spia sulle `Detection`)\n')
print(f"Estrazioni di rilevamento: {det['draws']} (fuori portata {det['out_of_range']}, in portata "
      f"{det['in_range']}). Rilevati ora {det['detected_now']}; con la soglia vecchia e la STESSA estrazione "
      f"sarebbero stati {det['detected_with_old_edge_same_draw']}. **Persi {det['lost']}** "
      f"({100 * det['lost'] / det['in_range']:.1f} % delle estrazioni in portata), **guadagnati {det['gained']}**. "
      "E' l'effetto di primo ordine: a cascata cambiano anche gli ingaggi e le estrazioni successive.\n")
print('| Fascia di distanza (d/R) | Estrazioni in portata | Rilevamenti persi |')
print('|---|---|---|')
for band in range(10):
    print(f"| {band / 10:.1f}-{(band + 1) / 10:.1f} | {det.get(f'band_{band}_in_range', 0)} | "
          f"{det.get(f'band_{band}_lost', 0)} |")
print()

print('## 4. Unita\' S36: `Detection` prima / dopo\n')
rows = report['s36_rows']
by_unit = {}
for row in rows:
    by_unit.setdefault(row[0].split('/')[0], []).append(row)
print('| Unita\' | `Detection` | Pd cambiata | Rilevato prima | Rilevato dopo | Rilevamenti persi | Guadagnati |')
print('|---|---|---|---|---|---|---|')
for unit, unit_rows in sorted(by_unit.items()):
    pd_changed = sum(1 for r in unit_rows if abs(r[5] - r[6]) > 1e-9)
    before, after = sum(1 for r in unit_rows if r[8]), sum(1 for r in unit_rows if r[9])
    lost = sum(1 for r in unit_rows if r[8] and not r[9])
    gained = sum(1 for r in unit_rows if r[9] and not r[8])
    print(f'| {unit} | {len(unit_rows)} | {pd_changed} | {before} | {after} | {lost} | {gained} |')
print()
print('Righe con esito di rilevamento o istante diversi (le altre hanno solo la Pd cambiata). Colonne: portata [m], '
      'CPA [m], Pd prima -> dopo, estrazione, rilevato prima -> dopo, istante prima -> dopo [s].\n')
print('| Esecuzione | Osservatore -> bersaglio | R | CPA | Pd | Estr. | Rilevato | Istante |')
print('|---|---|---|---|---|---|---|---|')
for row in rows:
    if row[8] == row[9] and row[10] == row[11]:
        continue
    key, obs, tgt, rng, cpa, pd0, pd1, draw, d0, d1, t0, t1 = row
    fmt = lambda v: '-' if v is None else f'{v:.1f}'
    print(f'| `{key}` | {obs} -> {tgt} | {rng:.0f} | {cpa:.0f} | {pd0:.4f} -> {pd1:.4f} | {draw:.4f} | '
          f'{d0} -> {d1} | {fmt(t0)} -> {fmt(t1)} |')
print()
