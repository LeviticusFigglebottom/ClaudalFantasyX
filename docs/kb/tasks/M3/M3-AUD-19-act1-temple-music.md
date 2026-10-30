---
id: M3-AUD-19
title: Act I temple and dungeon music: Ashcrown, Coilspire, the Tamsule Bell galleries
role: audio
status: review
reviewer: qa
owner_session: "audio (claude/audio; worktree agent)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
Ch5's Ashcrown temple, Ch8's Coilspire temple and Ch7's Bell galleries have no music of their own yet.

## Acceptance criteria
- [ ] Original seamless loops at -16 LUFS, music.json cue rows with pending zone notes, loop tests, listening notes, PROVENANCE.

## Notes
- `assets_src/music/ashcrown.py` -> `music/ashcrown.ogg` + `.loop.json`: an 80.0 s seamless loop, B-flat minor
  (the Terraces' five notes are all in it), 4/4 at 60 BPM, 20 bars (embers 1-4 | A 5-12 | B 13-16 | A' 17-20). A
  warm breath flute's call and answer over a low string pad, soft copper bowls, kettle gongs on 1 and 3, a large gong
  every four bars, a big-drum heartbeat, the men's hum on Bb (bars 13-20) and a plume rumble under B. Decoded: -16.02
  LUFS, TP -3.45 dBTP, 0.82 MiB (q3); seam jump x0.51, flux x0.27; no limiting.
- `assets_src/music/coilspire.py` -> `music/coilspire.ogg` + `.loop.json`: a 73.0 s seamless loop, F-sharp minor (the
  dominant of Corrow's B minor), 4/4 at 92 BPM, 28 bars (flues 1-4 | A 5-12 | B 13-20 | climb 21-24 | tail 25-28). One
  two-bar flute cell climbing a step each time, over damped copper "flues" in 3+3+2 eighths, a bass and drums on the
  same accents, a high pad, the rising bass hummed in B, surf washes and the F# beacon gong. Decoded: -16.03 LUFS, TP
  -1.53 dBTP, 0.81 MiB (q3); seam jump x0.22, flux x0.29. The limiter takes up to 2.0 dB on 0.26 % of samples (big drum).
- `assets_src/music/tamsule_bell_galleries.py` -> `music/tamsule_bell_galleries.ogg` + `.loop.json`: an 80.0 s seamless
  loop, 3/4 at 54 BPM, 24 bars, no drums. The drone is the Tamsule Bell's own partials (A2 prime; hum, prime, tierce,
  quint, nominal, deciem), snapped to whole cycles per loop; in B (13-20) the minor tierce sinks and the major deciem
  rises (A minor -> A major -> A minor). The Bell (tower_bell A2, dark 0.35, as in tidecup_match/tamsule) strikes at
  bars 1, 13 and 21; a flute song whose long notes come back a beat later from the other side (the gallery), glass
  doubling, a low plucked string. Decoded: -16.00 LUFS, TP -4.48 dBTP, 0.83 MiB (q3); seam jump x0.26, flux x0.39.
- Each file starts a sixteenth before bar 1 (`downbeat_offset_s`). Bus gains set from a first render's measured bus
  loudness to the planned levels (comment above each `render()`), re-rendered and confirmed. Original-material check
  in each docstring.
- `render_all --only ashcrown|coilspire|bell_galleries --determinism`: identical. JOBS rows + M2_CUES names; cue rows
  `ashcrown`, `coilspire`, `tamsule_bell_galleries` (resume) with "no zone row until <scene> exists" notes (the
  ch05/ashcrown and ch07/tamsule_bell_galleries scenes are only on claude/m2-slice; ch08/coilspire does not exist);
  LOOPING_CUES; Godot import with beat_count 0; listening notes "M3: Act I temples"; PROVENANCE rows. All audio now
  about 42 MiB of the 48 MiB budget.
- Checks: validate_data, taskboard --check, test_audio_data (39 OK), gdlint/gdformat on the test file, Godot
  `--filter=audio` (82 run, 0 failed), test_audio_loudness (3 OK). Skipped (cannot catch anything in this diff):
  screenshots, Blender, the full suite.
- To hear in review: the galleries' drone uses the bell's just thirds (about 15 cents off the flute's equal-tempered
  C/C#) on purpose; Coilspire's flute goes to E6.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): not reviewable yet. Its one criterion (loops, music.json rows, loop
  tests, listening notes, PROVENANCE) is unticked. Tick it, with the evidence, and it'll be reviewed with the rest.
