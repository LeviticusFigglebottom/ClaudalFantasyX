# Sefir Aurane: build review (M3-CHR-02)

Build: `assets_src/characters/sefir/build.sh` (Blender about 75 s + textures about 3.5 min on 4 vCPUs, then
`write_materials.py` and `hero_clips.py --hero sefir`). Sheet: [`act1_npcs.md`](act1_npcs.md) §1. Story:
[`sefir_aurane.md`](../../story/characters/sefir_aurane.md), ADR 0017. Pipeline: [`pipeline.md`](pipeline.md) §11-§16,
laid out like Toma ([`toma_review.md`](toma_review.md)). Stage: `game/levels/_tests/characters/sefir/sefir_stage.tscn`
(Asha's stage script and lighting; the face camera at -25 degrees, his right toward camera).

Shots (lavapipe baselines, viewed): `sefir_front` and `sefir_back` (A-pose turnaround), `sefir_three_quarter` (the hero
angle, his right and the mantle toward camera, in his `idle`: hands joined), `sefir_face` (neutral), `sefir_face_stylized`
(standard skin beside ADR 0019's dialogue finish, `soft_smile`), `sefir_silhouette_lineup` (with Toma, Asha and Rhen;
Ysolde is not on this branch yet, see §8) and `sefir_clip_raise_palm` (the Order's gesture, held).

## 1. How it is built (what is shared)

| Stage | Sefir | Shared |
|---|---|---|
| Body, face, rig, weights | `sefir_params.json`: every number of §1.1 and §1.10 (1.88 m, 7.65 heads, a long ageless face). **No asymmetric slider anywhere** (canthus offset 0) | `bb_donor`, `bb_rig`, `build_asha` helpers; host determinism as Asha's (`MIDLINE_SNAP`, `quantize_uvs`, `snap_shape_noise`, `PRE_ROUND`) |
| Face shapes | the 32 API shapes + 10 visemes (all 40); `sefir_face_poses.json` is the §1.6 table, 15 rows, **scalars only** (no left/right pair in any pose), blend 0.40 s, no overshoot | `asha_face_shapes`, `asha_glb.add_morph_normals` |
| Eyes | iris `#6F7E78`, limbal `#4A5652`; the Act II **`sefir_eye_still`** variant is a material pair, `eye_still` + `cornea_still` (cornea roughness 0.008, wet 1.8, highlight clamp 32: a mirror), swapped in by the scene | `asha_eyes` |
| Hair | `sefir_hair.py`: 300 scalp cards combed back off a centre part; the fall is 6 groups behind + 2 in front, **draped**: every card steps down under gravity held on the scalp, then free, kept 1 cm off `avoid()` (the body under its clothes and the mantle's outer face), and each group's strands close up below the head. 10.7k tris. Wind response 0.1 | `asha_hair` atlas and `_ribbon`; `asha_textures` scalp paint through `hairline_v`/`in_hair`/`_gather`/`_flow_dir` |
| Costume | `sefir_costume.py`: under-robe (closed torso, high collar, armholes 12 cm below the joints, wrist-length sleeves, **a gusset under each arm**), trousers, closed slippers, over-robe torso (armholes 13 cm down) and **dropped-shoulder yokes**, and **four robe panels**; the **half-mantle** shell | `asha_costume` charts, `rhen_costume.torso_sheet`/`limb_tube`/`arm_path`/`leg_path`, `toma_costume._plate`/`_shell` |
| Crown | `sefir_props.py`: a spherical cap 34 cm across and 6 cm deep, 3 mm wall, rolled rim, on edge behind the head (concave face `gilt_hi`, back `gilt`), on a band round the occiput and a stem | `asha_mesh` |
| Skin maps | `sefir_textures.py`: Asha's generator with `skin_sefir`, no freckles, no age layer, silver scalp underpaint, a muted rose-brown lip; pores at 0.6 is the materials' detail strength | `asha_textures.skin_maps` |
| Costume atlas | 2K (ORM 1K): ivory silk, ivory leather, plain still-blue satin, and the mantle's **Level scales from `motifs/level_scale.json`** (vector data: shingled discs, ring, bar), at 16.1 px/cm | — |
| Materials | `sefir/write_materials.py` (Asha's writer, by path); `gilt`/`gilt_hi` StandardMaterial3D metals; hair `wind_response 0.1`; cloth sheen 0.45 | eye, hair, lash, brow atlases, detail normals |

No Asha, Rhen or Toma source changed. The one shared edit is `hero_clips.py` (§5).

### The over-robe: four panels, never a tube
From the waist seam down, four panels (`PanelFL/BL/BR/FR`). The front and the back are split at the centre to mid-thigh,
the sides to 6 cm below the hip joints. Above a split the two neighbouring panels share their edge column exactly (one
welded seam: the probe's `seam coincident Costume` stays at 0); below it the upper panel laps 5 degrees past the seam,
lifted 6 mm (left front over right, fronts over backs, left back over right). Each panel takes `build_asha.skirt_weights`
(its own leg), and below its splits up to 30% of a chain of 4 panel bones (`DEF-robe_fl` ... `.003`) that hang from its
leg's thigh; the share is 0 on the seam columns above a split, so a welded seam has one set of weights. Hem 1.5 cm off the
floor. The left panels' spring settings (stiffness 0.8, damping 0.9) are data in the params for the physics pass; no
spring simulation runs in this build. The legs are under full-length trousers, so no shin can come through.

### The half-mantle
`shoulder_shell` (shared by the mantle and the yokes): slices across a guide curve (neck -> shoulder joint -> 9 cm above
the elbow), each a fan of rays cast onto the upper body and the right arm plus the 25 mm clearance and the 5 mm
thickness, the fan's half-angle a smooth curve (132 degrees at the neck, 124 at the shoulder, 102 down the arm), so the
front and back edges come down the chest and the back and rise toward the arm in a curve. Laplacian smoothing, the
pauldron's clearance pass, then the 4 cm flare off the arm. A closed plate (`toma_costume._plate`): 3,082 tris. Weights:
half on its hinge `DEF-mantle` (child of `DEF-shoulder.R`), half on `DEF-spine.003`, the part over the upper arm going over
to `DEF-upper_arm.R` (up to 90% at its lower edge).

## 2. Numbers

| | Built | Budget (§1.9) |
|---|---|---|
| LOD0 | **58,426** (head 20,862 · body skin 3,254 · eyes 2,216 · costume 16,232 · mantle 3,082 · hair 10,672 · crown 2,108) | 62,000 (ceiling 70k) |
| LOD1 | **27,118** (keeps the crown disc, the mantle and the front falls) | about 28k |
| `sefir.glb` | 4.42 MB | < 5 MB |
| `sefir_lod1.glb` | 1.29 MB | — |
| Textures | 12 PNGs, largest 3.04 MB (`sefir_head_skinmask.png`) | < 5 MB each |
| Bones | 75 standard + 58 extras (robe 16, mantle 1, crown 1, hair 40) | §1.10 |
| Mantle scales | 1,351 Level scales (the sheet guessed 900: the shell is larger than its estimate), 16.1 px/cm | >= 16 px/cm |

The costume is over the sheet's split (4.0k + 9.5k): the yokes and gussets (2.1k) were not in it, and the panels are
4.4k, not 9.5k. Under the LOD0 target overall.

## 3. The gold budget (the sheet's open point, decided here)

Measured by geometry: the posed GLB (idle) rasterised with flat ids, gold = the crown's pixels + the mantle's pixels x
the mantle's gold share, in a 16:9 waist-up frame (waist to the top of the crown):

| Framing | Crown | Mantle (area) | Gold at 40% (sheet option b) | **Gold at 14% (built)** |
|---|---|---|---|---|
| Front, waist-up | 4.38% | 4.18% | 6.05% | **4.96%** |
| Hero three-quarter, waist-up | 3.65% | 5.69% | 5.93% | **4.45%** |
| Profile, waist-up | 1.34% | 5.73% | 3.63% | 2.14% |
| Front, chest-up | 8.26% | 5.90% | 10.6% | 9.08% |
| Three-quarter, chest-up | 6.84% | 7.88% | 9.99% | 7.94% |

The sheet's option (b), 40% mantle gold, does not reach 5%: the crown's disc alone is 3.7-4.4% of a waist-up frame. The
mantle's gold is lowered instead of claiming an exception: **14% of the mantle** (`mantle_gold_coverage`, the scales'
ring width solved to it: ring 0.044 x the radius, bar 0.06, no rim, a 5 mm gold edge instead of the sheet's 1 cm). The
mantle now reads as black lacquer with fine gold Level line-work rather than a solid gold shell. `test_sefir` checks the
two waist-up framings stay at or under 5% and the clothmask's mantle gold is 14%. **Chest-up close-ups are 8-9% gold
and the crown is most of it**; no mantle setting fixes that. Cinematics should frame his close-ups waist-up or wider, or
the Art Director decides an exception for the crown in close-up (this build claims none).

## 4. Rig guards (`rig_probe --hero sefir --report`, 65 poses)

| Check | Worst | Limit |
|---|---|---|
| garment_in_body Costume | 2.98 mm (walk_glide, a trouser hem against the shin) | 3.0 |
| garment_in_body Mantle | 0.0 | 3.0 |
| garment_in_body HairBack | 0.0 | 3.0 |
| prop_in_body Crown | 0.0 | 3.0 |
| skin_through_garment Body | 0.37 mm | 3.0 |
| boundary exposed | 0 of 169 | 0 |
| seams coincident (Body+Head, Costume, Mantle) | 0.0 | 0.5 |
| weights | 0.0 | 0.001 |

**No ratchet**: every check passes at the default limits (`rig_checks.json` `sefir` has no allowance). What got it there:
the whole arm's skin and the torso skin within 11 cm of each shoulder joint are deleted (they are under the sleeve, the
yoke and the gusset; kept, they came through the cloth as the arm hung), and the gussets ride the torso so the armhole is
closed when the arm comes up (raise_palm left 5 boundary vertices open without them). The Costume's 2.98 mm is close to
its limit: a later costume change can tip it.

Also in `test_sefir` (posed on the committed GLB with the probe's skinning): the crown clears the mantle by at least
**39.7 mm** across head pitch -20 degrees and yaw +-40 degrees (the worst is pitch -20 with yaw +40, the bowl's lower rim
over the mantle; the crown was raised to 8.2 cm over the head centre and its band shortened to get there); and no hair
vertex is inside the mantle (winding number) at rest and through `glance`, `incline_head`, `raise_palm` and `talk`.

### Reproducibility
Job `sefir` (threads 4): `verify_blender_builds --job sefir` is 32 identical, and 32 identical again with numpy's AVX2
path (`NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4"`). Beyond Asha's M1-CHR-14 helpers, every mesh position is rounded to a
1 µm grid (`POS_GRID`; the donor's near-midline coordinates differed by a few ULP between SIMD paths) and the hair drape's
state to 10 µm each step (`DRAPE_GRID`; the iteration amplified ULP noise to a micron by the tips).

## 5. Clips and persona (hero_clips.py)

`PERSONA["sefir"] = {"sway": 0, "lean": 0, "staff": False, "arms_down": 30, "breath": 0, "hands_joined": True}` and
`CLIPS["sefir"]`, in a block of their own after `LENGTHS`; `pose_at` dispatches a `hands_joined` persona to
`sefir_pose_at`, so the shared clips are untouched (Asha's, Rhen's and Toma's libraries are byte-identical, checked by
regenerating them and by `test_hero_clips`). Ysolde's persona keys can merge beside it without a conflict: his `breath` is
read only inside his own clips.

| Clip | Loop | What it does |
|---|---|---|
| `idle` | yes | The joined pose, held: zero rotation delta across its keys (tested). **Intended: do not fix it.** |
| `talk` | yes | The left hand parts from the right and opens 10 degrees once per loop; the head under a degree |
| `raise_palm` | no | The left palm up flat to chest height in 0.6 s, held, lowered over 2.4 s (4.5 s) |
| `incline_head` | no | A 10 degree bow and a 3 degree tilt, held 1 s, up over 0.8 s |
| `glance` | no | Head 22 degrees to his left and back; the body does not follow (eyes are not keyed by body clips) |
| `pivot` | no | 30 degrees in place on the heels, no step, no bob; the arm turns are carried round with the body (`sefir_turned`), so the hands stay joined |
| `walk_glide` | yes | Ch13 (specified now): a 14 degree stride, no bob, hips level, no arm swing |

The joined hands were solved on his skeleton: wrists 6-7 cm in front of the robe at the navel, 14 cm apart, the right
forearm a little higher and 2.5 cm further forward, so the right hand lies over the left.

## 6. Honest assessment (SPEC §14)

What reads: the silhouette is the sheet's. In the lineup he is the tallest, palest figure and the only one with a disc
behind the head; the heavy right shoulder against the bare left is clear at a glance, and the column of the robe reads
plumb. The hands-joined idle is still in the way the story wants. The face is clean and symmetric.

What still looks wrong:
- **The scalp hair reads as a smooth cap** close up (a hard pale edge at the forehead, little strand break-up on top).
  The fall and the front lengths read better; the front lengths are thin strands rather than two full locks.
- **The over-robe's blue is near grey-white under the stage's warm key.** The atlas is `#8EB2C6` (the sheet's proposed
  `#9FBCC8` read white; I moved it a step bluer) and the cloth sheen is lowered to 0.45. It reads pale blue in the lineup
  and under cooler light; the Art Director should confirm the swatch under the Ch6 lighting.
- **The mantle is now mostly black lacquer** (§3): the gold line-work reads at mid range, but it is no longer the "gold
  shell" of the sheet's one-line read. This is the cost of the 5% budget with the crown as large as it is.
- The waist seam of the over-robe (torso over skirt) is a visible horizontal line, and the robe torso's surface has some
  faceting at the chest at close range.
- From behind, the crown's convex back is a strong specular disc that hides the head.
- `raise_palm`'s palm comes up a little higher than chest height, close to the chin, at the held key.
- The yokes are a design addition (the sheet's over-robe has no stated shoulder): without them the shoulder tops showed
  skin between the armholes and the collar.

## 7. Follow-ups
- Hair: scalp break-up (more clumps, a soft-root hairline row as Asha's), fuller front locks.
- The spring simulation for the robe panels and the hair chains (the parameters are in the params, unused).
- Cinematics M3-CIN-01 (his slow blink, face poses, blend); Rendering M3-RND-03 (the still reflection and the too-sharp
  shadow); Environment M3-ENV-1000 (the barge without a wake).
- Add Ysolde to `sefir_lineup.tscn` once M3-CHR-01 merges (the white figure and the black one), and re-approve the
  `sefir_silhouette_lineup` baseline.
- The battle actor (Act III final boss) on `sefir_lod1.glb`.
