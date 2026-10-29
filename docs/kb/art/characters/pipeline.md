# Character base-body pipeline (M1-CHR-01)

Owner: Character Artist. Decision record: [ADR 0010](../../decisions/0010-character-base-mesh.md) (from scratch, no MPFB). Pipeline frame: SPEC §7.3 and ADR 0005.
Source: `assets_src/characters/base_body/`. Output: `assets/characters/base_body/base_body_<variant>.glb`. Review scene: `game/levels/_tests/characters/base_body_test.tscn`.

Status: **PLACEHOLDER art** (SPEC §8.4). The output is a sculpt-ready, rigged base body with a flat skin-tone material and painted placeholder eyes. It is the foundation for M1-CHR-02 and is not shippable art.

## 1. Build

```bash
python3 tools/dev/fetch_blender.py                       # once: Blender 5.0.1 (Debian) into ~/.cache/hymn
assets_src/characters/base_body/build_all.sh             # all variants, ~20 s each
# one variant, with every option:
blender --background --factory-startup --python assets_src/characters/base_body/build.py -- \
  --variant slender --out assets/characters/base_body/base_body_slender.glb \
  [--set height_m=1.66] [--params my.json] [--report r.json] [--dump-npz m.npz] [--blend rig.blend] [--no-rig]
python3 assets_src/characters/base_body/preview.py m.npz out.png --zoom head   # seconds-fast clay preview
tools/screenshots/capture.sh --shots base_body_slender_front                     # the real Forward+ review
```

The build is **deterministic**: two builds of the same variant are byte-identical (`sha256` checked). `--blend` saves the Rigify control rig for animators. It is not committed (size, and it is regenerable).

## 2. Stages

| Stage | File | What happens |
|---|---|---|
| Parameters | `bb_params.py`, `variants/*.json` | Merge defaults, then the variant file, then `--set`. Unknown keys are an error. |
| Landmarks | `bb_params.Landmarks` | Joint centres and surface reference points (crown, chin, notch, shoulder, elbow, wrist, the full hand with 5 digits, hip, knee, ankle, heel, ball, toe, eyes, mouth, ears), all from head-unit proportions. |
| Anatomy field | `bb_anatomy.py` | A smooth union of primitives (ellipsoids, round cones, round boxes) per region: torso, head, arm, hand, leg, foot (×2 for paired regions). Muscle bellies (deltoid, biceps, triceps, forearm mass, pecs, lats, scapulae, trapezius, SCM, quads, hamstrings, adductors, calves) scale with `muscle`. Fat pads (belly, hips, glutes) scale with `mass` and `femininity`. The **face** is a cranium plus lower-face "egg", jaw, chin, masseter and zygomatic arch, plus **sculpt displacement**: a nose profile spline and 17 named Gaussian terms in face space (alae, lips, cupid's bow, philtrum, mentolabial sulcus, orbits, brow, glabella, cheekbones, temples and others). |
| Cage | `bb_cage.py` | Explicit quad topology, ray-cast onto each region's own field (§3). |
| Subdivide | `catmull_clark` | One Catmull-Clark level, written in numpy. Pins, seams and groups propagate. |
| Project | `project` | Newton steps onto the joined field (regions blended with `k_join` = 1.4 cm), interleaved with tangential Laplacian relaxation. Lid margins, the lip line, the eye sockets and the mouth bag are pinned. Soles are flattened onto z = 0. |
| UV | `build.mark_seams_and_unwrap` | Seams placed by the cage builder (§4), then a conformal unwrap and pack. |
| Rig | `bb_rig.py` | Rigify metarig fit, generate, deform-only skeleton, bone-heat skinning (§5). |
| Export | `build.py` | GLB with skinned body, two eye meshes, the `DEF-*` skeleton, tangents, and `extras.hymn_tag = "PLACEHOLDER"` on the scene, nodes, meshes and materials. Materials are named `PLACEHOLDER_*`. About 0.98 MB each. |

## 3. Topology notes

Base mesh: **25,696 triangles** (12,848 quads, 12,850 vertices) for every variant, plus 1,440 for the two eyes. (21,120 before the M1-CHR-02 head rebuild.) Every face is a quad, the mesh is closed and manifold (the build logs `non-manifold edges 0`), and it is ready for further subdivision.

| Part | Cage (before Catmull-Clark) | Loops |
|---|---|---|
| Torso + neck | 32 around × 18 rings (+ a yoke at the shoulders, tilted rings at the crotch) | Hip, waist, chest, armpit and neck loops |
| Armholes | 2 × 3-cell holes per side → 10-vert arm tube | Armhole loop, shoulder, 4 upper-arm loops, **elbow** loop, 4 forearm loops, **wrist** |
| Legs | The bottom torso ring splits at a crotch vertex into two 18-vert loops (a briefs-line leg loop) | 5 thigh loops, **knee**, 6 shin loops, **ankle** |
| Feet | 12 around × 11 rings, ankle enters through a 4×5-cell hole | Heel and toe caps are 2×4 grids. Toes are a mitten (see weaknesses). |
| Hands | 10-vert palm tube. Four 4-sided finger tubes consume the knuckle end, the thumb grows from the radial side | Rings at **MCP, PIP, DIP** with mid-phalanx rings; fingertips capped with a quad |
| Head (`bb_head.py`, M1-CHR-02) | A box lattice (18 × 17 × 8 cells) whose lines sit on the face's landmarks, ray-cast from the head centre. The neck enters a 12×4-cell hole centred under the neck column | **Eyes:** a 6×2-cell block (16-vertex loops) refilled with two orbicularis-oculi loops, a crease/lower-lid loop, the lid surface, the lid margin as two pinned loops (outer edge and the edge on the globe, so the margin has thickness) and a socket, capped. The canthi are loop vertices. **Mouth:** a 12×4-cell block (32-vertex loops): nasolabial/outer orbicularis loop, a second orbicularis loop, vermilion border, mid-vermilion, contact line (pinned), inner lip and mouth bag (tagged `mouth`), capped |

After one subdivision level every loop doubles: eye loops 32 verts (6 concentric loops), lip loops 64 (7 loops), fingers 8 around, arm 20, leg 36. Poles (valence 3 and 5) sit at the eye and mouth block corners (lateral brow, side of the bridge, below the outer canthus, beside the alae, below the mouth corners), the armhole corners, the crotch vertex and the finger webs, away from the lid and lip lines and the main bend lines.

**The head field (M1-CHR-02, `bb_face.py`)** is a lofted solid (horizontal superellipse sections from tables you can read as a profile: chin, mouth base, nose base, nasion, glabella, forehead, vertex), closed underneath by the mandible's lower border as a tilted plane (no shelf, no web into the neck); heightfield terms for the soft forms; nose tip, columella and alae as primitives with the nostrils subtracted; and **lids as a solid**: an ellipsoid around each globe with the almond aperture cut through it, cross-faded into the face by distance from the fissure, so the lid margin has its 1.9 mm thickness and the brow overlaps the lid to form the crease. `assets_src/characters/asha/sdf_preview.py` sphere-traces this field directly (seconds per view) for sculpt iteration.

## 4. UV notes

950 seam edges in these islands: torso (back centre line), head (back of head to crown, plus the neck junction), each eye socket and the mouth bag, arms (underside line), palms (ulnar edge), **each finger and thumb**, legs (inner line), ankle bands, sole, upper foot, heel and toe caps. The build reports coverage of about 0.7, **0 degenerate faces**, and texel-density spread p95/p5 of about 2.7 overall (about 6 at the fingertips). These UVs are for bakes and procedural masks on the base. M1-CHR-02 re-lays the face onto its own 4K set (asha.md §8.2).

## 5. Rig notes

- **Rigify is available** in this Blender build. The script adds the stock human metarig, deletes its face bones (faces use the shared blendshape API in asha.md §6.2), adds `eye.L` / `eye.R` (`basic.super_copy`), fits every bone to the landmarks, keeps each bone's original roll axis (`align_roll`) and the metarig's own connect flags, then runs `rigify_generate` (416 control bones).
- The **game skeleton** is a separate deform-only armature: all **75 `DEF-*` bones**, each parented to its nearest deforming ancestor (`DEF-upper_arm.L ← DEF-shoulder.L ← DEF-spine.003`, and so on). Limbs have 2 twist segments each (`DEF-upper_arm.L.001`). The GLB carries only this skeleton.
- **Weights:** Blender automatic (bone heat) against the generated rig's DEF bones, then re-pointed to the game skeleton. No vertex was left unweighted, and the build has a nearest-bone fallback that logs a count. The eyes are rigid on `DEF-eye.L/R`. The glTF exporter keeps the 4 strongest influences.
- **Check:** the `base_body_slender_posed` shot bends the elbows, hip, knee, neck and right fingers through `BaseBodyStage.test_pose`. Bends hold volume at review distance. A close review of the weights (crotch, armpit, finger webs) is M1-CHR-02 work.

## 6. Parameters and adding a variant

All keys, with defaults, are in `bb_params.DEFAULTS`. Widths are in **head heights** (vertex to chin), the canon asha.md uses.

| Key | Meaning |
|---|---|
| `height_m`, `heads_tall` | Stature and head ratio (SPEC §7.3: 7–7.5) |
| `shoulder_width_heads` | **Biacromial** (acromion to acromion). Rhen's and Toma's sheets give bideltoid figures (1.95 and 2.30 heads); the variant files convert them (1.76 and 1.86) and say so in `_about`. |
| `chest_width_heads`, `chest_depth_heads`, `waist_width_heads`, `hip_width_heads` | Torso masses |
| `crotch_height_heads`, `arm_span_ratio`, `hand_length_heads`, `foot_length_ratio`, `neck_length_heads` | Limb proportions. Upper arm to forearm is 0.555 : 0.445, thigh is 0.525 of the leg. |
| `neck_width_ratio`, `head_width_ratio` | Of head width and head height |
| `femininity` (0–1), `muscle` (0–1), `mass` (0–1), `breast` (0–1) | Sliders: pelvis/jaw/fat pattern, muscle-belly size, subcutaneous volume, breast volume |
| `eye_scale`, `ipd_m` | SPEC §7.3's ×1.10 eyes, interpupillary distance |
| `arm_abduction_deg` | A-pose angle (47° below horizontal) |
| `skin_hex` | Placeholder albedo (from `palette.json`) |

To add a variant:
1. Copy a file in `variants/` and set `name` and the values.
2. Run `build_all.sh <name>`.
3. Add a `PROVENANCE.md` row.
4. If it needs review, add a stage to `base_body_test.tscn` and shots to `shots.json`.

Hero builds (M1-CHR-02) should read their body block from `assets_src/characters/<hero>/<hero>_params.json` (asha.md §9.1) through `--params`.

Results (from the build report):

| Variant | Height | Head | Heads tall | Body tris |
|---|---|---|---|---|
| slender (Asha-like) | 1.630 m | 0.222 m | 7.34 | 25,696 |
| athletic (Rhen-like) | 1.770 m | 0.237 m | 7.47 | 25,696 |
| heavy (Toma-like) | 1.890 m | 0.252 m | 7.50 | 25,696 |

The heavy variant was reshaped on review-sweep-B (less belly fat, broader shoulders, a shallower trunk, a slightly larger head).

## 7. Review scene and shots

`base_body_test.tscn` instances `base_body_stage.tscn` four times, 40 m apart: Slender, SlenderPosed, Athletic and Heavy. Each stage has a three-point light (key spot with shadows, fill, two rims), a grey floor and an enclosing grey cyclorama, plus Front, ThreeQuarter (the body's right side, asha.md's hero angle), Side and Face cameras. The Face camera aims itself at the `DEF-eye` bones. Set `spin_degrees_per_second` on a stage to use it as a turntable by hand.

Shots in `tests/screenshots/shots.json` (432×768, Face 512², 24 settle frames): `base_body_{slender,athletic,heavy}_{front,q34,side}`, `base_body_slender_face` and `base_body_slender_posed`. Captured alone they match bit for bit. Inside a full `capture.sh` run they differ by RMSE ≈ 0.002 (state carried over from earlier shots), well under the 0.008 limit.

## 8. Known weaknesses (honest)

*M1-CHR-02 update:* the head now has loop flow, real lids, a lofted face, nostrils (in the field and the bake) and a softened jaw/neck junction; see `asha_review.md` for the hero's state. The base bodies still use the flat placeholder material, so the notes below about the face describe the **placeholder** read.

- **Face:** reads as a mannequin or wax bust, not a person. The mid-face is long and slightly muzzle-like in 3/4. The lip line is a hard slit, the eyes stare (no lashes, brows, tear line, caruncle or lid thickness detail), the ears are lumps, and there are no nostrils. **This is the main §14 risk and it is not solved.**
- **Hands:** proportions and joint loops are right, but fingers are smooth tubes (no knuckle or nail detail) and the thumb root is soft. **Feet** are mittens with no separate toes, which matters because Asha wears sandals.
- **Torso:** the heavy and athletic chests are plausible but generic, with no serratus, abdominal or clavicle definition. The slender shoulders are a little peaked at the acromion. Breasts are simple volumes.
- **Bald, nude, flat-shaded placeholder**, which by itself pushes any human toward uncanny. It has no skin shader, hair or costume.
- **Weights** are automatic and unreviewed. There are no corrective shapes, and no face blendshapes yet (the names are fixed by asha.md §6.2).
- Some UV distortion remains at the fingertips and the lid corners.

## 9. Assessment against the SPEC §14 uncanny risk

At battle and field distance (5–15 m, LOD1 range) the bodies read as believable adults of three distinct builds, with correct proportions and nothing toy-like or chibi. At cinematic distance the face fails: it sits in the uncanny valley today. The pipeline is the right shape to fix that, because every facial feature is a named, data-driven term, and topology, UVs and rig survive any change to those terms. It does not yet hold the knowledge MakeHuman's targets would have given us.

## 10. What M1-CHR-02 (Asha at final fidelity) needs next

1. **Face sculpt pass:** a denser face lattice (or a second subdivision level on the head only, about +9k tris inside the asha.md §8.1 budget), lid thickness and crease, caruncle and tear line, nostrils, philtrum and lip vermilion border, cheek fat pads, ear helix and antihelix. Tune against asha.md §6.1 (oval face, narrow jaw, cheekbones at 0.70 head width, almond eyes with a 4° tilt, mouth at 0.40 head width) using the Face shot plus front and profile orthographic previews.
2. **Blendshapes:** the 32 asha.md §6.2 shapes and 10 visemes, as procedural displacement deltas on the same face-space terms.
3. **Eyes:** a cornea shell plus iris, with refraction (M1-RND-04), lashes and brow cards.
4. **Hair cards:** the braid, scalp layers and flyaways (asha.md §5). The scalp cap reuses the head lattice region above the hairline.
5. **Costume panels** (asha.md §9.2): hidden body under clothing is deleted. The torso ring and column indices give stable selection regions for that.
6. **The skin shader from Rendering (M1-RND-04):** pre-integrated SSS with a painterly bias. The `*_skinmask` bake inputs (thickness, cavity) can come from the field (distance to bone axes) and from mesh curvature.
7. **Weight review and correctives** (elbow, knee, shoulder raise, hip flexion), then LOD1–3.
8. If the face review fails twice, escalate SPEC §16 Q2 (MPFB as a topology donor) to the human, per ADR 0010.

## 11. M1-CHR-03: the donor topology (ADR 0021)

Since M1-CHR-03 the mesh is no longer the procedural cage. `bb_donor.generate(params)` puts the **MakeHuman hm08 CC0 base mesh** (vendored in `assets_src/third_party/mpfb2/`, read by our own `mpfb_data.py`) behind the same interfaces: the parameter files, `Landmarks`, the `DEF-*` skeleton and the asha.md §6.2 shape names. The cage builder (`bb_cage`, `bb_head`) is kept for its helpers (`check_manifold`, `cast`, `eye_mesh`) and as history.

| Step | What happens |
|---|---|
| Macro mix | The donor's young sex/ethnicity targets plus the muscle/weight targets, mixed by `femininity`, `muscle`, `mass` and `donor_mix_{african,asian,caucasian}` |
| Fit | A polyharmonic RBF warp from the donor's joint markers onto our landmarks; the head, hands and feet move as exact similarity transforms (head height, palm length, foot length). The face, finger and foot landmarks are then **read back from the placed donor**, so the rig and the eye and mouth parts agree with the mesh |
| Girth | Torso, arm and leg cross-sections are scaled (22 sections × 16 angles, smoothed) to our anatomy field's radius, so the width, depth, muscle and mass sliders still shape the body |
| Eyes and mouth | An RBF re-shapes each lid margin onto `EyeFrame` (fissure ×1.10, tilt, canthus) and tucks the socket behind our globe; the donor's resting lip parting is 45% closed |
| Face sculpt | The bb_params face sliders as smooth face-space deformations (1.0 / 0.0 = the donor's own form) |
| Field | Every anatomy-field region is offset by a grid so its zero set lies on the donor skin (p95 error < 2 mm). Costume panels, hair cards, brows and sandals ray-cast against it unchanged |
| Weights | The donor's Rigify weights mapped onto our 75 `DEF-*` bones (`bb_donor.bone_of`; `bb_rig.skin_with_weights`). No bone heat |
| UVs | Base bodies keep the donor's atlas. The hero head is our own unwrap (face mask, rest of head cut down the back, sockets and mouth cavity); the hero body re-flattens the donor's islands |

Base bodies: 13,380 vertices, 13,378 quads (26,756 triangles) for every variant, closed and manifold. The hero adds one Catmull-Clark level (`bb_donor.subdivide`, a linear stencil that also carries weights, masks and shape deltas) on the face mask and lips; the neighbouring quads are fan-triangulated through the edge points, so the mesh stays watertight. `python3 assets_src/characters/base_body/preview.py ... --zoom face` is the quick clay view.

Known weaknesses: the base bodies' breasts are flattened by the girth fit (the field's breast volume, not the donor's). The heavy variant's depth comes only from the field's torso and is still shallow. The donor's ears and hands keep the native density.

## 12. Adding a hero (M2-CHR-01, Rhen)

A new hero is a folder `assets_src/characters/<hero>/` that **imports** Asha's modules instead of copying them:
- `build_<hero>.py` imports `build_asha` as a helper library (`make_object`, `unwrap_faces`, `submesh`, weights, `dump_bake`,
  `make_lod1`, …). It adds preview colours for new material names to `build_asha.MATERIALS` and replaces `build_asha.LOD1_RATIO`
  with its own object names. Head, face shapes, eyes and teeth are built exactly as Asha's.
- Hair, costume and props are the hero's own modules, written on the shared helpers (`asha_hair` cards and atlas columns;
  `asha_costume` charts; `asha_mesh`). A hair module must also provide `hairline_v`, `in_hair`, `_gather` and `_flow_dir`, which
  the skin maps read to paint the scalp.
- `<hero>_textures.py` sets `asha_textures.OUT`, `PREFIX`, `SKIN_HEX`, `FRECKLES` and `HAIR_UNDERPAINT`, may wrap
  `asha_textures.albedo` for its own skin terms, then calls `skin_maps`; it writes its own cloth atlas.
- `write_materials.py` loads Asha's writer by path and points it at the hero's folder; generic atlases (eyes, hair, lashes,
  brows, detail normals) are referenced from `assets/characters/asha/textures/`.
- A job in `tools/dev/blender_builds.json` whose sources include `assets_src/characters/asha/**` (so a shared change
  re-verifies every hero), PROVENANCE rows, a stage `game/levels/_tests/characters/<hero>/` on `asha_stage.gd`
  (`character_name`), and shots. Rhen's review: [`rhen_review.md`](rhen_review.md).

Toma (M2-CHR-02, [`toma_review.md`](toma_review.md)) is the second hero on this layout. Two additions worth reusing:
- **Face hair in the Head object.** A beard (or any card layer that must follow the face shapes) goes into the Head's
  extras before the shapes are built; after `build_shapes`, each of its vertices takes the delta (and the skin weights)
  of its nearest skin vertex, with deltas under 0.15 mm zeroed so the sparse morph accessors stay small (`build_toma.py`).
  Every Head vertex carries 40 morph targets, so the card count there is bounded by the 5 MB GLB cap, not the triangles.
- **Hero costume helpers are importable too:** `toma_costume` imports `rhen_costume` (`torso_sheet`, `limb_tube`,
  `bandolier`), so the `toma` job lists `assets_src/characters/rhen/**` among its sources.
- **Hero-specific bones (M2-CHR-04):** extra `DEF-*` bones go on after `bb_rig.build_game_skeleton` in the hero's own
  build (`build_toma.add_bones`: sash-tail chains, the pauldron hinge, shield and spear prop bones), with the costume or
  prop vertices re-weighted to them; bb_rig stays the same for every hero. The standard 75 keep their names and
  relative order; their absolute joint indices move (the exporter walks the hierarchy), so find bones by name.
- **Card hair for short lengths (M2-CHR-04):** a hero-owned strand atlas (`toma_shorthair.png`, tufts of tapered
  strands with soft sides) and mostly-Lambert hair shading (`kajiya_diffuse_mix` 0.15) for cropped hair and a short
  beard; paint the skin between the painted hairs as shaded scalp, not lit skin.
- **Short cards at dialogue range (M2-CHR-524):** at 1-2 px per mm a card is 10-15 px wide and the strands inside it are
  far below a pixel, so what reads is the card's mip-averaged alpha and its shading. Keep both flat: (1) the atlas
  spreads its strands evenly across a column at partial opacity (no dense core: a core resolves as a dark lozenge per
  card); import the atlas **with mipmaps** (the contract's rule; Toma's atlas had them off). (2) Shade the cards with
  the skin's normal (`toma_hair.surface_normals`, sign-matched to the card's winding), not their own tilted, rolled
  face: own normals light each card separately and the crown breaks into flakes. (3) Keep the cards' albedo and
  occlusion near the scalp paint's rendered value (`root_occlusion`/`depth_occlusion` 0.85 on cards that lie on the
  skin), so the cards add grain over the paint rather than dots. (4) Grey cards are a veil (`alpha_boost` 0.6), so
  salt-and-pepper reads as a lighter haze, not pale chips. (5) Region edges (the beard round the mouth) are distances
  in head heights, so the skin's beard shadow ramps over millimetres; a steep term draws a hard notch.

## 13. Body clips (M2-FP-07)

`assets_src/characters/asha/hero_clips.py` (pure Python, no Blender) writes each hero's body clips as a Godot
AnimationLibrary text resource, `assets/characters/<hero>/anim/<hero>_clips.tres`, from the skeleton rest read out of
the hero's committed GLB. Poses are rotations in world axes on top of what each bone inherits (as `AshaStage.world_pose`),
plus a hips offset, sampled at 15 fps; every clip keys the same 31 body bones (spine, neck, head, arms, legs and their
twist segments), so a clip change never leaves a limb in the previous clip's pose. The `characters` import rule
(`animations` in `game/data/import/characters.json`) puts the library on an `AnimationPlayer` at the asset root with a
0.3 s default blend. `tools/tests/test_hero_clips.py` rebuilds the libraries and compares them byte for byte, so rerun
`python3 assets_src/characters/asha/hero_clips.py` after any rebuild that moves a skeleton.

| Clip | Loop | Notes |
|---|---|---|
| `idle` | yes | Stillness with breath and a slow weight shift (sway 40% for Asha, 130% for Rhen, his 4° lean) |
| `walk`, `run`, `walk_to_chamber` | yes | In place (the sequencer moves the actor); Asha's staff arm swings less and its hand keeps the staff upright |
| `talk` | yes | The free hand lifts and falls once per loop; head and shoulders move a little |
| `kneel_over_rhen` | no | Onto the right knee, the left foot planted, leaning over someone lying in front; holds |
| `laugh`, `offer_hand` | no | **Kneeling** (the beach scene plays them while she kneels); the head tilts back in the laugh |
| `rise_to_stand` | no | From the kneel to standing |
| `emerge_doorway` | no | A tired settle, one step, the head lifts (ADR 0017: on her own feet) |
| `face_west` | no | A settle into the singing stance, the free hand to the breastbone; the facing comes from the `@mark` |
| `take_hand` (Rhen) | no | From the kneel, the right hand reaches forward and up |
| `spear_level` (Toma) | no | Both hands on the shaft, the spear levelled forward and a little down, knees bent, leaning in; holds |
| `lower_spear` (Toma) | no | From `spear_level` back to his planted stance |
| `palms_level` (Toma) | no | "Be level": the left palm comes up flat at chest height and sweeps slowly out; the head bows |
| `catch_rhen` (Toma) | no | The left arm reaches forward and takes Rhen's weight, a small turn toward him, the knees brace; holds |
| `sit_steps` (Toma) | no | Down onto a step at knee height, knees apart, the left forearm on the thigh, the spear upright; holds |
| `turn_seaward` (Toma) | no | Head first, then chest and hips turn about 50° to his left; the facing itself comes from the `@mark` |

**Toma (M2-CHR-04):** persona sway 0.7 (toma.md §1: 70% of the party default) and a **planted** base pose for his
standing clips (`idle`, `talk` and his own): each leg swings out so the ankles sit 1.4× the shoulder-joint spacing apart
(about 10° per leg on his skeleton), the knees soften 7° and the hips drop by what the two take (2.7 cm), feet flat. His
spear is held like Asha's staff (the hand counter-rotates so it stays upright) except where `spear_level` turns it;
the spear rides the `DEF-spear` prop bone, which the clips leave at rest (only the 31 body bones are keyed). Asha's and
Rhen's libraries are byte-identical (`planted` is `stand` for a persona without a `stance`).
`tools/tests/test_hero_clips.py` checks that every `@anim toma <clip>` has a clip, the stance ratio and feet on the
floor, the spear upright in the standing clips and levelled in `spear_level`, and the seat height of `sit_steps`.
Rerun `python3 assets_src/characters/asha/hero_clips.py --hero toma` after any Toma rebuild.

Review shots: `asha_clip_kneel_over_rhen`, `asha_clip_walk`, `asha_clip_offer_hand`, `asha_clip_face_west`,
`asha_clip_laugh`, `asha_clip_run` (AshaStage `clip` and `clip_time`).

## 14. Battle-scale heroes (M2-CHR-06)

`game/characters/heroes/<hero>_battle.tscn` instances `<hero>_lod1.glb` (about 27–29k triangles, under 1.5 MB). The import
rule's `animations.strip_suffixes` lets the LOD file share its hero's clip library, so the battle actor has the same
`AnimationPlayer` clips as the dialogue model. The battle's capsules are swapped by UI+Combat (task M2-UI-07: a `"scene"`
key in the stand-in spec of `game/data/ui/battle_sandbox.json`).

## 15. Villagers at an NPC budget (M2-CHR-03)

`assets_src/characters/villagers/` is the §12 layout made parametric: **one** build (`build_villager.py --npc <id>`) and
one `params/<npc>.json` per villager (the bb_params block plus `_skin`, `_hair`, `_costume`, `_tints`, `_persona`,
`_build`), seven Blender jobs (`villager_<npc>`) and `build.sh [npc ...]`. Review: [`villagers_review.md`](villagers_review.md).
- **Budget levers:** no face subdivision (head about 9.9k triangles instead of 20k), the head maps at 1K/512 and the
  body at 512, morph normals only on the 12 expression shapes the pose tables lean on; all 40 shapes still fit (about
  25-35k LOD0 triangles, 1.7-2.2 MB per GLB).
- Without the subdivision the face is 1.9 mm facets that cross the smooth anatomy field: anything laid on the field at
  the face (the brow cards) must be re-seated on the shipped skin (`head_surface(...).project`).
- **One cloth atlas for every villager** (`villager_textures.py --cloth`), painted near-neutral; the colour variants are
  `col_albedo` tints on each villager's `cloth_a/b/c` materials. A new villager is a params file, not a texture set.
- Hair styles (`villager_hair.HairStyle`: short, cropped, bun, wrap) carry their own hairline and flow, which the skin
  maps read through the same interface as the hero hair modules.
- Every villager folder is in the `characters` import rule, so an instanced GLB comes dressed and with an
  `AnimationPlayer` (`idle`, `talk`, `walk` from `villager_clips.py`); `<npc>_actor.tscn` turns it to face -Z for the
  level's NPC nodes.

## 16. Rig integrity guards (M1-CHR-14)

A headless probe skins each hero's committed GLB in numpy for the poses the game plays, then measures three faults:
a braid that floats off the head, clothing or props passing through the body, and seams or hidden-face holes that open
in a pose. It needs no Blender and no Godot.

```bash
python3 tools/dev/rig_probe.py --hero asha --report            # verdicts, then per-pose tables (about 45 s)
python3 tools/dev/rig_probe.py --report --json /tmp/rig.json   # every hero, with the full rows as JSON
python3 tools/dev/rig_probe.py --hero toma --report --every 1  # every clip key (slow)
HYMN_RIG_ROOT=/path/to/checkout python3 tools/dev/rig_probe.py --hero asha  # GLBs from another checkout (or --root, --glb)
python3 -m unittest tools.tests.test_rig_integrity             # the CI guard (about 2 min for all three heroes)
```

**Poses.** The rest pose, any stage test pose listed under `stage_poses` (Asha's `asha_extreme_pose.tscn`, composed the
way `AshaStage._apply_world_pose` does it), and every third key of every clip in `hero_clips.py`. Long clips widen the
stride to about 10 samples each. The clip poses come from the same functions that write the AnimationLibrary, so a
pose here is the frame the game shows. Bones the clips don't key (fingers, eyes, props, sash tails) stay at rest
relative to their parents. The skinning is plain linear blend (`sum w * G_joint * IBM`), the same as Godot's. At rest
it reproduces the stored mesh to within 1e-5 m, which `TestProbeMath` checks along with a synthetic single-bone turn.

**Checks** (thresholds are in `tools/dev/rig_checks.json`; per-hero overrides go under `heroes`):

| Check | What it measures | Limit |
|---|---|---|
| `braid gap` | Each woven strand of the braid (a connected piece of `HairBraid:hair` with at least 300 vertices) has a root ring: its open end nearer the scalp at rest. The gap is the ring's closest signed distance to the hair cap plus the head skin, with inside counted as 0. | 2 mm |
| `braid drift` | How far a root-ring vertex moves in the head bone's frame (`DEF-spine.006`) compared with rest. It is 0 when the root is skinned to the head. | 2 mm |
| `penetration garment_in_body` | A garment vertex inside the skin (Body plus the head skin): its signed distance to the posed skin surface, with each of the deepest candidates confirmed by the skin's winding number. That way a point beside a limb, or over a hole where hidden faces were deleted, doesn't count. | 3 mm |
| `penetration prop_in_body` | The same for props (staff, spear, shield, Rhen's kit), except where the skin belongs to the holding hand (`grip_bones`). | 3 mm |
| `penetration skin_through_garment` | Skin poking out through cloth, measured relative to rest. At rest, a ray along each Body vertex's normal finds the garment point over it, within 20 mm. In each pose, the check measures how far the skin has passed that same cloth point (same triangle and barycentrics) along the posed skin normal. At rest this is 0 by construction, so a garment edge beside the skin can't trigger it. A layer that already passes inside the body at rest is the job of `garment_in_body`. | 3 mm |
| `seam coincident <group>` | Positions welded at rest (the Head/Body neck seam, UV-seam and panel duplicates) that separate in a pose. | 0.5 mm |
| `seam boundary_exposed` | The Body's open boundary, where faces hidden under clothing were deleted. Each boundary vertex casts a ray along its normal and must meet a garment within 300 mm. Rays pass through skin, so the inner leg under a skirt still counts as covered. The count is of uncovered vertices. | 0 |
| `skin weights` | Weights sum to 1 (±0.001), no negative weights, every joint index exists. | — |

Each failure names the pose (`clip@key`), the mesh and material, the dominant bone on both sides, and the vertex's rest
position, so the fix can be found in the source. The garment-in-skin count only covers confirmed vertices among the
deepest 24 per group and pose, so treat it as a lower bound; the worst depth is exact. Add a new hero by adding a
`heroes` entry (its props, garments and seam groups). Meshes named in the config but missing from a GLB are skipped,
and a hero with no braid skips the braid checks.

## 17. Helper bones for deep poses (M1-CHR-15)
Linear blend skinning cannot keep a floor-length skirt over a lunge or the underarm out of the bodice, so the builds
add helper bones that no pose names, and every clip keys them from its own pose.
- **Where they live:**
  - the bones and their weights: `assets_src/characters/asha/helper_bones.py`, wired in through `build_asha.add_bones`
    and `build_asha.armpit_helpers` (used by Asha, Rhen and Toma);
  - the solve: `hero_clips.helper_pose`, called from `Skeleton.local_pose`;
  - the parameters: `game/data/characters/helper_bones.json`, shared with the runtime solve
    `game/characters/hero_helper_bones.gd`.
- **Clips:** `hero_clips.build` keys every helper bone the GLB has (`Skeleton.keyed`), so any new clip gets them with
  no extra code. A skeleton without helpers (Sefir, the villagers) gets no extra tracks.
- **Shoulder correctives, `DEF-armpit.L/.R` (every hero):**
  - Each is a copy of the upper arm (head, tail, roll), parented to the shoulder.
  - It turns `share` (0.35) of the upper arm's own turn while the arm comes down, rising to all of it once the arm lifts
    30° above its rest elevation.
  - The underarm skin moves its upper-arm weight onto it: full on the underside, from 0.13 of the arm's length to 0.3,
    fading out by 0.65 (`helper_bones.armpit_share`).
  - Asha's verse-sleeve bag also rides it partly, by how far it hangs below the arm (`hanging_weights`).
- **Skirt panels, `DEF-skirt_<k>` and `DEF-skirt_<k>.001` (Asha):**
  - There are 8 sectors round from the front. Each is a two-bone chain on the hips. It pivots on the outer skirt 7.5 cm
    above the hip joints, and the joint sits 70% of the way to the knees.
  - Skirt cloth below the pivot rides the two nearest chains. Cloth within 1.2–3.5 cm of a leg keeps that leg's
    M1-CHR-14 weights.
  - Per pose, each bone swings out by the least angle that keeps every cloth vertex it carries at its rest distance
    from the leg axes (capped at 8.5 cm, 4 mm slack). The search is 2.5° steps, then bisection.
  - Neighbours may not lag each other by more than 20° per sector.
  - The inner skirt is a convex tube (`asha_costume.convex_radii`): it used to pinch to the centre between the legs.
- **Kept body:** the legs and hips stay whole under the skirts. Only the band above the panels' pivot is cut, because a
  cut edge lower down showed through the open hem. The kept part is decimated to 25% (`UNDER_SKIRT_RATIO`), so LOD0
  is 64,952.
- **Hand-set poses:**
  - `AshaStage` calls `HeroHelperBones.drive(skel)` after `world_pose` or `test_pose`.
  - `rig_probe`'s stage poses do the same (`hero_clips.helper_locals`).
  - The Haluna placeholder pose needs the same call (M2-ENV-14).
  - `test_hero_stage.gd` checks that the runtime solve matches the baked keys within 1°.
- **Host determinism:** Rhen and Toma now use Asha's snaps (midline, UVs, shape-key noise, `PRE_ROUND`). They also put
  every mesh position on a 1 µm grid (`build_asha.snap_positions` / `part_object_snapped`), as Sefir does.
