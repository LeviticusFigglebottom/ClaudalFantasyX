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
| M2-MNU-05 screenshots, navigation, accessibility sweep | **doing**: every new screen rendered at 130% text and with the colorblind palette and viewed. Palette OK everywhere; Items, Status, field menu and pause OK at 130%. Lattice side panel and Equip stat table overlap at 130%: sent back to their agents |

## For other tracks
- **ui (claude/ui):** I changed your field-menu shell, minimally: `FieldMenuModel` gained the rows (ROOT_IDS, PARTY_ROWS, root_enabled, quit_rows, `field_heroes()` extracted from from_game), `FieldMenu` gained `Level.QUIT`, `child` (a FieldSubmenu opened from `CHILD_PAGES`) and `quit_to_title()`; `field_menu.json` panel and root rects grew for nine rows; `FieldMenuShot` now walks down to Swell by id. Baselines `field_menu` and `field_menu_swell_modes` re-approved after viewing. Please merge `claude/menus` before your next field-menu change.
- **battle-presentation (claude/battle-presentation):** `battle_sandbox.tscn` has a new last child `BattlePause` (a plain Node; script `game/ui/menus/battle_pause/battle_pause.gd`). The pause is a tree pause, so anything that must hold still has to run in the default process mode: no `PROCESS_MODE_ALWAYS`, no `get_tree().create_timer(..., true)` (SceneTreeTimers ignore pause by default; pass `process_always = false`), tweens bound to nodes. Today nothing in game/battle or game/ui/battle breaks that rule. Pause is refused in the states listed in `game/data/ui/battle_pause.json` `blocked_states` (idle, result); if BattleChoreo's intro or outro should not be pausable, tell me and I'll add a hook rather than a state.
- **Lead / combat agent (live payouts):** M2-MNU-02 edits `BattleVitals.setup` (game/battle/scene/battle_vitals.gd): worn gear (EquipmentEffects.modifier between the Lattice and the vitals) and `engine.currency_multiplier` (Full Net) in live battles. If your live-payout change touches the same function, keep both.
- **Controls:** `battle_pause` is added to the InputMap at runtime (FieldInput.add_actions), not yet in `controls.json`, so it can't be remapped yet. Follow-up for the UI track's Controls page (a `battle` context).

## Exact next step
Merge the three worktree agents' branches as they report (Lattice, Equip, Items/Status), view every new shot, then M2-MNU-05; then merge the integration branch and `claude/ui`, run the FULL `tools/ci_local.sh`, and write MERGE-READY here.

## Log
- 2026-10-24: branch created from the integration branch, merged `claude/ui`, pushed. Tasks M2-MNU-01..05 claimed. Foundation pushed (456c9a4, 42124b4, fa109a4). Battle pause and Quit to Title pushed (cdbb916): tests 6 + 4 new, field_menu 19/19, battle 418/418.
- 2026-10-24: M2-MNU-03 merged (Items 11/11, Status 5/5, field_menu 19/19, battle_pause 6/6). Field menu root widened for 130% text (ce979d0). Two worktree agents still running (Lattice, Equip).
- 2026-10-24: M2-MNU-01 merged (lattice 49/49, field_menu 19/19). Equip agent still running.
- 2026-10-24: M2-MNU-02 merged (equip 61/61, battle_vitals 14/14, menu 185/185). claude/ui merged (fd8f484). M2-MNU-05 sweep started: 130% and colorblind renders of all 7 new shots viewed; two layout bugs sent back.
