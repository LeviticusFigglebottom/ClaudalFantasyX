---
draft: pre-gate
id: glass_skate
kind: reef beast
chapter: 16
exists: yes, on the integration branch (built; `creatures.json` row, review baseline, portrait)
meets_bar: yes
---
# glass_skate (Ch16, the Pale Rim, the white shallows)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30). Docs only: no asset is built from this sheet
before the `act1-complete` tag. The art sheet is [glass_skate.md](../../../art/creatures/act2/glass_skate.md).

## Silhouette
A skate buried in the white sand of the shallows, its back the colour of the water, only its eyes showing; it rises to strike.

## Materials
`back`, `belly`, `eye`.

## Rig
14 bones; 3638 triangles in `assets/creatures/glass_skate/glass_skate.glb` (job `creature_glass_skate` in tools/dev/blender_builds.json).

## Clips
`idle`, `attack`, `cast`, `hit`, `ko`, `hit_b`, `idle_b` (the clip contract: idle, attack, cast, hit with its peak near 0.1 s, ko, plus the kit's hit_b and idle_b).
Clip audit (tools/creatures/clip_audit.gd, 2026-10-30): worst slip 62.9 cm (cast), worst one-frame pop 6% of its size (attack), deepest dip 0.1 cm (attack).

## Battle-distance read
Buried and white-on-white **on purpose** (untargetable until it acts). Once it has acted it must read: its risen pose shows a darker belly and the eyes. Risk: medium (the arena's white water).
Encounters in data: `ch16_rim_skates` (no Act II arena is named yet: judge it in the arena the encounter gets).

## Reuse of existing generators
Its own disc build (see gallery_ray).

## State against the final bar
Meets the bar. Its `cast` slides 63 cm: that is the burial wriggle into the sand (it moves itself), not a planted foot.

## Work at the gate (after `act1-complete`)
Enemy `model` key; `skate_sting` effect; check the risen read in the Rim arena.
