# Live log: ui-menus (branch `claude/ui`)

The old **ui** and **menus** tracks merged into one (Lead, 2026-10-25). `claude/menus` is retired: it is merged into `claude/ui` at 0b5c2bd9 and gets no more commits. The old logs, `ui.md` and `menus.md`, stay as history.

**Owns:** the HUD, objectives and map, prompts, title, tips, the dialogue box, settings, input parity, pseudo-loc, resolutions, and the field menu (Lattice, Equip, Items, Status, Formation, portraits, bestiary, codex, save).
**Id block:** tasks 200–399 (ui 200s, menus 300s), ADRs 0110–0129 (0120 is taken), handoffs `<date>-ui-ui-menus-<n>.md`.
**Integration branch:** `claude/new-session-mj8c3c` (from 2026-10-29; Lead `session_01Bg3iP7cPGyjbX4CyniBahc`).

## NEW ACCOUNT (from 2026-10-25)

### ANSWER TO THE LEAD'S 17:14 LIST (2026-10-27 17:20) — all six are DONE or BLOCKED; nothing is left for this track
1. **M2-MNU-305 menu motion — DONE** (30378725, on origin/claude/ui since 10-25; `test_screen_motion` 7/0; bestiary, codex, map, save and Settings all fade).
2. **Creature rim light in `creature_stage` — DONE** (3ffe83bd: per-creature `light_scale` and `stage_environment` for the five black creatures; viewed before/after). PC parity render requested (RENDER-REQUEST line below).
3. **Duplicate M2-UI-26 id — DONE** (the portrait task is M2-UI-1000, your big9 id; one file).
4. **Bestiary portrait-path ADR — DONE**: `docs/kb/decisions/0110-bestiary-uses-baked-portraits.md` (baked PNGs per ADR 0120, silhouette kept).
5. **Reefball menus — BLOCKED, not this track's:** M3-RBL-201 is `todo` for **combat** (engine fields in `game/minigames/reefball/**`, combat's files; the HUD holds no rules by design). M3-MNU-201 no longer exists: commit 4 of the Reefball patch closed it (the TextFitProbe fix, ef5dcd9f). The Reefball HUD itself (M3-UI-01) is in: reefball 67/0 on today's head.
6. **Every `todo` for ui/menus — DONE:** M2-UI-100 (d526ca72) and M3-UI-100 (6454c06c) were the only ones; the board shows no other `todo` with role ui, and it has no `menus` role.
**PC render gpu/render-ui-5317c0e: viewed, 25 battle shots re-approved (99623a0c).** Remaining waits are other tracks' or the PC's (see the queue line below). Route new ui-menus work here.

### STATUS FOR THE LEAD (2026-10-27 15:55; every sha below is on origin/claude/ui)
1. **M3-UI-01 Reefball HUD patch: DONE** (00f91c6c..ef5dcd9f, applied 10-25; reefball 67/0 then, battle 687/0 now). Do not re-apply: it is in.
2. **M2-MNU-305 menu motion: DONE** (30378725; screen_motion 7/0).
3. **Creature rim light: DONE** (3ffe83bd; `light_scale` + `stage_environment` in portraits.json for the five black creatures). PC parity render requested: `portraits:hullgnaw,scuttler,squall_wing,tide_crawler,undertows_reach` in the RENDER-REQUEST @ 5317c0e6 below.
4. **Duplicate M2-UI-26 id: DONE.** The bestiary portrait task is **M2-UI-1000** (your big9 id; this track's interim M2-UI-201 is retired). One file: `docs/kb/tasks/M2/M2-UI-1000-bestiary-creature-portrait.md`.
5. **Bestiary portrait path: DONE** — ADR 0110 (baked PNGs through BestiaryPortraitSlot, silhouette kept); 3ffe83bd.
6. **M3 UI from the board: DONE.** M2-UI-100 (narration as subtitles, d526ca72); M2-HER-1103 (80d358bf); **M3-UI-100 Ch8 set-piece HUD (ab855d62, merged at 6454c06c)**. Nothing else on `taskboard.py --role ui` is todo; M3-UI-100's running total across waves waits on M3-C08-02's `ch08_stair_groups_up` flag (blocked, logged in the task).

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
- 2026-10-27: **Battle shots recaptured on claude/ui (not approved; for the Lead to view on the PC gate).** 56 compared, 30 pass, 26 drift: drownbell_flood 0.01467, battle_choreo_melee 0.04321, battle_choreo_hit 0.02938, battle_choreo_support 0.03279, battle_choreo_ko 0.04996, battle_choreo_swap 0.01973, battle_arena_tideline 0.02916, battle_arena_causeway 0.02495, battle_choreo_lamp_dive 0.05946, battle_choreo_toll 0.06784, battle_arena_raft 0.05174, battle_arena_underway 0.05512, battle_arena_route 0.09482, battle_arena_derelict 0.02933, battle_arena_terrace 0.03472, battle_arena_tideline_dawn 0.03008, battle_arena_causeway_disc_sunset 0.02416, battle_arena_causeway_route_afternoon 0.09742, battle_arena_derelict_deck_night 0.02823, battle_arena_ash_terrace_lanternfall 0.03419, battle_arena_oruvel_raft_morning 0.05218, battle_arena_underway_tower 0.05802, battle_arena_shoals 0.03735, battle_arena_camp 0.03775, battle_boss_intro_matron 0.02519, battle_boss_intro_drownbell 0.06428. Viewed battle_arena_route, battle_arena_underway and battle_choreo_melee side by side: the big8 baselines show capsule stand-ins where claude/ui now draws the hero models (M2-UI-07 hero actor scenes), and Rhen's strike pose follows his clip. The other arena, boss-intro and drownbell shots drift the same way (heroes in frame). Under the limit but drifting: battle_pause 0.0054, battle_boss_intro_inquisitor 0.0040. Captures: /tmp/claude-0/-home-user-ClaudalFantasyX/f20129b0-04a0-5ef5-b544-556ac648a792/scratchpad/uim/bshots/out on this container only.

**MERGE-READY @ dcd69ed7** (claude/ui = big8 integration + claude/menus 0b5c2bd9 + this track): M3-UI-01 Reefball HUD (patch applied), M2-MNU-305 screen motion, M2-UI-202 dialogue box motion, M2-ARC-09 box width at ultrawide, M2-ARC-06 save menu follows UiSettings, M2-ARC-07 (review; already covered), M2-UI-201 baked bestiary portraits (ADR 0110) and stronger light for the five black creatures, M2-MNU-306 request (progression), the ported KO-test fix 9369e8c0; all in review. Checks run: gdlint + gdformat clean, validate_data 0/0, taskboard OK, full Godot suite 2431/1 before the KO fix, then battle 620/0, bestiary 37, portrait 18, creature 26, pseudo 21, aspect 13, dialogue 76, cutscene 37, save 194, theme 8, settings 48, map 22, codex 14, title 33, screen_motion 7; shots compared as listed above and in the earlier lines (reefball, settings, save, map, codex, dialogue unchanged). Skipped: coverage (no game/battle or game/progression code changed by this track; the one battle change is a ported test), Blender (no Blender source), the full manifest (Lead). Not yet in: M2-HER-1103 (waits on big9; ready on local `ui/her-1103`), hero portrait re-render (the new hero models come with big9).
- 2026-10-27: big9 is not on the integration branch yet. **M2-HER-1103 saved as a patch:** `docs/kb/handoffs/live/patches/ui-her-1103-big9.patch` (from `ui/her-1103` @ 15983dcd on `lead/gate-big9`; `git am` it after merging big9 into claude/ui). The Lead may also apply it straight onto big9/big10 as the FAST-TRACK for real heroes in battle: one data file, battle tests 687/0 on big9.
- 2026-10-27: **Hero portraits checked against big9's models:** `tools/portraits/render.sh --only rhen,asha,toma` on `lead/gate-big9` writes all 15 PNGs byte-identical to the committed ones, so the menus already show the current heroes. Re-run it after any later hero model change (characters / hero-integration).
- **Queue state:** items 1, 2, 4 and 5 done; item 3 (M2-HER-1103) is ready as a patch and lands when big9 does; item 6 is all in review. Next: the Lead's reviews of this track's tasks, M2-HER-1103 on big9's merge, and m2-slice's one-line `dismiss()` (M2-UI-202).
- 2026-10-27: **big9 merged into claude/ui (58357243) and M2-HER-1103 applied (80d358bf, FAST-TRACK):** Rhen, Asha and Toma's battle stand-ins now use `game/hero_motion/battle/<hero>_battle_actor.tscn`. Merge notes: PNG baselines take big9's (Lead-approved on the PC gate); shared files unioned (no duplicate loc keys); project.godot keeps the reefball_hud and ch08 translations; fighter_stand_in, formation_menu and test_battle_ko_once take big9's; the bestiary-portrait task keeps the Lead's id **M2-UI-1000** (this track's M2-UI-201 is retired unused; code, tests and ADR 0110 updated). Import clean, gdlint/gdformat clean (731 files), validate_data 0/0, taskboard OK. Battle tests, battle shots and the full suite running; the MERGE-READY line follows with the moved shots.
- 2026-10-27: **For the Lead (your 15:33 note):** M3-UI-01 (Reefball patch), the portraits re-render with the stronger creature light, M2-MNU-305 and the HANDOVER items were all done on 10-25 (see the queue table and the MERGE-READY @ dcd69ed7 line above). Since then: battle tests on claude/ui with the heroes 687/0. **M2-UI-100** (narration and #vo lines as subtitles: a faint 136 px panel on the letterbox band, an outlined line) is done on worktree branch `ui/vo-subtitles` @ d526ca72 (vo_subtitles 4/0, subtitles 9/0, dialogue_assist 12/0); it merges into claude/ui once the battle-shot and full-suite runs on the main tree finish. New shot `dialogue_voice_over`, baseline **new, for the Lead to view**. Next: M3-UI-100 (Ch8 set-piece battle HUD; M3-CMB-01's engine is in).

### Render requests
RENDER-REQUEST @ 5317c0e6: battle_hud_preview,battle_swap_menu,battle_victory,battle_statuses,battle_swell_ring,battle_read_panel,battle_opening_banner,battle_swell_modes,battle_vowbound_call,battle_vowbound_out,drownbell_flood,battle_swell_chant,battle_swell_brace,battle_swell_glyph,battle_statuses_colorblind,battle_pause,battle_choreo_melee,battle_choreo_hit,battle_choreo_cast,battle_choreo_support,battle_choreo_read,battle_choreo_ko,battle_choreo_swap,battle_arena_tideline,battle_arena_causeway,battle_choreo_lamp_dive,battle_choreo_toll,battle_choreo_vowbound_rise,battle_choreo_summon,creature_drownbell,creature_drownbell_rim_broken,creature_drownbell_toll,battle_hud_21x9,battle_hud_16x10,battle_arena_raft,battle_arena_underway,battle_arena_route,battle_arena_derelict,battle_arena_terrace,battle_boss_intro_hullgnaw,battle_arena_tideline_dawn,battle_arena_causeway_disc_sunset,battle_arena_causeway_route_afternoon,battle_arena_derelict_deck_night,battle_arena_ash_terrace_lanternfall,battle_arena_oruvel_raft_morning,battle_arena_underway_tower,causeway_c08_drownbell_disc_approach,battle_arena_shoals,battle_arena_camp,battle_boss_intro_inquisitor,battle_boss_intro_matron,battle_boss_intro_hermit,battle_boss_intro_wraith,battle_boss_intro_drownbell,dialogue_voice_over,dialogue_continue,dialogue_backlog,cutscene_hold_prompt,cutscene_act_card,bestiary_menu,creature_portraits,settings_hub,settings_accessibility,settings_controls,save_menu,save_menu_overwrite,save_shrine_field,field_tip_card,field_menu_codex,field_menu_map_haluna,field_menu_map_shrine,field_menu_map_underway,reefball_hud_choice,reefball_hud_goal,boot_title, portraits:hullgnaw,scuttler,squall_wing,tide_crawler,undertows_reach; why: claude/ui after big9 + M2-HER-1103 (hero battle actors in every battle shot), M2-UI-100 (dialogue_voice_over is new; its committed baseline is a cloud render, replace it with yours), M2-UI-202/ARC-09 dialogue box, M2-MNU-305 screen motion, M2-ARC-06 save menu, ADR 0110 bestiary portrait, the merge drifts listed above (settings_accessibility, field_tip_card, save_shrine_field), and a PC parity check of the five black creatures' portraits (rendered in the cloud with light_scale/stage_environment).
RENDER-REQUEST @ 6454c06c: battle_ch08_stair_hold, battle_hud_preview, battle_swap_menu; why: M3-UI-100: battle_ch08_stair_hold is NEW (no baseline yet: entry chips for the Climb and the Surge, the stair meter at 2 / 3, Kerrid kept out); the two others check the timeline chip and battle_hud.json changes leave a normal fight unchanged.

**MERGE-READY @ 6454c06c** (claude/ui = integration @ big9 + this track): M2-HER-1103 battle heroes (FAST-TRACK, 80d358bf), M2-UI-100 narration as subtitles, M3-UI-100 Ch8 set-piece HUD, plus everything in the MERGE-READY @ dcd69ed7 line; all in review. Checks run: full Godot suite on 5317c0e6 (big9 + heroes + M2-UI-100) **2601 run / 0 failed**; after merging M3-UI-100: import clean, gdlint + gdformat clean (736 files), validate_data 0/0, taskboard OK, no duplicate loc keys, set_piece 34/0 (worktree: battle 687/0, ch08 8/0, timeline 30/0, pseudo 22/0, aspect 13/0). Shots: none captured in the cloud (rendering is the PC's now); see the two RENDER-REQUEST lines. Moved battle shots expected from big9 + the hero repoint: every battle_* and drownbell shot with heroes in frame (the 10-27 list above). Skipped: coverage (no game/battle or game/progression core change; game/battle/scene only), Blender (no Blender source).
- 2026-10-27: **Coverage on claude/ui @ 6454c06c+: OK (within baseline)** — game/battle/ 99.89 % (2677/2680), game/progression/ 96.98 %, game/minigames/reefball/ 100 %; 2608 tests. (Correction to the MERGE-READY @ 6454c06c line: coverage was not skippable, since M3-UI-100 touched game/battle/scene/; it is now run and passes. On a 4-CPU cloud container it needs `HYMN_STEP_TIMEOUT=7000`: the default 600 s step limit times out.) Waiting on the PC's renders for both RENDER-REQUEST lines.
- 2026-10-27 16:58: **Re the Lead's 16:54 note:** M3-UI-01 Reefball HUD checked on the current head: reefball 67 run / 0 failed (patch merged since 10-25). M2-MNU-305, the creature light (+ PC render requested), the M2-UI-26 renumber (now M2-UI-1000) and the ADR 0110 follow-up are all done (status block at the top). Added: the M3-UI-100 stair meter is now in the aspect audit (`test_aspect_layouts` `test_set_piece_hud`: keeps its top pin at 16:10, 21:9 and 43:18, 100 % and 130 %), aspect 14/0.
- **Queue: empty or blocked, with reasons.** `taskboard.py` has no `todo` with role ui (there is no `menus` role on the board). Waiting on others: the PC's renders (two RENDER-REQUEST lines); M2-MNU-306 role word (progression); M3-RBL-201 Reefball preview fields (combat); M3-UI-100's running total (M3-C08-02's `ch08_stair_groups_up`); m2-slice's one-line `dismiss()` (M2-UI-202). Not taken without routing: the shrine teleport list (Systems owns the shrine UI) and the Kite world-map menu (M6). **Lead: route the next ui-menus item here, or name one of those two.**
- 2026-10-27: **PC render gpu/render-ui-5317c0e viewed:** 51 pass (including the cloud-rendered dialogue_voice_over and the four baselines self-approved on 10-25), 25 drift, all battle shots, all the heroes only (the hero battle actors' stance and pose replace big9's hero models; arenas, foes and HUD unchanged). **Re-approved after viewing** (99623a0c), with the PC's llvmpipe metadata.
RENDER-REQUEST @ 99623a0c: portraits:hullgnaw,scuttler,squall_wing,tide_crawler,undertows_reach; tool: tools/portraits/render.sh --only hullgnaw,scuttler,squall_wing,tide_crawler,undertows_reach; why: PC parity for the five black creatures' portraits rendered in the cloud with light_scale/stage_environment (3ffe83bd). (The ui@6454c06c request, battle_ch08_stair_hold etc., stays queued for after the big11 gate, per the Lead.)

### Queue from the Lead (2026-10-27 17:19): ui-menus also owns combat's, progression's and systems' UI-adjacent work
| # | Item | State |
|---|---|---|
| 1 | M3-RBL-201 Reefball preview fields (engine + HUD) | **done** (fe4faefa): against, fetches, refused_actions(), stakes_key; reefball 70/0, pseudo 22/0, aspect 14/0, parity 3/0; coverage running |
| 2 | M2-MNU-306 Formation role word (characters.json role_key, loc, validator, Formation) | **done** (89ff0d23): six role words, validator rule + test, on Formation's place line; formation 18/0, pseudo 22/0 |
| 3 | Shrine teleport list (visited shrines, confirm, fade) | **done** (f1b22523): ShrineTravelMenu after the save menu; shrine 43/0 (6 new), save_menu 20/0 |
| 4 | M3-UI-100 running total (`ch08_stair_groups_up` flag + request to act1-chapters) | **done**: flag declared, `objective.carry_flag` on the stair waves (validated), the meter shows "· N in all" (read only: a view never writes game state); M3-UI-203 asks act1-chapters to raise it in the flow; set_piece 35/0, pseudo 22/0, aspect 14/0, ch08 8/0 |
| 5 | "Parts look primitive" pass: title life, save slots with place/playtime/party portraits, battle result pacing, eased transitions | **done**: title reveal (84c5c37e), save rows' party faces (1f54fe28), result stagger, shop/inn motion; title 40/0, save 195/0, battle 689/0, shop 27/0, inn 10/0, pseudo 22/0, aspect 14/0; render requested |
| 6 | Accessibility sweep (100/130 %, colour vision, reduced motion; aspect + pseudo-loc for every new screen) | **done**: every screen added today is in the pseudo-loc walk at 100 and 130 % and in the aspect audit (Ch8 set piece, Reefball HUD with refused rows, Formation with the role, shrine travel: pseudo 23/0, aspect 15/0); every new motion has a Reduced-motion test (screens, dialogue box, title reveal, result stagger; the shop and inn use the same MenuMotion); colour is never alone: the stair meter's pips are filled vs ringed plus the count in words, Reefball's Contests / On a miss are words, refused actions are greyed with a reason |
| 7 | Controller and keyboard prompt audit | **done**: the interaction prompt, hold prompt, tip cards and dialogue {action} lines follow the last device (test_input_parity_glyphs, test_hold_prompt); menus' help lines use device-neutral action words; every `{action}` placeholder in loc is shown through InputNames.fill; one hard-coded key left, the Ch1 tutorial's "Hold F" (DLG_CH01_TUT_003), already filed as M2-FP-30 for its owner. New guard: `tools/tests/test_loc_key_names.py` fails on any player-facing string that names a key (allow-list: that one line until M2-FP-30) |
| 8 | Act I UI: area maps Ch4–Ch9, codex and bestiary for the 27 Act I creatures and NPCs | **done**: **maps**: Ch4, Ch5, Ch7 and Ch9 already had theirs; the Brine Shoals (Ch6) map and route stop added (bce52605; read only from act1-chapters' layout, so no request task was needed; Ch8 has no field zone of its own); zone_map 20/0, objective 15/0, test_zone_map_pois OK. **Bestiary**: after merging the integration branch (ff024dba) all 28 enemies (27 creatures plus the Inquisitor) have lore and the 27 creatures have baked portraits; the Inquisitor, a man, has none, and the slot falls back cleanly; bestiary 37/0. **Codex**: 22 Act I entries (26755f97): places Ch1 to Ch9, the Act I people, and the lamp-divers, the Order, the Pilgrim's Wake and the Saltwrights, each on the flag where Rhen learns it; codex 14/0, pseudo 23/0, aspect 15/0; Narrative asked to review (M3-NAR-01 note) |
RENDER-REQUEST @ 26755f97: field_menu_codex, field_menu_map_haluna, field_menu_map_underway; why: Act I codex (ch02_met_asha now also unlocks the Order entry, so World's count and New move in the codex shot) and the Brine Shoals route stop (check that the map strips near Haluna and the Underway are unchanged).

**MERGE-READY @ 26755f97** (claude/ui = integration @ 7cccb551 + this track): the Lead's 17:19 queue items 1–8, all done (see the table): M3-RBL-201, M2-MNU-306, shrine travel, M3-UI-100's running total, the 'parts look primitive' pass, the accessibility sweep, the prompt audit (test_loc_key_names), and Act I UI (the Ch6 map, 22 codex entries). Merge notes (ff024dba): encounters.json keeps carry_flag on the stair waves and adds the integration branch's three Ch8 field encounters; each conflicted baseline PNG takes the side approved last (11 ours, 1 theirs: battle_choreo_hit); balance_report.md is the integration branch's; shots/baselines/flags/PROVENANCE by merge_union.py. Checks run: import clean, gdlint + gdformat clean (765 files), validate_data 0/0, taskboard OK, no duplicate loc keys, test_zone_map_pois + test_loc_key_names OK; Godot: set_piece 35/0, bestiary 37/0, codex 14/0, zone_map 20/0, objective 15/0, shrine 43/0, pseudo 23/0, aspect 15/0, screen_motion 7/0, field_menu 32/0. Skipped: coverage (no game/battle or game/progression code since the coverage run at 6454c06c+; this batch is data, UI and tests), Blender (no Blender source), the full suite (the Lead's, after the merge batch). Shots: none in the cloud; three RENDER-REQUEST lines are pending (17325e00, 99623a0c portraits, 26755f97).
RENDER-REQUEST @ 17325e00: boot_title, save_menu, save_menu_overwrite, battle_victory, battle_read_panel, shop_menu_buy, shop_menu_sell, inn_menu, reefball_hud_choice, reefball_hud_goal, formation_menu, battle_ch08_stair_hold; why: the 'parts look primitive' batch (title reveal: boot_title settles 72 frames now; save rows' party faces; result row stagger; shop/inn motion), M3-RBL-201 (Reefball Contests tags, greyed refused rows, stakes from matches.json), M2-MNU-306 (Formation role word on the place line), M3-UI-100's meter with the running total (battle_ch08_stair_hold is new, no baseline).

- 2026-10-27: **Item 8 follow-up and the next item taken (M3-C07-05).**
  - **Correction to item 8:** the integration merge brought Ch8's field zones, so "Ch8 has no field zone" no longer holds. `ch08/corrow` and `ch08/coilspire` now have maps and route stops (a195cd39). The codex adds Coilspire and Ivo Brannick, and Corrow now unlocks on `ch08_arrived_corrow`. That makes 24 Act I entries.
  - **The tools codex test** still capped the set at 10. It is fixed (843448c2).
  - **M3-C07-05**, progression's, UI-adjacent, now in review (f0accc4c):
    - Tamsule's trader and inn;
    - the Tidecup rewards on the match row (validated);
    - the Oruvel Float, as a key item.
  - **ShrineServices**, so greybox shrines save, attune and offer travel. The Brine Shoals camp is in the network. The layout payloads go to act1-chapters as request **M3-UI-204**.
  - **Lead decision needed:** an accessory slot. The game has none (`equip_slots` is weapon and armor), so the Float can't be equipped and the Reefball outfitter has nothing to sell.
  - **Checks:**
    - shrine 47/0, reefball 70/0, shop 27/0, inn 10/0, item 82/0, save_menu 21/0;
    - zone_map 20/0, objective 15/0, map 22/0, codex 14/0, pseudo 23/0, aspect 15/0;
    - validate_data 0/0; gdlint and gdformat clean.
    - Tools suite: 1147 tests. The one failure is the expected `test_screenshots` gap: `battle_ch08_stair_hold` has no baseline until the PC renders it (RENDER-REQUEST @ 17325e00).
RENDER-REQUEST @ a195cd39: field_menu_codex; why: the codex set grew (Ch8 entries; the shot's flags unlock the Order entry as well). The map shots near Haluna and the Underway don't show the new Ch6 and Ch8 stops (the strip shows near stops only), so only the codex shot is asked again; it supersedes the 26755f97 line's field_menu_codex.

**MERGE-READY @ a195cd39** (claude/ui = integration @ 7cccb551 + this track): everything in the MERGE-READY @ 26755f97 line, plus:
- the Ch8 maps and codex entries;
- M3-C07-05 (Tamsule's data, the Tidecup rewards, ShrineServices);
- the tools codex test fix.

Checks are as listed in the line above. Skipped: coverage (no change in game/battle or game/progression), Blender (no Blender source), and the full Godot suite (the Lead's).

- 2026-10-27: **M3-C08-100 battle barks (combat's, UI-adjacent; 213a822f).**
  - BattleBarks floats "Hold." (Toma, Hold the Stair), "Pull!" (Liss, Haul) and "Virel." (Asha's call), from skills.json `bark_key` and vowbound.json `call_bark_key`. Speech shows with damage numbers off.
  - The sailmaker's needle is **blocked** on the same accessory-slot ruling as the Oruvel Float.
  - **M3-UI-203 is done:** M3-C08-02 already raises `ch08_stair_groups_up` after every set-piece fight. The Reach's objective now carries the flag too.
  - **Checks:** battle_barks 4/0, set_piece 35/0, ch08 14/0, validate_data 0/0, gdlint and gdformat clean. The battle filter and coverage results follow (game/battle/scene changed).
- 2026-10-27: **Viewed PC render `gpu/render-ui-6454c06`** (07f1a2e8; compare.txt: battle_hud_preview and battle_swap_menu PASS; battle_ch08_stair_hold has no baseline).
  - **The out PNG is NOT approved.** The stair meter sits on top of Wave 1's wrapped two-line tutorial; the help line grows to about y 155 at 1080p.
  - **Fixed in 121362b3:** the meter moves to y 164, with a test against the real node rects (set_piece 36/0, aspect 15/0, pseudo 23/0).
  - battle_ch08_stair_hold's first baseline comes from the 17325e00 request, which must now be re-rendered at or after 121362b3. **RENDER-REQUEST @ 121362b3 below supersedes the shot in 17325e00.**
  - **Known overlap:** the opening banner ([560,156,800,120], shown for a moment at battle start) overlaps the meter's first second. It is transient, and is listed here for the Lead's eye on the render.
RENDER-REQUEST @ 121362b3: battle_ch08_stair_hold, battle_hud_preview; why: the stair meter moved below the two-line help line (the 6454c06 render showed it over the tutorial); first baseline for battle_ch08_stair_hold; battle_hud_preview confirms a normal fight is unchanged.
- 2026-10-27: **big11 merged into claude/ui (abf39c37).**
  - **Merge notes:**
    - ownership.md keeps both rows;
    - conflicted baseline PNGs take the side approved last (6 theirs; battle_hud_16x10 and battle_hud_21x9 ours, from the 5317c0e approvals);
    - unions by merge_union.py;
    - **git's line merge had dropped `tut_menu_save_seen` from flags.tres; it is restored in the merge commit.**
  - **Checks on the merged tree:**
    - import clean, gdlint and gdformat clean (793 files), validate_data 0 errors;
    - the one warning is the integration branch's PROVENANCE row for a missing `haluna/offering_step.glb`;
    - battle 716/0, set_piece 36/0, battle_barks 4/0, shrine 47/0, codex 14/0, zone_map 20/0, settings 48/0, pseudo 23/0, aspect 15/0, field_menu 32/0, save_menu 21/0;
    - coverage on the pre-merge head is OK: battle 99.89 %, progression 96.98 %, reefball 100 %.

**MERGE-READY @ abf39c37** (claude/ui = integration @ 3cbcff9e (big11) + this track): everything in the MERGE-READY @ a195cd39 line, plus:
- M3-C08-100 battle barks (Hold. / Pull! / Virel.);
- M3-UI-203 closed, with the Reach's carry_flag;
- the stair meter moved below the two-line help (from the 6454c06 render).

Lead decisions open: an accessory slot (the Oruvel Float, the sailmaker's needle, the Reefball outfitter). Requests open: M3-UI-204 (act1-chapters: shrine payloads, Tamsule's trader, inn and shrine). Renders pending: 17325e00 (minus battle_ch08_stair_hold), 99623a0c portraits, a195cd39 codex, 121362b3 stair hold.
- 2026-10-27: **Viewed PC render `gpu/render-ui-99623a0`** (the five black-creature portraits). hullgnaw, scuttler, tide_crawler and undertows_reach are byte-identical to the committed PNGs. squall_wing differs only in its wing-edge glints (rmse 0.00835), the same image to the eye side by side. **Approved:** the PC's squall_wing.png replaces the cloud render, since the PC is the rendering authority. The portraits request is closed.
- 2026-10-27: **ADR 0040 implemented (the Lead's ruling: no accessory slot).**
  - **The sailmaker's needle** (4752ee3b) is a Customize material. With two Tide Pearls it crafts **Sea Legs** (a new armour ability, a ward against Slow) and is spent. The niche's `give` is requested in M3-UI-204.
  - **The Oruvel Float** (44d027c5) stays a key item, and its effect is a gate: `matches.json` `requires_item` and `ReefballMatch.is_open(row, holds)`, validated. It opens Oruvel's Act III league match.
  - **Reefball-only gear** (e4142ec0): `gear.json` holds two bands and two floats, worn one per kind, which add stats to the player's side through `ReefballMatch.setup(..., worn)`. The flags are `rbl_gear_<id>_owned` and `rbl_worn_<kind>`.
    - **The Tamsule outfitter:** ReefballOutfitterMenu, a TownMenu opened by a `{"reefball_outfitter": id}` payload. It buys, puts on, swaps and takes off gear.
    - The match HUD says "The side wears ...".
    - The outfitter is in the pseudo-loc walk and the aspect audit. **New shot `reefball_outfitter` (no baseline yet).**
  - **Checks:**
    - reefball 79/0, reefball_outfitter 6/0, customize 12/0, equip 66/0, item 82/0, shop 27/0, inn 10/0, town 6/0, pseudo 23/0, aspect 15/0;
    - **coverage OK** (2788 tests, all passing): reefball **100 %** (466/466), battle 99.89 %, progression 96.98 %;
    - validate_data 0 errors; tools test_reefball_validate 19/0.
  - **Tools suite:** test_zone_map_pois caught the Brine Shoals Channel spawn moving with Ch6's dressing (M3-C06-1200). The map POI follows it (fixed in this push). test_screenshots fails only on the new shots without baselines. test_audio_loudness and test_shrine_gi_bake are the integration branch's known failures, owned by audio and by the PC's `gpu/shrine-gi-big12` (CONSOLIDATED).
RENDER-REQUEST @ da7891cf: reefball_outfitter, reefball_hud_choice, reefball_hud_goal; why: ADR 0040: the new outfitter shot (first baseline), and the Reefball HUD's framing panel has a new line, hidden when the side wears nothing, so the two HUD shots should be unchanged.

**MERGE-READY @ da7891cf** (claude/ui = integration @ 3cbcff9e + ADR 0040 commit ceaa77b0 + this track): everything in MERGE-READY @ abf39c37, plus ADR 0040's three homes, plus request task M3-UI-204. **M3-UI-204 is new on this branch only; act1-chapters sees it after this merge:** the shrine payloads, Tamsule's trader, inn, outfitter and shrine, and the needle's give.

- 2026-10-27: **The Lead's 19:34 'continue' list.**
  - The title and save polish, the accessibility sweep and the prompt audit were finished earlier (queue items 5–7, table above).
  - Today's additions are covered:
    - the outfitter is in the pseudo-loc walk at 100 and 130 % and in the aspect audit;
    - its states are words (Owned, Worn, a refusal in words plus the danger colour);
    - the barks float through the HUD's motion scale;
    - test_loc_key_names passes on the new rows.
  - **M3-UI-204** waits on this branch's merge, then on act1-chapters.
  - **Nothing else is queued for ui-menus. Lead: route the next item here.**

### Queue from the Lead (2026-10-27 20:25)
| # | Item | State |
|---|---|---|
| 1 | M3-HER-1120 Liss's battle stand-in row | **done** (eb2ca60f): her row names hero-integration's wrapper (`liss_battle_actor.tscn`, on claude/hero-integration @ 7a8bff79). Until it merges she shows her capsule, since a missing scene falls back to the primitive. New test_battle_party_stand_ins: every Act I party member but Kerrid (no model) has a row. **The task file lives on claude/hero-integration; review there.** |
| 2 | Battle result pacing (M3-BPR-415's panel) | **done** (e80a6e6a, 06447718): EXP, movement, lume and drops count up from 0 as their row arrives (eased, `panel_open.count_sec`). The first Confirm while counting shows every number, and the next one chooses; a defeat or escape chooses at once. Reduced motion shows the final numbers. battle_victory settles 90 frames. test_battle_vitals now ends the count before its Retry. |
| 3 | Lattice polish (pillar 5) | **done** (75982b75): a woken node or opened gate blooms (none under reduced motion). Path steps are marked filled where they cost movement and hollow where they're free. Walk tags read "N movement", and a wake shows its Facet cost before Confirm. lattice 66/0. |
| 4 | Options QoL | **done** (aa35ead0): SpeedPreview on the Accessibility page. The text speed row reveals a sample line at the dialogue speed, and the battle speed row moves a pip across in one action's hold, with the time in words. **Remappable controls already exist** (Controls page, M2-UI-13: keyboard and pad columns, listen, reset). |
| 5 | Loc readiness | **done** (34d6e51d): tools/tests/test_loc_readiness.py guards against literal player-facing text in game code and scenes, and against tr() keys or key constants with no loc row. It finds none today; I removed one dead key constant. The speed previews are in the pseudo-loc walk (they now fit at 130 %); every other screen added since big9 was already in it. |

**Checks:**
- Godot: battle 720/0, lattice 66/0, speed_preview 3/0, settings 48/0, accessibility 9/0, battle_result 4/0, reward 10/0, field_battle 12/0, battle_party_stand_ins 2/0, pseudo 24/0, aspect 15/0, shop 27/0.
- Tools: test_loc_readiness 3/0.
- validate_data: 0 errors.
- Coverage: running (game/battle/scene changed).

**Known, pre-existing:** the aspect and pseudo runs print an ObjectDB leak warning at exit. It is present at 213a822f~1 as well, so it is not from this queue, and it fails no test.

RENDER-REQUEST @ 34d6e51d: battle_victory, lattice_menu, lattice_menu_activate, lattice_overview, settings_accessibility; why: the result count-up (battle_victory settles 90 frames; it must come to rest at the final numbers), the Lattice step markers and "N movement" tag, and the accessibility page with its (hidden-by-default) speed preview, which should be unchanged.
- 2026-10-27: **The coverage gate on the 20:25 queue caught test_swell_save:** it pressed Confirm while the new result count was running. The test now ends the count first (05a903d6). Coverage then passed: OK, all 2799 tests; battle 99.89 %, progression 96.98 %, reefball 100 %. Pushed.
- 2026-10-27: **big12 merged (0e7c26a5).**
  - **Merge notes:**
    - encounters.json takes the integration's rows (their wall_head_storm arenas) and keeps this branch's carry_flag on the Reach;
    - ownership.md keeps both rows;
    - five baseline PNGs take the integration's;
    - no flag or loc key was lost.
  - **Ch8's zones moved onto env-art's kits** (M3-C08-1202, ADR 0200), which broke the Ch8 maps. Fixed generically (50182f0e):
    - ZoneMapShapes reads the layout's `collision_path`: its blocks, and its ramps as pads;
    - a shape hint ending in `*` names a kit's numbered pieces;
    - the POIs and bounds move to the kit frame;
    - Coilspire's tiers now stack vertically, so its map keeps the path, the hut and the door.
    - Checks: zone_map 21/0, objective 15/0, map 23/0, test_zone_map_pois OK. **Every map of a future kit-dressed zone will read its collision file the same way.**
- 2026-10-27: **Viewed renders.**
  - **`gpu/render-ui-a195cd3`: approved** field_menu_codex (the counts only, 9 of 34).
  - **`gpu/render-ui-121362b`: not approved.** Its battle_ch08_stair_hold has the meter fix but the old sandbox arena. big12's approved baseline (6e15d8d8) has the new wall arena, but **the meter is back over the tutorial**, because it was rendered from a tree without 121362b's fix. Neither image matches the merged tree, so the shot needs a fresh render:
RENDER-REQUEST @ 50182f0e: battle_ch08_stair_hold; why: big12's baseline shows the stair meter over the two-line tutorial (rendered without 121362b's fix); at this head the meter sits below the help line over the wall_head_storm arena. A small request for the Lead's cloud render server.
- 2026-10-27 22:30, **for the Lead's re-sent list:** items 1–5 were done before it arrived. See the "Queue from the Lead (2026-10-27 20:25)" table, pushed at 54a835a3. **Item 6, the accessibility and controller-prompt audit of every screen added since big9, is done** (5650bc47). Per screen:

| Screen | Checks |
|---|---|
| Shrine travel | pseudo-loc 100/130 %; aspect; reduced motion (MenuMotion); **new: input parity** (keys, pad, mouse) |
| Reefball outfitter | pseudo-loc; aspect; reduced motion (TownMenu's motion); states in words (Owned, Worn, refusals); **new: input parity** |
| Reefball HUD | the refused rows and the "The side wears" line: pseudo-loc, aspect, existing parity |
| Set-piece HUD | the meter now clears the two-line help (tested on real rects); pips filled vs ringed plus words |
| Speed previews | pseudo-loc (fits at 130 %); **new: aspect sweep with it showing**; under reduced motion the battle pip is words only |
| Result count-up | Reduced motion shows the final numbers; Confirm skips the count; parity via test_input_parity_battle |
| Lattice | the bloom is off under reduced motion; step markers are filled vs ringed (shape, not colour alone); existing Lattice parity |
| Battle barks | speech floats with damage numbers off, at the HUD's motion scale |

  - **Prompt audit:** every new help line uses device-neutral action words. test_loc_key_names and test_loc_readiness pass.
  - **Checks:** input_parity_shop 3/0, input_parity_shrine 2/0, aspect 16/0.
  - **Queue empty again. Lead: route the next item.**

- 2026-10-27 23:40, **the Lead's 22:50 backlog:**
  - **M3-UI-1212 and M2-HER-1108 (05429d6d, 109c827e):**
    - the Bell Galleries' walks and platforms and Corrow-by-night's wall-walk and strand are hinted as floors (their rails as structures), now that the map reads kit collision files;
    - Ysolde's battle stand-in names `ysolde_battle_actor.tscn` (yaw -90);
    - the primitive stand-in test uses the default spec.
    - **Checks:** zone_map, battle_choreo, battle_party_stand_ins pass.
  - **M3-UI-205, the Kite's world map (469851f6), now in review (design).**
    - **The model:** KiteMapModel over `game/data/world/kite.json`. Places show by flag. Here is marked and can't be chosen. Fly asks first (Stay under the cursor) and goes through `ShrineNetwork.travel_to`.
    - **Search:** "Search the chart" names a square (keys, pad, or the pointer over KiteChart) and finds secret places, which then join the list.
    - **Coverage:** validator `check_kite`; input parity 3/0; pseudo-loc 25/0; aspect 17/0; test_kite_map 5/0.
    - **Not mounted:** the Kite itself (Act III) doesn't exist. Its owner calls `KiteMapMenu.open_in(host, KiteMapModel.from_game())`.
    - **`game/data/world/kite.json`** is added to the ui-menus ownership row (a new file under Systems' path).
  - **Blocked on missing content, not started:**
    - The Act II codex and bestiary: no Act II enemy or boss exists yet; all 28 enemies are Act I.
    - The Ansedra and Lowlight maps: no zone exists for either.
    - Both start the day those rows or layouts land.
  - **Tools suite:** test_screenshots still fails only on missing baselines (`reefball_outfitter`, now `kite_map` too), which wait on renders.
RENDER-REQUEST @ 469851f6: kite_map; why: a new screen (the Kite's world map, M3-UI-205: the list with Here, the chart with gems and the cursor ring on Tamsule); no baseline yet, so test_screenshots needs it.
- 2026-10-27 23:55, **BACKLOG EMPTY:**
  1. **Renders:** no unviewed ui render branch. The latest, 121362b, a195cd3, 99623a0, 26755f9 and 17325e0, are all handled. Four requests are open: `kite_map`, stair_hold, the 34d6e51d batch, and the outfitter.
  2. **Tasks:** no `todo` ui task.
  3. **Requests:** none addressed to ui.
  4. **Parts-look-primitive audit:** done today (see "Parts look primitive", ui.md). The only new screen since, the Kite, has no render to view yet.
  5. **Next act:**
     - The Kite's world map is done (M3-UI-205).
     - The Act II bestiary and codex wait on Act II enemy rows. Only art briefs exist (`docs/kb/art/creatures/act2/`); `enemies.json` is still the 28 Act I rows.
     - The Ansedra and Lowlight maps wait on their zone layouts.

  Merged the integration branch (5720fa26). Handoff: `2026-10-27-ui-ui-menus-2.md`. **Lead: route the next item, or ping when Act II enemies or zones land.**
- 2026-10-28 00:40, **the Lead's 23:37 list:**
  1. **The Kite row in the field menu, behind `kite_flying` (abbb8476):**
     - The row isn't there until the Kite flies. Then it sits after Map, and the panel grows by one row (field_menu.json `extra_rows`, `FieldMenu.grown_for`), so Close never scrolls away unseen.
     - The row stays out of `ROOT_IDS`, so every other row keeps its index (tests and shots use it).
     - Cancel comes back to the menu; a flight closes the menu too.
     - **Checks:** test_field_menu_kite 4/0, aspect 18/0, pseudo-loc 26/0; shot `field_menu_kite`.
  2. **Renders viewed:** `lead/gate-render-ui-da7891c` **approved** (892334f2).
     - `reefball_outfitter` reads cleanly.
     - The `reefball_hud_choice` drift is the intended refused Loft row (M3-RBL-201). Nothing reefball changed since.
  3. **Merged `claude/act1-chapters` into claude/ui (4d2e25cf)** to build Act II UI against its Ch10–16 zones, flags and names. The shared files are a union (flags 190 + 174 = 205, none lost; shots, baselines, translations). env-art and creatures are not merged: nothing here needs them yet. **Lead: merge act1-chapters before or with claude/ui.**
  4. **M3-UI-206, Act II area maps (3e787f14):**
     - All 15 Ch10–16 greybox zones are in `zone_maps.json`.
     - The route runs on to the Drowned Choir (30 stops).
     - A layout's own `ramps` now draw as pads.
     - Strings: `maps_act2.csv`.
     - test_zone_map checks every greybox zone (27). Three shots.
  5. **M3-UI-207, Act II codex (ce258864):**
     - 14 places and 2 peoples (the Kirru, the Ullari), each on its chapter's arrival flag.
     - Spoiler-safe, per M3-NAR-01. Review: narrative.
  6. **The bestiary:** no branch has an Act II row in `enemies.json` (creatures added only the actors), so **M3-UI-208 asks Combat for them**. The bestiary lists them with no UI change.
  7. **Shops and inns (4d32a621):**
     - Shops: `quellan_trader`, `ansedra_purveyor`, `hollowmere_chandler`.
     - Inns: `quellan_inn`, `hollowmere_inn`.
     - Strings: `towns_act2.csv`.
     - The layouts have no such triggers yet, so **M3-UI-209 asks act1-chapters** for the triggers, the `Shrine` spawns and the shrines rows.
  - **Correction to 23:55:** the Act II zones and Ansedra/Lowlight do exist (on act1-chapters). The BACKLOG EMPTY line is withdrawn.
RENDER-REQUEST @ 4d32a621: kite_map, field_menu_kite, field_menu_map_keth_pass, field_menu_map_lowlight, field_menu_map_ansedra, field_menu_codex; why:
- the Kite's map;
- the field menu a row taller with the Kite;
- three Act II maps (the raised landings and flights, the drowned shaft, the domes on the lagoon);
- the codex counts move (34 → 50 entries).
- 2026-10-28 01:10, **item 5 (the board and the next act):**
  - **M3-UI-210:** the act card names "Act III: The Unbinding", for Ch16's act break (cinematics reviews; Ch16's `.dlg` calls it).
  - **The Kite** can land at Reedhollow, Lowlight, Quellan and Hollowmere, each on its arrival flag. Ansedra stays off.
  - **Reviewed M3-CRE-618 (approved, done).** The bestiary bake now gives the flue moth, oil slug and both polyps the dark rows' lighting (51f1a58d).
  - **Lead:** M2-MNU-306 (the formation role word) names ui as its reviewer, but ui-menus did the work. It needs another reviewer (progression or the Lead).
  - **Already covered for Act II, no change needed:**
    - the area title cards (they read `locations.json`);
    - the save slots' chapter text;
    - the Memories gallery (it lists chapters with replayable scenes; Act II has none until its beat sheets).
  - **Waiting on others:** M3-UI-208 (Combat: Act II enemy rows), M3-UI-209 and M3-UI-204 (act1-chapters: shop, inn and shrine triggers).
  - **A full Godot suite run** after the act1-chapters merge is in progress.
RENDER-REQUEST @ 51f1a58d: portraits for flue_moth, oil_slug, spawn_polyp, wall_polyp (tools/portraits/render.sh, the creatures list); why: the dark rows' light_scale and cool backing now apply to them (M3-CRE-618's follow-up). Rebake those four PNGs into assets/ui/portraits/creatures/.
- 2026-10-28 01:20, **for the Lead's two messages:**
  - **The Ch8 maps on the big13 tree.** claude/ui already has the fix, so nothing more is needed here. 50182f0e (2026-10-27) moved both Ch8 maps onto the kit frame:
    - ZoneMapShapes reads a layout's `collision_path`;
    - the POIs and hints follow the kit pieces.

    claude/ui also contains act1-chapters @ ed4dee69 (merged at 4d2e25cf). At this head, `test_zone_map` is 21/0 and `tools.tests.test_zone_map_pois` is OK. The big13 tree must have taken a claude/ui head from before 50182f0e. **Merge claude/ui at b5136683 or later.**
  - **`lead/gate-render-ui-34d6e51`: approved** `battle_victory`, `lattice_menu`, `lattice_menu_activate` and `lattice_overview`. `settings_accessibility` passed.
    - **Noted for my audit:** in `lattice_overview`, the heroes' small initials crowd their name tags (R R R next to "Rhen"). This predates the render.
  - **`lead/gate-render-ui-da7891c`:** approved earlier (892334f2).
  - **Render requests consolidated (TRACK-RULES: one open per track).** The requests @ 50182f0e, 469851f6, 4d32a621 and 51f1a58d are superseded by the single request below.
SUPERSEDED (self-rendered below, TRACK-RULES 2026-10-28 01:00): RENDER-REQUEST @ a8558176: battle_ch08_stair_hold, kite_map, field_menu_kite, field_menu_map_keth_pass, field_menu_map_lowlight, field_menu_map_ansedra, field_menu_codex, lattice_overview, plus the bestiary portraits for flue_moth, oil_slug, spawn_polyp and wall_polyp (tools/portraits/render.sh). Why:
- the stair meter clear of the tutorial on the wall_head_storm arena;
- the Kite's map, and the field menu a row taller with it;
- three Act II maps;
- the codex counts (34 → 50);
- four dark creatures relit.
- the Lattice overview's initials no longer crowd the name tags (own audit; a8558176; the request above now names this head).
- 2026-10-28 01:45, **for the Lead's 00:20 message ("you're idle"):** all four items were already done and pushed by then (see 00:40 and 01:20 above).
  - **Why big13 fails Ch8:** big13 merged claude/ui @ 6ea4998f. The Ch8 kit-frame maps came later, at 50182f0e.
  - **The fix is merged:** **claude/ui now contains lead/gate-big13 (e010d0f1)**, so merging claude/ui at e010d0f1 or later is conflict-free.
  - **How the conflicts were resolved:**
    - **`zone_maps.json`:** keeps M2-FP-1000's causeway map and adds Act II's fifteen zones. `test_zone_map` now counts 28 greybox zones.
    - **`battle_sandbox.json`:** keeps Liss's wrapper row.
    - **`test_battle_choreo.gd`:** takes big13's version.
    - **`test_ch08_flow.py` and the docs:** union.
    - **`ownership.md`:** keeps the newer ui-menus row, which adds `kite.json`.
    - **M2-HER-1108:** stays done, as big13 marked it.
    - **flags:** union, none lost.
  - **Checks on the merged tree:**
    - `test_zone_map_pois`, `test_ch08_flow`, codex, kite and loc: OK.
    - The tools suite: 1302 tests. The only failure is `test_screenshots`, the baselines waiting on the open render request.
  - **In progress:** a full Godot suite on the merged tree.
- 2026-10-28 02:10, **the Lead's 01:00 message (render your own):**
  - **The full Godot suite on the merged tree (e010d0f1): 3026 tests, 3 failing cases.**
    - `test_creature_portraits` was ui's: the Act II creatures were in the portrait manifest without their PNGs. Now **fixed:** 16 Act II creature and boss portraits baked with `tools/portraits/render.sh`, viewed, and given PROVENANCE rows. The four dark ones are relit for M3-CRE-618.
    - `test_hero_field_snaps` (the Bell Galleries, Coilspire, the Drowned Choir) is not ui's: hero-integration and act1-chapters.
    - `test_qa_capsules` (Pell as a capsule in Ossa Fen) is not ui's: act1-chapters and character.
  - **The 5317c0e request is superseded.** Every one of its 25 drifts has a newer baseline the Lead approved since. a8558176's request is superseded by the renders below.
SELF-RENDERED @ 5f9c71fd: battle_ch08_stair_hold, kite_map, field_menu_kite, field_menu_map_keth_pass, field_menu_map_lowlight, field_menu_map_ansedra, field_menu_codex, lattice_overview. What I saw:
- battle_ch08_stair_hold (drift): the meter clears the two-line tutorial on the wall_head_storm arena.
- field_menu_codex (drift): "9 of 50"; Places "3 of 27".
- lattice_overview: pass.
- field_menu_kite (new): the Kite row after Map, and all 13 rows show.
- The three Act II maps (new) read: Keth Pass's landings and flights, Lowlight's waterline over the shaft, Ansedra's domes on the lagoon.
- **Fixed after viewing:** every map said "Haluna's lanes are yours to walk". OBJ_NONE is now general; Haluna keeps its line through `idle_keys`.
- **kite_map (new), fixed after viewing:** the grid's 1 px lines vanished when scaled down; the labels sat off-centre; the gems were pushed into the next square; the line read "Tamsule, in Tamsule". The panel now grows so ten rows show.
SELF-RENDERED @ e2852192: kite_map, field_menu_map_keth_pass, field_menu_map_lowlight, field_menu_map_ansedra. Re-rendered after the fixes: the grid whole and the labels centred, the idle line general. Still to land: the baselines, at the Lead's gate. No open render request.

SELF-RENDERED @ (the Kite ring tweak) kite_map: re-rendered after the last tweak. Tamsule shows only its ring under the region label. Clean.
- 2026-10-28 02:25, **BACKLOG EMPTY:**
  1. No ui render branch is unviewed. My own shots are self-rendered and viewed (above).
  2. No `todo` ui task: M3-CRE-634 and M3-HER-1120 were already done and are now in review.
  3. No open request to ui.
  4. Audit: the Kite chart and the idle objective line were fixed today, the Lattice overview's initials yesterday.
  5. Act II UI is done as far as content allows. What's left waits on other tracks:
     - **M3-UI-208 (Combat):** Act II enemy rows, so the bestiary lists them. Their portraits are already baked.
     - **M3-UI-209 and M3-UI-204 (act1-chapters):** the shop, inn and shrine triggers.
     - **The Act II beat sheets (M4-C10-01 onward):** objectives, story codex entries, the farewell-tide and the Ch16 act card call.
  - **For the Lead:** the two non-ui failures in the full suite are `test_hero_field_snaps` (hero-integration and act1-chapters) and `test_qa_capsules` (Pell in Ossa Fen).
- 2026-10-28 03:30, **REFOCUS (ADR 0041, the human's directive): Act I at final quality.**
  - **Paused, blocked-by ADR 0041** (92a4f777): M3-UI-205 (the Kite), M3-UI-206 and 207 (Act II maps and codex), M3-UI-208 and 209 (the Act II requests) and M3-UI-210 (the Act III card). Everything built stays as is; nothing is reverted.
  - **M3-UI-211, the Act I menu audit** (full table: `docs/kb/qa/ui_act1_menu_audit.md`):
    - **Battle HUD:** heroes show their faces and foes their bestiary pictures, where initials and bare shapes stood (71689a7b).
    - **Ysolde and Liss** have portraits now, so the menus no longer show "Y" and "L" (71689a7b).
    - **Icons in every menu row:** 43 original vector icons in StatusGlyph's style for items, equipment, abilities and the lume. They show in the bag, shop, equip, battle Skills, Swell and Items, and the victory panel (1a79cdc9, 2b0a5ffb).
    - **The bestiary** has a portrait for every creature (5f9c71fd).
    - **The maps** no longer say Haluna's idle line in other zones (5f9c71fd).
  - **Waiting on others:** Kerrid's model (M3-CHR-505, characters, doing) and the Inquisitor's (M3-C06-06). Until then both show their letter, and the battle shows a primitive.
  - **Checks:**
    - test_battle_portraits 3/0, test_menu_glyphs 3/0, hero_portraits 9/0, creature_portraits 4/0;
    - items 13/0, shop 28/0, equip 66/0, input_parity 61/0, pseudo-loc 26/0, aspect 18/0, rewards and result OK;
    - the full battle filter is running.
SELF-RENDERED @ 2b0a5ffb: battle_hud_preview, battle_statuses, battle_swap_menu, battle_opening_banner, battle_ch08_stair_hold, items_menu, shop_menu_buy, equip_menu, battle_victory, menu_glyphs. What I saw:
- **Battle HUD:** faces in the party rows and timeline; foe pictures in the timeline diamonds; petrified Asha still stone with strata lines.
- **Items, shop and equip rows:** an icon before every label. The first render had the icons under the labels, because the cursor's nudge reset the label's x. Fixed and re-rendered.
- **battle_victory:** fighter faces, drop icons and the lume's coin.
- **menu_glyphs (new review sheet):** all 44 icons distinct. Flask, scale and sword were redrawn after the first view.
SELF-RENDERED @ d9bc59fc: reefball_hud_choice, reefball_outfitter, cutscene_act_card, save_menu, dialogue_continue. The first four pass. dialogue_continue drifts only in the palms' wind (environment); the box is unchanged. The audit's Act I screen list is done.
- 2026-10-28 04:00, **the Lead's 01:54 list:**
  1. **M3-HER-1147 (ui-menus' 3 rows in the Act I inventory).** The task and the audit tool are on claude/hero-integration only, so I'm not editing the task file here; this line stands in.
     - `ysolde_neutral.png` and `liss_neutral.png`: **done** at 71689a7b. Five emotions each, viewed, with PROVENANCE rows.
     - `kerrid_neutral.png`: his model and stage have **landed on claude/characters** (`game/levels/_tests/characters/kerrid/`). Next I merge claude/characters and bake him, with Moll (the Inquisitor, for his bestiary picture) and Sefir.
     - The inventory's line about Liss having no battle actor is stale for claude/ui: Liss's `battle_sandbox.json` row names `liss_battle_actor.tscn` (M3-HER-1120).
  2. **Dialogue portraits for every named Act I NPC:** next, after the bakes.
  3. **First-hour polish at 1080p and 720p:** after that.
MERGE-READY @ 9819ba71: M3-UI-211 (faces in the battle HUD, Ysolde and Liss portraits, icons in every menu row, the victory panel), the Act II pause. Checks: battle 765/0, items 13/0, shop 28/0, equip 66/0, input_parity 61/0, pseudo-loc 26/0, aspect 18/0, menu_glyphs, battle_portraits, hero_portraits, creature_portraits, rewards, result; validate_data, taskboard and lint clean; shots self-rendered and viewed. Skipped: the full tools suite (no tools/ change since the last run) and coverage (no game/battle core change; battle_menus and battle_rewards are scene layer, covered by the battle filter).
- 2026-10-28 05:10, **the Lead's 01:54 list, done:**
  1. **M3-HER-1147, all three rows are final.**
     - Ysolde and Liss: done at 71689a7b.
     - Kerrid: done at 22ad757e3. claude/characters is merged at 526856cf8 for his model, Moll's and Sefir's.
     - Two shared-file conflicts were resolved by three-way merge:
       - `blender_builds.json` adds characters' kerrid and moll jobs;
       - in `requested_clips.json` the characters track's specs win where both sides changed them, and Rhen's built `lie_in_shallows` leaves the list.
     - `tools.tests.test_hero_clips` is OK.
  2. **Portraits for named NPCs:**
     - Moll and Sefir are baked (Kerrid with them, five emotions each, viewed).
     - The Inquisitor shows Moll's face in the bestiary and the battle timeline (`creature_portraits.json` people).
     - **The dialogue box now shows the speaker's portrait** (58f2190c2) in the line's emotion. Untagged lines keep the last emotion. Narration, voice-over and speakers with no portrait yet show none, so no letter ever stands in. Aliases: inquisitor → moll.
     - Still to bake as characters land them: Tavi, Kell, Garo, Ivo, Neme, Pell, Osu, Fenn and the other named folk. Their stages don't exist yet; I'll watch claude/characters.
  3. **First-hour pass at 1080p and 720p:** title, save menu, area title, tip card, interact prompt, act card, the first battle's opening banner, the dialogue box.
     - The 1080p variants were rendered from a temporary manifest that was never committed.
     - All are legible, with no overflow or clipping. The title's "Development build" label is debug-only (title data `debug_only`), so release exports hide it.
     - The dialogue portrait's first size (180 px) pushed the box up; 156 px keeps its height. Re-rendered and viewed.
SELF-RENDERED @ 58f2190c2: dialogue_continue (Rhen's portrait beside his line, the box at its baseline height); dialogue_voice_over (no portrait on narration); plus 1080p and 720p views of boot_title, save_menu, field_area_title, field_tip_card, cutscene_act_card, field_interact_prompt, battle_opening_banner and dialogue_continue. All clean.
MERGE-READY @ 4faaa4f0: M3-HER-1147 (Kerrid, Moll and Sefir portraits; the Inquisitor shows Moll's face), the dialogue speaker portrait, and the first-hour pass; claude/characters is merged in (526856cf8). Checks: cutscene 77/0, dialogue 81/0, input_parity_dialogue 5/0, aspect 18/0, pseudo-loc 26/0, subtitle 9/0, hero_portraits 9/0, creature_portraits 4/0, battle_portraits 3/0, bestiary 37/0; tools test_hero_clips OK; validate_data and lint clean; shots self-rendered and viewed. Skipped: coverage (no game/battle core or progression change); the full tools suite (only test_hero_clips can see the merged files, and it ran).
- 2026-10-28 05:30, **BACKLOG EMPTY:** the Lead's 01:54 list is done and merge-ready. The next portrait bakes wait on claude/characters: it has stages only for the party, Moll and Sefir, plus a generic villagers stage, none for a named NPC (Tavi, Kell, Garo, Ivo, Neme, Pell…). I'll bake each one as its stage lands.
- 2026-10-28 06:00, **the Lead's 03:19 list:**
  - **M3-UI-101 (slice-polish's request; the task is on claude/m2-slice):** the audit rendered the m2-slice tree, which didn't have claude/ui's 71689a7b.
    - Already in place on claude/ui:
      - faces in the timeline and the party rows, Kerrid and Liss included;
      - foe pictures, with the Inquisitor showing Moll's;
      - the initial only where no picture is baked.
    - Added now (f6db67f0f):
      - the foe's picture fills its diamond (a textured polygon), so the shape cue stays;
      - a petrified hero's face greys to stone under the strata lines, as the criteria ask.
    - **slice-polish: please tick M3-UI-101's criteria on your branch** once claude/ui merges. I can't edit your task file from here.
  - **The first-hour pass at 1080p and 720p:** done (05:10 above).
  - **Field HUD audit: no stand-ins.**
    - The interaction prompt plate (the key cap and verb) and the save shrine's "Rest at the shrine" prompt and tip are final.
    - The objective line and the destination cue at the screen edge read cleanly.
    - The zone's name is the area title card (viewed). There is no minimap by design: the map is in the field menu.
SELF-RENDERED @ f6db67f0f:
- **battle_statuses:** the petrified face shows grey under the strata.
- **battle_boss_intro_drownbell and battle_hud_preview:** faces on every hero chip and row, and each foe's picture in its diamond.
- **field_objective_line, save_shrine_field, field_hero_party:** clean.
MERGE-READY @ 588faa1a: M3-UI-101 (a foe's picture fills its timeline diamond; a petrified face greys under the strata) and the field HUD audit (no stand-ins). Checks: battle 765/0, battle_portraits 3/0, party 30/0, status 51/0; lint clean; shots self-rendered and viewed. Skipped: coverage (game/ui only, no battle core change).
- 2026-10-28 04:25, **the Lead's 04:02 list:**
  - **(1) big13 merged** into claude/ui (d984de2c1, pushed). The full suite is running on it; the result follows in the MERGE-READY line.
  - **(2) Dialogue portraits as characters lands them.** claude/characters merged at c99275a1f. The **Stillguard** (M3-CHR-508; 4 Act I lines) is baked as `stillguard_neutral.png` (fc13fc1eb). Its stage has no face-pose table, so it gets neutral only; test_hero_portraits allows that for a speaking extra. Characters has no other new named NPC yet (Tavi, Kell, Garo, Ivo, Neme, Pell, Osu and Fenn are not modelled). I check again about every 30 min.
  - **(3) Field HUD pass over the dressed areas:** new shots `field_hud_over_{haluna,oruvel,tamsule,corrow_night}` hold all four overlays at once. Fixes (721efa2f0):
    - **Tip card vs area title (a real collision):** both show when the field first takes input. Corrow's long night name, "Corrow, the Night of the Ebbing", ran under the tip card. The tip card's top moved below the title band (y 156 → 396). test_field_hud_legibility keeps them apart at five aspects and checks every Act I name fits the title.
    - **The cue's distance words** ("A short walk") were illegible over Haluna's bright sky, because they float with no plate. They now carry a 6 px outline (`label_outline_px`).
    - **The title band** is deeper, at alpha 0.55 → 0.65, for bright clouds.
    - `field_tip_card`'s baseline moves with the tip card (expected).
  - **(4) Input pass:** test_input_parity_glyphs now reads every loc row (12349380c):
    - every `{field_*}`/`{ui_*}` token is a real action;
    - pad-button actions read as the pad button after a pad press and as the key after a key press;
    - stick-only actions (movement and camera) must say "stick" in their line;
    - no Act I row names a binding in plain words;
    - the interaction and Ch9 hold keycaps and Ch1's shutter follow the device.
    It caught one: the Ch1 tether tutorial said "Press interact". It now names `{field_interact}` (932916b1d; a one-token .dlg fix, recompiled with dlgc). **narrative: FYI.**
SELF-RENDERED @ 24bc20e15 (the shots' scratch interactable left of the cue): field_hud_over_haluna, field_hud_over_oruvel, field_hud_over_tamsule, field_hud_over_corrow_night, field_tip_card. What I saw:
- **Haluna (bright sand and sky):** all four overlays read. The cue's outlined "A short walk" is legible over the clouds.
- **Oruvel (open water):** clean; the edge arrow sits top right.
- **Tamsule (water and bright sky):** clean.
- **Corrow at night:** the long title is clear of the tip card, which sits below the band. The cue and its words read over the dark sea.
- No baselines written. No open render request.
- 2026-10-28 05:10, **the named Act I NPCs landed on claude/characters** (M3-CHR-526..539). Merged at a1c155de9.
  - **Baked dialogue portraits** (a2882374b): 20 speaking townsfolk, five emotions each (neutral, smile, determined, worried, grief), from their villager stages and face-pose tables. PROVENANCE rows added.
    - Named: Tavi, Kell, Garo, Neme, Osu, Fenn, Hobb, Marra, Sabe, Ione, Skipper Sadi.
    - By role: the poolkeeper, scale-man, ferrymaster, tender, Reed, net-mender, fisher, vendor and child.
  - **New guard:** test_dialogue_box fails when an Act I speaker's model lands without a baked portrait.
  - **Not modelled yet:** Ivo (M3-CHR-540, a Stillguard variant) and Pell. They show no portrait (no initial letter) until they land.
SELF-RENDERED @ a2882374b: portraits for all 20 NPCs (contact sheets of neutral, plus Tavi's and Marra's five emotions). What I saw: faces centred, hair and headwear inside the frame, and each emotion reads. The child's portrait frames a little smaller (a smaller body), which is acceptable.
- 2026-10-28 05:15: Liss's soft fringe (M2-CHR-521) merged at 201cde902. Her five portraits were rebaked (296ceb696) and compared with the old ones: the fringe now falls in soft clumps. characters' later skirt floor drape (M2-CHR-522) is a kneel-only change and touches no portrait, so nothing was rebaked for it.
MERGE-READY @ 296ceb696: the Lead's 04:02 list.
- big13 merged.
- Field HUD legibility over Haluna, Oruvel, Tamsule and Corrow at night (four new shots, the tip card below the title band, the cue words outlined).
- Act I input glyphs (test_input_parity_glyphs covers every prompt; the tether line fixed).
- Dialogue portraits: the Stillguard, 20 townsfolk, and Liss rebaked.
Checks:
- Full suite at 296ceb696: 3040 run, 2 failed, both outside UI and both present before this work:
  - test_hero_field_snaps (Asha and Rhen snap in tamsule_bell_galleries, coilspire and drowned_choir; hero-motion);
  - test_qa_capsules (ossa_fen shows Pell as a capsule; Pell is not modelled yet).
- gdlint and gdformat clean; validate_data 0 errors; dlgc --check clean.
- Shots self-rendered and viewed (see the SELF-RENDERED lines above).
Expected baseline moves at the Lead's gate: field_tip_card (the card sits lower), and the four new field_hud_over_* shots.
Skipped: coverage (no game/battle or game/progression change).
- 2026-10-28 10:40, **the Lead's big14 list and 09:35 item 1:**
  - **big14 gate merged** (7b5fe9304). The UI items:
    1. **test_creature_portraits:** the six Act II creatures were baked, plain and held, with PROVENANCE rows (bff8f1388). I viewed the contact sheet.
    2. **test_title_reveal and test_battle_result_motion:** these pass on the merged tree. The gate's shots.json had boot_title at settle_frames 10 and had dropped battle_victory's 90. Claude/ui keeps 72 and 90, and **the integration merge must keep them too**.
    3. **test_zone_map_pois:** every Ch4 wake POI already sat on its source. The wake now draws Haluna's shapes, so the test looked in the wrong layout. The entry now names its own layout in `points` (dd52da357).
    4. **test_field_audio:** the outfitter's hook is no longer pending (574aed47b). Its watch expressions were checked against the class first.
  - **Portraits:**
    - Toma, Kerrid, Moll and the net-mender were rebaked for characters' short-hair and beard look-dev (M2-CHR-524, eb78f07e9). I viewed them before and after.
    - Liss was rebaked for her softer fringe (296ceb696).
  - **Scene-change hitches (ADR 0111, 5702d5d3a; proposed, for the Systems Architect and hero-motion to accept):**
    - **Cause.** The hidden 1.3–3 s frames were mostly `HeroFieldActor.attach` reading the hero scenes from disk on the main thread, inside the swap frame. Measured headless (no renderer): 1.6–2.6 s, against 6–15 ms once cached. FieldHud.attach is 15–19 ms.
    - **Fix.** SceneRouter emits `change_started`. `ResidentLoads` threaded-loads the field bodies and the party's battle actors there, holds the swap until they are in, and keeps them. The title starts them as it shows.
    - **Headless, cloud box:** Ch1 1911 → 251 ms, Haluna 3386 → 964 ms.
    - **Left for others:**
      - Haluna's own build, haluna_zone.gd plus the Dresser, at about 0.9 s each: first-playable and env-art.
      - The first fight's arena and creature loads (not measured).
    - **The PC's next walk is the real measurement.**
  - **Housekeeping, for the Lead:** every `godot --import` regenerates about 500 `.import` files: `valid=false` for the LFS audio not fetched here, and new ones for docs/kb/qa/gate-runs images. I revert them each time. A `.gdignore` in docs/ would stop the second set.
MERGE-READY @ 5702d5d3a: the big14 UI fixes, the portrait rebakes and ADR 0111.
Checks:
- **Full suite at eb78f07e9:** 3168 run, 11 failed. None is this track's, and all appear in the gate's list:
  - act1 ability VFX, Liss's battle tint, hero snaps, villager routines, cutscene walks, fp_prologue Liss, capsules, save shrines;
  - Godot aborted at exit after reporting, the same segfault at exit as the gate.
- **5702d5d3a only adds ResidentLoads.** Its own tests, plus scene_router, title and boot, are 0 failed.
- **Tools suite:** 175 units, 5 failing units: audio_loudness (LFS audio not fetched), arenas, pemakar_kit, zone_dressing_ch01, and test_screenshots.
  - test_screenshots fails because 168 manifest shots have no baseline. Baselines are the Lead's gate.
- validate_data has 0 errors, dlgc is clean, taskboard --check passed, and lint is clean.
Skipped:
- The coverage step: no game/battle or game/progression change.
- Screenshots: no changed shots this batch. The portraits were viewed directly.
- 2026-10-28 11:20: **Ivo Brannick** (M3-CHR-540) and the Stillguard's short-hair rebuild landed on characters. Merged at 7ea66428f.
  - **Portraits (81301ec34):**
    - Ivo is baked. His stage has no face-pose table, so it is neutral only.
    - The Stillguard is rebaked; it is nearly unchanged under the helmet.
    - I viewed both against the old Stillguard.
  - **Checks:** test_hero_portraits 9/0 and test_dialogue_box 26/0; validate_data has 0 errors.
  - **Still missing:** Pell is the last named Act I speaker without a model.
  - **Merge note:** the merge kept shots.json's boot_title at 72 and battle_victory at 90.
MERGE-READY @ 81301ec34: Ivo's portrait and the Stillguard rebake, on top of MERGE-READY @ 5702d5d3a.
- 2026-10-28 12:40, **the Lead's 11:46 list: loading and the ui-menus rows in act1_gpu_qa.md** (the file is on gpu/act1-qa-2, so the answers are here, for the PC to copy into its rows):
  - **Coverage.** Every game scene change already goes through SceneRouter's opaque fade; only the debug swap probe changes scene directly. What froze was the frame inside the fade.
  - **Row 22 (New Game, Ch1, Ch2, first fight), row 41 (entries up to 4.3 s) and row 42 (Ch5's 6.2 s hidden frame) — FIX PUSHED, needs the PC's walk.** ADR 0111 plus its amendment (5702d5d3a, e65e18653, 045348c44):
    - **What fills the frame.** Profiled headless, most of the swap frame is runtime `load()`s on the main thread: the hero bodies, the zone's villagers (ZoneCast) and its kit pieces and materials (ZoneKitDressing).
    - **What ResidentLoads does.** It loads them on worker threads behind the fade (two at a time), and holds the swap until they are in:
      - the heroes, kept for the session;
      - the zone's generated list, `game/data/ui/scene_loads.json`, from `tools/loading/scene_loads.gd`;
      - for a battle, its arena and its enemies' actors.
    - **Headless worst hidden frame:** Ch1 1671 → 291 ms, Pemakar 7624 → 1128 ms (it reached the router's 120-frame hold cap), Corrow 7571 → 318 ms.
    - **Left for other tracks:**
      - Coilspire's dressing build (about 1.7 s of CPU): env-art-b and act1-chapters.
      - Haluna's zone build and dresser (about 0.9 s each): first-playable and env-art.
      - Possibly a progress-based hold cap: Systems Architect (ADR 0111 amendment).
    - **Row 42's 61.6 ms visible frame after the fade** isn't reproducible without the GPU. It may be the last of Pemakar's loads landing after the hold cap; the next walk will tell.
  - **Row 33 (BattleResultPanel._set_count casting a freed object, 506 times) — FIXED (503b99839).**
    - Cause: a result shown again, or left, while it still counted kept its tween writing into freed rows.
    - Fix: show_result kills the last open's tween, and _set_count and is_counting skip a freed row.
    - test_battle_result_motion reproduces the exact error without the fix and passes with it (5/0).
MERGE-READY @ 045348c44: ADR 0111's zone and battle loads, and the row 33 fix.
Checks:
- resident_loads 7/0, battle_result_motion 5/0, scene_router 15/0, boot 27/0, title 40/0 (3 nodes left in the tree, which predates this change).
- validate_data has 0 errors; lint and format are clean.
Skipped:
- Screenshots: nothing visual changed. Loading is behind the opaque fade, and the result panel's look is unchanged.
- A full suite: ResidentLoads is off in headless runs unless a test opts in, so the suite would not exercise it.
**The PC's next walk on this head is the real measurement.**
- 2026-10-28 12:15, **for big15:** rows 22 and 33 are both pushed on origin/claude/ui at 9190b833c.
  - **Row 22:** the loads already run behind SceneRouter's opaque fade and its ShaderPrewarm stage. ADR 0111 adds the threaded loads behind that fade: the hero bodies (resident), each zone's own runtime loads (scene_loads.json) and a battle's arena and enemies. The router holds the swap until they are in.
  - **Row 33:** the result panel's freed-row count-up is fixed (503b99839).
  - **MERGE-READY @ 045348c44**, as posted above. The PC's next walk on it is the measurement for row 22.
- 2026-10-28 14:05, **the Lead's 13:25 list:**
  - **M3-NAR-01 (this track holds the narrative seat), now in review:**
    - **Reviewed all 26 Act I entries and both records** against the voice guide, the bible and the glossary: 2–4 sentences, sincere, nothing past each entry's flag, no Act II or III terms. Neme's mixed metaphor is fixed.
    - **Added** (e83b13513): The Calm (`ch02_met_asha`), The Cantors (`ch03_ilun_bound`), The Ebbing (`ch09_ebbing_danced`; the Order's teaching only) and Inquisitor Hadric Moll (`ch06_inquisitor_yielded`).
    - **Placed both records** (a9bb4fd27):
      - `causeway_notice` is an Examine trigger on the causeway's first marker post, from the causeway generator.
      - `basin_steps` is on the shrine's first step inside the entrance, built with the new CodexRecordSpot.
    - Pell's entry is unchanged and keeps to what Rhen sees at Corrow. That is the canon characters asked about.
  - **Pemakar's load, still over 1 s: fixed. Coilspire is fixed too.**
    - **Pemakar** (662935b3a): past the 120-frame cap, a held swap now waits while its holders make progress (ResidentLoads counts finished loads). It still stops on a 30-frame stall or at the 900-frame cap. Its worst hidden frame went 1128 → 585 ms.
    - **Coilspire** (b82f36b6a): 1.4 s of its frame was ZoneKitDressing clipping every trimesh triangle against every lod0 box. A triangle clear of a box now skips the cut, with the same surface (tested by area). Its worst hidden frame went 1920 → 582 ms.
    - **Headless, cloud box, the worst hidden frame now:** Ch1 257 ms, Pemakar 585 ms, Corrow 318 ms, Coilspire 582 ms.
SELF-RENDERED @ b82f36b6a: field_menu_codex. What I saw:
- World reads "4 of 12" (The Calm unlocks with Haluna), and the total reads "10 of 54".
- Places and Records are unchanged; the text is clean.
- **The baseline will move** for the World count.
MERGE-READY @ b82f36b6a: M3-NAR-01, plus the Pemakar and Coilspire load fixes.
Checks:
- codex 15/0, shell_shrine 15/0, causeway 16/0, zone_kit_dressing 10/0, scene_router 16/0, resident_loads 7/0, boot 27/0.
- The causeway generator's --check is up to date. The Python causeway, codex and loc tests are OK.
- validate_data has 0 errors, taskboard --check passed, the banned scan is clean, and lint is clean.
Skipped: the full suite. The swap wait only differs past 120 held frames, and no test holds a swap that long.
LEAD-ANSWERED (13:46, approved; the Cantors' last line stays; task marked done): M3-NAR-01 is in review with no narrative reviewer. Will you, or Cinematics, review the four new entries' voice (the Calm, the Cantors, the Ebbing, Moll)? This matters most for the Cantors' last line: "Her village holds her funeral before she leaves, and no one says why."
LEAD-ANSWERED (13:46, ADR 0111 accepted; integration-qa and act1-chapters notified): ADR 0111 touches the Systems Architect's SceneRouter (change_started and the progress-based swap wait) and act1-chapters' ZoneKitDressing (the clip quick-reject). Please route them for acceptance.
- 2026-10-28 15:10, **Act I loads still over 1 s? Every Act I zone and battle was measured**, headless on the cloud box (about 1.8× slower than the PC), through SceneRouter with ADR 0111 on:
  - **Zones (worst hidden frame):** prologue 101 ms, Oruvel 135, Underway 234, causeway 127, shrine 112, ferry 134, wake 207, Ashcrown 146, Pemakar 615, Brine Shoals 190, Tamsule 201, Bell Galleries 164, Coilspire 741, Corrow 397, Corrow night 277.
    - **Haluna is 935–1085 ms.** With everything preloaded, what remains is its own build: the dresser 586 ms, Asha's stage pose 224 ms and the zone 222 ms. On the PC that should be about 0.6 s. **For the PC's walk to confirm**; if it is over, it belongs to first-playable and env-art.
  - **Battles:**
    - **The first battle was 1845 ms**, because 1.4 s of stage.spawn loaded Rhen's battle actor on the main thread.
      - Cause: the swap's stall window was 30 frames, which is milliseconds under the uncapped fade, and a model's threaded progress reads 0 until it is in.
      - Fix (fe0bcc367, "the held swap's stall and cap are wall time"): the wait now runs while some load finished within 3 s, capped at 15 s.
      - Now: 160 ms.
    - **Later battles:** 120–215 ms.
  - **Gotcha:** Godot exits with "double free or corruption" after a scripted run that ends mid-battle, with ResidentLoads off or on. It is the same abort at exit the gate and the full suite show; it is not this change.
SELF-RENDERED @ 068218034: field_hud_over_pemakar (night), field_hud_over_ashcrown (bright ash sky), field_hud_over_brine_shoals (grey flats, bright), field_hud_over_coilspire (dusk), field_hud_over_haluna_wake (night). What I saw:
- All four overlays read on every backdrop: the objective line, the area title band, the Listen keycap and the tip card. The cue's outlined "Far" and "A short walk" read over night and over the steps.
- No contrast fixes were needed this round.
- The Brine Shoals and Coilspire shots show the idle line, because their one flag starts no errand. That is shot setup, not a bug.
MERGE-READY @ 068218034: the first-battle and Haluna load measurements, and the second field HUD pass. Checks: scene_router 16/0, resident_loads 7/0; the shots were viewed; nothing visual changed in game code.
- 2026-10-28 17:45, **big15's two scene-router failures** (test_swap_frame_stays_under_threshold_for_every_target, test_launch_reveals_the_title_only_after_the_warm_up):
  - **Not ADR 0111's.** None of its code is in lead/gate-big15: 5702d5d3a, 662935b3a and fe0bcc367 first appear in big16.
  - **Both pass here,** in worktrees on lead/gate-big15 (15/0) and on lead/gate-big16 @ ff82858c (16/0), and on big16 with every core loaded (16/0). They run the real swap in a child Godot on an injected clock, so a full-suite-only failure points at the child (a crash, a timeout, or no stats printed) or at shared user:// state, not at the router's bookkeeping.
  - **One latent issue found and fixed anyway (84bbd575a, ADR 0111 amendment 2).** Past the 120-frame cap the swap wait followed every holder's wait_progress(). ShaderPrewarm's counts frames, so a prewarm staging past 120 frames (a slow box, real cards) could hold a swap to the 15 s cap and bust the 3 s entry check: exactly test 1's check. Only ResidentLoads' swap_wait_progress() extends the wait now. New test: test_only_loading_holders_extend_the_swap_wait. scene_router 17/0, resident_loads 7/0.
MERGE-READY @ 84bbd575a: the swap-wait fix for big16.
LEAD-ANSWERED (17:25: the runner prints FAILURE lines only in its end summary, and big15's isn't out yet; the Lead will paste them. The box was cloud lavapipe on 4 CPUs with two capture shards beside it, so load timing is likely. The surrounding swap checks pass. **Not reproduced on big15 or big16, in isolation or under load.** 84bbd575a stays: it fixes a real latent wait, documented in ADR 0111 amendment 2, and changes no test expectation): Please paste the two tests' FAILURE lines from big15's cloud suite, or the gate log path. I can't reproduce either one in isolation or under load on big15 or big16, and the message decides whether it's the child probe (crash or timeout) or the entry budget that 84bbd575a covers.
- 2026-10-28 17:50: **big15 router failures are LEAD-ANSWERED.** The causes were "printed no stats (exit 127)" for boot.tscn, battle_sandbox.tscn and launch: the cloud runner could not find the child probe's Godot binary. That is the environment, not the router. Run alone the test passed 15/0, and no logic was changed.
  - **Optional hardening done:** test_scene_router_swap's probe helper now fails with "the Godot binary was not found (exit 127, <path>); not a budget failure", so it cannot pass for a budget failure. scene_router_swap 17/0.

## FROM 2026-10-29 (Lead session_01Bg3iP7cPGyjbX4CyniBahc, integration claude/new-session-mj8c3c; the PC is offline)
- 2026-10-29: **merged** origin/claude/new-session-mj8c3c (600e05af; pc-gpu.md took the integration side) and origin/claude/characters (92566b71: Pell, M3-CHR-506; PROVENANCE and shots.json by merge_union; shots.json keeps boot_title 72 and battle_victory 90).
- **Work item 2, portraits: Pell baked** (fa8ab442): five emotions, framed closer (`camera` distance 0.86, aim_drop 0.05) so his head matches the humans' size with the crest in frame. Viewed as a contact sheet against Rhen, Kerrid and Tavi. His emotions differ only slightly at 256 px; that is the face-pose table (characters' call), not the bake. Every named Act I speaker now has a portrait (test_dialogue_box's guard). Pell joins the party only in Ch10 (flags.tres), so no Act I menu needs him.
- **Work item 1, every Act I scene change covered and under 1 s hidden (ADR 0042 §4; ADR 0111 amendment 3):**
  - SceneRouter records the fade's alpha on the swap frame and each hidden frame (`judge_cover`: `covered`, `cover_alpha_min`) and warns when one is not opaque (0bc329a6).
  - test_scene_change_cover: no game script outside the router and the debug probes changes scene directly; no CanvasLayer in a .tscn or a data table sits at or above the fade's layer 128. test_scene_router_swap: the probe's real changes report `covered`.
  - **Haluna fix (b7b1b53f):** tools/loading/scene_loads.gd collected each zone in the frame it entered, before VillagerLayer's deferred build, so Reed, the child, Neme and Osu (about 1 s) loaded inside the swap frame. It now lets each zone settle 3 frames; the regenerated lists add 89 paths. test_resident_loads::test_each_zone_s_villager_actors_are_listed fails on the old list. Haluna's worst hidden frame: 1245 → 453 ms.
  - **tools/loading/act1_swap_sweep.py** runs the probe per Act I zone, the title and the battle sandbox, with ResidentLoads on and the hero bodies warm (`--resident-loads --warm-resident`, as after the title); exit 1 on an uncovered change.
  - **Sweep at ec6be9da (headless, cloud box, about 1.8× slower than the PC): all 18 covered; worst hidden frame per target:** Oruvel 180, Underway 309, Haluna 453, causeway 149, shrine 142, ferry 247, wake 491, Ashcrown 168, **Pemakar 733**, Brine Shoals 222, Tamsule 287, Bell Galleries 227, Coilspire 475, Corrow 376, Corrow night 321, prologue 105, title 21, battle 130 ms. Worst visible frame 35 ms (Pemakar). Entries 0.4–3.9 s; Haluna (3.7 s) and the wake (3.9 s) are over ADR 0029's 3 s entry on this box, all under the fade.
  - Pemakar's remaining 0.6 s is spread over many small dressing nodes (no single culprit; profiled).
- **Work item 3, inventory rows:** `placeholder_audit.py --static-only` lists nothing for ui-menus. M3-HER-1147 and M3-UI-101 are set to review (both were done on 10-28).
- **M3-NAR-1000 (narrative seat), to review** (f5a1a17c): decisions_log N-27. Pell's echo check passes with no beat changes and four authoring guards; every Kerrid and Pell sheet question answered (story sheets' new sections); ADR 0020 append note; glossary superseding rows.
LEAD-ANSWERED (18:22, ADR 0201: SPEC v1.5 and pell.md reworded, the term banned): SPEC §3's roster row called Pell's niche by the series' job word, the inspiring series' own job word (also in ADR 0017 and pell.md's header). Reword SPEC to "learns enemy abilities by listening" (N-27 guard 3), and ban the term?
- **Known, not this track's:** test_qa_capsules fails (Haluna villagers and ossa_fen's Pell as capsules, ten foes without bodies): characters, creatures and integration-qa.

### PC-QUEUE
- **Act I scene-change hitches on the RX 9070 XT** (act1_gpu_qa rows 22, 41, 42): re-walk New Game→Prologue, Ch1, Ch2, the first fight, every Act I zone entry and Ch5's fresh entry on this head. Expect every hidden frame under 1 s (cloud headless worst 733 ms) and no visible frame over 50 ms. Then close or update the rows. Quick per-zone numbers: `python3 tools/loading/act1_swap_sweep.py` (headless; the walk is the budget-grade measurement).
- **Row 33** (the result panel's freed-row count-up, fixed 503b99839): confirm no `_set_count` SCRIPT ERROR in a pass.

MERGE-READY @ bcfb63160: Pell's portraits; the scene-change cover record, guards and Act I sweep; Haluna's villager loads; M3-NAR-1000; M3-HER-1147 and M3-UI-101 to review. Checks: hero/creature/battle portraits 16/0, dialogue_box 26/0, scene_change_cover 4/0, scene_router_swap 17/0, resident_loads 8/0; tools test_act1_swap_sweep OK; gdlint and gdformat clean; validate_data 0 errors; taskboard --check passed; banned-terms scan of the new text clean. Skipped: screenshots (no shot changed: portraits viewed directly, the cover record is invisible); coverage (no game/battle or game/progression change); the full tools suite (only the new tools test can see tools/loading).
- 2026-10-29 (superseded by the Lead's 18:22 list below) **BACKLOG EMPTY:** items 1–3 are done and merge-ready. Item 1's budget-grade numbers wait on the PC (PC-QUEUE). Item 2 waits on characters landing new Act I speakers: every named Act I speaker is baked. Item 3: the audit lists nothing for ui-menus. No ui `todo` tasks are left, and the narrative `todo`s are Act II or wait on other tasks. Handoff: docs/kb/handoffs/2026-10-29-ui-ui-menus-1.md.
- 2026-10-29 19:40, **the Lead's 18:22 list:**
  - **Merged** claude/new-session-mj8c3c (ADR 0201). N-27 no longer quotes the banned job word (validate_data is clean).
  - **Row 33, FIXED twice over** (c0e98a59): the result panel kills its count's tween in NOTIFICATION_PREDELETE. A bound
    tween only notices a freed node on the tree's next step, and stepped into freed rows until then.
    test_battle_result_motion::test_freeing_the_panel_mid_count_ends_the_count frees the panel mid-count (6/0).
  - **Row 42 (Ch5 fresh entry), headless:**
    - Pemakar's swap frame, fresh launch with ResidentLoads: 700–780 ms with a warm disk cache, 1.8–2.4 s cold (just
      after the container restarted).
    - The cold excess is not in any node's _ready, any load (every one under 20 ms) or the Ch5 arrival steps; the
      synchronous cutscene cues add about 215 ms (Rhen's `look_at` is 211 ms of it).
    - The visible spike is on the fade's last lift frame: 24–39 ms headless, under 50 ms, with no node added. The PC's
      61.6 ms came with the pre-ADR 0111 6.2 s hidden frame (loads landing late). PC-QUEUE below.
  - **Rows 22/41, field battles:** the probe takes `--encounter=<id>` (a real BattleRequest), and the sweep covers all
    31 Act I encounters (625dabd1).
    - All covered; worst hidden frame 266 ms (ch03_causeway_shore), most 115–240 ms; entries 0.56–1.5 s.
    - Run alone, the worst visible frame is 10–18 ms (the 160–277 ms in the first sweep were CPU contention with the
      playthrough tests).
    - Coilspire is 475–634 ms headless.
  - **The headless UI error sweep** (the Act I playthrough tests fp_ and ch01, ch04–ch09 _thread, plus the UI areas:
    menu 251, hud 76, dialogue 85, field_ 132, battle_ 737, codex, bestiary, title): **no SCRIPT ERROR anywhere.**
    - Every push_error in the UI areas is a test exercising an error path on purpose.
    - Not UI, for their owners:
      - rendering: `refresh_bounce_passes` called deferred with a freed node (underwater_rig.gd:401), 2–12 times a run;
      - battle-presentation: battle_vfx.gd:249/299 and battle_boss_vfx.gd:380 read get_global_transform off the tree;
      - cinematics: "@vfx rate=/drift=/motion=/form=" and "@camera grade=" are not performed yet (Ch1–Ch9 cutscenes).
    - Fixed while there: **Liss's battle tint** (c2d3a9b71): integration-qa's row set #7A8C5A, but the spec
      (M3-HER-1120) and test_battle_party_stand_ins say #7A8F6A. That was a big14 gate failure (3/0 now).
    - Other failures seen, not this track's: test_battle_act1_ability_vfx (battle-presentation), test_hero_field_snaps
      (hero-motion), fp_prologue's Liss vigil (characters).
### PC-QUEUE (added 19:40)
- **Row 42:** a fresh F8 Ch5 start on this head: the hidden frame (headless 0.7–2.4 s) and the visible frame at the lift's
  end (headless 24–39 ms). If it is still over 50 ms on the GPU, it is a draw-side cost (the cutscene's first camera or
  UI material) that headless can't see.
- **Row 41's field battles:** a walk of a few Act I field battles; headless they are 115–266 ms hidden, 10–18 ms visible.
MERGE-READY @ c2d3a9b71: rows 33 and 42 (diagnosis), the field-battle sweep, the UI error sweep, and Liss's tint. Checks:
battle_result_motion 6/0, battle_rewards 10/0, party_stand_ins 3/0, the UI areas above, and the Act I thread tests (fp_
29/1 = the Liss vigil, characters'). tools test_act1_swap_sweep OK. Lint, format and validate_data are clean.
Skipped: screenshots (nothing visual changed: a tint value matching the spec, and the panel's teardown) and coverage (no
game/battle core or game/progression change).
- 2026-10-29 19:40, **BACKLOG EMPTY:** the Lead's 18:22 list is done. What's left needs the PC (PC-QUEUE) or other
  tracks' fixes, listed above.
