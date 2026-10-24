# Handoff — cinematics — 2026-10-24 #6

Session: m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`. Task: M2-FP-14, B04 "Pila's Granddaughter" plus Haluna's two small inserts.

## Done
- **B04:** Grandmother Osu at the causeway head, at (−15, 1.53, −121.5), west of the B05 trigger box, on dry ground.
  - Talk prompt `npc_osu` from `ch02_met_asha`; the scene is `ch02_pila_granddaughter`, about 150 words in §4's five beats.
  - It sets `ch02_heard_pila`, and the chain into B09's Teyo line is tested. A second visit plays one short line.
  - H08 is a locked three-quarter shot; H08_hand is the insert on Teyo's shell.
- **The wall:** the real `wakeshell_wall` sits at (30, −196), 75 m past the walk rect and hidden by the coral tide-wall. Osu therefore stands at a greybox stand-in wall (`NPCs/Osu/ShellWall`): shells, the clean-edged gap at shoulder height, and a `Teyo` node. Filed **M2-ENV-04** for Environment to place the real piece.
- **B02 insert:** a bag stand-in (`NPCs/Neme/Bag`) in the lane behind Neme, and `@camera B02_bag` after her last line, then `@camera release`.
- **H03:** a "Look" prompt (`look_lintel_gull`, new key `FIELD_PROMPT_LOOK`) in the lane at house_tile_b's doorway gap. A raised camera holds on that house's ridge gull, with one Rhen line.
- **Night:** `night_hide` now also removes `NPCs/Osu` and `NPCs/Neme/Bag`.

## In progress
- Nothing. M2-FP-14 is in review (reviewer: narrative).

## Exact next step
- When M2-ENV-04 lands, delete the stand-in `ShellWall` box and shells, then re-aim H08 and H08_hand at the real piece's gap and Teyo node. The tests read those nodes by path.
- Osu needs a model, and the insert needs her hand. Both are stand-ins for now, like every slice NPC.

## Known issues
- H08_hand frames Teyo's shell among the others, but with no hand on it. The beat sheet's "inserts on Osu's hand" waits for a rig.

## Files touched
- game/levels/ch02/haluna/haluna.tscn (Osu, the stand-in wall, the bag, the gull prompt, four shots)
- game/data/dialogue/ch02/ch02_pila_granddaughter.dlg (new), ch02_look_lintel_gull.dlg (new), ch02_nemes_table.dlg; the compiled JSON; game/data/loc/dialogue.csv
- game/data/dialogue/speakers.json, game/data/loc/strings.csv (appended CHAR_OSU, FIELD_PROMPT_LOOK)
- game/data/flow/first_playable.json (night_hide)
- tests/integration/test_haluna_b04.gd (new), tests/integration/test_haluna_zone.gd
- docs/kb/tasks/M2/M2-FP-14-*.md, docs/kb/tasks/M2/M2-ENV-04-*.md (new)

## Gates
- lint and format; dlgc --check; validate_data; taskboard --check.
- The full Godot suite: 1355 run, all green after the test_haluna_zone shot-list update.
- No coverage step (no battle or progression code) and no shots (no manifest shot renders this scene).
