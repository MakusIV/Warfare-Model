# Guida concettuale al motore DES — Bibliografia verificata (fase A2)

**Data: 2026-11-19.**

> **Avvertenza: bibliografia verificata dall'agente il 2026-11-19, da ricontrollare dal responsabile.**
> «Verificata» significa che l'esistenza dell'opera e i dati di citazione sono stati riscontrati su almeno una
> fonte web affidabile (registro DOI/Crossref, catalogo di biblioteca o di editore, pagina dell'ente che
> pubblica) e che l'URL è riportato. **Non** significa che l'agente abbia letto le opere: i giudizi di
> pertinenza si basano su titolo, sommario o abstract effettivamente consultati; dove un'affermazione sul
> contenuto non è stata riscontrata lo si dice. Nessun capitolo o pagina è citato a memoria: i numeri di
> pagina riportati sono quelli dei registri (Crossref, cataloghi) o di un sommario aperto.

Convenzioni: **ISBN/DOI** = identificativo; **Verifica** = dove è stato riscontrato; **Perché** = pertinenza al
motore (simulazione a eventi di sessioni di combattimento, rilevamento, salve, riproducibilità, VV&A).
Per Crossref l'URL di controllo è `https://api.crossref.org/works/<DOI>`; il link per il lettore è
`https://doi.org/<DOI>`. «OL» = Open Library (catalogo bibliotecario aperto), `https://openlibrary.org/isbn/<ISBN>`.

---

## 1. Fondamenti della simulazione a eventi discreti

**Opera consigliata a un responsabile non tecnico: 1.1 (Robinson).**

**1.1 ★ Robinson, S. — *Simulation: The Practice of Model Development and Use*, 2ª ed.**
Palgrave Macmillan / Red Globe Press, 2014, 392 pp.
- ISBN 978-1-137-32802-1.
- Verifica: OL `https://openlibrary.org/isbn/9781137328021` (autore, titolo, 2014, 392 pp); la ricerca web
  riporta la dicitura «2nd edition» e l'indice a 13 capitoli (concettualizzazione, dati, codifica,
  sperimentazione, verifica e validazione) su schede di libreria (es. `https://www.foyles.co.uk/book/simulation/stewart-robinson/9781137328021`).
- Perché: testo di impronta non tecnica («non-technical textbook» nelle schede), centrato sul *processo* di
  costruzione e uso di un modello più che sulla matematica; adatto a chi deve decidere e non programmare.

**1.2 Banks, J.; Carson, J. S., II; Nelson, B. L.; Nicol, D. M. — *Discrete-Event System Simulation*, 5ª ed.**
Prentice Hall / Pearson, 2010.
- ISBN 978-0-13-606212-7.
- Verifica: OL `https://openlibrary.org/isbn/9780136062127` (2010, 622 pp, «Jerry Banks … [et al.]»);
  scheda Pearson «Discrete Event System Simulation, 5th edition»
  `https://www.pearson.com/en-us/subject-catalog/p/discrete-event-system-simulation/P200000003161/9780136062127`
  (indice: principi, code, numeri casuali, modellazione degli input, analisi dell'output).
- Perché: manuale universitario standard della simulazione a eventi discreti (lista degli eventi, orologio di
  simulazione, generazione di numeri casuali, verifica e validazione). Il confronto fra avanzamento al
  prossimo evento e a passo fisso è un tema di principi generali del testo; il capitolo esatto **non** è stato
  controllato (indice completo non aperto).

**1.3 Law, A. M. — *Simulation Modeling and Analysis*, 5ª ed.**
McGraw-Hill Education, New York, 2015 (copyright 2015; alcune schede riportano il 2014 come uscita in stampa).
- ISBN 978-0-07-340132-4 (esiste anche la 6ª ed., McGraw-Hill, 2023/2024, ISBN 978-1-264-26824-5).
- Verifica: OL `https://openlibrary.org/isbn/9780073401324` (800 pp); pagina editore
  `https://highered.mheducation.com/sites/0073401323/information_center_view0/` (5ª ed., copyright 2015, riportata
  dai risultati di ricerca); 6ª ed.: `https://www.mheducation.com/highered/mhp/product/simulation-modeling-analysis-sixth-edition.html`
  (descrizione: simulazione, software, verifica e validazione, modellazione degli input, generazione di numeri
  e variabili casuali).
- Perché: il riferimento classico (insieme a Banks et al.) per eventi discreti, generatori casuali, analisi
  dell'output e validazione; è l'opera di cui Law & Kelton sono le edizioni precedenti.

**1.4 Zeigler, B. P.; Praehofer, H.; Kim, T. G. — *Theory of Modeling and Simulation: Integrating Discrete Event and Continuous Complex Dynamic Systems*, 2ª ed.**
Academic Press, San Diego, 2000, 510 pp.
- ISBN 978-0-12-778455-7.
- Verifica: OL `https://openlibrary.org/isbn/9780127784557`; recensione indicizzata da Crossref che cita
  edizione, editore e anno (`https://doi.org/10.1002/rnc.610`).
- Perché: trattazione formale (formalismo DEVS) della separazione fra modello, simulatore e tempo a eventi.
  Più teorico: utile al lettore tecnico, non al responsabile non tecnico.

**1.5 Al Rowaei, A. A.; Buss, A. H.; Lieberman, S. — «The effects of time advance mechanism on simple agent behaviors in combat simulations»**
*Proceedings of the 2011 Winter Simulation Conference (WSC)*, 2011, pp. 2426-2437.
- DOI 10.1109/WSC.2011.6147952.
- Verifica: Crossref (autori, titolo, atti, pagine, anno).
- Perché: è l'articolo già segnalato nel documento di analisi del progetto (`Architettura_esecuzione_sessioni_virtuali_ANALISI.md`
  §10) come riferimento sul meccanismo di avanzamento del tempo nelle simulazioni di combattimento: ora ha
  citazione completa. Il suo contenuto non è stato letto (solo i dati di registro).

---

## 2. Numeri casuali, riproducibilità, flussi indipendenti, numeri casuali comuni

**Opera consigliata a un responsabile non tecnico: 1.3 (Law) o 1.2 (Banks et al.) per il quadro; 2.1 per la sola idea di «flussi e sotto-flussi» (3 pagine).**
Nessuna opera di questo argomento è propriamente «non tecnica»; i manuali di simulazione sono il punto di
ingresso più leggibile.

**2.1 ★ L'Ecuyer, P.; Simard, R.; Chen, E. J.; Kelton, W. D. — «An Object-Oriented Random-Number Package with Many Long Streams and Substreams»**
*Operations Research*, 50(6), 2002, pp. 1073-1075.
- DOI 10.1287/opre.50.6.1073.358.
- Verifica: Crossref.
- Perché: l'articolo che formalizza i **flussi** (streams) e **sotto-flussi** (substreams) di numeri pseudo-casuali
  indipendenti e riproducibili per esperimenti di simulazione con più repliche: l'idea alla base di un RNG di
  sessione con semi controllati.

**2.2 L'Ecuyer, P. — «Random numbers for simulation»**
*Communications of the ACM*, 33(10), 1990, pp. 85-97.
- DOI 10.1145/84537.84555.
- Verifica: Crossref.
- Perché: rassegna classica sui generatori di numeri casuali per la simulazione (qualità, periodo, uso). Non
  letta; titolo e sede di pubblicazione verificati.

**2.3 L'Ecuyer, P. — «Good Parameters and Implementations for Combined Multiple Recursive Random Number Generators»**
*Operations Research*, 47(1), 1999, pp. 159-164.
- DOI 10.1287/opre.47.1.159.
- Verifica: Crossref.
- Perché: generatore di riferimento da cui derivano i flussi e sotto-flussi di 2.1 (utile solo per chi implementa).

**2.4 L'Ecuyer, P.; Munger, D.; Oreshkin, B.; Simard, R. — «Random numbers for parallel computers: Requirements and methods, with emphasis on GPUs»**
*Mathematics and Computers in Simulation*, 135, 2017, pp. 3-17.
- DOI 10.1016/j.matcom.2016.05.005.
- Verifica: Crossref.
- Perché: requisiti e metodi per ottenere flussi indipendenti in esecuzioni parallele; rilevante se in futuro le
  sessioni verranno eseguite in parallelo mantenendo la riproducibilità.

**2.5 Glasserman, P.; Yao, D. D. — «Some Guidelines and Guarantees for Common Random Numbers»**
*Management Science*, 38(6), 1992, pp. 884-908.
- DOI 10.1287/mnsc.38.6.884.
- Verifica: Crossref.
- Perché: condizioni in cui l'uso dei **numeri casuali comuni** (stessi flussi per scenari confrontati) riduce
  la varianza della *differenza* fra alternative: è il fondamento del confronto «prima/dopo» a parità di
  casualità.

**2.6 Matsumoto, M.; Nishimura, T. — «Mersenne twister: a 623-dimensionally equidistributed uniform pseudo-random number generator»**
*ACM Transactions on Modeling and Computer Simulation*, 8(1), 1998, pp. 3-30.
- DOI 10.1145/272991.272995.
- Verifica: Crossref (il registro riporta il titolo breve «Mersenne twister»; il sottotitolo esteso qui riportato
  è il titolo comunemente citato dell'articolo, **non** riscontrato nel registro).
- Perché: algoritmo del generatore predefinito di molti linguaggi (compreso Python): utile a capire che cosa
  c'è dietro un «seme».

**2.7 Salmon, J. K.; Moraes, M. A.; Dror, R. O.; Shaw, D. E. — «Parallel random numbers: as easy as 1, 2, 3»**
*Proceedings of SC '11 (International Conference for High Performance Computing, Networking, Storage and Analysis)*, ACM, 2011, pp. 1-12.
- DOI 10.1145/2063384.2063405.
- Verifica: Crossref (titolo «Parallel random numbers», sottotitolo «as easy as 1, 2, 3»).
- Perché: generatori «a contatore» (famiglia Philox), che danno flussi indipendenti per chiave senza stato
  condiviso; alternativa moderna ai flussi di L'Ecuyer.

---

## 3. Wargaming e modellazione di campagne/guerra

**Opera consigliata a un responsabile non tecnico: 3.1 (Sabin, *Simulating War*).**

**3.1 ★ Sabin, P. — *Simulating War: Studying Conflict through Simulation Games***
Continuum / Bloomsbury Academic, London, 2012, 363 pp (ristampa in brossura: Bloomsbury Academic, 2014).
- ISBN 978-1-4411-8558-7 (ed. 2012); 978-1-4725-3391-3 (brossura 2014).
- Verifica: OL `https://openlibrary.org/isbn/9781441185587` (2012, Continuum/Bloomsbury Academic, 363 pp) e
  `https://openlibrary.org/isbn/9781472533913` (2014); scheda di libreria `https://www.foyles.co.uk/book/simulating-war/philip-sabin/9781472533913`;
  la recensione del *Times Higher Education* (`https://www.timeshighereducation.com/node/80238`) risulta fra i risultati di ricerca.
- Perché: manuale di progettazione di simulazioni di conflitto (con giochi storici completi di regole);
  discute il rapporto fra simulazione, teoria dei giochi e analisi operativa. Tesi utili al progetto:
  semplicità deliberata dei modelli e uso della simulazione per capire, non per predire.

**3.2 Perla, P. P. — *The Art of Wargaming: A Guide for Professionals and Hobbyists***
Naval Institute Press, Annapolis, 1990, 364 pp.
- ISBN 978-0-87021-050-1.
- Verifica: OL `https://openlibrary.org/isbn/9780870210501` (autore, titolo, editore, 1990, 364 pp); la ricerca web
  riporta lo stesso ISBN su cataloghi bibliotecari. Esiste una ristampa a cura di J. Curry (2011-2012,
  ISBN 978-1-4710-3373-5), non esaminata.
- Perché: il testo classico sul wargaming professionale (storia, scopi, metodi, differenza fra gioco e
  analisi). Complementare a Sabin.

**3.3 Hughes, W. P., Jr. (ed.) — *Military Modeling for Decision Making*, 3ª ed.**
Military Operations Research Society (MORS), Alexandria (VA), 1997.
- ISBN: **non verificato per la 3ª edizione** (vedi sezione «Non verificate»). La 2ª edizione (*Military Modeling*,
  MORS, 1989, 325 pp, ISBN 0-930473-01-9) è verificata su OL `https://openlibrary.org/isbn/0930473019`.
- Verifica della 3ª ed.: scheda del Naval War College Review (vol. 52, n. 4, 1999, articolo 10, «Military Modeling
  for Decision Making, 3d. ed.») `https://digital-commons.usnwc.edu/nwc-review/vol52/iss4/10`; articolo di
  presentazione di Hughes su *Phalanx* 30(4), dicembre 1997, p. 23, `https://hdl.handle.net/10945/64643` (metadati
  letti sul repository dell'NPS); l'articolo di Lucas & McGunnigle (voce 4.5) cita nella propria bibliografia
  «W. Hughes (Editor), Military Operations Research Society, Alexandria, VA, 1997» sia per l'introduzione di
  Bettencourt sia per il capitolo «Overview» di Hughes (pp. 1-66).
- Perché: antologia curata dal maggior esperto di modellazione militare per le decisioni; la «Overview» è
  la sintesi di che cosa i modelli militari possono e non possono dire. Per un responsabile è, con Sabin, la
  lettura più utile sulla *prudenza d'uso* dei modelli.

**3.4 Caffrey, M. B., Jr. — *On Wargaming***
Newport Papers n. 43, U.S. Naval War College Press, Newport (RI), 2019.
- ISBN: non riportato sulla pagina aperta.
- Verifica: `https://digital-commons.usnwc.edu/newport-papers/43/` (titolo «On Wargaming», autore, serie «The
  Newport Papers, Number 43», gennaio 2019, PDF scaricabile). Il sottotitolo («How Wargames Have Shaped History and
  How They May Shape the Future») compare nei risultati di ricerca ma non sulla pagina aperta.
- Perché: storia del wargaming professionale, scaricabile gratuitamente; utile per il contesto.

**3.5 Sabin, P. — *Lost Battles: Reconstructing the Great Clashes of the Ancient World***
Hambledon Continuum, London, 2007 (l'ISBN 978-1-84725-187-9 reca nel catalogo la data gennaio 2008; 320 pp).
- ISBN 978-1-84725-187-9.
- Verifica: OL `https://openlibrary.org/isbn/9781847251879` (titolo, sottotitolo, editore, gennaio 2008, 320 pp) e
  scheda di lavoro `https://openlibrary.org/works/OL4222866W` (prima pubblicazione 2007).
- Perché: origine del «comparative dynamic modelling» di Sabin (già nel wiki); metodo di calibrazione su fonti
  storiche. Più lontano dal motore: pertinente come metodo.

---

## 4. Modelli di attrito: Lanchester e modello a salve di Hughes

**Opera consigliata a un responsabile non tecnico: 4.5 (Lucas & McGunnigle), articolo disponibile gratuitamente
presso l'NPS; per Lanchester, la fonte primaria 4.1 è storicamente leggibile (testo integrale su archive.org).**

**4.1 Lanchester, F. W. — *Aircraft in Warfare: The Dawn of the Fourth Arm***
Constable and Company, London, 1916.
- ISBN: nessuno (edizione originale); ristampa Lanchester Press, Sunnyvale (CA), 1995 (Internet Archive; l'ISBN
  978-1-57321-002-7 è associato all'opera nel catalogo OL, ma non verificato per questa specifica ristampa).
- Verifica: scansioni integrali su Internet Archive
  `https://archive.org/details/aircraftinwarfar00lancrich` («Aircraft in warfare, the dawn of the fourth arm»,
  London, Constable and company limited, 1916) e record OL `https://openlibrary.org/works/OL1544424W`.
- Perché: fonte primaria delle leggi lineare e quadratica di attrito; serve a spiegare **perché non sono il
  modello** del motore (aggregate, continue, senza saturazione). Il passaggio esatto non è stato localizzato.

**4.2 Hughes, W. P., Jr. — «A salvo model of warships in missile combat used to evaluate their staying power»**
*Naval Research Logistics*, 42(2), 1995, pp. 267-289.
- DOI 10.1002/1520-6750(199503)42:2<267::AID-NAV3220420209>3.0.CO;2-Y.
- Verifica: Crossref (autore, titolo, rivista, volume, fascicolo, pagine, anno). Lucas & McGunnigle (4.5, voce [23]
  della loro bibliografia) citano lo stesso lavoro come capitolo di *Warfare Modeling* (Bracken, Kress, Rosenthal
  eds., Wiley, 1995, pp. 121-143): quella sede **non** è stata verificata autonomamente.
- Perché: fonte primaria del modello a salve (capacità offensiva, difensiva e *staying power*). **Conferma
  il titolo e i dati del documento di analisi del progetto e del wiki.**

**4.3 Hughes, W. P., Jr.; Girrier, R. P. — *Fleet Tactics and Naval Operations*, 3ª ed.**
Naval Institute Press, Annapolis, 2018, 408 pp.
- ISBN 978-1-68247-337-5.
- Verifica: OL `https://openlibrary.org/isbn/9781682473375` (2018, 408 pp). OL registra anche un'edizione del
  2025 con tre autori (con J. M. Richardson), ISBN 978-1-68247-112-8: non chiarito il rapporto fra le due.
  Edizioni precedenti verificate: *Fleet Tactics: Theory and Practice*, Naval Institute Press, 1986, 316 pp,
  ISBN 978-0-87021-558-2 (`https://openlibrary.org/isbn/9780870215582`); *Fleet Tactics and Coastal Combat*,
  2ª ed., Naval Institute Press, Annapolis, 1999/2000, 378 pp, ISBN 978-1-55750-392-3
  (`https://openlibrary.org/isbn/9781557503923`; l'anno è 1999 in OL e 2000 nell'articolo di Lucas & McGunnigle).
- Perché: monografia di tattica navale dalla quale il wiki fa discendere il modello a salve e il principio
  dell'«attaccare efficacemente per primi». **Non verificato** che l'edizione 2018 contenga le equazioni
  (non è stato aperto l'indice).

**4.4 Washburn, A.; Kress, M. — *Combat Modeling***
Springer (International Series in Operations Research & Management Science), 2009, 277 pp.
- ISBN 978-1-4419-0789-9 (stampa), 978-1-4419-0790-5 (elettronico); DOI 10.1007/978-1-4419-0790-5.
- Verifica: Crossref (libro e record dei capitoli, fra i quali «Attrition Models», pp. 79-109, e «Search»,
  pp. 133-160); OL `https://openlibrary.org/isbn/9781441907899` (277 pp); pagina dell'autore
  `https://faculty.nps.edu/awashburn/washbubk.htm`.
- Perché: manuale moderno che tratta insieme **attrito** (Lanchester e successivi) e **ricerca/rilevamento**:
  un solo testo per gli argomenti 4 e 5.

**4.5 ★ Lucas, T. W.; McGunnigle, J. E. — «When is model complexity too much? Illustrating the benefits of simple models with Hughes' salvo equations»**
*Naval Research Logistics*, 50(3), 2003, pp. 197-217.
- DOI 10.1002/nav.10062.
- Verifica: Crossref; copia aperta sul repository dell'NPS `https://hdl.handle.net/10945/65156` (letti titolo,
  abstract, riferimenti): confronta la semplicità delle equazioni a salve di Hughes con modelli complessi.
- Perché: giustifica la scelta di un modello d'ingaggio a salve **trasparente** invece di uno più complesso; dice
  in modo diretto quando la complessità non paga («All models are wrong, but some are useful», attribuito a Box).
  È la lettura più adatta a un responsabile per capire perché il motore tiene semplice il risolutore.

**4.6 Armstrong, M. J. — «Effective attacks in the salvo combat model: Salvo sizes and quantities of targets»**
*Naval Research Logistics*, 54(1), 2007, pp. 66-77. DOI 10.1002/nav.20187.
**Armstrong, M. J. — «The salvo combat model with area fire»**
*Naval Research Logistics*, 60(8), 2013, pp. 652-660. DOI 10.1002/nav.21559.
- Verifica: Crossref (entrambi).
- Perché: estensioni del modello a salve (dimensione delle salve, fuoco d'area); riferimento se il motore
  vorrà giustificare la saturazione o il fuoco su posizione. Contenuto non letto.

**4.7 Rassegna empirica su Lanchester e dati storici**
- **Bracken, J.** — «Lanchester models of the Ardennes campaign», *Naval Research Logistics*, 42(4), 1995,
  pp. 559-577, DOI 10.1002/1520-6750(199506)42:4<559::AID-NAV3220420405>3.0.CO;2-R (Crossref).
- **Fricker, R. D., Jr.** — «Attrition models of the Ardennes campaign», *Naval Research Logistics*, 45(1), 1998,
  pp. 1-22, DOI 10.1002/(SICI)1520-6750(199802)45:1<1::AID-NAV1>3.0.CO;2-D (Crossref).
- **Lucas, T. W.; Turkes, T.** — «Fitting Lanchester equations to the battles of Kursk and Ardennes», *Naval
  Research Logistics*, 51(1), 2004, pp. 95-116, DOI 10.1002/nav.10101 (Crossref).
- **Helmbold, R. L.** — «Letter to the Editor — A Modification of Lanchester's Equations», *Operations Research*,
  13(5), 1965, pp. 857-859, DOI 10.1287/opre.13.5.857 (Crossref). Il legame con le «soglie di ritirata»
  attribuito a Helmbold dal wiki **non** è stato riscontrato (solo il titolo).
- Perché: valutazioni dell'adattamento delle equazioni di Lanchester a battaglie storiche (Ardenne, Kursk);
  il documento di analisi del progetto cita già Lucas & Turkes (2004). Nota di discordanza con il wiki in
  «Già nel progetto».

---

## 5. Teoria della ricerca e del rilevamento

**Opera consigliata a un responsabile non tecnico: 4.4 (Washburn & Kress, capitolo «Search»), per il quadro
concettuale della ricerca e del rilevamento; per il radar, 5.4 (Skolnik) come testo standard di introduzione.**
Nessuna delle opere di questa sezione è priva di formule: non esiste, fra quelle verificate, un testo davvero non
tecnico su questo argomento.

**5.1 Koopman, B. O. — *Search and Screening: General Principles with Historical Applications***
Pergamon Press, New York/Oxford, 1980, 369 pp (riedizione del rapporto del 1946 dell'Operations Evaluation Group).
- ISBN 978-0-08-023136-5.
- Verifica: OL `https://openlibrary.org/isbn/9780080231365` (titolo, sottotitolo, editore, 1980, 369 pp); il
  record OL `https://openlibrary.org/works/OL17646127W` riporta anche la ristampa MORS (ISBN 0-930473-08-6) del rapporto
  originale (OEG, 1946).
- Perché: il testo fondativo della teoria della ricerca (legge esponenziale di rilevamento per «ricerca
  casuale», probabilità cumulativa di rilevamento). È il riferimento che il manuale cita come «Koopman».

**5.2 Koopman, B. O. — «The Theory of Search» (tre parti)**
*Operations Research*: I. *Kinematic Bases*, 4(3), 1956, pp. 324-346 (DOI 10.1287/opre.4.3.324);
II. *Target Detection*, 4(5), 1956, pp. 503-531 (DOI 10.1287/opre.4.5.503);
III. *The Optimum Distribution of Searching Effort*, 5(5), 1957, pp. 613-626 (DOI 10.1287/opre.5.5.613).
- Verifica: Crossref (le tre parti).
- Perché: la formulazione in rivista della teoria; la parte II («Target Detection») è la più pertinente alla
  probabilità di rilevamento.

**5.3 Washburn, A. R. — *Search and Detection***
INFORMS (Military Applications Society), 4ª ed., 2002 (ISBN 978-1-877640-17-9, OL `https://openlibrary.org/isbn/9781877640179`);
5ª ed., CreateSpace, 2014 (ISBN 978-1-5027-5799-9, OL `https://openlibrary.org/isbn/9781502757999`).
- Verifica: pagina dell'autore `https://faculty.nps.edu/awashburn/washbubk.htm` (indica «Search and Detection», 5ª
  ed., CreateSpace, 2014) e record OL per entrambe le edizioni.
- Perché: introduzione moderna e compatta alla teoria della ricerca (legge esponenziale, sweep width, rilevamento).

**5.4 Skolnik, M. I. — *Introduction to Radar Systems*, 3ª ed.**
McGraw-Hill, 2001, 772 pp.
- ISBN 978-0-07-288138-7.
- Verifica: OL `https://openlibrary.org/isbn/9780072881387` (titolo, autore, McGraw Hill, 2001, 772 pp); la ricerca
  web riporta la scheda di una biblioteca universitaria (Texas A&M, 3ª ed., Boston, McGraw Hill, 2001, collocazione
  TK6575 .S477 2001) e un elenco dei capitoli iniziali (introduzione, equazione radar, rivelazione di segnali nel
  rumore).
- Perché: testo standard sulle basi del radar: equazione radar, dipendenza dalla distanza, portata e rilevamento
  nel rumore. **Non verificato** che tratti la probabilità di rilevamento cumulativa (non trovato un indice
  completo): la voce 5.5 è più sicura per quel punto.

**5.5 Mahafza, B. R. — *Radar Systems Analysis and Design Using MATLAB*, 2ª ed.**
Chapman & Hall/CRC, Boca Raton, 2005, 638 pp.
- ISBN 978-1-58488-532-0.
- Verifica: OL `https://openlibrary.org/isbn/9781584885320` (2005, 638 pp); **sommario aperto e letto**
  `https://sisis.rz.htw-berlin.de/inh2012/12423454.pdf` (frontespizio «Second Edition»; capitolo 4 «Radar Detection»,
  con sezioni dedicate alla rivelazione di bersagli Swerling I, II, III, IV, V e una sezione intitolata
  «Cumulative Probability of Detection»).
- Perché: unico testo, fra quelli aperti, in cui sono **verificati sul sommario** sia le curve di Swerling sia la
  probabilità di rilevamento cumulativa; contiene codice, quindi utile ai tecnici.

**5.6 DiFranco, J. V.; Rubin, W. L. — *Radar Detection***
SciTech Publishing, 2004 (ristampa; prima ed.: Prentice-Hall, 1968; ed. Artech House, 1980), 300 pp.
- ISBN 978-1-891121-36-4.
- Verifica: OL `https://openlibrary.org/isbn/9781891121364`; Crossref registra il capitolo 13 con titolo
  «Cumulative Detection Probability of Stationary and Moving Targets» (pp. 476-494), DOI 10.1049/sbra028e_ch13.
- Perché: trattazione estesa della rivelazione a più sguardi (singolo, impulsi multipli, cumulativa).

**5.7 Mallett, J. D.; Brennan, L. E. — «Cumulative probability of detection for targets approaching a uniformly scanning search radar»**
*Proceedings of the IEEE*, 51(4), 1963, pp. 596-601. DOI 10.1109/PROC.1963.2207.
(Correzione: *Proceedings of the IEEE*, 52(6), 1964, pp. 708-709, DOI 10.1109/PROC.1964.3053.)
- Verifica: Crossref (articolo e correzione).
- Perché: l'articolo classico sulla probabilità cumulativa di rilevamento di un bersaglio che si avvicina a un
  radar con scansione uniforme (cioè: Pd per scansione composta lungo la traiettoria).

**5.8 Swerling, P. — «Probability of detection for fluctuating targets»**
*IRE Transactions on Information Theory*, 6(2), 1960, pp. 269-308. DOI 10.1109/TIT.1960.1057561.
**Marcum, J. — «A statistical theory of target detection by pulsed radar»**
*IRE Transactions on Information Theory*, 6(2), 1960, pp. 59-267. DOI 10.1109/TIT.1960.1057560.
- Verifica: Crossref (entrambi).
- Perché: fonti primarie dei modelli di fluttuazione (Swerling) e della probabilità di rivelazione per radar a
  impulsi (Marcum); il manuale cita Swerling senza riferimento: ora ha la citazione completa.

**Nota: Pd per scansione e Pd cumulativa.** Sì, la letteratura le distingue. I sommari aperti mostrano il
trattamento come argomenti separati: la rivelazione di un bersaglio per ogni caso di Swerling (5.5, sezioni
Swerling) è distinta dalla «Cumulative Probability of Detection» (5.5; 5.6, cap. 13; 5.7, titolo). La forma
standard `Pc = 1 − Π(1 − Pd,i)` presuppone scansioni indipendenti; nei casi di Swerling I e III la fluttuazione
è correlata da una scansione all'altra (casi II e IV: da impulso a impulso), quindi la cumulativa non è un
semplice prodotto: **questa precisazione è conoscenza generale dell'agente, non riscontrata su un passaggio
letto**: da verificare in 5.5/5.6/5.8. Una distinzione analoga vale per la legge di Koopman (5.1): rilevamento
continuo (esponenziale) contro sguardi discreti. Quanto alle convenzioni di «portata dichiarata a Pd 0,5 o 0,9»
(segnaposto del manuale): **non trovata una fonte specifica** (vedi «Limiti»).

---

## 6. Verifica e validazione dei modelli di simulazione, in particolare di difesa

**Opera consigliata a un responsabile non tecnico: 6.2 (Youngblood et al.), perché spiega in poche pagine che cosa sono verifica, validazione e accreditamento e che l'accreditamento è un giudizio di gestione.**

**6.1 Sargent, R. G. — «Verification and validation of simulation models»**
*Journal of Simulation*, 7(1), 2013, pp. 12-24. DOI 10.1057/jos.2012.20.
- Verifica: Crossref.
- Perché: la rassegna di riferimento sui metodi di verifica e validazione e sul processo di «credibilità» del
  modello (aggiornamento di una serie di articoli dell'autore alla Winter Simulation Conference).
  Esistono versioni precedenti a WSC (es. 1994, 2007, 2008, DOI 10.1109/WSC.1994.717077,
  10.1109/WSC.2007.4419595, 10.1109/WSC.2008.4736065, Crossref).

**6.2 ★ Youngblood, S. M.; Pace, D. K.; Eirich, P. L.; Gregg, D. M.; Coolahan, J. E. — «Simulation Verification, Validation, and Accreditation»**
*Johns Hopkins APL Technical Digest*, 21(3), 2000, pp. 359-367.
- Identificativo: nessun DOI trovato.
- Verifica: PDF **aperto e letto** `https://secwww.jhuapl.edu/techdigest/Content/techdigest/pdf/V21-N03/21-03-Youngblood.pdf`
  (titolo, autori, volume, numero, anno, 9 pagine consecutive 359-367, abstract: VV&A come «cornerstones» della
  correttezza e credibilità; l'accreditamento è un «management judgment» sull'idoneità a un uso specifico).
- Perché: sintesi chiara del ruolo di verifica (costruito bene?), validazione (costruito il modello giusto?)
  e accreditamento (adatto a questo uso?) nel contesto della difesa USA.

**6.3 Balci, O. — «Verification, validation and accreditation of simulation models»**
*Proceedings of the 29th Winter Simulation Conference (WSC '97)*, 1997, pp. 135-141. DOI 10.1145/268437.268462.
**Balci, O. — «Principles and techniques of simulation validation, verification, and testing»**
*Proceedings of the 27th Winter Simulation Conference (WSC '95)*, 1995, pp. 147-154. DOI 10.1145/224401.224456.
- Verifica: Crossref (entrambi).
- Perché: elenco sistematico di tecniche di VV&A (1997 con l'accreditamento, 1995 con principi e tecniche).

**6.4 Hodges, J. S.; Dewar, J. A. — «Is It You or Your Model Talking? A Framework for Model Validation»**
RAND, R-4114-A/AF/OSD, 1992, 43 pp.
- Verifica: `https://www.rand.org/pubs/reports/R4114.html` (titolo, autori, anno, numero, pagine; sintesi: un
  modello è validabile per la previsione solo se osservabile, strutturalmente stabile, coerente in condizioni non
  specificate e con dati adeguati).
- Perché: argomento centrale per un modello di combattimento: quando un modello **non può** essere validato per
  predire. Citato anche da Lucas & McGunnigle (voce [20] della loro bibliografia).

**6.5 Davis, P. K. — *Generalizing Concepts and Methods of Verification, Validation, and Accreditation (VV&A) for Military Simulations***
RAND, R-4249-ACQ, 1992, 61 pp.
- Verifica: `https://www.rand.org/pubs/reports/R4249.html`.
- Perché: schema pratico di VV&A per simulazioni militari, comprese quelle che rappresentano il comportamento
  decisionale di C2.

**6.6 *MIL-STD-3022 — Documentation of Verification, Validation, and Accreditation (VV&A) for Models and Simulations***
Department of Defense Standard Practice, 28 gennaio 2008, con Change 1 dell'aprile 2012.
- Verifica: `https://everyspec.com/MIL-STD/MIL-STD-3000-9999/MIL-STD-3022_4197/` (titolo, data 28 gennaio 2008,
  CHG-1 aprile 2012, stato «Active»).
- Perché: modelli di documento per piano di accreditamento, piano e rapporto di V&V, rapporto di accreditamento:
  è lo standard ufficiale della documentazione VV&A del Dipartimento della Difesa.

**6.7 Box, G. E. P. — «Robustness in the Strategy of Scientific Model Building»**
In: Launer, R. L.; Wilkinson, G. N. (eds.), *Robustness in Statistics*, Academic Press, 1979, pp. 201-236.
- ISBN 978-0-12-438150-6; DOI 10.1016/B978-0-12-438150-6.50018-2.
- Verifica: Crossref; la sede è quella citata da Lucas & McGunnigle (4.5) per la massima «All models are wrong,
  but some are useful».
- Perché: fonte della massima, richiesta dal segnaposto del manuale («tutti i modelli sono sbagliati, alcuni
  utili»). Un articolo precedente, Box, G. E. P., «Science and Statistics», *Journal of the American Statistical
  Association*, 71(356), 1976, pp. 791-799 (DOI 10.1080/01621459.1976.10480949, Crossref) è spesso citato per la
  prima parte della frase: non verificato il passo.

---

## 7. Modellazione a risoluzione variabile e comando e controllo a livelli

**Opera consigliata a un responsabile non tecnico: 7.1 (Davis, «Introduction to MRMPM», 80 pp).**

**7.1 ★ Davis, P. K. — *Introduction to Multiresolution, Multiperspective Modeling (MRMPM) and Exploratory Analysis***
RAND, WR-224, 2005, 80 pp.
- Verifica: `https://www.rand.org/pubs/working_papers/WR224.html`.
- Perché: introduzione organica ai modelli a più risoluzioni e prospettive e all'analisi esplorativa; la più
  breve e generale fra le opere RAND.

**7.2 Davis, P. K. — *An Introduction to Variable-Resolution Modeling and Cross-Resolution Model Connection***
RAND, R-4252-DARPA, 1993, 66 pp.
- Verifica: `https://www.rand.org/pubs/reports/R4252.html`.
- Perché: il report già segnalato nel documento di analisi del progetto (§10, «Davis, RAND R-4252»): ora
  verificato (titolo completo, 1993).

**7.3 Davis, P. K.; Hillestad, R. — «Families of models that cross levels of resolution: issues for design, calibration and management»**
*Proceedings of the 1993 Winter Simulation Conference (WSC '93)*, 1993, pp. 1003-1012. DOI 10.1145/256563.256913.
- Verifica: Crossref (titolo esteso confermato anche nella versione IEEE, DOI 10.1109/WSC.1993.718351).
- Perché: articolo classico sulle famiglie di modelli a risoluzione diversa e sul loro collegamento.

**7.4 Davis, P. K.; Bigelow, J. H. — *Experiments in Multiresolution Modeling (MRM)***
RAND, MR-1004-DARPA, 1998, 86 pp.
- Verifica: `https://www.rand.org/pubs/monograph_reports/MR1004.html`.
- Perché: esperimenti pratici sulla coerenza fra modelli a risoluzione diversa (citato anche nel documento di analisi).

**7.5 Hillestad, R.; Moore, L. R. — *The Theater-Level Campaign Model: A Research Prototype for a New Generation of Combat Analysis Model***
RAND, MR-388-AF/A, **1996**, 201 pp.
- Verifica: `https://www.rand.org/pubs/monograph_reports/MR388.html` (titolo completo, autori, **anno 1996**,
  numero di rapporto, 201 pp; ISBN non riportato dalla pagina).
- Perché: modello di campagna a eventi con rete generalizzata e attrito calibrato; già fonte del wiki (vedi
  discordanza sull'anno in «Già nel progetto»).

**7.6 C2 in modelli a livelli (RAND)**
- **Davis, P. K.; Howe, R.** — *Representing Operational Strategies and Command-Control in the RAND Strategy
  Assessment System (RSAS)*, RAND, N-3232-OSD, 1990, 38 pp. `https://www.rand.org/pubs/notes/N3232.html`.
- **Schwabe, W.; Wilson, B.** — *Analytic War Plans: Adaptive Force-Employment Logic in the RAND Strategy
  Assessment System (RSAS)*, RAND, N-3051-NA, 1990, 202 pp. `https://www.rand.org/pubs/notes/N3051.html`.
- **Davis, P. K.; Bankes, S. C.; Kahan, J. P.** — *A New Methodology for Modeling National Command Level
  Decisionmaking in War Games and Simulations*, RAND, R-3290-NA, 1986, 136 pp. `https://www.rand.org/pubs/reports/R3290.html`.
- **Wilson, B.; Fox, D. B.** — *Ground Combat in the JICM*, RAND, MR-422-NA, 1995, 230 pp. `https://www.rand.org/pubs/monograph_reports/MR422.html`.
- **Allen, P. D.** — *Situational Force Scoring: Accounting for Combined Arms Effects in Aggregate Combat Models*,
  RAND, N-3423-NA, 1992, 116 pp. `https://www.rand.org/pubs/notes/N3423.html`.
- Verifica: pagine RAND aperte (titolo, autori, anno, numero, pagine). MR-422 e N-3423 sono i due rapporti già
  segnalati nel §10 del documento di analisi.
- Perché: rappresentazione adattiva del comando e controllo, piani di guerra analitici e punteggio di forza
  aggregato nei modelli di teatro; il wiki ha già RSAS e JICM come entità.

**7.7 Alberts, D. S. — *Understanding Command and Control*** (Future of Command and Control series)
Command and Control Research Program (CCRP), US DoD, gennaio 2006, 222 pp.
- ISBN 978-1-893723-17-7 (10: 1-893723-17-8); LCCN 2006000771; collocazione UB212 .A435 2006.
- Verifica: OL `https://openlibrary.org/isbn/9781893723177` (titolo, anno 2006, 222 pp, LCCN, ID Internet Archive).
  L'autore indicato dal catalogo è **D. S. Alberts**; che il libro sia scritto con R. E. Hayes (come compare in altre
  fonti) **non è stato riscontrato su una fonte aperta**: verificare il frontespizio. Copia DTIC
  (`ADA457162`) non apribile dall'agente (403).
- Perché: concettualizzazione dell'efficacia di C2 e dei livelli di comando; contesto generale, non strumento
  di modellazione.

**7.8 Tolk, A. (ed.) — *Engineering Principles of Combat Modeling and Distributed Simulation***
Wiley, Hoboken (NJ), 2012, 888 pp.
- ISBN 978-0-470-87429-5; DOI 10.1002/9781118180310.
- Verifica: Crossref (tipo «edited-book», 2012, Wiley, ISBN stampa ed elettronico); OL
  `https://openlibrary.org/isbn/9780470874295` (888 pp).
- Perché: manuale di modellazione del combattimento e simulazione distribuita con aspetti di risoluzione,
  aggregazione e interoperabilità. Il contenuto non è stato letto.

---

## 8. Dati storici e metodi quantitativi sul combattimento

**Opera consigliata a un responsabile non tecnico: 8.2 (Lawrence, *War by Numbers*), per leggibilità e
attualità; 8.1 (Dupuy) come classico.**

**8.1 Dupuy, T. N. — *Numbers, Predictions and War: Using History to Evaluate Combat Factors and Predict the Outcome of Battles***
Bobbs-Merrill, Indianapolis, 1979, 244 pp (rist. riveduta: Hero Books, Fairfax, 1985, 256 pp).
- ISBN 978-0-672-52131-7 (1979); 978-0-915979-06-6 (Hero Books, 1985).
- Verifica: OL `https://openlibrary.org/isbn/9780672521317` (1979, 244 pp) e
  `https://openlibrary.org/isbn/9780915979066` (1985, 256 pp, «Numbers, Prediction, and War» nel titolo del
  catalogo; il frontespizio può dire «Predictions»).
- Perché: metodo dei «fattori di combattimento» (QJM) e uso di dati storici per prevedere esiti: il riferimento
  sul tema, e base delle critiche alla validazione dei modelli.

**8.2 ★ Lawrence, C. A. — *War by Numbers: Understanding Conventional Combat***
Potomac Books (University of Nebraska Press), 2017, 390 pp (ed. rilegata).
- ISBN 978-1-61234-886-5 (rilegata); OL riporta anche 978-1-61234-917-6 (498 pp, altra versione/edizione).
- Verifica: OL `https://openlibrary.org/isbn/9781612348865` e `https://openlibrary.org/isbn/9781612349176`.
- Perché: analisi quantitativa moderna dei dati di combattimento convenzionale dell'autore, presidente del
  Dupuy Institute; è la fonte «Lawrence» che il wiki segnala come lacuna (voce *lanchester-models.md*).
  Il contenuto non è stato letto.

**8.3 Dati e confronti già citati in 4.7**: Bracken (1995), Fricker (1998), Lucas & Turkes (2004) per l'uso delle
campagne storiche delle Ardenne e di Kursk.

---

## Altri segnaposto `[FONTE: …]` della scaletta coperti da opere verificate

Non richiesti come argomenti, ma emersi dalla lettura di `Guida_Concettuale_DES_Scaletta.md`:

| Segnaposto | Opera verificata | Nota |
|---|---|---|
| assegnazione arma-bersaglio (WTA) | Manne, A. S., «A Target-Assignment Problem», *Operations Research* 6(3), 1958, pp. 346-351, DOI 10.1287/opre.6.3.346; Ahuja, R. K.; Kumar, A.; Jha, K. C.; Orlin, J. B., «Exact and Heuristic Algorithms for the Weapon-Target Assignment Problem», *Operations Research* 55(6), 2007, pp. 1136-1146, DOI 10.1287/opre.1070.0440 | Crossref. Contenuto non letto. |
| «tutti i modelli sono sbagliati» | Box 1979 (6.7); Lucas & McGunnigle 2003 (4.5) | vedi sopra |
| livelli dei modelli di difesa | Hillestad & Moore (7.5); Davis (7.1-7.2) | |
| simulatori a livello di entità, aggregati a passo fisso | **nessuna fonte primaria trovata** | resta pendente |
| Ph/Pk, shoot-look-shoot, tempi di reazione SAM, soglie di rottura 30%, golden master, bingo fuel, turnaround | **non cercati / non coperti** | fuori dai soli otto argomenti richiesti |

---

## Già nel progetto (wiki `Analysis/WIKI_LLM_SIMULATION/wiki/`)

Opere citate dal wiki e pertinenti, con il percorso e l'esito del completamento bibliografico.

| Opera citata dal wiki | File del wiki | Completamento / esito della verifica |
|---|---|---|
| F. W. Lanchester, 1916 (equazioni lineare e quadratica) | `concepts/lanchester-models.md` | Completata: *Aircraft in Warfare: The Dawn of the Fourth Arm*, Constable, London, 1916 (voce 4.1, scansione su archive.org). Il wiki non dà titolo né editore. |
| W. P. Hughes, *Fleet Tactics* (1986) e *Fleet Tactics and Coastal Combat* (2000); salva, anno 1995 | `entities/wayne-hughes.md`; `concepts/salvo-combat-model.md`; `sources/source-hughes-salvo-event-driven.md` | Completata: *Fleet Tactics: Theory and Practice*, Naval Institute Press, 1986 (OL, 316 pp, ISBN 0-87021-558-2); 2ª ed. *Fleet Tactics and Coastal Combat*, 1999/2000 (OL, ISBN 1-55750-392-3); articolo 1995 *Naval Research Logistics* 42(2):267-289 (4.2). Il wiki dichiara di non avere una «fonte primaria»: **ora c'è** (4.2, DOI). |
| P. Sabin, *Simulating War* (2012), *Lost Battles* (2007), articolo del 2008 | `entities/philip-sabin.md`; `concepts/wargaming.md`; `concepts/comparative-dynamic-modelling.md`; `concepts/historical-conflict-simulation.md`; `sources/source-simulation-techniques-past-conflicts.md` | Completata: 3.1 (2012, Continuum/Bloomsbury) e 3.5 (Hambledon Continuum, 2007/2008). Il documento del 2008 (workshop dell'Higher Education Academy, Warwick) **non** è stato cercato. |
| R. Hillestad, L. Moore, *The Theater-Level Campaign Model* (anno 1994 nel wiki) | `sources/source-theater-level-campaign-model.md`; `entities/tlc-model.md`; `concepts/campaign-model.md`; `concepts/cross-resolution-modeling.md`; `concepts/variable-resolution-modeling.md` | Completata: titolo esteso e **anno 1996** (RAND MR-388-AF/A, 201 pp). **Discordanza sull'anno** (voce 7.5). |
| J. Bracken (calibrazione Ardenne/Kursk), Dupuy Institute/KDB, Helmbold, Lawrence | `concepts/lanchester-models.md`; `sources/source-lanchester-scenari-ai.md` | Completata in parte: Bracken 1995, Fricker 1998, Lucas & Turkes 2004, Helmbold 1965, Lawrence 2017, Dupuy 1979 (voci 4.7, 8.1, 8.2). **Discordanza** (vedi sotto). Peterson (modello logaritmico) e SINDy: non cercati. |
| RSAS, JICM, TAC BRAWLER, EADSIM, JMEM, RJARS (entità) | `entities/rsas.md`; `entities/jicm-model.md`; `entities/tac-brawler.md`; `entities/rjars.md` | Per RSAS e JICM, rapporti RAND di appoggio in 7.6. Per gli altri modelli non è stata cercata bibliografia. |
| «mean value equivalence», stocastico contro deterministico | `concepts/stochastic-simulation.md`; `concepts/event-driven-simulation.md` | Il wiki li deriva dal rapporto RAND TLC; per testi di riferimento si veda 1.2-1.3, 2.1-2.5. |

**Discordanze fra il wiki e le fonti web:**
1. **Anno di Hillestad & Moore**: wiki 1994, pagina RAND 1996 (MR-388-AF/A).
2. **Bracken e Kursk**: il wiki (conversazione con un assistente AI, confidenza bassa) attribuisce a Bracken la
   calibrazione su Ardenne **e** Kursk; il titolo dell'articolo di Bracken (1995) riguarda le sole Ardenne; l'adattamento
   congiunto Kursk-Ardenne compare in Lucas & Turkes (2004). Nulla è stato riscontrato sul valore p ≈ q ≈ 0,5 citato.
3. **Anno di *Fleet Tactics and Coastal Combat***: wiki 2000; OL 1999 (con anno di prima pubblicazione 2000 nel
   record dell'opera); l'articolo di Lucas & McGunnigle riporta 2000.
4. **Salva «da *Fleet Tactics*»**: il wiki fa derivare il modello da *Fleet Tactics*; l'articolo di riferimento con le
   equazioni verificato è quello del 1995 (*Naval Research Logistics*). Che le equazioni compaiano nel libro del 1986
   non è stato riscontrato.
5. Il wiki cita **«Fleet Tactics … 1986, poi *Fleet Tactics and Coastal Combat*, 2000»** e omette la 3ª edizione
   *Fleet Tactics and Naval Operations* (Hughes & Girrier, 2018): non è una discordanza ma un'integrazione.

**Fonti ingerite nel wiki che NON sono letteratura primaria** (come dichiara il wiki stesso):
`sources/source-hughes-salvo-event-driven.md` e `sources/source-lanchester-scenari-ai.md` sono conversazioni con un
assistente AI; per le parti citabili vanno sostituite con 4.2, 4.5, 4.7.

---

## Non verificate

| Opera | Motivo |
|---|---|
| **Hughes, W. P., Jr. (ed.), *Military Modeling for Decision Making*, 3ª ed., MORS, 1997: ISBN** | Esistenza della 3ª edizione riscontrata (NWC Review 1999, *Phalanx* 1997, bibliografia di Lucas & McGunnigle), **ma l'ISBN no**: HathiTrust (`catalog.hathitrust.org/Record/004005599`) risulta bloccato (403), e il codice 0-930473-01-9 riportato da alcune fonti di ricerca corrisponde, nel catalogo OL, alla 2ª edizione (1989). Nessun ISBN attribuito. |
| **Taylor, J. G., *Lanchester Models of Warfare*, 2 voll., 1983** | Citato da un'opera di riferimento (Springer, enciclopedia di ricerca operativa) con editore INFORMS Military Applications Society, Linthicum (MD), e dalla biblioteca nazionale israeliana con Ketron, Arlington (VA), 1983: **editori in contrasto**, nessun ISBN, nessun catalogo aperto. Esiste anche il rapporto DTIC del 1980 *Lanchester-Type Models of Warfare*. |
| **DoD Instruction 5000.61 (DoD Modeling and Simulation VV&A)** | Esistenza e aggiornamento al 17 settembre 2024 riportati da fonti secondarie (articolo di stampa, risultati di ricerca); le pagine ufficiali (`esd.whs.mil`) restituiscono 403 e le copie d'archivio sono vuote. Numero, titolo esatto e data **non riscontrati su una fonte aperta**; il documento di Lucas & McGunnigle lo cita nella versione dell'aprile 1996. Da scaricare dal sito del DoD. |
| **VV&A Recommended Practices Guide (DoD MSCO)** | Non trovata una pagina ufficiale apribile. |
| **Hughes, W. P., Jr. «A salvo model…», in Bracken, Kress, Rosenthal (eds.), *Warfare Modeling*, Wiley/MORS, 1995, pp. 121-143** | Citato da Lucas & McGunnigle; il libro non è stato trovato in alcun catalogo aperto. È probabile che sia la ristampa dell'articolo di 4.2: **non verificato**. |
| **Skolnik, *Introduction to Radar Systems*, 3ª ed.: contenuto su Pd cumulativa e Swerling** | L'opera esiste (5.4), ma nessun indice completo è stato aperto. |
| **«Poe 1974» (visione umana, bande di scansione 1,75-6 s)** citato dal manuale | Non cercato a fondo: nessuna fonte individuata. |
| **Convenzioni sulla portata dichiarata di un radar (Pd 0,5 o 0,9)** | Nessuna fonte specifica trovata. |
| **Peterson (attrito logaritmico), SINDy** (citati dal wiki) | Non cercati. |
| **Pace, D. K., e le linee guida VV&A del DoD in forma di libro o di rapporto** | Non cercati oltre l'articolo di Youngblood et al. |
| **Biddle, S., *Military Power* (Princeton UP, 2004); Epstein, J. M., *The Calculus of Conventional War* (Brookings, 1985)** | Candidati per l'argomento 8: l'accesso al catalogo ha avuto errori di rete; per Epstein la scheda OL riporta 31 pp, dato incoerente con un libro: **scartato**. Non inclusi. |

---

## Limiti della ricerca

- **Strumenti**: ricerca web, lettura di pagine, interrogazione dei registri Crossref e Open Library. Molte pagine di
  editori (Bloomsbury, Springer, USNI, McGraw-Hill, Pearson, Routledge) e cataloghi (HathiTrust, TAMU, Library of
  Congress, WorldCat, Google Books per quota esaurita) erano **bloccati o non apribili** dall'agente; per i libri si è
  quindi usato Open Library come catalogo bibliotecario, con ISBN, anno, editore e numero di pagine, e schede di
  librerie o biblioteche emerse dalla ricerca come conferma di edizione. **Le schede editoriali ufficiali non sono
  state aperte**: il responsabile dovrebbe riscontrare almeno ISBN e anno dei libri sul frontespizio o sul catalogo
  della propria biblioteca.
- Il contenuto delle opere **non è stato letto**, tranne: l'articolo di Youngblood et al. (6.2), l'articolo di Lucas &
  McGunnigle (4.5, titolo, abstract e bibliografia), il sommario di Mahafza (5.5) e le pagine RAND (sommari).
  Le affermazioni su «che cosa tratta» ogni opera derivano da titoli, abstract e sommari; dove non verificate è detto.
- Nessun numero di capitolo o pagina interna è citato; i soli numeri di pagina sono quelli dei registri.
- Le **edizioni** sono quelle trovate: per Law e Hughes & Girrier esistono edizioni più recenti, non esaminate in
  dettaglio.
- Non trovate fonti primarie per: simulatori militari a eventi e a passo fisso (segnaposto della scaletta),
  convenzioni di portata radar, Poe 1974; non cercati Ph/Pk, shoot-look-shoot, tempi di reazione, soglia del 30%,
  golden master, carburante e turnaround.
- Le ricerche web hanno usato solo titoli, autori e argomenti generici di letteratura; nessun termine del progetto.
