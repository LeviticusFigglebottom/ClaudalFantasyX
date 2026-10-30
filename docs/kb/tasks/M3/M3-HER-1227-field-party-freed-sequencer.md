---
id: M3-HER-1227
title: "Request: HeroFieldParty.should_hide casts a freed sequencer (SCRIPT ERROR every physics frame after one is freed)"
role: combat
status: review
owner_session: "integration-qa (claude/hero-integration)"
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
`game/hero_motion/hero_field_party.gd` `should_hide()` does `var seq := s as CutsceneSequencer` before
`is_instance_valid(seq)`, so once a CutsceneSequencer it cached (`_sequencers`, found under the zone) is freed, every
physics frame raises "Trying to cast a freed object" (the same class of bug as M3-AUD-814's LifeAudio). act1-chapters
hit it with `tools/act1/cutscene_stills` (a sequencer freed after each scene); a zone that frees a scene's sequencer
in play would hit it the same way.

## Acceptance criteria
- [x] Check validity before the cast (`if not is_instance_valid(s): continue`), or drop freed sequencers from the
      cache; a test that frees a cached sequencer and steps the party.

## Review log
- 2026-10-29 integration-qa: the check had been in since 41c277d26 (M3-HER-1149's freed-cast sweep); the test was
  missing. Added `test_hero_followers::test_a_freed_cached_sequencer_is_skipped`: a freed cached sequencer ahead of a
  playing one. It fails on the old order (the freed cast aborts should_hide() before the live one is seen). 13/0.
  Reviewer: cinematics (act1-chapters, the requester).
