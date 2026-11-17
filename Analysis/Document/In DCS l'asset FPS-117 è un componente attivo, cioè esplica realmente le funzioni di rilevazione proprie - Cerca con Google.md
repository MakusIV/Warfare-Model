## Hai detto: In DCS l'asset FPS-117 è un componente attivo, cioè esplica realmente le funzioni di rilevazione proprie

In DCS l'asset FPS-117 è un componente attivo, cioè esplica realmente le funzioni di rilevazione proprie

### Risposta di AI Mode per In DCS l'asset FPS-117 è un componente attivo, cioè esplica realmente le funzioni di rilevazione proprie

**Sì, in DCS World l'asset AN/FPS-117 è un componente attivo** a tutti gli effetti.

Non si tratta di un semplice oggetto scenico o statico, ma di una stazione radar funzionante integrata nelle logiche di gioco.

Le sue caratteristiche operative principali includono:

-   **Funzione EWR (Early Warning Radar):** Se posizionato e configurato correttamente nel Mission Editor, agisce come radar di prima allerta. Rileva i contatti a lungo raggio all'interno dello spazio aereo simulato.[](https://www.missiledefenseadvocacy.org/defense-systems/an-fps-117/)
-   **Interazione con la rete AWACS/GCI:** Può trasmettere le informazioni di tracciamento alla propria coalizione. Tramite i menu radio di bordo (comandi AWACS F7), permette ai piloti IA e umani di ricevere vettori e informazioni sul traffico aereo nemico.[](https://www.reddit.com/r/hoggit/comments/1g5nvn5/trouble_using_awr_anfps117/)
-   **Emissione e RWR:** Genera reali emissioni elettromagnetiche in banda L. I velivoli dotati di Radar Warning Receiver (RWR) rileveranno il segnale dell'FPS-117, identificandolo come sorgente di ricerca aerea (solitamente marchiata con la simbologia dei radar di ricerca generici "U" o "EWR").[](https://en.wikipedia.org/wiki/AN/FPS-117)
-   **Agganciabile dai missili anti-radar (SEAD):** Poiché emette attivamente onde radio, l'FPS-117 è un bersaglio legittimo per i missili cercatori di radiazioni. Velivoli come l'F/A-18C o l'F-16C possono agganciarlo e distruggerlo utilizzando missili come l'**AGM-88 HARM**.

Se riscontri problemi con il suo funzionamento (come la mancata trasmissione dati), assicurati che nel Mission Editor sia impostato come unità di tipo "EWR" attiva e che non si tratti della mera variante _Static Object_ (decorativa), e verifica che non vi siano bug di build temporanei legati alla variante dotata di cupola (_domed_).[](https://forum.dcs.world/topic/358310-domed-fps-117-no-longer-performs-as-an-ewr/)

Se desideri approfondire, fammi sapere:

-   Se stai riscontrando problemi a **configurarlo come GCI** nel Mission Editor
-   Se ti serve aiuto per **integrarlo in uno script** (es. IADS o Skynet)
-   Quale **variante specifica** (base o con cupola/dome) stai utilizzando nella tua missione

Copiato negli appuntiImpossibile copiare negli appunti. Riprova più tardi.

-   Trouble using AWR AN/FPS-117 : r/hoggit
    
    \# Comments Section Ewr is a dcs task that goes on Russian origin EWR units and it does 2 things. Do Russian voice intercept contro...
    
    ![](data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAFIAUgMBIgACEQEDEQH/xAAbAAACAwEBAQAAAAAAAAAAAAAABAIDBgUBB//EADcQAAEDAgIFCQYHAQAAAAAAAAEAAgMEESExEkFRkZIFBhMUIlJTYaFCQ1RxgdEVJDIzcsHhY//EABgBAAMBAQAAAAAAAAAAAAAAAAABAgME/8QAHREBAQADAQADAQAAAAAAAAAAAAECERIDFCExBP/aAAwDAQACEQMRAD8Adk5Xn/58KUk5WmcfY4UjNIly+5W+mboHlCU5hm5R6445gJeCmnnbpRRPeBgS1pKtNBWfDS8BRow6oJ2Kt05upGirPh5eAqPUav4eXgKOS0j05BPmrGVBUOo1XgScBUhSVI9xJwFGhpe2c7Fc2qsP0+qoZTT64n8JUnQSNFyxw+bSpo5XdcHcQkTe6EFovK9VtxKnI3tIa2y3xmzanmnCyaCcPv2Xgix8l3RSwgW0X4fNcLmY7tVTfJpWnxLRY2Kwztl0qFxTsAwD9y96Bmx+5MgeZUtFT1RoqKZpyLvqvDTNHtFNOadRN1U8G2YupudPRR8Db/qKoqoYxC9zjfRaUzJcZu3Bc7lObRopydTEt202WJFyhKmbHP1QteaQmIGKo6XFVSy3Gaoa/FduGKLWy5lSfmKhu1gPqtg04LC8zJLV0g2xf2Fs2yav7XJ7TWasfwyCpApfTsLqTXrE1riqXuXjn44iyolksFJoSvzXC5wS6HJs1szYLpzPWe5zy2oNHa8KsJvIVmTKUJYuxQuzlntZpXCg09perxo7S6cUtDzUfo8ofOMhbNshvq3L51Q1MlJKJYiA4AjEXXR/Ha7xG8IWHr43LLcOXTc9KbZjcgSkDBw3LD/jld425oUTy3XeMeELK/z5KmTbvnPeSstSLZrGScs1p9+7cEu/lSsd796n49HTYS1Pms7zlm04omg+0SuW+vqz7+TiSlRUSy/uyOdbLSKeHlzdi1VdChhtQtydHoo9bnfQD7qbYYRm6T0CZmo5dUb7fxKXfRzaon8JRMqz3E/y7fFPycPsjTph7MvGPslX0k/hvH0VJpJu45X1S6h8zUwyjf8AWUfZVunp7ftb5P8AEkaKbuqIpJQ4XaLeZStp9Q06oh1RjjKh08Xhs3lRnpzJJeKFsYta11EUcnkp+x1Fomj7jPVRMrNTWeq9bRv2hWNoXFLVHcUaTfDYhN9QO1CNUum8naLnALnTgbAhC1jCkJQL5JSRCFYLvzVEhN80ISoV3O1SBO1CFJrWq+LNCEqcMWGxCEKVP//Z)
    
-   Digital Combat Simulator | DCS World
    
    EWR RADAR MOD V1.5 Update - User Files
    
    The EWR RADAR MOD simulates the GE Aerospace/Lockheed Martin Domed AN/FPS-117 and Hughes Aerospace HR-3000 HADR. Enjoy! NOTE: Vers...
    
    ![](data:image/jpeg;base64,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)
    
-   Domed FPS
    
    \# Recommended Posts \* spikef22 Posted October 1, 2024 spikef22 Members 139 Posted October 1, 2024 As title says issue does not see...
    
    ![](data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAFIAUgMBIgACEQEDEQH/xAAbAAABBQEBAAAAAAAAAAAAAAAAAQIDBQYEB//EADgQAAEDAgMDCgQEBwAAAAAAAAEAAgMEEQUSUSExQQYTFCJSYXGBkaEWMkKSFTNE0QdDVYLB4fD/xAAYAQADAQEAAAAAAAAAAAAAAAAAAQIDBP/EACMRAAICAgIBBAMAAAAAAAAAAAABAgMRFBNSURIhQZEEMTL/2gAMAwEAAhEDEQA/APJCEhapsiMqoRBZBCmy9yTKmBFZJY6KbIgtsLlAiKyhmmbHsG1yZUVO9sW7i5ciTYxz3uebuKapIYJJjZjb9/Bd8NExm2Tru9lJSRWeaFdZG9keiVA8HTzZ0SGMqy6K7RKaV2i1wZZK0R6oMeisxRPduCf0Ajek8DSbKZ7Qxpc8gNG8lVNZVc6SyM9QcdVPjVSHzmCI3jjO09oqvYxz3BrQS4mwA4qWxpDVYUuHOdZ84IHZ4lWuHYO2nAkn60ultjVYcyOA9lJaiVbYg0ANFgOAS5FZGIaX8knMPPysPojJWCuyIVj0ebsH0SoyHpNf+FaMR+GycGN+0Lc9Dh1CaaODULn3qOxPFYvgw/4bIPpHos/yvqThVCGCwnnu1mzaBxK9UlpqZjHPkexrWglzidgA4rwDlVi/41jdRVtuIL5IG6MG713+a1rvhb/InGUf2VC3fJ3ky+lgbU1UZ6Q8XDT/ACx+6i/hlydbiuIPxCrA6LSHqg7nycB5b/RequootR6rKz8muEvS37lxrk1nBhzh57KYcPdp7rbOoYu71UL6GPuWe5X5L4peDGGhcOHuozRv71sX0Ufd6rnfRR9ye3W/kfFIynQ3d6Fpuhx9yEbMPI+ORg/ibG/6hN95TTyjxo/rpfuVCJDql506rXgr6r6J2LOzLLEsfxWWjlinq5XRyNyuGbeCs3xXTWSlwa2+zeoYReVt9VpGEYrEUZznKby2X2HYxiGHUjKemmdGwXNhqd66vijFx+peqfnQVFNUZBlZ8x46LJ01yeXFGyvsisKReO5X4kzY6pN9LKN3LXFPpkv4rOzRSRPLZmlrr7bpuU2GzeL7Ea1PVC2rexofjXGO3H9p/dPby1xL6ww+Fws6YjkY7tmw0UgjhdDcSFsjTZwduPgjWp6oW1b2ND8aVnZ90LOGA3/MiP8AeEiWtT1Ht2+STOkMgHFc90LoOcc92Z1yka4tcCE1KgCTnX93okddzr7dCUwKanqHwElliHbHNcLgoA7BM9lG9smRwIAH1b77f+04LnpnRl0jSOu4ZWEbG+fsnTziZoMYyBtyWg7bnju8FyuaWhpuOsL7CkJImi55kkZLCcvyh9wEyQPaDm2ZjtbfiNRw3obNIbNdK8NNgdu4BTBwk5yMujJNsrgz5j/goAhD4gBeIk8Tn/0hNMTwSC1wI7kJ+w8kaEIQAJUIQAvBCEIAkpyRKyxI6w3J9L+fbhlOzyQhAEDvmPipKckTMINjmG7xQhAMmq55hVzASyAc476jqhCEkSj/2Q==)
    
-   Produzione di acido ialuronico mediante processi ... - Inail
    
    Sommario. L'acido ialuronico è una molecola preziosa naturalmente presente nell'organismo, fondamentale per mantenere idratazione,
    
-   EWR AN/FPS-117 Radar (domed) : DCS World : USA
    
    DCS World : USA : dcs\_class\_radar : EWR AN/FPS-117 Radar (domed) ... Bombers · Multirole fighters · Fighters · Interceptors · Batt...
    
-   Missile Defense Advocacy Alliance
    
    AN/FPS-117 - Missile Defense Advocacy Alliance
    
    The AN/FPS-117 is a fixed position, solid state, long-range, three-dimensional radar that provides airspace surveillance.\[i\] It co...
    
    ![](https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcTQuR1KLYkoRggXRpu24ABj4rYMYvrZ8q74haRKehiLk1B2xw4ji65s1Z0b-aIoky0f8gJz6ompx-6aJ385Bs53emIuZwTa95JWrCCF)
    
-   AN/FPS-117
    
    \# Description The system is a long range (up to 250 nautical miles or 460 kilometres), L-band pencil beam search radar with solid-
    
    ![](https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcTtqTZSLjEcb1QQdvW6QaVhY6V4WuYmw3l_BpvRnuuQ0yYg2VjcJDPV3-YTqOU1doQFBEihgWr1vJqwrW4ElNA1Ypz1WuGBDcF1U1MO)
    

Come è classificato l'FPS-117 all'interno del DCS editor: Vehicle?

### Risposta di AI Mode per Come è classificato l'FPS-117 all'interno del DCS editor: Vehicle?

No, nell'editor delle missioni di DCS World l'asset **AN/FPS-117 non si trova sotto la categoria "Vehicle"**, bensì all'interno della macro-categoria **Ground Crew** (indicata dall'icona del carro armato nella barra laterale sinistra).

Per posizionarlo come unità attiva e funzionante, devi seguire questa classificazione interna:

-   **Macro-categoria dell'editor:** `Ground Crew` (Unità di terra).
-   **Category (Tipo/Sottocategoria):** `Air Defence` (Difesa Aerea).
-   **Type (Modello specifico):** Lo troverai elencato come `EWR AN/FPS-117 Radar` oppure `EWR AN/FPS-117 Radar (domed)` (a seconda della variante con o senza cupola protettiva).

💡 Un dettaglio importante sul Mission Editor:

Se cerchi l'FPS-117 cliccando sull'icona delle strutture o degli oggetti statici (`Static Objects`, l'icona a forma di ponte/casa), troverai una versione puramente estetica e decorativa del radar. Quella variante _Static_ non emette segnali, non rileva aerei e non può svolgere compiti di GCI/AWACS.

Per farlo funzionare attivamente, usa sempre l'icona del carro armato (`Ground Crew`), impostalo come coalizione USA (o qualsiasi paese NATO che lo includa in database) e vedrai che l'editor gli assegnerà automaticamente il task predefinito **EWR** (Early Warning Radar).[](https://www.reddit.com/r/hoggit/comments/1g5nvn5/trouble_using_awr_anfps117/)

Copiato negli appuntiImpossibile copiare negli appunti. Riprova più tardi.

-   EWR AN/FPS-117 Radar : DCS World : USA : dcs\_class\_radar
    
    Strategic bombers · Bombers · Multirole fighters · Fighters · Interceptors · Battle planes · Reconnaissance aircrafts
    
-   AN/FPS-117 - Wikipedia
    
    AN/FPS-117. Article · Talk. Language; Save; Edit; Download PDF. The AN/FPS-117 is an L-band active electronically scanned array (A...
    
    ![](data:image/jpeg;base64,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)
    
-   EWR AN/FPS-117 Radar (domed) : DCS World : USA
    
    DCS World : USA : dcs\_class\_radar : EWR AN/FPS-117 Radar (domed)
    
-   Mission Editor Static Vehicles - DCS World 1.x (read only) - ED Forums
    
    15 nov 2015 — Well there is simple static icon. By clicking static window open on right side of editor. Just check the mouse pointer and tool ti...
    
    ![](https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQ_4lTSMOF2P-eyXGOILe-q1tVyAsrGqlx8MQW0XqgNMwZ8crCLsehzz2nIfgfcft9oG9ZDEYNYhUjufyaGeOz8cCG3enQp6IiyQMAm)
    
-   YouTube·Lock Ostrie | Kestrel 1-1
    
    DCS World Mission Editor: Static Objects
    
    4 mag 2023 — Adding static objects enhances missions by providing ground targets and increasing environmental detail. Static objects lack AI an...
    
    ![](https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcSRWiF-TsbAgE8UWGPTLrRKcCj8s19wDdzDSUW2pBQCLp99PZc3)
    
-   Trouble using AWR AN/FPS-117 : r/hoggit
    
    Ewr is a dcs task that goes on Russian origin EWR units and it does 2 things. Do Russian voice intercept control and pass detectio...
    
    ![](https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcRpmUpZlTBkJiFq6UyZ1bDInUD9eDscYPZPmYSgRtw59czcSgUVp6vFxNm8wY43nk2pAXGaPL-WQz4NBIpfA2ugwKMRmh_1WUAOh_ch)
    
-   DCS editor FAQ - DCS World Wiki
    
    The unit is missing from a database that assigns it to a given country. Liveries are assigned on a per country basis in its descri...
    
    ![](https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcR68Rigp2pItgcvyagiNc9tFLSf3Vth1deqRRZLtCVylJztwL_yua2Vha6gCV7bGBgjT5aDzFyqnZmRE1p0REhycApIrnoLTjVjDDzl)
    

Quali sono gli altri asset attivi presenti in DCS non classificati come vehicle, ship, aircraft?

### Risposta di AI Mode per Quali sono gli altri asset attivi presenti in DCS non classificati come vehicle, ship, aircraft?

All'interno dell'architettura di DCS World, gli "attivi" (ovvero entità dotate di script, intelligenza artificiale, capacità di emettere segnali o interagire dinamicamente con il mondo di gioco) che **non** sono classificati formalmente come veicoli semoventi (`Vehicle`), navi (`Ship`) o aeromobili (`Aircraft`), appartengono principalmente a tre macro-categorie del Mission Editor o del motore di gioco:[](https://wiki.hoggitworld.com/view/DCS_Scripting_orig_Part_2)

1\. La Fanteria (`Infantry`)

Pur trovandosi sotto l'icona generica delle unità di terra (`Ground Crew`), la fanteria non è considerata un "veicolo". Si tratta di asset attivi a tutti gli effetti:[](https://flyawaysimulation.com/ask/answers/ground-forces-infantry-dcs-world/)

-   **Soldati standard, MANPADS e anticarro:** Si muovono, rispondono al fuoco in modo autonomo, ingaggiano minacce aeree (es. con missili _Igla_ o _Stinger_) o terrestri e possono essere imbarcati e trasportati dagli elicotteri tramite le funzioni di script di DCS.

2\. Le Strutture e Postazioni Fisse (`Fortifications` / `Air Defence` fisse)

Esattamente come l'AN/FPS-117, esistono altre strutture che, se posizionate tramite il menu delle unità di terra (`Ground Crew`), smettono di essere semplici palazzi distruttibili e diventano sistemi d'arma attivi, dotati di radar e sensori propri:[](https://wiki.hoggitworld.com/view/DCS_Scripting_orig_Part_2)

-   **Punti FARP (Forward Arming and Refueling Point):** Le piazzole di atterraggio avanzate per elicotteri. Sono asset attivi che forniscono attivamente servizi di rifornimento, riparazione e riarmo dialogando con la radio del pilota.
-   **Sistemi SAM fissi (es. Linee Hawk, S-75 / SA-2, S-125 / SA-3):** Molti di questi vecchi sistemi missilistici storici hanno componenti radar o lanciatori pesanti che l'editor gestisce come postazioni fisse collegate a una rete logica di difesa aerea, emettendo radiazioni agganciabili dai missili SEAD proprio come l'FPS-117.
-   **Bunker e Postazioni d'artiglieria costiera/fissa:** Strutture d'arma statiche che ruotano e sparano autonomamente contro i bersagli designati nella loro linea di tiro.

3\. Gli Aeroporti e le Basi Aeree (`Airbases` / `Airdromes`)

A livello di codice di DCS, l'aeroporto intero non è uno sfondo grafico, ma un **asset attivo del motore di gioco**:[](https://wiki.hoggitworld.com/view/DCS_Scripting_orig_Part_2)

-   Possiede frequenze radio dedicate, sistemi ATC (Air Traffic Control) guidati dall'IA che gestiscono attivamente i flussi di decollo/atterraggio, e controlla l'accensione e lo spegnimento delle luci di pista o dei sistemi di navigazione assistita (come i canali **TACAN** o **ILS**).

Ti interessa approfondire come **far cooperare la fanteria e i SAM fissi** tramite trigger nell'editor, oppure stai cercando una lista per **configurare le zone di difesa** della tua missione?

Copiato negli appuntiImpossibile copiare negli appunti. Riprova più tardi.

-   Civilian Objects And Vehicles - Static/AI Mods for DCS World
    
    4 mag 2021 — 1\. CIVILIAN ASSETS PACK - NAUTICAL v2.1 DOWNLOAD v2.1 Content, installation, credits, etc: README.pdf If you have downloaded v2.0,
    
    ![](data:image/jpeg;base64,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)
    
-   DCS Scripting orig Part 2 - DCS World Wiki - Hoggitworld.com
    
    Unit (airplanes, helicopters, vehicles, ships, structures, ammo, sensors); Airbase … tasks, commands, behavior options); Refueling...
    
-   Does DCS World have infantry, tanks and ground combat?
    
    DCS World supports AI-controlled armoured vehicles, artillery, air defences, transport units and several types of infantry.
    
    ![](data:image/jpeg;base64,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)