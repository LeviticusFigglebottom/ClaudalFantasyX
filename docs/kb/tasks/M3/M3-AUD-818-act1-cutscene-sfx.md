---
id: M3-AUD-818
title: "Act I's 68 cutscene `@sfx` cues (Ch1, Ch4–Ch9): every one had no file and played nothing"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M3-AUD-817]
milestone: M3
request-from: audio
---
## Goal
The CutsceneSequencer plays `@sfx <id>` from `assets/audio/sfx/<id>.ogg` (sequencer.json `sfx_dir`) and only warns
when the file is missing. Across Act I's cutscenes (claude/act1-chapters and claude/m2-slice), 68 ids had no file,
so the roaring wall in "Going Under", the crowd's "Up." at the naming, the coast's bells and every other scripted
sound were silent.

## Acceptance criteria
- [x] All 68 synthesized in assets_src/sfx/act1_cutscene_sfx.py, each written for its scene (the cue's lines are in
      its comment): Ch1 11, Ch4 9, Ch5 6, Ch6 8, Ch7 6, Ch8 24, Ch9 4. Deterministic, PROVENANCE rows, 2.1 MiB.
- [x] Four sung or hummed cues (neme_humming, asha_hum_lullaby, pell_storm_note, current_song) are short original
      phrases in a five-note mode, quoting nothing.
- [x] Each has its own loudness rule in tools/audio/targets.py; the loudness test passes.
- [x] tools/tests/test_cutscene_sfx_files.py fails on any `@sfx` with no file. It passes on claude/audio and on a
      scratch merge with claude/act1-chapters (all of Ch8).

## Notes
- 2026-10-27 audio: the sequencer plays these flat (no `at=`); the director routes its players to a bus. Levels:
  sharp one-shots about −18 LUFS (momentary max), foley about −22, the long beds under a line about −24.
- Listen-for notes: docs/kb/audio/listening_notes.md, "M3: Act I cutscene cues".

- 2026-10-27 audio, to act1-chapters' briefs (M3-C06-04, M3-C08-101, M3-C09-06):
  - `barge_pole` is wood creak and the Reeds' footfalls only, with no water, so `brine_iron_hiss` stays B05's only
    water sound. `raft_pole` (Ch9) keeps its water.
  - `pell_storm_note` is a voice doing a storm: one huge, low, rising and falling throat note.
  - `staff_bell_shells` is pitched in the_ebbing's A minor pentatonic.
  - `current_song` sings **Dace's current-song**, now written once in assets_src/music/motifs.py `CURRENT_SONG`
    (D dorian, distinct from the Hush). `rhen_current_hum` and `going_under` (Ch1) must use those notes, so the
    melodies match by construction.
- Still open from those briefs (music, not `@sfx`): the chapters' missing `@music` cues, `vein_run`
  (AshcrownTrial `ran`/`landed`) and `float_ring_bell`. Those are M3-AUD-819 and on.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
