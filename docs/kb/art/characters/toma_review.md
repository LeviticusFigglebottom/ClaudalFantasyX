# Toma: build review (M2-CHR-02)

Build: `assets_src/characters/toma/build.sh` (Blender about 30 s + textures about 4 min on 4 vCPUs). Sheet:
[`toma.md`](toma.md). Pipeline: [`pipeline.md`](pipeline.md) §11-§12 (MPFB2 donor, ADR 0021; laid out like Rhen,
[`rhen_review.md`](rhen_review.md)). Shots: `toma_front`, `toma_q34` (the hero angle: **his left** toward camera,
toma.md §2, camera `ThreeQuarterLeft`), `toma_profile`, `toma_back`, `toma_face_neutral`, `toma_face_smile`, on
`game/levels/_tests/characters/toma/toma_stage.tscn` (Asha's stage script and lighting; the body cameras sit 8 cm higher
and 35 cm further back than Rhen's so the 2.10 m spear and the 1.89 m figure fit the frame).

## 1. How it is built (what is shared)

| Stage | Toma | Shared |
|---|---|---|
| Body, face, rig, weights | `toma_params.json` (the heavy block from `base_body/variants/heavy.json`, male donor mix, a broad square face: jaw 1.10, brow ridge 1.35, nose bridge 1.14) | `bb_donor`, `bb_rig`, `build_asha` helpers |
| Face shapes | the same 32 API shapes + 10 visemes; `toma_face_poses.json` is the toma.md §6 table (brows already at 1.15 range), blend 0.22 s | `asha_face_shapes`, `asha_glb.add_morph_normals` |
| Eyes, lashes, brows, teeth | iris `#2A1A10` in the material | `asha_eyes`, `asha_mouth` |
| Hair | `toma_hair.py`: about 1,200 tiny single-segment cards (8-13 mm, 3.5-6 mm wide) lying along a crown-whorl flow, sampling the thinning tip zone of the atlas columns; scalp shadow at 60% density in the skin albedo; the receding temple line in `hairline_v` | `asha_hair` card machinery and atlas |
| Beard | `toma_hair.beard_cards`: about 920 single-segment cards (11-16 mm) in three lifted layers along the jaw, chin and lip, cheeks clean above the line; 3% `beard_grey` cards, most at the chin. **In the Head object**: every beard vertex takes the shape deltas (and skin weights) of its nearest skin vertex, so `jaw_open`, the smile and the visemes carry it. The beard shadow is painted into the skin albedo with grey flecks at the chin | the Head's blendshapes |
| Costume | `toma_costume.py`: under-tunic (closed body + hip skirt open at his right side), wrapped trousers gathered into shin wraps, the three-wrap indigo sash with the knot at the left front and tails to the knee, harness with bronze buckles, **the five-lame pauldron** | `asha_costume` charts; `rhen_costume` (`torso_sheet`, `limb_tube`, `leg_path`, `bandolier`, `wrapped_sandal`) |
| Props | `toma_props.py`: tide-shield (13 Lloyd-relaxed Voronoi scutes, red lacquer rim, bronze boss, wooden back), placed on his back clear of the costume; hooked spear rigid on `DEF-hand.R` | `asha_mesh` |
| Skin maps | `toma_textures.py`: Asha's generator with knobs, plus the 60% scalp, the beard shadow, deeper lips for `skin_toma`, the faint right-jaw scar, the reach-bands (left 11, right 9; seeded tick codes) and the pale prayer-cord band at the left wrist | `asha_textures.skin_maps` |
| Costume atlas | 2K: salt-yellowed bone tunic, indigo sash with the wave-tick resist stencil on the tails, faded indigo trousers, leather, the lacquer lames with gold piping, the scar strata | — |
| Shield atlas | its own 2K set: tortoiseshell mottling with bone flecks, growth rings, grooves, the lacquer rim | — |
| Materials | `toma/write_materials.py` (Asha's writer, by path); `shield` is a second `character_cloth` material on its own maps; `beard`/`beard_grey`/`hair` matte and windless (`wind_response 0`) | eye, hair, lash, brow atlases, detail normals |

Asha's and Rhen's files are untouched (no new knob was needed).

### The chiselled scar (toma.md §3)
`toma_costume.scar_depth` is one depth field on the top lame's chart: a floor cut below both lacquer layers everywhere
inside a ragged circle (11 cm), random flakes chipped off along the rim, and 52 radial wedge strokes (V-section,
uneven length, width and depth) on top. The mesh is displaced by it and the albedo is painted from it by depth
(red lacquer -> the 0.3 mm black under-layer -> the pale `bone` shell), so the strata agree. There is no emblem in the
data at all, only strokes, and `tools/tests/test_toma.py` checks that no lacquer island survives inside the circle.
The shell is tilted out over the deltoid and turned a little forward so the scar faces the hero three-quarter camera
(it faced the sky at first).

## 2. Numbers

| | Built | Budget (toma.md §8) |
|---|---|---|
| LOD0 triangles | **58,160** (head 20,844 incl. ears, lashes, brows and mouth; beard 1,840; body 6,844; eyes 2,216; costume 18,748 incl. pauldron 5,472; hair 2,400; props 5,268: shield 4,200, spear 1,068) | 66,000 |
| LOD1 triangles | 26,988 | 33,000 |
| `toma.glb` / `toma_lod1.glb` | 4.86 MB / 1.43 MB | 5 MB cap |
| Textures | head 2K ×4, body 1K ×4, costume 2K (ORM 1K), shield 2K (ORM 1K); largest 3.06 MB (head skinmask) | 5 MB cap |

Budget deviations, on purpose: the sheet asks for a 4K costume atlas; a 4K normal map passes the 5 MB blob cap, so the
costume atlas is 2K (the scar gets its own 0.30 × 0.30 island, about 0.5 mm per texel). The beard is lighter than
the sheet's 900 cards × multi-segment (single-segment cards) because its vertices carry all 40 Head morph targets and
the GLB sits close to the cap; the hair and beard together are 4,240 triangles against 8,000.

## 3. Strict §14 assessment (lavapipe, stage lighting)

**Reads at field and battle range.** The silhouette is his: the widest figure in the party, the red pauldron dome
raising and widening the left shoulder with the pale scar as the brightest value on the figure (front, q34 and
profile), a bare right arm with the reach-bands, the indigo sash as the strongest horizontal, the shield's disc showing
past both sides of the torso from the front, and the spear with its hook rising above his head. From the back the
shield is the whole back: a red rim, mottled scutes and the boss.

**Close range: passable for the face shape, not final for hair.**
- Face: broad and square, heavy brow, low wide nose; the donor face takes the heavy male mix well. The eyes and lids
  are Asha's tuned parts. The mouth reads small and a little pursed in three-quarter (the lip sliders), and the
  sheet's crease normal layer at the eye corners (30% always on) is not built.
- Hair: reads as a cropped, dark cap at field range. At the face close-up the cards are visible as small flakes and
  the cap reads brown rather than `hair_black` under the orange key (the 60% scalp paint over the warm skin shows
  through). **Needs a GPU look and a hair pass** (a dedicated short-hair atlas column would help more than more cards).
- Beard: reads as a short full beard with clean cheeks and a moustache, and it moves with the jaw and the smile. Up
  close it is a mosaic of small cards with a few light flecks (the grey cards and highlights); the jaw-line
  silhouette is a little ragged.
- Costume: the tunic, sash and trousers are clean pattern-grid panels. The sash tails hang as stiff flat panels, and
  the stencil on them reads as a ladder of bars at mid range. The sandal soles barely show (Rhen's thin
  `wrapped_sandal` sole; the sheet's reinforced sole is not modelled). The harness passes under the pauldron.
- Pauldron: the dome reads, the lames read as layers below it, the gold piping shows. Seen square-on from the hero
  angle the scar is a pale, chipped patch with the stroke relief visible only up close; it does not read as any
  shape.
- Shield: the dome and the scutes read; the wooden back is plain; the rim lacquer is bright.

## 4. Known gaps and follow-ups (honest list)
1. **Rig extras** from toma.md §9 are not built: sash tails (2 × 4), the pauldron hinge bone, the shield unsling bone
   and the spear prop bone. Everything is on the 75 `DEF-*` bones; the shield is rigid on the chest, the spear on the
   right hand, and the pauldron and sash take transferred skin weights.
2. The eye-corner crease normal layer (30% / 100% under `smile`); the thickened ears.
3. A short-hair atlas (cropped hair and beard reuse Asha's long-strand columns).
4. The sandals' reinforced sole; softer, draped sash tails.
5. **Found in passing, for the shared modules:** `asha_costume._panel` flips its front layer when the grid already faces
   outward, so its front faces point inward and only the back layer (same UVs) is seen (measured here: Toma's pauldron plates, built on the same `grid`, showed their inner face with that test); single-layer pieces built on
   that convention render their inner side. Toma's own pauldron plates use the opposite (correct) test. Not changed
   here (it would change Asha's and Rhen's bytes).
6. A GPU capture from the PC session for the face, hair and lacquer verdict.
