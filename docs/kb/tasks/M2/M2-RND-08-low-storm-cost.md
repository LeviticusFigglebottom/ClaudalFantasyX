---
id: M2-RND-08
title: The Low tier's storm (lathe shells) costs more than High's compute body; bring it under
role: rendering
status: doing
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
- [ ] Low's storm costs less than High's on every undertow camera at 1440p, measured by difference.
- [ ] Low still reads: silhouette, banding, rents, flashes (`undertow_horizon_low`). List the drift for the Lead.

## Review log
