---
id: M2-NIT-05
title: "tools/tests: test_blender_builds passes on Windows (the scratch path's spelling)"
role: rendering
status: review
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: qa
depends_on: [M2-NIT-04]
milestone: M2
request-from: "lead"
---
## Goal
The last red tools test on the PC, the only Windows host: `test_blender_builds.test_python_runs_use_this_interpreter`.
A known red test hides new ones.

## Acceptance criteria
- [x] `python -m unittest discover -s tools/tests` is green on Windows (498 run, 6 skipped).

## Notes (PC GPU, 2026-10-24)
- `verify_blender_builds.expand()` writes `{scratch}` as `str(scratch)`, which is `\s` on Windows. Mixed separators
  work there, so the tool is right. The test expected the POSIX spelling `/s/b`; it now builds its expectation from
  the same `Path`.
- Merged M2-NIT-04 (gpu/m2-nit-04-capture-test-windows: test_capture_sh through Git Bash) so this branch shows the
  whole suite green on Windows.

## Review log
