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

Base mesh: **21,120 triangles** (10,560 quads, 10,562 vertices) for every variant, plus 1,440 for the two eyes. Every face is a quad, the mesh is closed and manifold (the build logs `non-manifold edges 0`), and it is ready for further subdivision.

| Part | Cage (before Catmull-Clark) | Loops |
|---|---|---|
| Torso + neck | 32 around × 18 rings (+ a yoke at the shoulders, tilted rings at the crotch) | Hip, waist, chest, armpit and neck loops |
| Armholes | 2 × 3-cell holes per side → 10-vert arm tube | Armhole loop, shoulder, 4 upper-arm loops, **elbow** loop, 4 forearm loops, **wrist** |
| Legs | The bottom torso ring splits at a crotch vertex into two 18-vert loops (a briefs-line leg loop) | 5 thigh loops, **knee**, 6 shin loops, **ankle** |
| Feet | 12 around × 11 rings, ankle enters through a 4×5-cell hole | Heel and toe caps are 2×4 grids. Toes are a mitten (see weaknesses). |
| Hands | 10-vert palm tube. Four 4-sided finger tubes consume the knuckle end, the thumb grows from the radial side | Rings at **MCP, PIP, DIP** with mid-phalanx rings; fingertips capped with a quad |
| Head | A box lattice (front face 12×12) ray-cast from the head centre. The neck enters an 8×8 hole underneath | **Eyes:** a 3×2-cell block becomes concentric loops (rim, lid margin on the globe, socket inside the globe, capped). **Mouth:** a 4×2-cell block becomes lip border, lip contact line and mouth bag (capped) |

After one subdivision level every loop doubles: eye 20 verts, lip line 24, fingers 8 around, arm 20, leg 36. Poles (valence 3 and 5) sit at the eye and mouth block corners, the armhole corners, the crotch vertex and the finger webs. Those are the conventional places for them, and they are kept away from the main bend lines.

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
| slender (Asha-like) | 1.630 m | 0.222 m | 7.34 | 21,120 |
| athletic (Rhen-like) | 1.770 m | 0.237 m | 7.47 | 21,120 |
| heavy (Toma-like) | 1.890 m | 0.252 m | 7.50 | 21,120 |

## 7. Review scene and shots

`base_body_test.tscn` instances `base_body_stage.tscn` four times, 40 m apart: Slender, SlenderPosed, Athletic and Heavy. Each stage has a three-point light (key spot with shadows, fill, two rims), a grey floor and an enclosing grey cyclorama, plus Front, ThreeQuarter (the body's right side, asha.md's hero angle), Side and Face cameras. The Face camera aims itself at the `DEF-eye` bones. Set `spin_degrees_per_second` on a stage to use it as a turntable by hand.

Shots in `tests/screenshots/shots.json` (432×768, Face 512², 24 settle frames): `base_body_{slender,athletic,heavy}_{front,q34,side}`, `base_body_slender_face` and `base_body_slender_posed`. Captured alone they match bit for bit. Inside a full `capture.sh` run they differ by RMSE ≈ 0.002 (state carried over from earlier shots), well under the 0.008 limit.

## 8. Known weaknesses (honest)

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
