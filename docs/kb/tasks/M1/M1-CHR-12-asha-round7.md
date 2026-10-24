---
id: M1-CHR-12
title: "Asha round 7: crown and hairline geometry, lid band residue, lip bow, smile eyes, ADR 0024/0025 checks"
role: character
status: review
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
depends_on: [M1-CHR-11]
milestone: M1
request-from: "lead"
reviewer: rendering
---
## Goal
These are the faults that rounds 5 and 6 (M1-CHR-10 and M1-CHR-11) carried without closing, as filed by review-sweep-O. M1-CHR-10's open criteria 1, 2 and 6 move here.

## Acceptance criteria
- [~] **The crown and hairline** (M1-CHR-10 criterion 1, open since M1-CHR-04): the crown no longer reads as a sleek shell at dialogue range. The hairline is not one hard, even arc over a very tall forehead; it has some wisps or a fringe break. This is card geometry, not shading.
- [~] **The lid band** (M1-CHR-10 criterion 2, M1-CHR-11 "reduced, not gone"): the tan or orange strip between the lashes and the crease is no warmer than the cheek. M1-CHR-11 measured R:B 3.3 on the lid against the cheek's 2.2. Target: within 0.3 of the cheek.
- [x] **The upper-lip bow peaks** are not lumpy at 5× (M1-CHR-11 criterion 4 residue).
- [x] **The smile's eyes at 1×.** In `asha_face_smile` the lower-lid raise and crow's feet are hard to see at full frame, and the smile still reads lopsided, closer to a smirk than the Duchenne smile ADR 0025 asks for. Judge it at 1×, not only in crops, and record the call in asha_review.md.
- [x] **ADR 0024 check 1** (review-sweep-M, still owed): render `asha_face_neutral` under a neutral white key on lavapipe, and measure the crown's R:B and the temple lock's hue. Try the near-neutral cool tint `Color(0.88, 0.90, 0.95)` against the current `Color(0.76, 0.85, 1.0)`. Record the numbers in ADR 0024's table, and state which way `root_occlusion` and `depth_occlusion` run.
- [ ] **ADR 0025:** Art adopts the smile weights into asha.md §6.3, or overturns them (the ADR's own status line).
- [x] **Skin evenness** (M1-CHR-10 criterion 6): judge it on the M1-QA-08 GPU capture, not on lavapipe.
- [x] **Budget:** `asha.glb` is 4.60 MB against the 5 MB limit (ADR 0005). Report the headroom after this round. If it drops under 0.2 MB, propose what to cut.
- [x] Blender gate byte-identical (`verify_blender_builds.py --job asha`); the asha_* baselines are re-approved after viewing each one; strict §14 is recorded in asha_review.md §12.

## Notes
- Merge M1-RND-21 (the mouth-interior fill, PC branch `gpu/rnd-21-mouth-fill`) first, if it has landed. M1-CHR-11's "exact next step" lists the order.

## Delivery (2026-10-24, characters track; details in asha_review.md §12)
- **Crown and hairline [partial]:** hairline 6 mm lower, uneven, with wisps crossing it; looser crown clumps and
  flyaways. The forehead is no longer "very tall"; at 1× the crown still reads smooth (GPU to judge).
- **Lid band [partial]:** lit eye R:B 2.61 against the cheek's 2.32 (**within 0.3**); the far eye 3.23 against 2.00
  (fails: it's in the brow's cast shadow, and pushing the albedo further paints a pale band). Root cause found by
  diagnostic renders: the band's albedo already matches the cheek, so the warmth comes from the shadow under this key.
- **Lip bow:** passed on QA-08 (no change).
- **Smile's eyes:** stronger AU6 (crow's feet, lower-lid push, roll). The call at 1× is recorded: the eyes now take part,
  but the mouth still reads as a lopsided smirk. That is the asha.md §6.3 weights, which are Art's (ADR 0025); a proposal
  is in asha_review.md §12.4.
- **Grief fault B (peg teeth):** fixed on lavapipe. **Fault A** is left for after M1-RND-24, per the Lead note.
- **ADR 0024 check 1:** measured and appended to ADR 0024 (keep the cool tint for warm keys; the occlusion uniforms run
  "1 = none").
- **ADR 0025:** not adopted; Art's call.
- **Budget:** `asha.glb` 4.61 MB, 0.39 MB headroom; LOD0 63,368 (target 63,500).
- **Gates:** `verify_blender_builds.py --job asha --job rhen` 44 and 31 identical (rebuilt with every change);
  `tools/tests` test_asha, test_asha_face_drive, test_rhen, test_hero_clips, test_post_import green; Godot
  post_import, hero_stage, character_shading green. Re-approved after viewing: asha_face_neutral, _smile, _grief,
  _stylized_compare. Drift within limits, not re-approved: asha_front 0.0025, asha_q34 0.0029, asha_profile 0.0018,
  asha_extreme_pose 0.0025, asha_sleeve_s0/s4 0.0007.
- **Next:** M1-RND-24, then fault A, then the PC's GPU re-check (M1-QA-09).

## Review log

## Lead note (2026-10-24)
- Grief fault A, the black lip-edge rim, may be a shader bug rather than Asha's bake. Review sweep P found that the mouth family's cavity bounce is shadowed for positional lights, because Godot 4's ATTENUATION includes the shadow. That's **M1-RND-24**, which the Lead's Rendering agent is fixing. Do fault B (the peg teeth), the lid band, the smile eyes and the crown first, and revisit A after RND-24 merges.
- The next GPU re-check after this round is **M1-QA-09** (with tighter rigour).
