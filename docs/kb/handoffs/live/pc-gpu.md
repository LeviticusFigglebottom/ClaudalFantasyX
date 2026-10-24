# Live log: pc-gpu environment

Seeded by the Lead on 2026-10-23. **This environment owns this file** (CLAUDE.md §7a). It's updated on each `gpu/*`
branch after every finished item, and it replaces `docs/kb/qa/gpu/2026-10-23-pc-queue-progress.md` as the canonical
record. The newest copy is on the most recently pushed `gpu/*` branch.

> **Current session:** `session_01UFcBRsk9M9EKtxJKdBU2mB` (Remote Control on this PC). It took over from
> session_01778wbLbDFnRRLTKjnawv3T on 2026-10-23. The Lead is cloud session `session_019iimsngAgPLEram1wcbLpE`.
> **This copy, on `gpu/m2-rnd-04-drownbell-vfx`, is the newest.**

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
  (`git worktree add --detach <dir> origin/claude/undertow-lead-handoff-423ixt`, then import it), and remove the
  worktree afterwards. For a drift that covers only uncommitted work: `git stash`, capture, `git stash pop`.
- **Metrics in `tools/`:** `mote_metrics.py` (glimmer halos/streaks), `aa_shimmer.py --ghost`, `sss_probe_metrics.py`,
  `perf_budget.py`, plus `tools/gpu_bench/eave_glow.tscn` and `lod_pop.tscn`.
- **GPU → min-spec projection:** RTX 3060 about 2.3–2.8× this card (the Lead uses ~3× for the Undertow); GTX 1060
  4.2–5.0×.

### Rules (from the Lead)

- **Branches:** work on new `gpu/*` branches only, one per item, cut from
  `origin/claude/undertow-lead-handoff-423ixt`. That's the integration branch from 2026-10-23; it replaces
  `claude/new-session-mj8c3c`, which is frozen at a504072. Never push to someone else's branch.
- **Baselines:** never overwrite lavapipe baselines; list the shots that drift. The Lead re-approves on lavapipe.
- **Gate scope** (CLAUDE.md §3): run only the checks a change can break, and say in the report what was skipped.
- **Tasks:** claim a task in its file (`status: doing`, `owner_session`) in the first commit, and set `status:
  review` at the end.
- **Asha's materials change only through `assets_src/characters/asha/write_materials.py`.** Run it with plain Python,
  normalise CRLF to LF, and commit the script and its outputs together. A hand edit to a `.tres` fails the Blender
  rebuild gate.
- **Commit trailers:** messages end with the Co-Authored-By and Claude-Session lines the harness gives.
- **Queue:** message the Lead when two queue items remain. Keep this file current after every item.
- **Reports to the Lead:** after each pushed item, send the branch, the commit and the shots that drift.
- **Standing interrupt:** GPU checks before a lavapipe re-approval (captures at High and Ultra, compared against the
  base). These jump the queue.
- **Gate before every push:** validate_data, the tools unittests, lint and format, and Godot tests filtered to the
  area.

### Gotchas

- `tests/screenshots/capture.tscn` hung for 100 minutes on the Undertow shots here. Use `capture_preset.tscn` with
  `timeout`.
- **Line endings:** Python generators and gdformat write CRLF on Windows. Normalise to LF before committing.
- `water_look_probe.tscn` needs its `--out` folder to exist, or it errors and hangs.
- **The compute body's Godot traps** (undertow.md, "Gotchas"):
  - A `.glsl` file expands one include level, and re-imports only when it changes itself, so run
    `tools/rendering/gen_undertow_compute.py`.
  - `get_cam_projection()` is already corrected.
  - Set `Texture2DRD` RIDs on the main thread.
  - Detach textures before freeing them.
- **New capture options:** `--add-box=x,y,z,sx,sy,sz` (a test box) and `--node-set=Path:prop=value` (e.g.
  `Storm:half_res_compute=false` for the SubViewport A/B).
- **`capture_preset --mat-set` doesn't reach the Undertow body.** The body renders in the half-res SubViewport.
  Edit undertow.json for the run instead, and restore it afterwards.
- **The capture size:** `capture_preset` writes 960×540 by default and 1920×1080 with `--scale=2`. Compare like with
  like.
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
| gpu/m2-rnd-04-drownbell-vfx | **M2-RND-04 in review** (reviewer Environment; contains gpu/m2-rnd-03-battle-vfx, so merge that first) | The Drownbell's set piece: `BattleBossVfx`, attached through BattleVfx (no controller edit), playing every battle_ctb.md hook point. That's the toll telegraph and shockwave, rim sparks and the break, polyp lights and mend streams, Ilun's Floodnet, and the bell's seaward release. **The flood rig** is a WaterSurface (the lagoon_low_sun look) that rises −0.7 → +0.6 m over 8 s; it's the battle's one `hymn_water_level` publisher, and the key light and sea-glow follow it. **High 1440p, worst frame 2.0 ms** (Ultra 3.4). Reduced motion is covered. Also fixes RND-03's retry leaving the old view. **Finding:** nothing shipped drives the weather clock `hymn_wind_time` (only test rigs do); the rig runs it in the boss battle. One pending shot: `docs/kb/qa/gpu/2026-10-24-rnd-04-pending-shots.json`. Docs: battle_vfx.md "The Drownbell" |
| gpu/m2-rnd-02-underwater | **M2-RND-02 in review** (reviewer Environment) | Underwater look: `UnderwaterRig` (`game/world/water/underwater/`) gives a per-pixel absorption and scatter post with a wave-following waterline (a meniscus, no pop at the crossing); the underside (the Snell window with the refracted sun, and TIR); volumetric god rays on High and Ultra; marine snow; Rhen's oil-lamp lantern. The light level follows the scene's sun, so night dives are dark. Tiers: `tiers.underwater` in graphics_presets.json. **The rig costs +0.32 ms at High 1440p; the whole frame is 1.1–1.5 ms.** On Low: +0.14 ms. gpu_bench and capture_preset now apply every system tier (`GraphicsRuntime.apply_system_tiers`), so their Low, Medium and Ultra captures of water scenes can change. Three new pending shots: `docs/kb/qa/gpu/2026-10-24-rnd-02-pending-shots.json`. Art sign-off is **M2-ART-02**. Docs: `docs/kb/tech/underwater.md` |
| gpu/fp-10-keylight-check | pushed (from origin/claude/m2-slice 0408806; Lead request) | M2-FP-10 GPU check. No artefacts; cost ≤ 0.03 ms; Haluna sun at bias 1.0, no face regression. H05's 74° sun leaves the face in brow and nose shadow, so set `key_pitch_deg` 30 on H05 and H06. **Layer 20 conflict** between the key light and the Undertow half-res body. New tool `tools/gpu_bench/keylight_probe.tscn`. Report: `docs/kb/qa/gpu/2026-10-24-fp-10-keylight.md` |
| gpu/m2-rnd-03-battle-vfx | **M2-RND-03 in review** (reviewer Environment) | Battle VFX library: `BattleVfx`, listen-only (one controller line). The data (`effects.json`) holds 14 effects: element hits, Lamp Dive, Shallows Verse, Read, heal, status, KO into released glimmer, and the opening flashes. Flashes are photosensitivity-capped and below the HUD; reduced motion is supported. The worst 3v3 burst costs +0.04 ms at High 1440p. Battle shots move ≤ 0.0022 on the GPU (under the gate). Docs: `docs/kb/tech/battle_vfx.md` |
| gpu/m1-rnd-22-prewarm | **M1-RND-22 in review** (reviewer Environment) | Prewarm hitch floor. Battle transitions now 34–46 ms on every preset (before 308–371). The floor was a test material in every transition, other presets' tier variants, and variant compiles on first draw. Fixes: the `preset_tier` filter, a boot warm-up of resident shaders, the FSR2 stage size (no more FFX error spam), and the router frame-0 timing. Zone and storm entries are 142–312 ms behind the fade: ADR 0029 (proposed). Threaded loads and harvest were tried and crash Godot, so they were reverted. Report: `docs/kb/qa/gpu/2026-10-24-rnd-22-prewarm.md` |
| gpu/m2-rnd-01b-undertow-compute | **M2-RND-01 in review** (contains gpu/m2-rnd-01-undertow; merge that first) | Compute body (ADR 0028): exact occlusion; High body_scale 0.35 (motion-checked). The storm's own cost is 0.58–0.80 ms at High 1440p. All 5 Undertow shots drift. Follow-up task M2-RND-05. Report: m2-rnd-01-start.md, the last two sections |
| gpu/m2-rnd-01-undertow | **WIP, not merged** (task `doing`) | M2-RND-01. Earlier: the wall foot, the sea's storm response, joined flanks, the half-res body and 3-octave multiple scattering. This session: noise-warped striations, fringe billows with sun-ward shading, softer sea streaks, and the wound-stipple fix (skin step refinement). High 1440p: Day 2.56, Eye 3.11 ms. All 5 Undertow shots drift. Integration branch merged in (a504072). Report: `docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md` |
| gpu/qa-08-asha-recheck | task `review` (reviewer: character) | M1-QA-08: Asha GPU recheck at 2× High and Ultra (96a6585 / 9a133ee). Neutral passes; smile passes on shading but reads as a smirk at 1×; grief still fails on two Character mouth faults (black rim, peg teeth). CHR-12: crown, lid band (R:B 3.7 against 2.0–2.5) and smile eyes fail; lip bow and skin pass. ADR 0024 check 2 confirmed. Report: `docs/kb/qa/gpu/2026-10-24-qa-08-asha.md` |
| gpu/qa-05d-asha-recheck | superseded by qa-08 | The first cut of the same recheck, before the task file existed. Don't merge. |
| gpu/rnd-21-mouth-fill | merged (96a6585) | M1-RND-21: the `mouth` shader family's cavity bounce. Report: `docs/kb/qa/gpu/2026-10-23-rnd-21-mouth-fill.md` |
| gpu/rnd-18-20-followups | in review; Lead's lavapipe check ci35 | RND-18 S1: deep lift gated by SSS (no drift). RND-20 S1: measured, Haluna stays at 1.0 (bias is in texels); rule in character_shading.md. Filed M1-ENV-08. Report: `docs/kb/qa/gpu/2026-10-23-rnd-18-20-followups.md` |
| gpu/qa-07-windows-interpreter-test | new, not merged | Files M1-QA-07 (the Windows-only test failure), Lead request |
| gpu/env-03-vegetation-v2, gpu/rnd-17-dusk-motes-v2 | merged + lavapipe-approved (c940d77) | ENV-03 v2 (final-cut-only LOD fade, Shelter enum/mask, ShaderGlobals); RND-17 v2 |
| gpu/chr-04-materials, gpu/qa-05b-asha-recheck | pushed; not ancestors of the integration branch (the Lead took their content earlier, per the queue log; check before deleting) | CHR-04 material half; QA-05b note |
| gpu/env-03-vegetation, gpu/rnd-17-dusk-motes, gpu/perf-sweep, gpu/qa-05-asha-gpu, gpu/qa-05c-asha-final, gpu/results-2026-10-23, gpu/rnd-07-presets, gpu/rnd-08-water-glimmer, gpu/rnd-09-undertow-shading, gpu/rnd-10-undertow-perf, gpu/rnd-11-undertow-params, gpu/rnd-12-sky, gpu/rnd-15-prewarm, gpu/rnd-18-sss-crest, gpu/rnd-20-smile-terminator | merged | Earlier items; reports under `docs/kb/qa/gpu/` |
| gpu/grief-mouth-fill | **local only, abandoned** | An empty branch plus `stash@{0}` (a stage FillLight); superseded by the RND-21 shader family. Safe to delete. |

## Unfinished queue, in order (exact next step first)

**The queue is empty** (2026-10-24): every item is in review. Waiting for the Lead to top it up. Merge notes:
- RND-03 goes before RND-04.
- The RND-02 and RND-04 branches each add an ownership.md row after the same line (a trivial conflict).
- RND-22 and RND-04 both touch prewarm_materials.json.


1. **M2-RND-01: in review** (reviewer Environment), on `gpu/m2-rnd-01b-undertow-compute`; merge
   `gpu/m2-rnd-01-undertow` first.
   - High `body_scale` is 0.35 (motion-checked); Medium stays at 0.5.
   - The storm's own cost is 0.58–0.80 ms at High 1440p, ~2–2.4 ms projected on an RTX 3060.
   - All 5 Undertow shots drift: re-approve them on lavapipe.
   - The storm-event criteria moved to **M2-RND-05** (todo).
2. **M1-RND-22: in review** (`gpu/m1-rnd-22-prewarm`). Battle transitions are in budget. Follow-ups are in ADR 0029: the
   export shader baker (needs export templates on the PC), a SceneState harvest for big zones, and slicing the
   boot warm-up.
3. **M2-RND-03: in review** (`gpu/m2-rnd-03-battle-vfx`). Next passes are in battle_vfx.md: an art pass for the pale effects, and contact-frame timing once body clips exist.
4. **M2-RND-02: in review** (`gpu/m2-rnd-02-underwater`). The Lead adds the 3 pending shots on lavapipe. Open:
   - the glimmer-motes boost underwater (Art's call, in M2-ART-02);
   - caustics on characters;
   - a splash at the crossing.
5. **M2-RND-04: in review** (`gpu/m2-rnd-04-drownbell-vfx`). Next passes are in battle_vfx.md: the arena's sunset grade, sinking the bell, rim crack decals, and re-measuring battle transitions once M1-RND-22 merges. Originally: Drownbell boss VFX and flood rig. Read the First Playable boss data first (session
   session_01ELR13ohWMPrprcpcgLa7UR, branch `claude/first-playable`).
- **Standing:** GPU checks of shots before the Lead re-approves lavapipe baselines.
- **Open findings to route** (filed or noted, not this queue):
  - M1-ENV-08: the vegetation LOD hysteresis hole.
  - The M2 dialogue key light: a few metres of shadow range, bias 4.5 (character_shading.md).
  - Teeth albedo: M1-CHR-11.

## Local-only state (not in git)

- **This session's scratch:** captures, CSVs and the helper scripts `bench.sh`, `cap.sh`, `cap5.sh`, `capd.sh` and `jset.py`.
  It's in `C:/Users/Aaron/AppData/Local/Temp/claude/C--Users-Aaron/d3383506-5a83-49e1-8dcf-15422406b087/scratchpad/m2rnd01` and `.../rnd02`. Temporary.

None of it is needed: everything quoted in the reports can be reproduced from the commands in them.
- **`C:\Users\Aaron\Hymn_Playtest`:** a separate clone for the human's playtest, with untracked `PLAY.bat` and
  `EDITOR.bat`. Delete it after the playtest.
- **`C:\Users\Aaron\hymn_shots_gpu`:** 87 GPU screenshots (base body, Asha and others) from early QA passes.
  Scratch.
- **Scratch renders and CSVs:** `C:\Users\Aaron\chr04`, `rnd12`, `m2rnd01` (including `cur/undertow_day_ch08.png`, the
  2× capture that shows the two defects above), `rnd15`, `rnd17`, `rnd18`, `qa05b` and `env03`, plus the old
  session's scratchpad (temporary).
- **`stash@{0}`** and the local branch `gpu/grief-mouth-fill` in `C:\Users\Aaron\hymn_gpu`: abandoned (see above).
