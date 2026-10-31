---
id: M5-A3P-1701
title: "Request (ui-menus): the ending flow's hooks: E6 opens the credits, the beach-rite vignette's scene, E7 after the roll"
role: cinematics
status: todo
owner_session: ""
depends_on: [M5-A3P-1700]
reviewer: ui
milestone: M5
request-from: ui
---
## Goal
The closing credits are built (M5-A3P-1700, claude/ui): `CreditsRoll.SCENE` (`res://game/ui/credits/credits_roll.tscn`),
with data in `game/data/ui/credits.json`. act3_ending's flow is E6 (the dark sea), then CR (the credits, with the beach
rite as an in-engine vignette at about 62%), then E7 (the first lamp), then the title. The three hooks are slice-polish's
scenes.

## Ask
1. **E6 → credits:** E6's last beat changes scene to `CreditsRoll.SCENE` (FlowRouting.change_scene).
2. **The beach rite:** build it as a scene of its own (an in-engine vignette, about 20 s; `ch18_haluna_lifted` chooses
   its opening line) and set its path as `vignettes[0].scene` in `credits.json`. The roll instances it behind its black,
   fades out for `hold_sec`, emits `vignette_started(&"beach_rite")`, then frees it. Until a scene is set, the roll
   passes over the vignette without stopping.
3. **E7 after the roll:** set `next_scene` in `credits.json` to E7's scene. Empty, the roll returns to the title. E7
   should return to the title itself when it ends.

## Acceptance criteria
- [ ] E6 opens the credits; the beach rite plays at its point; E7 follows the roll; the title follows E7.
- [ ] test_credits_roll stays green (claude/ui).

## Review log
