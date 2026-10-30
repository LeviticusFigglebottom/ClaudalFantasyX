---
draft: built
id: fen_kingfisher
kind: wildlife (bird)
chapter: 10
exists: yes
meets_bar: yes (greybox placement; re-seat on the dressed kit)
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
**Built 2026-10-30 (creatures track, ADR 0205, M4-A2P-056):**
- assets/wildlife/kingfisher/kingfisher.glb (assets_src/wildlife/kingfisher/build_kingfisher.py): the gull generator's two meshes and masks, its own shape. A stocky body, a big head, a long black dagger bill, a stub tail, short rounded wings (0.26 m span); a tannin-brown back and crown, a blue-green flash on the wings and rump (sea_blue_cloth toward palm_green: not a glimmer teal, and it never glows), a pale rust breast, a pale throat, red feet. 796 triangles flying, 920 perched.
- A `kingfisher` kind in wildlife.json: the gull's flock (WildlifeGullFlock, the same keys) tuned small and low, with fast whirring bursts (11 Hz), brief glides, a tight orbit, long perches and quick head turns. It has its own zone rows (`kingfishers`), budget (6) and two MultiMeshes (draw_calls 9).
- Placed: three pairs in ch10_ossa_fen.json over the channels by Walk0, Walk2 and Walk3, perching on the root-walk rails facing the water, one of each pair sitting at the start. Review shot `wildlife_zone_ossa_fen_rail0` (self-rendered and viewed: a kingfisher on Walk0's rail, another flying).
- Not built: a plunge-dive state. The tight, low orbit carries the read. Birds can pass through a greybox trunk (wildlife has no collision); re-seat the flocks on the dressed kit.

## Work at the gate (after `act1-complete`)
Left: re-seat the flocks and perches on the dressed kit when env-art replaces the greybox blocks.
