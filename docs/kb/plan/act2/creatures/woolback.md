---
draft: built
id: woolback
kind: wildlife (herd animal)
chapter: 12
exists: yes
meets_bar: yes (greybox placement; move to the troughs on the dressed kit)
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
**Built 2026-10-30 (creatures track, ADR 0205, M4-A2P-056):**
- assets/creatures/woolback/woolback.glb (assets_src/creatures/woolback/build_woolback.py) imports build_avalanche_ram. It keeps the ram's body, neck, camelid head, mane, six lock chains, tail, legs and its herd-cord, and drops the seep partings, the belly and lock ice, and the jaw's icicle; the frost tint is sun-bleached wool instead. 13,615 triangles; the ram's 38-bone rig.
- Its clips: `idle` (grazing, neck down, the muzzle just over the grass, chewing), `look` (lifts its head, looks round to the left and back, grazes again), `walk` (a lateral-sequence amble in place, every hoof solved per frame: planted hooves slide back at WALK_SPEED, so the herd moving it at that speed keeps them still; within 2 cm in game).
- game/creatures/woolback/woolback_actor.tscn draws the model at 0.3 (head about 1 m).
- WildlifeHerd and WildlifeLayer's `herds` rows give skinned actors (not MultiMesh), the `woolback` kind in wildlife.json and a budget of 6. Each animal grazes, sometimes looks round, ambles to a spaced spot at the walk clip's speed (0.208 m/s) and looks up at a close player; nothing flees.
- Placed: game/data/world/wildlife/ch12_keth_pass.json, a pair at the pass foot and three on the saddle (greybox: there are no troughs yet). Review shots `wildlife_zone_keth_pass_foot` and `_saddle` (self-rendered and viewed: cream fleece, dark legs, the red herd-cord, heads down grazing).

## Work at the gate (after `act1-complete`)
Left: move the herds to the Keth kit's `woolback_trough` points and re-seat them when the dressed kit replaces the greybox.
