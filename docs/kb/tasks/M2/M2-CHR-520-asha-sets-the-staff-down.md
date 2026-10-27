---
id: M2-CHR-520
title: "Asha sets the staff down (and picks it up) in the clips that kneel, sit or bow, so it never crosses her skirt"
role: character
status: todo
owner_session: ""
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
- [ ] `allow_clips` is empty for Asha (attack's sleeve line fixed too); `test_rig_integrity` passes.
- [ ] The set-down and pick-up read as deliberate on the PC render (the affected asha_clip_* and story shots).
- [ ] The runtime stage drive (`HeroHelperBones._drive_prop`) leaves a laid staff where the clip put it.

## Notes
- Filed 2026-10-27 by the characters track with M2-CHR-515's guard.

## Review log
