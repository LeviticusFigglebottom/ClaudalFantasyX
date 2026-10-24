---
id: M2-RND-08
title: The Low tier's storm (lathe shells) costs more than High's compute body; bring it under
role: rendering
status: review
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: environment
depends_on: [M2-RND-05]
milestone: M2
request-from: "lead"
---
## Goal
From M2-RND-05's findings (docs/kb/qa/gpu/2026-10-24-rnd-05-undertow-events.md). The Low tier's storm costs
1.32–1.65 ms on the RX 9070 XT at 1440p, by `gpu_bench --hide-storms`. That's more than High's compute body
(0.6–0.8 ms), on the tier meant for GTX 1060-class cards.
- **The shells** are full-resolution and alpha-hashed: four overlapping surfaces.
- **They hash their noise:** two 3-octave fBms, 48 PCG3D hashes, where the other tiers fetch the baked lattice.

## Acceptance criteria
- [x] Low's storm costs less than High's on every undertow camera at 1440p, measured by difference.
- [x] Low still reads: silhouette, banding, rents, flashes (`undertow_horizon_low`). List the drift for the Lead.

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
- **The change.** The shells read the baked lattice (new `undertow_lattice.gdshaderinc`, also used by the body's march;
  the compute body is regenerated), and evaluate the wounds only on the wall shells' band. The storm pushes
  `noise_tex` to the shells.
- **Low's storm**, 1440p by difference: Day 1.41 → 0.60, Eye 1.64 → 0.31, Night 1.65 → 0.66, Horizon 1.32 → 0.48 ms.
  That's under High's 0.59–0.83 on every camera. High is unchanged (Day 2.05, Eye 2.25 ms whole frame).
- **Drift** (GPU): `undertow_horizon_low` 0.025, and the Low night view 0.028. The billow layout changes, but the
  silhouette, banding, rents and flashes read the same. Please re-approve `undertow_horizon_low` on lavapipe.
- **Tests.** Godot `undertow` 51/0, plus the tools unittests (the generator's stale-output test).

## Review log
