---
id: M1-CHR-10
title: Asha round 5: hair black and strand-broken, lashes, lid band, brows, teeth, mouth normals
role: character
status: review
reviewer: rendering
owner_session: "worktree-agent-a109a5ba219573018"
depends_on: [M1-CHR-09]
milestone: M1
request-from: "rendering"
---
## Goal
From the review-sweep-L entries (file:line references there).

## Acceptance criteria
- [ ] Hair reads black (asha.md:121), not auburn: check albedo, the hair shader primary tint and anisotropic highlight colour; the crown is no longer a smooth shell. **Partial:** black is done, but the crown is still a sleek shell. The cause was the base colour, not the shader, so no shader change was needed (ADR 0024, proposed). The card geometry is unchanged.
- [ ] Lashes: tapered clumps, not comb teeth; the pale upper-lid band is gone (albedo, AO, or lid geometry). **Partial:** the lashes are tapered clumps; the band is reduced, not gone: a tan strip still shows between the lashes and the crease (asha_review.md §10.4).
- [x] Brows: soft edges, hair-stroke density falloff
- [x] Grief: no blue-grey tooth slab (teeth albedo and occlusion; mouth-interior AO). The hard inner lower-lip edge remains.
- [ ] Morph normals on the mouth surface as well as skin_head (88 vertices); no diagonal striations at the smiling mouth corner. **Split:** the mouth normals are done (16 shapes). The striations are a key-light shadow terminator, not normals, and they remain. Handed to M1-RND-20 (§10.3).
- [ ] Evenly lit skin: work with the shading (cavity, roughness breakup, the painterly close-range look per ADR 0019). **Partial:** the material levers are used (roughness range, cavity, micro-roughness, a head mottle). At 1× the skin still reads smooth and evenly lit.
- [ ] Blender gate byte-identical; under 5 MB; §14 review strict in asha_review.md §10; then a 2x High GPU capture by the PC session (M1-QA-05c) as final judge. **Done except the GPU capture:** the gate passes (see Notes), every file is under 5 MB, and the review is written. The GPU capture is still to come.

## Notes
- **Verdict** (asha_review.md §10.4):
  - Five of the six named faults are fixed or clearly reduced at the asset.
  - **Strict SPEC §14 at dialogue range: FAIL as built**; borderline with the ADR 0019 look.
  - What still fails, in order:
    1. skin evenness;
    2. the crown shell;
    3. the smile-corner striations (M1-RND-20);
    4. the grief inner-lip edge;
    5. the lid strip;
    6. brows a touch thin;
    7. the hair's slight warm cast.
- **Diagnostics** (lavapipe, one override per render):
  - With every hair lobe off, the crown still rendered auburn, so the fault was the base colour.
  - The grief slab was the teeth's sky specular: the teeth turned pure red with specular 0 went dark.
  - The corner striations vanish with the key shadow off and sharpen with finer shadow texels.
- **Gates** (scoped, CLAUDE.md "Gate scope"):
  - `verify_blender_builds.py --job asha`: **44 identical**, rc 0, 288 s (Blender 5.0.1, --threads 4) on commit e863a98; the later write_materials.py edit is comment-only (re-running it leaves every .tres byte-identical)
  - asha_* shots: the 4 face shots re-approved after viewing; the 6 field shots pass within their limits, baselines kept; re-compare 10/10 PASS.
  - tools unittest 415 OK; validate_data 0 errors; taskboard pass; manifest 60 valid.
  - **Skipped:** gdlint/gdformat and the Godot character filter (no `.gd` or shader touched; materials are `.tres` generated from Python), coverage (no battle or progression code), and the other Blender jobs and screenshots.
- **Numbers:** LOD0 62,290; LOD1 29,378; `asha.glb` 4,487,948 B; largest file the head skinmask, 3.28 MB.
- **For the reviewer (Rendering):**
  - ADR 0024's hair values. Watch the cool tint under a non-warm key.
  - M1-RND-20.
  - The skin's evenness, which is now shading.
  - The GPU 2× High capture of asha_face_* (M1-QA-05c).

## Review log
