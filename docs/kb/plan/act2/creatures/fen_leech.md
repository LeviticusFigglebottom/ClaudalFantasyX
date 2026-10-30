---
draft: pre-gate
id: fen_leech
kind: variant (sail leech)
chapter: 10
exists: yes, on the integration branch (built; `creatures.json` row, review baseline, portrait)
meets_bar: yes (hung low and draped, checked in the ossa_fen_roots arena 2026-10-30)
---
# fen_leech (Ch10, Ossa Fen, the dark water)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30). Docs only: no asset is built from this sheet
before the `act1-complete` tag. The art sheet is [variants.md](../../../art/creatures/act2/variants.md).

## Silhouette
The sail leech drawn ribbon-narrow and long (HALF_W 0.44, HALF_L 0.95), flat, its underside tannin-amber.

## Materials
The sail leech's `carapace`, with the slits' spawn_wound glow; since the Act I audit the base has a salt-pale canvas edge (CANVAS), which the fen leech also carries.

## Rig
11 bones; 5980 triangles in `assets/creatures/fen_leech/fen_leech.glb` (job `creature_fen_leech` in tools/dev/blender_builds.json, built on build_sail_leech).

## Clips
`idle`, `attack`, `cast`, `hit`, `ko`, `hit_b`, `idle_b` (the clip contract: idle, attack, cast, hit with its peak near 0.1 s, ko, plus the kit's hit_b and idle_b).
Clip audit (tools/creatures/clip_audit.gd, 2026-10-30): worst slip 15.0 cm (idle), worst one-frame pop 4% of its size (attack), deepest dip 114.7 cm (ko).

## Battle-distance read
**Risk: high.** The sail leech, hung at eye height, was seen edge-on as a row of glowing dashes on the Ch4 night deck (Act I audit); the fen leech is narrower still and keeps the 1.38 m hover. At the gate: hang it lower as the sail leech now is (its build pins `base.KO_DROP = 1.38`; lower both together) and check it against the dusk fen.
Encounters in data: `ch10_fen_leeches` (no Act II arena is named yet: judge it in the arena the encounter gets).

## Reuse of existing generators
build_sail_leech (rig, clips, KO_DROP). Its own: proportions, palette.

## State against the final bar
Below the bar for its read (not its model): the edge-on silhouette.

## Work at the gate (after `act1-complete`)
DONE 2026-10-30: hover 0.85 m (KO_DROP matched; its attack dips 0.70 m), so it reads as a long dark ribbon with glowing slits over its shadow (viewed in its ch10_fen_leeches encounter on the default arena). Arena check DONE 2026-10-30 (ossa_fen_roots preview): from that arena's low camera the 3.5 cm ribbon read edge-on, like a branch with cyan dots. Now it has a raised back (DOME 0.05), a body of (0.06, 0.035) and edges draped 0.1 m like a ray's, so edge-on it is an arch with height. Viewed: two leeches read as leeches with their row of slits. Left: `leech_bite` effect.
