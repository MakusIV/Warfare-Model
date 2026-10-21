# Proposta — Allineamento del Piano della Missione (manuale DES §9.6, voce 11)

- **Stato**: APPROVATA (2026-10-21, richiesta dell'utente: prova U4a del sistema multi-LLM)
- **Esecutore previsto**: `oc-developer` con modello `openrouter/deepseek/deepseek-v4.1-flash` (prova del ruolo developer-normal)
- **Tipo**: solo testo di un documento; nessun file di codice, nessun test nuovo

## 1. Problema

Il manuale DES (`Analysis/Document/Manuale_Motore_DES/10_Limiti_Estensioni_Divergenze.md`, §9.6 voce 11) segnala che
`Analysis/Document/Piano_Implementazione_Missione.md` non e' allineato al lavoro fatto:
- l'intestazione (riga 3) non cita F5, F6 e G1-G5 e dice la F7b "in attesa di approvazione";
- nella tabella di §5 "Stato di avanzamento" la colonna «Commit» ha segnaposto «(commit F5-B)» ecc. per F5-B, F5-C, F6-A, F6-B1,
  F6-B2, e' vuota per F6-B2bis, G1-G5, F7a e F7b, e la riga F5-A riporta `94859d8a`, un commit «WIP ... (NON verificato)» che non e'
  un antenato di `HEAD` (il commit nel ramo e' `e723e82a`);
- le righe F6-B2bis e G1 dicono «FATTA (da verificare e committare)» e la riga F7b «FATTA (da verificare e approvare)», mentre sono
  committate e approvate (F7b: `dcedc541` «F7b verificata e approvata», fotografia 982).

I commit sono stati verificati con `git log` e `git merge-base --is-ancestor` il 2026-10-21.

## 2. Alternative

Una sola: sostituzioni testuali esatte. Nessuna decisione aperta.

## 3. Decisioni aperte

Nessuna.

## 4. Piano di intervento

Un solo file: `Analysis/Document/Piano_Implementazione_Missione.md`. Applicare le **16 sostituzioni** seguenti, ciascuna
**esattamente** come scritta (ogni testo "attuale" compare una sola volta nel file; il resto delle righe resta identico,
comprese le colonne «Note»). Non modificare nient'altro, in nessun altro file.

### Sostituzione 1

Testo attuale:
```
**Stato**: APPROVATO (2026-10-05, Q1-Q4 sì) e IN CORSO: fatte F0, F1, F2, F3, F4a, F4b, F4b+, F4b++, la riprogettazione dei test S3/S5, F4c, (2026-10-18) F7a e (2026-10-20) F7b, in attesa di approvazione (v. §5 "Stato di avanzamento").
```
Testo nuovo:
```
**Stato**: APPROVATO (2026-10-05, Q1-Q4 sì) e IN CORSO: fatte F0, F1, F2, F3, F4a, F4b, F4b+, F4b++, la riprogettazione dei test S3/S5, F4c, F5-A, F5-B, F5-C, F6-A, F6-B1, F6-B2, F6-B2bis, G1-G5, (2026-10-18) F7a e (2026-10-20) F7b; da fare F8-F9 (v. §5 "Stato di avanzamento").
```

### Sostituzione 2

Testo attuale:
```
| F5-A | FATTA | `94859d8a` (+ verifica e documentazione) |
```
Testo nuovo:
```
| F5-A | FATTA | `e723e82a` |
```

### Sostituzione 3

Testo attuale:
```
| F5-B | FATTA | (commit F5-B) |
```
Testo nuovo:
```
| F5-B | FATTA | `90f2d4de` |
```

### Sostituzione 4

Testo attuale:
```
| F5-C | FATTA | (commit F5-C) |
```
Testo nuovo:
```
| F5-C | FATTA | `4da618b1` |
```

### Sostituzione 5

Testo attuale:
```
| F6-A | FATTA | (commit F6-A) |
```
Testo nuovo:
```
| F6-A | FATTA | `00b6b531` |
```

### Sostituzione 6

Testo attuale:
```
| F6-B1 | FATTA | (commit F6-B1) |
```
Testo nuovo:
```
| F6-B1 | FATTA | `15ac3d3d` |
```

### Sostituzione 7

Testo attuale:
```
| F6-B2 | FATTA | (commit F6-B2) |
```
Testo nuovo:
```
| F6-B2 | FATTA | `6b1b7225` |
```

### Sostituzione 8

Testo attuale:
```
| F6-B2bis | FATTA (da verificare e committare) | |
```
Testo nuovo:
```
| F6-B2bis | FATTA | `96942ca7` |
```

### Sostituzione 9

Testo attuale:
```
| G1 (nuovo modello di bingo) | FATTA (da verificare e committare) | |
```
Testo nuovo:
```
| G1 (nuovo modello di bingo) | FATTA | `c1c0f576` |
```

### Sostituzione 10

Testo attuale:
```
| G2 (nuovo modello di bingo) | FATTA, verificata e approvata 2026-10-16 (fotografia 794) | |
```
Testo nuovo:
```
| G2 (nuovo modello di bingo) | FATTA, verificata e approvata 2026-10-16 (fotografia 794) | `e1d08121`, `e5465b31` |
```

### Sostituzione 11

Testo attuale:
```
| G3 (nuovo modello di bingo) | FATTA, verificata e approvata 2026-10-17 (fotografia 802) | |
```
Testo nuovo:
```
| G3 (nuovo modello di bingo) | FATTA, verificata e approvata 2026-10-17 (fotografia 802) | `b1931ec3`, `20f0e0db` |
```

### Sostituzione 12

Testo attuale:
```
| G4a (nuovo modello di bingo) | verificata e approvata 2026-10-17 (fotografia 878, con G4b) | |
```
Testo nuovo:
```
| G4a (nuovo modello di bingo) | verificata e approvata 2026-10-17 (fotografia 878, con G4b) | `9de461e0` |
```

### Sostituzione 13

Testo attuale:
```
| G4b (nuovo modello di bingo) | verificata e approvata 2026-10-17 (fotografia 878, con G4a e uscita di scena) | |
```
Testo nuovo:
```
| G4b (nuovo modello di bingo) | verificata e approvata 2026-10-17 (fotografia 878, con G4a e uscita di scena) | `9de461e0` |
```

### Sostituzione 14

Testo attuale:
```
| G5 (nuovo modello di bingo) | FATTA, verificata e approvata 2026-10-18 (fotografia 918) | |
```
Testo nuovo:
```
| G5 (nuovo modello di bingo) | FATTA, verificata e approvata 2026-10-18 (fotografia 918) | `6e7a9b81` |
```

### Sostituzione 15

Testo attuale:
```
| F7a (regole d'ingaggio di missione) | FATTA, verificata e approvata 2026-10-18 (fotografia 970) | |
```
Testo nuovo:
```
| F7a (regole d'ingaggio di missione) | FATTA, verificata e approvata 2026-10-18 (fotografia 970) | `9f87a3ad` |
```

### Sostituzione 16

Testo attuale:
```
| F7b (fuoco su posizione) | FATTA (da verificare e approvare) | |
```
Testo nuovo:
```
| F7b (fuoco su posizione) | FATTA, verificata e approvata 2026-10-20 (fotografia 982) | `dcedc541` |
```

## 5. Verifiche ed esito atteso

- `bash tools/ai/verifica.sh suite start` poi `wait` fino all'ESITO: atteso **Ran 4555 tests, OK (skipped=7)** (nessun codice
  toccato).
- `bash tools/ai/verifica.sh confronto start` (dopo la fine della suite, mai in parallelo) poi `wait`: atteso **982 identiche,
  0 cambiate, 0 nuove**.
- `git diff --stat` del commit: **1 file** (`Piano_Implementazione_Missione.md`, 16 righe cambiate) piu' il rapporto.

## 6. Rischi e limiti

- La voce 11 del manuale (§9.6) va segnata come chiusa nel manuale: **non** fa parte di questo piano (il manuale e' di
  `des-manual-writer`).
- Le colonne «Note» non vanno toccate anche se contengono riferimenti datati.

## 7. Rapporto

`Analysis/Document/Rapporti/Rapporto_allinea-piano_oc-developer.md` secondo `Rapporti/TEMPLATE.md`; commit sul branch
`ai/oc-allinea-piano` con messaggio in italiano.
