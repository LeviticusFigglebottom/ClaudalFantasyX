# Handoff: audio, 2026-10-28, part 2: Act I at final quality (ADR 0041) (session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)

## Done (all pushed)
- **The refocus (ADR 0041; the Lead's 01:12):**
  - Act II/III audio stopped. The cloudloom/undertow_layers composer was stopped before it wrote anything.
  - 19 Act II/III tasks are `blocked` with `blocked-by: ADR 0041`.
  - Everything already in LFS stays: Act II finals 23.65 MiB, Act III 9.65 MiB, Kite foley 0.94 MiB.
- **M3-AUD-861, the Act I audio audit:** `tools/audio/act1_audio_audit.py` (test: tools/tests/test_act1_audio_audit.py).
  - It reads the runtime's own data (zones, enemies, battles, skills, cutscenes in the sequencer's order, UI hooks
    walking base classes, notes) and lists its by-design cases with their reasons.
  - **46 items at the start, 5 now, all of them other tracks' blockers.**
  - **Fixed:**
    - Zone music rows ×4, bed rows ×5, and three new beds (oruvel_raft, brightwater_deck, coilspire_flues).
    - The coilspire_flues stand-in, and the corrow_day alias.
    - The Inquisitor's voice. Own sets for wreck_crab, wallcrab, wall_polyp and stormgull. wickfry owns glassfry's set.
    - 16 silent boss and set-piece skills (`battle_sfx.skills`).
    - UI hooks for CodexMenu, SettingsMenu, ReadPanel and ObjectiveHud.
    - The Undertow's Reach's own music and phase stems, and the seawall waves' stems.
    - Footstep defaults: wood for Oruvel and the ferry; sand for Haluna's wake, the Shoals and Corrow's night strand.
  - **Also landed:** M3-AUD-862, the prologue's score (`prologue_dusk`); M3-AUD-863, Ysolde's theme final, in place
    of the sketch.
- **ADR 0173:** new Act I audio goes to Git LFS under `assets/lfs/audio/`, because plain git has about 0.45 MiB
  left. test_audio_loudness measures it by the same rules. No existing file was moved. Ysolde's final replaced its
  sketch at the same path, because the sequencer reads that path; it fits the budget.

## In progress
Nothing un-pushed.

## Exact next step
1. **When M3-AUD-834 lands** (the cutscene owner plays `@music` through the MusicDeck):
   - Drop the stand-ins for undertow_rising, seawall_hold and undertow_reach in game/data/cutscene/sequencer.json.
   - Rerun the audit; its Cutscenes section should go to 0.
2. **When claude/ui merges:**
   - Drop `pending` on ShrineTravelMenu and ReefballOutfitterMenu.
   - Smoke-test them on the real classes, as test_field_audio does for CodexMenu.
3. Rerun `python3 tools/audio/act1_audio_audit.py` after each integration merge. A new Act I scene, enemy, skill or
   UI class shows up there.

## Known issues
- **Memory:** run one render or composer at a time. Three at once restarted the container.
- `test_creature_portraits` still fails on the Act II bosses' portraits. That's the creatures track's, not audio's.
- A fresh clone needs `git lfs pull` to hear the Act I files under `assets/lfs/audio/`.

## Files touched
- **Sources:**
  - assets_src/sfx/{act1_final_creature_sfx, act1_skill_sfx, act1_final_ambience}.py
  - assets_src/music/{prologue_dusk, ysolde_theme}.py
- **Audio (LFS):** assets/lfs/audio/**. **Audio (plain git):** assets/audio/music/ysolde_theme.*
- **Data:**
  - game/data/audio/{music, ambience, footsteps, ui_sfx, battle_sfx, creature_voices, sfx_creatures, sfx_act1_skills}.json
  - game/data/cutscene/sequencer.json
- **Tools:** tools/audio/{act1_audio_audit, render_all}.py
- **Tests:**
  - tools/tests/{test_act1_audio_audit, test_audio_loudness}.py
  - tests/unit/{test_field_audio, test_battle_audio}.gd
- **Docs:**
  - docs/kb/decisions/0173-act1-final-audio-in-lfs.md and assets/PROVENANCE.md
  - task files M3-AUD-834, 861, 862 and 863, and the 19 blocked Act II/III tasks
  - docs/kb/handoffs/live/audio.md
