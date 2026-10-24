# Live log: creatures environment

Feature track for the battle creatures (cloud session_01CYks9e592YBEfygyTawcJD), branch `claude/creatures`, started from `origin/claude/undertow-lead-handoff-423ixt` aeb0875. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE.

## Now
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
- **Hook:** the UI track's M2-UI-07 (on `claude/ui`, 08c872c1) already makes `FighterStandIn` instance a spec's `"scene"`. The creatures build on that hook rather than a parallel one: the enemies.json `model` field becomes the stand-in spec's `scene`.
- **Materials:** one creature shader (`game/shaders/creature/creature.gdshader`) reading vertex data (albedo, wetness, cavity, wound mask), not the texture-based character families. Why: pipeline.md §2.
- **Import:** a new `creatures` category. Clip loop modes are set at runtime from `game/data/creatures/creatures.json`, so the shared `AssetImportRules` (which the characters track is also changing) is not touched.
- **Task ids:** M2-CRE-* (free on every branch at the claim).

## Exact next step
Two items remain in this queue: (1) when m2-slice's Ch4/Ch5 rows land, check their phase ids against creatures.json
(rename the Matron's `crust_breaks` if needed); (2) polish passes from the review notes (the Matron's crack lines and
the mask's size; the squall wing's see-through tears; the wreck crab's crust). Daily: merge the integration branch.

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
