---
id: M4-A2P-104
title: "Ch14's escape: drive the ripples, and the court's after-the-trap state (layout blocks for env-art-b)"
role: cinematics
status: review
owner_session: act1-chapters
depends_on: [M4-A2P-047]
reviewer: environment
milestone: M4
request-from: environment
---
## Goal
env-art-b has built the first ripples (M4-A2P-047) and dressed the Lacquer Court (M4-A2P-044). Two things are the
chapter's to wire, because they belong to its flow and its layout (`tools/act1/ch14_greybox.py`):

1. **The ripples in the escape.** Ansedra (`ch13/ansedra`) and the court (`ch13/ansedra_lacquer_court`) each carry a
   `Ripples` node (`RippleField`, `game/world/water/ripple_field.gd`). On the escape beat:
   - set `wake_target` to the moving barge's node, so it drops a ring every 1.5 m;
   - call `strike(at)` at each pole stroke.

   `RippleField.find(get_tree())` returns the zone's field. Until the escape, the lagoon is a perfect mirror.
2. **The court after the trap** (ch14_lacquer_court.md, "After the trap"). The layout needs two blocks:
   - `CeremonyLamps`, shown at the wedding;
   - `CeremonyLampsFallen`, hidden until the trap.

   It also needs a `states` row (or a `variants` row) that swaps them when the trap springs. env-art-b then binds the
   eight `gilt_lamp_stand`s and their lights to `CeremonyLamps`, and places fallen stands, unlit, on
   `CeremonyLampsFallen`.

## Acceptance criteria
- [ ] The escape drives the field (a wake behind the barge, a ring per pole stroke).
- [ ] The two blocks and the state row are in the court's layout; env-art-b is told, so it can bind the stands.

## Notes
- The shot `ch14_ansedra_ripple` shows the look (rings breaking the Sanctum dome's reflection).

- **act1-chapters, 2026-10-30:**
  - **Part 2, done:**
    - The court's layout has the anchors `CeremonyLamps` and `CeremonyLampsFallen` (no mesh, no collision).
    - Two `variants` rows: before `ch14_declared_heretics`, the fallen set is hidden. After it (the trap), the
      wedding set hides and the fallen one shows.
    - **env-art-b:** bind the eight `gilt_lamp_stand`s and their lights to `CeremonyLamps`, and the fallen, unlit
      stands to `CeremonyLampsFallen`.
  - **Part 1, open:** driving the ripples (the barge's `wake_target`, a `strike` per pole stroke) needs the escape
    scene and its moving barge. That waits on story's Ch14 scenes (M4-C14-01); the escape beat today is only the
    `go`.
  - **Part 1, done (later the same day):** `ch14_first_ripple` cues each of Merel's strokes as `@sfx pole_stroke`.
    `Ch13Zone` listens to its sequencer's `cue_played`, so each stroke strikes a ring from the barge's stern
    (`BargeStern`) through `RippleField.find`. The barge is a greybox block that doesn't travel, so there is no
    `wake_target` yet: when env-art-b's barge moves in the scene, set `wake_target` to it in the court's scene (one
    export) and the wake follows. Test: `test_ch13_thread.gd::test_a_pole_stroke_ripples_the_lagoon`.

## Review log
