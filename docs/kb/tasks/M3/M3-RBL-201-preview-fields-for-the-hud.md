---
id: M3-RBL-201
title: "Reefball engine: what the HUD cannot show yet (contesters, refusal reasons, fetches, stakes)"
role: combat
status: todo
owner_session: ""
depends_on: [M3-RBL-01]
milestone: M3
request-from: ui
---
## Goal
The Reefball HUD (M3-UI-01) shows only what `ReefballMatch` tells it, so it holds no rules. Four things
pillar 4 wants on screen are not in the engine's API yet. Each is a small, previewable field.

## Acceptance criteria
- [ ] **Who presses an option.** `preview()` adds `against: Array[StringName]`: the opponents counted in its
      odds (a rise's contesters in the carrier's band and the band above, a pass's markers in the receiver's
      band, a loft's wardens and pressers). The opponent read marks them, beside `fail_to`.
- [ ] **Why an action is not on the menu.** A way to list the actions that are not legal now with a reason
      key (rise into the ring with an unfetched float, loft unfetched or from below `loft.max_depth`, a pass
      to a diver at the ring, a dive at the weep), for example `refused_actions() -> [{action, target,
      reason_key}]`. The HUD would show them disabled with the reason. Today it shows the legal ones only,
      and its fetch line explains the commonest refusal.
- [ ] **`fetches: bool`** on `preview()`: a success takes an unfetched float to `fetch_depth` or deeper.
- [ ] **`stakes_key`** on `matches.json` rows (validated like `name_key`). The HUD prefers it over its own
      `game/data/ui/reefball_hud.json` `stakes` fallback, which can then go (UI deletes it).
- [ ] Decide whether `strokes_left` may end below 0 (a 2-stroke rise with 1 stroke left). The HUD shows
      "0 strokes left" either way; document it in `docs/kb/design/reefball.md`.

## Notes
- The HUD reads `preview()` word for word (`tests/unit/test_reefball_hud.gd`
  `test_each_option_shows_the_engines_preview_before_it_is_chosen` compares them), so new fields are additive.
- Docs: `docs/kb/tech/ui.md` "Reefball HUD".

## Review log
