---
id: M1-RND-12
title: Haluna sky: quality tiers, cubemap update policy, compositing fix
role: rendering
status: review
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-12-sky)"
depends_on: [M1-ENV-01]
milestone: M1
request-from: "rendering"
---
## Goal
From the review-sweep-H entries (file:line references there).

## Acceptance criteria
- [x] Sky quality tiers in graphics_presets.json (march steps, noise octaves), validated; High within budget on the GPU (measure)
- [x] The radiance cubemap does not re-render every frame when the sun or cloud drift animates (time-sliced or thresholded)
- [x] The iteration cap no longer silently cuts off far clouds
- [x] Cloud colour is not multiplied by alpha twice
- [x] The 1.5x visible-sky lift recorded in color_script.md and water.md
- [x] The net material does not become a solid sheet in the far mips
- [x] palette_check: the zenith minimum fraction raised so a mostly grey zenith fails; underside hue sampling restricted to cloud pixels

## Notes (PC GPU session, branch gpu/rnd-12-sky)
Measured on an RX 9070 XT; full report `docs/kb/qa/gpu/2026-10-23-rnd-12-sky.md`.
- Cloud cost was 2.4 ms (Low 1080p) to 3.7 ms (High 1440p) on every preset (projected 8.5–13 ms on the target cards). It is now **0.21–0.24 ms at Low 1080p and 0.39–0.42 ms at High 1440p** (projected 0.9–1.2 ms on a GTX 1060 / RTX 3060). Whole H01 frame at High 1440p: 5.96 → 2.67 ms.
- How: baked lattices (`assets/vfx/sky/cloud_lattice2.png` for the height field, exact to the hash, so the layout is unchanged; the Undertow 3D lattice for erosion) plus the `sky_detail` setting (steps 32/32/40/64, erosion octaves 2/3/4/4, sun-sample erosion 0/0/0/1, cubemap steps 16/24/24/24) and trapezoid integration, which stops the contour bands at 32–40 steps.
- R2: Incremental sky process mode plus a cheap cubemap march. A drifting cloud field used to spike GPU p99 to 11.4 ms; it now costs ≤ 0.45 ms. R3: the remainder is marched instead of cut off. R4: premultiplied over-compositing. R5: color_script.md + water.md. R6: kit_net alpha hash. palette_check: zenith 90 %; underside hue on cloud pixels only (mutation tests).
- Edits on Environment-owned paths (env_sky_cumulus.gdshader, haluna_noon_environment.tres, kit_net via materials.py), routed here by the Lead from review-sweep-H.
- **Drift:** all five `haluna_*` baselines (RMSE 0.022–0.060 on the GPU). Not overwritten; they need a Lead re-capture and AD re-approval. Look at the hashed net in H04 without TAA (fine stipple).
- **Reviewers:** Environment (Rendering ↔ Environment pair, fidelity versus performance) and the Art Director for the new look.

## Review log
