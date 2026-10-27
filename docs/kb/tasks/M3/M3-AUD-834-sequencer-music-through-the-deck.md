---
id: M3-AUD-834
title: "Request (cutscene owner): play @music through the director's MusicDeck, and an @stem cue"
role: cinematics
status: todo
owner_session: ""
depends_on: [M3-AUD-833]
milestone: M3
request-from: audio
---
## Goal
The CutsceneSequencer plays `@music` on its own AudioStreamPlayer from `<music_dir><id>.ogg` (`_cue_music`,
`_music_stream`), so a cutscene can't use music.json's stems or start_stems. Two cues need them:
- **`undertow_rising`** (M3-AUD-819): Ch1 C1-13's run brings stem 1 (the pulse) in over about 2 s (M3-AUD-829).
- **`seawall_hold`** (M3-AUD-822): Ch8's waves bring stems 1 and 2 in.

Until this lands, M3-AUD-833's stand-ins play each cue's first stem only. That is correct for the opening, but the
second-stem trigger can't happen.

## Acceptance criteria
- [ ] `@music <id>`: when music.json has the cue, play it through `AudioDirector.play_music` (or its MusicDeck),
      keeping the sequencer's fade and volume semantics. A file or stand-in is the fallback.
- [ ] `@stem <index> on|off fade=<s>` (or `@music <id> stems=0,1`): calls `MusicDeck.set_stem` on the playing cue.
- [ ] The zone bed's hold while the sequencer's music plays keeps working (audio_director.gd `_seen_seq_music`).
- [ ] `@wait music=<marker>` waits for the playing cue to reach music.json's `markers.<marker>` (seconds from the
      cue's first sample), instead of only holding for `max=`. The Ch4 song's sung lines and the Ebbing's movements
      have markers now; tools/tests/test_music_markers.py keeps them equal to their sources.
- [ ] Tell audio when this lands: audio will drop the two stem stand-ins and act1-chapters can add the
      `@stem 1 on fade=2.0` line to the run (M3-AUD-829).

## Review log
