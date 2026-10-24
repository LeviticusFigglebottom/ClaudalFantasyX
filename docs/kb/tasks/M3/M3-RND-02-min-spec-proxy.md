---
id: M3-RND-02
title: "Minimum-spec proxy: emulate a GTX 1060-class GPU on the RX 9070 XT and validate the Low preset"
role: rendering
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: "lead"
---
## Goal
SPEC §4.2's minimum tier is GTX 1060 / RX 580 class at 1080p, 30–60 fps on Low. There's no such card in the
project. Every min-spec number so far is an estimate scaled from ALU ratios (graphics_settings.md, undertow.md,
glimmer.md). This task builds a repeatable proxy on the PC's RX 9070 XT and uses it to validate Low.

## Acceptance criteria
- [ ] **A method**, written into `docs/kb/qa/gpu/`, for making the 9070 XT behave like a 1060-class GPU closely
      enough to rank costs and catch budget misses:
  - a clock or power limit (driver tuning, recorded and reverted);
  - plus render scale, so the pixel load matches 1080p Low's internal resolution;
  - with the calibration (a known workload's ratio to published GTX 1060 numbers) and its error bars.
- [ ] **Low validated through the proxy:** the slice sweep (launch, the zones, the battles, the Flood) at 1080p
      Low. Frame times against 30 fps (33.3 ms) and 60 fps, and ADR 0029's hidden, visible and entry budgets.
      Anything over budget is filed.
- [ ] The existing min-spec estimates in graphics_settings.md, undertow.md and glimmer.md are checked against the
      proxy, and corrected where they're off.

## Notes
- Changing the GPU's clock or power limit is a setting on the owner's machine. Get the owner's OK, record the
  exact values, and restore the defaults afterwards.

## Review log
