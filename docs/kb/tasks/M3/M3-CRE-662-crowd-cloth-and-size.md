---
id: M3-CRE-662
title: "Crowd follow-up: cloth never near skin (a perceptual metric, no fallback), and a smaller crowd (shared clip libraries)"
role: character
status: doing
owner_session: "creatures (worktree agent)"
reviewer: art
depends_on: [M3-CRE-659]
milestone: M3
request-from: creatures
---
## Goal
The coordinator's review of M3-CRE-659's renders and data (2026-10-28):
1. **Cloth near skin.** In crowd_lineup_a two pale peach tops read close to bare skin. The generator's
   `draw_cloth` measures plain sRGB distance, and when 12 draws all miss `skin_min_distance` it keeps the farthest
   anyway. 3 body defaults and about 10 people's tints fall below the floor (56/47 units on the Brine Shoals wrights,
   38 on an Oruvel diver's sash). Fix:
   - a perceptual metric (CIELAB ΔE, hue-aware), with a floor that grey-on-tan passes and peach-on-tan fails;
   - no silent fallback: widen the draw or pick another swatch set, and fail loudly if none clears;
   - apply it to the bodies' default `_tints` too;
   - the validator checks the same metric.
2. **Size.** assets/crowd is 43 MB, of which 12.2 MB is clip and material text. If every crowd body shares the
   villager skeleton, share one AnimationLibrary (or a few, by age band) instead of one copy per body, if the import
   and actor scenes allow it. Report the new size.

## Review log
