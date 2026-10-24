---
id: M2-HRO-03
title: "Battle hero actors: the real heroes play the clip contract in battle (integration of UI-07, CHR-07, BPR-10)"
role: combat
status: doing
owner_session: "hero-integration (claude/hero-integration)"
reviewer: combat
depends_on: [M2-UI-07]
milestone: M2
request-from: lead
---
## Goal
In battle the heroes are still capsules on the integration branch. The pieces are on three branches: the stand-in hook
data (claude/ui, M2-UI-07), the 12 contract clips (claude/characters, M2-CHR-07) and the choreography plus placeholder
clips (claude/battle-presentation, M2-BPR-10). Make them meet, check every contract clip on the real model, and fix
what does not read naturally (clip crossfades, KO hold, idle micro-motion, ready and victory).

## Acceptance criteria
- [ ] A trial merge of the three branches shows Rhen, Asha and Toma in battle playing idle, ready, attack (contact on
      the marker), hit, KO, victory, cast and finisher; any gap is fixed in this track's files or requested from the
      owner track.
- [ ] Clip changes crossfade (no pops), and a one-shot returns to idle smoothly.
- [ ] Shots battle_hero_* (viewed), and tests for the hero actor path.

## Notes
- Also depends on M2-CHR-07 (claude/characters) and M2-BPR-10 (claude/battle-presentation), not on this branch yet.
battle-presentation owns the choreography; this track only adds the hero-actor side and reports.

## Review log
