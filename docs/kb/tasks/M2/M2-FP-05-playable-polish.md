---
id: M2-FP-05
title: First-playable polish - cutscene skip, Haluna entry hitch, retry after a lost battle
role: architect
status: review
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M2-FP-04]
milestone: M2
request-from: lead
---
## Goal
Fix the three limits listed in M2-FP-04: no way to skip a cutscene, a ~1.5 s frame when Haluna loads, and a lost field battle that leaves its trigger skippable.

## Acceptance criteria
- [x] Hold-to-skip on every cutscene (an on-screen fill so it can't fire by accident); the skip plays the rest of the script instantly (flags, branches with the default choice, events), and the autosave hold and player freeze end exactly as on a normal finish.
- [x] Entering Haluna has no frame over the swap budget on this machine (work spread over frames or moved off the main thread, behind the router fade).
- [x] After a defeat the result panel offers Fight again and Return to last save (the newest readable record; the title if none). The field trigger can no longer be walked past after a loss.
- [x] Tests for each, docs/PLAYTEST.md updated.

## Notes: Haluna entry hitch and lost battle (worktree agent, parts 2 and 3)
Both criteria are met on this branch; the lead ticks the boxes on merge.

**Entry hitch.** Most of the frame was not the dressing: per-node `_ready` timing showed Asha's
character materials loading in `HalunaActorPose` (~1 s), the mood dresser (~0.55 s), the sea's ocean
grid (~40 ms) and our collision (~0.1 s). `HalunaZone.prebuild()` now does all of it on
`NOTIFICATION_SCENE_INSTANTIATED` when the zone is instantiated off the main thread (SceneRouter's
WorkerThreadPool thread, under the opaque fade). The mood dresser is swapped to `HalunaZoneDresser`
(empty `_ready`); collision uses local transforms (`HalunaCollision.frame_in`); the sea gets its grid
through `WaterSurface.surface_mesh`. No Environment, Rendering or Systems file is edited and the router
is unchanged. Swap probe, boot → Haluna, five fresh runs each: max swap frame median **1684 ms → 33 ms**
(after: 31–44 ms; budget 50). Main-thread instances (tests, the ShaderPrewarm scan) build in `_ready` as
before; `test_the_prebuild_matches_the_in_tree_build` checks that the prebuilt zone is the same zone.
Details and numbers: `game/levels/ch02/haluna/README.md`, "Entry hitch".

**Lost battle.** On a defeat, FieldBattle offers Fight again and Return to last save
(`FLOW_RESULT_LAST_SAVE`). The second one loads the newest readable record (autosave included) through
`TitleSaveEntry.continue_game`, or opens the title when there is none; the row then reads Return to
title (`FLOW_RESULT_TITLE`). `return_to_field()` refuses after a defeat. An escape returns to the
request's new `escape_spawn`. Haluna passes `BeforeBattle` (new spawn on the beach about 5 m seaward of
the strip, through `first_playable.json` `haluna.battle_escape_spawn`), so only a win reaches
`BattleReturn`. Known gap, documented in first_playable_flow.md: a pre-win save in Haluna with no
respawn would continue at `Shrine`, past the strip. No such save is written in the first playable today.

Tests: `--filter=fp_` 21/21, `--filter=haluna` 8/8, `--filter=world_return` 17/17. The new tests are
test_fp_field_battle's escape and defeat tests, plus the prebuild and BeforeBattle checks in
test_haluna_zone.

## Review log
