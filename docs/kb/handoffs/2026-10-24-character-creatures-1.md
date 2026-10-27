# Handoff — character (creatures) — 2026-10-24 #1

Environment `creatures`, branch `claude/creatures` (cloud session_01CYks9e592YBEfygyTawcJD). The live log is
`docs/kb/handoffs/live/creatures.md`; the earlier session handoff is `2026-10-24-character-21.md`.

## Done
- **Act I bestiary:** 27 creatures built, wired and shot-approved. Each has a design sheet in
  `docs/kb/art/creatures/act1/`, a procedural Blender build in `assets_src/creatures/<id>/`, a byte-identical job,
  PROVENANCE rows, a creatures.json row and a review shot. Ch7 has no foes and Ch9 has no fight.
  - Bosses: hullgnaw, spar_wraith, cinder_matron, the raid_hound pair, undertows_reach, plus the slice Drownbell.
  - Variants built by importing a base build: wreck_crab, wall_polyp, squall_wing, stormgull, wallcrab.
- **Phases match m2-slice's enemy ids:** flood, breaking, pour, hauled_down; dark and breach for Ch8.
  - New CreatureActor phase keys: `show`/`hide`, `hide_after`/`show_after`, and a `clips` map for phase strikes.
- **Clip contract (M2-BPR-02):** every creature has idle, attack, cast, hit and ko, with contact times. Strikes are
  in place (kit `IN_PLACE_CLIPS`). BattleChoreo now plays the action and hit clips; that landed in big7.
- **Slice polish:**
  - LOD1 is covered by Godot's import LODs (`tools/dev/creature_lods.gd`).
  - Portrait framing set for the gull and the eel.
  - Polish passes done on the Matron, squall wing and wreck crab.
- **Integration:** big7 (with the models) is merged, and m2-slice's `model` lines landed on claude/m2-slice. The
  polish batch rides big8 (MERGE-READY @ b6d98d1c and later commits).

## In progress
Nothing.

## Exact next step
After big8 merges, merge the integration branch and check that m2-slice's spar_wraith `hauled_down` rows validate.
Then add `undertows_reach` `dark`/`breach` when m2-slice builds Ch8. New task ids use the 600–699 block (M3-CRE-6xx),
ADRs 0150–0159, and handoffs `<date>-<role>-creatures-<n>.md`.

## Known issues
- The Matron's re-crust mid-`pour` needs a battle-presentation hook. The `Crust` mesh is ready; see
  act1/cinder_matron.md.
- send_message to the Lead fails (elevated_session_untrusted_device), so the live log is the channel.
- The wreck crab's leg barnacles are faceted (58 triangles of budget left). The Matron's yoke cells are still even.
- The Undertow's Reach `water` slot is a creature-shader stand-in for the PC GPU session's Undertow look.

## Files touched
assets_src/creatures/**, assets/creatures/**, game/creatures/**, game/data/creatures/creatures.json,
game/data/import/creatures.json, tools/validate_creatures.py, tools/tests/test_creatures.py,
tools/dev/blender_builds.json, tools/dev/creature_lods.gd, tests/unit/test_creature_actor.gd,
tests/screenshots/{shots.json,baselines/*}, assets/PROVENANCE.md, docs/kb/art/creatures/**,
docs/kb/tasks/M3/M3-CRE-0*, docs/kb/handoffs/live/creatures.md.
