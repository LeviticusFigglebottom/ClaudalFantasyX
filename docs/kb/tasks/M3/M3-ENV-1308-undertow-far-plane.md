---
id: M3-ENV-1308
title: The Undertow in Ch8's zones was clipped by the camera far plane (4 km), so make the dressing reach past it
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: [M3-ENV-1302]
milestone: M3
reviewer: rendering
---
## Goal
The `storms` rows (M3-ENV-1302) place Rendering's UndertowStorm 10–14 km out (undertow.json `ch08_seawall`,
`ch08_landfall`). A Camera3D's default far plane is 4 km, and neither the field camera nor the cutscene and shot
cameras raise it. So the storm's body never drew: Coilspire's gallery saw an empty sea, and Corrow got the rain and
shadow without the wall.

## Notes (2026-10-28, env-art-b)
- `ZoneKitDressing._keep_storms_in_view()` raises the current camera's `far` past every shown storm (distance plus
  bound plus 2 km) each frame. New test in `tests/unit/test_zone_kit_waters.gd`; `--filter=zone_kit` 11/0.
- Self-rendered ch08_coilspire_storm and ch08_corrow_storm: the storm wall and its lit eye now stand on the sea.
- For Rendering: any other scene that places an UndertowStorm under a default camera has the same clipping. Your test
  rig's cameras set far 90 km by hand.

## Review log
