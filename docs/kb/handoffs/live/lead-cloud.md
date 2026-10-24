# Live log: Lead (cloud) environment

**Session:** `session_019iimsngAgPLEram1wcbLpE` (new account) · **Branch:** `claude/undertow-lead-handoff-423ixt` (**the integration branch from 2026-10-24**; it replaces `claude/new-session-mj8c3c`, which is frozen at a504072) · **Container:** 4 CPUs, Ubuntu, lavapipe.

## Current state (2026-10-24)
- **HEAD:** see `git log -1 origin/claude/undertow-lead-handoff-423ixt`.
- **Toolchain:** Godot 4.6.3, render deps and Blender 5.0.1 fetched. `~/.local/bin/{godot,blender}` are symlinks to `~/.cache/hymn/`.
- **Environments:**
  - **pc-gpu:** Remote Control `session_01UFcBRsk9M9EKtxJKdBU2mB` (desktop-jj0o43o). It was briefed, acked, and is on M2-RND-01. Its queue: RND-01 → M1-RND-22 → M2-RND-03 → M2-RND-02 → M2-RND-04, with GPU checks before re-approvals jumping the queue. The human approved cross-session messaging on a trusted device, so it can message back.
  - **m2-slice:** cloud `session_01DQ9tdk8Uatb8Jr6raAkXiC`, branch `claude/m2-slice` (from claude/first-playable). Its queue: M2-FP-10 → Drownbell follow-ups → FP-05/ARC-15 follow-ups → Haluna slice quality → Shell Shrine trial → first Vowbound and Cutscene A/B faces. Its log: `m2-slice.md` on its branch.
  - **Lead subagents (worktrees, local):** Character (M1-CHR-08, then M2-CHR-01 Rhen on MPFB2), Combat (battle_engine.gd split, then one slice combat item), Reviewer (sweep O over the review column).
- **Merged (2026-10-24):**
  - gpu/qa-07 and gpu/rnd-21-mouth-fill. For rnd-21: asha_face_grief was re-approved after viewing it, and the 10 asha shots and the Blender asha job are green.
  - M1-CHR-08 (Character agent), review sweep O (14 of 15 closed, 8 tasks filed), and gpu/qa-08-asha-recheck.
  - claude/first-playable at bada1db. Its gate: 1254 tests, battle 99.95%, progression 96.52%, 6 shots with 0 drift, sim --check passing. The Drownbell ADR is now 0026.
- **Fixed:** the Rhen WIP build.sh is parked as build.sh.wip; it had broken the manifest test.
- **In flight:**
  - The Combat branch (M2-CMB-03 engine split, M2-CMB-04 Vowbound + ADR 0027) is test-merged in `lead/cmb` (`../wt-cmb`); its gate and sim are running.
  - The UI agent is on M2-UI-04.
- **Don't merge:** gpu/qa-05d (superseded by qa-08), gpu/chr-04-materials, gpu/qa-05b.

## Exact next step
1. When the cmb gate is green, merge lead/cmb and ping m2-slice to merge the integration branch and wire engine.summon(&"ilun").
2. Merge the UI agent's branch when it reports.
3. Full gate in a `lead/integration` worktree.
4. Sweep P over the review column (CHR-08, QA-08, CMB-03, CMB-04 with its design call on the 38.9% masher+Ilun line, and the track hand-ins).

## Log
- 2026-10-24: merged rnd-21, CHR-08, sweep O, qa-08 and first-playable. Spawned the characters track. Hourly check-in routine trig_01LJyLo42xCq3WVmAza3BMhe.
- 2026-10-24: new Lead took over. Toolchain up. PC and m2-slice briefed. Merged qa-07. Three subagents launched.
- 2026-10-24 (old account): see CONSOLIDATED-history-2026-10-23.md.
