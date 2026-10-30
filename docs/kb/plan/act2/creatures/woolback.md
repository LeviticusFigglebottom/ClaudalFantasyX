---
draft: pre-gate
id: woolback
kind: wildlife (herd animal)
chapter: 12
exists: no
meets_bar: n/a
---
# woolback (Ch12, Keth Pass, the terraces and the herd-gate)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30), for M4-A2P-056 (Act II wildlife). Docs only: no
asset is built before the `act1-complete` tag. Wildlife is never a foe and never glimmer.

## Silhouette
The Ullari woolback (bible §5.7): a long-necked, deep-chested, shaggy pack animal, cream and slate fleece in layered locks, a small head held high, split hooves. Grazing in twos and threes by the herders' troughs (the Keth kit's `woolback_trough`). The Avalanche Ram is one grown monstrous; these are the ordinary ones it came from, so they must read as the same animal at a third of its size and without the seep's light.

## Materials
The avalanche ram's materials without the seep: `fleece` (layered locks in vertex colour), `skin`, `hoof`, `eye`; no spawn_wound, no glimmer.

## Rig and motion
A skinned actor (not MultiMesh: a few per zone, close to the path): the ram's quadruped rig, with idle (grazing, the neck down), a look-up, a walk; a FieldNpc-like wander between trough points, or WildlifeLayer's crab-beach wander scaled up.

## Clips
The wildlife kinds have no battle clips; their motion is the layer's procedural cycle (above). The woolback, a skinned
actor, needs `idle` (graze), `look`, `walk`.

## Read
Cream fleece against grey-green terraces: high value contrast. Not a battle actor.

## Reuse of existing generators
build_avalanche_ram (the woolback body, neck and fleece) at 0.3 scale, its ice, seep and battle clips dropped; the planted-foot pin on its walk.

## State
Does not exist (the ram does).

## Work at the gate (after `act1-complete`)
Build, a wildlife.json kind with its budget, placement in the zone file with tools/creatures/wildlife_snap.gd and
wildlife_audit.gd on the zone's dressed kit, a review shot, PROVENANCE rows.
