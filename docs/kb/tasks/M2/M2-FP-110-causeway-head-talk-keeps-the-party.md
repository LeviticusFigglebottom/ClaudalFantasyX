---
id: M2-FP-110
title: "FAST-TRACK: B05 at the causeway head keeps Asha and Toma in view, and their lines play on them"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-FP-107]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
B05 (`ch02_low_tide`) is a conversation between Asha and Toma at the causeway head. Played as a held scene, it made
HeroFieldParty hide both followers, so Rhen stood alone while they talked. Their stage actors are hidden after
Cutscene A, so no body played their talk clip either.

## Acceptance criteria
- [x] HalunaStory plays B05 like a bark (`_play_unstaged`: `freeze_player`, not `hold_player`).
- [x] A line whose stage actor is hidden plays on that hero's visible follower (`CutsceneNpcTalk.follower`).
- [x] Test: test_haluna_villagers `test_the_causeway_head_talk_keeps_asha_and_toma_and_they_talk`; haluna 57/0.

## Review log
