---
id: M2-FP-11
title: The Drownbell at slice quality (standing boss read-out, retry loop)
role: combat
status: doing
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-06, M2-FP-05]
milestone: M2
request-from: lead
---
## Goal
M2-FP-06 follow-up from the m2-slice standing queue. The Drownbell's mechanics work, but they show only in transient floats (which don't appear at all when damage numbers are off) and in one timeline chip suffix. Pillar 4 says the player always knows what the boss is building toward and what answers it. Bring the fight's read-out and its defeat/retry loop to vertical-slice quality without touching the balance.

## Acceptance criteria
- [ ] A standing boss read-out (`BattleBossStatus`), shown for as long as a boss with mechanics is on the field: the boss and phase name, the telegraphed skill with its turns left, the weak point's progress, and the field with how many are bound to it. It is independent of the damage-numbers setting, and its layout comes from battle_hud.json.
- [ ] Strings through loc keys; the opening phase's name and the field's name come from enemies.json.
- [ ] The phase change is announced even with damage numbers off.
- [ ] Defeat → Fight again restarts the Drownbell at phase 1 with Call Ilun still known, and the read-out resets.
- [ ] Tests; `sim.py --check` unchanged (no balance data touched).

## Review log
