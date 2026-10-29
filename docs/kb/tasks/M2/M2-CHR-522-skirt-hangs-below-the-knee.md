---
id: M2-CHR-522
title: "Asha's skirt hangs from the knee: a third panel bone, so walking and running no longer flare a rigid bell"
role: character
status: review
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
- [x] Each panel gets a third bone from about the knee to the hem (`DEF-skirt_<k>.002`). The solve swings the third
      bone back toward the vertical (hanging) as far as the leg clearance allows, so the cloth below the knee drapes.
      The lag between neighbours and the floor gather and overhang carry over.
- [x] `game/characters/hero_helper_bones.gd` (the stage port) solves the same, and the Python and GDScript stay
      equivalent (the existing stage tests).
- [x] The front panel's lowest bone stays within about 25 degrees of vertical through walk and run, except at the
      knee's peak; the rig probe is clean at the current ratchets; verify --job asha is identical on the three numpy
      paths.
- [ ] A render (asha_clip_run, asha_clip_walk_cycle, asha_clip_turn, asha_extreme_pose, asha_clip_walk) shows a
      skirt that swings and drapes. (Software renders in the worktree look right; the rendering review on the GPU shots
      is still to do, and the baselines are not updated.)

## Notes
- Filed 2026-10-28 by the characters track from the Lead's big12 review. The "staff gone" report in the same review
  does not reproduce: asha_front, asha_q34 and asha_sleeve_s0 in gpu/gate-big12-shots all show the staff.

- 2026-10-28 (characters, worktree skirt-wt, branch chr-skirt-wip): done, ready for review.
  - **Build** (`helper_bones.py`): a third bone per panel, `DEF-skirt_<k>.002`, from SKIRT_SHIN_SPLIT (0.1) of the way
    from the knees' height to the hem, on to the hem; `.001` now runs from the first joint (mid-thigh) to there. The
    lower cloth's weights split smoothly between `.001` and `.002` over SKIRT_SHIN_BAND (8 cm at s = 1) about that
    joint. `skirt_weights` takes the hem height (`build_asha.py` passes `DEF-foot.L`'s head).
  - **Solve** (`hero_clips.skirt_solve`, `game/characters/hero_helper_bones.gd`): the chain is the data's new
    `skirt.levels` (`["", ".001", ".002"]`), solved from the hips down, each bone about its head where the bones above
    put it, with the lag limit at each level. The upper bone is as before. The middle bone clears its own cloth and all
    the cloth below it carried straight, which is exactly the old rigid lower bone's solve, so it clears the knee and
    leaves a straight line below it that clears. The lowest bone takes the least swing from the vertical, searched only
    up to the middle bone's swing (`_swing`'s new `top`), so it hangs back from the knee as far as the shin lets it
    and never flares past the line above. The floor gather and the overhang moved to the lowest bone.
  - **Why not solve the lowest bone on its own cloth alone, from 0 up to max_swing:** tried first. The front was
    fine, but the back panels' lowest bones went to 54-95 degrees in walk and run. The trailing calf meets the cloth
    right at the lowest bone's head, and turning a bone about its head cannot move that point (it pushes the inner
    layer into the calf). So no angle cleared, and `_swing` returned its "nearest" angle (up to max_swing). Solving the
    middle bone with the cloth below it fixes this: the straight continuation always clears.
  - **Measured** (`skirt_solve` over the clips, swing from the vertical in the pelvis's frame, degrees; the front
    panel's are the same within 2 degrees from the world vertical). Max over the cycle, before (upper / lower) ->
    after (upper / middle / lowest):

    | panel (0 front, to her left) | walk before | walk after | run before | run after |
    |---|---|---|---|---|
    | 0 front | 17 / 52 | 17 / 52 / **0** | 31 / 69 | 31 / 69 / **0** |
    | 1 | 39 / 17 | 39 / 17 / 14 | 50 / 32 | 50 / 32 / 14 |
    | 2 left | 6 / 23 | 6 / 23 / 15 | 11 / 26 | 11 / 26 / 20 |
    | 3 | 14 / 31 | 14 / 31 / 31 | 33 / 54 | 33 / 53 / 53 |
    | 4 back | 1 / 25 | 1 / 25 / 25 | 16 / 31 | 16 / 31 / 31 |
    | 5 | 15 / 32 | 15 / 32 / 32 | 40 / 52 | 40 / 52 / 52 |
    | 6 right | 7 / 22 | 7 / 22 / 13 | 12 / 22 | 12 / 21 / 13 |
    | 7 | 39 / 15 | 39 / 15 / 15 | 51 / 32 | 51 / 32 / 16 |

    The front panel's lowest bone is 0.0 to 0.5 degrees from the world vertical in every walk frame and 0.3 to 2.0 in
    every run frame (the old lower bone: 24-52 and 30-69). The front and side panels hang back below the knee. The back
    panels' lowest bones carry on in the middle bone's line, because the trailing calf and heel push the cloth out;
    those angles are the old lower bone's (31 at most in walk). The kneel (kneel_over_rhen's end): the front is
    92 / 32 / 0 with no gather, and the sides and back gather on the floor (0.2-0.9). The extreme pose's flat front is
    the upper bone lying over the raised thigh (81 degrees, unchanged); below the knee it now hangs (0, was 39).
  - Only Asha's library changed when the clips were rebaked (all heroes run). Asha's face is untouched (ADR 0019).
  - Gates: `python3 -m unittest tools.tests.test_asha tools.tests.test_hero_clips tools.tests.test_hero_battle_clips
    tools.tests.test_hero_locomotion tools.tests.test_rig_integrity`: 149 run, OK (26 skips: heroes with no braid or
    prop). The rig probe is clean at the current ratchets, with none raised. Godot import OK; `--filter=hero_stage` 10/10
    (including test_helper_bones_match_the_baked_clips, Python against GDScript); `--filter=post_import` 21/21. gdlint and
    gdformat clean. `validate_data` clean. `verify_blender_builds.py --job asha`: 44 identical natively, with
    `NPY_DISABLE_CPU_FEATURES="X86_V4"` and with `"X86_V3 X86_V4"`.
  - Left: the GPU review shots and new screenshot baselines for the asha_clip_* and asha_extreme_pose shots (the
    skirt changed in every Asha shot that moves her legs).

## Review log
