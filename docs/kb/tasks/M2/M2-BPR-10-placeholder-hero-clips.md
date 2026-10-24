---
id: M2-BPR-10
title: Placeholder hero battle clip poses through the clip contract (until M2-CHR-07 lands)
role: combat
reviewer: character
status: review
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-02]
milestone: M2
request-from: lead
---
## Goal
The heroes' battle actors (M2-UI-07, characters' asha/rhen/toma battle scenes) have a skeleton but not yet the battle
clip set (M2-CHR-07, in progress). So the choreography reads on them now, a hero actor that lacks a contract clip
gets a simple placeholder pose clip, generated at runtime on its skeleton's main bones from data. A real clip with
the same name always wins, so M2-CHR-07 replaces them without a code change.

## Acceptance criteria
- [x] Placeholder clips per contract name (bone rotations in data, keyed by the MPFB2 rig's bone names)
- [x] Only for actors with a Skeleton3D and missing clips; real clips win; primitives keep the procedural root motion
- [x] Tests on a synthetic skeleton

## Notes
- 2026-10-24 combat (battle-presentation): `BattlePlaceholderClips` (game/battle/scene/battle_placeholder_clips.gd),
  hooked in `BattleClips.player_of` (first sight of a model's player; no change to battle_controller.gd). Data:
  `choreo.json` `placeholder_clips` (roles -> MPFB2 bone names with alternatives, `min_roles`, a standing `base`,
  12 clips of keyed poses in hero_clips.py's convention: model-axis turns on top of the inherited rotation, YXZ).
  The clips go into the player's own copy of its default library, only for missing names, so M2-CHR-07's real clips
  win. Creature actors and non-humanoid skeletons get nothing. Also: a hero model's `ko` clip now plays on the
  collapse beat (`BattleClips.play_ko`; before, nothing played it) and a revive idles again (`ko_changed`).
  Validation in tools/validate_choreo.py (`placeholder_errors`). Docs: battle_presentation.md "Placeholder clips".
- **For the character reviewer:** the pose angles were written against hero_clips.py's axis convention and the
  rest read from asha_clips.tres, but not yet seen on a real hero (the battle actors are not on this branch). Please
  check the reads on asha/rhen/toma once claude/characters + M2-UI-07 meet this branch, and tune the numbers in
  choreo.json (no code change). Bones not in the role list (spine.002, twist segments, shoulders) keep idle's pose.

## Review log
