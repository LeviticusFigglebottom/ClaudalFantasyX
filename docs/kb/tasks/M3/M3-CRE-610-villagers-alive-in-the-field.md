---
id: M3-CRE-610
title: "Haluna's villagers alive in the field: idle loops, talk gestures, eased turn-to-face, ambient walk routes"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CHR-03]
milestone: M3
request-from: lead
---
## Goal
The human's playtest note ("parts look primitive / placeholder"): villagers stand static or as stand-ins. Give the
villager actors (claude/characters' M2-CHR-03 models, idle/talk/walk clips) a field behaviour layer: idle loops
offset per villager, a talk gesture when spoken to, an eased turn to face the player (never snapping; reuse
hero-integration's HeroLocomotion turn and HeroIdleMicro, not a copy) and short ambient walk routes.

## Acceptance criteria
- [x] FieldNpc (game/world/npc/): idle, talk-on-interact, eased face-the-player and back, walk routes with pauses
- [x] Data-driven tuning (game/data/world/npc/), tests, a review scene and shot
- [x] Handed to m2-slice (who places villagers in the zones) with a one-node integration note
  (docs/kb/tech/field_npc.md; placing them in Haluna is m2-slice's, the zone was not touched)

## Notes
- Depends on hero-integration's game/hero_motion reaching the integration branch; built against it locally and
  landed after it merges.
- Built (worktree agent-a8078f4bd9ab409ea on a local merge of origin/claude/hero-integration, which is not
  part of this task's commits): `FieldNpc` (game/world/npc/field_npc.gd) reuses HeroLocomotion (`step_yaw`,
  `step_speed`, `weights`, configured from hero_motion.json with npc.json's `locomotion` merged over it)
  and HeroMotion (`play`, `add_micro_motion` -> HeroIdleMicro, `set_locomotion_speed`). Nothing under
  game/hero_motion/** was changed.
- Idle phase = HeroIdleMicro.share(npc_id, "idle_clip") x clip length; the idle always resumes at phase +
  clock. Talk ends on end_talk(), on DialogueRunner.finished via follow_dialogue(runner) (no bus signal for
  "dialogue finished" exists; FieldEvents has none), or when the player passes release_radius_m.
- All seven villagers (child, fisher, neme, netmender, osu, reed, vendor) have idle (6.0 s), talk (3.2 s)
  and walk (1.1 s), all looping, and a 75-bone DEF-* skeleton, so HeroIdleMicro applies. walk_clip_mps 0.66
  (adult) / 0.46 (child), measured from foot travel in the walk clip.
- Review: game/levels/_tests/npc/npc_stage.tscn, shot `npc_stage_field` (150 fixed frames; a re-render
  matches the baseline at RMSE 0). Tests: tests/unit/test_field_npc.gd (10).

## Review log
