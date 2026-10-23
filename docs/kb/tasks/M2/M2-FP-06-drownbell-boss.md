---
id: M2-FP-06
title: The Drownbell, a two-phase boss on the CTB engine (vertical slice B10)
role: combat
status: doing
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M2-FP-04]
milestone: M2
request-from: lead
---
## Goal
The boss Cutscene B calls to battle (`<<event start_battle drownbell>>`), per vertical_slice.md §5 and balance_targets.md: phase 1 the Toll (timeline push, break the rim), phase 2 the Flood (polyps heal it, calling Ilun clears the water). Data-driven, deterministic, tested, written up in battle_ctb.md, then wired into the thread before the end card.

## Acceptance criteria
- [ ] Encounter `drownbell` in encounters.json; enemies, skills and AI as data.
- [ ] A phase mechanism in the engine (data-driven, headless, seeded); the phase change shows in the timeline preview.
- [ ] Phase 1 and phase 2 gimmicks as designed; a first-playable stand-in for the Ilun summon if the full Vowbound system is out of scope (documented).
- [ ] Balance sim run against the `boss_drownbell` bands; results in balance_report.md.
- [ ] Cutscene B → the Drownbell → end card in the thread; tests.

## Review log
