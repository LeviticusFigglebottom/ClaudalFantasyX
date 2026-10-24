# Godot 4.7.2 port prep (2026-10-24)

Branch: **`gpu/godot-472-port`**. It's long-lived and isn't merged until the Lead calls it (the first M3 task, after the
M2 slice review; ADR 0032). It's cut from the integration branch and kept current by merging it in.
Machine: RX 9070 XT, Windows 10, 2560×1440. Worktree: `C:\Users\Aaron\hymn_472port`.
Earlier findings: `docs/kb/qa/gpu/2026-10-24-godot-472-port-check.md` (branch `gpu/godot-472-port-check`).

## Done on this branch

1. **`tools/dev/fetch_godot.py --official VERSION [--templates] [--dest DIR]`.**
   - It downloads the official Linux x86_64 editor and, with `--templates`, the export templates, from GitHub
     releases.
   - It checks each against the release's own `SHA512-SUMS.txt`, and refuses a mismatch or an unlisted file.
   - The Ubuntu-sysroot path for the pinned 4.6.3 is unchanged.
   - Tests: `tools/tests/test_fetch_godot.py`, offline.
2. **The 4.7 import-key churn, in one commit.** 4.7.2's importer adds three keys, at their defaults, to all 45
   scene `.import` files: `gltf/texture_map_mode=0`, `array_mesh/deduplicate_surfaces=true` and
   `mesh_library/use_node_names_as_mesh_names=false`. A second `--import` logs 0 errors, and project.godot isn't
   touched by a headless import.

## Verified on the PC

- **The official files.** `Godot_v4.7.2-stable_linux.x86_64.zip` and `Godot_v4.7.2-stable_export_templates.tpz`
  match `SHA512-SUMS.txt`. So does the Windows editor already in `C:\Users\Aaron\Tools\godot-4.7.2`
  (`Godot_v4.7.2-stable_win64.exe.zip`).
- **The templates are installed** in `%APPDATA%\Godot\export_templates\4.7.2.stable`.
- **The suite.** The full Godot suite on 4.7.2, headless: **1451 run, 0 failed**. Run windowed on the GPU, these
  filters all pass:
  - `character` 17, `undertow` 51, `underwater` 5, `glimmer` 36, `water` 31 and `prewarm` 15.
  - That covers the compute storm body, the mouth bounce pass's `light()` built-ins (M1-RND-24) and the
    underwater post.
- **A baked release export** (`Windows Perf`, shader baker on) through the slice sweep, High:

| Segment (hidden worst / whole entry ms; visible worst) | 4.7.2 baked, first launch | 4.7.2 baked, second | 4.6.3 baked (M1-RND-29), first / second |
|---|---|---|---|
| Launch (behind the card) | 612 / 5602; 0.7 | 243 / 1978; 0.6 | 542 / 5242 · 226 / 1907 |
| Haluna Beach | 244 / 1372; 5.2 | 319 / 2690; **38.7** | 143 / 1257 · 272 / 2430 |
| Tideline battle | 153 / 549; 6.4 | 153 / 641; 7.3 | 123 / 553 · 105 / 658 |
| Shell Shrine | 201 / 563; 1.3 | 161 / 523; 1.2 | 146 / 507 · 141 / 501 |
| Drownbell battle | 107 / 484; 5.0 | 363 / 996; 5.9 | 82 / 456 · 300 / 935 |

  On the baked build 4.7.2 is level with 4.6.3, within about 10%. One new thing: on the second launch, Haluna
  had a 38.7 ms visible frame. That's under ADR 0029's 50 ms, but 4.6.3 had 4.1; re-check it.

## Re-checks of the 4.6.3-era workarounds

| Workaround | On 4.7.2 |
|---|---|
| The `.glsl` importer expands only one level of `#include` (gen_undertow_compute.py flattens) | **Still needed.** A nested include fails to parse on both 4.6.3 and 4.7.2. |
| The process `delta` is capped at ~140–150 ms (ShaderPrewarm measures wall time; BootCard M2-ARC-05) | **Still capped** (port check: a 500 ms stall reports 138.6 ms). |
| Threaded loads crashed Haluna (RND-22: rejected) | **Not conclusive.** A probe of threaded registry loads racing a worker-thread Haluna instantiate completes 6/6 on both engines, so it doesn't reproduce the crash on 4.6.3 either. The original crash needed the real prewarm staging inside the router's entry. Re-test that path before relying on threaded loads. |
| FSR2 and transparent draws (M1-RND-26) | Moot: the bounce pass is now drawn only where a positional light reaches the mouth (gpu/m1-rnd-26-bounce-gate). |
| The shader baker needs a real renderer | **An export with `--headless` doesn't bake** (nothing happens, the .pck is 66 MB, and the first launch is fully cold: a 30 s boot and a 1.18 s visible frame). Export with a window: 94 MB, baked. The same is true of 4.6.3. |
| The editor re-saves project.godot | The same on 4.7.2: a windowed export dropped the pinned header comments. Revert it before committing. |

## Still to do (when the Lead calls the switch)
- The ADR that supersedes ADR 0001, and the SPEC, CLAUDE.md, CI and `fetch_godot.py`'s pin.
- project.godot's engine pin and feature tag.
- Re-approve every lavapipe baseline.
- Re-test the threaded-load path, and the 38.7 ms visible frame on Haluna's second launch.
- Keep this branch current by merging the integration branch in.
