---
id: M3-AUD-08
title: Act I boss music, part 1: Hullgnaw (Ch1) and the Spar-Wraith (Ch4)
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-03]
milestone: M3
request-from: lead
---
## Goal
act_outline.md: Hullgnaw, an Undertow-spawn eel grown through a ship's ribs, fought on a breaking raft (the turn-order tutorial); the Spar-Wraith, a spawn tangled in a drowned trader's rigging, fought on the derelict's deck.

## Acceptance criteria
- [x] Two original boss loops (intro + loop as battle_standard_v2), −16 LUFS, distinct from the Drownbell; music.json cues and battle.encounters rows when the encounters exist; listening notes.

## Notes
- **Hullgnaw** (`assets_src/music/hullgnaw.py` -> `assets/audio/music/hullgnaw.ogg`): G minor, 6/8 at a dotted
  quarter of 90, a 2.67 s intro (a copy of bars 47-48) and a 64.0 s loop (48 bars). The eel is a fingered bass that
  crawls chromatically into each next root. Muted rope plucks through a wooden body, frame drums and the big drum,
  a G1 gong for the hull, and a hard breath-flute theme with an open plucked counterline. Readable for the
  turn-order tutorial: one tune at a time, two big beats a bar. Balance vs the flute (measured): drums -6, big drum
  -8, eel -5, rope -9, counter -9, gong -14. Decoded -16.09 LUFS, TP -1.49 dBTP, 720 KB, seam flux x2.45, splice
  residual -127 dB. The limiter takes up to 4.6 dB on one stack in bar 27, on 0.9 % of samples.
- **Spar-Wraith** (`assets_src/music/spar_wraith.py` -> `spar_wraith.ogg`): F# Locrian, 7/8 (2+2+3) at an eighth of
  300, a 2.8 s intro (bars 51-52) and a 72.8 s loop (52 bars). Wind in the shrouds, stick-slip rope creaks (both
  synthesized in the cue file), a slack hull drum, a bass on the root and the tritone, a low breathy flute, high
  shroud plucks, and a quiet pad for the dead sails in the becalmed bars 33-44. Balance vs the flute: drums -5, big
  -7, bass -6, hull -10, rope -11, wind -13, shrouds -9, sails -13. Decoded -16.08 LUFS, TP -1.44 dBTP, 867 KB, seam
  flux x0.90, splice -99 dB, limiter 0.1 dB.
- Both: Vorbis q3.0, `render_all.py --only <name> --determinism` identical; .import synced and committed; music.json
  `cues` rows (no battle.encounters rows: the encounters don't exist yet); LOOPING_CUES; listening notes "M3: Act I
  bosses (sea)".
- **Budget:** all shipped audio is now about 23.5 MiB against the 24 MiB TOTAL_BUDGET (tools/audio/targets.py). The
  two parallel M3 cue batches will push it over, so the Lead needs to raise the budget or re-encode.
- Gates: validate_data, taskboard --check, test_audio_data, Godot `--filter=audio` (51/51), test_audio_loudness
  (OK). Skipped: screenshots, Blender, full suite, coverage (no game/ code touched).

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
