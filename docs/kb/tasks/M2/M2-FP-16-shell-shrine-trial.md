---
id: M2-FP-16
title: The Shell Shrine temple trial (B07) at slice quality: puzzle data, level, hooks, reward
role: cinematics
status: doing
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-13]
milestone: M2
request-from: lead
reviewer: design
---
## Goal
Queue item 5 of the m2-slice track. SPEC §10.2 asks the slice for "one small temple trial". The beat sheet's B07 (docs/kb/story/beats/vertical_slice.md) and the Shell Shrine brief (docs/kb/art/environments/haluna.md §3) describe it: three rotating shell-basins redirect water until the inner pool fills and the chamber door floods open. There's no dialogue during the puzzle, apart from one Toma hint bark after 90 s idle. Optionally, draining the side pool reveals the net-float charm, which sets `ch03_found_net_float` (Cutscene B pays it off).

## Acceptance criteria
- [ ] The puzzle rules are headless and deterministic (`ShellShrineTrial`, no Node dependencies): basins with 90° rotation steps, each spout's channel target, water traced from the source, the inner pool filling over time while water reaches it, and the side sluice draining the side pool. All of it is data in JSON (`game/data/world/trials/shell_shrine.json`).
- [ ] A tools test checks the data: the puzzle is solvable from the start state, the minimum solution length is in the band the data names (it shouldn't solve in one turn), and the side pool can be drained.
- [ ] The level `ch03/shell_shrine`: a greybox until Environment's shrine kit exists. It has the three basins (interact to rotate, a 1.2 s eased turn), channels that light while water runs through them, the inner pool rising, the door sinking, the side pool and the charm pickup (the `net_float_charm` key item and the flag), and camera shots S01–S05 for the approach, the threshold, the overview, the water and the side pool.
- [ ] Hooks: the trial's start, each rotation, the pool filling, the door opening and the charm pickup are signals (for VFX, audio and the HUD). The hint bark (`ch03_trial_hint`) plays once after `hint_idle_sec` with no rotation.
- [ ] The thread runs the causeway head (B05) → the Shell Shrine trial → Cutscene B → the Drownbell → the end card. The whole-thread test solves it.
- [ ] File Environment's (shrine kit) and Audio's (`shell_shrine_interior`, water and stone SFX) requests.

## Review log
