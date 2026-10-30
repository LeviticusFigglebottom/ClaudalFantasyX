---
id: M3-BPR-441
title: "Request: relight a mended part on stage (BattleEngine.part_restored), and give the crawler's mend its shot"
role: combat
status: todo
owner_session: ""
depends_on: [M4-A2P-022]
milestone: M4
request-from: cinematics
---
## Goal
To battle-presentation. M4-A2P-022 makes a broken part stay broken in the engine (BattleParts):
- An enemy row's `parts` names charge skills. Breaking that charge on the weak point keeps the part in
  `broken_parts`, and its gather is off the AI's menu.
- A `restores_part` skill (the conduit crawler's `crawler_mend`) mends the oldest broken part. The hit carries
  `part_restored` and the engine emits `part_restored(enemy, skill_id)`. The skill id is the same key
  creatures.json `break_parts` uses.

Today `battle_actor_motion.gd` shows a part whole again only on `charge_started`. A broken part can no longer start
its charge, so the ring would stay dark after a mend.

## Acceptance criteria
- [ ] `part_restored` sets the part whole (`set_part_broken(skill_id, false)`), in the beat of the mend's contact.
- [ ] The lamp_engine.md §6 `actor` shot on the crawler while it mends ("so the player sees why the ring relit").
- [ ] A test that a `part_restored` signal relights the part on a stand-in.

## Review log
