---
id: M3-ENV-748
title: "Haluna's Neme is a capsule stand-in; her model exists (request to slice-polish)"
role: cinematics
status: review
owner_session: "slice-polish (session_01F3vrUPLtDQMGSRrMHJtpz1)"
depends_on: []
milestone: M3
request-from: environment
reviewer: character
priority: high
---
## Goal
ADR 0041 and the Act I inventory (M3-HER-1140, Ch2 row): `game/levels/ch02/haluna/haluna.tscn` `NPCs/Neme/Neme/StandIn`
is a primitive mesh. Characters' `assets/characters/villagers/neme/` is ready, as the other villagers' are (Kell's
`kell_actor.tscn` is how Oruvel's layout names one).

## Acceptance criteria
- [ ] Replace `StandIn` (and the `Facing` marker mesh) with Neme's actor scene, keeping the StaticBody and its Shape.
- [ ] Re-render a Haluna shot that shows her, and view it.

## Review log
- 2026-10-28 slice-polish: done. In play, VillagerLayer (creatures' `ch02_haluna.json` row) already adopted Neme with her model and hid the capsule; the static `StandIn` and `Facing` meshes (and their capsule sub-resources) are now gone too, so no primitive remains in the scene. The layer's body is the only one. Viewed in `slice_neme_table`: Neme in her apron. Checks: haluna 65, haluna_villagers 7, slice_primitives 1, all 0 failed.
