---
id: M2-AUD-01
title: Shell Shrine trial audio: the interior cue and the puzzle's sounds
role: audio
status: todo
owner_session: ""
depends_on: [M2-FP-16]
milestone: M2
request-from: cinematics
---
## Goal
Request from the m2-slice track. The trial (M2-FP-16) has no sound yet. The beat sheet's music cue for B07 is `shell_shrine_interior` (today the sequencer's stand-in is `temple_trial`), and the puzzle needs diegetic feedback (pillar 4: you hear the water go where you sent it).

## Acceptance criteria
- [ ] The `shell_shrine_interior` cue (original; the "temple trial ambience" of SPEC's score list), looping under the trial.
- [ ] SFX on the trial's signals (`ShellShrineTrial`: `rotated`, `flow_changed`, `side_pool_drained`, `pool_filled`; `ShellShrineLevel.charm_taken`): a stone grind for a basin turn, the water's new route (a pour into a basin, a spill onto a grate, the inner pool filling), the side pool emptying, the door's shell valve sinking, and a small glint for the charm.
- [ ] Wired by a listener node, as with the boss VFX hooks (battle_ctb.md). The rules are never touched.

## Review log
