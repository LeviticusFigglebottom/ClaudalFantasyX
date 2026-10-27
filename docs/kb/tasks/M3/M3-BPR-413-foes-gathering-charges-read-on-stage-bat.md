---
id: M3-BPR-413
title: "Foes' gathering charges read on stage (BattleTelegraph)"
role: combat
status: review
owner_session: claude/battle-presentation
reviewer: lead
depends_on: []
milestone: M3
request-from: lead
---
## Done (2026-10-27)
- [x] test_battle_telegraph: a regular foe's charge gathers on its contact and each later charge turn; the Drownbell keeps its own; the party none. Hullgnaw, the Matron, the Spar-Wraith, the Tide Crawler and the Reach showed nothing before.
- [ ] Viewed on a PC render (the consolidated battle request).

## Audit and blocked items (2026-10-27 night)
- `test_battle_party_kits.test_every_swell_vowbound_and_enemy_skill_has_a_real_style`: every skill of the 28 enemies
  resolves, through `BattleChoreoPlan.style_id_for`, to a style with a contract clip and camera shots. The same test
  covers every Swell technique and every Vowbound skill.
- **Blocked:** the 6 Act II creatures and bosses have no enemies.json rows yet. The audit covers them once they land.

## Review log
