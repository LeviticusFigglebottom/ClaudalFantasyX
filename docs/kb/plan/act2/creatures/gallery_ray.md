---
draft: pre-gate
id: gallery_ray
kind: reef beast
chapter: 11
exists: yes, on the integration branch (built; `creatures.json` row, review baseline, portrait)
meets_bar: yes (read fixed 2026-10-30)
---
# gallery_ray (Ch11, Sunken Vey, the drowned galleries)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30). Docs only: no asset is built from this sheet
before the `act1-complete` tag. The art sheet is [gallery_ray.md](../../../art/creatures/act2/gallery_ray.md).

## Silhouette
A dusky cave ray gliding above the water line between the columns: a broad flat disc with a whip tail, freckled with the salt-glass floors' light.

## Materials
`body`, `margin` (the disc's translucent edge), `eye`.

## Rig
12 bones; 4504 triangles in `assets/creatures/gallery_ray/gallery_ray.glb` (job `creature_gallery_ray` in tools/dev/blender_builds.json).

## Clips
`idle`, `attack`, `cast`, `hit`, `ko`, `hit_b`, `idle_b` (the clip contract: idle, attack, cast, hit with its peak near 0.1 s, ko, plus the kit's hit_b and idle_b).
Clip audit (tools/creatures/clip_audit.gd, 2026-10-30): worst slip 15.4 cm (hit_b), worst one-frame pop 9% of its size (attack), deepest dip 140.1 cm (ko).

## Battle-distance read
**Risk: high by design.** It is camouflaged against salt-glass (pale on pale) and flat (edge-on from the battle camera, like the leeches). Pillar 4 needs it found at once: give it a darker dorsal pattern or a rim of the sea-glow along its margin, and a hover below eye height so the camera sees its back. Decide with its arena's grade.
**Done 2026-10-30 (creatures track, ADR 0205):** the back is now dusky (`cumulus_shadow` mottled toward `lacquer_black`, with dark rosettes and pale `salt_glass` freckles), the margin's `sea_glow` doubled (energy 1.6), the body's wet clearcoat cut to 0.25 (at the battle camera's grazing angle its sheen washed the back white), and the hover dropped from 1.4 to 0.95 m (the attack's bank dips 0.65 m; the cast's pool and the KO follow `HOVER`). Self-rendered in `ch11_vey_rays`: slate-blue discs with a teal rim on pale sand.
Encounters in data: `ch11_vey_rays`, `ch11_vey_urchins` (no Act II arena is named yet: judge it in the arena the encounter gets).

**Arena check 2026-10-30 (lowlight_engine_hall preview, the nearest built Ch11 arena):** the dusky disc with its teal margin reads against the teal pool. In a three-enemy layout, slot 0 can sit in front of an urchin in slot 1 (an encounter-layout matter, not the model's).

## Reuse of existing generators
Its own build (a disc rig of wing chains and a tail). The glass skate's disc build is its sibling; share a disc module if both get reworked.

## State against the final bar
Model meets the bar; the read fix is in (dusky back, margin glow, hover 0.95 m). Judge it again in its Act II arena's grade.

## Work at the gate (after `act1-complete`)
~~Read fix~~ (done); `glide_lash` effect; ~~enemy `model` key~~ (done 2026-10-30).
