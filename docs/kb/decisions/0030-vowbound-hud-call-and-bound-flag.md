# 0030 — The Vowbound on the battle HUD: a Call row per caller, bound by a data flag

- **Status:** proposed
- **Date:** 2026-10-24
- **Roles affected:** UI, Combat (vowbound.json, validate_data.py), the m2-slice track (M2-FP-17), Narrative (the flag)
- **Author role:** UI (M2-UI-05)

## Context
ADR 0027 gives the engine its Vowbound rules and says the scene must build `engine.vowbound` from the story flags before `begin()` (the engine never reads `Game`). Pillar 4 asks the HUD to show what the call costs, and the acceptance asks for a greyed Call command that names its reason (`not_bound`, `silenced`, `vowbound_fallen`). Two choices cross roles: where the flag-to-Vowbound map lives, and when the Call row is on the menu at all (it changes the caller's root menu in every battle, and so screenshot baselines).

## Options
1. **Hard-code the map in the scene** (`ch03_ilun_bound` → `ilun`). This is one line, but it puts a story id in code, and a second Vowbound needs a code change.
2. **A `bound_flag` field on each vowbound.json row**, read with `Game.get_flag` in the scene glue and checked by `validate_data.py` (the flag must be declared).
3. **Show the Call row only once something is bound.** No baseline moves, but the `not_bound` reason is never seen, and the command appears out of nowhere at the Shell Shrine.

## Decision
Option 2, and the Call row is shown for every fighter who is the `caller` of a vowbound.json row:
- **Bound** (`bound_flag` set in a live battle, or a fixture's `vowbound` list): one "Call {name}" row per bound Vowbound, after Skills, with the call's rank on the right. Greyed when refused, with the reason in place of the rank ("Silenced", "Fallen").
- **None bound yet:** one greyed "Call" row, "None bound", without the Vowbound's name (no spoiler).
- **Capture fixtures** get rows only when they name `vowbound`, so every existing baseline keeps its root menu. Tests and previews that are neither live nor a fixture load the rows with nothing bound.
- **While a Vowbound is out**, its own root page is Attack, its finisher (greyed until full, showing how full), Skills, Dismiss, then Items, Escape and Swap greyed.
- **Previews** are engine-side and read-only, like `preview_swap`: `BattleVowbound.preview_call` and `preview_dismiss`, each tested against the order the engine really has after the action.

## Consequences
- **M2-FP-17 should not wire the flag again.** The scene already binds Ilun from `ch03_ilun_bound` (`BattleVowboundHud.live_bound`). FP-17 removes `call_ilun` and re-bands the Drownbell.
- A future Vowbound needs only its row and its flag.
- Asha now shows a greyed "Call · None bound" row in live battles before Chapter 3. Narrative may prefer the row hidden until the Shell Shrine. If so, it is one condition in `BattleMenus.call_rows`, and the `not_bound` reason then stays for tests only.
- The return of the party cannot be shown before the call, because it depends on when the Vowbound leaves. The call preview shows the order with the Vowbound in it, and its help line states the caller's delay. The Dismiss preview shows the real return, with the caller after that delay.
