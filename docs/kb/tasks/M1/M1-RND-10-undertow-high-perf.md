---
id: M1-RND-10
title: Undertow High-tier performance to the SPEC §4.2 budget
role: rendering
status: review
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
