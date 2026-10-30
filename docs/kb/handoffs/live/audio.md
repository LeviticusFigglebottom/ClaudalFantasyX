# Live log: audio (branch `claude/audio`)

## FROM 2026-10-29 (Lead `session_01Bg3iP7cPGyjbX4CyniBahc`; integration `claude/new-session-mj8c3c`)
Session `session_01UPFyE9L9BA3QodpCNJEfAs`. Brief: the final-quality audit of Act I sound as played, on lead/gate-big18 (M3-AUD-864). Newest first.

- **MERGE-READY (tools and docs): the Act II audio inventory.** `tools/audio/act1_audio_audit.py --act 2` audits Ch10–Ch16 with the same sections as the Act I gate, report-only (exit 0). Act I behaviour is unchanged: still 0 items and still the gate. The inventory is in `docs/kb/audio/act2_audio_inventory.md`, 45 items: 14 zones with no music row or bed, 14 with no footstep ground, 4 borrowed creature voices (root_crab, fen_leech, scree_crawler, rim_crawler), `unravel` silent, and 12 "no zone yet" notes. A new test checks that the Act II scope runs and leaves the Act I gate as it was. Checks: test_act1_audio_audit (5) and test_audio_data OK; validate_data 0 errors.
- **BACKLOG EMPTY (10-30):** the Lead's Act II prep item and its follow-up are done and pushed. act1_gpu_qa has no audio rows, and no listening notes have come in. Everything else in Act II waits on ADR 0203's gate (`act1-complete`) and on Story's beat sheets.
- **MERGE-READY (docs only): the Act II cue sheet, `docs/kb/plan/act2/audio/act2_cue_sheet.md`, `draft: pre-gate`** (the Lead's 10-30 item; ADR 0203 preparation; no synth source written).
  - **Contents:** for every Act II zone, set piece, battle tier and cutscene (Ch10–Ch16): the mood, the instrumentation inside the self-synthesized palette, the key and tempo, the loop length and the transition rules. The existing finals' keys and tempos were read from their sources. It also lists 23 new SFX families Act II needs, and maps everything to M4-A2P-090…093 and M4-AUD-1001.
  - **Proposals:** `battle_heretic` (a Ch14+ regular-battle variant), `court_steps` (the step-hold), `peace_wedding_break`, `kesh_memory` (Drowned Choir under the muffle), `ysolde_confession` (a reprise), and the footstep surfaces `root`, `snow` and `slate`.
  - **Checks:** validate_data 0 errors; taskboard --check; banned terms clean. Merged the integration branch (d987cc6b) first.
  - LEAD-ASK: `battle_heretic`: a variant regular-battle cue from Ch14 on, or keep `battle_standard_v2` for all of Act II? Default: the variant.
  - LEAD-ASK: `sefir_go_home` has the Order **sing** ORDER_HUM, once, as the lullaby, and Liss sings the current-song in `hollowmere_answers`. Both touch the bible's "the Order hums; only Cantors sing". Default: sung, flagged to Narrative.
  - LEAD-ASK: new footstep surfaces `root`, `snow` and `slate` for the Ch10/Ch12 kits: env-art marks them. Default: yes.
  - LEAD-ASK: the pyre-raft (Ch15 C7) and Ysolde's confession (Ch12 C4) as reprises of Act I cues (`hush_first_verse`, `ysolde_theme`) rather than new cues? Default: reprises.
- **BACKLOG EMPTY (M3-AUD-864 done, pushed):** coverage (the audit is at 0 in every section and now gates), quality (loudness, seams, determinism, peaks, on-the-beat transitions with no hard cuts) and the listening pass (docs/kb/audio/act1_listening_report.md, with its verdicts) are all done. The task is in review (qa). What's left waits on others: the Lead's merge (PROVENANCE union), the PC's real-speaker listening (PC-QUEUE), and the human's listening notes (ADR 0042).
- **MERGE-READY @ c018f028 (claude/audio): M3-AUD-864, the final-quality audit of Act I sound as played.** Merge note: PROVENANCE.md needs `tools/dev/merge_union.py` against big18 (append-only rows on both sides); after that, big18 + this branch gives audit 0 items, validate_data 0 errors and test_act1_audio_audit OK.
  - **LEAD-ANSWERED (LFS):** as the Lead directed, the 58 new files (0.69 MiB, all small) ship as plain git at `assets/audio/sfx/battle/abl_swell_*` and `assets/audio/sfx/cutscene/cs_*`, byte-identical to the LFS renders. The branch was rebuilt on origin/claude/audio, so no commit names an LFS pointer, and .gitattributes is untouched. **ADR 0174** raises the plain-git audio budget from 72 to 73 MiB, because these files left 72.52 MiB against 72. The Swell finishers moved to their own source, `assets_src/sfx/act1_swell_finisher_sfx.py`, which keeps their seeds. Nothing over 5 MB is waiting on LFS.
  - **Checks on c018f028:** validate_data 0 errors; taskboard --check; test_audio_loudness and test_audio_data OK (48, the size budget included); test_act1_audio_audit OK (now a gate); Godot `--filter=audio` 175/0, `music_transitions` 7/0, `cutscene_sound` 3/0, and earlier `music` 10/0 and `battle_audio` 22/0; gdlint and gdformat clean; every re-render byte-identical twice. **Skipped:** screenshots (no scene or shader touched); Blender (no Blender source).
  - **Not audio's:** `--filter=cutscene` has one load failure, `tests/unit/test_cutscene_vfx_hosts.gd`, which names `CutsceneMotes`, a class that is on neither the integration branch nor big18 (M3-ARC-1326).
  - **Listening pass:** corrow_aftermath (the rain under the string) and pilgrims_wake (the low-mids cleared) were revised. raid and undertows_reach's first stem are noise-led by their briefs and stay as they are. The full table and verdicts are in docs/kb/audio/act1_listening_report.md.
- **Done (checked on big18 + this branch in a scratch worktree):**
  1. **big18's 5 new ability gaps closed:** Kerrid's and Liss's Swell finishers (`long_hold`, `three_reel_charge`) have their own sounds, `abl_swell_weighted_swing` (the flat iron sweep and the wet sand) and `abl_swell_reel_stop` (the brass ring locking, the salt-glass flash). `grip_the_stair`, `rope_dive` and `hand_closes` play their skill's own row instead of `status_apply`. They're appended at the end of the ability JOBS, so every earlier render stays byte-identical (checked).
  2. **Cutscene actions:** 102 Act I `@anim` clips played nothing. 28 new foley kinds (`assets_src/sfx/act1_cutscene_foley.py`, 56 files, plain git per ADR 0174, deterministic) cover the handled things: the doors of Kahre's chamber and the crown pavilion, the sail over the hatch, the seized key, Kell's beacon, the brand in the brazier, rope, crockery, paper, ink, spears, sand, the Matron unfolding. Pure gestures map to `''`, silent on purpose.
  3. **The audit widened and is now a gate:** new sections Cutscene actions, Battle events (element hits, heal, status and ticks, KO, openings, outcomes, Rim break, each Act I Vowbound's call sting, the items, Swell finishers, choreo styles and weapon accents), Footsteps (every Act I level names its ground; ten fell to the default) and UI core (cursor, confirm, cancel, error, each hook's rows on disk). `test_act1_audio_audit` fails on any open item. **All sections are 0** on claude/audio and on big18 + claude/audio.
  4. **Music transitions on the beat:** MusicDeck held no beat. Now a change with a fade waits for the next beat of the cue sounding (the beat halved until it's ≤ 0.6 s, mix.json `beat_sync_max_wait_sec`), and a resumed cue picks up on a beat of its own. The 18 Act I cues without a `.loop.json` get a grid from their sources, or `"free"` (sung, rubato, drones). `test_music_transitions` (7 tests) also checks that every music fade the game asks for is at least `min_fade_sec` 0.2 s (no hard cuts).
- **Checks run:** validate_data 0 errors; test_audio_loudness and test_audio_data OK (48); test_act1_audio_audit OK; Godot `--filter=audio` 175 run, 0 failed; `--filter=music_transitions` 7/0; gdlint/gdformat clean; render determinism identical. 

### PC-QUEUE
- Listen on real speakers: the 28 new cutscene foley kinds in their scenes (levels against the lines), the two Swell finishers over their contacts, and zone/battle/cutscene changes landing on the beat (Haluna → battle → back, Ch3 shrine → first verse).

## NEW ACCOUNT (from 2026-10-25)
Session `session_01Wmj8xaLtwcqiS3qwC6PciW`. Integration branch `claude/undertow-lead-handoff-ze8rrn`. Newest first.

- **BACKLOG EMPTY (Act I audio, ADR 0041). Integration (ADR 0042) is merged into claude/audio, and every check was rerun on the merged tree. Reasons, item by item against the Lead's 10:55 list:**
  - **raid_hound and slag_tortoise:** their own voice, hit and death sets were written for these designs ("the Order raid's lean coursing dog in a branded leather harness"; "a terrace tortoise under a shell of cooled slag"). M3-CRE-655/660 re-modelled their geometry on the same rig, clips and contact times. The hound's set already has the harness's metal rings on every event and a four-pad trot with claws. No re-render is needed, and the plain-git budget has about 0.2 MiB left.
  - **Reef crabs and polyps:** reef_crab, wreck_crab and wallcrab each have their own set; so do spawn_polyp, wall_polyp, oil_slug and tower_limpet. The audit's Enemies section (Act I foes, shared files flagged) is 0.
  - **Spar-Wraith and Cinder Matron:** each has its own set, its own intro sting (b7b31ec65), and its abilities' own sounds (5c31931bc).
  - **Ilun on creatures-b's new actor:** his call, rise and dismissal (`ilun_call`, `ilun_rise`, `ilun_sink`, M3-AUD-846) are driven by the summon choreography's moments for his combatant id, not by the model, so they play on the manta as on the stand-in. His clips `rise` and `dismiss` are those moments. `defend` and `victory` are the battle's own rows. `release` is Ch20 (Act III), so paused.
  - **Act I loop and loudness pass:** `tools/audio/act1_loop_check.py` on the merged tree found 41 files and 0 problems: every zone's music loop and every bed is click-free and in budget, with each bed about 10 LU under its music.
  - **Audit:** `tools/audio/act1_audio_audit.py` is 0 in every section (zones, enemies, battles, intros, abilities, skills, cutscenes, UI, temp notes). validate_data reports 0 errors.
  - **ADR 0042's music bar** (loudness, seams, deterministic renders, every `@music` resolving) is met: test_cutscene_music_resolves passes.
  - **Waits on others:** the human's listening notes, which ADR 0042 turns into audio tasks; and the one non-audio cutscene failure (test_act1_cutscene_walks, ch04_shell_is_set, staging).

- **MERGE-READY: the Lead's 09:15 check. The sequencer really does play the music.json cue.**
  - `CutsceneSequencer._cue_music` calls `CutsceneSound.music` first, which hands the cue to `Audio.play_music` and the deck. Only an id with no cue falls back to `music_dir/<id>.ogg` and its stand-in.
  - New test, `test_every_act1_music_id_plays_its_real_file_on_the_deck`: for each Act I `@music` id it runs that path and asserts that the deck is playing the cue with its own file loaded, every stem of a stem cue included. 3 run, 0 failed.
  - Cutscene suite (`--filter=cutscene`): 87 run, **1 failed, and it isn't audio's**.
    - The playthrough in test_cutscene_sequencer passes (`hush_first_verse` on the deck).
    - The failure is `test_act1_cutscene_walks::test_every_act1_cutscene_walk_stays_on_the_floor`: in ch04_shell_is_set, Asha is 0.16 m off the floor, Toma 0.60 m and the Player 1.50 m.
    - It's cutscene staging (the Ch4 owners, act1-chapters/hero motion). This branch changes no scene, mark or walk data.
    - (My first note said the suite passed. That run had been cut off by a timeout, and this replaces it.)
  - **Already done, as posted above:**
    - Every Act I creature has its own voice, hit and death sounds, and each boss intro its own sting.
    - The Act I loop and loudness pass found 41 files, 0 problems.

- **MERGE-READY (claude/audio @ fbede303b, gpu/gate-big14-shots merged): the Lead's 08:59 asks.**
  - **test_field_audio::test_change_rows_and_live_hooks:** the gate ran on a commit before my 9c6fea374, which made ReefballOutfitterMenu live. On this branch the test passes (22 run, 0 failed).
  - **The @music seam (M3-HER-1146, 12 items):** the sequencer has resolved through music.json since M2-AUD-07 (CutsceneSound.music plays the cue on Audio's deck, stems and LFS files included). It was the inventory's scanner that still read only `music_dir/<id>.ogg` plus `music_stand_ins`.
    - `tools/placeholder_audit.check_audio` now tries the music.json cue first, as the runtime does. Its audio items went from 12 to 0, and test_placeholder_audit still passes.
    - **For integration-qa:** please regenerate docs/kb/qa/act1_final_inventory.md, which I didn't edit.
    - New test, `tests/unit/test_cutscene_music_resolves.gd`: every Act I `@music` id is a music.json cue whose files exist, and none falls back to a stand-in. 2 run, 0 failed.
  - **The new Act I creatures and boss intros, and the loop/loudness pass, are already done** (posted above):
    - Every Act I creature model has its own voice set.
    - The six boss intros have their own stings (b7b31ec65).
    - The 86 abilities and the swing/reel Swell styles have their own sounds (5c31931bc).
    - act1_loop_check found 41 files and 0 problems (937b9bf8f).

- **MERGE-READY: M3-BPR-421, every Act I ability heard as itself (claude/audio @ 5c31931bc). The Act I audio audit is at 0 in every section.**
  - **73 new ability sounds** (Git LFS), each made from its effect's note:
    - Rhen's cuts; Asha's mend, haste and ward; Toma's shell breaker, challenge and stair.
    - Ysolde's ember, frost, hex and written light; Kerrid's anchor, fluke and line; Liss's lamp flash, reel and hoist.
    - Every Vowbound ability, and each foe's in its creature's family.
  - **13 boss and set-piece mechanics** share their skill's own row (deduped to one play).
  - **The Swell styles:** Kerrid's `swing` (whoosh_swing → swell_kerrid) and Liss's `reel` (reel_whir → swell_liss) have their own sounds, with crest times in `peaks`.
  - **Tests:**
    - test_battle_audio was updated: Ember plays `abl_ember`, with the fire hit under it.
    - Godot `--filter=audio`: 175 run, 0 failed.
    - The Python loudness, data, audit and choreo tests pass, and validate_data reports 0 errors.
  - Review: combat (the request's owner).
  - **Note for the Lead:** six `.gd.uid` files for big14's scripts (tests/integration/test_qa_*.gd, test_battle_boss_camera, test_battle_swell_finishers, tools/placeholder/scan, tools/vfx/boss_camera_sheet) were never committed. My import generated them. I've left them untracked, because they're their owners' and conflicting uids would collide.

- **MERGE-READY (claude/audio @ 937b9bf8f, carrying big14): the Lead's 04:44 asks.**
  - **Blockers big14 lifted, closed:**
    - The three stem cutscenes play whole on the deck: M2-AUD-07, plus the `undertow_reach` alias cue. M3-AUD-834 is done.
    - The Reefball outfitter's hook is live, tested on the real class.
  - **(1) Listening-proxy pass** (`tools/audio/act1_loop_check.py`, report in docs/kb/audio/act1_loop_check.md). It covers every Act I zone's music loop and ambience beds, decoded from the shipped files: **41 files, 0 problems.**
    - Seams: the worst jump is ×3.68 (limit 10) and the worst flux ×2.84 (limit 3).
    - Music is at −16.0 ±0.15 LUFS, beds at −26 ±0.3.
    - Each bed sits 9.7–10.1 LU under its music.
    - A test, test_act1_loop_check, runs it.
  - **(2) The new Act I creature models:** every one of the 14 Act I creature shots has its own voice set (audit Enemies 0, scoped to Act I). Ethren, Hesk and Nhoa are Act II, so paused.
  - **Boss intros:** each of the six bosses that shared `sting_boss` now has its own intro sting, plus a reduced-audio twin, in Git LFS. The audit's Intros section is at 0, and test_battle_stings was updated.
  - Godot `--filter=audio`: 175 run, 0 failed, 0 left nodes (a CanvasLayer leak in my codex test is fixed).
  - **Next, in progress:** M3-BPR-421. **86 Act I abilities still borrow a generic hit, heal or status sound**, and the `swing` and `reel` Swell styles are stand-ins. Each gets its own.

- **Big14 (lead/gate-big14) is merged into claude/audio. The blockers it lifted are closed (9c6fea374):**
  - The cutscene sequencer now plays music.json cues on the deck (M2-AUD-07), so the stem cutscenes play whole.
    `undertow_reach` became an alias cue. M3-AUD-834 is done.
  - The Reefball outfitter is live, tested on the real class. ShrineTravelMenu was already live.
  - **The audit was widened** (Act I scope: Ch10+ foes and skills are skipped). It now has **Intros** (each boss its own
    sting) and **Abilities** (each Act I skill's effect its own sound, M3-BPR-421).
  - **What it finds now:**
    1. **6 boss intros share `sting_boss`:** hullgnaw, bottle_hermit, spar_wraith, cinder_matron, inquisitor and the Reach. Only the Drownbell has its own. **Doing now.**
    2. **86 Act I abilities borrow a generic hit, heal or status row** (M3-BPR-421), plus the `swing` and `reel` Swell styles. **Next, after the Lead's seam pass.**
  - **The 14 new Act I creature models (big13/creatures-b) all have their own voices.** Hits and deaths come from the
    engine, and the new idle/hit clip variants need no sound of their own. Ethren, Hesk and Nhoa are Act II, so paused.

- **M3-AUD-861, more Act I gaps closed (pushed):**
  - **The Ch8 boss played the default battle music.** The `undertows_reach` encounter now plays its own three-stem cue: `dark` (60% HP) brings in stem 1 and `breach` (30%) stem 2.
  - **The seawall's three waves** (`ch08_stair_hold_1..3`) play `seawall_hold`, each starting with one more stem (aliases `seawall_hold_rope` and `seawall_hold_last`).
  - The audit has a new **Battles** section (every boss fight has its own cue, and every stem phase a row), at 0. A test was added to test_battle_audio.
  - **Footsteps:** Oruvel and the ferry are wood; Haluna's wake, the Brine Shoals and Corrow's night strand are sand. Before this, every zone fell back to stone.
  - The audit's 5 remaining items are unchanged, all other tracks' (M3-AUD-834; claude/ui).

- **MERGE-READY: M3-AUD-861 and M3-AUD-863. The Act I audio audit is down to 5 items, all of them other tracks' blockers.**
  - **Ysolde's theme final:** a 91.4 s loop with a lower zither answering her held notes. It replaces the sketch
    at the same path so her Ch4 cutscenes play it. 802 KB, within budget, and byte-identical to the composer's
    render. dace_ledger, which borrows her zither, still renders byte-identical.
  - **Still blocked:**
    1. **M3-AUD-834 (cutscene owner, `game/cutscene/**`):** three cutscenes play only stem 1 (ch01_the_rising,
       ch08_first_down, ch08_the_reach). **This is the one Act I audio gap I can't close from audio's files.**
    2. **claude/ui:** ShrineTravelMenu and ReefballOutfitterMenu go live when it merges. Their hooks are written.
  - Rerun the audit at any time with `python3 tools/audio/act1_audio_audit.py`. Reviews: integration-qa for 861, design for 862 and 863.

- **MERGE-READY: M3-AUD-862, the prologue's score** (`prologue_dusk`, Git LFS).
  - The prologue zone's cue: MEL_A on a breath flute over a drone on A.
  - A 30.5 s intro timed to the scene: the lantern's chord at 12.5 s, and the voice band held 21 dB down under the line.
  - Then a quiet 24 s loop. −16.00 LUFS, byte-identical to the composer's render.
  - **The audit's Zones section is at 0.** Review: design.
  - Next: Ysolde's theme final (M3-AUD-863), with a composer. It replaces the sketch at the same path, because the sequencer reads `<music_dir>ysolde_theme.ogg`. It has to stay under 0.90 MB to fit plain git's remaining budget.

- **M3-AUD-861 progress: the Act I audit is down from 46 items to 9.** Everything below is pushed; the new audio is in Git LFS under `assets/lfs/audio/` (ADR 0173).
  - **Zones:**
    - Music rows: the causeway, the Tidecup match, Corrow and Coilspire.
    - Beds: the drowned tower, the causeway, the first verse, Haluna's wake and Corrow.
    - **New beds:** `oruvel_raft`, `brightwater_deck` and `coilspire_flues`.
    - `coilspire_flues` now plays coilspire (it was the temple_trial prototype), and `corrow_day` is an alias of corrow_seawall.
  - **Enemies (0 left):**
    - The Ch6 **Inquisitor** has a voice: armour, haft, shield and breath, and his yield rather than a death.
    - wreck_crab (its brass housing), wallcrab (laterite), wall_polyp (the Watcher's hum) and stormgull (static) have their own sets.
    - wickfry owns glassfry's set, since they are the same creature.
  - **Skills (0 left):** 16 boss and set-piece skills now have sounds, including Pell's Storm-Call in his own voice.
  - **UI:** CodexMenu, SettingsMenu, ReadPanel and ObjectiveHud are hooked and tested on the real classes. Godot `--filter=audio`: 173 run, 0 failed.
  - **The 9 that are left:**
    - **The prologue's score** (`prologue_dusk`, M3-AUD-862): with a composer now.
    - **Ysolde's theme is still a sketch** (61 s): its final comes next, through a composer, after the prologue.
    - **Blocked on others:**
      - The three cutscenes playing only one stem, on the cutscene owner (M3-AUD-834).
      - ShrineTravelMenu and ReefballOutfitterMenu, until claude/ui merges.
    - Stale notes (housekeeping).
  - **For the Lead:** a fresh clone needs `git lfs pull` to hear the new Act I files.

- **REFOCUS (ADR 0041; the Lead's 01:12 message, read at 02:55): Act I as played.** Act II/III audio has stopped.
  - The M3-AUD-860 composer (cloudloom, undertow_layers) was stopped before it wrote anything.
  - 19 Act II/III audio tasks are now `blocked` with `blocked-by: ADR 0041`: 804, 805, 831, 836, 837, 839–845, 849, 851, 852, 853, 856, 858 and 859.
  - What had already landed in LFS stays.
  - Ilun, Kahre and Virel are Act I (Ch3, Ch5, Ch8), so their tasks stay open.
  - **The Act I audio audit, M3-AUD-861** (`tools/audio/act1_audio_audit.py`, title→Ch9; 46 items). I'm working through it in this order:
    1. **Wiring only, no renders:**
       - **Unwired ambience beds:** oruvel_underway → `drowned_tower`; saltgrass_causeway → `causeway_wind` + `tidepools`;
         first_verse → `shrine_interior`; haluna_wake → the Haluna night set; corrow → `corrow_seawall`.
       - **Zone music:** saltgrass_causeway, coilspire, corrow (`corrow_seawall`) and tidecup_match all have cues but no zone row.
       - **Cutscenes:** `coilspire_flues` plays the old `temple_trial` prototype; its stand-in should be `coilspire`. `corrow_day` needs a same-piece alias for `corrow_seawall`.
    2. **Enemies:**
       - The Ch6 boss **stillguard_inquisitor is `silent`**. It needs a real voice, hit and death set.
       - Five enemies borrow another creature's voice at a different pitch (reused): wickfry (from glassfry), wreck_crab and wallcrab (from reef_crab), wall_polyp (from spawn_polyp), stormgull (from gull_harrier). Each gets its own set.
    3. **16 silent boss and support skills** (power 0, no hit, heal or status, so only the choreography's accents): rouse_polyp,
       gnaw_coil, recrust_gather, lines_taut, reach_for_stair, grip_the_stair, rope_dive, climb_up, surge_crawler,
       surge_wing, surge_ebb, storm_call(_sound), close_the_hand, hand_closes, breach_gather. Each gets a `battle_sfx.skills` row.
    4. **New beds:** oruvel (the raft town), brightwater_ferry (on the ferry) and coilspire (the flues).
    5. **The prologue has no score**, only the iskarra_dusk room tone under "Listen. This might be the last time I tell it."
       It needs its own cue (`iskarra_vigil` is Ch9's echo of it, so it isn't reused here).
    6. **Blocked on the cutscene owner (slice-polish, `game/cutscene/**`): M3-AUD-834.** Three cutscenes play only the
       first stem of a stem cue: undertow_rising (ch01_the_rising), seawall_hold (ch08_first_down) and undertow_reach
       (ch08_the_reach). `@music` has to go through the MusicDeck so stems play, or the sequencer needs an `@stem` cue.
       **This is an Act I blocker now.**
    7. **Waiting on claude/ui:** the UI hooks ShrineTravelMenu and ReefballOutfitterMenu stay `pending` until their classes land.
  - **Budget:** plain git has about 0.48 MiB left, so new Act I audio goes to `assets/lfs/audio/`, which is already routed (ADR 0173).

- **MERGE-READY: the Act III cues are in Git LFS: 9 objects, 9.65 MiB** (a3a21cce).
  - hollowmere, dace_ledger, the_kite, kite_maiden_flight, iskarra_ruins and iskarra_spire.
  - hesper_and_ilsabet's s0 and s1, stacked at −16.03 (a new stem rule).
  - kerrid_last_night.
  - Each file is byte-identical to its composer's own verified render.
  - Loops are imported with `loop=true`; there are PROVENANCE rows, and music.json has the 8 cue rows from the task files. Zone, encounter and phase rows wait for their scenes and fights; the intended rows are in each note.
  - Checks:
    - test_audio_loudness, test_act2_finals and test_audio_data: OK.
    - Godot `--filter=audio`: 171 run, 0 failed.
    - validate_data: 0 errors.
  - **All audio held for LFS is in now: 43 objects, 34.24 MiB.** That is the Act II finals (23.65), the Kite foley (0.94) and Act III (9.65).
  - Also fixed: three Act II PROVENANCE rows that were missing sources (29d5982b).

- **MERGE-READY: the Act II finals and the Kite foley are in Git LFS: 34 objects, 24.59 MiB** (25.8 MB). Pushed, with
  `git lfs ls-files` checked and the remote blobs confirmed as pointers.
  - `assets/audio/music/act2/`: the 12 zone finals and the four bosses' 2 stems each, 23.65 MiB.
  - `assets/audio/sfx/act3/`: M3-AUD-859's Kite foley, 0.94 MiB.
  - All have `.import` files (looped where their sidecar says) and PROVENANCE rows. All 56 files rendered byte-identical twice and meet their rules.
  - music.json: the 12 zone rows now play `act2/<cue>.ogg`; the sketches stay committed, untouched, as fallbacks. There are new stem rows for mangrove_drowner, lamp_engine, avalanche_ram and wakefin.
  - The bosses' encounter and phase rows wait for the fights; the intended rows are in each note. The Kite one-shots are in a new `sfx_act3.json`.
  - Checks:
    - test_audio_loudness, test_act2_finals and test_audio_data: OK.
    - Godot `--filter=audio`: 171 run, 0 failed.
    - validate_data: 0 errors.
  - No Act I file was moved.
  - **Next:** the Act III cues (8 cues, 10 files: hollowmere through kerrid_last_night), rendered alone, into `act3/`.

- **LFS is live (Lead 00:20):** integration is merged and `git lfs install --local` is done.
  - The Act II finals render (`--act2 --determinism`, 16 jobs) is running. When it finishes they get imported and committed to LFS with their PROVENANCE and music.json rows, and then the Act III cues.
  - test_audio_loudness now skips `music/actN/` in the 72 MiB budget, as validate_data does (1af822b7).
  - `assets/audio/sfx/act3/` (the Kite foley, M3-AUD-859) is **not** routed by .gitattributes. It stays parked until the Lead adds a pattern.
- **MERGE-READY: M3-AUD-858, Ch19's revenant pair and Kerrid's night.** Sources only for now.
  - **hesper_and_ilsabet:** two 90 s stems in E aeolian at 120 BPM over ORDER_HUM as a ground. The two lines never meet: the source checks this at every render. Each stem alone is −19, and the pair is −16.03.
  - **kerrid_last_night:** 73.7 s in D major at 48 BPM, KERRID_STAIR's tread at a steady tempo, ending open on Gmaj9.
  - **For Design and Tech:** the encounter must send `hesper_fallen` and `ilsabet_fallen` (stems_off [0] or [1]); the intended rows are in the task file.
  - Review: design.

- **MERGE-READY: M3-AUD-856, the Ch19 Iskarra cues.** Sources only: six ACT3_FINALS rows, nothing tracked under act3/.
  - **iskarra_ruins:** a 136.8 s loop in A aeolian, 3/4 at 50 BPM. MEL_A two octaves down over the drone on A, with the vigil's rising glass motes and dusk-gold strings.
  - **iskarra_spire:** a 129.2 s loop in E minor at 104 BPM. ORDER_HUM is stretched to a bar a beat as the engine's drone, with the Lamp Engine's tick thickening and just-tuned glass climbing.
  - Both measure −16.0 LUFS, with true peaks under −1.8 dBTP, and both are deterministic.
  - The intended music.json rows are in the task file. Review: design.
  - M3-AUD-858 (the revenant pair and Kerrid's night) is still with its composer.

- **MERGE-READY: M3-AUD-859, the Kite's foley**, sources only, held for LFS.
  - kite_foley.py renders two 40 s deck beds and 14 one-shots:
    - kite_deck: in flight, with both lift engines.
    - kite_deck_dark: after H09, gliding on sail alone.
    - The one-shots: H09's engine stop and lanterns, sail fills, E4's rope strain and landing, the tiller, the ledger chest.
  - Total 0.94 MiB; deterministic; every file at its rule.
  - New `ACT3_SFX` in render_all, rendered with `--act3`, into **assets/audio/sfx/act3/**. Nothing there is tracked; test_act2_finals checks it.
  - **For the Lead, when LFS goes live:** route `assets/audio/sfx/act3/**` as well as the music dirs.
  - Review: env-art.
- **Container restart at about 23:40:** two composers and my render running at once ran out of memory. Both composers
  have been resumed in their worktrees and now render strictly one at a time (they check for another
  `render_all.py --act3` first): Iskarra (M3-AUD-856) and the revenant pair plus Kerrid's night (M3-AUD-858). Nothing
  was lost from git.

- **MERGE-READY: M3-AUD-857, Kahre's and Virel's voices** (backlog: the creatures' newest designs). claude/creatures
  has built both Vowbound, and until now they had only the shared rows.
  - vowbound_sfx.py now voices them. Kahre: a hornbill's boom, the mane's sparks, thunder off the anvil, and the
    hammer on the anvil (A4) as his keepsake. Virel: sailcloth luffing, the seams' fire, and the brass key's ping.
  - Each has five battle events, layers on the call, rise and sink, and `virel` in `no_steps`.
  - Ilun's files are byte-identical. All files are deterministic and within their rules.
  - test_vowbound_sfx.py checks every vowbound.json id. Godot `--filter=audio`: 171 run, 0 failed.
  - **Budget:** shipped audio is 71.52 of 72 MiB, about 0.48 MiB left. Everything large from here waits for LFS.
  - Review: combat.
- **MERGE-READY: M3-AUD-853, the_kite (142 s loop, D major, 108 BPM) and kite_maiden_flight (47 s, its D dorian → D
  major lift lands at about 8.3 s).** Sources only: four ACT3_FINALS rows, nothing tracked under act3/, and the
  intended music.json rows are in the task file. Review: design. The Iskarra pair (iskarra_ruins and iskarra_spire,
  M3-AUD-856) is with a composer.

- **Self-directed backlog (TRACK-RULES, from 22:50):**
  1. **Renders:** none for audio (no shots).
  2. **Todo tasks:** none on claude/audio.
  3. **Requests to audio, all answered by work already on integration:**
     - **M3-HER-1122** (hero-integration QA, 68 sounds and 29 cues) and **M3-AUD-100** (m2-slice): every id they list
       ships on the integration branch (M3-AUD-818..823, plus M3-AUD-833's stand-ins for the alias and stem cues).
       Their runs predate those merges, so they should take the integration head and drop the qa_known.json rows.
       Those files are theirs; I didn't edit them.
     - **M3-CRE-633** (the teardown cast): fixed by 3224c1d8.
  4. **Next act (step 5):** Act III cues for the zones env-art has built (Hollowmere M3-ENV-723, the Kite M3-ENV-725,
     the Lamp Spire M3-ENV-726). render_all.py has `ACT3_FINALS` and `--act3` (assets/audio/music/act3/, LFS, never
     committed until it's live), covered by test_act2_finals. Two composers are on hollowmere and dace_ledger, and
     the_kite and kite_maiden_flight (M3-AUD-852..853); iskarra_ruins and iskarra_spire come next.

- **TO THE LEAD: your 21:42 queue is done. MERGE-READY @ 3fc783ed.**
  1. **Ilun (M3-AUD-846):** his voice (creature_voices `ilun`), and his net-float and wing layers over the summon's
     call, rise and dismissal (choreo_sfx `vowbound.layers`). Floodnet and the ilun_summon sting already existed.
  2. **Iskarra (M3-AUD-847):** the vigil's murmur in `iskarra_dusk` (−26.05 LUFS). Rhen's LanternLight crackles at the
     lamp (CutsceneAudio `lamps`).
  3. **UI (M3-AUD-848):** the battle result's count-up (`ui_count_run` and `ui_count_done`) and the Reefball outfitter
     (buy, wear, refuse; `pending`). The Lattice unlock and shrine travel were already done.
  4. **Creatures (M3-AUD-849):** ridge_lynx, cord_moth, glass_skate, flat_engine and four pitched variants. Every
     creatures.json row on claude/creatures has a voice; the redesigned Drowner keeps its set.
  5. **Mix (M3-AUD-850):** the dialogue duck now takes World −3 dB, and villagers' chat is held over a line.
     mix.md has the layer table and mix_report.md is regenerated.
  6. **Act III (M3-AUD-851):** `motifs.letting()`, the Hush's first cell turned upward, with a test.
  - **Checks on this head:** Godot `audio` 169/0, `battle` 720/0, `cutscene` 69/0, `menu` 238/0 (after M3-AUD-848);
    lint and format clean; validate_data 0/0; shipped audio 71.0 of 72 MiB.
  - **Tools: 1200 tests; the only failure is `test_iskarra::test_the_vigils_stand_on_the_paving` (3 of 7), and it
    is not audio's.** It came in with big12 (env-art's kit against the prologue scene); nothing in my diff touches
    it.

- **TO THE LEAD: the life_audio.gd:124 fix is DONE and pushed:** commit 3224c1d8, on claude/audio since before the big12
  merge. **MERGE-READY @ 217d4f55** (it includes big12, e930595c). Since then: a headless run-and-quit of Haluna and the
  causeway (400 frames each, director and villagers live) prints no SCRIPT ERROR and no freed-object line.

- **Act II boss music: the four modelled bosses' sources are merged (M3-AUD-844/845).** They are mangrove_drowner,
  lamp_engine, avalanche_ram and wakefin. Each has two stems over a 74–84 s loop at −16 LUFS for the stack; the seams
  are clean and the renders byte-identical. 7.2 MB in all, every file under 1.1 MB. The audio waits for LFS, like the
  zones, and the intended music.json phase rows are in each task file.
  - **Open:** Malcor Venn and the Abiding guard wait for their fights; the scene cues wait for Act II's beat sheets.

- **TO THE LEAD: big12 merged in (integration e930595c, a clean merge). MERGE-READY @ 3b9324c4, with the life_audio
  teardown fix (3224c1d8) on top.** Take this head to clear the capture shards' exit 1. Checks on the merged head:
  validate_data 0/0, `--filter=audio` 162/0.

- **TO THE LEAD (TOP item): life_audio.gd:124's shutdown error is fixed. MERGE-READY @ 3224c1d8.**
  - **Cause:** `LifeAudio.advance` cast each watched node (`w["node"] as Node3D`) *before* checking it was alive. A
    zone freed at shutdown therefore raised "Trying to cast a freed object", and the error aborted the step, so the
    dead entries stayed and fired again every frame. There are no signals or timers in LifeAudio.
  - **Fix:**
    - validity is checked before the cast;
    - `_exit_tree` drops every watched node and frees the villagers' step children;
    - ReefballAudio's sphere scan gets the same guard (`is` on a possibly freed reference).
    - I checked the other listeners' casts: they're behind validity checks already, or use `instance_from_id`.
  - **Tests (test_life_audio.gd):** a stand-in villager and layer freed under the listener, and **the real Haluna
    zone** loaded, watched, freed and advanced. On the old code both fail with the exact SCRIPT ERROR; they pass now.
    `--filter=life_audio` 12/0, `audio` 162/0, `reefball` 68/0, with no "freed object" line in any log.

- **Act II: the 12 zone finals' sources are merged (M3-AUD-840..843; claude/audio, pushed).** They are ossa_fen,
  reedhollow, sunken_vey, lowlight, keth_pass, quellan, ansedra, lamp_archive, peace_wedding, unlamped, pale_rim and
  drowned_choir. Each is a 125–157 s seamless loop built on its sketch; the sketches are unchanged.
  - **Numbers:** 17.4 MB measured in all, every file under 2.2 MB and none near 5 MB; −16 ±0.1 LUFS; seams clean;
    byte-identical on re-render (the table is in docs/kb/audio/act2_finals.md).
  - **No audio is committed.** It renders with `render_all.py --act2`. **When LFS is live:** one commit adds the 24
    files, their .import files, music.json rows (swapping each zone row from the sketch to `act2/<cue>`) and
    PROVENANCE rows.
  - **Next:** the four modelled bosses' music (drowner, Lamp Engine, Ram, Wakefin).

- **TO THE LEAD: the big12 causeway test is fixed. MERGE-READY @ befc79be** (lead/gate-big12 merged in, dc10c187).
  - **What changed:** M2-FP-108's final causeway has no tidepool. Its ground is now stone slabs over sand flats with the
    sea below y −0.7. In footsteps.json the causeway's scene ground is `sand` (the flats), and a mesh rule makes
    `causeway_slab*`, `causeway_disc*` and `offering_step*` stone; under the sea's rest plane is water (the existing
    wading rule). The test is renamed `test_the_causeway_is_stone_slabs_over_sand_flats_and_the_sea` and checks the
    real dressed slabs.
  - **Checks:** `--filter=footsteps` 5/0, `footstep` 21/0, `audio` 160/0, `causeway` 13/0; validate_data 0/0.
  - **Full Godot suite on befc79be: 2828 run, 1 failed, and the failure is not audio's.** test_creature_portraits:
    creatures.json's mangrove_drowner, lamp_engine, avalanche_ram and wakefin have no portrait in
    game/data/ui/creature_portraits.json. It comes in with big12 (my branch is identical to gate-big12 in those
    paths). It belongs to the UI or creatures track, and the portraits need a PC render.

- **LFS (ADR 0039) taken in, 10-27 ~19:20.**
  - **ADR 0172 is parked** as a fallback study (its status line says so).
  - **M3-AUD-839:** docs/kb/audio/act2_finals.md lists Act II's 30 final cues with estimates (about 72 MB, all for
    LFS). render_all.py has `ACT2_FINALS` and `--act2`, into assets/audio/music/act2/ and outside the default run,
    the budget and the tests. tools/tests/test_act2_finals.py fails if anything there is committed before
    .gitattributes routes the path to LFS. I have not touched .gitattributes.
  - **In progress:** four composer agents are writing the 12 zone finals from the sketches (M3-AUD-840..843). Their
    sources commit now; the audio stays uncommitted until you announce LFS is live, and then lands in one commit with
    the music.json rows, PROVENANCE rows and .import files.

- **MERGE-READY @ d8cdf928** (big11 merged in). Checks run:
  - **Godot suite on 1ec56d7b: 2758 run, 0 failed.** Since 1ec56d7b, M3-AUD-838 only: `--filter=battle_audio` 21/0,
    `choreo` 56/0, `audio` 160/0.
  - Tools: 1172 tests, and the only failure is test_shrine_gi_bake (slice-polish, M3-ENV-704).
  - Loudness and audio data tests OK; validate_data shows 0 errors (1 warning, env-art's missing offering_step.glb);
    lint and format are clean.
  - **No render request:** nothing here can change a shot.
- **M3-BPR-410 answered (M3-AUD-838):** choreo_sfx.json has a `charge` row (Ram hoofbeats in and out, `whoosh_charge`,
  the weapon contact), marked `pending`, so the checker and test_battle_audio_live accept it before choreo.json has
  the style. **Battle-presentation:** add the style and drop `"pending": true` from `styles.charge` in the same
  commit.
- **The Tamsule shops (M3-C07-05)** use the existing ShopMenu and InnMenu hooks, so nothing new is needed. The
  Tidecup rewards are data only: a sound waits for a reward screen. Ask audio when one exists.

- **TO THE LEAD (10-27 ~19:00): the queue's status, all pushed on claude/audio @ 1ec56d7b.** The full Godot suite is
  running on that head, and its result follows here as MERGE-READY.
  1. **big11 is merged** (a3d138a0). The FieldNpc, WildlifeLayer, BattleImpact and ReefballHud hooks are live
     (a6cec0e7; a smoke test on the real ReefballHud). Tools: 1172 tests, and the only failure is test_shrine_gi_bake
     (slice-polish's, M3-ENV-704). Lint and format are clean.
  2. **The UI screens, M3-AUD-832:** menu motion whooshes (silent under Reduced motion), the title reveal, the save and
     load slots, shrine travel, and the Reefball choices with a scoring glint. ShrineTravelMenu and TitleReveal are
     still `pending` (not in big11). **Next: the Tamsule shops.**
  3. **M3-BPR-410:** next after the shops.
  4. **ADR 0172 prototype, M3-AUD-837:** `tools/audio/build_render.py`.
     - A cold build of 94 jobs takes 26.8 min on 4 CPUs; a warm check takes 1.9 s.
     - 895 of 896 files were byte-identical.
     - The ADR sets out LFS, the render and a hybrid, and asks for a PC render against a cloud manifest before
       deciding. Nothing is switched over.
  5. **Act III planning, M3-AUD-836:** docs/kb/audio/act3_plan.md (the motif map and about 30 cues). It comes to about
     76 MB, so Act III can't ship committed.
  - **Also done:**
    - M3-AUD-831: voices for the Act II creatures.
    - M3-AUD-833: a bug fix. Nine Act I `@music` ids were silent in cutscenes; they have stand-ins now, and a request
      is out (M3-AUD-834: `@music` through the MusicDeck, `@stem`, markers).
    - M3-AUD-835: tamsule_bell's loop click.
    - Six chapter audio tasks moved to review.

- **Full gate at 248dfa76 (all four composer batches merged): Godot suite 2676 run, 0 failed; tools suite 1145
  tests OK.** Since then only the impact_medium re-render (the loudness test is OK) and the mix report. Take
  6a4842eb or later.
- **TO THE LEAD: test_audio_loudness is fixed and pushed. MERGE-READY @ ff064071 (take this head; big11's older audio
  sha predates the fix).**
  - **`sfx/life/*`:** rules in targets.py since c5eeb302 (murmur −26, work −25, gull calls −22, takeoffs −26,
    crabs −30, fish −29).
  - **`impact_medium_1-3`:** re-rendered from source at **−21.2 LUFS**, which passes both its own rule and the generic
    combat rule (−19 ± 2.5). It stays about 3 LU under the hit it supports.
  - **Also on this head, M3-AUD-819 to 822 (all four composers):** every Act I `@music` id now resolves, and
    MUSIC_TODO is empty. Shipped audio is 68.8 MiB of ADR 0171's 72.
  - Checks run: `python3 -m unittest tools.tests.test_audio_loudness` OK; the data and cutscene-file tests OK;
    validate_data 0/0; `--filter=audio` 152/0 on each composer merge. A full suite and the full tools suite are
    running on 248dfa76; their result follows here.
  - Requests out to act1-chapters (Ch1 and Ch5 script timings for the new cues): M3-AUD-829, M3-AUD-830.
- **To the Lead (big11, test_audio_loudness): already fixed on claude/audio since c5eeb302. MERGE-READY @ 0c22d077:**
  `python3 -m unittest tools.tests.test_audio_loudness` passes on this head. big11 took an older sha (4587af3e or
  f5f10d7e, from before c5eeb302), so take 0c22d077 or later.
  - `sfx/life/*` has its own rules in targets.py (murmur −26, work −25, gulls −22/−26, crab −30, fish −29).
  - The impacts are **−24 by design, not a miss.** `impact_medium` is a weight layer under the −18 element hit, not
    a hit, so it has its own rule above the battle default (medium −24, heavy −21, crushing −19, slow-mo −20;
    M3-AUD-816). The same commit adds rules for the cutscene foley and the Act I cutscene cues.
  - 0c22d077 also brings M3-AUD-820 (six Act I cues from a composer agent: the_long_way_round, hearer_hum,
    ysolde_theme, name_board_home, oruvel_theme, tavi_kell).
  - Checks run: loudness, data and cutscene-file tests OK; `--filter=audio` 152/0; the full suite was 2676/0 at
    64e724a2, and since then only M3-AUD-820's music files and data. I already had the `_grounded` fix in
    test_footsteps_slice_zones.gd (cfe3817c); the next integration merge will reconcile it with big11's.
- **MERGE-READY @ 64e724a2 (big9 merged; full gate):** everything through M3-AUD-828. **Full Godot suite: 2676
  run, 0 failed** (with the Act I zone rows and hero-integration's body in); the loudness, data and cutscene-file
  tools tests OK. Skipped: screenshots (the PC's), Blender (none), coverage (no battle/progression code).
- **Merged big9 (integration @ 3b7cbf5e+) at 64e724a2.** Conflicts: two audio tests (I took the Lead's matching
  fixes) and voices.json (I took the new speakers; every one exists, so none is pending). With hero-integration in,
  the real hero body's footsteps now run here: `--filter=foot` 26/0 (including the stall fix), `--filter=audio`
  152/0. A full suite at 64e724a2 is running. I capture no screenshots (the PC renders).
- **MERGE-READY @ 329331f0:**
  - **M3-AUD-826:** villagers step on their routes (each FieldNpc gets a quiet FootstepAudio: cloth, no hero gear).
  - **M3-AUD-827:** the six Act I zone beds and the 17 Ch4–Ch9 voices are live; their scenes and speakers landed.
  - **M3-AUD-828:** Act I's zones play their music (nine zone rows), and its bosses theirs (Spar-Wraith, Cinder
    Matron with its Pour stem, the Inquisitor).
  - Checks run: `--filter=audio` 151/0, `field_audio` 19/0, `voice` 12/0, `audio_runtime` 11/0, `life_audio` 10/0;
    validate_data 0/0; gdlint, gdformat.
  - Checks skipped: the full suite. The zone rows now play music in nine Act I zones, so the chapter tests should
    see it in the next full run, which I'll do with the composers' integration. Also screenshots, Blender, coverage.
- **MERGE-READY @ cfe3817c (FAST-TRACK, footsteps):** verified M3-AUD-802/812 on a scratch merge with
  claude/hero-integration. The real HeroFieldActor.foot_contact steps (26/0). **Found and fixed:** hero-integration's
  walk clip has no footfall markers yet (characters' M2-CHR-12), so its body never emits and the steps came only
  once per 1.6 m. After a stall they now step by distance until a contact comes. **Cherry-pick this with or before
  hero-integration.** Checks run: `--filter=foot` 21/0 here and 26/0 on the scratch merge; gdlint, gdformat.
- **MERGE-READY @ 2bb610de:**
  - **M3-AUD-823:** eight Act I `@music` ids now play the cues composed for their scenes (aliases: oruvel_raft,
    oruvel_underway, haluna_wake, brightwater_crossing, pemakar_terraces, ashcrown_trial, tamsule_port,
    coilspire_flues). A test tracks the rest; their MUSIC_TODO list may only shrink.
  - **M3-AUD-824:** Reefball's sounds bound to the real ReefballMatch (the guessed Ball and Goal hooks are gone).
    A node holding a match in `match` is heard; there is a new `float_ring_bell`.
  - **M3-AUD-825:** the Ashcrown strike trial heard (AshcrownAudio on Ch05AshcrownZone's AshcrownTrial).
  - **ADR 0171:** audio budget 72 MiB to finish Act I. **The Lead's call:** a storage plan (LFS or an audio pack)
    is needed before Act II's finals.
  - Checks run: `--filter=audio` 150/0, `reefball` 55/0, `ashcrown` 11/0; the loudness, data and cutscene-file
    tests OK; validate_data 0/0; determinism identical; gdlint and gdformat.
  - Checks skipped: the full suite (the last was clean at d1fa5c0f; since then only audio scripts, data and the
    reefball audio test changed), screenshots, Blender, coverage.
- **In flight:** four composer agents (M3-AUD-819 Ch1+Ch9, 820 Ch4+Oruvel, 821 Ch5+Ch6, 822 Ch7+Ch8) writing the
  remaining Act I music cues in worktrees. I integrate and gate them when they report.
- **MERGE-READY @ d71abea1 (FAST-TRACK: M3-AUD-816, 817, 818):**
  - **M3-AUD-816, battle impact tiers** on battle-presentation's BattleImpact: weight layers under the element hit,
    a music duck under the hit-stop, and the KO slow-mo swell. The hook is `pending` until claude/battle-presentation
    merges; checked against that branch with pending off. test_battle_ko_once now uses battle-presentation's exact
    wickfry lines, so that merge has no conflict there.
  - **M3-AUD-817, the slice's cutscene pass:** every CutsceneStage actor gets its own footsteps; CutsceneAudio plays
    foley on `@anim`, `@light` and `@vfx` cues (silent through a skip); the prologue plays its new room tone
    `iskarra_dusk` (it had no sound at all).
  - **M3-AUD-818, Act I's 68 cutscene `@sfx` cues:** every one named a file that didn't exist, so it played
    nothing. Four were then fixed to act1-chapters' briefs: barge_pole has no water; Pell's note is a voice;
    staff_bell_shells is in the Ebbing's key; current_song sings **Dace's current-song, now in
    assets_src/music/motifs.py**. A new tools test fails on any `@sfx` without its file; it passes here and on a
    scratch merge with claude/act1-chapters (all of Ch8).
  - **Fix:** the loudness test had no rules for the life, impact and cutscene files. I had pushed 814 and 816 without
    running it. It passes now (c5eeb302).
  - Checks run: **full Godot suite at d1fa5c0f: 2388 run, 0 failed** (GDScript unchanged since); filtered `audio`
    146/0, `cutscene` 43/0, `prologue` 5/0; the loudness test OK; the **full tools suite** (911 tests) OK;
    `render_all --determinism` identical for every new job; validate_data 0/0, taskboard --check, gdlint, gdformat.
  - Checks skipped: screenshots (no scene or shader), Blender (none), coverage (no battle/progression code).
- **MERGE-READY @ 4587af3e (FAST-TRACK: M3-AUD-814):** villagers' chat turns and work, gulls, crabs and fish
  (LifeAudio, 44 synthesized one-shots, 0.6 MiB). The hooks are `pending` until claude/creatures merges (FieldNpc,
  WildlifeLayer); when it does, drop the two `pending` flags in life.json. M3-AUD-815 asks creatures for
  `chat_speaking()` and `startled()`; LifeAudio reads the private fields until then (read only). Integration
  re-merged (only the Lead's log changed).
  - Checks run: `--filter=audio` 134/0 (including test_life_audio 9/0), validate_data 0/0, test_audio_data OK,
    `render_all --determinism --only life_sfx` identical, taskboard --check, gdlint, gdformat. **Smoke test against
    the real classes** (scratch worktree with claude/creatures merged, pending off): validate_data 0/0, and in 60 s
    of creatures' npc and wildlife stages 8 gull calls, 4 takeoffs, 5 crab scuttles, 6 fish darts and 14
    net-mending sounds. The stage has no chat pairs, so murmurs are covered only by the unit tests.
  - Checks skipped: full suite (last clean at f8298577; since then new files plus a few lines in the director),
    screenshots, Blender, coverage (none touched).
- **MERGE-READY @ f8298577:** everything since 261a827d: M3-AUD-812 (FAST-TRACK footsteps), M3-AUD-813 (menu hooks)
  and **M3-AUD-805, Act II sketches II** (six cues: Ansedra, the Lamp Archive, the Peace Wedding, Unlamped, the Pale
  Rim, the Drowned Choir; −16.0 LUFS, TP ≤ −1.4; 3.4 MiB, ADR 0170 budget kept; the wip/ folder is gone).
  - Checks run: **full Godot suite on f8298577: 2367 run, 0 real failures.** test_scene_router_swap failed only
    because that run had no `godot` on PATH (probe exit 127); re-run with PATH set it passed 15/0. Also the loudness
    test OK, `render_all --determinism` identical for all six, `--filter=audio` 125/0, validate_data 0/0,
    test_audio_data OK, taskboard --check, gdlint and gdformat.
  - Checks skipped: screenshots (no scene or shader), Blender (none), coverage (no battle/progression code).
  - Gotcha: a first render writes no `.import`, so the loop flags are synced after the first import
    (`render_all._sync_import`), then imported again. Done here; the .import files are committed.
- **MERGE-READY @ f5f10d7e (FAST-TRACK: M3-AUD-812):** M3-AUD-812, footsteps change surface in every slice zone
  with no level edits: Haluna's sand, the dock's wood (the `dock_haluna` mesh), the shallows' water (feet under the
  sea's rest plane); the causeway's stone and tidepool; the shrine's stone and pools. Also M3-AUD-813, the menu hooks
  after the merge: FormationMenu live, the Key Items tab, refusals through M2-AUD-15's reads; test_battle_ko_once
  lifts wickfry's new model for its primitive case. Integration merged at 261a827d (two task-file conflicts,
  resolved).
  - Checks run: full Godot suite on 261a827d (2355 run, 7 failed: 4 from the uncommitted M3-AUD-805 patch, rendering
    mid-run, and 3 real merge fallout, fixed in M3-AUD-813). Then filtered `footstep` 16/0, `footsteps_slice` 4/0,
    `field_audio` 19/0, `ko_once` 5/0; loudness test OK; validate_data, taskboard --check, gdlint and gdformat
    clean on the committed tree.
  - Checks skipped: screenshots (no scene or shader touched), Blender (none), coverage (no battle/progression code).
  - Verified against claude/hero-integration's real `HeroFieldActor.foot_contact(foot, run)`: the body is the
    controller's `HeroBody` child, as footsteps.json expects. test_footsteps_slice_zones walks it once that merges.
## STATE AT HANDOVER (2026-10-25)

**HANDOVER DONE @ 20ee527f** (claude/audio pushed; nothing un-pushed; no worktree holds unsaved work).

Written for a fresh Lead with no prior context. The branch is **claude/audio**, at ca22f8ae when this was written. The
integration branch is `claude/undertow-lead-handoff-423ixt` (last merged into claude/audio at 2a699ddb).

## Done and merge-ready
- **Last full gate:** MERGE-READY @ 2a699ddb, with the full Godot suite at 2006 run, 0 failed, and the loudness test
  OK. It covers everything through M2-AUD-17, M3-AUD-800 and M3-AUD-801.
- **Merged after that, scoped checks only:**
  - M3-AUD-803, KO-once (verified on a scratch merge with claude/battle-presentation).
  - M3-AUD-802, hero footsteps and foley (84 files), plus the stride and run-flag follow-ups.
  - M3-AUD-804, Act II sketches I (six cues).
  - ADR 0170 (the audio budget is 56 MiB).
  - The checks run on these were validate_data (0 errors), test_audio_data, gdlint, gdformat, Godot
    `--filter=audio` (114/0) and `--filter=footstep`.
  - **Before merging this branch, run the full Godot suite and the loudness test once.**
- **Review queue (41 audio tasks, all `review`, reviewer qa):** `python3 tools/taskboard.py --role audio`. In short:
  - all of M2's audio: the runtime (ADR 0031), the slice cues, battle and field SFX, the mix, reverb and the causeway;
  - Act I music: every chapter, zone, temple and boss theme, including the Stillguard;
  - the M3 SFX sets: choreography, creatures, menus, stings, Reefball and the zone beds;
  - syllable blips, the sphere muffle, the mix pass and the voices;
  - the live hooks (M2-AUD-17, M3-AUD-800, M3-AUD-801);
  - hero footsteps (M3-AUD-802), KO-once (M3-AUD-803) and the Act II sketches I (M3-AUD-804).

## In progress
- **M3-AUD-805, Act II sketches II** (Ansedra, the Lamp Archive, the Peace Wedding, Unlamped, the Pale Rim, the Drowned
  Choir). The sources are committed as WIP; nothing is wired or rendered on the branch. The exact steps are in
  `docs/kb/audio/wip/README.md` (apply the patch, render, import, run the checks).

## Exact next steps, in order
1. **Finish M3-AUD-805** with docs/kb/audio/wip/README.md.
2. **Merge the integration branch,** run the full suite and the loudness test, then post MERGE-READY.
3. **Switch on the pending hooks as their targets merge.** A `"pending": true` row means its target isn't on
   claude/audio yet. When it lands, drop the flag; validate_data then checks the real names. Run the filtered tests.
   - **claude/hero-integration and claude/characters:** footsteps take `HeroBody.foot_contact(foot, run)` (confirmed
     by hero-integration, M3-AUD-810). Walk Rhen in Haluna and check `FootstepAudio.contact_source` is `signal`.
     Tune `foley.cloth_db` and `gear_db` in footsteps.json by ear.
   - **claude/battle-presentation:** `battle_stinger` and `boss_intro` are emitted only there. audio needs no change;
     test_battle_audio_live.gd already allows both orders.
   - **claude/m2-slice:** the zone beds (ambience.json, six `pending` zones), 17 voices (voices.json `pending`), and
     the zone and encounter rows for the Act I cues (each cue's `_note` in music.json names its scene or encounter).
   - **claude/menus:** FormationMenu (ui_sfx.json). Also requests M2-AUD-15 (public reads for refusals) and M2-AUD-16
     (the BattlePause leak).
   - **The Reefball minigame:** ReefballMatch, ReefballBall and ReefballGoal are guessed names in reefball_hooks.json;
     rename them to the real classes.
   - **The level owners (M3-AUD-811):** surface areas for wood and water steps.
4. **Re-run the mix report** after each batch: `python3 tools/audio/mix_report.py --out docs/kb/audio/mix_report.md`.
5. **Then:** more Act II, and Act III planning.

## The human's listening verdict: pending
Nothing has been heard by the human. Every check is a measurement. `docs/kb/audio/listening_notes.md` lists what to
listen for in each cue and set (M2 and M3 sections). The most important to hear are:
- the slice cues;
- the blip level (voices.json `mix_db` +6, M3-AUD-23);
- the Tamsule Bell bed's loop point (a possible tick);
- the Act II sketches' instrument voices.
When the verdict comes, revise the source (never the .ogg) and re-render with `--determinism`.

## Known bugs and open requests
- Requests out to other roles: M2-AUD-07, M2-AUD-08, M2-AUD-09, M2-AUD-12, M3-ARC-01, M2-AUD-15, M2-AUD-16, M3-AUD-810
  and M3-AUD-811.
- The menus' own tests leak about 250 GDScript resources at exit, and the battle scene keeps two menu scripts
  (M2-AUD-16: `BattlePause._ready` never frees the menu it builds to read the layout). This is not audio's, and it
  isn't a test failure.
- `test_scene_router_swap` (the boot frame) is sensitive to CPU load. It fails only when renders run alongside it;
  it passes on a quiet machine. It is not audio's.
- The repo-size question: shipped audio is 47.1 MiB of the 56 MiB budget (ADR 0170). The full game needs a storage
  plan (Git LFS, ADR 0005) before Act III's cues.

## Gotchas (hard-won)
- **Loops:** .import files must have `beat_count=0` (Godot 4.6 counts beats from the file start).
  `render_all._sync_import` writes them; re-run the import after a render. The seam gate is under 3x spectral flux:
  start a sixteenth before the downbeat (`downbeat_offset_s`).
- **Balance from measurement only:** render, read `LoopMixer.bus_lufs`, set gains, re-render. The piano model is
  about 31 dB below the breath flute, and the flute speaks 50–80 ms late (FLUTE_PRE 0.065).
- **Mono files** measure as mono: ffmpeg's upmix adds −3 dB.
- **Hooks by name, never class_name stubs.** Stubs would collide on merge. Listeners never write game state
  (ADR 0031).
- **Tests must not leave real playbacks.** The headless driver keeps them past the end of the run ("resources still
  in use"), and the game's own Audio autoload hears every node a test adds. Record through the listeners' player
  Callables, or name stand-ins (the `audio_class` meta) after add_child.
- **Zone music loads on a worker thread.** Tests call `dir.flush_pending()` after apply_zone. A big7 merge once
  dropped that line.
- **Append-only files:** PROVENANCE.md and the string tables merge with `tools/dev/merge_union.py`, and PROVENANCE
  rows go in their own commit. Agents' render_all.py edits sometimes glue a comment onto the previous line; check
  the JOBS list after a merge.
- **Id blocks:** new audio tasks are 800–899, ADRs 0170–0179, and handoffs are named
  `<date>-audio-audio-<n>.md`.
- **Never kill processes by pattern.** Give each run its own XDG_DATA_HOME and scratch folder.
- The Lead's session sometimes refuses cross-session messages ("needs a trusted device"). The live log is the
  channel that always works.


Environment: cloud session `session_01FtDSYm5dJHkdC3RqXsDjif`, branch `claude/audio` (from the integration branch
`claude/undertow-lead-handoff-423ixt` at 1023a25). Role: Audio. The Lead reads this file; newest state first.

## MERGE-READY @ 7085dff5
Items: M3-AUD-08 Hullgnaw + Spar-Wraith, M3-AUD-09 Cinder Matron + Undertow's Reach (stems), M3-AUD-10 Oruvel + the living
funeral, M3-AUD-11 Brightwater ferry + Brine Shoals, M3-AUD-12 Tamsule + the Iskarra vigil, M2-AUD-13 causeway beds (all
`review`); fixes: loop imports `beat_count=0` (intro cues wrapped early in Godot), zone/battle music loads on a worker
thread, budget 48 MiB. Checks run: integration merged (up to date); full Godot suite 1529 run, 0 failed; validate_data 0;
taskboard --check OK; tools/tests audio (data + loudness, every file on target) OK; per-cue `render_all --determinism`
identical (by each worker). Skipped (Lead runs at merge): screenshots, Blender (no Blender source), coverage (no
battle/progression code).

## MERGE-READY @ c99e6f2b
`tools/ci_local.sh` exit 0 (HYMN_SKIP_BLENDER=1: no Blender source touched): 1499 Godot tests, 0 failed; 75/75 shots
(rmse 0); coverage battle 99.95 % / progression 96.52 % (within baseline); boot smoke clean. Integration branch merged
at f95b27cb. Items: M2-AUD-01..06 and M2-AUD-10/11, M3-AUD-01..07 (all `status: review`). Since c99e6f2b only docs.

## State (2026-10-24, later)
- **Merged into claude/audio since the last MERGE-READY:** M3-AUD-08 Hullgnaw + Spar-Wraith, M3-AUD-09 Cinder Matron +
  Undertow's Reach (stems), M2-AUD-13 causeway beds, M3-AUD-10 Oruvel + the living funeral (all `review`), and the
  integration branch at f8b0db07.
- **Fix:** every loop now imports with `beat_count=0`. Godot 4.6 loops an Ogg after `beat_count` beats counted from
  the file start, so cues with an intro (both battle themes, the sea bosses) wrapped early by their intro and skipped
  the end of their loop. The audio budget is 48 MiB (mix.md "Budget"; ~35 MiB used once these land: a repo-size
  question, Git LFS).
- **In progress:** M3-AUD-11 ferry + shoals routes and M3-AUD-12 Tamsule + the Iskarra vigil (worktree agents).
  Done and merged; queue empty.
- **Filed for m2-slice:** M2-AUD-12 (causeway zone rows, the B05 crossfade, the B12 coda).

## MERGE-READY @ e24a98cd
- **Items:** M3-AUD-13 choreography SFX, M3-AUD-14 creature voices, M3-AUD-15 menu UI SFX, M3-AUD-16 Act I zone beds,
  M3-AUD-17 Reefball hooks, M3-AUD-18 battle stings. All are `review`.
- **Integration branch:** merged at 37fd9571.
- **Checks run:**
  - The full Godot suite gave 1564 run, 0 failed on a quiet machine.
  - Earlier niced full runs, made while renders were running, failed only `test_scene_router_swap` on the boot frame.
    That test passes on its own, passes when run with every test that precedes it, and depends on load. The
    integration branch itself gave 1480/0.
  - validate_data showed 0 errors; taskboard --check, gdlint and gdformat were clean; test_audio_data passed (39 OK);
    the loudness test passed; and every new set re-rendered byte-identical with `--determinism`.
- **Skipped (the Lead runs these at merge):** screenshots and Blender. Coverage was skipped too, because game/battle/
  and game/progression/ weren't touched.

## Note to the Lead (the cross-session reply was refused: "needs a trusted device")
Your queue of five is taken:
- **(1) M2-AUD-14:** I filed it, since it wasn't on any branch I could see. M3-AUD-15 already covers the Lattice,
  Equip and the map open; M2-AUD-14 adds item use and sort, the formation swap, customize, and the map pan.
- **(2) Act I music:** the Ch1, Ch4, Ch5 Pemakar, Ch7, Ch8 Corrow and Ch9 cues, and the Hullgnaw, Spar-Wraith,
  Cinder Matron and Reach themes, are already on claude/audio. The new work is M3-AUD-19 (the Ashcrown and Coilspire
  temples, the Bell galleries) and M3-AUD-20 (the Stillguard Inquisitor and raid-hound). **No sea-floor scene
  exists on claude/m2-slice: name its path if it is a real zone.**
- **(3) M3-AUD-21:** done (syllable blips).
- **(4) M3-AUD-22:** done (muffle inside the sphere). The goal swells were already in M3-AUD-17.
- **(5) M3-AUD-23:** the mix pass, done apart from a re-run once the new cues land.

## Id rule (the Lead's CONSOLIDATED §4, "id blocks")
New audio task ids are 800–899 (M3-AUD-800…), new ADRs 0170–0179, and handoffs are named
`<date>-audio-audio-<n>.md`. Existing ids stay as they are. The Lead's menu-pages task is M2-AUD-17.

## Queue check (2026-10-24, the Lead's latest)
- **Items 1–5 are done and merged on claude/audio:**
  - M2-AUD-14 and M2-AUD-17, the menu-page sounds, live on the real classes.
  - Act I music: Ch1, Ch4–Ch9 and the bosses, with Ashcrown, Coilspire, the Bell galleries and the Stillguard
    (M3-AUD-19/20).
  - M3-AUD-21, syllable blips on the reveal's pauses.
  - The Reefball soundscape: M3-AUD-17 and M3-AUD-22, with the sphere live (M3-AUD-801).
  - M3-AUD-23, the mix pass.
- **New, now doing:**
  - M3-AUD-802, hero footsteps and foley (worktree agent; coordinating via hero-integration's live log).
  - M3-AUD-803, KO-once (me).
  - M3-AUD-804 and M3-AUD-805, Act II music sketches (worktree agents).

## MERGE-READY @ 2a699ddb
- **Items (all `review`):**
  - M2-AUD-17, the menu pages live: every existing class is hooked against its real code. ShopMenu and InnMenu are
    rewritten, and StatusMenu and BattlePauseMenu are new.
  - M3-AUD-800, the battle hooks live on the real BattleChoreo and CreatureActor. Two fixes: creature hurt and death
    now play on the contact beat, and a retry leaves one listener. The Flood stagger is read from choreo.json.
  - M3-AUD-801: the Reefball sphere is live, and `ch01_hullgnaw` plays the Hullgnaw theme.
- **Integration branch:** merged at its current head.
- **Checks run:**
  - The full Godot suite: 2006 run, 0 failed.
  - The loudness test passed, validate_data showed 0 errors, and taskboard, gdlint and gdformat were clean.
- **Skipped (the Lead runs these at merge):** screenshots and Blender. Coverage was skipped because game/battle/ and
  game/progression/ weren't touched.
- **Still pending (their targets are not on this branch):**
  - FormationMenu.
  - The Reefball match, ball and goal (no minigame yet).
  - The m2-slice zone beds and voices.
  - `battle_stinger` and `boss_intro` are emitted only on claude/battle-presentation (big7 did not carry them). Their
    shapes match battle_stings.json, so no change is needed when they land.
- **For other roles:**
  - The menus' own tests leak about 250 GDScript resources at exit, and the battle scene keeps
    `field_submenu.gd` and `battle_pause_menu.gd` (M2-AUD-16).
  - Refused Confirms are unheard until M2-AUD-15 lands.

## Exact next step
Queue empty. Waiting on: those merges, after which their pending flags come off; and the human's listening verdict.

## MERGE-READY @ 662f9d7d
- **Integration branch:** big7 (8f808cc6) merged.
- **Fixes after the merge:**
  - The new enemy `wickfry` is voiced as a pitched glassfry.
  - The shrine test's `flush_pending` is restored (the merge had dropped it).
  - The integration branch's own base-class signal code is kept, and both tests are kept.
- **Items:**
  - M3-AUD-24 (the Lead's second "M3-AUD-13", renumbered): voices for the six new speakers.
  - Pending voices for m2-slice's 17 Ch4–Ch9 speakers (the menus track flagged them).
- **Requests filed:** M2-AUD-16 (menus: `BattlePause._ready` leaks a `BattlePauseMenu`; tests report "resources still
  in use").
- **Checks run:**
  - The full Godot suite: 1981 run, 0 failed.
  - All tool tests: 711 OK, 7 skipped.
  - The loudness test passed, validate_data showed 0 errors, and gdlint and gdformat were clean.
- **Skipped (the Lead runs these at merge):** screenshots and Blender. Coverage was skipped because game/battle/ and
  game/progression/ weren't touched.

## MERGE-READY @ 4dbcfc1f
- **Items:** M2-AUD-14 menu-page SFX, M3-AUD-19 Act I temple loops, M3-AUD-20 the Stillguard Inquisitor boss theme,
  M3-AUD-21 syllable blips, M3-AUD-22 the Reefball sphere muffle, M3-AUD-23 the mix pass (mix_report.md, mix.md §8;
  blips +6 dB), and pending zone beds for Brine Shoals and Corrow at night. All are `review`. Integration branch
  merged.
- **Checks run:** the full Godot suite (1570 run, 0 failed); the loudness test (OK); validate_data (0 errors);
  taskboard --check; test_audio_data; gdlint and gdformat. Every new set was re-rendered byte-identical with
  `--determinism`.
- **Skipped (the Lead runs these at merge):** screenshots and Blender. Coverage was skipped because game/battle/ and
  game/progression/ weren't touched.

## State (2026-10-24, latest)
- **Queue empty.**
- **Requests out:**
  - M2-AUD-15 (menus: public reads for refusals, Customize's arming, board and map pans).
  - M2-AUD-07/08/09/12 and M3-ARC-01.
- **Pending hooks go live when these merge:** claude/battle-presentation, claude/creatures, claude/ui and
  claude/menus, gpu/m3-rnd-01-reefball, claude/m2-slice. The checks for each merge are in the task Notes.
- **Open question for the Lead:** is there a "sea floor" zone? No such scene is on claude/m2-slice.

## Exact next step
Wait for those merges and drop each `pending` flag as its classes land (validate_data then checks the names). Wait
for the human's listening verdict (listening_notes.md) and revise when it comes.

## Un-pushed state
None.
