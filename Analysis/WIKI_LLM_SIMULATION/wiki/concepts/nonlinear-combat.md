---
title: "Nonlinear Combat — Combattimento Non-Lineare Post-Guerra Fredda"
type: concept
tags: [campaign-model, post-cold-war, maneuver, spatial, doctrine]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[campaign-model]]", "[[piston-network]]", "[[generalized-network]]", "[[tlc-model]]", "[[tacwar]]", "[[variable-resolution-modeling]]"]
---

# Nonlinear Combat — Combattimento Non-Lineare

## Definizione

Il **combattimento non-lineare** (nonlinear combat) descrive operazioni militari in cui le forze non operano lungo un fronte continuo e lineare, ma si muovono in modo fluido, con penetrazioni profonde, manovre di aggiramento, e combattimento su assi multipli e non contigui. È il paradigma operativo dominante nel periodo post-Guerra Fredda.

## Contrasto con il Paradigma Lineare

| Paradigma | Caratteristiche | Esempio storico |
|-----------|----------------|-----------------|
| **Lineare** | Fronte continuo, avanzata/difesa uniforme | Fronte Orientale WWII, Piano OPLAN per Europa Centrale |
| **Non-lineare** | Penetrazioni, envelopment, deep attack, fronti discontinui | Operazione Desert Storm, operazioni in Iraq/Afghanistan |

La struttura a [[piston-network]] è progettata per il paradigma lineare. Il combattimento post-Guerra Fredda richiede strutture più flessibili.

## Elementi del Combattimento Non-Lineare

1. **Deep attack**: forze che attaccano ben oltre il fronte immediato (elicotteri, forze speciali, missili)
2. **Envelopment**: manovre di aggiramento su grandi distanze (es. "Left Hook" Desert Storm)
3. **Fronti discontinui**: vuoti nel fronte, settori non coperti, sacche di resistenza
4. **Rapidità**: la velocità di manovra crea condizioni che cambiano prima che la pianificazione si adatti
5. **Multi-asse**: operazioni simultanee su direttrici non parallele

## Perché i Modelli Legacy non lo Rappresentano

I modelli a piston ([[tacwar]], [[cem-model]]) falliscono nel rappresentare il combattimento non-lineare perché:

- **Il fronte è una singola linea**: non ci sono vuoti, sacche, o fronti discontinui
- **Movimento unidirezionale**: impossibile manovrare su assi laterali o in profondità
- **Aggregazione**: le forze in una banda sono un numero — non hanno posizione, non possono frazionarsi

> "Post-Cold War conflicts require the ability to represent deep operations, envelopment, and noncontiguous battle — phenomena impossible in piston structures." (Hillestad & Moore, 1994, parafrasato)

## Soluzione: Generalized Network

La [[generalized-network]] del TLC è progettata specificatamente per abilitare il combattimento non-lineare:
- Reti libere con archi in qualsiasi direzione
- Percorsi alternativi per manovre di aggiramento
- Regioni sovrapposte per rappresentare deep battle
- Multiple reti per rappresentare forze su assi diversi simultaneamente

## Applicabilità al Warfare-Model

Il DWM opera in scenari DCS tipicamente non-lineari (es. Caucaso, Golfo Persico) dove:
- Le forze aeree attaccano su direttrici multiple simultaneamente
- Le forze navali e terrestri operano su assi indipendenti
- La minaccia SAM si estende su tutto il teatro (non è confinata a un "fronte")

Il DWM deve quindi usare una struttura spaziale analoga alla rete generalizzata, non un modello a piston — conferma l'architettura Route/Area/Region attuale.

## Fonti

- Menzionato in: [[source-theater-level-campaign-model]] (pp. 6-10 — requisiti post-Guerra Fredda per i campaign models)
