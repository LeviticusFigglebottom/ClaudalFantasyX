---
id: M3-C07-06
title: "Ch7 music cues and SFX (the Tidecup)"
role: audio
status: review
reviewer: cinematics
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
depends_on: [M3-C07-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch7's scripts (M3-C07-02, `game/data/dialogue/ch07/`) name these cues and sounds. None exist yet, so the chapter plays silent. Brief: act1_ch07.md §6.

## Acceptance criteria
- [ ] **Music:** (all but the afternoon variant: see Notes)
  - `tamsule_port`, with an afternoon variant;
  - `tavi_kell`, solo piano entering after "She couldn't swim, Tavi.", quoting two notes of `oruvel_theme`;
  - `tidecup_crowd`;
  - `tidecup_after`;
  - the `oruvel_theme` reprise on one flute, over `bell_hum`;
  - `reefball_match` belongs to the Reefball agent.
- [x] **SFX:**
  - `column_weep`;
  - `crowd_up` (the naming's answer, low and together, plus a cheering variant);
  - `crowd_warm`;
  - `bell_hum_rise` (B04: the `bell_hum` layer rising under Asha's close-up; the same family as the bound element of `shell_shrine_interior`);
  - `mooring_ring` (iron, touched);
  - `bell_crowd_roar` (B10);
  - `float_ring_bell` (the match's).
- [x] **True silence at the naming.** B05 fades the bed with `@music silence fade=3.0` and leaves only the column's weep.

## Notes
- All Ch7 cues delivered (M3-AUD-12, M3-AUD-820, M3-AUD-17): `tamsule_port` (as `tamsule`), `tavi_kell`, `tidecup_crowd`, `tidecup_after`, the `oruvel_theme` reprise; the SFX are files under sfx_dir; `float_ring_bell` is the match's (sfx/reefball, ReefballAudio). The afternoon variant is not made (no time-of-day switch).
- Checked 2026-10-27 (M3-AUD-833's resolution test and the thread runs): `--filter=_thread` (Ch1-Ch9, 34 tests) passes with no "no music" or "no sound" warning from any scene; the only sequencer warnings are other kwargs' placeholders (`@vfx drift=`, `@camera grade=`, `@sfx at=`).

## Review log
