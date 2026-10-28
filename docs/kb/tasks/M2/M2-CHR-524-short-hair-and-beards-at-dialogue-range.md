---
id: M2-CHR-524
title: "Short hair and beards at dialogue range: Toma, Kerrid, Moll (no blotches, no hard edges)"
role: character
status: review
owner_session: "characters (worktree hair-wt)"
depends_on: [M2-CHR-515]
milestone: M2
request-from: lead
reviewer: rendering
---
## Goal
ADR 0041, scope item 4: faces at dialogue range. Self-renders of toma_face_neutral, kerrid_face and moll_face show the
short hair (toma_hair's cards on toma_shorthair.png) and the beards as blotchy dark clusters with white flecks, not as
hair. Kerrid's beard also has a hard rectangular notch round the mouth. M1-QA-09 reported Toma's beard edge blotchy on
the PC's GPU, so it is not only the software capture.

## Acceptance criteria
- [x] The cause is found and stated: card size and density, the atlas sampling and mips, the dither, or the region
      masks. (Notes, Cause.)
- [x] Fixed in the character assets and data. A shader change needs Rendering's agreement (ownership.md). No shader
      change: `game/shaders/**` is Rendering's, and none was needed.
- [x] Every rebuilt hero verifies identically on the three numpy paths, and the tests pass.
- [x] Self-rendered and viewed: toma_face_neutral, toma_face_smile, kerrid_face, moll_face and moll_face_yield, plus
      a full-figure shot each.

## Notes (worktree hair-wt, branch chr-hair-wip)

### Cause
Not the dither (30 TAA settle frames resolve it; the capture is one process per shot) and not burial (an exact
closest-triangle probe on toma.glb: 0.1% of card vertices under the skin, median lift 2.2 mm). Diagnostic captures
(hair cards tinted green at alpha_boost 1.15 and 3.0; shadows, SSAO and transmission switched off in turn) showed:
1. **The atlas made every card a blob.** `_sh_column` packed each tuft's strands round the column middle (normal,
   sigma 0.16) at opacity 0.6-1.0. At dialogue range a card is 10-15 px wide, so only the mip average of a column
   shows: a near-opaque core (0.9 x alpha_boost 1.15) with empty sides. Every card drew a dark lozenge.
2. **The cards were shaded far darker than the paint between them.** Card albedo #111013 times root and layer
   occlusion (0.7 x 0.75, meant for long hair's deep layers) against a scalp paint that is lit as skin: dark dots on
   brown. Grey cards (Kerrid's 25-35%, Moll's temples) at full alpha were the white flecks / pale chips.
3. **Each card took its own light.** Its face normal is tilted by its rise and rolled by up to 0.15 rad, so cards
   lit as separate flakes.
4. **Kerrid's notch was the region math.** toma_hair.beard_v's lip clearing was a box whose distance was divided by
   0.02-0.04 (25-50x too steep for a head-height field), and kerrid_hair's trim was a second box over it. The cards
   and the skin's beard shadow (which ramps over 0.026 head heights) both stopped dead on its straight sides.
5. **Moll's scalp paint was lit skin.** The villager path mixed 60% hair paint with *bare* skin, so his scalp read
   ginger between the cards.
6. Also: `toma_shorthair.png` imported with mipmaps off (against the character_shading.md contract). Turning them
   on alone changed nothing visible (out1 vs the old renders), so it was not the blotches, but it is fixed.

### Changes
- `toma_textures._sh_column`: strands spread evenly across the column at opacity 0.45-0.80, soft only in a 0.14
  band at each side (`SH_STRANDS`, `SH_X_MARGIN`, `SH_SIDE_SOFT`, `SH_OPACITY`). Mip alpha is a ragged 0.3-0.7 field.
- `toma_shorthair.png.import`: `mipmaps/generate=true`.
- `toma_hair.surface_normals` (new): the skin's normal under each card vertex, sign-matched to the card's winding
  (the hair shader is double-sided and flips back faces). Used for the scalp cards (build_toma, build_kerrid,
  build_moll) and the beard cards in the Head (build_toma, build_kerrid).
- `toma_hair.mouth_clear` (new): the mouth clearing as a lens in true head heights (edges meet at the corners along
  (1 - (u/a)^2)^0.5, a 2.5 mm wander on the trimmed edge). `beard_v` uses it; `kerrid_hair.beard_v` uses it raised by
  `lip_trim_h` (`TRIM_HALF_W` 1.15). The skin's beard shadow now fades over millimetres into the lip skin.
- Materials (toma, kerrid, moll write_materials): card colour near the paint (Toma/Kerrid Color(0.11, 0.10, 0.10) at the root, was
  #111013), `root_occlusion`/`depth_occlusion` 0.85 (`CROP_AO`), grey cards `alpha_boost` 0.6 (Moll 0.45:
  `GREY_ALPHA`), scalp cards `alpha_boost` 0.85 (`CROP_ALPHA`, Toma and Kerrid; beards keep 1.1).
- Toma `_hair`: 2240 narrower cards (4-6 mm wide; were 1280 at 6-9 mm). Hair+beard 5,560 tris (budget 8,000);
  toma.glb 4,951,260 B, toma_lod1.glb 1,546,752 B (was 1.39 MB; pipeline.md §14 says "under 1.5 MB" for the battle
  LOD: see Left).
- Moll: `villager_textures` gains an opt-in `scalp_shade` (default 0: every villager byte-identical); Moll sets
  Toma's `SCALP_SHADE`. `moll_textures._grey_temples` paints the temple grey into the scalp under the cards.
- Netmender rebuilt: his stubble reads toma_hair.beard_v, so his head albedo moved with the lens (only that file).
- `tools/tests/test_short_hair_dialogue.py` (new): hair/beard textures import with mips; beard_v's slope round the
  mouth is bounded (old code: 50, now under 2).
- pipeline.md §12: a note on short cards at dialogue range.

### Checks
- verify_blender_builds --job toma/kerrid/moll/villager_netmender: native all identical (38/43/40/30 files);
  NPY_DISABLE_CPU_FEATURES=X86_V4 all identical. X86_V3+X86_V4 all identical. The other jobs
  that import the changed modules (villager_neme, osu, child, vendor, reed, fisher, tavi, kell and ysolde, native): all identical.
- Python: test_toma, test_kerrid, test_moll, test_hero_clips, test_short_hair_dialogue, test_character_id_maps,
  TestRigIntegrity{Toma,Kerrid,Moll}: 106 run, OK (8 skips: no braid / no held prop).
- Godot `--filter=post_import` 21/0, `hero_stage` 10/0, `character_shading` 17/0. gdlint, gdformat --check,
  validate_data (0 errors), taskboard --check: clean.
- Screenshots (lavapipe, viewed, not written as baselines): toma_face_neutral/smile 0.0124/0.0125 RMSE against the
  GPU-approved baselines (the change is the hair and beard); toma_front 0.0178 is everywhere on the figure (the
  baseline is a PC GPU render from 265bbcf0 and predates M2-CHR-515's grip), not hair. Kerrid and Moll have no
  baselines; against the pre-task self-renders their front shots change only round the head (RMSE 0.0018/0.0025).

### What the renders show
- Toma: the beard reads as a dense short beard with a fine grain and a soft cheek line; the mouth sits in a soft lens,
  no box; no pale flecks. The crown still shows faint, small, lighter patches where the key catches overlapping cards
  (card value vs the paint under a strong key); much finer and fainter than before, but visible on close inspection.
- Kerrid: the notch is gone (the moustache curves down into the chin beard); hair and beard read as fine cropped hair;
  the grey reads as a light haze at the chin and temples rather than white chips. The grey is quieter than kerrid.md's
  25% / 35% may intend: Art should judge.
- Moll: dark brown cropped hair with a grey haze at the temples, no blotches or chips; a few faint grey specks on the
  crown (`grey_elsewhere` cards).

### Left
- Toma's crown mottling under the strong key (above). Next levers: more scalp cards (size cap allows about 1,000
  more), or Rendering adding a per-strand grey / coverage-to-alpha option to the hair shader.
- toma_lod1.glb is 1.55 MB, over pipeline.md's "under 1.5 MB" battle-LOD note (no test enforces it for Toma). Lower
  `LOD1_RATIO["HairHead"]` for Toma, or accept it.
- Baselines: toma_* shots that show his head (faces, fronts, battle, clips) and the netmender's face need re-approval
  on the PC GPU runner (Lead).
- Moll's fringe still ends in a fairly straight line over the forehead (the hairline card row): a shape note, not part
  of this task.

## Review log
