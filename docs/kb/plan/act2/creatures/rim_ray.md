---
draft: pre-gate
id: rim_ray
kind: wildlife (fish shoal)
chapter: 16
exists: no
meets_bar: n/a
---
# rim_ray (Ch16, the Pale Rim, the white shallows)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30), for M4-A2P-056 (Act II wildlife). Docs only: no
asset is built before the `act1-complete` tag. Wildlife is never a foe and never glimmer.

## Silhouette
Small pale rays (40 cm across) gliding in loose groups over the white sand in the ankle-deep water, their shadows sharper than their bodies. They swim and turn; they never bury. Distinct from the glass skate (a 2 m buried ambusher foe): the rays are fish-sized, always moving and always in groups, so the player never mistakes the wildlife for the foe (pillar 4).

## Materials
The fish kind's material, a pale sand-white back with a faint darker margin.

## Rig and motion
The fish shoal (WildlifeShoal: wander, startle and dart), with a ray's flapping margin as the swim cycle instead of the fish's tail wag.

## Clips
The wildlife kinds have no battle clips; their motion is the layer's procedural cycle (above). The woolback, a skinned
actor, needs `idle` (graze), `look`, `walk`.

## Read
In the zone, low pale shapes and crisp shadows on white sand: their shadows carry them. Not a battle actor.

## Reuse of existing generators
The shoal-fish generator with a disc body (the gallery ray's and glass skate's disc profile, small); a `ray` kind with a flap cycle.

## State
Does not exist.

## Work at the gate (after `act1-complete`)
Build, a wildlife.json kind with its budget, placement in the zone file with tools/creatures/wildlife_snap.gd and
wildlife_audit.gd on the zone's dressed kit, a review shot, PROVENANCE rows.
