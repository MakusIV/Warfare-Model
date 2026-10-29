# Ricerca radar EWR / early warning a terra, WWII - Guerra Fredda (2026-10-29)

> Rapporto di ricerca (web) richiesto dall'utente. **Non e' una fonte finale dei dati**: serve a decidere
> quali radar modellare e con quali numeri, in una Proposta separata. Nessun file del repository e' stato
> modificato (questo e' l'unico file nuovo). Periodo: Seconda guerra mondiale - Guerra Fredda (confermato
> dall'utente).

## 0. Metodo, limiti, convenzioni

**Strumenti e limiti reali della ricerca** (da leggere prima dei numeri):
- Le pagine sono state lette con uno strumento che le passa a un piccolo modello riassuntore: i numeri sono
  quelli riportati dal riassunto, non una lettura diretta del sorgente. Dove un valore e' stato ripetuto da
  piu' passaggi (o da due fonti indipendenti) la confidenza e' piu' alta; i casi dubbi sono segnalati.
- **radartutorial.eu non e' scaricabile** dallo strumento (404): i suoi dati vengono dai riassunti del motore
  di ricerca (indicati come "radartutorial, via ricerca"). Le schede radartutorial sono di norma ben fatte ma
  il campo "instrumented range" e' la portata di visualizzazione/strumentale, NON la portata di rilevamento
  contro un bersaglio reale.
- Non erano raggiungibili: GlobalSecurity (402), Hoggit wiki (404), forum DCS (403, solo snippet di ricerca),
  FortWiki (403), il catalogo di export russo (reset), il PDF Lockheed dell'FPS-117 (testo non estraibile: dati
  presi dal riassunto del motore di ricerca che cita la scheda).
- Nessuna fonte primaria (manuali tecnici d'epoca, Jane's, TM militari) e' stata consultata direttamente,
  tranne quando indicato. Molte schede sono quindi di **seconda mano**: Wikipedia (infobox spesso senza
  qualificare il bersaglio), schede divulgative, banche dati di gioco.

**Scala di confidenza**: **alta** = piu' fonti indipendenti concordi o fonte tecnica primaria/ufficiale;
**media** = una fonte tecnica secondaria seria, o piu' fonti non indipendenti; **bassa** = fonte unica o
debole (forum, banche dati di giochi/wargame, giornalismo di guerra, enciclopedie collaborative non
verificate).

**Tipo di dato** (colonna "T"): **F** = dato di fonte; **D** = dedotto da dati di fonte con un calcolo
(mostrato); **S** = STIMA mia / scelta di design (mai dato tarato). "non trovato" = cercato e non reperito.

**Cosa e' "portata di rilevamento" qui.** Per tutti i radar la portata dipende da quota e RCS del bersaglio,
e dall'orizzonte radar. Le fonti danno spesso un singolo "range" senza qualificarlo (tipicamente il massimo
teorico o di visualizzazione). Nelle schede la colonna "Portata aria" riporta ogni valore con il bersaglio e
la quota a cui si riferisce quando la fonte lo dice, altrimenti con "bersaglio non qualificato". Il
bersaglio di riferimento "caccia" ha RCS ~ 1-5 m2 (le fonti russe usano MiG-21 o ~1 m2; Lockheed 1 m2).

## 1. Contesto nel codice e come il dato verrebbe usato

- Enum `Ground_Vehicle_Asset_Type.EWR` presente (`Context/Context.py:751`), **0 voci** in
  `Asset/Vehicle_Data.py` (verifica richiesta dal compito, non rifatta).
- Schema del campo `radar` (es. `1RL33 Gun Dish`, riga ~3747): `model`; `capabilities` per `air`/`ground`/`sea`
  = `(bool, {tracking_range, acquisition_range, engagement_range, multi_target_capacity})` in km;
  `reliability {mtbf, mttr}`. Per un EWR sensato: `air` True; `ground`/`sea` False (a zero) salvo scelta
  diversa; `engagement_range` = 0 (nessuna arma); `tracking_range` e `multi_target_capacity` da decidere
  (v. sez. 5).
- Uso nei volumi di rilevamento (`Logic/Air_Route_Manager.py`, ~290-300 e ~620-640): `acquisition_range` e'
  la "portata nominale di scoperta [m], prima dell'orizzonte" ed e' la R della legge Pd del DES
  (`Engagement_Resolver.detection_probability`); il cilindro ha raggio = min(acquisition_range, orizzonte
  radar alla quota del bersaglio), con orizzonte `d = 4121,8 * (sqrt(h_antenna) + sqrt(h_bersaglio))` m
  (k = 4/3, commento nel codice). Quindi un EWR VHF con `acquisition_range` di 250 km e' tagliato
  dall'orizzonte per i bersagli bassi: es. (D) bersaglio a 500 m e antenna a 10 m: 4,1218*(3,16+22,36) ~ 105
  km; bersaglio a 10 000 m: ~ 412 + 13 = 425 km (non limitante). Una R unica non rappresenta il crollo di
  portata a bassa quota che le fonti russe documentano (v. P-18: 60 km a 500 m contro 180 km a 10 km).
- File locali: `DCS_-_Overview_Vehicles/DCS-Unit_overview.ods` e il `.xlsx` **non contengono nessuna riga EWR**
  (cercati: EWR, 1L13, 55G6, Nebo, Bar Lock, P-37, Tall King, Spoon Rest). Contengono solo radar di ricerca
  integrati nei sistemi SAM (P-19 Flat Face/SA-3, 9S80M1 Dog Ear/SA-9, 5N66M Clam Shell e 64H6E Big Bird/
  SA-10, Roland Radar), che **non** sono EWR: restano parte del rispettivo SAM.
- Unita' EWR di DCS World: l'editor ha due radar di scoperta a terra, **1L13 EWR** e **55G6 EWR** (categoria
  Air Defence). Fonte: forum.dcs.world (snippet di ricerca di piu' thread: "radar support questions",
  "Western/US ground EWR systems", "Can I detect EWR radar with HTS") - **confidenza bassa-media** (forum;
  non ho potuto aprire la wiki Hoggit). Il forum segnala anche l'assenza di EWR occidentali in DCS.

## 2. Elenco ragionato (19 schede)

Criterio: includo (a) le due unita' EWR di DCS; (b) i radar di scoperta a lunga portata piu' numerosi o noti
di ciascun blocco e periodo; (c) radar che coprono una fascia di quote/portate diversa (bassa quota, lunga
portata, trasportabile, fisso). Esclusi con motivo in sez. 2.3.

### 2.1 Seconda guerra mondiale

| # | Radar | Paese | Servizio | Utilizzatori | Perche' rilevante |
|---|---|---|---|---|---|
| 1 | Chain Home (AMES Type 1) | Gran Bretagna | 1938-1955 | RAF | Prima rete EWR operativa; 21 stazioni a settembre 1939, >40 a fine guerra. Lettura manuale, alta quota |
| 2 | Chain Home Low (AMES Type 2) | Gran Bretagna | 1939-dopoguerra | RAF, Canada, Terranova | Copre la bassa quota che il CH non vede (aerei a ~150 m). 100+ costruiti |
| 3 | Freya (FuMG 80) | Germania | 1938-1945 | Luftwaffe, Kriegsmarine; Romania | Il EWR tedesco di massa (>1000), base della Linea Kammhuber |
| 4 | Wassermann (FuMG 41/42) | Germania | 1942?-1945 | Luftwaffe | EWR a lunga portata, 4-8 Freya su torre |
| 5 | Mammut (FuMG 41/42 secondo la fonte) | Germania | 1944?-1945 | Luftwaffe | Array fisso a scansione elettronica; lunga portata (attenzione ai nomi/designazioni confusi fra fonti) |
| 6 | Wurzburg (FuMG 62) | Germania | 1940-1945 (un esemplare ceco fino al 1994) | Luftwaffe, Kriegsmarine | Radar GCI/di tiro a corta portata: **limite** della categoria EWR (v. 2.3) |
| 7 | SCR-270 / SCR-271 | USA | 1940-1945 | US Army, USMC | EWR americano; individuo' l'attacco a Pearl Harbor; mobile (270) e fisso (271) |
| 8 | AMES Type 7 (GCI) | Gran Bretagna | 1941-anni '50/'60 | RAF | Radar GCI/EWR 1,5 m a 360 gradi, 33 stazioni; anello di congiunzione CH -> Type 80 |

### 2.2 Guerra Fredda

| # | Radar | Paese | Servizio | Utilizzatori | Perche' rilevante |
|---|---|---|---|---|---|
| 9 | P-12 "Yenisei" (Spoon Rest A/B) | URSS | 1956-oggi (varianti) | URSS e Patto di Varsavia, Egitto, Vietnam, Iraq, Siria, ecc. | VHF mobile 2D anni '50-'60, in Vietnam e Medio Oriente |
| 10 | P-14 "Lena" (Tall King) | URSS | 1959-2003 (731 stazioni) | URSS, Bulgaria, Cina, Egitto, Iraq, Serbia, Vietnam... | EWR VHF statico di grandissima portata, rete PVO |
| 11 | P-18 "Terek" (Spoon Rest D) | URSS | 1970/71-oggi | >20 paesi (URSS, DDR, Polonia, Siria, India, Vietnam, Finlandia...) | EWR mobile VHF piu' diffuso del periodo '70-'80; DATI PIU' COMPLETI (rilevamento per quota, MTBF, tempo di messa in opera) |
| 12 | P-15 "Tropa" / P-19 "Danube" (Flat Face A/B) | URSS | 1955 / 1974 | URSS, DDR, Siria, Algeria, Finlandia... | UHF a bassa quota, radar di scoperta dei battaglioni SAM (S-125); P-19 e' il Flat Face di DCS |
| 13 | P-35 / P-37 (Bar Lock) | URSS | 1958 / 1961 | URSS (PVO, VVS, Marina), Cecoslovacchia, altri | Banda S, 2D, EWR/GCI a lunga portata, alta risoluzione; richiede altimetro PRV-11/13 |
| 14 | 1L13 "Nebo-SV" (Box Spring) | URSS | sviluppo 1982, truppe ~1990 | Forze Terrestri URSS/Russia; export (SVU: Iran) | **Unita' EWR di DCS**; VHF 2D mobile, sostituto del P-18 |
| 15 | 55Zh6 "Nebo" / 55Zh6U "Nebo-U" (Tall Rack) | URSS/Russia | 1982-87 (55Zh6, in servizio dal 1986); Nebo-U 1986-92, in servizio 1995 | PVO URSS, Russia | **Unita' EWR di DCS ("55G6 EWR")**; primo 3D VHF sovietico; lunghissima portata |
| 16 | AMES Type 80 (Green Garlic) | Gran Bretagna | 1955-1993 (UK) | RAF, RCAF (1 a Metz), Svezia (PS-08, 1957-79) | EWR fisso occidentale del ROTOR, banda S ad alta potenza; ~35 costruiti |
| 17 | AN/FPS-20 | USA | 1956/57 - fine anni '60 (varianti oltre) | USAF ADC/NORAD, Canada (AN/FPS-508), Giappone, India | Il EWR/search piu' numeroso occidentale (>200) |
| 18 | AN/TPS-43 | USA | 1968 (citation needed) - oggi | USA, Argentina (6; uno perso alle Falkland), Bangladesh, Spagna | 3D trasportabile (due camion M35), bande S |
| 19 | AN/FPS-117 | USA (Lockheed) | 1980-oggi | >15 paesi (>120 prodotti) | EWR allo stato solido a lunga portata, MTBF dichiarato dal costruttore: unico con affidabilita' quantificata |

### 2.3 Esclusi o ai margini (con motivo)

- **SCR-584 (USA, 1943)**: radar di tiro contraerei (rilevamento ~64 km, tracciamento automatico ~29 km, Wikipedia
  "SCR-584 radar") - non e' un EWR; appartiene alle armi AAA. Esclusa.
- **P-40 "Long Track" (1S12, URSS 1963)**: radar di acquisizione del sistema 2K11 Krug (2 MW, 370 km infobox
  Wikipedia) - parte di un SAM; esclusa (come i radar SAM del file DCS).
- **Wurzburg**: tenuto in elenco ma da valutare se rientra nella categoria "EWR" o in "radar di tiro/GCI".
- **Nebo-SVU (1L119)** e **Nebo-M** (anni 2000+): fuori periodo (post-Guerra Fredda); i dati di Nebo-SVU sono
  usati solo come confronto per l'1L13 (stessa famiglia), mai attribuiti all'1L13.
- Non cercati (dichiarato): radar giapponesi WWII (Tachi-6 ecc.), francesi/italiani/svedesi della Guerra Fredda
  (salvo il PS-08 svedese = Type 80), cinesi (YLC-8 deriva dal P-12), radar navali/aerei.

## 3. Schede

Formato di ogni tabella: dato | T | fonte | confidenza. Fonti abbreviate in fondo (sez. 6). I numeri fra parentesi sono conversioni mie (D).

### 3.1 Chain Home (AMES Type 1)

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Banda/frequenza | 20-55 MHz (4 frequenze spot, cambio in ~15 s); tipico 20-30 MHz | F | [W-CH], [GEC85] via ricerca, [BoB] 22-30 MHz | media-alta (concordi, sfumature) |
| Potenza di picco | 100 kW-1 MW secondo versione; 350 kW tipico, 750 kW in guerra; [BoB] 200 kW | F | [W-CH], [GEC85], [BoB] | media (contraddizione: 200/350/750 kW) |
| Portata aria | "tipicamente 120 mi (190 km)" (testo W-CH); infobox 100 mi (160 km); [BoB] fino a ~120 mi ad alta quota. Bersaglio non qualificato (bombardieri ad alta quota) | F | [W-CH], [BoB] | media (160 vs 190 km) |
| Quota | copertura in elevazione 2,5-40 gradi; "scarsa copertura a bassa quota sotto 2 gradi" [radarpages] | F | [W-CH], [radarpages] | media |
| Tracciamento | non applicabile (rilevamento a CRT, nessun tracking automatico) | D | [W-CH] | media |
| Multi-bersaglio | non trovato (lettura manuale a operatore; il documento descrive la valutazione di raid, non un numero) | - | - | - |
| Precisione | portata <=8 km (1 km tipico), azimut +-12 gradi (tipicamente meno) | F | [W-CH] | media |
| MTBF/MTTR | non trovato | - | - | - |
| Antenna/mobilita' | fissa; torri trasmittenti 4x110 m (cortina), ricezione 4 torri da 73 m (Adcock); trasmette in polarizzazione orizzontale; copertura 150 gradi in azimut | F | [W-CH] | alta |
| Messa in opera | non applicabile (installazione fissa) | - | - | - |
| Servizio | 1938 (primi 5 siti ago 1938) - 1955 | F | [W-CH] | alta |

### 3.2 Chain Home Low (AMES Type 2)

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | 200 MHz (1,5 m) | F | [W-CHL] | media |
| Potenza | 150 kW (infobox, non dice se di picco) | F | [W-CHL] | media-bassa |
| Portata aria | **non trovato** (la fonte da' solo: "rileva con affidabilita' aerei fino a 500 piedi / 150 m di quota") | - | [W-CHL] | - |
| Quota | minima ~500 ft (150 m); CHEL (3 GHz, sistema distinto) arriva a 50 ft | F | [W-CHL] | media |
| Antenna | 4 schiere impilate da 5 dipoli (altezza per confronto); dal Mk V (apr 1941) antenna unica rotante 1-3,3 giri/min; fascio 1,5 gradi | F | [W-CHL] | media |
| Mobilita' | siti fissi; adattamenti mobili su camion (Type 11, 500-600 MHz) | F | [W-CHL] | media |
| Multi-bersaglio, MTBF/MTTR, messa in opera | non trovato | - | - | - |
| Servizio/produzione | luglio 1939 - dopoguerra (sostituito da Type 80 nel ROTOR); 100+ | F | [W-CHL] | media |

### 3.3 Freya (FuMG 80)

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | 250 MHz (1,2 m) originale; 120-130 MHz (2,3-2,5 m) a meta' guerra; FuMG 451 "Freiburg" 162-200 MHz | F | [W-Freya] | media |
| Potenza di picco | 20 kW infobox; 15-20 kW testo | F | [W-Freya] | media |
| Portata aria | infobox 120 km; testo "fino a 160 km" nella guerra avanzata; misura reale: raid di 22 Wellington rilevato a 113 km (18 dic 1939). Bombardieri, quota non qualificata. un riassunto di ricerca riporta 200 km come infobox di Wikipedia (non confermato dalla pagina letta) | F | [W-Freya] | media (120/160/200 km in contraddizione) |
| Quota | "non puo' determinare con precisione la quota" nella forma finale | F | [W-Freya] | media |
| Precisione | lobe switching, risoluzione angolare fino a 0,1 gradi per operatore esperto (versione "AN") | F | [W-Freya] | media-bassa |
| Antenna/mobilita' | schiera fissa orientabile 360 gradi, "semi-mobile"; versione LZ smontabile per trasporto aereo | F | [W-Freya] | media |
| Multi-bersaglio, MTBF/MTTR, messa in opera | non trovato | - | - | - |
| Produzione | >1000; 8 operative a inizio guerra, 11 sul confine occidentale primavera 1940 | F | [W-Freya] | media |

### 3.4 Wassermann (FuMG 41 L / 42 S)

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | 120-150 MHz ([W-Wass]); radartutorial: 125-158 MHz, 158-250 MHz per "Wassermann M" (designazione FuMG 402) | F | [W-Wass], [RT-Wass] via ricerca | media (contraddizione di banda e di designazione) |
| Potenza | 100 kW (infobox, non qualificata) | F | [W-Wass] | bassa |
| Portata aria | 300 km (infobox e radartutorial "instrumented range"); dalla sezione tecnica: **35 km a 50 m di quota, 190 km a 6000 m**; rilevamento "forse fino a 12 000 m". Bersagli: aerei, quota come sopra | F | [W-Wass], [RT-Wass] | media (il 300 km e' quello massimo/strumentale) |
| Precisione | portata +-300 m, azimut +-1/4 grado, quota +-3/4 grado (3-18 gradi) | F | [W-Wass] | media |
| Antenna | L: 4 antenne Freya su traliccio di ~40 m (ruotabile); S: 8 antenne su palo di 60 m; altezza mast 37-57 m; massa 30-60 t | F | [W-Wass] | media |
| Mobilita' | impianto fisso (massa 30-60 t); setup non trovato | D/- | [W-Wass] | bassa |
| Multi-bersaglio, MTBF/MTTR | non trovato | - | - | - |
| Servizio | "1942?" - 1945 (la fonte dubita: sviluppo 1942 per Wikipedia, 1940 per radartutorial) | F | [W-Wass], [RT-Wass] | bassa |

### 3.5 Mammut

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | 120-150 MHz (infobox) / 116-146 MHz (tabella tecnica) | F | [W-Mammut] | media (contraddizione) |
| Potenza | 200 kW (infobox) / 20 kW (tabella): contraddizione di un ordine di grandezza | F | [W-Mammut] | bassa |
| Portata aria | 300 km (infobox e testo) / 325 km (tabella tecnica); bersaglio non qualificato | F | [W-Mammut] | media-bassa |
| Precisione | +-0,5 gradi, risoluzione 300 m | F | [W-Mammut] | media |
| Antenna/mobilita' | schiere fisse 30x16 m (Luftwaffe) / 20x14 m (Marina); fascio a scansione elettronica su un arco di 100 gradi; 6-8 schiere Freya per stazione | F | [W-Mammut] | media |
| Servizio | "1944?"-1945 (informazione di intelligence ancora errata ad aprile 1945) | F | [W-Mammut] | bassa |
| Multi-bersaglio, MTBF/MTTR, messa in opera, numero costruito | non trovato | - | - | - |

### 3.6 Wurzburg (FuMG 62) - limite della categoria

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | 560 MHz (infobox), banda 553-566 MHz | F | [W-Wurz] | media |
| Potenza | 8 kW (infobox) / 7-11 kW (sviluppo) | F | [W-Wurz] | media |
| Portata aria | set base ~29 km massimo; Riese fino a 70 km. Bersaglio non qualificato | F | [W-Wurz] | media |
| Precisione | portata +-15 m (infobox) / ~25 m (testo); azimut ~0,2 gradi, elevazione ~0,3 gradi | F | [W-Wurz] | media (contraddizione 15/25 m) |
| Antenna/mobilita' | parabola da 3 m ripiegabile, rimorchio; Riese da 7,4-7,5 m su rotaia (Riese-E) | F | [W-Wurz] | media |
| Produzione | infobox ~1500; testo ">4000 Wurzburg di vari modelli" (il 1500 riguarda il solo Riese-E) | F | [W-Wurz] | bassa (contraddizione 1500/4000) |
| Multi-bersaglio (inseguimento di un bersaglio per radar), MTBF/MTTR, messa in opera | non trovato | - | - | - |

### 3.7 SCR-270 / SCR-271

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | 106 MHz (~3 m) | F | [W-SCR270] | media-alta |
| Potenza di picco | 100 kW | F | [W-SCR270] | media-alta |
| Portata aria | nominale "150 mi (240 km)"; **singolo bombardiere su sito piano a livello del mare** (tabella SCR-270-D): **32 km a 1000 ft, 80 km a 5000 ft, 160 km a 20 000 ft, 180 km a 25 000 ft**; raid di Pearl Harbor rilevato a 130 mi (210 km) | F | [W-SCR270] | media-alta |
| Precisione | 4 mi (6,4 km), 2 gradi | F | [W-SCR270] | media |
| Antenna/mobilita' | schiera 8x4 (fissa) o 4x8 (mobile) di dipoli, 1 giro/min; versione mobile = 4 veicoli, equipaggio di 9; antenna ripiegabile e alzata a 55 ft; SCR-271 fisso | F | [W-SCR270] | media |
| Messa in opera | non trovato (la fonte non lo dice) | - | - | - |
| Multi-bersaglio, MTBF/MTTR | non trovato | - | - | - |
| Servizio | 1940-1945 (sostituito da unita' a magnetron); utilizzatori: US Army, USMC (Guadalcanal, Bataan, Okinawa) | F | [W-SCR270] | media-alta |

### 3.8 AMES Type 7 (GCI)

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | 209 MHz (1,5 m), poi 193 e 200 MHz | F | [W-T7] | media |
| Potenza | 80-100 kW; con Mk 2/3 fino a 500 kW | F | [W-T7] | media |
| Portata aria | infobox: 220 nmi (410 km) teorici, **~90 mi (140 km) in pratica**; bombardiere: ~16 km a 150 m, 140 km a 6100 m; Mk 4/5 su Meteor NF.11 all'orizzonte ~390 km, a 10 gradi sull'orizzonte ~110 km | F | [W-T7] | media |
| Quota | 24 000 m (80 000 ft) | F | [W-T7] | media |
| Precisione | azimut ~1,5 gradi, quota ~150 m | F | [W-T7] | media |
| Antenna/mobilita' | 32 dipoli (4 file da 8) con riflettore a rete; 0,5-8 giri/min; sito fisso con pozzo radar | F | [W-T7] | media |
| Servizio | 1941; 33 stazioni complete nel 1944; Mk III dal 1955; usato fino a Linesman/Mediator (anni '60) | F | [W-T7] | media |
| Multi-bersaglio, MTBF/MTTR, messa in opera | non trovato | - | - | - |

### 3.9 P-12 "Yenisei" (Spoon Rest A/B)

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | VHF; 150-170 MHz (Spoon Rest B, radartutorial via ricerca); 147-161 MHz (A) e 141-167 MHz (C) secondo [AC-P12] | F | [RT-P12], [AC-P12] | media (bande diverse per variante) |
| Potenza di picco | 180 kW (Wikipedia en/ru); 160-250 kW (radartutorial); 250/350/180-350 kW per variante [AC-P12] | F | | media (contraddizione 160-350 kW) |
| Portata aria | **200 km con quota massima 25 km** (Wikipedia en e ru); 250 km (testo W-P12); 275 km (A, GlobalSecurity/[AC-P12]); 360 km "instrumented range" radartutorial (portata di visualizzazione); Serbia P-12M "estesa a 350 km". Bersaglio non qualificato | F | [W-P12], [WRU-P12], [AC-P12], [RT-P12] | media (200-360 km, bersaglio non qualificato) |
| Quota | 25 km; elevazione massima del lobo 30 gradi; angolo di elevazione 3-14 gradi | F | [WRU-P12] | media |
| Tracciamento | non applicabile (2D di scoperta) | D | [WRU-P12] | media |
| Risoluzione/precisione | 2 km in portata, 11 gradi in azimut | F | [WRU-P12] | media |
| Antenna/mobilita' | 12 Yagi (2x6), un'antenna per Tx e Rx, 10 giri/min (2-6 giri/min secondo [AC-P12]); mobile su 2 camion ZiL | F | [W-P12], [AC-P12] | media (rotazione 2-6 o 10 giri/min) |
| Multi-bersaglio | non trovato | - | - | - |
| MTBF/MTTR | non trovato. **Non attribuire** i 800 h del P-18-2/YLC-8 | - | - | - |
| Messa in opera | non trovato | - | - | - |
| Servizio | 1956 (sviluppo 1954-56), P-12M 1958, P-12MP 1962, P-12NP/NA 1970; utilizzatori: URSS, Egitto, Vietnam, DDR, Iraq, Cecoslovacchia (92 acquistati 1961-65), Serbia... | F | [W-P12], [AC-P12] | media |

### 3.10 P-14 "Lena" (Tall King A/B/C)

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | 171,5 MHz (Wikipedia ru); radartutorial "Tall King A" 150-170 MHz | F | [WRU-P14], [RT-P14] | media (leggera contraddizione 171,5 vs 150-170) |
| Potenza di picco | >=700 kW (ru); 700-900 kW (radartutorial); 900 kW (Wikipedia en, armedconflicts) | F | | media |
| Portata aria | **400 km (infobox Wikipedia en; non qualificato)**; "40-540 km" ([AC-P14], da una tabella di fonte secondaria); radartutorial: portata strumentale 320 NM (D: ~593 km), schermo massimo 600 km. **Portata contro caccia/quota: non trovato** | F | [W-P14], [AC-P14], [RT-P14] | bassa-media (400/540/593 km, tutti non qualificati) |
| Quota | 30 km standard, 65 km con fascio alto (infobox W-P14; l'altro motore attribuisce i 65 km a P-30: possibile confusione) | F | [W-P14], [AC-P14] | bassa-media |
| Precisione | 1,2 km in portata, 1,2 gradi in azimut | F | [W-P14] | media |
| Antenna/mobilita' | parabola troncata a griglia, 32 m x 11 m, un'antenna Tx/Rx; 2-6 giri/min; 1RL113 statico (2 edifici, cabina entro 1 km), 5N84A mobile su 6 rimorchi | F | [W-P14], [WRU-P14] | media |
| Messa in opera | **24 h** (ru), "oltre 24 h per assemblare" (en) per la versione mobile 5N84A | F | [WRU-P14], [W-P14] | media (concordi, non indipendenti) |
| Multi-bersaglio, MTBF/MTTR | non trovato | - | - | - |
| Servizio/produzione | 1959-2003 (ru: 731 costruiti, 24 esportati; en: ~2000 infobox, 731 solo 1RL113); equipaggio 12 | F | [WRU-P14], [W-P14] | media (contraddizione 731/~2000) |

### 3.11 P-18 "Terek" (Spoon Rest D) - scheda con i dati migliori

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | VHF 150-170 MHz | F | [RT-P18] via ricerca | media |
| Potenza di picco | 260 kW (infobox en, non qualificata); 160-260 kW (radartutorial) | F | [W-P18], [RT-P18] | media |
| Portata aria | **contro MiG-21: 60 km a 500 m; 180 km a 10 000 m; 260 km a 20 000-27 000 m** (in presenza di disturbo attivo: 40 / 90 / 170 km). Infobox en: 250 km con quota 35 km; radartutorial: portata strumentale 360 km (display). Notizie belliche: "Su-34NVO rilevato a 180 km" (titolo giornalistico, bassa) | F | [WRU-P18] (principale), [W-P18], [RT-P18] | media-alta per la tabella MiG-21 (concorda con l'infobox su 250 km a quota alta); i 360 km sono di visualizzazione |
| Tracciamento | 10 bersagli (senza elaborazione digitale 7-12 in uscita, dipende dall'operatore); aggiornamento 10-30 s | F | [WRU-P18] | media |
| Multi-bersaglio | **10** (base); P-18-2: 120 | F | [WRU-P18] | media |
| Precisione | portata 1800 m (1400 m dopo ammodernamento); azimut 6 gradi (47' dopo); infobox en 1 km | F | [WRU-P18], [W-P18] | media (1,0 vs 1,8 km) |
| MTBF | **140 h** (P-18 base); 800 h (P-18-2). Un altro estratto russo attribuisce 800 h "alla P-18 derivata da P-12MP": **contraddizione 140/800 h** (probabile confusione di variante) | F | [WRU-P18], [WRU-P12 search] | media-bassa |
| MTTR | non trovato | - | - | - |
| Antenna/mobilita' | 16 Yagi (2x8), Tx/Rx, 10 giri/min, elevazione -5/+15 gradi; 2 camion Ural-4320 | F | [W-P18] | media |
| Messa in opera | **45 min** (90 min dopo ammodernamento, ru); radartutorial pl/ru 45 min; P-18-2 "5 min" ([W-P18] via ricerca) | F | [WRU-P18], [RT-P18] | media-alta per i 45 min |
| Equipaggio/consumo | 7 persone (4 dopo), 10 kW | F | [WRU-P18] | media |
| Servizio | 1970 (en) / 3 nov 1971 (ru); sostituito dall'1L13 nel 1984 (en); ancora in uso | F | [W-P18], [WRU-P18] | media (1970 vs 1971) |

### 3.12 P-15 "Tropa" (Flat Face A) / P-19 "Danube" (Flat Face B)

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | P-15: UHF, 4 frequenze preselezionate; P-19: 830-875 MHz | F | [W-P15], [W-P19] | media |
| Potenza | P-15: 270 kW (non qualificata); P-19: 900 kW (non qualificata) | F | [W-P15], [W-P19] | bassa-media |
| Portata aria | P-15: 150 km con quota 3 km (infobox, non unito a bersaglio); banca dati CMANO (gioco): caccia ~70 km a 300 m, ~140 km a 3000 m, 210-250 km a 10 000 m; GlobalSecurity (snippet): 200-250 km e 70 km a 300 m. P-19: 260 km (infobox, non qualificato) | F | [W-P15], [W-P19], [CMANO-P15] (bassa), [GS-FF] (snippet) | bassa (fonti deboli o non qualificate; il profilo per quota viene dal gioco) |
| Precisione | P-15: 0,3 km in portata | F | [W-P15] | media-bassa |
| Antenna/mobilita' | 2 antenne ellittiche aperte (Tx e Rx), 360 gradi; ZIL-157 (P-15), ZIL-131 (P-19); quota con altimetro PRV-11 | F | [W-P15], [W-P19] | media |
| Messa in opera | **P-15: fino a 10 min per montare/smontare**; P-19: non trovato | F | [W-P15] | media-bassa |
| Multi-bersaglio, MTBF/MTTR | non trovato | - | - | - |
| Servizio | P-15 sviluppo 1952, in servizio 1955; P-19 1974 (il file DCS locale indica "P-19 Flat Face 1961", anno dell'SA-3: **contraddizione**) | F | [W-P15], [W-P19], file DCS | media |

### 3.13 P-35 "Saturn" / P-37 "Mech" (Bar Lock)

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | P-37: 2695-3115 MHz (radartutorial), 2700-3100 MHz (Wikipedia ru); P-35: 2700-3100 MHz | F | [RT-P37], [WRU-P37], [WRU-P35] | alta (concordi) |
| Potenza | 5x700 kW di picco (radartutorial); 700 kW per i trasmettitori 1,2,3,5 e 600 kW per il 4 (ru); infobox P-35 "6x1 MW" (non qualificata) | F | | media (contraddizione 5x700 kW vs 6x1 MW) |
| Portata aria | **P-37: bombardiere 350 km, caccia 280 km, missile da crociera 235 km** (Wikipedia ru; quota non indicata); radartutorial: portata strumentale 450 km (500 km nella scheda francese); P-35: 350 km (infobox en/ru); P-37 per quota bassa 50-300 m solo in zona vicina; S-200 article: 392 km | F | [WRU-P37], [WRU-P35], [RT-P37], [W-P35] | media (la tabella per tipo di bersaglio e' utile, la quota manca) |
| Quota | P-35: 25 km (infobox en) vs "altezza di scansione 85 000 m" (ru) - **contraddizione** | F | [W-P35], [WRU-P35] | bassa |
| Tracciamento/Multi-bersaglio | 2D, nessun tracking; quota tramite PRV-11/PRV-13: non trovato il numero di bersagli | - | | - |
| Precisione | 0,5 gradi e 500 m a 100 km (P-37, ru); 300 m (radartutorial de) | F | [WRU-P37], [RT-P37] | media (500 vs 300 m) |
| Antenna/mobilita' | 2 antenne a griglia troncata (6 corni di alimentazione), 6 canali, 3-6 giri/min (P-37) / 6-7 giri/min (P-35); fascio 0,7 gradi (P-35) / 2 gradi (P-37); semi-mobile (rimorchio + camion) | F | | media |
| Messa in opera | **P-35: 12 h (equipaggio addestrato, ru); P-37: "24 in estate, 36 in inverno" (la fonte scrive 'ч', ore)** | F | [WRU-P35], [WRU-P37] | media-bassa (unita' non esplicita, p. es. ore o altro) |
| Multi-bersaglio | non trovato | - | - | - |
| MTBF/MTTR | non trovato (radartutorial lascia vuoti MTBCF e MTTR) | - | [RT-P37] | - |
| Servizio | P-35 1958; P-35M 1961; P-37 1961; versione "90" a stato solido in ricezione | F | | media |

### 3.14 1L13 "Nebo-SV" (Box Spring) - unita' EWR di DCS

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | VHF 180-220 MHz (radartutorial via ricerca), polarizzazione verticale | F | [RT-1L13], [APA-Nebo] | media |
| Potenza di picco | >=140 kW (tab.) / 120-140 kW (testo) | F | [APA-Nebo] | media |
| Portata aria | **caccia: >=50 km a 500 m; >=250 km a 10 000 m; >=330 km a 27 000 m** ([APA-Nebo], valori "non inferiori a"). Fonti secondarie (Defense Express, ripresa da armedconflicts): 60 km a 500 m, 350 km a 27 km - **contraddizione** (50/60 km e 330/350 km). Radartutorial: portata strumentale 360 km | F | [APA-Nebo] (principale), [AC-Nebo] | media (APA analisi tecnica; contraddizione con la fonte giornalistica) |
| Quota | max 40 km; elevazione max 30 gradi | F | [APA-Nebo] | media |
| Tracciamento | 2D (richiede radioaltimetro separato); aggiornamento 10/20 s | F | [APA-Nebo] | media |
| Precisione | portata <=400 m; azimut <=0,67 gradi | F | [APA-Nebo] | media |
| Multi-bersaglio | non trovato per l'1L13 (la variante 1L119 SVU: 100 bersagli - **non trasferire**) | - | - | - |
| MTBF/MTTR | non trovato per l'1L13; SVU: MTBF >=500 h e MTTR 0,5 h ([APA-Nebo]) come confronto, **variante successiva** | - | - | - |
| Antenna/mobilita' | 72 Yagi in 4 file (6 sottoschiere da 12), fascio 6 gradi, 3-6 giri/min; 3 camion Ural e rimorchio; massa 48 t | F | [APA-Nebo], [BigEnc] | media |
| Messa in opera | **40 min** (APA); SVU: 20 min | F | [APA-Nebo] | media |
| Servizio | sviluppato 1982 (ruota il P-18); consegnato alle truppe ~1990 (radartutorial de) | F | [RT-1L13], [WEN-Rus] | media-bassa (date poco chiare) |

### 3.15 55Zh6 "Nebo" / 55Zh6U "Nebo-U" (Tall Rack) - "55G6 EWR" di DCS

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | VHF; 13 frequenze (radartutorial de via ricerca) | F | [RT-Nebo-U] | media-bassa |
| Potenza | 500 kW di picco, 5 kW medi (radartutorial de via ricerca) | F | [RT-Nebo-U] | media-bassa |
| Portata aria | **caccia di 4a gen.: ~400 km a 20 km di quota; ~65 km a 500 m** (Defense Express riportato da [AC-Nebo]); 600 km per bersaglio a 75 000 m; ~360 km per bersagli fino a 40 000 m; radartutorial: portata strumentale 700 km | F | [AC-Nebo], [RT-Nebo-U] | media-bassa (fonte giornalistica ucraina di seconda mano; manca il dato a 10 km) |
| Quota | copertura fino a 75 km (radartutorial); Nebo-UM 80 km | F | | media-bassa |
| Tracciamento | 3D (misura portata, azimut, elevazione); STAP contro disturbo attivo | F | [RT-Nebo-U] | media-bassa |
| Precisione | 500 m e 0,4 gradi | F | [RT-Nebo-U] | media-bassa |
| Multi-bersaglio | non trovato | - | - | - |
| MTBF/MTTR | **MTBCF > 250 h** (radartutorial de via ricerca); MTTR non trovato. (Nebo-M: 1000 h - variante diversa, non trasferire) | F | [RT-Nebo-U] | media-bassa |
| Antenna/mobilita' | 7 rimorchi (55Zh6); array a fasi, 6 giri/min; "semi-mobile" 3D | F | [AC-Nebo], [APA-Nebo] | media-bassa |
| Messa in opera | non trovato (Nebo-M: 15 min - non trasferire) | - | - | - |
| Servizio | 55Zh6 sviluppato 1982-87, in servizio 1986; Nebo-U sviluppato 1986-92, in servizio 1995 (ma forniture dal 2006: 17 stazioni 2006-11) | F | [AC-Nebo], [Espreso] | media (nota: Nebo-U e' in gran parte post-Guerra Fredda) |

### 3.16 AMES Type 80 (Green Garlic)

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | banda S 2850-3050 MHz | F | [W-T80] | media-alta (concordi con altre schede) |
| Potenza di picco | 1 MW (Mk I-II), 2,5 MW (Mk III) infobox; il testo cita una magnetron da 2 MW nel Mk III; radarpages: 2 MW (Mk1, allarme) / 1 MW (controllo) | F | [W-T80], [radarpages-T80] | media (contraddizione 1/2/2,5 MW) |
| Portata aria | infobox: **migliore di 240 nmi (440 km)**; testo: un caccia grande o bombardiere piccolo "rilevato affidabilmente oltre 210 nmi (390 km)"; aerei alti e grandi fino all'orizzonte; (Green Garlic sperimentale: Canberra a 45 000 ft 230-250 nmi) | F | [W-T80] | media |
| Quota | visibile oltre ~22 000 ft (6700 m) alla portata nominale, con quota massima di progetto 60 000 ft | D | [W-T80] | media |
| Precisione | 1 miglio a 150 nmi; separa bersagli vicini a 95 nmi | F | [W-T80] | media |
| Antenna/mobilita' | riflettore semi-parabolico 75x25 ft (22,9x7,6 m), 4 giri/min (fino a 6), fascio 1/3 grado, elevazione 0-30 gradi, torre piramidale 25 ft; fisso | F | [W-T80] | media |
| Messa in opera | non applicabile (fisso; prima installazione richiese la gran parte del 1954) | F | [W-T80] | media |
| Servizio | 1953 installazione / 1955 operativo - ultimo sito (RAF Buchan) chiuso 1993; ~35 costruiti; Svezia PS-08 1957-79 | F | [W-T80] | media-alta |
| Multi-bersaglio, MTBF/MTTR | non trovato | - | - | - |

### 3.17 AN/FPS-20

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | banda L 1250-1350 MHz | F | [W-FPS20], [CMANO-FPS20] | media-alta |
| Potenza di picco | 750 kW x2 (Wikipedia, due magnetron 5J26); >=2 MW (MIL-HDBK-162A, klystron, via ricerca); 2,5 MW (CMANO) | F | | bassa (contraddizione 0,75/1,5/2/2,5 MW; la fonte della ricerca avverte che alcune sintesi ripetono i valori dell'FPS-3) |
| Portata aria | 220 nmi (~407 km) (FortWiki via ricerca); 322 km (CMANO, banca dati di gioco). Bersaglio non qualificato | F | [FortWiki-FPS20], [CMANO-FPS20] | bassa (contraddizione 322/407 km, ambedue non qualificate) |
| Quota | limite FPS-3 ~55 000 ft (17 km), con GPA-27 65 000 ft (20 km) | F | [W-FPS20] | media |
| Antenna/mobilita' | antenna a striscia, 3,3/5/10 giri/min (normale 5); sito fisso (variante mobile = AN/MPS-7 per l'FPS-3) | F | [W-FPS20] | media |
| Servizio | FPS-3 dal dicembre 1950; FPS-20 dal 1956/57; sostituiti a fine anni '60; >200 FPS-20 | F | [W-FPS20] | media |
| Multi-bersaglio, MTBF/MTTR, messa in opera | non trovato | - | - | - |

### 3.18 AN/TPS-43

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | banda S 2,9-3,1 GHz | F | [W-TPS43] | media |
| Potenza di picco | 4,0 MW (Wikipedia, 4 MW picco/6,7 kW medi CMANO); 2,8 MW (FortWiki) | F | [W-TPS43], [CMANO-TPS43], [FortWiki] | media-bassa (4,0 vs 2,8 MW) |
| Portata aria | **massimo 240 nmi (440 km)**, display 450 km (Wikipedia; non qualificato); CMANO (banca dati, bersaglio 2 m2 con Pd 80%): 300 km a 100 m, 408 km a 18 000 m (TPS-43E) | F | [W-TPS43], [CMANO-TPS43] | media per il massimo, bassa per i dati per quota |
| Quota | fascio impilato: 6 fasci su 20 gradi, apertura verticale 1,5-8,1 gradi; max quota non trovata | F | [W-TPS43] | media |
| Antenna/mobilita' | riflettore 1,3x6,1 m, fascio orizzontale 1,1 gradi, 6 giri/min; 3D; trasportabile (due camion M35 / due pallet aerei; <3400 kg con shelter) | F | [W-TPS43] | media |
| Messa in opera | non trovato | - | - | - |
| Multi-bersaglio, MTBF/MTTR | non trovato | - | - | - |
| Servizio | sviluppo completato 1963; servizio USA 1968 (citation needed) | F | [W-TPS43] | bassa |

### 3.19 AN/FPS-117 (Seek Igloo)

| Dato | Valore | T | Fonte | Conf. |
|---|---|---|---|---|
| Frequenza | banda L 1215-1400 MHz, salto casuale su 18 canali | F | [Lockheed-FPS117], [W-FPS117] | alta |
| Potenza | non verificata (la pagina Wikipedia recuperata mescola le caratteristiche di TPS-59/FPS-117: 24,6 kW, 44x32 elementi non attribuibili con certezza all'FPS-117) | - | [W-FPS117] | - |
| Portata aria | scheda Lockheed (via riassunto di ricerca): **portata strumentale 10-470 km (5-250 nmi); rilevamento con Pd 80% di un bersaglio da 1 m2 a 330 km**; copertura in quota 0-30,5 km; elevazione da -6 a +20 gradi; 360 gradi | F | [Lockheed-FPS117] (costruttore) | media-alta (fonte primaria del costruttore, letta tramite snippet; quota del bersaglio per i 330 km non specificata) |
| Multi-bersaglio | non trovato | - | - | - |
| MTBF/MTTR | **MTBF critico >2000 h, MTTR <45 min, disponibilita' 99,5%** | F | [Lockheed-FPS117], [EverythingRF] | media-alta |
| Antenna/mobilita' | array planare a stato solido (trasportabile/minimally attended); trasportabilita' del TPS-77 da un prime mover | F | [W-FPS117] | bassa-media |
| Messa in opera | non trovato | - | - | - |
| Servizio | prodotto dal 1980; accettazione finale Seek Igloo 30 set 1983; >120 prodotti; operatori: 15 (testo) vs 30 (elenco) della pagina, contraddizione | F | [W-FPS117] | media |

## 4. Tabella riassuntiva e proposta di compilazione dello schema

Le colonne "Proposta" sono **mie scelte (S)**, non dati: convertono i dati di sez. 3 nello schema. La regola
adottata e' quella piu' difendibile con la lettura del codice: `acquisition_range` = portata contro un caccia
(RCS ~1-5 m2) a quota di crociera (~10 000 m) quando una fonte la da'; altrimenti la migliore stima non
qualificata, **marcata come tale**. La scelta della quota di riferimento va confermata dall'utente (v. sez. 5).

| Radar | acquisition_range proposta (km) | Base del numero | Quota/bersaglio | Conf. | tracking | multi-target | mtbf / mttr (h) |
|---|---|---|---|---|---|---|---|
| Chain Home | 160 (alternativa 190) | infobox/testo W-CH | bombardieri, alta quota | media | 0 (S) | non trovato | non trovato |
| CHL | non trovato (vincolo: quota >=150 m) | - | - | - | 0 (S) | non trovato | non trovato |
| Freya | 120 (alt. 160) | W-Freya | bombardieri, quota non qualificata | media | 0 (S) | non trovato | non trovato |
| Wassermann | 190 (alt. 300 massimo) | tabella tecnica W-Wass | 6000 m | media | 0 (S) | non trovato | non trovato |
| Mammut | 300 (alt. 325) | W-Mammut | non qualificato | media-bassa | 0 (S) | non trovato | non trovato |
| Wurzburg | 29 (Riese 70) | W-Wurz | non qualificato | media | - | non trovato | non trovato |
| SCR-270 | 160 | tabella SCR-270-D | bombardiere a 20 000 ft | media-alta | 0 (S) | non trovato | non trovato |
| Type 7 | 140 | W-T7 "in pratica" | bombardiere a 20 000 ft (6100 m) | media | 0 (S) | non trovato | non trovato |
| P-12 | 200 | W-P12/WRU-P12 | quota max 25 km, non qualificato | media | 0 (S) | non trovato | non trovato |
| P-14 | 400 (non qualificato) | W-P14 infobox | non qualificato | bassa-media | 0 (S) | non trovato | non trovato |
| P-18 | 180 | WRU-P18 | MiG-21 a 10 000 m | media-alta | 0 (S) | 10 | 140 / non trovato |
| P-15 | 150 (alt. 140 a 3000 m dal gioco; non usare senza conferma) | W-P15 | quota 3 km, non qualificato | bassa | 0 (S) | non trovato | non trovato |
| P-19 | 260 | W-P19 | non qualificato | bassa | 0 (S) | non trovato | non trovato |
| P-35 | 350 | W-P35/WRU-P35 | non qualificato | media | 0 (S) | non trovato | non trovato |
| P-37 | 280 | WRU-P37 | caccia, quota non indicata | media | 0 (S) | non trovato | non trovato |
| 1L13 | 250 | APA-Nebo | caccia a 10 000 m, ">=" | media | 0 (S) | non trovato | non trovato |
| 55G6/Nebo | 400 (a 20 km); non trovato a 10 km | AC-Nebo/Defense Express | caccia a 20 000 m | media-bassa | 0 (S) | non trovato | >250 / non trovato |
| Type 80 | 390 (alt. 440) | W-T80 | caccia grande/bombardiere piccolo, quota alta | media | 0 (S) | non trovato | non trovato |
| FPS-20 | 322 o 407 (contraddizione) | CMANO / FortWiki | non qualificato | bassa | 0 (S) | non trovato | non trovato |
| TPS-43 | 300 a 100 m; 408 a 18 000 m (gioco) o 440 massimo | W-TPS43/CMANO | 2 m2, Pd 80% (CMANO) | bassa-media | 0 (S) | non trovato | non trovato |
| FPS-117 | 330 | Lockheed | 1 m2, Pd 80% | media-alta | 0 (S) | non trovato | >2000 / <0,75 (45 min) |

Nota sul MTTR dell'FPS-117: la fonte dice "MTTR < 45 minuti"; 0,75 h e' una conversione (D), non un dato misurato.

## 5. Dubbi e decisioni per l'utente

### 5.1 Non risolvibile col web (da dichiarare come tale in registro)
1. **Multi-target capacity** e' quasi sempre "non trovato". Le uniche eccezioni sono il P-18 (10; variante P-18-2: 120)
   e le varianti moderne (Nebo-SVU: 100, fuori periodo). Per i radar WWII a lettura manuale (CH, CHL, Freya,
   Wassermann, SCR-270, Type 7) non esiste un numero: il concetto di "capacita' multi-bersaglio" e' definito dalla
   risoluzione dell'operatore, non da un parametro. Ogni valore sarebbe una STIMA.
2. **MTBF/MTTR**: trovati solo per P-18 (MTBF 140 h; 800 h nel P-18-2), Nebo-U (MTBCF >250 h, bassa), FPS-117 (MTBF
   >2000 h, MTTR <45 min). Per tutti gli altri servirebbero manuali tecnici d'epoca non reperibili online. I
   registri esistenti usano valori generici (es. 45/4) per i radar: va deciso se applicare un valore generico
   per categoria o lasciare "non disponibile".
3. **Portata per quota/RCS**: per la quasi totalita' dei radar non c'e' una curva portata-quota con RCS
   dichiarato. Vera eccezione: P-18 (MiG-21: 60/180/260 km), 1L13 (50/250/330 km), SCR-270 (tabella per quota),
   Wassermann (35 e 190 km), Type 7 (16 e 140 km). Per gli altri il numero e' "massimo" non qualificato.
4. **Messa in opera** e' un dato di aggiornamento strategico rilevante (24 h P-14, 12 h P-35, 24-36 h P-37,
   40 min 1L13, 45 min P-18, 10 min P-15) ma le unita' dei dati P-35/P-37 non sono esplicite (le fonti ru scrivono
   "ч", ore: verificare).
5. Contraddizioni irrisolte con fonti equivalenti: potenza di picco CH (200/350/750 kW), potenza Mammut (20 vs
   200 kW), P-12 (180-350 kW), portata P-14 (400/540/593 km), portata FPS-20 (322/407 km), TPS-43 (2,8 vs 4 MW),
   MTBF P-18 (140 vs 800 h), 1L13 (50-60 km a 500 m e 330-350 km a 27 km), quota P-35 (25 km vs 85 km). Servono
   fonti primarie per chiuderle.
6. La **categoria EWR in DCS** (1L13, 55G6) e l'assenza di EWR occidentali sono confermate solo da snippet di
   forum: da verificare in DCS o sulla wiki Hoggit.

### 5.2 Scelte di design che emergono
1. **Mappatura di `acquisition_range`.** Il codice lo usa come R unica della Pd e come raggio del cilindro (poi
   tagliato dall'orizzonte). Un EWR reale ha portata che dipende dalla quota (P-18: 60 km a 500 m, 180 km a 10
   km, 260 km a 27 km). Opzioni: (a) un solo valore a quota di crociera (~10 000 m) e lasciare che l'orizzonte
   faccia il resto (come proposto in sez. 4); (b) un valore piu' conservativo (media tra le quote, p. es. tra 60 e
   180 km = D); (c) estendere lo schema con una curva portata-quota (cambio al core, Proposta a parte).
   **Raccomando (a) con dichiarazione esplicita della quota**; ma la R e' anche la R della legge Pd, quindi
   scegliere la portata massima sovrastima la Pd a bassa quota, e la portata a bassa quota la sottostima in alto.
2. **`engagement_range`**: gli EWR non hanno armi: 0 e' coerente, ma va verificato che il core non tratti
   `engagement_range` = 0 come "radar non utilizzabile" (ho letto solo `acquisition_range` in
   `Air_Route_Manager`, non il resto).
3. **`tracking_range`**: un EWR non traccia per il tiro. Opzioni: 0 (nessun tracciamento) oppure uguale a
   `acquisition_range` (come "traccia continua per cedere il bersaglio al SAM"). Questa scelta incide su come il
   futuro "sensore di rete" (non esiste ancora nel DES, v. `Proposta_Volumi_Rilevamento_Intercettazione.md`)
   passerebbe i dati fra siti. Da decidere con quella Proposta.
4. **Radar WWII a lettura manuale con tempi lunghi**: il core non modella un tempo di acquisizione/riconoscimento
   (c'e' il `reaction_time` delle minacce AA). Per CH/Freya/SCR-270 la latenza di plotting (minuti dal rilevamento
   al dato utile) e' parte del sistema ma non c'e' un dato numerico trovato. Opzione: ignorarla (EWR "istantaneo"),
   oppure introdurre un campo tempo di acquisizione per radar WWII (non nello schema attuale).
5. **Fissi, trasportabili, mobili**: il registro e' di veicoli (`Ground_Vehicle`). CH, CHL, Wassermann, Mammut,
   Type 7, Type 80, FPS-20 sono installazioni fisse (centinaia di tonnellate o torri da 110 m); P-14 richiede 24 h
   di montaggio; modellarli come "veicoli" richiede decidere se esistono come asset fissi senza `speed_data`
   (come gli SAM statici, se presenti) o se escluderli. **Candidati naturali come veicolo**: P-12, P-18, P-15/P-19,
   1L13, FPS-117/TPS-43 (trasportabili), SCR-270 (mobile). Da decidere quali includere nel registro.
6. **Quali includere**: scegliendo con il criterio "utile al DES + dati disponibili", i piu' solidi sono P-18,
   1L13, SCR-270, Type 7, Type 80, P-37, FPS-117, TPS-43; i piu' deboli (dati contraddittori) sono Mammut, Freya,
   FPS-20, P-14, P-15/P-19, CHL (portata non trovata). Suggerisco di includere almeno le due unita' DCS (1L13 e
   55G6) piu' un campione per blocco/epoca, e di lasciare i radar "limite" (Wurzburg) fuori finche' non si decide
   se la categoria EWR comprende i radar GCI.
7. **Periodo e anni di servizio**: Nebo-U/Nebo-SV entrano in servizio nel 1986-1995, ai margini o oltre la
   fine della Guerra Fredda (1991); il 55G6 di DCS e' pero' la scelta naturale per la fazione russa moderna.
   Va deciso se il registro e' limitato al 1991 o include i radar DCS indipendentemente dalla data.
8. **Unita' del codice**: il registro usa km per queste portate (`acquisition_range` in km nello schema, ma
   `DetectionThreat` in metri): verificare la conversione in `Mobile.detection_range`.

## 6. Fonti (abbreviazioni usate sopra)

Enciclopediche/tecniche (letti via strumento di fetch, quindi a seconda mano):
- [W-CH] https://en.wikipedia.org/wiki/Chain_Home ; [BoB] https://battleofbritain1940.com/chain-home/ (via ricerca) ; [GEC85] https://www.hellschreiber.com/pdf-hell/article-CH-GEC-85.pdf (via ricerca) ; [radarpages] https://www.radarpages.co.uk/mob/ch/chainhome.htm
- [W-CHL] https://en.wikipedia.org/wiki/Chain_Home_Low
- [W-Freya] https://en.wikipedia.org/wiki/Freya_radar ; [W-Wass] https://en.wikipedia.org/wiki/Wassermann_radar ; [RT-Wass] https://www.radartutorial.eu/19.kartei/11.ancient/karte007.en.html (via ricerca) ; [W-Mammut] https://en.wikipedia.org/wiki/Mammut_radar ; [W-Wurz] https://en.wikipedia.org/wiki/W%C3%BCrzburg_radar
- [W-SCR270] https://en.wikipedia.org/wiki/SCR-270 ; [W-T7] https://en.wikipedia.org/wiki/AMES_Type_7 ; [W-T80] https://en.wikipedia.org/wiki/AMES_Type_80 ; [radarpages-T80] https://radarpages.co.uk/mob/mrs/type80.htm (via ricerca)
- [W-P12] https://en.wikipedia.org/wiki/P-12_radar ; [WRU-P12] https://ru.wikipedia.org/wiki/%D0%9F-12 ; [AC-P12] https://www.armedconflicts.com/topic/view/37623 ; [RT-P12] https://www.radartutorial.eu/19.kartei/11.ancient/karte046.de.html (via ricerca)
- [W-P14] https://en.wikipedia.org/wiki/P-14_radar ; [WRU-P14] https://ru.wikipedia.org/wiki/%D0%9F-14 ; [AC-P14] https://www.armedconflicts.com/-t51939 ; [RT-P14] https://www.radartutorial.eu/19.kartei/11.ancient/karte047.en.html (via ricerca)
- [W-P18] https://en.wikipedia.org/wiki/P-18_radar ; [WRU-P18] https://ru.wikipedia.org/wiki/%D0%9F-18 ; [RT-P18] https://www.radartutorial.eu/19.kartei/11.ancient/karte049.en.html (via ricerca)
- [W-P15] https://en.wikipedia.org/wiki/P-15_radar ; [W-P19] https://en.wikipedia.org/wiki/P-19_radar ; [CMANO-P15] https://cmano-db.com/facility/172/ ; [GS-FF] https://www.globalsecurity.org/military/world/russia/flat-face.htm (snippet; pagina non leggibile)
- [W-P35] https://en.wikipedia.org/wiki/P-35_radar ; [WRU-P35] https://ru.wikipedia.org/wiki/%D0%9F-35_%C2%AB%D0%A1%D0%B0%D1%82%D1%83%D1%80%D0%BD%C2%BB ; [WRU-P37] https://ru.wikipedia.org/wiki/%D0%9F-37 ; [RT-P37] https://www.radartutorial.eu/19.kartei/11.ancient/karte051.en.html (via ricerca)
- [APA-Nebo] https://www.ausairpower.net/APA-Nebo-SVU-Analysis.html (analisi di Carlo Kopp/APA: fonte tecnica, ma autore "stima" alcuni valori) ; [AC-Nebo] https://www.armedconflicts.com/topic/view/82950 ; [RT-1L13] https://www.radartutorial.eu/19.kartei/11.ancient3/karte071.en.html (via ricerca) ; [RT-Nebo-U] https://www.radartutorial.eu/19.kartei/02.surv/karte039.de.html (via ricerca) ; [BigEnc] https://bigenc.ru/c/nebo-sv-8bc237 (non leggibile, solo snippet) ; [Espreso] https://espreso.tv/ (snippet, giornalistica)
- [W-FPS20] https://en.wikipedia.org/wiki/AN/FPS-20_Early_Warning_Radar ; [CMANO-FPS20] https://cmano-db.com/facility/573/ ; [FortWiki-FPS20] https://fortwiki.com/FPS-20 (non leggibile, solo snippet)
- [W-TPS43] https://en.wikipedia.org/wiki/AN/TPS-43 ; [CMANO-TPS43] https://cmano-db.com/facility/620/ ; [FortWiki] https://fortwiki.com/TPS-43 (snippet)
- [W-FPS117] https://en.wikipedia.org/wiki/AN/FPS-117 ; [Lockheed-FPS117] https://sustainability.lockheedmartin.com/content/dam/lockheed-martin/rms/documents/ground-based-air-surveillance-radars/FPS-117-fact-sheet.pdf (PDF non leggibile direttamente: dati dal riassunto del motore di ricerca) ; [EverythingRF] https://www.everythingrf.com/products/radar-systems/lockheed-martin/1069-1512-an-fps-117
- Per l'elenco DCS: https://forum.dcs.world/topic/230793-westernus-ground-ewr-systems/ ; https://forum.dcs.world/topic/108775-radar-support-questions ; https://forum.dcs.world/topic/308227-can-i-dectect-ewr-radar-with-hts/
- Altre menzioni: https://en.wikipedia.org/wiki/SCR-584_radar ; https://en.wikipedia.org/wiki/P-40_radar ; https://en.wikipedia.org/wiki/Russian_air_surveillance_radars

**Fonti piu' deboli usate**: forum DCS (solo per l'esistenza delle unita' EWR in DCS), cmano-db.com (banca dati di un wargame:
profili per quota di P-15, FPS-20, TPS-43), armedconflicts.com (portale divulgativo: P-12, P-14, 55Zh6, 1L13), snippet
giornalistici ucraini (Defense Express, Espreso, Militarnyi) per le portate del 55Zh6/Nebo-U e delle perdite,
Wikipedia (infobox senza qualifica del bersaglio) e riassunti del motore di ricerca per radartutorial.eu e per la scheda
Lockheed dell'FPS-117.
