---
id: M4-A2P-081
title: "Portraits for Act II's new people, bosses and Vowbound"
role: ui
status: doing
owner_session: "ui-menus (claude/ui)"
depends_on: [M4-A2P-050, M4-A2P-051, M4-A2P-052]
reviewer: character
milestone: M4
request-from: lead
---
## Goal
Bake portraits for Tobin, Merel, Malcor Venn, Liss's father, the Kirru eldest and child, the Ullari woman, the Abiding guard, Kesh, and any other speaking NPC the beat sheets add.

## Acceptance criteria
- [ ] Portraits via `tools/portraits/`; manifest rows; viewed.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.5.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30 ui-menus: **Kerrid's `guilty` baked** (kerrid.md section 2): portraits.json lists it, the bake is viewed (gaze lowered, distinct from grief), PROVENANCE row, test_hero_portraits::test_kerrid_has_the_guilty_face_for_his_reveal. The Status page's "Unrisen: held since the stair at Corrow" line shows under his name after `ch15_kerrid_revealed` (declared; the reveal's script sets it), test_status_menu, render viewed. The NPC bakes still wait on their models (characters track).

- 2026-10-30 ui-menus: **Warden Malcor Venn's face is baked** from his model (M4-A2P-051, venn.glb on the Stillguard kit): neutral, cold and determined (tools/portraits/portraits.json `venn`, rendered from his `venn_face_cold` stage, whose face poses are Asha's; PROVENANCE rows). The dialogue box shows it for speaker `malcor_venn` (dialogue_portrait.json alias), so his Ch14 decree (ch14_the_vows.dlg, [cold]) reads with his face. test_hero_portraits, test_dialogue_box; the three bakes viewed. Note for characters: on his face Asha's pose weights read faintly, so the three look nearly alike at 256 px; a Venn face-pose table would give the decree its chill. Still waiting: the Abiding guard (no model yet).

## Review log
