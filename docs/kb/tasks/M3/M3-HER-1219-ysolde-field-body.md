---
id: M3-HER-1219
title: A field body for Ysolde (her stage actors and her follower are capsules in Act I)
role: architect
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
`game/data/hero_motion/hero_motion.json` `field.heroes` gives Rhen, Asha and Toma a field body, so
`HeroFieldActor.attach_stage` turns their capsules on every zone's stage into them. Ysolde joins in Ch4 and is on
stage in every Act I chapter after it (ysolde, ysolde_edge, vigil_ysolde, ...), and her glb exists
(`assets/characters/ysolde/ysolde_lod1.glb`), but she has no row, so she stays a capsule (and her follower too).
Add her row (and her gait clips if the field needs them).

## Acceptance criteria
- [ ] Ysolde's stage actors and follower show her model in the Act I zones.

## Review log
