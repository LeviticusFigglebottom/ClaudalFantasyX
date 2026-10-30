---
id: M4-A2P-1401
title: "Ch4 beauty pass (the Haluna wake, the Brightwater ferry) and the Prologue-to-Ch4 arrivals as played (the Lead, 10-30)"
role: environment
status: review
owner_session: "claude/env-art"
depends_on: []
reviewer: art
milestone: M4
request-from: lead
---
## Goal
The same eye-height beauty pass as M4-A2P-1400, for Ch4. Then the Prologue-to-Ch4 transitions as played: the frame the
player sees on arriving at each hand-off's spawn.

## Acceptance criteria
- [x] Eye-height stills along the walkthrough's legs viewed: ch04_wake (18) and ch04_ferry (18).
- [x] An arrival still (tools/hero/walk_stills, the real camera and party) viewed at each spawn: Drop, Surface,
      Beach, FromHaluna, Entry, NemeDoor, DockShore and Landing.
- [x] Env-art's defects fixed; other tracks' noted for the Lead.

## Notes
- **Fixed:**
  - The Seventh Terrace's galley: its glossy black lacquer boards caught the night sky as one bright streak per board
    indoors. The walls now use `bf_lacquer_black_satin` (7d2197e6).
  - The Landing arrival was a black rock under the cold fill alone. A ferry lantern is set down at the gangplank's
    head and casts one warm key light (`tools/act1/ch04_ferry_dressing.py` `landing_lantern`).
- **For the Lead (not env-art's to change):**
  - **Haluna wake:** the night shallows by the dock glow bright day-cyan. `haluna_mood.gd` gates the night sea-glow
    with the held glimmer, so this may be intended; keep it or calm it?
  - **DockShore arrival:** the camera sits behind Rhen's head, so he fills the frame (camera).
  - **Shell Shrine Entry arrival:** Asha and Toma stand stacked into Rhen (party spawn spots).
- **Arrived cleanly:** Drop, Surface, Beach, FromHaluna and NemeDoor.

## Review log
