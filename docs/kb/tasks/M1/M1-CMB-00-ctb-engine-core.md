---
id: M1-CMB-00
title: CTB engine core: formulas, timeline, swap, enemy AI
role: combat
status: review
owner_session: "lead-bootstrap"
depends_on: []
milestone: M1
request-from: ""
---
## Goal
A headless, deterministic CTB engine that the sandbox, simulator, and tests drive.

## Acceptance criteria
- [ ] Formulas mirror docs/kb/design/formulas.md, with a test per formula
- [ ] Timeline predicts 16 turns and previews rank and delay effects
- [ ] Swap at no turn cost, XP credit rule, escape
- [ ] Data-driven enemy AI (conditions, weights, scripted turn_mod)
- [ ] Same seed → identical battle (test)

## Notes
Written in the bootstrap session without a local Godot binary; verified by gdparse and gdlint only until CI runs. Reviewer: Progression.

## Review log
