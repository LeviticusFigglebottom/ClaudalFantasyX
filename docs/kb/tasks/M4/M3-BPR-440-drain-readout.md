---
id: M3-BPR-440
title: "Request: show a drain on stage (the hit's `drained`: the user's HP won back)"
role: combat
status: todo
owner_session: ""
depends_on: [M4-CMB-1001]
milestone: M4
request-from: cinematics
---
## Goal
To battle-presentation. The engine now resolves `drain_pct` on a skill row (M4-CMB-1001; formulas.md § Damage, "Drain").
The hit dictionary carries `drained`: the HP its user won back. Ch10's fen leech (`leech_bite`, drain 50%) is the first
user.

Pillar 4: the player must see the leech heal from the bite, or the lesson ("kill it, don't trade with it") never
lands. A heal number on the user, tied to the hit, plus a thread or VFX from the target to the user. The VFX row for
`leech_bite` exists; it may only need the return leg.

## Acceptance criteria
- [ ] A `drained` hit shows the user's heal (number and HP bar) in the same beat as the damage.
- [ ] A test in the battle-presentation suite that a drain hit raises the readout.

## Review log
