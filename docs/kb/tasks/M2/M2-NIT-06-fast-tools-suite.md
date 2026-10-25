---
id: M2-NIT-06
title: Tools test suite under ~3 minutes on 4 cores, with no weaker checks
role: qa
status: review
owner_session: "agent-aca13b68502135d77"
depends_on: []
milestone: M2
request-from: "lead"
reviewer: lead
---
## Acceptance criteria
- [x] Profile the suite and one validate_data run; list the top costs per test file
- [x] check_banned: same files, same extensions, same messages in the same order, much faster
- [x] Validator tests stop copying the 200 MB `assets/` tree per test; no shared temp paths
- [x] test_audio_loudness: the same measurements, in parallel and cached by content hash
- [x] A parallel runner that runs exactly the tests `unittest discover` runs
- [x] Equivalence: validate_data output identical (0/0); seeded violations caught or ignored exactly as before, as tests
- [x] Timings before and after

## Notes
- 2026-10-24 qa (agent-aca13b68502135d77): ready for **lead** review. Handoff: docs/kb/handoffs/2026-10-24-qa-3.md.
  - **Before:** each file in its own process, 2 at a time: 589 s wall, about 1,100 s of serial work. test_audio_loudness 410 s, test_items_validate 235, test_validate_data 134, test_lattice_validate 98, test_rig_integrity 85, everything else under 22 s each.
  - **After:** `python3 tools/run_tool_tests.py -j 4`: **82 s** with a warm loudness cache, 191 s cold (load 1 to 6 from another agent). Plain serial `unittest discover`, warm: 283 s. 703 tests, 4 skipped, in every run.
  - **check_banned** (validate_data 7 to 10 s, 93% of it this scan, 9.4 M `re.search` calls): each file is now tested once with one combined regex. The shared word guards sit outside the alternation and each term keeps its own case flag, so it matches exactly where any of the per-term patterns match. Only a file with a hit gets the old line-by-line pass, so the messages and their order are unchanged. validate_data now takes 1.4 s. The file walk is unchanged. I did not switch to `git ls-files`: today the tracked set and the walked set are the same 1,374 + 261 files, the walk costs 0.1 s, and ls-files would stop catching untracked files before a commit (a weaker local check) and break the scratch-tree tests. The binary extensions were already outside the scan (an allowlist of text extensions), so nothing changed there.
  - **Validator tests** (items, validate_data, lattice): `tools/tests/tree_mirror.py` copies `game/` for real and fills `assets/` with symlinks, in /dev/shm. Copying `assets/` per test cost about 5 s, and on this disk deleting the ~2,600 entries afterwards cost another 4.6 s (0.02 s on tmpfs). Directories are never symlinked, because `rglob` does not follow them and the validator would see less.
  - **test_audio_loudness**: 335 of its 410 s are `true_peak_dbtp`'s FFTs on music beds whose lengths are not FFT-friendly (Bluestein: up to 24 s per file). loudness.py is untouched (Audio owns it, and render_all uses it). The test runs each file, and each boss stack, in a process pool, largest first, and caches the numbers by SHA-256 of the files, every `tools/audio/synth/*.py`, the test file, the numpy version and the ffmpeg version. The target comparison always runs fresh. `HYMN_TEST_CACHE=off` turns the cache off.
  - **Equivalence evidence:** validate_data output is byte-identical (0/0) before and after. The old and new scans on the real tree give 0 = 0, and with 800 random seeds (mixed case, word-boundary neighbours, Unicode line breaks, 312 of them in files outside the scanned extensions) they give 206 = 206 identical errors. test_banned_scan.py pins this on a fixture (.gd, .md, .json caught; .png, .glb, .ogg, .wav, .res, .import ignored) and checks every result against a copy of the old scan. For loudness, 171 files and 3 stacks match the old in-process code with exact float equality, and seeded target misses are still reported.
