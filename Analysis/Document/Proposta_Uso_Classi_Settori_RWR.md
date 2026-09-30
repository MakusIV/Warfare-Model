# Proposta: uso delle classi e dei settori RWR nel risolutore

Attività 2 dell'elenco del 2026-09-29, stato al commit `5c982062`.

## 1. Cosa usa oggi il modello (dal codice)

`Asset/Aircraft_Rwr_Data.py` registra per ogni aereo: `classes`, `modes`, `sectors`, `ewr`,
`confidence`. Il risolutore ne consuma una parte sola, tramite
`Air_Defense_Efficacy.rwr_perception`:

- **l'unione delle classi** (`rwr_categories`): *se* l'RWR riconosce la categoria SAM
  dell'emettitore;
- **le modalità** (`rwr_modes`): *quando* la minaccia è percepita, al rilevamento se l'RWR vede la
  ricerca, altrimenti al lancio (SPO-10).

Percepita la minaccia, `_perceive` la mette in `seen_by` della forza dell'aereo senza distinguerne
la fonte. `_perceived_ratio` pesa ogni nemico percepito con la E(N) del **sistema esatto**
(`air_threat_weight`). Un Su-25 illuminato da uno Shilka "sa" che è uno Shilka, anche se lo SPO-15
lo mette nella stessa classe del Tunguska. Un MiG-21 (SPO-10, "SAM" generico) sa lo stesso.

Non usati: **granularità delle classi**, **settori**, **ewr**, **confidence**.

## 2. Le classi: la minaccia percepita dalla sola RWR è stimata sulla classe

### Regola proposta (R-CLS)

Un nemico percepito **solo** dall'RWR (nessun sensore della forza lo ha rilevato entro t) pesa nel
rapporto di forze percepito con la E(N) **rappresentativa della classe** in cui l'RWR lo mette,
non con la sua E(N) esatta. Appena un sensore della forza lo rileva, è identificato e pesa con la
propria E(N) (come oggi).

- **Classe**: quella, fra le `classes` dell'RWR dell'aereo illuminato, che contiene la categoria
  dell'emettitore. Con aerei diversi illuminati dallo stesso emettitore vale la classe **più fine**
  (la formazione si scambia le informazioni via radio).
- **Catalogo della classe**: i sistemi dei registri che **emettono** (solo loro accendono un RWR)
  e la cui categoria sta nella classe, **dello stesso dominio** dell'emettitore (terra o mare). Il
  pilota sa se sorvola il mare. Senza questo filtro le navi, con E(N) ≈ N, dominerebbero ogni classe.
- **Rappresentativo**: v. Q1.

### Numeri (E(N) contro 4 aerei, catalogo terrestre dei registri, emettitori)

| Classe | Sistemi | E(4) esatte | media | massimo |
|---|---|---|---|---|
| VSHORAD | Gepard, Shilka | 0,38 / 0,62 | 0,50 | 0,62 |
| SHORAD | Tunguska, Osa, Tor, Roland | 2,66 / 1,81 / 2,20 / 2,53 | 2,30 | 2,66 |
| MRSAM | Kub, Buk | 1,04 / 1,98 | 1,51 | 1,98 |
| LRSAM | S-300PS | 1,98 | 1,98 | 1,98 |
| SPO-15: VSHORAD+SHORAD | i 6 sopra | | 1,70 | 2,66 |
| SPO-10: tutte | i 9 terrestri | | 1,69 | 2,66 |

Esempio: 4 Su-25 illuminati da uno Shilka. Oggi la minaccia vale 0,62. Con R-CLS vale 1,70
(media) o 2,66 (massimo): lo SPO-15 non separa lo Shilka dal Tunguska. Un F-16 (ALR-69, classi
separate) resta a 0,50/0,62. Un MiG-21 (SPO-10) illuminato da un Buk vale 1,69 invece di 1,98:
la classe generica può anche **sottostimare**.

Effetto a valle: un rapporto di forze percepito più basso abbassa la soglia di rottura; la forza
aerea con un RWR grossolano rompe il contatto prima davanti a sistemi deboli e più tardi davanti a
quelli forti. È l'effetto voluto: meno informazione, stima più incerta.

### Aggancio per il futuro

Il catalogo è un parametro iniettabile (`rwr_catalogue`) di `resolve_engagement`. Il chiamante potrà
restringerlo all'inventario del nemico (campo `users` dei registri, quando esisterà la corrispondenza
lato → paesi). Oggi vale il catalogo per dominio.

## 3. I settori: nessun consumatore oggi

La direzione servirebbe a:

1. **evasione / ripianificazione della rotta** verso il settore libero: il DES segue rotte fisse, e il
   disingaggio è astratto (la forza esce dall'ingaggio, senza direzione);
2. **puntamento di armi antiradiazione** (SEAD): serve la direzione precisa, e la `fire_control`
   non sceglie bersagli dalla sola percezione RWR;
3. **fusione degli emettitori**: due emettitori della stessa classe nello stesso settore visti come uno
   (lo SPO-15 mostra per esteso solo la minaccia principale). Le fonti sono deboli (v.
   `Ricerca_RWR_2026_09_29.md`), e la regola sottostimerebbe la minaccia con un dato incerto.

**Raccomandazione**: non usare i settori ora. Restano registrati per il modulo rotte/evasione e per
un futuro SEAD. `ewr` e `confidence`: stesso trattamento (l'EWR non ha E(N); `confidence` è un dato
di tracciabilità, non di modello).

## 4. Decisioni richieste

- **Q1** (rappresentativo della classe): **media** del catalogo (stima neutra, l'errore può andare
  nei due sensi) oppure **massimo** (dottrina prudente, "assumi il peggio della classe": un RWR
  grossolano fa sempre sovrastimare)? *Raccomandato: media.*
- **Q2** (identificazione): un sensore della forza che rileva l'emettitore lo identifica esattamente
  (come oggi per ogni rilevamento)? *Raccomandato: sì.*
- **Q3** (settori, ewr): rimandati al modulo rotte/evasione e SEAD? *Raccomandato: sì.*

## 5. Impatto sul codice

- `Air_Defense_Efficacy`: `rwr_class_of(aircraft, emitter)` (la classe che contiene la categoria),
  `class_threat_weight(classe, dominio, n_aircraft, catalogue)` con cache per (classe, dominio, n).
  Il catalogo di default si costruisce una volta dai registri (asset leggeri per `_model`).
- `Engagement_Resolver`: la percezione registra la fonte (`seen_by` resta com'è; nuovo
  `identified_by[force][asset]` per i sensori, `rwr_class[force][asset]` per l'RWR, classe più fine);
  `_perceived_ratio` sceglie il peso esatto o di classe. Il flusso RNG non cambia (nessuna estrazione).
- Test: classe fine vs grossolana, identificazione successiva, più aerei con RWR diversi, dominio,
  catalogo iniettato; misura degli scenari con forze aeree (S19, S1, combined arms) prima/dopo.

## 6. Decisioni dell'utente (2026-09-30)

- **Q1**: media del catalogo della classe.
- **Q2**: un sensore della forza che rileva l'emettitore lo identifica esattamente.
- **Q3**: settori, `ewr` e `confidence` rimandati al modulo rotte/evasione e al SEAD.

## 7. Implementazione (2026-09-30)

- `Air_Defense_Efficacy`: `rwr_class_of`, `emitter_domain` (`GROUND`/`SEA`),
  `default_rwr_catalogue` (emettitori dei registri con categoria ed E(N), costruiti come asset
  leggeri dal solo modello, in cache), `class_threat_weight` (media, in cache per classe, dominio
  ed N; None se la classe non ha sistemi nel catalogo → peso esatto), `ALL_SAM_CLASS`.
  `clear_cache` svuota anche queste cache.
- `Engagement_Resolver`: `identified_by` (sensori) e `rwr_class` (RWR, una voce per aereo
  illuminato) accanto a `seen_by`; `_perceive_rwr`, `_air_threat` in `_perceived_ratio`; parametro
  `rwr_catalogue` di `resolve_engagement`.
- Test: `Test_Air_Defense_Efficacy.TestRwrClassThreat` (5) e
  `Test_Engagement_Resolver.TestRwrClassThreat` (5). Suite 3753 OK.
- **Misura sugli scenari di sessione** (4 moduli, con e senza la regola): 866 calcoli di minaccia,
  41 con peso di classe, **esiti identici**. Gli scenari usano aerei con RWR digitali (A-10C,
  F-16), le cui classi hanno una sola categoria. Lo Shilka pesa quindi con la media VSHORAD
  (Gepard + Shilka): 0,46 invece di 0,57. Il Buk pesa con la media MRSAM (Kub + Buk): 1,20 invece
  di 1,49. L'effetto forte (SPO-15, SPO-10) non è esercitato da nessuno scenario: è coperto dai test
  unitari.
