---
id: M3-AUD-850
title: "Mix pass on the slice: cutscene foley, villager beds and wildlife together; ducking under dialogue"
role: audio
status: review
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: design
depends_on: [M3-AUD-23, M3-AUD-814, M3-AUD-817]
milestone: M3
request-from: lead
---
## Goal
The Lead (10-27, 21:42), item 5: a mix pass on the slice now that cutscene foley, villager life and wildlife play
together, covering loudness targets and ducking under dialogue.

## Acceptance criteria
- [x] mix_report.md regenerated (tools/audio/mix_report.py). Every new layer is at its rule (targets.py), and the
      shipped audio is 71.0 of 72 MiB.
- [x] **Ducking:** the dialogue duck took only Music (−4) and Ambience (−2). Footsteps, villagers' work, wildlife and
      cutscene foley (all on World) now dip −3 dB under a line (mix.json).
- [x] **The chat:** villagers' murmurs are voice-like and pitched where the voice is, so a duck isn't enough.
      LifeAudio's `quiet` (the director's dialogue duck) holds a murmur from starting while a line is up. Work sounds
      go on, ducked.
- [x] mix.md has the slice's layer table (plain against under a line): every world layer is ≥ 3 LU under the
      voice.
- [x] Tests: test_life_audio (the chat held over a line; the duck takes World down). `life_audio` 14/0,
      `audio_runtime` 11/0, `audio` 169/0.
- [ ] By ear on the slice, with the human's listening pass.

## Review log
