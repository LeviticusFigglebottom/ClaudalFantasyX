---
id: M1-CMB-00
title: CTB engine core: formulas, timeline, swap, enemy AI
role: combat
status: done
owner_session: "lead-bootstrap"
depends_on: []
milestone: M1
request-from: ""
---
## Goal
A headless, deterministic CTB engine that the sandbox, simulator, and tests drive.

## Acceptance criteria
- [x] Formulas mirror docs/kb/design/formulas.md, with a test per formula
- [x] Timeline predicts 16 turns and previews rank and delay effects
- [x] Swap at no turn cost, XP credit rule, escape
- [x] Data-driven enemy AI (conditions, weights, scripted turn_mod)
- [x] Same seed → identical battle (test)

## Notes
Written in the bootstrap session without a local Godot binary; verified by gdparse and gdlint only until CI runs. Reviewer: Progression.

## Review log
- 2026-10-22 progression (fresh agent): approve-with-fixes. It found a blocker: swapping in for a KO'd member rewound time and granted free turns. It also found inexact float damage, a preview that ignored expiring statuses, dead targets costing MP and the turn, turn_mod 0 crashing, an infinite loop with everyone asleep forever, phantom statuses_added on a kill, and test gaps.
- 2026-10-22 lead: all fixed. Integer-exact damage; swap never rewinds time; the timeline simulates status countdown and previews time statuses; target validation; a stalemate guard; the validator checks AI args, weights, and permanent Stop/Sleep. Tests went from 42 to 61, plus balance-band assertions. Docs updated (rounding rule, Break floors, lost turns skip Poison/Regen, Haste on others, XP rule). Moving to done.
- 2026-10-22 lead: first real run on Godot 4.6.3: all engine, timeline, and formula tests pass. Progression review pending.
