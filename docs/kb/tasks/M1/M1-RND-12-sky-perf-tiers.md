---
id: M1-RND-12
title: Haluna sky: quality tiers, cubemap update policy, compositing fix
role: rendering
status: doing
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-12-sky)"
depends_on: [M1-ENV-01]
milestone: M1
request-from: "rendering"
---
## Goal
From the review-sweep-H entries (file:line references there).

## Acceptance criteria
- [ ] Sky quality tiers in graphics_presets.json (march steps, noise octaves), validated; High within budget on the GPU (measure)
- [ ] The radiance cubemap does not re-render every frame when the sun or cloud drift animates (time-sliced or thresholded)
- [ ] The iteration cap no longer silently cuts off far clouds
- [ ] Cloud colour is not multiplied by alpha twice
- [ ] The 1.5x visible-sky lift recorded in color_script.md and water.md
- [ ] The net material does not become a solid sheet in the far mips
- [ ] palette_check: the zenith minimum fraction raised so a mostly grey zenith fails; underside hue sampling restricted to cloud pixels

## Review log
