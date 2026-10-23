---
id: M1-ARC-13
title: Never drop Lattice progress when the lattice tables are missing or broken
role: architect
status: doing
owner_session: "worktree-agent-a26ce419921db7765"
depends_on: [M1-ARC-12]
milestone: M1
request-from: "qa"
---
## Goal
From the review-sweep-I entries (file:line references there).

## Acceptance criteria
- [ ] MUST: a broken or missing lattice_*.json never drops Lattice progress; no save is written while it is broken (mirror the ARC-12 ItemDB guard) (lattice_progress.gd ~:278-293, battle_rewards.gd ~:29)
- [ ] Unknown node ids are kept and round-trip untouched
- [ ] Tests with a torn, a missing and an empty lattice table
- [ ] Audit every other game/data table that save state references (party ids, inventory items, flags, locations) for the same failure mode and guard each; list them in architecture.md

## Review log
