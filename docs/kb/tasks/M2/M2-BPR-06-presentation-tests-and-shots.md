---
id: M2-BPR-06
title: Battle presentation tests and mid-action freeze-frame shots
role: combat
reviewer: lead
status: review
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-01]
milestone: M2
request-from: lead
---
## Goal
Deterministic mid-action freeze-frame shots per action type, plus tests. View every changed battle baseline and re-approve only what's intended, with the RMSE.

## Acceptance criteria
- [x] A freeze-frame shot per action type in shots.json
- [x] Every changed battle baseline viewed, RMSE noted
- [x] Tests

## Notes
- Battle-presentation track standing queue (Lead, 2026-10-24). Listen-only presentation: the engine stays headless (CLAUDE.md §3).

- 2026-10-24 (track lead): 11 freeze-frames (melee, hit, cast, support, read, ko, swap, lamp_dive, toll, vowbound_rise, summon) plus 2 arena shots, all viewed, run-to-run RMSE 0. Changed baselines (viewed, intended): drownbell_flood (arena, then the flood brace), battle_choreo_vowbound_rise (help line). Items have no shot (capture fixtures carry no items).

## Review log
