---
id: M2-CHR-07
title: Battle clip set for Asha, Rhen and Toma (the battle-presentation clip contract)
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
reviewer: combat
depends_on: [M2-CHR-06, M2-FP-07]
milestone: M2
request-from: combat
---
## Goal
The battle-presentation track (branch `claude/battle-presentation`) added a choreography layer, BattleChoreo. It plays named clips when a hero's actor has them, and falls back to procedural motion otherwise. Its clip contract is in `docs/kb/tech/battle_presentation.md` § Clip contract on that branch.

Give each hero's clip library (`hero_clips.py` → `assets/characters/<hero>/anim/<hero>_clips.tres`, which the battle actors already load through the import rule) these clips:
- **Looping:** `idle`, `victory`.
- **One-shot:** `ready`, `attack`, `cast`, `item`, `read`, `defend`, `finisher`, `hit`, `dodge`.
- **Hold the last frame:** `ko`.

All clips are in-place: no root translation, because the sequencer moves the root. A strike's contact frame lands at `contact_at` of its length, per style in `game/data/battle/choreo.json`: attack 0.55, cast 0.8, finisher 0.62.

## Acceptance criteria
- [ ] The clips exist for all three heroes, and each reads in the hero's own idiom:
  - Asha: the staff, low sway;
  - Rhen: a light, quick crouch with the reef-hooks;
  - Toma: a broad stance with the spear and shield.
- [ ] The existing clips (idle and the dialogue clips) keep their names. The battle `idle` may be the existing `idle` if it suits.
- [ ] Contact frames are at the contract's `contact_at` fractions, with a test asserting them.
- [ ] Rig guards: `tools/tests/test_rig_integrity.py` samples the new clips, and the ratchets do not rise. Any new hit is fixed or documented.
- [ ] The clip-library .tres files regenerate deterministically; `verify --job asha` (and rhen, toma) stay identical.
- [ ] Shots: `<hero>_battle_attack` (at the contact frame) for each hero, viewed and approved.
- [ ] Handoff, and a note in characters.md.

## Notes

## Review log
