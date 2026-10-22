---
id: M1-CMB-05
title: Headless balancing simulator
role: combat
status: todo
owner_session: ""
depends_on: [M1-CMB-00]
milestone: M1
request-from: ""
---
## Goal
SPEC §6.9: thousands of seeded fights per encounter, reporting win rate, average turns, and item use.

## Acceptance criteria
- [ ] A GDScript runner scene runs N seeds with a pluggable party policy
- [ ] tools/balance/sim.py invokes Godot headless and writes a Markdown/CSV report
- [ ] Target bands per chapter documented in docs/kb/design/balance_targets.md

## Notes
Sandbox note: a naive all-attack policy probably loses to sandbox_reef by design (the elegant answer is swapping). Report it.

## Review log
