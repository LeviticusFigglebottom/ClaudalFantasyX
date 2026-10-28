---
id: M3-CRE-625
title: "Request: a battle model for Inquisitor Hadric Moll (stillguard_inquisitor), the last foe still drawn as a capsule"
role: character
status: todo
owner_session: ""
reviewer: art
depends_on: []
milestone: M3
request-from: creatures
---
## Goal
The PC gate's `battle_arena_camp` shot shows a white capsule beside the raid hound in `ch06_inquisitor` ("Inquisitor
Moll · The Hound's Watch"). That capsule is `stillguard_inquisitor`: the only enemies.json foe on any branch
(integration, act1-chapters, m2-slice, battle-presentation, characters) with no `model`. Summoned foes and set-piece
entries are clean (2026-10-27 sweep, creatures live log). He is a person, so the characters track builds him
(M3-C06-06 item 3 describes him: forties, red-lacquered shell armour, the Inquisitor's white sash, a round shield,
a long-hafted brine-iron held upright like a standard).

## Acceptance criteria (characters)
- [ ] A skinned GLB from source (the villager or base-body pipeline), with the battle clips `idle`, `attack`
      (the brine-iron, with a contact time), `cast` (the shield raised: Challenge), `hit` (peak near 0.1 s, M3-CRE-617)
      and `ko`. He **yields** at 0 HP rather than dying (`yield_at_hp_pct` 0): the `ko` clip is a kneel, the iron
      laid down flat, the shield set aside, never a fall.
- [ ] Hand the GLB to creatures. Creatures wires the battle side: a CreatureActor scene
      `game/creatures/stillguard_inquisitor/` (or reuse of the hero battle actor if characters prefers), a
      creatures.json row (contact times, portrait, rim), and the enemies.json `model` line (or m2-slice/act1-chapters
      adds that line, as with the Act I creatures).
- [ ] A PC render of `battle_arena_camp` and `battle_boss_intro_inquisitor`, viewed and approved.

## Notes
- Until the model lands the capsule stays (it is the stand-in spec in battle_sandbox.json).

## Review log
- 2026-10-28, creatures: the ADR 0041 inventory (M3-HER-1142) also lists the **field** stand-in `inquisitor` in Brine Shoals (brine_shoals_layout.json `actors.inquisitor`). Same person, same body: once Moll has an actor scene, act1-chapters adds `"model"` to that row as for Kell (M2-FP-111).
