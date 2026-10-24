---
id: M2-CRE-10
title: "Bestiary art hook per creature"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CRE-03]
milestone: M2
request-from: lead
---
## Goal
If the bestiary UI supports a portrait, give each creature one from its model (reproducible); otherwise file the UI request.

## Acceptance criteria
- [x] See Goal; the notes record what shipped.

## Notes
- 2026-10-24: the bestiary UI has no portrait slot, so the art side ships as a live control instead of stored images: `game/creatures/creature_portrait.tscn` (`CreaturePortrait`, a SubViewportContainer with its own small world, a transparent background, a key and a rim light). `show_enemy(id)` instances the enemy's enemies.json `model`, holds creatures.json `portrait.clip` at `clip_time` and frames it from `portrait.yaw_deg`/`pitch_deg` (CreatureFraming, shared with the review stage). An enemy without a model shows nothing. No PNG to keep reproducible: a model change updates every portrait.
- Review shot `creature_portraits` (every enemy with a model on the UI's deep panel colour). Test in `test_creature_actor.gd`.
- UI request filed: **M2-UI-26** (filed as M2-UI-16; renumbered at the big7 merge) (put the portrait on the bestiary page and the Read panel).

- Portraits use a frustum fit (CreatureFraming.frame_fit), so tall and wide creatures fill their frame alike.

## Review log
