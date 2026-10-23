---
id: M1-ART-05
title: Art sign-off on caustics, dusk halo chroma and noon crests (RND-08 S5)
role: character
status: done
owner_session: "worktree-agent-aac106b1f5eef6855 (Art Director)"
depends_on: [M1-RND-08]
milestone: M1
request-from: "environment"
---
## Goal
From the review-sweep-J entries (file:line references there).

## Acceptance criteria
- [x] Art Director reviews water_*, glimmer_* and haluna_h0* baselines for the new caustics, the dusk halo chroma and the noon SSS crests against palette.json and color_script.md; records approve or the changes needed

## Notes
- 2026-10-23 character (Art Director, worktree-agent-aac106b1f5eef6855): this is a sign-off only, so no code or baselines changed and the task goes straight to **done**. The changes it asks for are in **M1-RND-17** and **M1-RND-18** (rendering, request-from character). Both come back to Art for review. The verdict table and numbers are in docs/kb/art/color_script.md, "Art sign-off 2026-10-23". RND-08 S5 is closed by this sign-off.

## Review log
- 2026-10-23 character (Art Director): **sign-off recorded. 11 baselines approved, 1 baseline and 1 probe view need changes.**
  - **Approve:**
    - `water_shallows` and `water_lagoon` (caustics: curved, uneven web; no far tiling; floor mean no longer darkened);
    - `water_lagoon` and `water_horizon` noon crests from low cameras (pale-turquoise share 29.5 → 12.2 % and 21.9 → 3.0 %);
    - `water_night`;
    - `haluna_h01`, `h02`, `h03`, `h04`, `h07`;
    - `glimmer_night_held` (cyan 217°, low band on the water);
    - `glimmer_release`;
    - `glimmer_bound` (core `#6AA9AB` against `#66A7A6`; still, no trails).
  - **Changes needed:**
    - `glimmer_dusk`: `halo_chroma_gain` 1.6 is not visible. Halos bleach the sky (C 0.029 against a background of 0.043) and shift it toward cyan against peach. The streaks are at a median 37° from vertical, against 20° before RND-08, which reads as sideways. → **M1-RND-17**.
    - The 40 m survey probe at noon: SSS crests still add ΔE_ok > 0.05 over 22.5 % of the deep water. → **M1-RND-18**.
  - **Nit:** the caustic knots are weaker (p95/p50 2.65 → 2.15). Not blocking.

