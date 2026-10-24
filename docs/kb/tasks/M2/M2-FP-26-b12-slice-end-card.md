---
id: M2-FP-26
title: B12 slice end card: Rhen's voice-over, the piano coda and a short credits roll
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: []
reviewer: narrative
milestone: M2
request-from: lead
---
## Goal
The Lead's 2026-10-24 13:09 intro audit found this M2-review BLOCKER; it goes ahead of M3. The end card shows a title and a line but lacks B12's voice-over ("I said yes to a girl I'd known for two days. I didn't know yet what I was walking her toward."), the `hush_first_verse` piano coda (audio has the cue) and a short credits roll.

## Acceptance criteria
- [x] The end card plays the voice-over line as text (a loc key) over black, then the coda, then a short credits roll from data, then the prompt.
- [x] Tests updated; the shots that show the end card are unchanged, or re-approved with the reason given.

## Notes
- 2026-10-24 m2-slice, **done, for review by narrative.**
  - **The sequence:** the end card opens on Rhen's voice-over (`FLOW_END_CARD_VOICE`, the beat sheet's line, held 7 s), then the title and line fade in, then six credit rows one at a time (`end_card.credits`, loc keys: the game, the slice, the music, the engine's MIT notice, the OFL fonts, thanks). The prompt follows after 16 s.
  - **Timing:** everything is timed from `first_playable.json` `end_card` and computed from `elapsed`; there are no tweens.
  - **The coda:** the piano coda is `hush_coda`, which the audio track's `game/data/audio/music.json` plays as the end card's zone music, so it lands when claude/audio merges. Nothing else is needed here.
  - **Tests:** `test_fp_end_card.gd` (3). No screenshot shows the end card.

## Review log
