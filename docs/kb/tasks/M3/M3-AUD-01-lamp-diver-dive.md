---
id: M3-AUD-01
title: Ch1 "Lamp-Diver": the underwater dive cue
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents for M2-AUD-10, M3-AUD-02, -04, -06, -07)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
Act I Ch1 (act_outline.md): Rhen's salvage dive in a drowned tower, a tutorial dungeon lit by his lantern. It must sit with the underwater look (M2-RND-02, docs/kb/tech/underwater*.md).

## Acceptance criteria
- [x] An original loop (muffled, pressurised, the lantern's warmth against the dark; the current-song hinted, never quoted), −16 LUFS, listening notes, a music.json cue row.

## Notes
- 2026-10-24 audio (claude/audio): `assets_src/music/lamp_diver.py`: a 90 s loop, D Dorian, everything through a ~900 Hz water muffle into a 5 s dark reverb: sub pressure drone, a warm swelling lantern chord, dulled metallophone glints, a muffled heartbeat, bubble trains, and once per loop a single far hummed voice with the Hush's opening gesture (a hint of the current-song, never the phrase). −16.0 LUFS, −2.95 dBTP, 0 % limited. Cue row added; zone row when ch01/oruvel_underway exists. Original material (see the docstring); byte-reproducible (render_all --determinism).

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
