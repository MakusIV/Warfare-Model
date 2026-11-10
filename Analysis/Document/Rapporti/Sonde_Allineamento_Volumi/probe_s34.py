"""Sonda di geometria di S34-BAND (sola lettura, prima del test 1 del blocco 2 VA).

Verifica la regola di fermata di §4.2.1 della Proposta_Allineamento_Volumi_DES_Pianificatore.md:
1. `climb_off`: salve dell'Osa in almeno 3 semi su 4 (spento, il filtro statico lascia sparare a 6000 m);
2. `descend_on`: NESSUN rilevamento dell'Osa mentre l'A-10C e' sopra i 5000 m relativi;
3. `late_descend_on`: almeno un rinvio (decisione dell'Osa con l'A-10C sopra i 5000 m) in almeno 3 semi su 4.

Non consuma l'RNG oltre le esecuzioni degli scenari (nessuna estrazione in piu': sono le stesse
esecuzioni dei test). Non modifica alcun file.
"""
from Code.Dynamic_War_Manager.Source.Context import Reaction_Profile as RP
from Code.Dynamic_War_Manager.Source.Test import Test_Session_Scenarios_S34 as S34

OSA_REACTION_TOTAL_S = RP.REACTION_PROFILES['9A33-Osa'].total


def report_climb_off():
    print('== climb_off (atteso: salve dell\'Osa sopra i 5000 m in >= 3 semi) ==')
    seeds_with_salvos = 0
    for seed in S34.SEEDS:
        outcome, results, routes = S34.run_variant(seed, 'climb_off')
        osa_salvos = S34._salvos(results, S34.OSA)
        altitudes = [S34._relative_altitude(routes, s.target_id, s.t_launch) for s in osa_salvos]
        seeds_with_salvos += 1 if osa_salvos else 0
        print(f'  {seed}: salve={len(osa_salvos)} altitudini_rel={altitudes}')
    print(f'  semi con salve: {seeds_with_salvos}/4')


def report_descend_on():
    print('== descend_on (atteso: NESSUN rilevamento dell\'Osa sopra i 5000 m) ==')
    detections_above = 0
    for seed in S34.SEEDS:
        outcome, results, routes = S34.run_variant(seed, 'descend_on')
        detections = [d for d in S34._detections(results, S34.OSA) if d.detected and d.time is not None]
        above = []
        for d in detections:
            alt = S34._relative_altitude(routes, d.target_id, d.time)
            if alt is not None and alt > S34.BAND_MAX_M:
                above.append((d.target_id, round(d.time, 2), round(alt, 1)))
        detections_above += 1 if above else 0
        print(f'  {seed}: rilevamenti={len(detections)} sopra_5000={above}')
    print(f'  semi con rilevamento sopra 5000 m: {detections_above}/4')


def report_late_descend_on():
    print('== late_descend_on (atteso: almeno un rinvio per >= 3 semi) ==')
    seeds_with_deferral = 0
    for seed in S34.SEEDS:
        outcome, results, routes = S34.run_variant(seed, 'late_descend_on')
        detections = [d for d in S34._detections(results, S34.OSA) if d.detected and d.time is not None]
        osa_salvos = S34._salvos(results, S34.OSA)
        # Una "decisione" (t_ready = rilevamento + reazione) cade sopra i 5000 m -> rinvio VA-2.1.
        decisions = []
        for d in detections:
            t_ready = d.time + OSA_REACTION_TOTAL_S
            alt = S34._relative_altitude(routes, d.target_id, t_ready)
            if alt is not None:
                decisions.append((d.target_id, round(d.time, 2), round(t_ready, 2), round(alt, 1)))
        above = [x for x in decisions if x[3] > S34.BAND_MAX_M]
        seeds_with_deferral += 1 if above else 0
        print(f'  {seed}: decisioni={decisions} sopra_5000={above} salve={len(osa_salvos)}')
    print(f'  semi con almeno una decisione sopra 5000 m: {seeds_with_deferral}/4')


if __name__ == '__main__':
    report_climb_off()
    report_descend_on()
    report_late_descend_on()
