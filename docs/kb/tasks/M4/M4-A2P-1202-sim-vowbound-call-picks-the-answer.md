---
id: M4-A2P-1202
title: "The sim's Vowbound call rule calls the first callable (Ilun), so a masher with six Vowbound stalls the Wakefin"
role: combat
status: todo
owner_session: ""
depends_on: [M4-A2P-019]
reviewer: qa
milestone: M4
---
## Goal
`SimPolicy.call_vowbound` calls `field_answer(ids)`: the Vowbound whose finisher clears a field that's up, otherwise
`ids[0]`. On an Act II loadout, `ids[0]` is always Ilun, the first bound. So the `naive_swell` masher (`at_once`)
re-calls the weakest Vowbound all fight. On the Wakefin with `ch15_sea`, its losses run long: p90 91 actions
against the boss cap of 80. This is the one `--check` red left after M4-A2P-019, and it isn't a balance fault of
the fight (naive 0%, role_answer 73%, smart 100%).

## Ask
Have the call rule pick the strongest callable Vowbound (for example, the latest bound, or the highest finisher
power) when no field calls for one. Then re-run every suite whose loadout lists more than one Vowbound (Act I's
ch05 onward and all of Act II) and retune anything the change moves. It changes report-only `naive_swell` numbers
across Act I, which is why it isn't folded into M4-A2P-019.

## Acceptance criteria
- [ ] The call rule picks by strength; `sim.py --check` is clean on every Act I and Act II suite.

## Review log
