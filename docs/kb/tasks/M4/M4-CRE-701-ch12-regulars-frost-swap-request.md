---
id: M4-CRE-701
title: "Request (creatures-b): ridge_lynx and scree_crawler swap frost for snow and grit (ADR 0204, ADR 0015's reading)"
role: character
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: []
reviewer: rendering
milestone: M4
request-from: creatures-b
---
## Goal
ADR 0204 (answering creatures-b's LEAD-ASK): the Ch12 regulars follow the Avalanche Ram's reading of ADR 0015. Nothing
frozen on the pass's wildlife either; snow and grit are weather.
- `ridge_lynx`: the "frosted" ear tufts become snow-caked tufts (opaque, rough; no rime, no ice sheen).
- `scree_crawler`: "frost-split scree" and its frost counter become wet-split, grit-packed scree; the counter's VFX and
  wording read as snow and stone, not frost. Check skills.json and loc for any frost name on its counter.
Source sheets: docs/kb/art/creatures/act2_roster.md, docs/kb/art/creatures/act2/{ridge_lynx,scree_crawler}.md.
Like M4-CRB-001 (the Ram), this is a build-script and material change, not a new model. It starts at the Act I gate.

## Review log
