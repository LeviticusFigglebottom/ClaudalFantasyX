---
id: M3-AUD-818
title: "Act I's 68 cutscene `@sfx` cues (Ch1, Ch4–Ch9): every one had no file and played nothing"
role: audio
status: review
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

## Review log
