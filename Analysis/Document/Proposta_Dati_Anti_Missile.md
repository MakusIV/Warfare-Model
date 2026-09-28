# Proposta dati: capacità `Anti_Missile` delle armi di difesa aerea (A6, passo 1)

**Stato**: APPROVATA e IMPLEMENTATA il 2026-09-28 (D-AM1, D-AM2, D-AM3 come raccomandato), insieme
al passo 2 del §7.6 della proposta SAM (D + F). Esiti cambiati, v. §6.
**Contesto**: `Proposta_Regole_Allocazione_SAM.md` §7 (D + F + L, approvata). La regola D dice che un
asset intercetta un'arma autonoma solo con un'arma **dichiarata capace** (task `Anti_Missile`,
decisione Q6: un solo task per missili, bombe plananti e droni). Questo documento propone a quali armi
assegnarlo.

Confidenza: **A** = fonte primaria o due fonti concordi; **M** = una fonte secondaria; **B** = stima o
analogia.

## 1. Armi terrestri (`Ground_Weapon_Data`, 16 armi `Anti_Air`)

Oggi nessuna arma terrestre ha il task (`Context.GROUND_WEAPON_TASK` non lo contiene).

| Arma | Sistema (veicolo nel registro) | Proposta | Conf. | Motivo |
|---|---|---|---|---|
| 9M331-SAM | Tor-M1 (`9K331-Tor`) | **Sì** | A | Progettato contro aerei, elicotteri **e munizioni guidate**: missili da crociera, bombe guidate e plananti, bersagli piccoli e manovranti, da 10 m a 6 km di quota [T1][T2] |
| 9M38-SAM | Buk-M1 (`9K37-Buk`) | **Sì** | M | Ingaggia missili da crociera e antinave: Pk su singolo colpo contro ALCM ≥ 0,4, fra 3,5 e 6-10 km [B1][B2] |
| 5V55R-SAM | S-300PS (`S-300PS`) | **Sì** | M | Progettato per aerei a bassa quota, "capace anche contro missili balistici e da crociera" [S1] |
| 9M311-SAM | Tunguska (`2K22-Tunguska`) | **Sì** | M | Il 9M311-M1 (Tunguska-M1) ha la spoletta radio per bersagli piccoli come i missili da crociera [U1]. Il registro non distingue M e M1: si assume M1 |
| 2A38M-30mm | Tunguska (`2K22-Tunguska`) | **Sì** | B | Cannone dello stesso sistema, con la stessa direzione del tiro radar |
| Oerlikon-KDA-35mm | Gepard (`Flakpanzer-Gepard`) | **Sì** | M | Abbattimenti documentati in Ucraina di missili da crociera (Kalibr) e di droni Shahed [G1][G2] |
| 9M33-SAM | Osa (`9A33-Osa`) | **Da decidere** (proposta: No) | M | L'Osa-AKM è dichiarato capace contro "missili da crociera e droni" fino a 500 m/s [O1]. Contro un ASM piccolo e veloce (Maverick, Kh-29) non ci sono fonti. Vedi §4, D-AM1 |
| 3M9-SAM | Kub (`2K12-Kub`) | No | B | Sistema anni '60-'70 contro aerei. Nessuna fonte di capacità antimissile |
| 9M37-SAM | Strela-10 (`9K35-Strela-10`) | No | M | IR a corto raggio contro aerei ed elicotteri. È il caso che ha aperto la questione (§1 della proposta SAM) |
| 9M31-SAM | Strela-1 (`Strela-1-9P31`) | No | M | IR di prima generazione |
| FIM-92-Stinger | M6 Linebacker (`M6-Linebacker`) | **Da decidere** (proposta: No) | B | MANPADS IR. Ci sono dichiarazioni recenti contro UAS; contro gli ASM nessuna. Stessa classe dello Strela-10. Vedi D-AM1 |
| MIM-72-SAM | Chaparral (`MIM-72G-Chaparral`) | No | B | IR derivato dall'AIM-9, contro aerei |
| Roland-SAM | Roland (`MIM-115-Roland`) | No | B | Progettato contro aerei ed elicotteri a bassa quota |
| AZP-23-23mm | Shilka (`ZSU-23-4-Shilka`) | No | B | Portata 2,5 km. Nessuna fonte di impiego contro missili |
| S-68-57mm | ZSU-57-2 (`ZSU-57-2`) | No | B | Senza radar di tiro, puntamento ottico |
| M61-Vulcan-20mm | VADS (`M163-VADS`) | No | B | Portata 1,2 km, radar di sola misura della distanza |

Risultato: **6 armi Sì** (Tor, Buk, S-300PS, Tunguska missile e cannone, Gepard), **8 No**, **2 da
decidere** (Osa, Stinger).

Effetto: smettono di intercettare ZSU-57-2, Shilka, VADS, Strela-1, Chaparral, Strela-10, Roland e Kub.
Osa e Linebacker dipendono da D-AM1. Continuano Tor, Buk, S-300PS, Tunguska e Gepard.

## 2. Armi navali (`Ship_Weapon_Data`)

Le 12 armi con il task già assegnato (ESSM, Sea Sparrow, SM-2, SM-2ER, SA-N-9, S-300F, HHQ-7/9/16,
Phalanx, AK-630, Type-730) si confermano.

| Arma | Proposta | Conf. | Motivo |
|---|---|---|---|
| RIM-66-SM-1 (FFG-46) | No, invariato | B | SM-1MR contro aerei; l'antimissile della Perry è il Phalanx |
| SA-N-4-Gecko (Rezky, Grisha, Molniya) | No, invariato | M | Versione navale dell'Osa: si allinea a D-AM1 |
| URK-5-Rastrub | No, invariato | A | Arma antisommergibile/antinave, il task Anti_Air è da verificare a parte |
| Cannoni navali (Mk-45, OTO 76, AK-100/130/176, Type-79A) | No, invariato | B | Il tiro antimissile con cannone di medio calibro esiste (OTO 76 con munizioni DART/Strales), ma non con le munizioni modellate qui |

### 2.1 Difetto scoperto: i CIWS oggi non intercettano

Verificato nel codice (`Asset/Mobile.py:188-190`, `interceptor_weapons_from_registry`):
- per le navi sono intercettori solo i tipi `INTERCEPTOR_WEAPON_TYPES_SHIP = ('MISSILES_SAM',)`, quindi
  il tipo `CIWS` è **escluso**;
- in più il filtro richiede `min_altitude`/`max_altitude`, che per Phalanx, AK-630 e Type-730 sono
  `None`;
- inoltre, nella scorta per arma delle navi i CIWS sono contati **a unità** ("Phalanx ×1"), non a colpi.

Conseguenza: le armi antimissile per eccellenza della flotta non intercettano. Con la regola D le navi
con solo SM-1 o SA-N-4 (FFG-46, Grisha, Molniya, Rezky) perderebbero **ogni** capacità d'intercettazione,
pur avendo un Phalanx o un AK-630 a bordo.

Proposta (**D-AM2**):
- aggiungere `'CIWS'` a `INTERCEPTOR_WEAPON_TYPES_SHIP` e a `INTERCEPTOR_GUN_WEAPON_TYPES`: sono
  cannoni e consumano `ROUNDS_PER_GUN_INTERCEPT` colpi per intercettazione;
- dati di quota (m, relativi al tiratore, come le armi terrestri): Phalanx 0-1500, AK-630 0-3000,
  Type-730 0-3000 (B, dalla portata del registro: 1,5 / 4 / 3 km, limite "la traiettoria non sale
  oltre la portata" già usato dalla fire control);
- colpi a bordo, perché il CIWS entri nella scorta per arma: Phalanx 1550 (A), AK-630 2000 per
  impianto (M), Type-730 1280 circa (M). Senza questo dato il CIWS non avrebbe vincolo di scorta
  (None), che è la politica corrente per i dati mancanti ma darebbe intercettazioni illimitate.

Effetto collaterale da tenere presente: con i dati di quota i CIWS entrano anche in
`air_defense_volume` e nei cilindri `ThreatAA` delle navi (portata 1,5-4 km). Per navi che hanno già
SAM a lungo raggio l'effetto sul pianificatore delle rotte è trascurabile.

## 3. Modifiche al codice (passo 2 del §7.6, dopo l'approvazione)

- `Context.GROUND_WEAPON_TASK`: aggiungere `'Anti_Missile'`.
- `Ground_Weapon_Data`: task sulle armi del §1.
- `Ship_Weapon_Data` e `Mobile.py`: CIWS come da D-AM2.
- `Mobile.interceptor_weapons_from_registry`: filtro `Anti_Missile`.
- `Military.salvo_interceptors`: selezione degli asset con almeno un'arma intercettrice, e ordine F.
- `Fire_Control.AIR_ONLY_TASKS` contiene già `'Anti_Missile'`: un'arma con i soli task Anti_Air e
  Anti_Missile continua a non sparare a superficie.

## 4. Decisioni richieste

- **D-AM1 — Osa e Stinger.** Proposta: **No** per entrambi. Le fonti parlano di missili da crociera
  (grandi e lenti) e di droni, non degli ASM tattici su cui si gioca il caso tipico. Con un solo task
  (Q6), un "Sì" li renderebbe intercettori anche dei Maverick. Alternativa: Sì per l'Osa (M), No per
  lo Stinger.
- **D-AM2 — CIWS navali** come intercettori, con quote e colpi a bordo come da §2.1? (Raccomandato.)
- **D-AM3 — Tunguska = M1.** Il registro ha un solo 9M311: lo si tratta come la versione M1
  (raccomandato), o come l'originale, senza capacità antimissile?

Verifica suggerita in DCS: quali unità l'IA fa effettivamente sparare contro missili in arrivo (Tor,
Buk, S-300, Tunguska, Gepard, Osa). Per la compatibilità con le sessioni DCS conviene che il modello
non si discosti dal comportamento del simulatore.

## 5. Fonti

- [T1] Missile Threat (CSIS), *Tor (SA-15 Gauntlet)*: https://missilethreat.csis.org/defsys/tor/
- [T2] Wikipedia, *Tor missile system*: https://en.wikipedia.org/wiki/Tor_missile_system ; Missilery.info,
  *9K331 Tor-M1*: https://en.missilery.info/missile/torm
- [B1] Missilery.info, *9K37 Buk-M1*: https://en.missilery.info/missile/bukm1
- [B2] Military Wiki, *Buk missile system*: https://military-history.fandom.com/wiki/Buk_missile_system
- [S1] Missile Threat (CSIS), *S-300*: https://missilethreat.csis.org/defsys/s-300/ ; Wikipedia,
  *S-300 missile system*: https://en.wikipedia.org/wiki/S-300_missile_system
- [U1] Wikipedia, *2K22 Tunguska*: https://en.wikipedia.org/wiki/2K22_Tunguska
- [G1] Militarnyi, *Gepard SPAAG shoots down Russian cruise missile*:
  https://militarnyi.com/en/news/gepard-spaag-shoots-down-russian-cruise-missile/
- [G2] Defense Express, *How Gepard SPAAG takes down Shahed drones*:
  https://en.defence-ua.com/news/how_gepard_spaag_takes_down_shahed_drones_and_why_its_so_effective_in_doing_so_ukrainian_operators_explain-8093.html
- [O1] Army Technology, *9K33 Osa*: https://www.army-technology.com/projects/9k33-osa-air-defence-missile-system-russia/ ;
  Missilery.info, *9K33M3 Osa-AKM*: https://en.missilery.info/missile/osa-akm
- I "No" a confidenza B e i dati dei CIWS (colpi a bordo) non sono stati verificati online in questa
  sessione: sono conoscenza generale da confermare.

## 6. Implementazione (2026-09-28)

- Dati: `Context.GROUND_WEAPON_TASK['Anti_Missile']`; task sulle 6 armi del §1; CIWS con
  `min_altitude`/`max_altitude`/`rounds_per_mount`.
- `Asset/Mobile.py`: `INTERCEPTOR_TASK`, CIWS in `INTERCEPTOR_WEAPON_TYPES_SHIP` e
  `INTERCEPTOR_GUN_WEAPON_TYPES`, scorta CIWS = impianti x `rounds_per_mount`
  (`_mount_rounds`), filtro D in `interceptor_weapons_from_registry`, nuovo
  `interceptor_capability()` (True / False / None = dato mancante).
- `Block/Military.salvo_interceptors`: esclude gli asset con capacità False; None ricade sulla
  ThreatAA (stub, modelli ignoti). Ordine F: `Weapon_Stores.interceptor_rank` (soli cannoni prima),
  poi id; lo stesso ordine in `Engagement_Resolver._interceptors_of`.
- Esiti dei test cambiati, attesi:
  - S13: il FARP (Shilka + Strela-10) non ha più intercettori;
  - S11: difesa sostituita con Gepard + Tor, perché le verifiche sulle scorte d'intercettazione
    avessero casi (con Shilka + Strela si sarebbero saltate in silenzio);
  - S1 con CAS: i Maverick non vengono più intercettati, Red-Line perde 2-3 mezzi su 6 da fuori
    portata e si disingaggia prima dello scontro coi blindati, quindi Blue non subisce danni.
    È l'effetto della regola D sommato al difetto noto del disingaggio alla prima perdita per
    forze piccole (§5.3 della proposta SAM), che diventa più visibile.
- Suite: 3650 test OK.
