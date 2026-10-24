---
id: M2-UI-05
title: Vowbound commands and HUD (call, the Vowbound's menu, Dismiss, the call preview)
role: ui
status: review
owner_session: "agent-a9031fbbea441e647"
reviewer: lead
depends_on: [M2-CMB-04]
milestone: M2
request-from: combat
---
## Goal
M2-CMB-04 added the Vowbound engine rules (battle_ctb.md § Vowbound, ADR 0027): `engine.summon(id)`, `engine.dismiss()`, `engine.vowbound.unleash(engine, targets)`, `callable_ids`, the refusal reasons, and the `called` and `departed` signals. Nothing draws them yet, so Ilun cannot be called in play.

## Acceptance criteria
- [x] The controller builds `engine.vowbound` from the story flags before `begin()` (`ch03_ilun_bound` → `ilun`; the engine never reads `Game`)
- [x] The caller's root menu gets a call row: greyed with its reason (loc keys for `not_bound`, `silenced`, `vowbound_fallen`)
- [x] The Vowbound's own menu: its skills, its finisher when the gauge is full, and Dismiss. Swap, items and escape are hidden or greyed while it is out
- [x] Pillar 4: the timeline previews the call (the caller's `call_rank` delay once the party returns) and the dismissal
- [x] The stage: the stood-down party steps off the field, and the Vowbound stands in (placeholder, as the Drownbell's stand-ins do)
- [x] Tests and the affected screenshots

## Notes
- Keep the controller edit small (it is near the lint cap). A `BattleVowboundHud` view built like `BattleBossHud` (claude/first-playable) is the clean shape.
- The summon cinematic (SPEC §6.3) is a cinematics task, not this one.

## Implementation notes (agent-a9031fbbea441e647, 2026-10-24)
- **Glue:** `BattleVowboundHud` (`game/battle/scene/battle_vowbound_hud.gd`), built like `BattleBossHud`. The controller gained 8 lines (995/1000): the attach, `vow.perform` in `act()`, `vow.highlight` in the highlight guard, `vow.choose` as the root `match`'s default, `vow.show_note`, the finisher in `_highlight_root`, and `_after_action` → public `after_action`.
- **Binding (ADR 0030, proposed):** each vowbound.json row has a `bound_flag` (Ilun: `ch03_ilun_bound`), read with `Game.get_flag` in a live battle; `validate_data.py` checks it is declared. Fixtures bind through a `vowbound` list over a frozen `tables.vowbound`. Other battles load the rows with nothing bound.
- **Menus:**
  - The caller's "Call Ilun" row comes after Skills, with `R3`. Greyed, it names the reason: "Silenced", "Fallen", or a nameless "Call · None bound".
  - Ilun's page: Attack, Floodnet (greyed until full, showing how full), Skills, Dismiss, then Escape and Swap greyed. Items is hidden.
  - Six new `HUD_FAIL_*` lines.
- **Pillar 4:** `BattleVowbound.preview_call` and `preview_dismiss` are read-only engine previews, like `preview_swap`, each tested against the engine's real order after the action. The call's help states the caller's rank delay; the Dismiss preview shows the real return.
- **Stage and panel:**
  - `BattleStage.sync_party` takes off any party stand-in no longer on the field, and seats a Vowbound on `vowbound_slot`.
  - The panel shows the Vowbound alone, with a Swell gauge and a "Standing down: …" note. A departure leads the next menu's help line.
- **Also fixed:** a six-row root (live Rhen with a bag already had one) spilled below the command panel. The root now grows upward from the same foot; five-row pages are unchanged.
- **Shots:** new `battle_vowbound_call` and `battle_vowbound_out`. The other eight battle shots pass.

## Review log

## Lead decision (2026-10-24)
- **The Call row is hidden until a Vowbound is bound.** It should not appear greyed as "Call · None bound". Before Chapter 3 it would be a dead row that hints at a beat to come. "Silenced" and "Fallen" stay as greyed reasons, because they're tactical information. This is a one-line change in `BattleMenus.call_rows`; the next UI touch on the battle menu makes it, with a test.
