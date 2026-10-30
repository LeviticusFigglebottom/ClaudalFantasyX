---
draft: pre-gate
id: conduit_crawler
kind: construct
chapter: 11
exists: yes, on the integration branch (built; `creatures.json` row, review baseline, portrait)
meets_bar: close
---
# conduit_crawler (Ch11, Lowlight temple, the conduits)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30). Docs only: no asset is built from this sheet
before the `act1-complete` tag. The art sheet is [conduit_crawler.md](../../../art/creatures/act2/conduit_crawler.md).

## Silhouette
A Lit Age conduit-cleaning machine: a salt-glass dome shell on six brass feet, a dim `glimmer_bound` light inside, two brass work-arms forward.

## Materials
`shell` (salt-glass), `seam` (the bound light), `frame` (brass).

## Rig
18 bones; 4752 triangles in `assets/creatures/conduit_crawler/conduit_crawler.glb` (job `creature_conduit_crawler` in tools/dev/blender_builds.json).

## Clips
`idle`, `attack`, `cast`, `hit`, `ko`, `hit_b`, `idle_b` (the clip contract: idle, attack, cast, hit with its peak near 0.1 s, ko, plus the kit's hit_b and idle_b).
Clip audit (tools/creatures/clip_audit.gd, 2026-10-30): worst slip 10.8 cm (ko), worst one-frame pop 7% of its size (hit_b), deepest dip 0.1 cm (hit_b).

## Battle-distance read
The glowing glass dome reads on any temple floor. Risk: low.
Encounters in data: none (no Act II arena is named yet: judge it in the arena the encounter gets).

## Reuse of existing generators
Its own build; a construct, so no pin (it should step mechanically; its attack slips 2.5 cm only).

## State against the final bar
Close: the dome is good, the brass legs are plain thin tubes (the primitive pass would add knuckle joints and foot pads).

## Work at the gate (after `act1-complete`)
**No enemy row** (the plan's default: a Lamp Engine boss add that repairs parts, M4-A2P-022); leg detail; its repair effect.
