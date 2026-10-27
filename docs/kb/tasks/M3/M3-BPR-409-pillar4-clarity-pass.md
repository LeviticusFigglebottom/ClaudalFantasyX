---
id: M3-BPR-409
title: "Pillar 4 clarity pass: who acts next through cinematics, the target under VFX, reduced shake and flash"
role: combat
status: review
owner_session: claude/battle-presentation
reviewer: lead
depends_on: [M3-BPR-401]
milestone: M3
request-from: lead
---
## Goal
The player always knows who acts next and what an action costs (Pillar 4), including while a cinematic or heavy VFX
plays.

## Done (2026-10-27)
- [x] **Turn order through cinematics:**
  - the boss intro hides only the command menu, the target cursor and the help line;
  - the timeline and the party panel stay on screen (test_battle_clarity);
  - the C10 summon cinematic never hides the timeline.
- [x] **The target under heavy VFX:**
  - the ground ring now draws after other transparent effects (battle_sandbox.json `ring.render_priority` 10), so
    smoke, splashes and the flood no longer sort over it;
  - solid bodies still occlude it;
  - the 2D target cursor is UI and always on top.
- [x] **Reduced motion and the shake setting, for every new impact:**
  - the hit-stop shake obeys the Screen shake setting;
  - Reduced motion drops every shake, the withdrawal's backing-away, the Breach push-in and the boss-intro camera,
    and dims the impact flash (tests in test_battle_impact, test_battle_set_piece_stage, test_battle_boss_intro);
  - BattleImpact never flashes the screen.
- [ ] View the ring over the toll's wave and the flood on the PC renders (battle_choreo_toll, drownbell_flood): see the
      render request in the live log.

## Review log
