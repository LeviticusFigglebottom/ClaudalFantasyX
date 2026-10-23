---
id: M2-FP-05
title: First-playable thread hardening (review-sweep-K)
role: architect
status: todo
owner_session: ""
depends_on: [M2-FP-04]
milestone: M2
request-from: "qa"
---
## Acceptance criteria
- [ ] A defeat-path integration test (loss, then Return, Fight again, Continue)
- [ ] test_fp_thread drives the story's real battle trigger, not a direct start; it adds a save then load leg
- [ ] No latch is marked done before its scene change is confirmed (field_battle.gd ~:64, end_card.gd ~:84, haluna_story.gd ~:90); the router reports busy, the caller retries or waits; test it
- [ ] ch02_met_asha comes from the zone JSON, not hard-coded (haluna_zone.gd ~:31); a test proves the battle strip can't be walked around
- [ ] The close-up lighting rule (QA-05/CHR-04 shadow normal bias) is applied in the playable zones' suns (haluna_mood.tscn ~:83 via the zone or an override, first_verse.tscn ~:169)
- [ ] The sequencer host resumes, or is cancelled, if the sequencer leaves the tree; unsupported cue args warn

## Review log
