# Handoff — cinematics — 2026-10-24 #3

Session: m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`. Task: M2-FP-16, the Shell Shrine temple trial (B07).

## Done
- `ShellShrineTrial`: the headless rules. `ShellShrineLevel` plus `shell_shrine.tscn`: a greybox room built from `game/data/trials/shell_shrine.json`.
- Three basins to turn, lit channels, the pool filling, the door sinking, the side pool draining, the net-float charm (key item and flag), Toma's 90 s hint, the S04/S05 inserts, and the exit to Cutscene B.
- The thread is now: the causeway head → low tide → the trial → Cutscene B → the Drownbell → the end card.
- Requests filed: M2-ENV-03 (the shrine kit) and M2-AUD-01 (the cue and SFX). The level README sits beside the scene.
- Fixed Neme's facing in haluna.tscn (a mirrored transform from M2-FP-13).

## In progress
- Nothing. M2-FP-16 is in review (reviewer: design, on whether three basins are enough puzzle).

## Exact next step
- Queue item 6: the first Vowbound (Ilun as a real summon replacing ADR 0024's stand-in) and Cutscene A/B facial animation. File task files first; check the integration branch for id collisions. FP-14 (B04) waits on the wake-shell wall's placement.

## Known issues
- In `.tscn`, `Transform3D(...)` lists the basis the other way from the "columns first" reading. Probe a node's `-global_basis.z` before trusting a hand-written rotation.
- No manifest shot covers the shrine (greybox), so the renders were checked by eye only.

## Files touched
- game/levels/ch03/shell_shrine/ (new: shell_shrine_trial.gd, shell_shrine_level.gd, shell_shrine.tscn, README.md); game/data/trials/shell_shrine.json (new)
- game/flow/first_playable_config.gd; game/data/flow/first_playable.json; game/data/flags.tres; game/data/loc/strings.csv; game/data/dialogue/ch03/ch03_trial_hint.dlg (+ compiled, dialogue.csv)
- game/levels/ch02/haluna/haluna.tscn (Neme's facing)
- tests/unit/test_shell_shrine_trial.gd, tests/integration/test_shell_shrine_level.gd (new), test_fp_thread.gd, test_haluna_slice_beats.gd; tools/tests/test_shell_shrine_trial.py (new)
- docs: PLAYTEST.md, ownership.md (a new row), task files M2-FP-16, M2-ENV-03, M2-AUD-01
