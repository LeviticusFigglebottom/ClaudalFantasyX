# Ysolde: build review (M3-CHR-01)

Build: `assets_src/characters/ysolde/build.sh` (Blender about 50 s, textures about 5 min on 4 vCPUs). Sheet:
[`ysolde.md`](ysolde.md). Pipeline: [`pipeline.md`](pipeline.md) §11-§16 (MPFB2 donor, ADR 0021; the hero layout of
§12, as Rhen and Toma: [`rhen_review.md`](rhen_review.md), [`toma_review.md`](toma_review.md)). Shots, all on
`game/levels/_tests/characters/ysolde/` (Asha's stage script and lighting, the body cameras as Toma's):
`ysolde_front`, `ysolde_back`, `ysolde_three_quarter` (the hero angle: her left toward camera, camera
`ThreeQuarterLeft`), `ysolde_face`, `ysolde_face_stylized` (the ADR 0019 dialogue finish and `lid_wide` 0.18 beside
the field finish), `ysolde_silhouette_lineup` (Asha, Rhen, Toma and Ysolde in flat black: no lights, black ambient),
`ysolde_clip_cast_glyph` (0.8 s: the fan open, the second stroke), `ysolde_clip_reink_shell` (1.6 s) and
`ysolde_night_ch4` (a night grade: fog `#22354F`, a cool moon key and a strong cool rim). Nine lavapipe baselines,
each viewed before approval.

## 1. How it is built (what is shared)

| Stage | Ysolde | Shared (imported, nothing copied) |
|---|---|---|
| Body, face, rig, weights | `ysolde_params.json`: every number of ysolde.md §1 and §9 (1.76 m, 7.55 heads, the long oval face, `femininity` 0.95, the Asian-leaning donor mix) | `bb_donor`, `bb_rig`, `build_asha` helpers |
| Host determinism | `MIDLINE_SNAP`, `quantize_uvs` after each unwrap, `snap_shape_noise` on every exported object, `PRE_ROUND` in the texture run (M1-CHR-14), plus her own 1e-6 m midline snap on the head skin and hair (a few coordinates at 1e-9..1e-8 still flipped between numpy's AVX-512 and AVX2 paths) | `build_asha`, `asha_textures` |
| Head UVs | Blender's pack put her rest-of-head island over the corner the teeth are painted into (her temples sampled the teeth). `clear_teeth_corner` tries the four quarter turns of the packed skin islands (rotations keep the tangent handedness), then the smallest shrink; hers takes a 90 degree turn | `asha_mouth.TEETH_UV` |
| Face shapes | the 30 API shapes + 10 visemes; `ysolde_face_poses.json` is ysolde.md §6.2, her rest `brow_outer_up_L` 0.08 added to every row, blend 0.28 s, no overshoot | `asha_face_shapes`, `asha_glb.add_morph_normals` |
| Hair | `ysolde_hair.py`: the villagers' `bun` style moved to the crown (`villager_hair.HairStyle`), 410 back-swept scalp and hairline cards, a 40-ribbon drum knot (11 × 9 cm), the 30-card ash streak on `hair_streak` (no grey card inside it), 6% `hair_grey`, 20 flyaways at the knot only; head-rigid | `asha_hair` cards and atlas, `villager_hair` |
| Costume | `ysolde_costume.py`: gown, trousers, slippers, the bodice, the four panels, sleeves, the left cuff, the cord belt, the collar (its own mesh) | `asha_costume` charts, `rhen_costume` (`torso_sheet`, `limb_tube`, `arm_path`, `leg_path`), `toma_costume` (`_plate`, `_outer_radius`) |
| Rig extras | `DEF-robe_fl/_fr/_bl/_br` (3 each, on the thighs), `DEF-cord_a/_b` (3 each, on the hips), `DEF-book` (on `DEF-hand.R`); 94 joints, the 75 standard ones in their order | `build_toma.add_bones`, `chain_weights`, `polyline_points` |
| Props | `ysolde_props.py`: the 12-panel book with its `book_fan` shape, four ink-guards, the Level-pin, the ring | `asha_mesh` |
| Skin maps | Asha's generator with her knobs and **the villagers' age layer at 0.4** (`villager_textures._albedo_villager`, `_detail_with_age`), ash under the streak | `asha_textures`, `villager_textures` |
| Script | `motifs/glyphs.json` (the Glyph Trace as brush strokes, twelve original letterforms) rendered by `ysolde_motifs.py`: pressure-driven weight 0.8-2.4 mm, tapered entries, pooled corners, a dry-brush break on the fourth stroke; laid out in metres on the garment, so crowded rows and columns only add texels | — |
| Materials | `write_materials.py` (Asha's writer by path): `cloth` and `props` on `character_cloth`, `silver` and `gold` standard metals, three hair materials on Asha's atlas | eye, hair, lash, brow atlases, detail normals |
| Clips | `hero_clips.py`: the `ysolde` persona and ten clips, `book_fan`/`cast_glyph` key the book's shape (a blend-shape track) | `hero_clips` |

The M1-CHR-14 rules as built:
- **The robe** is four lapped panels, not a tube: the front-left panel's edge is the split at 14 degrees left of
  centre and it laps over the front-right one; both front panels end at the side lines over the back sheet, whose
  halves follow their own legs with the left/right blend only across the back seam. Each row is at least as wide as
  the one above (a column), and the hem is 9 cm off the floor. The panels hand over from the hips to the legs below
  the crotch (`panel_weights`, after `skirt_weights`), with 20% at the hem on the panel chains. The knees and shins
  under them are kept.
- **Armholes 12 cm below the shoulder joint** on the side line, for the gown and the bodice. The bodice holds the
  strap's height over the front and back of the shoulder cap (a sleeveless cut there showed skin between it and the
  sleeve) and blends toward the arm's weights only where it lies within 4 cm of the arm (its own gusset). The torso
  skin is cut on the sleeveless line, so nothing opens under those pieces.
- **Dropped-shoulder sleeves** reach in over the shoulder top, are pushed clear of the shipped chest and back skin,
  take the arm's weights and blend 60% toward the torso's within 4 cm of it (the gusset).
- **The collar** rides `DEF-spine.003`/`.004` only. It clears the head skin and hair by 27 mm at a ±40 degree head turn
  and by 46 mm or more at 20 degrees down or 15 up (`test_ysolde.TestCollarClearance`, skinned with the probe).
- **The book** sits 13.1 mm off the nearest hand skin (measured on the mesh, `book_gap`), on its own prop bone.
- **The ink-guards** are rigid on `DEF-f_*.03.L`; the slippers take the feet's weights and are pushed clear of the
  shipped foot and ankle skin (the field is narrower than the donor's foot at the sole's edge).

## 2. Numbers

| | Built | Budget (ysolde.md §8) |
|---|---|---|
| LOD0 triangles | **58,918** (head 20,838 incl. ears, lashes, brows and mouth; body 7,160 incl. the kept shins; eyes 2,216; costume 19,472; collar 1,580; hair 6,168; props 1,484: book 144, guards and ring 1,000, pin 340) | 60,000 (ceiling 70,000) |
| LOD1 triangles | 27,894 (the book copied whole with its shape) | about 28,000 |
| `ysolde.glb` / `ysolde_lod1.glb` | 4.31 MB / 1.27 MB | 5 MB / 1.5 MB |
| Textures | head 2K ×4, body 1K ×4, costume 2K (ORM 1K), props 2K (ORM 1K); largest 3.32 MB (head skinmask) | 5 MB each |
| Reproducible | `verify --job ysolde`: 37 identical, and 37 identical again with `NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4"` | |

Deviations, on purpose or for lack of time: the costume is 19.5k against the sheet's 16k (the panels' crowded rows
and the border's columns), the book only 144 against 3,200 (twelve plain boxes, no bevels or hinge geometry), so the
total still lands under 60k. The gold border's density is 15-37 px/cm across the glyph depending on the island
(the sheet asks for 18): the front-left edge gets the most; the bodice's vertical run about 15.

## 3. Rig guards (`python3 tools/dev/rig_probe.py --hero ysolde --report`, 88 poses)

| Check | Worst | Limit |
|---|---|---|
| Collar in body | 0.0 mm | 3 |
| Book, ink-guards, pin in body | 0.0 mm each | 3 |
| Costume in body | 30.7 mm (run@0, 4 vertices) | **31 / 6 (ratchet)** |
| Skin through garment | 44.6 mm (cast_glyph@16, 67 vertices) | **45 / 70 (ratchet)** |
| Boundary exposed | 4 vertices, 14 mm (talk@18) | **4 (ratchet)** |
| Welded seams (Body+Head, Costume, Collar) | 0.0 mm | 0.5 |
| Skin weights | clean | |

The ratchets and their reasons are in `rig_checks.json` (`_allowances`): the trousers and the back panel fold into
the calf behind the 85 degree knee of the run (under the robe); the armpit under linear skinning (the top of the
upper arm passes the sleeve's gusset with the arm raised forward in `book_fan` and `cast_glyph`, the chest's side
passes it by up to 33 mm in `vigil_book_shut` and `stand_apart`), viewed in `ysolde_clip_cast_glyph` and
`ysolde_clip_reink_shell`, where the sleeve covers it; four upper-arm boundary vertices at the armpit inside the
sleeve's mouth. Lower than Toma's (71 / 200) and Rhen's (63 / 50). `test_rig_integrity.TestRigIntegrityYsolde` covers
her.

## 4. Strict §14 assessment (lavapipe, stage lighting)

**Reads at field and battle range.** In the flat-black lineup she is the one closed column: the collar's headboard,
the knot and pin on the centre line, the book as a block at her right hand, the guard points at her left. She does not
read as any of the other three at 960 px; downscaled to a 128 px figure the column and the knot still carry it, the
guards do not. From the back the collar is a dark headboard the knot rises out of (ysolde.md §2.4). The front-left
border reads as one thin gold line from the collar to the hem, and the hem border as a gold band.

**Close range: passable, not final.**
- **Colour:** under the stage's orange key the robe reads mauve-brown, not indigo-black; in the night grade it is the
  indigo the sheet asks for and the edge holds against the fog with the rim. The value is lighter than the sheet's 70%
  very dark at the stage key. Needs a GPU look and possibly a darker albedo or less sheen.
- **Face:** the long oval and the high cheekbones read; the nose is long. The lids are not visibly hooded (no extra
  shape for it), the age layer is subtle at this range, and the lips read warm and a little full for the sheet's thin
  upper lip.
- **Hair:** a dark, pulled-back mass with a severe hairline and a large drum knot. The cards take the same olive-brown
  sheen as Asha's under the key. **The streak** reads as a flat pale ribbon running from the left temple over the
  crown, too even and too opaque to read as ash worked into hair.
- **Collar:** the white, gold-bordered inner face frames the face as intended. The wings are wide and stiff and read
  more as a funnel than as two curved blades, and from the front the outside is barely visible. Thin dark shards show
  at the bodice's top beside the collar (the bodice rows bunch where they rise over the shoulder).
- **Book:** shut, it is a dark block; open (cast_glyph), the twelve panels fan into a clean arc with the gold glyphs
  readable. At 0.8 s the left hand traces near her chin, above the fan, not in front of it.
- **Feet:** the slippers read as bulky dark shells.
- **Not built or simplified** (see §5): the satin back at the splits (the back layers share the face's UVs), the
  book's bevels and hinges, the turned-back cuff as a real fold (it is a lining-coloured band).

## 5. Known gaps and follow-ups (honest list)
1. `reink_shell` keeps the book in her right hand at the waist; the sheet's open palm on the wall with the book on the
   belt needs a second book attachment (a belt-loop bone or a reparent), not built.
2. The robe's value under warm light (§4); the satin back `mourning_indigo_hi` at the splits and turn-backs.
3. The streak's look; hooded lids (a shape or a crease layer); a thinner upper lip.
4. The collar's wing shape (two curved blades rather than a funnel); the bodice's shards beside it.
5. The proposed swatches (`mourning_indigo`, `mourning_indigo_hi`, `skin_ysolde`, `ash_white`, `silver`) are not in
   `palette.json` (Art Director); Narrative's three open questions (the ring, the ash streak, standing to re-ink) are
   carried with the sheet's defaults (the ring is built).
6. A `face_poses` entry for `sequencer.json` is to be requested from Cinematics; Sefir is not in the lineup (he
   merged after this branch was cut).
7. A combined 40 degree turn and 20 degree downward look brings the jaw to 17 mm of a wing (the clips never do both).
8. GPU capture for the lacquer, the gold and the hair.
