---
name: project-ammunition-per-weapon-stock
description: "Scorta munizioni per modello d'arma (Weapon_Stores.py) — A1/A3/A5 implementate 2026-09-26 (commit 1d0c1127), A2 (cannone) implementata (commit 8bd69727); A4 e A6 ancora da fare"
metadata:
  type: project
  originSessionId: b183e431-8211-4d82-bd56-aecf65301f45
  modified: 2026-09-26T21:38:11.777Z
---

**Problema risolto** (bug reale, verificato con numeri concreti prima di correggere): `Mobile.ammunition`
era un solo intero che sommava armi eterogenee (bombe+missili+colpi cannone). `Fire_Control.py`
sceglieva un'arma specifica per nome (pura/memoizzata: stessa arma sempre per la stessa coppia
tiratore/bersaglio), ma il risolutore consumava sempre lo stesso scalare aggregato — un A-10 con 4
Maverick reali ne lanciava 642 (pagati dai colpi cannone nello stesso contatore); F-16 con 4 Mk-83 ne
sganciava 523; BMP-2 con 4 Konkurs ne lanciava 252.

**Design** (commit `1d0c1127`, dettaglio in `Analysis/Document/Proposta_Munizioni_Compatibili_e_Rotte_Attacco.md`):
nuovo `Asset/Weapon_Stores.py`, funzioni pure e condivise fra l'asset reale (`Mobile._stores`) e lo
stato ombra del risolutore (`Engagement_Resolver._Shadow`), così non possono divergere. `_stores:
{modello_arma: quantità}` è lo stato primario; `ammunition`/`interceptor_stock` sono VISTE calcolate
("quattro forme della scorta": pool anonimo per stub/test, voce per arma, arma reale senza dato di
scorta = nessun vincolo, nome estraneo = aggregato di fallback). La regola "SAM puro"
(`interceptor_shares_ammunition`) è ELIMINATA: con la scorta per arma un lanciatore che intercetta e
tira diretto con lo stesso missile scala naturalmente la stessa voce, non serve più il caso speciale.

**A1** (scorta per arma) + **A3** (`ShotSpec.stock_per_round`, armi a raffica consumano più unità per
colpo, `GUN_BURST_ROUNDS=50`) + **A5** (criterio scelta arma `score = Pk / costo^0.5`,
`WEAPON_COST_EXPONENT` stima dichiarata e ricalibrabile — non solo Pk massima) FATTE e committate
insieme. Risultati scenario cambiati e attesi: A-10 preferisce Mk-82AIR a Maverick (più economico); S1
non dà più vittoria netta all'attaccante; S16 alzato a `STRIKE_SIZE=16` (con munizioni reali un raid di
4 F/A-18C veniva assorbito interamente dalle intercettazioni del porto).

**A2** (cannone di bordo come arma candidata vera) FATTA in un secondo commit (`8bd69727`): campo `gun`
su 37 modelli in `Aircraft_Data.py` (i 13 cannoni reali erano già completamente modellati nel
registro, mancava solo l'associazione aereo→cannone). Comportamento cambiato: un aereo in CAP può ora
impegnare un bersaglio terrestre col cannone. Anomalia dati non risolta: AJ/ASJ 37 Viggen ha 150
`gun_rounds` nel loadout ma nessun cannone interno assegnato (Oerlikon-KCA è della variante JA 37) —
lasciato senza `gun` deliberatamente.

**Ancora da fare**:
- **A4** (filtro per tipo di missione/bersaglio, tabella `MISSION_WEAPON_TASKS`): rimandata
  esplicitamente all'entità `Mission`, che non esiste ancora nel motore (v.
  [[project_session_2026_09_26_summary]], punto sulle 6 decisioni di `Analisi_Modello_Missione_Sessione.md`).
- **A6** (revisione della proposta SAM D+B+F, [[project_session_2026_09_25_summary]]): va rifatta
  sopra la scorta per arma, non più sullo scalare — l'utente ha confermato l'ordine A1 prima, poi A6.
- Il `cost` dei cannoni nel registro è il prezzo dell'arma non del colpo, quindi col criterio Pk/costo
  il cannone finisce quasi sempre dopo i missili — noto, non corretto.
- `Campaign_State` non salva ancora `stores` (nessuna migrazione necessaria: non salvava nemmeno lo
  scalare `ammunition` prima).
