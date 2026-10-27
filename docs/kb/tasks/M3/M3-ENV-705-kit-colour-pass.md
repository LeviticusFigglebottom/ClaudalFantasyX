---
id: M3-ENV-705
title: "Colour pass on the Act I kits under their zone grades (the human: no greyscale or flat scenes)"
role: environment
status: doing
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The human has complained about greyscale and flat scenes. Check every env-art kit under its zone's light and
grade and lift the frames that read grey, without breaking each zone's colour-script intent.

## Acceptance criteria
- [x] A colourfulness ranking of every env-art baseline (mean HSV saturation, luminance, contrast). Lowest:
      the Shell Shrine interior (S02 0.086, S03 0.095), Ashcrown A10 (0.105) and A01 (0.135).
- [x] Ashcrown: `lut_ch05_ashcrown` keeps full saturation outside the leaf greens (was ×0.88) and lifts the
      copper, lacquer and ember accents +18% (was +6%). `ashcrown.md` updated. PC render requested.
- [ ] View the PC renders of A01, A04, A10; re-approve or adjust.
- [ ] The Shell Shrine interior: proposed to slice-polish with M3-ENV-704 (its grade and GI are theirs; the kit
      stone `kit_shrine_stone` is env-art's and can warm a step if they want it with the rebake).
- [ ] The next lowest kits after the shrine and Ashcrown: the causeway route arena and Brine Shoals B01/B05.
