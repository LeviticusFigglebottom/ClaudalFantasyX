# Live log: creatures environment

Feature track for the battle creatures (cloud session_01CYks9e592YBEfygyTawcJD), branch `claude/creatures`, started from `origin/claude/undertow-lead-handoff-423ixt` aeb0875. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE.

## STATE AT HANDOVER (2026-10-25)

**HANDOVER DONE @ 7683996d** (claude/creatures, pushed; this line's own commit follows it).

Branch `claude/creatures` @ 5065b869 (pushed). Nothing is uncommitted, and no subagents are running. Any worktree
branches left under `.claude/worktrees/` are already merged or applied here and need nothing.

### Done and merge-ready
- **On the integration branch already** (big7 d6a0886d, big8 6c6e5514): all 27 Act I creatures, the creature pipeline,
  battle wiring, the M2/M3 creature tasks.
- **On claude/creatures since big8**, MERGE-READY @ 5065b869 for the Lead's next batch:
  - integration big8 merged at its own merge commit, and claude/hero-integration (MERGE-READY for big9) merged at
    9c5e4c26 with the Lead's approval;
  - **M3-CRE-610 villagers alive** (ac7ea5b9..bada52a9): FieldNpc, docs/kb/tech/field_npc.md;
  - **M3-CRE-611 ambient wildlife**: WildlifeLayer, the `wildlife` import category, docs/kb/art/wildlife.md;
  - **M3-CRE-612 battle polish**: hit_b and idle_b for every creature, hit rotation, the idle fidget, and flier
    `stand_in.hover` so KOs land;
  - the spar_wraith's `hauled_down` phase, phase `clips` and `show_after`, and the polish passes.
- **Checks at 5065b869** (combined tree):
  - validate_data 0/0, taskboard, lint and format clean, tools creature, wildlife and post_import tests OK;
  - Godot field_npc 10/0, hero 68/0, field_ 106/0, creature 24/0, wildlife 10/0;
  - **post_import: 3 FAIL, battle: 1 FAIL (see Known bugs).**
  - Shots not re-run after the big8 and hero merges.

### Exact next steps (for the new environment)
1. **Triage the failures after the big8 merge:**
   - `test_post_import.gd`: test_fixture_lod_ranges_follow_the_rules, test_vegetation_import_matches_vegetation_plant_defaults
     and test_a_distance_sweep_draws_exactly_one_lod.
   - `test_battle_ko_once.gd`: test_a_primitive_foe_falls_once_and_is_hidden.
   - First check whether they fail on the integration branch itself (6c6e5514). If so they aren't ours: tell the
     owners. The KO test assumes `wickfry` has no model, but m2-slice's model lines (big8) give it glassfry's, so
     battle-presentation needs another primitive foe for that test.
2. Capture and compare the creature, battle, npc and wildlife shots on the merged tree (60+2). View any change before
   approving. Big8 took the three battle baselines that conflicted from the integration branch.
3. Write the MERGE-READY line for the Lead batch.
4. When it lands: m2-slice adds a WildlifeLayer to haluna.tscn and GreyboxZone, and calls FieldNpc begin_talk/end_talk
   around villager barks (agreed by message; see the 22:20 entry).
5. Open: the Matron's re-crust hook (battle-presentation); the Undertow's Reach `water` slot (PC GPU look); a "dialogue
   finished" signal on FieldEvents (Systems request, optional).

### Open questions
None for the human.

### Known bugs
- The 4 test failures above, not yet triaged.
- The wreck crab's leg barnacles are faceted (budget nearly spent); the Matron's yoke cells are even.

### Gotchas (the creature pipeline)
- **Builds:** procedural numpy in `assets_src/creatures/<id>/build_<id>.py` on `common/creature_kit.py`, exported by
  Blender 5.0.1 with `--threads 4`. Every job in `tools/dev/blender_builds.json` must rebuild byte-identical
  (`tools/dev/verify_blender_builds.py --job <id>`). Append jobs as text: reformatting the JSON breaks merges.
- **The kit changes every creature:** a kit change (`with_variety`, `IN_PLACE_CLIPS`) rebuilds all 27, so rebuild them
  all and verify.
- **Variants:** stormgull, wallcrab, wreck_crab, squall_wing and wall_polyp import their base build. Their jobs list
  the base folder as a source.
- **Vertex data carries the look:** COLOR_0 albedo and wetness, UV2 cavity and emission. Materials come from each
  creature's `materials.json` through `write_materials.py`.
- **Import rule:** the `game/data/import/creatures.json` `assets` list is not recursive: list each folder. Run
  `godot --import` before new class_names resolve.
- **Shots:** `capture.sh` ignores HYMN_SHOTS; use `--shots a,b`. Set HYMN_LOG_DIR and XDG_DATA_HOME to scratch dirs.
  Never kill processes by pattern.
- **Data:** creatures.json phase ids must match enemies.json phases once an enemy uses the model. KO end must sit on
  the floor (a tools test pins a flier's drop to its `stand_in.hover`).
- **Messages:** send_message to the Lead was refused (untrusted device) for most of the session, so the live log is the
  channel.

## Now
- **22:20, m2-slice:** once wildlife_layer.gd reaches the integration branch, they add a WildlifeLayer to haluna.tscn,
  and GreyboxZone will add one automatically for any location with a game/data/world/wildlife/<zone>.json. For
  FieldNpc (after it lands) they'll call begin_talk/end_talk around HalunaStory/ZoneStory barks, or
  follow_dialogue(runner).
- **MERGE-READY @ d9001836: the Lead's new queue (M3-CRE-610..612), all in review.**
  - **611 ambient wildlife (merged):** gull (flying and perched), shore crab and shoal fish, built from the kit in a
    new `wildlife` import category. WildlifeLayer is MultiMesh, 4 draw calls a zone, 0.27 ms average and 0.56 ms worst
    in Haluna (budget 1 ms); off-screen groups pause and anything past 120 m hides. Data for ch02/haluna and
    ch03/saltgrass_causeway. **Zone owners add one WildlifeLayer node** (docs/kb/art/wildlife.md); m2-slice has been
    asked.
  - **612 battle polish:** hit_b and idle_b for every creature, hit rotation, the idle fidget, and flier `hover` so
    KOs land on the floor (KO audit viewed).
  - **610 villagers:** parked as patches until hero-integration merges (see the 22:10 entry).
  - **Checks run:** validate_data, taskboard, lint, format, tools unittest (creatures, wildlife, post_import; the
    agent ran the full tools suite: 706 OK), Godot wildlife 10/0, creature 16/0, post_import 19/0, battle 527/0, the
    Blender verify of all 27 creature jobs and 3 wildlife jobs (identical), 60 creature and battle shots unchanged,
    wildlife_stage and npc_stage_field approved after viewing. **Skipped:** the full manifest and coverage (no change
    in game/battle or game/progression).
- **21:30, the Lead's new queue (M3-CRE-610..612, id block 600–699; ownership row added for game/world/npc,
  game/world/wildlife and their data, tests and assets paths):**
  - **610 villagers alive** (worktree agent): FieldNpc, which gives villager actors idle loops, a talk gesture, an eased
    turn to face the player (reusing hero-integration's HeroLocomotion and HeroIdleMicro) and walk routes. It is built
    on a LOCAL merge of claude/hero-integration (not yet on the integration branch); only the NPC commits land here,
    after hero-integration merges. Zones stay m2-slice's: they add the node (docs/kb/tech/field_npc.md).
    **Done and parked (22:10):** 3 commits as patches in docs/kb/tasks/M3/M3-CRE-610-parked/ (`git am` after
    hero-integration merges). field_npc 10/0, hero 35/0; the npc_stage_field shot was viewed and approved.
  - **611 ambient wildlife** (worktree agent): gulls, shore crabs and fish shoals; a WildlifeLayer node plus per-zone
    data for the zone owners to add.
  - **612 battle polish** (here): hit_b and idle_b derived for every creature (f426c0e8), hit rotation, and an idle
    fidget. In progress: Blender verify of all creature jobs, the 60 creature/battle shots, and a KO end-pose audit
    (BPR-11 plays a KO once, then fades, so KOs must end grounded).
- **19:50, m2-slice: the `model` lines are in** on claude/m2-slice (544958b1, after big7). 15 Act I enemies point at
  their creature scenes; the internal id `wickfry` is kept and points at glassfry's scene (flags and saves use it).
  stillguard_inquisitor is the character track's. spar_wraith's `hauled_down` row comes with big8. This unblocks the
  last blocked creatures item; only the Matron's re-crust hook (battle-presentation) is left outside this track.
- **19:45: big7 merged into claude/creatures** (integration 8f808cc6). Conflicts were three battle baselines, taken from
  the integration branch, then re-captured on the merged tree: all 60 creature and battle shots pass against them.
  BattleActorMotion's action/hit handoff to BattleChoreo arrived as agreed. Checks after the merge: validate_data,
  taskboard, lint, format, tools tests, Godot creature 14/0 and battle 527/0. m2-slice has been told the `model`
  lines can land now (the scenes are on the integration branch). The polish batch rides big8.
- **MERGE-READY @ b6d98d1c (+ this log).** Since 0eb5a1a9: the spar_wraith's two phases (d2848fbd) and the minor
  polish (the Matron's slag cells in mixed sizes, salt bands and barnacles on the wreck crab's legs, smoothed rent edges
  on the squall wing). Checks: validate_data, taskboard, lint and format, tools creature tests, Godot creature 14/0
  and battle 412/0, Blender verify of each changed job (identical). 4 creature shots compared and passing:
  creature_spar_wraith was re-approved at 0.03089, the Matron 0.02893, the crab 0.02448, the wing 0.00742, each after
  viewing. Skipped: other shots and coverage (no shared code beyond CreatureActor's phase keys, which the creature
  tests cover).
  - **Queue:** every item is done or blocked. Blocked: enemy `model` lines (m2-slice adds them once this branch is on
    the integration branch) and the Matron's re-crust hook (battle-presentation). Nothing open on the creatures side
    beyond optional finesse (the wreck crab's leg tubes are coarse; only 58 triangles of budget left).
- **Resumed after the usage-limit stop (17:30).** Integration 81651b7e merged. The Lead's resume list (Ch6–Ch9, clips,
  slice polish) was already done (see the entries below). New since then: m2-slice's Ch4 boss phase `hauled_down` for
  the spar_wraith is built at d2848fbd (Shroud, drop, water Sheath, deck strikes; new `show_after` phase key; the
  kit's `pose_of`/`in_pose`). Now running: one agent on the three minor polish notes (the Matron's cell-size variety,
  the wreck crab's leg detail, the squall wing's saw-toothed rents).
- **MERGE-READY @ 63f7bed3: polish batch.** The Cinder Matron's crack lines (Voronoi slag cells with ember seams, 23.2k
  triangles) and a cleaner mask; the squall wing's see-through rents in wings and body; the wreck crab's salt-plate
  crust and bleached legs; phase strikes (a phase `clips` map, the Reach's Dark and Breach strikes).
  - **Checks run:** validate_data, taskboard, lint and format, tools creature tests, Godot `--filter=creature` 14/0,
    Blender verify of each changed job (identical). Shots creature_cinder_matron (0.03653), creature_squall_wing
    (0.02447) and creature_wreck_crab (0.03140) were re-approved after viewing; the Reach's shot is unchanged.
  - **Checks skipped:** other shots and coverage (no shared code beyond CreatureActor's phase-clip lookup, which
    the creature tests cover).
  - **Queue:** every item is done or blocked. Blocked: the enemy `model` lines (they wait for this branch to reach
    the integration branch, then m2-slice adds them) and the Matron's re-crust hook (battle-presentation). Open
    polish notes, low priority: the Matron's cells are a bit even in size; the wreck crab's legs are smooth up close.
- **16:30, queue state** (answering the Lead's 16:03 note: items a–c were already done at 539d145a):
  - Done since then: integration c1607d89 merged at 438a1445 (creature 13/0, battle 412/0 after it), and phase
    strikes at 468fa197 (a phase `clips` map; the Reach strikes from its Dark and Breach poses).
  - In progress in two worktree agents: the Cinder Matron's crack lines and mask edge; the squall wing's see-through
    tears and the wreck crab's crust and bleached legs.
  - Blocked: `model` lines on enemy rows wait for claude/creatures to reach the integration branch (m2-slice adds
    them in their next merge after that). The Matron's re-crust hook is battle-presentation's.
- **MERGE-READY @ 539d145a: the Lead's queue items 1–4 (15:30).** Ch6–Ch9 had nothing left to build (Ch7 has no
  foes, Ch9 no fight). M3-CRE-07 (review): clip-contract audit, strike clips in place (17 GLBs rebuilt, 10
  byte-identical), LOD1 verified as Godot's import LODs (`tools/dev/creature_lods.gd`), portrait framing for the gull
  and eel. Phase ids reconciled: `pour`, `breaking` (with the new `hide_after`).
  - **Checks run:** validate_data, taskboard, lint and format, tools creature tests, Godot `--filter=creature` 13/0 and
    `--filter=battle` 412/0, all 27 creature jobs rebuilt and audited. 42 creature and battle shots compared: 37
    unchanged, 5 re-approved after viewing (RMSE in M3-CRE-07).
  - **Checks skipped:** the shots outside the creature and battle sets (no change reaches them), coverage (no
    `game/battle/` change).
  - (My send_message to the Lead is refused with elevated_session_untrusted_device, so this log is the channel.)
- **MERGE-READY @ 0ce0bee6 (batch): the Act I bestiary, M3-CRE-02..06 in review.** Branch `claude/creatures`
  (integration 1a6f7645 merged at 1ed50955, docs only).
  - **Items:**
    - Ch1: glassfry (renamed from wickfry), scuttler.
    - Ch5: ashwing (ember eye-spots), slag_tortoise, **cinder_matron** (the kiln forge-construct with a ladle, tongs
      and a steady glimmer_bound heart, 23.9k triangles), vein_sparker.
    - Ch6: shoal_skipper, raid_hound (mud coat, red muzzle cage), wreck_crab (in a lamp housing, glimmer_bound).
    - Ch8: tide_crawler, squall_wing, wall_polyp (on a Watcher block), **undertows_reach** (phases `dark`/`breach`),
      flue_moth, stormgull, wallcrab.
    - CreatureActor phases gained `show`/`hide`.
  - **Checks run:** validate_data 0/0; taskboard OK; gdlint and gdformat clean; tools test_creatures and
    test_post_import OK; Godot `--filter=creature` 12/0, `--filter=post_import` 17/0, `--filter=battle` 412/0;
    Blender verify of every creature job added or changed in this batch (all identical). 27 creature shots, each new
    one approved after viewing.
  - **Checks skipped:** the full shot manifest (no battle scene, shader or HUD change since 2f36b275; only creature
    review shots changed), the full Godot suite and coverage (nothing in `game/battle/` or `game/progression/` touched
    since 2f36b275).
  - **Review asks (art):** glimmer_bound on two creatures (the Matron's heart, the wreck_crab's lamp), both steady per
    colour rule 2, and noted in creatures README rule 3 as Lit Age constructs only.
  - **For m2-slice:** they add `model` lines after this lands on the integration branch (see below).
  - **For PC GPU:** undertows_reach's `water` slot is a stand-in for the Undertow look (act1/undertows_reach.md).
  - **m2-slice's reply (14:41):** `model` lines come in their first merge after claude/creatures reaches the
    integration branch (the scenes must exist for their validate_data). wickfry's row points at glassfry and is
    renamed. They use `dark`/`breach` for the Reach; the Matron's phase ids come with their Ch5 build.
- **MERGE-READY @ 2f36b275: ci_local exit 0, 1467 tests, 91 shots, Blender identical.** Branch `claude/creatures`, with `origin/claude/undertow-lead-handoff-423ixt` e9938ed merged in at 4cfc523.
  - Full `tools/ci_local.sh` in this container (2026-10-24, about 13:00–13:50 UTC), every shot, Blender required.
  - Blender: 17 jobs, 0 failed, 0 uncovered, all identical. The change base was `main`, which ran every job, a superset of the integration base. Every creature job is pinned at `default_threads` 4.
  - Godot tests 1467 run, 0 failed. Coverage: battle 99.95%, progression 96.52%, within the baseline. Boot smoke clean.
  - Screenshots 91 compared, 0 failed.
  - The 11 battle shots the models change were re-approved after side-by-side viewing; the RMSE list is in M2-CRE-09. They are battle_hud_preview, battle_swap_menu, battle_victory, battle_statuses, battle_swell_ring, battle_read_panel, battle_opening_banner, battle_swell_modes, battle_vowbound_call, battle_vowbound_out and drownbell_flood.
  - New: 17 creature shots, approved after viewing.
- **Contents of the batch:**
  - Slice creatures: M2-CRE-01..10, all in review. The five slice creatures carry `model` in enemies.json.
  - M3 first passes: M3-CRE-01 (roster and sheets), M3-CRE-02 (Ch1 models) and M3-CRE-03 (Ch4 models), all in review. Their models are not referenced by any enemy yet.
- **Merge notes for the Lead:**
  - `fighter_stand_in.gd` carries M2-UI-07's hook verbatim from `claude/ui` (ef3937c, bf37755, 08c872c), plus small creature delegations.
  - `battle_stage.gd` gained the model merge, the `BattleActorMotion` attach and `settle_actors()`.
  - The PC's `drownbell_flood_shot.gd` gained one line, `ctl.stage.settle_actors()`.
  - Shared files got appends only: enemies.json `model` lines, PROVENANCE, blender_builds.json jobs, shots.json, and the validate_data.py import plus one call.
- **Battle-presentation (agreed by message):** BattleChoreo will take the action and hit clip timing. `BattleActorMotion._on_action_resolved` defers to `stage.choreo` when it is present; they may make that change at merge time. Phase and rim handling stays in BattleActorMotion. The clip names match their contract (attack, cast, hit, ko, idle). `contact_time()` gives each strike's contact second. A creature's `ko` clip replaces their procedural collapse.
- **m2-slice (by message):** they adopted the Act I roster. Pending on my side:
  - rename `wickfry` (the word "wick" stays Mother Kell's);
  - add `scuttler` (Ch1) and optional `vein_sparker` (Ch5);
  - `wreck_crab` lives in broken lamp housings with a bound-teal glow;
  - the bottle hermit's glass is a plain oil-lamp glass.
  The per-zone foe counts are in their message, and their Ch1 enemy rows come first.
- **Un-pushed state:** none. Drafts for Ch5 (ashwing, slag tortoise, Cinder Matron), Ch6 (shoal skipper, raid-hound), Ch8 (tide crawler) and the Ch1 scuttler build cleanly in the scratchpad. They land after this merge-ready point, on top of 2f36b27.

## Decisions so far
- **Id blocks (Lead, 21:00):** new task ids M3-CRE-600..699, ADRs 0150–0159, handoffs `<date>-<role>-creatures-<n>.md`. Existing ids stay.
- **Hook:** the UI track's M2-UI-07 (on `claude/ui`, 08c872c1) already makes `FighterStandIn` instance a spec's `"scene"`. The creatures build on that hook rather than a parallel one: the enemies.json `model` field becomes the stand-in spec's `scene`.
- **Materials:** one creature shader (`game/shaders/creature/creature.gdshader`) reading vertex data (albedo, wetness, cavity, wound mask), not the texture-based character families. Why: pipeline.md §2.
- **Import:** a new `creatures` category. Clip loop modes are set at runtime from `game/data/creatures/creatures.json`, so the shared `AssetImportRules` (which the characters track is also changing) is not touched.
- **Task ids:** M2-CRE-* (free on every branch at the claim).

- **15:15: m2-slice's phase ids applied.** The Matron's `crust_breaks` is renamed `pour`. The hullgnaw gains `breaking`:
  its frames are now their own `Ribs` mesh, a `phase_break` clip has them burst off and fall, and a new phase key
  `hide_after` (CreatureActor, validator, test) hides them once the clip has played. Its shot is unchanged (RMSE 0)
  and its job is identical. The Matron's re-crust can be a phase with `show: ["Crust"]` once m2-slice names it.
  **15:20, m2-slice: the re-crust is not a phase.** She stays in `pour`. The `Crust` comes back when her `recrust`
  skill resolves, or on a water or ice hit with `reacted: true` (game/battle/boss_mechanics.gd on claude/m2-slice).
  It hides again when the armour break lands. That hook is battle-presentation's (m2-slice logged the request), and no
  creatures.json row is needed. If they want a CreatureActor call for it, `set_part_broken` already shows and hides
  named nodes per key; a `break_parts` entry could carry it.
  Checks: creature 13/0, battle 412/0, validate_data, tools creature tests, lint, format.

## Exact next step
The Lead's queue (15:30):
1. **Ch6–Ch9 creatures:** done. Ch6 (shoal_skipper, raid_hound, wreck_crab, plus the reused gull_harrier) and Ch8
   are built. m2-slice's sheets confirm that Ch7 has no foes and Ch9 has no fight.
2. **Clip contract** (M3-CRE-07): audited, and strikes made in place (kit `IN_PLACE_CLIPS`, 17 GLBs rebuilt).
   Shots re-compared: 5 re-approved after viewing (RMSE in M3-CRE-07).
3. **Slice polish** (M3-CRE-07): LOD1 verified as Godot's import LODs; portrait framing for the gull and the eel.
   Next: approve the changed shots, then the polish notes (the Matron's crack lines, the squall wing's tears, the
   wreck crab's crust).
4. **Reconcile ids** when m2-slice's rows land: done for the Ch1/Ch5 phase ids (`pour`, `breaking`); the `model`
   lines are theirs to add after this branch reaches the integration branch.

## Previous next step (done)
Merge the three creature worktrees as they finish (they append to creatures.json, enemies.json, the import rule, blender_builds.json and PROVENANCE.md: union the rows). Then capture every battle shot and the creature shots, view each, approve the creature baselines, and re-approve the battle shots whose change is the models (list each RMSE in M2-CRE-09).

## Queue
1. ~~M2-CRE-01 design sheets~~ (review)
2. M2-CRE-02 pipeline, M2-CRE-03 battle integration, M2-CRE-04 reef crab (pushed; crab polish and shots pending)
3. M2-CRE-05..07 lantern eel, gull harrier, spawn-polyp (worktree agents running)
4. ~~M2-CRE-08 the Drownbell~~ (first pass pushed)
5. M2-CRE-09 shots and re-approvals
6. ~~M2-CRE-10 bestiary portrait hook~~ (CreaturePortrait pushed; M2-UI-16 filed)
7. **Queue tail (Lead, 2026-10-24 12:00, M3 in parallel):** the Act I bestiary (act_outline.md Ch1 and Ch4–9: the Ch1 dive's sea-floor creatures, the Terraces of Ash and Brine Shoals foes, the Seawall). Design sheets first; rosters coordinated with m2-slice, which designs the Act I encounters.

## Setup notes
- `fetch_blender.py` failed twice on truncated debs from the proxy (`dpkg-deb ... unexpected end of file`). Delete the named `.deb` under `~/.cache/hymn/blender-*/debs/` and rerun; it finished on the third pass.
- `ln -s ~/.cache/hymn/godot-4.6.3+ds-2/godot ~/.local/bin/godot` (and `godot-render`, and `~/.cache/hymn/blender-5.0.1+dfsg-5/blender`).

## NEW ACCOUNT (from 2026-10-25)
- **MERGE-READY @ 52c2d19c: integration -ze8rrn (de93e79e) merged; item 1 triage, no code change needed.**
  - `test_post_import.gd` (3 FAIL at handover): **21/0 on a fresh import.** It was a stale `.godot` import cache,
    not code.
  - `test_battle_ko_once.gd::test_a_primitive_foe_falls_once_and_is_hidden`: **it fails on the integration head too**
    (wickfry has glassfry's model since big8). It's **already fixed in lead/gate-big9 by 2e956d3f** (the test now
    picks any encounter led by a model-less foe), so it clears when big9 lands. Nothing to file.
  - **Lead, note:** big9 took claude/creatures @ 23f94ed5 (612 only). **611 wildlife and 610 FieldNpc are not in
    big9**; take this head in big10. The zone wiring (slice-polish) waits on them.
  - Checks run: validate_data 0/0, taskboard, Godot post_import 21/0, field_npc 10/0, wildlife 10/0, creature 24/0,
    hero 68/0, battle_ko_once 4/1 (the known one above). Skipped: lint and format (no code change), shots, Blender
    (nothing changed).
- **MERGE-READY @ 78b8a992: M3-CRE-613, villagers alive (FAST-TRACK candidate: the human's "placeholder villagers").**
  - **What it adds:**
    - NpcLook head modifier;
    - FieldNpc attention (a glance at a party that comes near, look-arounds), chat pairs in bouts, work, storm (shelter, brace, sky looks, home again), and a talk that ends on its own;
    - **VillagerLayer**: one node per zone turns the stand-ins into the real M2-CHR-03 villagers from `game/data/world/npc/zones/<zone>.json`. Haluna's file places all seven.
  - Four shots of the real Haluna zone with the layer (npc_haluna_dock/market/chapel/lane), each viewed and approved. The dock shows the netmender and the fisher facing each other in a chat.
  - Also restored the llvmpipe metadata of save_shrine_field and settings_accessibility (the "?" the Lead flagged).
  - **Checks run:** validate_data 0/0 (the new validate_npc included), taskboard, gdlint, gdformat, tools test_npc 8 OK, screenshot manifest valid; Godot villager_routines 11/0, field_npc 10/0, hero 68/0.
  - **Checks skipped:** other shots (no shared scene or shader touched; the layer only exists in my review stage until a zone adds it), coverage (no game/battle or game/progression change), Blender (no asset change).
  - **Lead:** 610 (FieldNpc) and 611 (wildlife) are not in big9. They ride with this head.

### For other tracks (relay, please)
- **slice-polish:** Haluna's villagers are still capsules. Add ONE node to `haluna.tscn` at the root:
  `[node name="VillagerLayer" type="Node3D" parent="."]`, script `res://game/world/npc/villager_layer.gd`,
  `zone_id = &"ch02/haluna"`.
  - It hides only the stand-ins' StandIn and Facing (plus Reed's Broom and Osu's Bowl), and keeps the collision and the Talk Interactables, so ids, payloads and dialogue are unchanged.
  - It puts each villager beside its stand-in, so night_hide still works.
  - Talks end by themselves when the player gets control back.
  - For GreyboxZone.build(): add a VillagerLayer when `FileAccess.file_exists(VillagerLayer.path_for(location_id))`, as with WildlifeLayer.
  - Also add the WildlifeLayer node.
  - Tell me (via your log) the stand-in paths in the causeway and shrine zones, if they have any.
  - Docs: docs/kb/tech/field_npc.md, "VillagerLayer".
- **act1-chapters:** VillagerLayer has a `storm_flag`. Oruvel with `ch01_gulls_cried` sends its villagers to shelter when the storm rises, with no zone call needed (or call `FieldNpc.set_storm_all(get_tree(), on)` from OruvelZone.set_storm). List the Act I villager stand-in paths in your log and I'll write the data files.
- **characters:** request task M3-CRE-614: villager work clips (mend_net, tend_stall, sweep, hold_bowl), an optional `brace` loop, hand props (broom, bowl, net), and bodies for Haluna's Shopkeeper, Smith and Innkeeper.
- **hero-integration (FYI):** NpcLook is a SkeletonModifier3D added after HeroIdleMicro on villager skeletons; it turns DEF-spine.004/.005/.006. Tell me if the idle_micro bones or the modifier order change.
- **MERGE-READY @ ee52f218: M3-CRE-615, ambient wildlife in the Act I zones (queue item 3).**
  - Data on the greybox layouts:
    - gulls over Oruvel, the Brightwater ferry and Tamsule;
    - crabs on Brine Shoals' flats and tideline, the Haluna wake-night shore and Pemakar's quay;
    - fish shoals in the drowned tower (oruvel_underway).
  - Corrow's strand, Ashcrown and the bell galleries are empty on purpose (docs/kb/art/wildlife.md, "Act I zones").
  - Three shots of the real greybox zones, each viewed and approved (wildlife_zone_brine_flats/brine_wrecks/underway_crown).
  - **Checks run:** validate_data, validate_wildlife, Godot wildlife 10/0, taskboard. **Checks skipped:** coverage and Blender (no code or asset change).
  - **Zone owners (act1-chapters):** add the one WildlifeLayer node, or have GreyboxZone add it for any location with a file.
- **In progress: M3-CRE-616, insects** (moths at lamps, dragonflies over flats and paddies) as a fourth wildlife kind,
  built in a worktree agent. It lands as its own MERGE-READY.
- **MERGE-READY @ 9bf973cc: M3-CRE-617, hits land on the contact frame (queue item 4, syncs with M3-BPR-401).**
  - Every creature's hit peaks 0.13–0.20 s in, so the hit-stop used to freeze the pre-hit idle pose. A hit now cuts in at 0.1 s with no blend (creatures.json `hit_snap`).
  - The Drownbell, Matron, limpet and Reach hits barely moved; they are rebuilt with real recoils (Blender verify identical; hit frames viewed before and after).
  - **Checks run:** validate_data, lint, format; Godot creature 25/0 and battle 619/1 (the 1 is the known test_battle_ko_once primitive-foe test that battle-presentation is fixing); 11 battle_choreo shots all pass (battle_choreo_hit rmse 0.006, which is the struck crab now mid-recoil, viewed).
  - The creature stage shots of the four rebuilt bosses and creature_portraits are re-rendering; I'll report any drift.

### For other tracks (relay, please)
- **battle-presentation (M3-BPR-401 bug, your files):** the struck target's clip is NOT held during the hit-stop.
  - `_step_beats` fires contact, so BattleImpact._hold sets every involved AnimationPlayer's speed_scale to 0.
  - Then the react beat calls `BattleClips.play`, which sets `p.speed_scale = speed` again. So the target's hit clip runs through the hold while the attacker and the procedural recoil stay frozen.
  - Suggested fix: BattleImpact holds the targets again after their reactions start (or BattleClips.play leaves a held player at 0 and BattleImpact restores `speed` on release).
  - My side is done: creature hits now start on a struck pose (M3-CRE-617), so once the hold works the frozen frame shows the blow.
- Re-checked after M3-CRE-617: creature_drownbell, _toll, _cinder_matron, _tower_limpet and _undertows_reach have rmse 0 (the rebuilt hits don't touch them).
- **MERGE-READY @ 15c8c997: M3-CRE-618, portrait rim for the dark creatures (queue item 5).**
  - CreaturePortrait's key and rim now come from the camera, not the world, so every portrait yaw is lit alike.
  - The 9 darkest creatures by measured albedo get rim 2.8 plus a low kick light.
  - The review sheet fits all 20 (it cropped its top and bottom rows); viewed and re-approved.
  - **Checks run:** validate_data, lint, format, Godot creature 25/0, tools test_creatures. **Checks skipped:** other shots (nothing else uses CreaturePortrait on this branch).
- **For ui-menus (relay):** your bestiary bake (tools/portraits) uses the same camera-relative rims, with `light_scale` for hullgnaw, scuttler, squall_wing, tide_crawler and undertows_reach. By measured albedo, add `spawn_polyp` and `wall_polyp` (black bases), `flue_moth` and `oil_slug` (glossy near-black). creatures.json `portrait.rim_energy` > 1.1 marks the dark ones if you'd rather read it than keep a list.
- **MERGE-READY @ b5e05d2f: M3-CRE-616 insects, M3-CRE-613 wake villagers, M3-CRE-620/621 Act II.**
  - **616, ambient insects (merged from a worktree agent):**
    - moths at lamps and dragonflies over water and paddies, as a fourth wildlife kind (6 draw calls a zone, 0.07 ms in Pemakar);
    - zone data for Haluna (dragonflies) and Pemakar (two moth swarms and a paddy patrol, unioned with my Act I crabs);
    - wildlife_stage re-approved by the agent after viewing.
  - **613, follow-up:**
    - VillagerLayer rows can ride inside a greybox cutscene actor (`attach: child`);
    - Haluna's wake night (ch04/haluna_wake) gets the seven villagers at the feast;
    - fixed a FieldNpc bug where two villagers in different parents read 0 m apart and turned away;
    - new review shot npc_wake_feast (PC render requested).
  - **620:** the Act II roster (7 regulars, 4 variants, 4 bosses and a boss part) and design sheets for all of them (docs/kb/art/creatures/act2/).
  - **621, the Mangrove Drowner (Ch10 boss, worktree agent):**
    - 16.4k triangles; phase `uprooted` with the stump hidden after it; risen strike clips;
    - no enemies.json row yet (Act II encounters don't exist).
    - Polish notes are in M3-CRE-622: the roots read as smooth tubes and the risen pose as spidery.
  - **Checks run:** validate_data, taskboard, gdlint, gdformat, screenshot manifest; tools test_creatures, test_wildlife and test_npc OK; Godot creature 26/0, villager_routines 12/0, field_npc 10/0, wildlife 14/0; Blender verify identical for wildlife_insect and creature_mangrove_drowner.
  - **Checks skipped:** coverage (no game/battle or game/progression change); shots (now the PC's, see below).
- **Lead (for big10):** the KO-test fix is in big9. Act I's encounter needs are met: every enemy on every branch has a model except stillguard_inquisitor (a person).
- **Note for act1-chapters' Ch6 dressing:** when it merges, the wildlife_zone_brine_* shots will drift (the greybox becomes the kit). Re-approve after viewing; the wildlife data keeps its coordinates.

### Render requests
SUPERSEDED RENDER-REQUEST @ b5e05d2f: creature_drownbell, creature_drownbell_toll, creature_cinder_matron, creature_tower_limpet, creature_undertows_reach, creature_portraits, battle_choreo_melee, battle_choreo_hit, battle_choreo_cast, battle_choreo_support, battle_choreo_read, battle_choreo_ko, battle_choreo_swap, battle_choreo_lamp_dive, battle_choreo_toll, battle_choreo_vowbound_rise, battle_choreo_summon, creature_mangrove_drowner, creature_mangrove_drowner_risen, wildlife_stage, wildlife_zone_brine_flats, wildlife_zone_brine_wrecks, wildlife_zone_underway_crown, npc_haluna_dock, npc_haluna_market, npc_haluna_chapel, npc_haluna_lane, npc_stage_field, npc_wake_feast; why: M3-CRE-617 hit snap and rebuilt boss hits, M3-CRE-618 portrait lights, M3-CRE-621 new boss, M3-CRE-616 insects, M3-CRE-613/615 villager and wildlife review stages (every shot but npc_wake_feast was cloud-rendered, viewed and approved or compared before the directive; this pass confirms PC parity; npc_wake_feast has no baseline yet).
- **Merged big9 (integration 7cccb551) at d435d939.**
  - Append-only unions: ownership, asset_import, blender_builds (60 jobs), test_post_import, shots, baselines.
  - creature_portraits.png keeps this branch's version (it's in the render request).
  - **Checks run:** validate_data, taskboard, manifest, lint, format, tools tests; Godot creature 26/0, villager_routines 12/0, field_npc 10/0, wildlife 14/0, post_import 21/0, battle_ko_once 6/0 (big9's fix is in).
- **Lead's capsule item (battle_arena_camp):** the white capsule beside the raid hound is **`stillguard_inquisitor`** (Inquisitor Hadric Moll), a person, so it belongs to the characters track.
  - **Request filed:** M3-CRE-625 (role character, request-from creatures). It asks for a GLB with idle, attack, cast, hit and a kneeling yield `ko`. Creatures then wires the battle side (actor scene, creatures.json row).
  - characters' own M3-C06-06 (todo, unowned) lists him among a dozen Ch6 assets.
- **Capsule sweep** (enemies.json and encounters.json on the integration branch, act1-chapters, m2-slice, battle-presentation and characters; plus every skill summon and every set-piece entry):
  - **the only foe without a model is `stillguard_inquisitor`** (encounter ch06_inquisitor);
  - summons (spawn_polyp, squall_wing, tide_crawler) all have models;
  - set-piece entries (the_climb, the_surge, the_kirru) are timeline-only and never seated on the stage, so they draw no capsule.
- **MERGE-READY @ 10f21a17: M3-CRE-623, the Lamp Engine (Ch11 boss, worktree agent).**
  - 18.5k triangles; phase `opened` (the rings fold back as petals and the core shows), with opened-pose strike clips.
  - Checked by numbers, not renders: feet at y 0, every lamp clear of the frame, the core 1.3% visible closed and 48% open, every colour a palette swatch, no break parts yet (they need a charge skill).
  - **Checks run:** Godot creature 27/0, post_import 21/0, validate_data, taskboard, manifest, Blender verify identical.
- **Kit-wide finding (to fix later, M3 polish):** every creature GLB's clips play one frame (1/30 s) late in the file; a hit authored to peak at 0.10 s peaks at 0.13 s. The hit snap (0.1 s) still lands near half the recoil, so nothing is broken. Fixing it rebuilds all 29 creatures, so it waits for a batch rebuild.
SUPERSEDED RENDER-REQUEST @ 10f21a17: creature_lamp_engine, creature_lamp_engine_opened; why: M3-CRE-623 new Act II boss, never rendered (no baselines); check the battle-distance read, the closed-seam glow, and the hub and lamp teals reading apart.
- **MERGE-READY @ 21125780: M3-CRE-624, the Avalanche Ram (Ch12 boss, worktree agent).**
  - 15.2k triangles; a woolback grown huge, with frozen fleece locks, partings that glow spawn_wound, and the herd-cord.
  - Measured from the GLB: the head at 2.86 m; hooves solved to y 0 in every clip; the KO lies down without going below the floor.
  - **Checks run:** Godot creature 28/0, post_import 21/0, Blender verify identical (and the Lamp Engine's again on the merged tree), validate_data, taskboard, manifest, lint, format.
SUPERSEDED RENDER-REQUEST @ 21125780: creature_avalanche_ram; why: M3-CRE-624 new Act II boss, never rendered (no baseline); check the chest's front, the charge's raised foreleg, and the muzzle length at portrait distance.
- **DECISION: one villager runtime, two placements (the Lead's big11 note on the duplicate systems).**
  - **Creatures owns the runtime:** FieldNpc, NpcLook, the routines, npc.json, the zone routine files and VillagerLayer.
  - **Zone owners own placement.** Haluna keeps slice-polish's HalunaVillagers (M2-FP-102: it places a FieldNpc inside each body in HalunaZone.prebuild(), under the fade). That is the right place for it.
  - **The join, new here:** VillagerLayer now **adopts** villagers a zone placed itself, wiring only the chat partner, the work and shelter points and the storm flag. It never doubles them (tested: test_the_layer_adopts_villagers_a_zone_placed_itself).
  - **slice-polish (relay, please):** after `HalunaVillagers.populate(self)`, add **`VillagerLayer.wire(self, &"ch02/haluna")`**. That gives the netmender and the fisher their chat on the dock, and the work and shelter points. Glances, look-arounds and work already run on your FieldNpcs from npc.json.
    - Reed's sweep route and the child's lane walk need those two placed beside their bodies (a FieldNpc carries its body when it walks). Optional; tell me if you want it.
  - My review stage's Haluna placement is only for my shots; the game uses yours. Written into docs/kb/tech/field_npc.md, "Who owns what".
  - **Lead:** I'll take big11's test_villager_routines storm-flag fix when big11 reaches the integration branch.
- **MERGE-READY @ b99be560: M3-CRE-626, the Wakefin (Ch15 boss, worktree agent).** With it, all four Act II bosses are built.
  - 11.1k triangles; a black sailfish whose blade cuts the waterline at y 0, with sea-glow flank seams and spawn_wound wounds along the spine.
  - Measured: the blade top is 2.21 m at rest; the body sits below y 0 except in the breach; the KO lies belly-up at the surface.
  - **For the arena owner (Ch15, act1-chapters or whoever builds Act II arenas):** the submerged body stays hidden only if the barge arena has an opaque water surface at y 0. Its portrait shows the whole fish.
  - **Checks run:** Godot creature 29/0, Blender verify identical, validate_data, taskboard, manifest, lint, format, tools test_creatures.
SUPERSEDED RENDER-REQUEST @ b99be560: creature_wakefin; why: M3-CRE-626 new Act II boss, never rendered (no baseline); check the fin reads at battle distance and the waterline sits at the blade's base.
- **RENDERED @ b5e05d2f (gpu/render-creatures-b5e05d2), viewed:** 28 of 29 pass on the PC (most rmse 0), so every cloud-approved shot in it has pixel parity. npc_wake_feast had no baseline; viewed (Osu and the vendor face each other) and approved. Still open: the Lamp Engine, Avalanche Ram and Wakefin requests.
- **MERGE-READY @ 44080e1e: M3-CRE-627, Act II regulars for Ch10–11 (worktree agent)**, plus ADR 0150 (proposed).
  - The four regulars: tannin_archer 4.5k triangles, gallery_ray 4.1k (a flier, hover 1.4), rime_urchin 8.8k, conduit_crawler 4.8k (a construct; its light is glimmer_bound).
  - Every hit peaks at 0.10 s; checked from the GLBs; none is dark, so default portrait lights.
  - **Checks run:** Godot creature 33/0, Blender verify identical ×4, validate_data, taskboard, dlgc, manifest, lint, format.
  - **Lead, a rule conflict (ADR 0150, request M3-CRE-629 routed to you for art direction):**
    - palette.json forbids `spawn_wound` as a non-Undertow creature's weak point;
    - the creature README and every shipped beast use it (reef crab, lantern eel, gull harrier, shoal skipper, ashwing, slag tortoise).
    - Proposal: one weak-point colour for every foe (pillar 4). The spawn keep the wound language: open seams and motes. Nothing shipped changes.
SUPERSEDED RENDER-REQUEST @ 44080e1e: creature_tannin_archer, creature_gallery_ray, creature_rime_urchin, creature_conduit_crawler; why: M3-CRE-627 new Act II regulars, never rendered (no baselines).
- **MERGE-READY @ 37e4b4eb: M3-CRE-629 done (Lead-approved).**
  - ADR 0151 accepts one weak-point colour for every foe; ADR 0150 stays as the proposal.
  - docs/kb/art/palette.json `spawn_wound.usage_limit` amended: every foe's weak point; on a beast or construct, one small closed mark; the wound seams and motes stay the spawn's.
  - **M3-CRE-630 filed:** the one-frame-late clips, a kit fix for the next batch rebuild.
  - Checks: validate_data, taskboard. Nothing else touched.
- **MERGE-READY @ f21fba5f: M3-CRE-628, the Act II regulars for Ch12/16 and the four variants (worktree agent).** With it, every Act II creature on the roster is built.
  - **Regulars:** ridge_lynx 7.0k, cord_moth 4.1k (hovers at 1.25 m), glass_skate 2.6k (0.16 m tall, so its encounter row will want a low battle height for damage numbers and VFX anchors).
  - **Variants:**
    - root_crab, fen_leech and scree_crawler use new base-build parameters that default to the bases' own values; every base rebuilds identical (reef crab, wallcrab, wreck crab, sail leech, slag tortoise);
    - rim_crawler is palette only;
    - root crab, fen leech and scree crawler are dark, so they get rim 2.8 and kick 1.8.
  - **Checks run:** Godot creature 37/0 (no test lost in the merge), Blender verify identical ×12, validate_data, taskboard, manifest, lint, format, tools test_creatures.
  - **Filed M3-CRE-631:** shipped base clips that dip under the floor (reef crab family and tide crawler legs in the KO, down to −0.32 m; slag tortoise claws 4.5 cm at rest), the reef crab's faint weak point, and its triangle count over budget. It rides the M3-CRE-630 batch rebuild.
SUPERSEDED RENDER-REQUEST @ f21fba5f: creature_ridge_lynx, creature_cord_moth, creature_glass_skate, creature_root_crab, creature_fen_leech, creature_scree_crawler, creature_rim_crawler; why: M3-CRE-628 new Act II regulars and variants, never rendered (no baselines); judge whether the moth's knot rows and the skate's near-clear back read at battle distance.
- **MERGE-READY @ cbd1ce38: M3-CRE-630, creature clips no longer play one frame late.**
  - The kit keyed frame f+1 for clip time f/FPS, so every clip started and peaked 1/30 s late. Now fixed.
  - All 46 kit-dependent jobs rebuilt: 42 creature GLBs changed; materials and wildlife are unchanged.
  - **Checks run:** Blender verify identical ×46; Godot creature 37/0, battle 687/0, post_import 21/0.
  - **Lead:** the GLBs got heavier in git history (all 42 at once). One batch was on purpose: a kit change rebuilds them all.
  - **The PC render is held** until M3-CRE-631 (the shipped clips that dip under the floor, in progress in a worktree agent) lands, so one cycle re-approves every creature and battle_choreo shot.
- **MERGE-READY @ 32f33a75: M3-CRE-631 (worktree agent) and M3-CRE-632 filed.**
  - Every frame of every clip of the reef crab, tide crawler and slag tortoise families (8 creatures) now stays at or above the floor, through a new `common/grounding.py` that turns or lifts a leg the least it takes.
  - The reef crab is within budget (7,928 triangles); its weak point reads (mask peak 1.0) as one small closed mark (ADR 0151).
  - New `GroundedClipsTest` in tools/tests/test_creatures.py.
  - **Checks run:** Godot creature 37/0, battle 687/0; tools test_creatures and test_blender_builds; Blender verify identical (all 42 creature jobs re-verified by the agent); validate_data, taskboard, lint, format.
  - **M3-CRE-632 filed:** ground the rest. The worst are the scuttler (−0.37), Matron (−0.35), shoal skipper (−0.32), raid hound and Drownbell (−0.22), and the ashwing (−0.63 even with its hover). It extends the test to every creature.
- **One render for everything since b5e05d2f** (it supersedes my open Act II requests): M3-CRE-630 shifted every creature clip a frame earlier and M3-CRE-631 re-posed 8 creatures, so any creature or battle shot can move. Expect small drift in the battle and creature shots; the Act II shots are first renders.
SUPERSEDED RENDER-REQUEST @ 32f33a75: battle_hud_preview, battle_swap_menu, battle_victory, battle_statuses, battle_swell_ring, battle_read_panel, battle_opening_banner, battle_swell_modes, battle_vowbound_call, battle_vowbound_out, battle_choreo_melee, battle_choreo_hit, battle_choreo_cast, battle_choreo_support, battle_choreo_read, battle_choreo_ko, battle_choreo_swap, battle_arena_tideline, battle_arena_causeway, battle_choreo_lamp_dive, battle_choreo_toll, battle_choreo_vowbound_rise, battle_choreo_summon, battle_swell_chant, battle_swell_brace, battle_swell_glyph, battle_statuses_colorblind, battle_pause, creature_reef_crab, creature_reef_crab_attack, creature_drownbell, creature_drownbell_rim_broken, creature_drownbell_toll, creature_portraits, creature_hullgnaw, creature_mangrove_drowner, creature_mangrove_drowner_risen, creature_lamp_engine, creature_lamp_engine_opened, creature_tower_limpet, creature_lantern_eel, creature_oil_slug, creature_spawn_polyp, creature_glassfry, creature_bottle_hermit, creature_gull_harrier, creature_sail_leech, creature_spar_wraith, creature_scuttler, creature_ashwing, creature_slag_tortoise, creature_cinder_matron, creature_shoal_skipper, creature_raid_hound, creature_tide_crawler, creature_vein_sparker, creature_undertows_reach, creature_flue_moth, creature_wallcrab, creature_stormgull, creature_squall_wing, creature_wreck_crab, creature_wall_polyp, battle_arena_raft, battle_arena_underway, battle_arena_route, battle_arena_derelict, battle_arena_terrace, battle_boss_intro_hullgnaw, battle_arena_tideline_dawn, battle_arena_causeway_disc_sunset, battle_arena_causeway_route_afternoon, battle_arena_derelict_deck_night, battle_arena_ash_terrace_lanternfall, battle_arena_oruvel_raft_morning, battle_arena_underway_tower, battle_arena_shoals, battle_arena_camp, battle_boss_intro_inquisitor, battle_boss_intro_matron, battle_boss_intro_hermit, battle_boss_intro_wraith, battle_boss_intro_drownbell, battle_hud_21x9, battle_hud_16x10, creature_avalanche_ram, creature_wakefin, creature_tannin_archer, creature_gallery_ray, creature_rime_urchin, creature_conduit_crawler, creature_ridge_lynx, creature_cord_moth, creature_glass_skate, creature_root_crab, creature_fen_leech, creature_scree_crawler, creature_rim_crawler; why: M3-CRE-630 clip timing (all creature GLBs), M3-CRE-631 grounding (8 creatures), and the never-rendered Act II creatures (M3-CRE-623/624/626/627/628).
- **TOP ITEM, the big11 gate's shutdown errors ("Trying to cast a freed object"): root-caused. MERGE-READY @ 731beb70 for my part. FAST-TRACK candidate.**
  - **Reproduced** headless on lead/gate-big11 @ 23ea8c6f with capture.gd's lifecycle (no render: instance, 20 frames, queue_free, next shot): **64 errors, every one at `LifeAudio.advance` (game/audio/life_audio.gd:86)**.
    - That file is the audio track's (M3-AUD-814).
    - `var node := w["node"] as Node3D` casts a freed villager or wildlife node one line before its `is_instance_valid` check.
  - **Verified fix:** check as a Variant first, then cast (5 lines). The same repro then gives **0 errors, exit 0**.
  - The exact patch is in request **M3-CRE-633** (role audio). Its newest branch (M3-AUD-826) also casts the footstep child it frees, which the task covers too.
  - **Lead: suggest fast-tracking that patch onto big11.** It's audio's file, so with their OK or yours.
  - **My side (0a6a0937):** VillagerLayer had the same latent pattern (a typed loop variable over freed keys), now fixed. New test `test_the_layer_survives_its_villagers_being_freed_first`, verified red on the old code with exactly this error.
  - **Checks run:** Godot villager_routines 14/0, field_npc 10/0, wildlife 14/0, lint, format, taskboard.
- **Merged big11 (integration f85a361b).**
  - Unions: blender_builds by job id (74 jobs, the integration's text plus my 16 newer jobs); shared files via merge_union.
  - **Checks run:** villager_routines 14/0 (includes big11's storm-flag fix), field_npc 10/0, wildlife 14/0, battle 710/0, post_import 21/0, the tools suites, validate_data (1 warning, env-art's: `offering_step.glb` listed in PROVENANCE but missing), lint, format.
  - **Known red, FAST-TRACK for ui-menus or the Lead:** creature 41/1. ui's test_creature_portraits wants a bestiary portrait for every creatures.json row, and my 15 Act II creatures have no enemy yet (so no bestiary entry).
    - **Request M3-CRE-634** (role ui) carries a 3-line patch, verified 4/0 here, that limits the rule to the creatures enemies use. I didn't commit it to their file.
    - The integration branch itself is green: it doesn't have the Act II rows yet.
  - **The shutdown freed-object error on the integration branch** is fixed only once audio's LifeAudio takes the M3-CRE-633 patch. My VillagerLayer fix doesn't clear it on its own.
- **RENDERED @ 10f21a1, 2112578, b99be56 (the Lamp Engine ×2, the Avalanche Ram, the Wakefin), viewed: not approved.**
  - These shas predate M3-CRE-630, which shifted every creature clip by a frame. Baselines come from the 98-shot render at 4214a48e, which covers the same ids.
  - **Review:**
    - **The Lamp Engine** reads as its sheet, closed and opened.
    - **The Ram's head reads as a duck's:** the dark flat muzzle on a white face looks like a bill. It needs a camelid head.
    - **The Wakefin's review shot** shows only the fin, because the stage floor hides the body; it needs a shot that shows the fish, and stronger wounds.
  - Filed **M3-CRE-635**.
- **MERGE-READY @ 5ff54f27: M3-CRE-635 (worktree agent).**
  - **The Avalanche Ram:** a camelid head (long, narrow, a soft muzzle dark only at the nose, long upright ears); the neck slimmer; the icicles fewer and irregular. 14.9k triangles. Silhouettes viewed: it reads as a llama-like woolback, no longer a duck.
  - **The Wakefin:** stronger spine wounds, and a new shot `creature_wakefin_body` through a new creature-stage `show_floor` option (existing shots unchanged).
  - **Checks run:** Godot creature 41/1 (the known M3-CRE-634, ui's), Blender verify identical ×2, tools test_creatures, validate_data, lint.
  - Note: tools' test_screenshots baseline check stays red for shots that wait on their first PC render (expected under the render protocol).
SUPERSEDED RENDER-REQUEST @ 5ff54f27: creature_avalanche_ram, creature_wakefin, creature_wakefin_body; why: M3-CRE-635 the Ram's new head, the Wakefin's wounds and its new body shot (these three supersede the same ids in the 4214a48e request).
- **MERGE-READY @ fce2e82b: M3-CRE-632, every creature grounded (worktree agent).**
  - 19 creatures re-keyed or grounded. The worst before: spar-wraith −0.91, ashwing −0.63, flue moth −0.62, scuttler −0.38, Matron −0.35. Now every frame of every clip is ≥ −0.005 m, fliers measured with their hover.
  - GroundedClipsTest covers every creature except six whose sheets put them in water or behind a parapet: hullgnaw, lantern eel, Mangrove Drowner, Undertow's Reach, Wakefin, tannin archer. Each is commented with its sheet.
  - Contacts and hit peaks are unchanged, except the squall wing's hit_b, which now peaks at 0.20 s instead of 0.27 s.
  - Noted for review: the oil slug floats 5 cm at rest.
  - **Checks run:** Blender verify identical (all 42 creature jobs re-verified by the agent; 5 re-verified here after merging with M3-CRE-635); tools test_creatures and test_blender_builds; Godot battle 710/0, creature 41/1 (the known M3-CRE-634, ui's); validate_data, taskboard, lint, format.
- **One render for everything at fce2e82b.** It supersedes the 4214a48e and dc7b81aa requests: since them, M3-CRE-632 changed 19 creatures and M3-CRE-635 changed the Ram and the Wakefin.
SUPERSEDED RENDER-REQUEST @ fce2e82b: battle_hud_preview, battle_swap_menu, battle_victory, battle_statuses, battle_swell_ring, battle_read_panel, battle_opening_banner, battle_swell_modes, battle_vowbound_call, battle_vowbound_out, battle_choreo_melee, battle_choreo_hit, battle_choreo_cast, battle_choreo_support, battle_choreo_read, battle_choreo_ko, battle_choreo_swap, battle_arena_tideline, battle_arena_causeway, battle_choreo_lamp_dive, battle_choreo_toll, battle_choreo_vowbound_rise, battle_choreo_summon, battle_swell_chant, battle_swell_brace, battle_swell_glyph, battle_statuses_colorblind, battle_pause, creature_reef_crab, creature_reef_crab_attack, creature_drownbell, creature_drownbell_rim_broken, creature_drownbell_toll, creature_portraits, creature_hullgnaw, creature_mangrove_drowner, creature_mangrove_drowner_risen, creature_lamp_engine, creature_lamp_engine_opened, creature_tower_limpet, creature_lantern_eel, creature_oil_slug, creature_spawn_polyp, creature_glassfry, creature_bottle_hermit, creature_gull_harrier, creature_sail_leech, creature_spar_wraith, creature_scuttler, creature_ashwing, creature_slag_tortoise, creature_cinder_matron, creature_shoal_skipper, creature_raid_hound, creature_tide_crawler, creature_vein_sparker, creature_undertows_reach, creature_flue_moth, creature_wallcrab, creature_stormgull, creature_squall_wing, creature_wreck_crab, creature_wall_polyp, battle_arena_raft, battle_arena_underway, battle_arena_route, battle_arena_derelict, battle_arena_terrace, battle_boss_intro_hullgnaw, battle_arena_tideline_dawn, battle_arena_causeway_disc_sunset, battle_arena_causeway_route_afternoon, battle_arena_derelict_deck_night, battle_arena_ash_terrace_lanternfall, battle_arena_oruvel_raft_morning, battle_arena_underway_tower, battle_arena_shoals, battle_arena_camp, battle_boss_intro_inquisitor, battle_boss_intro_matron, battle_boss_intro_hermit, battle_boss_intro_wraith, battle_boss_intro_drownbell, battle_hud_21x9, battle_hud_16x10, creature_avalanche_ram, creature_wakefin, creature_wakefin_body, creature_tannin_archer, creature_gallery_ray, creature_rime_urchin, creature_conduit_crawler, creature_ridge_lynx, creature_cord_moth, creature_glass_skate, creature_root_crab, creature_fen_leech, creature_scree_crawler, creature_rim_crawler, drownbell_flood, causeway_c08_drownbell_disc_approach; why: M3-CRE-630 clip timing, M3-CRE-631/632 grounding (every creature), M3-CRE-635 the Ram's head and the Wakefin, and the never-rendered Act II creatures (101 shots; supersedes 4214a48e and dc7b81aa).
- **MERGE-READY @ 95b6daf8: the bestiary portrait manifest (the Lead's big12 note).** All 15 Act II creatures added to tools/portraits/portraits.json (the dark five with light_scale ×3). test_creature_portraits stays red until the bake below lands; I then commit the PNGs and their PROVENANCE rows.
- **The Wakefin, answering the Lead:**
  - Yes: in battle, the fin breaking the surface is intended (sheet act2/wakefin.md: "most of the fight: the fin alone"). The body shows when it breaches to attack, and in its KO (belly-up at the surface).
  - The review stage's opaque floor hid the body. M3-CRE-635 (in this branch) adds `creature_wakefin_body` with the floor off and strengthens the spine wounds.
  - **For the Ch15 barge arena** (whoever builds the Act II arenas): it needs an opaque water surface at y 0, so the submerged body stays hidden. On a plain floor it reads like the creature stage.
  - The bestiary portrait has no floor, so it shows the whole fish.
SUPERSEDED RENDER-REQUEST @ 95b6daf8: portraits:mangrove_drowner,lamp_engine,avalanche_ram,wakefin,tannin_archer,gallery_ray,rime_urchin,conduit_crawler,ridge_lynx,cord_moth,glass_skate,root_crab,fen_leech,scree_crawler,rim_crawler; tool: tools/portraits/render.sh --only mangrove_drowner,lamp_engine,avalanche_ram,wakefin,tannin_archer,gallery_ray,rime_urchin,conduit_crawler,ridge_lynx,cord_moth,glass_skate,root_crab,fen_leech,scree_crawler,rim_crawler
- **Queue status for the Lead (your 19:34 list):**
  1. **Portrait manifest and Wakefin:** done before your note. 95b6daf8 has all 15 Act II creatures and the portrait RENDER-REQUEST; the Wakefin answer is above.
  2. **The one-frame-late clips:** done at cbd1ce38 (M3-CRE-630: 46 jobs rebuilt, verify identical ×46). hit_snap re-tuned now at the push after 27f39bbe: 0.067 s default, the ashwing 0.1 s, measured over all 42 on-time hits. Render: the 101-shot request at 5e46d7dd covers every creature and battle shot. The re-tune can move battle_choreo_hit again, so view that one against this head.
  3. **Capsule sweep on integration 73cddee1:** still only stillguard_inquisitor (Moll, characters, M3-CRE-625). Summons and set-piece entries are clean.
  4. **Act II:** the roster's 15 creatures are built. The flat-engine (Ch14 boss part) has its sheet now and is building (M3-CRE-637). The Drowner polish (M3-CRE-622) is building. Both are worktree agents.
  5. **Wildlife:** Ch8 corrow and coilspire added (M3-CRE-636). Ch5 Ashcrown, Ch7 bell galleries and Ch9 Corrow-night stay empty on purpose (reasons in docs/kb/art/wildlife.md; Corrow-night: crabs among the shrouds would read as carrion). Ch4, Ch5 Pemakar and Ch7 Tamsule have had data since M3-CRE-615/616.
  6. **Task board, creatures' todos:** M3-AUD-815 done (`chat_speaking()`, `startled()`); M3-CRE-201 closed (the Matron's model had landed); M3-CRE-622 in progress. The rest of the character todos are the characters track's.

- **MERGE-READY @ db3c9507: M3-CRE-637 (the flat-engine, Ch14 boss part) and M3-CRE-622's first pass.**
  - Flat-engine: 7,620 triangles; a lacquer drum, chimney, salt-glass window and eight paddles flat on the water; 13 bones; `cast` presses the paddles at 0.8 s; `ko` splits the drum. Grounded at 0.000 in every frame; no allow-list.
  - **Not wired yet:** its `break_parts` entry needs a charge skill that doesn't exist yet. The task file has the exact entry. Until then the window stays lit through the KO.
  - The Drowner's first polish pass is merged as a step. On review its silhouettes still read as a spider (the top view a sunburst), so M3-CRE-622 is reopened with a redesign direction: a vertical trunk, tiered lopsided roots, and hanging aerial roots.
  - **Checks run:** Blender verify identical (flat_engine ×5); Godot creature 42/1 (the known portrait red); tools test_creatures and test_blender_builds; validate_data, taskboard, lint, format.
SUPERSEDED RENDER-REQUEST @ db3c9507: creature_flat_engine, creature_mangrove_drowner, creature_mangrove_drowner_risen; why: M3-CRE-637 first render of the flat-engine (its near-black drum: check it reads on default lights) and M3-CRE-622's first Drowner pass (to compare with the redesign).
SUPERSEDED RENDER-REQUEST @ db3c9507: portraits:flat_engine; tool: tools/portraits/render.sh --only flat_engine
- **big12 merged in (integration e930595c).** Conflicts were unioned:
  - blender_builds.json: the integration's text, with the 12 creature jobs only here appended;
  - ownership, PROVENANCE, shots and baselines;
  - creature_portraits.png: the integration's PC-gated baseline.
- **TOP ITEM (Lead): Ilun, Asha's Vowbound, is building (M3-CRE-638, claimed by creatures, worktree agent).**
  - The order: a design sheet (docs/kb/art/creatures/vowbound/ilun.md), the model and clips (idle … victory, plus rise, dismiss and special), then the attach.
  - The attach goes through CreatureModels (a creatures.json row with `"vowbound": true`), so ui's battle_sandbox.json capsule row stays only as the fallback.
  - **For battle-presentation:** M3-CRE-639 (role combat) asks you to play `rise`, `dismiss` and `special` from choreo.json once the model lands. The existing `ready` and `ko` keep working until then.
  - **Checks run on the big12 merge:** Godot full 2830/2 (the Lead's known two: creature portraits, ours, waits on the PC bake; the footsteps causeway test, audio's); tools test_creatures, test_blender_builds, test_npc; validate_data, taskboard, lint, format.
- **MERGE-READY @ 3b0e44b0: M3-CRE-622, the Mangrove Drowner redesigned** (the redesign, after the first pass still read as a spider).
  - It's a walking mangrove stump now: a tall trunk; twelve roots in four lopsided bundles, the bank side longest; aerial roots.
  - Risen, it tears the trunk up, leans 48° and walks on three root clusters.
  - Grounded in every clip at +0.002 m with no allow-list (the old allow-list entry is removed). 14,700 triangles.
  - Silhouette check (side, front and top for rooted, KO, phase change and risen): every top view is lopsided bundles, no sunburst. The one risk left is the risen front view, a dark dome on splayed roots, so the render decides.
  - **Checks run:** Blender verify identical ×3; tools test_creatures (the grounding test passes) and test_blender_builds; Godot creature 42/1 (the known portrait red); validate_data, taskboard.
SUPERSEDED RENDER-REQUEST @ 3b0e44b0: creature_mangrove_drowner, creature_mangrove_drowner_risen, creature_flat_engine; why: M3-CRE-622 redesign (supersedes the db3c9507 Drowner ids; is the risen front still spider-like?) and M3-CRE-637's first flat-engine render (carried over from db3c9507).
SUPERSEDED RENDER-REQUEST @ 3b0e44b0: portraits:mangrove_drowner,flat_engine; tool: tools/portraits/render.sh --only mangrove_drowner,flat_engine
- **The PC is paused (Lead, 21:27), so here are my open render requests in priority order, kept small.** Serve them one line at a time; each line stands alone.
  1. The `aa762dee` portraits line (mangrove_drowner, flat_engine) and the 13 other Act II portraits from `95b6daf8`. These turn test_creature_portraits green, the one red owned by creatures in big12. Split them into batches of five if needed.
  2. The `aa762dee` shots line: creature_mangrove_drowner, creature_mangrove_drowner_risen, creature_flat_engine.
  3. A small sample to check the clip-timing and grounding batch: battle_choreo_hit, battle_choreo_ko, creature_reef_crab, creature_ashwing, creature_avalanche_ram, creature_wakefin, creature_wakefin_body.
  4. The rest of the 101-shot `fce2e82b` request is **deferred, not cancelled.** It waits for the PC to return. Until then those baselines stay as they are; they drift by a frame, not by design.
SUPERSEDED RENDER-REQUEST @ aa762dee: battle_choreo_hit, battle_choreo_ko, creature_reef_crab, creature_ashwing, creature_avalanche_ram, creature_wakefin, creature_wakefin_body; why: priority 3 above (sample of M3-CRE-630/631/632/635 while the PC is paused).
- **PC render gpu/render-creatures-fce2e82 viewed (101 shots: 41 passed, 60 drifted). Approved 28 at c69a14de.**
  - **Approved:** 16 creature shots, which moved only where M3-CRE-630/631/632 meant them to (legs, feet and rims lifted onto the floor), plus 12 first baselines (creature_wakefin_body and 11 Act II creatures).
  - **Not approved from it (stale):** the 27 battle_* shots that drifted, creature_portraits, creature_lamp_engine(_opened), creature_avalanche_ram and creature_wakefin. big12 changed their baselines or their battle-scene sources after fce2e82b; the integration's PC gate already approved the big12 versions.
  - **For the art review (no blocker):** at review distance the gallery ray and the glass skate read small and plain (a flat sheet); the ridge lynx's muzzle reads short. They're baselined as built, with possible polish later.
  - **Supersedes my priority 3 above:** the reef crab, the Ram, both Wakefin shots and the ashwing are settled (the ashwing passed). What's left is the battle sample against this head:
SUPERSEDED RENDER-REQUEST @ c69a14de: battle_choreo_hit, battle_choreo_ko, battle_choreo_melee, battle_boss_intro_matron; why: M3-CRE-630 clip timing and the hit_snap re-tune, on the big12 tree (small sample while the PC is paused).
- **MERGE-READY @ 14e26ef6: M3-CRE-638, Ilun, Asha's Vowbound, in place of the battle capsule (the Lead's top item).**
  - **The model:** a 4.6 m spectral manta with a heron's crest; a net of glimmer_bound light, as geometry on both wing faces; the glass net-float on a drooping tail.
    - 13,655 triangles; 16 bones; every glow is steady glimmer_bound at 1.2.
    - Opaque (the creature shader has no alpha). He reads as spectral through a dark core, pale edges and a rim sheen. True alpha is a possible follow-up after the render.
  - **Clips:**
    - the stand-in set: idle, ready, attack, cast, hit, defend, ko, victory;
    - rise (2.6 s), dismiss (1.0 s) and special (Floodnet, contact 1.45 s).
    - None goes below the water.
  - **The attach:** CreatureModels.stand_in_overrides now also resolves a creatures.json row with `"vowbound": true`. No ui or battle-presentation file changed; battle_sandbox.json's capsule row is only the fallback.
  - **For battle-presentation (M3-CRE-639, updated):** a data-only change to play rise and dismiss. Until then ready plays, which works. Framing: in the vertex preview his tail and float cross the right edge of the safe frame, so the render decides.
  - **For ui (M3-CRE-634, updated):** test_creature_portraits now also flags the ilun row (the bestiary is foes only). The same enemies-only fix covers it.
  - **Checks run:** Blender verify identical; tools test_creatures and test_blender_builds; Godot creature 46/1 (the known portrait red), vowbound 54/0, battle 720/0; validate_data, taskboard, lint, format.
SUPERSEDED RENDER-REQUEST @ 14e26ef6: creature_ilun, battle_vowbound_out, battle_choreo_vowbound_rise, battle_choreo_summon; why: M3-CRE-638, Ilun's first renders (the three Vowbound battle shots move from the capsule to the model; creature_ilun has no baseline). Check his framing in the safe frame.
- **For battle-presentation: Ilun's model is live in the real summon path @ a785a613.**
  - BattleStage.sync_party → _place → stand_in_spec → CreatureModels gives the called Vowbound the model in battle_vowbound_call and battle_vowbound_out, the short entry (battle_choreo_vowbound_rise) and the full first-call cinematic (battle_choreo_summon).
  - New integration test tests/integration/test_ilun_summon_path.gd calls him the way the shots do and asserts the stand-in shows the actor, not the capsule.
  - Your summon choreography already moves the model; only the clip names are left (M3-CRE-639: rise and dismiss in choreo.json).
- **Portrait manifest complete @ a785a613:** `ilun` added (the Lead's list); mangrove_drowner, lamp_engine, avalanche_ram and wakefin were already there (95b6daf8). test_creature_portraits now fails only on the 17 unbaked PNGs below. **This one bake request supersedes my earlier portrait lines (95b6daf8, aa762dee).** Batches of six:
SUPERSEDED RENDER-REQUEST @ a785a613: portraits:mangrove_drowner,lamp_engine,avalanche_ram,wakefin,ilun,flat_engine; tool: tools/portraits/render.sh --only mangrove_drowner,lamp_engine,avalanche_ram,wakefin,ilun,flat_engine
SUPERSEDED RENDER-REQUEST @ a785a613: portraits:tannin_archer,gallery_ray,rime_urchin,conduit_crawler,ridge_lynx,cord_moth; tool: tools/portraits/render.sh --only tannin_archer,gallery_ray,rime_urchin,conduit_crawler,ridge_lynx,cord_moth
SUPERSEDED RENDER-REQUEST @ a785a613: portraits:glass_skate,root_crab,fen_leech,scree_crawler,rim_crawler; tool: tools/portraits/render.sh --only glass_skate,root_crab,fen_leech,scree_crawler,rim_crawler
- **Queue status for the Lead (your 22:29 list):**
  1. **Ilun in the real summon path:** done, with an integration test and a note for battle-presentation above.
  2. **Portrait manifest:** done, ilun added. One bake request now covers all 17 missing PNGs (above).
  3. **One-frame clip batch rebuild:** done earlier (M3-CRE-630 @ cbd1ce38, 46 jobs). The kit still keys frame f. The PC render fce2e82 confirmed it, and I approved 28 shots from it.
  4. **Wildlife Ch4–Ch9:** every zone has data except ch05/ashcrown, ch07/tamsule_bell_galleries and ch09/corrow_night, which are empty on purpose (docs/kb/art/wildlife.md gives the reasons).
  5. **More creatures:** the Act II roster is fully built (the outline has no other foe fights: Ch13 has none, Ch14's boss is the Warden plus the flat-engine, Ch16's is people). The next gap is the **Vowbound**:
     - Kahre (Ch5) and Virel (Ch8) are callable in vowbound.json, but a call shows a primitive placeholder, as Ilun did. Now building in parallel: M3-CRE-640 and M3-CRE-641.
     - After them, Act II's Nhoa (Ch11), Hesk (Ch12) and Ethren (Ch13). They aren't in vowbound.json yet; Combat adds the rows.
- **Act II Vowbound: design sheets written** (docs/kb/art/creatures/vowbound/nhoa.md, hesk.md, ethren.md). Build tasks M3-CRE-642/643/644 are filed as `todo`; they follow Kahre and Virel.
  - **For Combat:** none of the three has a vowbound.json row yet. The models don't wait on stats, only their skill-to-clip maps do.
  - **For the Lead (no human question):** two palette calls are flagged in the sheets, each with a default that stays inside the palette rules:
    - Hesk's "white light" is drawn as glimmer_bound on gauze-white cords; a true white-gold holy light would need a palette ADR.
    - Ethren is lacquer with gold only on the edges, to hold gold_leaf's 5%-of-frame budget; a fully gold figure would need a Sanctum exception.
  - **For rendering:** Nhoa's Farewell-Tide rising column is the one bound-light exception vowbound.md names. color_script.md should say so; it's your file.
- **MERGE-READY @ e1229633: M3-CRE-640, Kahre, the Forge-Crowned, the Ch5 Lightning Vowbound, in place of the placeholder.**
  - **The model:** a 3.37 m hornbill-headed smith-beast: an anvil-plate chest, a spark mane of 25 skinned bolt blades (not particles), and the smith's hammer fused into his brass casque (never lit). Every glow is steady glimmer_bound.
    - 14,080 triangles, 22 bones.
    - Feet planted at 0.000 m in every clip.
  - **Clips:** the stand-in set, plus rise, dismiss and special (Last Strike, contact 1.55 s).
  - **Framing:** projected through the camera director's own math, every frame stays inside the default camera's right safe edge. The cast and the Last Strike's rear-up cross the top margin, but the action's own lead shot plays then.
  - **The attach:** the same CreatureModels vowbound path as Ilun. His creatures.json stand_in carries height 3.3 and radius 0.75, because ui's battle_sandbox.json has no kahre row and the effect anchors need a height.
  - **For battle-presentation:** M3-CRE-639's rise and dismiss request covers Kahre too. choreo.json has no first-call flag for kahre, so his first call never plays the summon cinematic; that's for story/your call.
  - **For ui:** optionally, a battle fixture binding Kahre, so a Vowbound shot can show him.
  - **Checks run:** Blender verify identical; tools test_creatures and test_blender_builds; Godot creature 50/1 (the known portrait red, now including kahre.png), vowbound 58/0, kahre 6/0, ilun 6/0, battle 720/0 (run by the agent); validate_data, taskboard, lint, format.
SUPERSEDED RENDER-REQUEST @ e1229633: creature_kahre; why: M3-CRE-640 first render (no baseline). Check that the hide reads as dark stone, not teal, and that the anvil reads as iron.
SUPERSEDED RENDER-REQUEST @ e1229633: portraits:kahre; tool: tools/portraits/render.sh --only kahre
- **MERGE-READY @ 3d853298: M3-CRE-641, Virel, the Kite-Serpent, the Ch8 Fire Vowbound, in place of the placeholder.**
  - **The model:** a 6.25 m ribbon of sailcloth panels on light timber spars, coiled once around an upright loop, hovering 1.7 m up. A three-line bridle carries the brass tuning key.
    - The seam light is skinned bands of steady glimmer_bound (not particles). There's no warm colour on her form: palette.json keeps ember_orange to flame, and act1_ch08.md F07 says her seams read as bound teal, with the fire in her battle VFX.
    - 12,158 triangles; 16 bones.
  - **Clips:** the stand-in set, plus rise, dismiss and special (Flare Line, contact 1.4 s: pulled into one taut 5.4 m line).
  - **Framing:** the coil keeps her inside the default camera's safe frame. One frame of Flare Line touches the right edge, by under 3 px.
  - **For ui:** battle_sandbox.json has no `virel` row, so her damage numbers sit at 1.0 m and the chest anchor at 1.7 m (the bottom of her loop). A row with height 2.6 fixes both. (Kahre's height lives in creatures.json for the same reason; either place works, your call.)
  - **For battle-presentation:**
    - choreo.json first_call_flags lists only ilun, so Virel's first call at the wall-head (Ch8) needs a `virel` flag to play the cinematic;
    - M3-CRE-639's rise and dismiss request covers her too.
  - **For battle VFX:** her fire has to come from the Kite Flare and Flare Line effects; her seams never change colour.
  - **Checks run:** Blender verify identical (virel, kahre); tools test_creatures and test_blender_builds; the screenshot manifest (357 valid); Godot creature 54/1 (the known portrait red, now 19 PNGs with kahre and virel), vowbound 62/0, kahre, virel and ilun 6/0 each, battle 720/0; validate_data, taskboard, lint, format.
SUPERSEDED RENDER-REQUEST @ 3d853298: creature_virel, creature_kahre; why: M3-CRE-641 and M3-CRE-640 first renders (no baselines). Supersedes the 25f03f01 kahre line.
SUPERSEDED RENDER-REQUEST @ 3d853298: portraits:kahre,virel; tool: tools/portraits/render.sh --only kahre,virel
- **Self-directed backlog (TRACK-RULES 22:50):**
  - **Render branches:** none for creatures yet (the Lead's server has rendered other tracks so far).
  - **M3-CRE-100 done (request from cinematics) @ 80027744:**
    - Haluna's shopkeeper, smith and innkeeper are now VillagerLayer rows, with an optional `actor` override; they wear the netmender's, fisher's and vendor's models until M2-CHR-100.
    - The review stage reuses the zone's own layer.
    - A layer added during its zone's `_ready` builds deferred, so it adopts what the zone places after it; nothing doubles while the shim exists.
    - **Cinematics: you can delete game/data/flow/haluna_villagers.json and the HalunaVillagers placement shim** (keep end_talks).
    - Checks run: Godot villager 25/0, haluna_villagers (yours) 7/0, field_npc 10/0, life_audio 10/0, fp_thread 2/0; tools test_npc; validate_data, lint, format.
  - **M3-C05-05, M3-C06-06 and M3-C04-06, the creature parts:** all ten Ch4–Ch6 creatures are seated in battle. The Matron's skills now map to her clips (slag_pour → the ladle pour-swing) @ 842a2b6e. The humans, VFX and rulings stay with their tracks (noted in each task).
SUPERSEDED RENDER-REQUEST @ 842a2b6e: npc_haluna_dock, npc_haluna_market, npc_haluna_chapel, npc_haluna_lane, npc_wake_feast, battle_boss_intro_matron; why: M3-CRE-100 (the review stage now reuses Haluna's own VillagerLayer, so no doubled villagers, and the three shop villagers appear), and the Matron's skill clips.
- **test_creature_portraits (Lead, big13): the manifest is complete. The red is unbaked PNGs, not missing manifest rows.**
  - On `lead/gate-big13` @ 1d83553f, all 43 creatures.json rows have a tools/portraits/portraits.json entry (I checked by script).
  - On claude/creatures @ 6082090b, all 46 do.
  - The failures are each portrait's "exists / is imported / has a PROVENANCE row" checks for PNGs nobody has baked yet: 16 on big13, 19 here (plus ilun, kahre and virel, which landed after big13).
  - The fix is the bake. **ONE request for all of them, superseding my earlier portrait lines (95b6daf8, aa762dee, a41ab41c, 25f03f01, 1f69ca74):**
SUPERSEDED RENDER-REQUEST @ 6082090b: portraits:avalanche_ram,conduit_crawler,cord_moth,fen_leech,flat_engine,gallery_ray,glass_skate,ilun,kahre,lamp_engine,mangrove_drowner,ridge_lynx,rim_crawler,rime_urchin,root_crab,scree_crawler,tannin_archer,virel,wakefin; tool: tools/portraits/render.sh --only avalanche_ram,conduit_crawler,cord_moth,fen_leech,flat_engine,gallery_ray,glass_skate,ilun,kahre,lamp_engine,mangrove_drowner,ridge_lynx,rim_crawler,rime_urchin,root_crab,scree_crawler,tannin_archer,virel,wakefin
  - Once the PNGs land (a lead/gate-render-creatures branch), I'll view each one, commit them with their PROVENANCE rows, and the test turns green.
- **MERGE-READY @ f5025cdb: M3-CRE-642 Nhoa and M3-CRE-643 Hesk, Act II's Ice and Holy Vowbound.**
  - **Nhoa (Ch11):** a 3.19 m figure of 1,623 bound-light mote beads skinned to her bones (not particles), with mangrove-root antlers. Her carved name-shell never glows; nothing on her is frozen (ADR 0015). 14,820 triangles, 28 bones. Inside the default camera's safe frame in every frame.
  - **Hesk (Ch12):** a condor whose primaries are knotted cords; the two leading cords read 47 and 7 in keth. Steady glimmer_bound light, strongest at the knots; the keth bundle is unlit. She stands on the water: every frame at y ≥ 0. 13,602 triangles, 25 bones. Inside the default camera's frame in every frame.
  - **New validator key `vowbound_pending` (tools/validate_creatures.py, ours):** both are modelled ahead of their vowbound.json rows (Combat's). The key names the task asking for the row, allows the missing row, and becomes an error once the row lands.
  - **For Combat:** vowbound.json rows for nhoa (her copy-the-last-action skill and farewell_tide) and hesk (cleanse and pass_cord), plus their loc keys. We then map their skills to clips and drop the pending keys.
  - **For battle-presentation:** first_call_flags for nhoa and hesk if their first calls should play the cinematic, plus M3-CRE-639 (rise and dismiss).
  - **For battle VFX and rendering:** Nhoa's Farewell-Tide rising column (the one bound-light exception) and Hesk's Pass-Cord line of knots.
  - **Checks run:** Blender verify identical (nhoa, hesk); tools test_creatures and test_blender_builds; the screenshot manifest (359 valid); Godot creature 65/1 (the known portrait red), vowbound 73/0, nhoa 7/0, hesk 8/0, villager 25/0; validate_data, taskboard, lint, format.
SUPERSEDED RENDER-REQUEST @ f5025cdb: creature_nhoa, creature_hesk, creature_kahre, creature_virel; why: first renders of the four new Vowbound (no baselines). Nhoa: do the beads read as one figure at battle distance? Hesk: do the knots read? Kahre: is the hide stone, not teal?
SUPERSEDED RENDER-REQUEST @ f5025cdb: portraits:nhoa,hesk; tool: tools/portraits/render.sh --only nhoa,hesk
- **Cloud render lead/gate-render-creatures-3b0e44b viewed and approved** (dc524c0c, 41493382):
  - creature_mangrove_drowner and creature_mangrove_drowner_risen: the redesign reads as a walking mangrove stump, no longer a spider, so M3-CRE-622 can close;
  - creature_flat_engine: first baseline;
  - the mangrove_drowner and flat_engine portraits are committed with PROVENANCE rows, which leaves test_creature_portraits 19 PNGs short.
- **ONE open render request (TRACK-RULES limit). Every earlier line above is now SUPERSEDED.** It covers only what changed since my last approved render:
  - the battle sample for the clip timing and hit_snap (4 shots);
  - Ilun's three Vowbound battle shots plus creature_ilun;
  - the Haluna villager stages (M3-CRE-100);
  - the four new Vowbound review shots;
  - the 19 unbaked portraits.

  The rest of the old 101-shot set stays deferred until the PC is back.
SUPERSEDED RENDER-REQUEST @ 41493382: battle_choreo_hit, battle_choreo_ko, battle_choreo_melee, battle_boss_intro_matron, creature_ilun, battle_vowbound_out, battle_choreo_vowbound_rise, battle_choreo_summon, npc_haluna_dock, npc_haluna_market, npc_haluna_chapel, npc_haluna_lane, npc_wake_feast, creature_kahre, creature_virel, creature_nhoa, creature_hesk, portraits:avalanche_ram,portraits:conduit_crawler,portraits:cord_moth,portraits:fen_leech,portraits:gallery_ray,portraits:glass_skate,portraits:ilun,portraits:kahre,portraits:lamp_engine,portraits:ridge_lynx,portraits:rim_crawler,portraits:rime_urchin,portraits:root_crab,portraits:scree_crawler,portraits:tannin_archer,portraits:virel,portraits:wakefin,portraits:nhoa,portraits:hesk; tool: tools/portraits/render.sh --only avalanche_ram,conduit_crawler,cord_moth,fen_leech,gallery_ray,glass_skate,ilun,kahre,lamp_engine,ridge_lynx,rim_crawler,rime_urchin,root_crab,scree_crawler,tannin_archer,virel,wakefin,nhoa,hesk; why: everything owed since my last approved renders (fce2e82, 3b0e44b): hit_snap and clip timing, Ilun, Kahre, Virel, Nhoa and Hesk (first renders), M3-CRE-100's villager stages, and the 19 portraits that turn test_creature_portraits green.
- **MERGE-READY @ 1b919d27: M3-CRE-644, Ethren, the Level Saint, the Ch13 Glimmer Vowbound.**
  - **The model:** a lacquer shrine-figure: lacquer_black and lacquer_red_deep, with gold_leaf on the edges only. Steady glimmer_bound shows only at the seams and the halo's inner face.
    - A still veil on its own bone and mesh (cinematics can drop it for Ch20; no face is modelled).
    - Four folded two-leaf wings that open only in ready, cast, special and victory.
    - The copper ring is unlit.
    - 14,406 triangles, 27 bones; hovers 0.2 m.
  - **Gold share (projected estimate):** 0.27–0.33% of the default frame and 1.2–1.35% of the summon frame, well under palette.json's 5%. The palette tool should confirm it on the first render.
  - **Framing:** inside the default camera's safe frame in every frame.
  - **Requests:**
    - Combat: his vowbound.json row and skills (his row carries vowbound_pending M3-CRE-644).
    - Battle-presentation: a first-call flag, and M3-CRE-639.
    - Battle VFX: Still Water's field stop at 1.45 s.
    - Characters: Corran's face under the veil for Ch20.
  - **Checks run:** Blender verify identical; tools test_creatures and test_blender_builds; the manifest (360 valid); Godot creature 71/1 (the known portrait red), vowbound 79/0, ethren 8/0, hesk 8/0, nhoa 7/0; validate_data, taskboard, lint, format.
- **The one open render request, re-posted to add Ethren** (the fef63392 line is SUPERSEDED):
SUPERSEDED RENDER-REQUEST @ 1b919d27: battle_choreo_hit, battle_choreo_ko, battle_choreo_melee, battle_boss_intro_matron, creature_ilun, battle_vowbound_out, battle_choreo_vowbound_rise, battle_choreo_summon, npc_haluna_dock, npc_haluna_market, npc_haluna_chapel, npc_haluna_lane, npc_wake_feast, creature_kahre, creature_virel, creature_nhoa, creature_hesk, creature_ethren, portraits:avalanche_ram,portraits:conduit_crawler,portraits:cord_moth,portraits:fen_leech,portraits:gallery_ray,portraits:glass_skate,portraits:ilun,portraits:kahre,portraits:lamp_engine,portraits:ridge_lynx,portraits:rim_crawler,portraits:rime_urchin,portraits:root_crab,portraits:scree_crawler,portraits:tannin_archer,portraits:virel,portraits:wakefin,portraits:nhoa,portraits:hesk,portraits:ethren; tool: tools/portraits/render.sh --only avalanche_ram,conduit_crawler,cord_moth,fen_leech,gallery_ray,glass_skate,ilun,kahre,lamp_engine,ridge_lynx,rim_crawler,rime_urchin,root_crab,scree_crawler,tannin_archer,virel,wakefin,nhoa,hesk,ethren; why: everything owed since my last approved renders (fce2e82, 3b0e44b): hit_snap and clip timing, the five new Vowbound (first renders), M3-CRE-100's villager stages, and the 20 portraits that turn test_creature_portraits green.
- **Backlog progress:**
  - **Primitive audit:** the only foe in encounters without a model is stillguard_inquisitor (Moll, a person: characters, M3-CRE-625). The plain reads from the fce2e82 render are now M3-CRE-645, building in a worktree: the gallery ray and glass skate (flat sheets at battle distance) and the ridge lynx's short muzzle.
  - **Next act (M3-CRE-646, review: Lead):** Act III roster proposal, docs/kb/art/creatures/act3_roster.md.
    - **Releases first:** the six Vowbound as foes in their Ch20 release fights. Same GLB, a held material set, a `release` clip; no second model, and the validator's "no Vowbound scene as an enemy model" rule holds.
    - **Then:** the Cage frame, with characters for the four founders; the Lamp Spire's three; two Undertow-layer regulars; the Ch18 revisit set and a secret-coordinates superboss.
    - **Lead / chapter designer:** confirm or cut ids before I build.
- **MERGE-READY @ 4320496f: M3-CRE-645, the plain reads polished** (from the primitive audit).
  - **Gallery ray:** a midline ridge with tubercles, pectoral bulges, brow ridges and spiracles, a barbed banded whip tail, and curling wing tips in idle. Its weak point is now one small closed spawn_wound lens (ADR 0151).
  - **Glass skate:** thornback rows, a sand_wet rim, and raised eye turrets.
  - **Ridge lynx:** a longer wedge muzzle with nose leather, whisker pads and whiskers.
  - Budgets, bones, clips and contacts are unchanged, and grounding holds.
  - **Checks run:** Blender verify identical (×3); tools test_creatures and test_blender_builds; Godot creature 71/1 (the known portrait red); validate_data, taskboard.
- **The one open render request, re-posted to add the three polished shots** (the 0276445e line is SUPERSEDED):
SUPERSEDED RENDER-REQUEST @ 4320496f: battle_choreo_hit, battle_choreo_ko, battle_choreo_melee, battle_boss_intro_matron, creature_ilun, battle_vowbound_out, battle_choreo_vowbound_rise, battle_choreo_summon, npc_haluna_dock, npc_haluna_market, npc_haluna_chapel, npc_haluna_lane, npc_wake_feast, creature_kahre, creature_virel, creature_nhoa, creature_hesk, creature_ethren, creature_gallery_ray, creature_glass_skate, creature_ridge_lynx, portraits:avalanche_ram,portraits:conduit_crawler,portraits:cord_moth,portraits:fen_leech,portraits:gallery_ray,portraits:glass_skate,portraits:ilun,portraits:kahre,portraits:lamp_engine,portraits:ridge_lynx,portraits:rim_crawler,portraits:rime_urchin,portraits:root_crab,portraits:scree_crawler,portraits:tannin_archer,portraits:virel,portraits:wakefin,portraits:nhoa,portraits:hesk,portraits:ethren; tool: tools/portraits/render.sh --only avalanche_ram,conduit_crawler,cord_moth,fen_leech,gallery_ray,glass_skate,ilun,kahre,lamp_engine,ridge_lynx,rim_crawler,rime_urchin,root_crab,scree_crawler,tannin_archer,virel,wakefin,nhoa,hesk,ethren; why: everything owed since my last approved renders (fce2e82, 3b0e44b): hit_snap and clip timing, the five new Vowbound, M3-CRE-100's villager stages, M3-CRE-645's polish, and the 20 portraits that turn test_creature_portraits green.
- **MERGE-READY @ db895430: M3-CRE-647, the six Vowbound as foes for their Ch20 releases** (Act III roster item 1).
  - **The models:** each keeps its one GLB.
    - Held material sets (`materials_held/`, glimmer_held in place of glimmer_bound, steady) come from an optional `held` block in write_materials.py. Every creature job still verifies byte-identical (53 jobs, run by the agent).
    - A `release` clip each (3.3–3.5 s): the form opens, holds, and lifts away at peace. Ilun gentle; Kahre "setting the tools down"; Ethren's ringed hand toward Ysolde.
  - **The rows:** a `<id>_held` battle scene and creatures.json row for each, facing the party, with `release` as the KO.
    - New CreatureActor `material_dir` export and a phase key `hold`, so the release stays on its last frame instead of falling back to idle.
  - **For Combat and the chapter designer:** the Ch20 enemies.json rows can now name `res://game/creatures/<id>/<id>_held_battle.tscn` as `model`.
  - **For battle VFX and presentation:** the turn to glimmer_lift and the rising motes at the release are yours. Nhoa's strands are short, so her column moment needs the VFX.
  - **Checks run:** Blender verify identical (the six plus spot checks here; all 53 by the agent); tools test_creatures and test_blender_builds; the manifest (366 valid); Godot creature 75/1 (the known portrait red, now 26 PNGs), vowbound 83/0, battle 720/0; validate_data, taskboard, lint, format.
- **The one open render request, re-posted to add the six held shots and their portraits** (the 0af5df49 line is SUPERSEDED):
SUPERSEDED RENDER-REQUEST @ db895430: battle_choreo_hit, battle_choreo_ko, battle_choreo_melee, battle_boss_intro_matron, creature_ilun, battle_vowbound_out, battle_choreo_vowbound_rise, battle_choreo_summon, npc_haluna_dock, npc_haluna_market, npc_haluna_chapel, npc_haluna_lane, npc_wake_feast, creature_kahre, creature_virel, creature_nhoa, creature_hesk, creature_ethren, creature_gallery_ray, creature_glass_skate, creature_ridge_lynx, creature_ilun_held, creature_kahre_held, creature_virel_held, creature_hesk_held, creature_nhoa_held, creature_ethren_held, portraits:avalanche_ram,portraits:conduit_crawler,portraits:cord_moth,portraits:fen_leech,portraits:gallery_ray,portraits:glass_skate,portraits:ilun,portraits:kahre,portraits:lamp_engine,portraits:ridge_lynx,portraits:rim_crawler,portraits:rime_urchin,portraits:root_crab,portraits:scree_crawler,portraits:tannin_archer,portraits:virel,portraits:wakefin,portraits:nhoa,portraits:hesk,portraits:ethren,portraits:ilun_held,portraits:kahre_held,portraits:virel_held,portraits:hesk_held,portraits:nhoa_held,portraits:ethren_held; tool: tools/portraits/render.sh --only avalanche_ram,conduit_crawler,cord_moth,fen_leech,gallery_ray,glass_skate,ilun,kahre,lamp_engine,ridge_lynx,rim_crawler,rime_urchin,root_crab,scree_crawler,tannin_archer,virel,wakefin,nhoa,hesk,ethren,ilun_held,kahre_held,virel_held,hesk_held,nhoa_held,ethren_held; why: everything owed since my last approved renders (fce2e82, 3b0e44b): hit_snap and clip timing, the Vowbound and their held forms, M3-CRE-100's villager stages, M3-CRE-645's polish, and the 26 portraits that turn test_creature_portraits green.
- **M3-CRE-648 merged (docs; review: Lead):** Act III design sheets in docs/kb/art/creatures/act3/.
  - **the_cage:** the Lit Age lattice of four lamp bays, with the founders standing in it. Wrist rings and a sill bone per quarter for the characters track's figures. The weak point is each quarter's keystone clasp above the founder's head, so the party strikes the lock, never the person. Each break opens the clasp and rings, and the founder's light lifts gold.
  - **Ch19:** wick_crawler (a lamplighter's pole that walks), chain_lamp (steady light, louvres open on the beat, so the bound-light rule holds), spire_moth (a pale glass-winged flue moth variant).
  - **Ch20:** held_shoal (24 fish of held light as skinned beads, never rising) and drowned_lantern (a jellyfish-like lamp globe whose light settles downward).
  - **For Combat / the chapter designer** (the full list is in each sheet):
    - the Cage as one combatant with phases at 75/50/25% (the board has three enemy slots);
    - a no-travel style for the Cage and the chain lamp;
    - the chain lamp's sweep cadence;
    - what turns the held shoal targetable;
    - who brightens the room when a drowned lantern falls.
  - **For Tech:** the Cage's last quarter needs a hide/show at the KO (or a fourth phase).
  - **Builds wait for the Lead's go on the Act III ids (M3-CRE-646/648).**

## REFOCUS: ADR 0041, Act I at final quality first (from 2026-10-28 ~01:15)
- **Act II and later paused:** M3-CRE-620/621/623/624/626/627/628/635/637/642–649 are set to `blocked` (`blocked-by: ADR 0041`). Their work stays merged; nothing is reverted.
- **The render-request queue is retired** (TRACK-RULES): every RENDER-REQUEST line above is SUPERSEDED. I self-render from here on.
- **New split (Lead):** creatures-b takes the Act I bosses and the Vowbound. This session keeps the regular Act I enemies, the field wildlife and the villager runtime.
- **The 20 Act I regulars** (encounters.json): ashwing, flue_moth, gull_harrier, lantern_eel, oil_slug, raid_hound, reef_crab, sail_leech, scuttler, shoal_skipper, slag_tortoise, squall_wing, stormgull, tide_crawler, tower_limpet, vein_sparker, wall_polyp, wallcrab, wickfry (the glassfry model), wreck_crab.
  - **Audit:** all have a real mesh, rig and full clip set (idle, ready, attack, cast, hit, hit_b, ko). 17 carry a spawn_wound weak point. The missing three (flue_moth, raid_hound, vein_sparker) are M3-CRE-650, building in a worktree.
  - **Spawn/death VFX hooks (M3-CRE-651):** `CreatureActor.vfx_anchor(&"wound" | &"core")` plus creatures.json `vfx_anchors` for all 20, with tests. **For battle VFX: M3-CRE-653** asks you to play KO and spawn effects at those anchors.
- **MERGE-READY @ e9e3e1cb: M3-CRE-651** (checks run: Godot creature 78/1, the known portrait red; battle 720/0; vfx_anchors 3/0; tools test_creatures; validate_data, lint, format).
- SELF-RENDERED @ e9e3e1cb: creature_ashwing, creature_gull_harrier, creature_lantern_eel, creature_oil_slug, creature_reef_crab, creature_sail_leech, creature_scuttler, creature_shoal_skipper, creature_slag_tortoise, creature_squall_wing, creature_stormgull, creature_tide_crawler, creature_tower_limpet, creature_wall_polyp — all 14 PASS against their baselines (RMSE ≤ 0.00003).
  - **Viewed:** the gull, eel, reef crab, scuttler, tide crawler, stormgull, limpet, wall polyp, ashwing and squall wing read finished.
  - **Unfinished:** shoal_skipper, slag_tortoise, sail_leech and oil_slug read primitive (M3-CRE-654, in a worktree).
  - **Portraits:** all 20 bestiary portraits viewed, all present. The raid hound reads crude (M3-CRE-655, after 650).
- SELF-RENDERED @ f5ebf9a5: creature_wallcrab, creature_glassfry, creature_wreck_crab — all 3 PASS (RMSE 0) and read finished. That covers all 17 untouched regulars; the other three get rendered after M3-CRE-650 and M3-CRE-654 land.
- **MERGE-READY @ (this push): M3-CRE-656, villager runtime in the Act I greybox zones.**
  - VillagerLayer adopts a GreyboxZone stage actor's villager `Model` (M2-FP-111) into a FieldNpc inside the actor, so it glances, turns to talk and idles out of step; cutscenes still find it.
  - Oruvel's Kell is the first (zones/ch01_oruvel.json).
  - **For slice-polish (M3-CRE-657):** GreyboxZone should `VillagerLayer.wire(self, location_id)` when a zone file exists, as it already adds the WildlifeLayer. One `if` after `_build_stage()`.
  - **For characters (M3-CHR-100 and the chapter NPC tasks):** about 150 Act I stage actors are still capsules (oruvel 10, brightwater_ferry 7, pemakar 14+, brine_shoals 16+, tamsule 8, corrow 22+, corrow_night 19+, …). The bodies are yours. As each gets a layout `model`, I add its villager row.
  - **Checks run:** Godot villager 27/0, ch01 14/0, oruvel 14/0, field_npc 10/0; tools test_npc; validate_data, lint, format.
- **MERGE-READY: M3-CRE-650** (merged): flue_moth, raid_hound and vein_sparker now each carry one small closed spawn_wound mark (ADR 0151). The vein sparker's starlight is confined to point sparks at its spine tips and four flank sparks (0.30% of a filled frame, within palette.json's 0.5%). Their vfx_anchors wounds are set (head, chest, tail1).
- SELF-RENDERED @ (this push): creature_flue_moth (drift 0.010), creature_raid_hound (0.005, pass), creature_vein_sparker (drift 0.031), plus the three portraits (re-baked and committed as assets).
  - Viewed: the drifts are exactly the marks (the moth's brow, the hound's breast, the sparker's tail root) and the sparker's coil, now bare copper. **Lead: these three baselines need your re-render on the next gate.**
  - Wildlife self-render: wildlife_stage, wildlife_zone_brine_flats, wildlife_zone_brine_wrecks and wildlife_zone_underway_crown all PASS. Capture still exits 1 on audio's shutdown "Trying to cast a freed object" at game/audio/life_audio.gd:124 (audio's, M3-CRE-633); the images are fine.
- **Lead's 01:54 assignment: my two inventory rows (M3-HER-1142) and the generic villagers.**
  - **`hound` (Brine Shoals):** our raid hound can now stand on a greybox stage (CreatureActor.play_clip takes HeroMotion's blend; tested). **act1-chapters: M3-CRE-658** is one layout line, `"model": "res://game/creatures/raid_hound/raid_hound_battle.tscn"` on `actors.hound`. The hound's polish (M3-CRE-655) lands on the same scene.
  - **`inquisitor` (Brine Shoals) is Moll, a person.** The audit's name list routes it to creatures, but it's characters' (M3-CRE-625, noted there). **integration-qa:** please route `inquisitor` to characters in placeholder_audit.py's creature_ids.
  - **Generic villagers: ADR 0152 + M3-CRE-659 (doing).** A crowd generator on the characters' villager modules (imported, unedited): about 20 crowd bodies at the LOD1 tier, per-person tints, and work clips, swapping about 51 capsules in 10 zones.
    - Paths claimed in ownership.md: assets_src/crowd/**, assets/crowd/**, game/data/world/npc/crowd.json.
    - **slice-polish:** M3-CRE-657 (GreyboxZone adds the VillagerLayer) is now what lets those rows show.
  - Checks run: Godot creature 79/1 (the known portrait red), battle 720/0, vfx_anchors 4/0; validate_data, taskboard, lint, format.
- **MERGE-READY: M3-CRE-655, the raid hound re-modelled.**
  - It's now a lean, deep-chested greyhound: real joints, paws, a wedge head with a moving jaw and folded ears. The Order's harness is leather with a lacquered plate, and the muzzle cage is red lacquer.
  - 7,424 triangles (the budget raised to the regulars' 8k ceiling). The rig, clips, contacts, vfx_anchors and the breast scar are kept, and grounding holds.
- SELF-RENDERED (by the agent; viewed here): creature_raid_hound and battle_boss_intro_inquisitor (the hound beside Moll's capsule) both read as a real hound; the portrait is re-baked and committed. **Lead: both baselines need your re-render.**
  - Minor issues left (in the handoff): the KO's ears lift slightly; a small gap between the breast strap and the neck ring at the howl's peak.
- **MERGE-READY: M3-CRE-654, four Act I regulars to final quality** (scree_crawler and fen_leech, the paused Act II variants, were rebuilt from the same builds).
  - **Shoal skipper:** a real mudskipper: wide head, opening jaw, lidded goggle eyes, fan fins, spined sail, wet mottled skin.
  - **Slag tortoise:** a dripping slag crust over scaled, clawed legs, and a beaked head.
  - **Sail leech:** a segmented body with suckers and the wound slits as seams; ribbed, frilled sails.
  - **Oil slug:** eye-tipped tentacles, a mantle, a ruffled foot and an oily sheen.
  - Bones, clips, contacts, weak points and anchors are kept; grounding holds.
  - **Checks run:** Blender verify identical ×6; tools test_creatures; Godot creature 79/1 (the known portrait red); validate_data.
- SELF-RENDERED (the agent rendered the four review shots, drift 0.04–0.10, all intended; I viewed before/after here) plus the four portraits, re-baked and committed. **Lead: creature_shoal_skipper, creature_slag_tortoise, creature_sail_leech and creature_oil_slug need your re-render** (and the Act II scree_crawler and fen_leech, if you gate them).
- **The 20 Act I regulars are now all final in my review:** every one has its mesh, rig, full clips, a weak point and vfx_anchors, and has been viewed at the review shot and in its portrait. What's left is the Lead's baseline re-render, and battle VFX using the anchors (M3-CRE-653).
- **big13 merged in @ 89e381ba** (integration 90ecee18).
  - Unions: ownership, blender_builds (the six Vowbound jobs kept), PROVENANCE, shots, baselines. The drowner and creature_portraits baselines are the gate's.
  - Checks run: Godot creature 79/1 (the known portrait red), vowbound 83/0, villager 27/0, vfx_anchors 4/0, field_npc 10/0; tools test_creatures, test_blender_builds, test_npc; the manifest (414 valid); validate_data, taskboard, lint, format.
- **Lead's 03:41 primitive list, queued as M3-CRE-660 (after the crowd generator):**
  - **Already done:** raid_hound (M3-CRE-655) and slag_tortoise (M3-CRE-654) were both re-modelled after the sheets you viewed. Please look at their new renders (creature_raid_hound, creature_slag_tortoise and their portraits) on your next gate.
  - **"pumice_crawler" doesn't exist in the repo.** Did you mean scree_crawler (Act II, the tortoise's variant, already rebuilt with it)?
  - **avalanche_ram is Act II, paused by ADR 0041.** Say if it's back in scope.
- **MERGE-READY: M3-CRE-659, Act I's background villagers (ADR 0152).**
  - **What:** a crowd generator on the characters' villager modules (imported, unedited). 22 bodies (5 children, 10 adults in three builds and both sexes, 4 elders, 2 Order robes) wear 56 people in 10 zones (game/data/world/npc/crowd.json).
  - **Variety:** per-person cloth and hair tints (palette swatches or mixes, never near skin); no body repeats in a zone; work clips for mend, sweep, carry, fold, haul, kneel and vigil.
  - **Tamsule's `board`** is a person, the Reefball board-caller. **Brine Shoals' `wrights`** stands for six kneeling wrights.
  - **Size:** assets/crowd is 43 MB (GLBs 15.6, maps 14.8, clip and material text 12.2), all under 5 MB per file. That's above ADR 0152's estimate; trimming the clip libraries is a follow-up.
  - **Checks run:** Blender verify identical (all 22 by the agent; 3 spot-checked here); tools test_npc (the variety rule), test_blender_builds, test_creatures; Godot crowd 5/0, villager 32/0, field_npc 10/0, life_audio 12/0, creature 79/1 (the known portrait red); the manifest (428 valid); validate_data, lint, format.
- SELF-RENDERED (the agent; viewed here):
  - crowd_lineup_a/b/c, crowd_market, crowd_work, crowd_mourners and the zone shots (pemakar, brine_shoals, tamsule, corrow, corrow_night, oruvel, bell_galleries). At walking distance, no two read as clones.
  - **One to watch:** two pale peach tops in lineup_a sit close to skin tone; the generator's skin clearance may need widening.
  - **Lead: the 14 new crowd_* shots need baselines from your gate.**
- **What still keeps them off the player's screen:** GreyboxZone adding the VillagerLayer (**slice-polish, M3-CRE-657**, one `if`). Until then only the review stages attach one.
- **For characters (M3-CRE-661):** four small asks of the villager pipeline. The first, Saltwright line-marks and the brine-brand for the wrights, is the one that matters.
- **MERGE-READY @ aceedf4a: M3-CRE-662, the crowd follow-up.**
  - **Cloth never near skin:** a perceptual metric (CIELAB with lightness and hue down-weighted, floor 18.5), calibrated on the renders. There's no silent fallback any more: a draw widens to other sets, then errors. The validator uses the same function.
    - 35 of 66 body defaults and 88 of 168 person tints changed; none is under the floor now.
  - **Smaller:** four shared clip libraries (adult, elder, child, child_small) replace 22 per-body copies (clips 12.0 → 2.8 MB; assets/crowd 43 → 34 MB). Worst bone error is 1 cm against the per-body clips; feet still plant.
  - **GOTCHA for every checkout (Lead, gates):** the post-import changed but Godot doesn't re-import unchanged GLBs. Run `rm -f .godot/imported/crowd_*.glb-*` and re-import, or the shared libraries don't apply.
  - **Checks run:** Blender verify identical ×22 (by the agent); tools test_npc and test_blender_builds; gen_crowd --check; Godot crowd 6/0, villager 33/0, field_npc 10/0, life_audio 12/0; validate_data, taskboard.
- SELF-RENDERED (the agent; viewed here): crowd_lineup_a/b/c, crowd_market, crowd_work, crowd_mourners, crowd_zone_brine_shoals and crowd_zone_bell_galleries. No cloth reads as skin; kneelers' knees are on the floor; children and elders stand at their own heights.
- **Waiting (everything open is blocked on another track or on the Lead):**
  - **M3-CRE-657 (slice-polish):** GreyboxZone adds the VillagerLayer. Without it the 56 crowd people and Kell's life don't appear in game. **This is the critical one.**
  - **M3-CRE-660 (Lead):** confirm "pumice_crawler" (scree_crawler?) and whether avalanche_ram (Act II) is in scope. The raid hound and slag tortoise are already rebuilt.
  - **M3-CRE-658 (act1-chapters):** the hound's model line in Brine Shoals.
  - **M3-CRE-661 (characters):** Saltwright line-marks and the brand for the crowd's wrights.
  - **M3-CRE-653 (battle VFX):** effects at the creature anchors.
  - **M3-CRE-634 (ui):** limit the portrait test to enemies.
  - **M3-CRE-633 (audio):** the shutdown cast.
- **BACKLOG EMPTY (for now):** every creatures item is merged and every open item waits on the tracks above. The handoff is docs/kb/handoffs/2026-10-28-art-creatures-9.md.

## big14 gate fixes (2026-10-28, the Lead's top priority)
Merged `origin/gpu/gate-big14-shots` and the integration branch, then fixed on the merged tree:
1. **test_villager_routines: no awaits, no crash at exit.** The tests build their layers directly. **test_crowd_villagers** had the same await (Brine Shoals) and was fixed the same way. The creature and Vowbound tests now free their actors at the end of each test: 0 nodes left (was 83).
2. **Osu and the vendor at the wake:** the chat pair is dropped (cinematics stages them apart: M3-CIN-1220).
3. **Blender:**
   - **avalanche_ram.glb** is deterministic. numpy's SIMD path put the head's midline at ±1e-17 on one host and 0 on another; the build snaps |x| < 1e-9 to 0. It is identical natively, under `NPY_DISABLE_CPU_FEATURES="X86_V4"` (the PC's AVX2 path, which reproduced the gate's 8d990e hash) and on baseline. Rebuilt GLB committed.
   - **kirru_roost.glb** is env-art's (M3-ENV-718): request **M3-CRE-663**, with the same diagnosis.
4. **cord_moth has its actor:** a foe whose enemies.json row names no `model` uses its same-id creatures.json scene. That also covers the nine Act II foes the gate listed (fen_leech, gallery_ray, glass_skate, ridge_lynx, rim_crawler, rime_urchin, root_crab, scree_crawler, tannin_archer). `test_every_foe_and_vowbound_has_a_body` passes.
5. **Portraits:** ilun, kahre, virel, nhoa, hesk and ethren, plus their six `_held` forms, are rendered, viewed and committed with PROVENANCE rows. test_creature_portraits passes 21/0.
6. **Also from the merged tree's QA capsule test:** Haluna's seven villagers showed as capsules, because the layer deferred its build when added in the zone's `_ready` and the test steps no frame.
   - VillagerLayer now builds at once.
   - The shop rows sit inside their bodies under a new row key `node_name: "Villager"`, so HalunaVillagers.populate skips them and nothing doubles.
- **Not ours, left as they are:**
  - `ossa_fen.tscn shows pell as a capsule`: a named Act II person (env-art and characters).
  - `test_battle_act1_ability_vfx` cord_moth `unravel` has no effect: battle VFX.
- **GOTCHA (local checkouts after a disk-full):** a truncated `.godot/imported` file loads as "corrupt" or "Failed loading" (it was 64 KiB-aligned here). Delete it and its `.md5` and re-import.
- **Checks run:**
  - Godot: creature 84/0 (0 left), vowbound 87/0 (1 left: test_battle_vowbound, battle UI's), villager 33/0, crowd 6/0, haluna 65/0, field_npc 10/0, portrait 21/0, qa_capsules 2/3 (pell only).
  - Blender verify for avalanche_ram: identical ×3 paths.
  - validate_data, lint and format.
- **Battle suite (merged tree): 790 run, 3 failed, all from the gate's own list, none ours:**
  - test_battle_act1_ability_vfx (eight foe skills with no Act I effect, M3-BPR-420 and M4-C11-03);
  - test_battle_party_stand_ins (Liss's timeline tint);
  - test_battle_result_motion.
  - Wildlife 14/0, npc 10/0.
- **MERGE-READY @ (this push): the big14 gate fixes above.**
- **BACKLOG EMPTY (after big14):**
  - The villager generator waits on M3-CRE-657 (slice-polish: GreyboxZone adds the VillagerLayer) and M3-CRE-661 (characters).
  - The primitive pass waits on M3-CRE-660 (the Lead: "pumice_crawler" and avalanche_ram scope).
  - The open character-role todos are creatures-b's (M3-HER-1134, M3-HER-1143: Act I bosses) or characters' named people (M3-C07-07, M3-CHR-5xx).

## The Lead's 10:34 orders (2026-10-28)
- **MERGE-READY @ (this push): M3-CRE-660, the primitive pass on raid_hound and slag_tortoise.** pumice_crawler and avalanche_ram are Act II and skipped, per the Lead.
  - **Tortoise:** the crust breaks into tilted slag slabs at dark, copper-lipped seams on a 44×112 lathe, with less gloss, 12 clinkers and overlapping leg scutes. The scree crawler is rebuilt from the same build.
  - **Hound:** the shoulder sits in the chest, and the leg tops blend into the body's shading and colour, so no flat plate shows. Fuller, folded rose ears.
  - Portraits re-baked.
  - Blender identical ×3 numpy paths for raid_hound, slag_tortoise and scree_crawler; Godot creature 84/0.
- **MERGE-READY @ (this push): the crowd in every Act I zone with background people.**
  - Crowd rows already covered every generic person in Oruvel, Brightwater Ferry, the Ch4 wake, Pemakar, Ashcrown, Tamsule (and the bell galleries), Brine Shoals and Corrow (day and night). The audit's remaining capsules there are named people or heroes (characters, act1-chapters).
  - **New finding:** cinematics' ZoneCast (M3-CIN-1217) dresses those zones' generic stage actors as Haluna's villagers. A crowd row now replaces that body (ADR 0152: Haluna's faces stand for no other town); a named row adopts its Cast. With both, the Ashcrown tender had two bodies.
  - `VillagerLayer.wire` reuses a zone's own layer.
  - **Still needed in game: M3-CRE-657** (slice-polish's GreyboxZone adds the layer). A trialled, ready patch is in `live/patches/m3-cre-657-greybox-villagers.patch`. Apply it with cinematics' test_zone_cast change (in the task).
  - **For characters and cinematics:** ZoneCast also dresses named people in other towns as Haluna's villagers. That is outside my rows.
- **SELF-RENDERED (walking distance), all ten viewed:** crowd_zone_oruvel, crowd_zone_brightwater_ferry (new), npc_wake_feast (re-aimed), crowd_zone_pemakar (re-aimed), crowd_zone_ashcrown (new), crowd_zone_tamsule, crowd_zone_bell_galleries, crowd_zone_brine_shoals, crowd_zone_corrow (re-aimed), crowd_zone_corrow_night.
  - Each shows its people as distinct crowd bodies with one body per actor.
  - The Corrow children face the sea as staged. **No baselines written:** the Lead's gate does that.
- **Checks:** villager 35/0, crowd 7/0, zone_cast 3/0, field_npc 10/0, haluna 65/0, creature 84/0; qa_capsules: Pell only (Act II, not ours).
- **MERGE-READY @ (this push): the big15 post_import fix.**
  - The crowd GLBs already ran their category script (`crowd_post_import.gd`, set in each .glb.import). The crowd category (`game/data/import/crowd.json`) exists, but test_post_import's `KINDS` list lacked `crowd`, so every crowd GLB read as "in no import category". `crowd` is added; no import needed regenerating.
  - The integration branch is merged in.
  - Checks: post_import 21/0, villager 35/0, crowd 7/0.

## FROM 2026-10-29 (new Lead session_01Bg3iP7cPGyjbX4CyniBahc; integration claude/new-session-mj8c3c)
Merged `origin/claude/new-session-mj8c3c` (pc-gpu.md conflict: kept ours, the newer PC text) and **claude/characters @ 3346484b** (the head big17 carries). The crowd generator avoids the Haluna/Act I villager faces in `assets_src/characters/villagers/params`, so its output can only match on a tree with characters' new villagers.

### big17 gate reds (mine): fixed
- **test_npc:** characters' new Act I villagers (M3-CHR-512: three wrights and others) changed the faces the crowd must avoid. `gen_crowd.py` re-run: only **crowd_girl_teen** changes (now clears wright_child_a, ≥0.28). Rebuilt in Blender (+ the child clip library it owns). Verify: `crowd_girl_teen` 21 identical.
- **test_post_import (tools):** `tools/tests/test_post_import.py` KINDS lacked `crowd` (the big15 fix only did the Godot test).
- **Confirmed on big17 itself:** cherry-picked onto `origin/lead/gate-big17` in a scratch worktree: test_npc + test_post_import 33/0.
- **Also:** dropped a stale `shrine_offering.glb` PROVENANCE row the characters merge re-added (big17 has none): validate_data 0/0.
- **villager_shopkeeper_front (NO BASE):** SELF-RENDERED and viewed: a full Haluna shopkeeper in T-pose on the review stage, clean, no placeholder (characters' M3-CHR-512 villager). **LEAD-ANSWERED: villager_shopkeeper_front approved at the gate (I wrote none).**
- Checks: tools test_npc 27/0, test_post_import 6/0; Godot crowd 7/0, villager 35/0, post_import 21/0, npc 10/0; validate_data, lint, format.

### M3-HER-1142: Corrow's storm figure (audit row, high): done, in review
- The capsule `figure` in `corrow.tscn` is the cyan silhouette in the storm wall (act1_ch08 W22). It is now `corrow_storm_figure` in `zones/ch08_corrow.json`: the Oruvel diver's crowd body (`crowd_man_lean_a`) drawn as one `#5fd6e0` silhouette.
  - New VillagerLayer row keys: `body` (a crowd body with no crowd person), `silhouette` (NpcSilhouette: an unshaded fresnel-rim shader that fades in from the feet, depth prepass, no shadow, no TIME, render priority 1 so the storm sea doesn't paint over it) and `tuning` (zeroes its glance and talk radii). Validator and docs (field_npc.md "Silhouette rows") updated.
  - It rides inside the `figure` stage actor, so the layout's flags and the cutscene's `@mark figure figure_gone walk` drive it.
- **New shots:** `npc_corrow_storm_figure` (from the wall, about 31 m) and `npc_corrow_storm_figure_near`.
- **Still needed in game:** M3-CRE-657 (GreyboxZone adds the VillagerLayer; patch in `live/patches/`). Until then Corrow's crowd and the figure appear only where a layer is wired (the shot stages, tests).

### GPU QA row 40: the Oil Slug's read at battle distance: done
- Flank-on in battle (`stand_in.yaw_deg` 60) at 1.3× (its battle scene's Model). A lighter back, a stronger oil sheen, a body rim sheen, brighter cerata tips.
- `LampGlow`: a small shadowless `oil_lamp` omni light over the cerata (the design's "the only warm light in the underway"), which lights its back and a pool of floor. CreatureActor now fades a creature's lights with its KO (test).
- New shot `creature_oil_slug_battle` (its real ch01_oil_slug encounter). Portrait re-baked (margin 1.2: its head had always been cropped). Blender verify identical.

### Primitive pass
- Rendered the current builds of the shoal skipper, raid hound and hullgnaw: they read finished (the old baselines predate their rebuilds).
- **The tide crawler read primitive** (a plain ellipsoid on smooth cone legs), so it's rebuilt, 4.8k tris, rig and clips unchanged:
  - a crab's carapace: a low dome widest forward, a rim lip, grooved plates split by glowing seams, a dorsal ridge, brow teeth and mandible hooks;
  - jointed legs with coxa, knee and ankle knobs, dull joint membranes, a glowing seam along each femur, femur spines;
  - serrated scythe forelegs.
  - The paused Act II rim crawler imports this build, so it was rebuilt (verify identical).

### Checks (this batch)
- tools: test_npc, test_post_import, test_creatures OK; validate_data 0/0; taskboard; gdlint and gdformat on game/tests clean.
- Godot: creature 85/0, portrait 21/0, crowd 9/0, villager 37/0, npc 10/0, post_import 21/0.
- Blender verify identical: crowd_girl_teen, creature_oil_slug, creature_tide_crawler, creature_rim_crawler.
- Skipped: coverage (nothing in game/battle or game/progression changed), the full manifest.

### SELF-RENDERED (all viewed; no baselines written)
- villager_shopkeeper_front (NO BASE): a clean villager.
- crowd_zone_pemakar, crowd_zone_brine_shoals: crowd bodies, no capsules.
- crowd_lineup_a/b/c/back: every body present. A first render came out empty because I had edited field_npc.gd mid-capture before the class cache was re-imported; re-rendered after the import.
- npc_corrow_storm_figure(_near) (new): one cyan man's shape in the storm sea.
- creature_oil_slug, creature_oil_slug_battle (new): it reads; a warm glow and crest at battle distance.
- creature_tide_crawler: drift expected (rebuilt).
- creature_shoal_skipper, creature_raid_hound, creature_hullgnaw: current builds; the old baselines are stale.
- **LEAD-ANSWERED (ADR 0204 message: approved with big17/18): at the gate, approve baselines for villager_shopkeeper_front, creature_oil_slug_battle, npc_corrow_storm_figure, npc_corrow_storm_figure_near (new), and re-approve creature_oil_slug, creature_tide_crawler, creature_rim_crawler, plus the stale creature_shoal_skipper, creature_raid_hound, creature_hullgnaw and creature_slag_tortoise. Crowd shots for crowd_girl_teen's zones (pemakar, brine_shoals, lineups) may drift slightly.**

### PC-QUEUE
- GPU QA row 40: recheck the Oil Slug in ch01_oil_slug on the RX 9070 XT (LampGlow on real GPU; the arena's lit floor patches are env-art-b's row 15).
- The Corrow storm figure on real GPU (bloom on the rim; rain over it).

### Primitive pass (continued)
- Rendered the other 15 Act I regulars' current builds (ashwing, bottle hermit, flue moth, gull harrier, lantern eel, reef crab, sail leech, scuttler, squall wing, stormgull, tower limpet, vein sparker, wall polyp, wallcrab, wreck crab) and viewed them.
- **The tower limpet read primitive** (a smooth striped cone), so it's rebuilt, 9.1k tris, rig and clips unchanged:
  - sharp primary and secondary ribs running out into a scalloped margin, growth ledges, a worn pitted apex;
  - the shutter as louvred slats in a frame with two rusted iron straps, the shell growing over its ends;
  - barnacle clusters and a fringe of mantle tentacles round the foot.
  - Portrait re-baked; verify identical. The doc's budget is raised to ≤10k (a lone foe).
- **Read finished, left as they are:** the wall polyp's stone (worn, chipped, mortared laterite with the carved Watcher; its blockiness is masonry) and the reef crab family (7.9k of an 8k budget; shaped, banded legs, no blockiness at battle distance). The rest read finished.
- Battle suite on this tree: 790 run, 3 failed, all on the known list (test_battle_act1_ability_vfx's Act II foe effects, test_battle_party_stand_ins' Liss tint, test_battle_result_motion), none from these changes.
- **Added to the (now answered) baseline list:** creature_tower_limpet (rebuilt).

MERGE-READY @ (this push): the big17 gate reds (test_npc, test_post_import), M3-HER-1142 (the Corrow storm figure), GPU QA row 40 (the Oil Slug), and the primitive pass on the tide crawler and the tower limpet. Checks run: validate_data 0/0, taskboard, gdlint and gdformat (game, tests), tools test_npc, test_post_import and test_creatures; Godot creature 85/0, portrait 21/0, crowd 9/0, villager 37/0, npc 10/0, post_import 21/0, battle 790/3 (known); Blender verify identical for every changed job (crowd_girl_teen, oil_slug, tide_crawler, rim_crawler, tower_limpet). Skipped: coverage (no game/battle or game/progression change) and the full manifest.

BACKLOG EMPTY: the Lead's four items are done.
- No todo or request tasks for creatures on the board.
- Every Act I regular reads final in fresh renders.
- Open items are others': M3-CRE-657 (slice-polish adds the VillagerLayer to GreyboxZone; without it Corrow's crowd and the storm figure appear only in the stages), the baselines (the Lead, at the gate) and the PC-QUEUE (real GPU).

### big17 red from the Lead (20:46): test_zone_cast::test_a_cast_actor_shows_its_model_and_idles_out_of_step: fixed
- Reproduced on `lead/gate-big17` in a scratch worktree; it passes on my head, which doesn't have M3-CRE-657.
- **Two causes, both from M3-CRE-657** (GreyboxZone wires the VillagerLayer after ZoneCast):
  1. The test read ZoneCast's `Cast` model, but Tamsule's crowd rows replace it with the crowd person. The test now reads the body the actor wears through `HeroMotion.player_of(actor)`, as the cutscene sequencer does, and accepts a resting clip (idle or work). `tests/unit/test_zone_cast.gd` is act1-chapters' file: edited on the Lead's routing.
  2. **A real bug of mine:** FieldNpc phased only the idle loop per villager, so the crowd fisher and boatman both started `haul` at 0.0 and hauled in step. Work and storm loops now start at a per-villager phase plus the clock (`FieldNpc.loop_phase`). New test in test_crowd_villagers.
- Checks: on big17 with these files, zone_cast 3/0, crowd 10/0, villager 38/0; on my head, crowd 10/0, villager 38/0, npc 10/0, zone_cast 3/0; lint and format clean.
- **Shots:** crowd zone shots where people work (crowd_work, crowd_market and the crowd_zone_* shots) will drift, because work clips now start at each person's own phase. Expected; re-approve at the gate.

MERGE-READY @ (this push): the test_zone_cast fix (plus everything in the previous MERGE-READY).
BACKLOG EMPTY (again): no other items.

## The Lead's Act I final-quality audit (from 2026-10-29 23:10): regular foes, wildlife, villagers
**Tools (new, tools/creatures/):**
- `clip_audit.gd`: headless, every clip of every Act I regular foe and crowd body at 60 fps. It reports skinned contact-vertex slip, one-frame pops, loop seams, floor penetration, and any missing hit/KO/idle/talk/walk.
- `foot_slip.py`: numpy, a build's own clips.
- `clip_sheet.tscn`: a close-up plus idle/attack/hit/KO poses on one fixed camera over a checker floor.
- `wildlife_audit.gd`, `wildlife_snap.gd` and `wildlife_apply.py`: placements checked and re-seated against the zone's visible meshes.

**Findings and fixes:**
- **Missing reactions:** none. All 44 actors have hit and KO (foes) or idle, talk and walk (villagers).
- **Foot sliding: FIXED.** Planted feet slid up to 37 cm on legged foes' hit, attack and idle (`grounded()` kept feet on the floor but let them slide). New `grounding.pinned()`: a damped two-bone solve holds a planted foot where it touched down, floor-safe and byte-reproducible. Now ≤5 cm on every pinned clip (was 8–37):
  - tide crawler (hit 22→0.2);
  - the crab family: reef, wall, wreck and root (attack 14→0.5);
  - raid hound (attack 37→2.7, its lunge now steps its forepaws);
  - vein sparker (hit 20→5);
  - bottle hermit (hit 14→3);
  - shoal skipper's fins (its tail's sweep is a mudskipper's, kept).
- **KOs that didn't read: FIXED.** The vein sparker's belly-flop looked like its idle (it now rolls onto its side), and the tide crawler's sink read as a crouch (now a dead spider's curl).
- **Pops:** the crabs' crusher smash (17 cm a frame) is a deliberate 0.15 s strike; all others are within 8% of body size.
- **Floor penetration:** fliers and burrowers read "under" only off their battle hover. The crowd's kneel and mend dip is skirt cloth under the floor, not visible (crowd_mourners and crowd_work viewed).
- **Faceting and texture:** creatures carry no textures (vertex colour plus procedural detail); crowd heads are 512², bodies 256² (walking-distance LOD1). Faces read at close-up.
- **Wildlife placement: FIXED in 10 of 11 zones.** Placements were still on greybox layouts:
  - perches inside roofs or on air (Oruvel and Tamsule under awnings and roofs; Corrow 38 m off its relaid wall; Brightwater's rails gone);
  - crabs on nothing (Pemakar's moved quay; the wake);
  - all re-seated on the kits, Corrow's gulls on the Watchers' heads (none on the Breach's stretch).
  - Crabs can follow uneven ground (`"ground": {"physics": true}`).
  - The causeway's file is generated by `tools/causeway`, so its crab ground is request **M3-CRE-664** (environment).
- **Ambient life:** fish added where the kits brought deep water (Oruvel's open sea, Tamsule's river, Pemakar's harbour, Corrow's sea). Left without, by reason:
  - Brightwater (its sea is 0.4 m deep) and Brine Shoals (dry flats);
  - Ashcrown (a volcanic forge under ash-fall);
  - the bell galleries, the shell shrine and the prologue (interiors or a cutscene);
  - Corrow by night (the strand of the drowned: animals among the shrouds would undercut it, pillar 1; the motes are its life).
- In progress: battle-distance renders of all 16 Act I encounters with a regular (arena silhouette and value).

### The Act I audit: finished
- **Battle-distance renders of all 16 Act I encounters with a regular, viewed.** Fixed in my lane:
  - **The ashwing** read as two small pale slivers: 1.35× in battle, hover 1.86 so its KO still lands. test_creatures now reads a battle scene's Model scale.
  - **The sail leech** was seen edge-on as glowing dashes on the Ch4 night deck: it hangs lower (hover 1.26, its KO's fall matched, `KO_DROP`), at 1.3×, with brighter slits and a salt-pale canvas edge. The paused fen leech pins its own fall.
  - **The Oil Slug, the tower limpet:** re-rendered, they read.
  - **Request M3-CRE-665 (combat):** in two-foe openings the back foe stands hidden behind the front one (the vein sparker behind the slag tortoise, the shoal skipper behind the wreck crab).
- **Villagers and wildlife moving: `tools/creatures/life_audit.tscn`** loads every Act I zone with villagers or wildlife. **All 14 zones: no frozen villager, wildlife moving everywhere** (culling off; a 4-second run).
- **Final clip audit:** 44 actors, none missing a reaction. The legged foes' worst residual slides are the raid hound's attack 8 cm (was 37), the tide crawler's hit 6 cm (was 22) and the vein sparker's hit_b 10 cm (was 27).
- **Checks:**
  - Godot: creature 85/0, wildlife 15/0, crowd 10/0, villager 38/0, npc 10/0, zone_cast 3/0, portrait 21/0, battle 790/3 (the known three).
  - tools test_creatures, test_wildlife, test_npc, test_post_import OK; validate_data 0/0; gdlint and gdformat clean; taskboard ok.
  - Blender verify identical: 49 creature jobs after `pinned`, then sail_leech, fen_leech, ashwing.
- Integration merged (c789b9a9): test_zone_cast kept mine (it accepts a work clip as the resting clip; integration's version requires `idle`, which Tamsule's crowd fisher on `haul` fails); shots.json rebuilt by hand (merge_union couldn't parse the base); the three stale wake-dressing PROVENANCE rows dropped again.
- **SELF-RENDERED (viewed, no baselines written):** creature_tide_crawler, creature_tower_limpet, creature_oil_slug(_battle), npc_corrow_storm_figure(_near), crowd_mourners, crowd_work, crowd_lineup_*. The 16 encounter renders were scratch shots in a worktree, not committed.
- **LEAD-ANSWERED (approved with big17/18; many at the partial gate d987cc6b): baselines at the gate.** Add creature_tower_limpet, creature_sail_leech, creature_ashwing, creature_reef_crab, creature_wallcrab, creature_wreck_crab, creature_raid_hound, creature_vein_sparker, creature_bottle_hermit, creature_shoal_skipper and creature_rim_crawler (all rebuilt or rescaled) to the earlier list.

MERGE-READY @ (this push): the Act I final-quality audit (planted feet, KOs, the ashwing, the sail leech, the wildlife re-seated, fish, crab ground, M3-CRE-664/665, the audit tools).

### Act II preparation, docs only (ADR 0203; the Lead, 2026-10-30 01:08)
- **`docs/kb/plan/act2/creatures/`, all `draft: pre-gate`.** README plus 11 regular foes and 4 wildlife proposals: silhouette, materials, rig, clips, the battle-distance read, reuse of existing generators, and the state against the bar (measured with clip_audit and clip_sheet).
- **All 11 regulars exist and are built.** Meeting the bar: tannin archer, root crab, rime urchin (but its KO), cord moth, scree crawler, glass skate. Close: conduit crawler. Below it:
  - ridge lynx (paws slide 18–29 cm; plain legs);
  - fen leech and gallery ray (edge-on or pale-on-pale reads);
  - rim crawler (chalk on white).
- **None of the ten enemy rows has a `model` key.**
- **Wildlife proposals:** fen kingfisher (never a heron: the Kirru), fen fireflies (never glimmer), woolback (the ram's build at 0.3 scale), rim rays (fish-sized, always moving, unlike the glass skate).
- **LEAD-ANSWERED (ADR 0204 §1: dropped from M4-A2P-056; Ch12 regulars: frost to snow, filed as M4-CRE-670): Ansedra has "no seabirds" (bible §5.8, ansedra.md). M4-A2P-056's "still-city birds (Ch13)" contradicts canon. Drop it from the task (I proposed no Ansedra wildlife, by design).**
- PC rows (the Oil Slug, the storm figure) come first when the PC reports on gpu/act1-qa-3.

BACKLOG EMPTY: the Act I audit is clean in my lane. The Act II sheets are written (docs only until `act1-complete`). The rest waits on others: M3-CRE-664 (environment), M3-CRE-665 (combat), the PC's QA pass, the Lead's baselines.

- 10-30 01:30, the Lead (ADR 0204): M4-A2P-056 edited (no Ansedra wildlife). **M4-CRE-670** filed (blocked by ADR 0203): the ridge lynx and scree crawler swap frost for snow and grit. The plan sheets are updated. BACKLOG EMPTY stands.

### The PC's pass 3 (big18), the Lead's 01:50 relay
- **GPU QA row 40, the Oil Slug in battle: CLOSED** (readable on the RX 9070 XT, per the PC's pass 3).
- **The Corrow storm figure logged 4× `Parameter "material" is null` on free: FIXED.**
  - NpcSilhouette's static per-colour material cache outlived the figure. Now each surface gets its own material, owned by its mesh alone, and FieldNpc clears the overrides in `_exit_tree`.
  - New test `test_a_freed_silhouette_leaves_no_material_behind`: after the figure is freed, no silhouette material is alive. It gathers its weak references in a helper, because GDScript keeps an expression's last value in a stack slot until the function returns.
  - It doesn't reproduce on lavapipe, so the PC's next pass confirms it on hardware (PC-QUEUE).
- **npc_corrow_storm_figure_near, "a smooth featureless glowing mannequin": FIXED.**
  - Under the glow, each surface keeps its own albedo brightness (cloth folds, seams, the belt), its occlusion and its normal map (the rim breaks along folds), plus brine tide lines and drip streaks (deterministic, no TIME).
  - SELF-RENDERED and viewed: npc_corrow_storm_figure_near (folds, hem, belt, seams, tide lines, drips); npc_corrow_storm_figure (still one clean cyan figure from the wall).
- Checks: crowd 11/0 (×2), villager 39/0, npc 10/0; lint and format clean.
- MERGE-READY @ (this push).
- **PC-QUEUE:** confirm no "material is null" after the Corrow shots on hardware; the storm figure's detail with bloom.

### ADR 0205: Act II regulars (the Lead's directive, 2026-10-30)
- **M4-CRE-670, the frost-to-snow swap: in review** @ 87edc76c. The ridge lynx's back holds settled snow and its paws carry grit; the scree crawler is patinated snow-grey and gritty. The lynx's paws stay planted (grounding.pinned gains an opt-in hip roll plus a rest pull; the three-turn path is byte-identical, verified).
- **Ch10, the fen leech** @ 35816168: it hangs at 0.85 m (stand-in hover and KO fall matched), so its back faces the battle camera instead of its edge.
- **Ch11, the gallery ray** @ c4360dfb: the back is dusky (cumulus_shadow toward lacquer_black, dark rosettes, salt-glass freckles); the margin's sea_glow is doubled; the wet clearcoat drops to 0.25 (its sheen washed the back white at the grazing battle angle); the hover drops from 1.4 to 0.95 m, and the cast pool and the KO follow it. Portrait re-baked. SELF-RENDERED and viewed: audit ch11_vey_rays (slate discs with a teal rim on pale sand) and creature_gallery_ray. **The creature_gallery_ray baseline needs the Lead's re-approval** (the colour and the hover changed).
- **Ch11, the rime urchin's KO** @ 8152d4de: the spines fall open 50 degrees, with their tips lifting so the low ones lie on the floor, not in it, and the test slumps and tips. Viewed on the clip sheet: the idle ball turns into a flat, parted star. The ice cracking is left to the KO effect (VFX).
- Checks: validate_data 0/0; tools test_creatures OK; Godot creature 87/0 (test_creature_actor's ray constants now 0.95 m hover and 0.8 m pool drop); gdlint and gdformat clean; Blender verify identical (gallery_ray, rime_urchin, plus ridge_lynx, scree_crawler and fen_leech for the earlier commits). Skipped: coverage (no battle or progression code) and the full manifest.
- **MERGE-READY @ 8152d4de** (it includes 87edc76c, 35816168 and c4360dfb).
- Next: the conduit crawler's legs (Ch11), the cord moth's battle scale (Ch12), the rim crawler's value (Ch16), the ridge lynx's leg shaping, then the Act II wildlife builds.
- **Ch11, the conduit crawler's legs** @ 563eda19: knee knuckles with brass caps, thigh collars and shin piston sleeves; the leg tubes drop to 4 rings, so the total is 4,608 triangles (budget 5k). Viewed on the clip sheet. It has no enemy row (a boss add), so no portrait.
- **Ch12, the cord moth** @ 506425f2: battle Model at 1.35× (the ashwing's fix), stand-in hover 1.35 m, the build's KO falling 1.0 m in model space. SELF-RENDERED audit ch12_pass_moths (broad wings, not slivers). test_creature_actor's MOTH_HOVER_M is now 1.35. The portrait re-bake came out pixel-identical, so it's unchanged.
- **Ch16, the rim crawler's value** @ 7bb55186: wet storm_slate flanks and seams, overcast_slate weathering on the chalk, wounds at energy 1.7. SELF-RENDERED audit ch16_rim_crawlers on pale sand (it reads). Portrait re-baked.
- **Ch12, the ridge lynx's legs** @ 7fbc0202: flatter side to side, shaped along their length (muscle, forearm or gaskin, slim wrist or hock, pastern), tops buried in the torso, toes as creased knuckles; 7,544 triangles (budget 8k). Viewed before and after on the clip sheet. Portrait re-baked.
- **M4-A2P-056, the fen fireflies (Ch10)** @ 2ea2d324:
  - A firefly mesh and slot in insect.glb. Its lantern glows warm yellow-green, never glimmer.
  - The wildlife shader gains mode 6 (the flutter with the blink in the mode parameter). The lit lantern swells toward a 0.006 rad view angle, so it reads as a point without bloom.
  - WildlifeSwarm gains the `firefly` type; the layer gets a seventh MultiMesh (the draw_calls budget goes 6 → 7).
  - Placement: ch10_ossa_fen.json, four swarms of six on the greybox.
  - New shots `wildlife_zone_ossa_fen_walk0` and `wildlife_zone_ossa_fen_pocket` (SELF-RENDERED, viewed). **Baselines needed from the Lead.**
  - zone_wildlife.gd now keeps a zone's own WildlifeLayer instead of adding a second.
  - Checks: validate_data, tools test_wildlife, Godot wildlife 17/0 and ch10 3/0, lint and format, Blender verify identical.
- Baselines to approve, all self-rendered: creature_gallery_ray, and the new wildlife_zone_ossa_fen_walk0 and _pocket. Other shots whose assets changed (I viewed the audit renders, not these shots): portraits for gallery_ray, rim_crawler and ridge_lynx; any shot with the rime urchin, conduit crawler or cord moth.
- LEAD-ASK: M4-A2P-056 (role: character) is still `blocked` by ADR 0203. Please record my claim (`doing`, claude/creatures) on the integration branch per ADR 0205.
- **MERGE-READY @ 2ea2d324** (includes everything above).
- Next: the fen kingfisher (Ch10), the woolback (Ch12), the rim rays (Ch16).
- **M4-A2P-056, the Act II wildlife: all four built and placed, task in review (reviewer: environment)**:
  - fen fireflies @ 2ea2d324;
  - fen kingfishers @ 0ebe065a (gull recipe, their own kind, rows and two MultiMeshes);
  - woolback herds @ 97291f9b (the ram's build without seep or ice, drawn at 0.3; the new skinned WildlifeHerd; idle, look and walk clips with the walk's hooves solved per frame);
  - rim rays @ fe0da8c2 (a ray kind of the fish shoal drawn with the flap mode).
  - Budgets and draw_calls: draw_calls 10, kingfishers 6, woolbacks 6, rays 16.
  - Validator, tools and Godot tests: wildlife 22/0, ch10, ch12, ch16. Blender verify identical for wildlife_insect, wildlife_kingfisher, creature_woolback and wildlife_rim_ray.
  - New shots, SELF-RENDERED and viewed, **baselines needed**: wildlife_zone_ossa_fen_walk0, wildlife_zone_ossa_fen_pocket, wildlife_zone_ossa_fen_rail0, wildlife_zone_keth_pass_foot, wildlife_zone_keth_pass_saddle, wildlife_zone_pale_rim_wade.
  - All four are placed on the greybox layouts. Re-seat them when the dressed kits arrive; the woolbacks go to the Keth troughs.
  - LEAD-ASK: the task file now says `review`, owner claude/creatures. Please carry the claim and the status to the integration branch.
- **MERGE-READY @ fe0da8c2** (includes everything since 2ea2d324).
- **Act II regulars: enemies.json `model` keys** @ 52ad6adb, for the ten built Act II foes. They had battle scenes but no `model`, so CreatureModels left them as capsules in battle. The additive field is ours (ownership.md). Checks: creature 87/0, portrait 21/0, battle_ko_once, part_cues, vfx_anchors; validate_data.
- LEAD-ASK: the slag tortoise (and the scree crawler, the same mesh) is 17,502 triangles since M3-CRE-660's primitive pass on your list (the crust lathe went from 24×64 to 44×112), but its sheet's budget says ≤ 8k. Either approve about 18k for this pair (a few on screen at once), or I cut the crust back to about 32×80 (about 10k) and re-render. I've noted it on both sheets.
- **Act II arena checks** (temporary previews of the built arenas with the regulars; viewed, not committed):
  - ossa_fen_roots: root crab, tannin archer, fen leech.
  - lowlight_engine_hall: gallery rays, rime urchin.
  - keth_seep_terrace: ridge lynx, cord moth, scree crawler.
  - drowned_choir_ring: glass skate, rim crawler.
  - Two fixes came out of them:
    - **cord moth** @ 3cbc4a17: it read as a pale sliver against Keth's white walls. It now has dusky wing margins and a hover of 1.12 m (model 0.83); test_creature_actor's MOTH_HOVER_M is 1.12.
    - **fen leech** @ cd21ece0: it read edge-on, like a branch, from the fen's low camera. It now has a raised back and edges draped 0.1 m like a ray's.
  - The rest read as they are (sheet notes).
  - Palette: M4-CRE-670's snow #E8E6DF is now `gauze_white` (lynx, scree crawler @ a0430bc7), and the sail leech's canvas #B9B1A0 is now a sand_cloth/coral_stone_weathered mix @ 9224953c. Portraits re-baked; the changes are 2 levels.
- **M4-A2P-058, the regulars' part:** specified in docs/kb/art/creatures/act2/skill_vfx.md, eight entries in the Act I generator's vocabulary, for M4-A2P-060 (combat) to generate into effects.json (rendering's file, not edited here).
- **MERGE-READY @ cd21ece0** (includes everything above).
