---
id: M3-ENV-106
title: "The colour script's grades as runtime looks, so `@camera grade=` and a node's `grade:` take effect"
role: environment
status: todo
owner_session: ""
depends_on: []
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
M3-HER-1123's last cue placeholder. The `.dlg` scripts name colour-script frames (cues.json `sets.grades`: ch02,
ch02_noon, ch02_night, ch03, ch03_causeway, ch03_steps, ch03_boss, ch03_shrine_int), on a node (`grade:`) and on a
cut (`@camera C08 grade=ch03_boss`). The sequencer drops them: no table maps a grade id to a look. The art docs
define each (haluna.md §0: sun, ambient, LUT, exposure).

By the Lead's split (10-28), zone and kit looks are env-art-b's, so this is a request for the data. Slice-polish
wires the sequencer once it exists.

## Ask
- [ ] One file, e.g. `game/data/art/grades.json`: per grade id, an Environment `.tres` (LUT, exposure, ambient, fog)
      and the key light's colour, energy and angle. Or say which existing zone environments to reuse. Slice-polish
      then blends to it on `grade=` (over the cut's blend) and applies a node's `grade:` as the node starts.

## Review log
