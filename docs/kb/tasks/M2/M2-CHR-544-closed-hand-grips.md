---
id: M2-CHR-544
title: "Real closed-hand grips on the held props (the PC's M1-QA-09 on big15: open hands)"
role: character
status: review
owner_session: "characters (claude/characters, worktree drape-wt)"
depends_on: [M2-CHR-515]
milestone: M2
reviewer: rendering
---
## Goal
The Lead, relaying the PC's M1-QA-09 on big15: Asha's staff and Toma's spear aren't gripped (open hands in run,
walk_cycle and offer_hand). Close the hands round the props in every clip.

## Acceptance criteria
- [x] The cause was that the GLBs build the shaft through the open rest hand's fingers (joints 6–36 mm from a 19.6 mm
      shaft's axis), so no curl could wrap it. Now the fingers close to a fist, and the prop's bone moves in the hand's
      frame so its shaft runs through the fist's hole (Asha 13 mm, Toma 24 mm).
- [x] Each finger joint is solved on its own, kept level with its knuckle, and the thumb's search is wider.
- [x] The offset is in every clip's prop keys, in `grips.json` for the stages (HeroHelperBones), and in rig_probe.
- [x] Covers Asha, Toma, Moll and Stillguard A–F; Rhen's hooks get the per-joint solve.
- [x] Rig probe clean for all of them, and the hero and Godot tests pass. Self-rendered at 1920×1080 and viewed zoomed.

## Notes
- Merged @ 9e9b8aa2. Asha's grip is looser than Toma's: on her smaller hand the index and ring tips sit about 38 mm
  from the axis.

## Review log
