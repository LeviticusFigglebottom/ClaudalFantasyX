---
id: M2-FP-28
title: Fixes from the human's playtest of claude/m2-slice (back-to-back battles, the New Game route, the greyscale opening)
role: cinematics
status: doing
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: []
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
The Lead relayed the human's playtest on 2026-10-24 (URGENT, ahead of everything else).

## Acceptance criteria
- [x] **1. Random battles back to back.** Two causes, both in `game/world/zone/field_encounters.gd`:
  - **(a)** After a battle the zone is instanced again, and the first physics frame anchored the walk at the default spawn. `place_at` then jumped Rhen to the return spot, and that jump counted as walking. Now `place_at` re-anchors, and any move over `max_step_m` in one frame is ignored.
  - **(b)** `setup()` reseeded on every instance, so the same first gap came back each time. The meter (walked, next gap, grace and rng state) is now kept per location in `FieldEncounters.meters`; a new or loaded game clears it.
  - **The fix also adds a post-battle `grace_m`.** It and `max_step_m` default to `greybox_defaults.json` `encounters` (12 m and 1.5 m) and can be overridden per layout.
  - **Tests** in `test_zone_story`: battle → return → walk; nothing fires inside the grace; the meter carries on; jumps never count; a new game forgets the meters.
- [x] **2. The New Game route.** `first_playable.json` `prologue.next_location` is back to `ch02/haluna` at `Beach`, the M2 route. Act I's `ch01/oruvel_underway` / `Drop` is the switch the Lead flips together with `end_card.next_location`. Until then, F8 (M3-ARC-02) reaches Ch1.
- [ ] **3. The opening cutscene rendered greyscale.** Under investigation.
- [ ] **4.** Merge big7 (characters, creatures, battle presentation) from the integration branch once it lands.

## Notes

## Review log
