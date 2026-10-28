---
id: M3-AUD-833
title: "Nine Act I @music ids were silent in cutscenes: stand-ins for the alias and stem cues"
role: audio
status: review
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: cinematics
depends_on: [M3-AUD-823]
milestone: M3
request-from: audio
---
## Goal
Found while following up M3-AUD-829. The CutsceneSequencer plays `<music_dir><id>.ogg`, or the file its
`music_stand_ins` row names, and never reads music.json. M3-AUD-823's alias rows and the two stem cues therefore
resolved in music.json and passed test_cutscene_sfx_files, but played nothing in a cutscene. The affected ids are
oruvel_raft, oruvel_underway, haluna_wake, brightwater_crossing, pemakar_terraces, ashcrown_trial, tamsule_port,
undertow_rising and seawall_hold. The sequencer only warned "no music".

## Acceptance criteria
- [x] game/data/cutscene/sequencer.json `music_stand_ins`: each id names its file, appended after the existing
      rows. An alias points to its cue's file. A stem cue points to its first stem (`undertow_rising_p1`,
      `seawall_hold_p1`), which is what music.json starts.
- [x] tools/tests/test_cutscene_sfx_files.py `test_every_music_cue_plays_as_the_sequencer_finds_it`: every
      script `@music` id has a file under music_dir by its own name or its stand-in. It fails on the old table and
      lists the nine ids.
- [ ] A stem cue's later stems (undertow_rising's pulse for C1-13; seawall_hold's waves) need the sequencer to play
      music.json cues through the director's MusicDeck: request M3-AUD-834.

## Review log
