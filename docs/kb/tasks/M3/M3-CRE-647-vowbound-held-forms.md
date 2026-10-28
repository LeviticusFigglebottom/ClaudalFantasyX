---
id: M3-CRE-647
title: "The six Vowbound as foes for their Ch20 release fights: held material sets, a release clip each, held battle scenes"
role: character
status: doing
owner_session: "creatures (worktree agent)"
reviewer: art
depends_on: [M3-CRE-646]
milestone: M3
request-from: creatures
---
## Goal
act3_roster.md "The Vowbound as foes" (M3-CRE-646). Ilun, Kahre, Virel, Hesk, Nhoa and Ethren are fought and released
in Ch20, one per layer (act_outline.md; vowbound.md "The final fight"). Each keeps one GLB; the foe form gets:
- a **held** material set: `glimmer_held` in place of `glimmer_bound`, otherwise the same, written by
  `common/write_materials.py` from a `held` block in the creature's materials.json into `materials_held/`;
- a **`release`** clip: the form's last unfurling, the light lifting off;
- its own battle scene `game/creatures/<id>/<id>_held_battle.tscn` and creatures.json row `<id>_held`, whose
  `phases` include the release (the material swap back to `glimmer_lift`-tinted light is presentation; motes are VFX).

## Acceptance criteria
- [ ] The six held scenes load headless with their clips, including `release`; the ally scenes and GLBs are unchanged
  except for the added clip.
- [ ] Every existing creature job verifies identical (the write_materials.py change must not change any other output).
- [ ] The validator accepts the `_held` rows (not Vowbound rows; no enemies.json row yet, Combat's).

## Review log
