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
  - **M1-RND-12**: `build_shader_test_meshes.py` fails on Blender 5.0.1 (`bm.faces.sort` key must be a number).
  - asha (2 `.glb`), vegetation (7) and haluna_kit (30 `.glb` + manifest) are **byte-identical**.
- Proposed CLAUDE.md §3 text for the Lead is in the 2026-10-23 qa-1 handoff.

## Review log
