---
name: Ship_Weapon_Data scoring fixes
description: Correzioni ai template di efficienza in Ship_Weapon_Data.py — principio destroy_capacity e ordinamento punteggi
type: project
---

Corretti i template di efficienza in `Asset/Ship_Weapon_Data.py` per rispettare il principio:

**Ordine atteso:** Soft > Armored > ship > Structure > Hard

**Why:** La formula score = accuracy × destroy_capacity confondeva due concetti:
- `accuracy` = specializzazione dell'arma (alta per il target per cui è progettata)
- `destroy_capacity` = fragilità del bersaglio SE colpito (Soft fragile → dc alta; nave compartimentata → dc moderata; carro colpito da testata grande → dc alta)

**How to apply:** Quando si aggiungono nuove armi o si modificano template di efficienza, verificare sempre che il prodotto acc×dc rispetti l'ordine Soft > Armored > ship. Non impostare destroy_capacity in base alla "destinazione d'uso" dell'arma ma in base alla resistenza del bersaglio.

## Template corretti

### ASM anti-nave (3 template)
- `_EFF_ASM_ANTISHIP_SUBSONIC` (Harpoon/YJ-83, 220 kg): Soft.dc 0.78-0.88, Armored.dc 0.72-0.84, ship.dc 0.30-0.52
- `_EFF_ASM_SUPERSONIC` (Moskit/YJ-12, 320 kg): Soft.dc 0.82-0.90, Armored.dc 0.78-0.90, ship.dc 0.32-0.55
- `_EFF_ASM_SUPERSONIC_HEAVY` (P-700/P-1000, 750 kg): Soft.dc 0.88-0.92, Armored.dc 0.90-0.98, ship.dc 0.42-0.72
- `_EFF_ASM_CRUISE_LANDATTACK` (Tomahawk): già corretto (land-attack → Soft > Structure > ship)

### GUNS (4 template) — solo Armored.dc modificata
- `_EFF_NAVAL_GUN_76MM`: Armored.dc 0.06-0.10 → 0.40-0.65
- `_EFF_NAVAL_GUN_100MM`: Armored.dc 0.08-0.13 → 0.45-0.72
- `_EFF_NAVAL_GUN_127MM`: Armored.dc 0.10-0.16 → 0.50-0.75
- `_EFF_NAVAL_GUN_130MM`: Armored.dc 0.12-0.18 → 0.52-0.78

### CIWS
- `_EFF_CIWS`: Armored.dc 0.01 → 0.04-0.08 (20-30mm danneggia APCs/ottiche ma non carri pesanti)

## Test aggiornati in Test_Ship_Weapon_Data.py
- `test_asm_vs_ship_higher_than_vs_armored` → `test_asm_vs_armored_higher_than_vs_ship`
- `test_asm_ship_score_higher_than_armored` → `test_asm_armored_score_higher_than_ship`
- `test_higher_ship_weight_gives_higher_score_for_asm` → `test_higher_soft_weight_gives_higher_score_for_asm`

## Run tests
`python -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Ship_Weapon_Data.py"`
(il flag --tests-only NON è implementato in questo file — usare unittest discover o pytest)
