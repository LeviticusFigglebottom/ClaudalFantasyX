---
id: M2-CHR-520
title: "Asha sets the staff down (and picks it up) in the clips that kneel, sit or bow, so it never crosses her skirt"
role: character
status: review
owner_session: "characters (branch claude/characters)"
depends_on: [M2-CHR-515]
milestone: M2
request-from: qa
reviewer: rendering
---
## Goal
M2-CHR-515 grips the staff in every clip and pivots it in the fist clear of the skirt and legs (`hero_clips.prop_pivot`),
which clears walking, running, battle and every stand. Its rig-probe guard (`prop through_garment`) proves it still
crosses Asha's floor-length skirt where she kneels, sits or bows with the staff hand low: no pivot clears cloth pooled
round her. Those clips are listed, with this task, as `heroes.asha.prop_grip.allow_clips` in `tools/dev/rig_checks.json`:
attack (one line through her sleeve at the wind-up), bow_palms_flat, feed_fire, float_boat, kneel_hum, kneel_over_rhen,
kneel_touch_ring, laugh, offer_hand, pole_in, pole_out, rise_to_stand, sit, sit_beside.

The fix: a set-down weight per clip and time (as HOOK_HOLD draws the hooks): the hand lowers the staff to lie on the
floor beside her right knee as she goes down, releases it (the fingers open), and takes it again as she rises; the prop
bone keys the laid frame while it is down. The poling pair keeps it in hand but re-authors the arm so the shaft passes
outside the skirt.

## Acceptance criteria
- [x] `allow_clips` no longer lists a kneel, sit or bow clip; `test_rig_integrity` passes. Left: pole_in and pole_out
      (poling with the staff in both hands, which is not a set-down; the arms need re-authoring) and attack's one sleeve
      line.
- [ ] The set-down and pick-up read as deliberate on the PC render (the affected asha_clip_* and story shots).
- [ ] The runtime stage drive (`HeroHelperBones._drive_prop`) leaves a laid staff where the clip put it.

## Notes
- Filed 2026-10-27 by the characters track with M2-CHR-515's guard.
- **2026-10-27, done (characters).** Two other approaches failed first. The probe showed neither a 45 degree pivot of
  the hand nor one of the staff clears cloth pooled round a kneel.
  - **Schedule:** `hero_clips.prop_down(hero, clip, u)` gives the set-down weight, 0 to 1. It comes from `PROP_DOWN`
    for the hand-coded clips (kneel_over_rhen, laugh, offer_hand, rise_to_stand, feed_fire, float_boat). A story clip
    whose posture change goes down to a kneel or seat derives its own, over the first 60% of that change, and one coming
    up from a kneel or seat takes the staff up over the last 60%. A story spec can give `staff_down` itself.
  - **Laying it down:** `prop_pose` tips the staff about its foot as it lowers. The foot slides along the floor to the
    laid place (`prop_laid`): 0.75 m to her right and 0.5 m behind the hips, pointing forward, in the pelvis's frame.
    The fingers open over the first 30%.
  - **Probe:** `hook_hold` carries the weight as `_down`, and the probe's Pose gets it. The grip check skips a
    set-down pose; the garment check covers the laid staff.
  - Every kneel, sit, crouch and bow clip is clear. The render will show whether the lowering reads as deliberate,
    since the hand is not authored to follow it down.

## Review log
