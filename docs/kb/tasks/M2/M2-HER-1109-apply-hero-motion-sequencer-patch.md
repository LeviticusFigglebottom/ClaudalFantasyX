---
id: M2-HER-1109
title: "Apply the HeroMotion sequencer patch so cutscene heroes ease into walks and runs (request to slice-polish)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M2-HER-1104]
milestone: M2
request-from: combat
---
## Goal
Cutscene heroes still get their walk speed from a flat sequencer value, and a `@move` run has no run start. The patch
`docs/kb/tech/hero_motion_sequencer.patch` routes cutscene clip plays through `HeroMotion` (eased cross-fades, idle
micro-motion), sets `sequencer.json` walk_mps 1.3 → 1.0 (ADR 0191's field walk speed, so feet don't skate), and has
`_cue_mark` call `HeroMotion.set_locomotion_speed(actor, run_mps)` at the start of a run move. This is part of the
human's #1 playtest complaint (rigid, snapping motion).

## Acceptance criteria
- [ ] `git apply docs/kb/tech/hero_motion_sequencer.patch` on claude/m2-slice (checked clean against 6c50823f on
      2026-10-25).
- [ ] cutscene, fp_ and haluna filters green; the prologue and beach cutscene shots viewed.

## Notes
- game/cutscene/** is m2-slice's (now slice-polish's); the hero track does not edit it.

## Review log
