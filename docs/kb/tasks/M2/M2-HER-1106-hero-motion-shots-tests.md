---
id: M2-HER-1106
title: "Hero motion shots and tests: field heroes, battle heroes, a cutscene turn strip"
role: qa
status: review
owner_session: "hero-integration (claude/hero-integration)"
reviewer: lead
depends_on: [M2-HER-1101, M2-HER-1102, M2-HER-1103, M2-HER-1104]
milestone: M2
request-from: lead
---
## Goal
Screenshots and tests that hold the heroes' naturalness: field hero shots, battle hero shots and a cutscene turn
strip, viewed and judged; tests for the turn-rate cap, blend weights by speed and no snapping.

## Acceptance criteria
- [x] Shots in tests/screenshots (manifest rows) viewed and approved on lavapipe: field_hero_rhen_walk, field_hero_party,
      field_hero_gait_strip, hero_cutscene_turn_strip and battle_heroes_idle/attack/hit/ko/victory/cast/finisher (11).
- [x] tests/unit/test_hero_*.gd cover the cap, the blend, no snapping, the followers and the battle actor path
      (14 files, plus tests/integration/test_hero_cutscene_snaps.gd; ADR 0192).

## Notes
- 2026-10-27: battle_heroes_idle re-approved from lead/gate-render-hero-integration-1c9bf8b (big12's tutorial prompt).
  Ready for the Lead's review.

## Review log
