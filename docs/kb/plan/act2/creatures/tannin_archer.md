---
draft: pre-gate
id: tannin_archer
kind: fen beast
chapter: 10
exists: yes, on the integration branch (built; `creatures.json` row, review baseline, portrait)
meets_bar: yes
---
# tannin_archer (Ch10, Ossa Fen, the mangrove channels)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30). Docs only: no asset is built from this sheet
before the `act1-complete` tag. The art sheet is [tannin_archer.md](../../../art/creatures/act2/tannin_archer.md).

## Silhouette
An archerfish a dog's length, lying half out of the tannin water on a mangrove root: a deep, laterally flat body with a high back, a big upturned mouth for the jet, dark vertical bars over a pale tannin-gold flank. The root it lies on is part of the model (y 0 is the water).

## Materials
`body` (wet scales, the bars in the vertex colour), `fin` (translucent rim), `eye`, `root` (wet bark). spawn_wound weak point per the art sheet.

## Rig
10 bones; 4464 triangles in `assets/creatures/tannin_archer/tannin_archer.glb` (job `creature_tannin_archer` in tools/dev/blender_builds.json).

## Clips
`idle`, `attack`, `cast`, `hit`, `ko`, `hit_b`, `idle_b` (the clip contract: idle, attack, cast, hit with its peak near 0.1 s, ko, plus the kit's hit_b and idle_b).
Clip audit (tools/creatures/clip_audit.gd, 2026-10-30): worst slip 10.3 cm (cast), worst one-frame pop 2% of its size (hit_b), deepest dip 8.3 cm (attack).

## Battle-distance read
The fen at dusk is dark tannin water under a mangrove canopy (ossa_fen.md): its pale flank and bars read against dark water; the root keeps it grounded. Risk: low. At battle distance it reads as a fish on a branch (clip sheet viewed).
Encounters in data: `ch10_fen_archers` (no Act II arena is named yet: judge it in the arena the encounter gets).

## Reuse of existing generators
Its own build (no base). The fen's water is y 0: it sits in the water plane like the Act II wakefin and Act I lantern eel (test_creatures ALLOW: half out of the water).

## State against the final bar
Meets the bar on the clip sheet: a clear fish body, bars and fins; slightly simple. Its 8 cm dip is the root's ends under the water by design.

## Work at the gate (after `act1-complete`)
~~enemy `model` key~~ (done 2026-10-30); a battle shot in its arena; its `tannin_jet` effect (battle VFX, test_battle_act1_ability_vfx lists it).
