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

## LEAD DECISION NEEDED: act1-chapters dressed the same zones in parallel (found 2026-10-28)
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
that test at this branch's zones. I stopped new Ch5–Ch9 dressing until this is settled, to avoid a third copy.

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

### Render requests
(Self-rendered per TRACK-RULES; lines are SELF-RENDERED notes.)
SELF-RENDERED @ ea946ec8: ch07_tamsule_mouth, ch07_tamsule_market, ch07_tamsule_gantry — new shots, read final (Liss and Kerrid are capsules: no field body yet).
SELF-RENDERED @ 00e15816: ch05_pemakar_weir, ch05_pemakar_harbour_day, ch08_corrow_storm, ch08_coilspire_storm, ch08_coilspire_gate, ch08_corrow_flood, ch08_corrow_lake, ch09_corrow_landing, ch09_corrow_rocks, ch09_corrow_strand — new shots (the strand is an existing baseline: no longer dark); viewed after fixes (re-aimed cameras, the flood lifted, the rocks' lamp). ch05_pemakar_harbour drifts by the new quay (the party's lanterns are the two glows).
SELF-RENDERED @ 4081127f: ch05_ashcrown_causeway, ch05_ashcrown_forecourt, ch05_ashcrown_crown, ch05_ashcrown_tiers, ch05_ashcrown_court, battle_arena_ashcrown_forecourt_day, battle_arena_ashcrown_anvil_court, ch06_brine_road, ch06_brine_camp — all new shots or a changed zone, all viewed. The anvil court arena was re-lit after viewing (interior fill 1.4, exposure 1.35, plus a forge-spill lamp over the fight floor); its first render had a black near half.
