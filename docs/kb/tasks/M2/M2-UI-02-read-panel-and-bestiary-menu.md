---
id: M2-UI-02
title: Read result panel, bestiary menu and opening banner
role: ui
status: done
owner_session: "worktree-agent-ab3d864d1e75fe481"
depends_on: [M1-CMB-03]
milestone: M2
request-from: combat
---
## Goal
SPEC §6.1 and §6.11. M1-CMB-03 ships Read, the bestiary log and preemptive/ambush openings with only two float lines for feedback. Give them real HUD and menu views.

## Acceptance criteria
- [x] After a Read, a short panel shows the foe from `BattleController.bestiary.last_reveal` (`BattleRead.reveal`): name, HP and MP as they stand, the eight stats, the four affinity lists, delay immunity, current statuses, and the lore text (`lore_key`). It closes on confirm and costs no battle time.
- [x] A bestiary menu (out of battle) lists `Bestiary.known_ids()` from `Game.state.bestiary`. A Read entry shows the page from enemies.json (stats, weaknesses, lore) and the defeat count. An entry that was defeated but never Read shows its name and count only. Ids enemies.json no longer lists are skipped on screen, never removed from the save.
- [x] A clear banner for a preemptive or ambush opening (`BattleOpening.CAPTION_KEYS`, `engine.opening`), replacing or joining the float that `BattleBestiary` shows today. Keep it within the HUD build budget (M1-UI-03), and add screenshot fixtures if it is visible in a capture.
- [x] New strings go through loc keys appended to strings.csv. Element names are already there as `ELEMENT_*`.

## Notes
- Rules and data: docs/kb/design/battle_ctb.md "Read, the bestiary and openings", formulas.md § Openings.
- **Reviewer: combat** (the requester; BattleBestiary, BattleFixture and one controller line changed). Branch `worktree-agent-ab3d864d1e75fe481`, not pushed. How it is built: tech/ui.md § Read, the bestiary and openings, and deviations 10-12.
- **Read panel.** `EnemyPage.from_reveal` (Node-free words) + `EnemyPageView` (layout, shared with the bestiary) in `ReadPanel`, opened by `BattleBestiary` on every Read of a foe. The weakness float stays. It closes on confirm, cancel or a click, and swallows the other `ui_*` actions while it is open.
  - **No battle time:** `BattleHud.holds_battle()` is a condition added to an existing line of `BattleController.tick()`, so every wait holds until it closes. The Read paid its rank and nothing else moves.
  - Instant pacing (tests, captures) drains waits inside `act()`, so the `battle_read_panel` capture shows the next turn already open under the panel. In live pacing the controller is `busy` then.
- **Opening banner** (`OpeningBanner`). It replaces the caption float with a title, the caption and what the opening means for the order ("Every foe acts before your party."). It sits on a fading dark band for contrast, and the rule ends carry the timeline's side shapes (square: preemptive, chevron: ambush), so it is not hue alone. Reduced motion drops its rise. Both views are built on first use (`BattleHud.read_panel()`, `opening_banner()`), so the staged build (M1-UI-03) is unchanged.
- **Bestiary menu** (`game/ui/bestiary/`). `BestiaryMenu.open_in(host)` over `BestiaryMenuModel.from_game()`: logged foes in enemies.json order with `×N`, and "Not Read" in words on unread rows. A Read foe gets the full page from its row and the defeat count; an unread one its name, count and how to learn more. Ids the table dropped are skipped (`skipped_ids()`) and kept in the save. It pauses the tree like SaveMenu. **Not reachable in play yet:** there is no field or party menu to open it from. Whoever builds one calls `open_in`.
- **Fixtures and shots:** `BattleFixture.battle_opening` (applied in `prepare()`). Fixtures `read_panel` (the frozen tables gain the `read` row, and overrides add lore keys) and `opening_banner`. New shots `battle_read_panel`, `battle_opening_banner` and `bestiary_menu`, viewed and approved.
- **Tests:** `test_read_panel.gd` (12), `test_bestiary_menu.gd` (8). `test_bestiary.gd`'s caption-float test now checks the banner.
- **Follow-ups (not done):** the target info panel still says "HP unknown until Read" for a foe the party has Read (`revealed: false` in `BattleController._show_pick`). Combining it with `bestiary.book.is_read` is a one-line change at the controller's cap. The art review of deviations 10-11 is in M2-ART-01.
- **Gate:** `HYMN_SHOTS=battle_read_panel,battle_opening_banner,battle_swell_modes,bestiary_menu,battle_hud_preview,battle_swap_menu,battle_swell_ring,battle_statuses,battle_victory tools/ci_local.sh` rc 0 at b2dbe53: validate_data 0/0, tool tests 411 OK, audio 9 OK, taskboard, gdlint and gdformat clean, **1105 Godot tests, 0 failed**, coverage battle 99.93% (1524/1525) and progression 96.52% (unchanged from baseline), boot smoke OK, 9 shots at rmse 0. Filters beforehand: swell 62, bestiary 27, read_panel 12, swell_mode 12, ui 87, battle 287, all passing.

- **Gate after merging claude/new-session-mj8c3c (merge 9186104):** the scoped `tools/ci_local.sh` with all 9 battle and bestiary shots gives rc 0. 1169 Godot tests, 0 failed. Coverage: battle 99.94% (1770/1771), progression 96.52%, within baseline. All shots at rmse 0, so none needed re-approval.

## Review log
- 2026-10-24 review-sweep-O (combat): **approve with fixes.** All four criteria hold.
  - **What I read:** `git show --stat` of 0bd8d07, b2dbe53 and 1fb9241, plus enemy_page.gd, enemy_page_view.gd, read_panel.gd, opening_banner.gd and game/ui/bestiary/.
    - Every size and timing comes from HudLayout data (`HudLayout.num`), so there are no magic numbers in the views.
    - Every string is a loc key, appended in 1fb9241.
    - "First Strike" and "Caught Unaware" are generic. They are not the source game's opening captions, and nothing in banned_terms.txt matches.
  - **Checks:** Godot `--filter=` read_panel 12/0 failed, bestiary 27/0, opening 13/0, ui 87/0, battle 307/0. gdlint and gdformat are clean.
  - **Battle time:** `BattleHud.holds_battle()` holds every wait in `tick()` while the panel is open. The Read pays its rank and nothing else, which matches battle_ctb.md.
  - **Filed as M2-UI-04:** the bestiary menu isn't reachable in play (`BestiaryMenu.open_in` has no caller outside tests and shots). The task's own follow-up, the target panel's `"revealed": false` for a foe already Read (battle_controller.gd:769), had no task either.
