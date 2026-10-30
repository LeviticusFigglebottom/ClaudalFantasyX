---
draft: pre-gate
id: root_crab
kind: variant (reef crab)
chapter: 10
exists: yes, on the integration branch (built; `creatures.json` row, review baseline, portrait)
meets_bar: yes
---
# root_crab (Ch10, Ossa Fen, in the roots)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30). Docs only: no asset is built from this sheet
before the `act1-complete` tag. The art sheet is [variants.md](../../../art/creatures/act2/variants.md).

## Silhouette
The reef crab on longer climbing legs (LEG_KNEE and LEG_FOOT raised and widened), bark-brown and lichen-spotted.

## Materials
The reef crab's slots, `shell`, `chitin`, `eye`, retinted toward `timber_weathered`.

## Rig
26 bones; 8888 triangles in `assets/creatures/root_crab/root_crab.glb` (job `creature_root_crab` in tools/dev/blender_builds.json, built on build_reef_crab).

## Clips
`idle`, `attack`, `cast`, `hit`, `ko`, `hit_b`, `idle_b` (the clip contract: idle, attack, cast, hit with its peak near 0.1 s, ko, plus the kit's hit_b and idle_b).
Clip audit (tools/creatures/clip_audit.gd, 2026-10-30): worst slip 14.6 cm (ko), worst one-frame pop 9% of its size (attack), deepest dip 0.1 cm (idle).

## Battle-distance read
Bark-brown on the fen's dark root-walk planks: a value risk at dusk, the reef crab's pale shell top is what carries it. Check in its arena; a lighter lichen on the shell top is the fix if it melts.
Encounters in data: `ch10_fen_roots` (no Act II arena is named yet: judge it in the arena the encounter gets).

## Reuse of existing generators
build_reef_crab (rig, clips, the planted-foot pin since 2026-10-29, `grounding.pinned`); only proportions and tint are its own.

## State against the final bar
Meets the bar (the crab family's audit: feet held, KO a collapse).

## Work at the gate (after `act1-complete`)
~~Enemy `model` key~~ (done 2026-10-30); arena shot; the `root_drag` skill's effect.
