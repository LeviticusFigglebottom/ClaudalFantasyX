---
id: M3-BPR-423
title: Boss intros get a hero shot of the boss (Hullgnaw's rail, the Drownbell reading small)
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: [M3-BPR-404]
milestone: M3
reviewer: lead
request-from: lead
---
## Goal
The Lead, 03:41, from the big13 gate shots:
1. In battle_boss_intro_hullgnaw, a rope rail runs across the foreground and cuts the frame in half.
2. In battle_boss_intro_drownbell, the bell reads small.
3. Every Act I boss intro needs a hero shot of the boss, not a wide view of the arena.

## What changed
- New `BattleBossHeroShot` (choreo.json `boss_intro.hero`), tried before the fitted shot (shot id `hero`). A low lens
  on the viewer's side looks up at the boss.
  - The search runs biggest fill first, over each lens (40°, 30°, 24°, 58°, 68°), each angle off the boss-to-party
    line, and each lens height.
  - The boss's top and middle stay inside the safe frame, and its upper body stays clear of the title card. Its feet
    may pass behind the card, as on a poster. The old feet-above-the-card rule is what had shrunk the bosses.
  - **Nothing in front:** each arena mesh's bounds (and each multimesh instance), plus every hero's bounds, are tested
    against sight lines to the boss, and the lens may sit inside none of them.
  - **Party rule:** a hero is off screen, or small and inside the safe frame's top and sides. The command menu is
    hidden through the intro, so a hero may stand at the foot of the frame. A pose with the party in frame is
    preferred.
  - The rule tests each hero's projected rectangle, so a hero filling the lens no longer passes as "off screen".
    `BattleBossIntro._party_clear` still has that corner-only blind spot; the fitted shot keeps using it.
- The Inquisitor's row keeps the fitted shot (`hero: false`): his model hasn't landed, and a hero shot of the capsule
  read worse. Remove it when the model lands.
- Viewed (lavapipe):
  - Hullgnaw arches above the card, Rhen on the deck, no rail.
  - The Drownbell fills the frame.
  - The Matron stands in three-quarter profile with the party at the right.
  - The Hermit is close and low.
  - The Reach towers over a tiny party on the wall-head.
  - The Wraith is centred above the card. It still reads thin and dark: a gaunt model on a night deck.

## Acceptance criteria
- [x] Hullgnaw's intro has no rail across it; the Drownbell dominates its intro.
- [x] Each Act I boss intro with a model is a hero shot (test_battle_boss_intro: its shot, clear of the card,
  nothing in front of the boss, no hero crowding).
- [ ] The Lead's gate re-approves the six moved intro baselines (hullgnaw, matron, hermit, wraith, drownbell, reach).

## Review log
