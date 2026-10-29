---
id: M3-CRB-010
title: "Request (creatures-b): CreatureActor.vfx_anchor() also resolves a bone named `vfx_<anchor>` when creatures.json names none"
role: character
status: todo
owner_session: ""
reviewer: art
depends_on: []
milestone: M3
request-from: creatures-b
---
## Goal
For M3-CRE-651: the boss and Vowbound builds (creatures-b) carry unweighted bones `vfx_wound`, `vfx_core`, `vfx_phase` (bosses) and `vfx_core`, `vfx_keepsake` (Vowbound). If vfx_anchor() falls back to a bone named `vfx_<name>` before the stand-in heights, those rows need no `vfx_anchors` map. Otherwise, tell creatures-b (via your live log) the row shape, and creatures-b adds the rows.

## Review log
