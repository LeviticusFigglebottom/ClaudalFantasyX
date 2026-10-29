---
id: M3-CIN-1240
title: "Pell's face poses in the cutscene sequencer: the crest column and the 0.25 s onset delay"
role: cinematics
status: todo
owner_session: ""
depends_on: [M3-CHR-506]
milestone: M3
request-from: character
---
## Goal
Pell's face (M3-CHR-506, `docs/kb/art/characters/pell.md` §6 and §12 item 12) is on the shared 40-shape API, plus two
keys on his `Crest` mesh: `crest_raise` and `crest_flat`. **His crest speaks before his face does:** each `@face` tag
carries a crest value, and the face itself starts 0.25 s after the crest. The table is
`game/levels/_tests/characters/pell/pell_face_poses.json` (`emotions` rows with `crest_raise`, `grief` also
`crest_flat` 0.4; `crest` the column alone; `blend_in_s` 0.36; `onset_delay_s` 0.25).

## Acceptance criteria
- [ ] The sequencer's `face_poses` entry for `pell` applies the crest values with each tag (the shapes are found by name
      on any mesh of the model, as AshaStage does).
- [ ] The face shapes start `onset_delay_s` after the crest and blend over `blend_in_s`.
- [ ] Ch9 B09: "His crest lifts a little" at Kerrid: `crest_raise` 0 -> 0.35 over 0.8 s with the face held `neutral`.
- [ ] Ch8 Storm-Call (seawall, rain): the wet materials (`*_wet.tres`) and `crest_flat` 1.0 (see the `pell_storm_ch8`
      review shot).

## Notes
- The name-shell has two meshes, `NameShellBlank` and `NameShellCarved`, one visible at a time:
  `PellNameShell.apply(root, carved)` (`game/characters/heroes/pell_name_shell.gd`). The blank one is the default until
  his Act III re-carving.

## Review log
