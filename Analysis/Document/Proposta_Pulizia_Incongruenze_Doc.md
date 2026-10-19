# Proposta — Pulizia di incongruenze documentali (manuale §9.6, voci 14-18)

- **Data**: 2026-10-19 · **autore**: sessione principale Claude (pilota della Fase 7 del sistema multi-LLM)
- **Stato**: APPROVATA dall'utente (2026-10-18 la pulizia era già fra i "prossimi" passi; perimetro ridotto
  al pilota il 2026-10-19)
- **Esecutore previsto**: `oc-developer` (OpenCode) sul branch `ai/oc-pulizia-doc`

## 1. Problema
Il manuale DES (`Analysis/Document/Manuale_Motore_DES/10_Limiti_Estensioni_Divergenze.md` §9.6) elenca testi
di commenti, docstring e documenti di progetto superati dal codice. Il codice è corretto; vanno allineati
**solo i testi**. Questo piano copre le voci 14, 16, 17 e 18 (codice) e 15 (documenti).

## 2. Alternative
Nessuna: si tratta di allineare testi a fatti già verificati nel manuale. Le voci 11, 12, 19, 21 restano
fuori (richiedono ricostruzioni dalla storia git o scelte di presentazione).

## 3. Decisioni aperte
Nessuna.

## 4. Piano di intervento
**Vincolo generale**: si modificano SOLO commenti, docstring e testo Markdown. Nessun identificatore,
istruzione, valore o import del codice cambia. Se un testo "attuale" sotto non si trova esattamente
(righe spostate), cercarlo nel file: se non c'è più, **fermarsi e riferire**.

### P1 — `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py` ~riga 1676 (voce 14)
Attuale:
```
        # Dominio di coordinamento di ogni forza (2026-10-11, v. "Dominio di coordinamento" nel
        # docstring del modulo): calcolato in _build_forces, default = la forza stessa.
```
Nuovo:
```
        # Dominio di coordinamento di ogni forza (2026-10-11, v. "Dominio di coordinamento" nel
        # docstring del modulo): calcolato in _build_domains (chiamato subito dopo _build_forces),
        # default = la forza stessa.
```

### P2 — `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py` ~riga 374, docstring del modulo (voce 18)
Attuale:
```
- **Re-scheduling delle finestre NON implementato (R4, seconda parte, rimandato).** Una
  forza che si disingaggia e' solo *segnalata* nell'esito; il nuovo instradamento e il
  ricalcolo delle finestre di contatto spettano a un livello superiore (C2/campagna).
```
Nuovo:
```
- **Re-scheduling delle finestre NON implementato nel risolutore (R4, seconda parte).** Una
  forza che si disingaggia e' solo *segnalata* nell'esito; il nuovo instradamento e il
  ricalcolo delle finestre di contatto non li fa questo modulo: dal G4b li fa la sessione
  (`Session_Simulator`, ri-pianificazione dopo il disingaggio).
```

### P3 — `Code/Dynamic_War_Manager/Source/Logic/Mission_Adapter.py` ~riga 165, docstring del modulo (voce 16)
Attuale:
```
    di una base del suo lato, `air_base_points` entro `AIR_BASE_AREA_RADIUS_M`, stima); altrimenti
    esce di scena all'arrivo, come prima (postura
    `OFF_SCENE_POSTURE`), finche' la F6 non portera' il rientro nella rotta.
```
Nuovo:
```
    di una base del suo lato, `air_base_points` entro `AIR_BASE_AREA_RADIUS_M`, stima); altrimenti
    esce di scena all'arrivo (postura `OFF_SCENE_POSTURE`; dal G4b la stessa postura vale per chi
    esce di scena per `BINGO_EXIT`).
```

### P4 — `Code/Dynamic_War_Manager/Source/Logic/Mission_Adapter.py` ~riga 371, commento di `OFF_SCENE_POSTURE` (voce 16)
Attuale:
```
# Postura finale (F5, nell'esito di sessione) di un aereo uscito di scena alla fine di una rotta che
# non termina su una base vera: ETICHETTA PROVVISORIA, finche' la F6 non portera' il rientro (RTB)
# nella rotta. Non e' un valore di Context ne' una grandezza.
```
Nuovo:
```
# Postura finale (F5, nell'esito di sessione) di un aereo uscito di scena alla fine di una rotta che
# non termina su una base vera e, dal G4b, di chi esce di scena per BINGO_EXIT: ETICHETTA (non piu'
# provvisoria: il rientro portato dalla F6 e' il bingo). Non e' un valore di Context ne' una grandezza.
```

### P5 — `Code/Dynamic_War_Manager/Source/Command/Session_Types.py` ~riga 163, docstring di `SessionOrder` (voce 17)
Attuale:
```
        missions: le `Mission` della sessione (Fase 3 del piano della Missione), default
            nessuna: gli asset senza missione restano fermi. Vincoli: `mission_id` unici; un
```
Nuovo:
```
        missions: le `Mission` della sessione (Fase 3 del piano della Missione), default
            nessuna. Gli asset senza missione non si muovono (dalla F4c gli aerei sono a terra e le
            unita' di superficie in difesa); gli asset di missione, dalla F5, sono presenti anche
            fuori dalla rotta. Vincoli: `mission_id` unici; un
```

### P6 — `Analysis/Document/Piano_Implementazione_Missione.md` ~riga 161 (voce 15)
Attuale:
```
Rende possibili TOT comune, CAP con tempo sulla stazione e sosta a terra.
```
Nuovo:
```
Rende possibili TOT per missione, CAP con tempo sulla stazione e sosta a terra. **[Esito: il TOT comune
d'Operazione previsto qui è stato rimosso il 2026-10-12, decisione dell'utente: il TOT è di ogni missione,
`Mission.tot`; v. §5, F5-C.]**
```

### P7 — `Analysis/Document/Proposta_Struttura_Missione_Decisioni.md` ~riga 160 (voce 15)
Attuale:
```
  sosta, schieramento in attesa). Serve a sincronizzare le missioni di un'Operazione (TOT comune),
```
Nuovo:
```
  sosta, schieramento in attesa). Serve a rispettare il TOT di ogni missione (**[Esito 2026-10-12: nessun
  TOT comune d'Operazione, il TOT è di ogni missione]**),
```

### P8 — `Analysis/Document/F4_Differenze_Scenari.md` ~riga 856 (voce 15)
NON cambiare il titolo della sezione (è citato altrove). Inserire, fra il titolo
`## F5 passo (c)-(d): attese WAIT, ETA bloccate, TOT comune, ETA effettive (F5-C, deviazione 13)` e la riga
vuota che lo segue, una riga vuota e poi:
```
> **Nota (2026-10-19)**: le parti di questa sezione sul TOT comune d'Operazione sono storia della F5-C: il TOT
> comune è stato rimosso il 2026-10-12, v. «Correzione: TOT per missione» in fondo alla sezione.
```

### Fuori perimetro
- Il manuale (`Manuale_Motore_DES/`) NON si tocca: lo stato delle voci §9.6 lo aggiorna `des-manual-writer`
  al prossimo aggiornamento del manuale.
- Nessun test da scrivere o modificare (cambiano solo testi).

## 5. Esito atteso delle verifiche
- Suite completa (`bash tools/ai/verifica.sh suite ...`): **Ran 4490 tests, OK (skipped=7)**, come prima.
- Confronto con la fotografia (`bash tools/ai/verifica.sh confronto ...`): **compared 970 runs: IDENTICAL**.
- `git diff --stat` del branch: esattamente i 6 file di P1-P8 più il rapporto.

## 6. Rischi e limiti
Minimi: un errore di indentazione in un commento o docstring Python non cambia il comportamento ma un
errore di sintassi (es. triple virgolette toccate) romperebbe l'import: la suite lo rileverebbe.
