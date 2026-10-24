---
id: M3-C05-07
title: Show the Cinder Matron's Crust when she re-crusts (a battle-presentation hook, not a phase)
role: ui
status: doing
owner_session: "claude/ui"
depends_on: [M3-C05-02]
milestone: M3
request-from: cinematics
---
## Goal
For the battle-presentation track. Creatures' `cinder_matron` model hides its "Crust" when she enters phase `pour` (the crust breaks, and the plates beneath glow red-hot). In play, the crust comes back without a phase change, through two engine events (`game/battle/boss_mechanics.gd`):
1. **Her `recrust` skill resolves.** She telegraphs `recrust_gather` two turns ahead; `recrust` cleanses `armor_break` and adds `protect`.
2. **A reaction:** a water or ice hit lands on her during `pour` (enemies.json `reactions`). The hit result records `"reacted": true`, cleanses `armor_break`, and adds `protect` and `shell`.

Show the Crust on either event, and hide it again when Kerrid's `armor_break` lands. Creatures' model already supports `show: ["Crust"]`; this needs the presentation side to call it on those events.

## Acceptance criteria
- [ ] The Crust shows on `recrust` resolving and on a `reacted` hit, and hides on `armor_break` landing. A battle-scene test covers each.

## Notes

## Review log
