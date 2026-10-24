---
id: M2-CHR-07
title: Battle clip set for Asha, Rhen and Toma (the battle-presentation clip contract)
role: character
status: review
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
- [x] The clips exist for all three heroes, and each reads in the hero's own idiom:
  - Asha: the staff, low sway;
  - Rhen: a light, quick crouch with the reef-hooks;
  - Toma: a broad stance with the spear and shield.
- [x] The existing clips (idle and the dialogue clips) keep their names. The battle `idle` may be the existing `idle` if it suits.
- [x] Contact frames are at the contract's `contact_at` fractions, with a test asserting them.
- [x] Rig guards: `tools/tests/test_rig_integrity.py` samples the new clips, and the ratchets do not rise. Any new hit is fixed or documented.
- [x] The clip-library .tres files regenerate deterministically; `verify --job asha` (and rhen, toma) stay identical.
- [x] Shots: `<hero>_battle_attack` (at the contact frame) for each hero, viewed and approved.
- [x] Handoff (2026-10-24-character-12.md). The characters.md live-log line is left to the characters session, which owns that file.

## Notes
- 2026-10-24 (worktree subagent of the characters session): done; handoff `docs/kb/handoffs/2026-10-24-character-12.md`
  has the clip names, lengths and contact times for the battle track, and what to ask of choreo.json.
- Code: the "M2-CHR-07" block of `assets_src/characters/asha/hero_clips.py` (new functions, plus one dispatch line in
  `pose_at` and one marker line in `build`). The clips before it are byte-identical, so their shots are unchanged.
- Contact = a pose marker in the clip data: `BATTLE_CONTACT` keys each strike pose at exactly that fraction, and the
  library writes it as an Animation marker named `contact`. `tools/tests/test_hero_battle_clips.py` also checks that the
  striking bone (`BATTLE_STRIKER`) peaks on the key nearest the marker.
- Ratchet: Asha's VerseSleeve count 4 -> 6 (depth limit unchanged), viewed; the note is in rig_checks.json.

## Review log
