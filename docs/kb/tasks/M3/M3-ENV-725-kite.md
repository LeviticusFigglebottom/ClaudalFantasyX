---
id: M3-ENV-725
title: "The Kite (Ch18 hub, the Ending's stage): sheet and kit"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-723]
milestone: M3
reviewer: story
---
## Goal
The Lead's queue item 4 (the later zones): the Kite, Ch18's hub and the Ending's stage. Nothing had designed it
yet. It is built on Dace's hull from Ch17 (`dace_hull_frame`), with a rig after Virel and bound-light lift engines
that go dark at H09.

## Acceptance criteria
- [x] The design sheet: `docs/kb/art/environments/kite.md`.
- [x] The kit, `kite.py`: `kite_hull`, `kite_rig` and `kite_engine`.
- [x] Tests: `tools/tests/test_kite.py` (4).
- [ ] Story review: does the look match Ch18, H09 and E4?

## Notes
- **2026-10-27 (env-art):** built. The engine core and the lanterns share `kit_bound_core`, so at H09 Cinematics
  darkens every bound light with one material swap. There is no shot yet: the hub zone places it.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log
