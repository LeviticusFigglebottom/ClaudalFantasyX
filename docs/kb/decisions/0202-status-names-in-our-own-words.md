# 0202 — Status effects get our own names

- **Status:** accepted
- **Date:** 2026-10-29
- **Roles affected:** design, ui, combat, battle-presentation, all writers
- **Author role:** lead

## Context
SPEC §6.8 lists the statuses. On their own most are generic genre words, but Shell, Protect, Reflect, Regen, Doom, Zombie and the four "X Break" statuses together reproduce the inspiring series' own status set and naming (SPEC §2, IP guardrail). ui-menus raised it on 2026-10-29 and proposed replacements.

## Decision
**Player-facing names** (loc text, SPEC, codex, tips, battle log) change as follows:

| Old | New |
|---|---|
| Shell | Tide Ward |
| Protect | Bulwark |
| Reflect | Mirrorwater |
| Regen | Mending |
| Doom | Last Tide |
| Zombie | Hollowed |
| Armor Break | Sundered |
| Mental Break | Unmoored |
| Power Break | Weakened |
| Magic Break | Dimmed |

Poison, Sleep, Silence, Darkness, Petrify, Slow, Haste, Stop, Berserk, Confuse and Provoke stay as they are, since they are generic.

**Internal ids** (JSON keys, enum names, test names) may keep their old spelling. They are never shown to players, and renaming them would churn every battle table for no player-visible gain. New ids should use the new names.

**`tools/banned_terms.txt`** gains the four "X Break" phrases (case-insensitive). ui-menus adds them in the same commit as the rename, so the data gate never goes red. The single generic words (shell, protect, reflect, doom) are **not** banned, because they occur innocently, as in the Shell Shrine.

SPEC §6.8 is updated (v1.6).

## Consequences
- ui-menus owns the loc and text change across Act I, plus a check that no player-facing string uses an old name.
- Formulas and mechanics are unchanged.
