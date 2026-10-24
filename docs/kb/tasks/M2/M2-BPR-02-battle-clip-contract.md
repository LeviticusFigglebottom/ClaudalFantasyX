---
id: M2-BPR-02
title: Battle clip contract: named clips on models, procedural fallback on stand-ins
role: combat
reviewer: lead
status: review
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-01]
milestone: M2
request-from: lead
---
## Goal
Fighters play named clips (idle, ready, attack, cast, item, hit, ko, victory, ...) when their model has them, and fall back to procedural motion (lunge, recoil, collapse) on primitive stand-ins. Agree the names with the characters and creatures tracks; document in docs/kb/tech/battle_presentation.md.

## Acceptance criteria
- [x] Clip names and fallbacks in docs/kb/tech/battle_presentation.md and choreo.json
- [x] A model's AnimationPlayer clip is used when present (hero actors M2-UI-07, creature actors M2-CRE-03)
- [x] Procedural fallback for every clip on primitives
- [x] Requests posted to the characters and creatures tracks
- [x] Tests

## Notes
- Battle-presentation track standing queue (Lead, 2026-10-24). Listen-only presentation: the engine stays headless (CLAUDE.md §3).

- 2026-10-24 (track lead): BattleClips + § Clip contract. Messages sent to the characters and creatures sessions; follow-up at merge: BattleActorMotion (claude/creatures) should defer its action/hit clips to the sequencer beats.

## Review log
