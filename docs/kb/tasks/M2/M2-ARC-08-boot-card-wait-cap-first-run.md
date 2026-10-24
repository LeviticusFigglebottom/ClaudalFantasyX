---
id: M2-ARC-08
title: The boot card's 10 s wait cap is within 0.5 s of a fresh install's first-run warm-up (title can reveal mid-warm-up)
role: architect
status: todo
owner_session: ""
reviewer: rendering
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
- [ ] A first-run warm-up is never cut short by the cap. For example, the cap scales with the work (the prewarm's
      remaining batches), or a first run gets its own named, much larger cap, or the cap applies only while the work
      makes no progress. Make it a named constant or a data value, and explain the choice in architecture.md
      ("The boot card").
- [ ] When the card does open on the cap, the still-running warm-up is stopped or moved out of the visible frames
      rather than left staging under the title. Record which you chose.
- [ ] Tests in `test_boot_card.gd`: a slow first-run warm-up (with an injected frame time) past 10 s keeps the card
      closed, and the stall path still opens it.
- [ ] Check this against M2-ARC-05's wall-time FrameClock once that is merged.

## Notes
- Source: review-sweep-R (2026-10-24) on M2-ARC-03 and M1-RND-29.

## Review log
