# Live log: act1-chapters environment

Branch `claude/act1-chapters`, cut by the Lead from `claude/m2-slice` @ 6c50823f (2026-10-25). Integration branch:
`claude/undertow-lead-handoff-ze8rrn`. Binding rules: CLAUDE.md and `docs/kb/handoffs/live/TRACK-RULES.md` (on the
integration branch).

## Scope
Act I from **Ch4 onward**: Ch4–Ch9 (greybox, built by m2-slice) and the chapters after them; the greybox-to-final swaps
with env-art's Act I kits; Ch7's real Reefball match; real casts; encounters per chapter; the cutscene quality bar;
greyboxing Ch10 onward to the end of Act I. **slice-polish** (`claude/m2-slice`) keeps the M2 slice, Ch1–Ch3, the
cutscene sequencer (`game/cutscene/**`), `game/flow/**` and the playtest fixes.

- **Id block:** tasks 1200–1299 (e.g. `M3-C04-1200`), ADRs 0200–0209, handoffs `<date>-cinematics-act1-chapters-<n>.md`.
- **Paths claimed** (docs/kb/ownership.md, last row): `game/levels/ch04/**`–`ch09/**` and later chapters,
  `game/data/dialogue/ch04/**` onward, `game/data/flow/chapters/ch04.json` onward, `game/data/flow/ch0[4-9]_*.json`,
  `game/data/loc/ch04.csv` onward, `docs/kb/story/beats/act1_ch04.md` onward, the Ch4+ thread tests.
  **For slice-polish:** Ch1 (`game/levels/ch01/**`, `game/data/dialogue/ch01/**`, `ch01.json`) stays yours with
  Ch2–Ch3. Ch5 and Ch7's zones subclass your `Ch01Zone`; I won't edit it (I'll ask via a task if I need a hook).
- **The Act I switches** in `first_playable.json` stay EMPTY until the human signs off M2 (the Lead flips them). F8
  chapter select reaches Ch4–Ch9 meanwhile.

## NEW ACCOUNT (from 2026-10-25)
- **MERGE-READY @ 14ea50b9**: the integration branch (big8, c6a960ab) merged in (d7b55c10).
  Conflicts: encounters.json (theirs' arenas + Ch8's rows), voices.json (theirs + Ivo; the 17 Act I speakers' `pending`
  flags cleared now they're in speakers.json), translations (union, +ch08), validate_data (both sides' checks),
  test_hero_clips (the all-dialogue check with M3-CHR-01's pending list), the two different combat-14 handoffs (both
  kept; m2-slice's renamed `-cmb01`), balance_report (theirs). Ownership claim for Ch4+.
  - **Checks run:** `--import`; Godot `--filter=ch0` 59 run, 0 failed; validate_data 0/0; dlgc --check 0/0;
    taskboard --check; gdlint, gdformat clean; `tools.tests.test_hero_clips` 9 OK.
  - **Checks skipped:** the full suite and sim (the merge touched no battle code on this side; the Lead gates the
    integration merge); coverage (no game/battle or progression change of mine); Blender (no source); shots (no
    scene of mine changed).

- **PROGRESS @ e2fed1fc (2026-10-27): M3-C06-1200, Ch6 greybox → final (pushed, not yet MERGE-READY).**
  `ZoneKitDressing` (ADR 0200, `game/levels/act1/`) dresses a greybox zone with env-art's kit from a generated layout
  (`tools/act1/ch06_brine_shoals_dressing.py`), keeping the greybox's collision, triggers and states; story pieces
  follow their blocks. Ch6 takes the ch06 sun and grade. Request M3-ENV-1201 (six story pieces the kit lacks).
  - **Checks run:** `--filter=zone_kit` 5/0, `--filter=ch06` 5/0, `tools.tests.test_fog_lamps` OK, validate_data,
    taskboard, gdlint, gdformat clean. First lavapipe views made and viewed; fixes in (greybox stand-ins hidden, plank
    walk smoothed); the re-render is being viewed now, then two baselines are registered and a MERGE-READY line follows.

- **MERGE-READY @ 09233381: M3-C06-1200 Ch6 greybox → final, done (status review, reviewer environment).**
  Since e2fed1fc: greybox stand-ins hidden (an ember bed for the fire, crates for the purser; the shrine is the
  wreck's bow), a smooth plank walk, a dusk shot rig, Ch04Zone `ramps` + `collision_path` (for Corrow next),
  baselines `ch06_brine_road`, `ch06_brine_camp` (viewed, approved).
  - **Checks run:** `--filter=zone_kit` 5/0, `--filter=ch06` 5/0; tools test_screenshots + test_fog_lamps 19 OK;
    validate_data, taskboard, gdlint, gdformat clean; the two new shots captured in isolation and viewed.
  - **Checks skipped:** the full suite (only Ch04Zone, the Ch6 zone and new files changed; Ch04/05/07/08/09 zones
    inherit Ch04Zone's new `_build_blocks`: `--filter=ch0` 59 run, 0 failed); coverage (no battle
    or progression code); Blender (no source); other shots (no other scene touched).

- **Merged the integration branch (big9) @ 1b1caea0**: requested_clips union, encounters (theirs + Ch8's headland
  rows), the Lead's combat-20 renumber (my -cmb01 copy dropped). `--filter=ch0` 59/0, zone_kit 5/0.
- **MERGE-READY @ bf9267fa: M3-C08-1202 Ch8 Corrow greybox → final, done (status review, reviewer environment).**
  Corrow now stands on the seawall kit's heights in the kit's own frame (`tools/act1/corrow_frame.py`; the layout
  migrated once by `ch08_corrow_relayout.py`): the walk at y 12 among the Watchers, the Fisher Stair on the wall's
  inner face (ramps under 45°), the low town at y 1, the Bastion a platform at walk height dressed with outward
  seawall revetments, the mole's pier and ramp over the parapet, the stair breach from M3-ENV-04B on the fall.
  Ch06Zone light rows can swap the Environment (`environment_res`: the fallen grade). ZoneKitDressing gained per-piece
  `kit_dir` and trimesh colliders. Request M3-ENV-1203 (the mole, the Bastion's own pieces, kites, gate, nets).
  - **Checks run:** `--filter=ch08` 19/0 (with the new `test_ch08_corrow_walkable`: the mole, the walk, the stair
    both ways, the town lane, every mark on a floor); zone_kit 6/0; validate_data, taskboard, gdlint, gdformat;
    tools test_screenshots, test_fog_lamps OK. Baselines `ch08_corrow_arrival`, `ch08_corrow_stair` viewed and
    approved (captured before the PC-rendering directive reached me; none since).
  - **Checks skipped:** the full suite and coverage (no battle or progression code); Blender (no source).
- **PROGRESS @ 180510e1: M3-C04-1204 Ch4 ferry (WIP, not merge-ready until its shots are approved).** Dressed with
  the ferry kit and the Seventh Terrace; collision from the kit's hull constants; `test_ch04_thread` 11/0. The two new
  shots fail `test_screenshots` (no baseline) until the PC render comes back.

- **MERGE-READY @ 69c8a5e6 for M3-C07-1206 only** (cherry-pickable: `ch07.json`, `game/levels/ch07/tidecup_match/`,
  `ch07_tidecup.json`, the two Ch7 tests, the task files): Ch7's real Reefball match replaces the stand-in. TidecupMatch
  plays `tidecup_opening` through the HUD by path (M3-UI-01, on claude/ui, not yet integrated), else the engine's AI
  plays both sides; flags and reward per act1_ch07.md §5.4; back to CatchPool. Requests M3-PRG-1207 (Oruvel Float:
  no accessory slot exists), M3-RBL-1208 (the opponent is Sorrin in the story, Pemakar in the data; the §5.3 barks).
  - **Checks run:** `--filter=ch07` 8/0; validate_data, taskboard, gdlint, gdformat. **Skipped:** shots (no scene with
    a camera changed), coverage (no battle/progression code), the full suite.
  - **Ch4 (180510e1) is still WIP in this branch's head** until its render request is answered.

- **PROGRESS @ 77a6a777: M3-C09-1209 Ch9 corrow_night on the Corrow kit's fallen wall (WIP until rendered).**
  Strand of the drowned (sunk shingle banks), the landing at the breach, a bridge to Ch8's mole up to Liss at her cut
  hoist, the road as the walk east of the gate, the lake behind the wall; Iskarra's set moved 1700 m east. Shared
  `KitCollision` (Ch04Zone, Ch05Zone), `environment_res` in Ch05Zone variants (Ch9's dawn), `KitWalkProbe`.
  - **Checks run:** `--filter=ch0` 71/0 (thread tests Ch4–Ch9 and both Corrow probes); validate_data, gdlint, gdformat.
  - **Encounters (queue item 5):** `sim.py --check` on every Act I suite at 400 seeds: all in band but
    `ch08_flue_moths` naive (60.8% vs 20–60%); at 1000 seeds it is in band (58.4%; role_answer 93.2% vs 92). Near
    both edges; left as is. The 27 Act I creatures are all in the encounter tables (only Ch1's `wickfry` still
    carries its old id; the creature is `glassfry`: slice-polish's Ch1).
  - **Queue item 7 note for the Lead:** Act I ends at Ch9 (act_outline.md; Ch9's act card). Ch10 opens Act II (M4), so
    I'm not greyboxing it unless you say so; Act I polish (swaps, casts, cutscene bar) continues.

- **PROGRESS @ b30c2cf2: M3-C08-1210 Coilspire stood upright on its kit (WIP until rendered).** The greybox's flat
  tiers are now the kit's: the hall, landings at 9/18/27 m, the crown at 35, the gallery at 42.6, the path from the
  walk's end. Trimesh from the kit's shell/tiers/ground/hut plus ramp chains over the five flights and the path; the
  trial's gates across flights 1–4, its 14 keys on the kit's flue-keys (wheels spin with the Key blocks), braziers
  and their lights with the Flame blocks. `--filter=ch08` 19/0; `tools.tests.test_act1_kit_collision` 4 OK.

- **MERGE-READY @ 6a1501d5: the integration branch (big10, 7f187123) merged in.** One conflict (`voices.json`
  `wright`: took the integration's `pending: true`); flags, shots and baselines by `merge_union.py`. Re-imported;
  `--filter=ch0` 75/0, `--filter=zone` 57/0, gdlint/gdformat clean, validate_data 0/0.
- **Fixed @ 091623d8: the area-map POIs of ch04/brightwater_ferry and ch09/corrow_night** had stayed on the greybox
  positions after the kit relayouts (`tools.tests.test_zone_map_pois` was red): moved onto their sources, stale
  hints and bounds fixed. Request **M3-UI-1212** (role ui): let `ZoneMapShapes` read a kit zone's `collision_path`
  file, so kit zones' maps aren't thin.
- **PROGRESS @ 5112837a: M3-C07-1211 Ch7 the Bell's galleries on the Tamsule Bell kit (WIP until rendered).** The
  kit's arena frame; the party's gallery is the west (Oruvel's), the naming trigger on Oruvel's platform before the
  prow step where Tavi stands; Oruvel's moorings moved from azimuth 35 to 325 (the two runs of galleries are parted by
  the boat lanes, so 35 was unreachable from the party's side), with a boardwalk staging and bridge. Map-only pads
  and gallery "buildings" in the layout keep the area map drawn. `--filter=ch07` 8/0, `test_ch07_bell_walkable` 4/0.
- **PROGRESS @ 8daa0c63: M3-C05-1213 Ch5 Pemakar on its kit (WIP until rendered).** The kit's ten tiers in its own
  frame: a quay at the shore (kit wall/tread modules) with the Ch4 ferry alongside, the harbour road up the massif's
  rows to the first flight, ten flights as ramps; the story near the stair (the kit's tiers are dressing, not lanes:
  verandas and plinths close the lanes, roofs reach over the next tier), so the smithy trades places with the house
  by the stair and the inn moves along its arc to x −6.6. The Lanternfall night (388 lamps, 943 leaf-boats, far and
  sea lights) follows the `Lamps` block, which the day variant hides; the day uses the kit's dusk grade (M3-ENV-1214
  asks env-art for a day grade, the sea-cut weir, the wake-wall, the crown bell, a quay). ZoneKitDressing gained
  `multimeshes`, `far_lights`, per-light `color`, `trimesh_lod0`; KitWalkProbe now reads kit box colliders and can
  query the physics space for trimesh pieces. `--filter=ch0` 79/0, `zone` 58/0, `walkable` 13/0.
- **PROGRESS @ c0ee5230: M3-CIN-1217 villager casts.** ZoneCast puts the villager models on the Act I stage actors (`"cast"` on each actor row): Neme, Osu, Tavi as themselves, the rest as fisher, netmender, vendor, child, reed; heroes come from hero-integration (Rhen, Asha, Toma). Requests: M3-CHR-1218 (Garo, Marra, Hobb, Fenn, Ione, the Stillguard), M3-HER-1219 (Ysolde's field body). Also fixed: Ch7's galleries faced their story points the wrong way (an actor faces its -Z), 68406c91. `--filter=ch0` 79/0, `zone` 60/0, `walkable` 13/0.
- **FOR THE LEAD / m2-slice: M3-CIN-1221, a sequencer patch** (`docs/kb/tech/cutscene_mark_via.patch`, applies clean): `@mark <actor> <mark> via=<mark>,<mark>` walks a path as one eased walk turning at each corner (CutsceneSequencer, CutsceneMotion path helpers, `cues.json` `mark.via`, a unit test). Why: `test_act1_cutscene_walks` (6a016642) replays the Act I threads and finds 66 seen walks leaving the floor or passing through something (Corrow's mole rails and the Fisher Stair walked as a slope through the air, Pemakar's harbour to its crown, Tamsule's decks over the water, houses and tables in the greybox zones). The ones that need a path wait on this patch; I'm fixing the rest (marks, off-screen places) now (M3-CIN-1220).
- **PROGRESS @ 9ccd51b2: M3-CIN-1220, Act I cutscene walks.** 66 → 33 known, and every one left is a path: the
  `via=` cues are written as `docs/kb/tech/act1_walk_vias.patch` (36 cues, 19 `.dlg` + compiled), which applies on
  top of M3-CIN-1221's sequencer patch; with both applied the audit is clean bar the exempt `figure_gone`. Along the
  way: Coilspire's shell and tiers collide from LOD1 with the doorways from LOD0 (`collide_lod0_in`, triangles clipped
  to boxes), so the doors and all five flights walk (`test_ch08_coilspire_walkable`); Corrow's wall boxes overlap at
  the joints; Ch9 has a path down Pell's rocks; Ch5's scene-change walks start near the scene (`place_actor`);
  `tools.tests.test_ch08_flow` green again. `--filter=ch0` 83/0, `zone` 61/0, `kit` 30/0, `cutscene` 55/0.
  `tools.tests.test_screenshots` stays red until ch04_ferry_deck is baselined (the render below).
- **FOR THE LEAD / m2-slice:** after `cutscene_mark_via.patch` (M3-CIN-1221), apply `act1_walk_vias.patch` too and
  empty `known` in `tests/integration/act1_cutscene_walks_known.json` (or tell me and I will).
- **MERGED big12** (integration 7f355a8f) @ 18a11bc0; the full suite there: 2833 run, 2 failed, neither in act1-chapters'
  files (they come with big12): `test_creature_portraits` (mangrove_drowner, lamp_engine, avalanche_ram, wakefin have
  manifest portraits but no creatures.json rows) and `test_footsteps_slice_zones` (Ch2 causeway tidepool reads stone).
  Tools tests red on the integration branch too: `test_audio_loudness`, `test_shrine_gi_bake`, `test_screenshots`.
- **MERGE-READY @ 84352ccc: big12 merged (18a11bc0), M3-CIN-1220's walks (9ccd51b2), M3-CIN-1217's casts for every
  non-hero actor with a body (3e354c8c, 84352ccc), the Ch9 strand's light and Pemakar's harbour view.** Checks:
  the full Godot suite on the merge 2833/2 (the two big12 failures above, not act1-chapters'), then on 84352ccc
  `--filter=zone_cast` 3/0, `ch0` 84/0, `kit` 30/0, `zone` 67/1 (the same footsteps one), gdlint, gdformat,
  validate_data, taskboard, dlgc. `test_screenshots` waits on the render request below (ch05_pemakar_harbour).
- **MERGE-READY @ 5696ffde: Corrow's story boxes become env-art's pieces (M3-ENV-707/708).** Ch8: the barracks,
  the Order chapel, the chandler's stall, the trader, the wall-gate, the kites, Marra's step, the hoist's pins and
  basket, the net racks, the shrine and the mole (only Flood and Lake, the water, stay greybox). Ch9: the drowned in
  their rows (head to foot along each row: the rows are 1.5 m apart), the Stillguard's shields at their feet, a clay
  lamp under each vigil light, the Ebbing raft, Ivo's shroud, the coil, the milestone; the night's grade lift is now in
  the generator (copy_grades had been overwriting it). `--filter=zone_kit` 8/0, `corrow` 17/0, `ch08` 23/0, `ch09`
  11/0, `act1_cutscene_walks` 1/0, validate_data. Still greybox in Ch9: the landing, the rocks, the bridge, the lake,
  the burner. **@ 2d3ccdf2:** the Iskarra set is env-art's Iskarra (its drop-in scene's 20 pieces; ZoneKitDressing
  `scale_y`); `ch09_corrow_walkable` 5/0 (a test of the pieces), `zone_kit` 8/0, walks 1/0.
- **MERGE-READY @ 46b2f418: Ch6 has no greybox left** (M3-ENV-1201's pieces: the burning tide-wheel and its light, the
  fire, the purser's boat, the Level-stone shrine with its rest light, the chalk sign, the hatch). `zone_kit` 8/0
  (the Ch6 fire-light count now 5), `ch06` 5/0, `brine` 5/0. Requested **M3-ENV-1222** (env-art): Ch4's islet landing
  pieces and Coilspire's flue gates, niche seal and wright's mark, the last Act I story boxes without a kit piece.
- **ACT II STARTED: MERGE-READY @ e0358dc3, M4-C10-02 Ch10 greybox** (`ch10/ossa_fen`, `ch10/reedhollow`, from
  `tools/act1/ch10_greybox.py`): the fen's edge where Pell stops (act1_ch09.md §10), the root-walks, the Drowner's
  clearing, the way on; Reedhollow's causeway, lagoon ring, houses and shore. `chapters/ch10.json` (the chapter
  becomes 10; there and back; Pell out of Reedhollow), two flags, `loc/ch10.csv` (imported in project.godot: one
  translation path appended), `locations.json` rows. `--filter=ch10` 3/0 (thread, walkable), validate_data,
  test_chapter_flow, test_locations_validate, test_zone_map_pois, test_loc_literals. Requested the beat sheet
  (M4-C10-01, narrative). Pell isn't a party hero yet (M3-C09-07), so he's not in the formation. Ch9's act break
  still ends on the end card: switching it to Ch10 is the Lead's call (Act I switches stay empty).
- **MERGE-READY @ 27b9a4c7: M4-C11-02 Ch11 greybox** (`ch11/sunken_vey`, `ch11/lowlight`, from
  `tools/act1/ch11_greybox.py`, sharing Ch10's builders): the drowned galleries and the conduit court (Liss's
  housing-mark), the fig-choked side gallery; Lowlight's atrium (the lamp bench), the Lamp Engine's hall, the
  well-shaft's flights (ramps) down past the waterline to the drowned sanctum (Nhoa). `chapters/ch11.json`, two flags,
  `loc/ch11.csv` (project.godot: one more translation path), `locations.json` rows. `--filter=ch11` 3/0, validate_data,
  the chapter/location/map/loc tools tests. Beat sheet requested (M4-C11-01, narrative).
- **MERGE-READY @ 1e802dcb: M4-C12-02 Ch12 greybox** (`ch12/keth_pass`, `ch12/quellan`, `ch12/cloudloom`, from
  `tools/act1/ch12_greybox.py`): the pass's switchback flights, pass-cords, knotted post, the Ram's shelf under the
  seeping Lit Age wall, the saddle; Quellan's street, inn and road north; Cloudloom's weaving-hall, keth and Hesk's dais.
  `--filter=ch12` 4/0, validate_data, the chapter/location/map/loc tools tests. Beat sheet requested (M4-C12-01).
- **MERGE-READY @ ab243228: M4-C13-02 Ch13 greybox** (`ch13/ansedra`, `ch13/sanctum`, `ch13/lamp_archive`, from
  `tools/act1/ch13_greybox.py`): the moorings (Kerrid's nights), the causeways, Sefir's house, Corran's old house, the
  mirror lagoon's gold domes; the Sanctum's still basin, Ethren's and Corran's places (Kerrid kept out by `party` steps:
  a zone's own `party` only fills an empty party, noted on M4-C10-02 for Pell); the archive's tables. `--filter=ch13`
  4/0, validate_data, the chapter/location/map/loc tools tests. Beat sheet requested (M4-C13-01).
- **MERGE-READY @ a4410fd9: M4-C14-02, the rest of Act II's greybox (Ch14-16)**: the Lacquer Court
  (`ch13/ansedra_lacquer_court`), the open sea (`ch15/open_sea`), Hollowmere's first visit (`ch17/hollowmere`, Act
  III's zone), the Pale Rim and the Drowned Choir (`ch16/*`); `chapters/ch14.json` .. `ch16.json` chain court → sea →
  Hollowmere → Rim → Choir, each arrival setting its chapter. A shared test base (`tests/integration/
  act2_greybox_case.gd`); `--filter=ch14_16` 5/0, validate_data, the chapter/location/map/loc tools tests. Beat sheets
  requested M4-C14-01 .. M4-C16-01. **Act II now has a walkable greybox end to end (Ch10-16), story to come.**
  Full Godot suite @ a4410fd9: 2854 run, 2 failed, the same two big12 failures as above (not act1-chapters').
- **MERGE-READY @ 37789274: M4-C10-03, Ch10's field fights** on creatures' Act II roster: `tannin_archer`, `root_crab`,
  `fen_leech` (enemies.json, appended), three skills (skills.json, appended in its own commit 3a7a47c6 **for Combat's
  review**), three encounters and Ossa Fen's table; the three foes "silent" in creature_voices.json (appended, f3e1932d)
  until audio voices them (request M4-AUD-1001). Suites (1000 seeds, `--check` clean, loadout ch08_seawall): archers
  54.0/97.3, roots 33.8/93.9/99.9, leeches 48.5/99.9 (two role_answer bands report only, reasons in targets.json).
  Request M4-CMB-1001 (Combat): a drain on enemy skills for the leech. `--filter=battle` 720/0, `ch10` 3/0, balance
  and creatures tools tests.
- **MERGE-READY @ 52e5ee37: M4-C11-03, Ch11, Ch12 and Ch16's field fights** (Lead queue 00:13 item 3): seven regulars
  (`gallery_ray`, `rime_urchin`, `ridge_lynx`, `cord_moth`, `scree_crawler`, `glass_skate`, `rim_crawler`), five skills
  (skills.json, its own commit 2424ce9e **for Combat's review**), seven encounters, tables on Sunken Vey, Keth Pass and
  the Pale Rim (none in towns, the court or open sea); silent voices (6aa50b19, audio's file). All ten Act II suites
  `--check` clean at 1000 seeds (figures in the task file); four role_answer bands report only, reasons in targets.json.
  `validate_data` 0/0, balance and creatures tools tests, `--filter=battle` 720/0, `ch11`/`ch12` thread tests.
- **Lead queue (21:23), status:**
  1. Ch9 road capsule: it is **Kerrid** at the milestone (no model yet: M3-CHR-505, characters); so are the two on
     ch06_brine_road (Ysolde, no field body yet: M3-HER-1219; Kerrid). They go when those land; no villager body on a
     hero. The dark strand: brighter moon (1.25), fill and exposure, softer vigil lamps up on poles, linen shrouds
     (3e354c8c); re-render requested below.
  2. Off-floor walks: 33 left, all `via=` paths, written (`docs/kb/tech/act1_walk_vias.patch`); they need the
     sequencer's via support (`cues.json` mark.via), which is on claude/m2-slice, not on the integration branch yet.
     When it is merged I apply the patch and empty the known list.
  3. Ashcrown: waits on hero-integration's steep stairs (MERGE-READY @ bccce923, not on the integration branch yet).
  4. Capsule folk: every non-hero actor that a body exists for is cast (ZoneCast `creature:` and `hero:` casts: the
     hound, the Matron, the spar wraith as their creatures; the Stillguard, the watch, the officer, the inquisitor, the
     board-caller as villagers; Ch9's vigil Rhen/Asha/Toma as themselves). Left: heroes without bodies (Kerrid, Liss,
     Pell, Ysolde) and Ch8's storm figure (a cyan silhouette by design, not a person).
  5. **Act I balance at 1000 seeds: all 23 Act I suites, 97/97 bands ok** (`sim.py --seeds 1000 --check`, exit 0).
  6. Act II (Ch10+): next once 2-3 land. Requested the Ch10 beat sheet from narrative now (M4-C10-01), so it's ready.
- **Blocked swaps:** Ch5 Ashcrown (M3-C05-1215): the kit's flying stair is 48° and its vein stairs 60°, past the controller's 45°, so it needs a steep-stair traversal (request M3-ARC-1216). Ch4 `haluna_wake` belongs on the real Ch2 Haluna once it is ZoneStory (ADR 0035, slice-polish) with env-art's wake dressing (M3-C04-03); I'm not building a second dressed Haluna.
- **Ch7's port (`ch07/tamsule`) is waiting on a kit:** env-art's "Tamsule stilt" kit (M3-C07-04, role environment) is
  still todo. The galleries part of M3-C07-04 is done by M3-C07-1211. I'll compose the port from the Bell kit's port
  pieces and Oruvel's rafts only if the Lead wants it before env-art gets to it.

- **MERGE-READY @ adf680fa1: big14's gate failures in act1-chapters' lane fixed** (merged gpu/gate-big14-shots @ 36c5f5ec7):
  - test_act1_cutscene_walks: Asha and Toma staged at the dock before C4-06; three wake walks clean and off the known
    list; the lamps walk was fixed before the gate (712bc98a).
  - test_qa_save_shrines: the wake has a `Shrine` spawn, and Ch04Zone points the dressing's SaveShrine at the wake.
  - test_hero_field_snaps (haluna_wake): the floor probe put NemeDoor on a tree canopy 18 m up; it now takes the
    ground or a deck within 3.5 m of it, never a roof, a tree or the player. The drowned_choir pop (Act II) is the
    body, not the floor: request M3-HER-1230.
  - test_villager_routines (wake): the vendor within Osu's chat range.
  - test_battle_act1_ability_vfx: my ten Act II foes are `"act": 2` in enemies.json, and **battle-presentation: I
    added a one-line skip of act > 1 rows to your test** (its title and doc are Act I; Act II effects come with Act II).
  - test_qa_capsules: Pell in Ossa Fen and the Act II regulars listed known (ADR 0041). Haluna's own villager
    capsules (ch02/haluna) are slice-polish's.
  - Checks on the merged tree: act1_cutscene_walks, qa_save_shrines, zone_map, ability_vfx, ch04-ch09, hero_cutscene_snaps
    green; villager_routines' two Oruvel/layer await failures and the Haluna capsules are other tracks'.
- **MERGE-READY @ 548ba5222: Act I walks on their paths, and pacing** (details in
  `docs/kb/qa/act1_playthrough_ch04_ch09.md`, "Walks and pacing").
  - M3-CIN-1220 (review): M3-CIN-1221's `via=` landed in b2d39f8cc, `act1_walk_vias.patch` is in, and
    `act1_cutscene_walks_known.json` is empty. The dawn causeway is re-staged on the real Haluna (32d59e75d).
  - Pacing (d212b0413, 3c3839c84, 548ba5222): scenes no longer hold a frame, a black screen or a released camera
    while walks finish. Every Act I scene ends within about 11 s of its last step, on a visible walk; stuck_key's
    14 s is a harness artefact. Flow, mark and script staging changes: ch04 shell_is_set/dock/dawn, ch06
    raid/after_barge/liss_lantern, ch07 into_tamsule/after_the_bell/empty_moorings, ch08 landfall (party on the
    mole stair, MoleStair spawn; `test_ch08_thread` expects it)/spire_door/wall_falls/cut_rope.
    **For env-art-b:** the new and moved marks (`landfall_kerrid`, `MoleStair`, `figure_gone`, `W02`; Ch6
    `inq_halt`, `hound_halt`; Ch7 `drift_*`, `tavi_leaves`, `tavi_away`) are hand edits after the one-time
    relayouts. Keep them if you regenerate.
  - `tools/act1/cutscene_stills`: `STILLS_TIMING` (headless TAIL report), `STILLS_EVERY`, per-still debug
    positions; the plan runs in story order (flags needed and raised, trigger flags, reloads, beat triggers).
  - Request M3-CIN-1231 (slice-polish): an advanced line's box stays up through silent holds.
  - Checks: `--filter=` act1_cutscene_walks 1/0, hero_cutscene_snaps 1/0, ch0 107/0, ch04 13/0, ch06 5/0,
    ch07 18/0, ch08 25/0; validate_data, dlgc --check, taskboard --check, gdlint, gdformat clean;
    `tools.tests.test_chapter_flow` and `test_act1_poi_views` OK. Skipped: coverage and sim (no battle or
    progression code), shots (no manifest camera changed).
- **MERGE-READY @ 81b997807: the playthrough's third pass and the field POI pass** (Lead brief 10-28; details in
  `docs/kb/qa/act1_playthrough_ch04_ch09.md`).
  - Cutscene cameras (7000ae2b5): R08 off the waterline; W07 and W07_storm west of the gate (they sat inside the
    gate leaves, which have no collision); F08_key from the north, with Asha placed at the wheel (`great_key_asha`, a
    ch08.json `place_actor` before ch08_beacon_opened); N09 frames the standing mourner (the kneel is M3-C09-08 §5).
  - Field cameras: every Ch4–Ch9 zone map POI (69) rendered at the hub orbit's default view. The wake now uses
    ch02/haluna's own CameraVolumes (Ch04Zone rebuilds them from that scene's SceneState) plus Neme's door (c48cba476).
    Pan-follow `camera_volumes` were added where the orbit saw a sail, roof, wall or beacon: the ferry (775a44dd0),
    Pemakar's harbour (e66297f98), Tamsule's stilt lane, Corrow's wall-gate, the Coilspire (the hut, each tier, the
    gallery's two halves) and Ch9's road gate, milestone and wall head (3e43e1e71). **For env-art-b:** these are
    camera entries in the layouts (the act1-chapters lane); keep them if you regenerate.
  - Pacing scan: only pinned holds (ch08_wall_falls rule 4, ch09_the_stair ADR 0022 (f), the Ebbing). Balance: no spike
    or trivial fight showed, so no sim run.
  - Checks: `--filter=` ch0 107/0, zone 74/0, camera 54/0 (new `test_ch08_coilspire_camera` 2/0,
    `test_the_wakes_field_camera_is_halunas`), ch07 18/0, ch08 23/0, ch09 12/0, hero_cutscene_snaps 1/0,
    act1_cutscene_walks 1/0; validate_data, dlgc --check, taskboard --check, gdlint, gdformat clean;
    `tools.tests.test_chapter_flow` and the new `tools.tests.test_act1_poi_views` OK (`tools/act1/poi_views.py`, the
    POI pass as a tool). Skipped: coverage and sim (no battle or progression code).
  - SELF-RENDERED @ 81b997807: ch04_ferry_deck PASS 0.0014, ch05_pemakar_crown PASS 0.00002, ch04_haluna_wake_lane
    (no baseline: the lane at night with the folk under the lamps; approve at the gate), ch04_haluna_wake_feast (no
    baseline; re-aimed from east of the mats because a palm trunk crossed the old frame; approve at the gate).
    ch07_tamsule_quay and ch07_tamsule_lane are no longer in shots.json (env-art-b's manifest won the merge).
- **Playthrough (Lead brief 10-28):** `docs/kb/qa/act1_playthrough_ch04_ch09.md` (181 stills of every Ch4-Ch9 cutscene
  played in flow order, `tools/act1/cutscene_stills`; camera solver `tools/act1/shot_check`). Two passes fixed: the
  wake staging, Coilspire's cameras, 16 blocked shots, ch08_captain staged at the flooded stair foot (ADR 0022 (c)),
  Garo/Kerrid/Toma/Tavi framings, the dawn road. Open rows are listed there with owners and requests.
- **MERGE-READY @ 91f21337: the Act I chapter threads and cutscenes are clean.** All 39 `_thread` tests pass;
  `hero_cutscene_snaps` (ADR 0192, the merged suite) went from 6 new failures to 0: the wake's feast villagers face
  the wall's gap, Coilspire's tender and Liss face where they first turn, Liss stands 0.6 m back from the seized key
  (she stood on it), Ch9's Kerrid climbs the broken stair up instead of stepping down backwards, and Toma's run in
  ch08_beacon_opened ends before the fade (a 0.6 s hold). **For env-art-b:** those are NPC-placement yaw/point
  edits in `coilspire_layout.json` (tender, liss, t3_liss_wait, seized_key_liss) and `corrow_night_layout.json`
  (kerrid_stair, stair_climb); keep them if you regenerate. Known snaps (M2-HER-1113, the via walks) unchanged.
- **M3-HER-1145 done @ 41bc33e7** (the inventory's three act1-chapters rows): ch08_headland_gulls/crabs on
  `coilspire_headland_path`, ch08_flue_moths on `coilspire_tier_landing`; the static audit lists nothing for us.
- **Lead DECISION (10-28 02:35): env-art-b's Ch5–Ch9 dressing wins; dressing is env-art's (Prologue–Ch4) and
  env-art-b's (Ch5–Ch9) from now on.** Merged origin/claude/env-art-b, every conflict in tools/act1/ch0[5-9]_*, their
  generated json, `zone_kit_dressing.gd` (`waters`) and the Ch7 port's scene and rig taken from env-art-b; my Ch9 Lake
  node, lake material and waters test dropped; shots.json is theirs plus my two wake shots. Kept: my Ch4 work and the
  keep-list guard (re-pointed: Coilspire keeps Virel only). act1-chapters now owns encounters, NPC/trigger placement,
  cutscene staging and flow only. Superseded below: the Ch5–Ch9 bullets of the ADR 0041 batch.
- **ADR 0041 (Act I at final quality first), act1-chapters' batch @ f307b8a8, MERGE-READY.** My own audit
  (`<scratch>/a1/audit`: every visible PrimitiveMesh in each Act I zone and shot rig) drove it; tracks self-render now.
  - Ch9 (778fdd4e): the landing and the mole bridge decked in Haluna's timber on piles, the rocks Pell comes down as
    coral boulders, the vigil's brazier, the drowned low town as still water (a WaterSurface, not a box).
  - Ch4/Ch5 (6c012aee, f90e3df1): the islet's coral rock, a plank gangplank, a hatch for the stern gate, the name board
    laid on open deck (it and shot F06 were inside the kit's deckhouse; the party's marks moved with it); Pemakar's wake
    wall, weir and crown bell.
  - Coilspire (f90e3df1): valve doors across the four flights, the niche's slab, the wright's mark.
  - Ch7's port (0d8f0e2d, `tools/act1/ch07_tamsule_port_dressing.py`): decks on piles over a real river, the stilt
    lane, market, boats, the trader, the Bell on its gantry and the banks' shophouses (env-art's stilt kit M3-C07-04
    may replace the pieces later). New shots `ch07_tamsule_quay`, `ch07_tamsule_lane`.
  - Corrow (0737523e): ZoneKitDressing `waters` (a still WaterSurface following its block); the flood and the lake.
  - **Ch4's wake on the real Haluna (f307b8a8, M3-C04-1226)**: Haluna's dressing at night via the layout's
    `dressing` row, its walk collision (tuning read from ch02/haluna's Collision node), env-art's wake sets by flag,
    every story point and camera re-laid on Haluna; zone map POIs (UI's file, as for the earlier relayouts) and
    `test_zone_map`'s count (8). New shots `ch04_haluna_wake_feast`, `ch04_haluna_wake_lane`.
  - Guard: `test_act1_dressings_keep_only_blocks_that_wait_on_a_request` (each dressed zone's keep list names a request).
  - What still draws as a stand-in, all waiting on other tracks: Virel (M3-CRE-627), the weeping column and the storm
    (M3-RND-27), Kerrid (M3-CHR-505), Pell (M3-CHR-506), Liss (M3-C06-06 / M3-CHR-03), Sefir (M3-HER-1225); Ashcrown
    (steep stairs, M3-ARC-1216). Ysolde has her body now (vigil_ysolde cast).
  - Checks: `--filter=` ch04 12/0, ch05 8/0, ch07 12/0, ch08 23/0, ch09 12/0, kit_dressing 10/0, zone_cast 3/0,
    zone_map 20/0, battle 720/0; validate_data, taskboard, gdlint, gdformat clean.

## 2026-10-29 (new Lead session_01Bg3iP7cPGyjbX4CyniBahc; integration `claude/new-session-mj8c3c`)
- Merged `origin/claude/new-session-mj8c3c` @ b60a8f61 (65f76b85; pc-gpu.md taken from the integration branch).
- Filed requests checked: none landed on the integration branch since my last pass (it holds only Lead docs commits
  since big13; big16/17 are not merged yet). M3-CHR-505 (Kerrid) and M3-ARC-1216 (steep stairs) are in review and
  were already in my tree; re-verified in the fresh playthrough below.
- My five kit-swap tasks (M3-C04-1204, C05-1213, C07-1211, C08-1210, C09-1209) to review (94beed00): their shots
  have baselines from the Lead's gates.
- **MERGE-READY @ c56cce89: ch04_the_ink's H15 close-up was filled by Rhen's hip.** The ink trigger's centre is
  Ysolde's own spot at the wall gap, so the player stood between the lens and her hand. The flow now places him at a
  new `InkLamp` spawn just behind the camera, turned to her (`tools/act1/ch04_haluna_wake.py`, floors re-probed);
  `test_ch04_thread` checks it. Checks: `--filter=ch04` 13/0; validate_data, dlgc --check, taskboard --check,
  gdlint, gdformat clean; `test_chapter_flow`, `test_act1_poi_views` OK. Skipped: coverage, sim (no battle or
  progression code); shots (no manifest shot uses the ink scene). Stills re-render queued behind the full pass.
- Playthrough so far (Ch4, Ch5 Pemakar, Ashcrown): only the known rows (the derelict and harbour grades, Ashcrown's
  greybox). Ashcrown on its kit (env-art-b's M3-ENV-1303, reviewer cinematics) is in big16, not on the integration
  branch yet; reviewing it from a `lead/gate-big16` worktree next.
- **MERGE-READY @ 4b07cd09: the fresh playthrough's fixes** (details: `docs/kb/qa/act1_playthrough_ch04_ch09.md`,
  "Fourth pass"). All 40 `_thread` tests pass on the merged tree (title, Prologue, slice, Ch1–Ch16).
  - Ch6 (5a8a6d06, c13057f5): B10's party wades the channel with Rhen (`channel_*` marks, dawn beat), W10_dawn re-aimed;
    W06_after holds Liss in profile (the wrights walked into the old lens).
  - Ch8 (ba54943c): the kites stay up through the run back (W04_kite framed an empty sky); they come down with
    `ch08_wave1_held`. **Manifest shot ch08_corrow_storm can now show the kites** (its flags: arrived + beacon_opened).
  - Ch8 Virel (ed235044, my request M3-CRE-700-virel-field-body, was M3-CRE-627): `creature:virel` on `virel_coil`, `cast_still`
    (new ZoneCast row key), `Virel` dropped from Coilspire's `greybox.keep`, hidden after the binding.
    **For env-art-b:** the keep-list line in `tools/act1/ch08_coilspire_dressing.py` changed (the request named me).
  - Ch7 R07 and Ch9 D02 re-aimed (4b07cd09).
  - Checks: `--filter=` thread 40/0, ch04 13/0, ch06 5/0, ch08 25/0, zone_cast 5/0, kit_dressing 9/0,
    hero_cutscene_snaps 1/0; validate_data, dlgc --check, taskboard --check, gdlint, gdformat clean.
    Known reds not mine: qa_capsules (ch02/haluna's villager capsules, slice-polish), hero_field_snaps (drowned_choir,
    Act II, M3-HER-1230; Coilspire's PathFoot row re-routed to env-art-b as M3-HER-1129). Skipped: coverage, sim (no
    battle or progression code).
  - Viewed in re-rendered stills: F07 (46c9811b: Virel side-on, head to tail, Asha before her), F06_out (Asha alone),
    R07 (the walkway, Oruvel's side going out), D02 (Kerrid's face clear of the box), W10_dawn, W06_after, H15.
  - SELF-RENDERED @ 46c9811b: ch08_corrow_storm (no baseline: the kite lines now hang in the top of the frame, as
    the story has them at the run back; the Watchers read as silhouettes, the known storm grade M3-ENV-1229).
  - Ch1's stills (24, slice-polish's chapter): five frames show a wall, a post or nothing (O02, O09, U03, U09, U11);
    filed as M3-CIN-1232 (request to slice-polish). The rest read; the storm is M3-ENV-751's.
- **MERGE-READY @ f67d6134: Ashcrown on its kit, staged** (8fc911c7). M3-ENV-1303 was already on the integration
  branch (I first misread its frames as greybox). A02, A11 and A12 re-staged; Kahre's own body (`creature:kahre`,
  `cast_still`) stands behind the shut chamber door, seen only in A11; `chamber_in` sits in front of the door; seven
  POI camera volumes (shot_check solver). **For env-art-b:** hand edits in `ashcrown_layout.json` (shots A02/A11/A12,
  marks chamber_in/kahre_bound_at, actor kahre, camera_volumes): keep them if you re-run `--relayout`.
  M3-ENV-1303 reviewed (approved); M3-C05-1215 superseded (to review).
  - Checks: `--filter=` ch05 13/0, camera 54/0, zone_map 21/0, act1_cutscene_walks 1/0, zone_cast 5/0,
    hero_cutscene_snaps 1/0; validate_data, dlgc --check, taskboard --check, gdlint, gdformat clean;
    `test_act1_poi_views`, `test_chapter_flow` OK. Viewed: every Ashcrown still and POI view. Skipped: coverage and
    sim (no battle or progression code), manifest shots (no shot camera changed; the court's shut door hides Kahre).
- LEAD-ANSWERED (10-29): two task files shared the id M3-CRE-627. **My Virel request is now M3-CRE-700**
  (`docs/kb/tasks/M3/M3-CRE-700-virel-field-body.md`, status review, reviewer character); the Act II regulars file
  keeps M3-CRE-627. **For creatures:** review Virel's field body under M3-CRE-700. `test_zone_kit_dressing`'s
  Coilspire keep list is now empty.
- (superseded) IN PROGRESS: a fresh title → Ch9 headless playthrough (all `_thread` tests; Ch1 and Ch4–Ch9 cutscene stills).

### Render requests
DONE @ 180510e1 (viewed gpu/render-act1-chapters-180510e): ch04_ferry_derelict approved (df86873f); ch04_ferry_deck re-aimed (the camera stood 0.6 m from the ferrymaster), re-requested below
DONE @ 77a6a777 (viewed gpu/render-act1-chapters-77a6a77): ch08_corrow_arrival, ch08_corrow_stair, ch06_brine_camp pass (rmse 0); ch06_brine_road re-approved (its drift is the real hero model in front), ch09_corrow_road approved (df86873f); ch09_corrow_strand was near-black: vigil lamps and a brighter moon added, re-requested below
SUPERSEDED by the request @ c0ee5230 below: b30c2cf2
SUPERSEDED by the request @ c0ee5230 below: 5112837a
SUPERSEDED by the request @ c0ee5230 below: 8daa0c63
SUPERSEDED by the request @ c0ee5230 below: eeaf91bf
SUPERSEDED by the request @ 9ccd51b2 below: c0ee5230
SUPERSEDED by the request below: 9ccd51b2 (c0ee523 viewed: ch05_pemakar_crown and ch08_corrow_stair approved 160eadea; the rest were approved by big12)
SUPERSEDED by the request below: 225370ba
SUPERSEDED by the request below: 5696ffde
SUPERSEDED by the request below: 2d3ccdf2
RETIRED (TRACK-RULES 10-28 01:00, tracks self-render; rendered below) @ 760a0e4c: ch05_pemakar_harbour, ch06_brine_road, ch06_brine_camp, ch08_corrow_arrival, ch08_corrow_stair, ch08_coilspire_hall, ch09_corrow_strand, ch09_corrow_road; why: the one open request (TRACK-RULES), folding 225370ba and 2d3ccdf2: Pemakar's harbour view re-aimed, Ch6's last greybox now kit pieces, the casts (Stillguard, hound), Coilspire's key t4_d, Corrow's story pieces, Ch9's drowned, lamps, raft and its lit night
SELF-RENDERED @ c242d54d: ch05_pemakar_harbour (no baseline: the re-aimed harbour view reads, the stair and lit houses under Ashcrown's lamps; approve at the gate), ch06_brine_road PASS 0.0032 (Kerrid still a capsule, M3-CHR-505), ch06_brine_camp drift 0.0115 (Ch6's kit pieces in place of the last greybox; the Stillguard casts read as red robes at this distance), ch08_corrow_arrival drift 0.072 (the trader boat and the story pieces; the mole's top is flat, env-art's mole_pier), ch08_corrow_stair drift 0.0087 (Kerrid's capsule in the foreground), ch08_coilspire_hall PASS 0, ch09_corrow_strand drift 0.109 (the lit night: shrouds, lamps, the vigil; the landing still greybox, being replaced now), ch09_corrow_road PASS 0.0072 (Kerrid's capsule). For the Lead's gate: all intended.

- **MERGE-READY @ cb97a0cf: the Lead's three real-GPU QA rows** (act1_gpu_qa.md on gpu/act1-qa-2; brief 10-29 19:45).
  Integration merged @ ccf44ba4 (22994324).
  - **Row 34** (ae27be2f): doesn't reproduce on this head. New guard `test_act1_encounters_resolve`: every
    encounters.json `ch01_`..`ch09_` row (31) is started the way the field starts it (a pending BattleRequest, then
    field_battle.tscn) and plays on its own arenas.json scene against exactly its row's enemies; all pass,
    ch06_ridge_skippers included. The data was the same on the QA build, so that run met a battle scene with no
    request pending (the sandbox's own fight). PC-QUEUE below.
  - **Row 39** (de745039): Ch9's dawn state stood the stage Asha and Toma at the gate (road_asha/road_toma), so their
    followers stayed hidden and Rhen walked to the milestone alone. RoadGate's arrival now hides those stage bodies (the
    followers walk), and the road scene places them on near_asha/near_toma under its opening cut (viewed: D01, D02B).
    The gate's field view is the camera volume I added on 10-28 (viewed: along the road past the gate leaf). Ch4's
    battles already carry Rhen, Asha and Toma (`test_ch04_thread` asserts each request); Ch4's field staging of Toma
    (the wake, the ferry) is story staging. PC-QUEUE below.
  - **Row 23** (cb97a0cf): U03 clear of the post; O02 a two-shot from the scale hull's open side, with the Scale-Man
    moved out in front of the hull (he stood inside it, facing away); O09 Rhen and Kell, with Kell moved to the front
    of her stall (she stood inside it). M3-CIN-1232 updated: U09 and U11 stay with slice-polish.
  - Checks: `--filter=` act1_encounters_resolve 1/0 (exit 0), ch01 21/0, oruvel 17/0, ch09 12/0,
    hero_cutscene_snaps 1/0, act1_cutscene_walks 1/0; validate_data, taskboard --check, gdlint, gdformat clean.
    Skipped: coverage and sim (no battle or progression code).
  - SELF-RENDERED @ cb97a0cf: ch01_oruvel_dressed drift 0.0124 (the Scale-Man now stands visibly at his hull's front;
    intended), ch01_bell_room, ch01_scale_hull, ch01_kell_stall (no baselines: each frames its speaker). For the gate.

- **Lead (10-29 21:48, big18):** Coilspire's Virel stays my ZoneCast actor (env-art-b drops their duplicate dressing
  piece). Ch1's U03 and O02 (the Scale-Man) keep **slice-polish's** framing in big18 (they own Ch1 staging): don't
  re-apply mine (cb97a0cf's Ch1 hunks lose to theirs on merge). After big18 lands, if a speaker is still out of frame
  there, file a request to slice-polish with the still. O09 (Kell) is not named; check it after big18 too.

- **MERGE-READY @ ae713835: Kell's zone-map POI** (Lead, big18 gate 10-29 22:38). `zone_maps.json` ch01/oruvel
  `kell` moved to [29.0, -7.0] with her actor (cb97a0cf). `python3 -m unittest tools.tests.test_zone_map_pois`: OK on
  lead/gate-big18 with this row (5/0). On this branch alone the test still lists the eight ch04/haluna_wake rows as
  "source not found": big18 already fixes those (the wake's map row names its own layout in `points`, dd52da35), and
  they clear once that reaches the integration branch. For big19.

- **DONE (see `docs/kb/qa/act1_flow_pacing_pass.md`): the Lead's flow and pacing pass** (brief 10-29 23:10, on lead/gate-big18 @ d00d3284). Done so far
  (60b55833): `tools/act1/flow_audit.py` + `tools.tests.test_act1_flow_audit` (flags never set, read early, unreachable
  beats or triggers, unreached zones, orphan scenes): clean on big18 and here; orphans only the Reefball barks
  (M3-RBL-1208). Request **M3-CIN-1233** (slice-polish): the Prologue skips Ch1 and the slice's end card returns to the
  title, so Ch4–Ch9 can't be reached by play; one end_card block serves both end cards (Ch9's too).
  Pacing: no walked leg between beats over ~75 s. Ch1's dive may roll ~7 random fights (slice-polish's zone; noted).
  Balance sim, every Act I suite on big18: 138/138 in band; no wall (smart ≥ 84%), no walkover past Ch1's tutorial.
- LEAD-ANSWERED (10-29 23:31): yes; slice-polish makes it, act1-chapters reviews (run the `_thread` tests on it and view the Ch1 Drop and Ch4 NemeDoor arrivals in stills). Was: M3-CIN-1233: flip first_playable.json's M2 switch (Prologue → ch01/oruvel_underway @ Drop; the slice's
  end card → ch04/haluna_wake @ NemeDoor, Ch9's → the title)? It's slice-polish's file and the notes say the Lead sets it.

- Request **M3-CIN-1234** (slice-polish, the Lead's ask): Ch1's dive rolls ~4–5 random fights (130 m route, 18–34 m gaps); min 32 / max 52 gives ~3.

- **Act II preparation, docs only (ADR 0203; Lead 10-30 01:08):** `docs/kb/plan/act2/chapters/` (README + ch10..ch16,
  each `draft: pre-gate`): per chapter the flow outline (arrive rows, beats, flags, hand-offs), triggers and map POIs on
  the greybox frame, encounter tables (random density at ~3 per route, scripted fights with arenas, the Act II bands)
  and the field-camera plan (scene shots per zone letter, pan-follow volumes). Gaps found: the regular rows have **no
  arenas** (ch10–ch12, ch16 tables; Vey and the Rim need new arenas); Ch16's 254 m wade rolls ~6 fights without its
  montage cut; each act break needs its own end-card next stop. No game data touched. QA pass 3 (gpu/act1-qa-3) has no
  new rows yet; M3-CIN-1233 not MERGE-READY yet.

- **MERGE-READY @ fc564326: QA pass 3 row 23, ch01_bell_room** (Lead 10-30 01:50). U03 stood behind Rhen; it now
  faces him from 3.6 m (shot_check-solved) with the lantern on his shoulder, the listener of his monologue ("to the
  room, to the lantern, to nobody"). The hinge, 10 m off, carries his look off-frame. SELF-RENDERED: ch01_bell_room
  (no baseline: Rhen front-on, the lantern in frame) and the scene's still. `--filter=ch01` 21/0.
  - **For env-art (the Prologue–Ch4 zones):** the bell room's orange haze washes the frame and Rhen's face (the
    lantern's volume or the room's fog). Please bring it down; the shot is ready for it.

- **GPU QA pass 3 (gpu/act1-qa-3, on big18), my rows:**
  - **34 FIXED-PENDING-GPU:** ae27be2f (the encounter guard; data was right) is in lead/gate-big19.
  - **39 FIXED-PENDING-GPU:** de745039 (Ch9's road: Asha and Toma follow) is in lead/gate-big19. The gate camera is the
    10-28 volume (also in big19).
  - **23:** fc5643264 (ch01_bell_room U03 faces Rhen) is MERGE-READY, after big19. The haze asked of env-art.
  - **48:** the end card before Ch4 (F8 start) is M3-CIN-1233, slice-polish's. I review when they log MERGE-READY.
  - **49 MERGE-READY @ c9da92f3:** Pemakar's Harbour volume now looks seaward from the landward side (the old
    view looked into the quay's lamps, which bloomed over a silhouetted party), and Weir has its own volume across its
    lit quay (viewed: poi_views harbour and weir). **For env-art-b:** the harbour quay at the stair foot (x 0, z 22–26)
    has no fire light within 16 m (only the weir's lamp at 15.4, 23.5), so the party there stays dark until the night
    fill lands. Checks: test_act1_poi_views, test_zone_map_pois OK; validate_data clean.

- **MERGE-READY @ 3079abdcc (Lead 10-30 02:26, ADR 0205):**
  - **M3-CIN-1233 reviewed on lead/gate-big19: approved (done).** thread 40/0, act1_route 3/0, end_card 5/0; the
    Ch1 Drop and Ch4 NemeDoor arrivals viewed in stills. The stills harness drives M2-FP-121's time cards now
    (0e6fae230).
  - **Ch9's act card** is UI's ActCard on black (`#card`, ef0ca2337); test_ch09_thread accepts both (13/0 on big19,
    12/0 here).
  - **GPU QA row 49 (camera side): HELD.** c9da92f3f is reverted (2602bda20). The field camera never leaves a volume
    for the hub orbit, so the landward harbour shot stayed at InnGate and FromAshcrown and test_qa_field_camera went
    red. Request **M3-CIN-1251** (the director's owner, game/world/**) has the proposed patch and the Harbour and Weir
    positions to re-apply after it.
    - **LEAD-ASK:** M3-CIN-1251 needs an owner. game/world/** is the systems seat; you routed architect/tech to
      integration-qa. It affects play: walking out of any camera volume leaves the camera parked there.
  - **test_zone_cast** (red after the integration merge): the crowd layer's routines start in step (Tamsule's
    fisher and boatman both `haul` at 0.0). The test now accepts a routine clip but keeps the out-of-step check.
    Request **M3-CIN-1250** (creatures).
  - **Act II (ADR 0205), M4-A2P-010 claimed:**
    - Ch10's and Ch12's random fights name their arenas, and the encounter guard covers Act II (0388fcfd0). Vey and
      the Rim still need arenas (noted on M4-A2P-041 and M4-A2P-046).
    - Ch10's placement and cameras (25cf13c5f): every shot and volume shot_check-solved and viewed through the new
      ch10 rigs. The Kirru and Pell at Reedhollow are staged hidden until their bodies exist.
    - Next: Ch10's triggers and beats once story's scenes land (M4-A2P-001); the Drowner's enemy row and its sim
      band.
  - Checks:
    - `--filter=` ch10 3/0, camera 62/0 (after the revert), qa_field_camera 2/0, ch09 12/0, act1_encounters_resolve
      2/0, ch01 20/0;
    - validate_data, dlgc --check, taskboard --check, gdlint, gdformat clean;
    - test_chapter_flow, test_act1_flow_audit, test_act1_poi_views, test_zone_map_pois OK.
  - Still red here: test_zone_cast's out-of-step check (M3-CIN-1250, creatures).

- **MERGE-READY @ 40a8962cb: Ch10's Mangrove Drowner (M4-A2P-010, ADR 0205)**
  - **Data (9686fff6f):**
    - the enemy row on creatures' model and its `uprooted` phase: rooted (defence 120, Toma's Shell Breaker
      answers), uprooted at 55%;
    - five skills; `ch10_mangrove_drowner` on `ossa_fen_roots`; loc rows in ch10.csv.
  - **Sim** (1,000 seeds, ch08_seawall until the Ch10 loadout): naive 2.5%, role_answer 71.9%, smart 100% (report
    only with a 30-turn floor, as the Matron; logged in balance_targets.md; the 70–90% band needs M3-C05-06's
    escalation mechanic), p90 46.
  - **Flow (40a8962cb):** a clearing trigger runs the battle; the way on to Reedhollow requires
    `ch10_drowner_defeated` (declared).
  - **Checks:**
    - `--filter=` ch10 3/0, act1_encounters_resolve 2/0, creature_actor 30/0, boss 84/0;
    - `sim.py --suite ch10_mangrove_drowner --check` OK;
    - validate_data, taskboard --check, gdlint, gdformat clean;
    - flow_audit, chapter_flow, zone_map_pois OK.
  - Skipped: coverage (data only, no game/battle code).
  - **LEAD-ASK (combat review):** the smart-band exception. Same cause as the Matron; M3-C05-06 is the fix.

- **MERGE-READY @ 95a75dcf0: Ch11's shots, marks and field cameras (M4-A2P-011, claimed; 4e8ed0f8f).**
  - Sunken Vey: V02–V04 and the gallery and court volumes.
  - Lowlight: L02–L07, `pell_kneel`, and the atrium, hall, flight and sanctum volumes.
  - All shot_check-solved and viewed through the new ch11 rigs. The sanctum frames wait on Nhoa's and Pell's bodies
    to be judged.
  - Checks: `--filter=ch11` 3/0; validate_data clean; poi_views and zone_map_pois tests OK.
  - Next:
    - the Lamp Engine (enemy row, the conduit crawler adds, the repair effect M4-A2P-022) when combat's part-repair
      lands;
    - Vey's arena (M4-A2P-041);
    - then Ch12's placement and cameras.

- **MERGE-READY @ 555d62f76: Ch12's shots and field cameras (M4-A2P-012, claimed).**
  - Keth Pass: K02, K04, K05 (K01 is C1's breath); a climbing volume up each switchback flight; the shelf and saddle
    volumes.
  - Quellan: Q02 and two street volumes.
  - Cloudloom: C02, C03; the stair and hall volumes.
  - All shot_check-clear and viewed. Checks: `--filter=ch12` and the tools tests OK.
  - Next:
    - the Avalanche Ram's enemy row and sim band (its snow hazard is `field_rules` data);
    - Ch13's cameras (no fights).

- **LEAD-ANSWERED (10-30 03:44):**
  - M3-CIN-1251 is integration-qa's. They land it and tell me; I then re-apply row 49 (the Harbour and Weir
    positions are in the task).
  - Row 24 (the wake's spawn cameras) goes to integration-qa too, with my camera_volumes as the coordination point.
  - M3-CIN-1250 stays with creatures.
  - I hold the chapters combat seat.
  - **For battle-presentation (the provisional Act II boss rows):** the Mangrove Drowner already has its tuned row,
    skills, encounter `ch10_mangrove_drowner` and sim suite (9686fff6f, in band). Please don't add a second one:
    stage on that row. I review and tune the Lamp Engine, Ram and Wakefin rows with the sim when yours land.

- **Ch13 cameras (M4-A2P-013, claimed):**
  - Added A02–A06, S02, R02 and R03, all viewed. Marks for Sefir and Ysolde. Kerrid at the moorings on
    `ch13_guest_of_sefir`. Pan-follow volumes in all three zones.
  - **Fixed my own Ch12 red:** `test_qa_field_camera` failed on cloudloom:Hall (the camera sat beside the spawn) and
    keth_pass:Encounter (the origin return spawn sat outside every volume). I re-aimed the Hall and added Foot volumes.
    The test is green, and so are ch12, ch13 and layout.
  - Next: Ch14's cameras (W02–W07; the lagoon L01–L04 waits on the night variant).
- MERGE-READY @ 882564c90

- **Ch14 court cameras (M4-A2P-014, claimed):**
  - Added W02–W07 (viewed), `court_*` marks, the `Steps` spawn, and the Entry, Colonnade and Barge volumes.
  - field_camera, ch14 and layout are green.
  - Next: Ch15's open_sea and Hollowmere cameras (U02–U07, H02–H04).
- MERGE-READY @ 98088f53e

- **Ch15 cameras (M4-A2P-015, claimed):**
  - Added U02–U07 and H02–H04 (viewed) and the `Reveal` spawn (Rhen clear of U04).
  - Marks for the reveal, the bow, the confession and the supper. Deck, Dock and jetty volumes.
  - field_camera, ch14_16 and layout are green.
  - Next: M3-BPR-419 (battle-presentation's request on the Act II boss ids), then Ch16's cameras.
- MERGE-READY @ 65ea329f0

- **LEAD-ASK (merge note: the Drowner is on both act1-chapters and battle-presentation 1dbfed6d5):**
  - In enemies.json, skills.json and encounters.json, take **act1-chapters'** `mangrove_drowner`, `rising_water`,
    `drowner_drag`, `root_stamp` and `ch10_mangrove_drowner` rows. They are sim-tuned and in band (naive 2.5%,
    role 71.9%), with role_answer toma.
  - I've renamed my `root_lash`/`root_stomp` to battle-presentation's `drowner_drag`/`root_stamp`, so their VFX map
    keys stay valid. `tide_gather`/`drowning_grasp` have no VFX row yet (for battle-presentation).
  - In loc, drop the duplicate keys from **ch10.csv** and keep strings.csv's text: `ENEMY_MANGROVE_DROWNER`,
    `LORE_MANGROVE_DROWNER`, `PHASE_MANGROVE_DROWNER_UPROOTED`, `SKILL_RISING_WATER`. validate_data errors on
    cross-file duplicates.
  - After the merge I'll tune the Lamp Engine, the Ram and the Wakefin with the sim, and add their suites.
- MERGE-READY @ fd5b4414e

- **Combat seat: the provisional Act II bosses are tuned (1,000 seeds, in a scratch worktree of
  battle-presentation 1dbfed6d5):**
  - The values are in balance_targets.md ("Act II creature bosses"), with a reply on M3-BPR-419.
  - I apply them, and add the suites, once their rows are on the integration branch.
  - The Lamp Engine's role band stays report only until Liss's part repair (M4-A2P-022) exists.
  - Next: Ch16's cameras.
- MERGE-READY @ (this push)

### PC-QUEUE
- Row 34: on the real GPU, start ch06_ridge_skippers from the Brine Shoals field (a random fight) and confirm the
  arena and the Shoal Skippers.
- Row 39: on the real GPU, walk Ch9's road from RoadGate to the milestone (Asha and Toma follow) and look at the
  gate's camera with Rhen in it; check Ch4's fights show Toma.

## Exact next step
**BACKLOG EMPTY (2026-10-30 ~02:00):** the flow and pacing pass is done (`docs/kb/qa/act1_flow_pacing_pass.md`) and the
Act II chapter drafts are written (`docs/kb/plan/act2/chapters/`, pre-gate). Waiting on:
- **M3-CIN-1233** (slice-polish flips the M2 switch): when they log MERGE-READY, merge their head into a scratch
  worktree, run every `_thread` test, render stills of the Ch1 Drop and Ch4 NemeDoor arrivals, and write the review
  in the task's log.
- **gpu/act1-qa-3:** any new row for act1-chapters comes first.
- M3-CIN-1234 (Ch1's dive rate, slice-polish), and the filed Act I requests.
- At the `act1-complete` tag (ADR 0203): turn the Act II drafts into data, Ch10 first.

### Earlier exact next step
`docs/kb/handoffs/2026-10-29-cinematics-act1-chapters-1.md`). Every `_thread` test passes. Every Act I cutscene of
Ch1 and Ch4–Ch9 was viewed in flow-order stills, and every problem in my lane is fixed and re-viewed (the fourth pass in
`docs/kb/qa/act1_playthrough_ch04_ch09.md`). Ashcrown's POIs have camera volumes. What is left waits on filed requests:
M3-ENV-1228/1229 (night and storm grades), M3-HER-1225 (Sefir), M3-CHR-506 (Pell, on claude/characters), M3-RND-27/28
(the storm wall and figure), M3-CIN-1231 (the held box), M3-CIN-1232 (Ch1's five frames, slice-polish), M3-HER-1129
(Coilspire's ramp edge, env-art-b). Act II is paused (ADR 0041).
1. When any of them lands on the integration branch, re-run that zone's stills and POI views (commands in the
   handoff) and re-aim D06 at the name-board once the derelict's grade reads.

### Earlier exact next step (2026-10-28, superseded)
**BACKLOG EMPTY (2026-10-28, @ fe9bb143b):** in act1-chapters' lane, the Ch4-Ch9 playthrough is done. That covers
cutscene cameras and staging (three passes of stills), field cameras at every zone-map POI, every Act I walk on
the floor (known list empty), and pacing (no scene holds past its script beyond a visible walk ending). Ch1-Ch3 are
slice-polish's. The balance check had no trigger: no spike or trivial fight showed. Everything still open waits on
another track's request (below), and Act II is paused by ADR 0041.
1. Nothing left in my lane on the Ch4–Ch9 playthrough list. Every open row waits on another track, each with its
   request: the derelict's and Pemakar harbour's night grades (M3-ENV-1228, M3-ENV-1229); Ashcrown's kit and its
   field volumes after it (M3-ARC-1216); the kneeling mourners for N09 (M3-C09-08 §5); the stand-ins (Virel
   M3-CRE-627, Kerrid M3-CHR-505, Pell M3-CHR-506, Liss M3-C06-06, Sefir M3-HER-1225, the storm figure M3-RND-28,
   the column and storm M3-RND-27); drowned_choir's body pop (M3-HER-1230); the freed sequencer cast (M3-HER-1227).
2. When any of those lands: re-run `tools/act1/cutscene_stills` for that zone's visit and the POI views
   (`GODOT=<binary> python3 tools/act1/poi_views.py --zones <id> --render <dir>`: each POI's field view, its layout
   volume's camera or else the hub orbit), and re-aim D06 at the name-board (-9.24, 0.85, 21.04)
   once the derelict reads.
3. Act II is PAUSED (ADR 0041): its tasks and my requests for it are `status: blocked`, `blocked-by: ADR 0041`.
