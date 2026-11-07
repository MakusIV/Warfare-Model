---
name: project-bi-dati-decisioni
description: "Decisioni D1-D6 dell'utente sulla Proposta_Dati_Bersagli_Intercettabili.md (blocco 0 BI, dati dei 52 missili); aggiornare man mano"
metadata:
  node_type: memory
  type: project
  originSessionId: 695ff177-5a7a-4644-9469-5c6efb8cb41e
  modified: 2026-11-07T21:29:49.364Z
---

Proposta dati: `Analysis/Document/Proposta_Dati_Bersagli_Intercettabili.md` (non committata al 2026-11-07; lotti di ricerca `Bozze/Ricerca_Dati_Bersagli_L1..L7_oc-researcher.md` non committati). Le scelte vengono date in chat; la riga "scelta utente:" del documento NON e' ancora compilata (compilare solo se l'utente lo chiede).

**Attenzione alle lettere**: nel messaggio di chat avevo rinominato le opzioni di D1; nel documento (a)=R1-D, (b)=R1-K, (c)=R1-Ø. Citare sempre le lettere del documento.

- **D1 DECISA (2026-11-07)**: R1-K = inviluppo della famiglia Maverick fissata False da BI-6 (AGM-65D/K, RB-75T): diametro <= 304,8 mm **e** massa <= **304 kg** (valore verificato, colonna F/G di designation-systems; 306 kg di Wikipedia non riletto). **Lunghezza esclusa dal metro.** Zona grigia da approvare a mano: Kh-25MP, Kh-25MPU, AGM-88, RB-05A, RB-05E (+ Kh-25MR solo se vale 320 kg). Proposta resta False per tutte; i flag non cambiano. Cambia il testo di BI §2.5 / test 5 di §5.2 (massa limite 304 kg).
- **D2 DECISA (2026-11-07)**: (a) Mistral resta `tactical` con `ad_detectable` False, anomalia da segnalare al manutentore dei registri (nessuna classe `sam`).
- **D3.1 DECISA (2026-11-07)**: (a) Kh-22N `anti_ship` (classe per ruolo; domini {naval}).
- **D3.2 DECISA (2026-11-07)**: (a) KD-63/KD-63B restano `cruise` (solo da bombardiere H-6); correggere la frase di BI §2.2 nel blocco 4.
- **D3.3 DECISA (2026-11-07)**: (a) Kh-29L/T/TE, Kh-58, Kh-31P `ad_detectable` True (regola 2 del metro).
- **D4.1 DECISA (2026-11-07)**: (a) massa ancora Harpoon = 515,25 kg (FAS, aviolanciato); D_H = 343 mm. Nota: D5 e' raccomandata (b) ricerca mirata perche' D1 = R1-K, non R1-Ø.
- **D4.2 DECISA (2026-11-07)**: (a) valori discordi: 1) verificato dal principale, 2) fonte piu' specifica, 3) a parita' il piu' vicino al confine (basso per True, alto per False); l'altro valore nel commento.
- **D5 DECISA (2026-11-07)**: (b) ricerca mirata con oc-researcher V4 Pro su 6-8 voci (Kh-25MR, RB-05A/E, LD-10, AGM-65K 306 kg, Kormoran diametro, Kh-22N designazione/massa, KD-63); ~0,4-0,5 $ stimati; poi verifica del principale. Compito da preparare in `.ai-run/` DOPO D6; lo lancia l'utente.
- **D6 DECISA (2026-11-07)**: (a) voci senza dati propri (KD-63B, KD-20, Kh-555, 9M120-F, RB-05E, diametro Kh-65/RB-75T, massa YJ-18): classe per famiglia, nessuna dimensione nel registro; il test 5 salta le voci senza la coppia. TUTTE LE DECISIONI D1-D6 PRESE; restano ricerca mirata D5 (b) e le 5 voci grigie.

**Why:** la regola dell'utente e' "il Maverick e' piccolo"; il criterio misto diametro+massa tiene conto di entrambe le grandezze.
**How to apply:** nel blocco 1 della BI il test 5 usa 304,8 mm e 304 kg; le 5 voci grigie si chiedono una per una dopo D2-D6. Vedi [[project-session-2026-11-07-summary]].

**Ricerca mirata M1 (V4 Pro, 0,371 $) FATTA 2026-11-07**: `Bozze/Ricerca_Dati_Bersagli_M1_oc-researcher.md`. Verificati dal principale (web-fetch): Kh-25MR **299 kg**/275 mm (missilery.info, ru-wiki 320 respinto), RB-05A **305 kg** (AEF) e 304 kg (Astronautix)/300 mm. Non risolti: AGM-65K 306 (solo Wikipedia), LD-10 200/234 kg, KD-63 fonte unica, KD-63B/RB-05E inesistenti in fonti. Kormoran 600 kg/340-344 mm. Kh-22N: 2 fonti dicono "N = nucleare" (registro: Anti_Ship, testata 1000 kg convenzionale) -> anomalia di registro da aggiungere a §7, non cambia D3.1.
Implicazioni: con Kh-25MR 299 kg e limite 304 kg il Kh-25MR NON e' piu' zona grigia (F!). RB-05A/E restano grigie (305 > 304). Voci grigie finali: Kh-25MP, Kh-25MPU, AGM-88, RB-05A, RB-05E. Prossimo: presentare le 5 voci grigie, poi planner aggiorna la Proposta dati.

**Voci grigie TUTTE DECISE (2026-11-07)**: AGM-88, Kh-25MP, Kh-25MPU, RB-05A, RB-05E = **False** (opzione (a) per ciascuna). Kh-25MR non e' piu' grigia (299 kg < 304) -> False obbligatorio. TUTTE le decisioni sulla Proposta dati sono prese; prossimo: aggiornare la Proposta dati (scelte, §10.2 con D1=R1-K, §7 anomalia Kh-22N nucleare vs registro) e il testo di BI §2.5/test 5 (304 kg) con un planner, su conferma dell'utente.

**des-planner (Opus high) ha aggiornato Proposta dati + BI (2026-11-07 notte)**, non committato. Flag invariati (32 True/20 False). Cambi valori in §10.2: Kh-25MR 320->299 kg, LD-10 203/234->200/200 (criterio 2 D4.2: stessa portata 80 km del registro; Deagel 60 km), AGM-114 49->45,7 kg (colonna B/C). Test 5 con costante `GREY_ZONE_APPROVED`. **PUNTO APERTO**: il planner ha messo il **Kormoran** (340 mm con D4.2, quindi zona grigia sul lato alto) in `GREY_ZONE_APPROVED` come "approvato True (§6.11)", ma l'utente NON l'ha mai approvato esplicitamente (gli avevo detto "5 voci grigie"): chiedere conferma (Kormoran True o False) prima di dire la Proposta pronta. Altri dubbi del planner: YJ-18 senza diametro, YJ-12 tiene 500 mm/2000 kg (fonte debole), nessun effetto sui flag.

**Kormoran CONFERMATO True dall'utente (2026-11-07)**: punto aperto chiuso; la riga "approvata" del planner ora e' veritiera. Tutte le decisioni dati sono prese e le Proposte (dati + BI) sono allineate; restano da committare (insieme a bozza M1, lotti L1-L7, costi, memoria). Prossimo: commit su richiesta, poi delega codice BI blocchi 1-3 (des-developer Sonnet high proposto, branch `ai/...` dopo commit; conferma utente).
