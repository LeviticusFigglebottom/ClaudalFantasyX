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
- 2026-10-29 19:40 (superseded by the Lead's 19:24 list below) **BACKLOG EMPTY:** the Lead's 18:22 list is done. What's left needs the PC (PC-QUEUE) or other
  tracks' fixes, listed above.
- 2026-10-29 21:30, **the Lead's 19:24 list:**
  - **Underwater rig, at the Lead's request (rendering's file, `game/world/water/underwater/underwater_rig.gd`; no
    rendering track is running)** (ce8c1683): the lantern's bounce-pass refresh is deferred through the rig itself, so a
    rig or scene freed before the flush drops the call; it no longer hands a freed root to
    CharacterShaderTiers.refresh_bounce_passes. test_underwater::test_the_lantern_s_bounce_refresh_is_bound_to_the_rig
    (9/0). The Ch1 playthrough no longer prints the error.
  - **UI final-quality pass, Act I:**
    - **4:3 added** to the aspect audit (1440x1080 and 1024x768, laid out at 1920x1440), next to 16:9, 16:10, 21:9 and
      43:18, at 100 % and 130 % text (2dd514a4).
    - **No default Godot theme:** the aspect audit now fails on any visible Control drawing a stylebox, font or icon from
      Godot's built-in theme. None does (the only hits were Label focus styles, which never draw).
    - **No placeholder icons:** the menus' icons are drawn glyphs, and test_menu_glyphs already gives every item,
      equipment piece and skill one. No icon.svg or placeholder texture anywhere in game/ui.
    - **No focus dead ends** (35a18896): test_input_parity_dead_ends opens every field menu page with the keyboard and
      the pad, goes three Confirms deep, and Cancel always walks out until the menu closes with nothing left showing.
      Every page already has its own device-parity test (the codex through its action test).
    - **Text** (b2137061, e40234da): the pseudo-locale walk (+40 % length) passes, but with English strings at 130 % text
      it showed real trims:
      - the Customize header at 100 % ("Customize Coral-Bitten Hooks");
      - Equip's "Magic Defense" stat name;
      - the Reefball HUD's names, bands, counts and tags;
      - the battle help line on a Vowbound's call;
      - the shop and inn description and status lines;
      - two settings help lines.
      Fixes:
      - **HudLayout.fit_label and fit_lines** shrink a label's font to 80 % at the least before it ellipsizes;
      - MenuPage headers fit their row and are indented on the left only (488 px instead of 460);
      - Equip's stat-name column is 234 px;
      - the Reefball outfitter panel is 1400 px wide;
      - the shop's description has 165 px and its status 120 px;
      - the not-enough-lume line is shorter ("Not enough lume: 120 lume needed, 100 lume in hand.");
      - the Reefball Read panel's read line takes what the rows leave, so the panel no longer runs 80 px into the drop
        panel at 130 %.
      An English walk now trims nothing.
    - **Fixed while there:** the backlog parity test leaked its layer (3b792de6).
SELF-RENDERED (at e40234da's parent, before the text fixes; a temporary manifest, never committed): 17 Act I screens at
2560x1440, 1440x1080 (4:3) and 2560x1080 (21:9):
- boot_title, field_menu, equip, lattice, items, status, formation, codex, bestiary, map (Haluna), save, settings hub,
  shop buy, dialogue_continue, battle_hud_preview, battle_victory and battle_pause.
- All read. The frame is centred at every aspect; at 4:3 it sits in the middle with room above and below, as `expand`
  gives.
- The only oddity: the victory shot's sandbox greybox floor shows its edge at 21:9. That set is the battle sandbox's
  own, not an Act I arena.
- No baselines written. Baselines that will move: equip_menu (stat columns), shop_menu_buy (the shorter line), and any
  page whose title used to ellipsize.
MERGE-READY @ e562b48d1: the underwater rig fix (rendering's file, at the Lead's request) and the Act I UI final-quality pass
(4:3 in the aspect audit, the default-theme check, the dead-end test, English text fits at 100 % and 130 %).
Checks:
- aspect_layouts 18/0, pseudo_loc 26/0, menu 251/0, input_parity 65/0 (no node left), shop 28/0, reefball 80/0,
  equip 66/0, settings 48/0, underwater 9/0;
- battle_ 737/1: only test_battle_act1_ability_vfx (battle-presentation's, routed by the Lead);
- an English text walk trims nothing;
- lint and validate_data are clean.
Skipped: coverage (no game/battle core or game/progression change; game/ui/battle is the scene layer). I did not
re-render all 51 views after the text fixes; the five shots they touch are self-rendered below.
- 2026-10-29 21:40 (superseded by the Lead's 23:10 list below) **BACKLOG EMPTY:** the Lead's 19:24 list is done. What's left waits on the PC (PC-QUEUE) or on other
  tracks' routed findings.
SELF-RENDERED @ d7840ba0 (1280x720): equip_menu, equip_customize, shop_menu_buy, shop_menu_sell, inn_menu. What I saw:
- the Customize header reads whole ("Customize Coral-Bitten Hooks");
- Equip's stat columns line up with the wider names;
- the shop's shorter lume line wraps cleanly onto two lines;
- sell and inn are unchanged.
Baselines will move for equip_menu, equip_customize and shop_menu_buy.
- 2026-10-30 00:30, **the Lead's 23:10 list: the Act I narrative and onboarding seat.** Audited on lead/gate-big18 @ d00d3284 (a
  scratch worktree); the fixes are on claude/ui, which has claude/new-session-mj8c3c merged in (dae73fd8).
  1. **Codex, bestiary and item/skill/status text:** a scripted audit of every *_key in the codex, the 25 Act I foes'
     names and bestiary lore, the skills, statuses, items, equipment, gear types, abilities and Vowbound. Every key
     exists, is final text and is not its own id. Every codex unlock flag is declared in flags.tres and set by the
     story. There is no separate in-game glossary: the codex is it.
     - **Fixed:** statuses had names but no player-facing description (only the engine's notes, "x0.2").
       STATUS_<ID>_DESC is now written for all 21, and the Status page explains each carried status under its name
       (test_status_menu::test_every_status_has_a_description). Self-rendered status_menu: "Poison", then "Loses a
       tenth of their health at the end of each of their turns."
  2. **Tutorials and first-time prompts:**
     - field tips: objective, field menu, save shrine, shop, menu save;
     - battle prompts: commands (Ch1), items, escape, the timeline (tideline, Hullgnaw), Swap and Read (Ch4 hermit),
       armour break, fliers, the set pieces.
     Each shows once: the tips per save, the prompts in their one scripted fight, with a retry repeating its line.
     The tips name the bindings of the device in use; the prompts name none.
     - **Fixed: nothing taught Swell or the Vowbound** (c4ef3370):
       - a Swell tip (the gauge, techniques, the field menu's fill modes) follows the menu-save tip;
       - Asha's first turn in Ch4's first fight (ch04_sail_leeches; the call only needs ch03_ilun_bound) prompts the
         call. encounters.json is combat's table; one row gains turn_prompt fields, as Ch4's hermit has.
       test_tutorial_tips::test_the_swell_tip_follows_the_menu_tips. The tip test no longer leaves a card in the tree.
     - **Dismissal:** the tips never take input. Each fades after its reading time, hides while a menu is open, and
       the Accessibility page turns them off. I did not add a dismiss key: it would take a binding from the field.
       The Lead can overrule.
  3. **Save and load at every Act I save point:** test_qa_save_shrines (every shrine and rest point: zone, party,
     flags, respawn) passes. **Added test_save_music:** every Act I zone has music, and a save round trip, with each
     variant flag set, picks the same cue (eeb20c31).
  4. **Banned terms and tone:** validate_data's banned scan is clean.
     - Grepped every Act I line for meta, game-speak and slang. Three hits, all in-world: a Reefball "player", "one
       joke", and "cool" as temperature.
     - Read every grief or sad line followed by a smile or laugh within two lines: Osu's grandfather, the first
       verse, Neme, the wake vendor. All tender; none undercuts.
     - Ch2's "he's allowed one joke" comes before Rhen learns Oruvel is gone, and the scene then turns to grief.
     - **Fixed** (52ca86c1): the Ch8 net-mender bark shipped "Old Net-Mender [neutral]: ..." as its text. dlgc read
       the hyphenated name as narration. The speaker is now Netmender (CHAR_NETMENDER is "Old Net-Mender"), and dlgc's
       speaker-like check takes hyphenated and apostrophe-joined names (test_dlgc).
LEAD-ANSWERED (23:52, ADR 0202, SPEC v1.6: accepted as written): SPEC §6.8 names the statuses, and several are the series' own set: Shell, Protect, Reflect, Regen, Doom,
Zombie and the four Breaks (Armor, Mental, Power, Magic). Rename them in SPEC (like ADR 0201)? My proposal:
- Shell → Tide Ward, Protect → Bulwark, Reflect → Mirrorwater, Regen → Mending, Doom → Last Tide, Zombie → Hollowed;
- Armor/Mental/Power/Magic Break → Sundered, Unmoored, Weakened, Dimmed.
Poison, Sleep, Silence, Darkness, Petrify, Slow, Haste, Stop, Berserk, Confuse and Provoke are generic. Until you
answer, nothing is renamed: the names are SPEC's.
MERGE-READY @ 1d1bf96e7: the Act I narrative and onboarding pass (status descriptions, the Swell tip and Vowbound
prompt, the save-music test, the net-mender bark and dlgc's check).
Checks: status_menu 6/0, tutorial_tips 5/0, save_music 1/0, qa_save_shrines 2/0, boss_hud 4/0, aspect 18/0,
pseudo_loc 26/0, input_parity_glyphs 7/0, field_hud_legibility 3/0; tools test_dlgc and the corpus test (131) OK;
dlgc --check clean; validate_data has 0 errors; the text audit shows 0 problems.
Not this track's: test_ch04_zones::test_the_wakes_field_camera_is_halunas (Haluna's camera volumes).
Skipped: coverage (no game/battle core change).
- 2026-10-30 00:30 (superseded by the 23:52 answer below) **BACKLOG EMPTY:** the 23:10 list is done and clean. The LEAD-ASK on the SPEC status names is open,
  with nothing renamed until you answer.
- 2026-10-30 02:30, **the Lead's 23:52 answer: ADR 0202 applied** (dc257d86; claude/new-session-mj8c3c merged in).
  - **Every player-facing string renamed:** Tide Ward, Bulwark, Mirrorwater, Mending, Last Tide, Hollowed, Sundered,
    Unmoored, Weakened, Dimmed. That covers the ten STATUS_ names, three ability descriptions and the battle help and
    float lines.
    - No .dlg, codex text or tip named one.
    - The internal ids are unchanged.
    - "Shell" stays in the Shell Shrine, Shell Breaker, Shell Ram, Shell Wall and Bell-Shell, and lowercase "shell"
      stays in prose.
  - **banned_terms.txt** gains i:armor break, i:mental break, i:power break and i:magic break. The comments, data notes
    and story docs that used them now say sundering blow, Sundered or Weakened. validate_data has 0 errors.
  - **tools/tests/test_status_names.py** fails on any loc value with an old name. Capitalized Shell, Protect, Reflect
    and Doom count, Regen and Zombie count in any case, and proper nouns are allowed. It fails on the old strings.
  - Status descriptions use no status names, so none changed.
SELF-RENDERED @ dc257d86: battle_statuses, battle_statuses_colorblind and status_menu.
- The help line reads "Mirrorwater turns it onto Rhen · provoked: must strike Lantern Eel".
- The status glyphs are drawn shapes and are unchanged; status_menu shows Poison (unchanged).
- battle_statuses' baseline moves.
- 2026-10-30 03:00, **my Act I menu audit at gameplay pace, controller only** (the no-idle rule):
  - **Fixed (8cb7f517):** a held d-pad or stick did not repeat. Godot echoes held keys but not pad buttons or axes, so a
    pad player tapped through every row of the 40-item bag or the 54-entry codex.
    - The UiInput autoload now repeats a held pad direction after 0.4 s, every 0.08 s (ui_input.json).
    - Each repeat is a press and release marked with device -8.
    - Whether the direction is still held is read from the pad, so nothing sticks.
  - **Fixed (d5b25b32):** with repeats, a held direction raced round a list. MenuPage.move no longer wraps on a held
    key or pad (pressed but not just pressed); a fresh press still wraps.
  - **Checked, fine:**
    - menus take input during their open and close fades (MenuMotion never gates it);
    - the dead-end test walks every page with the pad.
  - Tests: test_ui_input_repeat 4/0, input_parity 65/0, menu 252/0.
  - **Liss's battle tint:** the integration branch's test now expects big14's #7A8C5A, so my earlier #7A8F6A is
    reverted (50678c8a). party_stand_ins is 3/0.
MERGE-READY @ 638fb3cb5 (for big19): ADR 0202's status names, held pad directions repeating, and lists that stop at
their end while held; Liss's tint back to big14's row.
Checks:
- battle_ 757/0, menu 252/0, input_parity 65/0, status 55/0, pseudo_loc 26/0, ui_input 4/0, party_stand_ins 3/0;
- tools test_status_names OK (it fails on the old strings);
- validate_data has 0 errors; lint is clean.
Skipped: coverage. game/battle got comment edits only (the renamed Breaks), no code change.
- 2026-10-30 03:30, **BACKLOG EMPTY:** the 23:52 list and my controller-only menu pass are done. Real-hardware
  pace (pad feel, menu sound latency) is a PC-QUEUE item: a pad walk of every Act I menu on the PC, holding the
  d-pad and stick in the bag, the codex and the Lattice.
- 2026-10-30 04:30, **the Lead's 01:08 item: Act II preparation, docs only (ADR 0203).** No act1_gpu_qa row is open for
  this track except row 33, which is fixed twice (503b99839, c0e98a59) and waits on the PC's re-walk.
  The spec, all `draft: pre-gate`, is in `docs/kb/plan/act2/ui/`:
  - README (the index, what exists, the loc-key totals);
  - screens (the document reader, seven heroes, six callable Vowbound, Pell's Listen, Act II shops);
  - hud (rooted, drain, repair, the flat-engine part and tide pulse, the darkness fight, element cycling, buff strip,
    the set pieces, objectives);
  - tutorials (12 battle prompts, 4 field tips);
  - codex_bestiary (6 world, 8 people, 4 Vowbound, 5 records, 14 bestiary rows, the Listen marks);
  - portraits (14 speakers; Merel's wedding red; Kerrid's `guilty`);
  - heresy (dark Order shrines refuse, travel lists them greyed, Order shops refuse, the heretic subtitle and slot tag);
  - kerrid (a second codex body, `guilty` baked, one quiet Status line, nothing in battle).
  About 225 loc keys are listed, plus Narrative's record sentences.
  Decisions taken as defaults (the Lead can overrule):
  - a Vowbound codex category, with Act I's three moved in;
  - dark shrines visible on travel and the map, greyed;
  - the heretic subtitle on the field menu, never red.
- 2026-10-30 04:30, **BACKLOG EMPTY:** the 01:08 item is done. Act II work waits on the `act1-complete` tag (ADR 0203).
- 2026-10-30 06:10, **the Lead's ADR 0205 items: row 43, then Act II from the ui specs.**
  - **Row 43** (602dcb31): field_hud_over_haluna_wake frames the real Ch4 wake through act1-chapters' shot rig, not
    the dropped wake preview. Viewed.
  - **Hitches:** amendment 4 to ADR 0111 (5c662779: the zone feed into the prewarm, Ch5/Pemakar/Ch6/Ch8/Ch9/Corrow
    night) landed before ADR 0205 dropped the profiling. It is harmless and tested (test_prewarm_zone_feed); nothing
    more is planned there.
  - **Ch10 first (critical path):**
    - the codex's three Ch10 entries: farewell-tide, name-shells, the Eldest (5b0b50ad);
    - the rooted glyph and its words (9b598345; rooted sheet viewed);
    - the seven-heroes field tip on Ch10's first field (84cc875b).
  - **Heresy** (`ch14_declared_heretics`, declared):
    - Order shrines go dark: prompt, one-line bark, no rest, the light out (d47f352c);
    - Order shops refuse with a line (90b410fd);
    - the field menu's "Heretics of the Level" subtitle and the save slot's "· Heretics" tag (3aebef84);
    - dark shrines stay on the shrine road, greyed "Dark: the Order's shrine", and refuse the trip (f7fd954c);
    - the map's hollow flame and "{place} · Dark" (d184f37f).
    Zone authors mark the Order's shrines: `order = true` on the SaveShrine, `"order": true` on locations.json shrine
    rows and on zone_maps.json shrine POIs.
  - **Kerrid** (c656a68c): `guilty` is baked (viewed, PROVENANCE row). The Status page shows "Unrisen: held since the
    stair at Corrow" under his name once `ch15_kerrid_revealed` is set (declared; the reveal's script sets it). Viewed.
  - **Merge:** big19 is in (39f98a64). zone_cast.gd conflicted between my off-tree prebuild and creatures' `cast_still`.
    I kept both: `cast_still` now shapes the body in _ready, after the idle starts. test_zone_cast is 5/0, and its old
    fisher-idle failure is gone too.
  - **Self-renders, viewed, none committed** (temporary scenes only):
    - the heretic field menu;
    - Kerrid's Status page (the note first ran past its width; fit_label now gets the explicit width);
    - the shrine road with a dark row;
    - Haluna's map with its shrine marked for the render.
  - **Waits on other tracks:**
    - the seven-hero formation check and Pell's Listen (combat's Pell row and kit);
    - the rooted swap-refusal reason (combat M4-A2P-020);
    - Act II NPC portraits (models);
    - Kerrid's second codex body (narrative's text after the reveal script).
  - **Next:** the document reader (M4-A2P-080, Ch13), all ui-menus.
MERGE-READY @ 39f98a64: row 43; Act II Ch10 codex, the rooted glyph and the seven tip; the heresy UI (shrines, shops,
title and slot tag, shrine road, map); Kerrid's guilty portrait and Unrisen line; big19 merged.
Checks:
- codex 15/0, tutorial_tips 5/0, save_shrine 13/0, shrine_network 7/0, shrine_travel 9/0, shop_menu 13/0;
- save_slot 4/0, field_menu 36/0, status_menu 7/0, hero_portraits 10/0, zone_map 22/0, zone_cast 5/0;
- prewarm_zone_feed and pseudo_loc are green;
- validate_data 0/0, taskboard --check clean, lint and format clean.
Skipped:
- coverage (no game/battle or game/progression code changed);
- Blender (no Blender source touched);
- the full manifest (no committed shot changed).
- 2026-10-30 07:20, **the document reader (M4-A2P-080, Ch13), all ui-menus.**
  - **Commits:** b842d60e (the reader) and 2cb811fd (the codex hook).
  - **What it does:** DocumentReader lays a record's one to three panes side by side in the codex's frame. Each pane
    holds one mark. A "hand" is found when every one of its lines is marked; its lines then turn gold and a gold rule
    draws on across the gaps (at once under Reduced motion). The last hand sets the record's `flag`, and the line
    under the panes counts the hands left.
  - **Input:** keys, pad and mouse (hover, click to mark, the wheel, right-click Cancel).
  - **The codex:** a record entry with `"reader": "<records.json id>"` opens in the reader, single pane, and gets the
    input back when the reader closes.
  - **Data:** `game/data/lore/records.json` ships empty. Narrative writes the Archive's ledgers, the Cantor roll,
    Corran's line, Wenna's marks and Ama's keth (RECORD_<ID>_<NN> keys and the hands). The Ch13 scene calls
    `DocumentReader.open_in(host, DocumentReaderModel.new(DocumentReaderModel.row_of(&"<id>")))`.
  - **Shots:** the scenes document_reader_three and document_reader_one (a fixture record under
    `game/levels/_tests/document_reader/`) are viewed. They are **not in the manifest**, because test_screenshots
    wants a baseline for every row. **LEAD-ASK:** please add both rows with their baselines.
  - **Sounds:** a DocumentReader hook in ui_sfx.json on existing rows (the act1 audio audit asks every input-taking UI
    class for one). Request M4-AUD-1080 asks Audio for the found hand's own row.
  - **Next:** the Act II items still waiting on other tracks (the seven-hero formation check, Pell's Listen, the rooted
    refusal reason, Act II NPC portraits, Kerrid's second codex body).
MERGE-READY @ 0bc20a3b: the document reader (M4-A2P-080) and its codex hook, with the reader's sound hook.
Checks:
- document_reader 7/0, codex 16/0, pseudo_loc_screens 17/0 (both reader scenes at 100% and 130%, no warnings),
  screen_audio 11/0;
- act1_audio_audit OK, audio data_check OK;
- validate_data 0/0, taskboard --check clean, lint and format clean.
The tools suite (-j 4) has 5 failures that the integration branch carries too; this branch doesn't touch their paths:
- test_screenshots: `kerrid_front` has no baseline;
- test_asha: the LOD0 and part budgets;
- test_npc: crowd_elder_woman_a is too near reed_c, and the committed output is stale;
- test_palette_check: the chapel-court marble;
- test_villagers: Kell's sheet.
They are for characters, env-art and the Lead.
Skipped: coverage (no game/battle or game/progression code changed) and Blender (no Blender source touched).
- 2026-10-30 07:50, **BACKLOG EMPTY.** The Lead's ADR 0205 list is done for everything ui-menus can build today. That
  covers row 43, Ch10's codex entries, the rooted glyph and the seven tip, all of the heresy UI, Kerrid's guilty
  portrait and Unrisen line, and the document reader with its codex hook. I merged the Lead's 8de373e5 (shot
  approvals only). What remains waits on other tracks:
  - the seven-hero formation check and Pell's Listen: Pell has no row in characters.json yet (combat);
  - the rooted swap-refusal reason: the engine has no rooted status yet (combat, M4-A2P-020);
  - portraits for Act II's NPCs: no models yet (characters, M4-A2P-081);
  - Kerrid's second codex body (CODEX_KERRID_BODY_CH15): narrative's text after the reveal script;
  - the reader's records: narrative fills `game/data/lore/records.json`, and Audio has M4-AUD-1080;
  - the reader's two shots: the Lead adds them to the manifest with baselines (LEAD-ASK above).
- 2026-10-30 08:00, **the Lead's 04:27 answer on the reader's shots.** I added document_reader_three and document_reader_one
  to the manifest with `"pending_baseline": true`. The gate captures them after the next fast batch, and the Lead
  approves the baselines. Resolves the LEAD-ASK above.
  test_screenshots now fails only on the integration branch's existing `kerrid_front`, which has no baseline.
MERGE-READY @ HEAD of claude/ui (this commit): the document reader's shots as pending baselines.
- **BACKLOG EMPTY:** still true. What remains waits on combat (Pell's row, the rooted status), characters (Act II NPC
  models), narrative (records.json, Kerrid's Ch15 body) and audio (M4-AUD-1080).
- 2026-10-30 09:40, **the Lead's FAST-TRACK: act1_gpu_qa row 67** (big19's heavy entries over 2 s, and one Brine Shoals
  hang). Commit 329e7bce; ADR 0111 amendment 5 has the detail.
  - **The hang:** one fresh run printed nothing for 600 s, so the main thread froze. If the router had only been
    waiting, the probe's 2400-frame cap would have printed stats long before that.
    - The router started instantiating the zone on a worker thread while ResidentLoads' threaded loads were still in
      flight. GreyboxZone builds during instantiate, so the zone's own `load()` calls ran beside those loads, as did
      the main thread's (ZoneCast and VillagerLayer in _ready). That is the engine's deadlock-prone path.
    - **Fix:** the router now waits on its swap holders first, then instantiates.
    - Headless: no hang in 7 Brine Shoals runs or the full 49-target sweep (every target covered and printed stats).
      Instantiate fell to 21–56 ms per zone, because everything is cached.
  - **The cost, per zone:** big19's cast models were never listed in scene_loads.json. VillagerLayer adopts or
    replaces each cast body before the tool looks, so all of them loaded cold on the instantiate thread.
    - Brine Shoals: 12 unlisted (Moll, the clerk, three Stillguard, a child, two wright children, four reeds), plus
      big19's five slot materials.
    - Corrow: 11 unlisted (Ivo, Hobb, two Stillguard, the gatekeeper, four children, Marra, the officer), plus six slot
      materials and +173 dressing rows.
    - Tamsule (Ch7): 7 unlisted villagers, plus the gold leaf.
    - Coilspire (Ch8): the new copper and iron slots, and a reshuffled dressing.
    - **Fix:** the tool lists each `cast` row's model, and the registry is regenerated (Brine Shoals +158 paths,
      Corrow +164). `max_in_flight` goes from 2 to 4, so the loads keep the PC's cores busy now that the instantiate
      no longer overlaps them.
  - **Nothing filed to asset owners yet.** The excess is loading order and listing, not proven asset weight. If the
    PC's re-measure is still over 2 s after big20, I'll split it by zone and file the heavy ones (env-art-b for the
    Corrow and Brine Shoals dressing, characters for the villager count).
  - **Headless numbers:** this 4-core box's entries are 2.3–7 s whatever the order. The time is disk and CPU
    decoding, which the PC does several times faster, so they don't predict the 2 s bar. Only the PC can confirm.
  - **Checks:** scene_router 17/0, resident_loads 8/0, prewarm 26/0, shader_prewarm 22/0, creature_ 88/0,
    dialogue_box 26/0; act1_swap_sweep tests OK; validate_data 0/0; lint and format clean. The full sweep found all 49
    targets covered.

### PC-QUEUE (row 67, after big20)
- Re-run pass 4's hitch probes on big20, which carries amendment 4 and amendment 5:
  - Brine Shoals: the walk, and **fresh ×5** (the hang showed in 1 of 2);
  - Corrow, fresh;
  - Ch7 and Ch8, in the walk.
- Report the hidden ms per entry, and any run that prints nothing.
- If an entry is still over 2 s, include the probe's stats line: instantiate_ms, prewarm_wait_frames and the holders
  warning.
MERGE-READY @ 329e7bce (FAST-TRACK row 67): the router instantiates only after its loads are in; scene_loads lists
every cast model; max_in_flight 4.
- 2026-10-30 10:30, **the Lead's 05:52 Act II lane.** I merged the integration branch (1e63e5ba, baseline approvals).
  - **Heresy words** (e9de89f6): ADR 0204 approved "Outside the Level". The field-menu subtitle, a heretic save's slot
    ("Chapter 14 · Outside the Level", rendered and viewed: it fits) and the Order shop's refusal now use it, along with
    heresy.md. The save fixtures can now carry `flags`.
  - **Codex, M4-A2P-008** (dbc4fa8a): `keth`, `conclave` (only the public "Conclave of Elders", nothing about its truth
    and no "revenant"), `malcor_venn` (a man, nothing stranger) and `heresy` ("Outside the Level"). These are every plan
    entry whose unlock flag is declared today. The rest land as the Ch11–Ch16 beats declare their flags.
    test_codex 16/0, pseudo_loc_screens 17/0; validate_data clean, banned terms included.
  - **No Vowbound category yet:** Act I's three have no entries of their own, and what the party knows of each one's
    human life at its binding is Narrative's call (vowbound.md holds the whole truth). I won't write these until a beat
    says what's known.
  - **Portraits:** none of Act II's new speakers has a model on any branch (Tobin, Merel, Malcor Venn, the Kirru, the
    Ullari, Liss's father), so none was baked and none was stubbed.
  - **Bestiary:** Ch10's three rows in enemies.json have no `model`, so the bestiary has no picture, and the fight
    probably draws a capsule. Noted on Combat's request M3-UI-208 (578a6ceb).
MERGE-READY @ 578a6ceb: the heresy's words per ADR 0204, and four Act II codex entries.
- **BACKLOG EMPTY:** the rest of Act II waits on other tracks:
  - Ch11–Ch16 flags and beats (more codex entries);
  - speaker models (portraits);
  - Combat: Pell's row, the rooted status, the enemy model links;
  - Narrative: records.json and the Vowbound text.
  - Row 67's PC verification (gpu/row67-verify) would jump ahead of everything.
- 2026-10-30 11:20, **the Lead's 09:01 items.** I merged big20 (7dc3ab41) as 0a85bf07.
  - In the codex merge, Narrative's Act II people set wins: its `malcor_venn` and `conclave` replace mine. My `keth` and
    `heresy` stay under World (test_codex 16/0).
  - **LEAD-ASK, row 67: big20 has amendment 4 (5c662779) but not the row 67 fix (329e7bce), and they belong together.**
    - Amendment 4 moves ZoneCast's model instancing into GreyboxZone.build. That runs on the router's instantiate
      thread while ResidentLoads' threaded loads are in flight, so big20 widens the window in which the hang showed.
    - 329e7bce closes it: the router waits on its loads before it instantiates.
    - Please take 329e7bce, and this branch, into big21 ahead of the next PC pass. If big20's PC pass shows more
      hangs, that is the reason.
  - **Portraits re-baked on big20's models** (cd38c0c9): 23 speakers, 115 images. Their models had all changed since
    the last bake: Pell, Moll, Sefir and 20 villagers.
    - Pell's fur now has texture (the PC's pass 3 note), and Sefir's veil hangs over his face. I viewed both, side by
      side with the old bakes.
    - **For characters:** Moll's new hair casts a hard shadow across half her face under her stage's key light. The
      bake is faithful to the model; the fix is in her stage or hair.
    - Every dialogue speaker without a portrait (the generic barks, and Act II's people with no model yet) shows no
      picture. No placeholder ever shows.
    - Shots that show these portraits (dialogue, status, the party cards) will drift on the gate.
  - **Act II map regions:** all 15 Act II zones already had maps. Each now gets a main-path objective, 17 rows chained
    on the declared Ch10–Ch16 flags, so the line and the gold marker point at the chapter's next place (8287ca8b).
    - Ch13 goes to the Sanctum first, then the Archive.
    - The lines are in Act I's register and say nothing past their beat.
    - The Lowlight map shot now stages arrival (`ch11_reached_lowlight`). I viewed Keth Pass, Lowlight and Ansedra.
    - test_objective_tracker 16/0 (a new walk of all 17 rows); zone_map 22/0; pseudo_loc_screens 17/0; validate_data
      0/0.
    - The three map shots will drift on the gate.
MERGE-READY @ 8287ca8b: the portraits re-baked on big20's models, and the Act II objectives.
- 2026-10-30 12:30, **Malcor Venn's portrait** waits on its merge. His model and stage are on claude/characters
  (3f0f5d679, M4-A2P-051), not on the integration branch. When they land, I add `malcor_venn` to portraits.json from
  his stage (`venn_stage.tscn`), bake his five faces, view them and add their PROVENANCE rows. No other Act II speaker
  has a model on any branch.
- **BACKLOG EMPTY** after the 09:01 items:
  - **Done:** big20 merged; portraits re-baked; Act II maps point along the main path; the heresy's words and four
    codex entries; row 67's fix waiting for a batch.
  - **Waits on others:**
    - Malcor Venn's model (its merge);
    - the other Act II speakers' models;
    - Ch11–Ch16 beat flags (more codex);
    - Combat: Pell's row, the rooted status, the enemy model links;
    - Narrative: records.json and the Vowbound text;
    - the PC's row 67 verification.
- 2026-10-30 13:40, **the Lead's 09:58 note:** big21 (0347aa74) carries row 67's fix, and the PC is measuring it.
  - **Merged big21** (59202bae1). Its own resolution wins for the codex, flags and Sefir's portraits (the characters
    track's GPU-QA re-render). strings.csv keeps my Act II objective lines; its four Act II LORE rows now live in
    ch10/ch15.csv. I redid the merge once, after a stash dropped its MERGE_HEAD, so the commit is a true merge.
  - **The Status page's Bound section** (5e1e8d38a): a caller (Asha) lists the Vowbound bound so far, in bind order, or "None
    yet". It sits under Lattice in the right column, because the left one has no room once seven heroes are listed
    (screens.md updated). I viewed it with all six of Act II. test_status_menu 8/0, aspect 18/0,
    pseudo_loc_screens 17/0.
  - **Act II inns** (92151e255): `ansedra_guest` (shops.json, `order: true`, price 0, from `ch13_started`).
    - The rest reads "No charge" and "A night here costs nothing."; an empty purse still rests.
    - Any inn marked `order` refuses those outside the Level ("The door stays shut. The Order keeps no guests
      outside the Level."). Saltwright inns still take them.
    - I viewed it through the inn shot (temporarily pointed at the guest house). test_inn_menu and test_inn 11/0,
      shop 28/0.
    - **For the Ch13 zone's owner:** place a trigger at Sefir's house (the `sefir` POI) with
      `{"inn": "ansedra_guest"}`, as Quellan's inn does.
  - **Portraits:** Malcor Venn and the three Abiding guards aren't in big21 yet; I'll bake them as soon as they land.
MERGE-READY @ 92151e255: big21 merged; the Bound section; Act II inns.
- 2026-10-30 14:20, **Act II battle floats** (a4336326a), on Combat's new hit keys:
  - a drain (`drained`, the fen leech, M4-CMB-1001) puts its heal number over the user, with "Drained";
  - a crawler's repair (`part_restored`, M4-A2P-022) floats "{part} mended" over the boss, the part named by its charge
    skill.
  Combat already built the rooted swap reason ("held by the roots") and the element cycle's timeline, so hud.md's
  rooted and cycle items are done on their side.
  test_battle_controller 33/0 (a new drain and repair test), battle_choreo 28/0, battle_reduced 5/0, pseudo_loc 26/0.
  No committed shot shows them.
MERGE-READY @ a4336326a: Act II battle floats.
- 2026-10-30 14:40, **PC pass 5: row 67 FIXED.** Every entry is under 1 s hidden, and Brine Shoals ran 5/5 fresh with no
  hang. No pass 5 row is routed to ui-menus. I merged the integration branch's 15d80358c (the Lead's log).
- **BACKLOG EMPTY** for what ui-menus can build without other tracks:
  - **Portraits:** Malcor Venn's model is still only on claude/characters, and the Abiding guards are on no branch.
  - **hud.md:**
    - buff strip, darkness and tide pulse: no engine support yet (Combat);
    - Pell's Listen and his absence: Pell's battle row;
    - a Read-panel ability list (drain and repair tags) would be a new feature, which I'm leaving until Combat's kit
      rows settle.
  - **Codex:** Narrative now writes the Act II entries (its people and world sets landed in big20 and big21).
  - **The reader's records:** Narrative.
- 2026-10-30 16:30, **the Lead's 10:47 item: the as-played Act I UI pass** (0347aa74 plus this branch).
  - **How:**
    - Twenty UI shots at 2560×1440 with the largest text (130%, from a pre-seeded settings.cfg; the manifest swapped
      temporarily and restored). All viewed:
      - battle: HUD, swap, Read, victory;
      - field: menu, codex, prompt, tip, dialogue;
      - title, settings, save, shop, bestiary, equip, items, status, formation, Lattice, Reefball.
    - test_pseudo_loc_screens (it fit-probes every screen at 100% and 130%), plus a new English mode
      (`HYMN_PSEUDO_OFF=1`).
    - The input-parity suite (focus order on keys, pad and mouse).
    - A new contrast test.
  - **Found and fixed:**
    - **Field menu at 130%:** the cards' names sat on their HP rows, the save hint sat on the date, and the objective
      ran into the help line.
      - The card rows and the Last saved and Objective blocks now grow with the text size; at 100% nothing moves.
      - The portrait gives up what the card text needs.
      - When the objective's lines need the room, the save hint steps aside, and then the objective shrinks to 80%
        at most.
    - **Shop at 130%:** a two-line refusal ran into the help line. The line about the row and the status now share
      the column above the help.
    - **Status table:** at 130% the stat names and heads now fit their columns ("Magic Defense", "Lattice").
    - **Contrast** (tools/tests/test_ui_contrast.py, WCAG 2): every text colour is at least 4.5:1 on the page panels
      in both palettes, and at least 3:1 (bold large text) on the raised cursor row.
      - The colorblind `danger` (#D15E1F) was 4.25 on the deep panel. It is now #C76E10: 4.52:1, and still
        distinct (0.171 Oklab worst-case under deuteranopia and protanopia; test_colorblind_palette).
      - docs/kb/tech/ui.md and test_ui_settings are updated.
  - **Checked and clean:**
    - **Pillar 4:** the timeline always shows who acts now and next. Every command row shows its cost (MP, rank,
      escape odds, "No time"). Every leaf command previews where the actor lands ("acts again in 5 turns").
    - **English at 130%:** no text is cut anywhere. Only Reefball's panels grow taller than their boxes, without
      overlapping.
    - **Focus order:** input_parity 65/0.
    - **Pseudo-loc:** it still cuts some text with an ellipsis (mostly Reefball's Read and Drop columns). These are
      localisation-length warnings with nothing cut in English, so I left them.
  - **Tests:** field_menu 29/0 (a new 130% overlap test), party_card 3/0, shop 28/0, inn 11/0, status_menu 8/0,
    pseudo_loc_screens 17/0, aspect 18/0, colorblind 2/0, ui_settings 11/0, input_parity 65/0; tools: ui_contrast OK;
    validate_data 0/0; lint and format clean.
  - **Drift:** the 100% field-menu shots move by about 1 px in the cards' text (and their baseline already predated
    Toma's portrait), and battle_statuses_colorblind changes with the new orange.
MERGE-READY @ 4edf33c21: the as-played Act I UI pass.
- 2026-10-30 17:40, **the Lead's 11:47 note.** I merged the integration branch (ADR 0206: British spelling).
  - **ADR 0206:** my new strings are British. The one older American string I own (`STATUS_MENU_ARMOR`, "Armor") is in
    act2-plan's FAST-TRACK, so I left it to avoid a clash.
  - **Focus order:** done in the 10:47 pass (input_parity 65/0, keys, pad and mouse).
  - **Battle at every text size** (8132685db):
    - **Method:** the HUD, swap and Read shots rendered at 115% and 130%, through the fixtures' `ui_settings` (data
      restored afterwards). All viewed.
    - **"Acting now" at 130%:** the head chip read "Acting …", and names like "Gull Harrier" lost their ends. Both now
      fit their width (down to 80%) before an ellipsis cuts them.
    - **Party rows at 130%:** the HP and MP numbers sat on their gauges. Above 100% a number's bottom now stays on its
      gauge's top. At 100% nothing moves; I checked against the baseline, and the party panel is pixel-identical.
    - **Costs:** every command's cost shows at both sizes (MP, rank, escape odds, "No time"), and so does the help
      line's outcome ("Rhen acts again in 5 turns").
    - **The Read panel at 130%** grows over the party panel's lower edge. It is modal, its own text is whole, and the
      battle waits while it is open, so I left it.
    - **Tests:** battle_controller 33/0, timeline 30/0, pseudo_loc_screens 17/0.
MERGE-READY @ 8132685db: the battle text-size fixes.
- 2026-10-30 13:10, **the Lead's 12:48 note: the black screen after a won battle.**
  - **Cause (ResidentLoads, fixed in 8df5fe2b4):** entering the field battle let the zone's own resident loads go.
    On Return they were read again from disk, and the prewarm feed staged about 950 materials a second time.
    - **Measured** with the probe's new `--round-trip=<encounter>` option, returning to Brine Shoals after
      `ch06_flats_crabs` (headless): **4875 ms** zone entry with 614 prewarm frames before the fix, **667 ms** with
      2 frames after.
    - **Fix:** a change into the battle scene now keeps the zone's loads, so the return loads nothing and prewarms
      nothing again.
    - **Test:** `test_a_field_battle_keeps_the_zone_s_loads_for_the_return` (resident_loads 9/0).
  - **Each segment after the fix:**
    - **Victory panel:** it opens 0.6 s after the last blow, with the battle still on screen. Nothing is black.
    - **Confirm on Return:** `FieldBattle.return_to_field` calls `FlowRouting.go_to` the same frame, with no wait.
    - **Fade-out:** `SceneRouter.FADE_SEC` 0.35 s.
    - **Black:** the entry from the cache (about 0.67 s headless), plus `MEASURE_FRAMES` 4 frames. The loading cover
      holds nothing on this path.
    - **Fade-in:** 0.35 s.
    - **Input:** live as the fade lifts. Field input doesn't gate on `SceneRouter.is_busy()`.
  - **To integration-qa (owner of the SceneRouter return):** my side has no fixed wait left. The black is now the
    cached entry alone, under 1 s. The fades are the router's 0.35 s each way. If the PC's entry still runs over 1 s,
    the next cut is in the router or the zone's `_ready`, not in ResidentLoads or the results panel.
  - **PC-QUEUE:** re-measure the return on the GPU, either with
    `scene_swap_probe.tscn -- --resident-loads --warm-resident --to=<brine shoals> --round-trip=ch06_flats_crabs`
    or by hand: win a fight and time from Return until you can walk.
  - **Tests:** resident_loads 9/0, scene_router 17/0, prewarm 27/0, act1_swap_sweep (tools) OK; lint and format clean.
  - **test_qa_threads and act1-chapters (ca5ce4037):** the guard failed 6 ways on my Act II objective rows.
    - **Cause:** a chapter's last row ran `until` the next chapter's start flag, which that chapter's thread never
      raises.
    - **Fix:** `reed_clutch`, `low_sanctum`, `cloudloom_dais`, `archive_ledgers` and `court_barge` now have
      `until: null`, holding until the zone changes, as Act I's `t_harbour` does.
    - **Still unraised:** Lacquer Court's `court_dais` and `court_barge` (filed under `ch13/`) wait on
      `ch14_started` and `ch14_declared_heretics`. Ch14 has no thread yet, so both are listed in `qa_known.json`
      "unraised" and point at M4-A2P-014.
    - **To act1-chapters:** when the ch14 thread raises those two flags, drop both rows from `qa_known.json`.
    - **Result:** qa_threads 1/0; objective 16/0, field_menu 37/0, zone_map 22/0; validate_data 0/0.
MERGE-READY @ ca5ce4037: the battle-return black screen (ResidentLoads keeps the zone through a field battle) and the Act II objective flags for test_qa_threads.
  - **To integration-qa:** the measurement method and the remaining end-to-end check are in request task **M4-UI-212** (role qa), per the Lead's 13:48 note.
- 2026-10-30 14:30, **the Lead's 13:48 note.**
  - **Request task to integration-qa:** M4-UI-212 (role qa) holds the measurement method and the end-to-end check.
  - **Next item, the Act II queue (M4-A2P-083):** a foe's broken parts now show on the battle's Read panel ("Broken ·
    Lamplight: silent until it is mended") until a tender mends them.
    - **Test:** test_read_panel 13/0, plus bestiary 37/0, battle_parts 4/0 and pseudo_loc 26/0.
    - **Render:** viewed with the line injected. The battle_read_panel shot itself is unchanged (no part there).
    - **Next:** the answered-by cursor line once Venn's row has `answered_key`; the Lacquer Court rows once ch14's
      flags exist (M4-A2P-014).
MERGE-READY @ eb1d12998: broken parts on the Read (M4-A2P-083).
BACKLOG EMPTY: everything left in this track's queue waits on another track.
- **M4-A2P-081 NPC portraits** (Malcor Venn, the Abiding guard): wait on their models (characters track).
- **M4-A2P-082 seven-hero formation check:** waits on Pell's battle row (combat).
- **M4-A2P-083:**
  - The answered-by cursor line waits on Venn's row carrying `answered_key` (M4-A2P-023, combat).
  - The darkness telegraphs are battle-presentation's, already in (M4-A2P-062, in review), and the timeline shows them.
  - The Act II bestiary pages fill as the foe rows land.
- **Lacquer Court objective rows:** wait on ch14's thread raising its flags (M4-A2P-014, act1-chapters); then drop the two
  `qa_known.json` "unraised" rows.
- **Battle return end to end:** M4-UI-212 (integration-qa, plus a PC measurement).
- 2026-10-30 16:10, **the Lead's 14:28 note: a controller-only pass over Act I's menus** (merged big23 at 63175d0b3).
  - **Merge:** act1-chapters' Act II objective rows replace my interim ones. Theirs cover every zone beat by beat, so
    I dropped my 17 `OBJ_*` strings and pointed the Act II objective test at their rows.
  - **The walk:** `tests/unit/test_input_parity_pad_walk.gd` (3/0) drives the pad alone over:
    - every field menu page, with a played save: Down, Confirm three deep (equip a piece, use a tonic, the Lattice, the
      map, Settings), then Cancel out;
    - every battle command (Attack, Skills, Items, Swell, Swap, Escape), into its page and target, then back;
    - the battle pause, including Settings and one of its pages;
    - the save list (with the overwrite question) and the title's load list.
  - **After every press it fails on:**
    - an unfilled `{action}`;
    - a key's name where the pad has its own button;
    - focus on a Control that isn't on screen;
    - a menu page with nothing saying how to go back.
  - **Found and fixed:**
    1. **Settings never said how to move or go back** (hub and pages, from the field, the title and the pause). A
       controls line now sits under the help. The Controls page hides it while listening, and the hub's line hides
       under an open page.
    2. **The save and load lists ignored the pad.** They take their input before the UiInput autoload, so a pad press
       left the prompts on the keys and a held D-pad never repeated there. They now let UiInput notice each event
       first (`UiInput.notice`).
    3. **The save and load lists never said how to go back.** A controls line now sits at the right of the help row:
       "Confirm: record · Cancel: close" (load: "continue"), and the question's "Up and Down: choose · Cancel: keep it".
  - **Not changed, by design:** the battle command menu's help line is the action's cost and turn, and Cancel at its
    root opens the pause (which says how to go back). The walk exempts only those stops.
  - **Focus:** no Control kept the focus while hidden. Dead ends: none (with test_input_parity_dead_ends).
  - **Renders viewed:** settings_hub, settings_accessibility (130%), settings_controls, save_menu, save_menu_overwrite.
    All five change baselines (the new lines). The Lead re-approves; I wrote no baselines.
  - **Tests:** pad_walk 3/0, settings 48/0, controls 12/0, graphics_menu 9/0, accessibility 9/0, save 201/0,
    title_menu 16/0, input_parity_title 2/0, pseudo_loc 26/0, aspect 18/0, objective 16/0, field_menu 37/0,
    zone_map 22/0, ui_input 4/0; validate_data 0/0; lint and format clean.
  - **For act1-chapters (seen on big23 itself):** test_qa_threads fails 15 ways on their new Act II objective rows.
    The ch10–13 threads don't yet raise the beats those rows wait on (`ch10_farewell_tide_seen`, `ch11_nhoa_bound`,
    `ch12_ram_felled`, `ch13_read_ledgers`, each chapter's `_complete`, and the Lacquer Court's ch14 beats). My
    merge took their `objectives.json` and threads unchanged. I only renamed the rows in my two qa_known notes.
MERGE-READY @ 0fda0d8b5: the controller-only pass (Settings and save/load controls lines, the save list's pad notice, the pad walk test).
- 2026-10-30 17:00, **the Lead's 16:09 note: as-played check of the new battle return** (merged big24 efe7fb10 at ce9c0d6d0).
  - **Merge:** `objectives.json`, `test_objective_tracker` and `qa_known` take the integration side (act2-plan's
    M4-A2P-109). The `OBJ_*` strings it keeps are restored, and `strings.csv` is the integration file plus my
    seven controls lines.
  - **Found and fixed (8d42e9508):** a resident field stopped following the text size and palette.
    - **Cause:** big24 keeps the field zone through a random fight. It leaves the tree and comes back without
      `_ready`, and `UiSettings.follow` stopped for good on `tree_exited`.
    - **Effect:** after the first random battle, nothing in that zone took a text-size or palette change again: the
      interact prompt, tip card, area title card, codex notice, objective HUD, hold prompt and dialogue box. That
      included a change made in the battle pause.
    - **Fix:** `follow()` now stops while out of the tree and catches up when back.
    - **Test:** test_ui_settings::test_a_control_out_of_the_tree_catches_up_and_keeps_following fails on the old code
      and passes now.
  - **Victory and rewards:** battle_victory rendered at 100% and at 130% (the fixture's `ui_settings`, restored
    afterwards), both viewed. The rows, XP, "+3 movement" (this game's level-up: Lattice movement), lume and drops
    fit, and so do the choices. Nothing is cut.
  - **Pad:** the result choices are covered by test_input_parity_battle (result panel, each device). The A press that
    picks Return can't fire an interaction on arrival: the field acts on the press event, which the battle consumed.
  - **Return:** test_battle_return 1/0 (the resident re-attach, under the fade).
  - **Tests:** ui_settings 12/0, settings 49/0, field_menu 37/0, objective_hud 7/0, interact 13/0, battle_return 1/0,
    pad_walk 3/0; validate_data 0/0; lint and format clean.
MERGE-READY @ 8d42e9508: a resident field keeps following the text size and palette; battle-return as-played check.
- 2026-10-30 17:50, **Act II menus for the content that has landed (big24).**
  - **Malcor Venn's portrait** (4eabd31f3): baked neutral, cold and determined from his model (M4-A2P-051). The
    dialogue box shows it for speaker `malcor_venn` (alias), so his Ch14 decree reads with his face.
  - **Merel, Tobin and Ansedra's clerk** (8b07bcd50): 16 faces, in the emotions their Act II lines use. A new test,
    test_every_act2_speaker_with_a_model_has_a_portrait, guards the next Act II model to land.
  - **Viewed:** every bake. Two notes for characters:
    - Venn's face uses Asha's pose weights, so his three expressions look nearly alike at 256 px. A Venn face-pose
      table would give the decree its chill.
    - Tobin's `laugh` reads as a lopsided grimace with the tongue showing.
  - **Still waiting:**
    - the Abiding guard's portrait (no model yet);
    - Venn's bestiary page and the answered-by cursor line (no Venn enemy row, no `answered_key` yet);
    - the seven-hero formation check (Pell's battle row).
  - **Tests:** hero_portraits 10/0, dialogue_box 27/0; validate_data 0/0 (PROVENANCE rows); lint and format clean.
MERGE-READY @ 8b07bcd50: Act II faces (Venn, Merel, Tobin, the clerk) in the dialogue box.
BACKLOG EMPTY: every remaining item waits on another track (the Abiding guard's model; Venn's enemy row with `answered_key`; Pell's battle row; ch14's thread for the Lacquer Court objectives).
- 2026-10-30 18:20, **the Lead's 16:45 note: big25's red test_aspect_layouts** (merged big25 at b67876dbf;
  `objectives.json`, `qa_known.json`, the objective test and `strings.csv` take act2-plan's integration side).
  - **Cause:** the failing label was the Read's "Weak to Fire" float (DamageLayer), not the panel. At 4:3 the Lantern
    Eel stands at the screen's left edge, so the centred float started at x -41 (-63 at 130%).
  - **Fix (430bd0471):** every damage number and float word is clamped inside the screen by `edge_px` (12;
    `battle_hud.json` `damage` and `float_text`).
  - **Tests:** aspect 18/0 (failed before), read_panel 13/0, battle_controller 33/0, accessibility_battle_speed 6/0;
    validate_data 0/0; lint and format clean.
  - **Render:** battle_read_panel with and without the fix is pixel-identical at 16:9. Its drift from the baseline
    (rmse 0.074) was already there without my change, so it's another track's (the staging).
  - **Battle return at 130% and on a pad:** done at 17:00 (80d453279). The victory and rewards renders at 100% and
    130% were viewed, the pad covers the result choices, and the fix for the resident field following the text size
    is in.
MERGE-READY @ 430bd0471: battle floats stay on screen (big25's 4:3 Read red).
- 2026-10-30 19:05, **M3-HER-1167 (integration-qa's request, the Lead's top priority): the first zone loads while the
  title shows** (082ab9166).
  - **What:** the title calls `ResidentLoads.load_scene` (no hold) for the zone its highlighted choice enters.
    - **New Game:** `locations.json` `new_game`, which on the Act I route is the prologue (157 loads), not
      Haluna.
    - **Continue:** the newest record's location, read with `slot_info` without loading it.
    - The loads queue behind the hero bodies. Moving between New Game and Continue switches the zone.
    - When the change starts, the same request loads nothing twice and keeps the queued prewarm, so the pipelines
      still compile under the cover.
  - **Measured** (headless lavapipe; `scene_swap_probe --resident-loads --warm-resident`, plus the new
    `--warm-scene` for the early start):

    | Zone | Start | Entry | Swap held | Worst hidden frame |
    |---|---|---|---|---|
    | Haluna | at the change | 4.9 s | 414 frames | 708 ms |
    | Haluna | early | 3.1–3.3 s | 158 frames | 796–928 ms |
    | Prologue | at the change | 1.78 s | 71 frames | 374 ms |
    | Prologue | early | 1.00 s | 72 frames | 120 ms |

  - **Haluna's remaining hold** is the prewarm staging its ~280 materials under the cover, plus 0.83–0.95 s to
    instantiate. That is pipeline compile, which loads can't absorb. Pre-compiling on the title would hitch the
    title, so I left it.
  - **To integration-qa:** please re-measure on the PC with `--warm-scene`, and log the split (acceptance item 2).
    Not done here: the prologue starting Ch1's loads (`oruvel_underway`, 102) while it plays. That's the prologue
    scene's (cinematics') to call, `ResidentLoads.shared().load_scene(next)`. I'd take it if handed over.
  - **Tests:** resident_loads 10/0 (new: the early start keeps the prewarm), title_menu 17/0 (new: each choice's
    first zone), input_parity_title 2/0, scene_router 17/0, pad_walk 3/0; lint and format clean.
MERGE-READY @ 082ab9166: M3-HER-1167, the title starts the first zone's loads.
- 2026-10-30 19:40, **the Lead's 17:24 note: the victory panel's stay prewarms the return** (95f51b987).
  - **What:** when the result panel opens on a win or an escape, `FieldBattle._prepare_return()` calls
    `ResidentLoads.prepare_return(request, SceneRouter.resident_path())`.
    - The return's scene starts loading with no hold: its `return_scene`, or else `return_location`'s scene.
    - Nothing loads when that scene is the field kept resident through the fight, or when nothing resolves.
    - When Return is pressed, the change asks for the same scene: nothing loads twice, and the queued prewarm stays.
  - **How much it saves:** whatever the panel's stay covers. Haluna fully loaded early took the entry from 4.9 to
    3.1 s headless (M3-HER-1167's numbers). A one-second stay covers part of that.
  - **Tests:** resident_loads 11/0 (new: test_the_victory_panel_starts_the_return_s_loads), field_battle 12/0,
    battle_return 1/0, input_parity_battle 8/0; lint and format clean.
  - **To integration-qa** (extending the resident return to scripted fights): my hook is one call in
    `FieldBattle._show_result` (`game/flow`, the slice's; one guarded line plus `_prepare_return`). If your change
    keeps a scripted fight's origin zone resident, `prepare_return` already skips it when `resident_path()` matches
    the return. Please merge around it rather than over it.
  - **Spotted, not mine:** nothing emits `EventBus.battle_ended`. FieldEncounters listens for it to grant the
    post-battle grace, so that grace never arms through the bus.
  - **The 4:3 Read panel:** already pushed (430bd0471, MERGE-READY at 18:20).
MERGE-READY @ 95f51b987: the victory panel starts loading the return's destination.
- 2026-10-30 19:55, **the Lead's 17:44 note: test_aspect_layouts still red in big26.** big26 (e605c9f4c) doesn't
  contain the fix. 430bd0471 ("keep battle floats on screen", MERGE-READY at 18:20) is on `claude/ui` but was never
  merged into the integration branch.
  - **Checked:** big26 merged into `claude/ui` (d311c5e38). On that head: aspect 18/0, read_panel 13/0,
    resident_loads 11/0, title_menu 17/0; validate_data 0/0.
  - **What fixes the red:** merging `claude/ui` at or after 430bd0471. The commits are 430bd0471 (the clamp in
    `damage_number.gd` plus `edge_px` in `battle_hud.json`) and its log.
MERGE-READY @ d311c5e38: claude/ui with big26 merged; carries the 4:3 Read fix (430bd0471), the title preload (082ab9166) and the victory-panel preload (95f51b987).
BACKLOG EMPTY (big26 checked at 20:00): every remaining item waits on another track.
- **Venn's bestiary page and the answered-by cursor line:** no Venn enemy row, no `answered_key` (combat).
- **The seven-hero formation check:** Pell has no battle row (combat).
- **The Abiding guard's portrait:** no model (characters).
- **Already covered:** every Act II speaker with a model has a face, and every foe with a model has its bestiary
  portrait.
- **To merge:** claude/ui at 43fa81abe for big26's aspect red.
- 2026-10-30 20:50, **the Lead's 18:04 note: the Act II UI as played on Ch10–Ch13** (M4-A2P-1700, my range 1700–1799).
  - **The walk:** `tests/unit/test_act2_ui_as_played.gd` (5/0) runs at 100% and 130%.
    - **Zone titles:** every Ch10–Ch13 location's area title card.
    - **Objective lines:** every Ch10–Ch13 line, main and side. A main line shows in its zone; on demand it's the
      Where-to-next card.
    - **Shops and inns:** Quellan's and Ansedra's, walked with the pad (Buy, every stock row, a purchase, Rest,
      Leave), open and closed.
    - **Vowbound calls:** Asha's battle menu with the six Vowbound bound by Ch13, each Call row reached by the pad.
    - **It fails on:** a Control off screen, text out of its panel, and text cut short (wrapped or one-line).
  - **Found and fixed (fca18c182):**
    1. **An inn's refusal was cut to one line.** "The door is barred. No rooms for…" at 130%: the status kept its
       built height. It now gets the column down to the help line.
    2. **Quellan's and Ansedra's Rest lines were cut at 130%.** They needed 365 px of a 326 px column. The inn panel
       is now 618 tall (was 558) and its line's cap is 400.
  - **Renders viewed:** inn_menu at 100% and at 130% (Quellan). The inn_menu baseline changes with the taller panel.
  - **Clean:** the area titles, every objective line, the shops' stock, and the six Call rows (all on screen; the
    root grows to 12 rows and still fits).
  - **Tests:** act2_ui_as_played 5/0, inn 11/0, shop 28/0, town 6/0, aspect 18/0, pseudo_loc 26/0,
    input_parity_shop 3/0; validate_data 0/0; taskboard ok.
MERGE-READY @ fca18c182: M4-A2P-1700, the Act II UI as played (inn refusals and Rest lines whole at 130%).
- 2026-10-30 21:40, **the Lead's 18:24 note: the Act I first hour from a fresh profile** (M4-A2P-1701, 07386b3d0).
  - **First battle (Ch1's wickfry):** TUT_CH01_COMMANDS is on the help line, in gold, when the first command menu
    opens. It shows once per fight, and the first cursor move gives the line back to the help. OK as is.
  - **Found and fixed:**
    1. **The menu tip never showed.** Its flag (`ch01_wickfry_won`, and the slice's `ch02_tideline_won` before
       it) is set in the battle scene, where no field tip card listens, and the zone reloads after a scripted fight.
       Flag tips are now caught up when the field next takes input (still once per save).
    2. **The Where-to-next and menu tips waited for Ch2's slice flags.** New Game plays the prologue and then Ch1,
       so a chapter went untaught. Both now come in Ch1 (`ch01_started`, `ch01_wickfry_won`) and still on the
       slice route. `tutorial_tips.json` `when` may list flags, and `requires_any` is new; `validate_data` and
       its test know both.
    3. **Tips couldn't be skipped.** Pressing an action a tip names now fades it out, so the menu tip no longer
       comes back after the menu closes.
  - **Unchanged and fine:** the save tip (the first shrine in reach), the menu-save and Swell tips in turn, and the
    objective line on each zone's first input.
  - **Render viewed:** the menu tip at 130%.
  - **Tests:** tutorial_tips 8/0 (three new), input_parity_glyphs 7/0, objective_hud 7/0, field_controller 5/0;
    tools test_tutorial_tips OK; validate_data 0/0; taskboard ok.
MERGE-READY @ 07386b3d0: M4-A2P-1701, the first-hour tips (once, in Ch1, skippable).
- 2026-10-30 22:30, **the Lead's 18:45 note: the Act II first-time hints** (M4-A2P-1702, a3065f588).
  - **Added** (act2-plan's `ui/tutorials.md` text, already on the integration branch):
    - Seven heroes on `ch10_started` (a flag tip, so it survives the fade-in);
    - Records on `ch13_archive_read`;
    - Dark shrines at the first shrine in reach after `ch14_declared_heretics`, never before.
    - Each shows once (`tut_records_seen` and `tut_dark_shrine_seen` are declared) and fades when its action is
      pressed.
  - **Ch10's Where-to-next:** the objective line slides in when `ch10_started` makes the Ch10 row live (the line
    shows on change), so the fade-in timing doesn't lose it.
  - **To act2-plan (narrative), M4-A2P-1004:**
    - **F1:** done in 07386b3d0.
    - **F5:** the objective tip now comes at the bell room (`ch01_saw_bell_room`, or `ch02_met_asha` on the slice
      route).
    - **F8:** layout shrines are tagged `shrine`.
    - **Optional wording, taken:** "objective", "Items, Equip … the Map".
    - Please move 1004 to done on your branch; it isn't on the integration branch yet.
  - **Waiting on others:**
    - The Swell-mode tip: no `<mode>_unlocked` flags yet (Progression).
    - The new statuses' lessons are combat's battle prompts (`TUT_CH10_ROOTED` and the rest), not in
      `encounters.json` yet. The help line shows each once per fight when they land.
    - Act II Vowbound: untaught by plan.
  - **Tests:** tutorial_tips 9/0, input_parity_glyphs 7/0, save_shrine 13/0; tools test_tutorial_tips OK;
    validate_data 0/0; taskboard ok.
MERGE-READY @ a3065f588: M4-A2P-1702, the Act II first-time tips and M4-A2P-1004's fixes.
- 2026-10-30 23:20, **the Lead's 19:25 note.**
  - **Requests filed:**
    - M4-A2P-1703 (combat): wire the Act II battle prompts (`TUT_CH10_ROOTED` and the rest) into
      `encounters.json`.
    - M4-A2P-1704 (progression): the Swell-mode unlock flags, for the "A New Swell" tip.
  - **Save and load pass (M4-A2P-1705, ace2d088c):**
    - **The sweep:** `tests/integration/test_continue_every_act1_zone.gd` covers every enterable Act I location
      (17, the prologue to Ch9). It writes a chapter autosave, then Continues as the title does. Chapter, location,
      party and reserve, flags, bag, money and play time come back, and the party enters that location's scene at a
      named spawn.
    - **Found and fixed (ADR 0121):** Continue from a chapter autosave went to the last shrine, a chapter back, while
      the slot named the new zone. 16 of 17 locations were wrong on the old code. The autosave now records its
      location as the respawn, on a copy (`SaveSystem.autosave_state`); Game.state keeps its shrine.
    - **Already covered and green:** the shrine round trip in every zone (test_qa_save_shrines); the autosave during
      a cutscene waits and saves its end (test_autosave_deferred); the pause menu's Settings and resume
      (pad walk, input_parity_battle).
    - **Tests:** autosave 23/0 (new: test_a_chapter_autosave_continues_in_the_chapter_s_zone), continue_every 1/0,
      save_system 11/0, world_return 17/0, title_menu 17/0, save_new_run 4/0; validate_data 0/0; taskboard ok.
MERGE-READY @ ace2d088c: M4-A2P-1705 (ADR 0121), plus requests M4-A2P-1703 and M4-A2P-1704.
- 2026-10-30 23:45, **the Lead's 20:26 note.**
  - **Save and load pass:** pushed. MERGE-READY @ ace2d088c (M4-A2P-1705, ADR 0121); origin/claude/ui is at b084899d9.
    - Every Act I zone: a chapter autosave, then Continue from the title, restores the party, flags, zone and spawn.
    - Mid-cutscene: the autosave waits for the cutscene's end and saves that (test_autosave_deferred, green).
    - Fixed: Continue from a chapter autosave went to the last shrine, a chapter back.
  - **The Drownbell re-measure waits.** integration-qa's trace (hero-integration 3b8d02d70, on big28) already splits
    the return:
    - 0.4–1.9 s: Haluna loading (the victory-panel preload, 95f51b987, is in effect there);
    - 1.9–5.0 s: the reveal held by VillagerLayer's per-frame builds, the fix filed as M3-HER-1168 (creatures),
      not landed.
    - Until it lands, a re-measure only measures that hold again.
    - **Next step:** when M3-HER-1168 is on the integration branch, run the return probe
      (`scene_swap_probe --resident-loads --warm-resident --encounter=<drownbell> --return=<haluna>`) with and
      without `FieldBattle._prepare_return`, and log the split here.
- 2026-10-31 00:20, **the Lead's 21:05 note: the Act II save and load pass in Ch10–Ch13** (M4-A2P-1707, 3df48256a).
  - **The sweep:** test_continue_every_act1_zone now has an Act II case. It covers all 11 enterable Ch10–Ch13
    locations, with the seven (Rhen, Asha and Pell in the line; Toma, Ysolde, Liss and Kerrid in reserve) and Act II's
    flags. A chapter autosave, then Continue from the title, restores everything, and the party enters that location
    at a named spawn. 2/0 (Act I and Act II).
  - **Shrine round trip:** test_qa_save_shrines walks every zone and stays green, 2/0.
  - **Found:** no Ch10–Ch13 zone has a save shrine or rest point. The player can only autosave at a chapter's start.
    The plan names Reedhollow, Lowlight, Quellan and Ansedra (whose flavour dialogue exists); the shrines are the
    chapters'. Requested as **M4-A2P-1706** (cinematics: act1-chapters).
  - **Waiting:** the Drownbell re-measure, on M3-HER-1168 (creatures).
MERGE-READY @ 3df48256a: M4-A2P-1707, the Act II Continue sweep; M4-A2P-1706 requested.
- 2026-10-31 00:50, **the Lead's 21:46 note: the Ch6 and Ch8 objective rows** (M4-A2P-1708, 5f317889c).
  - **The HUD already does it.** The line slides in by itself only when an objective applies. The empty line (OBJ_NONE,
    or a zone's idle_keys line) waits for the button, and the Where-to-next card says the same. New rows need nothing
    from the UI: the tracker reads them, and validate_data checks their targets.
  - **New guard, test_objective_coverage (2/0):** every location with a zone map (prologue to Ch13) has a main
    objective row, and the empty line on arrival stays hidden. Brine Shoals, Corrow and the Coilspire are KNOWN_EMPTY
    until act1-chapters' rows land. Then the run prints that the entry is stale, without failing.
  - **To act1-chapters:** four mid-zone gaps where the line goes empty unless a cutscene bridges them (list in
    M4-A2P-1708's notes): Haluna's wake after `ch04_shell_set`, Pemakar after `ch05_met_kerrid`, the bell galleries
    after `ch07_tidecup_played`, and Corrow night after `ch09_ebbing_danced`.
MERGE-READY @ 5f317889c: M4-A2P-1708, the objective coverage guard.
- 2026-10-31 01:40, **the Lead's 21:56 note (ADR 0207): Act III UI begins** (my range M5-A3P-1700–1799). The Ch6/Ch8
  objective check came first (M4-A2P-1708, already MERGE-READY).
  - **M5-A3P-1700, the closing credits roll** (act3_ending CR):
    - CreditsRoll and CreditsRollModel, data in `game/data/ui/credits.json`.
    - The roll is timed to `roll_sec` (credits_suite).
    - The beach-rite vignette at 62% fades the roll and its black out and emits `vignette_started(id)` for
      Cinematics. It plays once.
    - Holding Confirm runs it 4x faster (keys and pad). Holding Cancel skips once `credits_seen` is set. The hint is
      filled for the device in use.
    - At the end `credits_seen` is set, and `next_scene` or the title opens.
    - **Tests and checks:** test_credits_roll 4/0; shot `credits_roll` (pending_baseline), viewed; a ui_sfx.json row
      (the end turns the page), audio audit clean; validate_data 0/0; taskboard ok.
  - **LEAD-ASK:** who and what should the credits name? Today they hold facts only: the title, "Original score,
    composed for this game.", the Godot engine (MIT), the fonts (OFL), and the MakeHuman / MPFB2 data (CC0). The
    human's own credit, the tracks' roles, and any wording about how the game was made are the human's call; nothing
    is invented. Until then a 7-minute roll is sparse.
  - **For Cinematics:**
    - play `beach_rite` on `vignette_started`;
    - set `next_scene` to E7's post-credits scene;
    - for audio: match `roll_sec` to credits_suite's length when it's rendered.
  - **Next in Act III UI:** the Kite as the Ch18 hub (KiteMapMenu exists; Act III opens the world map, SPEC §6.6),
    then the optional-content log.
MERGE-READY @ 5c4c9ca6b: M5-A3P-1700, the closing credits roll.

- **2026-10-30, after the Lead's 23:26 note:**
  - **M5-A3P-1700 follow-up (c2b8608b5):**
    - The credits are a scene of their own (`credits_roll.tscn`, `CreditsRoll.SCENE`), for E6 to change to.
    - Vignettes are named by `scene`. One that isn't built yet is passed over, so the roll never holds on black.
    - Request M5-A3P-1701 to cinematics: E6 → credits, the beach-rite scene, and `next_scene` for E7.
    - The credits stay facts-only, per the Lead, while the content question is with the human.
  - **M5-A3P-1702, the Kite's Act III revisits (9a4d0b55f):**
    - Oruvel joins the chart (from ch01_started).
    - Ansedra is listed from Ch13 but greyed "Closed to heretics" once `ch14_declared_heretics` is set. These are the
      new `refused_flag` and `refused_key` fields; `fly()` refuses it.
    - **Tests and checks:** test_kite_map 13/0; `kite_map` rendered with Act III flags into scratch and viewed, with
      no baseline written; validate_data 0/0; taskboard ok; lint ok.
    - The audio audit's UI section is 0. It still exits 1 on three support skills from the integration branch
      (`cut_the_line`, `court_reinforce`, `court_wait`), which is not this track's.
  - **Next:** the optional-content log (Act III's revisits and errands, act3_ch18). Then the ending flow, once
    slice-polish's E7 lands.
MERGE-READY @ 9a4d0b55f: M5-A3P-1702, the Kite's Act III revisits (with c2b8608b5, the credits scene).

- **M5-A3P-1703, the Kite's log (52cd5a5bb):**
  - "The ship's log" on the Kite chart opens a read-only page:
    - the eight revisits (Seen once each side scene has played, with what changed there);
    - the seven heirloom errands ("Rhen, for Dace": where it waits, then Carried).
  - The chart's ring follows each row. There are no counts or percentages (act3_ch18 rule 3).
  - Data: `game/data/world/kite_log.json`. Model: KiteLogModel.
  - Declared `ch18_revisit_<town>` (8 flags). Request **M5-A3P-1704** asks cinematics to set them as each revisit
    scene plays; nothing sets them yet.
  - **Tests and checks:** test_kite_map 15/0; shot `kite_log` (pending_baseline), rendered and viewed;
    validate_data 0/0; taskboard ok; lint ok; audio audit UI 0.
  - **Next:** the ending flow, once slice-polish's E7 lands. Meanwhile, more Act III UI per ADR 0207.
MERGE-READY @ 52cd5a5bb: M5-A3P-1703, the Kite's log.

- **M5-A3P-1705, the Vowbound menus lose names (80f0fdcc3):**
  - A Vowbound whose `released_flag` is set leaves the battle Call list (`BattleVowboundHud.bound_ids`) and the
    Status page's Bound line, which now shares that rule. There is no animation (act3_ch20 §9).
  - **For combat (M5-A3P-1013):** add `released_flag` (`ch20_<id>_released`, already declared) to the six
    vowbound.json rows. The UI reads it as soon as it's there.
  - **Tests and checks:** vowbound 119/0 and status 57/0. Freeing the sandbox fixes the bound_ids test's leftover
    node, which was there before. validate_data 0/0; taskboard ok; lint ok.
MERGE-READY @ 80f0fdcc3: M5-A3P-1705, the Vowbound menus lose a name on release.

- **M5-A3P-1706, the ledger page for Ch17 B05 (dd8d136e1):**
  - LedgerReader writes Dace's entries (`ch17_ledger_page_*`) on a page under "Dace Sallow's ledger". They
    still caption below.
  - Each held `turn_page` gate turns the page when it ends. Past the last entry the turns land on blank pages.
  - It takes no input and fades out when the scene ends. Sound: page_turned → ui_page.
  - **Request M5-A3P-1707 (cinematics):** call `LedgerReader.mount(host, sequencer)` before `ch17_the_ledger`
    plays.
  - **Tests and checks:** test_ledger_reader 3/0; shot `ledger_reader` (pending_baseline), rendered and viewed;
    validate_data 0/0; taskboard ok; lint ok; audio audit UI 0.
MERGE-READY @ dd8d136e1: M5-A3P-1706, the ledger page.

- **M5-A3P-1708, the Vowbound answers (a27a38bc0):**
  - B09's hook. As Kesh is called she answers over herself, after Asha's call bark: "I hold. Call, and I will come."
    until `ch17_chose_the_unbinding` is set, then "You chose. A thousand years, and one of you finally chose."
  - The lines are the script's own keys, from `game/data/ui/vowbound_answers.json`.
  - No shot changes: captures read no flags.
  - **Tests and checks:** test_battle_barks 6/0; vowbound 119/0; validate_data 0/0; taskboard ok; lint ok.
MERGE-READY @ a27a38bc0: M5-A3P-1708, the Vowbound answers (Ch17 B09).

- **Small items:**
  - **M4-A2P-1708:** dropped the stale KNOWN_EMPTY entries. Ch6 and Ch8's objective rows have landed, so
    test_objective_coverage now holds every mapped zone (2/0).
  - **M5-A3P-1709, request to progression (design):** kite.json `secrets` is empty, so every chart search finds
    nothing. Design names the secret places; the menu reads them as they are.
  - Fixed M5-A3P-1702's reviewer to `progression`; the board has no design role.
- **Blocked or waiting, not idle:**
  - **The ending flow:** waits on E7's staging (M5-A3P-1015, todo). When E7 has a scene, set credits.json
    `next_scene` and the beach-rite vignette's `scene` (request M5-A3P-1701).
  - **The Drownbell re-measure:** waits on M3-HER-1168, in review.
  - **Mounts in the cinematics lane:** M5-A3P-1704 (revisit flags) and M5-A3P-1707 (the ledger page).
  - **For combat (M5-A3P-1013):** `released_flag` in vowbound.json.
MERGE-READY @ 9807c2d55: M4-A2P-1708 (KNOWN_EMPTY dropped) and M5-A3P-1709 (request), docs and tests only.

- **Act I and II requests, which come before Act III (ADR 0207):**
  - **M3-HER-1153:** BattleChoreo checks a leaving stand-in is valid before the cast. Its freed-cast lint row is
    gone (freed_cast_lint: 0 new); choreo 58/0.
  - **M3-UI-1242, answered:** the Act II objective rows were rewritten (M4-A2P-109). None ends on a later chapter's
    start; qa_threads 1/0.
  - **M4-A2P-1004, answered:** F1, F5 and F8 were already fixed in the first-hour pass; the task names the tests.
  - **M4-A2P-1007:**
    - A20: a new-Swell-mode tip on the first field after play unlocks a mode.
    - A8: Echo's help names its copy and reads as it.
    - A13: a cure names what it cures, so Cord Lift lists all seven.
    - The other rows are answered: A5 and A9 wait on M3-UI-1240/1241; A1, A2, A18 and A19 are already met.
    - Tests: tutorial_tips 10/0 and battle_help_lines 2/0.
- **Full battle suite after these pushes:** 871 run, 1 failed. The failure is not this track's:
  `test_battle_act2_ability_vfx::test_every_act_two_foe_skill_has_its_own_effect`. The flat-engine's `flat_pulse` and
  `engine_churn` (combat, M4-A2P-1200, fa9ac41ff on the integration branch) have no ability effect yet. That is for
  rendering or VFX, and nothing in this track touches skills.json or the effects.
