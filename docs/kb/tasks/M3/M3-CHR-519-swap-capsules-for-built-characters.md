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

## Review log
