---
id: M1-CHR-14
title: "TOP PRIORITY: Asha's braid is detached from her head; clothing and staff clip through her; limbs look detached in some frames"
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
depends_on: []
milestone: M1
request-from: "lead"
priority: top
---
## Goal
The human reported (2026-10-24) that Asha's braid has been visibly disconnected from her head "this whole time". Several frames also show her clothes and staff clipping through her body, and in some frames her limbs look detached. These read as broken at any distance. They outrank every polish item, including the rest of M1-CHR-12's smile and lid work and Rhen and Toma's follow-ups.

## Acceptance criteria
- [ ] **Braid attachment:** the braid's root sits in the scalp or hair cap with no visible gap, in every Asha shot (asha_front, q34, profile, back if present, extreme_pose, the face shots, the stylized compare) and every clip (asha_clip_*), and it follows the head through the clips. It must be weighted to the head bone, not a separate rigid object. Check the root against the hair cap and skull, and the vertex weights at the braid root.
- [ ] **Clipping:** no clothing (vest, sleeves, sash, skirt or trousers) and no staff passes through the body in the rest pose, the extreme pose, or any frame of Asha's 11 clips. Fix it with proper skinning or weight transfer from the body, cloth offsets, or the staff's grip and attachment, not by hiding geometry.
- [ ] **Limb continuity:** no gap or seam opens at the shoulders, elbows, wrists, hips, knees or ankles in any pose or clip frame. Check the weight normalisation and seam welding between the body and the costume pieces.
- [ ] **Automated guards** in tools/tests, so this can't silently return:
  1. A connectivity test: the braid's root vertices are within a small epsilon of the hair cap or scalp surface, in the rest pose and in sampled clip frames.
  2. A penetration test: sample body vertices against the clothing and staff meshes (or the reverse) at the rest pose, the extreme pose and N frames per clip, and fail on any penetration deeper than a threshold, kept in data.
  3. A seam test: no open boundary edges at the limb joints after the skin is applied.
  The Blender build can export the data for these (for example a JSON of sampled vertex positions per pose), so the tests stay headless.
- [ ] Apply the same three checks to **Rhen and Toma** and fix what they find; they share Asha's costume modules.
- [ ] Rebuild with byte-reproducible outputs (`verify_blender_builds.py` identical). View every changed shot side by side, then re-approve, and list the RMSE.
- [ ] Per-task handoff, and a note in characters.md.

## Notes
- The fix likely touches the shared `asha_costume` modules (see M1-CHR-13's `_outward()` sign flip and the `_panel` winding bug). Coordinate, or fold it into the same rebuild.
- The PC GPU session re-checks it on hardware afterwards, as part of M1-QA-09.
- **Automated guards (2026-10-24, guards sub-agent).** `tools/dev/rig_probe.py` is a numpy-only probe. It skins each hero's committed GLB with linear blend skinning, using the rest pose, the stage's extreme pose and every third key of every `hero_clips.py` clip, capped at about 10 samples per clip. It then measures braid root gap and drift, garment, prop and skin penetration (confirmed by winding number), welded-seam opening, uncovered hidden-face boundaries, and weight normalisation. Thresholds are in `tools/dev/rig_checks.json`. `tools/tests/test_rig_integrity.py` runs the checks for Asha, Rhen and Toma (about 2 min); these tests are deliberately left failing on today's GLBs. Run `python3 tools/dev/rig_probe.py --hero asha --report` for the per-pose table, and see pipeline.md §15. Today's worst values (mm), on the 5a7ce13 GLBs, are below. Asha: braid gap 32.2 in every pose. The strand roots float about 3 cm behind and below the hair cap, though they are rigidly head-skinned (drift 0). Costume inside skin 44.4 (walk: the hip-only skirt through the shin). Sleeve inside skin 38.6 (laugh: arm into torso). Staff 6.7 (wrist). Skin through cloth 264 (kneel: the foot out through the floor-length, hip-only skirt). 51 of 263 boundary vertices exposed (kneel: the thigh hole leaves the skirt). Rhen: costume inside skin 30.6, skin through cloth 61.4 (take_hand: upper-arm skin through the torso cloth, which is weighted to spine.003), 23 boundary vertices exposed. Toma: costume inside skin 31.7 (the arm through the tunic in idle and talk), spear wrap 27.4, skin through cloth 51.1, 7 boundary vertices exposed. Welded seams and weights are clean for all three. `skin_through_garment` is rest-relative: it tracks the cloth point over each skin vertex at rest, so it reads 0 at rest by construction. Point the probe at another checkout's GLBs with `HYMN_RIG_ROOT=<checkout>`, `--root` or `--glb`.

## Review log
