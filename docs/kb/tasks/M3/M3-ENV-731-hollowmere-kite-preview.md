---
id: M3-ENV-731
title: "Hollowmere and the Kite: a preview scene and shots, so the Ch17-18 kits are seen rendered"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-723, M3-ENV-725]
milestone: M3
reviewer: rendering
---
## Goal
TRACK-RULES' backlog, step 4: the "parts look primitive" audit can't see what was never rendered. The Hollowmere
(M3-ENV-723) and Kite (M3-ENV-725) kits had no scene and no shot.

## Acceptance criteria
- [x] `hollowmere_preview.py` writes `game/levels/_tests/hollowmere_kit/hollowmere_preview.tscn`:
  - the ch17 dusk grade and its sun, and the lagoon water;
  - the raft-city round Dace's unfinished hull;
  - the finished Kite moored on its own row at x 70.
- [x] Shots `hollowmere_m01_dace_hull`, `hollowmere_m02_raft_city_dusk` and `kite_k01_moored`.
- [ ] The renders viewed and approved, and anything that reads primitive fixed.

## Notes
- **2026-10-27 (env-art):** built. The preview is a kit preview, not the zone. The zone's layout and staging belong
  to whoever builds Ch17.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log
