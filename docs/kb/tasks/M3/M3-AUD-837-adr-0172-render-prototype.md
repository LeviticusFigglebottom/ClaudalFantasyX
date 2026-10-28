---
id: M3-AUD-837
title: "Prototype ADR 0172's build-time audio render and measure it on 4 CPUs (nothing switched over)"
role: audio
status: blocked
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: tech
depends_on: []
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
The Lead (2026-10-27): "prototype the fallback in ADR 0172 (proposed)… Measure render time on 4 CPUs and write the
trade-offs. Don't switch anything over."

## Acceptance criteria
- [x] tools/audio/build_render.py does three things: it writes a manifest of every JOBS file's sha256 with an input
      key per job (the job's import closure plus the toolchain); `--ensure` renders, or takes from the cache, what
      is missing or different, in parallel; `--plan` reports what it would do. tools/tests/test_build_render.py
      covers it.
- [x] Measured: a cold build of all 94 jobs (896 files, 73 MB) took 1605 s wall on 4 workers (6310 s of job time).
      A warm check takes 1.9 s. 895 of 896 files were byte-identical to the committed ones; the one that differed was
      changed on purpose mid-run.
- [x] docs/kb/decisions/0172-build-time-audio-render.md: the measurements, the cross-machine determinism risks,
      LFS against the render against a hybrid, and the check needed before either render option (a PC render
      against this manifest).
- [ ] The PC runner renders against a manifest written here and reports how many files differ (pc-gpu, when the
      human's storage decision needs it).

## Review log
