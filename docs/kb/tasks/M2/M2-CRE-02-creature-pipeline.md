---
id: M2-CRE-02
title: "Creature pipeline: procedural Blender builds, rig and clips, reproducible jobs, materials and import rules"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CRE-01]
milestone: M2
request-from: lead
---
## Goal
assets_src/creatures/<id>/ procedural builds on a shared kit, a bone rig with idle, attack, cast/special, hit and KO clips (plus phase_change for the boss) exported in the GLB, byte-reproducible jobs in tools/dev/blender_builds.json, creature materials, and a creatures import category (game/data/import/creatures.json).

## Acceptance criteria
- [x] See Goal; the notes record what shipped.

## Notes

- 2026-10-24: shipped as docs/kb/art/creatures/pipeline.md describes: assets_src/creatures/common/creature_kit.py (numpy geometry in Godot axes, a bone rig, eased clips baked at 30 fps, deterministic GLB export) and write_materials.py; game/shaders/creature/creature.gdshader (vertex albedo, wetness with clearcoat, cavity, a spawn_wound emission mask with a slow pulse, detail noise and bump, rim sheen); the `creatures` import category; one Blender job per creature (16 now, all byte-identical); PROVENANCE rows; tools/tests/test_creatures.py.
- Kit fix (found by the gull agent): `ellipsoid` and `tube` wound inward; fixed and every creature rebuilt (jobs identical).
- Why not the character shader families: pipeline.md §2.

## Review log
