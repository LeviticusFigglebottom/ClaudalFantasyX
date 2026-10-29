---
id: M3-CRE-659
title: "Act I background villagers: a crowd generator (ADR 0152) and the capsules swapped for it (about 51 people in 10 zones)"
role: character
status: review
owner_session: "creatures (session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-656]
milestone: M3
request-from: lead
---
## Goal
ADR 0041 and ADR 0152. The Lead moved every generic background person shown as a capsule in Act I to creatures.
- Build a parametric crowd generator: body, age, build, outfit by island and role, palette.
- Use real meshes, with idle, walk and work clips, varied enough that no two look cloned.
- Swap the capsules for it.
- Self-render crowd shots in Haluna and view them at walking distance.

## The people (placeholder inventory, 2026-10-28)
- ashcrown: tender
- brightwater_ferry: passenger_child, passenger_reed, trader_a, trader_b
- brine_shoals: brand_girl, clerk, wright_child_a, wright_child_b, wrights (a group)
- coilspire: tender
- corrow: boy, child_a, child_b, child_c, fisher_a, netmender, townsfolk_a, townsfolk_b
- corrow_night: child, mourner_1–4, tender
- haluna_wake: child, fisher, netmender, vendor (Haluna's own villagers; zones/ch04_haluna_wake.json has them)
- oruvel: cook, netmender, netmender_2, pen_child, roof_child
- pemakar: boat_fisher, boat_seller, ferryman_mate, folder, folder_2, forge_child, grave_child, lacquerer, sweeper,
  weir_child
- tamsule: boatman, child, fisher, netmender, trader_boatman, vendor (`board` looks like a notice board: check)
- tamsule_bell_galleries: oruvel_diver_1, oruvel_diver_2, sorrin_diver_1, sorrin_diver_2

## Plan
1. The roster `game/data/world/npc/crowd.json`: each person's zone, role, island, age band, sex, build and seed.
   The island and role ranges come from the story bible (docs/kb/story/bible.md) and palette.json.
2. `assets_src/crowd/`:
   - the generator, which turns the roster into about 20 crowd bodies' params files (the villager schema) plus
     per-person tints;
   - the build wrapper over the characters' villager modules (LOD1 only);
   - the work clips.
3. Runtime: FieldNpc and VillagerLayer apply per-person tints (material overrides).
4. The zone rows, with tests for the variety rule.
5. Self-render the Haluna crowd shots and the zone shots, and view them.

## Done (2026-10-28, creatures)
- **Roster** `game/data/world/npc/crowd.json`: 56 people in 10 zones (the inventory minus Haluna's own four at the
  wake, plus Tamsule's `board`, which **is a person**: the Reefball board-caller of `ch07_bark_board.dlg`, and six
  wrights for Brine Shoals' `wrights` group capsule: W06's "dozen wrights kneel" at a 0.9 m capsule, each with its own
  `offset`). Per person: zone, stage actor, role, community and island (bible §5/§7, the beat sheets), age band, sex,
  build, and the generated body, tints and work clip. Communities: oruvel, sorrin, brightwater, pemakar, corrow,
  tamsule, saltwright, order.
- **Generator** `assets_src/crowd/gen_crowd.py` + `ranges.json` (seeded, `--check`): 22 bodies in the villager
  schema (`assets_src/crowd/params/`): 5 children (one about 13), 10 lay adults (both sexes, lean/medium/heavy), 4
  elders, 2 Order robes; every villager_hair kind; faces rejection-sampled ≥ 0.28 from every Haluna face and from
  each other in a band.
- **Build** `assets_src/crowd/build_crowd.py`: the characters' modules imported unedited, LOD1 only, head maps
  512/256, body 256; jobs `crowd_<body>` in `tools/dev/blender_builds.json`; import rule `crowd`
  (`game/data/import/crowd.json`, `crowd_post_import.gd`, `write_imports.py`).
- **Work clips** `assets_src/crowd/crowd_clips.py`: mend, sweep, carry, fold, haul, kneel_mourn, vigil (each body
  ships the ones its wearers play, plus idle, talk, walk).
- **Runtime**: `NpcTints` (per-instance cloth_a/b/c `col_albedo` and hair `col_root`/`col_tip` overrides), FieldNpc
  `tints` and `tuning_over`, VillagerLayer `crowd` and `offset` rows; zone rows in 10 zone files (`attach: child`).
- **Variety**: no body twice in a zone; a body's wearers dress ≥ 40 sRGB apart (validated ≥ 24); cloth ≥ 55 from
  the wearer's skin; tints are palette swatches or two-swatch mixes (validated).
- Docs: `docs/kb/art/creatures/crowd.md`, `docs/kb/tech/field_npc.md` "Crowd rows".

## Self-render (2026-10-28, lavapipe, no baselines written)
Shots `crowd_lineup_a/b/c`, `crowd_lineup_back`, `crowd_market`, `crowd_work`, `crowd_mourners`, `crowd_zone_*`
(pemakar, brine_shoals, tamsule, corrow_night, corrow, oruvel, bell_galleries). Iterations: the lineup first faced
away (yaw); `mend` spread the hands out sideways (now together over the lap); `vigil` and `fold` hands sat at the
chest (lowered); a laterite-sand trouser read as bare legs (the generator now keeps every cloth ≥ 85 sRGB from the
wearer's skin); the wrights' leg-wrap span was drawn as one number (fixed in ranges.json); two Corrow cameras
reframed. Final: no two people read as clones in the lineups or the market; kneeling mourners and wrights, the
mending pair and the chatting townsfolk read at walking distance. **The Lead writes the baselines** (13 new shots).

## Gates
verify_blender_builds for the 22 crowd jobs: all identical; `tools.tests.test_npc` + `test_blender_builds` 47 OK;
validate_data 0 errors (1 pre-existing warning, haluna shrine_offering); taskboard --check; gdlint and gdformat
clean; Godot `--filter=crowd` 5/0, `villager` 32/0, `field_npc` 10/0.

## Requests to characters (what the crowd could not do without a change in `assets_src/characters/**`)
1. **Saltwright line-marks and the brine-brand** (bible §7; act1_ch06 W06, item 13 "visible line-marks on their
   pushed-up sleeves"): `villager_textures._albedo_villager` paints only Low Reaches reach-bands. Ask: a `_skin.line_marks`
   block (`{"L": n, "R": n, "seed": s, "opacity": o}`: fine parallel lines with node-dots along the forearm, toma_textures'
   `_forearm` frame) and a `_skin.brand` (`{"side": "L", "at": 0..1 along the forearm, "width_m": w}`: a salt-burn
   scar across the marks). The crowd params would then set them on the wright bodies.
2. **A LOD1-only build**: `build_villager.main` always builds, exports and morph-normals LOD0 before LOD1; the crowd
   throws it away (a third of each Blender run). Ask: `_build.lod1_only` (skip the LOD0 export and
   `add_morph_normals`, write only `<npc>_lod1.glb`, or honour `--out` as the LOD1 path).
3. **Module path constants**: `write_materials.write` and `ACTOR`, and `villager_clips.glb_path`/`out_path`, hard-code
   `assets/characters/villagers/`; the crowd re-roots `tables()`' texture paths and monkey-patches `glb_path` from
   outside. Ask: `OUT_ROOT` and `TEX_ROOT` module constants (as villager_textures already has) so a caller sets them.
4. **Hand props** for the work clips (a broom, a basket, a net section, leaf-boats): M3-CRE-614's props, built so any
   villager-schema body can carry one on a hand bone.

## Review log
