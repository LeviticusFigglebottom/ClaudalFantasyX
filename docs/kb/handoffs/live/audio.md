# Live log: audio (branch `claude/audio`)

Environment: cloud session `session_01FtDSYm5dJHkdC3RqXsDjif`, branch `claude/audio` (from the integration branch
`claude/undertow-lead-handoff-423ixt` at 1023a25). Role: Audio. The Lead reads this file; newest state first.

## State (2026-10-24): queue done; everything in review
- **Review (reviewer qa):** M2-AUD-01 shrine, M2-AUD-02 runtime, M2-AUD-03 three final cue families, M2-AUD-04 battle
  SFX, M2-AUD-05 ambience/footsteps/UI, M2-AUD-06 mixing pass. M2-AUD-03's "final" also needs the human's ears:
  docs/kb/audio/listening_notes.md "M2: the slice's three final cues" (+ "M2: Shell Shrine").
- **Gates at the last commit:** validate_data 0 errors; taskboard --check OK; gdlint/gdformat clean; tools/tests
  audio files OK (test_audio_data, test_audio_loudness: every shipped .ogg on its target); Godot full suite
  1466 run, 0 failed after updating two other-role tests (see M2-AUD-02 notes). No screenshots (no scene/shader
  touched). Byte-reproducibility: every new job was rendered and checked; `render_all.py --only <cue> --determinism`
  on all eight M2-AUD-03 jobs: every file byte-identical (and identical to the committed files).
- **Requests filed:** M2-AUD-07 (cinematics: sequencer -> Audio.play_music; drop music_volume_db −8), M2-AUD-08
  (ui: Audio section in settings), M2-AUD-09 (cinematics: footstep surface markers in Haluna).
- **Touched outside audio paths (Lead, please note):** project.godot autoload line; one `check_audio` call in
  tools/validate_data.py; appended rows in game/data/ui/accessibility.json (reduced_audio + 4 volume rows),
  game/data/loc/strings.csv, assets/PROVENANCE.md, docs/kb/ownership.md (Audio runtime claim);
  tests/unit/test_ui_settings.gd and test_cutscene_sequencer.gd expectations. ADR 0031 (number checked free on
  all branches at the time).
- **Gotcha:** tools/tests/test_audio_loudness.py takes ~4 min (decodes every file); ffmpeg upmixes mono at −3 dB,
  so it decodes mono files as mono.

## Exact next step
Merge `claude/audio` into the integration branch. Then: the human's listening verdict (§16 Q3) per cue;
next audio items: `saltgrass_causeway` field bed (B06) when that zone exists, a per-area world reverb bus, the
sung (formant voice) A/B of hush_first_verse if the human asks.

## Un-pushed state
None.
