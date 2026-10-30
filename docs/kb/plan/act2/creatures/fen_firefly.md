---
draft: built
id: fen_firefly
kind: wildlife (insect swarm)
chapter: 10
exists: yes
meets_bar: yes (greybox placement; re-seat on the dressed kit)
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
**Built 2026-10-30 (creatures track, ADR 0205, M4-A2P-056):**
- `insect_firefly` in assets/wildlife/insect/insect.glb: a slim 1.4 cm beetle, dusky wing covers with a pale margin held up, clear hind wings beating, a faded red shield, and the lantern (the abdomen's last segments, pale yellow-green wax).
- The `firefly` slot (materials.json): the lantern glows `glow_color` (sun_gold 30% toward palm_green: warm yellow-green, not a glimmer swatch) at up to energy 3, per instance by its blink; lit, it swells toward 0.006 rad of the view at its distance, so it holds a few pixels as a point of light at walking distance (a bloom stand-in) and stays small up close.
- The shader's mode 6 (wildlife.gdshader): the flutter, with the blink in the mode parameter. WildlifeSwarm's `firefly` type flies the moth's orbit, slower and lower, and flashes once every 2.5–4 s over 2 s (glow_floor 0.04 between). The layer's seventh MultiMesh (draw_calls budget 7).
- Placed: game/data/world/wildlife/ch10_ossa_fen.json, four swarms of six (the insect budget, 24) low over the water beside Walk0, Walk2, the side pocket's end and Walk4, on the greybox layout. Review shots `wildlife_zone_ossa_fen_walk0` and `_pocket` (self-rendered and viewed: warm points among the trunks over the tannin water).

## Work at the gate (after `act1-complete`)
Left: re-seat the swarms on the dressed kit when env-art replaces the greybox blocks.
