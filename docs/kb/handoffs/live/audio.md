# Live log: audio (branch `claude/audio`)

## ACT II (from 2026-10-30, ADR 0205: audio has no open Act I row)
Session `session_01UPFyE9L9BA3QodpCNJEfAs`. M4-A2P-090/091/093 and M4-AUD-1001 are claimed (`doing`). New Act II audio is plain git under `assets/audio/act2/` (**ADR 0175**; plain-git budget 105 MiB). Newest first.

- **MERGE-READY @ 5537dc6e8: the Lead's 01:41 FAST-TRACK (cloud-qa's 32 `used` reconnect ERRORs).**
  - **Is the first fix on integration?** Yes. 4d4fbd50 merged in big34 (9317c6b6, `Merge lead/gate-big34: UiAudio/unbind ERROR fixes`). I merged integration (big35 included) into claude/audio for this check.
  - **The repro** (M3-HER-1169's: scene_swap_probe `--encounter=ch03_causeway_shore --return=...saltgrass_causeway.tscn`, a resident return) logs **0** "already connected" on current integration.
    - The pre-fix ui_audio.gd also logs 0 there now, so since big35's return changes the probe no longer tells the two apart.
  - **cloud-qa's build:** its log isn't in the repo, so I can't tell whether its 32 came from a build before big34. **LEAD-ASK:** the build sha of that run, if it was big34 or later.
  - **Hardened either way:** UiAudio.watch now also skips any connection that already exists (`is_connected`, M3-HER-1169's tested guard), on top of the node's mark. So no path that brings a node back (a lost mark, a duplicate, a second watch) can connect `used` or any hooked signal twice.
  - **Test:** test_audio_reconnect +1. A real `Interactable`, routed as the director routes it (UiAudio and InteractAudio), goes through two resident returns and then once with its mark cleared: no engine error, one connection each, and the soft touch plays once.
  - **Checks:** gdlint and gdformat clean; Godot `--filter=audio` 189/0, ui_ 58/0; validate_data 0. **M3-HER-1169** is answered by this (hero-integration can close it on merge).
- **MERGE-READY @ bc41b3147: Act III cutscene sounds (M5-A3P-1953, to review).** Every `@sfx` the Act III drafts name now has a row.
  - **13 new** under `assets/audio/act3/sfx/`:
    - velamir_lullaby_hum: the lullaby hummed, one file for both Asha (Ch18) and Imra (E1);
    - pell_farewell_tide: Pell sings the clutch's rising line for Nhoa;
    - match_struck: E7's lamp;
    - the Kite's settle, strain and floor-touch;
    - Iskarra's engine stopping, Kerrid's hitch spilling, the flat sea, Haluna's murmured names, the clutch's hum, the shell into the lagoon, the wind in the sails.
  - **4 alias rows** to the Kite's existing foley (kite_engines_stop, sails_fill, rope_creak, hull_meets_water).
  - **Checks:** determinism; targets rule act3/sfx; validate_data 0; audio_loudness and audio_data OK; Godot audio_runtime 11/0.
  - **Next:** Ch17–Ch20's music cues: hollowmere_morning, the_choice, kite_first_lamp, kite_theme, kite_night, haluna_lifting, reedhollow_return, kerrid_hitch, engine_down, the_eye, undertow_descent, the six memory_* cues, the_cage, thank_you.
- **MERGE-READY @ 626528274: the Lead's 01:21 item, the Act II cue placement in slice-polish's newest Ch13–Ch16 staging (m2-slice @ ff50ec33).**
  - **Staged now:** Ch13's ansedra, ansedra_lacquer_court, lamp_archive (with the `archive_lamp` prop) and sanctum; Ch15's open_sea; Ch16's drowned_choir and pale_rim.
  - **The check:** act1_playthrough `--act 2 --holds`, run in a scratch worktree of m2-slice with audio's current data and tools copied in. No missing cue and no cue ending inside a held shot, in any of them; only the 13 known notes (deliberate `fade=0.0` cuts and ansedra named twice).
  - **The scripts the slice changed** (Ch13–Ch16): wording and marks only, plus `@memory on look=white … off` round ch16_kesh_memory. That scene already has its cue (`kesh_memory`), and the zone bed holds under a sequencer's music, so it needs nothing more.
  - **One addition, Ch13 R10 (ch13_sefir_closes_the_book):** after `@music silence`, Sefir squares the pages, closes the ledger and puts out the Archive's one lamp (`@light archive_lamp off 1.0`). The lamp is staged warm, an oil flame ("the only warm notes are human", act2_ch13.md rule 5), and nothing else sounds in that silence. So:
    - prop_sfx.json gives `archive_lamp.tscn` the `lamp_flame` loop, close (1.5 m), marked pending until the slice merges;
    - PropAudio rows may name a `light`: the loop's level follows its energy every frame, so the lamp's breath goes out with the light (a 1 s fade, then stopped).
  - **Test:** test_prop_audio +1 (lit at its level; half the energy about 6 dB down; out with the light).
  - **Checks:** validate_data 0; gdlint and gdformat clean; Godot prop_audio 3/0, flame_audio 3/0. Skipped: screenshots, Blender.
- **MERGE-READY @ 3e7910593: the Lead's 23:05 FAST-TRACK (the two ERRORs). It pre-empts the score (ADR 0207).**
  - **UiAudio "already connected" on every resident battle return (134 in Ch1–Ch6):**
    - Cause: the field leaves the tree for the battle and comes back with its connections intact. `step()` had dropped it from `watched`, so the director's `watch()` connected every hooked signal again.
    - Fix: a node now carries the UiAudio that connected it (meta `ui_audio_connected`). A second `watch()` only resumes its reads, and a signal still plays its row once.
  - **ashcrown_audio.gd:53 `unbind(0)`:** the trial's `ran` has three arguments and went through `unbind(argc - 3)`, which is 0 and an ERROR. Now three arguments connect plainly, and only a signal with more drops its extras.
  - **Test:** `tests/unit/test_audio_reconnect.gd` (2) fails on any engine error (QaLogger), not only script errors. It reproduces both on the old code (the exact messages) and passes on the fix.
  - **Checks:** gdlint and gdformat clean; Godot audio_reconnect 2/0, ui_ 58/0, ashcrown 22/0, audio_runtime 11/0, battle_audio 22/0. ui_'s "2 left nodes in the tree" happens without this change too.
- **MERGE-READY @ e8755571d: Act III production starts (ADR 0207; the Lead's 21:56 item). The score, part 1, is the Unbinding themes (M5-A3P-1950, to review); part 2, the finale, is begun (M5-A3P-1951).**
  - **Merged integration** (46d8a067 onward) into claude/audio; it was clean.
  - **Storage, ADR 0208:** Act III's new audio is plain git under `assets/audio/act3/`, the same route as Act II's (LFS uploads are still refused from the cloud). The budget is 150 MiB; plain audio was at 100.3 MiB of 105. **LEAD-ASK:** accept ADR 0208 (repository size) on merge.
  - **The sung Letting is derived, never retyped.** motifs.py `letting_verse()` is the first verse turned upward line by line, its close climbing to the held E6 on *tash*. `assets_src/music/act3/lamptongue.py` holds lamptongue.md's eight verses and its syllable rules. Asha's voice stays the vowel-shaped breath-flute vocalise (SPEC §16 Q4 still open); choirs use the procedural formant voices, as Act II's do.
  - **New cues** (assets/audio/act3/music/; music.json rows):
    - `the_letting` (H07, a 53 s loop): she sings the Eighth Verse twice; the score follows her, cool and held, then the choir and the rising glass. Its `release`, `the_letting_release` (H08), holds the E6 while the strings thin to it alone.
    - `release_sting`: Ch20's six releases and Kesh's; the Letting's cell on metallophone and glass, with no voice and no cadence.
    - `unbinding_swell` (H09, 109 s): the full choir and orchestra, the only time in the game, sing the Hush's first phrase in Lamptongue twice. The second time it resolves **upward**, B D E | A, to A major on *tash*.
    - `heart_approach` (H01–H02, a loop): the Hush's first phrase backwards, as reversed piano over the heart's drone.
    - `heart_rest` (R1): the drone alone.
  - **Battle:** `battle.encounters` maps `ch21_sefir_letting` (H07's fight, pending combat) to `the_letting`, so the battle keeps her song.
  - **Checks:**
    - render_all: loudness, loop seams, and `--determinism` (all identical).
    - mono fold: Act III has 0 failing files.
    - validate_data 0; taskboard OK.
    - tools tests: audio_loudness, audio_data, motifs (+1), lamptongue_sung (new), all OK.
    - Godot tests: music_release 4/0, audio_runtime 11/0, battle_audio 22/0, music_transitions 7/0.
    - Skipped: screenshots, Blender, coverage.
  - **PC-QUEUE, by ear:**
    - `unbinding_swell`'s A major resolution: the loudest moment in the game by design, momentary max -6.3.
    - The Letting's vocalise vowels.
- **MERGE-READY @ 4ff7c51c5: the Act III score, part 2, the finale (M5-A3P-1951, to review).**
  - **`kesh_first_voice`** (H03, a loop): the seven verses' first lines in turn, in Lamptongue, a step higher each, over a 3+3+2 drum and string ostinato; her own verse is the fullest.
  - **`sefir_warden`** (H04): the Order hums ORDER_HUM over airless strings, and his motif hangs on its C#.
  - **`sefir_heart`** (H05–H06): the storm's note on the heart's A under rock-fusion percussion in 7/8, his C# now the A's major third.
  - **Battle:** `ch21_kesh` and `ch21_sefir_heart` are pending rows in `battle.encounters`.
  - **For combat:**
    - H04's fight has no id in the drafts yet: it needs a row to `sefir_warden`.
    - A BattleCycle `cycle_changed` signal would let Kesh's verses follow her element.
  - **Checks:** render_all loudness, seams and determinism (all identical; kesh's seam re-placed half a beat in); true peaks under -1; mono fold 0 failing; validate_data 0; audio_loudness and audio_data OK; Godot battle_audio 22/0, music_transitions 7/0.
- **MERGE-READY @ 39e91137c: the Act III score, part 3, the ending (M5-A3P-1952, to review).**
  - **The cues:**
    - `goodbye_imra`: one piano A after she is gone.
    - `ending_lift_bed`: the drone and a glass shimmer.
    - `goodbye_dace`: the current-song on harp with four bars of the lullaby inside it; same notes, D dorian and A minor.
    - `goodbye_kerrid`: his stair slowing to a stop.
    - `ending_dock`: solo piano, the Hush resolving to A.
    - `credits_suite`: the shipped themes in pilgrimage order, ending on the lullaby on piano.
    - `post_credits_lamp`: the star-path on a low metallophone.
  - **Checks:** render_all loudness and determinism (all identical); the lift bed's seam; mono fold 0 failing; validate_data 0; audio_loudness and audio_data OK; Godot audio_runtime 11/0.
  - **PC-QUEUE:**
    - The credits suite's hush-to-piano join (it thins 7.5 dB in mono there).
    - goodbye_dace's harp by ear.
  - **Not done yet:** the 17 Act III cutscene `@sfx` (velamir_lullaby_hum, match_struck, hull_meets_water and the others); then the Ch17–Ch20 cues.
- **MERGE-READY @ 6fcbce03d: the Lead's 21:25 item, the audio accessibility pass (M4-A2P-1952, to review).**
  - **Sliders reach every sound.** Every bus sends to a slider bus (UI, World and Combat under SFX; Ambience with the effects slider). Two fixes:
    - **Strays:** a player that never names a bus would sit on Master, under no slider but the master's. `AudioDirector.route_stray` now moves it to mix.json `stray_bus` (SFX). Nothing hits this today (the dialogue blip goes to Voice, the cutscene sound fallback to SFX); it guards any track's future players.
    - **Voice-like barks:** the townsfolk's chatter (`villager_murmur_*`) was on World, under the effects slider only. It now plays on a new **Walla** bus sending through World, so the voice slider reaches it while it still ducks under a line and keeps the zone's reverb. The voice slider's help text says so.
    - Battle barks are dialogue lines (the Voice blip), and the creatures' voices are effects; neither changes.
  - **Mono.** A new `mono_audio` setting on the Audio page folds Master to (L + R) / 2: a StereoEnhance with `pan_pullout` 0, applied live.
    - The new `tools/audio/mono_check.py` checks all 1,289 renders (186 of them stereo).
    - One failed: `sefir_theme` lost 8.5 dB at 39.4 s, where its hall's late field went out of phase under the bar-9 hum. Re-rendered with the hall at width 0.7, it now thins by 6.4 dB for that moment; loudness is unchanged at -15.98 LUFS.
    - The largest whole-file loss is 2.1 LU (kesh_memory). Fifteen music cues thin by 4–7.4 dB for a moment and keep every part (listed by the tool). **PC-QUEUE:** sefir_theme at bar 9, by ear.
  - **Captions.** The game has no captions setting. Dialogue, narration and voice-over are subtitled, but non-dialogue cues aren't. That is requested from UI as **M4-A2P-1953**: a `captions` setting (default off) and a caption line. Audio then emits the battle tells and the off-screen story `@sfx` with loc keys.
  - **Act I tells are distinct.** The new `tools/audio/tell_check.py` checks the seven Act I wind-ups:
    - each against its enemy's attack;
    - each against every tell it can meet in one fight.

    All are distinct; the closest is Hullgnaw's coil against its bite (4.8 times as long, 1.28 times brighter). The Cinder Matron's recrust (Ch5) and the Grip (Ch8) sound alike (3.8 dB apart in colour) but never share a fight, so that pair is reported, not failed.
  - **Touched outside audio's files:**
    - `test_ui_settings.gd`: its pinned settings list gains `mono_audio`, one id appended.
    - accessibility.json, audio_menu.json, strings.csv: appended rows, each in its own commit.
  - **Checks:**
    - gdlint and gdformat clean (game, tests); validate_data 0; taskboard OK.
    - tools tests: audio_data, audio_loudness, dialogue_clarity, mono_check (new), tell_check (new), all OK.
    - Godot tests: audio_accessibility 3/0 (new), ui_settings 12/0, settings 49/0, audio_menu 4/0, audio_runtime 11/0, life_audio 14/0, battle_audio 22/0, battle_stings 8/0, flame_audio 3/0, prop_audio 2/0, music_release 4/0.
    - Skipped: screenshots (none shows the Audio page: the settings shots are the hub, Accessibility and Controls, and the Accessibility page leaves audio_menu.json's rows off, so `mono_audio` moves no baseline), Blender, coverage.
- **BACKLOG EMPTY (after 6fcbce03d):** waiting on Ch11 and Ch13 staging, combat's Ch14–Ch16 fights, env-art-b's merge and UI's M4-A2P-1953.
- **MERGE-READY @ 1ad5bbcfb: the Lead's 21:05 item.**
  - **The Act II boss themes as played in the intros (bdc5ef22):** done at d04d79422 (above). Each sting now lands with the title card at 0.7 s, under the boss cue's 3.5 s duck.
  - **Victory stings:** each Act II boss win returns to the field (the chapter flows: `victory_flag`, then the zone), not into a scene of grief, the same as Act I. So the one modest victory figure (pentatonic, open fifths) stays, with no triumphant boss fanfare. act1_mix_pass `--act 2`: 62 handovers, none with a step over 3 LU. Victory → field is level in every Act II zone (-16.0 against -16.0 to -16.1, at most 0.1 LU).
  - **Zone ambience against env-art-b's ambient life** (env-art-b @ 9a85e089, not on integration yet):
    - **What it added:** flames that flicker (the Lacquer Court's eight lanterns at 0.15; Hollowmere's seven warm lamps at 0.3 and four bound-teal conduit lights at 0.12), and tide debris that drifts at Hollowmere, the open sea and round the bridal barge. No birds; the gulls are already in hollowmere_flotilla.
    - **The flames now sound:** a new close loop, `lamp_flame` (20 s, act2_ambience.py: an oil wick's soft breath wavering at ZoneKitDressing's own flicker rates of 1.7 and 4.3 Hz, and a rare small gutter). It plays under each warm `fire_lights` row with a `flicker` of at least 0.1, through PropAudio and the new `flames` row in prop_sfx.json. The loop is heard within about 9 m and never across the zone, and each flame starts at its own point in the loop, so a row of lanterns doesn't breathe in step. The teal lights flicker but aren't flames, so they stay silent.
    - **How it hooks in:** it reads only ZoneKitDressing's public `layout`, the `FireLights` children in row order, and the `dressed` signal. It waits for `dressed` if the lights aren't placed yet, and it changes nothing until env-art-b merges.
    - **The drifting debris needs no new sound:** it rides the swell, and the beds already carry water on hulls and pilings (hollowmere_flotilla, open_sea_night, open_sea_fog).
  - **Checks:**
    - Run: render_all `--only act2_ambience` (only `lamp_flame` new, every other bed byte-identical; loudness re-checked); test_audio_loudness OK; validate_data 0; data_check OK; gdlint and gdformat clean.
    - Godot tests: flame_audio 3/0 (new), prop_audio 2/0, battle_stings 8/0, audio_runtime 11/0, ambience 5/0, footsteps 8/0.
    - Skipped: screenshots, Blender, coverage.
  - **PC-QUEUE:** walking past the Lacquer Court's lanterns once env-art-b merges.
- **BACKLOG EMPTY (after 1ad5bbcfb):** waiting on Ch11 and Ch13 staging, combat's Ch14–Ch16 fights, and env-art-b's merge (the flames go live then).
- **MERGE-READY @ d04d79422 (unchanged): the Lead's 20:45 item. Ch11 and Ch14–Ch16 were already rendered from the direction notes, so there was nothing to add.**
  - **Ch11 (`docs/kb/story/beats/act2_ch11_direction.md`):** the table is camera and blocking. Its only sound calls are already met:
    - the `nhoa_bound` sting on N07 (rendered);
    - "2 s of silence on V06" and "let the music cut to silence on the walk away (it does)";
    - its held shots (V00 8 s, V07 3 s, V09 4 s, T00 3 s, T03 5 s, N02–N09). Each has a row in `act2_direction_holds.json` (task 22), and act1_playthrough `--holds` finds no cue ending inside any of them.
  - **Ch12–Ch16:** a scan of every `@music`/`@sfx`/`@ambience` name in the six direction notes finds every one rendered and in a table: Ch12 6, Ch13 7, Ch14 9, Ch15 10, Ch16 12; missing 0. Ch14–Ch16's holds (three, three and one) pass too. `test_direction_holds` passes.
  - **When Ch11's staging lands:** I'll rerun act1_playthrough `--act 2 --holds` against it. A staged hold longer than the note's floor is the only thing that can need a cue retimed.
  - **Checks:** test_direction_holds OK and act1_playthrough `--act 2` (13 items, all known notes). Nothing changed but this log.
- **MERGE-READY @ d04d79422 (unchanged): the Lead's 20:26 item. There's nothing new to render or score yet.**
  - **Ch11's scoring as slice-polish stages it:** m2-slice @ e262e104 stages the same Ch11 and Ch12 scenes as before (lowlight, sunken_vey; cloudloom, keth_pass, quellan, inn_fire), and their cues were checked as played at faaa30a0. Every Ch11–Ch13 script difference between m2-slice and audio is audio's own newer side, already on integration @ 46d8a067: m2-slice predates the restored `@sfx pole_no_wake` in ch13_still_city and the `ch13/sanctum` location. I'll rescore Ch11 when slice-polish pushes a new stage.
  - **Ch12–Ch13 from act2-plan's cue tables:** every cue is rendered and every ref resolves. act1_playthrough `--act 2 --holds` reports no missing cue in Ch11–Ch13, only the four known notes: the Vowbound `fade=0.0` lines play as 0.2 s fades, and ansedra is named twice. Ch13 has no staging on any branch.
  - **Checks:** none. Nothing changed but this log.
- **MERGE-READY @ 425b1109: the Lead's 19:45 item.**
  - **Ch11–Ch13 cutscene cues:** Ch13 has no staging yet on any branch (Ch11 and Ch12's were checked at faaa30a0). act2-plan's cue tables have no missing cue (17:50), so there is nothing to render. I'll rerun the staged check when Ch13 lands.
  - **The Act II boss themes as played in battle-presentation's intros** (bdc5ef22 and the Ch10–Ch12 intros on big25; choreo.json boss_intro: camera_in 1.1 s, hold 2.0–2.4 s, camera_out 0.8 s; the title card at 0.7 s).
    - **Found:** BattleBossIntro announces `boss_intro` "as the intro starts", as the camera begins to move, but every boss sting (Act I's and Act II's) hits in its first 0–0.2 s. So the hit came before the boss's name was on screen.
    - **Fixed in audio's layer** (no battle-presentation change): battle_stings.json rows take a `delay_sec`, and `boss_intro`'s is 0.7 s (= choreo.json `card_at_sec`). StingAudio holds the row and plays it on time from `advance()`. The `boss_intro` duck still starts with the event, so the boss cue dips as the camera moves and the hit lands with the card.
    - A test ties `delay_sec` to `card_at_sec`, so a retimed card can't leave the sting behind.
    - **Levels:** the boss cues sit at ~-18 LUFS, -23 under the duck; the stings hit at -16 momentary. The shortest stings now ring until 2.5 s (Drowner) and 2.8 s (Wakefin) of a 3.9–4.3 s intro, and the ducked cue plays under the rest: not silence.
    - The battle cue enters at the battle's attach (battle_in_sec 0.3), before the reveal, as Act I's do.
  - **Checks:** validate_data 0; Godot battle_stings 8/0 (one new), battle_audio 22/0 (test_battle_audio_live now steps through the delay), audio_runtime 11/0, impact_audio 6/0. **Skipped:** screenshots, Blender, coverage.
  - **PC-QUEUE:** a boss intro by ear (the hit with the card).
- **BACKLOG EMPTY (after 425b1109):** waiting on Ch13's staging, combat's Ch14–Ch16 fights, and the listening verdict.
- **MERGE-READY @ 3d9476ea: the Lead's 19:25 item, the music of Act I's emotional beats as played** (cbc63b39 WIP, 3d9476ea).
  - **Scenes checked:** each key scene's cues traced against the scene's timeline (`act1_playthrough.py`'s pacing, including the player-paced hold gates): the Prologue, the Ch1 storm (the rising, going under, the Hullgnaw), the Drownbell, the Ch4 wake, Corrow (the storm against the wind, the Reach, Virel's binding, the Ebbing) and the Act I end (the road out, the vigil, the act card, the end card).
  - **Fine as they were:** the rising's loop gains its stem on cue; going_under fades 3 s before its own end; Hullgnaw, the Reach and the wake are loops; the storm against the wind is silent on purpose. The Drownbell is battle-driven (its stems on the Flood).
  - **Fixed:**
    - **The Ebbing (Ch9, "the most beautiful sequence in Act I") never peaked or resolved.** Its dance is player-paced (three hold gates), but the 114 s cue ran on fixed time, and at the scene's floor the letting-down silenced it ~44 s in, at bar 16. Its climax (bars 21–28) and its ending (35–40) were never heard.
      - Reordered to the scene: the gathering is the intro; MEL_A with the dance full and the glass doubling lands on the long line (N11, the hero frame, ~12 s in); then MEL_B, MEL_A, the thinning and its own ending for a player who lingers.
      - **New cue-level `release`** (music.json, AudioDirector.play_music): whenever a scene silences the Ebbing, `the_ebbing_release` plays instead of a fade. It is the last chord, the motes falling away twice and the Cantor's E held, unresolved, 9.5 s, sized to the next scene's `corrow_night`. No script change.
      - The markers (M3-C09-06) moved with the form; test_music_markers OK.
    - **The Act I end's vigil played the wrong cue.** The beat sheet says "hush_first_verse (piano coda, as the slice's end card)", but the script started the 80 s sung verse at its drone intro and faded it ~15 s in.
      - The script now says `@music hush_coda` (a one-word id fix to ch09_the_road_out, beat sheet's intent; dlgc recompiled one scene).
      - `hush_coda` is `resume` and `free`, so the end card's zone row picks the coda up where the vigil left it: one piece across the act break, never heard twice from the top.
    - **Virel's binding (Ch8, Corrow) ran out ~4 s before its scene ended**, then 3 s more until the zone returned. The flues' F# and C# now hold on, 12 dB down, for 10 s (17.9 s, -15.98 LUFS, unchanged). Act I's as-played check no longer flags it.
  - **Not changed (not key beats; noted):** Ch7's empty moorings (`oruvel_theme`, 17 s before the end) and Tavi (`tavi_kell`, 5 s) end before their scenes, then the zone returns. Say if they should hold too.
  - **Checks:**
    - Renders `--determinism` identical (the Ebbing, its release, virel_bound).
    - validate_data 0; the Act I audit 0; mix pass 98 hand-overs, 0 over 3 LU; test_audio_loudness, test_audio_data and test_music_markers OK.
    - Godot: music_release 4/0 (new), music_transitions 7/0, zone_return 9/0, audio_runtime 11/0, virel 6/0.
    - **Skipped:** screenshots, Blender, coverage.
  - **PC-QUEUE:** the Ebbing danced fast and slow (the peak on N11, the release at the letting-down); the vigil into the end card.
- **Ch11–Ch13 as staged:** unchanged since faaa30a0 (Ch13 not staged yet).
- **BACKLOG EMPTY (after 3d9476ea).**
- **Re the Lead's 18:45 message:** the slice-path polish (18:24) was already done, MERGE-READY @ b97ac894 (below). **Kite work is parked:** the one KiteMapMenu hook from that pass stays (data only, nothing more planned).
- **MERGE-READY @ faaa30a0: the Ch11–Ch13 cutscene cues as slice-polish stages them** (the 18:45 item).
  - **Staged so far** (integration + claude/m2-slice @ b710cfa9): Ch11's sunken_vey and lowlight, Ch12's cloudloom, keth_pass and quellan. Ch13 isn't staged yet.
  - **On m2-slice's tree** (a scratch worktree, nothing of theirs edited):
    - The Act II audit is clean: cutscenes 0, cutscene actions 0 (every `@anim` of the staged scenes has its foley).
    - `act1_playthrough.py --act 2 --holds` finds no gap in Ch11–Ch13.
    - The staging changed no script timing: the files are shots, marks and props, and the only Ch11–Ch13 script difference is ch13_still_city's restored `pole_no_wake`.
  - **New:** Ch12's staging adds cinematics' first practical, `inn_fire` (the Quellan inn hearth that ch12_forty_seven_voices plays beside). It was light only, so the scene's fire was silent.
    - `PropAudio` (game/audio/prop_audio.gd) and `game/data/audio/prop_sfx.json` give a staged prop a positional loop by its scene. It starts as the prop enters and goes with it.
    - The hearth's loop is `hearth_fire` (act2_ambience.py, appended: a low peat-and-pine fire, pops, a log shifting once; 24 s, -26 LUFS, seam flux x1.52, `loop=true`, rendered byte-identical twice). It plays on World, so it ducks under a line.
    - The row is `pending` until the scene merges from claude/m2-slice. `data_check` then requires the scene, and a planted missing scene is reported.
    - Any later practical (a lamp, a brazier) is one row.
  - **Checks:** validate_data 0; test_audio_data and test_audio_loudness OK; Godot prop_audio 2/0 (new), audio_runtime 11/0, field_audio 22/0, foley_detail 4/0. **Skipped:** screenshots, Blender, coverage.
- **BACKLOG EMPTY (after faaa30a0):** waiting on Ch13's staging (then a rerun), combat's Ch14–Ch16 fights, and the listening verdict.
- **MERGE-READY @ b97ac894: the Lead's 18:24 item, the Act I audio polish pass on the slice path (Prologue → Ch3), as played.**
  - **Interactables:** every interact trigger on the path is heard.
    - Oruvel's lashings and the underway's tethers, hinge and tin have their own rows (InteractAudio).
    - The underway kit's three new triggers (big23–26) are voiced elsewhere, per interact_sfx.json's rule:
      - `gauge_wheel` → the `ch01_gauge_wheel` cutscene (`salvage_cut` ×2);
      - `current_shaft` → `ch01_current_shaft` (`@anim clip_on` foley, `rhen_current_hum`);
      - `limpet` → a battle and its stinger.
    - `causeway_notice` opens the document reader (its page, cursor and mark sounds). Talkers speak their dialogue.
  - **Menus:** the audits' UI checks were 0, but they work per class.
    - Checked per action: every action signal on every hooked UI class, and on subclasses hooked through a base, against its hook.
    - One was silent: the Kite's flight map (`KiteMapMenu`, later in the game) had only the field submenu's open and close. It now has its own hook: open, close, `flight_chosen` → `ui_confirm`, its list and chart cursors → `ui_cursor`, its pages → `ui_page`.
    - `ReadPanel.closed` is heard through its `is_open()` watch.
    - New `tests/unit/test_ui_polish_audio.gd`: every ui_sfx.json watch expression parses and every signal names a real row (a typo there is silence, not an error), plus a real kite map driven through UiAudio.
  - **Ambience vs dialogue (keep dialogue clear):** a line's blip stream is -23.3 LUFS (mix.md §6).
    - Under an open box, the beds were ducked only 2 dB, and multi-bed zones stacked up to it (wind at its loudest): Haluna by day margin 0, the causeway 0, Haluna at night -1.3, Oruvel +1.8.
    - **Fix:** mix.json `ducks.dialogue.Ambience` -2 → **-6** (the bed breathes down over the 0.25 s ramp, it doesn't vanish), and the wake's mourners walla `volume_db` -4 → -7. The wake stacks four beds and the wind; the people at the tables hush while someone speaks.
    - Every zone in the game (34 states) now leaves the blips ≥ 2.5 LU clear (worst: the wake +2.5, Haluna at night +2.7). The slice path: Oruvel +5.8, Haluna day +3.9, causeway +4.0, single-bed zones +8.8.
    - New `tools/tests/test_dialogue_clarity.py` holds it.
  - **Checks:**
    - Act I audit 0; act1_loop_check 43 files, 0 problems (beds still ~10 LU under their music); validate_data 0.
    - test_audio_data, test_act1_audio_audit, test_dialogue_clarity and test_audio_loudness OK.
    - Godot: audio_runtime 11/0, field_audio 22/0, voice_audio 12/0, foley_detail 4/0, ui_polish_audio 2/0 (new), screen_audio 11/0.
    - **Skipped:** screenshots, Blender, coverage.
  - **PC-QUEUE:** a New Game run to Ch3 by ear, especially a line in Haluna at night and on the causeway (the duck's depth).
- **BACKLOG EMPTY (after b97ac894):** waiting on combat's Ch14–Ch16 fights, slice-polish's staging, and the listening verdict.
- **MERGE-READY @ 84ef34df: M4-A2P-1951, the Act II mix pass as played, Ch14–Ch16** (the second half of the 18:04 item).
  - **Loudness:** 22 hand-overs, 0 over 3 LU (62 across Ch10–Ch16; report `docs/kb/audio/act2_mix_pass.md`). Silences: none. Doubled starts: none.
  - **Found and fixed, the cutscene → battle seam:** three fights would have played the generic `battle_standard_v2` instead of their delivered two-stem cues.
    - The fights: `ch14_malcor_venn` (`malcor_venn`), `ch14_water_steps` (`court_steps`), `ch16_abiding_guard` (`abiding_guard`). The scripts already start them, but combat hasn't written their encounters.
    - music.json `battle.encounters` now names them, and `battle.pending_encounters` lets `data_check` accept them until encounters.json has them. It then asks for each to come off the list.
    - Each fight scores itself the moment it exists, and its arena bed follows (e.g. `ansedra_lagoon_escape` → `arena_lagoon_dusk`). The phase → stem rows are still to come with the fights' phase ids (the cue rows' notes say which).
    - The Wakefin's seam carries its own cue.
  - **LEAD-ASK:** the chapter plan (ch14.md §3) calls the steps set piece `ch14_hold_the_steps`, but `ch14_the_vows` starts `ch14_water_steps`. Both ids name `court_steps` for now; combat or act2-plan should settle one.
  - **Checks:** validate_data 0; test_audio_data OK; the Act I and Act II audits 0; Godot battle_audio 22/0, audio_runtime 11/0, music_transitions 7/0. **Skipped:** screenshots, Blender, coverage.
- **BACKLOG EMPTY (after 84ef34df):** waiting on combat's people-boss and set-piece encounters (then their phase rows), slice-polish's staging, and the listening verdict.
- **MERGE-READY @ a326ef8a: M4-A2P-1950 (the Lead's 18:04 item; audio's Act II ids are M4-A2P-1950–1979), the Act II mix pass as played, Ch10–Ch13.** The cue tables need no renders (17:44 entry below).
  - **Loudness steps** (`tools/audio/act1_mix_pass.py --act 2 --chapters ch10,ch11,ch12,ch13`, report `docs/kb/audio/act2_mix_pass.md`): 40 hand-overs, **0 over 3 LU**.
    - Cutscene cue → cue and → field: all within 0.2 LU, except a boss cue handing back to its zone (+1.9 to +2.1).
    - Field ↔ the regular battle: within 0.1 LU.
    - Field ↔ boss (Drowner, Lamp Engine, Ram): the bosses sit ~2 LU under the field, by their rows' `volume_db`, as Act I's do, so the fight carries its own weight.
    - **Victory → field (new pair):** the sting at its own momentary rule (-16.0) against each zone loop (-16.0 to -16.1): 0.0 to 0.1 LU, and the field fades in under it.
  - **Silences:** none (`act1_playthrough.py --act 2 --holds`, with the direction notes' holds).
  - **Doubled starts:**
    - Both cutscene → battle seams carry the same cue straight on with no restart: `ch11_the_engine` → `lamp_engine`, `ch12_weeping_wall` → `avalanche_ram`. The Drowner fight starts from the zone flow.
    - The one repeated `@music` (`ch13_still_city`'s second node, `ch13_sefirs_house`, says `ansedra` again) is harmless: the deck leaves a sounding cue be, and that node can play on its own.
  - **Tool:** the mix pass gains `--act`, `--chapters` and the victory → field pair. An encounter's chapter comes from its id (ch10_…), not just Act I's `ch0N`. A new test case covers Act II, and Act I's run is unchanged (98 hand-overs, 0 over).
  - **Task:** `docs/kb/tasks/M4/M4-A2P-1950-act2-mix-pass-ch10-13.md` (review: lead).
  - **Checks:** test_act1_mix_pass 3/3; taskboard --check clean. Tools only, so no Godot run. **Skipped:** screenshots, Blender, coverage.
  - **Next, unless the Lead says otherwise:** the same pass on Ch14–Ch16 (M4-A2P-1951), as their staging lands.
- **Re the Lead's 17:44 message ("render the Ch12–Ch13 cues from the cue tables, then Ch14–Ch16"): there is nothing to render. Ch12–Ch16 are MERGE-READY @ 0266514c (one line per chapter, below).** Checked again at 17:50:
  - **On integration** (e605c9f4, big26, without claude/audio), every one of the 70 refs in f5f0be21's tables has its file on disk: each music cue's own file or its stand-in's, each `@sfx` file. That is missing = []. So the tables play today even before this branch merges.
  - **What this branch adds for those chapters:** the six FAST-TRACK placeholder SFX replaced by their own cues (b4dcb22a), Ch14's low C held to "No." (0266514c), and longer binding tails (b39dfacb).
  - **Merged big26 @ 1363f80d:** dlgc regenerated the two compiled scenes that conflicted. Integration's new `ch15_the_dock_master` took shot H06 from `ch15_current_song`, which `test_direction_holds` caught; its hold moved with it. After the merge: no Act II music gap, cutscenes 0, dlgc --check 0, validate_data 0.
  - If the Lead means a different set of cues (another table, or cues to replace rather than add), name them in a LEAD-ANSWER and I'll do them at once.
- **MERGE-READY @ 1363f80d** (everything above, on big26).
- **Re the Lead's 17:24 message ("status? Ch12 cues, then Ch13–16; Lamptongue audio is yours"):**
  - **Ch12–Ch16 are done:** MERGE-READY @ 0266514c per chapter (below; pushed 17:00, answered again at 17:09). act2-plan's tables have no missing cue to render.
  - Not idle: the 17:04–17:20 entries below are on claude/audio. This line restates them only because messages here can't be answered by message.
- **MERGE-READY @ 688bd032: Lamptongue** (the Lead, 17:24; act2-plan's drafts README: "Audio owns the lyrics").
  - **`docs/kb/audio/lamptongue.md`**, the lyric sheet:
    - **Language and voicing:** the language (roots, juxtaposition, a doubled word is an address, *re* is "again", stress, *oan* and *ennu* as two syllables). Until SPEC §16 Q4/Q5 chooses a voice, the vocalise sings the texts' vowels.
    - **The Hush's eight verses, fixed:**
      - Verse 1 (Ch3) as written.
      - Verse 2 (Ch5) is **final as written** (ch05_kahre's "Audio sets the final text").
      - **Verses 3–7 are new**, one per Vowbound from its own world: Virel's kite of fire, Nhoa's deep water, Hesk's counted cords, Ethren's still water, Kesh's first storm. Each ends on *mir*.
      - **The Eighth Verse, the Letting**, is new: the first verse turned over, ending on *tash*.
    - **Act III's placeholder lines, final texts:**
      - `ch19_words_001` is the Eighth Verse as cut in the stones; `_002` is Asha's first line and last word.
      - `ch20_fight_006` *Mir, mir. Tash.* is kept.
      - The Cage founders' other lines are built from five named roots.
      - H07 is verse 8 on `motifs.letting()`.
  - **Glossary:** eight new roots (*arre, seli, aun, thel, sen, sev, kor, una*) in their own appended block. They collide with no glossary, loc or banned term, and validate_data's banned-terms grep is 0.
  - **No game file changes:** the shipped scripts already carry verses 1–2 as written. The bound stings stay instrumental until a voice is chosen; then they take their verse's first line.
  - **LEAD-ASK:** act2-plan's drafts (`docs/kb/story/act3/drafts/ch19_the_words.dlg`, `ch20_*`) still have the placeholder text. act2-plan takes the final lines from lamptongue.md §3 (I don't edit their branch).
  - **Checks:** validate_data 0 (it greps the glossary and every .dlg for banned terms). Docs only, so no Godot run.
- **Re the Lead's 17:04 message ("idle since 16:53; render the missing cues, Ch12 first"):**
  - The 16:45 item was done and pushed by 17:00, with MERGE-READY @ 0266514c per chapter, Ch12–Ch16 (the entries just below; head 8956ca68).
  - **The cue tables have no missing cues.** All 70 refs (36 distinct) at f5f0be21, unchanged on act2-plan since, play delivered renders. The only wrong ones were the morning FAST-TRACK's six placeholder SFX, now restored to their own cues (b4dcb22a). Ch14's low C now holds to "No." (0266514c).
  - **LEAD-ASK:** act2-plan's branch still names those six placeholders (`barge_pole` ×6, `hearth_crackle`, `undertow_wall_roar`, `current_song`) on the same lines. When both merge, keep claude/audio's ids (`pole_no_wake`, `pole_stroke`, `pyre_crackle`, `storm_wall`, `current_song_hum`, `barge_no_wake`), or ask act2-plan to take them.
- **The Lead's 16:45 item: score Ch12–Ch16 from act2-plan's audio cue tables** (`## Audio cues by shot` in `act2_ch12..16_direction.md`, f5f0be21 on claude/act2-plan).
  - **What the tables hold:** 70 `@music`/`@sfx` refs, 36 distinct, by shot. Every one already resolves: the 15 music refs through sequencer stand-ins point at the real Act II renders of the same name, and `hush_first_verse` → `hush_theme_v2` is ADR 0204 §12's reprise. So there was nothing new to render.
  - **Placeholders:** the morning's FAST-TRACK (ab6b7704) had made the scripts resolve by renaming six script SFX to existing generic sounds. Their own cues have since been delivered (`act2_cutscene_sfx.py`), so the scripts now name them again (b4dcb22a; `dlgc` recompiled only those five scenes).
    - **Lines restored:**
      - `pole_no_wake` (Ch13 still city);
      - `pole_stroke` ×4 (Ch14 first ripple);
      - `pyre_crackle` (Ch15 pyre-raft);
      - `storm_wall` and `current_song_hum` (Ch16 swept away);
      - `barge_no_wake` (Ch16 the High Warden).
    - **act2-plan:** their branch still has the placeholders on the same lines. Whichever merges second keeps these ids (a one-word merge each).
  - **Timing against the notes' holds:** `docs/kb/audio/act2_direction_holds.json` now carries the Ch14–Ch16 notes' stated holds too (W03, L02, L10, U01, U02, K11, H06, C01, C09, C13). With them, `act1_playthrough.py --act 2 --holds` finds no music gap anywhere in Act II.
    - **Ch14's one gap was audio's fault, not a question for Story.** The cue sheet makes `peace_wedding_break` "end in a held low C", and the script hard-cuts it (`@music silence fade=0.0`) on Asha's "No.". The C had run out ~12 s before. It now holds 18 s longer, settled 12 dB down, under the loudness gate (44.2 s; -15.96 LUFS; `--determinism` identical) (0266514c).
    - `test_direction_holds` no longer excuses any scene.
  - **Staging:** slice-polish has staged only Ch10 (`game/data/cutscene/ch10/`). The cues above are wired in the scripts, so nothing more is needed as each chapter's staging lands; I'll rerun the gap check on each.
  - **Checks (all chapters):** dlgc --check 0; validate_data 0; the Act II audit's cutscenes 0; test_cutscene_sfx_files, test_direction_holds, test_audio_loudness and test_audio_data OK; Godot music_transitions 7/0. **Skipped:** screenshots, Blender, coverage.
- **MERGE-READY @ 0266514c (Ch12):** every cue resolves to its render. With the notes' holds, `hesk_bound`'s tail (b39dfacb) covers C03 → C06 with ~7 s to spare. No change.
- **MERGE-READY @ 0266514c (Ch13):** `pole_no_wake` restored on A02. `ethren_bound`'s tail covers S07 → S09. The notes' "A05 is half a beat" falls under `ansedra`, a loop.
- **MERGE-READY @ 0266514c (Ch14):** `pole_stroke` ×4 restored on L02 and L03 (×3). `peace_wedding_break` holds to "No.". The notes' W03 ≥ 5 s and L02 ≥ 6 s fall under looping cues.
- **MERGE-READY @ 0266514c (Ch15):** `pyre_crackle` restored on H13. `kerrid_at_sea`, `hollowmere_answers` and the Ch15 SFX resolve. U01 (8 s) and H06 (≥ 8 s) fall under `unlamped`/silence as written.
- **MERGE-READY @ 0266514c (Ch16):** `storm_wall` (S01), `current_song_hum` (S02) and `barge_no_wake` (C10) restored. `kesh_bound`'s tail covers C04 → C05. C01, C09 and C13 fall under `drowned_choir`/`sefir_go_home`. B10's hard cuts are the scripts' `fade=0.0` lines (the deck's 0.2 s floor), as the notes ask.
- **BACKLOG EMPTY (after 0266514c):** waiting on slice-polish's Ch11–Ch16 staging (each gets a gap-check rerun), the people bosses' encounters, and the listening verdict.
- **MERGE-READY @ b39dfacb: the Lead's 16:27 item, the Ch12–Ch13 cutscene cues against act2-plan's direction notes** (`act2_ch12_direction.md`, `act2_ch13_direction.md`, on integration since big24; integration merged). Ch15–Ch16 ambience was already done (529a1f3c).
  - **What the notes change for audio:** time, as with Ch11. The scenes run about 3–5x their scripts' floor (B10–B11 Hesk 0.83 → 4.5 min, B05–B06 Ethren 0.86 → 6.5 min), with long held shots (K06 ≥ 5 s, S02 ≥ 8 s, S05 ≥ 6 s, A01 8 s, B13's rail ≥ 40 s).
    - Every Ch12–Ch13 scene sits under a looping cue (keth_pass, cloudloom, ansedra, lamp_archive, sanctum_of_the_level) or an intended `@music silence`, except the two bindings.
    - The notes' "P03: no music cue" is already so; B13's ≥ 40 s rail is under `keth_pass`.
  - **New tool option:** `act1_playthrough.py --holds docs/kb/audio/act2_direction_holds.json` applies the notes' stated shot holds (Ch11–Ch13, 13 scripts) to the timeline, so a one-shot cue's gap is measured against the staged scene. With them, the only gap in Act II is still `ch14_the_vows` (Story's question).
  - **Margins:** the binding tails (44c4ae1a) covered the staged scenes, but with only 1–2 s to spare (Hesk 1 s, Nhoa, Ethren and Kesh 2 s), and the notes' unmeasured pauses (Ch12's "2 s after 005", Ch13's 2 s for Ysolde's laugh) could eat that. Each tail is now 6 s longer (Nhoa 22, Hesk 20, Ethren 15, Kesh 12); the scene's next `@music` cross-fades over it.
    - Kesh's low pad then rose over the loudness gate and the -3 dBFS ceiling held its gain (-17.4 LUFS), so its tail is quieter (`TAIL_VEL`); it's back at -16.1.
  - **New test:** `tools/tests/test_direction_holds.py` checks that every script and shot in the holds file exists (a renamed shot can't drop out unseen), and that with the holds Act II has no music gap but the known Ch14 one.
  - **Checks:**
    - Renders `--determinism` identical; test_audio_loudness, test_audio_data, test_act1_mix_pass and test_direction_holds OK; validate_data 0.
    - Godot: music_transitions 7/0, creature_vowbound_act2 28/0.
    - **Skipped:** screenshots, Blender, coverage.
  - **Next:** act2-plan's Ch14–Ch16 direction notes are on claude/act2-plan, not yet on integration. When they land I'll add their holds to the file and rerun.
- **BACKLOG EMPTY (after b39dfacb):** waiting on the Ch14–Ch16 direction notes (integration), slice-polish's staging, Story's answer on ch14_the_vows, the people bosses' encounters, and the listening verdict.
- **MERGE-READY @ 21638070: the Lead's 16:09 item, the jog's footsteps on big24 (efe7fb10) and the victory → field handoff on the resident return** (995b61f1, 21638070; integration merged, c7f22ea1).
  - **Jog footsteps:** the heroes' steps come from the body's `foot_contact`, which fires on the clips' `foot_l_down`/`foot_r_down` markers. hero_clips.py places those on each heel strike from its own plant schedule, so the steps re-time with the jog: Asha, Rhen and Toma's `run` is 0.733 s with the feet 0.367 s apart (164 a minute).
    - Measured on the real Haluna scene and Rhen's body (new `tests/integration/test_footsteps_jog.gd`): a 3.55 m/s jog plays `hero_step_sand_run` every 0.367 s exactly (163.6 a minute, 13 intervals), with no doubled step.
    - The distance fallback is `run_step_m` 1.3 since 5fb30861, and the test holds it to the jog.
  - **Surfaces:**
    - Oruvel is its planks (`wood`, its zone default) with the sea round it wading (`water`) (new test).
    - Haluna is sand, with the dock's planks and the shallows; the causeway is stone slabs over sand flats and the sea (test_footsteps_slice_zones 5/0, on big24's scenes).
    - The run rows are the surfaces' own `*_run` rows.
  - **Victory → field on the resident return** (integration-qa's 99989c2b: the field kept through a random fight, about 0.39 s of black):
    - The router still emits `scene_swapping` on the way back, so `apply_zone` starts the zone's cue under the fade.
    - Zone loops resume (27 of the 32 zone cues, every Act II one), so it picks up where the fight interrupted it, on a beat of its own, over the 1.5 s crossfade.
    - On the quickest Return (0.45 s after victory, `battle_out_sec` 1.2 still fading) the cue is back within 0.7 s, from its resume point, still fading in under the 2.4 s victory sting. The sting is on Combat, which no zone change fades (new test in test_zone_return, 9/0).
    - The arena's beds hand back to the field's when the battle's listener leaves, whichever comes first (arena_ambience 5/0).
    - No data change was needed: `battle_return_sec` 0.3 / `battle_return_fade_sec` 2.0 still cover a battle that ends in place.
  - **Checks:**
    - Godot: footsteps_jog 3/0 (new), footsteps_slice_zones 5/0, footstep_contacts 8/0, hero_foot_contacts 5/0, zone_return 9/0, battle_audio 22/0, arena_ambience 5/0.
    - validate_data 0; test_cutscene_sfx_files and test_audio_data OK. The merge took integration's own empty to-do lists and both sides' PROVENANCE rows.
    - **Skipped:** screenshots, Blender, coverage.
  - **PC-QUEUE:** the jog on sand, planks and stone, by ear (the density at 164 a minute); a quick Return after a victory.
- **BACKLOG EMPTY (after 21638070):** waiting on slice-polish's Ch11 staging, Story's answer on ch14_the_vows, the people bosses' encounters, and the listening verdict.
- **MERGE-READY @ 5fb30861: the Lead's 14:28 and 15:08 items, the silence-gap check over the staged Act II cutscenes (Ch10–Ch11) and the jog's footsteps** (8ee646e0, 5fb30861). Ch15–Ch16 ambience was already done (MERGE-READY @ 529a1f3c below).
  - **Staging and timing:** the Ch10 staging (`game/data/cutscene/ch10/*.json`) holds shots and marks only. Walks don't stretch a scene: none of the Ch10–Ch11 scripts waits on one (`@wait arrive=`) or on a music marker. So the timeline is the scripts' `@wait`s and lines, plus the Ch11 direction notes' longer holds (Ch11 has no staging yet).
  - **Ch10 gap:** cinematics' `@music farewell_tide_release fade=0.5` (now on integration) left about 6 s of nothing under B10. The 16 s release ended before Pell and Kerrid's back-to-back shot, which closes on its own `@music silence fade=3.0`. The release now carries the backs-turned on: two more harp roots, softer, a bar apart, with clicks (26.4 s). The gathering loop is byte-identical, and the release's level is still set by its top note.
  - **Ch11:** the four binding gaps were closed in 44c4ae1a. With the notes' holds every other Ch11 scene sits under a looping cue. `act1_playthrough.py --act 2` now finds no gaps in Ch10–Ch13 or Ch16. Only `ch14_the_vows` (~12 s) remains, a question for Story (below).
  - **Tool fix:** `render_all.py` checked every file in a `music_loop` job as a loop and crashed on the one-shot release. Now only a file with its own `.loop.json` is checked as a loop.
  - **Jog footsteps** (characters' b344b974, coming in big24): the jog's clips keep their `foot_l_down`/`foot_r_down` markers, retimed to a step every 0.367 s (164 a minute), so the heroes' steps follow the new stride with no change. The distance fallback assumed a 1.0 m run step (~213 a minute at 3.55 m/s), so footsteps.json now uses `run_step_m` 1.3 (the 2.6 m stride's half) and `stall_m` 1.9 (about 1.5 steps, as before). After big24 I'll recheck that the markers arrived and listen to the density.
  - **SFX to-do lists:** `test_cutscene_sfx_files` was red on integration because its to-do lists still held the eleven Act II cutscene SFX and `kesh_memory`, all delivered. Both lists are empty now.
  - **Checks:**
    - Renders: `farewell_tide` `--determinism` identical; act1_playthrough as above; validate_data 0; test_audio_loudness, test_audio_data and test_cutscene_sfx_files OK.
    - Godot: creature_vowbound_act2 28/0, music_transitions 7/0, footstep 23/0, field_audio 22/0.
    - **The tools suite (-j 4):** red on 8 units that are red on integration too (`origin/claude/new-session-mj8c3c` @ 8fe3644b): test_avalanche_ram, test_causeway_gameplay, test_oruvel_underway_kit, test_palette_check, test_qa_flag_reach (`ch14_steps_held` has no setter), test_screenshots, test_status_names, test_villagers (`ch13_ethren.dlg: tender paint_gilt_line` has no clip). None is audio's.
    - **Skipped:** screenshots, Blender, coverage.
  - **PC-QUEUE:** the farewell-tide's B10 under the release's tail; the jog's footsteps after big24.
- **BACKLOG EMPTY (after 5fb30861):** what's left waits on input: big24 (the jog), slice-polish's Ch11 staging, Story's answer on ch14_the_vows, integration-qa's resident return, the people bosses' encounters, and the listening verdict.
- **MERGE-READY @ 44c4ae1a: the Lead's 13:48 item (2 of 2), Ch11's cues against act2-plan's direction notes** (`docs/kb/story/beats/act2_ch11_direction.md`, on claude/act2-plan).
  - **What the notes change for audio:** act2-plan's script updates are camera ids (V00, V10, T00) and Pell's mark (`pell_kneel`); no `@music`, `@sfx` or `@anim` changed. Every Ch11 cue resolves: the Act II audit shows cutscenes 0, and every `@anim` and walk has foley (the Vey and the sanctum are stone). What changes is time: the holds roughly triple the scenes (B03 1.1 → 3 min, B09 1.3 → 4 min).
  - **Checked scene by scene against the new holds:**
    - B01 V00 8–10 s under `sunken_vey`; B03's `@music silence fade=1.5` lands on the walk away, as the notes want.
    - B05 `lamp_engine` carries straight into the battle: same cue, no restart, and the tide-line dip releases before the black.
    - B07 T03's open-ended hold rides `cs_glimmer_lift` and the hall's bed (the fast battle return waits for the scene).
    - B10 and B11 are fine.
  - **The one fault was B09 `ch11_nhoa`:** the 8 s `nhoa_bound` sting ended about 12 s before the scene's next `@music`. With the notes' N09 hold (6 → 8 s) that was about 14 s of the music simply stopping while Nhoa turns to Pell and Kerrid stands behind him.
    - Fix: each `*_bound` sting now holds its light, a quiet pad on its last colour and one glass ring, steady (bound light never pulses), fading out over a tail (`vowbound_stings.py` TAIL). The scene's next `@music` cross-fades over it.
    - `nhoa_bound` gets 16 s; Hesk (13 s gap), Ethren (7 s) and Kesh (4 s) had the same fault and get 14, 9 and 6 s.
    - Integrated stays -16 LUFS. Momentary max moves 0.1–1.0 dB (Hesk's bell under the tail's pad). The summon stings are unchanged.
  - **Checks:**
    - `act1_playthrough.py --act 2`: the four binding gaps are gone.
    - Renders `--determinism` identical; validate_data 0; test_audio_loudness and test_audio_data OK.
    - Godot: music_transitions 7/0, vowbound 117/0 (its one left node is the same on the previous commit), audio_runtime 11/0.
    - **Skipped:** screenshots, Blender, coverage.
  - **Left for the scripts' owners** (not in this item; one line each):
    - `ch14_the_vows` still goes ~12 s without music after `peace_wedding_break`, before its `@music silence`. Story: is that silence meant? If not, I'll give it a tail the same way.
    - The scripts' `fade=0.0` lines play as 0.2 s fades (the deck's floor), as before.
  - **Not done:** N02/N08's "through the water" shots could take mix.json's `muffle`, but that's a proposal for cinematics, not a fault.
  - **PC-QUEUE:** the binding scenes' tails under the holds (B09 especially).
- **BACKLOG EMPTY (after 44c4ae1a):** what's left waits on input: slice-polish's Ch11 staging (`game/data/cutscene/ch11/*.json`), Story's answer on ch14_the_vows, integration-qa's resident return, the encounter spacing, the people bosses' encounters, and the listening verdict.
- **MERGE-READY @ 529a1f3c: the Lead's 13:48 item (1 of 2), the Ch15–Ch16 ambience loops and arena switching.**
  - **Gaps found:**
    - Hollowmere's first visit (`ch17/hollowmere`, Ch15 B10–B12) had no music or ambience row. The beat sheet (act2_ch15.md §6) says "ambience only, no zone loop": it is grief, and Act III's `hollowmere` cue belongs to Ch17.
    - The Ch15 dawn in fog at the bow (B09) had no bed of its own.
    - The Ch16 storm set piece (`ch16_holding_the_line`) fought on the moonrise Choir's bed.
    - Two of the beat sheets' SFX (`shoal_hum`, `choir_wind_chord`) didn't exist.
  - **New loops** (`act2_ambience.py`, appended so the earlier beds stay byte-identical):
    - `hollowmere_flotilla`: water among the hulls, two tide-wheels, a pump, gulls, far hammers, low voices; no laughter, no song.
    - `open_sea_fog`: `ch15/open_sea` swaps to it once B08's `ch15_pell_said_he_knew` is set, through the zone's `night` list.
    - `choir_storm`: the mouths roaring in a gale, surge and spray.
  - **Arena switching by encounter:** ambience.json `encounters` is tried before the arena (`AudioData.battle_beds`). `ch16_holding_the_line` plays `choir_storm` over `choir_bowl`, and `ch16_abiding_guard` keeps the Choir at moonrise. The encounter isn't written yet, so it's listed under `pending_encounters` and `data_check` accepts it.
    - Ch16's random fights (`ch16_rim_*`) have no arena yet (`pale_rim_shallows` is env-art-b's gap), so the field's `pale_rim_shallows` bed carries on under them, which is right.
    - The wade's footsteps are the `water` surface, already set for pale_rim.
  - **SFX:** `shoal_hum` (Ch15 B06, the held dead's hum and a sideways glass shimmer) and `choir_wind_chord` (Ch16), as rows in `sfx_cutscene_act2.json`, ready for a script's `@sfx`.
  - **Checks:**
    - Renders: the beds at -26.1 LUFS, seams flux ≤ x1.48, `loop=true` in their imports, re-rendered byte-identical. The SFX are `--determinism` identical and the earlier cutscene SFX unchanged.
    - Data and tools: validate_data 0; the Act I and Act II audits 0; test_audio_data, test_audio_loudness (two target rules added) and test_act1_audio_audit OK.
    - Godot: arena_ambience 5/0 (two new), battle_audio 22/0, audio_runtime 11/0, field_audio 22/0.
    - **Skipped:** screenshots, Blender, coverage.
  - **PC-QUEUE:** the fog swap at the bow, Hollowmere's first visit, the storm set piece.
- **MERGE-READY @ b436efa1: the Lead's 13:08 item, the Act II battle arenas' ambience and Ch11's cues** (b436efa1). The 12:28 item was already MERGE-READY @ 023c94f1 below.
  - **Arena beds:** before, a battle had no ambience of its own. The field's beds carried on 3 dB down, and with integration-qa's resident field nothing would have reset them. Now the encounter's arena (encounters.json `arena`) plays ambience.json `arenas` beds in place of the field's, fading over `arena_fade_sec` 1.0. The field's beds come back when the battle's listener leaves (`AudioDirector.set_arena_ambience` / `release_arena_ambience`, owned by its `BattleAudio`). A retry's new listener keeps the beds; an arena with no row keeps the field's.
    - Five new loops (`act2_ambience.py`, appended so the 14 existing beds stay byte-identical): `arena_fen_roots` (Ch10, the Drowner's mudbank: the fen gone quiet), `arena_engine_hall` (Ch11, the engine's throb near), `arena_seep_terrace` (Ch12), `arena_lagoon_dusk` (Ch14, Malcor Venn on the barge, a far wedding bell) and `arena_court_steps` (Ch14).
    - `bridal_barge_night` uses `open_sea_night` and `drowned_choir_ring` uses `choir_bowl`: same places.
    - `data_check` checks every arena id and bed.
  - **Ch11:** every `@music`, `@sfx` and `@anim` in the Ch11 scripts resolves; the Act II audit shows cutscenes 0. Ch11 has no staging yet on claude/m2-slice. The one silent Ch11 piece was the Lamp Engine's new conduit crawlers (big22): `crawler_mend` (leg-ticks, a spark, the bound light humming back up) and `crawler_tend` now sound (`act2_skill_sfx.py`, appended).
  - **Checks:**
    - Renders: all 19 Act II beds rendered, the old 14 unchanged; the 5 arena beds at -26.1 LUFS, seams flux ≤ x1.49, `loop=true` in their imports, re-rendered byte-identical; the crawler skills at -19 and `--determinism` identical.
    - Data and tools: validate_data 0; the Act I audit 0 and the Act II audit 0 (skills now 0); test_audio_data, test_audio_loudness and test_act1_audio_audit OK.
    - Godot: arena_ambience 3/0 (new), battle_audio 22/0, audio_runtime 11/0, zone_return 8/0, battle_stings 7/0, field_audio 22/0.
    - **Skipped:** screenshots (no scene or shader), Blender, coverage (nothing under game/battle or game/progression).
  - **PC-QUEUE:** the five arena beds under their bosses' cues; the field coming back after a fight.
- **BACKLOG EMPTY (after b436efa1):** what's left waits on input: Ch11 staging (slice-polish), integration-qa's resident return, the encounter spacing, the people bosses' encounters, and the listening verdict.
- **MERGE-READY @ 023c94f1: the Lead's 12:28 item, the victory sting into the field over the short return, then the battle-start stinger over the new encounter spacing** (e271faa7, 023c94f1).
  - **Victory → field:** before, the zone's music came back only through the router's `apply_zone` on the swap, or after 3 s of silence (`zone_return_sec`). With integration-qa's resident field, under 1 s back and no swap, that left a 3 s gap after the sting. Now, once a battle leaves the tree, the zone's cue returns after `battle_return_sec` 0.3 and fades in over `battle_return_fade_sec` 2.0 (mix.json; `AudioDirector._step_zone_return`, `_after_battle`).
    - It sits under the sting's 2.4 s tail. The sting plays on the Combat bus from the director's own SfxBank, so neither the scene change nor the music clips it.
    - If a scene or a swap takes the music first, its own cue stands. A defeat keeps the battle in the tree through its result screen.
    - Tests: `test_zone_return` 8/0 (two new).
  - **Battle-start stinger:** the tide line rises over 0.5 s and holds for 0.25 s, the router goes black at 1.10 s, and the battle cue enters from about 1.1 s with a 0.3 s fade. The old `sting_tideline` crested at 1.55 s, after the cut and on top of the battle cue's first bars. It is re-rendered to crest with the line at 0.5 s and is about 16 dB down at black, total 1.8 s.
    - The field music now dips 3 dB under it as the field dims (mix.json duck `encounter`; battle_stings.json `duck_sec` 0.75 = rise + hold). It is released before the black, so the battle cue never enters ducked. A test reads battle_transition.json and `SceneRouter.FADE_SEC` to keep that true.
    - With 30–45 s spacing, the row's 1000 ms cooldown can't drop a stinger. `BattleRequest` already refuses a second request while one opens (M3-BPR-427).
    - Tests: `test_battle_stings` 7/0 (one new).
  - **Checks:** validate_data 0 errors; gdlint and gdformat clean; the `battle_stings` render byte-identical with `--determinism` (the other five stings are unchanged); Godot battle_stings 7/0, battle_audio 22/0, audio_runtime 11/0, zone_return 8/0. **Skipped:** screenshots (no scene or shader touched), Blender, and coverage (no game/battle or game/progression changes).
  - **Note:** integration-qa's resident return and act1-chapters' spacing haven't landed on integration yet. Both changes are data-driven, so if the return path changes I'll re-check the timings as they land.
  - **PC-QUEUE:** a victory into the field with the short return (no gap, the sting's tail intact), and two encounters 30 s apart (the crest with the line).
- **BACKLOG EMPTY (after 023c94f1):** the Lead's 12:28 item is done. What's left waits on input: integration-qa's resident return, the encounter spacing, Ch11+ staging, the people bosses' encounters, and the listening verdict.
- **MERGE-READY @ 11463e21: the Lead's 11:48 item, the Act I foley detail audit as played** (4284c13d, plus the tests' follow-up).
  - **Footsteps:** every surface has its walk, run, stop and turn, but Ysolde, Kerrid and Liss clinked Rhen's lantern on every other step (gear_default). They now carry their own: Ysolde's lacquer book and ink-guards, Kerrid's anchor-ring, Liss's harness and launcher. There are no separate wet-stone, reed or shell grounds yet: those zones play stone or sand (env-art marks areas).
  - **Interactables:** every one played the menu's soft `ui_interact` only.
    - Ch8's **Coilspire flue-key trial** had no sound of its own. Its keys opening and shutting, the coughs, the lit tiers, the niche and the seized key now play (`coilspire_sfx.json`, through the Ashcrown listener, which gains `by_arg`).
    - Field objects play their own sound when used (`InteractAudio`, `interact_sfx.json`): the Oruvel lashings, the underway's tethers, hinge and tin, the quench charm, and the wake's shut inn door.
    - Talkers, shops, shrines and anything that opens a cutscene are voiced there.
  - **Walla:** Haluna by day, Oruvel, Tamsule and Pemakar had it. Corrow (Ch8) and the Ch4 wake had none, and now each has a people layer 4 dB under its bed (`act1_walla_ambience.py`).
  - **Battle hits and guards by material:** a blow sounded the same on a shell and on an eel. A landed weapon blow now adds what it struck: shell, soft, feather, wood, stone, metal or spawn (`choreo_sfx.json` materials for all 28 Act I foes). A bracing shell or stone has its own guard. Liss's launcher has its accent (she fell back to claw), and the biters have teeth.
  - **Checks:** every render byte-identical twice; the walla seams OK (flux x1.87 and x0.40); validate_data 0 errors; test_audio_loudness, test_audio_data, test_act1_audio_audit and test_vowbound_sfx OK; the Act I and Act II audits 0; Godot foley_detail 4/0, ashcrown_audio 3/0, choreo_audio 17/0, footstep 23/0, field_audio 22/0, battle_audio 22/0, audio_runtime 11/0, zone_return 6/0. **Skipped:** screenshots (no scene touched), Blender.
  - **PC-QUEUE:** the struck layers under the hits, the walla under the Corrow and wake beds, the flue trial.
- **BACKLOG EMPTY (after 11463e21):** the Lead's lists are done. What's left waits on input: Ch11+ staging (cinematics), the people bosses' encounters, Act II features, and the listening verdict.
- **Ch10 cutscenes against cinematics' staging (the Lead's 11:27 item; claude/m2-slice @ 5ca7eb69):** every Ch10 script's `@music`, `@sfx` and `@anim` resolves to a real cue or row. I checked the staged versions of ch10_farewell_tide and ch10_fen_edge in my tree: the Act II audit stays 0 and test_cutscene_sfx_files passes. The timeline check finds no Ch10 gaps or cuts, and the staging files (ch10/ossa_fen.json, reedhollow.json) carry no sound references. The one open item is cinematics': `@music farewell_tide_release fade=0.5` on the release gate. Until it lands, the gathering loops on to the scene's `@music silence fade=3.0`, which is not broken, just missing its top note. Ch11 has no staging yet; I'll score it as it lands. Nothing to push for this item (no change); the Act I transition pass is MERGE-READY @ 2b5a7593 and the farewell-tide split @ 4b32e8a9.
- **MERGE-READY @ 4b32e8a9: Ch10's staging synced (the Lead's "sync Act II cutscene cues to slice-polish's Ch10 staging"); M4-CIN-1301 in review with cinematics.** Cinematics' Ch10 staging (claude/m2-slice, 9dcc3c31/5ca7eb69) holds the farewell-tide on a release gate and was waiting on audio for the score in two parts.
  - `farewell_tide` is now the gathering: bars 1-14 as composed (the clutch climbs a step short of the top), then a 20 s loop (seam flux x1.11) that holds while the player holds.
  - `farewell_tide_release` is the top note held while the clutch turns, then the backs turned, ending on the rise. Its top note sits 1 LU over the loop, and a release anywhere in the loop lands between -1.1 and +2.2 LU.
  - **For cinematics:** add `@music farewell_tide_release fade=0.5` after `<<event release_input release_tide>>` in ch10_farewell_tide.dlg (on claude/m2-slice). Both cues have sequencer stand-ins.
  - **Checks:** byte-identical re-render; the loop seam OK; validate_data 0 errors; test_audio_loudness, test_audio_data and test_cutscene_sfx_files OK; Godot music 11/0.
- **BACKLOG EMPTY (2026-10-30, after 4b32e8a9):** the Lead's 10:27 list is done. What's left waits on input: Ch11+ staging as cinematics lands it (each scene cue retimed to its staged scene, as kerrid_at_sea and farewell_tide were), the people bosses' encounters, the remaining §4 families as their features land, and the listening verdict.
- **MERGE-READY @ 2b5a7593: the Lead's 10:27 item, the Act I as-played pass on 0347aa74** (report: docs/kb/audio/act1_playthrough.md). Every Act II cue the Lead listed already existed; the audits are 0, and test_cutscene_sfx_files plays every Act II `@music`.
  - **Fixed: the field fell silent.** A scene ending on `@music silence` or a one-shot (24 Act I scenes), or a battle ending in the zone it began in, left the field silent until the next scene swap. AudioDirector now brings the zone's cue back after mix.json `music.zone_return_sec` (3.0 s) of silence with no cutscene, battle or loading cue (c8fe0fa8). `tests/unit/test_zone_return.gd` covers 6 cases.
  - **Inside the scenes** (`tools/audio/act1_playthrough.py`, each script's timeline against the cues' lengths): no cuts and no double starts. Three statements end a few seconds before a quiet walk-away (ch07_empty_moorings, ch07_tavi, ch08_binding); they stay as the scenes' pacing.
  - **Loudness:** 81 hand-overs, 0 over 3 LU (act1_mix_pass.py).
  - **Act II, from the same tool:** `kerrid_at_sea` ran out about 88 s before ch15_the_shoal ends it. It is retimed to Story's scene at 270 s (2b5a7593). The 8 `fade=0.0` lines are still for Story.
  - **Checks:** gdlint and gdformat clean; Godot zone_return 6/0, music_transitions 7/0, audio_runtime 11/0; validate_data 0 errors; test_audio_loudness, test_audio_data and test_cutscene_sfx_files OK; kerrid_at_sea byte-identical twice. **Skipped:** screenshots (no scene touched), Blender.
  - **Next (the Lead's list):** sync the Act II cutscene cues to slice-polish's Ch10 staging as it lands.
- **Godot on 792ccc26 (all green):** vowbound 116/0 (one node left in the tree, as on fda21daa before this set: a test's leak, not audio's), choreo_audio 17/0, creature_audio 8/0, field_audio 22/0, document_reader 7/0, battle_audio 22/0.
- **BACKLOG EMPTY (2026-10-30, after 792ccc26):** the Lead's lists are done; the Act I and Act II audits are 0; 1010 and 1080 are in review. What's left waits on input: the people bosses' encounters (Combat), the remaining §4 families as their features land, and the listening verdict.
- **MERGE-READY @ 792ccc26: the Lead's 09:58 list on 0347aa74, plus two audio requests found on the board.** Merged 0347aa74 first.
  - **Already done, checked again:** env-art and env-art-b build exactly the 14 Act II levels, and every one has its zone music and its own bed. Battle themes for Ch13–16 are `battle_heretic` (regulars from Ch14) and the six boss stem sets. Every Act II boss sting exists, keyed by encounter id.
  - **Act I gate, red after the merge and fixed:** Nhoa's `nhoa_echo` and Hesk's `cord_lift` (new Vowbound skills, no enemy rows) were silent. Both are voiced now (`act2_skill_sfx.py`). Kesh is callable from Ch16, so she has her call sting, `kesh_summon` (`vowbound_stings.py`; Act III's H03 reuses it).
  - **M4-AUD-1010** (Combat's request, now in review): full battle voices and summon layers for Nhoa, Hesk, Ethren and Kesh in `vowbound_sfx.py`. Act I's three render byte-identical. Each has its own keepsake sound: Nhoa's bone name-shell, Hesk's holy bell, Ethren's ring click and gold bowl-halo, Kesh's brass lamp-key. All four are in `no_steps` (they hover, fly or are a column of water), and `sfx_pending` is dropped from their vowbound.json rows. Kesh's rise layer is `kesh_stand`, because the Ch16 cutscene owns `kesh_rise`. Their spectra were toned against the Act I Vowbound set. Nhoa's glass and Kesh's water stay a few dB past its medians on purpose.
  - **M4-AUD-1080** (ui-menus' request, now in review): the document reader's `ui_hand_found` (the same bar struck twice, quiet and certain) and `ui_mark` (a pen's stroke, -24), named in the DocumentReader hook. Source: `act2_ui_sfx.py`.
  - **Act I mix pass on 0347aa74:** 81 hand-overs, 0 over 3 LU, the same as the report (docs/kb/audio/act1_mix_pass.md).
  - **Checks:** validate_data 0 errors; test_vowbound_sfx, test_audio_loudness, test_audio_data, test_act1_audio_audit and test_cutscene_sfx_files OK; the Act I and Act II audits 0; Godot vowbound, ui_audio, choreo_audio and creature_audio filters running (the result follows in the next entry); every render byte-identical twice. **Skipped:** screenshots (no scene touched), Blender.
  - **PC-QUEUE:** the four Vowbound in battle; the reader's found hand.
- **BACKLOG EMPTY (2026-10-30, after 17ef4f2c):** both 10-30 lists are done, and the Act II and Act I audits are 0. What's left waits on input: the people bosses' encounters (Combat; their stings and court_steps are keyed by the planned ids), the remaining §4 families as their features land (drain and rooted, repair, part breaks, heresy and reader UI), and the listening verdict.
- **MERGE-READY @ 17ef4f2c: the Lead's second 10-30 list, and the Act I mix pass.** Merged the integration branch (7dc3ab41) first. Story's Act II scripts and Combat's boss rows had landed, so the Act II audit found new gaps; it is now **0 in every section**, and Act I is 0.
  - **Act I gate (red after the merge, fixed):** `ch01/oruvel/dive_lamp.tscn` (a light, not a level) was counted as a zone. The audit now treats only `<level>/<level>.tscn` as a level, and a test pins that. The Act II abilities Combat added without enemy rows are voiced (below).
  - **Boss music (Combat's ids):** `music.json` `battle.encounters` for ch10_mangrove_drowner, ch11_lamp_engine, ch12_avalanche_ram and ch15_wakefin, and phase rows `uprooted`, `opened`, `torn_fleece` and `close_circle` that bring stem 2 in over 3 s. Their intro stings are keyed by encounter id too.
  - **19 ability sounds** (`assets_src/sfx/act2_ability_sfx.py`), each the effect itself, made from its creature's materials, toned against the Act I ability set's spectra. `fin_cut`, `sound_dive`, `wake_breach` (the rise) and `wake_wheel` (the wash) use the Wakefin's set.
  - **Cutscenes:**
    - 61 `@anim` gestures map to foley or to silence (faces and voices).
    - 17 `@sfx` cues (`assets_src/sfx/act2_cutscene_sfx.py`): the egret, the lamp bench, the engine, the still water and the first ripple, the city's bells, the water-gate, the level pin, the pyre-raft and its lamp, Kerrid sitting, the storm wall, Liss humming the current-song, Kesh rising, the barge with no wake, the fin's first pass.
    - `kesh_memory`: the Choir through water, MEL_A sung by one far voice.
  - **Found:** the CutsceneSequencer finds `@sfx` at `sfx_dir/<id>.ogg` and `@music` by `music_dir` or a stand-in. So the Act II `@sfx` files are plain git in `assets/audio/sfx/` as Act I's are (not `assets/audio/act2/`, ADR 0175's folder), and `sequencer.json` gains 17 `music_stand_ins`; `../act2/music/<cue>` resolves in Godot.
  - **Act I mix pass** (`tools/audio/act1_mix_pass.py`, report `docs/kb/audio/act1_mix_pass.md`): 81 music hand-overs (cutscene -> field, field <-> battle, field <-> boss). 6 stepped over 3 LU, all Ch8's three-stem bosses starting on stem 1 at -19.4. `volume_db` +1.0 on the Reach and +0.5 on the seawall hold brought them to 0 over 3 LU. The beds are 10 LU under, 0 problems.
  - **For Story:** these `@music` lines use `fade=0.0`: nhoa_bound, hesk_bound and ethren_bound, peace_wedding_break, a `silence` in ch14_the_vows, and abiding_guard in ch16_swept_away. The deck holds every fade to `min_fade_sec` (0.2 s), so they play as near-cuts. That's right for the trap; the others may want 0.5.
  - **Checks:** validate_data 0 errors; test_audio_loudness, test_audio_data, test_cutscene_sfx_files, test_act1_audio_audit and test_act1_mix_pass OK; Godot battle_audio 22/0, cutscene_audio 8/0, cutscene_sound 3/0, cutscene_music_resolves 3/0, cutscene_sequencer 22/0, music_transitions 7/0, music 11/0, sting 18/0 (the whole `cutscene` filter outruns 18 min here and was stopped); every render byte-identical twice. **Skipped:** screenshots (no scene touched), Blender.
  - **PC-QUEUE:** the Ch8 boss hand-overs after the lift; kesh_memory's voice over the water; the cutscene cues in their scenes.
- **BACKLOG EMPTY (2026-10-30, after 79546256):** the Lead's list is done. The rest waits on inputs from other tracks: the `@music`/`@sfx` lines on Story's Act II `.dlg`; the encounter and phase rows (the Wakefin's skill ids included) on combat; the remaining §4 families (ripples and bells, drain and rooted, repair, part breaks, heresy and reader UI) on their features; and revisions on the listening verdict.
- **MERGE-READY @ 79546256: the Lead's 10-30 Act II list ("the remaining Act II cues"), since a6055ad2.** Merged the integration branch (3a5759ad) first.
  - **Already done before this item:** every Ch10–Ch16 field theme has its zone row, `battle_heretic` covers the Ch14–Ch16 regulars (Ch13 and Ch15 have no regular fights), all six Act II bosses have two stems, and all 14 zones have their own beds.
  - **New: `court_steps`** (Ch14's step-hold, `ch14_hold_the_steps`): two stems, a 60 s loop in C minor at 112 BPM. Stem 1 is the hold: the wedding's gong stepping, a 3+3+2 frame drum against it, the Stillguard's hum, and the couple's tune in diminution on the flute. Stem 2 is the last turn: the big drum, a building roll, the tune an octave up on bars, and a sixteenth ostinato. Every phrase ends on G, so it hands on the beat to `lagoon_escape`. Seam jump ×1.8 and flux ×0.2 against limits of ×10 and ×3.
  - **New: the people bosses' intro stings,** `sting_boss_malcor_venn` (the flat-engine's drone swelling, its gong on the slow tick) and `sting_boss_abiding_guard` (ORDER_HUM cut off by the big drum), each with a reduced-audio twin. They're keyed by the planned encounter ids `ch14_malcor_venn` and `ch16_abiding_guard`.
  - **Fixed: the Avalanche Ram's intro sting** was rendered before 114d5cf1 and still had the ice voice. It's re-rendered with the wet wool.
  - **New: the Wakefin's foley** (wakefin.md §4): `fin_cut`, `sound_dive` (says "gone deep": a falling plunk with a thrum left below), `wakefin_rise`, `wake_wash`, `bill_strike`, and `phase_close_circle` (the hull ram). Each telegraph wind-up sits in its own spot inside 1–4 kHz, checked by spectrum. The `battle_sfx.json` rows use the sheet's *proposed* skill ids; **for combat:** keep those ids, or tell audio the final ones.
  - **Checks:** validate_data 0 errors; test_audio_loudness and test_act1_audio_audit OK; the Act II audit is 0 and Act I is 0; Godot `sting` 18/0 and `battle_audio` 22/0; every render byte-identical twice. **Skipped:** screenshots (no scene touched), Blender.
  - **PC-QUEUE:** court_steps' stem change on real speakers; the Wakefin's telegraphs in the dark, against the `wakefin` stems.
- **MERGE-READY @ 114d5cf1: since 3ec09d01.**
  - **The four creature bosses' intro stings** (the Drowner, the Lamp Engine, the Avalanche Ram, the Wakefin), with reduced-audio twins. Their encounters aren't written yet, so `battle_stings.json` keys them by the intro's title key (`BOSS_TITLE_*`, choreo.json `boss_intro.by_enemy`). StingAudio now tries the encounter first, then later arguments, so a staged intro is named the moment combat writes the encounter (a new test in test_battle_stings).
  - **The Avalanche Ram's own voice lost its ice** (ADR 0204 §2): wet, matted wool shedding water. Only the ram's 7 files changed.
  - **Checks:** test_battle_stings 6/0; Godot `--filter=audio` 175/0; loudness and data OK; validate_data 0 errors; renders byte-identical twice.
  - LEAD-ANSWERED (2026-10-30): salt-glass spines on a salt-glass plinth. Its voice is re-materialled to match: glassy and brittle, no icicles. Was: Ch11's `rime_urchin` is designed with "ice-crusted spines on an ice plinth" (its sound rattles like icicles), but act2_plan notes ADR 0015's "nothing frozen" for Lowlight. Keep, or re-material it (salt-glass spines)? Default: keep until creatures answer. If it changes, its sound follows.
- **BACKLOG EMPTY (2026-10-30, after 114d5cf1):** every Act II audio item that needs no other track's input is done. act1_gpu_qa has no audio rows and no listening verdict has come in. What's left is below, each waiting on its input.
- **BACKLOG (Act II), what's left and why it waits:**
  - the `@music` and `@sfx` lines in the Act II scripts: Story's `.dlg` don't exist yet;
  - the boss encounter and phase rows: combat's encounters aren't written;
  - `court_steps`: the step-hold set piece isn't designed in data yet;
  - the rest of the cue sheet's §4 SFX families: each waits for its feature (ripples and bells with the lagoon scene, drain and rooted with M4-CMB-1001, repair and part breaks with the engine features, the Wakefin's telegraphs with its rows, heresy and reader UI with ui-menus);
  - retiming each scene cue to the final beat sheets.
  - Meanwhile I'll take Act I FAST-TRACK and PC rows first if any appear.

- **MERGE-READY @ 3ec09d01: Act II audio, all of the cue sheet that needs no beat sheet or encounter.**
  - **Every Act II zone plays:** `music.json` zone rows for all 14 levels, and 14 beds of their own (plain git under `assets/audio/act2/`, ADR 0175). The Act II audit is at **0 in every section** (`act1_audio_audit.py --act 2`); Act I is still 0.
  - **Loops:** `cloudloom` (the weaving-hall) and `sanctum_of_the_level` (one chord that never changes, flat by design).
  - **Battle:** `battle_heretic` (ADR 0204 §9; v2 darkened, measured against it). The people bosses `malcor_venn` and `abiding_guard`, two stems each. The seven Vowbound stings (nhoa, hesk and ethren bound and summoned; kesh bound).
  - **Scene cues:** farewell_tide, peace_wedding_break, lagoon_escape, kerrid_at_sea, hollowmere_answers (Liss sings, ADR 0204 §10), sefir_go_home (the Order's one sung lullaby), act2_break.
  - **SFX:** the root, snow and slate footsteps; the four variant creatures' own voices (M4-AUD-1001; scree_crawler with snow and grit, ADR 0204 §2); unravel's sound.
  - **Review fixes, each found by viewing spectrograms or level over time before commit:**
    - lacquer_court had no floor;
    - kesh_bound clipped when decoded;
    - sefir_go_home's piano sat 35 dB under the choir;
    - kerrid_at_sea's string filled the voice band;
    - the bosses' rolls cut their seams;
    - abiding_guard's guard stem sat at −36 LUFS.
  - **Checks:** validate_data 0 errors; taskboard --check; test_audio_loudness, test_audio_data and test_act1_audio_audit OK (the 105 MiB budget included); Godot `--filter=audio` 175/0, `footstep` 23/0, `music` 10/0; every render byte-identical twice. **Skipped:** screenshots (no scene touched), Blender.
  - **For combat:** `scree_slide` still has `"element": "ice"`, against ADR 0204 §2 (no frost from Ch12 to Ch15).
  - **Waiting on others:**
    - the `@music` lines need Story's Act II `.dlg`;
    - the boss encounter and phase rows, `court_steps` and the six boss-intro stings need combat's encounter ids;
    - the remaining §4 SFX families need their features: ripples and bells, drain and rooted, repair, part breaks, darkness telegraphs, heresy and reader UI.
  - **PC-QUEUE (real speakers):** the 14 beds against their zone music; sefir_go_home's sung lullaby; kerrid_at_sea under a voice; the bosses' stem changes.

- **MERGE-READY @ f86639b3: Act II, Ch10 and the two set pieces.**
  - **Ch10 zones play:** `music.json` zone rows for Ossa Fen and Reedhollow (the existing finals). Their own beds: `fen_dusk` (insects, frogs, drips in tannin water, root creak, a far fen bird) and `reedhollow_roost` (reed wind, the lagoon, a cook-fire, the clutch's wordless hum in the Kirru mode).
  - **The footstep surfaces root, snow and slate** (ADR 0204 §11), 48 files, and footsteps.json rows naming the ground of all 14 Act II levels. The Act II audit's Footsteps section is at 0.
  - **`farewell_tide`** (Ch10 C3, ~91 s): reedhollow's clutch line rising, and the Letting's first cell carried into the Kirru mode by its rhythm and contour.
  - **The wedding trap:**
    - `peace_wedding_break` (~27 s): the couple's tune cut off on the Stillguard's gong, the Order's hum close, a held low C;
    - `lagoon_escape` (~123 s): the pole's strokes, the city's bells one by one, the couple's tune reborn, Merel at the gate in C minor.
  - **The reveal:** `kerrid_at_sea` (~154 s), a bed for his telling. His bowed string stays low, under the voice band. KERRID_STAIR's tread slows until it stops, and the held motes drift sideways.
  - Every cue is −16 LUFS, its renders byte-identical twice, with a beat grid (or `"free"`) on its `music.json` row. The beds are −26 LUFS, with clean seams.
  - **Checks:** validate_data 0 errors; test_audio_loudness and test_audio_data OK (the 105 MiB budget included); test_act1_audio_audit OK (Act I still 0); Godot `--filter=footstep` 23/0 and `--filter=audio` 175/0, after fixing test_footstep_contacts_audio's hard-coded surface count. **Skipped:** screenshots (no scene touched), Blender.
  - **Not wired yet:** no Act II `.dlg` exists, so the scene cues wait for Story's scripts to name them (`@music farewell_tide` and the rest). The Drowner's intro sting waits for its boss encounter id.
  - **Next:** Ch11–Ch12 beds (rendering now) and their zone rows; then `cloudloom` and `sanctum_of_the_level`, the Vowbound stings, `battle_heretic`, the people-boss stems, and the remaining scene cues (`hollowmere_answers`, `sefir_go_home`, `act2_break`).

## FROM 2026-10-29 (Lead `session_01Bg3iP7cPGyjbX4CyniBahc`; integration `claude/new-session-mj8c3c`)
Session `session_01UPFyE9L9BA3QodpCNJEfAs`. Brief: the final-quality audit of Act I sound as played, on lead/gate-big18 (M3-AUD-864). Newest first.

- **MERGE-READY (docs): the cue sheet follows ADR 0204.** All four answers took the defaults. Ysolde's confession and the pyre-raft are now plain reprises (`@music ysolde_theme`, `@music hush_first_verse`; the `ysolde_confession` cue is dropped). The Ram's `torn_fleece` and the Wakefin's `close_circle` phases bring each boss's second stem in, and `sound_dive`'s telegraph says "gone deep", not "gone". Merged the integration branch first. Checks: validate_data, taskboard --check, banned terms.
- **MERGE-READY (tools and docs): the Act II audio inventory.** `tools/audio/act1_audio_audit.py --act 2` audits Ch10–Ch16 with the same sections as the Act I gate, report-only (exit 0). Act I behaviour is unchanged: still 0 items and still the gate. The inventory is in `docs/kb/audio/act2_audio_inventory.md`, 45 items: 14 zones with no music row or bed, 14 with no footstep ground, 4 borrowed creature voices (root_crab, fen_leech, scree_crawler, rim_crawler), `unravel` silent, and 12 "no zone yet" notes. A new test checks that the Act II scope runs and leaves the Act I gate as it was. Checks: test_act1_audio_audit (5) and test_audio_data OK; validate_data 0 errors.
- **BACKLOG EMPTY (10-30):** the Lead's Act II prep item and its follow-up are done and pushed. act1_gpu_qa has no audio rows, and no listening notes have come in. Everything else in Act II waits on ADR 0203's gate (`act1-complete`) and on Story's beat sheets.
- **MERGE-READY (docs only): the Act II cue sheet, `docs/kb/plan/act2/audio/act2_cue_sheet.md`, `draft: pre-gate`** (the Lead's 10-30 item; ADR 0203 preparation; no synth source written).
  - **Contents:** for every Act II zone, set piece, battle tier and cutscene (Ch10–Ch16): the mood, the instrumentation inside the self-synthesized palette, the key and tempo, the loop length and the transition rules. The existing finals' keys and tempos were read from their sources. It also lists 23 new SFX families Act II needs, and maps everything to M4-A2P-090…093 and M4-AUD-1001.
  - **Proposals:** `battle_heretic` (a Ch14+ regular-battle variant), `court_steps` (the step-hold), `peace_wedding_break`, `kesh_memory` (Drowned Choir under the muffle), `ysolde_confession` (a reprise), and the footstep surfaces `root`, `snow` and `slate`.
  - **Checks:** validate_data 0 errors; taskboard --check; banned terms clean. Merged the integration branch (d987cc6b) first.
  - LEAD-ANSWERED (ADR 0204, defaults taken): `battle_heretic`: a variant regular-battle cue from Ch14 on, or keep `battle_standard_v2` for all of Act II? Default: the variant.
  - LEAD-ANSWERED (ADR 0204, defaults taken): `sefir_go_home` has the Order **sing** ORDER_HUM, once, as the lullaby, and Liss sings the current-song in `hollowmere_answers`. Both touch the bible's "the Order hums; only Cantors sing". Default: sung, flagged to Narrative.
  - LEAD-ANSWERED (ADR 0204, defaults taken): new footstep surfaces `root`, `snow` and `slate` for the Ch10/Ch12 kits: env-art marks them. Default: yes.
  - LEAD-ANSWERED (ADR 0204, defaults taken): the pyre-raft (Ch15 C7) and Ysolde's confession (Ch12 C4) as reprises of Act I cues (`hush_first_verse`, `ysolde_theme`) rather than new cues? Default: reprises.
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
