---
id: M1-CHR-04
title: Asha close-range polish - lips, hair, skin micro-detail, costume materials
role: character
status: todo
owner_session: ""
depends_on: [M1-CHR-03]
milestone: M1
request-from: "lead"
---
## Goal
CHR-03 put Asha on the MPFB2 donor topology, which is a clear step up. At the Lead's look at `asha_face_stylized_compare`, the hero is still not at final fidelity at dialogue range.

## Acceptance criteria
- [ ] Lips: rest shape thinner and less rubbery; no dark seam line at the lip contact; the mouth interior and corners read correctly in neutral, smile and grief
- [ ] Scalp hair: no visible card blocks or gaps at dialogue range; a soft hairline; strand-level alpha detail; the braid kept (asha.md hair section)
- [ ] Skin: micro-detail (pores, fine lines) at the specified texel density; less waxy specular; the painterly close-up look stays per ADR 0019
- [ ] Costume: the bodice and vest read as cloth or leather of the right roughness, not glossy plastic (character_shading.md contract)
- [ ] Shadow banding on the shadow-side cheek: confirmed as a renderer artifact or fixed (the GPU-session check, M1-QA-05)
- [ ] §14 dialogue-range review re-run side by side with CHR-03 and recorded in asha_review.md; baselines re-approved with reasons

## Notes

The work is split between two sessions; each writes only its own subsection.

### Mesh and texture half: character, worktree `worktree-agent-a2cf1ae55d2ab435e` (2026-10-23)

**Done, on lavapipe.** Lips, scalp hair and skin micro-detail. Details are in asha_review.md §7 and handoff `2026-10-23-character-2.md`.
- **Lips:** the slit to the mouth interior is sealed on the final face (`bb_donor.lip_rest`; new `bb_params` sliders `lip_close`, `lip_seal` and `lip_lower_fullness`, whose defaults leave the base bodies unchanged). The rest shape is thinner. The misplaced CHR-03 crease is removed, and the contact and corners are baked. The striations are softened.
- **Hair:** cards sit on the head mesh (`MeshScalp`), with a hairline row, narrower layers, a strand-level atlas with feathered clump edges and soft-root columns, and a scalp underpaint. The braid is kept.
- **Skin:** pores, micro-relief and soft expression lines at 69 px/cm on the face mask (target ≥ 50). The head ORM and skinmask are now 2K. Roughness and cavity are broken up (less waxy), with colour zones added. The ADR 0019 dialogue material is unchanged.
- **The §14 review** is in asha_review.md §7.3: **passes at dialogue range as built**. The cheek banding remains, for the GPU half.
- **Numbers:** LOD0 63,444 tris, LOD1 29,862, `asha.glb` 4.04 MB. `verify_blender_builds.py --job asha` is identical.

**Not touched, for the GPU session (`gpu/chr-04-materials`):**
- no light, shadow or `shadow_normal_bias` setting;
- the cloth materials (`cloth.tres`, `cloth_sleeve.tres`), the cloth textures and the cloth shader.

`write_materials.py` changed only the `teeth` entry. Running it rewrites `cloth.tres` byte-identically from its unchanged table row, so merge your cloth changes into `write_materials.py` too, or they will be overwritten on the next run.

**Acceptance boxes this half covers:**
- lips;
- scalp hair;
- skin;
- the §14 review;
- the baselines, for this half.

Costume and banding are the GPU half's. When both halves are in, the boxes can be ticked and the task can go to review (Rendering).

## Review log
