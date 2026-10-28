---
id: M3-HER-1219
title: A field body for Ysolde (her stage actors and her follower are capsules in Act I)
role: architect
status: review
owner_session: "integration-qa (hero-integration track, architect role per the Lead 2026-10-28)"
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
- [x] Ysolde's stage actors and follower show her model in the Act I zones.

## Done
Ysolde's row was already in `game/data/hero_motion/hero_motion.json` `field.heroes` (ysolde_lod1). Her stage actors
(ysolde, ysolde_edge via `actor_aliases`, vigil_ysolde via the `vigil_` prefix) and her follower take her model. The
runtime audit after the 15:50 trial merge, with variants and states scanned, lists no Ysolde capsule anywhere in
Act I.

## Review log
- 2026-10-28 act1-chapters (requester): her row is in `field.heroes` on the integration branch; her stage actors show
  her body in Ch6's shot rig (ysolde: HeroBody). Ch9's `vigil_ysolde` now casts `hero:ysolde`. The criterion holds.
