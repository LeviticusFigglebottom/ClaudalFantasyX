---
id: M3-ENV-1321
title: The Bell's weeping column as a kit piece (the column half of M3-RND-26, taken under ADR 0041 at the Lead's ask)
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: []
milestone: M3
reviewer: rendering
---
## Notes (2026-10-28, env-art-b)
- New Tamsule Bell kit piece `weep_column` (`b_column.py`): a 31.5 m twisting fall (core and fraying sheath), a spray
  crown and ripple rings, on the kit's existing slots so env-art's material set is unchanged. The zones dress it with
  their own still, lit-from-within water (`game/levels/ch07/tamsule_bell_galleries/weep_*_water_material.tres`).
- Galleries: on the Column block, so the zone keeps no greybox (the last Act I inventory row of env-art-b's, M3-HER-1141).
  Port: under the kit's Bell at BELL_AXIS (the layout's BellColumn block is the greybox's old z -40).
- `--filter=` ch07 18/0, zone_kit 12/0; `test_tamsule_bell_kit` OK (Blender rebuild `--all`: older pieces
  byte-identical). Self-rendered ch07_bell_galleries and ch07_bell_moorings (the fall reads), ch07_tamsule_gantry and
  _mouth (the gantry's front leg hides it head-on).
- Left for Rendering (M3-RND-26): a flowing water shader on the column if wanted, and the drop's WaterSphereRig sizing.

## Review log
