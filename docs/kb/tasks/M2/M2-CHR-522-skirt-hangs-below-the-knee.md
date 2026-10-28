---
id: M2-CHR-522
title: "Asha's skirt hangs from the knee: a third panel bone, so walking and running no longer flare a rigid bell"
role: character
status: doing
owner_session: "characters (branch claude/characters; worktree skirt-wt)"
depends_on: [M1-CHR-15, M2-CHR-515]
milestone: M2
request-from: lead
reviewer: rendering
---
## Goal
The Lead's big12 review (gpu/gate-big12-shots): in asha_clip_run, asha_clip_walk_cycle, asha_clip_turn and
asha_extreme_pose the skirt flares as a stiff, wide bell, and the white underskirt as a flat disc. That is M1-QA-09's
rigid tube or bell in another form. Measured (`hero_clips.skirt_solve` over the clips): the front panel's lower bone
stands 40-70 degrees out through the whole walk and run, and is 0 in idle. Each panel is two rigid bones (pivot at the
hip line, a joint at about mid-thigh). A straight lower bone has to angle forward to pass the advancing knee, and being
rigid it carries on past the knee as a flat plate. Real cloth touches the knee and hangs from it. Tuning (a lower swing
foot, per-segment leg clearances) changes nothing, because the knee is the binding contact.

## Acceptance criteria
- [ ] Each panel gets a third bone from about the knee to the hem (`DEF-skirt_<k>.002`). The solve swings the third
      bone back toward the vertical (hanging) as far as the leg clearance allows, so the cloth below the knee drapes.
      The lag between neighbours and the floor gather and overhang carry over.
- [ ] `game/characters/hero_helper_bones.gd` (the stage port) solves the same, and the Python and GDScript stay
      equivalent (the existing stage tests).
- [ ] The front panel's lowest bone stays within about 25 degrees of vertical through walk and run, except at the
      knee's peak; the rig probe is clean at the current ratchets; verify --job asha is identical on the three numpy
      paths.
- [ ] A render (asha_clip_run, asha_clip_walk_cycle, asha_clip_turn, asha_extreme_pose, asha_clip_walk) shows a
      skirt that swings and drapes.

## Notes
- Filed 2026-10-28 by the characters track from the Lead's big12 review. The "staff gone" report in the same review
  does not reproduce: asha_front, asha_q34 and asha_sleeve_s0 in gpu/gate-big12-shots all show the staff.

## Review log
