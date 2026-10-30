---
id: M4-A2P-052
title: "Liss's father, and the Ansedran, Hollowmere and Quellan crowd costume sets"
role: character
status: doing
owner_session: "claude/characters"
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
Hollowmere's dock-master (named by M4-A2P-006) as a named NPC, and three costume sets on the crowd generator: Order Ansedrans (Tenders, pilgrims, barge-polers), Saltwrights (Hollowmere) and Ullari (Quellan).

## Acceptance criteria
- [ ] Built and baked; crowd rows; shots viewed.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch12, Ch13, Ch15.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30 (characters): **Aldous Varrow**, the dock-master (ADR 0204 §4), is built on the villager path
  (`params/aldous.json`).
  - **Look:** Liss's and Tobin's family face, older, heavier and sun-dark, with a grey crop. Line-marks run to the
    shoulders (forearm 7, upper arm 6, collar 2) and show on a sleeveless salt-faded tunic.
  - **Face rows:** a held-in `grief` for H05-H06.
  - **Clips:** `push_raft` (H13) and `hold_up_housing` (H14), plus `nod`.
  - **Shots:** villager_aldous_* (5, viewed).
  - **Checks:** villager_aldous is identical on the 3 numpy paths; test_villagers passes.
  - **Open:**
    - The dock-hook and the salt-glass lamp-housing are hand props for Cinematics to attach (prop request to follow).
    - The three crowd costume sets live in the crowd generator (`assets_src/crowd/**`, `crowd.json`), which
      ownership.md gives to the creatures track. LEAD-ASK in characters.md: route them to creatures, or reassign
      the claim?

## Review log
