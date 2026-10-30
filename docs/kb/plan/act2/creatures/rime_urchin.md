---
draft: pre-gate
id: rime_urchin
kind: reef beast
chapter: 11
exists: yes, on the integration branch (built; `creatures.json` row, review baseline, portrait)
meets_bar: yes
---
# rime_urchin (Ch11, Sunken Vey, the cold wells)

Plan sheet for ADR 0203's Act II preparation (creatures, 2026-10-30). Docs only: no asset is built from this sheet
before the `act1-complete` tag. The art sheet is [rime_urchin.md](../../../art/creatures/act2/rime_urchin.md).

## Silhouette
A long-spined urchin, dark teal test, its spines furred with rime, on a pale ice-crust base: a bristling sphere 2 m across with its spines.

## Materials
`body` (the test), `spine` (rimed, translucent tips), `ice` (the base crust).

## Rig
10 bones; 8822 triangles in `assets/creatures/rime_urchin/rime_urchin.glb` (job `creature_rime_urchin` in tools/dev/blender_builds.json).

## Clips
`idle`, `attack`, `cast`, `hit`, `ko`, `hit_b`, `idle_b` (the clip contract: idle, attack, cast, hit with its peak near 0.1 s, ko, plus the kit's hit_b and idle_b).
Clip audit (tools/creatures/clip_audit.gd, 2026-10-30): worst slip 0.0 cm (attack), worst one-frame pop 1% of its size (attack), deepest dip 0.0 cm (attack).

## Battle-distance read
Strong silhouette (bristles) and a pale base that separates it from any floor. Risk: low.
Encounters in data: `ch11_vey_urchins` (no Act II arena is named yet: judge it in the arena the encounter gets).

## Reuse of existing generators
Its own build.

## State against the final bar
Meets the bar for its model. **KO done 2026-10-30 (creatures track, ADR 0205):** after a last clench the spines fall open 50 degrees round the test (their tips lift as they open, so the low ones lie on the floor, not in it) and the test slumps 6 cm and tips 8 degrees: the ball of spines becomes a flat, parted star (clip sheet). The ice cracking is left to the KO effect (VFX).

## Work at the gate (after `act1-complete`)
~~A readable KO~~ (done); `rime_spine` effect; ~~enemy `model` key~~ (done 2026-10-30).
