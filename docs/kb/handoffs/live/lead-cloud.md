# Live log: Lead (cloud) environment

**Session:** `session_019iimsngAgPLEram1wcbLpE` (new account) · **Branch:** `claude/undertow-lead-handoff-423ixt` (the integration branch) · **Container:** 4 CPUs, Ubuntu, lavapipe. The container has restarted twice; the disk and the worktrees survived both times.

## Current state (2026-10-24, after merge batch 2)
- **HEAD:** `3e59f8d` (see `git log -1 origin/claude/undertow-lead-handoff-423ixt`).
- **Last gates:**
  - Full ci36 green at b533db0.
  - Batch-2 gate at lead/batch2: 1375 tests, coverage within baseline, 66 shots (2 re-approved after viewing: veg_beach_wide, battle_opening_banner), sim --check passing, including `sandbox_reef_vowbound` at 38.9% against the 40% line.
- **Merged today, in order:**
  - qa-07, rnd-21 (grief re-approved), CHR-08, sweep O, qa-08, first-playable (Drownbell; ADR 0024 → 0026).
  - Combat: CMB-03 engine split and CMB-04 Vowbound (ADR 0027).
  - UI-04 field menu, sweep P, RND-01 Undertow (4 undertow baselines re-approved; compute ADR 0028).
  - m2-slice through 9c1485a (FP-10..13, 16, 18, UI-10), fp-10-keylight-check, and RND-23/24 (router `scene_swapping`, mouth bounce pass).
  - **Batch 2:** CMB-05 (Vowbound A1–A3, handoff renumbered to combat-13), ENV-09+08 (vegetation LOD chain; shader_globals.gd conflict hand-merged: both APIs kept, with `project_default` = `default_value`), PC RND-22 prewarm (ADR 0029 proposed), PC RND-03 battle VFX, and PC RND-02 underwater.
- **Not merged yet:**
  - `gpu/m2-rnd-04-drownbell-vfx` (d6c6056, built on RND-03): needs a test merge plus its pending shot `drownbell_flood`.
  - The pending shots `underwater_below`, `underwater_window` and `underwater_waterline` (docs/kb/qa/gpu/2026-10-24-rnd-02-pending-shots.json) still need adding to tests/screenshots/shots.json and approving on lavapipe.
  - Newer m2-slice and characters work.
- **Don't merge:** gpu/qa-05d, gpu/chr-04-materials, gpu/qa-05b.
- **Environments:**
  - **pc-gpu:** `session_01UFcBRsk9M9EKtxJKdBU2mB`. Queue topped up: RND-24 GPU check → ENV-09 GPU LOD check → M2-RND-05 → ADR 0029 follow-ups (no threaded loads) → slice perf sweep → M1-QA-09 (after CHR-12).
  - **m2-slice:** `session_01DQ9tdk8Uatb8Jr6raAkXiC` (Auto). Next: FP-17 (the Drownbell with the real Ilun call; CMB-05 is now merged).
  - **characters:** `session_01JqzzxgJU9Dmu7fRhmCG9aQ` (Auto). On M1-CHR-12 and Rhen. New for it: M1-CHR-13 (vest normal flip), and M1-RND-25 (the grief lip rim is the inner-lip shadow, not the mouth shader).
  - **Local agents:** none running.
- **Routing via files:** the human denied one cross-session message, so routing goes into task files (Lead notes) where possible.

## Exact next step
1. Test-merge gpu/m2-rnd-04-drownbell-vfx. Add drownbell_flood and the 3 underwater shots to shots.json, capture them on lavapipe, view and approve them, and merge.
2. Tell m2-slice that CMB-05 is in, for FP-17 (see the CMB-05 handoff combat-13 "What m2-slice needs").
3. Review sweep Q over the review column: CMB-05, ENV-09, RND-22/23/24, RND-01, RND-02/03/04, UI-04, and the m2-slice tasks.
4. Launch local agents on open M2 work: M2-UI-05 (Vowbound HUD), M1-ENV-10, and M2-ART-02 prep.

## Log
- 2026-10-24: merge batch 2 (3e59f8d). PC queue topped up.
- 2026-10-24: merged rnd-21, CHR-08, sweep O, qa-08, first-playable, cmb, ui-04, sweep P, rnd-01, m2-slice, rnd-23. Spawned the characters track. Hourly check-in trig_01LJyLo42xCq3WVmAza3BMhe.
- 2026-10-24: new Lead took over. Toolchain up. PC and m2-slice briefed.
- 2026-10-24 (old account): see CONSOLIDATED-history-2026-10-23.md.
