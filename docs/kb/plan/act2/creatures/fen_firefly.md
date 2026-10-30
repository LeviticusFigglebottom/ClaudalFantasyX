---
draft: pre-gate
id: fen_firefly
kind: wildlife (insect swarm)
chapter: 10
exists: no
meets_bar: n/a
---
# fen_firefly (Ch10, Ossa Fen at dusk)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30), for M4-A2P-056 (Act II wildlife). Docs only: no
asset is built before the `act1-complete` tag. Wildlife is never a foe and never glimmer.

## Silhouette
Fireflies over the fen at dusk: points of warm light that blink slowly, low among the roots. Wildlife, **not glimmer** (ossa_fen.md: the fen's lights are animals, not the dead); warm yellow-green, never the glimmer swatches.

## Materials
The insect kind's emissive material, a new warm `firefly` colour from palette.json (checked against the glimmer swatches by tools/screenshots/palette_check.py).

## Rig and motion
The insect swarm (WildlifeSwarm, M3-CRE-616): the moth's loop, slower, with a per-insect blink (emission pulse from a hashed phase, no TIME so shots are stable).

## Clips
The wildlife kinds have no battle clips; their motion is the layer's procedural cycle (above). The woolback, a skinned
actor, needs `idle` (graze), `look`, `walk`.

## Read
Not a battle actor. In the zone, a cloud of a few dozen points at walking distance.

## Reuse of existing generators
assets_src/wildlife/insect (the moth and dragonfly): a third swarm type, `firefly`, sharing the MultiMesh path.

## State
Does not exist (the insect generator does).

## Work at the gate (after `act1-complete`)
Build, a wildlife.json kind with its budget, placement in the zone file with tools/creatures/wildlife_snap.gd and
wildlife_audit.gd on the zone's dressed kit, a review shot, PROVENANCE rows.
