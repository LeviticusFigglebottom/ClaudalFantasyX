---
draft: pre-gate
id: scree_crawler
kind: variant (slag tortoise)
chapter: 12
exists: yes, on the integration branch (built; `creatures.json` row, review baseline, portrait)
meets_bar: yes
---
# scree_crawler (Ch12, Cloudloom approach)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30). Docs only: no asset is built from this sheet
before the `act1-complete` tag. The art sheet is [variants.md](../../../art/creatures/act2/variants.md).

## Silhouette
The slag tortoise with snow-dusted, grit-packed scree slabs on its shell instead of slag (rebuilt with the tortoise's primitive pass, M3-CRE-660). Its build still says frost-split: no ice in Ch12 (ADR 0015, ADR 0204 §2), so the frost becomes dry snow in the seams and grit (M4-CRE-670).

## Materials
`crust` (scree; snow in the seams, no ice sheen after M4-CRE-670), `skin`, `eye`.

## Rig
9 bones; 17502 triangles in `assets/creatures/scree_crawler/scree_crawler.glb` (job `creature_scree_crawler` in tools/dev/blender_builds.json, built on build_slag_tortoise).

## Clips
`idle`, `attack`, `cast`, `hit`, `ko`, `hit_b`, `idle_b` (the clip contract: idle, attack, cast, hit with its peak near 0.1 s, ko, plus the kit's hit_b and idle_b).
Clip audit (tools/creatures/clip_audit.gd, 2026-10-30): worst slip 14.9 cm (ko), worst one-frame pop 3% of its size (hit_b), deepest dip 0.1 cm (ko).

## Battle-distance read
A big rounded shell; blue-grey scree on pale mountain stone may melt in value: its orange-brown skin carries it. Risk: medium.
Encounters in data: `ch12_pass_scree` (no Act II arena is named yet: judge it in the arena the encounter gets).

## Reuse of existing generators
build_slag_tortoise (rig, clips, the flip-over KO).

## State against the final bar
Meets the bar (17.5k tris: check the budget at the gate).

## Work at the gate (after `act1-complete`)
Frost to snow and grit (M4-CRE-670); enemy `model` key; arena shot; `scree_slide` effect.
