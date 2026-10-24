---
id: M2-ARC-08
title: The boot card's 10 s wait cap is within 0.5 s of a fresh install's first-run warm-up (title can reveal mid-warm-up)
role: architect
status: review
owner_session: "worktree-agent-a23fdd18373ec5031"
reviewer: lead
depends_on: [M2-ARC-03, M1-RND-29]
milestone: M2
request-from: "lead"
---
## Goal
Review-sweep-R found this across M2-ARC-03 and M1-RND-29. `BootCard.MAX_WAIT_MS` and `SceneRouter.REVEAL_WAIT_MAX_MS`
are both 10000 ms. After that the card opens with its work unfinished, with a warning. M1-RND-29's first-run warm-up
(`ShaderPrewarm.first_run`, 163–165 draws plus the `first_run_scenes` harvest) waits behind that card, and it took
**9.5 s on Low** on an RX 9070 XT (docs/kb/qa/gpu/2026-10-24-rnd-29-first-launch.md). The report also says a truly
fresh install is slower, because the AMD driver cache wasn't cleared. On a min-spec card, the first launch passes 10 s.
The title then shows and takes input while the warm-up is still staging, so it shows exactly the visible hitches
(up to the 1.35 s first 3D frame) that the card exists to hide.

Also, BootCard's `_wait_ms` adds up the capped process `delta` (about 140–150 ms a frame at most, M1-RND-29). So in
wall time the cap fires later than 10 s. M2-ARC-05's FrameClock (on `lead/batch4`) switches it to wall time, and that
makes the cap fire sooner.

## Acceptance criteria
- [x] A first-run warm-up is never cut short by the cap. For example, the cap scales with the work (the prewarm's
      remaining batches), or a first run gets its own named, much larger cap, or the cap applies only while the work
      makes no progress. Make it a named constant or a data value, and explain the choice in architecture.md
      ("The boot card").
- [x] When the card does open on the cap, the still-running warm-up is stopped or moved out of the visible frames
      rather than left staging under the title. Record which you chose.
- [x] Tests in `test_boot_card.gd`: a slow first-run warm-up (with an injected frame time) past 10 s keeps the card
      closed, and the stall path still opens it.
- [x] Check this against M2-ARC-05's wall-time FrameClock once that is merged.

## Notes
- Source: review-sweep-R (2026-10-24) on M2-ARC-03 and M1-RND-29.

### Notes (architect, worktree-agent-a23fdd18373ec5031, 2026-10-24)
- **Choice: the cap applies only while the work makes no progress**, plus an absolute safety cap. `ProgressWait`
  (`game/core/progress_wait.gd`, pure) ends `stalled` after `stall_timeout_ms` (10 s) with no change in the progress
  count, or `capped` after `max_wait_ms` (180 s). Both are data: `game/data/settings/boot_card.json`. The old
  `BootCard.MAX_WAIT_MS` and `SceneRouter.REVEAL_WAIT_MAX_MS` are gone. Explained in architecture.md ("The boot card").
- **Progress:** `BootCard.wait_progress()` sums each waited node's `wait_progress()` (`ShaderPrewarm`: its ticks;
  each is one step of a finite run), each condition's progress Callable (`wait_until(cond, progress)`; fonts:
  `SceneRouter.font_warm_progress()`), plus one per finished item. The router's reveal hold runs the same
  ProgressWait over `SceneRouter.holders_progress(reveal_holders())`. Both record `reveal_wait_end`
  (`done` / `stalled` / `capped`).
- **On a stall or the cap the warm-up is stopped** (not moved): the card calls `cancel()` on each waited node that
  has one before it opens. `ShaderPrewarm.cancel()` clears the stage, releases the swap hold, emits no `finished`
  and writes no first-run marker, so the next launch runs the first-run warm-up again.
- **First-launch cue** (pillar 1): `BootCard.show_first_run_cue()`, called by boot only when the resident warm-up
  is a first run. One line, `BOOT_FIRST_RUN_NOTE` ("Preparing the graphics for first use. This happens only
  once.", appended to `strings.csv`; Story may reword it), and a thin, low-alpha bar of
  `ShaderPrewarm.progress_fraction()`. It appears only after 1.5 s and fades in; it lifts with the card.
- **Against M2-ARC-05:** built on its FrameClock (merged into this branch). The card's stall and cap count wall
  time, and the tests drive the card through `_process` with a fake FrameClock and a capped `delta`.
- **Tests:** `test_progress_wait.gd` (5, new); `test_boot_card.gd` +8 (27): 60 s of 500 ms frames that progress, then
  one 12 s frame that progresses, keep the card closed; a stall opens it (`stalled`, worker cancelled); the cap opens a
  progressing wait; a condition's progress; the router's sum; the cue; boot's wiring. `test_shader_prewarm.gd` +1.
- **Also on this branch (Lead's request):** the boot smoke's "1 resources still in use at exit" from ARC-05's
  FrameClock in suspended router coroutines is fixed (commit `M2-ARC-05: fix the boot smoke ...`).

## Review log
