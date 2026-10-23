# F8-R — Ricerca dei tempi di turnaround e riparazione

- **Data**: 2026-10-23 · **Chi**: sessione principale di Claude (Sonnet 5.5) con ricerca web · **Piano**: `Proposta_F8_Sessione_Campagna.md` §4.3
- **Scopo**: sostituire, dove esiste una fonte, le STIME DI PROGETTO di `Context/Context.py` (`AIR_TURNAROUND_S`, `AIR_TURNAROUND_DEFAULT_S`,
  `GROUND_TURNAROUND_S`, `SEA_TURNAROUND_S`, `REPAIR_TIME_FULL_S`). **Questo documento NON modifica il codice**: i valori sono una proposta, li approva l'utente.
- **Esito in una riga**: i dati pubblici trovati sono pochi e quasi tutti di seconda mano. Reggono (con confidenza media o bassa) il turnaround dei velivoli ad ala fissa,
  dei trasporti e degli elicotteri e la riparazione rapida di aerei; **non c'e' nessuna fonte** per il turnaround di reparti terrestri e navi, e per la riparazione di mezzi di terra
  e navi si trovano solo dati qualitativi o di ordine di grandezza molto diverso. Dove non c'e' fonte il valore resta una STIMA e va detto.

## 1. Metodo e limiti (da leggere prima dei numeri)

- 14 ricerche web (ricerca "standard") e 7 tentativi di lettura della pagina originale; **solo 1 fonte e' stata verificata sulla pagina originale**
  (le altre pagine hanno restituito 403/402 o errori di rete). Livello di verifica di ogni fonte nella §5: **V** = letta sulla pagina; **S** = riportata dal motore
  di ricerca, non riletta; **F** = forum o sito secondario.
- Nessuna fonte e' un dato tarato per questo motore: sono ordini di grandezza di operazioni reali, non misure di un modello DES. Il "turnaround" qui e' il tempo da atterraggio
  a nuovo decollo possibile (riarmo, rifornimento, controlli), quindi comprende anche le ispezioni, non solo il tempo al parcheggio caldo.
- Cercato e NON trovato: tempi in ore di riarmo e rifornimento di un reparto corazzato; tempi di riarmo di una nave in porto; tempi di riparazione di carri Abrams; turnaround di ricognitori
  (UAV, U-2). Dove cercare ancora: pubblicazioni di sostenimento dell'Esercito USA sui battaglioni corazzati, rapporti RAND sulla *sortie generation* (la monografia MG611AF e' indicata
  da una fonte come possibile origine della formula del §2, NON verificata), rapporti GAO e CRS su prontezza e riparazione delle navi.

## 2. Turnaround aereo (`AIR_TURNAROUND_S`, secondi)

| Classe | STIMA attuale | Evidenza trovata | Valore proposto | Intervallo plausibile | Confidenza |
|---|---|---|---|---|---|
| Fighter | 7 200 (2 h) | F-35: "normalmente ~3 h per preparare una sortie", obiettivo di un *hot integrated combat turn* 25 min (Hadley, Air & Space Forces, 12/02/2025, **V**). Formula attribuita a RAND per F-15/F-16: 3,4 h + 0,68 x ore di volo, cioe' ~4,4-4,8 h per sortie di 1,5-2 h (**F**, forum, NON verificata). *Hot pit*: tempo a terra ridotto di circa due terzi (**F**, sito divulgativo) | **10 800 (3 h)** | 1 500 - 17 300 (25 min a caldo - 4,8 h) | media-bassa |
| Fighter_Bomber | 9 000 | nessuna fonte specifica; per analogia con Fighter | **10 800** | come Fighter | bassa (analogia) |
| Attacker | 9 000 | nessuna fonte specifica; per analogia con Fighter | **10 800** | come Fighter | bassa (analogia) |
| Bomber | 14 400 (4 h) | "turn-time tipico di un bombardiere circa 4-5 ore: ispezioni, rifornimento e, se serve, caricamento delle munizioni" (colonnello PACAF, campagna in Iraq 2003, generico, **S**, +20 anni) | **16 200 (4,5 h)** | 14 400 - 18 000 | media-bassa |
| Heavy_Bomber | 28 800 (8 h) | nessun dato affidabile su B-52/B-1: un servizio fotografico (**F**) parla di ispezione pre-volo "fino a 12 h" con equipaggio al completo e di 50-65 ore-uomo di manutenzione per ora di volo (grandezza diversa dal turnaround) | **28 800 (invariato)** | 16 200 - 43 200 | bassa: la STIMA resta |
| Awacs | 14 400 (4 h) | E-3: autonomia ~8 h senza rifornimento; di norma si resta in volo con rifornimento in volo e non si atterra; un turn a terra rapido e' citato come eccezionale ("una sola volta in 20 anni", esercitazione Cope Tiger 2008, **S**); un'unita' schierata volava 1-2 sortite al giorno e preparava gli aerei per il giorno dopo (**S**); disponibilita' di flotta 55,7% nel 2024 (**S**) | **43 200 (12 h)** | 21 600 - 86 400 | bassa |
| Recon | 7 200 (2 h) | nessun turnaround trovato: solo un U-2 per sortita al giorno e l'autonomia di ~30 h del Global Hawk (**S**), cioe' tassi di sortita, non tempi a terra | **7 200 (invariato)** | non determinabile | nessuna fonte: la STIMA resta |
| Transport | 10 800 (3 h) | C-17: turn di 3 h 15 min ridotto a 2 h (McChord) e "fino a 4 h per un volo di addestramento locale, fino a 8 h al ritorno da una missione reale" (Charleston); a Balad quasi immediato per l'alto ritmo (tutti **S**) | **10 800 (invariato)** | 7 200 - 28 800 | media-bassa: la STIMA e' confermata |
| Helicopter | 5 400 (1,5 h) | FARP per AH-64: riarmo 10-30 min in piu' dopo il rifornimento (Army Aviation, **S**); 45-50 min complessivi per un elicottero d'attacco (sito polacco, **F**, origine non verificata). Il dato copre il solo FARP, non le ispezioni a terra | **5 400 (invariato)** | 2 700 - 5 400 | bassa: dentro l'intervallo, non dimostrata |
| `AIR_TURNAROUND_DEFAULT_S` (classe ignota) | 9 000 | segue la classe tattica | **10 800** | | bassa |

Lettura: la ricerca **non contraddice** l'ordine di grandezza di Transport, Helicopter, Recon e Heavy_Bomber (restano STIME); suggerisce di **alzare** Fighter, Fighter_Bomber, Attacker (e il default)
da 2-2,5 h a 3 h, Bomber da 4 a 4,5 h e Awacs da 4 a 12 h. Con operazioni sostenute e *hot pit* un caccia puo' scendere sotto l'ora: il valore proposto e' il turn "standard",
non quello massimo di una campagna.

## 3. Terra e mare (`GROUND_TURNAROUND_S`, `SEA_TURNAROUND_S`)

| Dominio | STIMA attuale | Evidenza trovata | Valore proposto | Confidenza |
|---|---|---|---|---|
| Reparto terrestre (riorganizzazione e rifornimento di un reparto meccanizzato) | 21 600 (6 h) | **nessuna fonte con tempi in ore.** Si trovano solo descrizioni del metodo (*service station*, rifornimento a rotazione dal centro dell'area di sosta, **F**) e l'idea di un FARP per unita' pesanti (studio dell'Esercito USA degli anni '90, **S**, senza cifre) | **21 600 (invariato)** | nessuna fonte: la STIMA resta |
| Nave (rifornimento e riarmo in porto) | 43 200 (12 h) | **nessun tempo trovato.** Solo il quadro qualitativo: oggi i VLS si ricaricano solo in porto e il rientro tiene le navi fuori dal combattimento "per settimane" (Heritage Foundation su Defense News 2024, **S**); dimostrazioni di ricarica in banchina (USS Porter a Norfolk; USS Stout a Brest, nov. 2024, **S**) senza durata | **43 200 (invariato)** | nessuna fonte; **la STIMA e' probabilmente troppo bassa per il riarmo dei missili** (giorni, non ore), ma non c'e' un numero |

## 4. Riparazione (`REPAIR_TIME_FULL_S`, secondi per un danno da 100 a 0, lineare)

| Dominio | STIMA attuale | Evidenza trovata | Valore proposto | Confidenza |
|---|---|---|---|---|
| Aria | 86 400 (24 h) | Riparazione rapida temporanea (ABDR): l'aviazione israeliana nel 1973 rimise in combattimento il 72% degli aerei danneggiati entro 24 h; un documento NATO STO fissa il livello "eccellente" in 50% a 24 h e 80% a 48 h (entrambi **S**); la KC-135 colpita nel 2026 richiese 48 h solo per svuotare il carburante (**F**) | **86 400 (invariato)** | media, per il significato di "riparazione temporanea che rimette in volo" |
| Terra | 86 400 (24 h) | un documento DTIC sull'Esercito riporta che un'armata, perso circa tre quarti dei carri, ne rimise in battaglia l'80% entro 24 h (l'esercito non e' nominato, **S**) | **86 400 (invariato)** | bassa |
| Mare | 259 200 (72 h) | USS Samuel B. Roberts, mina del 04/1988 che distrusse la sala macchine: rimorchiata a Dubai per interventi temporanei, riparata in 13 mesi a Bath Iron Works, rientrata in servizio il 16/10/1989, cioe' ~18 mesi (BIW e Naval History and Heritage Command, **S**); USS Stark (Exocet, 05/1987): ritorno in servizio nel 1988, data non confermata (**F**) | **259 200 (invariato) come riparazione temporanea in porto** | **bassa e da decidere**: per un danno grave di una nave la riparazione vera dura **mesi**, non giorni |

## 5. Fonti

| Livello | Fonte |
|---|---|
| **V** | Greg Hadley, [Maintainers Reload and Refuel a 'Hot' F-35A for the First Time](https://www.airandspaceforces.com/maintainers-hot-ict-f-35/), Air & Space Forces Magazine, 12/02/2025 |
| S | colonnello PACAF sul turn-time di un bombardiere, 2003: [globalsecurity.org](https://www.globalsecurity.org/military/library/news/2003/04/mil-030405-pacafns02.htm) (pagina non riletta: HTTP 402) |
| S | AWACS, Cope Tiger 2008: [af.mil](https://www.af.mil/News/Article-Display/Article/124427/deployed-awacs-aircrews-overcome-unique-challenge/); unita' schierata e disponibilita' E-3: [afcent.af.mil](https://www.afcent.af.mil/News/Article/1201766/deployed-maintenance-airmen-enable-40-year-old-awacs-mission), [Air & Space Forces](https://www.airandspaceforces.com/article/awacs-enters-the-homestretch/) |
| S | C-17 McChord: [af.mil](https://www.af.mil/News/Article-Display/Article/126852/afso-21-changes-improve-c-17-availability-at-mcchord/); Charleston: [jbcharleston.jb.mil](https://www.jbcharleston.jb.mil/News/Article/235130/aircraft-maintenance-squadron-soars-high-with-quality/); Balad: [af.mil](https://www.af.mil/News/Article-Display/Article/124637/balad-airmen-take-on-galactic-mission) (pagine non rilette: errore di rete) |
| S | FARP e rearm AH-64: [Army Aviation](https://armyaviationmagazine.com/maximizing-farp-efficiency-in-large-scale-combat-operations/) (pagina non riletta: HTTP 403) |
| S | ABDR: [NATO STO, EN-AVT-156-09](https://www.sto.nato.int/publications/STO%20Educational%20Notes/RTO-EN-AVT-156/EN-AVT-156-09.pdf) (non riletta: HTTP 403); [DTIC ADA245827](https://apps.dtic.mil/sti/pdfs/ADA245827.pdf) (battle damage repair, carri e aerei) |
| S | navi: [USNI Proceedings, "Improving Sea Missile Rearming" (2024)](https://www.usni.org/magazines/proceedings/2024/june/improving-sea-missile-rearming); [Naval News, USS Stout a Brest (2024)](https://www.navalnews.com/naval-news/2024/11/u-s-navy-destroyer-demonstrates-vls-rearming-at-french-naval-base/); [BIW, USS Samuel B. Roberts](https://www.gdbiw.com/legacy-vault/uss-samuel-b-roberts-ffg-58/); [NHHC](https://history.navy.mil/news-and-events/news/2024/nhm-040224.html) |
| F | formula RAND per F-15/F-16 riportata da [un forum](https://forums.bharat-rakshak.com/viewtopic.php?p=793308) (da verificare sull'originale); [hot pit](https://migflug.com/afterburner/hot-pit-refuelling-integrated-combat-turn-explained/); [FARP artico](https://afterburner.com.pl/?p=5114); [service station](https://archive.armorama.com/forums/40101/index.htm) |

## 6. Valori proposti per l'approvazione (commit di soli dati su `Context/Context.py`, §4.4)

Cambiano 6 valori su 14; gli altri restano STIME e conservano il commento "STIMA DI PROGETTO" (con la nota "ricerca F8-R 2026-10-23: nessuna fonte" o "confermata").

| # | Costante | Ora | Proposto | Motivo |
|---|---|---|---|---|
| 1 | `AIR_TURNAROUND_S['Fighter']` | 7 200 | **10 800** | F-35 ~3 h (V); formula RAND non verificata |
| 2 | `AIR_TURNAROUND_S['Fighter_Bomber']` | 9 000 | **10 800** | analogia con Fighter (nessuna fonte) |
| 3 | `AIR_TURNAROUND_S['Attacker']` | 9 000 | **10 800** | analogia con Fighter (nessuna fonte) |
| 4 | `AIR_TURNAROUND_S['Bomber']` | 14 400 | **16 200** | 4-5 h (colonnello PACAF, 2003, S) |
| 5 | `AIR_TURNAROUND_S['Awacs']` | 14 400 | **43 200** | 1-2 sortite al giorno, 8 h di autonomia (S); confidenza bassa |
| 6 | `AIR_TURNAROUND_DEFAULT_S` | 9 000 | **10 800** | segue la classe tattica |

Invariati, con la sola nota nel commento: Heavy_Bomber 28 800, Recon 7 200, Transport 10 800 (confermato), Helicopter 5 400, `GROUND_TURNAROUND_S` 21 600, `SEA_TURNAROUND_S` 43 200,
`REPAIR_TIME_FULL_S` air/ground 86 400 e sea 259 200.

**Decisioni per l'utente**
- **D1**: approvare (o correggere) i 6 cambi della tabella. Alternativa: lasciare tutto com'e' e conservare questo documento come registro delle fonti.
- **D2**: i valori di Fighter_Bomber e Attacker sono per analogia, non da fonte: tenerli a 9 000 oppure allinearli al Fighter?
- **D3 (riparazione navale)**: `REPAIR_TIME_FULL_S['sea']` rappresenta una riparazione *temporanea in porto* (72 h) o la riparazione vera (mesi, cioe' una nave gravemente danneggiata esce di fatto dalla campagna)? Con il modello lineare attuale (salute 100 -> 0) i due significati non convivono: servirebbe una soglia oltre la quale la nave e' fuori servizio per la campagna. Fuori da F8; da decidere con la logistica (F8d).
- **D4 (riarmo navale)**: i 12 h di `SEA_TURNAROUND_S` sono probabilmente troppo pochi per ricaricare i VLS; senza un numero non lo cambio. Si puo' commissionare una ricerca mirata (rapporti GAO/CRS e documenti della Marina).
- **D5**: la verifica delle fonti **S**/**F** sulle pagine originali (soprattutto la formula RAND e il turn-time dei bombardieri) non e' stata possibile con questi strumenti: farla prima di dichiarare i valori "tarati".

## 7. Effetto sul modello

- Le costanti sono dati: nessun cambio di logica. I test sono scritti sulle costanti e sul registro, non sui numeri (S30 calcola gli istanti dai valori); `Test_Context` verifica solo che ogni classe aerea
  abbia un valore > 0.
- **Fotografia**: la prontezza e' usata solo da S30-CAMPAIGN. Il registro non fa parte dell'esito di sessione catturato dalla fotografia, quindi e' probabile che le 4 esecuzioni di S30 restino
  identiche anche con i nuovi valori; **da verificare con il confronto**, non assunto. La precondizione di S30 (`ready_at('mbt0') > t2`) non dipende dai valori aerei.
- Se D1 e' approvata: un solo commit di dati (6 costanti e i commenti), poi suite e confronto; il confronto dira' se qualcosa cambia; la fotografia si reinstalla solo se cambia, con la tua approvazione.
