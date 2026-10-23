# Blender asset rebuild gate (M1-QA-02, ADR 0005)

Every Blender-generated asset must regenerate from `assets_src/` with the pinned Blender. This gate rebuilds them and compares each output with the committed file.

```bash
python3 tools/dev/fetch_blender.py                   # once: Blender 5.0.1+dfsg-5 sysroot (ADR 0008 style)
python3 tools/dev/verify_blender_builds.py           # jobs whose sources or outputs changed
python3 tools/dev/verify_blender_builds.py --all     # every job (~95 s on the 4-vCPU sandbox)
python3 tools/dev/verify_blender_builds.py --job asha --keep /abs/dir   # keep the rebuilt files to diff
python3 tools/dev/verify_blender_builds.py --list
```

`tools/ci_local.sh` runs it after the Python steps:

| Variable | Effect |
|---|---|
| `HYMN_SKIP_BLENDER=1` | skip the step |
| `HYMN_BLENDER_ALL=1` | run every job, not only the changed ones (the Lead's merge run) |
| `HYMN_BLENDER_BASE=<ref>` | base ref for change detection (default `main`, then `origin/main`; with neither, every job runs) |
| `HYMN_BLENDER_TIMEOUT=<s>` | bound on the whole step (default 1800); `HYMN_BLENDER_JOB_TIMEOUT` bounds each job (default 900) |
| `HYMN_BLENDER=<path>` | Blender to use (default: the fetch_blender.py wrapper, then `blender` on PATH) |

Exit 3 (no Blender, or not the pinned 5.0.1) prints `SKIP`, as the screenshot step does when its render deps are missing. The CI workflow has a `blender` job that fetches the same package; it is `continue-on-error` until a run on the GitHub runner has matched.

## How it works

- **Jobs are data:** `tools/dev/blender_builds.json` lists, per job: `sources` (globs; `**` spans directories), `outputs` (globs of committed files), and `runs` (argv after `{blender}`, which expands to `blender --background --factory-startup --python-exit-code 1`; `{scratch}` is a per-job temp dir).
- **The working tree is never written.** `assets_src/` is copied into a temporary root, and the builds run there with their usual relative paths. The scripts resolve `ROOT` from their own location, so even a script with a hard-coded output path writes into the copy.
- **Change detection:** a job runs when any path in its `sources` or `outputs` changed since `git merge-base <base> HEAD`, or is modified or untracked in the working tree.
- **Comparison:** every committed file that matches `outputs` must be rebuilt, and every rebuilt file that matches must be committed.
  - `identical`: the bytes are the same. This is the rule.
  - `tolerance`: only for a job that declares `"tolerance": {"abs", "attributes", "why"}`. The glTF JSON must be equal, and all buffer data must be byte-equal except float accessors of the named attributes (for example `TANGENT`), which may differ by `abs`. Positions, normals, UVs, weights, indices and images are never tolerated.
  - `DIFF`: anything else. The message names the glTF accessors that differ (`<mesh>.<ATTRIBUTE>`).
- **Known failures:** `"expected_failure": {"task", "why"}` turns a failing job into `KNOWN`, which does not fail the gate. When the job passes again, the gate **fails** until the marker is removed, so a fix can't silently rot.
- The pinned version is checked from `blender --version` against `blender_version` in the manifest. A unit test keeps `blender_deb` equal to `PINNED_DEB` in `fetch_blender.py`, and another checks that every Blender `.glb` row in `assets/PROVENANCE.md` is covered by a job.

## State on 2026-10-23 (`--all`, 95 s wall, 4 vCPU, load ~4)

| Job | Owner | Time | Result |
|---|---|---|---|
| `base_body` (3 variants) | character | 33 s | **KNOWN (M1-CHR-05)**: the committed `.glb` files don't match their source. POSITION min/max differ by up to ~3 mm, and the indices differ too. Run to run, the rebuild is stable except for Blender's tangent export (1 vertex in 14.5k moves by 1e-4), hence the TANGENT tolerance of 1e-3 |
| `asha` (`asha.glb`, `asha_lod1.glb`) | character | 45 s | identical |
| `shader_test` | rendering | 2 s | **KNOWN (M1-RND-14)**: `build_shader_test_meshes.py` fails on Blender 5.0.1 (`bm.faces.sort(key=...)`: "the value returned by the 'key' function is not a number") |
| `vegetation` (7 `.glb`) | environment | 5 s | identical |
| `haluna_kit` (30 `.glb` + `kit_manifest.json`) | environment | 8 s | identical |

Not covered (no Blender involved): the numpy/Pillow texture scripts (`asha_textures.py`, `kit_textures.py`, vegetation `textures.py`, the shader-test textures), `write_materials.py`, the Undertow noise bake, and audio. They are candidates for the same runner with a non-Blender `{python}` job type.

## Adding a job

1. Add an entry to `tools/dev/blender_builds.json`. Make the build deterministic: fixed seeds, sorted iteration, and no exported tangents unless they're needed (see `docs/kb/tech/character_shading.md` on tangents).
2. Run `python3 tools/dev/verify_blender_builds.py --job <id>` twice. Both runs must be `identical` before you add any tolerance. Never tolerate anything to hide a real change; rebuild and commit instead.
3. `python3 -m unittest tools/tests/test_blender_builds.py` checks that the scripts exist and that the outputs are committed.
