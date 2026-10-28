# Handoff — art (creatures) — 2026-10-28 #4

Worktree agent for M3-CRE-650 (weak-point marks for the three Act I regulars that had none). The branch was cut
from `claude/creatures` and is not pushed; the coordinator merges it and self-renders.

## Done
- **raid_hound:** an old gaff scar, healed shut, on the breast below the throat toward its right (-x). It is one
  small closed `spawn_wound` mark (ADR 0151) in the `coat` slot, at the reef crab's values (1.4, 0.35 Hz, depth 0.35).
  The sheet's "no weak-point glow" is superseded.
- **flue_moth:** a seam seared shut across its brow, toward -x, in a new `wound` slot (the fur's emission is the
  embers). `materials/wound.tres` has a PROVENANCE row (appended at the end).
- **vein_sparker:** an old break, healed over, on top of the tail's root, in the `scale` slot. The **starlight
  decision**: the coil's surface glow broke palette.json's point-source rule (1.4% of a filled review frame). The
  charge now glows only at the 11 spine tips plus four small sparks on the coil's flanks, which is 0.30%. The coil's
  last third is bare copper.
- Each build has `build_mesh()` (the rig and mesh without Blender), and `main()` uses it.
- The sheets (act1/raid_hound.md, flue_moth.md, vein_sparker.md) are amended, and so are the task file's notes.
- **Camera side:** the marks face forward and up, a little toward **-x**. That is the battle camera's side in every
  creature source (the stand-in yaw is 90; BattleCamera is at (0.6, 2.8, 8.4)). The brief's "+x" is the review and
  portrait side (yaw 35 and yaw 30 from the +x front), so each mark is placed where both views see it.

## Gates (all run in the worktree)
- `verify_blender_builds.py --job creature_flue_moth --job creature_raid_hound --job creature_vein_sparker`: all
  identical (4, 5 and 4 files). No other job shares their sources (common/ is untouched).
- `unittest tools.tests.test_creatures tools.tests.test_blender_builds`: 48 OK, GroundedClipsTest included.
- validate_data: 0 errors (1 warning that was already there, haluna shrine_offering). taskboard --check: OK.
- gdlint and gdformat --check: clean.
- Godot `--import`, then `run_tests.tscn -- --filter=creature`: 75 run, 1 failed. The failure is the known
  test_creature_portraits missing-PNG one.
- Animation channels and node rests are bit-identical to before for all three, so contact times and grounding are
  unchanged.

## In progress
- None. M3-CRE-650 stays `doing` for the coordinator's self-render.

## Exact next step
1. Merge this branch into `claude/creatures`.
2. Self-render `creature_raid_hound`, `creature_flue_moth`, `creature_vein_sparker` and their portraits. Check in each
   that the mark reads at battle distance, and in the vein sparker that the coil's sparks read as points. Then
   re-baseline those shots, re-bake those three portraits, and move the task to review (reviewer: art).

## Known issues
- The numpy/PIL previews are flat-shaded estimates, not engine renders. The engine's bloom may make the marks read
  more strongly. If a mark still reads weakly at battle distance in the real render, raise its slot's emission
  energy; the gallery ray uses 1.8.
- The moth's brow mark sits just above its near eye. At the portrait angle it could read as eye-shine; check this in
  the render.
- The old baselines and portraits for these three are stale until the re-render.

## Files touched
assets_src/creatures/{raid_hound,flue_moth,vein_sparker}/ (build scripts and materials.json),
assets/creatures/{raid_hound,flue_moth,vein_sparker}/ (GLBs and materials, plus flue_moth/materials/wound.tres),
assets/PROVENANCE.md (one row appended), docs/kb/art/creatures/act1/{raid_hound,flue_moth,vein_sparker}.md,
docs/kb/tasks/M3/M3-CRE-650-act1-regulars-audit-and-weak-points.md, this handoff.

Previews (scratch, not committed):
/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-650/raid_hound_final.png,
/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-650/flue_moth_final.png,
/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-650/vein_sparker_final.png
(each with a `_zoom.png` of the battle-scale read).
