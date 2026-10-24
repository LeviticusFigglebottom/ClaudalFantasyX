---
id: M3-RBL-01
title: Reefball rules engine for the Ch7 story match (headless core, data, AI, odds preview, balance sim)
role: combat
status: review
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
- [x] RefCounted core under `game/minigames/reefball/` (SPEC §5.1 layout): match state, divers with
      stats, possession, passes and lofts resolved by data-driven formulas, a stroke clock, scoring,
      and an AI for the opposing side. No Node or scene dependencies; all randomness through one
      seeded `rng`.
- [x] An exact odds preview for every legal action (the same function resolution uses).
- [x] Data in `game/data/reefball/*.json`; a validator section appended to `tools/validate_data.py`
      with unit tests in `tools/tests/`.
- [x] Unit tests in `tests/unit/test_reefball_*.gd`.
- [x] A balance sim (`tools/balance/reefball_sim.py`) with bands showing the story match is winnable
      but not trivial.
- [x] Rules are original (CLAUDE.md §2): no terms, rules or layout from the inspiring game's sport;
      near-misses added to `tools/banned_terms.txt`.
- [x] Design doc `docs/kb/design/reefball.md`.

## Notes
- **Path:** the code is in `game/minigames/reefball/` (SPEC §5.1's layout, where a `.gitkeep` already
  stood), not `game/reefball/` as the brief said.
- **Rules (design doc):** five depth bands from the ring (surface) to the weep; one shared ring; the
  **fetch rule** (a float must go to low water or deeper before it can score); rise, dive, pass, loft;
  breath that only the ring gives back; roles that swim to data-driven bands; a 48-stroke clock with up
  to three golden overtime periods.
- **Balance (2000 seeds):** naive (carry it yourself) 18.4% wins, smart (reads the odds) 66.8% with
  4.0% draws, the opponent's own brain on Oruvel's side 55.2%. Bands: naive 10–30%, smart 55–80%.
- **Coverage (proposal):** `game/minigames/reefball` added to `MEASURED_DIRS` at 100% (421/421 lines);
  the baseline rows came from a `--filter=reefball` run.
- **For Narrative:** the opposing side (Pemakar Terraces) and Oruvel's other two divers (Noa, Old Ama)
  are provisional loc names.

## Review log
