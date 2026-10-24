---
id: M2-BPR-07
title: Per-encounter battle arenas (greybox here; env-art dresses them)
role: combat
status: doing
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-01]
milestone: M2
request-from: lead
---
## Goal
Battles all fight on the noon sandbox dais. Each story encounter gets its own arena: the Ch2 tideline at noon and the Drownbell on the Saltgrass Causeway at the ch03_boss sunset (color script), chosen by encounter in data, swapping the sandbox's WorldEnvironment, Sun and Arena. Greybox geometry here; a request to env-art for the final kits (intro audit 2026-10-24).

## Acceptance criteria
- [ ] game/data/battle/arenas.json maps encounters to arena scenes; fixtures and the sandbox keep the sandbox arena (no baseline moves)
- [ ] Arena scenes keep the node names the flood rig and the sun scaling look for (Sun, Arena/Sea)
- [ ] ch03_boss grade numbers from color_script.md
- [ ] Tests; a shot per arena
- [ ] A request task for env-art

## Notes
- From the Lead's intro audit (CONSOLIDATED.md, 2026-10-24).

## Review log
