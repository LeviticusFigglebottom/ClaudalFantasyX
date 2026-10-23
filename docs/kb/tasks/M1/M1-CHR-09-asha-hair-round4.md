---
id: M1-CHR-09
title: "Asha round 4: crown hair card layout, face-framing lock, lips, doll-like read"
role: character
status: done
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
- 2026-10-23 rendering (review-sweep-L, fresh reviewer): **approve the round (its four named faults are fixed); strict SPEC §14 verdict: FAIL as built.** No blockers for merging the round itself.
  - **Checks:** `verify_blender_builds.py --job asha`: **`44 identical`**, rc 0 (329 s, with the Lead's `--threads 4` build.sh in tree; the gate pins 4 threads too). Tool tests 411 OK, including test_asha_face_drive 5/5 and the part budgets (LOD0 62,290 ≤ 63,500; asha.glb 4.46 MB < 5 MB).
  - **What I viewed:** the four re-approved `asha_face_*` baselines and `asha_front`. I made old/new/diff sheets against CHR-07 (6551cae^) and a 2× crop of neutral, smile and grief side by side. The four faults are fixed: crown clumps with their own highlights, the lock as a fan, the bow without scallops, and a shaded sclera.
  - **Strict §14 verdict (a hero "at final quality" at dialogue range): not met.** What I still see at 960×540 and in the 2× crop:
    1. **Hair:** the crown still reads as a sleek shell with a hard, even hairline arc across a tall forehead. It reads warm auburn-brown, not black (asha.md:121), because the primary lobe dominates the #201A16 albedo.
    2. **Lashes and brows:** the upper lashes read as a sparse comb of thin dark ticks, with a pale lid band above them. The brows have a hard flat lower edge, and the left brow head is heavy.
    3. **Mouth:** in `grief` the teeth are a blue-grey slab with dark outlines, and the inner lower lip has a hard edge, which is the most uncanny frame of the set. In neutral and smile the lower lip reads as a separate pad. The smile has diagonal striations at the shadow-side corner.
    4. **Skin:** it is evenly lit and smooth between the features (the doll read the author also names).
    5. **`asha_front`:** a stair-stepped hem on the white underskirt, and a gauze sleeve that shows its grid. Both are out of scope (cloth), but they count against "final quality".
  - **Is it renderer-limited? Mostly not.** The evidence:
    - QA-05 (docs/kb/qa/gpu/2026-10-23-qa-05-asha.md) rendered every asha_* shot on an RX 9070 XT. At scene settings it matches lavapipe within RMSE 0.0011–0.0057. High and Ultra at 2× removed none of the defects then classified, which were all asset or look-dev issues, or shadow settings.
    - Lavapipe is a conformant Vulkan rasteriser, not a lower-quality one, so the **only real limit is the 960×540 capture.** The face spans about 330 px wide, which minifies the 2048² head maps about 3:1. Pores, single hair strands (far below a pixel) and lash thickness are resolution-limited, so "smooth skin" is partly a capture artefact.
    - **Not resolution-limited:** items 1, 2 (pale lid, comb lashes, brow edge), 3 and the evenness of skin lighting in 4. Each spans many pixels and would look the same at 2×, as QA-05's 2× captures did for the faults of their day.
    - Hair colour and the lid band depend on the lobe and SSS settings, which are the same on a GPU at scene settings. **Only a 2× High GPU capture can settle the lock's backlit half and the morph-normal shading.** Queue it on the PC (asha_face_* at 2× High).
  - **Should-fix (next round, not this merge):**
    - **S1:** the grief mouth interior: teeth albedo or roughness, and the inner-lip edge.
    - **S2:** the hair lobe against asha.md §5 (exponent 400 against 120). Settle it with Art and write an ADR or amend asha.md. Don't leave the spec and the asset disagreeing.
    - **S3:** the S2 smile-corner striation from M1-CHR-07.
    - **S4:** record this §14 FAIL-as-built in STATUS.md's risks for the Lead's M1 fidelity question, with the ADR 0019 stylised path as the mitigation SPEC §14 names.
- 2026-10-23 lead: closing the round on review-sweep-L approve; the SPEC §14 work continues in M1-CHR-10.
