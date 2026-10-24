---
id: M3-CRE-612
title: "Creature battle polish: hit reactions, idle variety, KO clips that suit the one-KO-then-fade rule"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: combat
depends_on: [M2-CRE-03]
milestone: M3
request-from: lead
---
## Goal
Battle-presentation's KO fix (M2-BPR-11) plays a foe's KO once, then fades it out and hides it. Make every
creature's KO end grounded and settled before the fade (fliers fall), give hits more life (a heavier variant), and
break up idle loops (an occasional idle variety clip), within the clip contract.

## Acceptance criteria
- [x] KO audit: every creature's last KO frame rendered and viewed; each ends settled. Fliers dropped by their hover but only the gull had one in battle, so creatures.json `stand_in.hover` now carries it (ashwing 1.38, sail_leech 1.38, squall_wing 1.2, stormgull and gull_harrier 1.05) and a tools test pins a flier's KO drop to its hover and keeps grounded KOs above the floor (the hullgnaw sinks by design)
- [x] Hit and idle variety, deterministic, through CreatureActor (no engine change): hit_b and idle_b for all 27 (f426c0e8)
- [x] Tests (creature 16/0, battle 527/0, tools creature tests 10 OK) and shots: all 60 creature and battle shots unchanged; all 27 jobs identical

## Review log
