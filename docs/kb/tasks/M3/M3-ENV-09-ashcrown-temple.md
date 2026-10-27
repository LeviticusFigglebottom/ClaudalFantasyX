---
id: M3-ENV-09
title: "Ch5 Ashcrown temple (kit at final quality)"
role: environment
status: review
owner_session: "env-art"
depends_on: [M3-ENV-03]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Act I zone kit, filed by env-art after the Lead's M3 queue emptied (the Lead's no-idle directive, 2026-10-24).
Ch5 "Terraces of Ash" from docs/kb/story/beats/act_outline.md, zone `ch05/ashcrown`: the temple at the crest above Pemakar, at the plume's foot, interior and approach. Match the `ashcrown` skyline massing already in the Pemakar kit (docs/kb/art/environments/pemakar.md), so the distant and near temples are one building.

Gameplay placement (spawns, triggers, NPCs, collision tuning) is m2-slice's: hand it over as swap-in notes.

## Acceptance criteria
- [x] **Design notes first:** `docs/kb/art/environments/<zone>.md` in the haluna.md format (mood in one line,
      layout and orientation, lighting sub-frame and grade from color_script.md, kit table with dimensions,
      materials against palette.json, composed shot list with lenses), reviewed against the act outline and the
      story bible before any geometry; references in words only (references.md).
      → `docs/kb/art/environments/ashcrown.md` (committed 37b322da before any geometry; checked against the act
      outline Ch5, bible §5.2, vowbound.md §2 (Kahre), decisions_log N-09, color_script `ch05` and pemakar.md;
      no Ch5 beat sheet exists yet (M3-C05-01 in progress); revised after the preview, see its §7 and Revisions).
- [x] A procedural kit in `assets_src/environments/kits/<zone>/` with its own Blender job, LOD0/LOD1 within
      budgets and chained per vegetation.md "One LOD at every distance", vertex-colour weathering per haluna.md
      §4, materials written by script, PROVENANCE rows, `verify_blender_builds` byte-identical, every file under
      5 MB, no reference images, packs or AI generation.
      → `assets_src/environments/kits/ashcrown/` (9 pieces), job `ashcrown_kit` (threads pinned at 4; the glbs,
      manifest, maps and materials: 40 files byte-identical), its own import category `ashcrown_kit`.
- [x] An Environment-owned preview scene with composed views of the design notes' key shots, viewed on lavapipe
      and iterated to final quality (pillar 2, the palette, the colour script). Register at most the two most
      telling shots as screenshot baselines (the repo's binary budget).
      → `game/levels/_tests/ashcrown_kit/` (7 composed views + 2 overviews); baselines `ashcrown_a01_approach`,
      `ashcrown_a04_anvil_hall`.
- [x] Tests for anything with runtime code; a swap-in note for m2-slice.
      → `tools/tests/test_ashcrown_kit.py` (22), `tests/unit/test_ashcrown_preview.gd` (5); swap-in note below.

## Notes
- **Same building as the far Ashcrown.** The kit's frame *is* the Pemakar layout's `ashcrown_silhouette` origin
  (`pemakar_skyline.massif_rim_point()`: (0, 306.72, −682) in the Pemakar town's frame; same axes, the temple
  faces south). The seven tiers use the silhouette's numbers exactly (f = 1 − k/8.5, 58 f × 38 f, centre z −1.2 k,
  base y −4, heights 10 then 6, tops 6 … 42), the veins stand where its copper strips are (x = ±0.3 w), the flying
  stair follows its 48° front slab, and the pavilion and spire reach its height (spire tip 64.8 vs 64.2 m); a test
  checks all of it against the silhouette mesh. The materials are the Pemakar kit's stone (its maps) under this
  kit's slot names. What the silhouette leaves out: the forecourt's substructure and the causeway (it floats over
  the 42° lip). **Follow-up for the Pemakar kit (env-art):** swap `ashcrown_silhouette` for this kit's LOD1 pieces
  (`ashcrown_tiers`, `flying_stair`, `crown_pavilion`, `forecourt`, `pilgrim_causeway`) in `pemakar_layout.py`, so
  far and near are one mesh; it re-renders Pemakar's baselines, so it is its own task.
- **Kit** (generators import the Haluna kit's `kit_common.py` and `village.py` (hip roof) and the Pemakar kit's
  `pemakar_common.py` (ash pass) and `pemakar_skyline.py` (massif_height, rim point) read-only; the material writers
  (`haluna/materials.py`) and the Pemakar defaults (`pemakar/pemakar_materials.py`) are loaded by path under their
  own module names; no other kit's file edited):
  - `ashcrown_tiers` (7 tiers; coursed ashlar; plinth courses; chamfered parapet copings; ambulatory paving; the
    veins and channels on one slot per tier `ac_vein_t0` … `t6`, with repair bands; vein stairs; the hall door and
    crater loggia openings), `flying_stair` (172 risers, piers on the court and each ambulatory), `crown_pavilion`
    (8 lacquered posts, three-tier roof with lacquered undersides, copper spire, **the ash crown**: 7 prongs, 3 burned
    short; strike target `ac_temple.strike_target()` ≈ (0, 65.1, −8.4)).
  - `forecourt` (court y −4, z 19 → 45, x ±32; three stepped lower tiers into the slope), `pilgrim_causeway` (101 m).
  - `anvil_hall` (vestibule, nave, crater loggia, ten pillars, lamp brackets, the shaft to the pavilion, the floor
    inlay `ac_vein_floor`), `anvil_altar` (lofted anvil with horn and bands, strike-scar, forge trough).
  - `crest_ground` (the zone's terrain in place of the Pemakar massif: `massif_height` on a polar grid, fine near
    the temple and 1.1 km out to the sea; carved under every floor), `plume_vent` (cinder apron and glowing fissures
    round the plume's foot).
  - Maps (`ac_textures.py`): `ashlar_courses` (2.4 × 1.0 m), `paving_slabs` (2.4 × 1.8 m); the Pemakar kit's
    `volcanic_stone` and `ash_soil` by path. 26 materials (`ac_materials.py`), including `ac_copper_live` (the strike
    state, on no mesh by default) and `ac_plume_day` (the plume's noon parameters). Grade LUT `lut_ch05_ashcrown`
    (`ac_zone_lut.py`).
- **Triangles, LOD0 / LOD1:** anvil_altar 994/30; anvil_hall 4950/12; ashcrown_tiers 25278/154; crest_ground
  40000/5760; crown_pavilion 2876/452; flying_stair 10836/174; forecourt 5950/8; pilgrim_causeway 10010/104;
  plume_vent 2950/352. Budgets in each module's `TRI_BUDGET`. Kit on disk 7.3 MB in 40 files, largest 2.3 MB (`ashcrown_tiers.glb`: the flat-shaded copings carry their own vertices)
  (crest_ground.glb).
- **Swap-in for m2-slice** (zone `game/levels/ch05/ashcrown/`):
  - Scene: every kit piece stands at the zone origin (yaw 0) in the kit's frame; dress with `HalunaDresser` from a
    layout like `game/levels/_tests/ashcrown_kit/ashcrown_layout.json` (generated by
    `assets_src/environments/kits/ashcrown/ac_preview_layout.py`: copy its lists, never reference the `_tests`
    file from shipped scenes). Kit dir `res://assets/environments/kits/ashcrown/`. Give the big pieces a large
    `lod1_from_m` (the layout's `FAR_LOD1_M`: their origin is the temple's, not their middle). Use `crest_ground`
    **instead of** the Pemakar `mountain_massif` (the massif would poke through the hall and the court).
  - Borrowed Pemakar pieces (read-only, already slotted by their import): `ash_plume` at (0, −56.72, −78) with
    `kit_plume` overridden by `ashcrown/materials/ac_plume_day.tres` and LOD1 pushed past 2,500 m; `open_hand_gate`
    at (0, −4, 45.5) scaled 1.6; `lamp_pillar`s along the court's sides and on the causeway's landings.
  - Anchors (kit frame, metres): the **court** is y −4, z 19 … 45, x ±32 (the gate at z 45.5; the flying stair's
    foot at z 39.8; the court piers at z 29, x ±1.6 … 3.0); the **causeway** top landing z 45 … 46.8 at y −4, its
    foot on the slope at z ≈ 146, y ≈ −81 (`ac_approach.causeway_profile()`); the **hall door** x ±2.25, y −4 … 2 in
    tier 0's front (z 19); the **nave** x ±7, z 15 … −16, floor −4, ceiling 8; the **anvil** at (0, −4, −8.4), its
    trough 2.6 m south; the **loggia** balustrade at z −19.2; **ambulatory** k is tier k's top (y 6 + 6k) between
    its edge and tier k + 1's faces; the **vein path** per side: tier k's vein at x = ±0.3 w(k) down its front face,
    the channel along ambulatory k at z mid-way; the **vein stairs** at x = ±(0.3 w(k+1) + 0.6 … + 4.1) against
    tier k + 1's face; the **strike target** at the ash crown, ≈ (0, 65.1, −8.4).
  - The trial: light the path a tier at a time by overriding one vein slot with `ac_copper_live`
    (`ac_vein_t6` at the crown down to `ac_vein_t0`, then `ac_vein_floor` in the hall).
  - The Cinder Matron: the court (64 × 26 m, flat, open to the sky; the stair foot and court piers at its back
    third) is the natural arena; the nave is the alternative.
  - Collision: the kit exports no `-col` proxies. Walkable: the court (a box), the causeway (a ramp per flight,
    the landings as boxes), the flying stair (one ramp at 48°), the ambulatories (boxes), the vein stairs (ramps at
    60°), the hall floor. Block: the parapets (0.8 m), the tier faces, the piers, the pillars, the anvil and its
    plinth, the loggia balustrade, the gate's plinths. The top ambulatory passes under the flying stair with 1.7 m
    of headroom at the axis; block it there or let it be a crawl.
  - Lighting: the preview rig's sub-frames are the zone's (`ch05_temple` outside, `ch05_temple_int` in the hall,
    ashcrown.md §0): keep the Sun's `sky_mode` light-and-sky for `env_sky_low_sun`; the hall wants a ReflectionProbe
    with interior ambient over x ±7.1, y −4 … 8, z −20.3 … 19.3, and the daylight stand-ins until Rendering picks the
    hall's GI. Every lamp keeps `light_volumetric_fog_energy` 0. Set the tide datum to the sea (y −306.72 in this
    frame) or the weathering shader paints a wet line round the crest at y 0.
- **Known limits:** the Pemakar plume is made for 900 m: closer than about 300 m its billows show sharp facets and
  its shaded side reads near-black (a near-plume piece, or a softer close LOD, is a follow-up for Pemakar's plume);
  the tier walls are textured planes (no per-course relief); the lower slope has no detail at distance (A07's
  haze); the dry lightning and the strike are Rendering/VFX's (the kit gives the target and `ac_copper_live`); the
  hall's daylight is stand-in OmniLights.

## Notes
- Arena lamps and lights near a dense FogVolume set `light_volumetric_fog_energy = 0`
  (the Lead's rule; `tools/tests/test_fog_lamps.py`).

## Review log
