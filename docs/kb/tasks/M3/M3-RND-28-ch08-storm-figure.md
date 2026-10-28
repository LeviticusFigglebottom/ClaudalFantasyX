---
id: M3-RND-28
title: "Request: Ch8's storm figure over the water (wall_falls W22) is a cyan capsule"
role: rendering
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
ADR 0041 (docs/kb/qa/act1_playthrough_ch04_ch09.md): `ch08_wall_falls` cuts to the storm figure standing on the water
(the `figure` stage actor in `ch08/corrow`, a cyan capsule by design while it waited). It needs a body: a silhouette
of Undertow water in a human shape (characters' mesh, rendering's shader), which act1-chapters casts on the actor.

## Acceptance criteria
- [ ] A figure scene act1-chapters can cast (`ZoneCast` `creature:<id>` or a villager-style actor scene).

## Review log
