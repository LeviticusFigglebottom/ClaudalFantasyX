# Handoff: creatures track (art), 2026-10-27, Act II bosses after their first render (worktree agent)

Branch `worktree-agent-a1a26860cbf12c949`, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY).
Not pushed. The Lead merges it and records the claim.

## Done
- **M3-CRE-635**, to review (art). The details are in docs/kb/tasks/M3/M3-CRE-635-act2-boss-render-review.md.
  - **The Avalanche Ram** (`6650b4cb`): the head reads as a camelid's, not a duck's.
    - Long and narrow, with a soft rounded muzzle in the coat's colour. `laterite` is darkened only at the nose and
      lips.
    - Eyes at the sides under a soft brow, long upright ears, and the woolly cap kept.
    - The neck is slimmer.
    - The icicles are few and uneven, longest at the lock tips.
    - Rig, bones and clips unchanged. 15,179 -> 14,855 triangles.
    - GroundedClipsTest is green, and the hit still peaks at 0.10 s.
  - **The Wakefin** (`cadd3630`):
    - CreatureStage `show_floor` (default true) and a `flank_high` view.
    - A new shot, `creature_wakefin_body`, shows the whole fish with the floor hidden.
    - The eight spine wounds are longer, wider, torn-looking seams.
  - **Verify:** both jobs identical.

## In progress
- Nothing. The renders wait for the PC.

## Exact next step
1. Merge the branch.
2. RENDER-REQUEST on the PC: `creature_avalanche_ram`, `creature_wakefin`, `creature_wakefin_body` (new, no baseline).
3. View them:
   - the Ram's head must read as a woolback's (camelid), not a duck's or a dog's;
   - the lock fringe must not read as teeth;
   - the wounds must read on the Wakefin's body.
   Then approve the baselines (from a post-M3-CRE-630 render only) and fill the task's Review log.

## Known issues
- `test_creature_portraits` fails on this branch: the Act II rows have no bestiary portraits (request M3-CRE-634).
  This change didn't cause it.
- `tools.tests.test_screenshots` `test_repo_manifest_is_valid_and_baselined` fails until the Act II shots are
  baselined; it was already failing at `creature_lamp_engine`. `creature_wakefin_body` adds one more unbaselined
  shot.
- The wounds sit at the Wakefin's waterline (y about 0), so in battle they show only when it breaches. That matches
  its sheet; it is only a problem if the review wants them seen while it circles.
- The flat silhouettes were sketches without shading. The PC render is the real check of the head's read, especially
  in profile, where a long head can drift toward a dog's.

## Files touched
- **Ram:** `assets_src/creatures/avalanche_ram/build_avalanche_ram.py`, `materials.json` (the `_doc` only),
  `assets/creatures/avalanche_ram/avalanche_ram.glb`, `docs/kb/art/creatures/act2/avalanche_ram.md`.
- **Wakefin:**
  - `assets_src/creatures/wakefin/build_wakefin.py` and `assets/creatures/wakefin/wakefin.glb`;
  - `game/levels/_tests/creatures/creature_stage.gd` and `.json`;
  - the new `game/levels/_tests/creatures/shots/creature_wakefin_body.tscn`;
  - `tests/screenshots/shots.json` and `docs/kb/art/creatures/act2/wakefin.md`.
- **Unchanged:** materials `.tres` and PROVENANCE (no source path changed).
- **Task:** `docs/kb/tasks/M3/M3-CRE-635-act2-boss-render-review.md`; this handoff.
