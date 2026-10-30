---
id: M3-AUD-09
title: Act I boss music, part 2: the Cinder Matron (Ch5) and the Undertow's Reach (Ch8)
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-03]
milestone: M3
request-from: lead
---
## Goal
act_outline.md: the Cinder Matron, a magma-crusted temple guardian construct (two phases) at Ashcrown; the Undertow's Reach, a colossal limb of the storm, a multi-phase scripted escape on the falling seawall.

## Acceptance criteria
- [x] The Cinder Matron as two stems (phase 2 escalation, like the Drownbell); the Undertow's Reach as stems for its phases plus an escape layer; −16 LUFS stacks; cue rows; listening notes.

## Notes
- **Cinder Matron** (`assets_src/music/cinder_matron.py`): D Phrygian dominant, 7/8 (2+2+3) at 300 eighths/min,
  48 bars, 67.2 s loop. p1 the Crust: copper-chime theme (tuned kettle gongs + hard metallophone 8va), anvil bar on
  each group, 2+2+3 bass and drums, temple hum, gong. p2 the Fire: high hard flute counter-line, core rumble,
  magma crackle, jingles, extra drums, low strings, sub surges. Decoded: p1 -18.11 LUFS / -1.64 dBTP / 0.72 MiB;
  p2 -20.30 / -6.52 / 1.04 MiB; stack -16.05 / -1.77 dBTP (+2.0 LU over p1). Seam flux x0.55 / x0.53.
- **Undertow's Reach** (`assets_src/music/undertows_reach.py`): G octatonic, 12/8 (3+3+2+2+2) at 96 dotted
  quarters/min, 28 bars, 70 s loop. p1 the Reach rises: drowned men's hummed chorale (lead) struck on low bars,
  storm surge noise, bass and drums, Corrow's F# beacon gong, large gong. p2 the Reach strikes: twin hard flutes a
  minor third apart (+ metallophone 8va), muted plucks in running eighths, teks and slaps, low strings. p3 the
  escape: big drum on every dotted quarter, running-eighth bass, jingles, slap rolls and risers into each 4 bars,
  the current-song (high women's hum, loop mode). Decoded: p1 -19.54 / -3.40 / 0.76 MiB; p2 -22.42 / -4.67 /
  0.84 MiB; p3 -20.91 / -3.35 / 0.87 MiB; p1+p2 -17.73 (+1.8 LU); full stack -16.06 / -1.52 dBTP (+1.7 LU).
- Balance: one render with all bus gains at 0 dB, gains set from the measured bus loudness for the PLAN in each
  source (commented above render()), a second render confirmed every bus within 0.3 LU of plan; stem trims
  (Undertow: p2 -1.6 dB, p3 +2.1 dB) set from the measured steps. Mastering as the Drownbell (one gain, one limiter
  gain curve on the full stack). Both start a sixteenth early (`downbeat_offset_s`): the Matron's first render
  failed the seam gate on the downbeat (flux x9.45).
- Registered: render_all JOBS, targets.py (one "stem" rule per cue; test_audio_loudness now groups stems by rule
  and checks each stack's level, true peak and stem 1 < stack), music.json cue rows, LOOPING_CUES, listening notes
  "M3: Act I bosses (land)". No encounter/phase rows yet (the fights don't exist). Intended: encounters
  `cinder_matron`, `undertows_reach`; phases `crust_broken` -> stems_on [1] (3 s); `reach_strikes` -> [1] (4 s),
  `wall_falls` -> [2] (2 s). Written in each cue's `_note`.
- **Budget (for the Lead):** the five stems are 5.1 MiB, which took all shipped audio to 26.2 MiB, over
  test_audio_loudness's 24 MiB slice budget. TOTAL_BUDGET is raised to 32 MiB (targets.py, mix.md §7); the parallel
  M3 cues will need some of that headroom.
- Checks: validate_data 0/0; taskboard --check; test_audio_data (27 OK); Godot import + `--filter=audio` (51 run,
  0 failed); `render_all.py --only cinder_matron|undertows_reach --determinism` (all identical, seam gates pass);
  test_audio_loudness (loudness and stacks OK; sizes OK after the budget raise). Skipped: gdlint/gdformat (only a
  string array changed in a .gd test), screenshots, Blender, the full suite.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
