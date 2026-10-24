---
id: M2-ENV-02
title: Haluna at night (H10) for the slice's dock scene
role: environment
status: todo
owner_session: ""
depends_on: [M2-ENV-01]
milestone: M2
request-from: cinematics
---
## Goal
Request from the m2-slice track (M2-FP-15). B11 plays on Haluna's dock at night: H10 in docs/kb/art/environments/haluna.md, with oil lamps in the windows, sea-glow at 0.12 and stars (color_script.md `ch03` night). The playable zone instances the mood scene, so it needs a night lighting state it can switch to: a sun or moon, the sky, the sea-glow value and window lamps.

## Acceptance criteria
- [ ] A night variant the zone can select by data (a second Environment and light rig, or a switch on the mood scene) with no edit to the noon baselines.
- [ ] Window lamps and sea-glow per the colour script; the dock reads at H10's framing.
- [ ] A screenshot shot for H10 at night (lavapipe baseline), with the cost noted.

## Review log
