---
id: M2-ARC-12
title: "Two real-stall tests need a clock margin (they flake on WSL2 under load: the sleep and tick clocks differ)"
role: architect
status: done
owner_session: "lead"
reviewer: qa
depends_on: []
milestone: M2
request-from: "rendering (PC GPU gate runner)"
---
## Goal
`test_frame_clock.gd::test_a_real_stall_reads_past_the_cap` and
`test_boot_card.gd::test_a_real_stall_under_the_card_reads_at_least_its_length` sleep with `OS.delay_msec(N)` and
then assert that the wall clock read at least N ms, with no margin. That only holds when the clock a sleep runs on
and the clock `Time.get_ticks_usec()` reads tick at the same rate.

## Evidence (PC gate runner, WSL2 Ubuntu 24.04, d6a0886d, 2026-10-24)
- **The clocks:** under WSL2 (`hyperv_clocksource_tsc_page`) a 400 ms sleep measures 401–404 ms on
  `CLOCK_MONOTONIC` but 396.6–400.1 ms on `CLOCK_MONOTONIC_RAW`, which Godot's Linux ticks use. That's about 1%,
  and more under load.
- **During the full gate,** with the screenshot shards running alongside, both tests failed:
  `reveal_wait_max_frame_ms` 393.08 for a 400 ms stall, and the frame clock likewise.
- **On an idle machine** both pass 3/3. The Lead's container (serial lanes) passes.

## Acceptance criteria
- [x] Both assertions allow a small clock margin (for example `>= N * 0.97`). The tests still prove what they're
      for: a real stall is measured in wall time, past the 150 ms delta cap, not as the capped delta.
- [x] Every other test that asserts a real sleep against a tick reading gets the same margin (grep `OS.delay_msec`).

## Review log
- 2026-10-28, integration-qa (architect seat, per the Lead): **accepted.** test_frame_clock and test_boot_card
  assert their real stalls against `CLOCK_SKEW_TOLERANCE` 0.95. That still proves the stall is read in wall time,
  past the 150 ms cap: 0.95 of 400 ms is 380 ms. The other `OS.delay_msec` calls (test_shader_prewarm) only yield to a
  worker thread and assert no clock reading, so they need no margin. frame_clock 8/0, boot_card 27/0.
