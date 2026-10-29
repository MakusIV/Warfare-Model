# Ricerca: sensori di scoperta di ZSU-57-2 e M163 VADS (2026-10-29)

Ricerca web, nessuna modifica al codice. Scopo: sapere che sensore avevano davvero i due semoventi
antiaerei oggi con `'radar': False` e `'TVD': False` in `Asset/Vehicle_Data.py`
(`ZSU_57_2_data` ~riga 3676, `M163_VADS_data` ~riga 3785), per poterli inserire con una Proposta
separata. Il pianificatore di rotte (`Logic/Air_Route_Manager.py`, `DetectionThreat`) legge
`acquisition_range` da `radar` o `TVD`; il sensore `'visual'` e' "previsto, non ancora nei dati"
(decisione D-4(c)).

Convenzioni di questo documento:
- **[FONTE]** = valore dichiarato da una fonte; **[DEDOTTO]** = ricavato da me da dati di fonte con un
  passaggio dichiarato; **[STIMA]** = mia stima, non e' un dato tarato.
- **Confidenza**: alta = piu' fonti indipendenti o fonte primaria/manuale tecnico; media = una fonte
  secondaria seria o piu' fonti deboli concordi; bassa = fonte unica o debole.
- Nessuna fonte primaria (manuale tecnico TM/FM, documento DTIC) e' stata letta: DTIC non raggiungibile
  (errore di rete), GlobalSecurity e Military Periscope (parte) bloccati (HTTP 402 / login), SWOV
  bloccato da un controllo anti-bot. Quindi **nessun valore qui sotto ha confidenza "alta" per fonte
  primaria**; l'"alta" e' possibile solo per concordanza di piu' fonti indipendenti.

---

## 1. ZSU-57-2

### 1.1 Cosa aveva davvero

| Punto | Valore | Tipo | Fonte | Conf. |
|---|---|---|---|---|
| Radar di scoperta o di tiro nella versione base | **nessuno** | FONTE | Wikipedia ZSU-57-2 ("lack of a search or fire-control radar" = difetto principale); armedconflicts/valka.cz (elenca "mancanza di guida radar" tra gli svantaggi); CMANO-DB (descrizione "lacked any fire control or tracking radar"); articolo russo techinsider.ru ("RLS assente") | **alta** (4 fonti concordi, per quanto non primarie) |
| Mezzo di condotta del tiro | mirino riflesso ottico-meccanico analogico, "unico sistema di condotta del tiro, quindi poteva ingaggiare solo bersagli visibili" | FONTE | Wikipedia ZSU-57-2 | media |
| Tipo di mirino | mirino automatico "plotter" a due collimatori (punto d'incontro), con mirino meccanico semplice di riserva; inseguiva bersagli fino a 350 m/s, angoli di picchiata 0-90 gradi, **"slant range" fino a 5.500 m** | FONTE | Wikipedia ZSU-57-2 | media (la pagina ha tag di accuratezza contestata) |
| Dati di tiro | velocita' e direzione del bersaglio **stimate a vista** e inserite a mano da un "sight adjuster"; distanza stimata a vista **o** da telemetro ottico | FONTE | Wikipedia; armedconflicts/valka.cz ("parameters entered manually", telemetro ottico) | media-alta (due fonti indipendenti) |
| Scoperta del bersaglio | **solo visiva**: "Обнаружение противника могло производиться только визуально" | FONTE | techinsider.ru (articolo divulgativo russo) | bassa-media (fonte popolare, ma coerente con le altre) |
| Chi scopre | non indicato dalle fonti; torretta aperta con buona visibilita' | non trovato | Wikipedia lo dice solo come "buona visibilita'" | - |
| Equipaggio | 6: comandante (punta in azimut), driver, puntatore (elevazione, spara), regolatore del mirino, 2 caricatori | FONTE | Wikipedia | media |
| Binocoli / telemetro in dotazione | un telemetro e' citato ("optical rangefinder"); binocoli: **non trovato** | FONTE/non trovato | armedconflicts/valka.cz | bassa |
| Notte | tiro notturno "impraticabile"; solo visore IR TVN-1 per il guidatore | FONTE | Wikipedia | media |
| Tempo / meteo | "limitato a tempo sereno", "quasi inutile contro jet moderni con scarsa visibilita'" | FONTE | riepilogo di ricerca su sintesi di GlobalSecurity/FAS (pagine non lette direttamente) | bassa-media |
| Tiro in movimento | tiro sugli aerei in movimento non previsto; fuoco efficace solo a veicolo fermo | FONTE | vk.ru (articolo divulgativo russo) | bassa-media |

### 1.2 Varianti con radar: esistono?

Risultato: **nessuna variante di serie con radar di tiro dimostrata**.
- Wikipedia (pagina con tag "accuratezza contestata / fonti autopubblicate") riporta: (a) versioni
  egiziane "modernizzate con un radar", senza modello ne' data; (b) una modernizzazione finlandese
  "ZSU-57-2M" con radar e munizioni configurabili, un solo prototipo. Confidenza **bassa**.
- **Contraddizione con il museo finlandese** (ilmatorjuntamuseo.fi): la modernizzazione finlandese dei
  primi anni '90 avrebbe aggiunto "calcolatori elettronici, sistemi di mira e visione notturna" (nessun
  radar), ma il progetto fu giudicato troppo costoso; i mezzi (57 ItPsv SU-57) furono radiati nel 2006.
  Il museo e' la fonte piu' specifica sul caso finlandese: preferirla. Per l'Egitto: non confermato.
- Confusioni da evitare: SON-9 / PUAZO-6 appartengono alla S-60 **trainata**; "Gun Dish" (RPK-2) alla
  ZSU-23-4. Le fonti dicono che la ZSU-57-2 non e' radar-guidata e che la batteria di S-60 con radar era
  piu' efficace (confidenza media, concordi: Wikipedia, FAS, valka.cz, vk.ru).
- Cenno non letto direttamente: un riepilogo di ricerca su GlobalSecurity parla di un sistema di mira
  "piu' sofisticato" nelle ultime produzioni (due piccole aperture sul frontale della torretta). Non
  verificato.
- Uso con cueing esterno: i ZSU-57-2 iracheni avrebbero ricevuto informazioni radar da ZSU-23-4 o da
  Strela (Wikipedia). E' un'operazione di rete C2, non un sensore del mezzo.

### 1.3 Portate

| Grandezza | Valore | Tipo | Fonte | Conf. |
|---|---|---|---|---|
| Portata obliqua massima del mirino automatico | 5,5 km | FONTE | Wikipedia | media |
| Gittata efficace contro bersagli aerei (ingaggio) | 4 km | FONTE | museo finlandese ("effective range 4000 m"); armedconflicts/valka.cz (quota 1.000-4.000 m, slant 5.500 m) | media |
| Quota massima efficace | 4,5 km (massima 8,8 km) | FONTE | Wikipedia | media |
| Autodistruzione dei proietti HE | 12-16 s, quindi slant range 6,5-7 km | FONTE | Wikipedia; forum russo 2005 (debole) | media |
| Raggio "Air Max" | 2,2 km | FONTE debole | CMANO-DB (database di gioco/simulazione) | **bassa; CONTRADDIZIONE** con i 4-5,5 km sopra: probabile valore tarato per il gioco |
| Portata visiva di scoperta contro un aereo | non trovato come dato del mezzo | non trovato | - | - |
| Portata "27,8 km" del "Generic Optical Sight" | CMANO-DB | FONTE debole | e' un valore generico di database di gioco (orizzonte), **da non usare** | bassa |

La modalita' operativa reale (da piu' fonti): l'equipaggio **scopre a occhio nudo** l'aereo, il
regolatore stima velocita'/rotta/distanza e le inserisce nel mirino, i puntatori seguono il bersaglio nel
collimatore; il tiro efficace era a veicolo fermo. Questa e' una descrizione dedotta dalla
combinazione delle fonti sopra, non una citazione.

---

## 2. M163 VADS

### 2.1 Che cosa e' vero

| Punto | Valore | Tipo | Fonte | Conf. |
|---|---|---|---|---|
| Radar AN/VPS-2 | esiste; **solo distanza (range-only)**; "incapace di usare il radar per scandire l'area" | FONTE | Wikipedia M163; AMPS review ("no search radar"); Military Periscope ("range-only radar", "coherent pulse-Doppler range-only radar"); Italeri; DTIC (elenco: "AN/VPS-2 range-only radar" tra gli elementi dell'XM163); War Thunder wiki (gioco: solo tracking, nessuna ricerca) | **alta** (fonti indipendenti concordi) |
| Cosa misura | distanza e variazione di distanza (range rate) | FONTE | FAS ("supplies range and range rate") | media |
| Portata minima / massima | **250 m / 5.000 m** per un bersaglio di 1 m2 | FONTE | AFV Database | media (unica fonte con la dipendenza dalla RCS) |
| Portata del radar secondo altre fonti | 5 km (PIVADS) | FONTE | weaponsystems.net | media (concorda) |
| Portata 7 km | War Thunder wiki | FONTE debole | **CONTRADDIZIONE**: 7 km contro 5 km; gioco, da scartare | bassa |
| Inseguimento di bersagli | velivoli ad ala fissa non a elica: velocita' minima 15 m/s; aerei a elica o elicotteri anche a 0 m/s, se la potenza della modulazione Doppler delle parti rotanti e' sufficiente | FONTE | AFV Database | media (unica fonte) |
| Antenna | montata sulla torretta, si muove con la canna; il mirino puo' essere puntato indipendentemente | FONTE | riepilogo di ricerca su una sintesi (pagina non identificata) | bassa |
| Funzione operativa | il puntatore **trova il bersaglio a vista**, lo inquadra nel mirino, poi aggancia il radar per la distanza; nessuna ricerca radar | FONTE/DEDOTTO | War Thunder wiki (debole), AMPS, Wikipedia; AFV db | media (coerente con le tre fonti serie sul "range-only") |
| Mirino | M61 "lead-calculating" (calcola l'anticipo), telescopio M134; "computing sight M61, telescope M134" | FONTE | Wikipedia, AMPS, AFV Database | media-alta |
| Mirino giroscopico | **"Navy Mk 20 Mod 0 gyro lead computing sight"** (Military Periscope); "gyro stabilized lead computing sight" (venditore di ricambi per l'M61) | FONTE debole | **CONTRADDIZIONE di denominazione**: Wikipedia e AMPS dicono "ottico M61", FAS "M1A1"; la presenza di un giroscopio per l'anticipo e' plausibile ma **non confermata da fonte primaria**: confidenza bassa-media. Wikipedia e AMPS non nominano il giroscopio | bassa-media |
| Notte | add-on AN/PVS montabile a destra del mirino (Wikipedia); AN/TVS-2B per il puntatore (AFV Database); "capacita' limitata di ingaggio contro aerei di notte" (AMPS); **"solo il guidatore" ha visione notturna** (weaponsystems.net) | FONTE | **CONTRADDIZIONE** fra le fonti sulla visione notturna del puntatore | bassa-media |
| Tempo | "limitato al tempo sereno" | FONTE | Wikipedia; weaponsystems.net ("clear weather only") | media (due fonti) |
| Equipaggio | 4 (comandante, puntatore, caricatore, driver) (Wikipedia); "torretta a un solo operatore" (Military Periscope); 1988: Stinger al 4o uomo | FONTE | non contraddittorio: in torretta c'e' solo il puntatore, in torretta aperta | media |
| Scoperta visiva da parte dell'equipaggio | torretta aperta: "migliore consapevolezza situazionale e campo visivo" | FONTE | AMPS | media |
| Mezzo di scoperta in dotazione oltre alla vista | **non trovato** | non trovato | - | - |

### 2.2 Portate del cannone (limite dell'ingaggio)

| Grandezza | Valore | Tipo | Fonte | Conf. |
|---|---|---|---|---|
| Gittata efficace con HEI-T-SD M246 | 1.200 m | FONTE | Wikipedia | media |
| Autodistruzione HEI-T | circa 1.800 m | FONTE | Wikipedia | media |
| Con M940 MPT-SD / Mk 149 APDS | 2.000 m / 2.500 m | FONTE | Wikipedia | media |
| Con APDS (PIVADS 1984) | 2.600 m | FONTE | FAS; weaponsystems.net (2,6 km) | media-alta (due fonti) |
| Anti-aereo (FAS, voce "range") | 5.249 ft (circa 1.600 m); terra 3.281 yd (3.000 m) | FONTE | FAS | bassa-media: **lieve contraddizione** con 1.200 m; riconciliabile con diverse munizioni |
| Gittata contro bersagli a terra | fino a 3 km | FONTE | weaponsystems.net; FAS | media |

### 2.3 Modellazione: `radar` o `TVD`?

Raccomandazione (mia, ragionata, **non decisa**): **`TVD` e non `radar`**. Motivi:
1. Il AN/VPS-2 non scopre nulla: non scandisce, serve solo a misurare la distanza dopo che il
   puntatore ha inquadrato il bersaglio a vista. L'`acquisition_range` della scoperta nel DES e' la
   portata di un sensore che *trova* i bersagli; metterla sotto `radar` sarebbe sbagliato.
2. Inoltre `build_air_defense_threats` usa per `radar` l'orizzonte con k = 4/3 e per `TVD` k = 1: il
   caso ottico e' quello giusto per un mezzo la cui scoperta e' visiva.
3. La portata del radar (5 km) resta come `tracking_range` del TVD (dato di fonte).
4. Tenere `'radar': False` e dare un nome esplicito al modello nel `TVD`, ad esempio
   `'M61 gyro lead-computing sight + visual (AN/VPS-2 range-only radar for ranging)'`.

Alternativa possibile: mettere sotto `radar` il solo AN/VPS-2 con `acquisition_range: 0` (nessuna
scoperta), per non perdere il dato nella scheda; ma l'attuale codice non ha un caso d'uso per un radar
senza scoperta, e un `acquisition_range: 0` rischia di cancellare il volume di rilevamento.

---

## 3. Portata di scoperta visiva diurna: valori di ripiego

| Dato | Valore | Tipo | Fonte | Conf. |
|---|---|---|---|---|
| Rilevamento a occhio nudo di un DC-3 su rotta di collisione, **piloti** | 5,5-8,7 km (media, secondo le condizioni) | FONTE | Howell, citato in Watson, Ramirez, Salud (2009), PMC2680596 | media |
| Rilevamento dello stesso DC-3 da parte di un **osservatore vigile** che conosce l'angolo di avvicinamento ("threshold distance") | 17,3-23 km, circa 3 volte quello dei piloti | FONTE | idem | media; e' un **limite superiore** (vigilanza costante, bersaglio noto) |
| Limite di risoluzione dell'occhio | circa 1 minuto d'arco | FONTE debole | siti di divulgazione e forum | bassa; e' un limite teorico, non una distanza di scoperta |
| "Tally" visivi di un controllore: 10-14 km | aneddotico | FONTE debole | forum | bassa; non usabile |
| Dati su caccia a bassa quota contro sfondo di terreno | **non trovato** (il rapporto HumRRO 1966 su osservatori a terra e' accessibile solo come abstract) | non trovato | - | - |

Deduzione [DEDOTTO]: la distanza di rilevamento scala all'incirca con le dimensioni angolari. Un DC-3
ha apertura alare di circa 29 m (conoscenza generale, non dalla fonte), un caccia/cacciabombardiere
dell'epoca 8-12 m: fattore circa 0,3. Quindi per un caccia: osservatore vigile circa 5-7 km (limite
alto), piloti distratti circa 1,5-2,5 km. Un servente di AAA che sa di dover guardare il cielo e riceve
un preavviso (radio, rumore) sta fra i due.

**Valore di ripiego proposto [STIMA]**: `acquisition_range` visiva diurna in cielo sereno contro un
aereo a bassa quota di dimensioni da caccia = **5-6 km** (intervallo plausibile 3-8 km). Il registro ha
gia' un 'Optical sight' (SA-9, `9K31`) con `acquisition_range` 8: e' piu' generoso; coerenza interna
da decidere (v. Dubbi).

**Non vale** di notte, in nebbia, pioggia forte, cielo coperto a bassa quota o contro un bersaglio con
sole alle spalle: tutte le fonti dei due mezzi dicono "solo tempo sereno" (Wikipedia, weaponsystems.net,
GlobalSecurity/FAS via riepilogo) e per la ZSU-57-2 "tiro notturno impraticabile". Il registro non ha
oggi un parametro giorno/notte o meteo per i sensori: se il modello li vorra', e' un'altra decisione.
Per il M163 di notte esistono add-on (AN/PVS, AN/TVS-2B) con "capacita' limitata" (AMPS): non
quantificabile con i dati trovati.

---

## 4. Bozza dei valori (PROPOSTA NON DECISA)

Unita': km, come nello schema del registro. Tutta la bozza e' marcata con i limiti di confidenza.

### 4.1 ZSU-57-2

```python
'radar': False,
'TVD': {
    'model': 'Optical sight (visual observation + analog reflex sight)',   # nome: STIMA descrittiva
    'capabilities': {
        # acquisition 6: STIMA (visiva diurna, intervallo 3-8); tracking 5,5: FONTE (Wikipedia, slant range
        # massimo del mirino, conf. media); engagement 4: FONTE (museo finlandese/valka.cz, conf. media)
        'air': (True, {'tracking_range': 5.5, 'acquisition_range': 6, 'engagement_range': 4, 'multi_target_capacity': 1}),
        # ground: opzionale; il mirino diretto era usato anche contro bersagli terrestri, efficaci 4 km
        # (Wikipedia, media); acquisition a terra NON trovata: STIMA
        'ground': (True, {'tracking_range': 4, 'acquisition_range': 5, 'engagement_range': 4, 'multi_target_capacity': 1}),
        'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
    },
    'reliability': {'mtbf': 50, 'mttr': 3},   # NON trovato: segnaposto copiato dal 'Optical sight' del registro (SA-9), STIMA
},
```

### 4.2 M163 VADS

```python
'radar': False,   # l'AN/VPS-2 e' range-only: non scopre. Vedi raccomandazione 2.3
'TVD': {
    'model': 'M61 gyro lead-computing sight + visual (AN/VPS-2 range-only radar for ranging)',   # "gyro": conf. bassa-media
    'capabilities': {
        # tracking 5: FONTE (AN/VPS-2 5.000 m per 1 m2, AFV Database + weaponsystems.net, media);
        # acquisition 6: STIMA (visiva, come ZSU-57-2); engagement 1,2: FONTE (HEI-T-SD, Wikipedia, media),
        #   2,0-2,6 con M940/APDS (PIVADS 1984, oltre il periodo base 1969)
        'air': (True, {'tracking_range': 5, 'acquisition_range': 6, 'engagement_range': 1.2, 'multi_target_capacity': 1}),
        # ground: opzionale; gittata a terra 3 km (FAS, weaponsystems.net, media); il radar non serve a terra;
        #   acquisition a terra NON trovata: STIMA
        'ground': (True, {'tracking_range': 3, 'acquisition_range': 5, 'engagement_range': 3, 'multi_target_capacity': 1}),
        'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
    },
    'reliability': {'mtbf': 50, 'mttr': 3},   # NON trovato: segnaposto STIMA
},
```

Riassunto dei limiti di confidenza:
- `acquisition_range` = 6 (entrambi): **STIMA bassa**. Nessuna fonte da' la portata di scoperta dei due
  mezzi; deriva dai dati di Howell via scala dimensionale (v. 3).
- `tracking_range` ZSU = 5,5: media (unica fonte, pagina con tag di accuratezza).
- `tracking_range` M163 = 5: media (due fonti indipendenti; 7 km di War Thunder scartato).
- `engagement_range` ZSU = 4: media. M163 = 1,2: media. Il valore 2,6 e' di una versione successiva.
- `reliability`: non trovato.
- `multi_target_capacity` = 1: logico (un solo bersaglio per volta, fonti concordi sul mirino unico),
  non una citazione.
- Nota sull'ordine: nei dati del registro `acquisition >= tracking >= engagement`; la bozza lo rispetta.

---

## 5. Dubbi e decisioni per l'utente

1. **`radar` o `TVD` per il M163**: raccomandato `TVD` con `'radar': False` (2.3). Confermare, oppure
   volere il VPS-2 nel campo `radar` con `acquisition_range` 0 (con il rischio descritto)?
2. **Il sensore `'visual'`** e' gia' previsto nel codice (decisione D-4(c)) ma non nei dati. Si usa
   `TVD` ottico (come SA-9) o si introduce `'visual'` con proprie regole (niente notte/maltempo, k = 1)?
   Con `TVD` il DES non distinguera' giorno/notte.
3. **Valore di `acquisition_range` visivo**: 6 km e' una stima; il registro ha 8 per l'Optical sight
   del SA-9. Si vuole armonizzare (tutti i visivi a 6? a 8?) o dichiarare il valore per piattaforma?
   Se serve una scelta prudente, 3-4 km e' compatibile con la scala dei piloti.
4. **Giorno/notte e meteo**: non rappresentabili oggi. Si accetta che la ZSU-57-2 e il M163 abbiano la
   scoperta piena anche di notte (irreale), o si aggiunge un parametro (altra Proposta)?
5. **Versioni**: M163 con PIVADS/APDS (dal 1984, 2,0-2,6 km) e radar identico: modellare una variante
   separata o tenere solo la base 1969? La ZSU-57-2 "con radar" (Egitto/Finlandia) e' non verificata:
   non inserirla.
6. **`ground`**: nei due record i sensori terrestri sono stime; si includono in questa Proposta o solo
   `air`?
7. **Contraddizioni irrisolte**: (a) "gyro" nel mirino M61: Military Periscope e un venditore dicono
   giroscopico, Wikipedia/AMPS "ottico"; (b) visione notturna del puntatore M163 (AN/TVS-2B vs "solo
   guidatore"); (c) radar finlandese ZSU-57-2M (Wikipedia) contro "solo calcolatori e visione
   notturna" (museo); (d) 2,2 km (CMANO) contro 4-5,5 km per la ZSU. Per risolverle serve una fonte
   primaria (manuale TM del M163, scheda Jane's): non accessibili qui.
8. **Reliability**: nessun dato trovato; i segnaposto copiano il SA-9. Decidere se tenerli o usare un
   valore medio del registro.

## Fonti usate

Piu' solide (non primarie):
- Wikipedia: [ZSU-57-2](https://en.wikipedia.org/wiki/ZSU-57-2) (tag di accuratezza contestata), [M163 VADS](https://en.wikipedia.org/wiki/M163_VADS)
- [AFV Database, M163](https://www.afvdatabase.com/usa/m163.html) (la sola con portata min/max del VPS-2 e velocita' minime)
- [Museo di difesa aerea finlandese, ZSU-57-2](https://ilmatorjuntamuseo.fi/ilmatorjuntamuseo/kokoelman_helmet/zsu-57-2/)
- [FAS, M163](https://man.fas.org/dod-101/sys/land/m163.htm), [weaponsystems.net, M163](https://weaponsystems.net/system/67-M163+Vulcan), [AMPS review, M163](https://www.amps-armor.org/SiteReviews/ShowReview.aspx?id=14234)
- [Military Periscope, AN/VPS-2](https://www.militaryperiscope.com/weapons/electronics/naval-radars/anvps-2/overview/) e [M163](https://www.militaryperiscope.com/weapons/ground-combat-vehicles/air-defense/m163-vulcan/overview/) (parti libere)
- Watson, Ramirez, Salud 2009, [PMC2680596](https://pmc.ncbi.nlm.nih.gov/articles/PMC2680596) (cita Howell)

**Deboli** (usate solo come conferma o contraddizione, mai come base):
- [CMANO-DB, ZSU-57-2](https://cmano-db.com/facility/104/), [War Thunder wiki, AN/VPS-2](https://wiki.warthunder.com/AN/VPS-2) e [forum Steam](https://steamcommunity.com/app/236390/discussions/0/1836811737971949533): database/wiki di giochi
- [armedconflicts/valka.cz](https://www.armedconflicts.com/-t963), [vk.ru](https://m.vk.ru/@modelist_na_leningradke-rasskazy-ob-oruzhii-zsu-57-2), [techinsider.ru](https://www.techinsider.ru/weapon/6232-okhotniki-za-samoletami-sami-ne-letaem-i-drugim-ne-daem/): articoli divulgativi/forum
- Riepiloghi di ricerca non letti direttamente (GlobalSecurity, DTIC XM163, antenna VPS-2, varianti con "mirino piu' sofisticato"): da non considerare verificati.

## Valori "non trovato"

- Portata di scoperta visiva *specifica* di ZSU-57-2 e M163 (nessuna fonte).
- Chi scopre i bersagli in ZSU-57-2; binocoli in dotazione.
- Reliability (`mtbf`, `mttr`) dei sensori.
- Capacita' notturna quantificata del M163; dati di ZSU-57-2 notturni.
- Conferma di un radar su varianti reali della ZSU-57-2.
- Fonte primaria sul giroscopio dell'M61 e sulla portata operativa del VPS-2.
