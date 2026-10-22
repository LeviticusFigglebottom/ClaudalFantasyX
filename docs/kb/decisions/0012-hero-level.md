# 0012 — Hero `level` is one fixed constant; growth comes only from the Lattice

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** Combat, Progression, UI, QA
- **Author role:** Combat (combat-stream-2), answering the question in the M1-PRG-01 review log (item 6)

## Context
The damage and healing formulas use `stat + level` (formulas.md § Damage). Enemies set `level` in `enemies.json`. Every hero sets `level: 5` in `characters.json`, but nothing ever raises it: growth comes from the Lattice (SPEC §6.4), whose stat nodes may not touch `level` (the validator rejects a `level` node). The inspiring genre has no experience levels in this sense either: the board *is* the growth. Pillar 5 ("growth you can see") asks that progression be spatial and visible, and pillar 4 asks that the numbers the player reads are the numbers that matter.

So `level` is a constant pretending to be a stat. Before M2 enemy tuning we need to decide what it is.

## Options
1. **Fixed constant, the same for every hero.** Keep the term in the formula as a flat "potency floor" (so a low-strength healer's Attack still scratches). It is declared once per hero in `characters.json`, must be equal across heroes, and no system changes it in play.
2. **Fixed per character.** Same as 1, but each hero may have a different value, for example a late-joining veteran.
3. **Derived from the Lattice**, e.g. `level = 1 + floor(nodes_activated / k)`. This is a second, hidden growth channel layered on stat nodes. It double-counts growth, so every Lattice node would be worth more than its label says. It needs changes in `game/progression/` (another role's code) and a retune of the LP pacing.
4. **Remove `level` from hero formulas** (enemy-only or gone). Every hero number drops by about 20–30% at M1 stats, which forces a full retune now. It also makes the shared damage formula asymmetric, or makes enemies lose their tuning knob.

## Decision
**Option 1.** Every hero has the same fixed `level`, which is **5** today. It stays in `characters.json` (`stats.level`), because the schema is shared with enemies.
- `tools/validate_data.py` errors if heroes disagree on `stats.level`.
- `BattleEngine` restores a hero's data level if a `party_modifier` (the Lattice's `apply_to`) changes it, and reports that with `push_error`.
- `LatticeProgress` already refuses `level` nodes.
- **Enemies keep `level` as a real data field**: their tuning tier, set per enemy in `enemies.json`.
- The UI does not show a hero level. Showing "Lv 5" forever would mislead (pillar 4). The bestiary may show enemy tier later.

Option 2 was rejected because a per-hero hidden potency is exactly the invisible stat pillar 5 warns against. A late joiner who should be stronger gets higher base stats, which the player can see.

Damage numbers do not change: every hero was already level 5. The sandbox balance bands are unaffected.

## Consequences
- One growth axis: a hero's damage changes only through visible stat nodes, equipment (later) and statuses. The sim and the balance targets reason about Lattice stats alone.
- `level` reads as a flat +5 on every offensive stat for heroes, which matters most early, when stats are small, and fades late. If late-game damage needs a curve, that is a new ADR (for example a Lattice-driven multiplier), not a quiet level bump.
- If a future design wants a visible "level" (for example the number of nodes activated, as a badge), it must be cosmetic and must not feed the formulas without superseding this ADR.
- Progression must keep `level` out of `LATTICE_STATS` (already true).
