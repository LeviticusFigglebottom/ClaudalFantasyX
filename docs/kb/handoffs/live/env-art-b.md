# Live log: env-art-b environment

Environment-art track B, cloud session `session_01F3vrUNt6trAMrjeYavaDNC`, branch `claude/env-art-b` (cut from the
integration branch `claude/undertow-lead-handoff-ze8rrn` on 2026-10-28). **This environment owns this file**
(CLAUDE.md §7a). The Lead is `session_018aiGwGLGkxsnMnu8VfCu1m`.

## Scope (ADR 0041, the Lead's brief of 2026-10-28)
The Act I zones of Ch5–Ch9 (`game/levels/ch05..ch09`) and the battle arenas those chapters use, at final quality:
dressed, lit, walkable and seamless, with no greybox geometry or material and no box stand-ins. env-art keeps the
Prologue–Ch4 zones and the shared kits; act1-chapters keeps the story (layouts' marks, triggers, states, scripts,
dialogue, casts). Claims: the last row of `docs/kb/ownership.md`.

## How this branch is built (read first when merging)
- **It carries two unmerged track heads**, because Ch5–Ch9's dressing and kits live there and building beside them
  would only make conflicts:
  - `claude/act1-chapters` @ 47de5a00: every Act I commit up to Ch6's last pieces (M3-C05-1213 Pemakar,
    M3-C07-1211 the galleries, M3-C08-1210 Coilspire, M3-C09-1209 Ch9, the casts, the walks). Nothing of its Act II
    (Ch10+) work.
  - `claude/env-art` @ 9cced155 (its head at 01:14): the Ch5 Pemakar pieces (M3-ENV-1214), the Tamsule port kit
    (M3-C07-04), the Ch8 arenas (M3-ENV-713), Ashcrown's flights (M3-ENV-715), and its paused later-act work.
  Merging this branch brings both in; their own heads merge cleanly on top afterwards.
- **Not applied here:** battle-presentation's `M3-BPR-407-seawall-repoint.patch` (the Ch8 encounters onto env-art's
  seawall/coilspire arenas). It is theirs, and the Lead applies it after env-art. Until then the Ch8 fights still
  load `wall_head_storm` (the greybox).

## RESOLVED (Lead, 2026-10-28): env-art-b's Ch5–Ch9 dressing wins; act1-chapters keeps Ch4 and merges this branch
The ownership row says so (8240c0e0). The table below is kept for the merge.

### Was: act1-chapters dressed the same zones in parallel (found 2026-10-28)
`claude/act1-chapters` (up to 0737523e, 02:16 UTC) dressed Ch5–Ch9 zones on 10-28 under its older ownership row
(`tools/act1/**`, `game/levels/act1/**`, 2026-10-25), at the same time as this branch under the Lead's 10-28 row:
| Zone | act1-chapters | env-art-b |
|---|---|---|
| Ch7 port | 0d8f0e2d (M3-C07-1211) | ea946ec8 (M3-ENV-1300) |
| Ch5 Pemakar's wake wall, weir, crown bell | 6c012aee (M3-C04-1204, with Ch4's) | 70664cd0 (M3-ENV-1301) |
| Ch8 Corrow flood and lake as water | 0737523e (`waters` in ZoneKitDressing) | 00e15816 (`waters` and `storms`) |
| Ch8 Coilspire trial pieces | f90e3df1 (M3-C08-1210) | 99063a1e + 00e15816 |
| Ch9 strand, landing, mole, lake | 778fdd4e (M3-C09-1209) | 99063a1e + 00e15816 |
| Ch5 Ashcrown + its day arenas, Ch6 road, the Undertow in Ch8 | (Ashcrown blocked, none) | 4081127f and before |
The two touch the same generated files (`*_dressing.json`, `*_collision.json`, `*_layout.json`, `tools/act1/ch0[5-9]_*.py`)
and both add a `waters` row type to `zone_kit_dressing.gd`, so they cannot both merge. **Recommendation:** take
env-art-b for Ch5–Ch9 dressing (the 10-28 row, and it has the Undertow, Ashcrown, the arenas and the Ch6 road that
build on it). Keep act1-chapters' Ch4 work and its "dressings keep only blocks waiting on a request" test, and re-point
that test at this branch's zones. 
## NEW ACCOUNT (from 2026-10-25)

### 2026-10-28
- **Ch7 port, M3-C07-04 (ea946ec8):** `ch07/tamsule` dressed from env-art's port preview
  (`tools/act1/ch07_tamsule_port_dressing.py`): the quay, market, stilt lane, gantry foot, Tavi's boats, the harbour
  and the trader, and the Bell's whole ring at (0, −1.6, −75). The river is water now (it was a floor 1 m down):
  invisible rails on every open deck edge (`tamsule_collision.json`) keep the player on the decks. The Bell's mark and
  T08/T09 look at the kit's ring; the zone takes the galleries' Ch7 noon sun and grade. New test
  `test_ch07_port_walkable` (6/0); `--filter=ch07` 12/0; `--filter=cutscene_walks` 1/0. Shots `ch07_tamsule_mouth`,
  `_market`, `_gantry` (new, rig `ch07_tamsule_shots.tscn`): viewed; the stalls, bunting, Bell and water read. The two
  capsules in them are Liss and Kerrid, who have no field body yet (characters' work, not kit).
- **MERGE-READY @ 00e15816** (with ea946ec8 above). Items:
  - **M3-ENV-1301, Ch5 Pemakar (70664cd0):** env-art's harbour pieces placed (M3-ENV-1214): `harbour_quay` replaces
    the module quay; `wake_wall` and `crown_bell` follow their blocks; the `sea_cut_weir` at the quay's EAST END
    (env-art's preview put it at the bottom channel's outlet, x −39, but B05's staging is at the quay's east end, so the
    weir moved to the story: cheek tops flush with the deck, `--weir-relayout` moved the weir folk 4.6 m east with
    P11/P12/P02D); a lamp pillar and the spill's light at night; the dawn variant takes `pemakar_day_environment.tres`.
    No greybox kept in Ch5 Pemakar.
  - **M3-ENV-1302, Ch8/Ch9 (00e15816):** `ZoneKitDressing` `waters` and `storms` rows (game/levels/act1, additive;
    **act1-chapters please note**). Ch8's Flood (waist-deep) and Lake, Ch9's lake and Iskarra's sea are water. **The
    Undertow now appears in Ch8** (it was missing entirely): Corrow from the beacon's opening to the cut rope (a new
    `Storm` marker block, `--storm-relayout` in `ch08_corrow_dressing.py`), and from Coilspire's gallery on the
    StormWall block. Ch9's landing, Pell's rocks (path on the RocksDown ramp), the mole gangway and the vigil burner are
    kit pieces. Coilspire's flue gates, niche seal, lamp niche and wright's mark (M3-ENV-1222's Coilspire half) too.
    Ch8 and Ch9 keep no greybox except Coilspire's `Virel` (the Vowbound's body: creatures-b).
  - **Kit pieces (99063a1e):** Corrow `b_strand.py` (3), Coilspire `b_trial.py` (4), Ashcrown `b_trial.py` (11, for
    the next item). Each kit rebuilt `--all` in Blender 5.0.1: every older glb, texture and material byte-identical.
  - **Checks run:** Godot `--filter=` zone_kit 10/0, corrow 18/0, ch08 23/0, ch09 12/0, ch05 8/0, pemakar 10/0,
    ch07 12/0, ch07_port 6/0, cutscene_walks 1/0; tools test_corrow_kit, test_coilspire_kit, test_ashcrown_kit OK;
    gdlint/gdformat, validate_data 0/0, taskboard --check. `test_screenshots` is red only for the new shots' missing
    baselines (I never write baselines).
  - **Checks skipped:** the full Godot suite and coverage (no battle/progression code); the whole tools suite (only
    the kits' tests can see these changes); Blender verify for other jobs (none touched).
  - **Known, not mine:** "12 resources still in use at exit" after the ch08/ch09 thread tests; it happens with the
    storms removed too, so it predates this branch.
  - **Known, follow-up:** the weir's cut has no channel feeding it down the flank, so by day its water reads as a pale
    slab; Coilspire's niche and mark have no shot (the flue-key wheels hang in front of them from every interior view).
- **Merged hero-integration @ bccce923** (M3-ARC-1216 steep stairs; MERGE-READY on their log since 10-27) because
  Ashcrown needs it. Conflicts: `battle_sandbox.json` (all four heroes' hero_motion actors, Ysolde's scene from
  theirs), shot manifests (union), the M3-ARC-1216 task file (theirs, as their log asks).
  - **FAST-TRACK for hero-integration (fixed here, their file):** `HeroStairs.build_from_layout` added the layout's
    flights to the zone during the zone's own setup, so in a real zone `add_child()` failed ("Parent node is busy")
    and no flight was ever built; their tests add flights by hand, so none caught it. Now it defers the add while the
    zone isn't ready. `--filter=hero_stairs` 7/0.
- **M3-ENV-1303, Ch5 Ashcrown on its kit:** the zone in the kit's own
  frame (`tools/act1/ch05_ashcrown_dressing.py`, `--relayout` once): the causeway (HeroStairs rows over walkable
  ramps), the forecourt, the flying stair (48°, HeroStairs over a blocking slab) to the crown, the trial on the east
  ambulatories of tiers 6..3 (t1..t4), the vein stairs (60°) chained by `Stair_t<k>` until the strike reaches the tier,
  the anvil court in the anvil hall (the Matron's alcove, Kahre's door at the loggia). New Ashcrown kit story pieces
  (`b_trial.py`), env-art's Ch5 day grade. **Edits to act1-chapters' shared code, additive:** `ZoneKitDressing`
  `turn_with` and `glow()`; `KitCollision` merges the collision file's `stairs`; `Ch05AshcrownZone._glow` lights the
  kit's bowl. New test `test_ch05_ashcrown_walkable`.
- **M3-ENV-1303b, Ch5's day arenas:** `ashcrown_forecourt_day` (the stair fights) and `ashcrown_anvil_court` (the
  Matron; `BossAnchor`) from the Ashcrown kit (`b_arenas.py`, through env-art's `arena_scenes.write_arena`, read-only);
  in `arenas.json` scenes and `test_battle_arenas`. **Request M3-BPR-1305 (combat):** repoint the five Ch5 encounters
  (they all fight on the night Pemakar terrace today).
- **Request noted on M3-RND-26 (rendering):** the Bell's drop in both Ch7 zones needs `WaterSphereRig` sized to the
  drop contract (14 × 11.5 m, not the 16 m sphere) and the weep column; the galleries' `Column` stays greybox until
  then.
- **For act1-chapters:** env-art's `ch05_harbour_dusk` grade (assets/environments/zones/ch05) is waiting for a light row
  in Pemakar's flow (B01–B03 are at dusk; the zone is night from the start): a flag at the Lanternfall's start plus
  `apply_variant`. Story flow, so yours.

- **M3-ENV-1304, Ch6's road:** the raid's aftermath along the road (`road_aftermath()` in
  `ch06_brine_shoals_dressing.py`), clear of story points; the crates, sacks, salvage and boat collide.
- **Zone map follows** (`game/data/ui/zone_maps.json`, UI's file; only the `at` values of POIs whose sources I moved,
  and Ashcrown's bounds). **For UI:** the map draws a greybox layout's blocks only; Ashcrown's floors are now in its
  `collision_path` file, so its map is sparse. Reading the layout's `collision_path` blocks as floors would fix it.
- **MERGE-READY @ 4081127f** (commits after 4eb5f642: the hero_stairs FAST-TRACK, the ownership claim,
  M3-ENV-1303 zone, its arenas, M3-ENV-1304, the zone-map follow, this log).
  - **Checks run:** Godot `--filter=` ashcrown 22/0, ch05 13/0, cutscene_walks 1/0, hero_stairs 7/0, zone_kit 10/0,
    battle_arenas 10/0, ch06 5/0; the whole tools suite (`run_tool_tests -j 4`): only `test_screenshots` is red, for
    the new shots' missing baselines (the first is ch05_pemakar_harbour, which is older); `test_zone_map_pois` was red
    and is fixed in this push. gdlint/gdformat, validate_data 0/0, taskboard --check.
  - **Checks skipped:** coverage (no battle/progression code); Blender (no Blender source touched: the arenas are
    written by a Python scene writer).
  - **Known, not mine:** Toma, Liss and Kerrid are capsules in the field (no field bodies yet).

- **Act I inventory (M3-HER-1141), my 11 rows:** an audit of this branch (hero-integration's
  `tools/placeholder_audit.py`, not committed here) left 3 of them, and the rest were already fixed by M3-ENV-1300..1304.
  - `ash_terrace_lanternfall` writer sphere flames: **fixed** (M3-ENV-1305: a Pemakar kit `votive_lamp` under each votive;
    `b_lanternfall.py` writes the arena; **request M3-ENV-1306 to env-art** to fold that into `arena_scenes.py`, or the
    next all-arena write brings the spheres back).
  - `tamsule_bell_galleries` Greybox/Column: **blocked** on Rendering's M3-RND-26 (the weep column), still `todo`.
  - `coilspire` Greybox/Virel: **not mine.** It is the Vowbound's body (creatures-b, M3-CRE-627). integration-qa,
    please move the row.
- **M3-ENV-1307:** Pemakar's weir is fed by a stepped leat (new kit piece `weir_leat`) from a culvert in tier 0's wall.
- **Weakest views (the Lead's list):**
  - **M3-ENV-1308, a bug:** the Undertow never drew in Ch8's zones. A camera's default far plane is 4 km and the storm
    stands 10–14 km out. `ZoneKitDressing` now raises the current camera's far plane past every shown storm.
    **For Rendering:** other scenes that place an UndertowStorm under a default camera have the same clipping.
  - **M3-ENV-1309:** Ch9's moon comes from the sea (yaw 200 to 60, `--moon-relayout`). The sea face (C03's
    counterpart), Pell's rocks and the strand read now.
  - **M3-ENV-1310:** Ashcrown's loggia (A08): the near plume is 0.75 across, standing back over its vent, with a vent
    glow. **For env-art:** the kit preview's A08 has the same cause.
- **FAST-TRACK for act1-chapters (e0ff695c):** `test_zone_kit_dressing` checked every piece against the zone's
  `kit_dir`, so Ch6's borrowed Haluna pieces failed it; it now honours a row's own `kit_dir`.
- **MERGE-READY @ 749bfc48** (everything after 4081127f, listed above, plus the ownership commit 8240c0e0).
  - **Checks run:** Godot `--filter=` zone_kit 11/0, battle_arenas 10/0, pemakar 10/0, ch09 12/0, ashcrown 22/0;
    gdlint/gdformat on the changed GDScript, validate_data, taskboard --check. Pemakar kit rebuilt `--all` in Blender
    5.0.1 twice: every older piece is byte-identical.
  - **Checks skipped:** the tools suite (the only tools change since its last full run is two generators, whose output
    is checked by the Godot tests above); coverage (no battle/progression code).

- **For act1-chapters:** in `ch05_pemakar_harbour` (your rig `ch05_pemakar_shots`, view Harbour), the two big orbs in
  the foreground are Asha's and Toma's hand lanterns, 2.5 m in front of the camera. Moving the view up or past them
  would let the town read.
- **BACKLOG EMPTY @ 749bfc48**, with reasons:
  - My inventory rows: 9 of 11 done. `Column` waits on Rendering's M3-RND-26; `Virel` is creatures-b's body.
  - The weir's channel: done (M3-ENV-1307).
  - The weakest views: done. Contact sheet of all 25 Ch5–Ch9 zone shots; fixed the Undertow (not drawn), Ch9's sea
    face and rocks (black), and Ashcrown's loggia (a flat wall of plume). What's left is the Pemakar harbour orbs
    (act1-chapters' rig and props, above).
  - Open requests: M3-ENV-1306 (env-art, the arena table), M3-BPR-1305 (combat, the Ch5 arenas), M3-RND-26
    (rendering).
  - **Next for a fresh env-art-b:** re-run the audit (`tools/placeholder_audit.py`, on hero-integration) after the
    Lead's merge; take any new Ch5–Ch9 rows; the galleries' `Column` when M3-RND-26 lands.

- **Lead's second pass (10-28): arenas, a walk-through, touched props.**
  - **Arenas, the weakest angle at battle distance (M3-ENV-1312..1314):** all 10 Ch5–Ch9 arenas from every
    CameraHint plus the battle camera (53 angles). Fixed:
    - Lanternfall's side angles ran into black: its terrace now continues past both ends.
    - The salvage camp had no fire: new kit fires (`camp_fire_large`/`_small`), with **request M3-RND-1315** to Rendering
      for animated fire.
    - **The Undertow was in no battle:** the three wall-head arenas get it, with `StormFarPlane`, a new node the zones
      now use too.
    - The headland's slopes get scrub.
    - Ashcrown's plume now uses its day material.
    - Wrapper writers over env-art's tables; `tools/tests/test_b_arenas.py` reproduces them.
  - **Ch8 arena ids:** the note on M3-ENV-714 says `ch08_headland_*` go to `coilspire_headland_path` and
    `ch08_flue_moths` to `coilspire_tier_landing`. That task is battle-presentation's. Ch5 is M3-BPR-1305.
  - **Walk-through (M3-ENV-1317):** 44 player-height views on the critical paths. Fixed: Ch6's camp burns in the
    zone too (until the evening camp). **Request M3-ENV-1316 to env-art:** the trader boat's white bales, Ashcrown's flat
    stair and tier faces, and the headland's far facets.
  - **Touched props:** every Ch5–Ch9 door, gate, lever, key, shrine and marker already wears a final kit model. Ch7's
    Signboard block is the shophouses' own hung boards (M3-ENV-1311, nothing to add). There are no chests or
    SaveShrine nodes in Ch5–Ch9.
  - **FAST-TRACKs:** `test_arenas.py` skips the wrapped arena ids and `test_pemakar_kit.py` counts 34 targets (for
    env-art); `test_zone_kit_dressing.gd` counts the Smoke block's eight followers (for act1-chapters).
  - **Correction:** MERGE-READY @ 749bfc48 was NOT tools-green. `test_arenas` (Lanternfall) and `test_pemakar_kit`
    (the count) were red because I skipped the tools suite there wrongly. Both are fixed in this push.
- **MERGE-READY @ 8d198f1e.**
  - **Checks run:** full tools suite (`run_tool_tests -j 4`): only `test_screenshots` red (baselines).
    Godot `--filter=` battle_arenas 10/0, battle_arena 18/0, zone_kit 11/0, ch06 5/0, ch07 18/0, cutscene_walks 1/0.
    gdlint/gdformat, validate_data, taskboard --check. Brine Shoals kit rebuilt `--all` in Blender: older pieces
    byte-identical.
  - **Checks skipped:** coverage (no battle/progression code).

- **Merged big13 (90ecee18) at c47cc9a7.** The Ch5 Ashcrown and Ch7 Tamsule scenes and layouts keep env-art-b's kit
  frames (they already carry act1-chapters' Cast node, marks and casts). In zone_maps.json, UI's new Ch8 Corrow and
  Coilspire entries are re-pointed to the kit frames (POIs, hints, bounds). ownership, PROVENANCE and shots.json are
  unions. Everything else is integration's.
  Checks after the merge: Godot zone_kit, ch05..ch09, battle_arena, cutscene_walks and hero_stairs all pass; tools
  test_zone_map_pois, test_arenas, test_b_arenas and the kit tests OK; validate_data, gdlint/gdformat.
- **The Lead's gate notes (10-28):**
  1. battle_boss_intro_reach / battle_ch08_stair_hold, "the Reach's backdrop is greybox": on integration
     `wall_head_storm` still maps to the greybox scene. This branch maps it (env-art's fix) to the final
     `seawall_stairhead_hoist`, now with the Undertow over it. Rendered on the merged tree: the wall, the town's roofs,
     the headland and the storm; no greybox. Resolved by merging this branch.
  2. ch09_corrow_strand, "a glowing white bar": the baseline is integration's greybox shroud rows lit by the vigil.
     On this branch they are the kit's shroud pieces, and the strand is moonlit shingle (M3-ENV-1309). Rendered:
     no slab. Resolved by merging this branch.
  3. ch05_pemakar_harbour, "a dark blob in the sky": the far plume in the kit's material read as a hard silhouette.
     It now uses the zone's own night plume material (`pemakar_plume_night.tres`, M3-ENV-1318): softer, thinner edges
     and the crater's ember up its underside. Rendered: it reads as smoke lit from below.
- **MERGE-READY @ 6cd17ce3.**

- **Merge fix (13c07138):** five files where this branch already held all of integration's commits (env-art's
  Haluna kit `build.py`, `materials.py` and `kit_manifest.json`, and the Ch4 and Ch6 layouts) went back to this
  branch's newer versions; `test_haluna_kit` is green again. The other 68 files taken from integration were checked:
  none of them lost a change from this branch.
- **M3-ENV-1319, encounter arenas (the Lead asked twice):** every Ch5–Ch9 encounter now names its final arena in
  `encounters.json` (only the `arena` fields), including the three Ch8 fights that had none. The seawall states take
  `wall_head_storm`'s staging. battle-presentation, please review (M3-BPR-1305, M3-ENV-714).
- **MERGE-READY @ f51f81f2.** Checks: Godot battle (757; the one failure was the pinned table, now updated), battle_arena
  18/0, ch04 11/0, ch06 5/0; tools suite: only test_screenshots red (baselines), test_haluna_kit green after the fix.
- **Queue state:** arenas for the remaining Ch5–Ch9 encounters are done (above). The player-height walk-through
  (M3-ENV-1317) and the interactable props are done; their findings and requests are above (M3-ENV-1316 to env-art).

- **big14 gate, test_pemakar_kit (34 targets, expected 32):** already fixed on this branch by e8944d6c (the count
  is 34 for `votive_lamp` M3-ENV-1305 and `weir_leat` M3-ENV-1307, both with their LOD chains, which the same test
  checks). big14 took an earlier commit. Any head from e8944d6c on is green (`test_pemakar_kit` OK at 5c077662).
  **MERGE-READY @ 5c077662** (it holds every earlier MERGE-READY item).

- **Merged lead/gate-big14 (8707ff90), 296c1248.** Each conflict was decided by ancestry (whichever side already
  held all of the other's commits on that file). For encounters.json, this branch's Ch5–Ch9 arena fields plus
  integration's Act II rows. The storm far-plane test now frees its zone (the runner's new leak check).
  `test_zone_map_pois` has 8 ch04/haluna_wake failures that **also fail at 8707ff90** (integration's, act1-chapters'
  or UI's), not this branch's.
- **Inventory (M3-HER-1141), re-audited on the merged tree:** 2 rows left. **M3-ENV-1320** fixes `Virel` (creatures-b's
  model now exists; it is placed in the crown chamber). That leaves `Column` only, still blocked on Rendering's
  M3-RND-26 (todo).
- **MERGE-READY @ 22b289bf.**

- **Walk-through repeated on the merged tree (after big14):** the same 44 player-height views; no new issue in Ch5–Ch9
  dressing. Today's fixes show (Pemakar's plume reads as lit smoke, Ch6's camp burns). Still open and not mine:
  Ashcrown's flat flying-stair and tier faces and the trader boat's white bales (env-art, M3-ENV-1316), and the
  placeholder capsules (characters). Interactable props: unchanged since M3-ENV-1311/1317, and every one is final.
  **Backlog:** only the galleries' `Column`, blocked on Rendering's M3-RND-26.

- **M3-ENV-1321, the Bell's weeping column (taken at the Lead's ask under ADR 0041):** a kit piece with zone water
  materials, so no new shader. It stands in the galleries (on the Column block) and at the port (under the kit's Bell).
  **env-art-b's Act I inventory rows are now all closed.** Rendering keeps M3-RND-26's sphere-rig sizing and an
  optional flowing column shader.
- **Walk-through and interactable props:** done on the merged tree (above); nothing new.
- **MERGE-READY @ 8c535d1e. BACKLOG EMPTY:** no inventory rows left; requests out to env-art (M3-ENV-1306, 1316),
  battle-presentation (M3-BPR-1305, M3-ENV-714 review) and Rendering (M3-RND-26 rig, M3-RND-1315 fire).

- **The PC's Act I GPU QA (docs/kb/qa/act1_gpu_qa.md on gpu/act1-qa-2), env-art-b's rows.** Pass A ran on integration
  048b0a7f, before this branch merged. Each row was re-rendered on this head:
  | Row | Shots | Status |
  |---|---|---|
  | 5 | ch06_brine_camp, _road | **fixed @ 0981fc15** (the camp burns; the road carries the raid's wreckage, 4081127f). The flat mudflat and the boxy `camp_tent` are kit meshes and materials: added to env-art's M3-ENV-1316. |
  | 6, 27 | ch08_coilspire_hall, _gate | **fixed @ 3109a2f5**: the green grid was the kit's verdigris gathered in the mortar joints; the zone now uses its own inner material (no grid), and wall-wash lamps on every tier light the well. |
  | 7 | ch08_corrow_arrival | **fixed @ 00e15816**: the mole is the kit's `mole_pier` and `mole_sea_stair` (integration had the greybox). |
  | 9 | ch09_corrow_strand | **fixed @ b1ca59b9**: the moon over the sea. |
  | 10 | battle_arena_wall_head, battle_ch08_stair_hold | fixed in big14 (as the row says). |
  | 11 | battle_boss_intro_reach | **fixed @ f51f81f2**: the Reach fights on `seawall_stairhead_surge`, with the Undertow. The light wedge is Rendering's, per the row. |
  | 15, 40 | battle_arena_underway, _underway_tower, the Ch1 fights | **explained: Ch1 is env-art's** (the Lead's split: env-art-b has Ch5–Ch9). Request **M3-ENV-1323**. |
  | 16 | battle_arena_terrace, _ash_terrace_lanternfall | **fixed @ 3be35a85**: a warm key over the party. The `terrace` shot (`ch05_stair_*`) now fights on `ashcrown_forecourt_day` (f51f81f2). |
  | 26 | ch05_ashcrown_causeway, _forecourt, _tiers | **explained**: the zone stands on env-art's Ashcrown kit as built, and the grey is its `ac_*` materials. Added to M3-ENV-1316. |
  | 28 | ch09_corrow_rocks | **fixed @ 47845c69**: the boulders are angular laterite, not glossy black spheres. |
  | 34 | ch06_ridge_skippers on the test stage | **explained: act1-chapters'.** The encounter names `brine_shoals_afternoon` (validate_data clean). A fight with the sandbox's own enemies means the BattleRequest never found the encounter (its flow). |
  | 38 | Coilspire spawns, camera against the wall | **explained: hero-integration's field camera**. The spawns stand on the tier landings by design; the camera doesn't pull in. |
  **MERGE-READY @ 3be35a85.**

- **M3-RND-26, the Tamsule Bell's held drop (the Lead's ask, 2026-10-28 13:25; rendering's zone and kit looks are env-art-b's):** done @ ce10e96a. `WaterSphereRig` gained data `profiles` and a flattened spheroid (`sphere_flatten`). `tamsule_drop` is the contract's 14.0 × 11.5 m drop: still (no swell, a steady web), pushed cyan, glowing steady with glimmer_bound, and throwing its web under it (pool, coping, posts) plus the pool's reflected web on the bell's underside, clipping to white. The Reefball ball is unchanged (empty profile). The weep column is the contract's 0.8 → 0.6 m now, turquoise in the zones. Placed in the preview (`SphereAnchor/Drop`, `/WeepColumn`) and both Ch7 zones (ZoneKitDressing `drops` rows). Contract accepted unchanged (written in the task file; pc-gpu.md is the PC's). Task → review (art).
  Checks run: gdlint/gdformat, validate_data, taskboard --check, Godot `water_sphere` (5, +1 new), `tamsule` (7), `zone_kit` (12), `ch07` (18), `reefball` (80), tools `test_tamsule_bell_kit` (13), kit rebuild `--all` (only weep_column changed). Skipped: the Reefball arena's own shots (no registered shot shows the ball; at the empty profile its math is unchanged).
  **MERGE-READY @ ce10e96a.**
  LEAD-ANSWERED (14:06: the PC measures it in its QA pass once this branch is in a batch; the Lead re-approves t01 and t03 at the gate): M3-RND-26's last criterion is the cost on the PC presets (the drop is seen through 48 glass bays and from beneath). Route it to the PC's QA pass? Also re-approve `tamsule_t01_bell_from_the_mouth` and `tamsule_t03_oruvel_moorings` at your gate (they drift by design: the cyan drop and the contract column). Going ahead meanwhile.

- **M3-RND-27** (→ review): already in place. The Ch7 column is the kit piece and the Ch8 storm wall is the Undertow on its block, and no zone keeps a box. **M3-HER-1141** (→ review): `placeholder_audit.py` with its runtime scan lists **nothing for env-art-b** (37 items, all other roles'). **M3-RND-1315** (→ review): the camp fires lick, tear and flicker on `hymn_wind_time` (`game/vfx/fire/flame_tongue.gdshader`, docs `tech/fire.md`), in dusk_gold → ember_orange.
  Checks run: gdlint/gdformat, taskboard --check, Godot `flame` (2, new) and `brine` (5), tools `test_brine_shoals_kit` (31). **MERGE-READY @ 51f5185c.**

- **M3-C09-10** (→ review): the colour script has `ch09_dawn` and the act-break vigil frame. The dawn variant now has its own grade, `corrow_ch09_dawn_environment.tres`, in place of the borrowed Ch8 storm grade. The vigil's own light waits on M3-C09-04. Checks run: Godot `ch09` (12), validate_data, taskboard --check. **MERGE-READY @ f11aca7d.**

- **M3-RND-21** (→ review): a volumetric smoke column (`SmokeColumn`, `game/vfx/smoke/`, docs `tech/smoke.md`), raymarched in a bounding box and clipped by depth, so no shells show up close. It replaces the kit's shells in `ch06/brine_shoals` (ZoneKitDressing `smokes` rows, on the Smoke block). Requests: **M3-ENV-1324** (env-art: the kit preview and the camp arenas' shells) and **M3-ARC-1324** (integration-qa: `apply_system_tiers` should also tier WaterSphereRig and SmokeColumn). Checks run: gdlint/gdformat, validate_data, taskboard --check, Godot `smoke_column` (3, new), `zone_kit` (12), `ch06` (5). **MERGE-READY @ 3eaa64a5.**
  LEAD-ANSWERED (14:47: yes, env-art-b takes it after the Fisher Stair prop; agree the cue vocabulary with integration-qa by task file): M3-C09-03 (the Ebbing's motes: GlimmerField fields, staff and mourner attractors, and a `.dlg` cue vocabulary with Systems and the Architect) is rendering's, but it's cutscene VFX, not a zone or kit look. Is it env-art-b's under your owners split? Meanwhile I'm leaving it and taking my own Ch5–Ch9 audit. Also: the cost criteria of M3-RND-21 (four columns under 0.3 ms at High 1440p) and M3-RND-1315 go to the PC's QA pass, as M3-RND-26's did.

- **GPU QA re-check on big15 (6466a6f5, gpu/act1-qa-2 62b2115c):** rows 6, 27 and 28 read "still open" only because their fixes (3109a2f5: the Coilspire grid lines; 47845c69: the Corrow rocks) came after big15. Both are on this branch @ MERGE-READY. Rows 15, 26 and 40 stay explained (env-art's M3-ENV-1323 and M3-ENV-1316). The PC can re-check once this branch is in a batch.

- **M3-RND-21 / M3-RND-1315 follow-up:** both Ch6 camp arenas (`salvage_camp_burning`, and `brine_shoals_afternoon` through a new wrapper, `b_shoals_arena.py`) now draw SmokeColumns instead of shells (`b_smoke_columns.py` swaps the written plume instances). The flames have volume (a brighter heart, an orange rim), and the fires sit on round, ragged ash beds instead of square trays (`b_fire.py`, rebuilt; only the two fire pieces changed). M3-ENV-1324 is narrowed to the kit preview. Checks run: tools `test_b_arenas` + `test_brine_shoals_kit` + `test_arenas` (53), Godot `flame`, `battle_arena`, `brine`, `smoke` (all green), gdlint/gdformat, taskboard --check. **MERGE-READY @ 9a9c0043.**

- **The Fisher Stair in Ch8's set piece (the Lead's ask, 14:27; M3-CRB-009 ask 4):** done @ 9c8e9c99.
  - **The capsule:** it is the greybox `wall_head_storm`'s `StairHead`. The integration branch still sends `ch08_stair_hold_1..3` and `undertows_reach` to that greybox. On this branch, encounters.json already sends them to the seawall arenas, which stand the Corrow kit's real `fisher_stair`, so merging this branch retires the capsule. Self-renders of `battle_ch08_stair_hold`, and of `undertows_reach` at the default camera (scratch), show no capsule.
  - **Added:** `StairHead_ward` and `StairFlight_ward` anchors on all three wall-head arenas, computed from the kit stair's own frame. The head lands 0.3 m from env-art's `EntryMarker_ward`. A `CameraHints/the_stair_head` hint frames the head landing and its down-steps from the walk.
  - **Request M3-BPR-1325** (battle-presentation): anchor the stair meter and climber VFX on these marks, and cut to the hint when the Climb acts. From the default camera the stair head sits just off frame right.
  - **Checks run:** tools `test_b_arenas` + `test_arenas` (22); Godot `battle_arena` (18), `set_piece` (48), `seawall_stair` (1, new). **MERGE-READY @ 9c8e9c99.**

- **M3-C09-03, the Ebbing's motes (the Lead, 14:47):** built @ 50db241b; the task stays `doing` until the cue hook lands.
  - **The rig:** `EbbingMotes` (`game/vfx/ebbing/`, data `game/data/vfx/ebbing.json`, docs `tech/ebbing.md`) sits on `ch09/corrow_night` through ZoneKitDressing's `ebbing` row. It plays eight HELD fields by the cue marks, about 5,100 motes at High and 1,800 at Low.
  - **Attractors:** a staff attractor on a `StaffHead` on Asha, kept low enough that under 5 % of the motes rise under the raised staff (a CPU replica test, which also shows a full-strength pull would lift 38 %). Mourner anchors let go over 4 s as the staff passes. The cutaway's field has no attractor and no focus. Reflections are on for the harbour fields.
  - **Test scene:** `game/levels/_tests/ebbing/ebbing_shots.tscn`. New shots `ebbing_n11` and `ebbing_n08` need the Lead's baselines.
  - **Request M3-ARC-1326** (integration-qa): `_cue_vfx` should offer each cue to the `cutscene_vfx_hosts` group first, plus the `follow=` / `anchors=` vocabulary. Until it lands, the chapter's cues still draw the placeholder.
  - **Checks run:** Godot `ebbing` (5, new), `ch09` (12), `glimmer` (36), `zone_kit` (12); gdlint/gdformat; validate_data; taskboard --check. `tools.tests.test_screenshots` fails on `kerrid_front` already at HEAD (pre-existing, not this branch's), and the two new shots have no baselines yet. **MERGE-READY @ 50db241b.**
  LEAD-ANSWERED (15:33: the Lead baselines them at the gate; M3-ARC-1326 routed to integration-qa): baselines for the new shots `ebbing_n11` and `ebbing_n08` at your gate. And M3-ARC-1326 needs integration-qa: the one hook that lets Ch9's cues play the real Ebbing. Can you route it?

- **BACKLOG EMPTY (14:58, @ the handoff commit):**
  - Every env-art-b and rendering zone/kit item is done or waiting on another track:
    - M3-ARC-1324 and M3-ARC-1326: integration-qa.
    - M3-ENV-1324, M3-ENV-1306, M3-ENV-1316 and M3-ENV-1323: env-art.
    - M3-BPR-1325: battle-presentation.
    - Costs: the PC.
  - The rendering board's other todos are battle VFX (battle-presentation's, per the owners split), Ch1 underwater (env-art's chapter), or M2 items blocked on others.
  - Next: the `ebbing_*` baselines and M3-ARC-1326. When the hook lands, play Ch9 through its cues and view N08 to N15.

- **Player-height placeholder audit, Ch5–Ch9 (the Lead, 15:33):** 44 walk views at eye height along each zone's path, plus every registered Ch8 and Ch9 Corrow shot, all viewed.
  - **Fixed @ 26a674f8:**
    - **The Corrow bastion yard** (the wall's west end, by the Stillguard barracks) was the low town's sand-and-cobble ground raised to walk level: a flat sand pad with hard-edged stone patches. It is now paved in the walk's laterite (`material_paths`) and dressed with ten pieces of stair-watch clutter inside its rims (crates, sacks, shields, rope, nets; two skipped for story-point clearance). This covers Ch8 and Ch9.
    - **Ch9's rubble at night** (the rip-rap, the breach, the strand rocks, the low-town rubble, the milestone) read as wet black pillows, the look GPU QA row 28 flagged. Its `cw_rubble` slot is now the kit's dry broken laterite.
  - **Explained, not mine:**
    - The trader boat's white box bales (Tamsule, Corrow): env-art's piece, request M3-ENV-1316.
    - Ashcrown's flat mint and red lacquer posts and strips: env-art's kit materials, M3-ENV-1316.
    - Pell and `kerrid_stair` as capsules: no field body yet, characters' M3-C09-08 (M3-CIN-1217 lists them).
    - Pemakar's black flank above the town at night: the colour script's ch05 fill of 0.25, so the lamps read.
  - **Sampling artifacts, not defects:**
    - Views starting inside the party's heads.
    - One Coilspire view interpolated through the hill.
  - **Checks run:** Godot `ch08` (23), `ch09` (12), `zone_kit` (12), validate_data. **MERGE-READY @ 26a674f8.**

### 2026-10-29 (new Lead session_01Bg3iP7cPGyjbX4CyniBahc; integration `claude/new-session-mj8c3c`)
- **Merged `origin/claude/new-session-mj8c3c`** (clean). Re-imported.
- **M3-C09-03 (the Ebbing):** M3-ARC-1326's hook (`CutsceneVfxHosts`) is on `claude/hero-integration` (5c11d034), not
  yet on integration. My side needs no change: `EbbingMotes.play_vfx` matches its signature, and it reads marks at
  runtime, so hero-integration's moved `mourner_hand` mark is followed. When it lands: play Ch9 and view N08–N15.
- **M3-ENV-1325, Ashcrown at player height (GPU QA row 26; the Ch5 half of M3-ENV-1316, zone-side):** a new walk
  (spawn → triggers at eye height, both ways) showed the tiers' shaded faces and the flying stair's flanks as flat
  near-black planes, and the trial's copper and the posts as flat mint and red plastic.
  - **Cause, black faces:** `Ch05Zone.apply_variant` writes the layout's `environment` row (ambient 0.45) over any
    grade, and the kit's stone bakes an occlusion (UV2) applied at 0.8. Now ambient 1.8 (layout row and the zone's own
    grade), and zone copies of `ac_ashlar`/`ac_dressed` at occlusion 0.3/0.35.
  - **Flat metals:** zone materials on `env_bronze` (patina, streaks, edge wear; the lacquers chip to black) swapped in
    by slot on every Ashcrown kit piece, including the tiers' veins (streaked verdigris).
  - **The day arenas** take the same swaps through a new `KitSlotSwaps` node (`game/levels/act1/`, additive) written by
    `b_arenas.py`, and the forecourt takes the zone's fill.
  - Everything is written by `tools/act1/ch05_ashcrown_dressing.py`.
  - **Checks run:** Godot `--filter=` ashcrown 22/0, ch05 13/0, zone_kit 12/0, battle_arena 18/0; tools test_b_arenas +
    test_arenas (22); gdlint/gdformat; validate_data; taskboard --check.
  - **Checks skipped:** coverage (no battle/progression code); Blender (no kit source touched).
  - **MERGE-READY @ a209511a.**
- LEAD-ASK: M3-ENV-1316 (env-art's kit faces, open since 10-28) is all Ch5–Ch9. I'm fixing what the zones can fix
  (Ashcrown done above; next the trader boat's bales and the Brine Shoals tent and mudflat, by slot swaps or new
  `b_*.py` pieces). env-art keeps the kit's own materials. Going ahead; overrule if env-art has it in flight.

- **Merged `origin/claude/new-session-mj8c3c` @ ccf44ba4** (clean).
- **big17's freed-cast lint (routed to me 18:40):** `EbbingMotes._process` cast a stored mourner ref before
  `is_instance_valid`; it now checks the raw ref first (e884cb93). hero-integration's `tools/freed_cast_lint.py` run
  on this tree: no env-art-b hit left (its `hero_field_party.gd` hit is fixed on hero-integration).
- **Player-height walk, all eight Ch5–Ch9 zones (10-29):** spawns and triggers at eye height, both ways (~290 views),
  plus an ID-colour pick to name what a view shows. Pemakar (night), Tamsule and the galleries read final.
- **M3-ENV-1326, what the walk found in Ch6–Ch9** (the rest of M3-ENV-1316 that the zones can fix):
  - **`ZoneKitDressing.kit_material_paths`** (additive; act1-chapters please note): a slot swap on every piece of the
    zone's own kit, under a row's own `material_paths`. Shared writers in `tools/act1/ch05_09_zone_looks.py`.
  - **Corrow, Ch8 and Ch9:** the Bastion's and the watch's doors were flat red planes, the copper and iron plastic,
    the trader's bales and Ch9's shrouds flat `cw_sail`. Zone looks: weathered lacquer (the hollows dull to an aged
    red), verdigris, sea iron, a tan sailcloth.
  - **The trader's bales** (Ch7, Ch8): a new Corrow kit piece `trader_cargo` (`b_cargo.py`), lashed and bellied
    canvas bales around the box bales. Corrow kit rebuilt `--all` in Blender 5.0.1: older pieces byte-identical.
  - **Coilspire:** pale flat mint pipes, housings and roof (`cs_copper`'s patina near full), flat worn copper and iron.
  - **The Level-stone shrine** (Ch6, and borrowed in Ch8): a white box. It takes Haluna's shrine stone.
  - **Daylight fire** (my M3-RND-1315 shader): opaque tongues read as cut card on the noon flats. Now translucent,
    with soft silhouettes, licks torn by the rising noise, and a hot heart.
  - **Arenas:** the seawall stairhead arenas and `coilspire_headland_path` take their zone's swaps (`KitSlotSwaps`).
- **Left for env-art (on M3-ENV-1316):** the kits' own flat slots, the headland's far facets, and Tamsule's
  `market_boat_a` sun umbrella (a flat 16-gon with no ribs: from the decks it reads as a pale-blue plate on the water).
- **Not mine, seen on the walk:** Inquisitor Moll is still a capsule in the camp fight (creatures-b, routed 18:43).
- **Checks run (M3-ENV-1326):** Godot `--filter=` zone_kit 12/0, ch06 5/0, ch07 18/0, ch08 23/0, ch09 12/0, flame 2/0,
  brine 5/0, battle_arena 18/0, ebbing 5/0; tools test_corrow_kit, test_coilspire_kit, test_brine_shoals_kit,
  test_b_arenas, test_arenas; gdlint/gdformat; validate_data; taskboard --check; Corrow kit `--all` in Blender.
  **Skipped:** coverage (no battle/progression code); the other kits' Blender jobs (untouched).
- **MERGE-READY @ 61c918b0** (M3-ENV-1325, M3-ENV-1326, the freed-cast fix).

- **`coilspire_tier_landing`** now wears the zone's slot looks too: `b_headland_arena.py` writes env-art's TIER_HALL
  table unchanged and adds KitSlotSwaps (`test_b_arenas` WRAPPED updated). Checks: test_b_arenas + test_arenas,
  Godot battle_arena 18/0. **MERGE-READY @ 2b882105.**

- **M3-C09-03, verified against the hook (trial merge of `origin/claude/hero-integration` @ 5c11d034, not pushed):**
  new `tests/integration/test_ch09_ebbing_cues.gd` runs every compiled Ch9 `@vfx glimmer_held` cue through
  `CutsceneSequencer._cue_vfx` on `ch09/corrow_night`: with the hook, the Ebbing takes all of them and no placeholder
  spawns (PASS on the trial tree; on this branch it only checks the cues until the hook arrives). Nothing else is
  needed from me; the task closes when M3-ARC-1326 lands on integration. **MERGE-READY @ 7dc2ba55.**
- **For integration-qa (FAST-TRACK, found on that trial):** hero-integration's own `tests/unit/test_cutscene_vfx_hosts.gd`
  fails to parse at 5c11d034: its `_motes()` checks `c is CutsceneMotes`, a class that branch removed (CutsceneVfx
  replaced it). Counting nodes named `Vfx_*` (the sequencer's names) works whatever draws the placeholder.

- **M3-C09-04's last piece:** the kit's `flood_debris` (built for it, never placed) now drifts among the low town's
  drowned roofs (12, seeded, 5–12 m from a house). Checks: Godot `--filter=ch09` 13/0; viewed from over the lake.
- **Stale placement tasks closed to review** (they were env-art's "placement is act1-chapters'" notes; Ch5–Ch9 dressing
  is mine since 10-28): M3-C05-03, M3-C08-102, M3-C09-04, each with what is built and where. B01's SaveShrine
  interactable and chandler stay act1-chapters' (systems). **MERGE-READY @ 078f3e07.**

- **Tamsule's gilt** (`tb_gold_leaf`, flat): a worn-gold look by `kit_material_paths` in the port and the galleries.
  Checks: Godot ch07 18/0, tamsule 7/0, zone_kit 12/0; viewed ch07_tamsule_market, ch07_bell_galleries.
  **MERGE-READY @ f248bb57.**

- **Pemakar and Brine Shoals** get the same zone looks for their kits' flat lacquer, copper, gold, brass and iron
  (`zl.lacquer()`, `NEW_COPPER`, `GOLD`), including the Pemakar pieces Ashcrown borrows; their arenas
  (`ash_terrace_lanternfall`, `salvage_camp_burning`, `brine_shoals_afternoon`) through KitSlotSwaps. Checks: Godot
  pemakar 10/0, ashcrown 22/0, ch05 13/0, ch06 5/0, brine 5/0, zone_kit 12/0, battle_arena 18/0; tools test_b_arenas,
  test_arenas, test_pemakar_kit, test_brine_shoals_kit. **MERGE-READY @ cff5dfd3.**

- **The Lead's "known red: test_arenas for ash_terrace_lanternfall" (lead-cloud.md):** not reproducible. `test_arenas`
  + `test_b_arenas` pass on `lead/gate-big17` @ be74f9a0 and on a trial merge of this head into it (env-art's
  M3-ENV-1306 table change doesn't clash: `b_lanternfall.py` starts from the raw `_terrace_arena()`, so its votives
  are never doubled). That trial did find a real latent bug of mine: Ashcrown's and Coilspire's kit modules were both
  `b_trial.py`, so a one-process `unittest discover` failed whichever kit test ran second. Coilspire's is now
  `b_spire_trial.py` (PROVENANCE sources updated; `flue_gate` rebuilt in Blender: byte-identical). Both orders pass.
  **MERGE-READY @ feafc90e.**

- **Full tools suite on this head (`run_tool_tests -j 4`, 1528 tests):** red only in test_screenshots (missing
  baselines for the new shots), test_shrine_gi_bake, test_hero_clips, test_zone_dressing_ch01 and test_zone_map_pois.
  The last four are not this branch's work: they come from Ch1/Ch3 files this branch carries from older env-art and
  m2-slice history that big17 has already reconciled. All four, plus test_b_arenas, pass on `lead/gate-big17` and
  on a trial merge of this head into it. They clear when big17 reaches integration and I merge it.

- **BACKLOG EMPTY (10-29, @ the handoff commit; session handoff `docs/kb/handoffs/2026-10-29-env-art-b-1.md`):**
  - My GPU QA rows and inventory rows are all fixed or explained. The latest inventory lists none of mine: the
    `*_drop_proxy` names are env-art's kit.
  - The player-height walk of all eight Ch5–Ch9 zones is done, and so is the "anything primitive?" audit. Everything it
    found that the zones, my arenas or my kit pieces can fix is fixed (M3-ENV-1325, M3-ENV-1326, M3-C09-04's debris).
  - What's left belongs to others:
    - env-art: M3-ENV-1316's kit-side items;
    - characters and creatures-b: the capsules;
    - integration-qa: M3-ARC-1326, which closes M3-C09-03;
    - the PC: the PC-QUEUE.
  - Next: merge the integration branch once big17 lands, run `--filter=ebbing` with the hook in, and move M3-C09-03
    to review.

- **The Lead's 18:43 and 20:46 messages, answered:**
  - **Freed-cast lint:** fixed @ e884cb93 (`EbbingMotes._process` checks the stored ref before casting). The lint run
    on this head lists no env-art-b hit; hero-integration's `hero_field_party.gd` hit is fixed on their branch.
    `--filter=ebbing` 5/0 (6/0 with the new cue test).
  - **`test_cutscene_vfx_hosts.gd` (hero-integration's file, red on big16/big17):** a patch for the gate:
    `docs/kb/handoffs/live/patches/m3-arc-1326-vfx-hosts-test-big17.patch` (`git apply` on lead/gate-big17 @ 6aae2fd1).
    It does not resurrect `CutsceneMotes`. `_motes()` now counts what replaced it: the sequencer's `CutsceneVfx`
    placeholders, GlimmerFields named `Vfx_<effect>_<n>`. Proven on a big17 worktree: `--filter=vfx_hosts` 4/0,
    `--filter=ebbing` 5/0. I didn't edit their file on any branch.
  - **GPU QA rows on this head:**
    - 6, 27 (Coilspire's green grid): gone in today's `ch08_coilspire_hall`/`_gate` renders and walk views.
    - 28 (black spheres): `ch09_corrow_rocks` shows broken laterite today.
    - 26 (Ashcrown's grey tiers): fixed today (M3-ENV-1325).
    - 15, 40 (the Underway's hard light rectangles): Ch1, env-art's M3-ENV-1323; big17's `arena_scenes.py` carries
      their soft underwater sun.
    - 34 (the Brine Shoals fight on the test stage): my side is sound. `ch06_ridge_skippers` names
      `brine_shoals_afternoon`, which is registered in `arenas.json`, and the zone's random table names the
      encounter. The fallback is in the BattleRequest's lookup (act1-chapters' flow).
    The PC can close all of these on its next pass.

- **Merged integration @ 502f6999 (big17)** at 1cda7ed9. Conflicts: PROVENANCE (union; then the three Ch4 wake rows
  big17 had dropped, re-added by the union, removed again) and ownership (both rows kept).
- **The Lead's big18 decision (Virel twice in Coilspire), done:** `ch08_coilspire_dressing.py` places no Virel model
  any more (ea54ea37). act1-chapters' ZoneCast `virel` actor on her coil owns her. There was no coil or plinth piece of
  mine under her to keep. **Self-rendered** on a trial merge with `claude/act1-chapters` @ 72254f9f (not pushed), from
  F07 and F06: before the binding one Virel coils in the crown chamber; after it (`ch08_virel_bound`) the chamber is
  empty under the storm grade.
  **Merge note for act1-chapters' merge:** `tools/act1/ch08_coilspire_dressing.py` conflicts on one line (their
  comment on `"greybox"`). Take this branch's file and add their comment; their side predates the kit looks.
- **M3-C09-03 → review:** the hook arrived with big17. `test_ch09_ebbing_cues` now exercises it for real
  (`--filter=ebbing` 6/0).
- **FAST-TRACKs on files that came with big17:**
  - `tests/unit/test_cutscene_vfx_hosts.gd` (hero-integration's; parse error): my patch is applied.
    `--filter=vfx_hosts` 4/0.
  - `tests/unit/test_zone_kit_dressing.gd`: the new clip test (b82f36b6) left before_each's zone in the tree; it now
    closes it. `--filter=zone_kit` 13/0, no leak.
- **Checks run:** Godot ch08 25/0, coilspire 11/0, zone_kit 13/0, ebbing 6/0, vfx_hosts 4/0; validate_data 0/0;
  taskboard --check; gdlint/gdformat.
- **Checks skipped:** the broad `--filter=cutscene` hit its 1500 s timeout inside the cutscene motion audit (90 passes,
  no failures, not scoped to these changes); coverage (no battle/progression code).
- **MERGE-READY @ 98d582ef.**

- **The Lead's 23:10 ask: the final-quality audit of Ch5–Ch9 as played. DONE.** Run on `lead/gate-big18` @ d00d3284
  with this head merged on top (a trial worktree, not pushed).
  - **Coverage:**
    - all eight zones at eye height: every spawn, trigger (doors, transitions, interactables) and mark (NPC and story
      spots), each looking four ways; about 700 stills, all viewed;
    - six story variants: Pemakar's day, the dusk camp, Corrow's storm and the wall's fall, Coilspire after the
      binding, Ch9's dawn;
    - a denser Pemakar pass;
    - all ten Ch5–Ch9 arenas from the battle camera and every CameraHint (56 stills).
  - **The Reefball venue:** the match itself is UI's 2D HUD. Its venue is the Tamsule Bell galleries (the catch-pool,
    the held drop), walked as a zone: clean.
  - **Fixed in my lane:**
    - Ashcrown: Kahre's door leaves (red lacquer with grey hollows) read as camouflage. All lacquers now use the
      shared same-hue lacquer look (`zl.lacquer`).
    - Pemakar: the quay where the party lands was pitch black. Three kit lamp pillars with lights now stand along its
      back edge, clear of the story marks.
    - Brine Shoals: the Level-stone shrine still read as a white cube. It is now weathered, salt-stained stone
      (`brine_shoals_level_stone_material.tres`; Ch8's borrowed shrine uses the same).
    - Brine Shoals: the camp fires still read as smooth cones at arm's length. The tongues now break into licks,
      with thinner tips and a softer heart.
    - Corrow (Ch8 and Ch9): the seawall's segment joints showed the sky as a jagged white line on the inland face
      (seen from the Fisher Stair's foot). The segments now overlap 1 percent.
    - Coilspire: the tiers' wall-wash lights had no source. A new kit piece, `wall_lamp` (`b_spire_trial.py`: an iron
      plate, an arm and a copper dish with its flame), now stands at each light: 9 lamps placed clear of every flight's
      treads and the trial's blocks. Coilspire kit rebuilt `--all` in Blender: older pieces byte-identical.
  - **Filed as requests:** M3-ENV-1327 to env-art:
    - Tamsule's shophouse ground floors are open, unlit voids from the lane;
    - Corrow's `lowtown_ground` puddles read as black holes at grazing angles;
    - carried items: M3-ENV-1316's umbrella and kit slots, and M3-ENV-102's chapel box.
  - **Not mine, seen:**
    - Pell (Ch9 rocks) and Inquisitor Moll (the camp fight) are still capsules (characters, creatures-b);
    - Coilspire's Virel shows once before the binding and none after.
  - **Clean on the walk:** Tamsule, the galleries, Coilspire's interior (after the lamps), Ch9's strand and its dawn,
    the storm variants, and every arena from every angle.
  - **Sampling artifacts, not defects:**
    - views where the ground ray landed on a roof (Pemakar's forge lane, re-shot from the trigger's height: lit);
    - views starting inside an actor.
  - **Checks run:**
    - Godot `--filter=` pemakar 10/0, ch05 13/0, ashcrown 22/0, brine 5/0, ch06 5/0, ch08 25/0, ch09 13/0, flame 2/0,
      battle_arena 18/0, coilspire 11/0, zone_kit 13/0;
    - tools test_b_arenas, test_arenas, test_corrow_kit, test_coilspire_kit (+ the new lamp's glow allowance),
      test_ashcrown_kit;
    - validate_data 0/0, taskboard --check, gdlint.
  - **Checks skipped:** coverage (no battle/progression code).
  - **MERGE-READY @ 10eaddfc.**
- **BACKLOG EMPTY (10-30, the audit is clean in my lane):** every Ch5–Ch9 zone, variant and arena I own is walked and
  viewed, and what it found in my lane is fixed. The rest is filed (M3-ENV-1327, env-art) or belongs to other tracks
  (the capsules).

- **The Lead's big17 gate review (00:47), both items fixed:**
  - **Rejected `battle_arena_terrace`, the grey slab top left:** it was the near ash plume's coarse LOD1. The
    Pemakar kit's chain switches at 70 m and the forecourt sits about 110 m from the plume, while the zone overrides
    the plume to 900 m and the arenas didn't. `b_arenas.py` now keeps LOD0 to 900 m and narrows the plume to 0.75
    across, as the zone does, in both Ashcrown arenas. My own audit still of the forecourt showed it too; I'd missed it.
  - **`ch07_bell_moorings`, the white net on the dark water by the dock:** the drop's direct caustic web, cast along
    the sun past the catch-pool onto the harbour water. A new `under.radius_m` (14.5 m, the pool's coping at
    13.2 m plus a soft edge; 0 = unbounded, so the Reefball ball is unchanged) bounds it to the pool and coping.
  - **Checks run:** Godot water_sphere 5/0, tamsule 7/0, reefball 80/0; tools test_b_arenas; validate_data; gdlint.
    Self-rendered battle_arena_terrace, battle_arena_ashcrown_forecourt_day, battle_boss_intro_matron, ch07_bell_moorings,
    ch07_bell_galleries, tamsule_t01_bell_from_the_mouth: the slab is gone (the crest's slope over the wall instead),
    the dock water is clean, and the pool keeps its web.
  - **MERGE-READY @ 9fdf14f9.** The shots that drift by design: the six above.

- **Merged integration @ d987cc6b** (big17 approved; clean).
- **The PC's QA pass 3 (the Lead's 01:08 order: it comes first):** still running on the PC (`gpu/act1-qa-3` @ 84422d11
  has only extended the walk list; no results yet). The open rows on that branch are pass 1–2's, all fixed or
  explained in this log (6, 26, 27, 28 fixed; 15, 40 env-art's Ch1; 34 act1-chapters' lookup; 38 hero-integration's
  camera). I take pass 3's rows when they land.
- **Act II preparation (ADR 0203, docs only), done @ 808faa2c:** `docs/kb/plan/act2/zones/`, all `draft: pre-gate`.
  - Eight zone kit specs for my chapters (act2_tracks.md: env-art-b has Ch13–Ch16): Ansedra (with Ch14's night
    lagoon), the Sanctum, the Lamp Archive, the Lacquer Court, the open sea, Hollowmere's first visit, the Pale Rim
    and the Drowned Choir.
  - The arenas: three exist, plus a new `lacquer_court_steps` for the step-hold.
  - Each spec covers the piece list (existing versus new `b_*.py` pieces), the materials in Act II's palette (the
    flat gold, lacquer and window slots take zone looks, as in Act I), the lighting from the colour script, the reused
    kits, and a shot list.
  - **Found on the way:**
    - `lut_ch13_still` and `lut_ch16_rim` don't exist yet;
    - Hollowmere's Ch15 dawn needs its own grade (only Ch17's dusk exists);
    - several greyboxes are smaller than their kit pieces (the Sanctum's basin, the Lacquer Court, the barge deck,
      the Choir's ring at r 24 versus the art sheet's r 44) and need a one-time relayout;
    - the still mirror and the ripples are the hero rendering items.
  - **The Ch10–Ch12 kit inventory** (`inventory_ch10_12.md`): all 40 pieces built across four kits, three arenas
    with baselines, no zone dressed; flat slots in every kit (the fen's canopy and reeds, Lowlight's conduits and
    copper, Keth's grass and seep); zone grades exist only inside the arenas.
  - **Checks:** validate_data 0/0 (banned terms included), taskboard --check. No builds and no game files (ADR 0203).
  - **MERGE-READY @ 808faa2c.**
- **BACKLOG EMPTY (10-30 ~01:40):** Act I is clean in my lane, and the Act II preparation docs are written. Next:
  the PC's pass-3 rows for env-art-b when they land.

- **The PC's pass 3, early findings (the Lead, 01:50), all three fixed:**
  1. **`ch05_ashcrown_crown` / `crowd_zone_ashcrown`, the streaked bench and step faces:** the short rounded risers
     interpolate their vertex normals toward +Y, so the triplanar base and the salt detail took the top-down
     projection on near-vertical faces. The zone's `ashcrown_dressed_material` now uses the mesh's metre UVs (as
     `ac_ashlar` does), and neither stone copy takes salt (none reaches a volcano's crown). The shared weathering
     shader is untouched.
  2. **`brine_b05_barge_channel`, the white untextured hull:** `bs_barge_white` was a flat StandardMaterial. It's now
     painted lacquer over planking on the weathering shader: triplanar (the barge's small blocks have no plank UVs),
     paint 0.86, a little salt and algae at the waterline, still the only clean white in the zone. **This is a change
     to env-art's kit material table** (`assets_src/environments/kits/brine_shoals/bs_materials.py`, one entry), at the
     Lead's routing: the source is the only place that fixes the kit preview, my Ch6 zone and the camp arenas at
     once. The other 29 materials are byte-identical.
  3. **`battle_arena_coilspire_headland_path`, the dark flat slab behind the fight:** the arena ground's centre stands
     ~80 m from the fight, so its import chain (LOD1 from 70 m, measured to the bounds' centre) drew the coarse LOD1 as
     the backdrop. A new `zl.pin_lod0()` holds it at LOD0 to 2 km in the arena (b_headland_arena.py). This was also
     M3-ENV-1316's "headland far facets", and the reason scrub beyond 45 m floated.
  - **Checks run:** tools test_brine_shoals_kit, test_b_arenas, test_arenas, test_ashcrown_kit; validate_data; Godot
    ashcrown 22/0, ch05 13/0, brine 5/0, ch06 5/0, battle_arena 18/0.
  - **Self-rendered and viewed:** `ch05_ashcrown_crown`, `crowd_zone_ashcrown`, `ch05_ashcrown_forecourt`,
    `battle_arena_ashcrown_forecourt_day`, `brine_b05_barge_channel`, `battle_arena_coilspire_headland_path`. Clean
    risers; a painted barge; the headland's textured, scrubby slope behind the fight. These six drift by design.
  - **MERGE-READY @ f7d74a74.**

- **The PC's pass 3, published rows (`gpu/act1-qa-3` @ f56c2e82, big18), checked against my head:**
  - **45, 52, 53:** fixed earlier (the early findings above, @ f7d74a74).
  - **49 (Pemakar's night harbour near-black):** the preview's night grade takes its ambient from a near-black sky, so
    the layout's fill colour did nothing. The zone's copy now takes a colour ambient (as the day grade does), and the
    layout's rows carry a moonlit fill (`#6c7898` 0.6) and a brighter moon key (0.45, `#5a6c94`). Both are written by
    `ch05_pemakar_dressing.py` as one-key edits. The party now reads on the quay; the lamp pools and stars stay.
  - **51 (Ch9 grave mounds as blurry orange rectangles):** the old shrouds' woven texture is about 3 px a tile from
    the field camera. New `shroud_bound_a/b/small` pieces (`corrow/b_strand.py`) are tied cloth over a body, with
    folds, a firm hem and four ties, under a damp grey canvas look. `test_ch09_corrow_walkable` now counts them.
  - **62 (weir slabs flat grey boxes):** new `kit_weir_stone` (dressed volcanic stone, an algae band at the
    waterline) and the water spill on the weir, in the zone and the kit preview. **This touches env-art's
    `pemakar_layout.py`** (the weir row's `materials`, at the Lead's routing) and relaxes `test_pemakar_kit`'s slot
    check to accept a file in the kit's materials folder.
  - **63 (Matron intro: stretched mouldings, flat light-grey panel):** the mouldings were the dressed-stone UV fix
    (@ f7d74a74). The panel was the arena's near plume filling the loggia, so the court drops it; the loggia shows the
    crater rim and sky.
  - **50 (Toma sunk at Ashcrown's Crown spawn): not reproduced on this head; hero-integration's.** With the party set
    to Rhen, Asha and Toma and placed with `place_at` (the recipe in `test_qa_party_spawns`), `catch_up` lays them
    straight back along −X. Asha lands at (2.05, 42, −3.2) and Toma at (0.9, 42, −3.2), both on `Tier6`'s floor at
    y 42, which matches the visible tiles. No stair flight covers those spots (the t6 vein flights' heights sit
    +0.3 m above the floor). The one solid nearby that could look chest-deep is `release_lever`'s collider:
    1.39 m tall, centred at (6.0, −3.0), 2.8 m in front of the spawn. A follower placed on it would keep y 42 (the
    hit is above `step_m`). It's worth checking in the PC's own run. Also seen: at `AfterTortoises`, Toma is held
    1.34 m above `Causeway10` (floor −75.74, kept at the leader's −74.4).
  - **Checks run:** tools test_corrow_kit, test_pemakar_kit, test_b_arenas, test_arenas, plus every tools test that
    imports the changed generators (94 OK); validate_data 0/0; taskboard --check; Godot pemakar 10/0, ashcrown 22/0,
    corrow 18/0, zone_kit 13/0; gdlint and gdformat on the changed test.
  - **Self-rendered and viewed:** `battle_boss_intro_matron`, `battle_arena_ashcrown_anvil_court`,
    `ch09_corrow_strand`, `ch05_pemakar_harbour`, `ch05_pemakar_weir`, `pemakar_p11_sea_cut_weir_day`,
    `ch05_pemakar_harbour_day`, plus scratch field-height views of the harbour, the strand and the Crown spawn with
    the party. These drift by design.
  - **MERGE-READY @ 1a6934e3** (rows 45, 49, 51, 52, 53, 62, 63; row 50 routed to hero-integration).
- **Act I rows closed; Act II started (ADR 0205, the Lead's 02:26 order).** Claimed M4-A2P-043 (Ansedra, the
  Sanctum, the Lamp Archive) and M4-A2P-047 (the still mirror and the ripples) @ 1b855b13. Working from
  `docs/kb/plan/act2/zones/ch13_ansedra.md`: the new pieces in `b_ansedra.py`, then
  `tools/act2/ch13_ansedra_dressing.py`, the `ch13` grade and `lut_ch13_still`.
- **LEAD-ASK (Act II order):** the 02:26 order says "Ch10 first", but `act2_tracks.md` gives Ch10–Ch12 to env-art
  and Ch13–Ch16 to env-art-b. I'm starting my own first chapter, Ch13, and not touching Ch10's paths. Say so if
  you want env-art-b on Ch10 instead.
- **Ansedra (ch13) dressed, with the still mirror (M4-A2P-043 part 1 of 3; M4-A2P-047's still half):**
  - **New pieces** in `haluna/ansedra.py` (mine under act2_tracks.md): `ansedra_causeway_6m`, `gold_lamp_post`
    (an unlit salt-glass globe), `island_plinth_16m` and `mooring_platform` (water-steps, bollards, punt-pole
    trestles, the lacquered mooring arch). Built, imported, with manifest and provenance rows.
  - **`tools/act2/ch13_ansedra_dressing.py`** dresses the zone in the greybox's own frame. The walk surfaces are
    flat at y 0 and match the kit, so the greybox keeps the collision and **no story point moved**. It places the
    plinths, 18 causeway modules, 32 lamp-posts (one per lamp block), 15 bowl-domes plus the skyline ring, Sefir's
    hall (×0.6) and Corran's plainer timber hall (×0.45), and the two mooring barges (`bridal_barge` ×0.55; the
    plain `mooring_barge` alternative is the spec's open item for Narrative). The flat gilt and lacquers get zone
    looks, and the marble is cooled to `#E8E8E2`.
  - **The still mirror:** `overcast_lagoon` (absorption ×1.5, deep `#5E6E80`, the turquoise scatter muted) with no
    waves, ripples, foam or sun glint, roughness 0, and SSR out to 400 m. The domes stand doubled in the lagoon.
    **Not yet:** Ch14's ripple propagation (M4-A2P-047's second half).
  - **The ch13 grade:** `ansedra_environment.tres` (overcast, exposure 0.75, a colour ambient so the layout's fill
    row applies) and `lut_ch13_still.png` (written through `zone_lut`'s functions with my own grade dict;
    env-art's table is untouched).
  - **`ansedra.tscn`:** I added the `Water`, `Tide` and `Dressing` nodes (as in Act I; named in my ownership row).
  - **Shots (new, no baselines):** `ch13_ansedra_arrival`, `_moorings`, `_causeway`, `_mirror`, `_sefir_house`,
    `_corran_house` (rig `game/levels/_tests/ansedra_kit/ch13_ansedra_shots.tscn`). All self-rendered and viewed;
    the moorings shot was re-rendered after removing the sun glint's hotspot.
  - **Checks:** tools test_ch13_ansedra_dressing (new), test_ansedra and test_haluna_kit pass, plus every kit test
    that reads the build. **`test_npc` fails twice on this head (crowd_girl_teen's face distance and committed
    params). It came in with the integration merge, and nothing here touches the crowd.** Also: validate_data 0/0;
    taskboard; Godot ansedra 4/0 (new test_ansedra_dressing: the routes walk, the kit covers the greybox, the lagoon
    is still), ch13 4/0, act2 5/0, zone_kit 13/0, party_spawns 3/0, placeholder 8/0, dressing 18/0, water 48/0.
  - **MERGE-READY @ 86e01d57.**
- **The Sanctum of the Level (ch13) dressed (M4-A2P-043 part 2 of 3):**
  - **New pieces** in `ansedra.py`: `sanctum_nave_bay`, `sanctum_nave_floor`, `sanctum_basin_nave`,
    `sanctum_vestibule`, `sanctum_bench`, `sanctum_apse` and `cantor_stand`. The spec reused `lowlight_nave_bay`, but
    that bay is Lowlight's flooded temple (floor 0.45 m under the datum, walls at ±9, niches, conduits), so the nave
    is its own.
  - **No relayout:** the spec asked to move the nave to the kit's square basin. Instead, `sanctum_basin_nave` is
    built to the greybox's 10 × 18 m, and its rim *is* the kneeling ledges (same footprint and height). The greybox
    keeps the collision and every story point stays.
  - **The light:** six steady `glimmer_bound` omnis in the basin (specular 0, so no hot points on the mirror), a
    dimmer bound core under the salt-glass, the basin's still water at y 0.3, an interior grade (exposure 1.0) and
    `lut_ch13_sanctum`. `ZoneKitDressing`'s `fire_lights` take an optional `specular` (one line).
  - **Requested of chapters: M4-A2P-103.** The layout's light rows are chapters' (`ch13_greybox.py`, "do not edit
    by hand") and today they are daylight (sun 1.6). Until they're changed, a sliver of sun crosses the vault in the
    gate and basin shots. A scratch render with the requested values (sun 0, fill `#8A96A4` 0.2) showed the nave lit
    only from below, as the spec asks.
  - **Shots (new):** `ch13_sanctum_gate`, `_basin`, `_vault`. All viewed (re-render after M4-A2P-103 lands).
  - **Checks:** tools test_ch13_sanctum_dressing (new), test_ch13_ansedra_dressing, test_ansedra and test_haluna_kit
    pass; validate_data 0/0; taskboard; gdlint and gdformat. Godot: sanctum 3/0, ansedra 4/0, ch13 4/0,
    zone_kit 13/0, dressing 21/0, placeholder 8/0, party_spawns 3/0.
  - **MERGE-READY @ f5675f19.**
- **The Lamp Archive (ch13) dressed; M4-A2P-043 → review (rendering):**
  - **New pieces** in `ansedra.py`: `archive_case` (on every greybox `Stack` block; black lacquer, red shelves, runs
    of ledgers), `archive_hall_bay` (open clerestories, so grey daylight is the only light, and a skinned vault),
    `archive_end_walls` (the shut door), `reading_table`, `roll_table` (the Cantor roll) and `ledger_stack`. The
    spec's `archive_stacks` and `lowlight_nave_bay` didn't match the greybox's blocks and walls, so I built to them.
  - **`tools/act2/ch13_archive_dressing.py`:** in the greybox's frame, no story point moved, under Ansedra's grade
    and looks. No lamp is lit.
  - **Fixed in passing:** `_paving` now lays a bedding slab where a floor has no block under it (the Archive bays,
    the Sanctum's floor and vestibule showed the dark through their joints). Paper is dry indoors (`PAPER_W`).
  - **Shots (new):** `ch13_archive_door`, `_aisle`, `_table`, `_roll`, all viewed. `ch13_sanctum_gate` was
    re-viewed after the bedding change. Known: shaded pages read a dim warm brown under the layout's warm 0.5
    ambient (chapters' row); the spec's day-by-day daylight variants (C6) are still to come.
  - **Checks:** tools test_ch13_archive/sanctum/ansedra_dressing, test_ansedra; validate_data 0/0; taskboard; gdlint
    and gdformat. Godot: lamp_archive 2/0, sanctum 3/0, ansedra 4/0, ch13 4/0.
  - **MERGE-READY @ 9b2f4e2f.**
- **Ch13 fix: no bier before Ch15.** `bridal_barge.py`'s canopy takes a `bier` switch, and a new target
  `bridal_barge_wedding` drops it. Ansedra's two mooring barges use it (they showed Tobin's bier before he dies).
  `bridal_barge` itself rebuilds byte-identical. @ 5ef3f163.
- **The Lacquer Court at the wedding (ch14; M4-A2P-044 claimed and in progress):**
  - **New pieces** in `ansedra.py`, all in the greybox's frame:
    - `court_ground` (the court, the terrace that carries the halls, the lagoon edge), `court_balustrades` (on the
      greybox's edge walls), `court_water_steps`, `court_colonnade_roofs`, `court_water_gate`.
    - `court_column`, solid: the greybox's columns aren't, so the party could have walked through red lacquer.
    - `court_gallery`, `wedding_dais`, `conclave_gallery`, `gilt_lamp_stand`, `stillguard_rack`.
  - **`tools/act2/ch14_lacquer_court_dressing.py`:** no mark moves (the spec's relayout isn't needed). It places
    three `lacquer_hall`s ×1.25, the wedding barge at the `Barge` block (deck −0.6), the pursuit barge moored off,
    the lit city, and eight lamp-stands, each with its light. The lagoon is Ansedra's still water at −1.0. The ch14
    grade uses `lut_ch14_wedding` at exposure 1.15: at the spec's 0.90 the court floor went black under the
    layout's fill (chapters' row).
  - **Caught before shipping:** my first court builder shadowed env-art's `build_court_ground` (the arena's
    `lacquer_court_ground`); `test_ansedra` caught it. Renamed; both glbs rebuild byte-identical, nothing shipped
    wrong.
  - **Shots (new):** `ch14_court_entry`, `_ceremony`, `_steps`, `_gate`, all viewed.
  - **Checks:** tools test_ch14_lacquer_court_dressing (new), test_ch13_ansedra_dressing, test_ansedra and
    test_haluna_kit; validate_data 0/0; gdlint and gdformat. Godot: lacquer_court 2/0, ansedra 4/0, ch13 4/0,
    zone_kit 13/0, dressing 25/0, placeholder 8/0, party_spawns 3/0.
  - **MERGE-READY @ 9fa8dce4.**
  - **Next, still in M4-A2P-044:** the after-the-trap `states` row (stands down, lights out); the ripples
    (M4-A2P-047's second half); the `lacquer_court_steps` arena; the `ch14_court_after` shot.
- **The first ripples (M4-A2P-047 → review, rendering):**
  - **The shader:** `water_surface_body.gdshaderinc` gains up to 16 ring sources (outward wave packets on their own
    clock, `ripple_now_s`), so a still water still carries them. With `ripple_count` 0 (the default) every other
    water is unchanged.
  - **`RippleField`** (`game/world/water/ripple_field.gd`, tuning in `game/data/vfx/ripple_field.json`): `strike()`
    sends a ring, and a `wake_target` drops a ring every 1.5 m. It works on its own copy of the water's material.
    Ansedra and the court carry a `Ripples` node (their generators write it).
  - **Shot (new):** `ch14_ansedra_ripple` (rig `ripple_shot_rig.gd`): the rings break the Sanctum dome's
    reflection. Viewed beside `ch13_ansedra_mirror`, which is unchanged.
  - **Requested of chapters (M4-A2P-104):** drive the field in the escape (the barge as `wake_target`, a strike per
    pole stroke), and add the court's `CeremonyLamps` / `CeremonyLampsFallen` blocks and the state row. Then I
    bind the stands and lights and add fallen stands.
  - **Checks:** Godot water 48/0, ripple 3/0 (new), environment_shaders 11/0, battle_arenas 10/0, ansedra 4/0,
    lacquer_court 2/0, sanctum 3/0; tools test_ch13_ansedra_dressing and test_ch14_lacquer_court_dressing;
    validate_data 0/0; taskboard; gdlint and gdformat.
  - **MERGE-READY @ b43b1610.**
  - **Next:** the `lacquer_court_steps` arena (the step-hold), written from my own table as Act I's Ashcrown arenas
    were (`b_arenas.py`'s pattern).
- **The step-hold arena `lacquer_court_steps` (M4-A2P-044):**
  - **How it's built:** `haluna/ansedra_arenas.py` writes it through env-art's `write_arena`, from the court zone's
    own placements, so the arena and the zone can't drift.
  - **The frame:** the fight is on the court's paving by the water-steps. Behind the enemy line stand the lit dais,
    the north colonnade and the Conclave's gallery (left, the enemy's side). Every lamp-stand is lit. The lighting is
    the escape arena's ch14 dusk, and Ansedra's looks go in through `KitSlotSwaps`.
  - **Hints:** `the_steps`, `the_gate`, `the_conclave`.
  - **A first render had the frame wrong.** A quarter turn put the side gallery and the open sea behind the fight,
    so it's now unturned. The barge and gate are behind the battle camera, and the hints turn to them.
  - **Registered** in `game/data/battle/arenas.json` (`scenes`). Added to `test_battle_arenas` (10/0: the flat
    floor and clear sightlines hold). Preview `preview_lacquer_court_steps.tscn`; shot
    `battle_arena_lacquer_court_steps`, viewed. The Stillguard shows as a stand-in capsule: it has no model yet
    (creatures').
  - **MERGE-READY @ a881234d.** **Correction:** that commit lacked the arena's provenance row, so `validate_data`
    failed on it. Fixed @ 003bb202 (that commit also carries the Hollowmere pieces' rows). Merge 003bb202 or later.
- **Hollowmere's first visit, Ch15's dawn (M4-A2P-045 → review, rendering):**
  - **New pieces** in `hollowmere.py`: `hm_dock_4m` with `_open_n`, `_open_s` and `_open_ns` variants (a floating
    plank walk on log pontoons), `pyre_raft` (unlit), `hm_ship` (the twin-hulled trader), `hm_supper_table` and
    `hm_oil_lamp`.
  - **`tools/act2/ch15_hollowmere_dressing.py`:** in the greybox's frame, no mark moved. The lagoon is 0.9 m under the
    walk, the lashed hulls' own deck height. Each dock module keeps a rail only where the greybox has one, so the
    jetty mouths and the gangway stay open.
  - **Placed:** 13 homes (on the three house platforms and in the lanes), windmills, tide-wheels, the Dace's frame at
    the edge, and the far flotilla. Six oil lamps are warm, each light at its flame, plus the supper's lamp, and four
    signal lamps are teal.
  - **The look:** the dawn grade with `lut_ch15_hollowmere_dawn` (fog 0.018, not the spec's 0.03, so the dock's far
    end still reads) and a grey-teal dawn water. `hollowmere.tscn` gets the `Water`, `Tide` and `Dressing` nodes.
  - **Shots (new):** `ch15_hollowmere_arrival`, `_dock`, `_lanes`, `_pyre`, `_supper`, all viewed.
  - **Checks:** tools test_ch15_hollowmere_dressing (new), test_hollowmere, test_kite, test_haluna_kit;
    validate_data 0/0 (after the fix); taskboard; gdlint and gdformat. Godot: hollowmere 2/0 (the dock to the pyre,
    a jetty to the father's door, lamps lit), dressing 27/0, placeholder 8/0, party_spawns 3/0.
  - **MERGE-READY @ bb1d7aca.**
- **Ch15's open sea at night (M4-A2P-045):**
  - **The barge:** `bridal_barge.py`'s canopy and bier take a shift, and `bridal_barge_sea` carries them mid-deck.
    The other two barges rebuild byte-identical.
  - **`tools/act2/ch15_open_sea_dressing.py`:** the barge at ×0.65 fits the greybox's 4 × 10 m deck, so no mark
    moves, and its bier lands on the greybox `Bier`. The sea is `night_sea` at the barge's waterline, sea-glow 0.12.
  - **The grade:** a starlit night with `lut_ch15_unlamped`, at exposure 1.4 against the spec's 1.10 (at 1.10 the bier
    and the party were black from the field camera, Act I's row 49). No light of any kind, per the rule.
  - **Shots (new):** `ch15_sea_deck`, `_bier`, `_wide`, all viewed.
  - **Checks:** Godot open_sea 2/0; tools test_ch15_hollowmere_dressing (open-sea cases) and test_haluna_kit;
    validate_data 0/0; taskboard.
  - **Requested of chapters (M4-A2P-105):** a `shoal` mark and the reveal's cue (the held dead: I'll make the Ebbing
    rig per-zone, with an attractor that follows Kerrid), and the dawn `variants` row (then I add the dawn grade and
    the bow's fog bank).
  - **MERGE-READY @ b49e37a5.**
- **The Pale Rim (ch16; M4-A2P-046 claimed, in progress):**
  - **New pieces** in `drowned_choir.py`: `pale_rim_strand` (the walked white sand under ankle-deep water, ±2.5 cm of
    relief, falling away to sandbars) and `rim_marker_pole` (the Cantors' bleached poles).
  - **`tools/act2/ch16_pale_rim_dressing.py`:** in the greybox's frame, no mark moved. It places the kit's flats out
    to the horizon, a cairn on every cairn block (Keth's, salt-crusted by slot looks: a bleached paint and salt over
    `keth_crag`), the poles, and the Hollowmere ship at anchor.
  - **The water:** the validated `pale_rim` look, lying still on Ansedra's zero-amplitude set. The lagoon's 10–13 cm
    swells bared the sand in 12 cm of water at the capture's wind time.
  - **The grade:** white overcast with `lut_ch16_rim` (written; it was missing).
  - **Shots (new):** `ch16_rim_ship`, `_wade`, `_cairns`, all viewed.
  - **Checks:** Godot pale_rim 2/0, dressing 31/0, party_spawns 3/0, placeholder 8/0; tools
    test_ch16_pale_rim_dressing (new) and test_drowned_choir; validate_data 0/0.
  - **MERGE-READY @ ab41c94b.**
- **The Drowned Choir waits on chapters (M4-A2P-106):** the greybox floor is flat, but the kit's amphitheatre has a
  flooded channel and six tiers to 2.15 m, and Kesh's and Sefir's marks stand on those tiers. It needs the spec's
  relayout (the marks to tier heights, a `collision_path` I'll write from the kit, the singers to r 44). Filed as a
  request with the exact asks.
- **Next:** what's open in my lane: Ch14's after-the-trap state (M4-A2P-104), Ch15's shoal and dawn (M4-A2P-105) and
  the Choir (M4-A2P-106) all wait on chapters. Meanwhile I'll make the Ebbing rig per-zone, so the shoal is ready
  when its mark lands.
- **Merged integration (big19) @ 8714e3bf.** `PROVENANCE.md` and `shots.json` were unions: all 31 of my shots are
  kept, 654 ids, all unique. Re-checked on the merged tree:
  - Godot: ansedra, sanctum, lamp_archive, lacquer_court, hollowmere, open_sea, pale_rim, ripple, battle_arenas 10,
    water 49, zone_kit 13, dressing 31, pemakar 10, ashcrown 22, corrow 18, all 0 failed;
  - every tools test of my generators and kits; validate_data 0/0; taskboard; lint.
- **The Ebbing reads a zone's own data (M4-A2P-045) @ 3c2ba4cb.**
  - `EbbingMotes.data_path` defaults to Ch9's file, and `ZoneKitDressing` passes `"ebbing": {"data": ...}` through.
  - `game/data/vfx/ebbing_ch15_open_sea.json`: one held field at the `shoal` mark under the barge, its attractor at
    Kerrid's hands. The open sea's dressing names it, and it plays when chapters' reveal cue names the mark
    (M4-A2P-105).
  - Godot ebbing 8/0 (new `test_ebbing_zone_data`), ch09 13/0, open_sea 2/0.
  - **MERGE-READY @ 3c2ba4cb.**
- **The Ch14–15 arenas carry the city's zone looks (arenas_ch13_16.md) @ c1ed49ad.**
  - `ansedra_arenas.py` also writes `ansedra_lagoon_escape` and `bridal_barge_night` from env-art's tables. Without
    the swaps they reproduce env-art's scenes byte for byte; with them, `KitSlotSwaps` puts Ansedra's gilt, lacquers
    and marble over the barges' and domes' flat slots.
  - Viewed beside their baselines: subtly richer lacquer and gilt, no regression. Both shots drift by design.
  - Godot battle_arenas 10/0; the tools test re-writes all three arenas and compares.
  - **Gotcha for env-art and the Lead:** re-running `arena_scenes.py` on its own rewrites these two without the
    swaps. Re-run `assets_src/environments/kits/haluna/ansedra_arenas.py` after it (it's in my ownership row).
  - **MERGE-READY @ c1ed49ad.**
- **PC QA pass 3, the rows still naming env-art-b (`gpu/act1-qa-3`), Act I first (ADR 0205):**
  - **65 (cost, mine alone): fixed @ edb18aae.**
    - The smoke columns now march 24 steps at High, not 32. By the PC's own figure (about 0.10 ms a column at 32),
      that's about 0.23 ms for three and 0.31 ms for four.
    - The Tamsule drop's profile keeps its refraction and caustic web at High, and leaves the god-ray FogVolume, the
      bulk of its 0.36–0.43 ms, to Ultra. The Reefball ball's base rows are unchanged.
    - Viewed beside their baselines: `ch06_brine_camp` and `tamsule_t01`/`t03` read the same. Godot sphere 5/0,
      smoke 3/0, tamsule 7/0.
    - **PC-QUEUE:** re-measure both at High 1440p.
  - **34 (`ch06_ridge_skippers` on the blank stage): not the arena.** `encounters.json` names `brine_shoals_afternoon`
    and the Shoal Skippers, and the arena is registered and loads. The fallback is the request path; the PC's own
    note ties it to battle-presentation's double-submit (the first still shows the Inquisitor's name plate).
  - **38 (Coilspire's camera at SpireBase, Tier2 and Tier4): the spawns are clear.** A probe of the zone's physics
    from each spawn found 12 m clear behind its facing at head height (the probe's reach), and no facing does better.
    The camera's pull-in isn't a collider behind the party, so it's the field camera's (hero-integration's) to trace.
  - **MERGE-READY @ edb18aae** (row 65; rows 45–63 were fixed earlier, see above).
- **BACKLOG EMPTY (10-30, session handoff `docs/kb/handoffs/2026-10-30-env-art-b-1.md`):**
  - No open Act I row is mine: 45–65 are fixed or traced. 34 is the request path, 38 the field camera, 50
    hero-integration's spawn.
  - Ch13 and Ch15 are dressed and with review, and the ripples are with review.
  - The rest of Ch14–Ch16 waits on chapters: M4-A2P-103 (the Sanctum's light rows), 104 (the escape's ripples and the
    after-the-trap blocks), 105 (Ch15's shoal mark and dawn row) and 106 (the Choir's relayout).
  - The looks only the PC can judge are queued.
  - The next step for each request is in the handoff.
- **GPU pass 4 (10-30, re-checked on big20 7dc3ab41 merged into this branch).** Pass 4 ran on big19, which had none of
  my pass-3 fixes.
  - 45 (crown steps), 52 (brine_b05 barge painted), 53 (headland textured), 62 (weir stone) and 63 (matron): fine on
    this head in self-rendered stills, so no change.
  - 49 (Pemakar harbour foreground black): the night fill goes from 0.6 to 0.8 (`ch05_pemakar_dressing.py`). The
    party reads from every spawn, and the quay foreground is lifted but still night-dark. It's a PC-QUEUE look.
  - 51 (Ch9 graves not readable): the shrouds were flat slabs at field range. They now have a rounded superellipse
    outline, are fuller (1.4) with a wider hem and shallower creases, and read as a row of bound mounds with rope
    ties from the strand spawn.
  - `lacquer_court_steps`' PROVENANCE row: it came in with big20 (one row, no duplicate added).
  - Ch16 Pale Rim: dressed (MERGE-READY @ ab41c94b, not in big20 yet). The Choir's amphitheatre stays mounted on
    M4-A2P-106: its kit pieces are built, and the zone's dressing slot is left empty until the relayout.
  - Checks: test_corrow_kit, test_pemakar_kit (50 OK), validate_data, taskboard; Godot --filter=corrow (18) and
    pemakar (10) pass.
  - **MERGE-READY @ c6abd321.**
- **BACKLOG EMPTY (10-30, after pass 4):** pass 4's Act I rows on my side are fixed or verified (above). Ch13–Ch16
  are dressed as far as the chapters allow. The rest waits on M4-A2P-103 to 106 (the mount points are in the handoff),
  and the looks are queued for the PC.

- **big21 FAST-TRACKs (10-30, on big21 6a8349e7 merged into this branch):**
  - Rows 45, 52, 53, 62 and 63, and the brine_b05 barge texture, were already verified fine on big20 in self-rendered
    stills (see pass 4 above). big21 doesn't touch them.
  - test_arenas (`bridal_barge_night`, `ansedra_lagoon_escape` not reproducible): `haluna/ansedra_arenas.py` writes
    them with the zone looks, as ownership.md says. They're now in `test_b_arenas.py`'s WRAPPERS with
    `lacquer_court_steps`, so test_arenas skips them and test_b_arenas reproduces them. Both suites pass (22).
  - test_ch14_16_walkable::test_hollowmeres_dock: the supper table stood on the line from the `supper` mark to the
    pyre-raft. It's now by the father's place against the south rail (42.0, 0.95). My own dock test now walks the
    north half through the supper mark. Godot --filter=ch14_16 (5) and hollowmere (2) pass. Viewed
    ch15_hollowmere_supper and _dock: the table stands by the rail, and the lane is clear.
  - Merge of big21: PROVENANCE.md, shots.json and ownership.md were taken as integration's (my side had only rows
    integration removed on purpose).
  - **MERGE-READY @ 7999fb30.**
- **BACKLOG EMPTY (10-30, after big21):** Ch16's Pale Rim is dressed (@ ab41c94b, in big21). What's left of Ch14–16
  waits on M4-A2P-103 to 106, and the looks are queued for the PC.
- **GPU pass 5 (gpu/act1-qa-5, run on big20; checked on this head with big21 merged):**
  - **Row 63** (a flat bright panel behind the Matron): it was the open crater loggia. A new kit piece,
    `loggia_screen` (`ashcrown/b_trial.py`), is the Tenders' black-lacquer wind lattice, and the anvil-court arena
    hangs it across the loggia (`b_arenas.py`). In `battle_boss_intro_matron` the opening now reads as a lattice
    window with the crater light through it. The moulding streaks don't show on lavapipe.
  - **Row 62** (the weir slabs flat grey): `kit_weir_stone` was in place but the shader's wet pass flattened and
    darkened the whole weir. Wet stone now keeps its relief (`wet_flatten` 0.15, `wet_darken` 0.75), and the weir
    gets per-block value 0.4, stronger relief, and wider salt and algae bands. The courses' pill shape (0.07 m radius on
    a 0.13 m half-height) and the flat water sheet over the crest are env-art's kit code: request **M3-ENV-1328**.
  - **Row 51** (the graves soft orange rectangles under the field camera): a red test showed the shrouds were
    full rectangular sheets. The superellipse had only lowered the corners. The shroud grid now maps onto its
    rounded outline, the cloth drapes the body more widely (10 passes), the grid is finer (1920 tris), and the
    canvas is cooler with a soft, coarser weave (at 1.7 its normal had shaded stripes that read as spikes). From the
    strand spawn they read as soft rounded bound mounds with rope ties.
  - **Row 34, the arena side:** `ch06_ridge_skippers` resolves to `brine_shoals_afternoon` and its own enemies on
    this head (test_act1_encounters_resolve passes). The arena scene and data are fine, so the GPU's sandbox fight is
    the request path's (act1-chapters).
  - Checks: test_corrow_kit, test_pemakar_kit, test_ashcrown_kit (the new piece's import settings), test_arenas,
    test_b_arenas, validate_data, taskboard; Godot --filter=corrow (18), ashcrown (22), arena (18) and
    encounters_resolve pass.
- **Ch16 Pale Rim: the `pale_rim_shallows` arena** (ch16.md names it for `ch16_rim_skates` and `ch16_rim_crawlers`;
  the gap was mine): `haluna/rim_arenas.py` writes it from the zone's dressing, sky, fog, water and `lut_ch16_rim`.
  The battle camera looks down the wade, with the cairn line into the white behind the enemy line. The id is in
  `arenas.json` `scenes`, with a preview, the shot `battle_arena_pale_rim_shallows` (viewed: white overcast, still
  water, cairns and poles into the fog) and a PROVENANCE row. Naming it on the two encounter rows is combat's:
  request **M4-A2P-107**. The Choir still waits on M4-A2P-106.
  - **MERGE-READY @ e1903b9e** (rows 51, 62, 63 @ e72c9631; the arena on top).
- **BACKLOG EMPTY (10-30, after pass 5):** my pass-5 rows are fixed, or handed off with a request (62's kit
  geometry: M3-ENV-1328). Row 34 is the request path's. The rest of Ch14–Ch16 waits on M4-A2P-103 to 107.
- **Player-height walk, Ch5–Ch9 (10-30, on big21 0347aa74+ merged into this branch):** 548 eye-height stills
  (every spawn, trigger and story mark, looking N, E, S and W) over the eight zones, all viewed on contact sheets.
  - **Fixed here:**
    - **Corrow (Ch8 and Ch9):** the Bastion's two end walls left a 0.5 m slit of sky between their 12 m
      segments (the end is 24.5 m). They now slide together to meet.
    - **The low town's black pools:** this was `corrow_far` showing through the town cells' hollows (they dip
      3.75 cm; the far ground lay 3 cm under the town). It's lowered 3 cm, and the pools now read as wet hollows.
    - **Tamsule's market cloths** (awnings, boat canopies, sun umbrellas) read as flat colour: the kit's cloths are
      92 % flat paint. The zone copies (`tamsule_cloth_*_material.tres`) show the weave through a sun-faded dye.
  - **Kit code, so requested from env-art:**
    - **M3-ENV-1329:** Brine Shoals' hard wet/dry lines where the channel tiles meet the mudflat tiles. A test
      showed it's the baked wetness, not variation or LOD. The task has a one-line patch.
    - **M3-ENV-1330:** Corrow's low town ground has per-triangle cobble patches with hard edges, which stop at the
      tile edges.
  - **Seen and left:**
    - **Ashcrown:** the plume is a lumpy grey mass seen close from the crown terraces.
    - **Coilspire:** north from the headland is the storm-graded flat of Corrow's far ground.
    - **Ch9's strand:** the shoreline is ruler-straight where the still water meets the beach's planar slope.
    - **Not walk views:** the marks out at sea, in the drop and inside actors (Kahre's heart).
  - Checks: test_corrow_kit, test_tamsule_bell_kit, test_ch08_flow, validate_data, taskboard; Godot
    --filter=corrow (18), tamsule (7), ch07 (18), ch08 (25) and ch09 (13) pass. Viewed `ch07_tamsule_market`,
    `ch08_corrow_flood` and `ch08_corrow_arrival`.
  - **MERGE-READY @ 008c7de3.**
  - Next: the same walk for Ch13–Ch16 once act1-chapters mounts them (the zones are dressed; the walk rig takes any
    zone and layout).
- **BACKLOG EMPTY (10-30, after the Ch5–Ch9 walk):** what's left from the walk is with env-art (M3-ENV-1328/1329/1330).
  Ch13–Ch16's walk waits on the mount, and the rest of Ch14–Ch16 on M4-A2P-103 to 107.
- **Eye-height walk, Ch13–Ch16, standalone (10-30, the Lead's order not to wait on mounts):** each zone scene was
  instanced alone at every spawn, trigger and mark (160 stills over 8 zones), plus the five Ch13–16 arenas from
  their hint cameras. All viewed.
  - **Fixed:**
    - **`lacquer_hall`** (Sefir's and Corran's houses, the court): one plain back-wall slab and the roof's bare
      underside read as flat navy in shade. The back wall is now five red panels in gilt rails on a black ground,
      with a beamed timber ceiling.
    - **Ansedra's red lacquer** is now satin over an oxblood undercoat; glossy over near-black, its shaded faces
      mirrored the grey sky.
    - **`archive_case`**'s plain black ends read as navy slabs down the Archive's aisles. They now carry a red inset
      in a gilt frame and a gilt label plate.
  - **Seen, fine:** the Lacquer Court at dusk, the Sanctum, the open sea, Hollowmere's dock, the Pale Rim, and all
    five arenas (the bridal barge's dark is by design).
  - **Mount points for act1-chapters** (story points stay theirs):
    - **Ch13 `corran_house`** (−44, −40.8) stands *inside* Corran's hall. The hall is built at 0.45, so its
      interior is about 1.9 m high, and at eye height the camera is under its shaded roof. Stand the mark at the
      hall's front, +X (about −41, −40.8).
    - **Ch16 Drowned Choir:** still greybox until M4-A2P-106 (the relayout to the kit's amphitheatre).
    - **Ch16 rim encounters:** need `"arena": "pale_rim_shallows"` (M4-A2P-107).
    - **The Ch13–16 zones' scenes** each instance cleanly alone, with their spawns
      (Ansedra 3, the Court 3, Archive 1, Sanctum 1, the open sea 2, the Rim 2, Choir 1, Hollowmere 1). Routing
      them in is chapters' mount; nothing on the dressing side blocks it.
  - Process note: an earlier Bash step waited on a permission prompt; this pass ran as plain single steps (no kills,
    writes only in the worktree and scratchpad).
  - Checks: tools test_ansedra, test_ch13_*_dressing, test_ch14_lacquer_court_dressing, test_haluna_kit and
    test_b_arenas (49) pass; Godot --filter=ch13 (4), ch14_16 (5), ansedra (4) and archive (2) pass.
  - **MERGE-READY @ 2d9a9c36.**
- **BACKLOG EMPTY (10-30, after the Ch13–16 walk):** the walk's findings are fixed or logged as mount points above,
  and the kit requests are with env-art (M3-ENV-1328/1329/1330). The rest waits on M4-A2P-103 to 107.
- **Walking into the water (the human's Oruvel playtest; on big23 8fe3644b merged, d4e21dde):** my zones' shores
  are kit terrain, not greybox walk blocks, so env-art's `zone_edges.py` (28b005ad) can't see them.
  `tools/act1/shore_walls.gd` (new) flood-fills the walkable ground from the spawns the way the controller walks
  (steps ≤ 0.35 m, blocked by anything at chest height), walls every edge onto water deeper than 10 cm, merges the
  runs and writes `<zone>_shore_walls.json`. The generator reads it into `edge_walls` (`zl.shore_walls`).
  - **Probed** (reachable cells whose ground lies more than 0.3 m under the water):
    - Pemakar: 463, on the beaches either side of the harbour (the quay itself was closed).
    - None in Brine Shoals, Ch8 Corrow, Ch9's strand and pier, Ansedra, the Lacquer Court (its water-steps end on
      the barge deck above the water), Hollowmere's dock or the open sea's deck. The Pale Rim's wade is in water by
      design.
  - **Pemakar:** 687 shore walls. Re-probed: 0 deep cells reachable. `tests/integration/test_shore_walls.gd` (new):
    one invisible body per row, and a body can't cross a sampled wall. Godot --filter=pemakar (10) and
    shore_walls (2) pass; test_pemakar_kit, validate_data and taskboard pass.
  - **MERGE-READY @ 02640c97.**
  - The Ch5–Ch6 eye-height walk and rows 62/63 were already done and pushed (above: 008c7de3, e72c9631).
- **BACKLOG EMPTY (10-30, after the shore walls):** what's left waits on env-art's kits (M3-ENV-1328/1329/1330) and
  on M4-A2P-103 to 107.
- **Ashcrown and Coilspire: floating props and stretching (10-30, the Lead's order):** a scratch probe measured every
  dressing piece under 8 m against the ground beneath it, then each flagged one was viewed.
  - **Ashcrown:**
    - **The problem:** 26 road graves (curbs and steles by the causeway's mid landings) floated 0.5–2.3 m over
      the slope. They were set on the analytic massif, and the crest's built mesh lies under it out there.
    - **The fix:** ZoneKitDressing gets an optional per-piece `"snap"`. After placing, a piece drops onto the
      ground under its origin, plus the offset. A terrain that collides as its LOD1 trimesh gets a temporary LOD0
      body for the snap, so props sit on the ground that draws, and walk collision is unchanged.
    - **Applied to:** the road graves (sunk 0.2 m) and the flank rock patches (−0.3).
    - Re-probed: 0 floating. Viewed: the curbs sit into the slope.
    - New test: `tests/integration/test_zone_snap.gd`.
  - **Coilspire:** nothing floats. The flagged wall lamps, flue keys, the niche and the beacon are wall-mounted, and
    the Watcher heads stand on the parapet, which has no collision under them. The scrub's 0.1–0.7 m was against
    the coarse collision; in view they stand on their stems.
  - **Texture stretching:** none seen in either zone's eye-height stills (the earlier walk plus these views).
  - Checks: Godot --filter=ashcrown (22), dressing (31), zone_kit (13), edge_walls, shore_walls and zone_snap pass;
    test_ashcrown_kit passes.
  - **MERGE-READY @ 4516750e.**
- **BACKLOG EMPTY (10-30, after the float pass):** the Ch13–16 water and dock edges were done in the shore-wall
  pass above, and rows 62/63 were already pushed. What's left waits on M3-ENV-1328/1329/1330 and M4-A2P-103 to 107.
- **Act II arenas at battle-camera angles (10-30):**
  - **Covered:** every Act II encounter's arena (`ossa_fen_roots`, `lowlight_engine_hall`, `keth_seep_terrace`,
    `bridal_barge_night`; `pale_rim_shallows` once M4-A2P-107 lands), plus my `lacquer_court_steps`,
    `ansedra_lagoon_escape` and `drowned_choir_ring`.
  - **Method:** each arena's battle camera and hint views rendered at 16:9 and 21:9. A scratch probe also
    measured every dressing piece against a temporary LOD0 collider of everything else, since arenas carry no
    collision.
  - **Floating:** nothing. What the probe flagged was standing in the sea (barges, domes, the water-steps and gate,
    the Rim's marker pole), resting on another piece's columns (the court's colonnade roofs) or mounted on a wall
    (Lowlight's conduit rail). The Choir singers' 7–9 cm is in the water.
  - **Gaps at the camera's edge and floor density:** my five arenas are clean at 21:9, and their floors (court
    paving, barge deck, ring tiles, the Rim's water) read at battle scale. Ossa Fen and Keth Seep are clean too.
  - **One blocker, env-art's:** in `lowlight_engine_hall`, the hall's own wall fills the left 45 % of the battle
    camera at 16:9 (an id pick says `Ground/engine_hall`). Request **M4-A2P-114**.
  - **MERGE-READY @ 34d374de** (the request; no arena of mine needed a change).
- **BACKLOG EMPTY (10-30, after the arena pass):** what's left waits on M3-ENV-1328/1329/1330 and M4-A2P-103 to 107
  and 114.
### PC-QUEUE
- Pass 3 row 65 (@ edb18aae): re-measure the camp's smoke columns (24 steps at High) and the Tamsule drop (High has no
  god rays now) at High 1440p against the 0.3 ms target.
- Act II looks only the PC can judge (M4-A2P-043/045/047 reviews): Ansedra's still mirror (SSR to 400 m) and the
  rings' cost; the Sanctum's upward-lit vault; Hollowmere's dawn fog density.
- The camp fires are alpha-blended now (M3-ENV-1326, `flame_tongue.gdshader`): add them to M3-RND-1315's cost check
  on the PC presets (two large and three small fires in `ch06/brine_shoals` and `salvage_camp_burning`).
- Carried: M3-RND-26's drop cost, M3-RND-21's four columns under 0.3 ms at High 1440p.

### Render requests
(Self-rendered per TRACK-RULES; lines are SELF-RENDERED notes.)
SELF-RENDERED @ 10eaddfc (audit on big18 + this head): about 700 zone stills across the eight Ch5–Ch9 zones and six variants, 56 arena stills, and before/after views of every fix (Kahre's door, Pemakar's quay, the shrine, the fires, the seawall joint, Coilspire's lamps). All viewed.
SELF-RENDERED @ 98d582ef (on a trial merge with act1-chapters @ 72254f9f): Coilspire's crown chamber from F07 and F06, before and after `ch08_virel_bound`. Viewed: one Virel before the binding, none after.
SELF-RENDERED @ cff5dfd3: ch05_pemakar_harbour, _harbour_day, _weir, _crown, ch05_ashcrown_causeway, _crown, ch06_brine_camp, battle_arena_ash_terrace_lanternfall, _camp, _shoals; ch07_tamsule_market, ch07_bell_galleries (gilt); a Ch9 low-town view (scratch, the flood debris). Viewed: no regressions; aged lacquer and worn gilt read.
SELF-RENDERED @ 2b882105: battle_arena_coilspire_tier_landing, _coilspire_headland_path, _ash_terrace_lanternfall. Viewed: the tier landing's pipes are verdigris over copper; the other two unchanged.
SELF-RENDERED @ 61c918b0: ch06_brine_camp, ch06_brine_road, ch07_tamsule_mouth, _market, _gantry, ch08_corrow_arrival, _stair, _flood, _lake, _storm, ch08_coilspire_hall, _gate, _storm, ch09_corrow_strand, _road, _landing, _rocks, battle_arena_camp, _shoals, _wall_head, battle_ch08_stair_hold, battle_boss_intro_reach, plus ~290 walk views (scratch). Viewed: lashed bales on the trader, translucent fire with torn licks, weathered red doors, verdigris and sea iron, a stone shrine; no regressions.
SELF-RENDERED @ a209511a: ch05_ashcrown_causeway, _forecourt, _tiers, _crown, _court, battle_arena_ashcrown_forecourt_day, battle_arena_ashcrown_anvil_court, battle_boss_intro_matron, plus 30 Ashcrown walk views (scratch). Viewed: the tiers' coursing and buttresses read in shade, the veins are streaked verdigris, the bowls aged copper; sunlit paving not blown out. None of these zone shots has a baseline yet.
SELF-RENDERED @ 26a674f8: ch08_corrow_arrival, _stair, _flood, _lake, _storm, ch09_corrow_strand, _road, _landing, _rocks, plus 44 scratch walk views and three bastion views. Viewed: the yard is paved and dressed, Ch9's rocks and rubble read as broken laterite, and nothing regressed.
SELF-RENDERED @ 50db241b: ebbing_n11, ebbing_n08 (new), plus a strand view (scratch). Viewed: cyan held motes over the harbour, mirrored in the still water and sinking seaward. N11's river overhead reads above and below the waterline, and nothing is gold or rising.
SELF-RENDERED @ 9c8e9c99: battle_ch08_stair_hold. Viewed: no capsule, and the anchors are invisible so the frame is unchanged. Also viewed `undertows_reach` at the default camera and the new `the_stair_head` hint (scratch): the head landing and its down-steps read clearly from the walk.
SELF-RENDERED @ 9a9c0043: battle_arena_camp, battle_arena_shoals. Viewed: the columns rise behind the camp, and the fires read as fire up close, with round beds and no trays.
SELF-RENDERED @ 3eaa64a5: ch06_brine_camp (clocks 40 and 44), ch06_brine_road. Viewed: grey-brown columns that lean downwind with lit tops, read at range, and billow between the clocks. The foot's grain is gone with the gradient-noise offset.
SELF-RENDERED @ f11aca7d: ch09_corrow_road. Viewed: the dawn road is a washed low gold looking east into the sun, slightly warmer than before.
SELF-RENDERED @ 51f5185c: ch06_brine_camp at clocks 40.0 and 40.37 (scratch). Viewed: the fires read golden-orange with torn tips that move between the clocks. It drifts from its baseline, which predates the fires.
SELF-RENDERED @ ce10e96a: tamsule_t01_bell_from_the_mouth, tamsule_t03_oruvel_moorings (drift by design: the cyan drop, the 0.8 m column), preview T02 and T05 (scratch), ch07_bell_galleries, ch07_bell_moorings, ch07_tamsule_gantry, ch07_tamsule_mouth — all viewed: the drop reads as held cyan water in every view, still, its light streaks the pool's coping white under it.
SELF-RENDERED @ ea946ec8: ch07_tamsule_mouth, ch07_tamsule_market, ch07_tamsule_gantry — new shots, read final (Liss and Kerrid are capsules: no field body yet).
SELF-RENDERED @ 00e15816: ch05_pemakar_weir, ch05_pemakar_harbour_day, ch08_corrow_storm, ch08_coilspire_storm, ch08_coilspire_gate, ch08_corrow_flood, ch08_corrow_lake, ch09_corrow_landing, ch09_corrow_rocks, ch09_corrow_strand — new shots (the strand is an existing baseline: no longer dark); viewed after fixes (re-aimed cameras, the flood lifted, the rocks' lamp). ch05_pemakar_harbour drifts by the new quay (the party's lanterns are the two glows).
SELF-RENDERED @ 4081127f: ch05_ashcrown_causeway, ch05_ashcrown_forecourt, ch05_ashcrown_crown, ch05_ashcrown_tiers, ch05_ashcrown_court, battle_arena_ashcrown_forecourt_day, battle_arena_ashcrown_anvil_court, ch06_brine_road, ch06_brine_camp — all new shots or a changed zone, all viewed. The anvil court arena was re-lit after viewing (interior fill 1.4, exposure 1.35, plus a forge-spill lamp over the fight floor); its first render had a black near half.
SELF-RENDERED @ 749bfc48: battle_arena_ash_terrace_lanternfall (votive lamps), ch05_pemakar_harbour_day and ch05_pemakar_weir (the leat), ch08_coilspire_storm and ch08_corrow_storm (the Undertow now drawn), ch09_corrow_rocks, ch09_corrow_strand and ch09_corrow_landing (the moon from the sea), ch05_ashcrown_court, _causeway and _crown (the loggia plume). All viewed, with before/after sheets for the moon and the plume. Plus a full contact sheet of the 25 Ch5–Ch9 zone shots to pick the weakest views.
SELF-RENDERED @ 8d198f1e: 53 arena angles (scratch hint rig) before and 30 after the fixes, all viewed: ash_terrace_lanternfall, salvage_camp_burning, seawall_stairhead_storm/hoist/surge, coilspire_headland_path, ashcrown_forecourt_day, ashcrown_anvil_court; 44 player-height walk views across the 8 zones; ch06_brine_camp (the zone burns), ch07_tamsule_market/mouth. A headland scrub ring out to 90 m was viewed and reverted (clumps floated).
SELF-RENDERED @ 6cd17ce3: battle_boss_intro_reach, battle_ch08_stair_hold, ch09_corrow_strand, ch05_pemakar_harbour, ch05_pemakar_crown (after the big13 merge), all viewed; the Lead's three gate notes are fixed.
SELF-RENDERED @ f51f81f2: battle_boss_intro_matron (the anvil court), battle_boss_intro_reach (the surge state, landfall storm), battle_ch08_stair_hold (the storm state), all viewed.
SELF-RENDERED @ 22b289bf: Virel in the Coilspire crown chamber (three scratch views) and ch08_coilspire_storm/_hall (unchanged), viewed.
SELF-RENDERED @ 8c535d1e: ch07_bell_galleries, ch07_bell_moorings (the weeping column reads), ch07_tamsule_gantry, ch07_tamsule_mouth (the column sits behind the gantry leg head-on), all viewed.
SELF-RENDERED @ 3be35a85: ch06_brine_camp, _road, ch08_coilspire_hall, _gate, ch08_corrow_arrival, ch09_corrow_strand, _rocks, battle_arena_underway, _underway_tower, _terrace, _ash_terrace_lanternfall, ch05_ashcrown_tiers (the GPU QA rows on this head), all viewed; hall, gate, rocks and Lanternfall re-rendered after the fixes.
SELF-RENDERED @ c6abd321: zz_pem_harbour, zz_pem_road, zz_pem_weir, zz_cor_strand (scratch spawn views), ch05_ashcrown_crown, crowd_zone_ashcrown, ch05_pemakar_harbour, ch09_corrow_strand, brine_b05_barge_channel, battle_arena_coilspire_headland_path, pemakar_p11_sea_cut_weir_day, battle_boss_intro_matron (GPU pass 4 rows on big20), all viewed; the strand re-rendered after each shroud change.
SELF-RENDERED @ 7999fb30: ch15_hollowmere_supper, ch15_hollowmere_dock, viewed (the supper table by the south rail).
SELF-RENDERED @ e1903b9e: battle_boss_intro_matron, battle_arena_ashcrown_anvil_court (the loggia lattice), pemakar_p11_sea_cut_weir_day (before, after and a tint test), ch09_corrow_strand plus the strand spawn view (scratch, each shroud step plus a red paint test), battle_arena_pale_rim_shallows (new), all viewed.
SELF-RENDERED @ 008c7de3: the Ch5–Ch9 eye-height walk (548 stills, scratch), Brine Shoals' variation, LOD and wet tests, Tamsule's cloth and Corrow's wall-slit and pool before/after views (scratch), ch07_tamsule_market, ch08_corrow_flood, ch08_corrow_arrival — all viewed.
SELF-RENDERED @ 2d9a9c36: the Ch13-Ch16 eye-height walk (160 stills over 8 zones, scratch), the five Ch13-16 arenas' hint views, lacquer_hall and archive_case before/after (scratch) — all viewed.
SELF-RENDERED @ 4516750e: Ashcrown's road graves before, snapped to collision, and snapped to the drawn crest; Coilspire's wall-end heads and a headland scrub clump (scratch) — all viewed.
SELF-RENDERED @ 34d374de: the eight Act II arenas' battle cameras and hint views at 21:9 and Lowlight at 16:9, plus the court balustrade and Lowlight conduit close views (scratch) — all viewed.
