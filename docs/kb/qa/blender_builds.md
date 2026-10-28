# Blender asset rebuild gate (M1-QA-02, ADR 0005)

Every Blender-generated asset must regenerate from `assets_src/` with the pinned Blender. This gate rebuilds them and compares each output with the committed file.

```bash
python3 tools/dev/fetch_blender.py                   # once: Blender 5.0.1+dfsg-5 sysroot (ADR 0008 style)
python3 tools/dev/verify_blender_builds.py           # jobs whose sources or outputs changed
python3 tools/dev/verify_blender_builds.py --all     # every job (~4.5 min on the 4-vCPU sandbox; Asha's textures are most of it)
python3 tools/dev/verify_blender_builds.py --job asha --keep /abs/dir   # keep the rebuilt files to diff
python3 tools/dev/verify_blender_builds.py --list
python3 tools/dev/verify_blender_builds.py --coverage-only   # no Blender: is every .glb and bpy script in a job?
```

`tools/ci_local.sh` runs it after the Python steps:

| Variable | Effect |
|---|---|
| `HYMN_SKIP_BLENDER=1` | skip the step |
| `HYMN_BLENDER_ALL=1` | run every job, not only the changed ones (the Lead's merge run) |
| `HYMN_BLENDER_BASE=<ref>` | base ref for change detection (default `main`, then `origin/main`; with neither, every job runs) |
| `HYMN_BLENDER_TIMEOUT=<s>` | bound on the whole step (default 1800); `HYMN_BLENDER_JOB_TIMEOUT` bounds each job (default 900) |
| `HYMN_BLENDER=<path>` | Blender to use (default: the fetch_blender.py wrapper, then `blender` on PATH) |
| `HYMN_BLENDER_REQUIRED=1` | fail instead of `SKIP` when Blender is missing or not the pin (the Lead's merge run, so a missing fetch never reads as green) |

Exit 3 (no Blender, or not the pinned 5.0.1) prints `SKIP`, as the screenshot step does when its render deps are missing. The coverage check runs first and needs no Blender, so an uncovered file fails even then. The CI workflow has a `blender` job that fetches the same package; it is `continue-on-error` until a run on the GitHub runner has matched.

## How it works

- **Jobs are data:** `tools/dev/blender_builds.json` lists, per job: `sources` (globs; `**` spans directories), `outputs` (globs of committed files), and `runs`. A run is an argv after `{blender}`, which expands to `blender --background --factory-startup --python-exit-code 1`, or after `{python}` (this interpreter), for a numpy/Pillow step that follows the job's Blender run. A job's first run is always a Blender run. `{scratch}` is a per-job temp dir the runs share.
- **The working tree is never written.** `assets_src/` is copied into a temporary root, and the builds run there with their usual relative paths. The scripts resolve `ROOT` from their own location, so even a script with a hard-coded output path writes into the copy. **Only `assets_src/` is copied** (`copy_into_sandbox`): a build that reads anything else (a palette in `game/data`, a `docs/kb` table) fails in the sandbox with a missing-file error. Add the folder to `copy_into_sandbox` if a build needs it.
- **Change detection:** a job runs when any path in its `sources` or `outputs` changed since `git merge-base <base> HEAD`, or is modified or untracked in the working tree.
- **Comparison:** every committed file that matches `outputs` must be rebuilt, and every rebuilt file that matches must be committed.
  - `identical`: the bytes are the same. This is the rule.
  - `tolerance`: a last resort, and **no job uses it since M1-QA-06** (pinned threads made every build deterministic). Only for a job that declares `"tolerance": {"abs", "attributes", "why"}`. The glTF JSON must be equal, and all buffer data must be byte-equal except float accessors of the named attributes (for example `TANGENT`), which may differ by `abs`. Positions, normals, UVs, weights, indices and images are never tolerated.
  - `DIFF`: anything else. The message names the glTF accessors that differ (`<mesh>.<ATTRIBUTE>`).
- **Known failures carry their signature** (M1-QA-06). `"expected_failure": {"task", "why", "kind", ...}` turns a failing job into `KNOWN`, which does not fail the gate, **only when it fails exactly as recorded**:
  - `"kind": "build_error"` with `"log_contains": "<a line of the build log>"`. The build must exit non-zero and its log must hold that line. A timeout, a different error, or a build that now runs and mismatches is a new failure.
  - `"kind": "mismatch"` with `"differs": {"<path>": ["<mesh>.<ATTRIBUTE>", ...]}`. The build must run, and exactly those files must differ, each in exactly those glTF accessors. The list comes from a full glTF diff (every accessor whose metadata or data differ, past any tolerance), not just the first difference. A new file, a new accessor (say `JOINTS_0` on base_body, whose sources Asha shares), or one that stopped differing is a new failure. Non-glTF files differ as `<bytes>`, and `<not produced>` or `<not committed>` mark a missing file.
  - **Content pin** (M1-NIT-01, review-sweep-J S1 on M1-QA-06). Accessor names alone cannot see a further change *inside* a listed accessor (say a `bb_donor` edit that moves base_body by centimetres). So a mismatch marker may carry `"rebuilt_sha256": {"<path>": "<sha256 of the rebuilt file>"}`, one per `differs` path, and **a `threads: 1` job must** (a single-threaded build is byte-stable, so the hash is reproducible; the manifest loader enforces it). Any other rebuilt hash is a new failure (`the rebuilt content changed`). base_body pins its three rebuilds (athletic `4523ba…`, heavy `58142e…`, slender `5da684…`; the same in 2 runs on 2026-10-23). After an understood source change, take the new hashes from `--report <file>.json` (`files[].rebuilt_sha256`).
  - `FAIL` lines say `NEW failure signature` and name what changed. Copy the printed `[...]` list into the marker only when the change is understood and tracked.
  - When the job passes again, the gate **fails** until the marker is removed, so a fix can't silently rot.
- **Threads are pinned** (M1-QA-06, Lead addition). Every Blender run gets `--threads N`: the job's `threads`, else `default_threads` (4). Blender's default is the host's CPU count, and two things depend on it:
  - **Tangent export races.** At 4 threads, base_body's rebuild varied from run to run: athletic `cbcee8…` or `4523ba…`, heavy `58142e…` or `06cf15…`. At `--threads 1`, every run was byte-identical (6 runs, 3 of them concurrent with other Blender jobs). This is the "1 vertex in 14.5k moves by 1e-4" that the TANGENT tolerance used to hide. It is the likely cause of the `vegetation` failure (palm_coconut_b.glb TANGENT) in another agent's full run. I could not reproduce that one: 38 default-thread vegetation rebuilds, up to 8 at once at load ~13, were all identical. Vegetation exports tangents the same way, though, and it matches its committed files at `--threads 1`. So **any job whose build exports tangents runs at `threads: 1`** (base_body and vegetation), and a unit test enforces it from `export_tangents=True` in the job's scripts. Single-threaded base_body costs ~45 s against ~35 s.
  - **Thread-count-dependent results.** Asha's body bakes (`asha_body_normal`, `_orm`, `_skinmask`) are stable at a fixed count but **different at 1 thread than at 4**. Her committed textures were built at 4, the sandbox's count, so the other jobs are pinned at 4. A runner with 2 or 8 vCPUs then rebuilds exactly what we committed.
    - **Unverified below 4 vCPUs** (M1-NIT-01, review-sweep-J S2 on M1-QA-06). "Never depends on the host's CPU count" is the intent, but every run so far was on this 4-vCPU box. A pinned `--threads 4` on a 2-vCPU host oversubscribes rather than changing the count, so it should match, but nobody has run it. To prove it: `taskset -c 0,1 python3 tools/dev/verify_blender_builds.py --job asha` (and `--job base_body`), then record the result here.
  - **Decision: deterministic builds, not tolerance.** base_body's TANGENT tolerance is removed, and no job declares one (a unit test checks). The tolerance mechanism stays in the code as a documented last resort.
  - **Owners' build scripts must match.** An asset rebuilt outside the gate with a different thread count can commit a variant that the gate then rejects. Request **M1-ENV-07**: vegetation builds at `--threads 1`, or drop exported tangents as the Haluna kit did (kit_common.py: Godot's `ensure_tangents` makes them on import). Request **M1-CHR-06**: base_body at `--threads 1`, and Asha's `build.sh` at `--threads 4`.
- **Coverage** (M1-QA-06, no Blender). Before any build, every `.glb` under `assets/` that git tracks (or would add) must match some job's `outputs`, and every `assets_src/**/*.py` that imports `bpy`, `bmesh` or `mathutils` must match some job's `sources`. Anything else fails the gate as `BLENDER UNCOVERED`, even when Blender is missing, unless `"coverage_exempt": [{"path": "<glob>", "why": "..."}]` lists it. The list is empty today. `--coverage-only` runs just this check.
- The pinned version is checked from `blender --version` against `blender_version` in the manifest. A unit test keeps `blender_deb` equal to `PINNED_DEB` in `fetch_blender.py`, and another checks that every Blender `.glb` row in `assets/PROVENANCE.md` is covered by a job.

## State on 2026-10-23, M1-QA-06

| Job | Owner | Time | Result |
|---|---|---|---|
| `base_body` (3 variants), `--threads 1` | character | 45 s | **KNOWN (M1-CHR-05), mismatch**, byte-stable run to run now: all three `.glb` differ in exactly `NORMAL`, `POSITION`, `TANGENT` and `indices` (the old report showed only the first, POSITION's min/max) |
| `asha`, `--threads 4` | character | 234 s | identical: `asha.glb`, `asha_lod1.glb`, the 23 `textures/*.png` (`asha_textures.py` from the Blender run's `--bake-dir` dump) and the 19 `materials/*.tres` (`write_materials.py`): 44 files |
| `shader_test` | rendering | 2 s | **KNOWN (M1-RND-14), build_error**: the log holds `ValueError: the value returned by the 'key' function is not a number` |
| `vegetation` (`--threads 1`), `haluna_kit` (`--threads 4`) | environment | 4 s, 8 s | identical (7; 30 + manifest) |

`--all`: 292 s, 0 failed, 0 uncovered. The M1-QA-02 state is below, for comparison.

**Update 2026-10-23 (M1-CHR-05, M1-CHR-06, M1-RND-14, M1-ENV-07; worktree-agent-a361fe4924e35dfcf):** no known failures are left, and `expected_failure` is gone from every job.
- `base_body`: recommitted from `build_all.sh`, which now passes `--threads 1`. The rebuild hashes are the pinned ones above. The committed files never matched their sources: a773ea1's own sources rebuild to today's bytes.
- `shader_test`: the face sort ranks the tuple keys, so the script runs on 5.0.1. Recommitted, because the old files came from an unsorted, irreproducible build. The `char_*` shots pass unchanged.
- `vegetation`: no exported tangents (`export_tangents=False`, as the Haluna kit does; the imports already `ensure_tangents`), so it runs at the default 4 threads again. Identical at 1 thread and at 4 threads (3 concurrent runs).
- Asha's `build.sh --threads 4` (M1-CHR-06) is still open for the Asha line.

Asha's texture chain is covered now (sweep I, S3 on M1-QA-02): the face textures are where the §14 fidelity review happens, so a change to `asha_textures.py`, the bake dump or the donor must reproduce them byte for byte. The texture step is most of the job's time, and it runs only when Asha's (or base_body's, or the donor's) sources or outputs change.

## Earlier state (M1-QA-02: `--all`, 95 s wall, 4 vCPU, load ~4; threads unpinned, TANGENT tolerance on base_body)

| Job | Owner | Time | Result |
|---|---|---|---|
| `base_body` (3 variants) | character | 33 s | **KNOWN (M1-CHR-05)**: the committed `.glb` files don't match their source. POSITION min/max differ by up to ~3 mm, and the indices differ too. Run to run, the rebuild is stable except for Blender's tangent export (1 vertex in 14.5k moves by 1e-4), hence the TANGENT tolerance of 1e-3 |
| `asha` (`asha.glb`, `asha_lod1.glb`) | character | 45 s | identical |
| `shader_test` | rendering | 2 s | **KNOWN (M1-RND-14)**: `build_shader_test_meshes.py` fails on Blender 5.0.1 (`bm.faces.sort(key=...)`: "the value returned by the 'key' function is not a number") |
| `vegetation` (7 `.glb`) | environment | 5 s | identical |
| `haluna_kit` (30 `.glb` + `kit_manifest.json`) | environment | 8 s | identical |

Not covered then (no Blender involved): the numpy/Pillow texture scripts (`asha_textures.py`, `kit_textures.py`, vegetation `textures.py`, the shader-test textures), `write_materials.py`, the Undertow noise bake, and audio. **Since M1-QA-06** Asha's `asha_textures.py` and `write_materials.py` run as `{python}` steps of the `asha` job. Still out of scope for this gate: `kit_textures.py`, vegetation `textures.py`, the shader-test textures, the Undertow noise bake and audio. They need no Blender, so they belong in a plain Python reproducibility check, not a Blender job; adding them as `{python}` runs needs a Blender run first, by design.

## Adding a job

1. Add an entry to `tools/dev/blender_builds.json`. Make the build deterministic: fixed seeds, sorted iteration, and no exported tangents unless they're needed (see `docs/kb/tech/character_shading.md` on tangents). A build that does export tangents needs `"threads": 1` (the unit test fails otherwise). Build the committed files with the same thread count as the job.
2. Run `python3 tools/dev/verify_blender_builds.py --job <id>` twice. Both runs must be `identical`; run them concurrently once, too, because a thread race shows up only sometimes. Pin `threads` before you consider any tolerance. Never tolerate anything to hide a real change; rebuild and commit instead.
3. `python3 -m unittest tools/tests/test_blender_builds.py` checks that the scripts exist and that the outputs are committed.

## Host determinism: character builds opt in to the host snaps (M2-CHR-11)
numpy picks its SIMD path at runtime (AVX-512 on the cloud, AVX2 on the PC's i9-12900K, baseline elsewhere), and
the last bits of a sum or a dot product move with it. Every character build therefore snaps what it hands on:
donor and part positions to a 1 µm grid, the head's midline coordinates under 1e-9 to 0, shape-key deltas to a 1 µm
grid (`snap_shape_noise`), UVs to 2^-16 (`quantize_uvs`), the float images before 8-bit rounding
(`asha_textures.PRE_ROUND`), and the hair and LOD1-decimate inputs on the grid. Asha, Rhen, Toma, base_body, the
nine villagers, Sefir and Ysolde all do (villagers via `host_snaps: true`). **A new character build opts in from its
first commit**, and its author proves it the way M2-CHR-11 did: `verify_blender_builds.py --job <id>` natively,
with `NPY_DISABLE_CPU_FEATURES="X86_V4"` (the AVX2 path) and with `"X86_V3 X86_V4"` (baseline), all identical.
Pin `"threads": 4` per job. A job whose build imports a module that reads game data (the villagers import
hero_clips, which reads game/data/characters/helper_bones.json) needs that folder in `copy_into_sandbox` and the
file in its `sources`.
