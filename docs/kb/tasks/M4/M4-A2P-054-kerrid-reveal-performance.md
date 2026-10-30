---
id: M4-A2P-054
title: "Kerrid's reveal: the rope-burn emission mask and the long-speech facial pass"
role: character
status: review
owner_session: "claude/characters"
depends_on: []
reviewer: cinematics
milestone: M4
request-from: lead
---
## Goal
Kerrid speaks at length once, in Ch15. Add the rope-burn emission mask and sockets for M4-A2P-049, and the facial pass kerrid.md reserves (`grief`, `guilty`; the mouth reading through the beard).

## Acceptance criteria
- [x] Material and face rows; a viewed close-up still of the confession framing.
- [x] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.3. M3-CHR-505 (his model) is in review.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30 (characters, ADR 0205 opened Act II for this track): done.
  - **Emission mask and sockets** were already in the M3-CHR-505 build: the `Burns` shell (material `burn_glow`, mask
    `kerrid_burn_glow.png`, energy 0 by default, so nothing shows in Ch5-Ch9) and 14 sockets (`VFX-burn_{L,R}_1..6`,
    `VFX-palm_{L,R}` after Godot's import rename).
  - **Runtime control:** `KerridBurnGlow.apply(root, glow, lift)` (game/characters/heroes/kerrid_burn_glow.gd) sets a
    per-instance copy of the material; `glow` x `energy_per_unit` 0.8 gives kerrid.md's 0.12 energy at 0.15. `lift`
    lerps `glimmer_held` to `glimmer_lift` for H09; `sockets(root)` hands M4-A2P-049 its emitters. The values are in
    game/data/characters/kerrid_glow.json. Tests: tests/unit/test_kerrid_burn_glow.gd (3/3).
  - **Face rows** `grief` and `guilty` are in kerrid_face_poses.json. The confession stages
    (`kerrid_confession_{grief,guilty}.tscn`: 9,000 K moonlight, burns at the Ch15 peak 0.6) were viewed: the lips
    read clearly through the beard in both, grief with knit brows and a frown, guilty with lowered lids.
    `kerrid_confession_burns` shows the bare right forearm's lit spiral.
  - **Known limits:** at the 0.6 peak the band reads pale cyan-white at distance. On the left arm a thin ring shows at
    the wrap's elbow edge, which reads as one of kerrid.md's "gaps".
  - **Cinematics** sets the per-scene glow by calling `apply`.

## Review log
