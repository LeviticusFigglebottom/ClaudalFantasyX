---
id: M3-CRE-05
title: "Ch6 creature models: shoal skipper, raid-hound, the wreck-crab variant"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M3-CRE-01]
milestone: M3
request-from: lead
---
## Goal
The Ch6 creatures (m2-slice: the shoals reuse gull_harrier as their flier). `model` on m2-slice's rows (M3-C06-02). Foes on screen: ridges 2–3, flats 3–4, the raid pair.

## Acceptance criteria
- [x] shoal_skipper (first pass: 1.6k triangles)
- [x] raid_hound (first pass: 3.1k triangles; no weak point; KO lies down)
- [x] wreck_crab (variant of reef_crab: lives in broken lamp housings, glows bound teal per m2-slice act1_ch06 §9; first pass 7.8k triangles. The bound teal is the lamp housing's own light, steady per color_script rule 2, recorded as the one sanctioned creature use in act1/wreck_crab.md: art to confirm in review)

## Notes
- The Inquisitor (Hadric Moll) is the character track's.
- 2026-10-24 (polish, review notes): wreck_crab's salt crust now has real relief: buckled salt plates (cells lifted and tilted on their own) split by grimy cracks and knobbed with salt nodules, as displacement plus cavity in vertex data, faceted shading; the crust ring is 20 x 44. The legs, claws and eye-stalks are bleached to grey wreck tones (coral_stone_weathered into timber_weathered, a storm_slate-greyed timber below) with salt patches, via an in-memory palette override and a wrapped finish call (reef_crab's build untouched). Hidden parts were trimmed to pay for it (underside 20 segs, mouthparts, lamp-light and abdomen ellipsoids). The lamp's glimmer_bound stays steady (no pulse on glass or lamp_light; materials.json unchanged). 7,942 triangles (budget 8k). Screenshot creature_wreck_crab re-approved after viewing.

## Review log
