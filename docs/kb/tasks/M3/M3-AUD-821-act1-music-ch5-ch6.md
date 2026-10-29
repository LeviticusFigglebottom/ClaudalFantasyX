---
id: M3-AUD-821
title: "Act I music: Ch5's lanternfall, hush_second_verse, kerrid_stair, kahre_summon; Ch6's liss_theme, raid, shoals_dusk"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW; composed by a worktree agent)"
depends_on: [M3-AUD-823]
milestone: M3
request-from: lead
---
## Goal
act1-chapters' M3-C05-04 and M3-C06-04: the scripts' missing Ch5 and Ch6 music.

## Acceptance criteria
- [x] `lanternfall`: 92 s. A 60 s thinning procession, then a 32 s loop of the one drum left at the weir.
- [x] `hush_second_verse`: 47 s, the Hush's MEL_B over a drone. *mir* is at 31.54 s and the thunder at 32.59 s, so
      the plume flash should land at 31.54 s.
- [x] `kerrid_stair`: 20 s, the motif's first statement. The motif itself is in motifs.py `KERRID_STAIR`, for
      goodbye_kerrid.
- [x] `kahre_summon`: a 6 s sting (assets/audio/sfx, wired like ilun_summon).
- [x] `liss_theme`: a 61 s loop.
- [x] `raid`: a 92 s loop in G at ORDER_HUM_BPM, with the Order's hum (motifs.ORDER_HUM) under the fire. Its first
      23 s are fire and drum, so the `stillguard_hum` SFX carries the first statement.
- [x] `shoals_dusk`: a 64 s loop.
- [x] All −16 LUFS ±0.1, deterministic; PROVENANCE; listening notes. 4.0 MiB in all.

## Notes
- For a listen: raid's hummed sections reach −7.4 LUFS momentary, about 6 LU over its fire-only sections.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
