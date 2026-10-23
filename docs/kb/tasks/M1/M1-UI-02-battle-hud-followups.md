---
id: M1-UI-02
title: "Battle HUD follow-ups: swap preview, fail copy, Provoke, auto-turns, status display, fixture captures, accessibility settings"
role: ui
status: review
owner_session: worktree-agent-a442bf3baa0b90315
reviewer: lead
depends_on: [M1-CMB-01, M1-CMB-02]
milestone: M1
request-from: ""
---
## Goal
Close the M1-CMB-01 review follow-ups and the UI-01 lead-review follow-ups on the battle HUD (SPEC §1 pillar 4, §6.1, §6.11, §7.6).

## Acceptance criteria
- [x] Swap-out state previews the timeline with `BattleEngine.preview_swap(out, in)`; chips move while hovering a reserve member
- [x] The help line shows a localized message for every engine failure reason (no raw ids); keys appended to `game/data/loc/strings.csv`
- [x] The target cursor respects Provoke (`forced_target()`), with a clear marker on the provoker
- [x] Berserk and Confuse party turns get their own labels and pacing (auto-run turns, not enemy actions)
- [x] Doom countdown on timeline chips and the party panel; Reflect bounce indicator and float text; Petrify state (stone-tinted greyed portrait, off the timeline); Zombie/Regen inversion feedback; every new status icon is a colorblind-safe vector shape
- [x] Victory/defeat/HUD captures render from deterministic fixture UI state, independent of `enemies.json` tuning; baselines re-approved after visual check; one new statuses shot (Doom, Reflect, Petrify, Provoke)
- [x] Data-driven accessibility settings layer (reduced motion, HUD text scale, colorblind palette) with tests
- [x] A more prominent current-actor marker (UI-01 lead review)

## Notes
How it works: `docs/kb/tech/ui.md` (HUD components, Battle sandbox, § Capture fixtures, § Accessibility).

Delivered:
- **Swap preview:** hovering a reserve member, and each leaver in the swap-out step, shows `preview_swap(out, in)` as a whole new order (`TurnTimeline` `full_preview`). A test checks it against the order after the real swap.
- **Refusals in words:** `BattleMenus.fail_text()` has a `HUD_FAIL_*` line for all nine reasons (`FAIL_REASONS`). A test reads the reasons out of `battle_engine.gd`, so a new engine reason fails the suite until it has a line. The fail text now stays on screen (before, re-opening the menu overwrote it at once).
- **Provoke:** the cursor starts on and is locked to `forced_target()`. A fish-hook glyph hangs over the provoker for the whole turn, the locked chevron gets a bar, and the help line leads with "provoked: must strike {name}".
- **Automatic turns:** Berserk/Confuse turns on either side are announced ("{name} is berserk and fights on their own"), held for `auto_announce_sec` (longer than an enemy's think time), and reported from `auto_reason`. The timeline caption, a hollow ▶ on the party row and a hollow actor marker show the player is not choosing.
- **Statuses:** all 21 statuses have their own vector silhouette, and polarity is coded by the backing shape (disc or diamond) as well as hue. Doom: an hourglass plus its count on the timeline chips and the party row. Reflect: a dashed bounce arc to the real recipient, a timeline mark there, help text, and "Reflected" float text. Petrify: a stone portrait in the party row and a stone stand-in, off the timeline. Zombie: the heal-preview warning, "Heal turns to harm", an inverted Regen glyph, and end-of-turn Regen harm ("Regen turns to harm"). Poison and Regen ticks and Doom running out now show too.
- **Fixture captures:** `BattleFixture` and `game/data/ui/battle_fixtures.json` hold a frozen copy of the sandbox tables plus per-state overrides and opening statuses. `player_preview`, `swap_menu`, `victory`, the new `defeat` and the new `statuses` all start from it. The baselines for `battle_hud_preview`, `battle_swap_menu` and `battle_victory` were re-approved after I looked at them (victory is unchanged at RMSE 0.00003). New shot: `battle_statuses`.
- **Accessibility:** `UiSettings` (`game/ui/settings/ui_settings.gd`, data in `game/data/ui/accessibility.json`) offers reduced motion, text scale 100/115/130% and a colorblind palette. It persists to `user://settings.cfg [accessibility]` and is followed live by `BattleHud.apply_settings()`. A critical hit now shakes the camera, except under reduced motion.
- **Current actor:** a 34 px diamond on a stem with the glow behind it (it was 18 px, under the glow). Slot 0 gets a 3 px frame, an outer glow and an "Acting now" caption. The party row gets a 4 px bar, a ▶ mark and a portrait.
- Tests: `tests/unit/test_ui_settings.gd` (new, 11 tests), plus additions to `test_battle_controller.gd` (15 tests), `test_ui_hud.gd` (5) and `test_ui_timeline.gd` (2). `tools/ci_local.sh` passes.
- Engine changes: none. Engine requests: see the session report (optional; nothing blocks).

## Review log
