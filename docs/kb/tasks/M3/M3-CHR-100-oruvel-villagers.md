---
id: M3-CHR-100
title: "Oruvel's named villagers for Ch1's stage: the scaleman, the cook, Sabe, Skipper Sadi, the children"
role: character
status: todo
owner_session: ""
depends_on: [M2-CHR-03]
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
M2-FP-111 lets a greybox stage actor stand as a villager actor (`"model"` on its layout row; Kell in Oruvel is the
first). Ch1's other Oruvel speakers are still capsules in `game/levels/ch01/oruvel/oruvel_layout.json`:
- `scaleman`, `cook`, `sabe` and `skipper_sadi`;
- the children `roof_child`, `pen_child`, `pen_child_2` and `pen_child_3`.

Haluna's M2-CHR-03 villagers must not stand in for them: Oruvel is a different town, and Ch2 meets those faces.

## Acceptance criteria
- [ ] Villager-path actors (pipeline.md §15) with `idle` and `talk` (and `walk` where the scene moves them) under
  `assets/characters/villagers/<id>/<id>_actor.tscn`, plus PROVENANCE rows. Two child variants are enough for
  the four children.
- [ ] Tell cinematics (slice-polish): it adds `"model"` to those rows.

## Review log
