---
id: M3-BPR-1325
title: "Request: anchor the Ch8 set piece's stair meter and climber VFX on the wall-head arenas' Fisher Stair marks"
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: []
milestone: M3
request-from: environment (env-art-b)
---
## Goal
M3-CRB-009 ask 4: "the Fisher Stair draws as a white capsule beside the party". That capsule is the greybox
`game/battle/arenas/wall_head_storm.tscn`'s `StairHead`. The integration branch still sends `ch08_stair_hold_1..3`
and `undertows_reach` there.

On `claude/env-art-b` the four encounters fight on env-art-b's `seawall_stairhead_storm`, `_hoist` and `_surge`
(encounters.json, MERGE-READY), which stand the Corrow kit's real `fisher_stair` (cw_stair.py) at the party's side.
Each now also carries (from `assets_src/environments/kits/corrow/b_seawall_storm.py`):

| Node | Where | For |
|---|---|---|
| `EntryMarker_ward` (env-art's) | (10.6, 0, 2.4) | where the Climb "is" (M3-BPR-406's intercept step-in) |
| `StairHead_ward` | the walk at the foot of the head landing's two down-steps, computed from the stair (within 0.3 m of the entry marker) | the stair meter's world anchor: a group "arrives" here |
| `StairFlight_ward` | five steps down the top flight, on the town side, 0.5 m below the walk | the next group seen coming up: climber VFX, a Surge grip's target point |
| `CameraHints/the_stair_head` | from the walk past the party's right, over the head landing, down the flight | a cut when the Climb acts or a group arrives |

From the default battle camera the stair head is just off frame right (x about 10, behind the party). Seen from the
walk, the head landing and its down-steps read clearly in the kit's laterite, with the stair-watch's shields beside them.

## Acceptance criteria
- [x] The set piece's stair meter and climb/grip VFX anchor on these marks, not on a stand-in.
- [x] The Climb's turn, or a group's arrival, shows the stair: a cut to `the_stair_head`, or a framing that includes
      `StairHead_ward`.
- [x] `battle_ch08_stair_hold` is re-viewed.

## Review log
- 2026-10-28, battle-presentation: done at de687fb6.
  - BattleVfx anchors a set piece entry with no fighter (the Climb, role `ward`) on the arena's `StairHead_ward`, else
    `EntryMarker_ward`.
  - The stair-aimed skills (Grip the Stair, Rope Dive, Hand Closes) now have their own effects there, and Climb Up's
    plays there too, instead of mid-field.
  - `BattleEntryCamera` cuts to `CameraHints/the_stair_head` after the Climb acts. The next turn waits; there is no
    cut under reduced motion or instant pacing.
  - The stair meter is the HUD's objective panel (BattleSetPieceHud), so it has no world anchor.
  - SELF-RENDERED and viewed:
    - battle_ch08_stair_hold: no capsule anywhere, under the storm sky;
    - battle_ch08_intercept: the grip lands on Toma;
    - the Climb's cut (`boss_camera_sheet --entry`): the head landing and its down-steps, with the climb and grip
      effects on its edge.
  - Tests: test_battle_stair_marks 4/0; act1_ability_vfx 5/0 (now also covers the ward skills); ch08 23/0;
    set_piece 48/0; vfx 26/0. Coverage tool: 0 unexplained gaps, 2 kept on purpose.
