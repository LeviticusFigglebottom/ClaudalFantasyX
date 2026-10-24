# Handoff — cinematics — 2026-10-24 #8

Session: m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`. Items from the Lead's 07:54 message (review sweep Q): the CMB-05 reconcile (FP-17 rebased), M2-FP-22 and M1-ENV-11.

## Done
- **CMB-05 duplicate:**
  - Merged the integration branch (4314dde) and took the canonical CMB-05 everywhere.
  - FP-17 is rebased: the loadout's `vowbound` and `retire_skills`, `flood_call` with `field_up`, and a [0, 95] band.
  - Bands at 1000 seeds: role_answer 71.0%, smart 85.3% (p90 60), flood_call 38.8%. `sim --check` rc 0.
  - The bell's lone-absorber rule was dropped as unneeded.
- **M2-FP-22:** the Shell Shrine has four basins, and the water starts looping b1 → b4 → b1. Shortest solution 6, side pool 4, random-turner median 75. Data plus tests; S03 is checked by eye.
- **M1-ENV-11:**
  - The Haluna collision bodies now enter the tree with their shapes, so the AUTO shelter probe sees them on the main-thread path too (before, it saw nothing).
  - `capture_setup.gd` goes through ShaderGlobals. Shots are unchanged byte for byte.

## In progress
- Nothing. FP-17, FP-22 and ENV-11 are in review.

## Exact next step
- M2-CMB-06 (sweep Q, optional for this track): a Swell-on ceiling of 50% for the Vowbound masher, plus a tuning-log entry.
- Or whatever the Lead queues next. Messages to the Lead are still refused, so the live log is the channel.

## Known issues
- The 200-seed Drownbell guard allows role 60% and p90 65 (sampling spread at the band edges). `sim --check` at 1000 seeds is the gate.

## Files touched
- **Merge:** game/battle and sim, game/data/battle, tools/balance/targets.json, the docs/kb/design docs, ADR 0026, tests (see the merge commit 7fa4400).
- **FP-22:** game/data/trials/shell_shrine.json, game/levels/ch03/shell_shrine/README.md, tests/unit/test_shell_shrine_trial.gd, tests/integration/test_shell_shrine_level.gd, tools/tests/test_shell_shrine_trial.py.
- **ENV-11:** game/levels/ch02/haluna/haluna_collision.gd, tests/integration/test_haluna_shelter.gd (new), tests/screenshots/capture_setup.gd.

## Gates
- lint and format, validate_data, dlgc, taskboard --check.
- Coverage: 1403 tests, battle 99.95%. The full suite after ENV-11: 1405, 0 failed.
- Tools unittest: 484 OK. sim --check rc 0.
- Shots: the veg and haluna shots pass, byte-identical across ENV-11.
