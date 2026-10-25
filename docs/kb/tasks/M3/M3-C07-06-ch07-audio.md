---
id: M3-C07-06
title: "Ch7 music cues and SFX (the Tidecup)"
role: audio
status: todo
owner_session: ""
depends_on: [M3-C07-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch7's scripts (M3-C07-02, `game/data/dialogue/ch07/`) name these cues and sounds. None exist yet, so the chapter plays silent. Brief: act1_ch07.md §6.

## Acceptance criteria
- [ ] **Music:**
  - `tamsule_port`, with an afternoon variant;
  - `tavi_kell`, solo piano entering after "She couldn't swim, Tavi.", quoting two notes of `oruvel_theme`;
  - `tidecup_crowd`;
  - `tidecup_after`;
  - the `oruvel_theme` reprise on one flute, over `bell_hum`;
  - `reefball_match` belongs to the Reefball agent.
- [ ] **SFX:**
  - `column_weep`;
  - `crowd_up` (the naming's answer, low and together, plus a cheering variant);
  - `crowd_warm`;
  - `bell_hum_rise` (B04: the `bell_hum` layer rising under Asha's close-up; the same family as the bound element of `shell_shrine_interior`);
  - `mooring_ring` (iron, touched);
  - `bell_crowd_roar` (B10);
  - `float_ring_bell` (the match's).
- [ ] **True silence at the naming.** B05 fades the bed with `@music silence fade=3.0` and leaves only the column's weep.

## Review log
