---
id: M3-HER-1225
title: "Request: a field body for Sefir (his stage actor is a capsule in Ch6's cutscenes)"
role: architect
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
ADR 0041: Sefir's model and clips exist (`assets/characters/sefir/sefir_lod1.glb`, M3-CHR-02; the slow blink is
M3-CIN-01), but no field row reaches them, so his stage actor (`sefir` in `ch06/brine_shoals`, on the reed bank in Ch6's
cutscenes) is still a capsule. Like M3-HER-1219 for Ysolde: a row that `HeroFieldActor.attach_actor` can load (in
`field.heroes`, or an NPC table if Sefir should not count as a party hero for `leader_id()`), with his deliberately
still idle.

## Acceptance criteria
- [ ] `ZoneCast` `hero:sefir` (or the actor's own id) shows his body; act1-chapters adds the cast to the Ch6 layout and
      any later Act I stage he stands on.

## Review log
