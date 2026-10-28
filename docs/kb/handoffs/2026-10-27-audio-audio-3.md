# Handoff: audio, 2026-10-27, part 3 (session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)

The Lead's queue of 10-27 (after ADR 0171 was accepted), worked in order.

## Done (all pushed)
- **M3-AUD-837, ADR 0172 (proposed):** a prototype of the build-time render, `tools/audio/build_render.py`.
  - It keeps a checksum manifest with an input key per job (the job's import closure plus the toolchain), a cache,
    and a parallel `--ensure`.
  - Measured on 4 CPUs: a cold build of all 94 jobs takes 26.8 min, a warm check 1.9 s, and 895 of 896 files come out
    byte-identical.
  - The ADR sets out the trade-offs (LFS against the render against a hybrid). Nothing is switched over.
- **Queue 1, M3-AUD-831:** voices for the Act II creatures (`assets_src/sfx/act2_creature_sfx.py`, 68 files, 1.5 MB).
  - Covered: mangrove_drowner, lamp_engine, avalanche_ram and wakefin (the bosses), and tannin_archer, gallery_ray,
    rime_urchin and conduit_crawler.
  - Wired in creature_voices.json under creatures.json's keys, so they play as soon as the models merge.
- **Queue 2, M3-AUD-832:** UI sounds for the UI track's new screens (`assets_src/sfx/screen_sfx.py`, 8 files).
  - UiAudio gained `motion` whooshes (from a node's `motion()` MenuMotion; silent under Reduced motion, because
    nothing moves), `layer` rows and `initial` rows.
  - SaveMenu has its own save and load sounds, and TitleMenu its reveal.
  - ShrineTravelMenu and ReefballHud are `pending` until claude/ui merges.
- **Queue 3, M3-AUD-833 (a bug found while following up 829):** nine Act I `@music` ids were silent in cutscenes.
  The sequencer reads `<music_dir><id>.ogg`, not music.json. They now have stand-ins, and a test checks resolution
  the sequencer's way. M3-AUD-834 asks the cutscene owner to play `@music` through the MusicDeck (stems), add an
  `@stem` cue and report markers. That is what `undertow_rising`'s second-stem trigger needs.
- **Queue 4, M3-AUD-835:** a seam report over all 78 loops. `tamsule_bell` was the only one near click level, and
  it is masked (rotated to its quietest point; the other beds keep their bytes). Listening notes added for 831,
  832 and 835.
- **Queue 5, M3-AUD-836:** docs/kb/audio/act3_plan.md, the Act III motif map and cue list.
  - About 76 MB, so Act III can't ship committed.
  - The 5 MB rule means credits_suite must be split.
  - Proposal: the farewell-tide carries the Letting's first cell.
- **Queue 6:** the six todo chapter tasks (M3-C04-05, C05-04, C06-04, C07-06, C08-101, C09-06) are in review.
  - The Ch1–Ch9 thread runs show no "no music" or "no sound" warning.
  - music.json now carries markers for the Ch4 song and the Ebbing (test_music_markers.py).
  - Decided: the Ebbing's music runs on through a held pause, and the dance re-syncs on the movement markers.

## In progress
Nothing un-pushed.

## Exact next step
1. When claude/creatures, claude/battle-presentation or claude/ui merge into the integration branch, merge it
   here.
   - Then drop the `pending` flags: life.json and impact_audio.json (creatures, battle-presentation);
     ShrineTravelMenu and ReefballHud in ui_sfx.json (ui).
   - Then run `--filter=audio` and test_screen_audio against the real classes.
2. When M3-AUD-834 lands: drop the `undertow_rising` and `seawall_hold` stand-ins and tell act1-chapters to add
   `@stem 1 on fade=2.0` to C1-13 (M3-AUD-829).
3. Act II finals and Act III wait on the human's storage decision (ADR 0172). Until then: the board, and the next
   creature or UI screens as they land.

## Known issues
- The human's listening verdict is pending. The Avalanche Ram's bellow and the Drowner's moan are this round's
  biggest character risks.
- The day, afternoon and dawn zone variants (Pemakar, Tamsule, Brine Shoals) were not made: no flow switches time of
  day yet.
- Shipped audio is 70.1 of 72 MiB.

## Files touched (main)
assets_src/sfx/{act2_creature_sfx,screen_sfx,act1_ambience}.py, assets_src/music/the_ebbing.py (markers only, bytes
unchanged); game/audio/ui_audio.gd; game/data/audio/{creature_voices,sfx_creatures,ui_sfx,sfx_ui_screens,music}.json;
game/data/cutscene/sequencer.json (stand-ins, appended); tools/audio/{build_render,render_all,targets,data_check}.py;
tools/tests/{test_act2_creature_sfx,test_build_render,test_music_markers,test_cutscene_sfx_files}.py;
tests/unit/test_screen_audio.gd; docs/kb/decisions/0172; docs/kb/audio/{act3_plan,listening_notes}.md;
docs/kb/tech/audio_runtime.md; tasks M3-AUD-831..837 and the six chapter tasks.
