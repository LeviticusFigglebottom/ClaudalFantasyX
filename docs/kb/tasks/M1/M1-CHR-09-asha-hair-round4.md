---
id: M1-CHR-09
title: "Asha round 4: crown hair card layout, face-framing lock, lips, doll-like read"
role: character
status: review
reviewer: rendering
owner_session: "worktree-agent-aaf1e4bd7d4a529a9 (session_01Bg3iP7cPGyjbX4CyniBahc)"
depends_on: [M1-CHR-07]
milestone: M1
request-from: "lead"
---
## Goal
Close the faults that still fail SPEC §14 at dialogue range in asha_review.md §8.3, plus an honest look at the doll-like read of the face. First find triangle headroom without visible loss (LOD0 is at exactly 63,500).

Out of scope (the PC GPU session owns them): shadow settings, and the cloth, vest and bodice materials, including `write_materials.py`'s cloth entries.

## Acceptance criteria
- [x] Triangle headroom found without visible loss: hidden or interior geometry decimated, or the costume or body rebalanced. LOD0 stays at or under 63,500
- [x] The crown no longer reads as a smooth shell: a card-layout pass with layered cards, breakup, strand clumps and flyaways
- [x] The face-framing lock reads as loose hair, not a dark streak
- [x] The lips are slightly fuller, and the bow's shoulders don't wobble
- [ ] The face no longer reads doll-like (eye white or iris scale, skin subsurface warmth), judged honestly from the asha_face_* shots. **Partial:** the sclera and the skin transitions are fixed; the pale upper lid (mostly shading) and the smooth, evenly lit skin remain (asha_review.md §9.3)
- [x] Material changes go only through `assets_src/characters/asha/write_materials.py`
- [x] `verify_blender_builds.py --job asha` reports all identical; every file under 5 MB
- [x] Only the asha_* baselines that intentionally change are re-approved, each looked at; the §14 review is re-run strictly in asha_review.md §9

## Notes

### Character, worktree `worktree-agent-aaf1e4bd7d4a529a9` (2026-10-23)

**Headroom.** `build_asha.delete_hidden_socket` deletes the head-skin faces that lie inside the opaque eyeball (0.95 R, at rest and under every shape key). It runs after the bake, so the textures don't change.
- It frees 1,230 triangles; the before/after face frames differ by at most 1/255.
- Inside the hair's own 16,000 line, the hidden base layer is now 230 wider cards (was 350).
- LOD0 is now **62,290**.

**Hair:**
- **Crown:** 62 strand clumps (2–4 cards gathering mid-length, arcing 0.8–3.7 mm off the scalp, rolled) replace the fixed-lift top layer.
- **Crown flyaways:** they stand 4–11 mm off.
- **Lock:** each of the two strands is a 6-ribbon fan rooted at the temple hairline outside the orbit (CHR-07 rooted it above the brow tail).
- **Random streams:** one per part.

**Lips:** the wobble came from the contact line rising toward the corners. The upper outline now falls monotonically from the bow's peaks, and the vermilion is 9.4 / 9.5 mm (was 8.8 / 9.0).

**Doll read:**
- The sclera darkens and warms toward the canthi; `col_sclera`, `limbus_softness` and the occlusion shell's upper and corner strengths changed.
- The upper lid is 15% darker in the albedo.
- `skin_head` `curvature_scale` is 1.3.
- `shadow_scatter` was tried and reverted (a shadow-penumbra term, out of scope).

**Verdict (asha_review.md §9.3):**
- The four named faults are fixed.
- It passes §14 with the ADR 0019 close-range look.
- As built it is still borderline: a slight doll quality remains in the surface and shading.

**For the reviewer (Rendering):**
- GPU look at the pale upper lid. It is mostly shading; the albedo is already darkened.
- Check the backlit lower half of the lock.
- Check the new `eye`, `eye_occlusion` and `skin_head` values.

**Not touched:** shadow settings, and the cloth, vest and bodice materials and their entries in `write_materials.py`.

## Review log
