---
id: M1-CHR-04
title: Asha close-range polish - lips, hair, skin micro-detail, costume materials
role: character
status: doing
owner_session: "lead-cloud (mesh half, merged b3b66ac) + session_01778wbLbDFnRRLTKjnawv3T (PC: shadows and materials)"
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
- 2026-10-23 rendering-side fresh reviewer (review-sweep-J): **progress note, NOT a final verdict.** The task is still in progress: the GPU half is outstanding. Note that the front matter says `status: todo` with an empty `owner_session`, while two sessions are working on it. The Lead should set `doing` and record both claims.
  - **What I viewed:** these baselines at 960×540: `asha_face_neutral`, `asha_face_smile`, `asha_face_grief`, `asha_face_stylized_compare`, `asha_front`, `asha_q34`. I also looked at 3× crops of the mouth and hairline, and read asha_review.md §7 and handoff character-2.
  - **Real progress since CHR-03:**
    - The lip slit is mostly closed at rest.
    - The grief teeth are warm.
    - The CHR-03 crease is gone.
    - The braid reads well.
    - The eyes read at dialogue range.
    - Asha's Blender job verifies 44 files identical.
  - **I do not agree with §7.3's "passes at dialogue range as built".** What still blocks SPEC §14 (the "uncanny" risk row) at dialogue range:
    1. **The mouth (mesh or texture half).**
       - The upper and lower lip read as one smooth, swollen, uniformly pink roll, with no cupid's bow, philtrum groove or vermilion edge. The lower lip still overhangs.
       - On the shadow side the contact still shows a black glossy slit in `asha_face_smile`, around x 430-500, y 345-360.
       - The striation banding runs through the lip shadow.
    2. **The expressions do not read.**
       - `asha_face_smile` differs from `asha_face_neutral` in only about 5,000 pixels (more than 10 levels), all around the mouth.
       - asha.md:158's `smile` asks for `cheek_raise` 0.45 and `lid_squint` 0.25. Neither cheeks nor lids move in the frame, so the smile is a mouth-only change, and that is the classic uncanny cue.
       - Check that the emotion's weight table actually drives the cheek and lid shapes. It looks like a data or driver gap, not polish.
    3. **The hair (mesh or texture half).**
       - At this framing the hairline is one hard, continuous dark edge over a very high bare forehead. The mass reads as a smooth painted shell, a helmet, not strands.
       - Flat stray cards show at both temples. On screen left a dark card with a pinkish streak crosses down past the brow, at about x 375-390, y 100-250 in `asha_face_neutral`. On screen right a pale rectangle sits above the ear, at about x 700-712, y 175-205. If that is the shell clasp, it is floating off the braid.
       - The hair is warm brown, but asha.md:121 says **black**. The handoff calls it a shader lobe, but at dialogue range it is off-spec, whatever the cause.
    4. **Brows** are solid dark bars with blocky ends, not hair strokes. They show most in the grief frame.
    5. **Shadow banding (GPU half).** Horizontal contour stripes cross the shadow-side cheek, the **forehead** and the lips in all three face shots. The nose casts a hard, detached wedge across the cheek. This is still the single most visible artefact.
    6. **Costume (GPU half).** The bodice, vest and collar read as glossy black plastic with mirror-like highlights: the collar in every face shot, and the bodice in `asha_front` and `asha_q34`. That fails the character_shading.md contract. The gauze sleeve reads as coarse netting in `asha_front`.
  - **Before the §14 re-review:**
    - The GPU half lands (banding, cloth).
    - Items 1-4 get a pass on the asset side.
    - Re-run the review with GPU 2× captures beside these frames, and record the result in asha_review.md as a new subsection. Do not overwrite §7.3.
- 2026-10-23 lead: status corrected to doing. The mesh half is merged; the sweep-J progress note's remaining faults are in M1-CHR-07 (mesh, rig and hair) and with the PC session (shadows and materials).
