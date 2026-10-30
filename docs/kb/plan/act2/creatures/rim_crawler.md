---
draft: pre-gate
id: rim_crawler
kind: variant (tide crawler)
chapter: 16
exists: yes, on the integration branch (built; `creatures.json` row, review baseline, portrait)
meets_bar: yes (value fixed 2026-10-30; re-judge in the Rim's grade)
---
# rim_crawler (Ch16, the Pale Rim)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30). Docs only: no asset is built from this sheet
before the `act1-complete` tag. The art sheet is [variants.md](../../../art/creatures/act2/variants.md).

## Silhouette
The tide crawler bleached chalk-white by days of white water, its wounds dimmer.

## Materials
The tide crawler's `carapace`, bleached.

## Rig
30 bones; 4796 triangles in `assets/creatures/rim_crawler/rim_crawler.glb` (job `creature_rim_crawler` in tools/dev/blender_builds.json, built on build_tide_crawler).

## Clips
`idle`, `attack`, `cast`, `hit`, `ko`, `hit_b`, `idle_b` (the clip contract: idle, attack, cast, hit with its peak near 0.1 s, ko, plus the kit's hit_b and idle_b).
Clip audit (tools/creatures/clip_audit.gd, 2026-10-30): worst slip 25.5 cm (ko), worst one-frame pop 5% of its size (hit_b), deepest dip 0.2 cm (idle).

## Battle-distance read
Chalk-white on white shallows: **risk: high** for value. The tide crawler's dark lacquer is what read; bleached, the legs' shadows and the dim seams carry it. Consider a grey-blue wet underside and stronger seam glow in the Rim's flat light.
**Done 2026-10-30 (creatures track, ADR 0205):** the flanks go a wet `storm_slate` toward the underside, the plate seams are slate, the chalk is weathered with `overcast_slate` mottling, and the wounds glow at energy 1.7 (from 1.0). Self-rendered in `ch16_rim_crawlers` on pale sand: slate flanks, black joints and cyan glows read; judge it again in the Rim's own grade.
Encounters in data: `ch16_rim_crawlers` (no Act II arena is named yet: judge it in the arena the encounter gets).

## Reuse of existing generators
build_tide_crawler (its 2026-10-29 primitive pass: carapace plates and seams, jointed legs, the planted-foot pin), so it inherited all of it.

## State against the final bar
Model meets the bar (rebuilt with the tide crawler); the value fix is in (slate flanks and seams, brighter wounds).

## Work at the gate (after `act1-complete`)
~~Value check~~ (done; re-judge in the Rim's grade); ~~enemy `model` key~~ (done 2026-10-30).
