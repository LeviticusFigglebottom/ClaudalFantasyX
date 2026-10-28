# UI audit for Act I at final quality (ADR 0041)

The ui-menus track's audit of every screen a player meets from the title through Ch9, for stand-ins: letters for
pictures, missing icons, placeholder text, frames or art. It feeds integration-qa's `act1_final_inventory.md`.
Task: M3-UI-211. Last updated 2026-10-28.

## How it was checked
- **Code sweep:** UI scripts for initials, fallbacks and placeholders. Loc and UI data for placeholder words.
- **Coverage scripts:**
  - every status has a glyph;
  - every enemies.json row has a bestiary portrait;
  - every Act I location has a map;
  - every item, piece of equipment and skill has an icon (`test_menu_glyphs.gd`).
- **Self-rendered and viewed** (TRACK-RULES 2026-10-28):
  - the battle HUD set;
  - the items, shop, equip and victory screens;
  - the Kite, field menu and map screens;
  - the `menu_glyphs` review sheet.

## Found and fixed

| Where | Stand-in | Fix |
|---|---|---|
| Battle party rows, timeline | The hero's initial in a coloured square; foes as a bare diamond | Hero faces (worried while down) and foe bestiary pictures (BattlePortraits). 71689a7b |
| Every menu with a hero picture (field menu cards, formation, status, equip, Lattice) | Ysolde and Liss had no portrait, so their initial showed | Both baked (five emotions each, viewed), with PROVENANCE rows; Ysolde's framing and face crop are her own. 71689a7b |
| The bag, shop, equip, battle Skills / Swell / Items | Rows of text, no icons | MenuGlyph: 43 original vector icons (items, equipment types, skill elements and kinds, the lume), drawn in StatusGlyph's style. 1a79cdc9 |
| Victory panel | Names only | Fighter faces, drop icons, the lume's coin. 2b0a5ffb |
| Bestiary | Portrait-less creatures in the manifest | Every creature baked; test_creature_portraits passes. 5f9c71fd |
| Zone maps (all zones) | "Haluna's lanes are yours to walk" in every zone with no errand | A general idle line, Haluna keeps its own (`idle_keys`). 5f9c71fd |
| Lattice overview | Initials crowding the name tags | Initials that touch a tag are left off. a8558176 |

## Checked and already final
- **Statuses:** all 21 have their own glyph, shape-coded, not hue alone.
- **Bestiary:** every Act I enemy with a model has a portrait.
- **Maps:** every Act I field location has a map (the Prologue is a cutscene with no field).
- **Codex:** covers Act I (34 entries).
- **Strings:** no placeholder words in any loc file.

## Waiting on other tracks (not ui's to make)

| Stand-in | Owner | Then ui |
|---|---|---|
| **Kerrid** (Ch5 to Ch9 party): no model. His battle body is the default primitive, and his menus and battle slots show "K". | character, M3-CHR-505 (doing) | Add him to the portraits manifest, bake, and view. The letter falls back automatically until then. |
| **The Stillguard Inquisitor** (Ch6 boss): no model. Capsule in battle, no bestiary picture. | character, M3-C06-06 (Inquisitor Hadric Moll) | Bake his bestiary portrait once his battle actor exists. |

## Re-rendered after the fixes
- **Pass:** reefball_hud_choice, reefball_outfitter, cutscene_act_card and save_menu all pass with no change.
- **dialogue_continue:** only the palms' wind moved, an environment change outside ui. The box is unchanged and has no stand-in.
