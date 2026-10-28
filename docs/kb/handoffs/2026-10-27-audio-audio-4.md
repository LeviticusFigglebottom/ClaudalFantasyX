# Handoff: audio, 2026-10-27, part 4 (session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)

## Done (all pushed)
- **Merges:** big11, the big12 gate and big12 (integration e930595c).
  - big12's causeway footstep test: M2-FP-108's final route is stone slabs over sand flats and the sea.
  - The shutdown freed-object error at `life_audio.gd:124`: validity is checked before the cast, LifeAudio drops
    everything in `_exit_tree`, and two teardown tests cover it (3224c1d8).
- **Git LFS approved (ADR 0039), not yet live in the cloud.** ADR 0172 is parked.
  - render_all.py has `ACT2_FINALS` and `--act2`, which render into assets/audio/music/act2/ and are never committed
    until the Lead says LFS is live (test_act2_finals).
  - **Act II finals, sources merged:** the 12 zone loops (M3-AUD-840..843: 17.4 MB measured) and the four modelled
    bosses' two-stem cues (M3-AUD-844/845: 7.2 MB). The renders sit in the composers' worktrees and scratch
    folders, and are reproducible with `--act2`.
- **The Lead's 21:42 queue:**
  1. M3-AUD-846: Ilun's voice and his layers on the summon (`vowbound.layers`, ChoreoAudio `_layer`).
  2. M3-AUD-847: Iskarra's vigil murmur in the prologue bed, and the lamp crackle at Rhen's LanternLight
     (`CutsceneAudio.watch_lamps`).
  3. M3-AUD-848: the battle result's count-up and the Reefball outfitter (pending).
  4. M3-AUD-849: the ridge lynx, cord moth, glass skate and flat-engine, and four pitched variants. Every creature
     on claude/creatures now has a voice.
  5. M3-AUD-850: the slice mix pass. The World bus ducks −3 dB under a line, villagers' chat is held over a line,
     and mix.md has the layer table.
  6. M3-AUD-851: the Letting written down in motifs.py.
- Earlier today: M3-AUD-831..838 (part 3's handoff).

## In progress
Nothing un-pushed.

## Exact next step
1. **When the Lead announces LFS is live:** render `python3 tools/audio/render_all.py --act2` (one cue at a time if
   memory is short), import, add the PROVENANCE rows, swap music.json's 12 zone rows from the sketches to
   `act2/<cue>` and add the four bosses' rows (each task file has them). Commit the 40 files and their .import files
   in one commit.
2. **When claude/ui merges:** drop `pending` on ShrineTravelMenu and ReefballOutfitterMenu, and smoke-test them and
   BattleResultPanel's count-up on the real classes.
3. **When M3-AUD-834 lands** (`@music` through the MusicDeck): drop the two stem stand-ins, and act1-chapters adds the
   undertow_rising stem trigger.
4. **Blocked on other tracks:** Malcor Venn's and the Abiding guard's music, the Act II scene cues and the Act II
   Vowbound stings wait for their fights, beat sheets and data.

## Known issues
- test_iskarra (tools) fails on `test_the_vigils_stand_on_the_paving` (3 of 7). It came in with big12 and belongs
  to env-art or slice-polish; it isn't audio's.
- test_creature_portraits (Godot) fails for the four Act II bosses' missing portraits; it belongs to the UI or
  creatures track and needs a PC render.
- The human's listening verdict is pending.

## Files touched (main)
game/audio/{life,choreo,cutscene,ui,reefball}_audio.gd, audio_director.gd; game/data/audio/*.json;
assets_src/sfx/{vowbound,charge,screen,act2_creature,prologue_ambience,cutscene_foley}_sfx.py and the music
sources under assets_src/music/act2/; assets_src/music/motifs.py; tools/audio/{render_all,data_check,targets}.py;
tools/tests/{test_act2_finals,test_motifs,test_act2_creature_sfx}.py; tests/unit/test_{life,choreo,cutscene,screen}_audio.gd;
docs/kb/audio/{act2_finals,act3_plan,mix,mix_report,listening_notes}.md.
