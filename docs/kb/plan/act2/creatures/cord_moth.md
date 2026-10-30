---
draft: pre-gate
id: cord_moth
kind: beast
chapter: 12
exists: yes, on the integration branch (built; `creatures.json` row, review baseline, portrait)
meets_bar: yes
---
# cord_moth (Ch12, Keth Pass, along the pass-cords)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30). Docs only: no asset is built from this sheet
before the `act1-complete` tag. The art sheet is [cord_moth.md](../../../art/creatures/act2/cord_moth.md).

## Silhouette
A pale moth with broad wings carrying knot patterns (real keth knots Ysolde can read), feathery antennae.

## Materials
`wing`, `knot` (the patterns), `body`, `eye`.

## Rig
12 bones; 4144 triangles in `assets/creatures/cord_moth/cord_moth.glb` (job `creature_cord_moth` in tools/dev/blender_builds.json).

## Clips
`idle`, `attack`, `cast`, `hit`, `ko`, `hit_b`, `idle_b` (the clip contract: idle, attack, cast, hit with its peak near 0.1 s, ko, plus the kit's hit_b and idle_b).
Clip audit (tools/creatures/clip_audit.gd, 2026-10-30): worst slip 5.4 cm (hit_b), worst one-frame pop 14% of its size (hit_b), deepest dip 124.4 cm (ko).

## Battle-distance read
Pale wings against grey stone and sky: value close to the background (risk: medium); its wings are held flat like the ashwing's, which read as slivers until the ashwing was scaled 1.35× in battle (Act I audit). Expect the same fix.
Encounters in data: `ch12_pass_moths` (no Act II arena is named yet: judge it in the arena the encounter gets).

## Reuse of existing generators
Its own build; the ashwing is its sibling (flat-winged flier).

## State against the final bar
Meets the bar for its model; its flap pops (9–14% of its size) are fast wingbeats.

## Work at the gate (after `act1-complete`)
Battle scale (the ashwing's 1.35×, hover to match); `unravel` effect (in test_battle_act1_ability_vfx's list); enemy `model` key.
