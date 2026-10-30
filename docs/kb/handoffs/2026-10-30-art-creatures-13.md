# Handoff: art (creatures), 2026-10-30, #13

Branch `claude/creatures`. The live log is docs/kb/handoffs/live/creatures.md. Its MERGE-READY lines are @ 3bf5cb75
(the as-played fixes) and @ 7b5deabd (the Haluna crowd); the commits after them are docs only.

## Done (the Lead's 10:27 directive)
- **The as-played pass:**
  - Every Act I and Act II regular rendered in its encounter's real battle (35 encounters; `arena_shot.gd` on the
    encounter's arena and lineup). All 35 stills viewed.
  - Fixed: the fen leech is bowed lengthwise and has a thicker body; the glass skate has its gloss cut, a darker,
    wider rim and an eyespot on each wing. Portraits re-rendered; both builds byte-identical.
- **Crowd variety, Haluna:**
  - The shopkeeper, smith and innkeeper are crowd people now, from a `haluna` community and a `smith` role.
  - validate_npc reads a stage actor that contains a `/` as the stand-in path.
  - VillagerLayer replaces the borrowed-model villager that HalunaVillagers places first. A unit test covers it.
- Every Act I zone was checked: no body repeats within a zone and no row borrows a model.

## In progress
Nothing.

## Exact next step
- The Lead's answer to the LEAD-ASK: the crowd people, or M3-CHR-512's bespoke shop villagers. To ship the bespoke
  ones, drop `crowd` from the three ch02_haluna.json rows; slice-polish then deletes haluna_villagers.json's rows.
- When characters land the Act II crowd sets (the Kirru clutch, the Ansedran, Hollowmere and Quellan sets;
  act2_tracks.md row 55), wire their VillagerLayer zone rows in game/data/world/npc/zones/.
- Rewrite the baselines for `creature_fen_leech` and `creature_glass_skate` (the Lead).

## Known issues
- Battle layout: enemies in one rank overlap (ch02_tideline, ch05_stair_tortoises, ch10_fen_roots,
  ch06_flats_crabs), and one sits under the command menu in the underway_tower encounters. Battle presentation's.
- Ch11 and Ch16 encounters name no arena.
- Pre-existing reds: test_palette_check on the `haluna_h07_chapel_court` baseline; `oruvel_seabed.glb` has no
  Blender job.

## Files touched
assets_src/creatures/{fen_leech,glass_skate}/; assets/creatures/{fen_leech,glass_skate}/;
assets/ui/portraits/creatures/{fen_leech,glass_skate}.png; assets_src/crowd/{ranges.json,params/}; game/data/world/npc/
{crowd.json,zones/ch02_haluna.json}; tools/validate_npc.py; tools/tests/test_npc.py; tests/unit/test_crowd_villagers.gd;
docs/kb/plan/act2/creatures/{fen_leech,glass_skate}.md; docs/kb/tasks (M2-CHR-100 note); the live log.
