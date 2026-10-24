---
id: M1-CHR-12
title: "Asha round 7: crown and hairline geometry, lid band residue, lip bow, smile eyes, ADR 0024/0025 checks"
role: character
status: todo
owner_session: ""
depends_on: [M1-CHR-11]
milestone: M1
request-from: "lead"
reviewer: rendering
---
## Goal
These are the faults that rounds 5 and 6 (M1-CHR-10 and M1-CHR-11) carried without closing, as filed by review-sweep-O. M1-CHR-10's open criteria 1, 2 and 6 move here.

## Acceptance criteria
- [ ] **The crown and hairline** (M1-CHR-10 criterion 1, open since M1-CHR-04): the crown no longer reads as a sleek shell at dialogue range. The hairline is not one hard, even arc over a very tall forehead; it has some wisps or a fringe break. This is card geometry, not shading.
- [ ] **The lid band** (M1-CHR-10 criterion 2, M1-CHR-11 "reduced, not gone"): the tan or orange strip between the lashes and the crease is no warmer than the cheek. M1-CHR-11 measured R:B 3.3 on the lid against the cheek's 2.2. Target: within 0.3 of the cheek.
- [ ] **The upper-lip bow peaks** are not lumpy at 5× (M1-CHR-11 criterion 4 residue).
- [ ] **The smile's eyes at 1×.** In `asha_face_smile` the lower-lid raise and crow's feet are hard to see at full frame, and the smile still reads lopsided, closer to a smirk than the Duchenne smile ADR 0025 asks for. Judge it at 1×, not only in crops, and record the call in asha_review.md.
- [ ] **ADR 0024 check 1** (review-sweep-M, still owed): render `asha_face_neutral` under a neutral white key on lavapipe, and measure the crown's R:B and the temple lock's hue. Try the near-neutral cool tint `Color(0.88, 0.90, 0.95)` against the current `Color(0.76, 0.85, 1.0)`. Record the numbers in ADR 0024's table, and state which way `root_occlusion` and `depth_occlusion` run.
- [ ] **ADR 0025:** Art adopts the smile weights into asha.md §6.3, or overturns them (the ADR's own status line).
- [ ] **Skin evenness** (M1-CHR-10 criterion 6): judge it on the M1-QA-08 GPU capture, not on lavapipe.
- [ ] **Budget:** `asha.glb` is 4.60 MB against the 5 MB limit (ADR 0005). Report the headroom after this round. If it drops under 0.2 MB, propose what to cut.
- [ ] Blender gate byte-identical (`verify_blender_builds.py --job asha`); the asha_* baselines are re-approved after viewing each one; strict §14 is recorded in asha_review.md §12.

## Notes
- Merge M1-RND-21 (the mouth-interior fill, PC branch `gpu/rnd-21-mouth-fill`) first, if it has landed. M1-CHR-11's "exact next step" lists the order.

## Review log
