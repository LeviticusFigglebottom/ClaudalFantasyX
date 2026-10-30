---
id: M3-AUD-04
title: Area themes: Terraces of Ash (Ch5) and the Seawall (Ch8)
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents for M2-AUD-10, M3-AUD-02, -04, -06, -07)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
Ch5 Pemakar's Lanternfall festival among the graves; Ch8 Corrow Bastion, nine hundred years of the same defence.

## Acceptance criteria
- [x] Two original area loops at −16 LUFS, listening notes, cue rows.

## Notes
- `assets_src/music/terraces_of_ash.py` -> `assets/audio/music/terraces_of_ash.ogg` (+ sidecar, .import). F with a
  five-note "in"-type scale (F Gb Bb C Db), 3/4 at 72 BPM, 32 bars, an 80.00 s loop. A plucked zither carries the
  tune. Lantern bars fall in short runs, tuned bubbles stand for the channels, copper gongs keep an 8-bar cycle,
  and women hum the tune an octave down in B and A'. No flute and no interlock (unlike Haluna).
  Decoded: -16.07 LUFS, -1.68 dBTP, 0.79 MiB (q3). Seam jump x2.38, flux x2.68. Determinism identical.
  Bus levels relative to the zither: low strings -9, lanterns -9, hum -6, gongs -11, drums -14, water -17.
- `assets_src/music/corrow_seawall.py` -> `assets/audio/music/corrow_seawall.ogg` (+ sidecar, .import). B minor,
  4/4 at 76 BPM, a ground bass (B D | A F# | G E G | F#) that comes round 6 times unchanged: "nine hundred years of
  the same defence". Above it: a low, dark breath flute, muted plucks (rope and block), footstep drums (the
  stair), a beacon kettle gong each time round, and the Watchers' hummed chorale (men, then women) in the second
  half. 75.79 s loop. The file starts a sixteenth before bar 1 (the sidecar's `downbeat_offset_s`), so the seam
  misses the heaviest downbeat: on the downbeat, flux was 4.46x and failed the gate; now jump x0.27, flux x0.19.
  Decoded: -16.05 LUFS, -1.49 dBTP, 0.73 MiB (q3). Determinism identical. Bus levels relative to the flute: hum
  -5, plucks -9, bass -7, drums -10, gongs -12. The limiter takes up to 4.5 dB on 0.6 % of samples (step-drum hits).
- `music.json` cues `terraces_of_ash` and `corrow_seawall` (resume: true, like Haluna). No zone rows: `ch05/pemakar`
  and `ch08/corrow` don't exist yet. Added to JOBS/M2_CUES and LOOPING_CUES. Listening notes (1) and (3).
- Gates: validate_data, taskboard --check, `unittest -p "test_audio_*.py"`, Godot `--filter=audio` (37/37).

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
