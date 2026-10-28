---
id: M3-CHR-540
title: "Request: Ivo Brannick (Ch8-9) as a Stillguard variant with his face uncovered"
role: character
status: todo
owner_session: ""
depends_on: [M3-CHR-507]
milestone: M3
request-from: character
reviewer: rendering
---
## Goal
`ivo` is a capsule in `game/levels/ch08/corrow/corrow.tscn` (inventory). act1_ch08.md B02: Ivo Brannick is a Stillguard,
Toma's shield-mate for seven years: he drops his shield to hug Toma (`@anim ivo hug_lift toma`), kneels to Asha
(`kneel_palms_flat`), stands in the W10 shield-line, and in Ch9 his is the only uncovered face among the shrouds. He needs
the Stillguard kit (red-lacquered shell armour, the shield), which the villager pipeline cannot build, so he belongs with
the Stillguard builds (the stillguard_a/b/c work, another agent's) as a named variant with his own face, no helmet.

## Acceptance criteria
- [ ] A Stillguard build variant `ivo` with his own face and params (thirties, broad, warm), the shield on the left arm.
- [ ] Clips `hug_lift`, `kneel_palms_flat` (shared spec), talk/idle; a lying-in-shroud pose for Ch9 if the Ch9 owner wants one.
- [ ] The usual wiring (job verified on three numpy paths, PROVENANCE, import rule, tests, a stage scene and shots).

## Notes
- Filed 2026-10-28 by chr-npc-wip (the named-NPC pass): not built on the villager pipeline on purpose (no armour there).

## Review log
