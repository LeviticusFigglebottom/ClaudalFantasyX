# Asha at final fidelity: build notes and the SPEC §14 review (M1-CHR-02)

Owner: Character Artist (character-stream-3). Reviewer: Rendering. Decision: [ADR 0019](../../decisions/0019-character-stylization.md).
Sheet: [`asha.md`](asha.md). Pipeline: [`pipeline.md`](pipeline.md). Shader contract: [`character_shading.md`](../../tech/character_shading.md).

> Every frame below is Forward+ on lavapipe (CPU; ADR 0009) under the M1-RND-04 shading-test lighting: warm key `#FFB87B` 2.4 and dusk rim `#F2A64A` 1.8. There's no screen-space subsurface blur, and nothing here was seen on a GPU.

## 1. Rebuild

```bash
assets_src/characters/asha/build.sh          # ~1 min Blender + ~15 min texture bakes (numpy)
python3 assets_src/characters/asha/sdf_preview.py out.png --look face   # sculpt look-dev in seconds
```

| Stage | File | What it does |
|---|---|---|
| Parameters | `asha_params.json` | The body block (asha.md §1), the face sliders (§6.1 and §9.1: eye tilt 4°, canthus 1 mm, jaw, cheekbones, chin, bridge, tip, lips, corner lift, brow), and the `_hair` and `_costume` blocks |
| Head field | `base_body/bb_face.py` | Lofted head solid, jaw-border cut, soft forms as heightfield terms, nose primitives with the nostrils subtracted, lid solids with the almond aperture cut through |
| Head topology | `base_body/bb_head.py` | A landmark-aligned lattice. Eye blocks hold 6 concentric loops of 32 verts (after subdivision); the mouth block holds 7 loops of 64, including the nasolabial loop. Face mask, scalp and mouth bag are tagged |
| Eyes | `asha_eyes.py` | Eyeball, cornea cap, occlusion shell and tear line per eye, as separate nodes on `DEF-eye.L/R` (origin at the globe centre, +Z gaze); lash ribbons and 3-layer brow cards |
| Ears, mouth | `asha_ears.py`, `asha_mouth.py` | Parametric ear (helix, scapha, antihelix, concha, tragus, lobe); 20 teeth on a dental arch; tongue |
| Hair | `asha_hair.py` | 3 scalp layers flowing from the left part to the braid's gather point; a 3-strand plait (woven tubes) over the left shoulder to the hip; 3 shell clasps; 9 cm tail; flyaways; 2 right-temple strands; the tortoiseshell comb |
| Costume | `asha_costume.py` | Pattern-grid panels ray-cast onto the body (the UVs *are* the pattern): under-bodice, vest with halter cut and back scoop, collar, inner and outer skirt (asymmetric hem, A-line, flare folds), sash with knot and tails, verse-sleeve, wraps, sandals. Hidden body is deleted |
| Staff | `asha_staff.py` | Shaft, brass cage, finial, 5 bell-shells on cords (rigid on `DEF-hand.R`) |
| Face shapes | `asha_face_shapes.py` | The asha.md §6.2 API (30 names: the sheet says "32", but its list adds up to 30) plus 10 visemes |
| Assembly | `build_asha.py` | Rigify rig and bone-heat weights on the welded body; head/body split carrying the welded normals as custom normals; weight transfer to cloth and hair; shape keys; LOD1; glTF |
| Textures | `asha_textures.py` | Skin bake from the sculpt field (normal, cavity, AO, thickness), procedural albedo, iris and sclera, pores, hair and lash atlases, cloth atlas with masks, sleeve set with band-ID map |
| Materials | `write_materials.py` | `assets/characters/asha/materials/*.tres`, named after the glTF materials they replace |

### Review-sweep-B fixes (M1-CHR-01), all done before the blendshapes
- **Loop flow:** concentric orbicularis-oculi and oris loops, a nasolabial loop, and poles only at the block corners (pipeline.md §3).
- **Split normals at seams:** normals are computed on the welded body and exported as custom normals on both the head and body objects, so the head/body cut and every UV seam shade continuously. The jagged line under the jaw came from a fold in the neck bridge, not from normals; the neck hole is now centred under the neck column. A small dark mark at the left trapezius remains on the base bodies. It is geometry near the shoulder-yoke pole (§5), and on Asha it is under the collar.
- **Jaw-underside shelf:** the jaw is now the loft cut by the mandible's lower border (a tilted plane with an 8.5% h fillet), and the head/neck fillet is 2 cm. There's no shelf and no web.
- **Heavy variant reshaped,** and **extreme-pose baseline** added (`asha_extreme_pose`).

## 2. Numbers

| | Triangles |
|---|---|
| Head (skin 11.5k, ears 1.3k, mouth interior 1.1k, lashes and brows 1.0k) | 14,896 |
| Visible body skin (hidden body deleted) | 8,800 |
| Eyes (2 × eyeball, cornea, occlusion, tear line) | 2,216 |
| Costume (vest and collar 3.9k, skirts 6.8k, sleeve 2.5k, sash 0.7k, bodice, wraps, sandals) | 15,288 |
| Hair (scalp 7.9k, braid and tail 4.6k, clasps, flyaways, front strands, comb) | 13,266 |
| Lantern-staff | 2,050 |
| **LOD0 total** | **56,516** (target 63,500; ceiling 70,000) |
| **LOD1** (`asha_lod1.glb`: decimated about 50%, no mouth interior, lashes or flyaways, no blendshapes; staff, sleeve, braid and collar kept) | **26,885** (48%) |

| Textures | Size | Notes |
|---|---|---|
| Head albedo, normal | 2048² | **68 px/cm on the face mask** (target ≥ 50, which asha.md set for 4K); 37 px/cm on the scalp, neck-side and under-jaw island (packed at 0.55×, under the hair). 4K is blocked by ADR 0005 (no LFS) |
| Head ORM, skinmask | 1024² | |
| Body albedo, normal, ORM, skinmask | 1024² | |
| Cloth atlas: albedo, normal, clothmask | 2048² | ORM 1024². About 5 px/cm on the skirt, below the 11 px/cm target until 4K is allowed |
| Sleeve albedo (gauze alpha), normal, clothmask | 1024 × 2048 | Band ID 512² |
| Hair atlas | 2048² | Flow 1024²; lash/brow atlas 1024² |
| Iris, sclera | 512² | Skin pores 512²; thread detail 256² |

Files: `assets/characters/asha/asha.glb` (4.58 MB, under the 5 MB cap; the 40 morph targets with normals take about 2.4 MB, so there is little headroom), `asha_lod1.glb` (1.28 MB), 23 PNGs (2.1 MB the largest, the cloth normal), 19 materials. Rig: 75 `DEF-*` bones (Rigify), bone-heat weights, 0 unweighted vertices.

## 3. Shots (960 × 540, `tests/screenshots/baselines/`)

| Shot | Scene / camera | What to look at |
|---|---|---|
| `asha_front` | `asha_stage` / Front | The full silhouette (asha.md §2.1): the staff 0.32 m over her head, the sleeve flag on her right, the collar, the braid over the left shoulder, the asymmetric hem |
| `asha_q34` | Front-right 45° (the hero angle, §2.2) | Sleeve and staff as one mass with air between them; the lacquer collar; the sash tails |
| `asha_profile` | Her left side | The upright line, the braid as a rope over the front of the shoulder, the bare shoulder, the white under-layer below the blue hem |
| `asha_face_neutral` | Dialogue close-up | Neutral (`mouth_smile` 0.08/0.07): lids, lashes, brows, iris refraction, skin |
| `asha_face_smile` | Same | `smile` (§6.3): the corner lift with the 10% left bias, cheek raise, squint |
| `asha_face_grief` | Same | `grief`: inner brows up, frown and stretch, the jaw parted over the teeth |
| `asha_sleeve_s0` / `asha_sleeve_s4` | Her right, closer | One mesh, one uniform: blank gauze with only the gold cuff ring; then four bands (net-knot, hammer-and-spark, kite-line, root-and-mote) stacked down the sleeve |
| `asha_extreme_pose` | Front | Weight regression gate: left arm overhead, right arm raised with the staff, a 22° spine twist, a 120° left knee |
| `asha_face_stylized_compare` | Two Ashas | SPEC §14 mitigation: as built (left, painterly 0.2) against the ADR 0019 close-range look (right: painterly 0.6, less pore and normal detail, `lid_wide` 0.18) |

The `base_body_*` baselines were rebuilt and re-approved (all 11 looked at): the shared head field and topology changed, and the heavy variant was reshaped.

## 4. The SPEC §14 verdict

**Battle and field range (5 m and beyond, LOD1 from 6 m): passes.** She is unmistakably Asha by silhouette and value (§2, §7). The staff, the sleeve flag, the braid, the collar, the asymmetric hem and the lacquer-and-gold read work exactly as the sheet intends. At battle framing the face is 30–60 px high and the shading carries it: lids, dark irises with refraction, brows, lips and nose read as a young woman's face. Nothing is toy-like.

**Dialogue range (head and shoulders, about 0.6 m): does not pass. She still sits in the uncanny valley,** and I'd rather say so plainly than grade it generously. What works and what doesn't, in order of how much each one costs us:

1. **Skin reads mannequin-smooth and slightly glossy.** The forms are now right (lids with thickness and a crease, a nose with alae and nostrils, lips with a vermilion border and philtrum, a jaw that flows into the neck). But the surface between the features has no life: no asymmetry, no fine creases at the eyes and mouth corners, no colour zoning beyond ±4%. The specular sits on it like a varnish. On lavapipe there is no subsurface blur; a GPU may soften this a little, but not enough.
2. **The face is stiff and slightly gaunt.** The sculpt is a set of numeric terms tuned by eye against previews. It has no reference knowledge of soft-tissue volumes, so the cheek-to-jaw plane is flat and the mouth corners are a little hard. Expressions move the right parts (smile, grief) but read as shapes, not as muscle. In motion this will look worse than in a still.
3. **The scalp hair is the weakest element.** About 330 cards lie flat to the scalp and leave visible card edges and gaps at the crown, and the hairline is a hard line. A sleek drawn-back style is the hardest case for cards. It needs a dedicated hairline card row with a tapered alpha, plus scalp-coloured fine strands.
4. Smaller artifacts:
   - a drawn outline round the alae, where the bake clamps what the mesh can't hold;
   - a faint V at the nasal root, from the side wall of the root and the lid cross-fade;
   - the two right-temple strands are single cards.

**The stylisation mitigation, side by side** (`asha_face_stylized_compare`): painterly 0.6 with less pore and normal detail and slightly wider lids moves her toward "a painted person". It removes some of the waxiness and is clearly the better close-range look. **It mitigates but does not cure** items 1–3: the stiffness and the hair are geometry and authoring, not shading.

**Recommendation (ADR 0019):**
- Ship the close-range stylisation now (`skin_head_dialogue.tres`).
- Keep battle and field framing as built.
- **Escalate SPEC §16 Q2 to the human.** This is the second face review to fail: the M1-CHR-01 base face was the first, so ADR 0010's trigger is met. The question is whether MPFB/MakeHuman may serve as a topology and shape donor behind the existing interfaces. That is the only option that adds the anatomical knowledge the from-scratch sculpt lacks.
- If Q2 is "no", the next step is option 3 of ADR 0019: stronger, explicit stylisation, which needs a SPEC §7.3 change from the Lead.

## 5. Known issues and follow-ups

| Item | Owner | Note |
|---|---|---|
| **Q2: MPFB as a topology and shape donor** | Lead → human | ADR 0010's two-failure trigger is met (ADR 0019) |
| Hairline card row, crown density, tapered-alpha hairline, scalp fine strands | Character | The weakest element at close range |
| Skin albedo colour zones and asymmetry, fine creases (crow's feet, nasolabial, lip lines) in the bake | Character / Art | Makes the painterly look intentional (character_shading.md says the same) |
| **Skirt rig** (asha.md §9.4: skirt 3 rings × 8, sash tails 2 × 4, braid 8, sleeve 6) | Character / Animation | Not built. In `asha_extreme_pose` the raised left knee pushes through the outer skirt, because the skirt is half-weighted to the pelvis. The braid and sleeve follow their nearest body bones |
| Body correctives (elbow, knee, shoulder raise) | Character | Not built. Shape keys alone need a runtime driver, which is a Rendering/Animation call. The extreme pose shows the shoulders and elbows holding volume acceptably at 3 m |
| Sclera vein map is subtle; the caruncle is albedo only | Character | |
| A small dark mark at the left neck/trapezius on the base bodies | Character | Geometry from the yoke pole near the shoulder, not a normal split. Under Asha's collar and vest, so not visible on her |
| GLB headroom: 4.58 MB of 5 MB | Lead | Morph targets with normals take about 2.4 MB. Adding the skirt chain or more shapes needs LFS (ADR 0005) or dropping morph normals |
| Cloth texel density about 5 px/cm on the skirt (target 11) | Art / Lead | 4K atlas blocked by ADR 0005 |
| Hero battle and dialogue scenes into `prewarm_materials.json` | Character | Only the test stage is listed until those scenes exist |
| GPU review of the skin (SSS softness), the hair overdraw and the cornea highlight | QA (M1-QA-01) | Every frame here is lavapipe |
| asha.md §6.2 says "32 shapes"; its own list is 30 names | Art | All 30 are built; fix the count in the sheet |

## 6. M1-CHR-03: rebuilt on the MPFB2 donor topology ([ADR 0021](../../decisions/0021-mpfb2-topology-donor.md))

The human answered SPEC §16 Q2 "yes, as a tool, with heavy modification". The head and body are now MakeHuman's CC0 hm08 mesh, driven through our interfaces (`bb_donor.py`, [`pipeline.md`](pipeline.md) §11). §1–§5 above describe the CHR-02 build. They stay as the record, and this section supersedes their numbers.

**Same lighting and cameras as §3. Every frame is lavapipe.** CHR-02 is on the left (the previous baselines), CHR-03 on the right (the re-approved baselines).

### 6.1 What changed in the build
- **Head:** the donor face (macro mix: female, young, `donor_mix` asian 0.5 / caucasian 0.3 / african 0.2, muscle 0.35, mass 0.22), placed and scaled to the asha.md §1 head canon. Lid margins are re-shaped onto our EyeFrame almond (×1.10 eyes, 4° tilt, 1 mm canthus) and conformed to our 13.2 mm globe. The resting lip parting is 45% closed. Our face sliders were re-tuned against the donor's own form (jaw 0.94, chin 0.95, cheekbones +0.004 h, bridge 0.95, lips 0.9, corner lift 0.8 mm, brow ridge 0.85). One Catmull-Clark level on the face mask and lips. The donor's ears replace the parametric ear.
- **Body:** donor topology with our proportions (RBF fit to the landmarks) and our volumes (the girth fit to the anatomy field). The donor's hands and feet are decimated to 30% for the budget. Skinning uses the donor's hand-made weights, not bone heat.
- **Shapes:** the same 30 + 10 names. Brows, nose sneer, smile, frown, stretch, pucker, upper-lip up and lower-lip down are the donor's expression units, re-targeted. Lids, cheek raise, dimple, press and jaw stay procedural.
- **Textures:** the skin bake no longer samples a sculpt field. AO, cavity and thickness are ray-cast from the mesh per vertex. The normal map is the welded normal plus our detail pass (lid crease, lower-lid line, lip lines). The lip colour follows the donor's vermilion, found by counting face rings from the inner lip loop.
- **Export:** morph-target normals are dropped to stay under 5 MB.

### 6.2 Numbers

| | CHR-02 | CHR-03 |
|---|---|---|
| Head (skin, mouth, lashes, brows, teeth) | 14,896 | 20,996 |
| Visible body skin | 8,800 | 7,358 |
| Eyes / costume / hair / staff | 2,216 / 15,288 / 13,266 / 2,050 | 2,216 / 15,288 / 14,292 / 2,050 |
| **LOD0** | **56,516** | **62,200** (target 63,500, ceiling 70,000) |
| **LOD1** | 26,885 | **29,242** (47%) |
| `asha.glb` | 4.58 MB (with morph normals) | **3.94 MB** (no morph normals) |
| `asha_lod1.glb` | 1.28 MB | 1.37 MB |
| Textures | 23 PNGs | the same 23 PNGs, same sizes (head 2048² albedo and normal, 1024² ORM and skinmask; body 1024²; hair, cloth and sleeve unchanged) |
| Head texel density, whole head skin | (68 px/cm on the face mask only) | 42.9 px/cm averaged over face, scalp, neck and ears. The face island gets the space; the rest is packed at 0.45× |
| Rig | 75 `DEF-*`, bone heat | 75 `DEF-*` (unchanged names), donor weights on 73, 0 unweighted |

### 6.3 The SPEC §14 dialogue-range review, side by side

| | CHR-02 (left) | CHR-03 (right) |
|---|---|---|
| Eyes and lids | Lids drawn on, a wide stare, a hard lid ring | Real upper-lid fold and lower-lid bulge, a lid that covers the top of the iris, an inner canthus. **Reads as an eye** |
| Nose | Alae outlined by the bake, a V at the root | A continuous bridge, rounded tip, alae and nostrils from the topology. **Reads as a nose** |
| Cheeks, jaw, ears | A flat cheek-to-jaw plane, ear partly hidden | Cheek volume, a jaw angle and a real ear (helix, antihelix, concha) |
| Mouth | Thin lips, slit-like | Full lips with a vermilion border. Still the weakest feature: slightly rubbery and heavy in the lower lip, with a dark line where the lips meet |
| Expressions | Smile and grief moved the right places weakly; "shapes, not muscle" | The donor units move the face as muscle does: the smile lifts the corners and bunches the cheeks, the grief brows knit. **Visibly better** |
| Skin | Mannequin-smooth, glossy | Still smooth (no colour zoning beyond ±4%, no fine creases besides the lid lines). The shadow-side cheek shows diagonal banding, which looks like shadow-map acne (also faint in CHR-02) |
| Hair | Weakest element | Unchanged design, now sitting on the donor scalp. Still card-edged at the crown and the part |

**Verdict: passes at dialogue range with the ADR 0019 close-range look; borderline as built.** The face is now a person's face. Structure, eyes, nose, ears and expression motion all moved out of the uncanny valley, and side by side the CHR-02 face reads as a mannequin while the CHR-03 face does not. What is left is surface and the mouth, not anatomy:
1. **The mouth** is the remaining near-miss: lips a little too full and rubbery at rest, the contact line a dark slit. A dedicated lip pass is the first follow-up: the lip rest shape, a contact-line albedo, and dropping `lip_fullness` further.
2. **The skin surface** needs colour zoning and fine creases (the §5 follow-up stands). Without them the as-built shader (painterly 0.2) still reads slightly waxy, and that is why the as-built frame is only borderline. With `skin_head_dialogue.tres` (painterly 0.6, `asha_face_stylized_compare`, right) the waxiness goes, and the face reads as a painted young woman.
3. **Hair** is unchanged and is now clearly the weakest element at close range.

**Recommendation:** keep the ADR 0019 close-range stylisation (painterly 0.6) for dialogue, cinematics and portraits. It is now a finish on a sound face, not a mask over an uncanny one. ADR 0019's option 3 (stronger stylisation, a SPEC §7.3 change) is **not** needed. Next: the lip pass, skin colour zones and creases, then a GPU and motion review (QA, M1-QA-01). Still frames hide what lip-flap and blinks reveal.

### 6.4 Known issues (CHR-03)

| Item | Note |
|---|---|
| Mouth at rest: lips heavy, dark contact slit | First follow-up (lip pass) |
| No morph-target normals | GLB budget (ADR 0005). Expressions shade with the rest normals; revisit with LFS |
| Head texel density 42.9 px/cm average (CHR-02 68 on the face mask) | The donor head carries more skin per island; a face-only 2K map or 4K needs LFS |
| Hands and feet decimated to 30% in LOD0 | Fine at battle range; finger close-ups would want the full donor density |
| Ears at the native donor density | Budget; check on a GPU |
| Base bodies: flattened breasts, shallow heavy torso (girth fit) | Placeholders (SPEC §8.4); pipeline.md §11 |
| Shadow-side diagonal banding on the cheek | Looks like shadow acne on lavapipe; Rendering to confirm |
