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
  6. Act II (Ch10+): next once 1-3 land; no Ch10 beat sheet exists yet, so the first step is a request to story.
- **Blocked swaps:** Ch5 Ashcrown (M3-C05-1215): the kit's flying stair is 48° and its vein stairs 60°, past the controller's 45°, so it needs a steep-stair traversal (request M3-ARC-1216). Ch4 `haluna_wake` belongs on the real Ch2 Haluna once it is ZoneStory (ADR 0035, slice-polish) with env-art's wake dressing (M3-C04-03); I'm not building a second dressed Haluna.
- **Ch7's port (`ch07/tamsule`) is waiting on a kit:** env-art's "Tamsule stilt" kit (M3-C07-04, role environment) is
  still todo. The galleries part of M3-C07-04 is done by M3-C07-1211. I'll compose the port from the Bell kit's port
  pieces and Oruvel's rafts only if the Lead wants it before env-art gets to it.

### Render requests
DONE @ 180510e1 (viewed gpu/render-act1-chapters-180510e): ch04_ferry_derelict approved (df86873f); ch04_ferry_deck re-aimed (the camera stood 0.6 m from the ferrymaster), re-requested below
DONE @ 77a6a777 (viewed gpu/render-act1-chapters-77a6a77): ch08_corrow_arrival, ch08_corrow_stair, ch06_brine_camp pass (rmse 0); ch06_brine_road re-approved (its drift is the real hero model in front), ch09_corrow_road approved (df86873f); ch09_corrow_strand was near-black: vigil lamps and a brighter moon added, re-requested below
SUPERSEDED by the request @ c0ee5230 below: b30c2cf2
SUPERSEDED by the request @ c0ee5230 below: 5112837a
SUPERSEDED by the request @ c0ee5230 below: 8daa0c63
SUPERSEDED by the request @ c0ee5230 below: eeaf91bf
SUPERSEDED by the request @ 9ccd51b2 below: c0ee5230
SUPERSEDED by the request below: 9ccd51b2 (c0ee523 viewed: ch05_pemakar_crown and ch08_corrow_stair approved 160eadea; the rest were approved by big12)
RENDER-REQUEST @ 225370ba: ch05_pemakar_harbour, ch09_corrow_strand, ch06_brine_road, ch08_corrow_arrival, ch08_corrow_stair, ch08_coilspire_hall; why: the harbour view re-aimed (it stood behind Asha's head), the strand lit (it was near-black), the casts (Stillguard, hound) and Coilspire's moved key t4_d

## Exact next step
1. When the PC answers RENDER-REQUEST @ 9ccd51b2 (`gpu/render-act1-chapters-9ccd51b`): view every out/diff PNG;
   approve what reads (copy to `tests/screenshots/baselines/`, the llvmpipe metadata in baselines.json); fix and
   re-request what doesn't; then write the MERGE-READY lines for Ch4 (M3-C04-1204), Ch9 (M3-C09-1209), Coilspire
   (M3-C08-1210), Ch7's galleries (M3-C07-1211), Ch5 Pemakar (M3-C05-1213) and the casts (M3-CIN-1217).
2. Queue item 6, the cutscene quality bar, on the Act I scripts (easing, HeroMotion, no snapping, no greyscale
   frames, villagers alive), now that the stage actors are real models.
3. Blocked or waiting: Ashcrown (M3-ARC-1216), `haluna_wake` (Haluna's ZoneStory move), Ch7's port (env-art's
   kit, M3-C07-04), the Reefball HUD (M3-UI-01: TidecupMatch loads it by path when it lands).
