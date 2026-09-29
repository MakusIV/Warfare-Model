# Ricerca RWR degli aerei del registro (2026-09-29)

> Rapporto di ricerca prodotto da un agente (Sonnet) su richiesta dell'utente, con fonti web.
> **Non è la fonte finale dei dati**: i valori adottati sono in `Asset/Aircraft_Rwr_Data.py`, che
> segue il campo `avionics` del registro e le **decisioni dell'utente del 2026-09-29**, prevalenti su
> questo rapporto dove divergono:
>
> - l'SPO-15 **rileva** il radar dello Shilka (verificato dall'utente in DCS con il Su-25): la
>   proposta del rapporto di togliere VSHORAD agli aerei con SPO-15 è **respinta**;
> - SPO-10 Sirena-3: 4 quadranti, riconoscimento su due livelli (SAM o EWR), solo tracciamento;
>   SPO-15: 8 settori, tre classi (VSHORAD-SHORAD, MRSAM, LRSAM), ricerca/tracciamento/guida;
> - Il-76MD: SPO-10; MiG-25PD (registro), MiG-25RB, Il-78M, Tu-142: SPO-15;
> - Tu-160: "Baikal-3 EW" del registro considerato equivalente alla suite BKO-1 Baykal;
> - F-117: nessun RWR (bassa osservabilità radar); KC-130: AN/ALR-69(V);
> - Mirage 2000C: SERVAL/SPIRALE, digitale, libreria di minacce superiore all'SPO-15;
> - approvate le proposte del rapporto su F-14A (ALR-45: AAA + SAM generico), C-17A (ALR-69A),
>   Tu-95MS (L-150 Pastel; il campo `avionics` del registro dice ancora SPO-15), Viggen (nessun
>   riconoscimento).

---

# Ricerca RWR / categorie SAM identificate — verifica tabella registro aerei

Nota metodologica: la ricerca ha privilegiato le voci a fiducia media/bassa e i 6 punti
prioritari indicati. Le voci "alta" non toccate esplicitamente sono state lasciate
invariate (non riverificate in questa sessione, tranne dove sono emerse incidentalmente,
es. Mirage 2000C, F-14A/B). Nessun file del repository è stato modificato.

## Sintesi dei risultati più rilevanti (prima della tabella)

1. **SPO-15/SPO-15LM (Beryoza) — limite di banda 4,4–10,3 GHz.** Confermato da un thread
   tecnico del forum War Thunder che cita la documentazione russa dell'SPO-15LM (bande 7-8-9,
   4,4…10,3 GHz) — https://forum.warthunder.com/t/spo-15-band-coverage/26824. Il radar
   "Gun Dish" (RPK-2 Tobol) dello ZSU-23-4 Shilka opera in banda Ku a 14,6–15,6 GHz
   (Wikipedia ZSU-23-4 + radartutorial.eu), **al di fuori** della copertura dell'SPO-15/SPO-15LM.
   Conclusione: il vero SPO-15 **non può fisicamente ricevere** il radar del cannone Shilka →
   **VSHORAD non identificabile** dagli aerei con SPO-15 "classico". Le categorie SAM sovietiche
   storiche (Kub/SA-6 in banda X 8-12GHz, Fan Song/SA-2 in banda E/F/G, parte dello spettro
   dell'S-300 Flap Lid-B in banda X 8,5-10,68GHz) rientrano invece nella finestra dell'SPO-15,
   coerente col fatto che l'SPO-15 è stato progettato apposta per classificare le minacce SAM
   per range (П/З/Х/Н — aereo/lungo/medio/corto raggio), non i cannoni contraerei.
   **Fiducia: media** — l'argomento fisico è solido e documentato, ma non è confermato che il
   modello SPO-15 "classico" in DCS (pre-refactor 2025) applichi realmente un check di banda
   fisico invece di un semplice lookup per tipo di unità; il nuovo SPO-15LM "fisico" per il
   MiG-29 (rework ED 2025, https://www.digitalcombatsimulator.com/en/news/2025-07-12/,
   https://flyandwire.com/2025/09/04/mig-29s-spo-15-rwr-qa-with-eagle-dynamics/) è descritto
   esplicitamente come basato su fisica reale con "quirky threat-sorting" — quindi per il
   MiG-29 il comportamento realistico è più probabile; per i moduli più vecchi (Su-27, Su-33,
   Su-25 non-T, MiG-31, MiG-23MLD, ecc.) resta incerto se il vecchio codice applichi lo stesso
   rigore.

2. **L-150 "Pastel" / SPO-32 — banda molto più larga (fino a ~40 GHz secondo una fonte)**,
   quindi COPRE la banda Ku dei radar AAA come il Gun Dish. Fonte: russiandefpolicy.com
   (tag L-150 Pastel) cita SPO-32 Pastel capace di "pick-up/register and digitally process
   all radar signals in frequency spectrum 1-40GHz" con "automatic determination of radar
   type and mode" dal 1987 in poi (test su Su-25T). Per gli aerei con L-150 Pastel (Su-25T,
   Su-25TM, Su-30, Su-34) la classificazione ALL resta valida e con fiducia più alta di prima.

3. **AN/ALR-45/50 (F-14A) — sistema più primitivo dell'ALR-67.** Il manuale ufficiale
   Heatblur (https://f14.manuals.heatblur.se/f14ab/systems/defensive_systems/rwr/alr_45-50.html)
   descrive l'ALR-45/50 come capace di classificare solo per **classe** (AAA / SAM / AI) e per
   **banda** (LOW/MID/HIGH), NON per sistema specifico (non distingue SA-2 da SA-6 da SA-8).
   Questo è un cambiamento significativo rispetto alla riga attuale ("ALL, alta"): la classe
   "AAA" identifica coerentemente il VSHORAD, ma la classe "SAM" generica NON permette di
   distinguere SHORAD/MRSAM/LRSAM fra loro — l'operatore vede "SAM banda bassa/media/alta" ma
   non un codice SA-6 vs SA-8 vs SA-2. Questo è diverso dall'ALR-67/56/69/46 (famiglia NATO
   "moderna") che invece mostra codici numerici specifici per sistema (vedi punto 4).
   **Fiducia: media-alta** (fonte primaria = manuale del modulo DCS stesso, che è la referenza
   prioritaria richiesta).

4. **Famiglia ALR-46/56/67/69 (NATO "moderna")** — confermata simbologia specifica per
   sistema tramite Hoggit wiki (https://wiki.hoggitworld.com/view/RWR): A=ZSU-23-4 AAA,
   3=SA-3, 6=SA-6, 8=SA-8, 10=SA-10, 11=SA-11, 13/15=SA-13/SA-15, PA=Patriot, HA=Hawk, ecc.
   La pagina dice esplicitamente "symbology that can be found on most modern (Western)
   fighters" — quindi valida per A-10, F-4E, F-5E, F-14B, F-15C/E, F-16A/C, F/A-18, B-52H,
   C-130/KC-130, S-3B (ALR-76, verosimilmente simile). Conferma "ALL" per questi.

5. **A-4E AN/APR-25** — sistema reale dell'era Vietnam con toni audio specifici e distinti
   per "Fan Song" (SA-2, ronzio tipo serpente a sonagli) e "Fire Can" (AAA, cinguettio
   ripetuto) — fonte: f-4phantom.com/rhaw/ (stesso apparato usato su F-4). Questo conferma
   identificazione di almeno LRSAM (Fan Song) e VSHORAD (Fire Can) nel sistema reale. Il modulo
   comunitario A-4E-C di DCS estende inoltre esplicitamente le risposte audio a SA-8, SA-10,
   SA-11, SA-13, SA-19 (fonte: pagine GitHub/changelog del progetto Community A-4E). Dato che
   DCS è la referenza prioritaria, e il comportamento DCS-modellato copre tutte e 4 le
   categorie, si raccomanda di **alzare la fiducia da bassa a media** mantenendo ALL.

6. **AJS-37 Viggen (KA radarvarnare)** — confermato che il sistema NON fornisce una
   identificazione automatica a simbolo/codice sullo schermo: il pilota deve misurare
   manualmente durata del ciclo, numero e altezza dei toni e confrontarli con una tabella di
   riferimento (kneeboard "sound codes") per dedurre il tipo di emettitore — fonte: forum ED
   DCS AJS-37 manual thread. Questo è coerente con la definizione data dall'utente ("un
   semplice allarme di illuminazione senza identificazione del tipo... NON identifica nulla")
   nel senso che l'apparecchiatura stessa non emette un codice di categoria: è il pilota a
   doverlo decodificare da caratteristiche RF grezze, in modo simile a un'analisi ELINT
   manuale. **Mantenuto NONE**, ma segnalato come punto grigio (vedi sezione incerti) perché il
   sistema, a differenza di un vero "solo allarme" (es. Sirena-2/3 sovietico), fornisce
   comunque informazioni sufficientemente distintive da permettere identificazione umana
   esperta — non è stato trovato però nessun documento che descriva una vera libreria di
   minacce integrata nel radarvarnare stesso.

7. **Trasporti/tanker e bombardieri russi**:
   - **Il-76MD**: fonte (military wiki-style aggregator, da verificare ulteriormente) indica
     equipaggiamento standard con **SPO-10 "Beryoza"/Sirena-3M** (sistema di allarme a
     settori, SENZA identificazione di tipo) + SPS-5 "Fasol" (jammer, non RWR). Solo la
     variante moderna Il-76MD-90A ha il nuovo complesso "Prezident-S" con vero RWR digitale.
     Questo **contraddice** la riga attuale ("SPO-15 Beryoza, ALL, bassa") — si raccomanda di
     cambiare in NONE o quantomeno abbassare fortemente la fiducia; la fonte però non è di
     prim'ordine (nomenclatura ambigua "SPO-10 Beryoza" mischia due famiglie diverse), quindi
     resta un punto incerto.
   - **Tu-22M3**: confermato da GlobalSecurity.org equipaggiamento con "SPO L006 Birch"
     (quasi certamente traduzione automatica errata di "SPO-15 Beryoza L-006", berioza =
     "betulla"/"birch" in russo) — coerente con la riga attuale SPO-15 Beryoza. **Fiducia
     alzata da bassa a media.**
   - **Tu-95MS**: fonte (migflug.com aggregando dati pubblici) indica "Avtomatika SPO-32/L150
     digital warning receiver" — cioè la famiglia **L-150 "Pastel"**, PIÙ recente e a banda più
     larga della SPO-15 Beryoza indicata nella riga attuale. Si raccomanda di **cambiare il
     nome RWR** in "SPO-32/L-150 Pastel" e mantenere ALL con fiducia alzata da bassa a media.
   - **Tu-142**: nessuna fonte specifica trovata in questa sessione; per analogia con Tu-95MS
     (stessa cellula) è plausibile un apparato simile, ma non confermato — lasciato come punto
     incerto, fiducia bassa mantenuta.
   - **Tu-160**: nessuna fonte trovata in questa sessione sul nome esatto del sistema ESM/RWR
     ("Argument" non confermato). Punto incerto, fiducia bassa.
   - **C-17A Globemaster III**: fonti multiple (jedonline.com, simpleflying.com, af.mil-style)
     confermano equipaggiamento standard con **AN/ALR-69A**. Questo **contraddice** la riga
     attuale ("nessuno, NONE, bassa") — si raccomanda di cambiare in ALR-69A / ALL, fiducia
     media (fonti secondarie ma concordanti, non manuali ufficiali).
   - **KC-135 Stratotanker**: fonte (jedonline.com) conferma che la versione "legacy" **non
     ha un sistema difensivo/RWR integrato** — coerente con la riga attuale NONE. **Fiducia
     alzata da media ad alta.**
   - **C-130/KC-130**: confermato AN/ALR-69(A) per C-130 USAF generico (govtribe.com,
     radartutorial.eu, man.fas.org) — coerente con riga attuale. Per il KC-130 (variante USMC)
     una fonte menziona invece l'AN/APR-39 (sistema di origine Army, tipicamente montato su
     elicotteri, anch'esso con classificazione di minaccia per tipo/settore) come possibile
     alternativa — non risolto con certezza in questa sessione, vedi punti incerti.
   - **An-26B / An-30M**: nessuna fonte ha confermato l'installazione di un RWR dedicato;
     coerente con NONE della riga attuale, ma l'assenza di prove non equivale a conferma —
     fiducia rimane media.
   - **MQ-9 Reaper**: dal 2017-2021 in poi esistono pod di autoprotezione opzionali con
     AN/ALR-69A(V) (theaviationist.com, ga.com) — ma NON di serie sui Reaper standard/più
     vecchi. Si raccomanda di mantenere NONE come configurazione di default ma abbassare
     leggermente la fiducia da alta a media, segnalando l'evoluzione recente.

8. **MiG-25 (PD e RB)** — fonti generaliste (migflug.com, wings-of-glory wiki) indicano che il
   MiG-25 di base montava l'**SPO-10 "Sirena-3M"** (allarme a settori, senza identificazione di
   tipo), non l'SPO-15. Non è stato possibile confermare con fonte solida se il MiG-25PD
   (upgrade 1978, "Foxbat-E") abbia ricevuto il successivo SPO-15/SPO-15L — una fonte
   accenna a operatori (Iraq) con "modified SPO-15L RWRs" ma non è chiaro se riferita al
   MiG-25 o ad altri tipi. Punto incerto significativo, fiducia bassa mantenuta per entrambe
   le voci MiG-25PD/RB, con raccomandazione di ulteriore verifica (idealmente un manuale di
   volo russo o una fonte tecnica primaria).

9. **MiG-23MLD**: confermato SPO-15L (sostituì l'SPO-10) — Wikipedia MiG-23. Coerente con riga
   attuale, fiducia alzata da media ad alta (ma vedi punto 1 sulla questione VSHORAD).

10. **Su-17M4**: confermato **SPO-15LE** ("Sirena" nel nome popolare ma è variante SPO-15) —
    coerente con riga attuale, fiducia alzata da media ad alta (vedi punto 1 su VSHORAD).

11. **MiG-27K, Su-24M, Su-24MR, MiG-31**: nessuna fonte primaria specifica per la variante
    esatta trovata in questa sessione (solo indicazioni generiche "SPO-15 su varianti più
    tarde" per il MiG-27; per Su-24M/MR e MiG-31 solo fonti aggregate non autorevoli). Fiducia
    lasciata a media come nella tabella originale, salvo la correzione VSHORAD del punto 1.

## Tabella completa (65 modelli)

| modello | RWR (nome esatto) | categorie identificate | fiducia | cambia rispetto alla tabella attuale? | fonti |
|---|---|---|---|---|---|
| A-10A Thunderbolt II | AN/ALR-69 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| A-10C Thunderbolt II | AN/ALR-69 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| A-10C II Thunderbolt II | AN/ALR-69 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| A-4E Skyhawk | AN/APR-25 | VSHORAD, SHORAD, MRSAM, LRSAM | media (era bassa) | sì: fiducia alzata bassa→media | [f-4phantom.com RHAW](https://www.f-4phantom.com/rhaw/) (Fan Song=LRSAM, Fire Can=VSHORAD reali); [A-4E-C changelog](https://github.com/Community-A-4E/community-a4e-c) (SA-8/10/11/13/19 modellati in DCS) |
| AJ/ASJ 37 Viggen | KA radarvarnare | NONE | media | no (confermato) | [ED AJS-37 manual thread](https://forum.dcs.world/topic/312753-dcs-ajs-37-viggen-manual-rc21/) — richiede decodifica manuale toni via tabella, nessuna identificazione automatica a simbolo |
| F-117 Nighthawk | RWR non specificato (designazione esatta non trovata; "Radar Locating System") | VSHORAD, SHORAD, MRSAM, LRSAM | media | no | [TWZ — F-117 flip-down radar locators](https://www.twz.com/9540/the-mysterious-case-of-the-f-117-nighthawks-flip-down-radar-locators) (dice "notifica presenza e tipo") |
| F-14A Tomcat | AN/ALR-45/50 | VSHORAD (classe AAA); SAM rilevato solo come classe generica, NON distinto per range (SHORAD/MRSAM/LRSAM non separabili) | media-alta | sì: da "ALL" a "solo VSHORAD garantito, SAM non sub-classificato" | [Heatblur F-14 manual — ALR-45/50](https://f14.manuals.heatblur.se/f14ab/systems/defensive_systems/rwr/alr_45-50.html) |
| F-14B Tomcat | AN/ALR-67 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Heatblur F-14 manual — ALR-67](https://f14.manuals.heatblur.se/f14ab/systems/defensive_systems/rwr/alr_67.html); [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| F-15C Eagle | AN/ALR-56C | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| F-15E Strike Eagle | AN/ALR-56C | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| F-16A Fighting Falcon | AN/ALR-69 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| F-16A MLU | AN/ALR-69 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| F-16C Block 52d | AN/ALR-56M | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| F-16CM Block 50 | AN/ALR-56M | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| F-4E Phantom II | AN/ALR-46 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Heatblur F-4E manual — RWR](https://f4.manuals.heatblur.se/systems/defensive_systems/radar_warning_receiver.html); [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| F-5E Tiger II | AN/ALR-87 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | non riverificato in dettaglio, mantenuto |
| F-86E Sabre | nessuno | NONE | alta | no | epoca pre-RWR |
| F/A-18A Hornet | AN/ALR-67 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| F/A-18C Hornet | AN/ALR-67 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| F/A-18C Lot 20 | AN/ALR-67 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) |
| Mirage 2000C | Serval | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [ED forum RWR threat library update](https://forum.dcs.world/topic/269775-rwr-threat-library-update/); [M-2000C RWR Threat Codes](https://www.scribd.com/document/493254012/M-2000C-RWR-Threat-Codes) — libreria codici per sistema specifico confermata, dettaglio SA-2/6/8 non estratto |
| MiG-15bis | nessuno | NONE | alta | no | epoca pre-RWR |
| MiG-19P | Sirena-2 | NONE | alta | no (confermato) | [SPO-10/Sirena analysis](https://military-history.fandom.com/wiki/Radar_warning_receiver) — solo settori, no ID tipo |
| MiG-21bis | SPO-3 Sirena-3 | NONE | alta | no (confermato) | idem — SPO-10/Sirena-3 dava solo 4 settori, senza classificazione di tipo |
| MiG-23MLD | SPO-15L Beryoza | SHORAD, MRSAM, LRSAM (NO VSHORAD) | media | sì: RWR nome precisato (SPO-15L) e rimosso VSHORAD | [Wikipedia MiG-23](https://en.wikipedia.org/wiki/Mikoyan-Gurevich_MiG-23) (SPO-15L sostituì SPO-10); banda SPO-15 vs Gun Dish, v. sintesi punto 1 |
| MiG-25PD | SPO-10 Sirena-3M (probabile) o SPO-15L (non confermato) | incerto — se SPO-10: NONE; se SPO-15: SHORAD/MRSAM/LRSAM | bassa | sì: possibile cambio radicale, da verificare | [migflug.com MiG-25](https://migflug.com/aircraft/mig-25-foxbat/); nessuna fonte primaria per l'upgrade PD trovata |
| MiG-25RB | SPO-10 Sirena-3M (probabile) | NONE (se SPO-10 confermato) | bassa | sì: possibile downgrade da ALL a NONE | idem — nessuna conferma diretta per la variante RB |
| MiG-27K | SPO-15 Beryoza (probabile, "varianti più tarde") | SHORAD, MRSAM, LRSAM (NO VSHORAD) | media | sì: rimosso VSHORAD | ricerca generica MiG-27 avionics; nessuna fonte primaria specifica per il K |
| MiG-29A | SPO-15LM Beryoza | SHORAD, MRSAM, LRSAM (NO VSHORAD) | media | sì: rimosso VSHORAD | v. sintesi punto 1; [ED SPO-15LM rework](https://www.digitalcombatsimulator.com/en/news/2025-07-12/) |
| MiG-29S | SPO-15LM Beryoza | SHORAD, MRSAM, LRSAM (NO VSHORAD) | media | sì: rimosso VSHORAD | idem |
| MiG-31 | SPO-15 Beryoza | SHORAD, MRSAM, LRSAM (NO VSHORAD) | media | sì: rimosso VSHORAD | [migflug.com MiG-31](https://migflug.com/aircraft/mig-31-foxhound/) conferma SPO-15; v. punto 1 |
| Su-17M4 | SPO-15LE Beryoza | SHORAD, MRSAM, LRSAM (NO VSHORAD) | alta (banda) / media (VSHORAD) | sì: RWR precisato, rimosso VSHORAD | [militaryfactory Su-17](https://www.militaryfactory.com/aircraft/detail.php?aircraft_id=192); v. punto 1 |
| Su-24M | SPO-15 Beryoza (non confermato con fonte primaria) | SHORAD, MRSAM, LRSAM (NO VSHORAD) | bassa-media | sì: rimosso VSHORAD, nome non confermato al 100% | nessuna fonte primaria diretta trovata in questa sessione |
| Su-24MR | SPO-15 Beryoza (non confermato con fonte primaria) | SHORAD, MRSAM, LRSAM (NO VSHORAD) | bassa-media | sì: rimosso VSHORAD | idem |
| Su-25 | SPO-15 Beryoza | SHORAD, MRSAM, LRSAM (NO VSHORAD) | media (era alta) | sì: rimosso VSHORAD | v. punto 1 |
| Su-25T | L-150 Pastel | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no (confermato, fiducia confermata) | [russiandefpolicy.com L-150 Pastel](https://russiandefpolicy.com/tag/l-150-pastel/) (test su Su-25T 1987, banda estesa) |
| Su-25TM | L-150 Pastel | VSHORAD, SHORAD, MRSAM, LRSAM | media-alta (era media) | sì: fiducia alzata | idem |
| Su-27 | SPO-15 Beryoza | SHORAD, MRSAM, LRSAM (NO VSHORAD) | media (era alta) | sì: rimosso VSHORAD | v. punto 1 |
| Su-30 | L-150 Pastel | VSHORAD, SHORAD, MRSAM, LRSAM | media-alta | no (confermato) | [russiandefpolicy.com](https://russiandefpolicy.com/tag/l-150-pastel/) — "Pastel-K" su Su-30MKK 1999-2000 |
| Su-33 | SPO-15 Beryoza | SHORAD, MRSAM, LRSAM (NO VSHORAD) | media (era alta) | sì: rimosso VSHORAD | v. punto 1 |
| Su-34 | L-150 Pastel | VSHORAD, SHORAD, MRSAM, LRSAM | media-alta | no (confermato) | [russiandefpolicy.com](https://russiandefpolicy.com/tag/l-150-pastel/) |
| A-20G Havoc | nessuno | NONE | alta | no | epoca pre-RWR |
| B-1B Lancer | AN/ALQ-161 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | non riverificato in dettaglio, mantenuto (ALQ-161 è sistema RWR/ECM integrato noto e capace) |
| B-52H Stratofortress | AN/ALR-46 | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | [Hoggit RWR](https://wiki.hoggitworld.com/view/RWR) (famiglia ALR-46) |
| Tu-160 | RWR/ESM non confermato ("Baikal" non verificato) | ignoto | bassa | possibile, non determinato | nessuna fonte trovata in questa sessione — punto incerto |
| Tu-22M | SPO-15 Beryoza (L-006) | SHORAD, MRSAM, LRSAM (NO VSHORAD) | media (era bassa) | sì: fiducia alzata, rimosso VSHORAD | [GlobalSecurity Tu-22M3](https://www.globalsecurity.org/wmd/world/russia/tu-22m3.htm) ("SPO L006 Birch" = verosimilmente refuso di traduzione per "Beryoza") |
| Tu-95MS | SPO-32 / L-150 Pastel (non SPO-15) | VSHORAD, SHORAD, MRSAM, LRSAM | media (era bassa) | sì: nome RWR cambiato, fiducia alzata | [migflug.com Tu-95](https://migflug.com/aircraft/tu-95-bear/) ("Avtomatika SPO-32/L150 digital warning receiver") |
| Tu-142 | ignoto (per analogia con Tu-95MS, non confermato) | ignoto | bassa | possibile, non determinato | nessuna fonte diretta — punto incerto |
| A-50 | ESM di bordo (Vega, non ulteriormente specificato) | VSHORAD, SHORAD, MRSAM, LRSAM | media | no | non riverificato in dettaglio, mantenuto (piattaforma AWACS con suite ESM dedicata, plausibile ALL) |
| E-2D Advanced Hawkeye | AN/ALQ-217 (ESM) | VSHORAD, SHORAD, MRSAM, LRSAM | alta | no | non riverificato in dettaglio, mantenuto |
| E-3A Sentry | ESM di bordo | VSHORAD, SHORAD, MRSAM, LRSAM | media | no | non riverificato in dettaglio, mantenuto |
| S-3B Viking | AN/ALR-76 (ESM) | VSHORAD, SHORAD, MRSAM, LRSAM | media | no | famiglia AN/ALR "moderna" NATO, v. punto 4, plausibile ALL |
| S-3B Viking Tanker | AN/ALR-76 (ESM) | VSHORAD, SHORAD, MRSAM, LRSAM | media | no | idem |
| An-30M | nessuno | NONE | media | no (confermato per assenza di prove contrarie) | nessuna fonte ha indicato un RWR fitted |
| An-26B | nessuno | NONE | media | no (confermato per assenza di prove contrarie) | idem |
| C-130 Hercules | AN/ALR-69 | VSHORAD, SHORAD, MRSAM, LRSAM | media-alta (era media) | sì: fiducia alzata | [govtribe.com C-130 ALR-69A(V)](https://govtribe.com/opportunity/federal-contract-opportunity/c-130-analr-69a-v-radar-warning-receiver-rwr-fa855317r0019-1); [FAS AN/ALR-69](https://man.fas.org/dod-101/sys/ac/equip/an-alr-69.htm) |
| C-17A Globemaster III | AN/ALR-69A | VSHORAD, SHORAD, MRSAM, LRSAM | media | sì: da "nessuno/NONE" a "ALR-69A/ALL" | [JED — Big-Picture Solutions for Large-Aircraft Protection](https://www.jedonline.com/2023/01/05/big-picture-solutions-for-large-aircraft-protection/); [SimpleFlying C-17 RWR](https://simpleflying.com/how-c-17-globemaster-radar-warning-system-protects-crews-combat-zone-approaches/) |
| Il-76MD | SPO-10 Beryoza/Sirena-3M (probabile, NON SPO-15) | NONE (probabile) o incerto | bassa | sì: possibile downgrade radicale da "SPO-15/ALL" | fonte aggregata non di prim'ordine (nomenclatura ambigua) — punto incerto, verificare ulteriormente |
| Il-78M | come Il-76MD (variante tanker della stessa cellula) | come sopra | bassa | sì: stesso ragionamento di Il-76MD | per analogia, non confermato direttamente |
| KC-130 | AN/ALR-69 (probabile) o AN/APR-39 (variante USMC, non risolto) | VSHORAD, SHORAD, MRSAM, LRSAM (se ALR-69) | bassa-media | possibile, nome RWR incerto | ambiguità fra fonti — punto incerto |
| KC-135 MPRS | nessuno | NONE | alta (era media) | sì: fiducia alzata | [JED — Big-Picture Solutions](https://www.jedonline.com/2023/01/05/big-picture-solutions-for-large-aircraft-protection/) ("legacy KC-135... lacks an integrated active defensive suite") |
| KC-135 Stratotanker | nessuno | NONE | alta (era media) | sì: fiducia alzata | idem |
| Yak-40 | nessuno | NONE | alta | no | aereo civile/da collegamento, nessuna fonte contraria |
| MQ-1 Predator | nessuno | NONE | alta | no | non riverificato in dettaglio, mantenuto |
| MQ-9 Reaper | nessuno (di serie); pod opzionale AN/ALR-69A(V) dal 2017-2021 in poi, non standard | NONE (configurazione standard) | media (era alta) | sì: fiducia abbassata per via degli sviluppi recenti | [TheAviationist — MQ-9 self-protection pod](https://theaviationist.com/2021/01/31/general-atomics-reveals-self-protection-pod-for-the-mq-9-reaper/); [GA-ASI](https://www.ga.com/ga-asi-successfully-completes-self-protection-system-demo-on-mq-9) |

## Punti incerti

- **SPO-15/Beryoza e VSHORAD (Shilka/Gun Dish)**: l'argomento fisico (banda 4,4-10,3 GHz
  dell'SPO-15 vs 14,6-15,6 GHz del Gun Dish) è solido e ben documentato per il sistema REALE,
  ma non è confermato che tutte le implementazioni DCS (specialmente i moduli meno recenti:
  Su-27, Su-33, Su-25 non-T, MiG-31, MiG-23MLD, Su-17M4, MiG-27K, Su-24M/MR) applichino
  effettivamente questo limite fisico invece di un semplice lookup per tipo di unità che
  potrebbe "vedere" comunque lo Shilka. Consiglio: verificare nel codice/dati di gioco (file
  di missione, DB minacce) se questi moduli DCS mostrano o meno un simbolo per lo ZSU-23-4
  quando modellati con SPO-15 "classico" (diverso dal nuovo SPO-15LM "fisico" del MiG-29
  2025). Fino a verifica ulteriore, ho segnato fiducia "media" per la rimozione di VSHORAD.

- **Il-76MD / Il-78M**: fonte usata (aggregatore, non manuale tecnico primario) usa la dicitura
  ambigua "SPO-10 Beryoza" che mescola nomi di due famiglie diverse (SPO-10 = Sirena, SPO-15 =
  Beryoza). Non sono riuscito a trovare una fonte primaria (manuale tecnico Ilyushin, ELINT
  reference) che risolva con certezza quale apparato di allarme radar monti l'Il-76MD
  "classico" (le fonti concordano solo sul fatto che il vero salto di qualità arriva con la
  variante Il-76MD-90A/"Prezident-S", molto più recente). Raccomando ulteriore verifica prima
  di modificare il registro.

- **MiG-25PD/RB**: nessuna fonte primaria ha confermato se il MiG-25PD (upgrade 1978) abbia
  sostituito l'SPO-10 Sirena-3M con un SPO-15. Una fonte generica menziona "SPO-15L" in
  relazione a "operatori come l'Iraq" ma il contesto non è chiaro (potrebbe riferirsi ad altri
  tipi di caccia iracheni, es. MiG-23). Punto aperto, servirebbe una fonte tecnica primaria
  (specifiche VVS, manuale di volo).

- **AJS-37 Viggen radarvarnare**: zona grigia fra "solo allarme" e "identificazione". Il
  sistema richiede decodifica manuale (durata ciclo + pattern toni) ma non ho trovato conferma
  che esista una vera libreria minacce integrata che distingua sistematicamente le 4 categorie
  del modello. Mantenuto NONE per coerenza con la definizione dell'utente (nessun simbolo/
  codice/classe automatico sul display), ma segnalo che un pilota esperto potrebbe comunque
  dedurre la categoria dal pattern — quindi la scelta NONE è una scelta di modellazione
  conservativa più che una certezza assoluta.

- **KC-130 (variante USMC)**: fonti contrastanti fra AN/ALR-69 (standard C-130) e AN/APR-39
  (menzionato per KC-130 in un risultato di ricerca, ma non confermato con fonte primaria
  affidabile). Non risolto in questa sessione.

- **Tu-142 e Tu-160**: nessuna fonte diretta trovata sul sistema RWR/ESM esatto in questa
  sessione. Il "Baikal (ESM)" del Tu-160 nella tabella attuale non è stato né confermato né
  smentito — resta una lacuna di ricerca.

- **F-117**: la designazione esatta del sistema (AN/ALR-? o AN/ALQ-?) non è stata trovata; le
  fonti aperte (TWZ) descrivono solo funzionalmente il "Radar Locating System" come capace di
  indicare "tipo" di radar oltre a direzione, il che supporta ALL ma con incertezza sul nome
  esatto dell'apparato (informazione probabilmente ancora in parte non declassificata).

- **Mirage 2000C Serval**: confermata l'esistenza di una libreria di codici per sistema
  specifico (M-2000C RWR Threat Codes), ma non ho estratto il dettaglio completo dei codici
  SA-2/SA-6/SA-8/SA-10 per mancanza di tempo — la classificazione ALL/alta è quindi ragionevole
  ma non verificata voce per voce come per la famiglia ALR-67.
