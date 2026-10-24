---
id: M1-CHR-11
title: Asha round 6: grief teeth, lash comb, lid band, brow notch, dead eyes in the smile, upper-lip edge
role: character
status: done
owner_session: "worktree-agent-a51a24232ad76bb4f (character)"
reviewer: rendering
depends_on: [M1-CHR-10]
milestone: M1
request-from: "rendering"
---
## Goal
From review-sweep-N and the PC's QA-05c GPU verdict (docs/kb/qa/gpu/*qa-05c*).

## Acceptance criteria
- [x] Grief: the teeth read as teeth, not a faceted gold-brass strip.
  - Done: separate, rounder crowns; gaps shaded in the atlas patch; cooler, rougher enamel.
  - Also found: the khaki band under the teeth was the inner lower lip, now painted as mucosa.
  - The atlas patch carries the albedo and roughness. `write_materials.py` is unchanged here, to leave M1-RND-21's mouth-family move clean.
  - In shadow the interior is still near-black: that is M1-RND-21.
- [x] Lashes are not a comb (fine, irregular, fanned). The brow notch is gone. The orange lid band is **reduced, not gone** (rendered R:B 4.2 → 3.3; the cheek is 2.2).
- [x] Smile: the eyes take part (lower-lid raise, crow's feet, brow-tail drop; ADR 0025 weights). The inner brows lift in grief (+3.9 mm, was +0.4).
- [x] The upper-lip edge is softer and smoother. The bow peaks are still slightly lumpy at 5×.
- [x] Blender gate byte-identical (44 identical, 283 s, on 6c9a8b1); under 5 MB; strict §14 in asha_review.md §11. Then the PC re-captures grief and smile on the GPU.

## Notes
- **Exact next step:**
  1. Merge `origin/claude/new-session-mj8c3c` and `origin/gpu/rnd-21-mouth-fill` (M1-RND-21's mouth-family materials; keep its write_materials.py entries).
  2. Rebuild, re-run `verify_blender_builds.py --job asha` (44 identical), and re-approve `asha_face_grief` (and smile, if it moves) after viewing.
  3. The PC re-captures grief and smile at 2× High.
- Handoff: docs/kb/handoffs/2026-10-23-character-9.md.

## Review log
- 2026-10-24 review-sweep-O (rendering): **approve with fixes, accepted as a round. The strict §14 judgement stays with the GPU (M1-QA-08, new) and the human.** No merge blockers. The round was merged in de5ac8d.
  - **What I read:** the task, asha_review.md §11, ADR 0025 and `git show --stat 6c9a8b1 b40df91`. Those touch asha_face_shapes.py, asha_mouth.py, asha_textures.py, the face poses, test_asha.py and test_asha_face_drive.py, and re-approve four baselines.
  - **What I viewed:** `asha_face_grief` and `asha_face_smile` at full size.
    - **Grief is clearly better.** The inner brows lift and knit, and the teeth read as separate teeth, not a strip. The interior is still very dark (M1-RND-21).
    - **The smile still reads lopsided at 1×**, nearer a smirk than a Duchenne smile. The lower-lid raise and the crow's feet that ADR 0025 adds barely show at full frame, so the eyes still look little changed. M1-CHR-12 judges this at 1×.
  - **Budget:** `asha.glb` grew from 4.49 to 4.60 MB, leaving 0.4 MB under the 5 MB limit. M1-CHR-12 tracks the headroom.
  - **Open, and filed:**
    - M1-CHR-12 takes the lid band residue (R:B 3.3 against the cheek's 2.2), the lumpy bow peaks, the smile's eyes at 1× and ADR 0025's adoption by Art.
    - M1-QA-08 takes the GPU re-capture of grief and smile after M1-RND-21. It had no task.
    - The Notes' "exact next step" (merge RND-21, rebuild, re-approve) is the integration step for RND-21. It is not a CHR-11 defect.
  - **Not re-run:** the Blender gate. The author reports 44 identical on 6c9a8b1, and nothing in the asha sources changed after it.
