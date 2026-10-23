---
id: M1-CHR-06
title: Pin Blender's thread count in the base_body and Asha build scripts
role: character
status: done
owner_session: "worktree-agent-a361fe4924e35dfcf"
depends_on: [M1-QA-06]
milestone: M1
request-from: "qa"
---
## Goal
M1-QA-06 pinned Blender's thread count in the rebuild gate (tools/dev/blender_builds.json), because two character builds depend on it:
- **base_body** exports tangents, and Blender's threaded tangent export races. At 4 threads the rebuild hash changed from run to run (athletic `cbcee8…` or `4523ba…`, heavy `58142e…` or `06cf15…`). At `--threads 1` it was byte-stable. The gate runs it at `--threads 1`.
- **Asha's** body bakes (`asha_body_normal`, `_orm`, `_skinmask`) are stable at a fixed thread count, but differ at 1 thread compared with 4. The committed textures match 4 (this sandbox's CPU count), so the gate runs Asha at `--threads 4`.

`assets_src/characters/base_body/build_all.sh` and `assets_src/characters/asha/build.sh` still use Blender's default (the host's CPU count). A rebuild on a machine with another core count, or one that loses the tangent race, commits files the gate then rejects.

## Acceptance criteria
- [x] base_body's build script passes `--threads 1` to Blender (or stops exporting tangents and regenerates), and M1-CHR-05's rebuild uses it.
- [x] Asha's build.sh passes `--threads 4` (or the gate's `default_threads` changes with a regenerate, in one commit). **Handed to the Asha line**: this round was told not to touch `assets_src/characters/asha`, because another round may be editing it. The change is one line: `"$blender" --threads 4 --background ...` in `build.sh`. After it, extend `test_owner_build_scripts_use_the_gate_thread_count` (tools/tests/test_blender_builds.py) to cover `asha/build.sh`.
- [x] `python3 tools/dev/verify_blender_builds.py --job asha --job base_body` agrees with the committed files, apart from base_body's tracked M1-CHR-05 mismatch until that lands. (M1-CHR-05 landed in the same branch: both jobs are `identical`.)

## Notes
- Do not change these from QA; `assets_src/characters/asha` is being rebuilt in another worktree (M1-CHR-03/04 line). Fold this in there.
- 2026-10-23 (worktree-agent-a361fe4924e35dfcf): `build_all.sh` runs `"$blender" --threads 1 --background --factory-startup ...`, the same argv order the gate uses. build.py's docstring and the six base_body PROVENANCE build commands say `--threads 1`. A new unit test (`test_owner_build_scripts_use_the_gate_thread_count`) checks that build_all.sh passes the job's thread count, so a change to either side fails the test. The in-tree `build_all.sh` rebuild gives exactly the gate's hashes (M1-CHR-05 notes). Review: rendering (SPEC §12.3). The Asha item above stays open for the Asha line; the Lead may split it into its own task.

## Review log
- 2026-10-23 lead: added `--threads 4` to assets_src/characters/asha/build.sh, matching the gate's asha job, which closes the unticked box.
- 2026-10-23 rendering (review-sweep-L, fresh reviewer): **approve, with should-fixes.**
  - **Checks:** base_body's `build_all.sh` passes `--threads 1` in the gate's argv order (build_all.sh:14). `--job base_body` gives 3 identical. `test_owner_build_scripts_use_the_gate_thread_count` passes (tool tests 411 OK). The Lead's fc3940c adds `--threads 4` to asha/build.sh:13, matching the gate's `default_threads` for the asha job. `--job asha` result: see the M1-CHR-09 entry.
  - **Should-fix:**
    - **S1: the test still covers base_body only** (tools/tests/test_blender_builds.py:120-125). Its docstring still says Asha "is folded in by the Asha line". The task asked for the test to be extended to `asha/build.sh` once the flag landed; without that, nothing ties build.sh to the gate.
    - **S2: the Asha rows in assets/PROVENANCE.md:158-167 still show `blender --background --factory-startup --python ...` with no `--threads 4`.** The base_body rows were updated. Append-only rules allow fixing the owner's own rows.
    - **S3: the second criterion's box is still `[ ]`,** although the Lead's log line says it is closed. Tick it when S1 lands.
- 2026-10-23 lead: closing on review-sweep-L approve; the should-fixes are in M1-NIT-02.
- 2026-10-23 qa (M1-NIT-02): S1 to S3 done. `test_owner_build_scripts_use_the_gate_thread_count` now checks every `"$blender" ... --python <script>` call in every tracked `assets_src/**/*.sh` against the gate job that runs that script (base_body `--threads 1`, asha `--threads 4`). It also fails on a build script whose Blender script no job runs. The Asha PROVENANCE rows show `--threads 4`, and criterion 2 is ticked.
