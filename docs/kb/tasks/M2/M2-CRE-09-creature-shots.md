---
id: M2-CRE-09
title: "Creature screenshot shots and the re-approved battle baselines"
role: character
status: doing
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CRE-03]
milestone: M2
request-from: lead
---
## Goal
A battle_sandbox fixture shot per creature, approved on lavapipe after viewing, and the existing battle shots that change when the capsules go, each viewed and re-approved with its RMSE listed.

## Acceptance criteria
- [ ] See Goal; notes below record what shipped.

## Notes
- 2026-10-24: `game/levels/_tests/creatures/creature_stage.tscn` (CreatureStage: a creature or lineup, a held clip, a named view, phase and broken parts) and per-shot scenes in `game/levels/_tests/creatures/shots/`. Shots so far: creature_reef_crab, creature_reef_crab_attack, creature_drownbell, creature_drownbell_rim_broken, creature_drownbell_toll, creature_portraits. Baselines wait until all five creatures are merged.

## Review log
