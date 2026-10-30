---
id: M3-AUD-864
title: "Act I sound at final quality, as played: coverage gate, quality checks, listening pass by analysis (ADR 0041, 0042)"
role: audio
status: review
owner_session: "claude/audio (2026-10-29)"
reviewer: qa
depends_on: [M3-AUD-861, M3-HER-1146]
milestone: M3
request-from: lead
---
## Goal
The Lead's 2026-10-29 brief: audit the whole of Act I's sound (title to Ch9, as played) on lead/gate-big18, which
carries every track's newest work, then fix what the audit finds.

1. **Coverage.** Every Act I zone has an ambience bed, and every cutscene `@music` and `@sfx` resolves to a real
   cue. Every battle action, hit, status, Swell, Vowbound call, UI confirm and cancel, footstep surface and door has
   a sound. A test fails on any missing or placeholder cue.
2. **Quality.** Loudness within each bus's budget, click-free loop seams, deterministic renders, no clipping, and
   music changes between zones, battles and cutscenes crossfading on the beat (no hard cuts).
3. **Listening by analysis.** Spectrograms and level over time for every Act I cue, looking for harshness, mud
   or monotony. The weakest cues are improved in their synth sources.

## Acceptance criteria
- [x] `tools/audio/act1_audio_audit.py` covers cutscene actions (doors included), battle events (statuses and ticks,
      Vowbound calls, Swell, weapon accents), footstep grounds and core UI as well as its earlier sections, and
      `tools/tests/test_act1_audio_audit.py` fails on any item. Every section is 0.
- [x] big18's 5 new ability gaps closed: Kerrid's and Liss's Swell finishers have their own sounds
      (`abl_swell_weighted_swing`, `abl_swell_reel_stop`). The three boss mechanics (`grip_the_stair`, `rope_dive`,
      `hand_closes`) play their skill's own row.
- [x] Quality: loudness and peaks (test_audio_loudness), seams (act1_loop_check), determinism (render_all
      --determinism on every re-render) and transitions: MusicDeck changes land on the beat, every Act I cue has a beat
      grid or is marked "free", and no music fade in the game is under min_fade_sec (test_music_transitions).
- [x] Listening by analysis: `tools/audio/act1_listening_report.py`, report in docs/kb/audio/act1_listening_report.md.
      Revised: corrow_aftermath (the rain under the string) and pilgrims_wake (the low-mids cleared). raid and
      undertows_reach's first stem are noise-led by their briefs and stay as they are.
- [x] 102 Act I cutscene clips that played nothing are heard (28 new foley kinds, `assets_src/sfx/act1_cutscene_foley.py`) or marked silent on purpose.

## Notes
- Work log: docs/kb/handoffs/live/audio.md.

- Git LFS uploads (lfs.github.com) are refused from the cloud environments, so on the Lead's direction the 58 small
  new files ship as plain git (ADR 0174, budget 73 MiB).

## Review log
