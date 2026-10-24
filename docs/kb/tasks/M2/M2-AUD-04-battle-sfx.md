---
id: M2-AUD-04
title: Battle SFX for the M2-RND-03/04 VFX library
role: audio
status: todo
owner_session: ""
depends_on: [M2-AUD-02]
milestone: M2
request-from: lead
---
## Goal
The battle VFX library (battle_vfx.md) is silent. Every effect and boss moment needs a sound, wired listen-only to the same engine and BattleVfx events.

## Acceptance criteria
- [ ] Synthesized SFX: element hits (none, fire, ice, lightning, water, holy), Lamp Dive, Shallows Verse, Read, heal, status, KO release, the ambush and preemptive stingers, the Drownbell toll (and its gather), the rim crack and break, polyp rise and mend, Floodnet, the bell's release, the Vowbound call and dismiss.
- [ ] A data table (`game/data/audio/battle_sfx.json`: VFX effect id or engine event -> SFX), a `BattleAudio` listener that never writes combat state, and a reduced-audio setting (fewer, softer layers; no stingers' sub-bass).
- [ ] Tests: every VFX effect id maps to a sound that exists, the trigger rules, reduced audio, determinism of the renders.

## Notes

## Review log
