---
id: M2-BPR-02
title: Battle clip contract: named clips on models, procedural fallback on stand-ins
role: combat
status: doing
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-01]
milestone: M2
request-from: lead
---
## Goal
Fighters play named clips (idle, ready, attack, cast, item, hit, ko, victory, ...) when their model has them, and fall back to procedural motion (lunge, recoil, collapse) on primitive stand-ins. Agree the names with the characters and creatures tracks; document in docs/kb/tech/battle_presentation.md.

## Acceptance criteria
- [ ] Clip names and fallbacks in docs/kb/tech/battle_presentation.md and choreo.json
- [ ] A model's AnimationPlayer clip is used when present (hero actors M2-UI-07, creature actors M2-CRE-03)
- [ ] Procedural fallback for every clip on primitives
- [ ] Requests posted to the characters and creatures tracks
- [ ] Tests

## Notes
- Battle-presentation track standing queue (Lead, 2026-10-24). Listen-only presentation: the engine stays headless (CLAUDE.md §3).

## Review log
