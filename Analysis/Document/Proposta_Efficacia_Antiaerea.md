# Proposta: efficacia delle armi contro bersagli aerei (B1)

**Stato**: PROPOSTA, in attesa di approvazione dell'utente (2026-09-24). Nessun registro modificato.
**Tutti i valori sono stime non tarate** (ragionamento + ordini di grandezza storici); vanno
marcati come stime anche nei commenti del codice.

Convenzione: cella = `accuracy / destroy_capacity`; Pk = acc × dc (Damage_Model). Per cannoni e
CIWS "un colpo" = una raffica, come nei template terrestri esistenti.

## 0. Principi

- Scala di riferimento: riga `Aircraft` di `Aircraft_Weapon_Data.py` (accuracy scende col bersaglio
  più piccolo; dc sale col bersaglio più piccolo e con testate leggere; testate ≥ 35 kg → dc 1.0).
- La **dimensione** (big/med/small, `Context.classify_asset_dimension`) porta già l'effetto taglia;
  la **classe** aggiunge manovrabilità (accuracy) e corazzatura (dc).

Classi proposte (nuove chiavi nei template di efficacia):

| Classe | Chi | Resistenza (dc) | Accuracy |
|---|---|---|---|
| `Aircraft` | Fighter, Fighter_Bomber (chiave generica e fallback) | riferimento "Soft" | base |
| `Aircraft_Attacker` | solo attacker con corazzatura CAS vera (A-10, Su-25) | più alta del fighter (v. controllo sotto) | come fighter |
| `Aircraft_Heavy` | Bomber, Heavy_Bomber, Awacs, Transport, Recon | uguale al fighter (ramo "uguale" della regola) | +0.10/+0.15 (meno manovrabili) |
| `Helicopter` | elicotteri | alta (rotore/trasmissione fragili) | molto più alta per i cannoni |
| `Helicopter_Attack` | Mi-24, AH-64, Ka-50 (corazzati vs 12.7–23 mm) | intermedia | come Helicopter |

### Controllo della regola "Attacker ≈ Armored" (k = dc_attacker / dc_fighter)

| Arma | dc riga Armored | Esito | Scelta |
|---|---|---|---|
| Cannoni AA 20–35 mm | 0.05/0.10/0.15 | A-10 ~4.5× meno vulnerabile di un Su-27: coerente (corazza progettata vs 23 mm) | Armored |
| Cannone AA 57 mm | 0.25/0.30/0.35 | k ≈ 0.4, plausibile | Armored |
| HMG 12.7/14.5 | 0.02/0.04/0.06 | quasi immune: vero per progetto | Armored |
| Cannoni navali 76–130 | 0.40–0.78 | k ≈ 0.55–0.7, plausibile | Armored |
| SAM IR SHORAD | 0.05/0.08/0.10 | Pk vs A-10 ≈ 0.036, 8× meno del fighter: **incongruenza** (le schegge distruggono ali/motori, solo la cabina è corazzata) | intermedio, k ≈ 0.5 |
| SAM MERAD / LORAD | 0.02–0.08 | A-10 quasi immune a SA-6/S-300: **incongruenza evidente** | k ≈ 0.7 / ≈ 0.9 |
| CIWS | 0.04/0.06/0.08 | k ≈ 0.12, incoerente col cannone AA terrestre (0.22) | k ≈ 0.25 |
| Autocannoni IFV | 0.15/0.25/0.35 | k ≈ 0.55, incoerente col cannone AA di pari calibro | dc del cannone AA |

## 1. Tabelle proposte (acc / dc)

### Ground_Weapon_Data

**`_EFF_SAM_SHORAD`** (IR, 3–11 kg: Stinger, 9M31, 9M37, MIM-72)

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.55 / 0.25 | 0.45 / 0.55 | 0.35 / 0.80 |
| Aircraft_Attacker | 0.55 / 0.13 | 0.45 / 0.28 | 0.35 / 0.40 |
| Aircraft_Heavy | 0.70 / 0.25 | 0.60 / 0.55 | 0.50 / 0.80 |
| Helicopter | 0.65 / 0.45 | 0.60 / 0.70 | 0.55 / 0.85 |
| Helicopter_Attack | 0.65 / 0.25 | 0.60 / 0.40 | 0.55 / 0.50 |

Pk risultanti: F-16 0.28, Su-27 0.25, A-10 0.13, B-52 0.18, An-26 0.33, elicottero med 0.42
(MANPADS di 3ª generazione in letteratura: 0.2–0.4).

**`_EFF_SAM_MERAD`** (radar/comando, 6.5–59 kg: Osa, Tor, Roland, 9M311, Kub)

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.70 / 0.55 | 0.55 / 0.85 | 0.45 / 0.95 |
| Aircraft_Attacker | 0.70 / 0.40 | 0.55 / 0.60 | 0.45 / 0.65 |
| Aircraft_Heavy | 0.85 / 0.55 | 0.75 / 0.85 | 0.65 / 0.95 |
| Helicopter | 0.65 / 0.75 | 0.60 / 0.90 | 0.55 / 1.00 |
| Helicopter_Attack | 0.65 / 0.50 | 0.60 / 0.65 | 0.55 / 0.75 |

Pk: Su-27 0.47, F-16 0.43, A-10 0.33, Su-24M 0.64.

**`_EFF_SAM_LORAD`** (SARH, 70–133 kg: Buk, S-300)

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.80 / 0.90 | 0.55 / 1.00 | 0.45 / 1.00 |
| Aircraft_Attacker | 0.80 / 0.80 | 0.55 / 0.90 | 0.45 / 0.90 |
| Aircraft_Heavy | 0.85 / 0.90 | 0.70 / 1.00 | 0.60 / 1.00 |
| Helicopter | 0.50 / 1.00 | 0.45 / 1.00 | 0.40 / 1.00 |
| Helicopter_Attack | 0.50 / 0.90 | 0.45 / 0.95 | 0.40 / 0.95 |

Pk: B-52 0.77 (cfr. Linebacker II), F-16 0.45. Contro elicotteri bassi: clutter e quota minima.

**`_EFF_AA_CANNON`** (20–35 mm, per raffica: ZU-23, M61 VADS, 35 mm, 2A38M)

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.45 / 0.20 | 0.30 / 0.45 | 0.25 / 0.65 |
| Aircraft_Attacker | 0.45 / 0.05 | 0.30 / 0.10 | 0.25 / 0.15 |
| Aircraft_Heavy | 0.60 / 0.20 | 0.45 / 0.45 | 0.40 / 0.65 |
| Helicopter | 0.65 / 0.45 | 0.60 / 0.65 | 0.55 / 0.80 |
| Helicopter_Attack | 0.65 / 0.15 | 0.60 / 0.25 | 0.55 / 0.35 |

**`_EFF_AA_CANNON_57MM`** (S-68)

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.40 / 0.45 | 0.25 / 0.75 | 0.20 / 0.90 |
| Aircraft_Attacker | 0.40 / 0.25 | 0.25 / 0.30 | 0.20 / 0.35 |
| Aircraft_Heavy | 0.55 / 0.45 | 0.40 / 0.75 | 0.35 / 0.90 |
| Helicopter | 0.50 / 0.75 | 0.45 / 0.90 | 0.40 / 1.00 |
| Helicopter_Attack | 0.50 / 0.45 | 0.45 / 0.55 | 0.40 / 0.65 |

**`_EFF_AUTOCANNON`** (IFV 20–30 mm, senza direzione del tiro AA) — quasi inutile vs jet, realistico vs elicotteri

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.10 / 0.20 | 0.05 / 0.45 | 0.03 / 0.65 |
| Aircraft_Attacker | 0.10 / 0.05 | 0.05 / 0.10 | 0.03 / 0.15 |
| Aircraft_Heavy | 0.15 / 0.20 | 0.10 / 0.45 | 0.08 / 0.65 |
| Helicopter | 0.35 / 0.45 | 0.30 / 0.65 | 0.25 / 0.80 |
| Helicopter_Attack | 0.35 / 0.15 | 0.30 / 0.25 | 0.25 / 0.35 |

**`_EFF_HMG`** (12.7 mm; la KPVT-14.5 ha tabella inline da allineare)

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.08 / 0.05 | 0.04 / 0.10 | 0.02 / 0.20 |
| Aircraft_Attacker | 0.08 / 0.02 | 0.04 / 0.04 | 0.02 / 0.06 |
| Aircraft_Heavy | 0.12 / 0.05 | 0.08 / 0.10 | 0.06 / 0.20 |
| Helicopter | 0.30 / 0.20 | 0.25 / 0.35 | 0.20 / 0.50 |
| Helicopter_Attack | 0.30 / 0.03 | 0.25 / 0.05 | 0.20 / 0.08 |

MMG 7.62, cannoni dei carri, ATGM, artiglieria, mortai: **nessuna riga aerea** → `fire_control` = None.

### Ship_Weapon_Data

**`_EFF_SAM_SHORAD` navale** (radar, 15–39 kg: Sea Sparrow, SA-N-4, SA-N-9, HHQ-7)

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.70 / 0.60 | 0.55 / 0.90 | 0.45 / 1.00 |
| Aircraft_Attacker | 0.70 / 0.42 | 0.55 / 0.63 | 0.45 / 0.70 |
| Aircraft_Heavy | 0.80 / 0.60 | 0.70 / 0.90 | 0.60 / 1.00 |
| Helicopter | 0.60 / 0.80 | 0.55 / 0.95 | 0.50 / 1.00 |
| Helicopter_Attack | 0.60 / 0.55 | 0.55 / 0.70 | 0.50 / 0.80 |

**`_EFF_SAM_MERAD` navale** (ESSM, SM-1, HHQ-16)

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.75 / 0.80 | 0.60 / 1.00 | 0.50 / 1.00 |
| Aircraft_Attacker | 0.75 / 0.68 | 0.60 / 0.85 | 0.50 / 0.85 |
| Aircraft_Heavy | 0.85 / 0.80 | 0.75 / 1.00 | 0.65 / 1.00 |
| Helicopter | 0.55 / 0.95 | 0.50 / 1.00 | 0.45 / 1.00 |
| Helicopter_Attack | 0.55 / 0.80 | 0.50 / 0.90 | 0.45 / 0.90 |

**`_EFF_SAM_LORAD` navale** (SM-2, SM-2ER, S-300F, HHQ-9): come il LORAD terrestre, dc big 0.95

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.80 / 0.95 | 0.55 / 1.00 | 0.45 / 1.00 |
| Aircraft_Attacker | 0.80 / 0.85 | 0.55 / 0.90 | 0.45 / 0.90 |
| Aircraft_Heavy | 0.85 / 0.95 | 0.70 / 1.00 | 0.60 / 1.00 |
| Helicopter | 0.50 / 1.00 | 0.45 / 1.00 | 0.40 / 1.00 |
| Helicopter_Attack | 0.50 / 0.90 | 0.45 / 0.95 | 0.40 / 0.95 |

**`_EFF_CIWS`** (Phalanx, AK-630, Type-730, per raffica)

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.65 / 0.25 | 0.50 / 0.50 | 0.45 / 0.70 |
| Aircraft_Attacker | 0.65 / 0.06 | 0.50 / 0.13 | 0.45 / 0.18 |
| Aircraft_Heavy | 0.75 / 0.25 | 0.65 / 0.50 | 0.60 / 0.70 |
| Helicopter | 0.70 / 0.50 | 0.65 / 0.70 | 0.60 / 0.85 |
| Helicopter_Attack | 0.70 / 0.15 | 0.65 / 0.25 | 0.60 / 0.35 |

**`_EFF_NAVAL_GUN_76MM`** (OTO 76/62, AK-176, spoletta di prossimità)

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.35 / 0.75 | 0.25 / 0.90 | 0.20 / 1.00 |
| Aircraft_Attacker | 0.35 / 0.40 | 0.25 / 0.52 | 0.20 / 0.65 |
| Aircraft_Heavy | 0.45 / 0.75 | 0.35 / 0.90 | 0.30 / 1.00 |
| Helicopter | 0.40 / 0.95 | 0.35 / 1.00 | 0.30 / 1.00 |
| Helicopter_Attack | 0.40 / 0.60 | 0.35 / 0.70 | 0.30 / 0.80 |

**`_EFF_NAVAL_GUN_100MM / 127MM / 130MM`** (stessa accuracy; terna Attacker = 100/127/130 mm)

| Classe | big | med | small |
|---|---|---|---|
| Aircraft | 0.25 / 0.85 | 0.15 / 0.95 | 0.10 / 1.00 |
| Aircraft_Attacker | 0.25 / (0.45, 0.50, 0.52) | 0.15 / (0.58, 0.62, 0.65) | 0.10 / (0.72, 0.75, 0.78) |
| Aircraft_Heavy | 0.35 / 0.85 | 0.25 / 0.95 | 0.20 / 1.00 |
| Helicopter | 0.30 / 1.00 | 0.25 / 1.00 | 0.20 / 1.00 |
| Helicopter_Attack | 0.30 / 0.70 | 0.25 / 0.80 | 0.20 / 0.85 |

## 2. Regole di mappatura

- La resistenza è della cellula, non del ruolo di missione: classe derivata dalla `category` del
  **modello** (`Aircraft_Data._registry[model].category`, lista), in mancanza da
  `asset.asset_type`, ultimo fallback `Aircraft`.
- Attacker nel registro: A-10A, A-10C, A-10C II, Su-25, Su-25T, Su-25TM, A-4E, A-20G. F-16, F-15E,
  F/A-18, Su-30, Su-33, MiG-23MLD, F-4E, Su-17M4, MiG-27K, Su-34, Viggen: NON attacker (corretto).
- Proposta: flag opzionale `ground_fire_armored: True` in `Aircraft_Data` (solo A-10 e Su-25);
  classe `Aircraft_Attacker` = ATTACKER **e** flag. A-4E e A-20G (senza corazza CAS) → `Aircraft`.
  Lo stesso flag su un futuro HELICOPTER → `Helicopter_Attack`.
- Categorie multiple: vince la più resistente (Attacker > Aircraft > Heavy; Helicopter_Attack >
  Helicopter). Oggi l'unico caso è [FIGHTER, FIGHTER_BOMBER] → `Aircraft`.
- Il registro non contiene elicotteri: le righe Helicopter servono per il futuro.

## 3. Impatto sul codice

- **Context non si tocca negli enum/mappe esistenti** (`TARGET_CLASSIFICATION`,
  `WEAPON_TARGET_CLASS_MAP`, ecc.): `Tactical_Analysis` e `Air_Resources_Assigner` richiedono
  l'unica chiave `'Aircraft'`. Si aggiunge solo una funzione pura
  `get_air_target_class(categories, armored=False) -> str` + costanti dei nomi.
- Nei template la chiave `'Aircraft'` = riga fighter → gli scorer di pianificazione ottengono un
  valore > 0 per SAM vs aerei (oggi 0).
- `fire_control`: `eff.get(sottoclasse) or eff.get('Aircraft')`; nessuna riga → None.
- `AMMO_TARGET_EFFECTIVENESS`: nessuna modifica (è codice morto: il suo unico uso è commentato).

## 4. Rischi e anomalie trovate (fuori scope)

1. **Nessun inviluppo quota** nei registri terrestri tranne `min/max_altitude` sulle armi AA:
   senza un filtro di quota in `fire_control` uno Stinger potrebbe ingaggiare un B-52 a 10 km.
2. Stealth, ECM e contromisure non entrano nell'accuracy (la stealth va nel rilevamento).
3. Le tabelle aria-aria non hanno sottoclassi (A-10 colpito da AIM-9 usa la riga fighter).
4. Anomalie nei dati: URK-5-Rastrub (ASW) fra i SAM navali MERAD; `9M331` (Tor) e `9M37M`
   (Strela-10) fra gli ATGM laser; MERAD terrestre con missili di classe SHORAD radar (Roland,
   9M311); tabelle inline per KPVT-14.5, 2A46M, Rheinmetall-120mm-L55, CN120-26, 9M119M.
