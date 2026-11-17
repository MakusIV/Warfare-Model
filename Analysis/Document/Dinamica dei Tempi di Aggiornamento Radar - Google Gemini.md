I radar di ricerca moderni — in particolare quelli a scansione elettronica (come i radar **AESA** - _Active Electronically Scanned Array_) — specificano spesso un **intervallo (range) di valori** per il tempo di aggiornamento della traccia o della scansione anziché un valore fisso perché **non sono più vincolati alla rigidità della rotazione meccanica**.

Nei vecchi radar meccanici, l'antenna ruotava a una velocità costante (es. 12 o 30 giri al minuto), garantendo un tempo di scansione fisso. I radar moderni, invece, gestiscono lo spazio e il tempo in modo **dinamico e adattivo**.

### Principali motivi della variazione del tempo di aggiornamento

I fattori che causano la variazione del tempo di aggiornamento (o _revisit time_) in un determinato settore o traccia comprendono:

#### 1\. Allocazione Dinamica delle Risorse (Priorità dei Bersagli)

I radar multifunzione non sprecano lo stesso tempo energetico su tutti i bersagli.

-   Un bersaglio lento, distante o con traiettoria prevedibile viene aggiornato meno frequentemente (intervallo di tempo più lungo).
    
-   Un bersaglio veloce, manovrabile o considerato una minaccia prioritaria viene tracciato con un "revisit rate" molto più elevato (intervallo di tempo più breve).
    

#### 2\. Modalità di Funzionamento (Ricerca vs. Inseguimento - _Track-While-Scan_)

Il radar divide le sue capacità tra la **sorveglianza di volume** (cercare nuovi bersagli su un'ampia area) e il **tracciamento di precisione** (mantenere il contatto sui bersagli già acquisiti). Il tempo necessario per completare un ciclo di ricerca dipende da quanti bersagli il radar sta seguendo contemporaneamente in quel momento.

#### 3\. Geometria del Volume di Ricerca (Settore vs. 360°)

Il tempo di aggiornamento varia a seconda di _dove_ e _come_ sta guardando il radar:

-   **Scansione a 360° (Volume completo):** Richiede più tempo per completare un ciclo completo.
    
-   **Scansione a settore ristretto (Es. modalità di difesa missilistica o puntamento avanzato):** Concentrando il fascio elettronico solo su una porzione angolare specifica, il radar può aggiornare la posizione dei bersagli in quel settore molto più frequentemente.
    

#### 4\. Tempo di Permanenza del Fascio (_Dwell Time_) e Integrazione degli Impulsi

Per rilevare bersagli a lunghissima distanza o in ambienti ad alto disturbo, il radar ha bisogno di accumulare più energia rimbalzata, aumentando il **tempo di permanenza** (_dwell time_) del fascio su una determinata direzione. Questo allunga temporaneamente il ciclo di aggiornamento rispetto a una ricerca rapida in condizioni di cielo pulito.

#### 5\. Condizioni Ambientali e Contromisure (Clutter e ECCM)

In presenza di forti disturbi ambientali (come maltempo, echi di terra/mare o contromisure elettroniche nemiche - ECM), il radar può decidere di ripetere i fasci di esplorazione o variare le frequenze, modificando dinamicamente i tempi di scansione per garantire l'affidabilità della traccia.

Want me to explain how AESA radar beam agility allows simultaneous tracking and searching?