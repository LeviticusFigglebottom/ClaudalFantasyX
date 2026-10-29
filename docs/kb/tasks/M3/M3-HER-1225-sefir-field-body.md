---
id: M3-HER-1225
title: "Request: a field body for Sefir (his stage actor is a capsule in Ch6's cutscenes)"
role: architect
status: review
owner_session: "integration-qa (hero-integration track, architect role per the Lead 2026-10-28)"
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
- [x] `ZoneCast` `hero:sefir` (or the actor's own id) shows his body; act1-chapters adds the cast to the Ch6 layout and
      any later Act I stage he stands on.

## Done
- Sefir's row in `field.heroes` (sefir_lod1). He has no stepping walk, only `walk_glide`, so a hero row can now name
  its own locomotion clips (`clips`: walk and run → walk_glide, 0.21 m/s measured by HeroClipGait).
- `HeroFieldActor.locomotion_clips()` / `clips_of(id)` read the field's clips under the row's. The clip-speed test
  measures each hero's own clips.
- test_hero_field_actor::test_sefir_s_stage_actor_takes_his_body_and_glides: his stage actor hides its capsule, his
  tree has his glide, and a walk moves him. hero_field_actor 15/0, hero_ 110/0.
- The audit now scans layout states too (tools/placeholder/scan.gd `_scan_states`). With Ch6's
  `ch06_inquisitor_yielded` set, Sefir stands on the reed bank with his body: no capsule.
- Left to act1-chapters: the ZoneCast line in later Act I stages he stands on, if any.

## Review log
