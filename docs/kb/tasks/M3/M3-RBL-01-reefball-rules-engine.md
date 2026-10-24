---
id: M3-RBL-01
title: Reefball rules engine for the Ch7 story match (headless core, data, AI, odds preview, balance sim)
role: combat
status: doing
owner_session: "worktree-agent-a7b959d1ec6dbcb5d"
reviewer: lead
depends_on: []
milestone: M3
request-from: "lead"
---
## Goal
A headless, deterministic, seeded Reefball rules core (SPEC §6.10, M3 "including the Reefball story
match") for the Ch7 Tidecup opening round: Oruvel's side (Tavi Orse captains, Rhen dives; ADR 0017)
against one other side. Turn-paused and tactical: the player decides at contact moments, and every
decision shows its odds before it is taken (pillar 4). No UI and no scene: a clean API and signals
for the UI track and the arena look later. Small and solid, so M6 "extended Reefball" builds on it.

## Acceptance criteria
- [ ] RefCounted core under `game/minigames/reefball/` (SPEC §5.1 layout): match state, divers with
      stats, possession, passes and lofts resolved by data-driven formulas, a stroke clock, scoring,
      and an AI for the opposing side. No Node or scene dependencies; all randomness through one
      seeded `rng`.
- [ ] An exact odds preview for every legal action (the same function resolution uses).
- [ ] Data in `game/data/reefball/*.json`; a validator section appended to `tools/validate_data.py`
      with unit tests in `tools/tests/`.
- [ ] Unit tests in `tests/unit/test_reefball_*.gd`.
- [ ] A balance sim (`tools/balance/reefball_sim.py`) with bands showing the story match is winnable
      but not trivial.
- [ ] Rules are original (CLAUDE.md §2): no terms, rules or layout from the inspiring game's sport;
      near-misses added to `tools/banned_terms.txt`.
- [ ] Design doc `docs/kb/design/reefball.md`.

## Notes

## Review log
