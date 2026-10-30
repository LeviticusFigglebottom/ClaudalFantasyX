---
draft: built
id: rim_ray
kind: wildlife (fish shoal)
chapter: 16
exists: yes
meets_bar: yes (greybox placement; judge again under the Rim's real water)
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
**Built 2026-10-30 (creatures track, ADR 0205, M4-A2P-056):**
- assets/wildlife/rim_ray/rim_ray.glb (assets_src/wildlife/rim_ray/build_rim_ray.py): a 0.4 m rounded diamond with a whip tail, a pale sand back freckled a shade darker, a faint darker margin, small dark eyes and a bone belly. 868 triangles. Its fins carry the flap mask.
- A `ray` kind in wildlife.json: the fish shoal (WildlifeShoal, the same keys), slow, loose and flat. WildlifeShoal takes a shader mode, so rays draw with the flap (their fins beat) instead of the swim. They cast shadows. They have their own zone rows (`rays`), a budget of 16 and a MultiMesh (draw_calls 10).
- Placed: game/data/world/wildlife/ch16_pale_rim.json, three groups (5, 6, 5) at y 0.04 under the hand-deep water, off the wade by Cairn0, Cairn2 and Cairn4.
- Review shot `wildlife_zone_pale_rim_wade` (self-rendered and viewed). The greybox's opaque Shallows plane would hide them, so the review stage hides it (zone_wildlife.gd `hide_nodes`). They read as low pale shapes with beating fins on the white sand.

## Work at the gate (after `act1-complete`)
Left: judge them under the Rim's real (transparent) water when env-art's water replaces the greybox plane.
