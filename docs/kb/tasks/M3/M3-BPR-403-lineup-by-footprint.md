---
id: M3-BPR-403
title: "Battle line-up: space the slots by the real models' footprints"
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: [M3-BPR-402]
milestone: M3
request-from: combat
---
## Goal
The party and enemy slots (BattleStage) were laid out for primitive stand-ins. With the creature models (and soon the
real heroes) some neighbours overlap on their marks: in sandbox_reef the reef crab and the gull harrier stand 1.92 m
apart against footprints of about 0.8 + 1.0 m plus clearance. Spread each side's slots so neighbours keep their
footprints (BattleChoreoPlan.footprint) + spacing.clearance_m apart, within the arena's floor, and keep the camera
shots' safe frames.

## Acceptance criteria
- [x] No two fighters on their marks overlap (a test over every encounter's line-up, with models).
- [x] Every battle shot viewed and re-approved: the integration's big11/big12 approvals (viewed on the PC gate)
      and this track's view of render db0819b (2026-10-27, superseded by them); the safe-frame tests pass.

## Review log
