---
id: M3-C08-100
title: "Ch8 combat follow-ups: the sailmaker's needle, the set piece's battle barks"
role: combat
status: review
owner_session: "ui-menus (claude/ui, session_01KGBUwbYgXe9JS6D8jXw6ZG)"
depends_on: [M3-C08-02, M3-CMB-01]
milestone: M3
request-from: cinematics
---
## Goal
Two things the Ch8 flow (M3-C08-02) sets up but the battle data doesn't have yet (act1_ch08.md B05, §5).

## Acceptance criteria
- [ ] **The sailmaker's needle**, an accessory (the sheet suggests an Ember Guard or a small fire ward). Coilspire's tier-2 niche sets `ch08_found_sail_needle` but gives no item today. Add the item and give it from the niche:
  - `Ch08CoilspireZone._on_niche` can call `give({"<item id>": 1})` (Ch01Zone);
  - or ask cinematics to add the item to `ch08_field.json` `trial`.
  Ch20's Virel release reads whether Liss carries it.
- [x] **Battle barks** (≤ 40 words; built by battle-presentation 2026-10-27: BattleBarks, choreo.json `barks`, keys BARK_CH08_*): Asha's call is one word, Virel's name. Toma says "Hold." on Hold the Stair and Liss says "Pull!" on Haul. Nobody speaks on Flare Line, and Virel has no line. There's no battle-bark system yet; today Toma's "Hold." is said once, in the Reach's intro scene (`ch08_the_reach`).

## Notes
- The headland's and the spire's fights (`ch08_headland_gulls`, `ch08_headland_crabs`, `ch08_flue_moths`) and their enemies were added by M3-C08-02 with `sim.py` bands; the combat reviewer should look at them:
  - the stormgull fight's `role_answer` is report only, the same logged exception as `ch06_ridge_gulls`;
  - the wallcrab is a high-defence shell (defence 220), so Toma's Shell Breaker is the answer.

- **2026-10-27, ui-menus (owns combat's UI-adjacent work).**
  - **Battle barks: done.** `BattleBarks` (`game/battle/scene/battle_barks.gd`) is a listen-only view that the controller attaches in one line. It floats a speaker's line as the skill resolves, or as a Vowbound is called. Damage numbers being off doesn't hide it, because it is speech.
  - **The data:** skills.json `bark_key` on `hold_the_stair` ("Hold.") and `hoist_haul` ("Pull!"), and vowbound.json `call_bark_key` on Virel ("Virel."). Flare Line and Virel himself stay silent. The loc rows are in battle_set_piece.csv; the validator's loc check covers the keys. Tests: `tests/unit/test_battle_barks.gd`.
  - **The sailmaker's needle: blocked** on the Lead's accessory-slot ruling. There is no accessory slot (see M3-C07-05; the Oruvel Float has the same question). Once it's ruled, add the item, and have `Ch08CoilspireZone._on_niche` give it (cinematics' code).
- **2026-10-27, ui-menus, after ADR 0040 (no accessory slot):** the needle is now `sailmakers_needle`, a Customize material. With two Tide Pearls it crafts **Sea Legs** (new armour ability, a ward against Slow) into an empty armour slot, and the needle is spent. The tests are in test_customize.gd. **Still open, cinematics:** `Ch08CoilspireZone._on_niche` should `give({"sailmakers_needle": 1})` (requested in M3-UI-204). Ch20 can read `ch08_found_sail_needle`, which stays true after the needle is spent.

## Review log
- 2026-10-27 battle-presentation: the barks half is done (the needle half stays open; it's an item, not mine).
  - BattleBarks (game/battle/scene/battle_barks.gd) floats the line over the speaker's head and emits
    `barked(speaker, key)` for audio's voice blips.
  - Data: choreo.json `barks` (`skills` keyed by skill and speaker, `calls` by vowbound).
  - Lines: Toma "Hold." on hold_the_stair, Liss "Pull!" on hoist_haul, Asha "Virel." on calling Virel. Flare Line
    and Virel say nothing.
  - Test: test_battle_set_piece_stage::test_the_stair_has_its_few_barks.
