# Live log: creatures environment

Feature track for the battle creatures (cloud session_01CYks9e592YBEfygyTawcJD), branch `claude/creatures`, started from `origin/claude/undertow-lead-handoff-423ixt` aeb0875. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE.

## Now
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
