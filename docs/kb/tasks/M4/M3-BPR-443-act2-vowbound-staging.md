---
id: M3-BPR-443
title: "Request: battle effects for Nhoa's, Hesk's and Ethren's skills, and Nhoa's echo double"
role: combat
status: todo
owner_session: ""
depends_on: [M4-A2P-024]
milestone: M4
request-from: cinematics
---
## Goal
To battle-presentation. M4-A2P-024 lands three Vowbound rows and their skills (plan/act2/bosses/nhoa.md, hesk.md,
ethren.md §4):
- **Nhoa:** `silt_fall`, `deep_well`, `nhoa_echo` and her Swell `farewell_tide`.
- **Hesk:** `knot_light`, `cord_lift`, `hesk_mending` and `pass_cord`.
- **Ethren:** `level_hand`, `hold_the_hour`, `lacquer_screen` and `still_water`.

Also landed:
- creatures.json `clip_by_skill` maps each skill to cast and each finisher to special.
- choreo.json `first_call_flags` covers all four new Vowbound (Kesh too).

**`nhoa_echo` resolves as the last enemy action (BattleEcho).** The result's `skill_id` stays `nhoa_echo`, so its
effect should play the copied element and add her faint double (the sheet's VFX).

## Acceptance criteria
- [ ] VFX map rows for the twelve skills, or element fallbacks where they read; then drop `cord_lift` and `nhoa_echo`
      from tools/battle_vfx_coverage.py's INTENDED map.
- [ ] Nhoa's echo double.
- [ ] The finishers' staging per the sheets (Farewell-Tide's motes go up).

## Review log
