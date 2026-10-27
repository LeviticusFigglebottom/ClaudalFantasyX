---
id: M2-FP-107
title: "FAST-TRACK: a bark freezes Rhen without hiding Asha and Toma"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-FP-102, M2-HER-1102]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
HeroFieldParty (M2-HER-1102) hides the followers while any sequencer that holds the player plays, so every Haluna
bark made Asha and Toma blink out of the street and back: a pop the playtest would read as primitive.

## Acceptance criteria
- [x] `CutsceneSequencer.freeze_player`: freezes the player's input like `hold_player`, but the scene doesn't count as
  staged, so HeroFieldParty keeps the followers in view. HalunaStory's barks use it; staged scenes still hold.
- [x] Test: test_haluna_villagers `test_a_bark_freezes_rhen_and_keeps_the_party_in_view`.

## Notes
- hero-integration's `hero_field_party.gd` is untouched. ZoneStory's dialogue beats still hold the player, since
  they are usually staged.

## Review log
