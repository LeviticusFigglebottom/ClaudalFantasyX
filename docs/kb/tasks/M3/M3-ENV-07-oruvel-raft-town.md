---
id: M3-ENV-07
title: "Ch1 Oruvel raft-town (kit at final quality)"
role: environment
status: review
owner_session: "env-art"
depends_on: [M3-ENV-05]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Act I zone kit, filed by env-art after the Lead's M3 queue emptied (the Lead's no-idle directive, 2026-10-24).
Ch1 "Lamp-Diver" from docs/kb/story/beats/act_outline.md, zone `ch01/oruvel`: the raft-town Rhen dives from, lashed hulls and plank bridges over the drowned city, the chandler, the dive raft, morning (colour script `ch01`, 10:30). It replaces the Haluna houses that M3-ENV-06's `oruvel_raft_morning` arena borrows; once it lands, rebuild that arena's town from this kit.

Gameplay placement (spawns, triggers, NPCs, collision tuning) is m2-slice's: hand it over as swap-in notes (below;
docs/kb/handoffs/live/env-art.md is the Lead's to merge).

## Acceptance criteria
- [x] **Design notes first:** `docs/kb/art/environments/oruvel.md` in the haluna.md format (mood in one line, layout
      and orientation, lighting sub-frame and grade from color_script.md, kit table with dimensions, materials against
      palette.json, composed shot list with lenses), reviewed against the act outline, the Ch1 beat sheet, the story
      bible and the sibling oruvel_underway.md before any geometry; references in words only.
      → committed 578cbf25 before any geometry; revised after the preview (its Revisions).
- [x] A procedural kit in `assets_src/environments/kits/oruvel/` with its own Blender job, LOD0/LOD1 within budgets
      and chained per vegetation.md "One LOD at every distance", vertex-colour weathering per haluna.md §4, materials
      written by script, PROVENANCE rows, `verify_blender_builds` byte-identical, every file under 5 MB, no reference
      images, packs or AI generation.
      → 18 pieces, job `oruvel_kit` (threads pinned at 4: the glbs, manifest and materials, 42 files identical), its
      own import category `oruvel_kit` (json + post-import script; KINDS in both post-import tests; a row in
      docs/kb/tech/asset_import.md). No maps of its own (the Haluna maps, read-only).
- [x] An Environment-owned preview scene with composed views of the design notes' key shots, viewed on lavapipe and
      iterated to final quality. At most two baselines.
      → `game/levels/_tests/oruvel_kit/` (8 views, generated); baselines `oruvel_o01_surfacing`,
      `oruvel_o19_dive_mooring`.
- [x] Tests for anything with runtime code; a swap-in note for m2-slice.
      → `tools/tests/test_oruvel_kit.py` (17), `tests/unit/test_oruvel_kit_preview.gd` (5); swap-in note below.
- [x] (From the task's Goal) `oruvel_raft_morning`'s town rebuilt from this kit; its baseline re-approved after viewing.

## Notes
- **Kit** (generators import the Haluna kit's `kit_common.py` and `village.py` (posts, the lintel-gull) read-only;
  the Haluna material writers are loaded by path as `haluna_materials`; no other kit's file edited):
  - Hulls and rafts (`ov_hulls.py`): `hull_outrigger` (6.5 m, float on two booms), `hull_cabin` (10 m, open),
    `raft_deck` (9 × 7 m on three 11 m hulls, deck +0.80), `raft_deck_small` (6 × 5 m on two hulls and four barrels,
    +0.70), `plank_bridge` (6 m, ends at local y 0 = the deck tops), `net_pen` (the Reefball pen / Hullgnaw's arena,
    12 m square, +0.60). Every hull is lapstrake (four lapped strakes), tarred below a boot line that follows the
    laps, its topsides in **one paint slot `ov_hull_paint`** that a placement overrides (HalunaDresser `materials`)
    with `ov_paint_red|ochre|teal|white`.
  - Cabins (`ov_cabins.py`): `cabin_keelroof` (salvaged-plank walls under an upturned 8 m hull; ridge
    `KEELROOF_RIDGE_Y`), `cabin_patched` (lean-to, Lit Age ceramic and brass patches, laundry line), `stall_awning`,
    `lintel_gull_open` (Haluna's crying gull with a bored throat; its lofts turned outward, see Known issues).
  - Heroes (`ov_heroes.py`): `keel_hull` (22 m, three decks, the meeting awning on the old mast, ridge
    `KEEL_HULL_RIDGE`), `chandlery` (Kell's: counter under a short striped awning, lamp racks, oil jars, wick board,
    post shelf, the roof beacon lamp, unlit), `scale_hull` (brass beam scale, chit stamp, Level plaque), `cookboat`
    (stove, tin hood, the knot tally), `dive_raft` (well 1.6 m at the origin, A-frame and block, tether winch,
    ladder to −2.4, lantern rack, lead weights).
  - Props (`ov_props.py`): `net_frame`, `salvage_heap`, `town_far` (80 m and beyond).
  - 23 materials (`ov_materials.py`), none emissive: every lamp is out at 10:30.
- **Triangles, LOD0 / LOD1:** in oruvel.md §2 (as built). Kit on disk: 6.7 MB in 42 files, largest 1.2 MB.
- **oruvel_raft_morning** (M3-ENV-06's arena): `arena_scenes._raft_town` now dresses the town rafts with this kit
  (keel-roof and patched cabins with open-throat gulls facing the sea, net frames, stalls, salvage, outriggers, cabin
  hulls, the far town); the deck (`arena_raft_deck`) and its clutter are unchanged; `battle_arena_oruvel_raft_morning`
  re-approved after viewing (19f2b099).
- **Swap-in for m2-slice** (zone `game/levels/ch01/oruvel/`):
  - Scene: dress with `HalunaDresser` from a layout like `game/levels/_tests/oruvel_kit/oruvel_layout.json`
    (generated by `assets_src/environments/kits/oruvel/ov_preview_layout.py`: copy its placement helpers —
    `on_deck`, `keelroof_cabin`, `bridge` — never reference the `_tests` files from shipped scenes). Kit dir
    `res://assets/environments/kits/oruvel/`. The frame is the Underway's: x east, z south, the sea at y 0.
  - Anchors (world; the layout's `anchors`): the **dive well** over the Underway's tether at (−9.9, 0.75, 5.2) (the
    C1-07 surfacing point and C1-11's mooring); the **neighbour raft** at (−3, 11), yaw −20 (the Underway's
    `hull_keels`, seen from below in U01); the **scale counter** at (6.4, 1.4, −1.0) (C1-08); **Kell's counter** at
    (−36.88, 1.55, −14.0) (C1-10), her **beacon** on the chandlery's roof at about (−38.5, 4.9, −15.8) (lit in the
    drill, C1-12: a light the zone adds, `light_volumetric_fog_energy = 0`); the **keel-hull's meeting deck**
    (−11.5, 1.0, −36.0) (C1-12's drill point); the **net-pen** centre (27.5, 0.6, −11.5) (C1-13/14).
  - Decks: `raft_deck` top +0.80, `raft_deck_small` +0.70, `dive_raft` +0.75, `net_pen` +0.60, `keel_hull` main deck
    +1.0 (roof deck +3.65), `chandlery` +0.5, `scale_hull` +0.4. A bridge spans 6 m between deck edges at the same
    height (`ov_preview_layout.bridge` centres it on a 5–6 m gap).
  - Collision: the kit exports no `-col` proxies. Walkable: each deck as a box at its top; each bridge as a ramp
    (it sags 0.15 m); the keel-hull's decks and ladders. Block: cabins' footprints (keel-roof 3.6 × 5.6 m, patched
    3.6 × 4.2 m), the counters, the dive well (1.6 m square: a fall-through to the Underway's tether is the
    dive's interact), the net-pen's pool (9.2 m).
  - Gulls: every `lintel_gull_open` faces the sea, yaw −70° ± 8° (C1-11's wind comes through their throats); the
    layout puts one on every cabin ridge.
  - Lighting: the preview rig's values are the zone's `ch01` (HalunaMood at sun 58° / 120°, `#FFEFE1` 3.0,
    `oruvel_ch01_environment.tres`, the `lagoon_clear` ×2.0 water); the storm sub-frame is the follow-up below.
- **Follow-ups:** the storm variant (snapped lashings, separating sections, capsized hulls, the net-pen's three-way
  split for Hullgnaw's phase 2: **M3-ENV-07B**, todo); the *Seventh Terrace* (act1_ch01 §9 item 4) and the rebuilt
  `post_credits` variant are not filed yet (oruvel.md §7).
- **Known issues:** the open-throat gull reads as a dark silhouette at O10 and its throat does not read at 85 mm
  from the mooring; the drowned crown under the dive raft does not read through the ×2.0 water at O19's angle; the
  town has no figures and little laundry; the far town is blocky; **the Haluna kit's `village.lintel_gull` lofts are
  wound inside-out** (negative signed volume, so a back-face-culled material shows their inner faces and they render
  dark) — `lintel_gull_open` corrects its own copy; the Haluna gulls are unchanged (a fix for the Haluna kit's
  owner: reverse `_loft`'s winding, then re-approve the Haluna shots it moves).
- Arena lamps and lights near a dense FogVolume set `light_volumetric_fog_energy = 0` (the Lead's rule;
  `tools/tests/test_fog_lamps.py`). This kit adds no lights.

## Review log
