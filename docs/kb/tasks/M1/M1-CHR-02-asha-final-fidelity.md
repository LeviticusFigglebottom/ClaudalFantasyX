---
id: M1-CHR-02
title: Asha at final fidelity: modeled, rigged, shaded
role: character
status: review
owner_session: character-stream-3
reviewer: rendering
depends_on: [M1-CHR-01, M1-RND-04]
milestone: M1
request-from: ""
---
## Goal
SPEC §10.2 M1 exit criterion: one hero at final fidelity.

## Acceptance criteria
- [x] 40–70k triangles with LODs (LOD0 56,516; LOD1 26,885); 2K face textures (4K blocked by ADR 0005); hair cards
- [x] Rigify body rig plus face blendshapes (the 30 asha.md §6.2 names + 10 visemes; the emotion table is in `asha_face_poses.json`)
- [x] Godot turntable scene plus portrait shots (10 `asha_*` shots at 960×540, baselined)
- [x] Honest assessment against the §14 uncanny risk: `docs/kb/art/characters/asha_review.md`; decision ADR 0016 (Q2 escalated)

## Notes
From review-sweep-B on M1-CHR-01 (do these FIRST, before blendshapes): rebuild the head with ring loops around the eyes and mouth and a nasolabial loop; fix split normals at UV seams (neck, shoulder yoke); soften the jaw-underside shelf; reshape the heavy variant; add extreme-pose baselines as a weight regression gate.
Blocked by Git LFS for 4K textures (ADR 0005).

2026-10-23 character-stream-3: all the review-sweep-B fixes are done (head loop flow in `bb_head.py`, welded custom normals, the jaw cut and the 2 cm head/neck fillet, the heavy reshape, `asha_extreme_pose`). Asha is built end to end by `assets_src/characters/asha/build.sh`; details and numbers are in `asha_review.md`.

**Verdict:** passes at battle and field range; **fails at dialogue range** (still uncanny). This is the second failed face review, so ADR 0010's trigger is met: **Q2 goes to the human** (ADR 0016). The close-range painterly look (`skin_head_dialogue.tres`) is the interim mitigation.

**Not done (follow-ups in asha_review.md §5):** skirt, sash and braid chain bones; body correctives; hairline card row; skin colour zones and fine creases.

## Review log
