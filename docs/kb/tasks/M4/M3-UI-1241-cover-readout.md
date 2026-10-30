---
id: M3-UI-1241
title: "Request: show a foe in cover (gliding or buried) on the timeline, in targeting and on stage"
role: ui
status: todo
owner_session: ""
depends_on: [M4-A2P-021]
milestone: M4
request-from: combat
---
## Goal
M4-A2P-021 adds BattleCover (`game/battle/battle_cover.gd`):
- `gallery_ray` (enemies.json `glide`) is out of reach after one of its turns and back down after the next.
- `glass_skate` (`ambush`) is buried from the start until it has acted once.
- A covered foe has `covered == true` and `untargetable == true`, so targeting and the sim already skip it.
- Cover never takes the last foe the party can strike.

**Pillar 4:** the player must see why a foe can't be picked, and when it comes back.

## Acceptance criteria
- [ ] The timeline chip of a covered foe is marked (a glide or buried mark). The entry where it comes up reads from the
      rule: a glider comes down at the end of its next turn; an ambusher comes up at the end of its first.
- [ ] The target cursor shows the covered foe greyed with a short reason (keys of your choosing: "Gliding",
      "Buried") rather than skipping it silently.
- [ ] On stage (battle-presentation): the ray lifts above the water line and the skate shows only a sand ripple.
      Creatures' clips if they exist; otherwise a request to them.

## Review log
