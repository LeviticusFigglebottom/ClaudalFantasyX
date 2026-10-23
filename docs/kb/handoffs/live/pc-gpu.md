# Live log: pc-gpu environment

Seeded by the Lead on 2026-10-23. **This environment owns this file** (CLAUDE.md §7a). It's updated on each `gpu/*`
branch after every finished item, and it replaces `docs/kb/qa/gpu/2026-10-23-pc-queue-progress.md` as the canonical
record. The newest copy is on the most recently pushed `gpu/*` branch.

> **HANDOFF (2026-10-23).** session_01778wbLbDFnRRLTKjnawv3T stopped here at the Lead's request. The project moves to
> a new account, with a new Remote Control session on this same PC as the GPU worker. **This copy, on
> `gpu/m2-rnd-01-undertow`, is the newest.** Every `gpu/*` branch is pushed. The only local-only state is listed under
> "Local-only state" below; none of it is needed.

## PC setup for a new session

- **Machine:** Windows 10 Home, AMD RX 9070 XT, 16 GB RAM, user `Aaron`.
  - Shells: PowerShell 5.1 and Git Bash.
  - Python 3.14 on PATH as `python`, with gdtoolkit (`python -m gdtoolkit.linter` / `.formatter`).
- **Clone:** `C:\Users\Aaron\hymn_gpu` (origin github.com/LeviticusFigglebottom/ClaudalFantasyX).
- **Godot:** `C:\Users\Aaron\godot_463\Godot_v4.6.3-stable_win64_console.exe` (4.6.3-stable official, Forward+/Vulkan).
  It isn't on PATH; set `G=/c/Users/Aaron/godot_463/Godot_v4.6.3-stable_win64_console.exe` in Git Bash.
- **The monitor must stay physically ON.** If the display is off or asleep, Vulkan swapchain creation fails, and every
  windowed run (gpu_bench, capture_preset) errors out.
  - Run `powershell -ExecutionPolicy Bypass -File tools/dev/keep_display_on.ps1 -Hours 10` in the background. It calls
    SetThreadExecutionState.
  - It stops sleep, not a human pressing the monitor's power button.
- **Load cap:** keep the cumulative CPU, memory and GPU load at or below ~75 %. Run benchmarks and captures one at a
  time, never in parallel. Kill only PIDs you started (CLAUDE.md §8a).

### Commands

```bash
# after any merge of the integration branch: re-import first (a stale class cache fails ~260 tests)
$G --headless --path . --import
# tests, filtered to the area you touched (check the "Tests: N run" count: a file that fails to parse just drops out)
$G --headless --path . res://tests/run_tests.tscn -- --filter=<area>
python tools/validate_data.py; python tools/taskboard.py --check
python -m gdtoolkit.linter game tests; python -m gdtoolkit.formatter -l 120 --check game tests

# GPU frame time (windowed, never --headless). Full option list at the top of tools/gpu_bench/gpu_bench.gd.
$G --path . --audio-driver Dummy --disable-vsync res://tools/gpu_bench/gpu_bench.tscn -- \
  --scene=res://game/levels/_tests/undertow/undertow_test.tscn --camera=<path> \
  --presets=high --res=2560x1440 --csv=C:/abs/out.csv [--png-dir=C:/abs/dir --hold-storm --undertow-half=0.5]

# GPU screenshots of manifest shots at a preset (use this, not tests/screenshots/capture.tscn, for Undertow shots)
$G --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync res://tools/gpu_bench/capture_preset.tscn -- \
  --shots=id1,id2 --preset=high --out=C:/abs/dir [--scale=2 --hold-storm \
  --manifest=res://docs/kb/qa/gpu/2026-10-23-rnd-09-pending-shots.json \
  --light-set=prop=value,... --mat-set=uniform=value|#rrggbb,... --push-override=key=value]

# drift between two captures: linear-light RMSE, the same as the lavapipe gate
python -c "import sys; sys.path.insert(0,'tools/screenshots'); import compare, pngio; \
  print(compare.rmse_linear(pngio.read(sys.argv[1]), pngio.read(sys.argv[2])))" before.png after.png
```

- **Base vs branch drift:** capture both in a detached worktree of the base
  (`git worktree add --detach <dir> origin/claude/new-session-mj8c3c`, then import it), and remove the worktree
  afterwards.
- **Metrics in `tools/`:** `mote_metrics.py` (glimmer halos/streaks), `aa_shimmer.py --ghost`, `sss_probe_metrics.py`,
  `perf_budget.py`, plus `tools/gpu_bench/eave_glow.tscn` and `lod_pop.tscn`.
- **GPU → min-spec projection:** RTX 3060 about 2.3–2.8× this card (the Lead uses ~3× for the Undertow); GTX 1060
  4.2–5.0×.

### Rules (from the Lead)

- **Branches:** work on new `gpu/*` branches only, cut from `origin/claude/new-session-mj8c3c`. Never push to someone
  else's branch.
- **Baselines:** never overwrite lavapipe baselines; list the shots that drift. The Lead re-approves on lavapipe.
- **Gate scope** (CLAUDE.md §3): run only the checks a change can break, and say in the report what was skipped.
- **Tasks:** claim a task in its file (`status: doing`, `owner_session`) in the first commit, and set `status:
  review` at the end.
- **Asha's materials change only through `assets_src/characters/asha/write_materials.py`.** Run it with plain Python,
  normalise CRLF to LF, and commit the script and its outputs together. A hand edit to a `.tres` fails the Blender
  rebuild gate.
- **Commit trailers:** messages end with the Co-Authored-By and Claude-Session lines the harness gives.
- **Queue:** message the Lead when two queue items remain. Keep this file current after every item.

### Gotchas

- `tests/screenshots/capture.tscn` hung for 100 minutes on the Undertow shots here. Use `capture_preset.tscn` with
  `timeout`.
- **Line endings:** Python generators and gdformat write CRLF on Windows. Normalise to LF before committing.
- `water_look_probe.tscn` needs its `--out` folder to exist, or it errors and hangs.
- **Shell traps:**
  - Don't run `cat > file` without input; it blocks on stdin.
  - Inline heredoc Python with Windows backslashes or `\n` escapes breaks. Write a `.py` file instead.
- **Godot behaviours:**
  - Transparent materials write no motion vectors.
  - TAA destroys a transparent SubViewport's alpha.
  - `VISIBILITY_RANGE_FADE_SELF` alpha-blends the instance (it isn't a dither).
  - `RenderingServer.global_shader_parameter_get` and `shader_get_parameter_default` don't work at runtime or headless.
    Use `ShaderGlobals` (game/core/shader_globals.gd) for the globals.
  - A shader uniform default must be a literal.
  - `shadow_normal_bias` is in shadow texels, not metres.
- The Undertow half-res body uses visual layer 20; don't use it for anything else in a storm scene.
- **Known Windows-only failure:** `tools/tests/test_blender_builds.py::test_python_runs_use_this_interpreter`, filed
  as M1-QA-07.

## Branches (all pushed)

| Branch | State | Content |
|---|---|---|
| gpu/m2-rnd-01-undertow | **WIP, not merged** (task `doing`) | M2-RND-01: wall foot / sea storm response / joined flanks; half-res body (High 4.94 → 2.27 ms); 3-octave multiple scattering; integration branch merged in (d5cbda2). WIP note and exact next step in the task file. Reports: `docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md` |
| gpu/rnd-21-mouth-fill | in review (character); Lead running asha shots + Blender job | M1-RND-21: `mouth` shader family with a cavity bounce, all heroes; grief interior median luminance 0.0121 → 0.0174. Drift asha_face_grief 0.0023. Report: `docs/kb/qa/gpu/2026-10-23-rnd-21-mouth-fill.md` |
| gpu/rnd-18-20-followups | in review; Lead's lavapipe check ci35 | RND-18 S1: deep lift gated by SSS (no drift). RND-20 S1: measured, Haluna stays at 1.0 (bias is in texels); rule in character_shading.md. Filed M1-ENV-08. Report: `docs/kb/qa/gpu/2026-10-23-rnd-18-20-followups.md` |
| gpu/qa-07-windows-interpreter-test | new, not merged | Files M1-QA-07 (the Windows-only test failure), Lead request |
| gpu/env-03-vegetation-v2, gpu/rnd-17-dusk-motes-v2 | merged + lavapipe-approved (c940d77) | ENV-03 v2 (final-cut-only LOD fade, Shelter enum/mask, ShaderGlobals); RND-17 v2 |
| gpu/chr-04-materials, gpu/qa-05b-asha-recheck | pushed; not ancestors of the integration branch (the Lead took their content earlier, per the queue log; check before deleting) | CHR-04 material half; QA-05b note |
| gpu/env-03-vegetation, gpu/rnd-17-dusk-motes, gpu/perf-sweep, gpu/qa-05-asha-gpu, gpu/qa-05c-asha-final, gpu/results-2026-10-23, gpu/rnd-07-presets, gpu/rnd-08-water-glimmer, gpu/rnd-09-undertow-shading, gpu/rnd-10-undertow-perf, gpu/rnd-11-undertow-params, gpu/rnd-12-sky, gpu/rnd-15-prewarm, gpu/rnd-18-sss-crest, gpu/rnd-20-smile-terminator | merged | Earlier items; reports under `docs/kb/qa/gpu/` |
| gpu/grief-mouth-fill | **local only, abandoned** | An empty branch plus `stash@{0}` (a stage FillLight); superseded by the RND-21 shader family. Safe to delete. |

## Unfinished queue, in order (exact next step first)

1. **M2-RND-01** (`gpu/m2-rnd-01-undertow`, WIP). The exact next step is in
   `docs/kb/tasks/M2/M2-RND-01-undertow-production.md`, under "WIP handoff":
   - Noise-warp the striation helix.
   - Add billowy surface detail with sun-ward derivative shading.
   - Fix two defects from the fresh capture: the hard straight sea wind streaks and the teal wound stipple.
   - Then the compute-pass occlusion inside the volume.
   - Undertow High 1440p is AT RISK on an RTX 3060 (~3×).
2. **M1-RND-22:** the prewarm hitch floor, measured at Low, High and Ultra. If 50 ms is impossible, draft an ADR
   proposing a SPEC §4.2 clarification. The earlier finding (RND-15): the floor is ~230–310 ms of stage set-up plus
   single heavy shader compiles. The fixes are the shader baker or a boot-time stage.
3. **M2-RND-03:** the battle VFX library. SPEC v1.2 power tiers: lesser, greater and grand. Never use -ra/-ga style
   suffixes; Narrative sets the in-game names.
4. **M2-RND-02:** underwater rendering: fog volume, god rays, particulate, caustics on characters, Rhen's lantern as
   the hero light.
5. **M2-RND-04:** Drownbell boss VFX and flood rig. Read the First Playable boss data first (session
   session_01ELR13ohWMPrprcpcgLa7UR, branch `claude/first-playable`).
- **Standing:** GPU checks of shots before the Lead re-approves lavapipe baselines.
- **Open findings to route** (filed or noted, not this queue):
  - M1-ENV-08: the vegetation LOD hysteresis hole.
  - The M2 dialogue key light: a few metres of shadow range, bias 4.5 (character_shading.md).
  - Teeth albedo: M1-CHR-11.

## Local-only state (not in git)

None of it is needed: everything quoted in the reports can be reproduced from the commands in them.
- **`C:\Users\Aaron\Hymn_Playtest`:** a separate clone for the human's playtest, with untracked `PLAY.bat` and
  `EDITOR.bat`. Delete it after the playtest.
- **`C:\Users\Aaron\hymn_shots_gpu`:** 87 GPU screenshots (base body, Asha and others) from early QA passes.
  Scratch.
- **Scratch renders and CSVs:** `C:\Users\Aaron\chr04`, `rnd12`, `m2rnd01` (including `cur/undertow_day_ch08.png`, the
  2× capture that shows the two defects above), `rnd15`, `rnd17`, `rnd18`, `qa05b` and `env03`, plus the old
  session's scratchpad (temporary).
- **`stash@{0}`** and the local branch `gpu/grief-mouth-fill` in `C:\Users\Aaron\hymn_gpu`: abandoned (see above).
