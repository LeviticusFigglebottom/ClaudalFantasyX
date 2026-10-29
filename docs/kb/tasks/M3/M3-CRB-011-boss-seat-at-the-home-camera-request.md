---
id: M3-CRB-011
title: "Request (creatures-b): seat or frame a lone Act I boss so the default battle camera shows all of it"
role: combat
status: review
owner_session: "creatures-b (the Lead assigned it back, 2026-10-28 10:55)"
reviewer: art
depends_on: []
milestone: M3
request-from: creatures-b
---
## Goal
ADR 0041 (pillar 4, tactical clarity). creatures-b rendered each Act I boss encounter on the big14 gate tree
(lead/gate-big14 @ 8707ff90) at the **default battle camera**, no intro, with the chapter's real party (a scratch
fixture modelled on game/battle/scene/shots/boss_intro_shot.gd that skips the intro; never committed). A lone boss
sits on EnemySlots/Slot0 (-2.4, 0, 0.9), close to the camera (BattleCamera at (0.6, 2.8, 8.4)) and near the frame's
left edge:
- **hullgnaw, drownbell, bottle_hermit:** read well (whole silhouette, good scale against the party).
- **cinder_matron (3.6 m):** her hood is clipped by the phase label at top-left.
- **spar_wraith (3.4 m, spars spread wide):** most of the A-frame is out of frame or behind the phase label and
  command menu; the body reads only as a fragment. **The worst read after the Reach.**
- **undertows_reach (a 16 m limb):** the hand fills the left two-thirds of the frame and crowds the camera; the
  party stands under its fingers (also in M3-CRB-009, ask 3).

## Ask
For an encounter whose boss has a choreo.json `boss_intro` row (or a new per-encounter flag), seat the boss on a
boss mark further back and nearer the centre (e.g. about (-1.6, 0, -2.4) for the 3–4 m bosses; further for the
Reach), or apply the intro's `fit` logic (M3-BPR-404: fit the model's bounds in the safe frame, card clear) to the
**home** camera for that encounter. The models cannot do this themselves: moving a model inside its own scene would
pull it off its target ring and the stand-in's VFX anchor heights, and creatures.json `stand_in` has no offset key.
creatures-b re-renders the six encounters at the home camera when it lands.

## Done (creatures-b @ 052d69a2, the Lead's assignment)
- `game/data/ui/battle_sandbox.json` `boss_seats` (enemy id -> a mark in EnemySlots space) and
  `BattleStage._seat_lone_boss`: when the boss is the only foe at spawn it stands on its mark before the line-up;
  a foe joining later uses the slots as before. Test: tests/unit/test_battle_boss_seat.gd (seated and unseated).
- Seats, each chosen by self-rendering the default camera and the boss intro in the real arena and viewing them:
  - **undertows_reach [-2.6, 0, -2.4]:** the hand grips the wall-head beside the party, the fingers read, the forearm
    rises out of frame (the limb is colossal by design); the intro shows it on the real wall-head.
  - **cinder_matron [-2.6, 0, -1.2]:** her whole figure, hood clear of the phase label; the intro is unoccluded.
  - **spar_wraith [-2.0, 0, -1.4]:** the body and shroud are in frame; the mast tops still leave the top of the frame.
    Every seat further back that showed more of it broke test_battle_boss_camera (its big-move shots fail their frame
    checks), so this is the furthest that keeps M3-BPR-420's shots.
- **Left for battle-presentation:** a tall lone boss (the Spar-wraith, ~5 m with its spars) needs the home camera to
  fit its bounds (the intro's M3-BPR-404 fit applied to the default framing for that encounter); a seat alone can't
  do it without breaking the big-move shots. hullgnaw, drownbell and bottle_hermit need no seat.

## Follow-up (creatures-b @ a654ccc5, d4d52043; GPU QA row 36, 2026-10-29)
- **undertows_reach [-2.6, 0, -2.4] -> [-5.0, 0, -2.4]:** at the old seat the hand's digits reached x 1.2-1.7, between
  Asha and Toma, so the arm lay over the party lane. Moved out along its own axis it still grips the wall-head and its
  fingers read (self-rendered with M3-BPR-425's rest_by_enemy frame), with a clear gap before the party. Pinned by
  test_battle_boss_seat `test_the_reach_keeps_its_arm_out_of_the_party_lane`: every clip's bones below 4 m stay 1.5 m
  short of the nearest party mark (it fails at the old seat on attack, cast, attack_dark and cast_dark).
  The intro frame is unchanged (its camera fits the boss bounds).
- **spar_wraith:** creatures.json `stand_in.yaw_deg` 45 (was the default 90). At 90 the battle camera saw the A-frame
  edge-on, one mast with the body hidden behind it; at 45 the frame, the hanging body and the glowing seam read.

## Review log
