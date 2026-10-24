---
id: M2-CRE-01
title: "Creature design sheets: reef crab, lantern eel, gull harrier, spawn-polyp, the Drownbell"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: []
milestone: M2
request-from: lead
---
## Goal
One sheet per creature in docs/kb/art/creatures/: silhouette, palette (palette.json swatches), scale against the heroes, the CTB read at battle-camera distance, and the attack, hit and KO reads. Original forms from the drowning archipelago, lamp-divers and glimmer (SPEC §7.5: dark wet carapaces and drifting glimmer wounds for Undertow-spawn).

## Acceptance criteria
- [x] A sheet per creature in docs/kb/art/creatures/ (reef_crab, lantern_eel, gull_harrier, spawn_polyp, drownbell) plus README.md (the shared rules, a scale chart against the heroes).
- [x] Each names its silhouette, palette.json swatches, scale, the read at the battle camera, and the idle/attack/cast/hit/KO reads with timings (plus phase_change for the boss).
- [x] Original: each starts from a real animal or object of Maresh with one exaggeration; banned-term scan clean.

## Notes
- 2026-10-24: the three lights stay separate: weak points are `spawn_wound`, Undertow-spawn motes `glimmer_held`, reef-beast bioluminescence uses sea swatches (`salt_glass`, `sea_glow`), never glimmer. The lantern eel's lure is `salt_glass`, so the stand-in's `glimmer_bound` emission goes away with the model.
- The Drownbell's broken rim is a model swap (`rim` / `rim_broken`) driven by `charge_broken`; the rim lip sits at the `rim` anchor (0.29 m) so BattleBossVfx's glow lands on it.
- Reviewer: art (originality and palette), with narrative welcome on the Drownbell's origin (the Shell Shrine's lost bell).

## Review log
