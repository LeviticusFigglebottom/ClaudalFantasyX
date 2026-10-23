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

## 7. M1-CHR-04: close-range polish, the mesh and texture half

The task is split between two sessions. This section covers the lips, the scalp hair and the skin micro-detail, built on this sandbox and rendered on lavapipe. The shadow terminator (cheek banding) and the vest and bodice materials belong to the PC GPU session on `gpu/chr-04-materials`. This section changes neither: no light, shadow or cloth-material setting, and no cloth texture, was touched. The cheek banding visible in the frames below is therefore unchanged.

**Same lighting and cameras as §3. Every frame is lavapipe.** In each comparison, CHR-03 (the previous baselines) is on the left or on top, and CHR-04 (the re-approved baselines) is on the right or below.

### 7.1 What changed and why

**Lips** (`bb_donor.lip_rest`, new `bb_params` sliders that leave the base bodies unchanged at their defaults):
- **The cause of the seam.** QA-05's no-shadow render showed a real gap between the lips. The donor rests with its mouth parted. CHR-03 closed 45% of that through the face warp, at the inner lip loop. That still left a slit to the mouth interior along the whole contact, and shadow darkened it into the line. Raising the warp alone doesn't close it: at 100% a sliver remains, because the subdivided lip surface sits in front of the inner loop.
- **The fix is a seal on the final, subdivided face.** Every vertex of the lip roll is squashed in z toward a smooth contact line. That line is an even polynomial fitted through the inner loop; pinning to the loop's own vertices made the lips wavy at the donor's vertex spacing. The map is monotone (`d → d(1 − k·e^{−(d/3.5 mm)²})`, k = 0.96 < 1), so no surface crosses another, and the inner roll stays behind the contact.
- **The new values:**
  - `lip_close` 0.45 → 0.6;
  - `lip_seal` 0.96;
  - `lip_fullness` 0.9 → 0.8;
  - `lip_lower_fullness` 0.55: the lower lip's forward roll, scaled about the contact plane, with a wide falloff toward the commissures so the corners don't crease.
- **Texture.** CHR-03's dark crease was drawn at the donor's *old* mouth line. The seal moved the lower lip over it, so that crease was QA-05's "dark horizontal line across the lower lip", and it is removed. The bake now gets two per-vertex terms from the seal: `CONTACT` (the line where the lips meet) and `CORNER` (the commissures). The lip colour deepens toward the contact. The contact is a thin line, and the corners are a small shadowed pocket in both albedo and cavity. The vermilion border gets a faint raised roll and a lighter edge. The vertical lip lines are now irregular streaks at a third of the old depth (QA-05's "striations"). Lip roughness went from 0.38 to 0.55.
- **Teeth:** warmer and rougher (0.35 → 0.5). In grief they had mirrored the cool sky and read blue-grey.

**Scalp hair** (`asha_hair`, `asha_textures.hair_atlas`, `build_asha.head_surface`):
- **The cause of the blocks and gaps.** The cards were traced over the anatomy field, which sits up to 11 mm off the donor scalp (11% of the card vertices were inside the skin). So whole patches of cards vanished into the head, and the skin showed between the ones left. Root candidates were also cast from *inside* the head (0.2 h from the centre), so their projection slid to the sides, and the crown got almost no roots.
- **The fix.** Cards now sit on the shipped head mesh itself, through `MeshScalp`: a BVH over the head triangles, with the welded normal interpolated at the closest point. Every card vertex is now 1.0–4.7 mm outside the skin, and all card normals face out. Roots are cast from outside the skull (`ROOT_CAST_H` = 0.6 h).
- **The layout:**
  - a **hairline row** of 100 narrow cards (5–9 mm);
  - base, mid and top layers of 350 / 210 / 85 cards, narrower than before (9–16, 7–13 and 5–10 mm, against 14–33 mm), lifted 1.2 / 2.6 / 4.0 mm, with 8 segments each;
  - half of the top layer on sparse clumps;
  - a narrower comb-away at the part line, which had left a bare wedge.
- **The atlas.** Each of the 16 columns is now 320–420 individual strands (0.6–1.5 px, about 0.1 mm on a card) in 3–5 sub-clumps. Strand density falls to nothing at the column edges, so a card never ends in a hard border, and each strand has its own opacity, lean, wave, length and tip taper. The CHR-03 columns were near-solid rectangles, which is what read as blocks.
  - Columns 12–13 are sparse breakup clumps.
  - Columns 14–15 are hairline clumps whose roots are staggered over the first fifth of V and fainter at the root.
- **The scalp underpaint.** Under the cards, the scalp is painted as hair: dark strands combed along the cards' own flow field (stretched value noise), so any gap reads as hair, not skin. At the hairline the paint breaks into separate strands over about 5 mm. The hairline also wanders by up to about 2.5 mm (`hairline_v`, which the cards, the underpaint and the skin maps all read). The skin under the hair is fully rough, with low cavity, so it does not shine like skin.
- **The braid is kept**, with the same weave and spine. Its tubes and tail use full clumps only, and the middle 60% of a column, because the feathered column edges would show as a bare stripe on a closed tube.

**Skin micro-detail** (`asha_textures.skin_zones`, `detail_height`, `albedo`):
- **Texel density.** The face-mask island is at **69 px/cm** in the 2K head maps; the target is ≥ 50 (asha.md §8.2). The new texel report prints it next to the whole-head average of 43 px/cm. The head ORM and skinmask went from 1K to 2K, because at 1K the pore-scale cavity and roughness averaged away. The skinmask's cavity is stored in 64 levels and its micro-roughness in 32, which keeps it at 3.4 MB, under the 5 MB cap. At 256 levels it was 5.2 MB.
- **Pores** are sparse value-noise pits, about 0.3 mm across and about 0.6 mm apart (finer on the forehead), at 30 µm depth. Their density is highest on the nose and inner cheeks, medium on the forehead and chin, and zero on the lids, the lips and under the hair.
- **Micro-relief:** two crossing families of fine creases, at 12 µm.
- **Soft expression lines** for a young face: crow's feet at the outer canthi and two faint, broken forehead lines.
- **Less waxy specular, from the maps only** (the shader and its 0.42–0.5 roughness range are unchanged):
  - the macro roughness is high (0.9) away from a smaller, broken-up T-zone;
  - roughness varies at 1.5 mm;
  - pores are rougher;
  - cavity carries the pores, lines, lip contact and corners, so the shader's cavity specular occlusion breaks the highlight up.
- **Colour zones:** a warmer flush on the cheeks, nose tip and ears; a cooler, slightly darker ring round the eyes; an olive cast on the upper lip; a low-frequency asymmetry; and pores slightly darker.
- **The ADR 0019 look stays.** `skin_head_dialogue.tres` is unchanged (painterly 0.6, detail 0.35, normal 0.8). The micro-detail reads under it as texture, not as a photographic surface.

### 7.2 Numbers

| | CHR-03 | CHR-04 |
|---|---|---|
| Head (skin, mouth, lashes, brows, teeth) | 20,996 | 20,996 (no topology change) |
| Hair (scalp cards / all) | 14,292 all | 10,132 / **15,528** (budget 16,000) |
| **LOD0** | 62,200 | **63,444** (target 63,500, ceiling 70,000) |
| **LOD1** | 29,242 | **29,862** (47%) |
| `asha.glb` | 3.94 MB | **4.04 MB** (4,036,596 B; cap 5 MB) |
| `asha_lod1.glb` | 1.37 MB | 1.43 MB |
| Head maps | albedo and normal 2K; ORM and skinmask 1K | all four at 2K (albedo 1.93 MB, normal 3.16 MB, ORM 1.36 MB, skinmask 3.38 MB) |
| Hair atlas | 2K, 1.16 MB | 2K, 1.34 MB |
| Rebuild | `verify_blender_builds.py --job asha`: identical | identical (both GLBs); the textures rebuild byte-identically from the same bake |

### 7.3 The SPEC §14 dialogue-range review, side by side with CHR-03

| | CHR-03 | CHR-04 |
|---|---|---|
| Lips, neutral | Heavy, rubbery lower lip; a dark slit showing the mouth interior along the whole contact; a dark crease across the lower lip; strong vertical striations | **Closed**, with a thin natural contact line. Thinner at rest, the lower lip no longer pouts in profile, and the striations have become a quiet texture. No interior shows |
| Lips, smile | Slit and crease as at rest | Corners lift into the cheek and read as corners. A thin parting at the centre is natural for a smile |
| Lips, grief | Teeth blue-grey; slit at the corners | The jaw opens over warmer teeth. The corners and the lower lip read correctly |
| Scalp hair | Rectangular card blocks and bare skin across the crown and the part; a hard hairline | **A continuous, combed-back mass with no blocks or bare patches**, strand-level breakup on the surface, and an uneven, soft hairline. The part shows a narrow line of underpaint, as a real part does |
| Braid | Kept | Kept; slightly more strand texture on the tubes |
| Skin | Smooth, slightly waxy, specular like varnish | Fine pore and crease texture on the cheeks and nose at this framing, a highlight broken up by cavity and roughness, warmer cheeks. Still smooth by photographic standards, which is the intended painterly finish at close range |
| Cheek banding | Present | **Unchanged.** It's a shadow-terminator setting, which the GPU session is handling |

**Verdict: passes at dialogue range as built, and passes clearly with the ADR 0019 close-range look.** The two features that kept CHR-03 borderline are fixed at the asset: the mouth's rest shape and seam, and the hair. Side by side, the CHR-03 hair reads as a cap of blocks and the CHR-04 hair reads as hair.

What still separates her from final fidelity:
1. **The shadow-side cheek banding.** It's the most visible artefact left in these frames, and it's not an asset fault (QA-05). It closes when the GPU session's normal-bias change lands.
2. **The lit hair reads warm brown, not black.** That comes from the hair shader's secondary and transmission lobes under the warm key. It's unchanged here and was the same in CHR-03. A material and shading look for Rendering and Art, to judge on a GPU.
3. **Still frames.** Lip-flap and blinks still need the motion review (ADR 0019 watch item 3).

The micro-detail is near the limit of what a 960 × 540 lavapipe frame can show. The GPU 2× captures (QA-05's method) are the right check for pores.

### 7.4 Re-approved baselines

I re-approved all 10 `asha_*` shots and looked at every one against its CHR-03 baseline. The values are linear RMSE against the old baselines.

| Shot | RMSE against CHR-03 | Why it changed |
|---|---:|---|
| `asha_face_neutral` | 0.0336 | Sealed and thinner lips, with the contact bake; rebuilt scalp hair; skin micro-detail and colour zones |
| `asha_face_smile` | 0.0337 | The same changes, under `smile` |
| `asha_face_grief` | 0.0333 | The same changes, plus warmer teeth |
| `asha_face_stylized_compare` | 0.0402 | The same changes, under both the as-built and the dialogue skin |
| `asha_sleeve_s0` | 0.0098 | The braid and the back of the head are in frame; the sleeve is unchanged |
| `asha_sleeve_s4` | 0.0099 | The braid and the back of the head are in frame; the sleeve is unchanged |
| `asha_front` | 0.0069 (within its limit) | The hair silhouette and surface |
| `asha_q34` | 0.0074 (within its limit) | The hair silhouette and surface |
| `asha_profile` | 0.0071 (within its limit) | The hair silhouette and surface |
| `asha_extreme_pose` | 0.0073 (within its limit) | The hair silhouette and surface |

The four shots still inside their limit were re-approved anyway, so the baselines record the new hair and not a drifted copy of the old one.

### 7.5 Known issues (CHR-04)

| Item | Note |
|---|---|
| Cheek banding and the plastic vest | The GPU session's half (`gpu/chr-04-materials`) |
| A small part-line wedge and a thin gap above the right ear in the card layer | Covered by the underpaint at every shot distance; visible only in a bare-geometry clay view |
| Hair reads warm brown under the warm key | Shading (secondary and transmission lobes); not changed here |
| `asha_hair.Scalp` (the field) is still the default when no mesh is given | `test_asha.test_part_budgets` uses it. `build_asha` always passes the head mesh |
| Face texel density 69 px/cm in 2K; whole head 43 px/cm | 4K is still blocked by ADR 0005 (no LFS) |

## 8. M1-CHR-07: face round 3 (smile driver, lips, hairline, brows, hair colour)

The review-sweep-J progress note on M1-CHR-04 listed what still blocked §14 at dialogue range. This round takes the asset-side items. The cheek and forehead shadow banding, the shadow settings and the cloth, vest and bodice materials belong to the PC GPU session and were not touched. The branch merged the session branch (the PC's `shadow_normal_bias` 2.5 and the vest lacquer values in `write_materials.py`'s cloth row) before the final build, so the frames below include those changes.

**Same lighting and cameras as §3. Every frame is lavapipe.** CHR-04 (the previous baselines) is on the left, CHR-07 (the re-approved baselines) on the right.

### 8.1 The smile driver gap: root cause

The data and the wiring were correct. `asha_face_poses.json` matches asha.md §6.3, AshaStage resolves every entry to `<shape>_L/_R`, and all 40 names are on the Head mesh. The gap was in the shapes and the export:

1. **No morph-target normals.** CHR-03 dropped them to keep `asha.glb` under 5 MB (ADR 0021), because Blender's exporter writes normals for every shape key or for none. Without them, a shape that only bunches smooth skin shades exactly as at rest. The cheek raise and the lid squint changed silhouettes and lid margins only.
2. **The amplitudes were too small to show even as displacement.** At full weight `cheek_raise` peaked at 3.6 mm under a 24 mm falloff, and `lid_squint` lifted the lower lid 2.6 mm. At the smile's 0.45 and 0.25, that is 1.6 mm and 0.65 mm. Measured on the committed GLB, the smile lifted the lower-lid margin 1.63 mm and the cheek 1.45 mm. Rendered alone, `cheek_raise` 0.45 changed 1,406 pixels and `lid_squint` 0.25 changed 1,301.
3. The same audit for every tag (`tools/tests/test_asha_face_drive.py`) found one more dead shape: `jaw_clench` (angry 0.5, determined 0.2). Its depth falloff was centred 7 mm off the masseter, so the 1.5 mm bulge peaked at 0.57 mm.

The fix:
- `asha_glb.add_morph_normals` runs after the export and adds sparse NORMAL deltas to the 30 expression shapes only (+0.53 MB). The visemes stay without them, because the lips' silhouette carries those.
- `cheek_raise` is rebuilt as FACS AU6 at full weight: a 6.5 mm malar lift and 2.8 mm forward, stopped at the nasolabial line so the fold deepens, plus the lower lid pushed up on the globe (−0.22 rad) and a bunched roll under it.
- `lid_squint` (lower lid −0.34 rad, upper +0.10) and `lid_wide` (−0.30) go to FACS scale, and `jaw_clench` gets a 4 mm masseter bulge and a firmer press.
- The emotion weights are unchanged. They are the asha.md API; the shapes at 1.0 are now full intensity.

After: the smile lifts the lower lid **3.28 mm** and the cheek **2.98 mm**, and both now shade.

The new test checks, for every tag and every shape it maps:
- that the shape exists;
- that it moves skin in its expected region (at least 60% of its motion there);
- a full-weight floor and about a pixel (0.33 mm) at the tag's own weight;
- normals on the expression shapes;
- that the smile lifts the lid and the cheek by at least 2.5 mm, and neutral by under 0.2 mm.

On the CHR-04 GLB the test fails 41 checks, on exactly these faults.

### 8.2 What else changed

- **Lips.**
  - The donor's lip face set ran 12–13 mm above the contact and was jagged at its 1.9 mm quads, which read as a soft pink rectangle. The vermilion is now drawn in the frame of the sealed contact line (`bb_donor.lip_rest` exports `lip_dz`, `lip_u` and `lip_front` to the bake).
  - The outline has a cupid's bow: an 18% dip over the philtrum, peaks at a quarter of the half-width, just under the upper lip's front-most ridge, where the donor geometry already has its bow.
  - The colour edge is crisp (±0.35 mm). Outside the upper border there's a lighter white roll and a raised border ridge, and a philtrum groove between two columns sits in the normal map. The lower vermilion is 9 mm (s = 1).
  - **The smile's slit:** the donor corner puller and the smile's `lip_upper_up` 0.10 parted the lips by up to 0.5 mm onto the dark interior. `mouth_smile`, `mouth_frown` and `lip_upper_up` are now sealed at the contact (`seal_contact`), and the smile's parting is 0.13 mm or less. Opening is `jaw_open`'s job; grief and the visemes still open.
- **Brows.** One atlas column of hair strokes per card layer (CHR-02 drew one set of hairs that all three layers sampled, at alpha boost 2.2). The head is upright and fades in, the body's lower rows rise and the upper rows lie down, and the edges feather. Alpha boost is now 1.6. The arch had a step at the lateral third: `sin(π u/0.72)` was back at 0 where the falling branch started at 1. It's smooth now. The lower lashes sample a sparse third of the lash strands.
- **Hairline.**
  - The temples are 0.01–0.02 h lower, so hair frames them. The bare temple silhouette read as a high forehead and, lit from behind, as a pinkish streak.
  - The underpaint transition is about 15 mm with fine, half-transparent first strands; CHR-04's 5 mm ramp drew the hard line.
  - The front hairline is unchanged: lowered, one hairline card rooted on bare forehead and ran down across the brow.
  - The two face-framing strands (asha.md §5) are thinner ribbons on full clumps, fanned apart as a lock.
  - The pale rectangle above the left ear was the tortoiseshell comb, projected 10 mm off the scalp (above the 4 mm top layer) with a mirror clearcoat. It now sits in the hair at 4.5 mm, with a softer finish.
- **Hair colour.** The albedo is on spec: the shader's `col_root` is `hair_black` #201A16, and so is the scalp underpaint. The warm-brown read was the **primary** Kajiya-Kay lobe; lavapipe diagnostics with it off turn the mass dark, while transmission had no visible effect. At exponent 120 on the smooth card shell the band spread over the whole lit side, and under the warm key its #E8D8C8 tint read as a broad gold sheen, which asha.md §5 rules out ("a thin ribbon, never a broad sheen"). The hair material now uses `spec_primary_exponent` 400, `spec_shift_jitter` 0.25 and `indirect_specular` 0.1. That departs from the sheet's exponent 120 and is **for Rendering and Art to confirm on a GPU**.

### 8.3 The SPEC §14 dialogue-range review, side by side with CHR-04

| | CHR-04 (left) | CHR-07 (right) |
|---|---|---|
| Smile | Mouth-only. Lids and cheeks as at rest; a black glossy slit on the shadow side | **The eyes smile.** The lower lids rise and the outer eyes narrow, and the cheeks bunch up against the nasolabial line on both sides. Lips closed, corners up, no slit. The upper face differs from neutral in 3,124 pixels (CHR-04: 1,980). The whole frame differs in 8,535 (CHR-04: 6,497), less than the eyes suggest, because the thinner lips move fewer pixels |
| Grief | Brows knit as heavy bars | The knit reads through the stroke brows, though less forcefully than the bars did. The squint narrows the eyes. The teeth and open jaw are as before |
| Lips, neutral | One swollen, uniformly pink roll; the colour spills onto the skin below | Thinner, with a defined vermilion edge, a cupid's bow and a lighter roll above it. The colour stays on the lip. The bow's shoulders still wobble slightly where the border crosses the donor lip's tubercle relief. The philtrum is too subtle to read at 960×540 |
| Brows | Solid dark bars with blocky ends; a step in the arch | Hair strokes, soft head, feathered edges, smooth arch. The medial head of the left brow is slightly heavy (a dense tuft) |
| Hairline | Hard dark edge over a high bare forehead; bare temples | Softer edge, strand fringe, temples framed. **Still a tight, smooth shell over the crown**: the cards follow the scalp closely, which is the pulled-back style, but at this framing the mass is still more "painted cap" than strands |
| Stray cards | A dark card with a pinkish streak at her right temple; a pale card above the left ear | The comb is seated and dark. The pinkish temple streak is gone. **The framing lock still reads as a thin dark streak down her right temple** in the front-on figure of `asha_face_stylized_compare`. It is in the sheet, but it doesn't yet read as loose hair |
| Hair colour | Warm brown to gold on the lit side | Near-black, with a thinner and broken warm highlight. Slight warmth remains on the lit side under this key |
| Cheek and forehead banding | Strong | Much reduced: the merged PC change, not this task |
| Costume | Glossy | The PC's vest values are merged. Not judged here |

**Verdict: improved, and the smile driver gap is closed. It does not yet pass §14 at dialogue range as built. With the ADR 0019 close-range look it is close, but I would not call it a clean pass on these frames.**

The expression read was the biggest uncanny cue, and it is fixed: the smile now involves the eyes and cheeks. The brows and the lip border were the next most visible faults, and both are fixed at the asset level.

What still keeps it from a clean pass:
1. **The hair mass** still reads as a smooth shell at the crown at this framing, and the face-framing lock reads as a streak, not loose hair. This needs a card-layout pass (lift and clump variation, a less regular top layer), which the 63,500-triangle cap leaves no room for unless triangles come from elsewhere. LOD0 is at exactly 63,500.
2. **The lips** have the right shape and border, but they are thin now. Their shoulders wobble slightly, and the philtrum doesn't read.
3. **Still frames.** Lip-flap, blinks and the smile blend (Cutscene A's smile → stillness → smile) need the motion review (ADR 0019 watch item 3).
4. All of this is lavapipe. The hair lobe change and the morph normals' shading should be confirmed on the GPU 2× captures.

### 8.4 Re-approved baselines

All 10 `asha_*` shots were re-approved. I looked at each one side by side with its CHR-04 baseline. All of them also take the merged `shadow_normal_bias` 2.5, and every shot with the vest in frame takes the merged lacquer values.

| Shot | RMSE against CHR-04 | Why it changed |
|---|---:|---|
| `asha_face_neutral` | 0.0206 | Lip outline and border, brow strokes, hairline and temples, darker hair, seated comb, thinner framing lock; less cheek banding (merged) |
| `asha_face_smile` | 0.0224 | As neutral, plus the smile driver: lid squint, cheek raise with normals, sealed lips |
| `asha_face_grief` | 0.0221 | As neutral, plus the stronger squint; the knit brows as strokes |
| `asha_face_stylized_compare` | 0.0310 | All the face and hair changes under both skins; `soft_smile` now moves lids and cheeks |
| `asha_sleeve_s0` | 0.0083 | Braid, hair and comb in frame; merged shadow bias on the sleeve and bodice. The sleeve is unchanged |
| `asha_sleeve_s4` | 0.0083 | Same; the verse bands are unchanged (checked at full size) |
| `asha_front` | 0.0061 (within its limit) | Hair colour and silhouette, shadow bias |
| `asha_q34` | 0.0054 (within its limit) | Same |
| `asha_profile` | 0.0048 (within its limit) | Same |
| `asha_extreme_pose` | 0.0056 (within its limit) | Same |

### 8.5 Numbers

| | CHR-04 | CHR-07 |
|---|---|---|
| LOD0 | 63,444 | **63,500** (hair 15,584: the lower temple lengthens a few card paths); the target is 63,500 |
| LOD1 | 29,862 | 29,891 |
| `asha.glb` | 4,036,596 B | **4,555,480 B** (morph normals on 30 shapes: 37,563 sparse rows, +525,896 B) |
| `asha_lod1.glb` | 1,427,336 B | 1,429,576 B |
| Head maps | — | albedo 1.94 MB, normal 3.04 MB, ORM 1.34 MB, skinmask 3.29 MB (all under 5 MB) |
| Rebuild | 44 identical | `verify_blender_builds.py --job asha`: **44 identical** (2 GLBs, 23 textures, 19 materials), 327 s |

### 8.6 Known issues (CHR-07)

| Item | Note |
|---|---|
| Hair mass reads as a smooth shell at the crown at dialogue range | Card layout pass; no triangle headroom (LOD0 63,500) |
| The face-framing lock reads as a thin dark streak | Same pass. It's per asha.md §5, but it needs loose-strand behaviour |
| Hair lobe values depart from asha.md §5 (exponent 400, not 120) | For Rendering and Art to confirm on a GPU, then update the sheet or revert |
| Brow head slightly heavy on the left brow | Lower the head-hair density in `brow_hairs` |
| Lips thin; bow shoulders wobble a little | `VERM_UP` and `VERM_DIP` in asha_textures; or smooth the donor tubercle relief under the border |
| One flyaway sticks out sideways near the jaw by the braid | The hair RNG reshuffled with the lower temple; per spec, but a candidate to pin |
| Visemes have no morph normals | GLB cap. The mouth's silhouette carries them; revisit with LFS |
| `seal_contact` keeps the lips together under `lip_upper_up` | Intended for Asha. A hero who must bare teeth without opening the jaw needs it off |

## 9. M1-CHR-09: round 4 (crown card layout, framing lock, lips, the doll-like read)

The task takes the faults still failing in §8.3: the crown shell, the framing-lock streak, the thin lips with wobbly bow shoulders, plus an honest look at why the face reads slightly doll-like. The shadow settings and the cloth, vest and bodice materials belong to the PC GPU session and were not touched; neither were `write_materials.py`'s cloth entries. Every material change goes through `write_materials.py`.

**Same lighting and cameras as §3. Every frame is lavapipe.** CHR-07 (the previous baselines) is the "before", CHR-09 (the re-approved baselines) the "after".

### 9.1 Triangle headroom, without visible loss

LOD0 was at exactly 63,500. `bb_donor.seat_eyes` tucks the deep eye-socket skin to 0.9 R, inside the opaque globe, where no camera can see it. `build_asha.delete_hidden_socket` deletes every head-skin face whose vertices all lie inside 0.95 R of a globe, at rest and under all 40 shape keys. It runs after the bake, so the AO and thickness rays still see a closed socket and the skin maps don't change.
- **1,230 triangles** are freed, and 100 KB of GLB with them, because every head vertex carries 40 morph targets.
- It is invisible: the four face shots rendered before and after differ by at most 1/255 in any channel, in 191 pixels (rounding noise, RMSE 0.00007).
- The hair was rebalanced inside its own 16,000 line (asha.md §8.1). The base layer lies under the mid layer, the clumps and the underpaint, so it is now 230 wider cards (12–20 mm) instead of 350 (9–16 mm). That paid for the crown clumps.

### 9.2 What changed and why

- **Crown** (`asha_hair.crown_clumps`). The CHR-07 top layer sat at one fixed 4 mm lift and followed the scalp exactly, so the outline was a clean arc and the highlight one band. It is replaced by 62 strand clumps:
  - 2–4 narrow cards (4–7 mm) share a traced path and gather toward mid-length;
  - each clump rises off the scalp in an arc (0.8–3.7 mm extra; 18% of them stand another 3–5.5 mm off);
  - each card rolls up to 0.35 rad about its length, so each clump catches its own highlight;
  - 40% of the cards use the sparse breakup columns.
- **Crown flyaways** now stand 4–11 mm off at the tip (CHR-07: 4 mm), so some of them cross the outline. The braid's flyaways start at the shoulder, so the one that stuck out sideways by the jaw is gone.
- **The framing lock** (asha.md §5: two uncut strands, 6–8 cm, free on the right temple).
  - Why it was a streak: CHR-07 rooted it 4.4–5.3 cm off the midline, right above the brow tail, as three 4–5 mm ribbons 4 mm off the skin. From the front that is a dark bar across the brow.
  - Now each strand escapes the drawn-back hair at the temple hairline (53° and 63° round from the front), outside the orbit.
  - Each strand is a fan of 6 ribbons (2.2–3.6 mm) that start together and spread 9 mm toward uneven tips. It hangs 1.5 mm off the skin at the root and 4.5 mm from mid-length, with a slight forward S.
  - The ribbons sample the dense middle of an atlas column. A narrow ribbon over a full column is mostly the column's feathered edges, and the first try was nearly invisible.
  - At 7 mm off the skin, the strands' shadow plus the skin's red penumbra scatter drew a pinkish scratch beside the lock. That is why the lock now hangs closer.
- **Separate random streams** per hair part, so re-laying the scalp no longer reshuffles the braid, the flyaways or the lock.
- **Lips** (`asha_textures`).
  - The cause of the wobble, found by tracing the drawn border on the baked mesh: the outline is the contact line plus the bow height, and the contact line *rises* toward the corners (her resting corner lift). Past each bow peak the outline dipped at 11 mm from the midline, then rose into a second hump at 18 mm. Smoothing the frame per texel, tried first, changed nothing.
  - `monotone_upper` keeps the bow (the dip and both peaks). Outside the peaks, the outline falls from the peak to the corner as a linear-plus-quadratic ramp.
  - The vermilion heights go from 8.8 / 9.0 mm to 9.4 / 9.5 mm (upper / lower). The geometry (`lip_fullness`) is unchanged.
- **The doll-like read**, judged on the asha_face_* shots. Three cues, in order of cost:
  1. **The sclera** was a flat, bright white round a hard-edged iris.
     - The sclera texture now darkens 16% and warms toward the canthi (v 0.12–0.42).
     - `col_sclera` goes from #DCD0C4 to #CCBEB0, and `limbus_softness` from 0.06 to 0.09.
     - The occlusion shell's upper and corner strengths go from 0.75 / 0.55 to 0.9 / 0.7.
     - The iris scale is the sheet's (×1.10, SPEC §7.3) and was not touched.
  2. **A pale band on the upper lid**, margin to crease, read as pale eyeshadow. A diagnostic render with the lashes hidden showed it is the lid skin, not the lashes. Its albedo is now 15% darker and slightly redder. That helps only a little: most of the band is shading (an upward-facing, thin, smooth lid under the key), which is a Rendering question.
  3. **The skin's subsurface warmth.** `skin_head` `curvature_scale` goes from 1.0 to 1.3, which warms the light-to-shadow transitions. I also tried `shadow_scatter` and reverted it. It is a shadow-penumbra term, close to the shadow settings this task must not touch, and it reddened the lock's shadow.

### 9.3 The SPEC §14 dialogue-range review, side by side with CHR-07

| | CHR-07 | CHR-09 |
|---|---|---|
| Crown | A smooth shell: a clean arc of an outline, one broad highlight band | **Strand clumps combed back**, each with its own highlight. Lifted clumps and flyaways break the outline. Still sleek, which is the style |
| Framing lock | A dark bar across the right brow tail (front-on figure of `asha_face_stylized_compare`) | **A loose fan of fine strands at the temple, outside the brow**, with skin between the strands and uneven tips. In `asha_face_neutral` it is a strand line at the temple outline. The lower half is pale where it is backlit, and faint where it crosses the dark wall |
| Lips | Thin; the bow's shoulders scalloped | Slightly fuller. A clean bow (centre dip, two peaks) and smooth shoulders into the corners. No scallops in any of the three expressions |
| Eyes | Flat bright sclera, hard iris edge | The sclera shades and warms toward the corners and sits under the lid's shadow. The iris edge is softer. **Less of a stare**, though still large and glossy, per the sheet's ×1.10 |
| Upper lid | A pale band over the iris | Slightly less pale. **Still visible**; it is mostly shading |
| Skin | Smooth, slightly flat in the transitions | Warmer transitions. Still smooth at this framing; the §7 micro-detail is near the limit of a 960×540 lavapipe frame |

**Verdict: the four named faults are fixed at the asset. The face is less doll-like, but not free of it.**
- **With the ADR 0019 close-range look:** it passes §14 at dialogue range.
- **As built:** it is still borderline. I would not call it a clean pass.

What is left:
1. **The doll cue is now mostly surface and shading:** the pale, evenly lit upper lid, skin that is smooth and evenly lit between the features, and large glossy eyes. The asset levers (albedo, sclera texture, occlusion shell) are used. The rest is for Rendering on a GPU (subsurface blur, the lid's shading) and for the motion review, because blinks and lid motion break a stare in a way a still can't.
2. **The lock** reads as loose hair but is pale in its backlit lower half. It needs a GPU look, plus spring bones (asha.md §5: front strands, 2 bones each, not built).
3. **The crown at the back, and the part,** are not in any close-up shot. They were judged in the field-range shots only.
4. All of this is lavapipe.

### 9.4 Re-approved baselines

Only the four face shots were re-approved. I looked at each one at full size, and in crops, against its CHR-07 baseline. The six field-range shots also change slightly (the crown, the lock, the eyes), but they stay inside their limits, so their baselines were kept.

| Shot | RMSE against CHR-07 | |
|---|---:|---|
| `asha_face_neutral` | 0.0106 | Re-approved: crown clumps, the lock at the temple outline, lips, sclera, lid, skin warmth |
| `asha_face_smile` | 0.0105 | Re-approved: the same under `smile` (the bow stays clean as the corners lift) |
| `asha_face_grief` | 0.0105 | Re-approved: the same under `grief` |
| `asha_face_stylized_compare` | 0.0205 | Re-approved: the same under both skins; the lock is front-on here |
| `asha_q34` | 0.0036 | Within its limit (0.008); kept |
| `asha_extreme_pose` | 0.0028 | Within its limit; kept |
| `asha_sleeve_s0` / `s4` | 0.0027 | Within their limit; kept |
| `asha_front` | 0.0019 | Within its limit; kept |
| `asha_profile` | 0.0018 | Within its limit; kept |

### 9.5 Numbers

| | CHR-07 | CHR-09 |
|---|---|---|
| Head | 20,996 | **19,766** (1,230 hidden socket triangles deleted) |
| Hair, on the mesh scalp | 15,584 | **15,604**. The scalp cards are 9,858: base 230, mid 210, 62 clumps and 100 hairline cards. The lock is 360 and the 48 flyaways 442. On the field scalp, which `test_part_budgets` uses, the hair is 15,824 of 16,000 |
| **LOD0** | 63,500 | **62,290**, 1,210 under the 63,500 target |
| LOD1 | 29,891 | 29,378 |
| `asha.glb` | 4,555,480 B | **4,455,676 B** |
| `asha_lod1.glb` | 1,429,576 B | 1,412,604 B |
| Head maps | albedo 1.94 MB, normal 3.04 MB, ORM 1.34 MB, skinmask 3.29 MB | 1.96 / 3.01 / 1.33 / 3.28 MB, all under 5 MB |

### 9.6 Known issues (CHR-09)

| Item | Note |
|---|---|
| The upper lid reads paler than the cheek | Mostly shading; the albedo there is already 15% darker. For Rendering, on a GPU |
| The lock is pale where it is backlit, and faint against the dark wall | GPU look. Spring bones for the front strands are not built (asha.md §9.4) |
| As built, the skin and the eyes keep a slight doll quality | Surface and shading, plus the motion review (ADR 0019 watch item 3) |
| 1,210 triangles of LOD0 headroom unused | Kept as margin. The hair is at 15,824 of its 16,000 line on the field scalp |
| The left brow's head is slightly heavy (§8.6) | Not taken this round |
| The hair lobe (exponent 400) still departs from asha.md §5 | Unchanged; for Rendering and Art to confirm (§8.2) |
