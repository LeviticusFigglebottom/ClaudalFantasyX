---
id: M3-UI-211
title: "Act I menus at final quality (ADR 0041): no letters for pictures, real icons, every Act I screen audited"
role: ui
status: review
owner_session: claude/ui (ui-menus)
reviewer: qa
depends_on: []
milestone: M3
request-from: lead
---
## Goal
The human's refocus (ADR 0041) puts every screen from the title through Ch9 at final quality. The audit and its results are `docs/kb/qa/ui_act1_menu_audit.md`.

## Acceptance criteria
- [x] Hero faces in the battle HUD (party rows, timeline); foe pictures in the timeline.
- [x] Ysolde and Liss portraits.
- [x] Icons for items, equipment and abilities in every menu row: bag, shop, equip, battle Skills, Swell and Items, the victory panel.
- [x] Every bestiary creature has a portrait.
- [x] No zone map says Haluna's idle line outside Haluna.
- [x] Tests: test_battle_portraits, test_menu_glyphs, test_hero_portraits (five heroes), test_creature_portraits.
- [x] Kerrid's portrait, when M3-CHR-505 lands. (`kerrid_*.png` are on lead/gate-big17.)
- [ ] The Inquisitor's bestiary picture, when his model lands (M3-C06-06).
- [ ] Baselines: the Lead's gate re-renders and approves. The shots are self-rendered and viewed in the live log.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **verified on lead/gate-big17; left in review for two items.**
  test_battle_portraits 3/0, test_menu_glyphs 3/0, test_hero_portraits 9/0, test_creature_portraits 4/0. Kerrid's
  portraits are there (box ticked), and Pell's are on claude/ui. Still open:
  - the Inquisitor's bestiary picture: big17 has no `stillguard_inquisitor` creature portrait; in battle he stands
    in on Moll's model;
  - the Lead's baseline approval.
  Close when both are in. Nothing else to change.
