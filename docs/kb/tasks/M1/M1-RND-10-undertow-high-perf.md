---
id: M1-RND-10
title: Undertow High-tier performance to the SPEC §4.2 budget
role: rendering
status: done
reviewer: environment
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-10-undertow-perf)
depends_on: [M1-RND-03, M1-QA-01]
milestone: M1
request-from: "qa"
---
## Goal
The GPU report (docs/kb/qa/gpu/2026-10-23-gpu-report.md) shows the Undertow at High 1440p taking 25.9 / 28.3 / 35.7 ms (Horizon/Eye/Night) on an RX 9070 XT, about 60-100 ms projected on an RTX 3060 against 16.7 ms.

## Acceptance criteria
- [x] At most 6.0 ms per frame on the 9070 XT, all three cameras, High 1440p (about 16.7 ms projected on a 3060); Medium proportionally cheaper; Low not regressed
- [x] Look preserved (GPU before/after diff stats in the report); drifting lavapipe shots listed for Lead re-approval
- [x] Tier params in data files, validated; tests where practical
- [x] Report docs/kb/qa/gpu/2026-10-23-rnd-10-undertow-perf.md with a per-lever table

## Notes (author, PC GPU session, 2026-10-23)
High 1440p on RX 9070 XT: 25.80 / 28.35 / 35.72 -> **3.95 / 5.35 / 5.04 ms** (Horizon / Eye / Night). Medium 3.6-4.0x cheaper, Ultra 5.9-6.3x, Low unchanged. Levers: baked 3D noise lattice (cloud fields; wounds keep hashing), wounds evaluated only where cloud has density, curl_reuse 2, temporal_jitter + 32 steps. Half-res (a) not needed. Look: same seams, mass and colour; billow layout changed. Re-approve undertow_horizon_dusk / undertow_eye / undertow_night on lavapipe (Lead). Report: docs/kb/qa/gpu/2026-10-23-rnd-10-undertow-perf.md.
Reviewer (Environment, SPEC 12.3 fidelity vs performance): please compare the before/after frames listed in the report and judge whether the new billow layout is acceptable.

## Review log

- 2026-10-23 environment (review-sweep-G): **approve-with-fixes**.
  - **Reproducibility.** I ran `python3 assets_src/vfx/undertow/bake_noise3d.py --out <scratch>`. The decoded pixels are identical to the committed `assets/vfx/undertow/undertow_noise3d.png` (np.array_equal on 512×512×4). The file bytes differ (sha256 93dd907a… vs 795fa5f2…), presumably because the PC and this machine build zlib differently. `test_committed_asset_is_current` compares pixels, which is the right gate.
  - **Provenance and tests.** The PROVENANCE row (PROVENANCE.md:202) and the ownership row are present. The .import is lossless with no mips. Tests: undertow 28 (0 failed) and test_undertow_noise in the 322 tool tests (OK).
  - **Fidelity versus performance (SPEC §12.3).** I compared the lavapipe `undertow_horizon_dusk` baseline before (45fe2a6) and after (d5f62c7) the change. The composition, wound seams, banding, flank masses and silhouette are kept. The billows are a little lumpier and more evenly sized, and the fine wispy edge at the top of the tower is softer. That is acceptable for a 5–7× cost cut, and the rejected 1′ variant (wounds baked) was the right call. The ghosting method and numbers hold up: motion adds no error in the silhouette band.
  - **S1: the tier parameters are data, but only a test validates them.** `curl_reuse`, `temporal_jitter` and `march_steps` are checked by `test_tier_perf_params_parse_and_validate`, not by validate_data.py, which has no undertow schema. At runtime `quality_plan` clamps only the lower bound (undertow_state.gd:261 `maxi(1, …)`), so `curl_reuse` 20 passes into the shader unclamped. Clamp to the shader's range there (or in the shader), or add an append-only undertow quality check to validate_data.
  - **S2: `temporal_jitter` ignores the AA the player actually runs.** `jitter_phase` reads only the tier flag (undertow_state.gd:451-454). High with FXAA or no AA (a settings override) gets the crawling grain that undertow.md lists as a gotcha. Gate the phase on the viewport's real temporal AA (TAA or FSR2) and return 0 otherwise. It is one check, and it turns a documented artefact into a non-issue.
  - Nit: the 3060/1060 figures are still projections, as the report says. Keep it as a top risk in STATUS until someone measures them.
- 2026-10-23 lead: closing on review-sweep-G approve-with-fixes; the runtime upper clamp, validated tier params and jitter without TAA go to the PC session as M1-RND-11.
