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

### Render requests
(Self-rendered per TRACK-RULES; lines are SELF-RENDERED notes.)
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
