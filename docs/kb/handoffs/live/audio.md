# Live log: audio (branch `claude/audio`)

Environment: cloud session `session_01FtDSYm5dJHkdC3RqXsDjif`, branch `claude/audio` (from the integration branch
`claude/undertow-lead-handoff-423ixt` at 1023a25). Role: Audio. The Lead reads this file; newest state first.

## MERGE-READY @ 7085dff5
Items: M3-AUD-08 Hullgnaw + Spar-Wraith, M3-AUD-09 Cinder Matron + Undertow's Reach (stems), M3-AUD-10 Oruvel + the living
funeral, M3-AUD-11 Brightwater ferry + Brine Shoals, M3-AUD-12 Tamsule + the Iskarra vigil, M2-AUD-13 causeway beds (all
`review`); fixes: loop imports `beat_count=0` (intro cues wrapped early in Godot), zone/battle music loads on a worker
thread, budget 48 MiB. Checks run: integration merged (up to date); full Godot suite 1529 run, 0 failed; validate_data 0;
taskboard --check OK; tools/tests audio (data + loudness, every file on target) OK; per-cue `render_all --determinism`
identical (by each worker). Skipped (Lead runs at merge): screenshots, Blender (no Blender source), coverage (no
battle/progression code).

## MERGE-READY @ c99e6f2b
`tools/ci_local.sh` exit 0 (HYMN_SKIP_BLENDER=1: no Blender source touched): 1499 Godot tests, 0 failed; 75/75 shots
(rmse 0); coverage battle 99.95 % / progression 96.52 % (within baseline); boot smoke clean. Integration branch merged
at f95b27cb. Items: M2-AUD-01..06 and M2-AUD-10/11, M3-AUD-01..07 (all `status: review`). Since c99e6f2b only docs.

## State (2026-10-24, later)
- **Merged into claude/audio since the last MERGE-READY:** M3-AUD-08 Hullgnaw + Spar-Wraith, M3-AUD-09 Cinder Matron +
  Undertow's Reach (stems), M2-AUD-13 causeway beds, M3-AUD-10 Oruvel + the living funeral (all `review`), and the
  integration branch at f8b0db07.
- **Fix:** every loop now imports with `beat_count=0`. Godot 4.6 loops an Ogg after `beat_count` beats counted from
  the file start, so cues with an intro (both battle themes, the sea bosses) wrapped early by their intro and skipped
  the end of their loop. The audio budget is 48 MiB (mix.md "Budget"; ~35 MiB used once these land: a repo-size
  question, Git LFS).
- **In progress:** M3-AUD-11 ferry + shoals routes and M3-AUD-12 Tamsule + the Iskarra vigil (worktree agents).
  Done and merged; queue empty.
- **Filed for m2-slice:** M2-AUD-12 (causeway zone rows, the B05 crossfade, the B12 coda).

## MERGE-READY @ e24a98cd
- **Items:** M3-AUD-13 choreography SFX, M3-AUD-14 creature voices, M3-AUD-15 menu UI SFX, M3-AUD-16 Act I zone beds,
  M3-AUD-17 Reefball hooks, M3-AUD-18 battle stings. All are `review`.
- **Integration branch:** merged at 37fd9571.
- **Checks run:**
  - The full Godot suite gave 1564 run, 0 failed on a quiet machine.
  - Earlier niced full runs, made while renders were running, failed only `test_scene_router_swap` on the boot frame.
    That test passes on its own, passes when run with every test that precedes it, and depends on load. The
    integration branch itself gave 1480/0.
  - validate_data showed 0 errors; taskboard --check, gdlint and gdformat were clean; test_audio_data passed (39 OK);
    the loudness test passed; and every new set re-rendered byte-identical with `--determinism`.
- **Skipped (the Lead runs these at merge):** screenshots and Blender. Coverage was skipped too, because game/battle/
  and game/progression/ weren't touched.

## State (2026-10-24, newest queue)
- **Done and merged into claude/audio (all `review`, reviewer qa):**
  - M3-AUD-13 battle choreography SFX (55 files). `ChoreoAudio` hooks BattleChoreo by name and is `pending` until
    claude/battle-presentation merges.
  - M3-AUD-14 creature voices and movement (194 files, 27 creatures). Hooked in BattleAudio; models by
    `CreatureActor` name.
  - M3-AUD-15 menu UI SFX (12 files). The title screen is live; Lattice, Equip, the map and tips are `pending`
    until claude/ui or claude/menus merges.
  - M3-AUD-16 Act I zone beds (6 beds).
  - M3-AUD-17 Reefball crowd and sphere hooks, `pending` until gpu/m3-rnd-01-reefball merges. The match, ball and
    goal names are guesses until the minigame exists.
  - M3-AUD-18 stings on battle-presentation's `battle_stinger`, `battle_bark` and `boss_intro` EventBus events. They
    go live when that branch merges.
- **To check at those merges:**
  - Drop the `pending` flags; validate_data then checks the real class and signal names.
  - claude/ui's ShopMenu and InnMenu hooks name signals those classes don't have, and need a rewrite.
  - Reefball swimmers must join the `reefball_swimmer` group.
  - BattleStage's creature actors must be under the BattleController.
  - The task Notes have the full lists.

## Exact next step
Queue empty. Waiting on: the human's listening verdict (listening_notes.md M2 and M3 sections; revise when it comes);
the merges of claude/battle-presentation, claude/creatures, claude/ui and claude/menus, gpu/m3-rnd-01-reefball and
claude/m2-slice, after which the pending hooks are switched on and tested against the real classes; and
M2-AUD-07/08/09/12 and M3-ARC-01 (requests to other roles).

## Un-pushed state
None.
