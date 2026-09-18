#### Installazione mappa

Innanzitutto, è necessario aver acquistato un qualsiasi DCS Teatro, qualsiasi di essi può essere installato in DCS World.  
È possibile acquistare la mappa nel nostro E-Shop: [Teatri DCS](https://www.digitalcombatsimulator.com/it/products/terrains/)  
Una volta installato DCS, accedete al gestore dei moduli del gioco: la mappa acquistata dovrebbe essere disponibile per il download.

In caso contrario, verificare che l'acquisto sia legato al proprio account ED utilizzando il [controllo della licenza.](https://www.digitalcombatsimulator.com/it/personal/licensing/)

#### Trasferire i moduli su un'altra unità

Trasferimento dei moduli su un'altra unità  

Spesso, a causa delle grandi dimensioni dei moduli di DCS World, non c'è abbastanza spazio libero sull'unità per installare nuovi moduli.

Se sul nostro sistema sono installate due o più unità, abbiamo la possibilità di trasferire separatamente i moduli di grandi dimensioni su un'altra unità utilizzando i collegamenti simbolici delle cartelle in Windows.

Come trasferire un modulo su un'altra unità utilizzando l'esempio della mappa del Caucaso inclusa nel gioco gratuito DCS World:  

Ad esempio, il gioco è installato in: D:\\Games\\DCS World (OpenBeta) e in aggiunta abbiamo l'unità E.  

1\. Creare una cartella sull'unità E, ad esempio DCS World Modules.  

2\. Spostare la cartella Caucasus in: D:\\Games\\DCS World\\Mods\\terrains nell'unità E nella cartella DCS World Modules.

2.1. Dopo aver spostato la cartella Caucasus, accertarsi che non si trovi nella cartella D:\\Games\\DCS World\\Mods\\terrains.

3\. Avviamo il prompt dei comandi (cmd) come amministratore; a tale scopo eseguiamo il comando attraverso il menu Start. Fare clic con il pulsante destro del mouse - Start - Esegui: scrivere cmd e fare clic su OK.

4\. Nella finestra della console visualizzata, scrivere il comando: mklink /J "D:\\Games\\DCS World\\Mods\\terrains\\Caucasus" "E:\\DCS World Modules\\Caucasus".

5\. Controllare se nella cartella terrains è presente un collegamento alla cartella Caucasus.

**In Windows sono consentiti i collegamenti simbolici:**  

Se, per qualche motivo, si ottiene l'errore "Il collegamento simbolico non può essere seguito perché il suo tipo è disabilitato", aprire un prompt dei comandi come amministratore e immettere il comando: fsutil behavior set SymlinkEvaluation L2L:1 R2R:1 L2R:1 R2L:1  

#### Come installare i teatri (mappe) senza Internet su PC? (o problemi di connessione sul PC)

A causa del volume piuttosto elevato del simulatore (soprattutto con il rilascio della mappe del Nevada) ci sono spesso domande sul modulo di aggiunta rapida, che è già stato scaricato su un altro computer. Il modo "frontale" di copiare può funzionare, ma prima o poi si finisce per reinstallare tutto. 

Come fare in modo corretto e sicuro:

1\. Copiare il modulo esistente in una posizione temporanea qualsiasi, mantenendo la struttura delle cartelle del simulatore (ad esempio, E:\\DCSCopy\\Mods\\terrains\\Nevada).   
2\. Creare nella directory principale del simulatore DCS il file di testo con il titolo: dcs\_local\_source.txt  
3\. Il contenuto del file è il percorso di una directory temporanea, in questo caso (UTF-8!): E:\\DCSCopy\\Mods\\terrains\\Nevada  
4\. Eseguire DCS World, andare in Gestione moduli e avviare l'installazione del terreno Nevada. L'Updater troverà i file esistenti, confronterà i numeri di versione, scaricherà tutto il necessario e lo installerà correttamente.  
5\. Dopo l'installazione di Nevada sul secondo PC, è possibile eliminare la directory temporanea.