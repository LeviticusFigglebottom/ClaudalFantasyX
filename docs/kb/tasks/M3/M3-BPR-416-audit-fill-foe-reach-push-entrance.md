---
id: M3-BPR-416
title: "Fill the staging audit: foes' blows staged by their reach, a push reaction, summoned foes walk in"
role: combat
status: review
owner_session: claude/battle-presentation
reviewer: lead
depends_on: [M3-BPR-411, M3-BPR-412, M3-BPR-413]
milestone: M3
request-from: lead
---
## Goal
The Lead (20:26): fill what the staging audit found missing, item by item, with tests, and log every remaining
entry as blocked with its reason.

## Done (2026-10-27)
1. **Foes' blows by their reach** (choreo.json `style_by_skill`; all existing styles, so no new audio row):
   - ranged or whole-party blows stay in place (cast): the crab's Brine Spit (its creature row already plays the cast
     clip), the Spar-Wraith's Shroud Sweep, the Reach's Undertow Pull. Before, each ran at one hero.
   - the foes' heaviest blows play the finisher: Hullgnaw's Gnaw (power 21), the Matron's Ladle Swing, the hound's
     Pounce.
   - Test `test_battle_party_kits.test_foes_stage_ranged_sweeping_and_heavy_blows_by_their_reach` (fails without).
2. **A push reaction** (choreo.json `reaction.push`, BattleChoreo.REACT_PUSH): a landed hit that only pushes its
   target down the timeline (Rope Dive, Grip the Stair and Hand Closes on the ward; the Drag Net) staggers it back.
   Before, it played no reaction at all. Reduced motion drops the tilt. Test `test_battle_push_reaction`.
3. **Summoned foes walk in** (BattleStage.add_enemy plays choreo.json `enter`): the flood's polyps, Rouse Polyp and
   the Reach's surges walk onto their marks instead of appearing. At instant pacing they are there at once.
   Test `test_battle_summoned_entrance` (fails without).
4. **The VFX audit names each gap's stage answer** (`tools/battle_vfx_coverage.py` `staged`); a tool test checks that
   every gap has one. All 17 skills and 8 items do.

## Blocked (each with its reason)
- **The particle for each VFX gap:** `game/data/vfx/battle/**` belongs to rendering (ownership.md). The proposed map
  is in request M3-BPR-411.
- **Sefir's kit:** no `sefir` row in characters.json (Act II). The kit audit covers it once the row lands.
- **The 6 Act II creatures and bosses:** no enemies.json rows yet. The audits cover them once the rows land.
- **Kerrid's and Liss's real clips:** request M3-BPR-412 (characters). Placeholder clips stand in.
- **A dedicated dive or sweep style for foes:** each new style needs an audio choreo_sfx row (the `dive` row plays
  Rhen's Swell accent). The stand-ins above read correctly until audio adds rows (as with M3-BPR-410).

## Review log
