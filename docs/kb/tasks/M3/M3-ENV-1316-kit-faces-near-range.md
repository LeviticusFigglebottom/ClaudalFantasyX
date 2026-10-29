---
id: M3-ENV-1316
title: "Request: kit pieces that read as plain at Act I's near range (trader boat's bales, Ashcrown's flying-stair side and tier faces, the headland arena's far hill)"
role: environment
status: todo
request-from: environment (env-art-b)
owner_session: ""
depends_on: []
milestone: M3
---
## Ask (from env-art-b's player-height walk-through and arena-angle passes, 2026-10-28)
These are env-art's kit meshes, so env-art-b can't fix them from the zones:
- **Corrow `trader_boat`** (Ch7 Tamsule's harbour, Ch8 Corrow's mole): its cargo bales take `cw_sail` and read as
  plain white cubes at player distance. Lashings, folds or a cloth texture would carry them.
- **Ashcrown `flying_stair` and `ashcrown_tiers`**: the stair's side and each tier's face are single flat dark planes
  tens of metres across. From the forecourt, and in `ashcrown_forecourt_day`'s battle angle, they read as bare walls.
  Coursing relief, buttresses or the copper veins running down them would carry them.
- **Coilspire `arena_headland_ground`** beyond about 45 m from the landing: broad flat facets behind the
  `coilspire_headland_path` arena's foe side. env-art-b added scrub out to 45 m (`b_headland_arena.py`), but past
  that the table's height function no longer matches the visible ground, so a scrub clump placed there floats.

## Review log
- **2026-10-28 (env-art-b), from the PC's GPU QA (act1_gpu_qa.md):**
  - Row 26: Ashcrown's tiers and crest ground read untextured grey at High (the kit's `ac_*` ashlar and crest
    materials).
  - Row 5: the Brine Shoals mudflat reads flat at High, and `camp_tent` reads as a box.
  Same ask as above: these are kit materials and meshes, which env-art-b can't fix from the zones.
