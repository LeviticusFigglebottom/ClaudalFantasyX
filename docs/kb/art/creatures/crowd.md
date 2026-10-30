# Act I's crowd (M3-CRE-659, ADR 0152)

Act I's generic background people (the capsules the placeholder inventory gave creatures) are **crowd people**: 56
rows in [`game/data/world/npc/crowd.json`](../../../../game/data/world/npc/crowd.json), each wearing one of **22 crowd
bodies** built through the characters' villager pipeline (pipeline.md §15) at a crowd tier, and coloured per
person at runtime. Runtime and zone rows: [`docs/kb/tech/field_npc.md`](../../tech/field_npc.md) "Crowd rows".

## 1. Pipeline

| Step | File | What |
|---|---|---|
| Roster | `game/data/world/npc/crowd.json` | per person: `zone`, `stage_actor`, `role`, `community` (+ `island`), `age_band`, `sex`, `build`; generated: `body`, `tints`, `work`. Plus the `bodies` plan, `age_tuning` and `work_tuning` |
| Ranges | `assets_src/crowd/ranges.json` | per community: skin endpoints, hair mixes, cloth mixes (a, b, c), reach-bands, `accepts`; per role: kits, work clip, cloth; per age band / sex / build: body sliders; per band: face sliders; per hair kind; per kit: villager_costume pieces |
| Generator | `assets_src/crowd/gen_crowd.py` | seeded (crc32 of names), deterministic: `params/<body>.json` in the villager schema (+ `_work`) and the roster's generated fields. `--check` for CI |
| Build | `assets_src/crowd/build_crowd.py` | Blender: `build_villager.main` with its `PARAMS_DIR` moved; LOD0 to the bake dir, LOD1 shipped as `assets/crowd/<body>/<body>.glb`. python3: `villager_textures.skin` (head 512/256, body 256), `write_materials.tables` re-rooted (only the GLB's slots), `<body>_actor.tscn`; a library's reference body also writes its group's shared clip library (§5) |
| Work clips | `assets_src/crowd/crowd_clips.py` | `mend`, `sweep`, `carry`, `fold`, `haul`, `kneel_mourn`, `vigil`, and the children's games `play_stones` and `play_clap`, on hero_clips; kneels solved from the skeleton's bone lengths |
| Import | `game/data/import/crowd.json`, `crowd_post_import.gd`, `write_imports.py`, `game/world/npc/crowd_clip_library.gd` | as the characters rule: slot materials, auto LODs; plus the group's shared clip library on an AnimationPlayer, the armature renamed and the hips track scaled to the body (§5) |
| Jobs | `tools/dev/blender_builds.json` `crowd_<body>` | verified byte for byte by `verify_blender_builds.py` |

Nothing under `assets_src/characters/` is edited: every module is imported and its module-level paths and sizes are
moved from outside. Rebuild one body: `blender --background --factory-startup --threads 4 --python
assets_src/crowd/build_crowd.py -- --body B --bake-dir D`, then `python3 assets_src/crowd/build_crowd.py --body B
--bake-dir D`.

## 2. Bodies

Five children (two boys, two girls, a girl of about thirteen), ten lay adults (men and women, lean, medium and
heavy), four elders, and two Order bodies in robes. Every villager_hair kind appears (short, cropped, bun, wrap).
Each face is rejection-sampled to stand at least `face_min_distance` (0.28, RMS in adult-range units) from every
Haluna villager's face (M3-CHR-100: crowd bodies are new people) and from the other crowd faces of its band
(`tools/tests/test_npc.py`). Per body about 0.6–0.85 MB of LOD1 GLB (15–19k triangles) and 0.6 MB of maps; the
clips are four shared libraries, 2.85 MB in all (M3-CRE-662, §5).

## 3. Variety scheme

- **Assignment** (`gen_crowd.assign`): a person's body must match their age band and sex, come from a community
  theirs `accepts` (skin and dress close enough), be a robe body if and only if they are Order, and be **unused in
  their zone**. Among those it scores the build, the body's own community, a preferred kit, and each earlier use
  (−2.5), so bodies spread (at most four wearers). Zones with the most people go first; within a zone, the person
  with the fewest choices.
- **Tints**: cloth_a, cloth_b and cloth_c are drawn from the person's community sets (roles and the Reefball sides
  override), each a palette.json swatch mixed toward another (`[a, b, t_lo, t_hi]`), so every tint is a palette
  swatch or a two-swatch mix (validated). Hair moves along the body's own hair mix by up to 0.35, so the baked
  scalp underpaint still sits under a near colour. A person's tints are redrawn (24 tries) until they stand 40 sRGB
  units from every other wearer of the body in some cloth slot; the validator holds the line at 24.
- **Cloth never near skin** (M3-CRE-662): every cloth tint, a person's and a body's default `_tints`, stands at
  least 18.5 from the body's skin by `skin_delta_e` (`tools/validate_npc.py`, the one function the generator and
  the validator share). The metric is CIE76 on CIELAB split into lightness, chroma and hue:
  `sqrt((0.3 dL)^2 + dC^2 + (0.5 dH)^2)`.
  - A warm low-chroma cloth (cream, sand, peach) reads as skin over a wide band of lightness and hue; a grey,
    white or strong colour clears on chroma or hue.
  - Calibration is in `ranges.json` `skin_clearance.calibration` and is re-measured by the `SkinClearance` tests.
    The fail pairs are what the renders showed as skin: the review's two pale tops in M3-CRE-659's crowd_lineup_a
    (cream #D1C0A1 on #AC7A5D and sand #BFAA86 on #A5765A), and the lighter cream #D7C9AF that a first pass at
    k 0.75 / floor 24 gave the same body, which still read as skin.
  - Lowest pass: order_marble on the lightest skin, 20.6 (greys 25.4 or more). Highest fail: 16.7.
  - Plain CIE76 can't do this: it ranks that cream (31.3) above the greys (26).
  - Consequence: creams and beiges fail near any crowd skin and are drawn away to whites, greys and colours.
  - `draw_cloth` never keeps a miss. It tries the slot's own mixes, then the community's other sets, then a darker
    or lighter mix of its swatches, and then stops with an error naming the person or body.
- **Motion**: FieldNpc's per-id idle phase and HeroIdleMicro already keep two wearers out of step; work clips and
  chat pairs vary the silhouettes further.

## 4. Review

`game/levels/_tests/npc/crowd_lineup.tscn` (shots `crowd_lineup_a/b/c`, `crowd_market`, `crowd_work`,
`crowd_mourners`) and the real zones with a layer (`crowd_<zone>.tscn`, shots `crowd_zone_*`). See the task's
review notes for what each render showed.

## 5. Clips: one library per group (M3-CRE-662)

Every crowd body is the villager rig, so the clips are shared: `assets/crowd/clips/crowd_<library>_clips.tres`
for `adult` (13 bodies, 10 clips, 1.35 MB), `elder` (4, 6 clips, 0.79 MB), `child` (3, 4 clips, 0.41 MB) and
`child_small` (2, 3 clips, 0.30 MB), replacing 22 per-body libraries (12.0 MB). The groups and their reference
bodies are `ranges.json` `clip_libraries`. The import map is the same table, which the validator checks.
- **Build**: the reference body's job builds its group's library from its own fresh GLB: `villager_clips.build`
  with the group's mean `_persona` and every member's work clips. The tracks are rooted at `crowd_skeleton`, and
  the file records the reference's hips rest height (`metadata/hips_rest_y`).
- **Import**: `CrowdClipLibrary` (run by `crowd_post_import.gd`) renames each body's armature to `crowd_skeleton`,
  so the tracks resolve on every body. It also sets the body's `Skeleton3D.motion_scale` to its own hips rest
  height over the reference's, so the hips track (absolute positions) fits each body's height.
- **Why these groups**: each member's own clips (its skeleton, the group persona) were compared with the
  reference's clips played on it, sampling world positions of the hands, feet, toes, knees and head over every
  clip.
  - Within the groups the skeleton's part is at most 1.0 cm, and 0.4 cm in foot height (`SharedClips` tests,
    tolerance 1.5 and 0.6 cm).
  - One library for every body would be 4.7 cm off on the small children and would flatten the elders' lean.
  - The two small children are 4.6 cm from the tall children's reference, so they get their own library.
  - The Godot test checks every body on its library: same resource per group, `motion_scale`, toes on the floor in
    idle and talk.
- **Trade-off**: a body's own `_persona` (sway, lean, arms down) now only feeds its group's mean. Per-body persona
  differences were at most about 1 cm at the hands, with wearers already kept out of step by idle phase and
  micro-motion.

## 6. Known limits (requests to characters in the task file)

- Saltwright line-marks and the brine-brand are not drawn: villager_textures paints only Low Reaches reach-bands,
  so the wrights' forearms are bare.
- No hand props: the work clips read through the hands and head alone (M3-CRE-614 covers props for the villagers).
- The build still makes and discards LOD0 (about a third of each Blender run).

## 7. Haluna's vignettes (the Lead, 2026-10-30)
"The slice zones lived in: mending nets, carrying baskets, children playing." Haluna had only its named villagers;
fifteen crowd people now work in it (`zones/ch02_haluna.json`, `at` spots, ground heights probed against the zone's
collision). Each stands beside something it would work on:
- **The causeway head:** a woman laying fish on the drying rack, a buyer with her basket at the stall, a man hauling a
  line at the water's edge below the causeway steps, and two children at a game of stones on the sand.
- **The tide-wall lane:** an old woman mending at the net heap by her door, a woman back from the dock with her basket
  by the sacks, two children at a clapping game, and a man sweeping between two stations in front of his house.
- **The dock:** a man mending at the net heap, an old woman turning fish on the rack, a man hauling a mooring line, and
  a man with a basket of the catch by the jars.
- **At night** (the dock at night, after the Drownbell): the dock's, the causeway head's and the children's rows are
  gone home (`shown: day`). The lane's mender and sweeper work on by lamplight, and one woman brings the last basket
  home past the market (`shown: night`).

The details:
- **Roster.** The community is `haluna` (ranges.json: Low Reaches, the haluna.md palette of indigo, sea blue and sand
  with one red note), with new faces only (ADR 0152).
- **No reshuffling.** Late people (`assign.late_zones`: Haluna; `assign.late_prefixes`: `oruvel_deck_`,
  `pemakar_quay_`) are assigned after everyone else, zone by zone, never wearing a body their zone already shows, so
  no body already placed moved (tools test `test_late_people_never_reshuffle_the_others`).
- **The children's games** (`crowd_clips.py`, roles `child_stones` and `child_clap`):
  - `play_stones`, 4 s: knelt back on the heels, a stone tossed to 0.66 m, the eyes up after it, a sweep of the
    ground and the catch, twice a loop;
  - `play_clap`, 3.2 s: a clap and both palms pushed out to the partner's, on a knee-bounce, eight beats a loop. The
    pair stand 0.6 m apart, where their palms meet.
- **Libraries.** The child and child_small libraries carry them.
- **Review:** `npc_haluna_vignette_causeway`, `_lane_games`, `_lane_mender`, `_dock`, `_night_market` and `_night_lane`
  (game/levels/_tests/npc/haluna_villagers.tscn; `night` stages the story's dock at night).

### Oruvel and the Pemakar quay (the Lead, 2026-10-30)
- **Oruvel's commons deck** (`zones/ch01_oruvel.json`), six people at its edges so the deck's paths stay clear:
  - a girl at stones by the north rail, and a man mending a diver's net bag;
  - a man sweeping along the west rail between two stations, and a woman with her basket by the cookboat;
  - along the south rail, a man laying fish to dry and a man hauling a line in.
- **The Pemakar quay at Lanternfall** (`zones/ch05_pemakar.json`), five people on the quay's two ends (the middle is
  the story's):
  - an old man mending a net;
  - two Low Reaches traders off the Brightwater crossing, one hauling his skiff in and one with a basket of salt fish;
  - a woman come down for the folded boats with a basket of lanterns;
  - an old woman folding leaf-boats.
- **Why so few children.** Body capacity decides the cast, because no body repeats within a zone and each community
  accepts only some bodies:
  - Oruvel had one child body left, so its child plays stones alone, and men carry most of its work;
  - Pemakar had no child body and no Pemakar-accepted man left. Its quay men are traders from the ferry
    (community `brightwater`, which the crossing brings), with Pemakar's own elders and a woman.
  - More children would need more planned child bodies (a characters-track body plan).
- **Review:** `crowd_vignette_oruvel_north`, `_oruvel_south`, `_pemakar_west` and `_pemakar_east`.
