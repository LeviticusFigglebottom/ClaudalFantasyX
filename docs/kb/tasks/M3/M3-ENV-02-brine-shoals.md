---
id: M3-ENV-02
title: Ch6 Brine Shoals: the route of wrecks and mud-flats, and the burning Saltwright camp (kit at final quality)
role: environment
status: review
owner_session: "env-art"
depends_on: [M2-ENV-06]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The Lead's env-art standing queue (2026-10-24; the human authorised M3 work in parallel): Ch6 "Salt Edict" from
docs/kb/story/beats/act_outline.md, zone `ch06/brine_shoals`. A route of wrecks and mud-flats with a shoal channel deep enough for Sefir's white barge (poled, no wake). The Saltwright salvage camp the Order raid burns: tents, racks, crates, salvage piles, brine-branding gear, and its burned state (smoke, char, embers) as a variant. The tideline where Liss buries a lamp.

Gameplay placement (spawns, triggers, NPCs, collision tuning) is m2-slice's: hand it over as swap-in notes in
docs/kb/handoffs/live/env-art.md.

## Acceptance criteria
- [x] **Design notes first:** `docs/kb/art/environments/<zone>.md` in the haluna.md format (mood in one line,
      layout and orientation, lighting sub-frame and grade from color_script.md, kit table with dimensions,
      materials against palette.json, composed shot list with lenses), reviewed against the act outline and the
      story bible before any geometry; references in words only (references.md).
      → `docs/kb/art/environments/brine_shoals.md` (committed 735a2dfb, before any geometry; revised after the
      preview, see its Revisions).
- [x] A procedural kit in `assets_src/environments/kits/<zone>/` with its own Blender job, LOD0/LOD1 within
      budgets and chained per vegetation.md "One LOD at every distance", vertex-colour weathering per haluna.md
      §4, materials written by script, PROVENANCE rows, `verify_blender_builds` byte-identical, every file under
      5 MB, no reference images, packs or AI generation.
      → `assets_src/environments/kits/brine_shoals/` (28 pieces), job `brine_shoals_kit` (the glbs, manifest,
      maps and materials: 61 files identical), its own import category `brine_shoals_kit`.
- [x] An Environment-owned preview scene with composed views of the design notes' key shots, viewed on lavapipe
      and iterated to final quality (pillar 2, the palette, the colour script). Register at most the two most
      telling shots as screenshot baselines (the repo's binary budget).
      → `game/levels/_tests/brine_shoals_kit/` (8 views); baselines `brine_b01_arrival`, `brine_b05_barge_channel`.
- [x] Tests for anything with runtime code; a swap-in note for m2-slice.
      → `tools/tests/test_brine_shoals_kit.py` (20), `tests/unit/test_brine_shoals_preview.gd` (5); swap-in
      note in docs/kb/handoffs/live/env-art.md.

## Notes
- **Kit** (generators import the Haluna kit's `kit_common.py` and `causeway.py` read-only; no Haluna file edited):
  - Ground: `mudflat_patch_a/b` (24 m cells, edges at y 0), `mudflat_far` (1.2 km apron with a hole for the
    6 × 8 preview block), `channel_straight_a/b` (bulging east / west, zero-slope ends, so any sequence meanders;
    bed −1.6 m, 12 m of water at low water), `camp_hard`, `tideline_wrack`, `lamp_burial` (with the burned
    Saltwright lamp), `plank_walk`.
  - Wrecks: `wreck_hull_section` (listing 28°, planks sprung, mud-filled), `wreck_bow`, `wreck_mast_fallen`,
    `wreck_mast_standing`, `wreck_ribs_large` (the Haluna `wreck_rib` at 1.6×).
  - Camp, intact and burned from one seed: `camp_tent`, `salvage_rack`, `crate_stack`, `salvage_pile`,
    `brine_vat` (+ `_burned`: collapsed frames, per-triangle char and scorch from a seeded char field, canvas
    burned through with charred rims, ember beds in ash on sooted ground). The raid: `branding_brazier`. Story
    props: `liss_crate` (seams leak steady `glimmer_bound`), `white_barge` (12 × 3.4 m, draft 0.5 m, white
    lacquer, red sheer line, tiered red base and gilded bowl-dome finial). `smoke_plume` (for the stand-in shader).
  - Maps (`bs_textures.py`): `mud`, `char` (alligatored), `shingle`. 26 materials (`bs_materials.py`), weathering
    stack per haluna.md §4 (VC R moss, G salt, B wet, A erosion).
- **Triangles, LOD0 / LOD1:** branding_brazier 764/97; brine_vat 2224/36; brine_vat_burned 2144/36;
  camp_hard 3456/160; camp_tent 1856/8; camp_tent_burned 1886/8; channel_straight_a 4608/392;
  channel_straight_b 4608/392; crate_stack 2176/48; crate_stack_burned 2104/48; lamp_burial 440/36;
  liss_crate 732/12; mudflat_far 1824/456; mudflat_patch_a 4608/288; mudflat_patch_b 4608/288; plank_walk 256/12;
  salvage_pile 1644/34; salvage_pile_burned 2354/34; salvage_rack 1896/224; salvage_rack_burned 2240/152;
  smoke_plume 936/60; tideline_wrack 4576/108; white_barge 2544/108; wreck_bow 3162/120;
  wreck_hull_section 4776/116; wreck_mast_fallen 528/54; wreck_mast_standing 419/41; wreck_ribs_large 754/168.
  Budgets in each module's `TRI_BUDGET` (checked by build.py and the tests). Kit on disk: 5.6 MB in 61 files,
  largest 0.6 MB.
- **Shots (lavapipe, 960 × 540), my read:**
  - `brine_b01_arrival` (baseline): flat wet flats, the creeks holding the hazed sky; the walk leads to the
    camp on its pale shingle hard at the right third; three columns lean away into the haze. Darks are the
    wrecks and the char. The smoke reads warm brown looking toward the sun.
  - `brine_b05_barge_channel` (baseline): the strongest frame. The white barge from astern, mirrored in
    still grey-green water, poled toward the burning camp and its dark smoke: the only clean white.
  - B02 route (broken hull and mast stub frame the walk), B03 camp (burned frames, ember beds, one standing
    tent), B07 Liss's crate (steady teal seams on weathered boards), B08 tideline (`ch06_after`: the burned lamp
    in its hole in the strand line, dark wrack), B10 overview, B11 intact/burned pairs: viewed, not registered.
  - Both baselines capture byte-identically twice in a row.
- **Grade:** `brine_shoals_ch06_environment.tres` (ambient `#A8B8B0` at 0.55 as the colour script's fill, exposure
  0.70, haze), `lut_ch06_smoke` (sat ×0.90, greens −25 %, the fire spared, teal toe, amber highlight haze).
  Water: `silted_flats` with foam, detail normals and SSS off (still, so it mirrors: "no wake").
- **Layout changes found in the preview** (recorded in the notes' Revisions): camp on the east bank, hard at
  +1.1 m, raid water −0.15 m, offshore wind toward 240° so the smoke crosses the channel below the camp,
  B05 framed from astern at 65 mm.
- **Swap-in for m2-slice:** docs/kb/handoffs/live/env-art.md, "M3-ENV-02". The preview layout is generated
  (`bs_preview_layout.py`); its heights come from the kit's own height functions.
- **Shared files touched (append-only or by the documented procedure):** assets/PROVENANCE.md (61 rows),
  docs/kb/ownership.md (one row), tools/dev/blender_builds.json (one job), tests/screenshots/shots.json (two
  shots). **Import category** per docs/kb/tech/asset_import.md "A new category": `game/data/import/brine_shoals_kit.json`,
  `game/core/import/brine_shoals_kit_post_import.gd`, `KINDS` in `tools/tests/test_post_import.py` and
  `tests/unit/test_post_import.gd`, a table row in asset_import.md (the Character + Tools row owns these; flagged
  for their review).
- **Requests filed:** M3-RND-21 (Rendering: a volumetric smoke column to replace the stand-in shader).
- **Known limits:** creek rims flash pale from high cameras (B10); tent LOD1 is the two slopes only; the barge has
  no pole-men (characters, Cinematics).

## Review log
