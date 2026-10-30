---
draft: pre-gate
id: ridge_lynx
kind: beast
chapter: 12
exists: yes, on the integration branch (built; `creatures.json` row, review baseline, portrait)
meets_bar: no
---
# ridge_lynx (Ch12, Keth Pass)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30). Docs only: no asset is built from this sheet
before the `act1-complete` tag. The art sheet is [ridge_lynx.md](../../../art/creatures/act2/ridge_lynx.md).

## Silhouette
A high-pass lynx in a thick slate-grey winter coat with snow caught in it, snow-tipped ear tufts, a short tail, big snowshoe paws gritty from the scree. No frost or rime (ADR 0015 and ADR 0204 §2: no ice in Ch12–Ch15; the swap is M4-CRE-670).

## Materials
`coat` (the fur in the vertex colour and shader detail), `eye`.

## Rig
27 bones; 7304 triangles in `assets/creatures/ridge_lynx/ridge_lynx.glb` (job `creature_ridge_lynx` in tools/dev/blender_builds.json).

## Clips
`idle`, `attack`, `cast`, `hit`, `ko`, `hit_b`, `idle_b` (the clip contract: idle, attack, cast, hit with its peak near 0.1 s, ko, plus the kit's hit_b and idle_b).
Clip audit (tools/creatures/clip_audit.gd, 2026-10-30): worst slip 29.3 cm (hit_b), worst one-frame pop 16% of its size (attack), deepest dip 0.3 cm (idle_b).

## Battle-distance read
Slate-grey on the pass's pale stone and snow: reads by value. Risk: low.
Encounters in data: `ch12_pass_lynxes` (no Act II arena is named yet: judge it in the arena the encounter gets).

## Reuse of existing generators
Its own quadruped build; the raid hound's rig is its nearest sibling.

## State against the final bar
**Below the bar:** its paws slide 18–29 cm on attack and hit (clip audit: the same `grounded()`-only slide the hound had), and its legs and paws read as plain rounded cylinders up close. At the gate: `grounding.pinned` on its four legs, and the hound's lunge treatment (forepaws step) on its pounce; a shaping pass on the legs and paws.

## Work at the gate (after `act1-complete`)
Pin and step; leg/paw shaping; frost to snow and grit (M4-CRE-670, one rebuild with the pin); `pounce` effect; enemy `model` key.
