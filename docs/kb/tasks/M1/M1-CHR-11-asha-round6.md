---
id: M1-CHR-11
title: Asha round 6: grief teeth, lash comb, lid band, brow notch, dead eyes in the smile, upper-lip edge
role: character
status: review
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
