---
id: M3-CRE-666
title: "Haluna lived in: ambient crowd vignettes at the causeway head, in the lane and on the dock, by day and at night"
role: character
status: review
owner_session: "creatures (claude/creatures)"
depends_on: [M3-CRE-659]
milestone: M3
reviewer: character
---
## Goal
The Lead, 2026-10-30: "the Act I crowd behaviour in the slice zones (Haluna, the causeway, the dock at night): ambient
vignettes such as mending nets, carrying baskets and children playing, so the towns feel lived in." Haluna had only its
named villagers, with no crowd.

## Acceptance criteria
- [x] Crowd people at work beside what they would work on: the causeway head (fish rack, stall, a line hauled at the
      water's edge, children at stones), the tide-wall lane (a mender at the net heap, a basket carrier, children at a
      clapping game, a sweeper) and the dock (a mender, fish turned on the rack, a mooring line hauled, a basket of the
      catch). There are 15 people, on the ground probed against the zone's collision.
- [x] Children play: new crowd clips `play_stones` and `play_clap` (crowd_clips.py), in the child libraries.
- [x] The dock at night: a row's `shown` (`day` / `night`) follows the zone's `is_night` (VillagerLayer). The dock's
      people and the children are gone home, the lane's mender and sweeper work by lamplight, and one woman brings the
      last basket home.
- [x] No body already placed in another zone moves (`assign.late_zones`).
- [x] Tests (tools test_npc; Godot test_crowd_villagers) and review shots `npc_haluna_vignette_*`.

## Review log
