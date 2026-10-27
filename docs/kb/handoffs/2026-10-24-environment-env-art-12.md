# Handoff — environment (env-art coordinating session) — 2026-10-24 #env-art-12

The single entry point is `docs/kb/handoffs/live/env-art.md`; its MERGE-READY line is @ 5ab6029c. Each worktree
agent's own handoff is listed below.

## Done (since 2026-10-24-environment-lead-session.md)
- **Merges:**
  - The integration branch, big7 and the big8 id work.
  - The final arenas swapped in through `arenas.json` (all seven ids), with the battle arena test pointed at the
    contract's `CameraHints`.
- **Act I zone kits, all in review:**

  | Task | Zone | Handoff |
  |---|---|---|
  | M3-ENV-07 | Oruvel raft-town | `-oruvel` |
  | M3-ENV-07B | Oruvel storm and Hullgnaw's split | `-env-art-1` |
  | M3-ENV-08 | Brightwater ferry | `-brightwater` |
  | M3-ENV-08B | the Seventh Terrace | `-seventh-terrace` |
  | M3-ENV-700 | the ferry's transom | `-env-art-11` |
  | M3-ENV-09 | Ashcrown | `-ashcrown` |
  | M3-ENV-09B | Pemakar's far Ashcrown | `-env-art-9` |
  | M3-ENV-10 | Coilspire | `-env-art-10` |
  | M2-ENV-12 | Haluna gull normals | `-gull-normals` |

- **Baselines:**
  - The ten arena and flood baselines are re-approved from isolated `capture.sh` captures. Shared single-process
    captures depend on capture order once creature models are in frame.
  - Rule for every agent: baselines come only from `capture.sh`.
- **Fixes:**
  - A merge-introduced empty job in `blender_builds.json`.
  - The union merge helper now refuses a job without an `id` or `runs`.

## In progress
- Nothing. M3-ENV-11 merged at d065835e (MERGE-READY in the live log).

## Exact next step
1. Done: M3-ENV-11 is merged and gated (MERGE-READY @ d065835e).
2. Take the next item from the Lead's queue. New task ids come from M3-ENV-701 onwards, ADRs from 0160, and
   handoffs are named `-env-art-<n>` (14 and up).

## Known issues
- Five UI and dialogue shots drift from the wetter Haluna tidewalls: `field_objective_line`,
  `field_interact_prompt`, `field_area_title`, `field_tip_card` and `dialogue_continue`. They are their owners'
  baselines and are flagged for the Lead.
- Owed by others:
  - Art: colour-script rows `ch01_storm`, `ch04_derelict`, `ch05_temple` and `ch08_day`.
  - Character + Tools: sign-off on eight new import kinds.
  - Rendering: M3-RND-24 and M3-RND-25.
  - m2-slice: M3-ARC-04.
- Battle-presentation's AudioDirector freed-instance error and the loader's owner warning in multi-shot captures.

## Files touched
- `game/data/battle/arenas.json`, `tests/unit/test_battle_arena.gd` and the arena and flood baselines.
- The task files M3-ENV-07..11, 07B, 08B, 09B, 700, M2-ENV-12, M3-ARC-04 and M3-RND-26.
- `docs/kb/handoffs/live/env-art.md`, `tools/tests/test_fog_lamps.py` and `tools/dev/blender_builds.json`.
- Merges of every worktree agent's branch (see each handoff).
