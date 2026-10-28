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
  already set): `game/levels/_tests/characters/stillguard/stillguard_{a,b,c,d}_stage.tscn` (a, b, c map 1:1 to the capsules), and
  `stillguard_lineup.tscn` for all six. Capsules they replace (actor id = variant id, so the dialogue's
  `@anim stillguard_a level_spear` cues resolve): `game/levels/ch06/brine_shoals/brine_shoals_layout.json` actors
  `stillguard_a`, `stillguard_b`, `stillguard_c`; `game/levels/ch08/corrow/corrow_layout.json` actors `stillguard_a`,
  `stillguard_b`; `game/levels/ch09/corrow_night/corrow_night_layout.json` actor `stillguard` (any variant, e.g. d).
  The other cues on these actors (ch06 `walk_torch`, `hold_arm`, `kneel_palms_flat`, `let_go`; ch08 `shake_head`) are
  not in the M3-CHR-508 clip set: they need a `role: character` clip request.
  The scenes that build those capsules (act1_final_inventory.md): `game/levels/ch06/brine_shoals/brine_shoals.tscn`
  (a, b, c) and `game/levels/ch08/corrow/corrow.tscn` (a, b).

- 2026-10-28 (chr-npc-wip): the Act I villager builds are ready to swap in (M3-CHR-509..517, status review). Actor scenes (the
  GLB turned to face -Z like the capsules' Facing boxes; the import rule dresses it and puts the clip library on an
  AnimationPlayer): Haluna `game/levels/ch02/haluna/haluna.tscn` NPCs/Town/Shopkeeper ->
  `res://assets/characters/villagers/shopkeeper/shopkeeper_actor.tscn`, Smith -> `.../smith/smith_actor.tscn`, Innkeeper ->
  `.../innkeeper/innkeeper_actor.tscn` (field idle `idle`, talk `talk`; trade gestures `offer_goods`, `hammer_strike`,
  `welcome_bow`). Ch6 (`game/levels/ch06/**`, speakers as the scripts name them): `clerk` -> `.../clerk/clerk_actor.tscn`
  (`heat_iron`, `iron_into_water`, `hand_over`), `reed_a`..`reed_d` -> `.../reed_a/reed_a_actor.tscn` .. `.../reed_d/reed_d_actor.tscn`
  (`pole_barge`, `bow_from_barge`; the pole is a scene prop on DEF-hand.R), the girl at the brazier (mark `brand_girl`) ->
  `.../wright_girl/wright_girl_actor.tscn` (`arm_held_out`, `kneel_wait`), `wright_child_a`/`wright_child_b` ->
  `.../wright_child_a/wright_child_a_actor.tscn`, `.../wright_child_b/wright_child_b_actor.tscn` (`crawl_out`, `kneel_wait`).
  The Prologue's Vigil3..Vigil7 are the party, not villagers (see M3-CHR-518): swap them for Toma, Ysolde, Kerrid, Liss
  (built) and Pell (not built yet).

- 2026-10-28 (chr-npc-wip, named-NPC pass, M3-CHR-526..539, status review): actor scenes for the named Act I NPCs, each
  `res://assets/characters/villagers/<id>/<id>_actor.tscn` (faces -Z like the capsules; the import rule dresses it and
  adds its clip library). Ch1 `game/levels/ch01/oruvel/oruvel.tscn`: `sabe`, `scaleman`, `skipper_sadi`. Ch4
  `game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn`: `ferrymaster`, `purser`. Ch5 `game/levels/ch05/pemakar/pemakar.tscn`:
  `elder`, `garo` (also its ch05_kahre_bound variant); `game/levels/ch05/ashcrown/ashcrown.tscn`: `tender` (the same model in
  `ch08/coilspire/coilspire.tscn` and `ch09/corrow_night/corrow_night.tscn`). Ch6: `clerk` (above). Ch7
  `game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn`: `ione`, `poolkeeper`. Ch8 `game/levels/ch08/corrow/corrow.tscn`:
  `gatekeeper`, `hobb`, `marra`; `ch08/coilspire/coilspire.tscn`: `fenn`; Ch9 `ch09/corrow_night/corrow_night.tscn`: `fenn`,
  `hobb`, `marra`. Not built: `ivo` (a Stillguard, M3-CHR-540), `ferryman`/`ferryman_mate` (another track's).
  The generic villagers built before the Lead's re-split (shopkeeper, smith, innkeeper, reed_a..d, wright_girl,
  wright_child_a/b; M3-CHR-510..517) are committed and work; the creatures track's villager generator may supersede them.

## Review log
