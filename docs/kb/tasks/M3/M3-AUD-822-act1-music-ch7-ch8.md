---
id: M3-AUD-822
title: "Act I music: Ch7's tidecup_after and tidecup_crowd; Ch8's virel_bound, virel_summon, corrow_aftermath, seawall_hold"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW; composed by a worktree agent)"
depends_on: [M3-AUD-823]
milestone: M3
request-from: lead
---
## Goal
act1-chapters' M3-C07-06 and M3-C08-101: the scripts' missing Ch7 and Ch8 cues.

## Acceptance criteria
- [x] `tidecup_after`: 57 s of warm strings in A minor, never resolving, ending on a held E.
- [x] `tidecup_crowd`: a 62 s loop, the match's own crowd (reefball_sfx's talkers and babble).
- [x] `virel_bound` (7.9 s) and `virel_summon` (5.8 s, into assets/audio/sfx): the Hush's first phrase
      (hush_theme_v2.MEL_A, imported) on a new double reed (`spire_reed`).
- [x] `corrow_aftermath`: a 62 s loop of rain and one slow plucked string.
- [x] `seawall_hold`: three stems stacking across the waves (−19.3, −17.6, then −16.1 together), the sub on the
      Reach's G.
- [x] All −16 LUFS ±0.2, TP ≤ −1.6, deterministic; PROVENANCE; listening notes. 4.3 MiB in all.

## Notes
- battle_sfx.json's `vowbound_stings.virel` → virel_summon; Virel herself is on claude/act1-chapters.
- For a listen: corrow_aftermath's plucks reach about −8 LUFS momentary.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
