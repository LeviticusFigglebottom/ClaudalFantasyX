---
id: M3-ARC-03
title: DialogueBox voice hook for the Audio listener (a blip signal with its voice, and the line's step)
role: architect
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M3-AUD-07]
milestone: M3
request-from: audio
reviewer: audio
---
## Goal
Request from Audio (M3-AUD-07). Each speaker now has its own blips (`game/data/audio/voices.json`), played by
`VoiceAudio` (`game/audio/voice_audio.gd`), which listens to the box without editing it (ADR 0031):
- it polls `blips_played` once a frame and plays the voice's blip for a new one;
- it keeps the box's own `Blip` player at −80 dB (it still plays, silently);
- it learns the voice and the line id from `CutsceneSequencer.line_shown(step)`. A box shown without a sequencer
  reports only `mouth_flap(speaker, ...)` at the first vowel, so the first blips of such a line can use the previous
  voice, and narration (empty `_speaker`) can't be told apart.

Every box is under a sequencer today, so it is exact in play. A small change in `game/ui/dialogue/dialogue_box.gd`
would make it exact everywhere and drop the poll and the muting.

## Acceptance criteria
- [x] `signal blip(voice: StringName)` emitted in `_play_blip()` (with `_voice`, the speaker or the narrator
  identity), and `signal line_started(step: DialogueStep)` in `show_line()` (or a public `voice()` getter).
- [x] A switch to leave out the box's own Blip player when something else voices it (for example
  `var external_voice := false`, which `_play_blip()` honours by counting and emitting without playing).
- [ ] Audio then switches VoiceAudio to the signals (one-line change on its side; tests in
  `tests/unit/test_voice_audio.gd` already drive the box).

## Notes
- Renumbered at the Lead's big7 merge (2026-10-24): filed by audio as M3-ARC-01, which collided with m2-slice's M3-ARC-01 (data-driven chapter flow, filed first). M3-ARC-02 is the next id free across all branches.

- **Renumbered again (Lead merge, big8, 2026-10-24):** big7's M3-ARC-02 collided with claude/m2-slice's M3-ARC-02 (debug chapter select). Now M3-ARC-03, the next id free across all branches.

- **slice-polish, 2026-10-27:** `DialogueBox` now has `signal blip(voice)`, emitted for every blip due (the speaker,
  or the narrator identity on narration) and counted in `blips_played`. It also has `signal line_started(step)` from
  `show_line()`, and `var external_voice := false`. With `external_voice` on, the box counts and emits but its own
  Blip player stays silent. The change is additive, 13 lines; the UI track's motion and subtitle code is untouched.
  Tests: `tests/unit/test_dialogue_box_voice_hook.gd` (3); `dialogue_box` 24/0, `voice_audio` 12/0, `cutscene`
  77/0. **Audio:** the third box is yours. Switch VoiceAudio to the signals, set `external_voice`, and drop the poll.

## Review log
