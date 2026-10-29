---
id: M3-AUD-804
title: Act II music sketches I: Ch10 Ossa Fen and Reedhollow, Ch11 Sunken Vey and Lowlight, Ch12 Keth Pass and Quellan
role: audio
status: blocked
reviewer: qa
owner_session: "audio (claude/audio; worktree agent)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
SPEC §3 and act_outline.md Act II. Sketches: the themes and palette of each place, as short loops the human can judge.

## Acceptance criteria
- [x] Original seamless loops at −16 LUFS, cue rows (no zone rows), listening notes, PROVENANCE, determinism.

## Notes
2026-10-24 (audio, worktree agent): six sketches, all score-as-code, synthesized only.
- **Sources:** `assets_src/music/{ossa_fen,reedhollow,sunken_vey,lowlight,keth_pass,quellan}.py`, plus a shared kit,
  `assets_src/music/act2_voices.py`, for the new voices (fen reed pipe; Kirru whistle, root-harp, water-gourd and
  tongue-click; glass harmonica copied from sefir_theme; Lamp Engine stroke and conduit hum; highland ten-string
  lute and strum; woolback bell) and the seamless textures (insects, wind, pass-cords, the deep's cold). Each
  docstring has the brief, key, form and an original-material check.
- **Outputs:** `assets/audio/music/<cue>.ogg` + `.loop.json` + `.ogg.import` (loop=true, beat_count=0). Each file
  starts a sixteenth before its first downbeat (`downbeat_offset_s`).

| Cue | Key, metre | Form (bars) | Length | Size | LUFS / TP | Seam flux |
|---|---|---|---|---|---|---|
| ossa_fen | G Dorian, 4/4 at 62 | 4 intro, 8 A (reed pipe), 4 B (low flute) | 61.94 s | 892,682 B (q2) | -16.08 / -2.91 | x1.37 |
| reedhollow | Kirru mode on A (A B C# D# F#), 5/4 (3+2) at 78 | 4, 6 A (whistlers), 4 B (clutch hum), 2 | 61.54 s | 646,381 B | -15.99 / -1.76 | x0.30 |
| sunken_vey | Eb Dorian, 3/4 at 46 | 4, 8 A/A' (glass), 3, 1 rest | 62.61 s | 409,995 B | -16.00 / -4.92 | x0.56 |
| lowlight | C minor, 4/4 at 58 | 3 engine, 4 A (Kirru call), 4 B (Hush on glass), 4 both, stall | 62.07 s | 543,854 B | -16.00 / -2.92 | x0.40 |
| keth_pass | E minor, 6/8 at 46 | 4, 8 A (hocket), 4 B (lone pipe), 8 A' | 62.61 s | 802,614 B | -16.05 / -2.92 | x1.11 |
| quellan | F major, 4/4 at 92 | 4, 8 A, 4 B, 8 A' (third below) | 62.61 s | 670,872 B | -16.02 / -2.00 | x0.77 |

- **Bus balance:** each cue was rendered once with every bus at 0 dB, the gains were set from `bus_lufs` to the
  planned levels relative to the lead (`LEVELS` in each source), then it was re-rendered; every bus is within
  0.1 LU of plan (reedhollow's clicks came out 1.1 LU low after its bus filter was added, and their gain was
  raised by that much for the shipped render). Limiter: reedhollow 1.5 dB on 0.4 % of samples
  (harp and clicks); quellan 0.2 dB on 0.03 %; the rest are untouched.
- **Size:** six cues 3,966,398 B (3.78 MiB). ossa_fen is Vorbis q2 (insect and drip noise cost bits: about
  1.05 MB at q3); the others are q3.
- **Leitmotifs:** lowlight develops the game's own motifs: the Kirru call from reedhollow (Ressa/Nhoa) and the
  Hush's outline (hush_theme_v2). Reedhollow's rising clutch line is the farewell-tide's *shape* only, and is offered
  as a candidate seed for the Letting; it is not decided here.
- **Wiring:** cue rows in `game/data/audio/music.json` (no zone rows until the scenes exist), JOBS and M2_CUES in
  `tools/audio/render_all.py`, LOOPING_CUES in `tests/unit/test_audio_loops.gd`, six PROVENANCE pairs, and a
  listening-notes section ("M3: Act II sketches I").
- **Gates:** validate_data, taskboard --check, test_audio_data, gdlint/gdformat, Godot --filter=audio (105 pass)
  and test_audio_loudness (all audio 46.55 MiB of 48) pass. Skipped: screenshots, Blender, full suite (no scene,
  shader or Blender source touched). Determinism: `render_all.py --only music/<cue>.py --determinism` is identical
  for all six.

## Review log
