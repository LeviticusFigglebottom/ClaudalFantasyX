---
id: M3-RBL-201
title: "Reefball engine: what the HUD cannot show yet (contesters, refusal reasons, fetches, stakes)"
role: combat
status: review
owner_session: "claude/ui (ui-menus; combat's UI-adjacent work, Lead 2026-10-27)"
reviewer: lead
depends_on: [M3-RBL-01]
milestone: M3
request-from: ui
---
## Goal
The Reefball HUD (M3-UI-01) shows only what `ReefballMatch` tells it, so it holds no rules. Four things
pillar 4 wants on screen are not in the engine's API yet. Each is a small, previewable field.

## Acceptance criteria
- [x] **Who presses an option.** `preview()` adds `against: Array[StringName]`: the opponents counted in its
      odds (a rise's contesters in the carrier's band and the band above, a pass's markers in the receiver's
      band, a loft's wardens and pressers). The opponent read marks them, beside `fail_to`.
- [x] **Why an action is not on the menu.** A way to list the actions that are not legal now with a reason
      key (rise into the ring with an unfetched float, loft unfetched or from below `loft.max_depth`, a pass
      to a diver at the ring, a dive at the weep), for example `refused_actions() -> [{action, target,
      reason_key}]`. The HUD would show them disabled with the reason. Today it shows the legal ones only,
      and its fetch line explains the commonest refusal.
- [x] **`fetches: bool`** on `preview()`: a success takes an unfetched float to `fetch_depth` or deeper.
- [x] **`stakes_key`** on `matches.json` rows (validated like `name_key`). The HUD prefers it over its own
      `game/data/ui/reefball_hud.json` `stakes` fallback, which can then go (UI deletes it).
- [x] Decide whether `strokes_left` may end below 0 (a 2-stroke rise with 1 stroke left). The HUD shows
      "0 strokes left" either way; document it in `docs/kb/design/reefball.md`.

## Notes
- The HUD reads `preview()` word for word (`tests/unit/test_reefball_hud.gd`
  `test_each_option_shows_the_engines_preview_before_it_is_chosen` compares them), so new fields are additive.
- Docs: `docs/kb/tech/ui.md` "Reefball HUD".

## Implementation notes (ui-menus, 2026-10-27)
- **Engine** (`game/minigames/reefball/reefball_match.gd`, headless and deterministic, no new rolls): `preview()` adds `against` (ids of the opponents counted in the odds) and `fetches`; `refused_actions()` lists the illegal actions with a `reason_key` (`REFUSE_KEYS`); `preview()` and `refused_actions()` share one rule source (`_refusal()`).
- **Data:** `matches.json` `tidecup_opening` has `stakes_key`; `tools/validate_data.py` checks a present `stakes_key` is a non-empty loc key (collected for the loc check), with `tools/tests/test_reefball_validate.py` `test_stakes_key`. The HUD's `stakes` fallback in `reefball_hud.json` is deleted.
- **Clock ruling:** the last action always completes and `strokes_left` may end below 0; the HUD shows 0 (`reefball.md` § Clock).
- **HUD:** the read tags `against` opponents "Contests" (beside "On a miss" for the taker); refused actions are listed greyed after the options with a short reason (`reefball_hud.json` `refused_short`); a fetching option's preview says "...; fetches the float".
- Tests: `test_reefball_match.gd` (`test_refused_actions_say_why`, `test_preview_names_who_presses_and_whether_it_fetches`), `test_reefball_hud.gd` (`test_refused_actions_are_listed_greyed_and_a_fetch_is_named`, the against tags); reefball 70/0.

## Review log
