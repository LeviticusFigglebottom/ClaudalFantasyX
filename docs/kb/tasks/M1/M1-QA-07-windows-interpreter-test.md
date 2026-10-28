---
id: M1-QA-07
title: test_python_runs_use_this_interpreter fails on Windows (path separator in the expected argv)
role: qa
status: review
reviewer: architect
owner_session: "integration-qa (hero-integration track, session_01PzF7Jc4XVQdTWcaYUyCjPB)"
depends_on: [M1-QA-06]
milestone: M1
request-from: "rendering"
---
## Goal
`python -m unittest discover -s tools/tests` has one failure on Windows, on every branch including the integration
branch:
`test_blender_builds.ManifestTest.test_python_runs_use_this_interpreter` (tools/tests/test_blender_builds.py:145).
A Windows contributor shouldn't have to wonder whether they broke it. Found on the PC GPU session (Windows 10,
Python 3.14).

```
-  '\\s/b']
+  '/s/b']
```

`verify_blender_builds.expand` (tools/dev/verify_blender_builds.py:459) substitutes `str(scratch)` for `{scratch}`.
On Windows, `str(Path("/s"))` is `\s`, so the argument becomes `\s/b`. The test hard-codes the POSIX `/s/b`. Linux
CI passes.

## Acceptance criteria
- [x] The test passes on Windows and Linux. Either expect `f"{Path('/s')}/b"`, or have `expand` substitute
      `scratch.as_posix()`. Blender and Python both accept forward slashes on Windows, and a POSIX path is
      unchanged.
- [ ] No other `tools/tests` failure on Windows. Today this is the only one: 433 run, 6 skipped.

## Notes
- The repro takes one command, on any Windows machine:
  `python -m unittest tools.tests.test_blender_builds.ManifestTest.test_python_runs_use_this_interpreter`.

## Notes (2026-10-27, integration-qa)
- Already fixed by c3e4c7da (M2-NIT-05): the test expects `f"{scratch}/b"` (the scratch Path as the OS spells it).
  It passes on Linux. The second box (no other Windows failure) needs a Windows run, so it's left for the reviewer
  or the PC once it's back.

## Review log
