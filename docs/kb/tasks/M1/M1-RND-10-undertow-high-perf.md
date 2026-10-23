---
id: M1-RND-10
title: Undertow High-tier performance to the SPEC §4.2 budget
role: rendering
status: doing
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-10-undertow-perf)
depends_on: [M1-RND-03, M1-QA-01]
milestone: M1
request-from: "qa"
---
## Goal
The GPU report (docs/kb/qa/gpu/2026-10-23-gpu-report.md) shows the Undertow at High 1440p taking 25.9 / 28.3 / 35.7 ms (Horizon/Eye/Night) on an RX 9070 XT, about 60-100 ms projected on an RTX 3060 against 16.7 ms.

## Acceptance criteria
- [ ] At most 6.0 ms per frame on the 9070 XT, all three cameras, High 1440p (about 16.7 ms projected on a 3060); Medium proportionally cheaper; Low not regressed
- [ ] Look preserved (GPU before/after diff stats in the report); drifting lavapipe shots listed for Lead re-approval
- [ ] Tier params in data files, validated; tests where practical
- [ ] Report docs/kb/qa/gpu/2026-10-23-rnd-10-undertow-perf.md with a per-lever table

## Review log
