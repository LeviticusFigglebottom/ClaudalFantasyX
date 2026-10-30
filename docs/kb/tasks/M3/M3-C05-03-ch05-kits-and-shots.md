---
id: M3-C05-03
title: Ch5 kits swap-in (Pemakar terrace stone, Ashcrown) and the P/A shots
role: environment
status: review
owner_session: "env-art-b (claude/env-art-b; Ch5–Ch9 dressing is env-art-b's, Lead 2026-10-28)"
depends_on: [M3-C05-02]
milestone: M3
reviewer: art
request-from: cinematics
---
## Goal
Ch5's two zones are greybox blocks:
- `game/levels/ch05/pemakar/` (Lanternfall night, and a day variant after the binding);
- `game/levels/ch05/ashcrown/` (the pilgrim stair, the four trial tiers, the anvil court).

Their story data doesn't depend on the blocks. Swap in the kits that act1_ch05.md §9 Environment 1–3 asks for:
- **Pemakar terrace stone:** terrace channels with running water, paddies, terrace graves with lacquer shrine-boxes, open-hand gates, the forge lane, the inn on the third tier, and the harbour wake-wall. The hero mesh is the sea-cut weir.
- **Ashcrown:** the outer stair, and four inner tiers with Lit Age copper veins, vein-gates (rotating, pair-linked and plate variants), a copper bowl, a stud ring and a catch-rod per tier, the crown pavilion and catch-spire, the anvil court with its sea-facing arch and Kahre's chamber door, and the quench-trough alcove.
- **The leaf-boat prop:** instanced, with a spent variant and Garo's big badly-folded one.

Write `pemakar.md` and `ashcrown.md` mood briefs with the shot table (P01–P12 plus P06N, P09_garo and P02D; A01–A12).

## Acceptance criteria
- [ ] Both zones play `tests/integration/test_ch05_thread.gd` unchanged.
- [ ] Every spawn, mark, trigger and shot id is kept.
- [ ] The trial's view still finds its pieces: `Bowl_<tier>`, `Stair_<tier>`, the gate blocks named for `ashcrown.json`'s gates, and `QuenchSeal`. Each gate should turn by 90° a step about its own centre.
- [ ] Every route can be walked with the kit's collision. The greybox has no step-up and is flat; the real terraces and tiers need ramps or steps the controller can climb.
- [ ] The night and day light come from the `ch05` frame (and `ch05_harbour_dusk`, `ch05_ashcrown_day` once Art defines them), replacing the layout's stand-in sun and the `variants` row.
- [ ] No rope-burn glow on Kerrid's hands in any frame (ADR 0022 (g)).

## Notes
- The stand-in light for a charged bowl is the layout's `trial_view.charge_color` (white-violet). Lightning VFX is Art's (sheet §9 Art 5): white-violet, never gold, cyan or teal.

- **env-art, 2026-10-27 (the kit side is done; the rest is placement):**
  - **Pemakar:** the Pemakar kit (M3-ENV-03, M3-ENV-1214), with the harbour, the weir, the wake-wall, the crown bell
    and a `day` grade.
  - **Ashcrown:** the Ashcrown kit (M3-ENV-09), with walkable stair variants for the controller (≤ 45°; the flights
    in `ashcrown_flights.json`, M3-ENV-715) and the leaf-boats.
  - **Sheets:** `pemakar.md` and `ashcrown.md`, with their shot tables.
  - **Grades (done, 2026-10-27):** the colour script now has `ch05_harbour_dusk` and `ch05_ashcrown_day`. Each has an
    Environment, a LUT and a sun row in `assets/environments/zones/ch05/ch05_grades.json` (`pemakar_grades.py`), for
    the zones' light rows as Ch6's (`environment_res` and the sun row).
  - **What's left is placement,** which is act1-chapters' (ADR 0200; their Ch5 swap waits on M3-ARC-1216 for the
    steep stair). For the Lead: re-route or close into act1-chapters' swap.

- **env-art-b, 2026-10-29 (placement done; the Lead gave Ch5–Ch9 dressing to env-art-b on 10-28):**
  - **Pemakar:** M3-ENV-1301 (the harbour quay, wake wall, crown bell, the sea-cut weir at the quay's east end),
    M3-ENV-1305 (votive lamps), M3-ENV-1307 (the weir's leat), M3-ENV-1318 (the night plume); the dawn variant takes
    `pemakar_day_environment.tres`. Spawns, marks, triggers and shots kept (`test_ch05_thread`, `--filter=pemakar`).
  - **Ashcrown:** M3-ENV-1303 (the zone in the kit's frame: the causeway and flying stair on HeroStairs, the trial on
    the east ambulatories with its bowls, gates, rods, chains, plates and seal, the anvil court), M3-ENV-1310 (the
    loggia), M3-ENV-1325 (player-height looks: the fill, the metals and lacquer). Walkable: `test_ch05_ashcrown_walkable`.
  - **Arenas:** M3-ENV-1303b (`ashcrown_forecourt_day`, `ashcrown_anvil_court`).
  - **Left elsewhere:** the `ch05_harbour_dusk` light row in Pemakar's flow is act1-chapters' (story flow).

## Review log
