# Rhen: build review (M2-CHR-01)

Build: `assets_src/characters/rhen/build.sh` (Blender 28 s + textures about 3 min on 4 vCPUs). Sheet:
[`rhen.md`](rhen.md). Pipeline: [`pipeline.md`](pipeline.md) §11 (MPFB2 donor, ADR 0021). Shots: `rhen_front`,
`rhen_q34` (the hero angle: **his left** toward camera, rhen.md §2, camera `ThreeQuarterLeft`), `rhen_profile`,
`rhen_back`, `rhen_face_neutral`, `rhen_face_smile`, on `game/levels/_tests/characters/rhen/rhen_stage.tscn` (Asha's
stage script and lighting).

## 1. How it is built (what is shared with Asha)

| Stage | Rhen | Shared with Asha |
|---|---|---|
| Body, face, rig, weights | `rhen_params.json` (athletic block, male donor mix, face sliders) | `bb_donor`, `bb_rig`, `build_asha` helpers (imported as a library) |
| Face shapes | the same 32 API shapes + 10 visemes, `rhen_face_poses.json` | `asha_face_shapes`, `asha_glb.add_morph_normals` |
| Eyes, lashes, brows, teeth | — | `asha_eyes`, `asha_mouth` (iris tinted in the material) |
| Hair | `rhen_hair.py`: short cards traced from a crown whorl, a fringe swept to his left, ruffled tufts | `asha_hair` card machinery and atlas layout |
| Costume | `rhen_costume.py`: undershirt, open single-sleeve jacket, stand collar, gauntlet with rivets, trousers, belt and buckle, tether coil, lantern strap, calf wraps, wrapped sandals | `asha_costume` chart helpers (`Fields`, `TorsoChart`, `cast_last`, `_panel`, `limb_wrap`) |
| Props | `rhen_props.py`: lantern (salt-glass globe, brass frame) and two reef-hooks | `asha_mesh` |
| Skin maps | `rhen_textures.py`: Asha's generator with knobs (`PREFIX`, `SKIN_HEX`, `FRECKLES`, `HAIR_UNDERPAINT`), plus sun-peel redness and the reach-band | `asha_textures.skin_maps` |
| Cloth atlas | `rhen_textures.cloth_atlas` (2K): sun-faded teal, Dace's wave stitch, salt tide-marks, oiled leather, rope | — |
| Materials | `rhen/write_materials.py` (Asha's writer, loaded by path) | eye, hair, lash and brow atlases, detail normals |

Asha's own outputs are unchanged by the knobs: `verify_blender_builds.py --job asha` stays byte-identical.

## 2. Numbers

| | Built | Budget (rhen.md §8) |
|---|---|---|
| LOD0 triangles | **57,914** (head 20,872 incl. ears, lashes, brows and mouth; body 6,610; eyes 2,216; costume 16,412; hair 8,784; props 3,020) | 58,500 |
| LOD1 triangles | 27,009 | 30,000 |
| `rhen.glb` / `rhen_lod1.glb` | 4.37 MB / 1.30 MB | 5 MB cap |
| Textures | head 2K ×4, body 1K ×4, cloth 2K (ORM 1K); largest 3.0 MB | 5 MB cap |

The head line is over its own 9,000 sub-budget (the subdivided donor face mask, as on Asha); the body skin, the hair
and the props come in under theirs, so the total fits.

## 3. Strict §14 assessment (lavapipe, stage lighting)

**Reads at field and battle range.** In silhouette he is unmistakable: one dark sleeve and gauntlet on the left, a
bare right arm, the lantern globe breaking the right shoulder line from the front, the coil ring on the left hip, and
the crossed hooks reading as an X from the back. The jacket is visibly short, so the waist and hips read. The sun-fade
on the jacket's shoulders and the salt lines on the trousers show at the full-body shots.

**Close range: passable, not final.**
- Face: the donor face takes the male mix and the sliders well; the eyes, lids and lashes are Asha's tuned parts.
  The neutral mouth reads slightly pursed in three-quarter, with the upper lip pushed forward (lip sliders, not the
  shapes). The crooked smile reads as a smirk, which is on character, but the cheeks barely move (`cheek_raise` 0.40).
- Hair: the fringe now lies across the brow to his left, and the copper tips read. Under the orange key the whole
  mass reads more copper than "dark roots, copper outer 40%"; at the close-up it is still a smooth cap with card
  edges at the temples. **Needs a GPU look and a second hair pass**: more tufts breaking the crown silhouette, and
  darker roots.
- Costume: the jacket, sleeve and gauntlet are clean pattern-grid panels. The trouser seat is boxy (the pelvis band is
  cast from one axis), and the rolled raw armhole edge (rhen.md §9) is not modelled. The sandal soles barely show.
- Lantern: the glass is a simple transparent StandardMaterial3D. The three hairline cracks and the oil-lamp light
  (Godot side) are not done.

## 4. Known gaps and follow-ups (honest list)
1. Rig extras from rhen.md §9 (lantern pendulum, rope coil, jacket hem, sleeve chain) are not built: everything is on
   the 75 `DEF-*` bones, with the props rigid (lantern on the chest, hooks on the hips).
2. Globe cracks in the normal map; the oil-lamp light rig; the jacket's rolled raw armhole edge.
3. **Sheet mismatch, for Art:** rhen.md §6 says `mouth_dimple_R` 0.3 "whenever `mouth_smile` > 0.3", but its table
   gives `soft_smile` a dimple of 0.1 with an R smile of 0.35. The build follows the table.
4. The hero three-quarter angle shows his left (rhen.md §2), which needs a second three-quarter camera
   (`ThreeQuarterLeft`). Asha's stage keeps hers.
5. A GPU capture from the PC session for the face and hair verdict.
