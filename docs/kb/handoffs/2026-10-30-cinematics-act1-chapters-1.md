# Handoff: act1-chapters (now chapters, with the combat seat), 2026-10-30, session 1

## Done
- **Act I rows (urgent):**
  - **Row 34:** the real cause was the double submit (M3-BPR-427). A second BattleRequest is now dropped while the
    first is opening, and field encounters hold off meanwhile. Tests added.
  - **Row 39:** reproduced green in real play (test_ch09_thread). The PC's walk reaches RoadGate under the night
    flags; the re-check recipe is in the live log.
- **Act II cameras (ADR 0205):** scene shots, marks and field camera volumes for Ch13 (A02–A06, S02, R02, R03),
  Ch14 (W02–W07), Ch15 (U02–U07, H02–H04) and Ch16 (P02–P04, D02–D07). Every frame was rendered and viewed. Ch12's
  Hall and pass-foot volumes are fixed.
- **Combat seat, engine:**
  - drain (`drain_pct`, M4-CMB-1001)
  - rooted (`root_turns`, M4-A2P-020)
  - glide and ambush (BattleCover, 021)
  - part repair (BattleParts, 022)
  - part-break targeting (`answered_by`, `when_down`, 023)
  - element cycling (BattleCycle, 025)
  - Nhoa's echo (BattleEcho, 024)
  - All with unit tests and validator rules.
- **Combat seat, data:**
  - The Act II Vowbound rows (Nhoa, Hesk, Ethren, Kesh; PROVISIONAL, `sfx_pending`).
  - One record row per Act II boss (big20), with my numbers: the Drowner, the Lamp Engine (now with its crawlers and
    lamps part), the Ram and the Wakefin.
  - All four suites are `--check` clean at 1,000 seeds.

## In progress
- Nothing un-pushed. The live log's last MERGE-READY line is the head.

## Exact next step
1. When integration-qa lands **M3-CIN-1251**, re-apply row 49's Pemakar harbour and weir positions (in the task),
   then run test_qa_field_camera and view the poi_views.
2. When story's Act II scenes reach integration (on `claude/act2-plan` today), wire the Ch10–Ch16 beats and triggers
   from docs/kb/plan/act2/chapters/ch1N.md §1–2.
3. When the Lattice and gear tiers (M4-A2P-030/031) land, add the Act II loadouts (M4-A2P-019) and re-run every
   Act II suite. The boss numbers are tuned against `ch08_seawall` today, so expect raises.

## Known issues
- The PC must re-check rows 34 and 39 (PC-QUEUE).
- Row 39 has an open LEAD-ASK: should companions follow on the night Strand?
- The full tools suite overran 20 minutes on this container. The battle and flow tool modules were run instead.

## Files touched (main)
- **Engine:** game/battle/{battle_cover,battle_parts,battle_cycle,battle_echo}.gd (new), battle_engine.gd,
  battle_hits.gd, boss_mechanics.gd, combatant.gd, enemy_ai.gd, ctb_timeline.gd, battle_vowbound.gd, formulas.gd,
  scene/battle_menus.gd.
- **Flow:** game/flow/battle_request.gd, game/world/zone/field_encounters.gd.
- **Data:** game/data/battle/{enemies,skills,encounters,vowbound}.json, choreo.json, creatures.json, flags.tres,
  loc ch10–ch16.
- **Tools:** tools/act1/ch12_greybox.py, ch13_greybox.py, ch14_greybox.py, ch15_16_greybox.py, poi_views.py,
  validate_data.py, battle_vfx_coverage.py, balance/targets.json.
- **Tests:** tests/unit/test_battle_{drain,rooted,cover,parts,answered_part,cycle,echo,request_double_submit}.gd,
  test_zone_story.gd, tools/tests/test_creatures.py, test_vowbound_sfx.py.
