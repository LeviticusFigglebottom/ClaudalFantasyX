---
id: M3-AUD-815
title: "Request (creatures track, claude/creatures): two read-only accessors for audio's LifeAudio (chat_speaking, startled)"
role: character
status: review
owner_session: "creatures (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY, branch claude/creatures)"
reviewer: audio
depends_on: [M3-AUD-814]
milestone: M3
request-from: audio
---
## Goal
Audio's LifeAudio (M3-AUD-814) murmurs a villager's chat turn and darts a startled shoal. Today it reads two private
fields to do so (read only, never written): FieldNpc `_chat_speaker` and WildlifeShoal `_startle`. A rename would
silence those sounds without failing anything.

## Acceptance criteria
- [x] `FieldNpc.chat_speaking() -> bool`: true while this villager speaks its turn of a chat (the same test as line
      469's `_chat_speaker == npc_id and chatting()`).
- [x] `WildlifeShoal.startled() -> bool`: true while the startle timer runs (`_startle > 0.0`).
- [x] No behaviour change. LifeAudio picks both up by name (game/data/audio/life.json) with no audio change.

## Notes
- Done on claude/creatures (2026-10-27): both accessors, covered by test_villager_routines (chat_speaking() agrees with the talk clip every frame of a chat) and test_wildlife (startled()). Audio may now switch life.json to the method names. Reviewer: audio.

## Review log
