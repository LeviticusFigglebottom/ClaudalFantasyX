---
id: M1-UI-04
title: economy.md refresh and self-revive warning
role: ui
status: done
reviewer: combat
owner_session: "worktree-agent-aa5733be52ed5e16a"
depends_on: [M1-CMB-06]
milestone: M1
request-from: "progression"
---
## Goal
Review-sweep-C follow-ups on CMB-06.

## Acceptance criteria
- [x] economy.md revive/petrify targeting rules updated to the merged behaviour
- [x] Item menu warns when a Zombie targets itself with a revive while it is the last one standing

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

- 2026-10-23 ui (worktree-agent-aa5733be52ed5e16a): economy.md has a new § Targeting in battle, read from `battle_engine.gd` and `item_battle_action.gd`. The battle UI had no item menu, so this adds the **Items** command (item list, then target, then `use_item`) with the `preview_item` preview. `BattleEngine.item_defeats_party()` and `item_fells()` are Node-free, and `_resolve_item_on` now uses `item_fells`. When `item_defeats_party` is true, the help line is `HUD_HELP_ITEM_DEFEAT_FMT` alone, in the danger role, on hover and on the target. It warns and does not block. To stay under gdlint's 1000-line cap, the controller was split with no behaviour change (`BattleCaptureScript`, `BattleMenus` targeting rules, `BattleStage.lattice_for`). Tests: `tests/unit/test_battle_item_menu.gd`. Follow-up for Combat: a heal item that KOs a Zombie on itself while it is the last one standing is flagged as harm, but the KO is not predicted. See handoff 2026-10-23-ui-1.
- 2026-10-23 combat (worktree-agent-a6210d9196b16c99a): sweep-E fixes on branch `combat/M1-CMB-07-item-preview-followups`, back to review (reviewer combat).
  - economy.md: the petrify-cure rejoin is `action_delay(agi, DEFAULT_RANK, speed)` (`_rejoin_time`; speed read after every effect). formulas.md got the same fix in both petrify lines, plus a preview/defeat paragraph. Also "the last *living* active member", the heal-KO now predicted, and the group-revive case.
  - Latent bug fixed: `item_defeats_party` counts allies the same group revive brings back (tests in tests/unit/test_battle_item_outcomes.gd).
  - Stale comments fixed: battle_engine.gd `item_can_target`, and item_battle_action.gd:8 (comment only, Progression's file).

## Review log
- 2026-10-23 combat (review-sweep-E): **approve-with-fixes.** I read the 0f67d5b and b820fc5 diffs, plus battle_engine.gd `use_item`, `_valid_item_targets` (:323), `_resolve_item_on` (:347), `preview_item`, `_rejoin_time` (:390), `_end_turn` and `_check_outcome`. I also read `ItemBattleAction.can_target` and combatant.gd `is_alive`/`fall`. Godot runs (own `XDG_DATA_HOME`): `--filter=item` gave 47 run, 0 failed, and `--filter=battle` gave 201 run, 0 failed. gdlint and gdformat are clean. battle_controller.gd is 994 lines, and the split moves code without changing logic.
  - **economy.md § Targeting in battle, checked bullet by bullet against the engine:**
    - **Side:** matches (`_valid_item_targets`: `self` takes only the actor, ally items take `party_active` only, foe items take `enemies`).
    - **Life state:** matches (item_battle_action.gd:76-81, combatant.gd:87-88: stone is not alive).
    - **Revive on the fallen:** matches. They rejoin at `_rejoin_time` (with `speed_mult`), and a KO clears every status (combatant.gd:178-181).
    - **Revive on a living Zombie:** matches. It fells the Zombie, reports `zombie_felled`, and `amount` is the HP lost. It may be aimed at yourself.
    - **Revive never reaches stone:** matches.
    - **Items ignore Silence, Reflect and Provoke:** matches (`use_item` has no checks; `item_candidates` ignores `forced_target`).
    - **Defeat on a self-fell:** matches. It's legal, and `_check_outcome` counts only `party_active`.
  - **Should-fix (doc mismatch):** economy.md:68 says a petrify-cured unit rejoins `action_delay(agi, DEFAULT_RANK)`. The engine uses `_rejoin_time`, which applies `speed_mult` (battle_engine.gd:390-391), as the revive bullet (:65) already says. Add the speed term.
  - **Should-fix (latent false warning):** `item_defeats_party` (battle_engine.gd:264-277) says "defeat" whenever every living active ally is hit and felled. It ignores fallen allies that the same group revive brings back. An `all_allies` revive on [the last-standing Zombie, a fallen ally] fells one and revives the other, so the battle goes on, but the menu warns of defeat. No such item ships yet. Fix it here, or add it to M1-CMB-07 with a test.
  - **Nit:** stale comments. battle_engine.gd:245-247 says a petrified ally is reached by "no item", which contradicts the petrify-cure rule. item_battle_action.gd:8 says revives target "KO'd allies ONLY", but the engine adds living Zombies.
  - **Nit:** economy.md:66 says "If the user is the last active member standing". Make it "the last *living* active member": a reserve member who is still alive doesn't count.
  - **Noted:** the heal item that KOs a Zombie on itself is flagged as harm but not predicted as a defeat. That's documented (economy.md:69) and filed as M1-CMB-07 AC1.
- 2026-10-23 combat (review-sweep-F, fresh reviewer): **approve.** I read 247304b and 64a618a, economy.md § Targeting in battle (:58-70), formulas.md :58, :122, :141-147, and item_battle_action.gd:1-15. Checks: validate_data 0/0; `unittest discover -s tools/tests` 300 OK; taskboard --check rc 0; `dlgc --check` 0/0; gdlint and gdformat clean. Godot: `--filter=item` 60 run, 0 failed.
  - **All sweep-E findings are fixed:**
    - The petrify-cure rejoin now has the speed term in economy.md:68 and in both formulas.md Petrify lines (:122, :146). This matches `_rejoin_time` (battle_engine.gd:416-417).
    - "The last *living* active member" (:66).
    - The group-revive false warning is fixed in the engine (`item_defeats_party` counts allies the item brings back) and documented.
    - The stale comments are fixed: battle_engine.gd `item_can_target`, and item_battle_action.gd:8 (comment only).
    - The heal-KO is now predicted, and :69 says so.
  - I re-checked every § Targeting bullet against `_valid_item_targets`, `item_can_target`, `_resolve_item_on` and combatant.gd, and they still match.
  - Nit: economy.md:72's "**For Combat:** formulas.md lists 'item formulas (Progression)' as unspecified … Please fold them into formulas.md" is stale. formulas.md now has them (§ Items, with `Formulas.revive_hp`/`item_damage` mirrored and tested), so replace it with a pointer.
  - Nit (also in M1-PRG-03 sweep F): economy.md:139 still prices Ember Pot at 80–110, but it is 220 (items.json:15).
- 2026-10-23 lead: closing on review-sweep-F approve; the Ember Pot price and the stale paragraph are in M1-CMB-08.
