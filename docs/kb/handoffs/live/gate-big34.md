# Gate big34 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 5695a69c (Merge lead/gate-big33).

## Pinned heads (merged --no-ff, in order)
- claude/audio @ 0643ae38
- claude/act1-chapters @ bfc89617
- claude/m2-slice @ 59cfb82a
- claude/hero-integration @ 322528b1
- claude/env-art @ 55188ef9
- claude/creatures @ 85a25787
- claude/characters @ b4881fe6
- claude/creatures-b @ ec63d5f3

The Lead's priority items aren't posted yet: audio's UiAudio and ashcrown_audio ERROR fixes (audio's newest is Act III score
work, M5-A3P-1950/1951), act1-chapters' touch-beat queue fix (its newest is the M4-A2P-1003 Act II flows), and slice-polish's
Haluna add-frame split (m2-slice's newest only logs M4-A2P-070's results). A watcher is on all three. Each is merged between
test runs, followed by a fresh import and a re-gate.

## Resolutions
- None needed: every merge was clean (ownership.md and append-only files through merge_union).

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1073 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ adab5e73

## Fast gate
- Selected: 10 test files.
- Lane A (mine): 5; lane B (GATE-HELPER): 5, in `gate-big34-lanes-b.txt` @ ec0a766c.

## Mid-batch (after lanes A and B finished)
- **audio @ 4d4fbd50** (FAST-TRACK 3e791059: no UiAudio reconnect ERROR on a resident battle return, no unbind(0) ERROR;
  plus Act III score part 2, M5-A3P-1951). Clean. Re-gate on a fresh import of 15 files (the audio, UI audio, ashcrown,
  battle-return and resident tests): **all green**, import and boot clean.
- **m2-slice @ f7fe9250** (slice-polish's **fdc9ece5: revert of the deferred Haluna beach pose 97c591c3**: 3 of 19
  scene_swap_probe runs into Haluna crashed mid-swap with signal 11, and 0 of 16 without it; the hidden frame stays under ADR
  0029's 1 s at a median of about 600 ms), with the Ch15/Ch16 staging (M4-A2P-075) and the Act III memory fixture. Clean.
  Re-gate of 52 files on a fresh import is running.
- act1-chapters' touch-beat queue fix didn't post during this batch; it goes to big35.
