---
id: M3-AUD-13
title: Battle SFX for the battle-presentation choreography (M2-BPR-01..08)
role: audio
status: doing
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
claude/battle-presentation adds BattleChoreo (approach, strike, contact, recover, return beats), the boss and Vowbound choreographies, KO collapse and entries (docs/kb/tech/battle_presentation.md on that branch). BattleVfx already fires on `contact` there, so the M2-AUD-04 sounds follow the blow.

## Acceptance criteria
- [ ] Contact hits per weapon/style, strike whooshes, approach/return footfalls on sand, the KO collapse, Swell finisher accents, the Drownbell's toll wave and flood beats, the Vowbound call, rise and fall.
- [ ] Listen-only hooks keyed by class and signal names in data (they must load without the battle-presentation classes present on claude/audio), tests with stand-in nodes, PROVENANCE, loudness targets.

## Notes

## Review log
