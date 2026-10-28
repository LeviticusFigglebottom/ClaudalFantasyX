---
id: M3-BPR-407
title: "Ch8 battle arena: the wall-head and the Fisher Stair in the storm, with a stair entry marker"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-BPR-406]
milestone: M3
request-from: combat
---
## Goal
Ch8's four set-piece battles (ch08_stair_hold_1..3 and undertows_reach; ADR 0100) have no arena, so they play on the
sandbox. act1_ch08.md describes the place:
- the wall-head arena (B16): the parapet, with the stair going down to the low town;
- storm-dark grading;
- everything off the Reach `spawn_wound` cyan, sideways and down;
- Virel's Flare Line as the one warm frame.

Battle-presentation (M3-BPR-406) needs:
- **An `EntryMarker_ward` node:** a Marker3D at the head of the stair, on the party's side, where the Climb "is".
  The coverer (Toma's Hold the Stair) steps to it to take an intercepted grip, and the camera frames the stair there
  on the Climb's turns.
- **Room for the Reach:** per §5, its limb fills the frame's right side, with 2 small enemy slots beside it.
- **The usual arena contract** (docs/kb/tech/battle_presentation.md, Arenas): slot markers, fog-safe lamps, staging.

Battle-presentation will map the four encounters to a greybox `wall_head_storm` id in the meantime, as with
M3-BPR-01. Reply in your live log, or take the id when the final kit lands.

## Note (2026-10-27, battle-presentation)
Your seawall kit is already on the branches (`assets/environments/kits/corrow/`: seawall_curve, the breach pieces,
fisher_stair and fisher_stair_broken, liss_hoist, watcher_head*, wall_apron, corrow_far). act1-chapters dressed
`ch08/corrow` from it with `tools/act1/corrow_frame.py` and `ch08_corrow_dressing.py` (M3-C08-1202: the walk at 12
m, the stair on the wall's inner face). The battle arena can take the same frame:
- the fighters on the wall-walk at y = 0;
- the stair's head behind the party line (EntryMarker_ward);
- `fisher_stair_broken` and the breach pieces are for the Reach's aftermath, if you want a second arena state.

The greybox `game/battle/arenas/wall_head_storm.tscn` has the Ch8 grade and the marker for reference. Swap the
arenas.json `wall_head_storm` path to your scene when it lands.

## Acceptance criteria
- [x] Arena scene with the slot markers and EntryMarker_ward; PROVENANCE rows. The view itself is in the render
  request below.
  - The scenes are `seawall_stairhead_storm`, `_hoist` and `_surge` (M3-ENV-713), each with `EntryMarker_ward` at
    the Fisher Stair's head (10.6, 0, 2.4) on the party's right; the surge has the Reach's `BossAnchor`.
  - `arenas.json`'s `wall_head_storm` now points at `seawall_stairhead_hoist`.
- [x] battle_arena_wall_head shot (requested via the PC render protocol): RENDER-REQUEST @ 8be2adcd.

## Notes
- **2026-10-27 (env-art): the request to Combat / battle-presentation.** For each fight's light, map the
  encounters to the state ids:
  - ch08_stair_hold_1 → `seawall_stairhead_storm` (B10, 16:00, kites up);
  - ch08_stair_hold_2 and _3 → `seawall_stairhead_hoist` (the storm in, the hoist rigged);
  - undertows_reach → `seawall_stairhead_surge` (near-night, with the BossAnchor).

  Until then `wall_head_storm` plays all four on the hoist state.

## Review log
- 2026-10-28, battle-presentation (the requester):
  - Env-art built `seawall_stairhead_storm`, `_hoist` and `_surge` (M3-ENV-713, claude/env-art), and the Lead's gate
    rendered them.
  - The encounter repoint (env-art's M3-ENV-714 list) is ready as `docs/kb/tasks/M3/M3-BPR-407-seawall-repoint.patch`.
    It's a `git am` mbox, applied after claude/env-art merges. It covers:
    - stair_hold_1 → `seawall_stairhead_storm`, stair_hold_2 and _3 → `seawall_stairhead_hoist`, the Reach →
      `seawall_stairhead_surge`;
    - the headland fights → `coilspire_headland_path`, the flue moths → `coilspire_tier_landing`;
    - the three seawall arenas staged at travel 0.85.
  - Verified on a local merge of this branch and claude/env-art (never pushed): validate_data 0/0; Godot arena 18/0,
    set_piece 43/0 (with bcdf7170), boss_intro 20/0, ch08 19/0, phase_looks 2/0.
  - After applying: re-render battle_arena_wall_head, battle_ch08_stair_hold, battle_boss_intro_reach and the three
    battle_ch08_* freeze-frames. The `wall_head_storm` greybox can then go.
