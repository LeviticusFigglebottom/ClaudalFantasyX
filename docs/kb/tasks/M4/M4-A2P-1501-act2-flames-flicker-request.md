---
id: M4-A2P-1501
title: "Ch11 Lowlight and Sunken Vey: let the lamp flames flicker (ZoneKitDressing \"flicker\")"
role: environment
status: review
reviewer: environment (env-art-b)
owner_session: env-art (claude/env-art)
depends_on: []
reviewer: environment
milestone: M4
request-from: environment (env-art-b)
---
## Goal
env-art-b's Act II ambient-life pass (the Lead, 10-30) added two opt-in rows to ZoneKitDressing
(`game/levels/act1/zone_kit_dressing.gd`, test `tests/integration/test_zone_ambient_life.gd`):
- `fire_lights[].flicker` (0..1): the share of a light's energy a flame's flicker takes away at its deepest.
- `pieces[].drift`: flotsam that bobs, rocks and wanders a slow eddy on the water.

Hollowmere's oil lamps (0.3), its signal lamps (0.12) and the Lacquer Court's lamp-stands (0.15) use it. Ansedra and
the Sanctum stay still (ADR 0204 §1; the Sanctum's light is bound). env-art's two Ch11 zones place `fire_lights` with
no flicker yet: `game/levels/ch11/lowlight/lowlight_dressing.json` and `.../sunken_vey/sunken_vey_dressing.json`.

## Ask
In env-art's generators for those two zones, add `"flicker"` to the open-flame rows: about 0.25–0.3 for oil and wick
flames, 0.1 for flames behind glass, none for the Lamp Engine's bound or electric-steady light (if that is the story's
read). Optional: a few `drift` rows (the kit's `tide_debris`) on Sunken Vey's flooded lanes.

## Acceptance criteria
- [ ] Ch11's open flames flicker; any bound or steady lights stay steady.
- [ ] env-art views a Ch11 shot with the flicker on.

## Notes
- 2026-11-03, env-art: **no flicker rows. Ch11 has no open flame.** Every light in both zones is bound teal or grey
  shaft daylight: the Engine's twelve trimmed lamps, the flights' conduits, the lamp bench's conduit light, the well's
  upwelling, the Vey's conduit court. lowlight.md §0 has them "bound teal, steady", and colour script rule 2 holds
  bound light still. The generator's comment now says so.
  - **Drift: done.** Nine `tide_debris` pieces lie adrift on the Vey's flooded lanes (`_vey_debris`, Hollowmere's
    float height). Each sits 4.2–6.5 m off a gallery walk, clear of every greybox block by 0.8 m and of the arcades.
  - Viewed in walk stills: a log and plank afloat, their weed under the surface.
  - Checks: test_ch11_lowlight_dressing OK.

## Review log
