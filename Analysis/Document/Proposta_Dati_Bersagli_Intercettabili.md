# Proposta dati: classe e rilevabilità dei 52 missili `MISSILES_ASM` (blocco 0 della BI)

**Stato**: **DECISO dall'utente il 2026-11-07** (D1-D6 in §9, zona grigia approvata voce per voce in §6): D1 = (b)
R1-K (metro del Maverick sull'inviluppo della famiglia: diametro ≤ 304,8 mm **e** massa ≤ 304 kg, lunghezza esclusa),
D2 (a), D3.1 (a), D3.2 (a), D3.3 (a), D4.1 (a), D4.2 (a), D5 (b) (ricerca mirata M1 eseguita, §2.4), D6 (a). Valori
definitivi per il blocco 1 in §10.2. Nessun file di codice o di test modificato; scritto solo questo documento.
**Contesto**: `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (BI, "bersagli intercettabili"), decisioni BI-1..BI-12
tutte prese il 2026-11-07. Questo documento è il prodotto del **blocco 0** (BI §5.1, `:875-906`): per ognuna delle 52
voci dà la classe di munizione, il flag `ad_detectable` e le dimensioni di supporto, con fonte, confidenza e livello di
verifica. Il **blocco 1** (BI §5.2, `:908-949`) le scrive nei registri.
**Esecutore del blocco 1**: `des-developer` o `oc-developer`, seguendo §10 di questo documento e §5.2 della BI.

**Convenzioni**:
- **[V]** = verificato nel repository (lettura del codice con `file:riga`, o esecuzione in sola lettura dei registri il
  2026-11-07 sul ProArt, checkout `analysis/dce-dcs-persistence` a `81f92846`);
- **[I]** = ipotesi o conoscenza generale, non verificata né nel repository né su una fonte in questa sessione;
- **[S]** = stima o scelta di progetto, mai dato tarato.
- **Livello di verifica dei dati esterni**: **principale** = il valore è stato letto dalla sessione principale sul
  testo letterale della pagina il 2026-11-07; **principale parz.** = solo alcuni valori della voce (indicati);
  **agente** = valore riportato solo da `oc-researcher`, con estratto e URL, non ricontrollato. Questo documento è
  scritto **senza accesso al web**: nessun valore esterno è stato riletto da chi scrive (i valori "principale" sono
  quelli che la sessione principale ha dichiarato riletti, nel §2.3 e nel compito di aggiornamento del 2026-11-07).
- **Confidenza** (stessa scala di `Proposta_Dati_Anti_Missile.md`): **A** = fonte primaria o due fonti concordi;
  **M** = una fonte secondaria, o fonti discordi; **B** = stima, analogia o designazione incerta. Dove ho corretto la
  confidenza dell'agente lo scrivo ("rivista").
- Percorsi di codice relativi a `Code/Dynamic_War_Manager/Source/`; percorsi delle bozze relativi a
  `Analysis/Document/Bozze/`.

## Glossario delle sigle

| Sigla | Significato |
|---|---|
| AD | *Air Defence*, difesa aerea (SAM, AAA, CIWS) |
| SAM / AAA | *Surface-to-Air Missile*, missile superficie-aria / *Anti-Aircraft Artillery*, cannoni contraerei |
| CIWS | *Close-In Weapon System*, cannone navale antimissile (Phalanx, AK-630) |
| ASM / AAM | *Air-to-Surface Missile*, missile aria-superficie / *Air-to-Air Missile*, missile aria-aria |
| A2G / A2S | aria-suolo / aria-nave |
| ARM | *Anti-Radiation Missile*, missile antiradar (AGM-88, Kh-58) |
| ATGM | *Anti-Tank Guided Missile*, missile controcarro (Hellfire, TOW) |
| MANPADS | *Man-Portable Air-Defence System*, SAM portatile (Mistral, Stinger) |
| ALCM / LACM | *Air-Launched Cruise Missile*, cruise aviolanciato / *Land-Attack Cruise Missile*, cruise da attacco al suolo |
| RCS | *Radar Cross Section*, superficie equivalente radar [m²] |
| IIR / CCD | *Imaging Infrared*, sensore all'infrarosso a immagine / *Charge-Coupled Device*, telecamera a stato solido |
| MCLOS / SACLOS | guida manuale / semiautomatica "sulla linea di mira" (comando a vista) |
| ARH | *Active Radar Homing*, autoguida radar attiva |
| SRM | *Solid Rocket Motor*, motore a propellente solido (qui: il booster di lancio) |
| VLS | *Vertical Launching System*, lanciatore verticale navale |
| FAS | *Federation of American Scientists* (schede `man.fas.org`) |
| CSIS | *Center for Strategic and International Studies* (sito Missile Threat) |
| d-s | `designation-systems.net` (Andreas Parsch, schede dei missili USA) |
| KTRV | *Korporatsiya Takticheskoye Raketnoye Vooruzhenie*, Tactical Missiles Corporation (costruttore russo) |
| AEF | sito "Flygvapnets historia" (`aef.se`), storia dell'aeronautica svedese, fonte per l'Rb 05 |
| CMANO | *Command: Modern Air Naval Operations*, banca dati di un simulatore (`cmano-db.com`), fonte secondaria |
| L1..L7 / M1 | i sette lotti della prima ricerca (`Ricerca_Dati_Bersagli_L<n>_oc-researcher.md`) e la ricerca mirata del 2026-11-07 (`Ricerca_Dati_Bersagli_M1_oc-researcher.md`, decisione D5); da non confondere con il punto "M1" del rapporto di revisione della BI (Kh-22N, D3.1) |
| R1-D / R1-K / R1-Ø | le tre varianti della regola (1) del metro del Maverick discusse in D1 (§5): sull'AGM-65D, sull'inviluppo della famiglia Maverick (**scelta**), sul solo diametro |
| F! / T! / ZG | esito del metro: False obbligatorio / True obbligatorio / zona grigia approvata dall'utente voce per voce |
| BI | `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` |
| DES | *Discrete Event Simulation*, il motore delle sessioni virtuali |

**Ruoli** (usati nelle tabelle delle decisioni, come nella BI): **lanciatore** = chi spara; **colpo** = il missile in
volo; **bersaglio dell'attacco** = l'unità colpita; **intercettore** = l'asset AD (con un'arma `Anti_Missile`, regola
D) che può fermare il colpo; **osservatore** = chi rileva (per l'intercettazione è l'intercettore); **bersaglio del
rilevamento** = il lanciatore o il colpo.

---

## 1. Sintesi e stato

**Il problema**. La regola dell'utente del 2026-11-07 (BI, `:27-42`) ammette come bersaglio di una difesa aerea solo i
missili cruise/balistici o di dimensione rilevabile. La BI (decisioni BI-1 C+F, BI-6, BI-7, BI-12) la traduce in una
**classe di munizione** dichiarata nei registri per le 52 voci `MISSILES_ASM` e in un flag **`ad_detectable`** che
conta solo per le difese **navali**. I registri non hanno né classe né dimensioni dei missili aerei (BI §1.5,
`:201-232` [V]). Questo documento fornisce quei dati.

**Che cosa è stato fatto**: sette lotti di ricerca web di `oc-researcher` (DeepSeek V4.1 Flash, sforzo alto), bozze
`Ricerca_Dati_Bersagli_L1..L7_oc-researcher.md`, costo **0,196 $**; verifica a campione della sessione principale
su 12 voci (§2.3); ricontrollo nel codice, da parte di chi scrive, di tutte le citazioni dei registri (righe, campi,
lanciatori nei loadout, righe di efficacia) [V]. Dopo le decisioni dell'utente: **ricerca mirata M1** su 7 voci
discordi (D5 (b); `oc-researcher` con DeepSeek V4 Pro, sforzo alto; bozza `Ricerca_Dati_Bersagli_M1_oc-researcher.md`;
costo **0,371 $**; totale della ricerca **0,567 $**), con i valori chiave riletti dalla sessione principale (§2.4).

**Risultato in breve** (classi e flag approvati dall'utente il 2026-11-07, identici alla proposta):

| Classe | Voci | `ad_detectable` |
|---|---|---|
| `cruise` | 10 (Kh-55, Kh-555, Kh-101, Kh-65, KD-20, Kh-59, Kh-59M, KD-63, KD-63B; navale BGM-109 Tomahawk) | True (per i cruise il flag non conta: bersagli di terrestri e navali) |
| `anti_ship` | 17 (aerei AGM-84A, RB-04E, RB-15, RB-15F, Kormoran, Sea Eagle, Kh-22N, Kh-31A, Kh-35, Kh-41; navali RGM-84, Granit, Moskit, Vulkan, YJ-12, YJ-18, YJ-83) | True ("non minori dell'Harpoon", salvo il Kormoran, 340 mm, in zona grigia approvata True, e lo YJ-18, senza dimensioni) |
| `arm` | 7 (AGM-45, AGM-88, Kh-58, Kh-25MP, Kh-25MPU, Kh-31P, LD-10) | True: Kh-58, Kh-31P; False: gli altri 5 |
| `tactical` | 18 (famiglia Maverick 3, ATGM 6, Mistral, Kh-25ML, Kh-25MR, Kh-66, RB-05A, RB-05E, Kh-29L/T/TE) | True: Kh-29L/T/TE; False: gli altri 15 |
| **Totale** | **52** (44 aerei + 8 navali) | **32 True, 20 False** |

- **Tutte le ipotesi di classe di BI §2.2 sono confermate dalle fonti**, salvo il **Mistral** (SAM, *Surface-to-Air
  Missile*, portatile nel registro A2G: resta `tactical` False, D2 (a)) e il **Kh-22N** (resta `anti_ship`, D3.1 (a);
  anomalia di designazione in §7, IR-21).
- **Metro deciso (D1 = R1-K)**: False obbligatorio se diametro ≤ 304,8 mm **e** massa ≤ 304 kg (inviluppo della
  famiglia Maverick fissata False da BI-6), True obbligatorio se diametro ≥ 343 mm **e** massa ≥ 515,25 kg (Harpoon
  aviolanciato, D4.1); lunghezza esclusa. Kh-29L/T/TE, Kh-58 e Kh-31P superano l'Harpoon (True, D3.3 (a)); Kh-25ML,
  Kh-25MR (299 kg dopo M1), Kh-66 e LD-10 sono False obbligatori; restano in **zona grigia**, approvate dall'utente
  voce per voce, **AGM-88, Kh-25MP, Kh-25MPU, RB-05A, RB-05E** (False) e, sul bordo alto, il **Kormoran** (True, 340 mm
  < 343).
- **Nessun flag è cambiato** rispetto alla proposta: le decisioni hanno fissato il metro, i valori da scrivere e
  l'elenco delle voci grigie che il test 5 del blocco 1 controlla (§5.3).

**Confidenza** delle 52 voci (sui dati che servono al metro, diametro e massa): **22 A, 21 M, 9 B** (dopo M1: Kh-25MR
da M ad A).
**Verifica**: **10 voci verificate dal principale** (AGM-65D, AGM-84A, Kh-29L, Kh-29T, Kh-29TE, AGM-88, Kh-58, Kh-35;
dopo M1 Kh-25MR e RB-05A, per diametro e massa), **4 in parte** (AGM-65K, RB-75T, Kh-22N, RGM-84-Harpoon), **38 solo
dall'agente**.

**Corrispondenza con la struttura obbligatoria delle Proposte**: problema e comportamento attuale = §1 e §2; alternative
e raccomandazioni = §5, §6, §9; decisioni (prese il 2026-11-07) = §9; piano di intervento = §10; rischi e limiti = §11.

## 2. Metodo e limiti

### 2.1 Come hanno lavorato gli agenti

- **Strumenti**: solo `webfetch` (lettura di una pagina dato l'URL). **`websearch` non era disponibile** in nessun
  lotto (dichiarato in tutte le bozze). Per scoprire gli URL gli agenti hanno usato la pagina di risultati
  **DuckDuckGo HTML** (`https://html.duckduckgo.com/html/?q=...`) prendendone **solo gli URL**, mai i dati; in L4
  (ultima ricerca), L6 e L7 DuckDuckGo ha risposto con una verifica anti-bot e gli agenti hanno proseguito con URL noti
  e con i riferimenti delle voci Wikipedia; Bing è stato provato due volte con risultati non pertinenti.
- **Fonti** usate più spesso: Wikipedia (inglese, russa, cinese, svedese), FAS (molte pagine `man.fas.org` danno 404:
  lette le copie di `web.archive.org`), d-s, CSIS (molte pagine 404), Arboga Robotmuseum (fonte museale svedese),
  missilery.info, redstar.gr, GlobalSecurity, Deagel, testpilot.ru, Rosoboronexport e KTRV (fonti primarie, una per
  Kh-31P e una archiviata per Kh-58E), il datasheet MBDA del Mistral 3.
- **airwar.ru** (e un sito russo archiviato per il Vulkan) arriva in codifica windows-1251 illeggibile: gli agenti
  hanno letto **solo i numeri ASCII** delle tabelle, senza le etichette delle righe. Quei numeri non sono attribuibili
  con certezza a una variante (caso evidente: Kh-22N, §2.3).
- **Estratti non sempre letterali**: nella prova di metodo (`Ricerca_Prova_V41Flash_oc-researcher.md`) il principale
  ha trovato valori corretti ma estratti con l'ordine delle unità normalizzato; gli estratti delle bozze vanno letti come
  parafrasi fedeli, non come citazioni.
- **RCS**: nessuna fonte, per nessuna delle 52 voci, pubblica un valore numerico. Solo aggettivi (Kh-555 "reduced radar
  cross-section", Kh-101 materiale radar-assorbente, KD-63 "poor stealth capability", tutti riportati dagli agenti). Il
  metro usa quindi le dimensioni come sostituto della traccia radar [S].
- **Lotti**: L1 ancore e famiglia Maverick (più il RGM-84 navale); L2 ATGM e Mistral; L3 Kh-25, Kh-66, Kh-29; L4 ARM
  e RB-05; L5 antinave aerei; L6 cruise e Kh-22N; L7 navali. Le due ancore sono state date agli agenti dal principale,
  non ricercate.

### 2.2 Cosa ho ricontrollato io nel repository [V]

Eseguendo in sola lettura i registri (`AIR_WEAPONS['MISSILES_ASM']`, `SHIP_WEAPONS['MISSILES_ASM']`) e
`AIRCRAFT_LOADOUTS` il 2026-11-07:
- **44 voci aeree e 8 navali**, nomi e righe di definizione come nella tabella del §4: tutte le righe citate dagli agenti
  sono esatte (`Asset/Aircraft_Weapon_Data.py:2115-5037`, `Asset/Ship_Weapon_Data.py:1240-1338`).
- I campi del registro citati dagli agenti (`task`, `start_service`, `warhead`, `range`, commenti) coincidono, per le
  voci usate nel §7.
- **Lanciatori nei loadout** (§4, colonna nelle note): solo 18 voci aeree su 44 hanno un aereo che le porta.
- **Righe di efficacia** (classi di bersaglio contro cui la fire control può usare il missile, `Logic/Fire_Control.py:664-684`
  e `:712-722`, filtro Pk > 0): i 7 ARM hanno **solo** la riga `Air_Defense`; AGM-84A, RB-04E, RB-15, RB-15F,
  Kormoran, Sea Eagle, **Kh-22N**, Kh-31A, Kh-35 e Kh-41 hanno **solo** la riga `ship`; BGM-71D non ha la riga `ship`;
  tutti gli altri hanno sia righe terrestri sia `ship`. Una nave è sempre bersaglio di classe `ship`
  (`Context/Context.py:1824-1828`, `Logic/Fire_Control.py:582-590`). Conseguenze nel §9 (D3).

### 2.3 Verifica del principale (2026-11-07, sul testo letterale delle pagine)

| Voce | Confermato | Non verificato |
|---|---|---|
| AGM-65D | Ø 304,8 mm (FAS); 2,49 m; 218,25-220 kg | — |
| famiglia AGM-65 (d-s) | colonna F/G 304 kg; il K è "an AGM-65G upgraded with the CCD seeker", senza pesi propri | 306 kg della colonna K di Wikipedia (non riletta) |
| AGM-84A | Ø 343 mm; 3,79-3,85 m; 515,25 kg aviolanciato (FAS); 556 kg nel testo CSIS; 691 kg RGM/UGM con booster | — |
| Kh-29L/T/TE | Ø 380 mm; 3,90 / 3,90 / 3,875 m; 660 / 685 / 690 kg (Wikipedia) | i valori FAS (657 / 680 kg; 3,875 m) |
| AGM-88 | Ø 254 mm; 4,17 m; 361 kg (Wikipedia) | i valori FAS e d-s (360 kg; 4,14 m) |
| Kh-58 | 380 mm; 4,8 m; 650 kg | che le dimensioni del Kh-58E valgano per il Kh-58U del registro |
| Kh-35 | 420 mm; versione aerea 3,85 m e 520 kg; navale 4,4 m e 610 kg | — |
| RB-75T | 295 kg; 2,5 m (Robotmuseum) | il diametro **non è nella fonte**: l'agente lo eredita dalla cellula AGM-65 e lo dichiara [S] (corretto) |
| Kh-22 (Wikipedia inglese) | 5.820 kg; 11,65 m; 92 cm; per Wikipedia inglese la **N è la versione nucleare** | Kh-22N da airwar.ru (5,635-5,78 t prime serie, 5,9 t successive): numeri senza etichette, **non attribuibili alla N**; la confidenza 'A' di L6 è esagerata (rivista: M) |
| KD-63 | — | la fonte GlobalSecurity dà 403 al lettore del principale: diametro 760 mm, ~2.000 kg, "only the H-6 bomber" **non verificati** |
| tutte le altre ~35 voci | — | **non controllate dal principale** |

**Plausibilità del KD-63 a 760 mm** (richiesta del principale) [I]: il valore coincide con quello che testpilot e
airwar danno per il Kh-41/Moskit (L5), ma L6 non ha letto pagine del Moskit (elenco delle pagine in `L6 §5`), quindi
una contaminazione fra lotti è improbabile. L'agente dice che il KD-63 deriva dall'YJ-6; per conoscenza generale [I,
non verificata] la famiglia P-15 Termit -> HY-2/C-601 -> YJ-6 ha una fusoliera di circa 0,76 m, quindi il valore è
plausibile come dato di famiglia. L'esito non dipende da questo numero: il KD-63 è `cruise` (bersaglio di tutti, BI-2)
e anche con metà del diametro resterebbe sopra l'Harpoon.

### 2.4 Ricerca mirata M1 (decisione D5 (b), 2026-11-07) e verifica del principale

- **Agente e costo**: `oc-researcher` con **DeepSeek V4 Pro** (0813, sforzo alto), 26 richieste, **0,371 $**
  (`Rapporti/Costi_Deleghe.md`, riga del 2026-11-07 "ricerca mirata M1"). Nell'intestazione della bozza l'agente si
  dichiara per errore "V4.1 Flash": il modello effettivo è quello del registro dei costi. Solo `webfetch`; DuckDuckGo
  in blocco anti-bot da metà sessione; 39 passi, 18 pagine utili.
- **Voci**: AGM-65K, Kh-25MR, RB-05A (e RB-05E), LD-10, Kormoran, Kh-22N, KD-63 (e KD-63B), cercate su fonti
  **indipendenti** da quelle di L1-L7.

| Voce | Esito M1 | Verifica |
|---|---|---|
| Kh-25MR | **299 kg**, Ø 275 mm (missilery.info, scheda X-25MR con bibliografia russa); 300 kg Astronautix; i **320 kg di ru-wiki respinti** (probabile massa di famiglia) | **principale** (299 kg, 275 mm) |
| RB-05A | **305 kg** (AEF, "Vikt 305 kg"), **304 kg** e Ø **0,30 m** (Astronautix, "Gross mass 304 kg (670 lb)") | **principale** (305, 304 kg; 300 mm) |
| RB-05E | nessuna fonte storica conosce una "E" (varianti note: Rb 05A di serie, Rb 05B prototipo TV, Rb 05C proposta) | agente |
| AGM-65K | massa propria della K solo in Wikipedia (306 kg, "675 lb"); d-s dà 304 kg per F/G e nessun peso per la K; fact sheet USAF e US Navy irraggiungibili (403) | **non risolto** (306 kg non verificato con fonte primaria) |
| LD-10 | nessuna terza fonte per massa e diametro (militarydrones.org.cn conferma solo 80 km e testata 20 kg) | **non risolto**: 200/234 kg, 200/203 mm |
| Kormoran | **600 kg** con tre fonti (Wikipedia, GlobalMilitary, CMANO "AS.34 Kormoran 1"); i 660 kg di missilery restano isolati; Ø 344 mm (Wikipedia, GlobalMilitary) contro 340 mm (missilery) / "0.34" (CMANO) | agente |
| Kh-22N | Ø **920 mm** (Weapons Parade "11.65 x 0.92 meters"); massa 5.635-5.900 kg secondo variante e fonte; **"N" = versione nucleare** per GlobalSecurity ("Kh-22N with a nuclear warhead and inertial guidance") e Weapons Parade ("nuclear type ... designated as Kh-22N"), come Wikipedia inglese; la versione antinave convenzionale sarebbe la Kh-22M/MA | agente (Ø 92 cm già verificato dal principale su Wikipedia, §2.3) |
| KD-63 / KD-63B | GlobalSecurity riletta per intero: 7 m, 0,76 m, "about 2000 kg", "only the H-6 bomber"; **nessuna seconda fonte**; **KD-63B assente** da ogni fonte | **non risolto** (fonte unica, non riletta dal principale) |

Effetti sui valori del §10.2: Kh-25MR 320 -> 299 kg; RB-05A invariato (305 kg); Kormoran invariato (600 kg, ora con tre
fonti); Kh-22N invariato. Nessun flag cambia. Altri due cambi del §10.2 (LD-10 e massa dell'AGM-114) non vengono da M1
ma dall'applicazione della regola D4.2 (a) a tutte le voci (§10.2, "Valori cambiati").

## 3. Le ancore del metro

Decisione BI-6 dell'utente: la famiglia Maverick è "piccola" in ogni contesto (`ad_detectable` False fisso); decisione
BI-7: l'Harpoon aviolanciato è il riferimento "rilevabile". Regole di coerenza della BI (§2.5, `:422-440`) [S], con
le ancore decise il 2026-11-07 (D1 = R1-K, D4.1 (a)): (1) un missile **non maggiore del Maverick** (diametro ≤ 304,8 mm
**e** massa ≤ 304 kg) è False obbligatorio; (2) un missile con diametro ≥ 343 mm **e** massa ≥ 515,25 kg (**non minore
dell'Harpoon**) è True obbligatorio; (3) in mezzo è **zona grigia**, approvata voce per voce. Lunghezza esclusa.

| Ancora | Ø [mm] | Lunghezza [m] | Massa [kg] | Fonti | Verifica |
|---|---|---|---|---|---|
| **bassa: AGM-65D** (`Aircraft_Weapon_Data.py:2499`) | 304,8 ("1 foot (30.48 centimeters)") | 2,49 | 218,25 (FAS) / 220 (d-s) | https://man.fas.org/dod-101/sys/smart/agm-65.htm ; https://www.designation-systems.net/dusrm/m-65.html ; https://en.wikipedia.org/wiki/AGM-65_Maverick | principale |
| famiglia Maverick (stesso diametro 304,8-305 mm) | — | 2,49 | A/B 209-210; D 220; E 285 (d-s); F/G 304 (d-s) / 301,5 (FAS, G); K 306 (Wikipedia) | stesse | principale per A/B, D, E, F/G (d-s); K 306 non riletto (M1: nessuna fonte primaria) |
| **ancora bassa decisa (D1 = R1-K)**: inviluppo della famiglia fissata False da BI-6 (AGM-65D, AGM-65K, RB-75T) | **304,8** | (esclusa) | **304** (d-s, colonna F/G, cellula del K) | d-s | principale |
| **alta: AGM-84A aviolanciato** (`Aircraft_Weapon_Data.py:2239`) | 343 (13,5 in) | 3,79 (FAS) / 3,85 (testo CSIS) | **515,25** (FAS, "1,145 pounds (515.25 kilograms)"); 556 (testo CSIS: "...with a launch weight of 556 kg") | https://man.fas.org/dod-101/sys/smart/agm-84.htm ; https://missilethreat.csis.org/missile/harpoon/ | principale |
| RGM-84 navale con booster (`Ship_Weapon_Data.py:1240`, `caliber` 343 a `:1244` [V]) | 343 | 4,55-4,63 | 661,5 (FAS) / 690 (d-s) / 691 (Wikipedia, "including booster") | https://en.wikipedia.org/wiki/Harpoon_(missile) | principale per 343 e 691 |

RCS: non pubblicata per nessuna delle due ancore. **Valori usati nel test di coerenza** (decisi il 2026-11-07): Maverick
304,8 mm e 304 kg (**D1** = R1-K; i 306 kg di Wikipedia per la K non sono verificati con fonte primaria e non si
usano), Harpoon 343 mm e 515,25 kg (**D4.1** (a)).

## 4. Tabella unica delle 52 voci

Legenda della colonna "Confronto" (aggiornata il 2026-11-07 al metro deciso, D1 = R1-K: ancora bassa 304,8 mm /
304 kg, ancora alta AGM-84A 343 mm / 515,25 kg; calcolata sui valori scritti nel registro, §10.2): **≤M** = diametro e
massa non maggiori dell'ancora bassa (False obbligatorio, F!); **ZG** = zona grigia (né ≤M né ≥H), flag approvato
dall'utente voce per voce (§6); **≥H** = diametro e massa non minori dell'Harpoon (True obbligatorio, T!); **n.d.** =
dati insufficienti (§8). Valori fra parentesi = di famiglia, non della voce. Le colonne Ø, lunghezza e massa riportano
tutti i valori trovati; quello scritto nel registro è nel §10.2.

| # | Voce (riga [V]) | Variante cercata | Classe proposta (ipotesi BI) | Ø [mm] | Lungh. [m] | Massa [kg] | Confronto | `ad_detectable` | Conf. | Verifica |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | AGM-65D (`:2499`) | AGM-65D IIR | `tactical` (confermata) | 304,8 | 2,49 | 218,25-220 | ancora bassa | **False** (BI-6) | A | principale |
| 2 | AGM-65K (`:2569`) | AGM-65G ricostruito con seeker CCD | `tactical` (conf.) | 304,8-305 | 2,49 | 301,5-306 | ≤M (304 kg; con 306 sarebbe ZG) | **False** (BI-6) | A | principale parz. (304 kg d-s, identità del K) |
| 3 | RB-75T (`:2409`) | Rb 75T, "tung stridsdel" (testata pesante) | `tactical` (conf.) | (304,8 [S] ereditato) | 2,5 | 295 | n.d. (Ø non nella fonte; 295 ≤ 304) | **False** (BI-6) | B | principale parz. (295 kg, 2,5 m) |
| 4 | AGM-114 (`:2639`) | famiglia A/B/C (testata della K) | `tactical` (conf.) | 178-180 | 1,63 | 45-49 | ≤M | False | A | agente |
| 5 | BGM-71D (`:2709`) | TOW-2 | `tactical` (conf.) | 152 | 1,17-1,51 | 21,5 | ≤M | False | A | agente |
| 6 | 9M114 (`:2904`) | 9M114 Kokon (sistema 9K114 Shturm) | `tactical` (conf.) | 130 | 1,625 / 1,83 | 31,4 (46,5 col tubo) | ≤M | False | A | agente |
| 7 | 9M120 (`:2840`) | 9M120 Ataka | `tactical` (conf.) | 130 | 1,83 | 46-49,5 | ≤M | False | M | agente |
| 8 | 9M120-F (`:2776`) | 9M120F termobarico | `tactical` (conf.) | (130) | (1,83) | (≈49,5) | ≤M solo per famiglia | False | B | agente |
| 9 | Hot-3 (`:2968`) | HOT-3 (1998) | `tactical` (conf.) | 150 | 1,30 | 24,5 (23,5-32,5) | ≤M | False | M | agente |
| 10 | Mistral (`:3032`) | Mistral 1/2, SAM portatile (ATAM su elicottero) | **contestata**: `sam` o `tactical` (D2) | 90-92 | 1,86-1,88 | 19,7 | ≤M | False | A | agente |
| 11 | Kh-25ML (`:3449`) | izd. 713, guida laser | `tactical` (conf.) | 275 | 3,57-3,75 | 299-300 | ≤M | False (F!, §6.2) | A | agente |
| 12 | Kh-25MR (`:3523`) | izd. 714, radiocomando | `tactical` (conf.) | 275 | 3,686-3,83 | 299-300 (320 ru-wiki respinto, M1) | ≤M | False (F!, §6.3) | A (rivista dopo M1) | principale (299 kg, 275 mm, M1) |
| 13 | Kh-66 (`:3301`) | izd. 66, beam riding | `tactical` (conf.) | 275 | 3,63 | 278-290 | ≤M | False (F!, §6.6) | M | agente |
| 14 | Kh-29L (`:3655`) | izd. 63, laser | `tactical` (conf.) | 380 | 3,875-3,90 | 657-660 | ≥H | **True** | A | principale |
| 15 | Kh-29T (`:3728`) | izd. 64, TV | `tactical` (conf.) | 380 | 3,875-3,90 | 680-685 | ≥H | **True** | A | principale |
| 16 | Kh-29TE (`:3804`) | export 30 km | `tactical` (conf.) | 380 | 3,875 | 690 | ≥H | **True** | M | principale |
| 17 | AGM-45 (`:2219`) | AGM-45B Shrike | `arm` (conf.) | 203 | 3,05 | 177 | ≤M | False | A | agente |
| 18 | AGM-88 (`:2259`) | AGM-88A/B/C HARM | `arm` (conf.) | 254 | 4,14-4,17 | 360-361 | ZG | False (approvata, §6.1) | A | principale |
| 19 | Kh-58 (`:3272`) | Kh-58U (dimensioni del Kh-58E) | `arm` (conf.) | 380 | 4,8 | 650 | ≥H | **True** | A | principale |
| 20 | Kh-31P (`:4012`) | izd. 77P | `arm` (conf.) | 360 | 4,7 | 600 | ≥H | **True** | A | agente |
| 21 | Kh-25MP (`:3626`) | izd. 711 | `arm` (conf.) | 275 | 4,19-4,36 | 315-320 | ZG | False (approvata, §6.4) | A | agente |
| 22 | Kh-25MPU (`:3597`) | MP modernizzato | `arm` (conf.) | 275 | 4,255 | 315 | ZG | False (approvata, §6.5) | M | agente |
| 23 | LD-10 (`:4644`) | LD-10 base | `arm` (conf.) | 200-203 | 3,5 / 4,1 | 200 / 234 | ≤M (con entrambi i valori) | False (F!, §6.9) | M | agente (M1: nessuna terza fonte) |
| 24 | RB-05A (`:2115`) | Rb 05A, MCLOS radiocomandato | `tactical` (conf.) | 300 | 3,6 | 304-305 (305 AEF e Wikipedia, 304 Astronautix) | ZG (305 > 304) | False (approvata, §6.7) | A | principale (305/304 kg, 300 mm, M1) |
| 25 | RB-05E (`:2299`) | designazione **non trovata** (dati di famiglia Rb 05) | `tactical` (conf. con riserva) | (300) | (3,6) | (305) | ZG solo per famiglia; n.d. nel registro (D6) | False (approvata, §6.8) | B | agente (M1: "E" assente dalle fonti) |
| 26 | AGM-84A (`:2239`) | aviolanciato | `anti_ship` (conf.) | 343 | 3,79-3,85 | 515,25 (556) | ancora alta | **True** | A | principale |
| 27 | RB-04E (`:2369`) | Robot 04E (1975) | `anti_ship` (conf.) | 500 | 4,45 | 600-625 | ≥H | True | M | agente |
| 28 | RB-15 (`:2479`) | RBS 15 Mk I navale/costiero | `anti_ship` (conf.) | 500 | 4,33-4,35 | 568 (746 col booster) | ≥H | True | A | agente |
| 29 | RB-15F (`:2190`) | RBS 15F aviolanciato | `anti_ship` (conf.) | 500 | 4,35-4,4 | 565-568 | ≥H | True | A | agente |
| 30 | Kormoran (`:2279`) | Kormoran 1 (dedotta) | `anti_ship` (conf.) | 340-344 | 4,40 | 600 (3 fonti, M1; 660 missilery isolato) | ZG con 340 mm (scritto), ≥H con 344 | True (approvata, §6.11) | M | agente |
| 31 | Sea Eagle (`:2389`) | P3T aviolanciato | `anti_ship` (conf.) | 400 | 4,10-4,14 | 580-730 | ≥H | True | M | agente |
| 32 | Kh-31A (`:3981`) | Kh-31A Mod 1 | `anti_ship` (conf.) | 360 | 4,7 | 610 | ≥H | True | A | agente |
| 33 | Kh-35 (`:4043`) | versione aerea | `anti_ship` (conf.) | 420 | 3,85 | 520 | ≥H (con 515,25, D4.1) | True | M | principale |
| 34 | Kh-41 (`:4074`) | Moskit aviolanciato | `anti_ship` (conf.) | 760 / 800 | 9,385 / 9,745 | 3.950 / 4.500 | ≥H | True | M (agente: A) | agente |
| 35 | Kh-22N (`:3243`) | Kh-22N, designazione controversa (per M1 la "N" è nucleare, §7 IR-21) | `anti_ship` (D3.1 (a)) | 900-920 | 11,3-11,67 | 5.820 (5.635-5.900 secondo variante e fonte) | ≥H | True | M (agente: A) | principale parz. (valori di Wikipedia inglese) |
| 36 | Kh-55 (`:3095`) | Kh-55/Kh-55SM | `cruise` (conf.) | 514 | 6,04 | 1.210 | ≥H | True | M | agente |
| 37 | Kh-555 (`:4286`) | Kh-555 convenzionale | `cruise` (conf.) | n.d. | n.d. | n.d. | n.d. | True (default) | B | agente |
| 38 | Kh-101 (`:3169`) | Kh-101 | `cruise` (conf.) | 510 | 7,45 | 2.300-2.400 | ≥H | True | A | agente |
| 39 | Kh-65 (`:4105`) | Kh-65SE | `cruise` (conf.) | (514, di famiglia [S]) | 6,04 | 1.650 | ≥H | True | M (Ø: B) | agente |
| 40 | KD-20 (`:5037`) | CJ-10K aviolanciato | `cruise` (conf.) | n.d. (famiglia 514-750) | n.d. | n.d. (famiglia 1.090-2.500) | ≥H solo per famiglia | True (default) | B | agente |
| 41 | Kh-59 (`:3375`) | Kh-59 base | `cruise` (conf.) | 380 | 5,37 | 760-790 | ≥H | True | M | agente |
| 42 | Kh-59M (`:4467`) | Kh-59M | `cruise` (conf.) | 380 | 5,70 | 930 | ≥H | True | M | agente |
| 43 | KD-63 (`:4675`) | KD-63 / YJ-63 | `cruise` (conf.; solo da bombardiere H-6, D3.2 (a)) | 760 | 7 | ~2.000 | ≥H | True | M | agente (fonte unica, riletta per intero in M1; 403 per il principale) |
| 44 | KD-63B (`:4856`) | KD-63B | `cruise` (per famiglia) | n.d. | n.d. | n.d. | n.d. | True (default) | B | agente |
| 45 | RGM-84-Harpoon (navale `:1240`) | RGM-84 con booster | `anti_ship` (conf.) | 343 (`caliber` 343) | 4,55-4,63 | 661,5-691 (con booster) | ≥H | True | M | principale parz. (343 mm, 691 kg) |
| 46 | BGM-109-Tomahawk (navale `:1254`) | Block IV (TLAM) | `cruise` (conf.) | 520 (`caliber` 519) | 5,55-5,56 | 1.300-1.315 senza booster (1.600 con) | ≥H | True | A | agente |
| 47 | P-700-Granit (navale `:1268`) | 3M45 | `anti_ship` (conf.) | 850 | 10 | 7.000 | ≥H | True | M | agente |
| 48 | P-270-Moskit (navale `:1282`) | 3M80/3M80E | `anti_ship` (conf.) | 800 (`caliber` 760) | 9,385-9,745 | 3.970-4.500 | ≥H | True | M | agente |
| 49 | P-1000-Vulkan (navale `:1296`) | 3M70 | `anti_ship` (conf.) | 880 | 11,7 | 7.000-8.000 / 4.800 | ≥H | True | B | agente |
| 50 | YJ-12 (navale `:1310`) | YJ-12A (dati dell'aviolanciato) | `anti_ship` (conf.) | 500 / 600 (stima) | 6-7 | 2.000-3.000 | ≥H | True | B | agente |
| 51 | YJ-18 (navale `:1324`) | YJ-18A | `anti_ship` (conf.) | 514 (stima CSIS; `caliber` 540) | <8,2 col booster | <1.579 (limite superiore) | ≥H | True | B (agente: M) | agente |
| 52 | YJ-83 (navale `:1338`) | YJ-83 (famiglia) | `anti_ship` (conf.) | 360 | 6,38 | 800 | ≥H | True | M | agente |

Fonti, estratti e URL di ogni riga: nella bozza del lotto (righe 1-3 e 26, 45: L1; 4-10: L2; 11-16: L3; 17-25: L4;
27-34: L5; 35-44: L6; 46-52: L7), sezione "Dettaglio per voce"; per le righe 2, 12, 23, 24, 25, 30, 35, 43 e 44 anche
la bozza M1 (§2.4). Le righe 1-3, 26 sono riprese anche nel §3.

**Lanciatori nei loadout** [V, `Asset/Aircraft_Loadouts.py`]: AGM-65D A-10C; AGM-65K A-10C II; AGM-84A F/A-18A/C e S-3B;
AGM-88 F-15E, F-16 (A MLU, C Block 52d, CM Block 50), F/A-18C; AGM-45 F-16A; AGM-114 MQ-1, MQ-9; Kh-25ML MiG-27K,
Su-17M4, Su-24M, Su-25T, Su-25TM, Su-30; Kh-25MP Su-25TM; Kh-25MPU Su-24M, Su-30; Kh-29L MiG-27K, Su-24M; Kh-29T
Su-25T, Su-25TM, Su-30, Su-34; Kh-58 Su-24M, Su-25TM, Su-30, Su-34; Kh-59 Su-30, Su-34, Tu-160; Kh-55 Tu-95MS; Kh-101
Tu-160; Kh-22N Tu-22M; RB-05A e RB-15F AJ/ASJ 37 Viggen. **Nessun lanciatore** per le altre 26 voci aeree (fra cui
Kh-29TE, Kh-31A/P, Kh-35, Kh-41, Kh-59M, KD-63/63B, KD-20, Kh-555, Kh-65, LD-10, Kormoran, Sea Eagle, RB-04E, RB-15,
RB-05E, RB-75T, Mistral, ATGM 9M114/9M120/Hot-3/BGM-71D).

**Missili citati dall'utente ma assenti dai registri**: Brimstone, Vikhr (9M127), APKWS [V: nessuna occorrenza nei
tre registri, ricerca del 2026-11-07]. Nessuna voce da creare (BI §5.1 punto 5).

## 5. Il metro del Maverick (deciso il 2026-11-07: D1 = R1-K) e l'esito sulle 52 voci

### 5.1 Le regole decise

Costanti del metro (scelte di progetto [S] su valori con fonte; sono le costanti del test 5 del blocco 1):

| Costante | Valore | Fonte | Decisione |
|---|---|---|---|
| `D_M` (diametro dell'ancora bassa) | **304,8 mm** | FAS AGM-65, "1 foot (30.48 centimeters)" [principale]; identico in tutta la famiglia | D1 = R1-K |
| `M_M` (massa dell'ancora bassa) | **304 kg** | d-s, colonna F/G ("304 kg (670 lb)"), cellula da cui deriva il K [principale]; i 306 kg di Wikipedia per il K **non** sono verificati con fonte primaria (M1, §2.4) | D1 = R1-K |
| `D_H` (diametro dell'ancora alta) | **343 mm** | FAS AGM-84 (13,5 in) [principale]; `caliber` 343 del RGM-84 [V] | D4.1 |
| `M_H` (massa dell'ancora alta) | **515,25 kg** | FAS AGM-84, "1,145 pounds (515.25 kilograms)" [principale] | D4.1 (a) |

- **Regola (1), False obbligatorio (F!)**: `diameter_mm <= D_M` **e** `mass_kg <= M_M`. È l'inviluppo della famiglia
  fissata False dalla BI-6 (AGM-65D 304,8 mm / 220 kg; AGM-65K 304,8 / 304; RB-75T Ø non pubblicato / 295 kg): nessun
  membro della famiglia supera l'ancora, quindi la regola non contraddice la BI-6 (a differenza di R1-D, che metteva
  AGM-65K e RB-75T in zona grigia).
- **Regola (2), True obbligatorio (T!)**: `diameter_mm >= D_H` **e** `mass_kg >= M_H`.
- **Zona grigia (ZG)**: ogni voce con la coppia diametro-massa che non soddisfa né (1) né (2); il flag è quello
  approvato dall'utente voce per voce (§6).
- **Lunghezza esclusa** (sotto-domanda di D1, decisa): se fosse condizione della regola (1), AGM-45 (3,05 m), LD-10
  (3,5 m), RB-05 (3,6 m), tutti i Kh-25 (3,6-4,4 m) e l'AGM-88 (4,17 m), più lunghi del Maverick (2,49 m), non
  risulterebbero mai F!; le lunghezze sono anche i dati più discordi (Kh-25MP 4,19 contro 4,36 m, 9M114 1,625 contro
  1,83 m). La lunghezza resta in questo documento come informazione e **non** entra nel registro.
- **Voci senza la coppia** (D6 (a)): fuori dal metro; il flag è il default di classe (BI `:965`) o quello
  approvato (RB-05E) o quello fissato dalla BI-6 (RB-75T).
- I valori confrontati sono quelli **scritti nel registro** (§10.2, scelti con la regola D4.2 (a)).

Le varianti scartate, per traccia: **R1-D** (AGM-65D, 304,8 mm e 220 kg) avrebbe messo in zona grigia 9 voci più AGM-65K
e RB-75T; **R1-Ø** (solo diametro ≤ 304,8 mm) avrebbe svuotato la zona grigia bassa (§9, D1).

### 5.2 Esito per voce (valori del §10.2)

| Voce | Classe | Ø [mm] | Massa [kg] | Esito (R1-K) | `ad_detectable` (decisione) |
|---|---|---|---|---|---|
| AGM-65D | tactical | 304,8 | 220 | F! | False (BI-6) |
| AGM-65K | tactical | 304,8 | 304 | F! (al confine: 304 ≤ 304) | False (BI-6) |
| RB-75T | tactical | — | 295 | senza coppia | False (BI-6; test 4) |
| AGM-114, BGM-71D, 9M114, 9M120, Hot-3, Mistral | tactical | 90-180 | 19,7-49,5 | F! | False |
| AGM-45 | arm | 203 | 177 | F! | False |
| LD-10 | arm | 200 | 200 | F! (anche con 203 mm / 234 kg di Deagel) | False |
| Kh-66 | tactical | 275 | 290 | F! | False |
| Kh-25ML | tactical | 275 | 300 | F! | False |
| Kh-25MR | tactical | 275 | 299 | F! (con i 320 kg di ru-wiki, respinti da M1, sarebbe ZG) | False |
| RB-05A | tactical | 300 | 305 | **ZG** (1 kg sopra `M_M`) | False, approvata (§6.7) |
| Kh-25MP | arm | 275 | 320 | **ZG** | False, approvata (§6.4) |
| Kh-25MPU | arm | 275 | 315 | **ZG** | False, approvata (§6.5) |
| AGM-88 | arm | 254 | 361 | **ZG** | False, approvata (§6.1) |
| RB-05E | tactical | — | — | senza coppia (D6 (a)); ZG per famiglia | False, approvata (§6.8) |
| 9M120-F | tactical | — | — | senza coppia (D6 (a)) | False (default di classe) |
| Kh-31P | arm | 360 | 600 | T! | True (D3.3 (a)) |
| Kh-58 | arm | 380 | 650 | T! | True (D3.3 (a)) |
| Kh-29L / T / TE | tactical | 380 | 660 / 685 / 690 | T! | True (D3.3 (a)) |
| Kormoran | anti_ship | 340 | 600 | **ZG** (340 < 343) | True, approvata (§6.11) |
| Kh-35 | anti_ship | 420 | 520 | T! | True |
| AGM-84A (ancora alta) | anti_ship | 343 | 515,25 | T! (al confine) | True |
| RB-04E, RB-15, RB-15F, Sea Eagle, Kh-31A, Kh-41, Kh-22N; Kh-55, Kh-101, Kh-59, Kh-59M, KD-63; navali RGM-84, Tomahawk, Granit, Moskit, Vulkan, YJ-12, YJ-83 | anti_ship / cruise | 360-920 | 565-7.000 | T! | True |
| Kh-555, KD-20, KD-63B (cruise), Kh-65 (solo massa), YJ-18 (anti_ship) | cruise / anti_ship | — | — (Kh-65: 1.650) | senza coppia | True (default di classe) |

### 5.3 Conteggi e trattamento della zona grigia nel test 5

- **44 voci con la coppia**: **13 F!** (tutte False), **26 T!** (tutte True), **5 ZG** (AGM-88, Kh-25MP, Kh-25MPU,
  RB-05A False; Kormoran True). **8 voci senza la coppia**: RB-75T, 9M120-F, RB-05E (False); Kh-555, Kh-65, KD-20,
  KD-63B, YJ-18 (True).
- **Controllo delle regole a mano**: fra le True con la coppia il diametro minimo è 340 mm (Kormoran) > 304,8, quindi
  nessuna True soddisfa la regola (1); fra le False con la coppia il diametro massimo è 304,8 mm (AGM-65D, AGM-65K) <
  343 e la massa massima è 361 kg (AGM-88) < 515,25, quindi nessuna False soddisfa la regola (2). Le regole (1) e (2)
  del test 5 passano.
- **Le voci grigie non sono eccezioni**: per definizione non soddisfano né (1) né (2), quindi passano le due regole
  qualunque sia il loro flag. Un elenco di "eccezioni" alle regole non serve (nessuna voce approvata le viola) e le
  indebolirebbe. Senza un controllo in più, però, il test non proteggerebbe l'approvazione dell'utente: un
  `'ad_detectable': True` scritto per errore sull'AGM-88 passerebbe.
- **Scelta per il test 5** [S, scelta di piano motivata, non una decisione di design nuova]: una costante del test
  `GREY_ZONE_APPROVED` (nome -> flag approvato, con il commento "approvate dall'utente il 2026-11-07,
  Proposta_Dati_Bersagli_Intercettabili.md §6") con **6 voci**: `{'AGM-88': False, 'Kh-25MP': False, 'Kh-25MPU': False,
  'RB-05A': False, 'RB-05E': False, 'Kormoran': True}`, e una terza asserzione:
  - (3a) ogni nome dell'elenco esiste in `AIR_WEAPONS['MISSILES_ASM']` (sono tutte voci aeree [V]) e ha
    `ad_detectable` **presente e uguale** al valore approvato (vale anche per RB-05E, che non ha la coppia);
  - (3b) l'insieme delle voci con la coppia che cadono in zona grigia (in entrambi i registri) è **uguale**
    all'insieme dei nomi dell'elenco che hanno la coppia, cioè `{'AGM-88', 'Kh-25MP', 'Kh-25MPU', 'RB-05A',
    'Kormoran'}`.
  Effetto: una voce nuova o modificata che entra in zona grigia senza approvazione fa fallire il test (esempio: il
  Kh-25MR scritto con 320 kg); così una voce approvata che ne esce per un valore cambiato (esempio: RB-05A scritto con
  304 kg). Il numero dei test del blocco 1 resta **6** (è sempre il test 5).

**Effetto sui flag**: nessuno rispetto alla proposta: tutte le voci F! sono False, tutte le T! True, le cinque ZG hanno
il flag approvato.

## 6. Zona grigia: voci da approvare una per una (approvate il 2026-11-07)

Ogni voce riporta i dati, l'esito con le tre varianti di D1, la proposta e il motivo. Le voci attese dalla BI ma
uscite dalla zona grigia (Kh-29, Kh-58, Kh-31P) sono in fondo, per conferma.
**Esito (2026-11-07)**: con D1 = R1-K (304,8 mm / 304 kg) e i valori del §10.2 restano in zona grigia **AGM-88, Kh-25MP,
Kh-25MPU, RB-05A, RB-05E** (approvate False dall'utente, opzione (a) di ciascuna voce) e il **Kormoran** sul bordo alto
(confermato True); Kh-25ML, Kh-25MR (299 kg dopo M1), Kh-66 e LD-10 sono False obbligatori; Kh-29L/T/TE, Kh-58, Kh-31P
e Kh-35 True obbligatori, confermati. Le righe "Dopo M1" e "scelta utente" sotto aggiornano le analisi scritte prima
delle decisioni.

### 6.1 AGM-88 HARM (arm) — Ø 254 mm, 4,17 m, 361 kg [principale]
R1-D ZG, R1-K ZG, R1-Ø F!. Massa 64% sopra il Maverick D, 70% dell'Harpoon; diametro 17% sotto il Maverick. Lanciato da
F-15E, F-16, F/A-18C [V]; ha solo la riga di efficacia `Air_Defense` [V]: non è mai sparato contro una nave, quindi il
flag conta solo se una nave è nel dominio di coordinamento del SAM terrestre attaccato (BI-5 (a)). Contro le difese
terrestri è escluso comunque (BI-3). **Proposta: False** (Conf. A).
scelta utente: (a) False (2026-11-07). Esito con R1-K: ZG (254 mm ≤ 304,8 ma 361 kg > 304); nell'elenco delle voci
grigie approvate del test 5 (§5.3).

### 6.2 Kh-25ML (tactical) — Ø 275 mm, 3,705 m, 299-300 kg [agente]
R1-D ZG, R1-K F!, R1-Ø F!. Più stretto del Maverick, più pesante del 36%. Ha la riga `ship` e 6 lanciatori (Su-24M,
Su-25T, Su-30...) [V]: è il Kh-25 che si può incontrare davvero contro una nave. **Proposta: False** (Conf. A).
scelta utente: False obbligatorio (2026-11-07): con R1-K (300 kg ≤ 304) la voce esce dalla zona grigia.

### 6.3 Kh-25MR (tactical) — Ø 275 mm, 3,69-3,83 m, 300-320 kg [agente, fonti discordi]
R1-D ZG, R1-K F! con 300 kg (Astronautix) / ZG con 320 kg (ru-wiki), R1-Ø F!. Nessun lanciatore nei loadout [V].
**Proposta: False** (Conf. M).
**Dopo M1** (§2.4): 299 kg e 275 mm (missilery.info, verificati dal principale); i 320 kg di ru-wiki sono respinti;
confidenza rivista: A.
scelta utente: False obbligatorio (2026-11-07): con 299 kg ≤ 304 la voce non è più in zona grigia.

### 6.4 Kh-25MP (arm) — Ø 275 mm, 4,19-4,36 m, 315-320 kg [agente]
R1-D ZG, R1-K ZG, R1-Ø F!. Lanciato da Su-25TM [V], solo riga `Air_Defense` [V] (come 6.1). **Proposta: False** (Conf.
A).
scelta utente: (a) False (2026-11-07). Esito con R1-K: ZG (320 kg scritto, §10.2); nell'elenco del test 5.

### 6.5 Kh-25MPU (arm) — Ø 275 mm, 4,255 m, 315 kg [agente, una sola fonte]
Come 6.4; lanciato da Su-24M, Su-30 [V]. **Proposta: False** (Conf. M).
scelta utente: (a) False (2026-11-07). Esito con R1-K: ZG (315 kg); nell'elenco del test 5.

### 6.6 Kh-66 (tactical) — Ø 275 mm, 3,63 m, 278-290 kg [agente]
R1-D ZG, R1-K F!, R1-Ø F!. Nessun lanciatore nei loadout [V]. **Proposta: False** (Conf. M).
scelta utente: False obbligatorio (2026-11-07): con R1-K (290 kg ≤ 304) la voce esce dalla zona grigia.

### 6.7 RB-05A (tactical) — Ø 300 mm, 3,6 m, 305 kg [agente]
R1-D ZG; R1-K F! con 306 kg, ZG con 304 kg (il caso più sensibile: 1 kg); R1-Ø F!. Lanciato dal Viggen [V], ha la riga
`ship`. Le due fonti (Wikipedia inglese e svedese) sono della stessa origine. **Proposta: False** (Conf. A).
**Dopo M1** (§2.4): due fonti nuove indipendenti, verificate dal principale: 305 kg (AEF) e 304 kg, 0,30 m
(Astronautix). Con D4.2 (a) si scrive 305 kg (stessa specificità, voce False: il valore più alto); la voce resta ZG.
scelta utente: (a) False (2026-11-07). Nell'elenco del test 5.

### 6.8 RB-05E (tactical) — dati della famiglia Rb 05 [agente; designazione non trovata]
Come 6.7, ma "Rb 05E" non esiste nelle fonti storiche: l'unica occorrenza è un video DCS (probabile nome di simulatore
per la versione radiocomandata). Nessun lanciatore nei loadout [V]. **Proposta: False** come default di classe
`tactical` (§8, D6), senza dimensioni nel registro (Conf. B).
**Dopo M1**: nessuna fonte storica conosce una "Rb 05E" (varianti note: A, B, C).
scelta utente: (a) False (2026-11-07), senza dimensioni (D6 (a)). Nell'elenco del test 5 solo per il controllo del
flag (non ha la coppia, §5.3).

### 6.9 LD-10 (arm) — Ø 200-203 mm, 3,5 / 4,1 m, 200 / 234 kg [agente, fonti discordi]
R1-D F! con 200 kg (zh-wiki, GlobalSecurity, che però sembra una traduzione della pagina cinese) / ZG con 234 kg
(Deagel); R1-K F!; R1-Ø F!. La portata del registro (80 km) coincide con la coppia 200 kg / 3,5 m. Nessun lanciatore
nei loadout [V]. **Proposta: False** (Conf. M).
**Dopo M1**: nessuna terza fonte (militarydrones.org.cn conferma solo 80 km e testata 20 kg). Con D4.2 (a) si scrive la
coppia della fonte più specifica per la variante a registro, zh-wiki/GlobalSecurity (200 mm, 200 kg: stessa portata di
80 km del registro; Deagel dà 60 km), §10.2.
scelta utente: False obbligatorio (2026-11-07): con R1-K è F! con entrambi i valori (200 o 234 kg ≤ 304).

### 6.10 Uscite dalla zona grigia verso l'alto: Kh-29L, Kh-29T, Kh-29TE, Kh-58, Kh-31P
Tutte con diametro 360-380 mm e massa 600-690 kg, sopra l'Harpoon in entrambe le grandezze: **True obbligatorio** per la
regola (2); con False il test 5 del blocco 1 fallirebbe (BI `:931-946`). Kh-29L/T/TE e Kh-58 verificati dal principale.
Conseguenze diverse (§9, D3.3): i Kh-29 hanno la riga `ship` e 6 aerei che li portano [V], quindi una nave potrà
fermarli; Kh-58 e Kh-31P hanno solo la riga `Air_Defense` [V] e una nave li incontra solo come difesa di dominio.
scelta utente: True, confermato (2026-11-07; D3.3 (a)).

### 6.11 Sul bordo alto: Kormoran e Kh-35
- **Kormoran** (anti_ship): Ø 344 mm (Wikipedia) / 340 mm (missilery), massa 600-660 kg. Con 340 mm la regola (2) non è
  soddisfatta (ZG), con 344 sì. Nessun lanciatore nei loadout [V]. **Proposta: True** (antinave di massa nettamente
  superiore all'Harpoon; Conf. M).
- **Kh-35** (anti_ship): Ø 420 mm, 520 kg [principale]. T! con l'ancora 515,25 kg, ZG con 556 kg (D4). Nessun
  lanciatore [V]. **Proposta: True** (Conf. M).
**Dopo M1**: Kormoran 1 a 600 kg con tre fonti (Wikipedia, GlobalMilitary, CMANO); diametro ancora 340/344 mm. Con
D4.2 (a) si scrive 340 mm (stessa specificità, voce True: il valore più basso), quindi il Kormoran è ZG e va
nell'elenco del test 5 con True. Kh-35: T! con l'ancora 515,25 kg (D4.1 (a)).
scelta utente: True per entrambe, confermato (2026-11-07).

## 7. Incoerenze di registro scoperte (da riportare, NON da correggere nel blocco 1)

Nessuna di queste incoerenze tocca la regola BI (che legge solo `munition_class` e `ad_detectable`); alcune toccano i
punteggi e la fire control (portata, velocità, testata). Il blocco 1 **non** le corregge (BI §5.2: "Nessun altro
registro cambia"): proposta [S] di raccoglierle in una Proposta separata di manutenzione dei registri, con fonti.

| # | Voce (riga [V]) | Registro [V] | Fonti (livello) | Effetto potenziale |
|---|---|---|---|---|
| IR-1 | RB-75T (`:2409`, testata a `:2417`) | `warhead` 57 kg con commento "WDU-20/B shaped-charge" (testata dell'Rb 75/AGM-65A-B); `range` 15 | Rb 75T = "tung stridsdel" (testata pesante), 295 kg [principale]; portata "<10 km (skjuthöjd <500 m)" (Robotmuseum) [agente] | punteggio e fire control con la testata leggera |
| IR-2 | AGM-65K (`:2569`) | `start_service` 1970 | il K è una conversione del G (G in servizio dal 1989), "in production as of 2007" [agente; identità del K: principale] | disponibilità per anno |
| IR-3 | BGM-71D (`:2709`) | `start_service` 1970; `warhead` 6,14 kg; `task` Strike/SEAD | BGM-71D = TOW-2 (1983, testata 5,9 kg); 6,14 kg è del BGM-71F [agente] | disponibilità, punteggio |
| IR-4 | Hot-3 (`:2968`) | `start_service` 1978 | HOT 1 dal 1978; HOT-3 dal 1998 [agente] | disponibilità |
| IR-5 | Mistral (`:3032`) | `type` 'ASM', `task` Strike/Anti_Ship, `start_service` 1985 | SAM portatile; versione ATAM aria-aria su elicotteri; Mistral 1 dal 1990 [agente]; già segnalato in BI §1.5 `:225-226` | classificazione (D2) |
| IR-6 | Kormoran (`:2279`) | non dice 1 o 2; 1973, 165 kg, 30 km | Kormoran 1 per anno e testata; 23 km (Wikipedia) / 30 km (missilery) [agente] | ambiguità di variante |
| IR-7 | YJ-83 (navale `:1338`) | `warhead` 165 kg | 165 kg è la YJ-83K aviolanciata; la YJ-83 navale ha 190 kg [agente] | punteggio |
| IR-8 | RB-05E (`:2299`); RB-05A (`:2115`) | RB-05E: designazione; RB-05A: `seeker` 'electro-optical' | "Rb 05E" non trovato (solo un video DCS); Rb 05A = MCLOS radiocomandato, la TV era il prototipo Rb 05B [agente] | ambiguità di variante |
| IR-9 (nuova, mia) | RB-05A (`:2115`, campi a `:2127-2129`) | `"speed": 340, # m/s` e **`"max_speed": 1`** | — | [V] `WEAPON_PARAM['MISSILES_ASM']['max_speed']` "in m/s" (`Aircraft_Weapon_Data.py:47`): il punteggio dell'RB-05A conta 1 m/s; `speed` non è letto dagli scorer aerei |
| IR-10 | unità di `range` | gli agenti scrivono "non dichiarate, assunte km [S]" | — | **non è un'incoerenza** [V]: km dichiarati in `WEAPON_PARAM` (`Aircraft_Weapon_Data.py:46`, "in km"), nel commento "# Km" di 15 voci su 44, nella testata del registro navale (`Ship_Weapon_Data.py:1030-1035`: `caliber` mm, `range` km, `speed` m/s), e la fire control converte da km per aereo e nave (`Logic/Fire_Control.py:396-409`) |
| IR-11 | Kh-25MR (`:3523`) | commento "radar guided" | guida a radiocomando [agente] | solo commento |
| IR-12 | Kh-25MP / MPU (`:3626`, `:3597`) | `range` 18 / 30 km; `start_service` 1975 (commento "1978 --1982 vers. U") | 40 km (MP), 60 km (MPU); MPU "Entered service: 1990" (redstar) [agente] | portata |
| IR-13 | Kh-66 (`:3301`) | `warhead` 111 kg | 103 kg (FAS, airwar) [agente] | punteggio |
| IR-14 | Kh-58 (`:3272`) | `range` 250 (versione U) | dimensioni e portata pubblicate per il Kh-58E export (46-200 km) [principale per le dimensioni] | nessuno sulle dimensioni |
| IR-15 | RB-15F (`:2190`) / RB-15 (`:2479`) | `start_service` 1985 / 1989; RB-15 (navale/costiero) nel registro aereo | F operativo dal 1989, navale dal 1984-85: date invertite [agente] | disponibilità |
| IR-16 | Kh-31A (`:3981`), Kh-35 (`:4043`), Kh-41 (`:4074`) | `start_service` 1991, 1992, 2000 | 1988-89; 2003 (export 1996); 1993 [agente] | disponibilità |
| IR-17 | Kh-59 (`:3375`), KD-63 (`:4675`) | `range` 90; 180 | Kh-59 base 40 km (ru-wiki), 115 km il Kh-59M; KD-63 200-240 km [agente] | portata |
| IR-18 | AGM-45 (`:2219`) | `range` 10 | 16 km (A) / 40 km (B) [agente] | portata |
| IR-19 | 9M114 (`:2904`), 9M120-F (`:2776`) | `range` 7; 6 | 7 km è del 9M114M2; 9M120F 1-5,8 km [agente] | portata |
| IR-20 | AGM-114 (`:2639`) | `warhead` 9 kg con anno e portata della A/B/C | 9 kg è della K [agente] | punteggio |
| IR-21 (aggiornata con M1) | Kh-22N (`:3243`; campi a `:3243-3270` riletti il 2026-11-07 [V]) | commento "# radar antiship", `task` ['Anti_Ship'], `warhead` 1000 kg (il registro non dichiara il tipo di testata), `range` 330, una sola riga di efficacia `ship`; unico lanciatore il Tu-22M (`Aircraft_Loadouts.py:3471` [V]) | la **"N" è la versione nucleare a guida inerziale** per Wikipedia inglese [principale], GlobalSecurity ("Kh-22N with a nuclear warhead and inertial guidance") e Weapons Parade ("nuclear type ... designated as Kh-22N") [agente, M1]; la versione antinave convenzionale con radar attivo è la **Kh-22M/MA** (GlobalSecurity) e i 1.000 kg convenzionali sono attribuiti al "Kh-22" (Weapons Parade) [agente, M1]; per Wikipedia russa e airwar la Kh-22N ha l'autoguida radar attiva [agente, L6] | **nome della voce**: i campi del registro descrivono un antinave convenzionale (cioè la Kh-22M/MA delle fonti inglesi) sotto il nome Kh-22N. Nessun effetto sulla regola BI: la classe è per ruolo (`anti_ship`, D3.1 (a)), coerente con `task` e riga di efficacia. Da segnalare al manutentore dei registri (rinominare la voce o dichiararne la variante), **non** da correggere nel blocco 1; dimensioni nel §10.2 invariate (Ø 920 mm e 5.820 kg sono della cellula del Kh-22; che le varianti M e N non ne differiscano in modo rilevante è un'ipotesi [I]) |
| IR-22 | navali Moskit, YJ-18, YJ-12 | `caliber` 760, 540, 500 | Moskit 0,8 m (Wikipedia; 0,76 m è il dato del Kh-41 di testpilot); YJ-18 0,514 m (stima CSIS); YJ-12 0,5-0,6 m; YJ-12 portata 150-300 km o 200-500 km [agente] | `caliber` entra nel punteggio navale (`Ship_Weapon_Data.py:51`): **non** va toccato dal blocco 1 |

## 8. Voci senza dati sufficienti

| Voce | Cosa manca | Proposta (default dichiarato [S]) |
|---|---|---|
| KD-63B | tutto: nessuna fonte nomina la "B" (confermato da M1) | classe `cruise` per famiglia (KD-63); `ad_detectable` True (default `cruise`, BI `:965`); nessuna dimensione nel registro |
| KD-20 | dimensioni specifiche (solo intervallo della famiglia CJ-10: 514-750 mm, 1.090-2.500 kg) | `cruise` (fonte: "Air-launched cruise missile"); True; nessuna dimensione |
| Kh-555 | dimensioni (solo "conventional variant of the Kh-55" e "reduced radar cross-section") | `cruise`; True; nessuna dimensione |
| 9M120-F | ingombri specifici (celle vuote nella tabella delle varianti) | `tactical` per famiglia; False (default `tactical`); nessuna dimensione |
| RB-05E | la designazione stessa (confermato da M1) | `tactical` per famiglia Rb 05; False (approvata, §6.8); nessuna dimensione |
| Kh-65 | diametro (dedotto dalla famiglia) | `cruise`; True; solo `mass_kg` 1.650 (il test di coerenza la salta: serve la coppia) |
| RB-75T | diametro (non nella fonte) | flag fissato da BI-6; solo `mass_kg` 295 |
| YJ-18 | diametro (stima CSIS "likely approximates the 3M-54E"), massa (solo limite superiore "<1.579 kg") | `anti_ship`; True; **nessuna `mass_kg`** (un limite superiore non è una massa); **nessun `diameter_mm`**: la stima CSIS non è un dato della voce (D6 (a); senza massa la voce resterebbe comunque fuori dal test 5) |
| YJ-12 | valori della versione navale con booster | `anti_ship`; True; valori dell'aviolanciata (GlobalSecurity) con commento, come già nel §10.2; la voce non è nell'elenco D6 (a) (punto da confermare, §11) |

Per tutte, l'esito della regola non dipende dai dati mancanti: i `cruise` sono bersagli comunque, i `tactical` piccoli
non lo sono comunque, gli `anti_ship` grandi sono True per default di classe. **Decisione D6 = (a)** (2026-11-07):
nessuna dimensione di famiglia nel registro.

## 9. Decisioni per l'utente (tutte prese il 2026-11-07; testo delle opzioni lasciato come presentato)

### D1 — Quale Maverick è l'ancora e quale grandezza si confronta

| Ruolo | Esempio |
|---|---|
| lanciatore | Su-24M (porta Kh-25ML [V]) |
| colpo | 2 Kh-25ML (Ø 275 mm, 299-300 kg) |
| bersaglio dell'attacco | una fregata FFG-46 |
| intercettore / osservatore | la stessa FFG-46 (Phalanx, task `Anti_Missile`) |
| bersaglio del rilevamento | il Su-24M, poi i colpi |

La famiglia Maverick è "piccola" per decisione dell'utente (BI-6), ma le masse vanno da 209-220 kg (A/B, D) a 285 kg
(E) e 304-306 kg (F/G, K), sempre con 304,8 mm. BI §5.1 dice "diametro e massa".
- **(a) R1-D**: AGM-65D (304,8 mm; 220 kg), diametro **e** massa. Lettera della BI. Contro: 9 voci in zona grigia, e
  la regola mette in zona grigia anche AGM-65K e RB-75T, che la stessa BI-6 fissa False (incoerenza interna); il test 5
  non intercetta un AGM-88 o un Kh-25 scritti True per errore (massa > 220).
- **(b) R1-K**: inviluppo della famiglia fissata da BI-6 (304,8 mm; 306 kg o 304 kg), diametro **e** massa. Coerente con
  BI-6 (nessun membro fissato è "più grande" dell'ancora); da 3 a 6 voci in zona grigia; dipende da un valore non
  verificato (306) o crea il caso limite RB-05 (305 kg contro 304).
- **(c) R1-Ø, raccomandata** [S]: solo il diametro (304,8 mm, identico in tutta la famiglia: la domanda "quale
  Maverick" scompare). Motivi: il diametro è il dato più concorde fra le fonti (le masse discordano per Kh-25MR, LD-10,
  Kormoran, Sea Eagle, Vulkan, Kh-22N); è il sostituto più semplice della traccia radar frontale [I]; zona grigia bassa
  vuota; il test 5 intercetta ogni `tactical`/`arm` stretto scritto True per errore. Contro: cambia il testo di BI §2.5
  e del test 5 di BI §5.2 (`:931-946`); ignora che Kh-25MP e AGM-88 sono lunghi e pesanti.

**Esempio numerico** (Kh-25ML): (a) 275 ≤ 304,8 ma 300 > 220 -> zona grigia, l'utente approva False; (b) 300 ≤ 306 ->
False obbligatorio; (c) 275 ≤ 304,8 -> False obbligatorio. Se un errore di trascrizione scrivesse
`'ad_detectable': True` sul Kh-25ML: (a) il test 5 passa (massa > 220), il motore farebbe fermare i Kh-25ML dal Phalanx;
(b) e (c) il test fallisce. In tutti i casi il flag proposto è False.
Sotto-domanda: **lunghezza fuori dal metro** (§5, raccomandato).

scelta utente: **(b) R1-K** (2026-11-07): "non maggiore del Maverick" se diametro ≤ 304,8 mm **e** massa ≤ **304 kg**
(inviluppo della famiglia fissata False da BI-6; 304 kg = colonna F/G di d-s, verificata; i 306 kg di Wikipedia per il
K non sono verificati con fonte primaria, anche dopo M1). **Lunghezza esclusa** dal metro. Applicazione: §5; voci in
zona grigia: AGM-88, Kh-25MP, Kh-25MPU, RB-05A, RB-05E (approvate False) e Kormoran sul bordo alto (True), §6.

### D2 — Il Mistral (SAM portatile nel registro A2G)

| Ruolo | Esempio |
|---|---|
| lanciatore | nessun aereo dei loadout lo porta [V]; ipotesi: un elicottero con la versione ATAM |
| colpo | 2 Mistral (Ø 90 mm, 19,7 kg) |
| bersaglio dell'attacco | una motovedetta (il Mistral ha la riga `ship` [V]) |
| intercettore / osservatore | la motovedetta, se ha un'arma `Anti_Missile` |
| bersaglio del rilevamento | l'elicottero |

- **(a) `tactical` con `ad_detectable` False, raccomandata**: è la trattazione già accettata in BI §1.5 (`:225-226`,
  "escluso, tattico, piccolo; da segnalare al manutentore"); nessun cambio al test 1 del blocco 1; anomalia IR-5
  rimandata alla manutenzione dei registri.
- **(b) `sam` dichiarato nel registro**: semanticamente esatto (L2 contesta `tactical`); costa aggiungere `'sam'`
  all'insieme ammesso del test 1 di BI §5.2 (`:927`); la fire control del blocco 2 lo gestisce già
  (`AD_TARGET_DOMAINS.get('sam', set())` = vuoto, BI `:962`, `:971-973`).
- **(c) togliere o spostare la voce** fuori da `MISSILES_ASM`: fuori perimetro (tocca scorer e `_WEAPON_PARAM_TYPE`,
  `Aircraft_Weapon_Data.py:190`).

**Esempio**: con (a) e (b) i `intercept_domains` del Mistral sono entrambi vuoti: la motovedetta non lo ferma mai.
L'effetto nel motore è identico; cambia solo l'etichetta.

scelta utente: **(a)** (2026-11-07): Mistral `tactical`, `ad_detectable` False; anomalia IR-5 da segnalare al
manutentore dei registri.

### D3 — Casi limite della BI (tre sotto-decisioni)

#### D3.1 — Kh-22N: `anti_ship` o `cruise` (M1 del rapporto di revisione)

| Ruolo | Esempio |
|---|---|
| lanciatore | Tu-22M (unico lanciatore del Kh-22N [V]) |
| colpo | 2 Kh-22N (Ø 920 mm, 5.820 kg) |
| bersaglio dell'attacco | una nave da trasporto in porto |
| intercettore / osservatore | la nave stessa (se ha CIWS) e un Tor a terra della stessa Operazione (difesa di dominio) |
| bersaglio del rilevamento | il Tu-22M |

Fatto nuovo [V]: il Kh-22N ha **solo** la riga di efficacia `ship` (§2.2), quindi la fire control **non lo usa mai
contro un bersaglio terrestre**: il caso M1 della BI (§2.3 `:387`, §5.1 `:899-906`: Kh-22N contro un bersaglio
terrestre) **non può accadere** con i registri attuali. La classe conta solo nella difesa di dominio: un intercettore
terrestre nel dominio di una nave attaccata.
- **(a) `anti_ship`, raccomandata**: classe per **ruolo**, come il `task` del registro e il commento "# radar
  antiship" (`:3243` [V]); coerente con gli altri "anti-ship cruise missile" delle fonti (Granit, Moskit, Vulkan, Kh-41,
  Sea Eagle, Kh-35, RB-15, YJ-12/18/83), tutti `anti_ship`. Con (a): `intercept_domains` = {naval}; il Tor non lo ferma.
- **(b) `cruise`**: classe per **profilo di volo** (entrambe le Wikipedia la chiamano "cruise missile"). Con (b):
  {land, naval}; il Tor può fermarlo se L1 e R-INT lo consentono. Per coerenza (b) imporrebbe di riclassificare
  `cruise` anche gli altri antinave "cruise", che diventerebbero bersagli dei terrestri nella difesa di dominio.

scelta utente: **(a)** (2026-11-07): Kh-22N `anti_ship`. Dopo M1 resta l'anomalia di designazione ("N" = nucleare per
due fonti nuove, contro `task` Anti_Ship e 1.000 kg del registro): §7, IR-21; la classe per ruolo non ne dipende.

#### D3.2 — KD-63: piattaforma corretta, classe confermata

| Ruolo | Esempio |
|---|---|
| lanciatore | bombardiere H-6 (secondo GlobalSecurity, non verificato); nessun lanciatore nei loadout [V] |
| colpo | 2 KD-63 (760 mm, ~2.000 kg, non verificati) |
| bersaglio dell'attacco | un deposito |
| intercettore / osservatore | un Buk della stessa forza |
| bersaglio del rilevamento | l'H-6 |

L6 corregge BI §2.2 (`:352-353`, ora corretta): il KD-63 (e per famiglia il KD-63B) **non** è un cruise "anche da cacciabombardieri", ma
solo da bombardiere. Con BI-2 (a) ("la categoria vince") la classe resta `cruise` e il Buk può fermarlo. Il caso vero di
cruise da cacciabombardiere resta il **Kh-59** (Su-30, Su-34 [V]), usato in S35 `land_cruise`.
- **(a) prendere atto, `cruise`, raccomandata**; correggere la frase di BI §2.2 nel blocco 4.
- **(b)** rinviare KD-63/KD-63B alla seconda ricerca (D5) prima del blocco 1: nessun effetto pratico (nessun
  lanciatore).

scelta utente: **(a)** (2026-11-07): KD-63 e KD-63B restano `cruise` (solo da bombardiere H-6); la frase di BI §2.2 che
li dice lanciabili anche da cacciabombardieri è corretta nella BI il 2026-11-07 (non più nel blocco 4). M1 ha riletto
GlobalSecurity ("only the H-6 bomber") senza trovare una seconda fonte.

#### D3.3 — ARM grandi (Kh-58, Kh-31P) e tattici grandi (Kh-29): `ad_detectable` True

| Ruolo | Esempio Kh-29 | Esempio Kh-58 |
|---|---|---|
| lanciatore | Su-25T [V] | Su-24M [V] |
| colpo | 2 Kh-29T (380 mm, 685 kg) | 2 Kh-58 (380 mm, 650 kg) |
| bersaglio dell'attacco | una corvetta | il radar di un S-300PS a terra |
| intercettore / osservatore | la corvetta (SA-N-9, AK-630) | l'S-300PS e un Tor (terrestri); una nave della stessa Operazione in porto (navale) |
| bersaglio del rilevamento | il Su-25T | il Su-24M |

- **(a) True, raccomandata**: è imposto dalla regola (2) del metro (diametro e massa sopra l'Harpoon) e dal test 5 del
  blocco 1. Kh-29T contro la corvetta: `intercept_domains` = {naval}, la corvetta ne ferma fino a min(canali liberi,
  scorta), come oggi. Kh-58 contro l'S-300PS: le difese terrestri non lo fermano (BI-3, BI-12); la nave in porto sì
  (BI-5 (a)). Il Kh-58 e il Kh-31P hanno solo la riga `Air_Defense` [V]: non sono mai lanciati contro navi.
- **(b) False per eccezione** ("un ARM non è mai bersaglio"): contraddice BI-6 (a) (criterio di dimensione per i
  navali) e richiede una lista di eccezioni nel test 5; per i Kh-29 toglierebbe alle navi un bersaglio grande e
  frequente nei loadout (6 aerei: MiG-27K, Su-24M, Su-25T, Su-25TM, Su-30, Su-34 [V]).

scelta utente: **(a)** (2026-11-07): Kh-29L/T/TE, Kh-58, Kh-31P `ad_detectable` True (regola (2)).

### D4 — Valori da usare quando le fonti discordano

| Ruolo | Esempio |
|---|---|
| lanciatore | F/A-18C (porta AGM-84A [V]) / nessun lanciatore per Kh-35 e Kormoran [V] |
| colpo | AGM-84A (ancora), Kh-35, Kormoran |
| bersaglio dell'attacco | un Arleigh Burke |
| intercettore / osservatore | l'Arleigh Burke |
| bersaglio del rilevamento | l'F/A-18C |

**D4.1 Massa dell'ancora Harpoon (M_H)**:
- **(a) 515,25 kg (FAS, aviolanciato, verificato), raccomandata**: è la massa della voce AGM-84A stessa; Kh-35 (520 kg)
  T!.
- (b) 556 kg (testo CSIS, verificato): Kh-35 e la stessa AGM-84A finirebbero in zona grigia (515,25 < 556): l'ancora non
  soddisfa la propria regola.
- 691 kg non è candidabile: è il RGM/UGM con booster (altro missile, voce navale).
D_H = 343 mm (concorde in tutte le fonti).

**D4.2 Valore da scrivere in `diameter_mm`/`mass_kg` per le voci con fonti discordi** (Kormoran 340/344 mm e 600/660
kg; Kh-22N 900-920 mm e 5.635-5.820 kg; Vulkan 7.000-8.000/4.800 kg; LD-10 200/234 kg; Kh-25MR 300/320 kg; AGM-65K
304/306 kg; Moskit 760/800 mm; RB-04E 600/625 kg; Sea Eagle 580-730 kg):
- **(a) raccomandata** [S]: nell'ordine, (1) il valore verificato dal principale; (2) quello della fonte più specifica
  per la variante a registro; (3) a parità, il valore più vicino al confine del metro (il più basso per le voci True, il
  più alto per le False), così il test è il più severo possibile; l'altro valore nel commento. Per i missili con booster
  la massa senza booster, se la fonte la dà.
- (b) sempre il valore più vicino al confine, anche se meno verificato o meno specifico.
- (c) non scrivere la grandezza quando le fonti differiscono di oltre il 5% [S]: il test salta la voce.

**Esempio numerico**: Kormoran con (a) = 340 mm (stessa specificità, voce True -> il più basso) e 600 kg (Wikipedia,
specifica del Kormoran 1): regola (2) non soddisfatta (340 < 343), ma il test 5 verifica la regola (2) solo sulle voci
False, quindi passa; il flag resta True. Kh-22N con (a) = 920 mm e 5.820 kg (Wikipedia inglese, verificata). Nessun flag
cambia con (a), (b) o (c). I valori risultanti con (a) sono nel §10.2.

scelta utente: **D4.1 = (a)** (2026-11-07): massa dell'ancora Harpoon 515,25 kg, D_H = 343 mm. **D4.2 = (a)**: per i
valori discordi, (1) il valore verificato dal principale, (2) la fonte più specifica per la variante a registro, (3) a
parità il valore più vicino al confine del metro (il più basso per le True, il più alto per le False); l'altro valore
nel commento. Applicata a tutte le 52 voci nel §10.2 (valori cambiati rispetto alla stesura precedente: §10.2, nota
"Valori cambiati").

### D5 — Seconda ricerca (V4 Pro) sulle voci a confidenza B o discordi

| Ruolo | Chi |
|---|---|
| ricercatore | `oc-researcher` con DeepSeek V4 Pro (prova di metodo: 0,1632 $ per 3 missili, `Rapporti/Costi_Deleghe.md:24`) |
| voci | quelle in cui un dato può cambiare una classe o un passaggio del test |
| verificatore | la sessione principale, sul testo delle pagine |

- **(a) nessuna seconda ricerca, raccomandata se D1 = (c)**: con il solo diametro nessuna voce è vicina al confine basso
  e nessuna proposta dipende da masse discordi; le voci deboli (Kh-555, KD-20, KD-63B, 9M120-F, RB-05E, YJ-12, YJ-18,
  Vulkan) restano al default di classe, che dà lo stesso esito.
- **(b) ricerca mirata** su 6-8 voci: Kh-25MR, RB-05A/E, LD-10, AGM-65K (306 kg), Kormoran (diametro), Kh-22N
  (designazione e massa della N), KD-63 (fonte non raggiungibile dal principale). Raccomandata se D1 = (a) o (b). Costo
  stimato [S]: ~0,4-0,5 $ (proporzione dalla prova, 0,054 $ per missile; non è un preventivo).
- **(c) verifica a mano del principale** di un campione delle 40 voci "solo agente" (per esempio 5 a caso più le 9
  della zona grigia), senza nuova ricerca: tempo della sessione principale, nessun costo di delega.
Le opzioni (b) e (c) si possono combinare; nessuna è necessaria per il blocco 1 se l'utente approva i default.

scelta utente: **(b)** (2026-11-07), **eseguita**: ricerca mirata M1 su 7 voci, V4 Pro, 0,371 $ (§2.4). Verificati dal
principale: Kh-25MR 299 kg / 275 mm (missilery.info; i 320 kg di ru-wiki respinti), RB-05A 305 kg (AEF) e 304 kg
(Astronautix) / 300 mm. Non risolti: massa dell'AGM-65K (solo Wikipedia, 306 kg), LD-10 (200/234 kg, 200/203 mm),
KD-63 (fonte unica GlobalSecurity), KD-63B e Rb 05E (inesistenti nelle fonti storiche). Kormoran 1: 600 kg (tre
fonti), 340/344 mm. Kh-22N: Ø 920 mm; "N" = nucleare per due fonti (§7, IR-21).

### D6 — Voci senza dati: dimensioni di famiglia sì o no

| Ruolo | Esempio |
|---|---|
| lanciatore | nessuno nei loadout [V] |
| colpo | KD-63B (nessun dato proprio) |
| bersaglio dell'attacco | un deposito |
| intercettore / osservatore | un Buk |
| bersaglio del rilevamento | il lanciatore |

- **(a) raccomandata**: classe per famiglia [S], flag = default di classe (BI `:965`), **nessuna dimensione** nel
  registro se la fonte non è della voce (KD-63B, KD-20, Kh-555, 9M120-F, RB-05E; diametro di Kh-65 e RB-75T; massa
  dello YJ-18). Il test 5 salta le voci senza la coppia diametro-massa.
- (b) scrivere i valori di famiglia con commento "di famiglia [S]": il test 5 lavorerebbe su dati non della voce.
**Esempio**: KD-63B con (a): `munition_class` 'cruise', `ad_detectable` True, nessun `diameter_mm`; il Buk può fermarlo
(cruise). Con (b): in più 760 mm e 2.000 kg del KD-63; esito identico.

scelta utente: **(a)** (2026-11-07): KD-63B, KD-20, Kh-555, 9M120-F, RB-05E con classe per famiglia e nessuna
dimensione; Kh-65 e RB-75T senza diametro; YJ-18 senza massa (e senza diametro, che è solo una stima CSIS: lettura di chi scrive, coerente con la stesura del
§10.2 presentata all'utente, da confermare, §11). Il test 5
salta le voci senza la coppia diametro-massa.

## 10. Piano d'uso nel blocco 1 della BI

### 10.1 Come i dati entrano nei registri

Il blocco 1 resta quello della BI §5.2 (`:908-949`), con questi dati:
- `munition_class` (str) e `ad_detectable` (bool) su **tutte le 52 voci**, dalla tabella del §10.2 (anche sui `cruise`,
  dove il flag non è letto dal motore: la BI-12 e la tabella `AD_TARGET_DOMAINS` li ammettono comunque; scriverlo rende
  il test 5 applicabile anche a loro). Commento per voce: `# STIMA [S]: <fonte breve>, Proposta_Dati_Bersagli_Intercettabili.md`.
- Famiglia Maverick (AGM-65D, AGM-65K, RB-75T): `'ad_detectable': False` con il commento della decisione BI-6 (BI
  `:916-918`), non `STIMA`.
- `diameter_mm` e `mass_kg` dove il §10.2 li dà; **nessun `length_m`** (D1, sotto-domanda: la lunghezza non entra nel
  metro).
- **Cosa non entra nel registro**: URL ed estratti (restano qui e nelle bozze), RCS ("non pubblicata"), lunghezze,
  correzioni delle incoerenze del §7, modifiche a `caliber` delle voci navali (entra nel punteggio,
  `Ship_Weapon_Data.py:51` e `:810` [V]: `diameter_mm` si aggiunge accanto, anche quando coincide).
- Gli scorer aerei e navali iterano sulle chiavi di `WEAPON_PARAM`, non su quelle della voce
  (`Aircraft_Weapon_Data.py:531`, `:612`, `:669`, `:733`, `:760`; `Ship_Weapon_Data.py:810` [V]): un campo nuovo non li
  tocca. La verifica completa resta all'esecutore (BI `:923-925`).
- **Test 5** (decisione D1 = R1-K; dettaglio e motivazione nel §5.3): sta in `Test/Test_Aircraft_Weapon_Data.py` e
  legge **entrambi** i registri (`AIR_WEAPONS['MISSILES_ASM']` e `SHIP_WEAPONS['MISSILES_ASM']`, importato da
  `Asset/Ship_Weapon_Data.py`) [scelta di piano, S]: le voci grigie approvate sono aeree e la regola (1) va controllata
  anche sulle navali. Costanti scritte nel test con la fonte (commento "STIMA [S]: ancore del metro, Proposta_Dati_...
  §5.1"): `D_M = 304.8` (FAS), `M_M = 304` (d-s, colonna F/G), `D_H = 343` (FAS), `M_H = 515.25` (FAS) e
  `GREY_ZONE_APPROVED` (6 voci, §5.3). Asserzioni, solo sulle voci con **entrambi** `diameter_mm` e `mass_kg` salvo (3a):
  (1) nessuna voce True con `diameter_mm <= D_M` e `mass_kg <= M_M`; (2) nessuna voce False con `diameter_mm >= D_H` e
  `mass_kg >= M_H`; (3a) ogni voce di `GREY_ZONE_APPROVED` esiste nel registro aereo e ha `ad_detectable` presente e
  uguale al valore approvato; (3b) l'insieme delle voci con la coppia che non soddisfano né la condizione di (1) né
  quella di (2) è uguale a `{'AGM-88', 'Kh-25MP', 'Kh-25MPU', 'RB-05A', 'Kormoran'}`. È il testo che sostituisce il test 5
  di BI §5.2 (`:931-946`), aggiornato nella BI.

### 10.2 Valori da scrivere nel blocco 1 (decisi il 2026-11-07: D1 (b) R1-K, D2 (a), D3.1 (a), D3.2 (a), D3.3 (a), D4.1 (a), D4.2 (a), D5 (b) con M1, D6 (a))

Regola D4.2 (a) applicata a tutte le voci con fonti discordi: (1) valore verificato dal principale; (2) fonte più
specifica per la variante a registro; (3) a parità, il valore più vicino al confine (il più basso per le True, il più
alto per le False); l'altro valore va nel commento della voce. L'esito del metro per ogni voce è nel §5.2.

| Voce | `munition_class` | `ad_detectable` | `diameter_mm` | `mass_kg` | Fonte del valore scritto (criterio D4.2; altro valore per il commento) |
|---|---|---|---|---|---|
| AGM-65D | tactical | False (BI-6) | 304.8 | 220 | FAS; d-s [principale] (criterio 3, entrambi verificati; 218,25 FAS) |
| AGM-65K | tactical | False (BI-6) | 304.8 | 304 | FAS; d-s colonna F/G [principale] (criterio 1; 306 Wikipedia, non verificato) |
| RB-75T | tactical | False (BI-6) | — | 295 | Robotmuseum [principale] |
| AGM-114 | tactical | False | 180 | **45.7** | Ø Wikipedia (criterio 3; 178 d-s, stesso 7 in); massa d-s colonna AGM-114B/C (criterio 2: variante A/B/C del registro; 45-49 Wikipedia, famiglia) |
| BGM-71D | tactical | False | 152 | 21.5 | Wikipedia, FAS |
| 9M114 | tactical | False | 130 | 31.4 | Wikipedia (missile senza tubo) |
| 9M120 | tactical | False | 130 | 49.5 | Wikipedia |
| 9M120-F | tactical | False | — | — | (default, §8) |
| Hot-3 | tactical | False | 150 | 24.5 | Wikipedia (riga HOT-3) |
| Mistral | tactical | False | 90 | 19.7 | Wikipedia |
| Kh-25ML | tactical | False | 275 | 300 | FAS (criterio 3; 299 Wikipedia) |
| Kh-25MR | tactical | False | 275 | **299** | missilery.info [principale, M1] (criterio 1; 300 Astronautix; 320 ru-wiki respinto) |
| Kh-66 | tactical | False | 275 | 290 | airwar (criterio 3; 278 FAS) |
| Kh-29L | tactical | True | 380 | 660 | Wikipedia [principale] |
| Kh-29T | tactical | True | 380 | 685 | Wikipedia [principale] |
| Kh-29TE | tactical | True | 380 | 690 | Wikipedia [principale] |
| AGM-45 | arm | False | 203 | 177 | Wikipedia, d-s |
| AGM-88 | arm | False | 254 | 361 | Wikipedia [principale] |
| Kh-58 | arm | True | 380 | 650 | KTRV (Kh-58E), Wikipedia [principale] |
| Kh-31P | arm | True | 360 | 600 | Rosoboronexport, Wikipedia |
| Kh-25MP | arm | False | 275 | 320 | FAS (criterio 3; 315 Wikipedia e ru-wiki) |
| Kh-25MPU | arm | False | 275 | 315 | redstar.gr |
| LD-10 | arm | False | **200** | **200** | zh-wiki, GlobalSecurity (criterio 2: portata 80 km come il registro; 203 mm, 234 kg Deagel, che dà 60 km) |
| RB-05A | tactical | False | 300 | 305 | AEF [principale, M1], Wikipedia en/sv (criterio 3, entrambi verificati; 304 Astronautix [principale]); Ø Astronautix [principale, M1], Wikipedia |
| RB-05E | tactical | False | — | — | (default, §8) |
| AGM-84A | anti_ship | True | 343 | 515.25 | FAS [principale] |
| RB-04E | anti_ship | True | 500 | 625 | Robotmuseum (scheda della E) |
| RB-15 | anti_ship | True | 500 | 568 | Robotmuseum, Wikipedia (senza booster) |
| RB-15F | anti_ship | True | 500 | 565 | Robotmuseum (scheda della F) |
| Kormoran | anti_ship | True | 340 | 600 | Ø missilery, CMANO "0.34" (criterio 3; 344 Wikipedia, GlobalMilitary); massa Wikipedia, GlobalMilitary, CMANO, Kormoran 1 (M1; 660 missilery) |
| Sea Eagle | anti_ship | True | 400 | 580 | Wikipedia (criterio 3; 600-730 missilery) |
| Kh-31A | anti_ship | True | 360 | 610 | Wikipedia, missilery |
| Kh-35 | anti_ship | True | 420 | 520 | Wikipedia, versione aerea [principale] |
| Kh-41 | anti_ship | True | 760 | 3950 | testpilot (scheda del Kh-41), airwar (criterio 2; 800 mm, 4.500 kg Wikipedia) |
| Kh-22N | anti_ship | True | 920 | 5820 | Wikipedia inglese [principale] (criterio 1; Ø anche Weapons Parade, M1; 5.635-5.900 kg secondo variante e fonte); nome della voce: §7 IR-21 |
| Kh-55 | cruise | True | 514 | 1210 | CSIS |
| Kh-555 | cruise | True | — | — | (default, §8) |
| Kh-101 | cruise | True | 510 | 2300 | CSIS (criterio 3; 2.400 Wikipedia) |
| Kh-65 | cruise | True | — | 1650 | Wikipedia (Kh-65SE) |
| KD-20 | cruise | True | — | — | (default, §8) |
| Kh-59 | cruise | True | 380 | 760 | ru-wiki, Kh-59 base (criterio 3; 790 stessa fonte) |
| Kh-59M | cruise | True | 380 | 930 | ru-wiki |
| KD-63 | cruise | True | 760 | 2000 | GlobalSecurity (fonte unica, riletta dall'agente in M1, non verificata dal principale) |
| KD-63B | cruise | True | — | — | (default, §8) |
| RGM-84-Harpoon | anti_ship | True | 343 | 691 | Wikipedia, con booster [principale] (criterio 1; nessuna fonte senza booster; 661,5 FAS, 690 d-s) |
| BGM-109-Tomahawk | cruise | True | 520 | 1300 | Wikipedia, senza booster (criterio 3; 1.315) |
| P-700-Granit | anti_ship | True | 850 | 7000 | Wikipedia |
| P-270-Moskit | anti_ship | True | 800 | 4150 | Wikipedia, sezione 3M-80E (criterio 2; 4.500 infobox, 3.970 3M-80E1) |
| P-1000-Vulkan | anti_ship | True | 880 | 7000 | ru-wiki (criterio 3 sull'intervallo 7.000-8.000; 4.800 sospetta copia del P-500, non specifica) |
| YJ-12 | anti_ship | True | 500 | 2000 | GlobalSecurity, versione aviolanciata (criterio 3; 0,6 m e ~3 t zh-wiki, "stimati") |
| YJ-18 | anti_ship | True | — | — | (§8 e D6 (a): stima e limite superiore, non scritti) |
| YJ-83 | anti_ship | True | 360 | 800 | Wikipedia |

**Totali**: **32 True, 20 False**; `munition_class` scritta su tutte le 52 voci (10 `cruise`, 17 `anti_ship`, 7 `arm`,
18 `tactical`); **44** voci con `diameter_mm`, **46** con `mass_kg` (in più Kh-65 e RB-75T, solo massa), **44** con la
coppia (quelle su cui girano le regole (1), (2) e (3b) del test 5): 27 True e 17 False. Senza la coppia: 8 voci
(RB-75T, 9M120-F, RB-05E, Kh-555, Kh-65, KD-20, KD-63B, YJ-18). Conteggi invariati rispetto alla stesura precedente.

**Controllo a mano del test 5 con D1 = R1-K** (§5.3): fra le True con la coppia il diametro minimo è 340 mm (Kormoran)
> 304,8, quindi la regola (1) passa (nessuna True "non maggiore del Maverick"); fra le False con la coppia il diametro
massimo è 304,8 mm (AGM-65D, AGM-65K) < 343 e la massa massima 361 kg (AGM-88) < 515,25, quindi la regola (2) passa.
Esiti con la coppia: 13 F! (tutte False), 26 T! (tutte True), 5 ZG = AGM-88, Kh-25MP, Kh-25MPU, RB-05A (False) e
Kormoran (True), esattamente le voci con la coppia di `GREY_ZONE_APPROVED`: la (3b) passa; la (3a) passa con i flag di
questa tabella (RB-05E False compreso). Il test 5 passa.

**Valori cambiati rispetto alla stesura precedente di questa tabella** (nessun flag cambia):

| Voce | Campo | Prima | Ora | Motivo |
|---|---|---|---|---|
| Kh-25MR | `mass_kg` | 320 (ru-wiki) | **299** | D5 (b): ricerca M1, valore di missilery.info verificato dal principale; D4.2 (a) criterio 1. Effetto: da ZG (con R1-K) a F! |
| LD-10 | `diameter_mm` | 203 (Deagel) | **200** | D4.2 (a) criterio 2: zh-wiki e GlobalSecurity descrivono la variante con la portata del registro (80 km); prima era stato scelto il valore più vicino al confine (criterio 3), che viene dopo |
| LD-10 | `mass_kg` | 234 (Deagel) | **200** | come sopra; F! con entrambi i valori |
| AGM-114 | `mass_kg` | 49 (Wikipedia, famiglia) | **45.7** | D4.2 (a) criterio 2: d-s dà la massa della colonna AGM-114B/C, la variante dell'anno e della portata del registro; F! con entrambi i valori |

Fonti cambiate senza cambio di valore: RB-05A (AEF e Astronautix, M1, verificate dal principale), Kormoran (massa con
tre fonti, M1), Kh-22N (diametro anche da Weapons Parade, M1), KD-63 (fonte riletta da M1, sempre unica).

**Alternative non scelte** (traccia): D2 (b) avrebbe dato Mistral `sam` e `'sam'` nell'insieme del test 1; D3.1 (b)
Kh-22N `cruise`; D3.3 (b) Kh-29/Kh-58/Kh-31P False con eccezioni nel test 5; D6 (b) i valori di famiglia.

### 10.3 Test, conteggi ed esito atteso

- Test del blocco 1: i **6** di BI §5.2 (`:926-948`), invariati nel numero. Il test 5 ha il testo aggiornato (§10.1:
  `M_M = 304`, elenco `GREY_ZONE_APPROVED` e asserzione (3)); il test 1 resta invariato (D2 (a)). Test 3 ("classi
  approvate") usa la colonna `munition_class` del §10.2.
- Test del blocco 2 (BI §5.3.5): nessuno dipende da una scelta di questo documento; i casi citati (AGM-65D/K vuoti,
  Kh-55/Kh-101/Kh-59 terrestre e navale, AGM-84A navale, AGM-88 vuoto, RGM-84 navale, Tomahawk entrambi) sono coerenti
  con il §10.2.
- Scenario S35-ADTGT (BI §5.4): usa AGM-65D, Kh-59, AGM-84A, tutti con classe e flag invariati dalle decisioni.
- **Esito atteso**: suite + 6 test, tutti OK; **confronto con la fotografia: tutte le esecuzioni identiche** (1009 alla
  data della BI), perché la fire control non legge i campi nuovi fino al blocco 2 e il blocco 2 è dietro
  `BI_AD_TARGET_RULE = False`. Nessuna esecuzione nuova in questo blocco. Con l'interruttore acceso (sonda B-1, dopo il
  blocco 2) l'atteso resta quello di BI §5.3.6: cambiano solo le 6 esecuzioni S19AD `tor_rear` (AGM-65D, `tactical`
  False).
- Nessuna estrazione RNG, nessun interruttore nuovo: sono dati.

### 10.4 Documenti da aggiornare dopo le decisioni

- `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`: **aggiornata il 2026-11-07** insieme a questo documento: §2.2
  (esito del blocco 0; KD-63/KD-63B solo da bombardiere H-6), §2.3 e §5.1 (Kh-22N `anti_ship`, mai lanciato contro
  bersagli terrestri [V]), §2.5 (metro R1-K, lunghezza esclusa), §5.2 (test 5), blocco 0 segnato come eseguito.
- `Manuale_Motore_DES/10_Limiti_Estensioni_Divergenze.md` (blocco 4 della BI): classificazione stimata, metro sulle
  dimensioni senza RCS, cruise "stealth" (Kh-101, Kh-555) trattati come rilevabili.
- `Piano_Implementazione_Missione.md`, `F4_Differenze_Scenari.md`: nessun cambio per questo blocco (nessuna esecuzione
  cambiata); le righe arrivano con i blocchi 2 e 3 della BI.

## 11. Rischi e cosa non è stato verificato

- **38 voci su 52 solo dall'agente** (dopo M1): i valori sono riportati con URL ed estratto, ma gli estratti non sono
  sempre letterali e nessuno li ha riletti. Con D1 = R1-K le voci vicine ai confini sono AGM-65K (304 kg, sul confine:
  valore verificato), RB-05A (305 kg, 1 kg sopra: verificato dopo M1), Kh-25MR (299 kg: verificato dopo M1), Kormoran
  (340 mm, 3 mm sotto `D_H`: solo agente, ma flag approvato a mano) e AGM-84A (ancora); per le voci grigie il flag è
  comunque un'approvazione dell'utente, non un esito del metro. Il rischio resta per le classi (Mistral, Kh-22N) e per le
  incoerenze del §7, che vanno riverificate prima di correggere il registro.
- **Non risolti dopo M1**: massa propria dell'AGM-65K (306 kg solo Wikipedia; non usata), LD-10 (200/234 kg, 200/203 mm:
  F! con entrambi), KD-63 (fonte unica), KD-63B e Rb 05E (designazioni senza fonti storiche).
- **Kh-22N**: il nome della voce indica, per tre fonti in inglese, la versione nucleare, mentre i campi descrivono un
  antinave convenzionale (§7, IR-21). La classe `anti_ship` non ne dipende; il nome va sistemato nella manutenzione dei
  registri.
- **Lettura di D6 per lo YJ-18**: la decisione D6 (a) cita la sola massa; questo documento non scrive neanche il
  diametro (514 mm è una stima CSIS "likely approximates the 3M-54E", non un dato della voce), come nella stesura del
  §10.2 presentata all'utente. Senza massa la voce è comunque fuori dal test 5: nessun effetto. Da confermare.
- **YJ-12**: non è nell'elenco D6 (a); il §10.2 gli dà i valori della versione aviolanciata (GlobalSecurity, fonte
  giudicata poco affidabile da L7). Nessun effetto sul flag (T! con qualunque valore trovato). Da confermare.
- **Bozza M1**: l'intestazione dichiara "V4.1 Flash", il modello effettivo è V4 Pro (registro dei costi).
- **Fonti deboli**: airwar.ru letto solo nei numeri, Wikipedia come unica fonte di molte voci, GlobalSecurity
  irraggiungibile per il principale (KD-63), pagine CSIS e FAS in parte assenti (404). Fonti primarie solo per Kh-31P
  (Rosoboronexport), Kh-58E (KTRV archiviata), Mistral 3 (MBDA, variante diversa dal registro).
- **Varianti**: il registro spesso non identifica la variante (AGM-114, Kormoran, Kh-58U contro Kh-58E, Kh-22N, YJ-12
  navale con booster, RB-05E); le dimensioni scelte sono quelle della variante più coerente con i campi del registro,
  per deduzione dell'agente.
- **Metro senza RCS**: il diametro (o la massa) sostituisce la traccia radar [S]; i cruise a bassa osservabilità
  (Kh-101, Kh-555) risultano "rilevabili" per taglia. Limite dichiarato, da riportare nel manuale.
- **Flag binario**: nessuna gradazione della probabilità di rilevamento del colpo (BI §2.5, estensione futura).
- **Incoerenza I-1 della BI** (stesso missile rilevabile dai navali e non dai terrestri): accettata con BI-12 (a); i dati
  la rendono concreta per Kh-29, Kh-58, Kh-31P (True per i navali, mai bersagli dei terrestri).
- **Non verificato da chi scrive**: nessun valore esterno (questo documento è scritto senza web); i valori marcati
  "principale" sono quelli dichiarati riletti dalla sessione principale; il valore di plausibilità del KD-63 è
  conoscenza generale [I]. Verificato nel repository [V]: righe e campi delle 52 voci (la voce Kh-22N riletta di nuovo
  il 2026-11-07 per IR-21), lanciatori nei loadout, righe di efficacia, unità dei registri, scorer, assenza di
  Brimstone/Vikhr/APKWS, import dei moduli di test dei registri (`Test/Test_Aircraft_Weapon_Data.py:98`,
  `Test/Test_Ship_Weapon_Data.py:84`). Le sonde sono state
  eseguite in sola lettura con l'interprete del ProArt e non sono versionate (lettura dei dizionari dei registri e di
  `AIRCRAFT_LOADOUTS`).
