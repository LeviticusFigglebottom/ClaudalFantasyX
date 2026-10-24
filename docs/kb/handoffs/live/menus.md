# Live log: menus environment

**Session:** `session_01Q26A4D653s52czT76QPURY` (cloud) · **Branch:** `claude/menus` (from `claude/undertow-lead-handoff-423ixt` e9938ed, merged with `claude/ui`) · **Role:** ui (with combat for progression logic) · **Lead:** `session_019iimsngAgPLEram1wcbLpE`

Why this track exists: the progression and equipment systems (Lattice, equipment, ability slots, Customize, items, wallet) had no player-facing menus. The field menu offered only Bestiary, Swell, Settings and Close. These are M2 review blockers (SPEC §10.2 "a first Lattice section, equipment"; pillar 5).

## Queue (tasks M2-MNU-01..05, claimed on this branch, role ui)
| Task | State |
|---|---|
| Foundation (no task of its own) | **pushed**: field menu root grows to 9 rows (Items, Equip, Lattice, Status, Swell, Bestiary, Settings, Quit to Title, Close) through FieldMenuModel; `FieldSubmenu` page base and `PartySheet` (a hero built exactly like a live battle builds them) in `game/ui/menus/`; loc files `menus*.csv`. |
| M2-MNU-01 Lattice board page | **merged on the branch, review** (3f2446c): original lozenge/rigging look, cheapest-path walking with cost shown first, wake and gate confirms; shots lattice_menu, lattice_menu_activate viewed and approved |
| M2-MNU-02 Equip + Customize, gear applied in live battles | **merged on the branch, review** (f25f4d6): stat-delta preview, ability slots, Customize with shortfalls; BattleVitals.setup now applies worn gear and Full Net's lume multiplier in live battles (fixtures unchanged); shots equip_menu, equip_customize viewed and approved |
| M2-MNU-03 Items + Status pages | **merged on the branch, review** (bcf4780): field use through ItemBattleAction.resolve_on, sort by kind/name/count, status split base + Lattice + gear; shots items_menu, items_menu_use, status_menu viewed and approved |
| M2-MNU-04 Quit to Title + battle pause | **done on the branch** (cdbb916): Quit behind a Stay-first confirm; battle pause on P / Pause / pad Start; shot `battle_pause` |
| M2-MNU-05 screenshots, navigation, accessibility sweep | **review**: every new screen viewed at 130% text and in the colorblind palette; the Lattice side panel and the Equip table now flow at any text size (tests at 1.0/1.15/1.3) |

## For other tracks
- **ui (claude/ui):** I changed your field-menu shell, minimally: `FieldMenuModel` gained the rows (ROOT_IDS, PARTY_ROWS, root_enabled, quit_rows, `field_heroes()` extracted from from_game), `FieldMenu` gained `Level.QUIT`, `child` (a FieldSubmenu opened from `CHILD_PAGES`) and `quit_to_title()`; `field_menu.json` panel and root rects grew for nine rows; `FieldMenuShot` now walks down to Swell by id. Baselines `field_menu` and `field_menu_swell_modes` re-approved after viewing. Please merge `claude/menus` before your next field-menu change.
- **battle-presentation (claude/battle-presentation):** `battle_sandbox.tscn` has a new last child `BattlePause` (a plain Node; script `game/ui/menus/battle_pause/battle_pause.gd`). The pause is a tree pause, so anything that must hold still has to run in the default process mode: no `PROCESS_MODE_ALWAYS`, no `get_tree().create_timer(..., true)` (SceneTreeTimers ignore pause by default; pass `process_always = false`), tweens bound to nodes. Today nothing in game/battle or game/ui/battle breaks that rule. Pause is refused in the states listed in `game/data/ui/battle_pause.json` `blocked_states` (idle, result); if BattleChoreo's intro or outro should not be pausable, tell me and I'll add a hook rather than a state.
- **Lead / combat agent (live payouts):** M2-MNU-02 edits `BattleVitals.setup` (game/battle/scene/battle_vitals.gd): worn gear (EquipmentEffects.modifier between the Lattice and the vitals) and `engine.currency_multiplier` (Full Net) in live battles. If your live-payout change touches the same function, keep both.
- **Controls:** `battle_pause` is added to the InputMap at runtime (FieldInput.add_actions), not yet in `controls.json`, so it can't be remapped yet. Follow-up for the UI track's Controls page (a `battle` context).

## Exact next step

**MERGE-READY @ bfd4436a** (claude/menus == claude/ui @ bfd4436a; contains the integration branch @ 2f57655): items M2-MNU-01 Lattice page, M2-MNU-02 Equip + Customize (+ live battles wear gear and pay Full Net's lume multiplier, BattleVitals.setup), M2-MNU-03 Items + Status pages, M2-MNU-04 Quit to Title + battle pause, M2-MNU-05 screenshot/navigation/accessibility sweep; all five in review. Checks run on bfd4436a: gdlint + gdformat (458 files clean), validate_data 0/0, taskboard --check OK, tools test_release_excludes_tests OK, full Godot suite 1700 run / 1 failed (background). The one failure is claude/ui's, not this track's: test_town_services::test_a_shop_payload_opens_that_shop_over_the_live_save fails only after test_interact_prompt.gd (M2-UI-20) runs (bisected; passes alone); reported to the UI track. Earlier on this branch: full tool unit tests 541 (1 failure, the objective_shot.gd release check, fixed by claude/ui dce9ab43), audio synth OK, Blender step (no Blender source touched), coverage OK within baseline (game/battle 99.95%, game/progression 96.69%, M2-MNU-02's run). New shots captured, viewed and compared at rmse 0: battle_pause, items_menu, items_menu_use, status_menu, lattice_menu, lattice_menu_activate, equip_menu, equip_customize, field_menu, field_menu_swell_modes. Skipped: the full screenshot manifest (Lead runs it at merge; the 2026-10-24 gate rule) and a fresh coverage run on the merged head (no game/progression change since).

The queue is empty. Next: answer reviews of M2-MNU-01..05, and re-merge claude/ui when it fixes the interact-prompt test leak. Follow-ups below.

Merge the three worktree agents' branches as they report (Lattice, Equip, Items/Status), view every new shot, then M2-MNU-05; then merge the integration branch and `claude/ui`, run the FULL `tools/ci_local.sh`, and write MERGE-READY here.

## Log
- 2026-10-24: branch created from the integration branch, merged `claude/ui`, pushed. Tasks M2-MNU-01..05 claimed. Foundation pushed (456c9a4, 42124b4, fa109a4). Battle pause and Quit to Title pushed (cdbb916): tests 6 + 4 new, field_menu 19/19, battle 418/418.
- 2026-10-24: M2-MNU-03 merged (Items 11/11, Status 5/5, field_menu 19/19, battle_pause 6/6). Field menu root widened for 130% text (ce979d0). Two worktree agents still running (Lattice, Equip).
- 2026-10-24: M2-MNU-01 merged (lattice 49/49, field_menu 19/19). Equip agent still running.
- 2026-10-24: M2-MNU-02 merged (equip 61/61, battle_vitals 14/14, menu 185/185). claude/ui merged (fd8f484). M2-MNU-05 sweep started: 130% and colorblind renders of all 7 new shots viewed; two layout bugs sent back.
- 2026-10-24: Lattice and Equip 130% fixes merged and viewed; M2-MNU-05 to review. Merged the integration branch and claude/ui (M2-UI-17/18: objective line and a Map row, ten root rows; field_menu shots still rmse 0). Full ci_local started.

## Follow-ups (not in this queue)
- ~~`battle_pause` into controls.json~~ done by claude/ui (dce9ab43).
- Light Step (`encounter_rate_pct`) is not read by the field encounter meter yet.
- Lattice page: no overview zoom or drag-pan; a sealed gate not next to the hero doesn't offer to walk there.
- Customize works only on worn pieces (equip a spare first).
- 2026-10-24: full ci_local on 8c2b427 stopped at the tool unit tests: 541 run, 1 failed, `test_release_excludes_tests::test_no_shipped_file_names_a_tests_path` -> `game/ui/objectives/objective_shot.gd` (claude/ui M2-UI-17's capture driver loads `res://game/levels/_tests/haluna_mood/haluna_mood.tscn`, which release presets exclude). Not this track's code; reported to the UI track with a proposed fix (move the driver under game/levels/_tests/). Re-running every other step with that one test recorded instead of fatal.
- 2026-10-24: merged claude/ui (fast-forward to bfd4436a; includes the sandbox_reef foe-order fix 667c4d56 that had made test_battle_vowbound loop forever on this branch, and the objective_shot move). Full Godot suite 1700/1 (claude/ui's interact-prompt leak, bisected and reported). MERGE-READY written.
