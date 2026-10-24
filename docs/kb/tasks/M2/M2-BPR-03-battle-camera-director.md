---
id: M2-BPR-03
title: Battle camera director with speed, skip and reduced-motion settings
role: combat
status: doing
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-01]
milestone: M2
request-from: lead
---
## Goal
Framed shots for an actor's turn, the target, a cast and a finisher, over a readable default, with tactical clarity first (the timeline and HUD are never covered and the default frame returns before input). Accessibility: battle speed, skip animations, reduced motion (cuts, no sweeps), no flashes beyond battle_vfx caps.

## Acceptance criteria
- [ ] BattleCameraDirector, listen-only, data in choreo.json
- [ ] Default framing returns before every command menu opens
- [ ] Battle speed and battle animations settings in accessibility.json (appended rows)
- [ ] Reduced motion: no camera travel, no shake
- [ ] Tests

## Notes
- Battle-presentation track standing queue (Lead, 2026-10-24). Listen-only presentation: the engine stays headless (CLAUDE.md §3).

## Review log
