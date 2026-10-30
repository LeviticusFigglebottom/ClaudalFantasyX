---
id: M4-A2P-047
title: "The still mirror and the first ripples: Ansedra's water look"
role: rendering
status: review
owner_session: env-art-b
depends_on: []
reviewer: environment
milestone: M4
request-from: lead
---
## Goal
A still-water mode of the water shader (no waves, an exact reflection) for Ansedra's lagoon and the Sanctum's basin, and a ripple propagation driven by pole strokes and wakes for Ch14's escape ("the first ripple in four hundred years"). The colour script's ch13 mirror check comes with it.

## Acceptance criteria
- [ ] A test scene and shots viewed; perf within the zone budget; the mirror validated in color_script.md.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch13–14. env-art-b holds rendering's zone looks (TRACK-RULES).
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30: started by env-art-b under ADR 0205 (Act II per track once its Act I rows are closed).
- 2026-10-30 (env-art-b):
  - **The still mirror:** Ansedra's `overcast_lagoon` still water (no waves, ripples, foam or glint; roughness 0;
    SSR to 400 m). The Sanctum's basin and the Lacquer Court reuse it.
  - **The ripples:** ring sources in `water_surface_body.gdshaderinc` on their own clock, driven by `RippleField`
    (`strike()`, a wake target). Shots `ch13_ansedra_mirror` and `ch14_ansedra_ripple`; unit test
    `test_ripple_field.gd`.
  - **Wiring into the escape** is chapters' (M4-A2P-104).
  - **For the reviewer (rendering, on the PC):** the SSR reach, the colour script's `ch13 mirror` row, and the rings'
    cost.

## Review log
