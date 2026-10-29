---
id: M3-HER-1227
title: "Request: HeroFieldParty.should_hide casts a freed sequencer (SCRIPT ERROR every physics frame after one is freed)"
role: combat
status: todo
owner_session: ""
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
- [ ] Check validity before the cast (`if not is_instance_valid(s): continue`), or drop freed sequencers from the
      cache; a test that frees a cached sequencer and steps the party.

## Review log
