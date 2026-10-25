---
id: M3-UI-01
title: The Reefball match HUD (Ch7 story match)
role: ui
status: review
owner_session: "claude/ui"
reviewer: lead
depends_on: [M3-RBL-01]
milestone: M3
request-from: lead
---
> **Branch note:** this work sits on a merge of the Lead's big8 gate (`origin/lead/gate-big8`, which carries
> the Reefball engine, M3-RBL-01) into claude/ui, kept as its own merge commit. Merge claude/ui only after
> big8 has landed on the integration branch.

## Goal
SPEC §6.10: the HUD for the Reefball minigame. It needs the score and clock, the ball carrier and the passing and shooting choices (in the battle UI's style), each player's stamina, the opponent read, and the story-match framing. Keyboard, mouse and pad parity are required (M2-UI-26).

## Blocked on
- ~~**M3-RBL-01,** the Reefball engine.~~ Merged in with the big8 gate (see the branch note).

## Acceptance criteria
- [x] Layout data in `game/data/ui/reefball_hud.json`; views over the engine's state only.
- [x] Parity tests with all three devices; shots of a pass choice and a scored goal.

## Implementation notes (claude/ui, 2026-10-24; reviewer: lead)
- **Code:** `game/ui/reefball/`: `ReefballHud` (the HUD), `ReefballSidePanel` (a side's diver rows; also the
  opponent read), `ReefballDropView` (the depth bands with a dot per diver), `ReefballHudController` (wires a
  match to the HUD), `ReefballHudShot` (capture driver). Layout `game/data/ui/reefball_hud.json` (HudLayout
  pins), strings `game/data/loc/reefball_hud.csv` (new per-domain file, registered in `project.godot`).
  Docs: `docs/kb/tech/ui.md` "Reefball HUD".
- **What the engine owns** (every rule, number and roll): the legal actions and their order; each option's
  odds, stroke and breath cost, end band, whether it scores, and who takes the float on a miss (`preview()`);
  the result of a choice (`perform()` / `play_ai_contact()`); the clock, overtime, fetched state, breath,
  resting, positions and the kickoff (`snapshot()` and the divers); whose contact it is
  (`is_player_contact()`); the opponent's decisions (`ReefballAI`); winded (`ReefballFormulas.winded`).
- **What is a view** (no rules): the words and colours for all of the above; which option the cursor is on
  and its preview (the option's own preview dict, shown word for word: a test compares every option to
  `preview()` and checks that looking draws no roll and changes no state); the marks for the cursor's option
  (the pass receiver, the miss-taker) in the drop and the panels; the banner for a goal and the end; the
  opponent read line chosen by the match's AI profile id (`reads`); the stakes line. The clock shows
  `max(0, strokes_left)`: the engine lets the last action overspend the clock.
- **The controller** opens the choices on the player's contact and performs the one chosen; on the other
  side's contact it waits `pacing.ai_think_sec` and calls `play_ai_contact()`; after a goal the banner holds
  `pacing.goal_hold_sec`; at the end it shows the final banner and emits `match_over(outcome, score)` (the
  reward hand-off is M3-C07-03's). `player_ai` plays the player's side for captures; `manual` keeps waits
  out of `_process`.
- **Stakes:** `matches.json` has no stakes field, so the framing reads a match row's `stakes_key` if present,
  else `reefball_hud.json` `stakes` by match id (`RBL_HUD_STAKES_TIDECUP_OPENING`, from act1_ch07.md §5.4:
  played for the dead, the Oruvel Float on a win, Oruvel goes home either way). Requested in M3-RBL-201.
- **Names** are the engine's provisional loc rows (`RBL_SIDE_PEMAKAR`, `RBL_DIVER_*`); M3-C07-03 renames
  them, and the HUD follows with no change.
- **Not shown yet, because the engine does not say** (M3-RBL-201): which opponents contest or mark an
  option, why an illegal action is not on the menu (the fetch line explains the commonest refusal), whether
  a success fetches the float.
- **Input parity:** ui_up / ui_down (keys and pad), hover and the wheel move the cursor; ui_accept or a click
  chooses. `tests/unit/test_input_parity_reefball.gd` walks each `InputDriver` kind (move, the preview
  follows, choose, the engine performs exactly the option shown at the odds shown), the wheel, and no
  input acts on the other side's contact.
- **Layout audits:** `test_aspect_layouts.gd` `test_reefball_hud` (both capture states, 16:9 / 16:10 / 21:9 /
  43:18, 100% and 130%: nothing off screen, no text out of its panel, every piece keeps its pin's margins);
  `test_pseudo_loc_screens.gd` `test_reefball_hud_fits` (both states, every option of the choice, the
  final banner; trims are warnings, no failures).
- **Tests:** `tests/unit/test_reefball_hud.gd` (data, kickoff state, every option's preview vs the engine,
  a choice performed and its result line, the AI's think then play, the goal banner and score, a whole
  match to the final banner, overtime, the fetch line, both capture drivers).
- **Shots** (viewed, approved; two captures each `cmp`-identical): `reefball_hud_choice` (seed 7: the
  player's first contact, Noa holding in mid water, the cursor on "Pass to Tavi Orse", 63%, a miss to the
  Pemakar lifter) and `reefball_hud_goal` (the AI on both sides; Old Ama brings the first float up at 48%,
  1 to 0, the kickoff positions after it). Over a plain backdrop; `game/levels/_tests/reefball/` is
  rendering's and untouched.
- **Found while merging:** `test_pseudo_loc_screens.gd` `test_party_pages_fit` fails on the Lattice page after
  big8's M3-MNU-04 overview button met M2-UI-28's walk. Not touched here: M3-MNU-201.
  The `battle` filter has 4 failures this diff does not touch (no battle, choreo or asset file changed):
  `test_battle_choreo.gd` (victory pose, creature actor contact frame) and `test_battle_specials_choreo.gd`
  (Written Light, Return Tide). They appear on the big8 merge; the Lead should check them on the gate.

## Review log
