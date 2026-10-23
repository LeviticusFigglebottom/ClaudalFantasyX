---
id: M2-FP-06
title: The Drownbell, a two-phase boss on the CTB engine (vertical slice B10)
role: combat
status: review
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M2-FP-04]
milestone: M2
request-from: lead
---
## Goal
The boss Cutscene B calls to battle (`<<event start_battle drownbell>>`), per vertical_slice.md §5 and balance_targets.md: phase 1 the Toll (timeline push, break the rim), phase 2 the Flood (polyps heal it, calling Ilun clears the water). Data-driven, deterministic, tested, written up in battle_ctb.md, then wired into the thread before the end card.

## Acceptance criteria
- [x] Encounter `drownbell` in encounters.json; enemies, skills and AI as data.
- [x] A phase mechanism in the engine (data-driven, headless, seeded); the phase change shows in the timeline preview.
- [x] Phase 1 and phase 2 gimmicks as designed; a first-playable stand-in for the Ilun summon if the full Vowbound system is out of scope (documented).
- [x] Balance sim run against the `boss_drownbell` bands; results in balance_report.md.
- [x] Cutscene B → the Drownbell → end card in the thread; tests. (Boss side and its tests done; the thread wiring is the first-playable Lead's: `BattleRequest` for encounter `drownbell`, party active `rhen, asha, toma`, reserve none, victory flag `ch03_drownbell_defeated`.)

## Notes (combat worktree, 2026-10-23)
- Engine: `game/battle/boss_mechanics.gd` (`BossMechanics`) holds the rules; the engine calls it at five points. Data shape, API, HUD: battle_ctb.md "The Drownbell (M2-FP-06)". Stand-in: ADR 0023.
- Balance (1000 seeds): naive 0.0%, role answer 79.7%, smart 89.6%, p90 51 actions (5000 seeds: 0.0 / 80.3 / 90.4%).
- Live battles fill `BattleEngine.story_flags` from `Game.get_flag` (`BattleBossHud.live_flags`), so `ch03_ilun_bound` must be set before the fight (Cutscene B sets it) for Asha to have Call Ilun.
- Touched UI-owned files minimally (additive): `game/ui/battle/turn_timeline.gd` (`intent_labels`, the `intent` slot field) and `game/ui/battle/timeline_chip.gd` (the "· The Toll" suffix). UI may restyle.

## Review log
