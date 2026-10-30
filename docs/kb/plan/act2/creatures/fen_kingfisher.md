---
draft: pre-gate
id: fen_kingfisher
kind: wildlife (bird)
chapter: 10
exists: no
meets_bar: n/a
---
# fen_kingfisher (Ch10, Ossa Fen, the mangrove channels and Reedhollow's edge)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30), for M4-A2P-056 (Act II wildlife). Docs only: no
asset is built before the `act1-complete` tag. Wildlife is never a foe and never glimmer.

## Silhouette
A small fen kingfisher: a stocky head and dagger bill on a short body, a stub tail; tannin-brown back with a sudden blue-green flash on the wings and a pale rust breast. Perched on mooring stakes and root-walk rails; darting low over the channels. **Never a heron, an egret or an otter**: those shapes are the Kirru people (act2_roster.md).

## Materials
The wildlife kit's vertex-colour material (`game/world/wildlife/wildlife.gdshader`, the gull's slots: body, wing, beak), new tints.

## Rig and motion
The gull kind's skeleton-free vertex animation (WildlifeGullFlock: orbit, perch, flee), shortened: a kingfisher flies low and straight, perches long, and plunges (a new flock state, `dive`, or a shorter orbit radius and lower altitude band).

## Clips
The wildlife kinds have no battle clips; their motion is the layer's procedural cycle (above). The woolback, a skinned
actor, needs `idle` (graze), `look`, `walk`.

## Read
A 1-2 cm silhouette at walking distance against dark water; it reads by its wing flash in motion. Not a battle actor.

## Reuse of existing generators
The gull's generator (assets_src/wildlife/gull: lathe body and wing quads) at a third of the size, with a longer bill; a `kingfisher` kind in wildlife.json with its own budget share.

## State
Does not exist.

## Work at the gate (after `act1-complete`)
Build, a wildlife.json kind with its budget, placement in the zone file with tools/creatures/wildlife_snap.gd and
wildlife_audit.gd on the zone's dressed kit, a review shot, PROVENANCE rows.
