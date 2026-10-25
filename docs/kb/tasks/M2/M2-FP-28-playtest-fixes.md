---
id: M2-FP-28
title: Fixes from the human's playtest of claude/m2-slice (back-to-back battles, the New Game route, the greyscale opening)
role: cinematics
status: review
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
- [x] **3. The opening cutscene rendered greyscale** (9036c019). Nothing was broken or missing; the lighting left every visible face colourless:
  - **The key Sun sits behind the towers** (about 3° high, toward the camera), so every face P01 sees is in shadow.
  - **The towers are near-white,** and those shadowed faces were lit only by a blue-grey fill and ambient.
  - **The colour script's Rim was never built** (`prologue_iskarra_dusk`: #F2A64A at 1.4).
  - **Ruled out:** nothing desaturates (`adjustment_saturation` stays 1.05 for the whole cutscene); a fresh checkout renders pixel-identical; there is no branch drift.
  - **Fix:** the Rim light, plus an ambient tinted toward `deep_teal_shadow` with sky contribution 0.3. Tower saturation goes 0.13 → 0.28, and the whole frame 0.27 → 0.37.
  - **Test:** `test_fp_prologue` `test_the_dusk_frame_carries_colour`.
  - **Still Rendering's:** the real grade (LUT, teal toe) from the colour script.
- [ ] **4.** Merge big7 (characters, creatures, battle presentation) from the integration branch once it lands.

## Notes

## Review log
