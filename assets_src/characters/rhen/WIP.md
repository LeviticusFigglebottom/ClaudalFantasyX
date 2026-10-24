# Rhen build: unfinished work (not a task yet)

Started by the Character agent (worktree-agent-af72bd4d8af383b91) on 2026-10-23, then stopped when the Lead moved Rhen to the dedicated Characters session. No task id was filed; M2-CHR-01 was free across all branches at the time.

## What's here
These are first-pass sources on Asha's pipeline. They use the MPFB2 CC0 donor only (ADR 0021).

| File | Contents |
|---|---|
| `rhen_params.json` | Body block and face sliders (rhen.md §1, §6) |
| `rhen_hair.py` | Short ruffled cards, crown whorl flow |
| `rhen_costume.py` | Open one-sleeve jacket, undershirt, gauntlet, trousers, belt, strap, wraps, sandals |
| `rhen_props.py` | Lantern, crossed reef-hooks, tether coil |
| `rhen_textures.py` | Skin through `asha_textures.skin_maps`, plus Rhen's cloth atlas |
| `build_rhen.py.wip` | Blender build. It reuses build_asha's helpers. |
| `build.sh.wip` | (parked by the Lead: the tools manifest test rejects a build.sh that calls an unlisted script) Blender at 2 threads, then textures, then materials |

## Where it got to
- **Blender build.** It ran once and succeeded in 28 s at 2 threads. The output was 53,300 LOD0 tris (rhen.md target 58,500) and 24,705 at LOD1, with `rhen.glb` at 4.06 MB. The outputs were deleted, since they had no PROVENANCE rows yet.
- **Textures.** `rhen_textures.py` has never been run.

## To resume
1. Rename `build_rhen.py.wip` to `build_rhen.py` and `build.sh.wip` to `build.sh`, and add the `rhen` job to `tools/dev/blender_builds.json`, in the same commit.
2. Add a `rhen` job to `tools/dev/blender_builds.json`:
   - `"threads": 2`;
   - sources: `rhen/**`, `asha/**`, `base_body/**` and mpfb2;
   - runs: build_rhen, then rhen_textures, then write_materials.
3. Apply `WIP_asha_textures_hooks.patch` (`git apply`). It adds PREFIX, SKIN_BASE, FRECKLES and ALBEDO_POST to asha_textures. Their defaults are Asha's values, so it should change nothing for her. Re-verify with `--job asha`, which must stay at 44 identical.
4. Still to write:
   - `write_materials.py`: Rhen's materials. Eye, detail, hair-atlas and lash maps can reference Asha's textures.
   - The `.import` files, with mipmaps on.
   - PROVENANCE rows.
   - A stage scene that reuses `AshaStage`.
   - New shot ids, with baselines approved on lavapipe.
   - `tools/tests/test_rhen.py`.
5. Known trim: the rope coil is 2,688 tris. Cut it to 5 sides and 20 segments, about 1,600.
