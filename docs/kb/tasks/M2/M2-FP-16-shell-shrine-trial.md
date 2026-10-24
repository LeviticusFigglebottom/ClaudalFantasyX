---
id: M2-FP-16
title: The Shell Shrine temple trial (B07) at slice quality: puzzle data, level, hooks, reward
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-13]
milestone: M2
request-from: lead
reviewer: design
---
## Goal
Queue item 5 of the m2-slice track. SPEC §10.2 asks the slice for "one small temple trial". The beat sheet's B07 (docs/kb/story/beats/vertical_slice.md) and the Shell Shrine brief (docs/kb/art/environments/haluna.md §3) describe it: three rotating shell-basins redirect water until the inner pool fills and the chamber door floods open. There's no dialogue during the puzzle, apart from one Toma hint bark after 90 s idle. Optionally, draining the side pool reveals the net-float charm, which sets `ch03_found_net_float` (Cutscene B pays it off).

## Acceptance criteria
- [x] The puzzle rules are headless and deterministic (`ShellShrineTrial`, no Node dependencies): basins with 90° rotation steps, each spout's channel target, water traced from the source, the inner pool filling over time while water reaches it, and the side sluice draining the side pool. All of it is data in JSON (`game/data/world/trials/shell_shrine.json`).
- [x] A tools test checks the data: the puzzle is solvable from the start state, the minimum solution length is in the band the data names (it shouldn't solve in one turn), and the side pool can be drained.
- [x] The level `ch03/shell_shrine`: a greybox until Environment's shrine kit exists. It has the three basins (interact to rotate, a 1.2 s eased turn), channels that light while water runs through them, the inner pool rising, the door sinking, the side pool and the charm pickup (the `net_float_charm` key item and the flag), and camera shots S01–S05 for the approach, the threshold, the overview, the water and the side pool.
- [x] Hooks: the trial's start, each rotation, the pool filling, the door opening and the charm pickup are signals (for VFX, audio and the HUD). The hint bark (`ch03_trial_hint`) plays once after `hint_idle_sec` with no rotation.
- [x] The thread runs the causeway head (B05) → the Shell Shrine trial → Cutscene B → the Drownbell → the end card. The whole-thread test solves it.
- [x] File Environment's (shrine kit) and Audio's (`shell_shrine_interior`, water and stone SFX) requests.

## Notes (m2-slice, 2026-10-24)
- **Puzzle.** Three basins, one lip each, 90° clockwise turns. b1 is fed by the spring. The shortest route to the inner pool is 3 turns (b1 once toward b2, b3 twice toward the pool). The side sluice also takes 3 (b1 once, b2 twice), and Rhen then has to turn b2 back. Looping water is lost. Data band: 3–8 turns. Design: please judge whether this is enough puzzle for B07's five minutes. The JSON can carry more basins or a longer chain without code changes.
- **Level.** A greybox room built from the JSON. The S03 overview frames the whole room, for puzzle clarity (pillar 4). Inserts: S04 when the water first reaches the pool, S05 when the side pool empties; Rhen waits out each one (`insert_sec`). The door sinks, and its collision goes, when the pool fills. Flags: `ch03_side_pool_drained` and `ch03_shrine_door_open` (new), `ch03_found_net_float`, plus the `net_float_charm` key item. A reload restores the door and the side pool from the flags.
- **Thread.** The causeway head (B05) now opens the shrine (`haluna.ending_scene`), and the shrine's exit opens Cutscene B (`shell_shrine.next_scene`). The whole-thread test solves the trial using the trial's own search.
- **Hint.** `ch03_trial_hint` (Toma: "Start at the spring. Follow the water, not the stone.") plays once after 90 s with no turn, on a non-freezing sequencer.
- **Lavapipe check** (scratch renders, not baselines): the overview reads, with the lit channel path b1→b2→b3→pool visible in cyan. The first render caught Rhen spawning in a threshold camera that sat a metre behind his head (I removed that volume; S03 covers the room), and an oculus light and a spawn that were both mirrored, because the `.tscn` basis order is the transpose of what I assumed. Neme's facing in haluna.tscn (M2-FP-13) had the same error and is fixed in the same commit.
- **Not here.** Asha and Toma don't appear in the room (there's no follower system). S01 (the approach) and S02 (the threshold) wait for the real kit. Requests filed: M2-ENV-03 (the interior kit) and M2-AUD-01 (the cue and SFX).
- **Tests:** `tests/unit/test_shell_shrine_trial.gd` (6), `tests/integration/test_shell_shrine_level.gd` (5), `tools/tests/test_shell_shrine_trial.py` (4), and `test_fp_thread.gd` updated.

## Review log
