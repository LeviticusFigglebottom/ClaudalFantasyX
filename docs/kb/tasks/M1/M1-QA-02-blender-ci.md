---
id: M1-QA-02
title: Blender headless CI job to re-verify generated assets
role: qa
status: review
owner_session: "worktree-agent-aafc786bec1f4e2c5"
depends_on: [M1-CHR-01]
milestone: M1
request-from: ""
---
## Goal
ADR 0005 consequence.

## Acceptance criteria
- [x] Pinned Blender version (`tools/dev/blender_builds.json`: 5.0.1 / `5.0.1+dfsg-5`, checked against `blender --version` at run time; a unit test keeps it equal to `fetch_blender.py`'s `PINNED_DEB`)
- [x] Rebuild plus hash compare for changed assets_src (`tools/dev/verify_blender_builds.py`: only jobs whose sources/outputs changed since the merge-base, or `--all`)

## Notes
- **Reviewer: character.**
- `tools/dev/verify_blender_builds.py` + `tools/dev/blender_builds.json` (5 jobs: base_body, asha, shader_test, vegetation, haluna_kit). It builds in a temporary copy of `assets_src/`, never in the working tree, and compares by sha256. On a mismatch it does a glTF-aware diff that names the accessors that differ. An optional per-job tolerance covers named float attributes only (TANGENT); positions, indices, weights and images are always exact. Docs: `docs/kb/qa/blender_builds.md`. Tests: `tools/tests/test_blender_builds.py` (12 tests, no Blender).
- `tools/ci_local.sh` step after the Python checks, with `HYMN_SKIP_BLENDER=1`, `HYMN_BLENDER_ALL=1`, `HYMN_BLENDER_BASE`, and `HYMN_BLENDER_TIMEOUT` (default 1800 s; each job is also bounded at 900 s, and SIGTERM kills the running Blender). Exit 3 means SKIP. The CI workflow has a new `blender` job, `continue-on-error` until a runner run matches.
- `--all` takes **95 s** on this sandbox (4 vCPU, load ~4): base_body 33 s, asha 45 s, shader_test 2 s, vegetation 5 s, haluna_kit 8 s. In changed-only mode, a change that touches no Blender source costs ~0 s. This checkout has no `main` ref, so the default falls back to every job (95 s). Agents can set `HYMN_BLENDER_BASE=<integration branch>`.
- **Findings** (both are expected failures, reported as `KNOWN`; the gate fails again once they pass, until the marker goes):
  - **M1-CHR-05**: the committed `base_body_*.glb` don't match their source (POSITION is up to ~3 mm off, and the indices differ). Base-body rebuilds also wobble one tangent by 1e-4 from run to run, hence the TANGENT tolerance of 1e-3 on that job only.
  - **M1-RND-14**: `build_shader_test_meshes.py` fails on Blender 5.0.1 (`bm.faces.sort` key must be a number).
  - asha (2 `.glb`), vegetation (7) and haluna_kit (30 `.glb` + manifest) are **byte-identical**.
- Proposed CLAUDE.md §3 text for the Lead is in the 2026-10-23 qa-1 handoff.

## Review log
- 2026-10-23 character (review-sweep-I, fresh reviewer): **approve-with-fixes.** No blockers.
  - **What I read:** the task, handoff qa-1, tools/dev/verify_blender_builds.py (all of it), tools/dev/blender_builds.json, the ci_local.sh step and the `blender` CI job (merge ae733de), and docs/kb/qa/blender_builds.md.
  - **Checks:** `unittest discover -s tools/tests` 359 OK, including test_blender_builds.py. I did not run Blender (the Lead's full gate was running). Every Blender-importing script under assets_src/ (8 files across the 5 build folders) is covered by a job, and so is every committed `.glb` (2 + 3 + 2 + 30 + 7).
  - **What passes:** builds run in a temporary copy, so the working tree is never written. The pin is checked against `blender --version`. Byte-identity is the default. The TANGENT tolerance is scoped to one job and to named float attributes, and positions, indices, weights and images stay exact. "Committed but not produced" and "produced but not committed" are both failures. A KNOWN job that starts passing fails the gate until its marker is removed. SIGTERM kills the running Blender (subprocess.run kills the child on the raised exception).
  - **Should-fix:**
    - **S1 (KNOWN masks new failure modes).** verify_blender_builds.py:371-386 treats *any* failure of a job with `expected_failure` as KNOWN. base_body is expected to *mismatch* (CHR-05), but if a later edit makes it *crash*, or makes a different output differ, the gate still says KNOWN. shader_test is expected to *crash* (RND-14), so any further breakage hides behind that. Add the expected kind to the marker (`"kind": "mismatch"` or `"build_error"`, and for a mismatch, the expected paths), and fail when the actual failure differs. This matters most for base_body, whose sources are shared with asha.
    - **S2 (coverage guard).** Nothing fails when a new Blender build script or a new committed `.glb` is outside every job. Today all are covered, but the next generator added will silently go unverified. Add a check (python, no Blender) that every tracked `assets/**/*.glb` matches some job's `outputs`, and every `assets_src/**/*.py` that imports `bpy` is under some job's `sources`, or is listed as exempt with a reason.
    - **S3 (the Asha texture chain).** The asha job's `--bake-dir {scratch}/asha_bake` dump is thrown away, and `assets/characters/asha/textures/*.png` (from asha_textures.py, numpy) is not verified. This is known ("a `{python}` job type"). Please track it as a task, because the face textures are where §14 fidelity review happens.
  - **Nits:**
    - Handoff qa-1:12 and :26 still say "RND-12". The Lead renumbered it to M1-RND-14 (cc90db6). blender_builds.json and blender_builds.md are right.
    - Exit 3 (no Blender, or the wrong version) prints SKIP and the local gate passes. That is fine for agents. The Lead's merge run should treat SKIP as a failure (`HYMN_BLENDER_REQUIRED=1`?), so a missing fetch never reads as green.
    - `copy_into_sandbox` is only `assets_src`. A future build that reads `game/data` (a palette, for example) will fail in the sandbox with a confusing error. Mention it in blender_builds.md.
