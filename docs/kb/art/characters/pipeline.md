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
