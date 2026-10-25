# Live log: ui-menus (branch `claude/ui`)

The old **ui** and **menus** tracks merged into one (Lead, 2026-10-25). `claude/menus` is retired: it is merged into `claude/ui` at 0b5c2bd9 and gets no more commits. The old logs, `ui.md` and `menus.md`, stay as history.

**Owns:** the HUD, objectives and map, prompts, title, tips, the dialogue box, settings, input parity, pseudo-loc, resolutions, and the field menu (Lattice, Equip, Items, Status, Formation, portraits, bestiary, codex, save).
**Id block:** tasks 200–399 (ui 200s, menus 300s), ADRs 0110–0129 (0120 is taken), handoffs `<date>-ui-ui-menus-<n>.md`.
**Integration branch:** `claude/undertow-lead-handoff-ze8rrn`.

## NEW ACCOUNT (from 2026-10-25)

### Standing queue
| # | Item | State |
|---|---|---|
| 1 | Merge `claude/menus` and the integration branch (big8) into claude/ui; re-import; full suite; MERGE-READY | merged (3497bc7d, cba891df); full suite 2431 run / 1 failed (test_battle_ko_once: Wickfry has a model now; battle-presentation's fix 9369e8c0 ported as b0778368; battle filter then 620/0) |
| 2 | M3-UI-01 Reefball HUD: apply `patches/ui-reefball-big8.patch` | applied (00f91c6c..ef5dcd9f; patch 1 by hand: its base blobs were gone); reefball_hud_choice/goal rmse 0, viewed |
| 3 | M2-HER-1103 battle heroes: repoint `battle_sandbox.json` stand_ins at `game/hero_motion/battle/<hero>_battle_actor.tscn` | waits for the Lead to announce big9 merged (FAST-TRACK when it lands) |
| 4 | "Parts look primitive": re-render hero portraits, stronger creature rim (`creature_stage`), M2-MNU-305 screen motion, dialogue box and HUD transitions | M2-MNU-305 done (a8cb5b80; 12 screen shots compared, only merge drifts); M2-UI-202 dialogue box motion done (704746f5; dialogue shots rmse 0); HUD pieces already fade; portraits re-rendering with `rim_scale` 2.2 on the five black creatures |
| 5 | Open items: M2-UI-26 duplicate id; bestiary portrait path (ADR 0120); battle_pause / dialogue_backlog drift; Formation role word | duplicate id fixed (M2-UI-201); portrait path chosen (baked PNGs, ADR 0110, lands with the re-render); drift flagged below; role word requested (M2-MNU-306, progression) |
| 6 | M3 UI from the task board: Act I maps, codex for Act I, Ch9 HoldPrompt and ActCard, Reefball menus (M3-RBL-201 / M3-MNU-201) | all in review already (M3-UI-01..04, M3-C09-05); M3-RBL-201 waits on combat. Adjacent: the dialogue box is this track's now, so M2-ARC-09 (ultrawide width) is done (15c94cf0); M2-ARC-07 is covered by M2-UI-30's DialogueAssist |

### Decisions and notes
- **Bestiary-portrait task id:** big8 renamed it M2-UI-28, which collides with pseudo-loc's M2-UI-28. It is now **M2-UI-201** (`docs/kb/tasks/M2/M2-UI-201-bestiary-creature-portrait.md`), from this track's block, so it cannot collide again. The M2-UI-26 and M2-UI-28 portrait copies are gone.
- **Bestiary portrait path (ADR 0120):** the bestiary will switch from the live `CreaturePortrait` SubViewport to the baked PNGs (`CreaturePortraits`), keeping the silhouette for unread foes. A live viewport costs load and render time on every page step on a weak machine, and ADR 0120 already chose baked portraits for every menu. It lands after the portraits are re-rendered with the stronger creature rim (queue item 4).
- **For the Lead, to view (not self-approved):** `battle_pause` (rmse ≈ 0.0054) and `dialogue_backlog` (≈ 0.0006) pass under the limit but drift in the 3D scene behind the menu, not in the menu. Refresh their baselines on the PC gate after viewing.
- **Merge notes (cba891df):** the four conflicting PNG baselines (battle_arena_causeway, battle_arena_tideline, drownbell_flood, field_tip_card) take the integration copy, which the Lead approved after viewing the PC gate. field_tip_card was then recaptured and re-approved after viewing: the same frame with M2-UI-29's pinned tip card 3 px left (0b0969e1). The debug overlay lists both F8 (chapter select) and F10 (pseudo-loc). `balance_report.md` keeps both sides' sections.

### Log
- 2026-10-25: session start. Read TRACK-RULES, CONSOLIDATED, and both HANDOVER sections. Merged claude/menus and the integration branch, applied the Reefball patch, re-imported (clean), gdlint and gdformat clean (692 files), validate_data 0/0, taskboard OK. Full Godot suite started in the background. M2-MNU-305 written in a worktree (`ui/mnu-305`); its scoped tests are green (bestiary 37, codex 14, map 22, settings 48, save 194, title 33, controls 12, graphics 54, accessibility 9, audio_menu 4, screen_motion 7).
- 2026-10-25: M2-MNU-305 merged (screen motion; tests 7/7 new, parity helper finishes a closing screen's fade). Re-approved after viewing: save_shrine_field and settings_accessibility (merge drifts from claude/ui's M2-UI-28/29, identical with and without MNU-305). M2-UI-202 (dialogue box motion) and M2-ARC-09 (box width capped at 1600 px, centred) merged (6b06217d): dialogue 76/0, cutscene 37/0, aspect 13/0. Battle shots recapturing; portraits re-rendering in the worktree.
- **For m2-slice (request in M2-UI-202):** `CutsceneSequencer._finish()` should call `overlay.box.dismiss()` instead of `overlay.box.visible = false`, so the box fades out at the end of a scene.
- 2026-10-25 (Lead's note received: list drifts, don't re-approve). **Before that note, this session re-approved four baselines after viewing; please check them on the PC gate:** `field_tip_card` (0b0969e1) and `save_shrine_field` (73257286), both M2-UI-29's pinned tip card 3 px left; `settings_accessibility` (73257286), rows' text 1 px up at 130 % (M2-UI-28/29); `bestiary_menu` (3ffe83bd), the baked Lantern Eel portrait replaces the live render (ADR 0110). From now on drifts are only listed here.
- 2026-10-25: **M2-HER-1103 (FAST-TRACK) ready for big9:** local branch `ui/her-1103` @ 15983dcd on `lead/gate-big9` (the three stand_ins in `game/data/ui/battle_sandbox.json` → `res://game/hero_motion/battle/<hero>_battle_actor.tscn`). On big9: clean import, battle tests 687 run / 0 failed. Battle shots not captured on big9 (the PC gate does them). It lands on claude/ui as soon as the integration branch carries big9.
