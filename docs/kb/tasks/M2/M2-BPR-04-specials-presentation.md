---
id: M2-BPR-04
title: Presentation for Swell finishers, the Drownbell's set piece and the Vowbound
role: combat
status: review
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-01, M2-BPR-03]
milestone: M2
request-from: lead
---
## Goal
Swell finishers (the four heroes), the Drownbell's toll, rim break and flood phase (with the PC's BattleBossVfx hooks), and the Vowbound's call, entry, dismiss and fall (Ilun).

## Acceptance criteria
- [x] Per-technique choreography rows
- [x] Drownbell beats coordinated with BattleBossVfx
- [x] Vowbound call, entry, dismiss and fall
- [x] Tests

## Notes
- Battle-presentation track standing queue (Lead, 2026-10-24). Listen-only presentation: the engine stays headless (CLAUDE.md §3).
- 2026-10-24 (worktree agent): done; docs/kb/tech/battle_presentation.md "Specials (M2-BPR-04)".
  - Styles `dive` (Lamp Dive), `verse` (Shallows Verse), `brace` (Return Tide), `glyph` (Written Light) and
    `toll`, from new generic BattleChoreo fields (`arc_m`, `windup_m`/`windup_at`, `trace_m`/`trace_strokes`,
    `stagger_sec`, `wave_m_s`, `react_scale`), all validated by tools/validate_choreo.py. No new clip: they play
    `finisher`.
  - `"shot": "finisher"` / `"toll"` in those rows is for BattleCameraDirector (the parallel camera agent); the
    plan carries it as `plan.shot`.
  - BattleBossChoreo (gather sway, rim stagger, flood brace) and BattleVowboundChoreo (call, rise, dismissal,
    fall), both built from BattleChoreo.attached; the controller is untouched. BattleStage.sync_party hands
    removed stand-ins to BattleChoreo.leave.
  - PC GPU's game/vfx/battle/battle_boss_vfx.gd: one hook, its action handler on BattleChoreo.contact when the
    stage has a sequencer (the BattleVfx.attach pattern), so the toll's ring starts on the contact beat.
  - Shots added (baselines not approved; the track lead approves after the camera merge):
    `battle_choreo_lamp_dive`, `battle_choreo_toll`, `battle_choreo_vowbound_rise`.
- Reviewer: Lead (presentation that touches pillars 1 and 4) and Cinematics (does the staging serve the beat?).

## Review log
