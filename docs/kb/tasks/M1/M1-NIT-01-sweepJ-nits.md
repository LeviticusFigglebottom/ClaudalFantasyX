---
id: M1-NIT-01
title: Small fixes from review-sweep-J (UI-05, QA-06, NAR-12)
role: qa
status: review
reviewer: lead
owner_session: "agent-a0094ffbbf8563d67"
depends_on: [M1-UI-05, M1-QA-06, M1-NAR-12]
milestone: M1
request-from: "lead"
---
## Goal
From the review-sweep-J entries (file:line references there).

## Acceptance criteria
- [x] UI-05 S1: the Swell ring steps and catches up on the same clock under Engine.time_scale (swell_ring_clock.gd ~:35 vs ~:47); S2: one metaphor in the help line, no stray punctuation (strings.csv ~:421/424); S3: the gauge frame added to art/ui.md ~:135
- [x] QA-06 S1: base_body's known failure matched by a content hash at 1 thread, not by accessor names (blender_builds.json ~:17-22); S2: record that thread-count independence was tested on 4 CPUs only
- [x] NAR-12 S1: the 'After the storm' break-off and the later 'Kell. Of course.' entry reconciled (act_outline ~:176, ADR 0022 append note, decisions_log ~:237); S2: the 'oil wick' remnants (decisions_log ~:14, ~:145)

## Notes
- **UI S1.** `press()` multiplies its wall-clock catch-up by `Engine.time_scale` (an injectable `time_scale` Callable). A frame's delta is already game time, so both now run on one clock. A frozen capture (`time_scale` 0) also freezes the catch-up. Two new tests are in test_swell_ring_clock.gd.
- **UI S2.** The new key `SWELL_INPUT_TIMING_RING_HELP_LAMP` is appended to strings.csv: "Strike each time the ring meets the lamp. Beats: {beats}". `swell.json` `help_key` points at it.
  - The old row stays, because loc files are append-only, and it is now unused.
  - test_battle_swell_hud asserts there is no ". ·" and that the metaphor matches `HUD_SWELL_RING_HINT`.
  - The battle_swell_ring baseline is re-approved: only the help line changed, and it still fits on one line.
- **UI S3.** A bullet in art/ui.md §6.2 describes the full-gauge frame. tech/ui.md notes the one clock and the slower ring below 20 fps (the sweep-J nit).
- **QA S1.** A mismatch `expected_failure` may carry `rebuilt_sha256 {path: sha256}`.
  - The loader requires it for a `threads: 1` job, and `known_verdict` reports a different hash as "the rebuilt content changed" (a NEW failure signature).
  - base_body pins `4523ba…`, `58142e…` and `5da684…`, the same over 2 runs. A placeholder pin failed as expected. With the real pin, `--job base_body` gives KNOWN (exit 0), here and in ci_local.
  - There are 3 new tool tests.
- **QA S2.** blender_builds.md and the `_threads` note say the thread pin was verified on a 4-vCPU host only, and give the `taskset -c 0,1` command to prove it. The proof run is still open: Asha is being rebuilt by another agent.
- **Narrative S1.** The ADR 0022 sweep-J append note puts the ledger in time order:
  - "Kell. Of course." comes first.
  - The broken-off "After the storm" entry is the last one, written the night Dace went after Imra, and every page after it is blank.
  - act_outline Ch17 is reordered to match, and decisions_log N-26 is clarified inline.
- **Narrative S2.** decisions_log N-02 (the answer and item 3) and the sweep-C Prologue line now say "oil burner", corrected inline.
- **Not in scope.** The ch02 .dlg "She never says so" nit is still open.

## Review log
