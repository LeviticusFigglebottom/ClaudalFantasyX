---
id: M2-CRE-09
title: "Creature screenshot shots and the re-approved battle baselines"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CRE-03]
milestone: M2
request-from: lead
---
## Goal
A battle_sandbox fixture shot per creature, approved on lavapipe after viewing, and the existing battle shots that change when the capsules go, each viewed and re-approved with its RMSE listed.

## Acceptance criteria
- [x] A shot per creature (14 `creature_*` shots, CreatureStage scenes), approved on lavapipe after viewing.
- [x] Every existing battle shot the models change, viewed side by side with its old baseline and re-approved (RMSE below).
- [x] Stable: a second capture of six of them (animated idle included) is RMSE 0.00000.

## Notes
- 2026-10-24: `game/levels/_tests/creatures/creature_stage.tscn` (CreatureStage: a creature or lineup, a held clip, a named view, phase and broken parts) and per-shot scenes in `game/levels/_tests/creatures/shots/`. Shots so far: creature_reef_crab, creature_reef_crab_attack, creature_drownbell, creature_drownbell_rim_broken, creature_drownbell_toll, creature_portraits. Baselines wait until all five creatures are merged.

- 2026-10-24, re-approved after viewing (old baseline → new, linear RMSE; each change is the creature models replacing the box/cylinder/prism/capsule stand-ins, nothing else moved):
  battle_hud_preview 0.05223 · battle_swap_menu 0.05250 · battle_victory 0.00913 (the fallen creatures fade behind the panel) · battle_statuses 0.05242 · battle_swell_ring 0.05033 · battle_read_panel 0.04324 · battle_opening_banner 0.05039 · battle_swell_modes 0.05250 · battle_vowbound_call 0.05621 · battle_vowbound_out 0.05475 · drownbell_flood 0.03279 (the bronze bell settled in the flood, and the polyp model under the water).
- New baselines: creature_reef_crab, creature_reef_crab_attack, creature_drownbell, creature_drownbell_rim_broken, creature_drownbell_toll, creature_portraits, creature_hullgnaw, creature_tower_limpet, creature_lantern_eel, creature_oil_slug, creature_spawn_polyp, creature_wickfry, creature_bottle_hermit, creature_gull_harrier (2.46 MB together).
- **Known, for art and the PC:** under the Flood the water absorbs most of the polyps' glow (mouths 12, tube tips and lips now emissive too); BattleBossVfx's polyp light is the stronger cue there. Brightening further blooms the polyp in open light.

## Review log
