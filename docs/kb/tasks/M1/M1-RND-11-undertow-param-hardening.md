---
id: M1-RND-11
title: Undertow tier-param hardening (review-sweep-G on RND-10)
role: rendering
status: review
reviewer: environment
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-11-undertow-params)
depends_on: [M1-RND-10]
milestone: M1
request-from: "environment"
---
## Acceptance criteria
- [x] Tier params (march_steps, curl_reuse, temporal_jitter, noise) validated by validate_data, not only by a test
- [x] The runtime clamps upper bounds as well as lower (undertow_state.gd ~:261)
- [x] temporal_jitter is off when the active AA mode has no temporal accumulation (undertow_state.gd ~:451); test
- [x] The dither pattern in the day-shot glow reduced, or documented as integrating under TAA

## Notes
- 2026-10-23 PC GPU session: all four done; report docs/kb/qa/gpu/2026-10-23-rnd-11.md. The dither integrates under native TAA (-85%), only partly under FSR2 (-36%, no reactive mask in Godot 4.6); documented with a cutscene mitigation.

## Review log
