---
id: M3-ENV-730
title: "Oruvel rebuilt (E7, post_credits): the rebuilt raft and the first lamp post"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-729]
milestone: M3
reviewer: rendering
---
## Goal
The post-credits scene (act3_ending E7) is Oruvel rebuilt at blue hour, with one new oil lamp lit from Mother Kell's
wick. oruvel.md §7 left the rebuilt variant as a follow-up.

## Acceptance criteria
- [x] `ov_rebuilt.py`: `raft_deck_rebuilt` (new hulls, new planks among the old) and `lamp_post` (the first lamp),
  plus the `ov_timber_new` material. Every existing Oruvel glb and material is byte-identical.
- [x] The Oruvel layout's `states.rebuilt` (hide, pieces, `first_lamp`); the day and storm states are unchanged.
- [x] oruvel.md §7 and ending.md §3; test_oruvel_kit covers the new pieces (budgets, slots, the layout).
- [ ] Rendering: E7's mood frame once Cinematics stages it (a preview phase for `rebuilt` would need a shot).

## Notes
- **2026-10-27 (env-art):** built.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log
