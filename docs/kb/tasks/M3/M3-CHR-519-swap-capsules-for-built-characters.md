---
id: M3-CHR-519
title: "Request: swap the Act I capsules whose characters are already built"
role: lead
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: character
reviewer: character
---
## Goal
The characters track's Act I audit found capsules standing in for characters whose models already exist
(assets/characters/<id>/): heroes Rhen and Asha in `game/levels/prologue/prologue.tscn` (City/Vigils/Rhen, Asha);
Rhen and Toma in `game/levels/ch03/first_verse/first_verse.tscn`; Rhen in `game/levels/ch03/shell_shrine/shell_shrine.tscn`;
Rhen, Toma, Osu, the vendor, Reed, the net-mender and the fisher in `game/levels/ch02/haluna/haluna.tscn`. Those scenes
are owned by the M2 slice (ownership.md), so this is a request: instance the character scenes (the hero stage or the
villager scenes) in place of each capsule, with their field idle.

## Acceptance criteria
- [ ] Each listed capsule replaced by its built character; the levels' tests still pass.
- [ ] Anything a level needs from the character side (a clip, a scene wrapper) filed back as a `role: character` task.

## Notes
- Filed 2026-10-27 by the characters track. Not ours to edit (the M2 slice owns game/levels/prologue, ch02, ch03); the Lead routes it.
- 2026-10-28, M3-CHR-508: the Stillguard soldiers are built, six variants `stillguard_a`..`stillguard_f`, each at
  `assets/characters/stillguard_<v>/stillguard_<v>.glb` (+ `_lod1.glb`, `materials/`, `anim/stillguard_<v>_clips.tres`
  with idle, walk, stand_watch_seaward, shield_up, level_spear). Stage wrappers to copy (materials and the field idle
  already set): `game/levels/_tests/characters/stillguard/stillguard_{a,b,d}_stage.tscn`, and
  `stillguard_lineup.tscn` for all six. Capsules they replace (actor id = variant id, so the dialogue's
  `@anim stillguard_a level_spear` cues resolve): `game/levels/ch06/brine_shoals/brine_shoals_layout.json` actors
  `stillguard_a`, `stillguard_b`, `stillguard_c`; `game/levels/ch08/corrow/corrow_layout.json` actors `stillguard_a`,
  `stillguard_b`; `game/levels/ch09/corrow_night/corrow_night_layout.json` actor `stillguard` (any variant, e.g. d).
  The other cues on these actors (ch06 `walk_torch`, `hold_arm`, `kneel_palms_flat`, `let_go`; ch08 `shake_head`) are
  not in the M3-CHR-508 clip set: they need a `role: character` clip request.

## Review log
