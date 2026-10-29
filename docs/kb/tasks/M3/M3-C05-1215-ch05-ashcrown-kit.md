---
id: M3-C05-1215
title: Ch5 greybox to final, ch05/ashcrown on env-art's Ashcrown kit (blocked on steep-stair traversal)
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-ENV-09, M3-C05-02, M3-ARC-1216]
milestone: M3
reviewer: qa
request-from: ""
---
## Goal
Swap Ashcrown's flat greybox (the outer pilgrim stair, the four inner trial tiers, the anvil court) to env-art's
Ashcrown kit (ashcrown.md), keeping the trial (AshcrownTrial: rods, gates, plates, releases, the Stair_<tier> walls)
and the Matron's arena.

## Blocker
The kit's ways up and down are steeper than the field controller can walk (it has no step-up and a 45° floor):
- the **flying stair** is 48° (172 risers of 0.267 m) from the forecourt (y −4) to the top tier (y 42);
- the trial's **vein stairs** down each tier's front face are 60°, 0.9 m wide;
- the causeway (0.22 / 0.23 m risers, landings every 32) is fine as ramps.
A ramp can't stand in for a 48° or 60° flight. That needs a decision (M3-ARC-1216): a steep-stair traversal (an
interact at a flight's foot or head that plays a climb and places the party at the other end), or env-art re-cutting
the flights under 40°. Until then the zone stays the greybox.

## Notes
- The kit's frame: tiers k = 0..6, tops y 6 + 6k (tier 0 to y 6), forecourt y −4 (z 19 → 45), hall inside tiers 0-1,
  the pavilion on the top tier at z −8.4. The vein path (§0.2) gives the trial its route; each tier's veins have
  their own material slot (`ac_vein_t<k>`) so the strike can light a tier at a time (`ac_copper_live`).

## Review log
- 2026-10-29 act1-chapters: superseded by env-art-b's M3-ENV-1303 (Ashcrown on its kit, with M3-ARC-1216's steep
  stairs), on the integration branch. My side, the story cameras and Kahre's staging, is done (see M3-ENV-1303's
  review log). To review, for closing.
