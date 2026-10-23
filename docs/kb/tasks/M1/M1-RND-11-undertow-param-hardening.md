---
id: M1-RND-11
title: Undertow tier-param hardening (review-sweep-G on RND-10)
role: rendering
status: todo
owner_session: ""
depends_on: [M1-RND-10]
milestone: M1
request-from: "environment"
---
## Acceptance criteria
- [ ] Tier params (march_steps, curl_reuse, temporal_jitter, noise) validated by validate_data, not only by a test
- [ ] The runtime clamps upper bounds as well as lower (undertow_state.gd ~:261)
- [ ] temporal_jitter is off when the active AA mode has no temporal accumulation (undertow_state.gd ~:451); test
- [ ] The dither pattern in the day-shot glow reduced, or documented as integrating under TAA

## Review log
