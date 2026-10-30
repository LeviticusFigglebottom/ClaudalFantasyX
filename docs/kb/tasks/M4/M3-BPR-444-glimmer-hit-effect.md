---
id: M3-BPR-444
title: "Request: a `hit_glimmer` effect (effects.json map.elements has no glimmer swatch)"
role: combat
status: todo
owner_session: ""
depends_on: [M4-A2P-024, M4-A2P-025]
milestone: M4
request-from: cinematics
---
## Goal
To battle-presentation (the Lead's FAST-TRACK, 10-30 09:00). Glimmer has been an element since Act I (ELEMENTS,
vowbound.md), but `map.elements` stops at holy, so a glimmer hit falls back to `hit_none`. The first glimmer skills:
- Kesh's `voice_glimmer` (M4-A2P-025)
- Ethren's `level_hand` and `still_water` (M4-A2P-024)

Add `hit_glimmer` in the held-light colour (`glimmer_bound`: steady, never flickering, colour script C10) and map
`glimmer` to it. Then audio gives it its row in battle_sfx.json `vfx`, as the other `hit_*` have.

## Acceptance criteria
- [ ] `effects.json` `hit_glimmer` and `map.elements.glimmer`; tools/battle_vfx_coverage.py has no glimmer element gap.
- [ ] Remove `voice_glimmer` from the coverage tool's INTENDED map.

## Review log
