---
id: M3-MNU-05
title: "Request (FAST-TRACK): a Spells page in the field menu (FieldSpell), and the Relighting Wick's field use checked"
role: ui
status: todo
owner_session: ""
depends_on: [M3-CMB-03, M3-CMB-05]
milestone: M3
request-from: combat
reviewer: combat
---
## Goal
The human's playtest (2026-11-03), FAST-TRACK 5: spells castable outside combat, and a revive usable in the field. combat-systems owns the rules and data (done on `claude/combat-systems`); ui-menus owns the screens.

## What combat-systems exposes
**Spells (M3-CMB-05): `FieldSpell`** (`game/progression/field_spell.gd`, Node-free; formulas.md § Field spells). It works on the party as the field menus build it, `PartySheet.combatant(cid)`:
- `FieldSpell.castable(sheet.battle_db, caster) -> Array[StringName]`: the caster's field spells in skill order (today: Asha's Mend; Chorus Mend once learned on the Lattice). A hero with none can be greyed out or hidden.
- `FieldSpell.for_skill(db, sid) -> FieldSpell` (null when battle-only). On it: `name_key()`, `mp_cost()`, `target()`, `is_group()` (all_allies / all_other_allies: no hero pick needed).
- `caster_error(caster)`: `ERR_NOT_KNOWN`, `ERR_CASTER_DOWN` (KO or stone), `ERR_NO_MP`, or `RESULT_OK`.
- `target_error(caster, t)`: `ERR_FALLEN`, `ERR_PETRIFIED`, `ERR_WOULD_HURT` (Zombie), `ERR_NOTHING` (full HP, nothing to clear), or `RESULT_OK`.
- `cast_error(caster, party, chosen)`: the caster's error first, then the target's; `ERR_NO_ONE` for a group spell that helps nobody.
- `preview(caster, party, chosen)` and `cast(caster, party, chosen)`: `{ok, error, mp_cost, mp_before, mp_after, changes: [{id, hp_before, hp_after, removed}]}`. The preview runs on copies and is exact (no RNG out of battle), so "Rhen: HP 120 → 350 · Asha MP 60 → 56" is the whole truth (pillar 4). `cast` spends the MP once and changes the combatants.
- **Saving is the caller's**, exactly as `ItemsMenuModel._save` does for items: `state.record_vitals(...)` for the caster (MP) and every changed target, keeping the saved Swell and mode and the carried statuses only.

**The revive (M3-CMB-03):** the Relighting Wick (`relighting_wick`) already works on the Items page (`ItemsMenuModel`: "field": true + a revive effect; `FALLEN_TAG_KEY` marks the KO'd). Please check it reads well now that it is bought at Haluna from Ch2: the fallen hero is pickable, the preview line shows "HP 0 → 105", and a standing hero gets the refusal in words.

## Acceptance criteria
- [ ] A Spells entry on the field menu (or a Spells view on the Items page; your call): pick the caster, then the spell (MP cost and the caster's MP shown), then the target, with the exact preview line and every refusal in words (new loc keys in a menus csv).
- [ ] Each cast writes the vitals back (the caster's MP and each target's HP) and the party cards update.
- [ ] Tests over a scratch GameStateData, as `tests/unit/test_items_menu.gd` does.
- [ ] The Wick's field use checked with a fallen hero.

## Notes
- After a won fight the KO'd now come back at 1 HP (M3-CMB-04), so a "fallen" hero in the field mostly comes from an escape or a carried state.

## Review log
