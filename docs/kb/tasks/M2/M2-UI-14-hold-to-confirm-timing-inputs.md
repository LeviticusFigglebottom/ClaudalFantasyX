---
id: M2-UI-14
title: Accessibility audit (5/5): a "hold to confirm" alternative for timed Swell inputs
role: ui
status: doing
owner_session: "claude/ui"
depends_on: [M2-UI-03]
milestone: M2
request-from: lead
---
## Goal
Timed inputs (Rhen's ring, Asha's chant, Toma's brace, Ysolde's glyph) ask for presses at moments. A player who cannot time presses can already widen the window or count misses as Good (timing assist, M2-UI-01). The audit asks for a "hold to confirm" way to play them: holding Confirm plays the input for you.

## Acceptance criteria
- [ ] A new `timing_assist` option, `hold`: while Confirm is held, each step is played at the assist floor's grade (good) when it comes up, so the input finishes on its own. Release pauses that, and the player may play steps by hand.
- [ ] It works through `SwellInput` and `UiSettings` like the other assist options (no engine rule changes). Swift (glyph) is never earned by the assist, as with "auto".
- [ ] The panel shows the assist tag, and the hint says "Hold Confirm".
- [ ] Tests for each kind.

## Review log
