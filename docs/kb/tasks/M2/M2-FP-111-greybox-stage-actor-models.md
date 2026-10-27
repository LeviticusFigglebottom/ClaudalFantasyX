---
id: M2-FP-111
title: "A greybox stage actor can stand as a villager model (Kell in Ch1's Oruvel)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-CHR-03]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
Ch1 to slice quality: every GreyboxZone stage actor was a capsule, unless a hero body attached to it. Kell (Mother
Kell, Ch1's lamp-wright) has had a real villager model since M3-CHR-02, and her `@anim` clips (press_wick,
trim_wicks, take_scissors, light_beacon) are built.

## Acceptance criteria
- [x] GreyboxZone: an actor row's `"model"` instances that actor scene in place of the capsule. It idles from the
  first frame (no T-pose) with HeroIdleMicro breathing. The option is per row, so no other chapter's actors or
  shots change.
- [x] Ch1's Oruvel: Kell wears hers. Request M3-CHR-100 covers the other Oruvel speakers.
- [x] Test: test_ch01_stage_models; ch01 14 and zone 51, 0 failed.

## Notes
- act1-chapters can adopt `"model"` in their layouts when they want (e.g. Tavi in Ch7).

## Review log
