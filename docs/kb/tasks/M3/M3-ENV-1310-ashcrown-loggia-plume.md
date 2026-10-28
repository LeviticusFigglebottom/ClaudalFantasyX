---
id: M3-ENV-1310
title: Ashcrown's crater loggia (A08) looks across the crater, not into the plume's skin
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: [M3-ENV-1303]
milestone: M3
reviewer: art-direction
---
## Goal
The Lead's "weakest view" pass (Ashcrown A08's loggia). At the preview's size, `ash_plume_near`'s billows reach the
loggia's rail, so Kahre's chamber and the court's view through it showed a flat grey wall of ash: no crater, no
rim, no sky.

## Notes (2026-10-28, env-art-b)
- `tools/act1/ch05_ashcrown_dressing.py`: the near plume is narrowed to 0.75 across, with its height kept
  (`scale`/`scale_y`), so it stands back over the vent with the far rim and the sky round it. A vent-glow fire light
  under it (VENT_GLOW).
- `--filter=ashcrown` 22/0. Self-rendered ch05_ashcrown_court, _causeway and _crown, compared with the old renders:
  the causeway's silhouette holds, and the loggia frames billows with sky beside them.
- For env-art: the kit preview's A08 (`ashcrown_a08_crater_loggia`) has the same cause. The preview's borrowed plume
  row could take the same scale.

## Review log
