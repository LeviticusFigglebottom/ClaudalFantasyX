---
id: M3-UI-208
title: "Request: Act II enemies.json rows for claude/creatures' actors, so the bestiary can list them"
role: combat
status: blocked
blocked-by: ADR 0041
owner_session: ""
reviewer: ui
depends_on: []
milestone: M3
request-from: ui
---
## Goal
The Lead routed "Act II codex and bestiary entries for every Act II creature and boss on claude/creatures" to ui (2026-10-27, 23:37). The bestiary (BestiaryMenuModel) lists whatever `game/data/battle/enemies.json` holds:
- stats and weaknesses;
- `name_key` and lore;
- its portrait, from creatures.json `portrait`.

claude/creatures has added the Act II battle actors to `game/data/creatures/creatures.json`:
- gallery_ray, rime_urchin, conduit_crawler, ridge_lynx, cord_moth, glass_skate, root_crab, fen_leech, scree_crawler, rim_crawler, flat_engine;
- the Act II bosses' actors;
- kahre.

No branch has an Act II row in `enemies.json` yet: every branch still has the 28 Act I rows. The data file is Combat's (`game/data/battle/**`), so this is a request.

## Acceptance criteria
- [ ] An `enemies.json` row for each Act II creature and boss: stats, weaknesses, `name_key`, its bestiary lore key, and `model` naming its creatures.json actor.
- [ ] Their encounters, where act1-chapters' Act II zones need them.
- [ ] **Then ui:**
  - the bestiary picks the rows up with no UI change;
  - ui checks the pages in the pseudo-loc walk;
  - ui posts a render request for a bestiary shot on an Act II page;
  - ui adds the `portrait` angles to the render request, if creatures hasn't.
- 2026-10-30 ui-menus: M4-C10-03 added `tannin_archer`, `root_crab` and `fen_leech` with names and lore, but **no `model`**. Each needs `"model": "res://game/creatures/<id>/<id>_battle.tscn"` (the creatures.json `scene`, already built, with its bestiary portrait baked). Without it the bestiary page has no picture, and the fight likely draws a capsule (the stand-in path). It is a one-field edit per row in Combat's file.

## Review log
- 2026-10-28, ui-menus: **paused (ADR 0041, the human's refocus on Act I at final quality).** What is built stays on claude/ui and merges as is; nothing is reverted. Resume when a new ADR lifts the pause.
