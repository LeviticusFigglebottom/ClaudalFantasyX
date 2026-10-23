---
id: M1-CHR-05
title: Base body .glb files do not reproduce from source
role: character
status: doing
owner_session: "worktree-agent-a361fe4924e35dfcf"
depends_on: [M1-QA-02]
milestone: M1
request-from: "qa"
---
## Goal
The Blender rebuild gate (M1-QA-02, `docs/kb/qa/blender_builds.md`) rebuilds `assets/characters/base_body/base_body_{slender,athletic,heavy}.glb` from `assets_src/characters/base_body/` with the pinned Blender 5.0.1. The rebuilds **don't match** the committed files: POSITION min/max differ by up to ~3 mm (slender max z 0.1831 rebuilt vs 0.1864 committed), and NORMAL, TANGENT and the indices differ too. The rebuild is stable from run to run, apart from a 1e-4 tangent wobble the gate tolerates, so the committed files were most likely exported from an intermediate state of a773ea1's sources.

## Acceptance criteria
- [ ] Rebuild the three variants with `assets_src/characters/base_body/build_all.sh`, look at them, and re-approve the `base_body_*` screenshot baselines (11 shots) if they move.
- [ ] `python3 tools/dev/verify_blender_builds.py --job base_body` passes, then remove the job's `expected_failure` from `tools/dev/blender_builds.json` (the gate fails until you do).
- [ ] Optional: drop `export_tangents=True` from `build.py` (Godot generates MikkTSpace tangents on import, `character_shading.md`), and then remove the TANGENT tolerance too.

## Notes
- Reproduce: `python3 tools/dev/verify_blender_builds.py --job base_body --keep /tmp/bb`, then compare `/tmp/bb/assets/...` with the committed files.

## Review log
