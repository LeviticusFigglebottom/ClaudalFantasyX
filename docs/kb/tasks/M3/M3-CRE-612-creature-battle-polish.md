---
id: M3-CRE-612
title: "Creature battle polish: hit reactions, idle variety, KO clips that suit the one-KO-then-fade rule"
role: character
status: doing
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: combat
depends_on: [M2-BPR-11]
milestone: M3
request-from: lead
---
## Goal
Battle-presentation's KO fix (M2-BPR-11) plays a foe's KO once, then fades it out and hides it. Make every
creature's KO end grounded and settled before the fade (fliers fall), give hits more life (a heavier variant), and
break up idle loops (an occasional idle variety clip), within the clip contract.

## Acceptance criteria
- [ ] KO audit: each KO ends grounded and still by the fade; fixes where not
- [ ] Hit and idle variety, deterministic, through CreatureActor (no engine change)
- [ ] Tests and viewed shots

## Review log
