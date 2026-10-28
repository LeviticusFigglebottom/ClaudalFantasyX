---
id: M3-BPR-1340
title: "Battle framing and formation spacing for Pell (2.30 m, the staff tip 30 cm higher still)"
role: combat
status: todo
owner_session: ""
depends_on: [M3-CHR-506]
milestone: M3
request-from: character
---
## Goal
Pell (M3-CHR-506, `docs/kb/art/characters/pell.md` §2.5 and §12 items 9-11) is the tallest hero: his crown sits 40-60 cm
above the others' and his staff's tip about 30 cm above his crest (2.6 m). Battle-presentation and UI+Combat keep his
head and the staff tip in frame at every battle camera framing, and give him enough formation spacing that his staff
(planted beside his left foot) does not cross his left neighbour.

## Acceptance criteria
- [ ] The battle camera's widest framing and its over-the-shoulder framings keep Pell's crest and staff tip in frame
      (check with `game/characters/heroes/pell_battle.tscn` on `pell_lod1.glb`, and the `pell_silhouette_lineup` shot
      for scale against the other heroes).
- [ ] The formation slot spacing on his left clears the staff (about 0.3 m out from his left foot).
- [ ] The sheet's open questions answered or carried with their defaults: "Listen" plays the `read` clip (no 13th clip);
      learned abilities play `cast` (a `choreo.json` style choice if a physical one should play `attack`).

## Notes
- His battle actor's library is `assets/characters/pell/anim/pell_clips.tres` (the 12 contract clips with contact markers
  at the shared `contact_at`, and `revive`). His `attack` darts the staff down and forward to knee height at reach
  (about 1.6 m in front of him); `finisher` sweeps the staff's foot low across the front from his left to his right.
- The battle actor shows the blank name-shell; `PellNameShell.apply(root, true)` shows the carved one after Ch9's
  re-carving (Act III), when the story flag lands.

## Review log
