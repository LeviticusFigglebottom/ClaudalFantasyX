---
id: M3-AUD-02
title: Ch7: the Tidecup / Reefball match theme
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents for M2-AUD-10, M3-AUD-02, -04, -06, -07)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
Act I Ch7: the story Reefball match, played for the ones who didn't come up (N-12). A sports theme that is also a lament.

## Acceptance criteria
- [x] An original loop for the match, −16 LUFS, listening notes, a cue row.

## Notes
- `assets_src/music/tidecup_match.py` -> `assets/audio/music/tidecup_match.ogg` (+ `.loop.json`, `.ogg.import`).
  A minor, 4/4 at 112 BPM, 32 bars, a 68.57 s seamless loop (LOOPSTART 0 / LOOPLENGTH 3024000). The game's drive
  (frame drums, big drum, a running plucked ostinato, walking bass) runs under a slow flute lament that never lands
  on A while the drums play. The Tamsule Bell (a padded tower bell, prime A2) marks the sections. The crowd hums the
  song's outline in B, and salt-glass bars double the song in A'. The last 4 bars ("the naming") drop to the big
  drum's heartbeat. Original material; the docstring says so.
- Decoded: -16.05 LUFS integrated, -1.86 dBTP, 0.78 MiB (q3.5). Seam jump x0.08, flux x0.90. `--determinism`
  identical. The limiter takes up to 2.9 dB on 0.7 % of samples (the big-drum downbeats).
- Bus levels relative to the flute, as measured: ostinato -9, bass -8, drums -5, Bell -6, glass -12, hum -10.
- `music.json` cue `tidecup_match` (no zone row: `ch07/tamsule_bell` doesn't exist yet). Added to render_all
  JOBS/M2_CUES and LOOPING_CUES. Listening notes: "M3: Act I area and match themes" (2).
- Gates: validate_data, taskboard --check, `unittest -p "test_audio_*.py"`, Godot `--filter=audio` (37/37).

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
