---
id: M2-CHR-515
title: "M1-QA-09 hardware findings on the heroes: props gripped, staff clear of skirt and floor, underskirt in deep kneels, Toma's beard edge"
role: character
status: review
owner_session: "characters (new account, branch claude/characters)"
reviewer: rendering
depends_on: [M1-CHR-15, M2-CHR-513]
milestone: M2
request-from: rendering (pc-gpu, M1-QA-09 on hardware)
priority: top
---
## Goal
The PC's M1-QA-09 hardware read (gpu/m1-qa-09-heroes, docs/kb/qa/gpu/2026-10-27-m1-qa-09-heroes/README.md, at the
integration head f580e756) found these on the heroes. The ⚠ ones a player sees in normal play.

## Acceptance criteria
- [x] ⚠ 1, 2, 7: Asha's staff and Toma's spear are gripped: the fingers close round the shaft in every clip (the
      clips key no finger today, so the hand stays open), and the prop reads as held in run, walk_cycle and turn.
      Rhen's fists close on his hooks while they are drawn (M2-CHR-513).
- [x] ⚠ 2: in offer_hand the staff no longer stands behind her back through the braid.
- [x] ⚠ 3: in kneel_over_rhen and laugh the staff stays out of the skirt and the floor.
- [ ] ⚠ 4: the white underskirt no longer reads as a rigid tube under the front knee in offer_hand, and the trailing
      shin stays under it.
- [ ] 5: extreme_pose's raised-knee skirt pocket (a stress stage; the two-bone panels' limit, see M1-CHR-15's notes).
- [ ] 8: Toma's beard edge at close-up (the alpha cards along the jaw).
- [ ] 6 (low): the gauze sleeve at large arm angles.

## Notes
- Item 9 (Rhen's hooks) is M2-CHR-513, done at 038d5651.
- **2026-10-27, the grip (characters).** Why the hands were open: no clip keyed a finger, and a shaft built upright
  through a hanging hand runs along the hand, so no finger can close round it.
  - **Built through the fist:** Asha's staff and Toma's spear are built upright, then turned about the fist's hole
    (palmar of the knuckles) into the line from the thumb to the little finger (`asha_staff.held_frame`, `to_held`).
    Each rides its own bone under the right hand: the new `DEF-staff`, and `DEF-spear`, now along that line.
  - **Hold:** `staff_hold` is exact now. It turns the hand so the prop stands at the pose's authored tilt (the hold
    read from the GLB: the turn that stands the prop upright). The forearm's own roll takes up to 100 degrees of that
    turn. If the wrist would still bend past 45 degrees, the forearm turns to take the rest (up to 60, continuous in
    the pose, so no pops); past that, the prop goes where the fist points. Strikes skip the forearm turn, so their arm
    paths stay as authored. `_exact_hold` is a no-op.
  - **Stand:** the staff arm comes forward (upper arm -14, forearm -60), so the wrist is straight with the thumb up.
    The battle keys add back the old stand's arm, so the strikes keep their authored totals.
  - **Slide:** the prop slides through the fist along its bone (a keyed position) so that, standing near upright, its
    foot rests on the floor. It never goes under it. This also fixes ⚠3: in the kneels the staff leans and rests on
    the floor instead of passing through the skirt into it.
  - **Fingers:** solved per finger around the shaft (`grips_init`: each chain curls about its bones' x until its
    joints lie just outside the shaft; the thumb opposes). Keyed in every clip; Rhen's are weighted by his hook hold.
  - **Re-authored:** Toma's `spear_level` and `lower_spear` (a straight arm forward and down levels the spear with a
    straight wrist), his attack's hit (an underhand thrust from the hip), the attack and finisher follow-throughs
    (the spear comes back up with the arm), and the ko's lying staff arm for both (`LYING_STAFF_ARM`, searched
    numerically: the staff lies on the floor).
  - **Stages:** `game/data/characters/grips.json` (written by hero_clips) and `HeroHelperBones.drive` apply the hold
    in the hand's posed frame, the fingers and the slide to hand-set poses. AshaStage drives it for a held-prop
    skeleton at rest too.
  - **Still open:** ⚠4 is the old skirt (the QA head predates M1-CHR-15's gathers): re-check it on the new render.
    5 (extreme_pose) is the stress stage. 8 (Toma's beard edge) needs groom iteration with a close-up render
    (toma_face_neutral is requested). 6 is low.

## Review log
