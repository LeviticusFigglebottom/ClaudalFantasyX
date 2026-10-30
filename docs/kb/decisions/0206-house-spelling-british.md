# 0206 — House spelling: British (Oxford) everywhere the player reads

- **Status:** accepted
- **Date:** 2026-10-30
- **Roles affected:** story/narrative, ui, combat, progression
- **Author role:** lead

## Context
Player-facing text mixes spellings. Prose, lore and the glossary use British forms (colour, armour, grey, harbour, honour), while some UI and stat strings use American ones (Defense, Armor, Color palette). The story track's Act I proofread found about 15 such strings.

## Decision
1. Every player-facing string uses British spelling with Oxford -ize: Defence, Armour, Colour, Colour-blind-friendly, grey, harbour, travelled. Customize and organize stay as they are.
2. Only display text changes. Loc keys, ids and code identifiers (for example `STAT_DEFENSE` and `EQUIP_MENU_SLOT_ARMOR`) stay as they are.
3. The story track (act2-plan) applies the change as one FAST-TRACK. New text follows this rule, and the glossary's style note records it.

## Consequences
The game's voice stays consistent. Nothing in code or data ids moves, so no save or validator impact.
