---
id: M3-BPR-02
title: Boss intros for the Act I bosses (Hullgnaw, Spar Wraith, Bottle Hermit, Cinder Matron, the Drownbell)
role: combat
status: review
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-03]
milestone: M3
request-from: lead
reviewer: lead
---
## Goal
A boss fight opens with a short, original intro: the camera finds the boss, its name and title card, and the
battle's first turn follows. Data per boss; skippable; instant in captures and with skip animations; reduced motion
cuts instead of moving.

## Acceptance criteria
- [x] An intro row per Act I boss (m2-slice's scripted boss encounters) and the Drownbell
- [x] The first turn waits for it (no controller line); it never covers the timeline longer than it plays
- [x] Tests and a freeze-frame shot

## Notes
- 2026-10-24 (battle-presentation worktree): BattleBossIntro (`game/battle/scene/battle_boss_intro.gd`), attached from
  BattleChoreo.attached (net zero lines there). Data `choreo.json → boss_intro` (+ shots `boss`, `boss_tall`), validated
  by `validate_choreo.boss_intro_errors`. The first wait holds through a new generic `BattleHud.holds` hook; a party
  turn's menu, help line and actor marker are hidden by modulate until it ends. Loc `BOSS_TITLE_*`/`BOSS_EPITHET_*`.
  Shot `battle_boss_intro_hullgnaw`. Docs: battle_presentation.md "Boss intros (M3-BPR-02)". Reviewer: lead
  (staging and the epithets' tone; Narrative may want to own the epithet text).

## Review log
