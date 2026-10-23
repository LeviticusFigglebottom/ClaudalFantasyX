---
id: M2-FP-05
title: First-playable polish - cutscene skip, Haluna entry hitch, retry after a lost battle
role: architect
status: doing
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M2-FP-04]
milestone: M2
request-from: lead
---
## Goal
Fix the three limits listed in M2-FP-04: no way to skip a cutscene, a ~1.5 s frame when Haluna loads, and a lost field battle that leaves its trigger skippable.

## Acceptance criteria
- [ ] Hold-to-skip on every cutscene (an on-screen fill so it can't fire by accident); the skip plays the rest of the script instantly (flags, branches with the default choice, events), and the autosave hold and player freeze end exactly as on a normal finish.
- [ ] Entering Haluna has no frame over the swap budget on this machine (work spread over frames or moved off the main thread, behind the router fade).
- [ ] After a defeat the result panel offers Fight again and Return to last save (the newest readable record; the title if none). The field trigger can no longer be walked past after a loss.
- [ ] Tests for each, docs/PLAYTEST.md updated.

## Review log
