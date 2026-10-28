---
id: M3-BPR-411
title: "Battle VFX coverage: 17 skills and 8 battle items play no effect (proposed library mappings)"
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: []
milestone: M3
request-from: combat
---
## Goal
The Lead's queue (battle-presentation, item 5): every skill and battle item should play a visible effect. Your
`game/data/vfx/battle/effects.json` `map` covers damage by element, heals, added statuses, KOs and the specials. But
an action with none of those plays nothing on the target: a guard, a cover, a cleanse, an MP restore, a delay push, a
summon, a withdrawal, a charge starting to gather.

`python3 tools/battle_vfx_coverage.py` lists the gaps on the current tables (`--json` for the proposal). As of
2026-10-27 that's 17 skills and 8 items, mostly Ch8's set-piece kit (the Climb, the Surge, Storm-Call), the
telegraph gathers and the cure items.

## Proposed `map` additions (library effects only, palette colours only; your call)
```json
{
 "items": {
  "bitterleaf": "heal",
  "brine_eyewash": "heal",
  "drag_net": "status_apply",
  "quiet_tea": "heal",
  "smelling_salts": "heal",
  "throat_honey": "heal",
  "tidewash_salve": "heal"
 },
 "skills": {
  "breach_gather": "status_apply",
  "climb_up": "status_apply",
  "close_the_hand": "status_apply",
  "gnaw_coil": "status_apply",
  "grip_the_stair": "status_apply",
  "hand_closes": "heal",
  "lines_taut": "status_apply",
  "reach_for_stair": "status_apply",
  "recrust_gather": "status_apply",
  "rope_dive": "heal",
  "rouse_polyp": "status_apply",
  "storm_call": "hit_lightning",
  "storm_call_sound": "status_apply",
  "surge_crawler": "status_apply",
  "surge_ebb": "status_apply",
  "surge_wing": "status_apply",
  "toll_gather": "status_apply"
 }
}
```
- **The revive** (`relighting_wick`) is reported but not proposed. Its hit likely carries the restored HP as a heal
  already; please verify before mapping it.
- **The telegraph gathers** get `status_apply` as a generic cue. A boss may keep its own gather (the Drownbell's
  `toll_gather` plays through BattleBossVfx on charge_started), so skip any that double.

## Acceptance criteria
- [x] `tools/battle_vfx_coverage.py` reports 0 unexplained gaps; the 5 left are kept on purpose (`INTENDED`).
- [x] Viewed on a render (the Act I sheets, M3-BPR-420) (the reduced-motion flash rules already hold: test_battle_reduced_motion_audit).

## Review log
- 2026-10-28, battle-presentation (the Lead, 13:25: rendering has no track, so battle-presentation owns effects.json):
  closed by M3-BPR-420. Every Act I ability and battle item has its **own** effect instead of the library mapping
  proposed here; the cure items, the wick and the drag net have their own too.
  - Five gaps stay on purpose, each with its reason in `INTENDED`:
    - the three ward-aimed skills: the stair entry has no fighter, so the push reaction is their motion;
    - the Drownbell's toll gather, which has its own rig;
    - Act II's `unravel`, paused.
  - Test: `test_every_gap_is_explained`.
