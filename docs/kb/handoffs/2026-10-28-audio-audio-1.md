# Handoff: audio, 2026-10-27 night to 2026-10-28 (session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)

## Done (all pushed)
- **Self-directed backlog** (TRACK-RULES § SELF-DIRECTED BACKLOG):
  - **M3-AUD-857: Kahre and Virel**, the second and third Vowbound (vowbound_sfx.py).
    - Each has a battle voice and layers on the call, rise and sink.
    - Kahre: a hornbill's boom, sparks, thunder off the anvil, and the hammer on the anvil (A4).
    - Virel: sailcloth, the seams' fire, and the brass key. She is in `no_steps`.
    - test_vowbound_sfx.py checks every vowbound.json id.
  - **Act III cue sources, by composers in worktrees:**
    - M3-AUD-852: hollowmere and dace_ledger.
    - M3-AUD-853: the_kite and kite_maiden_flight.
    - M3-AUD-856: iskarra_ruins and iskarra_spire.
    - M3-AUD-858: hesper_and_ilsabet, two stems that never meet, and kerrid_last_night.
  - **M3-AUD-859: the Kite's foley.**
    - Files: the deck beds `kite_deck` and `kite_deck_dark`, H09's engine stop and lantern-out, sail fills, E4's rope strain and landing, the tiller, the ledger chest.
    - Source: `assets_src/sfx/act3/kite_foley.py`, rendered through render_all's `ACT3_SFX`.
- **Git LFS live (ADR 0039, Lead 00:20; sfx/act3 routed 01:00).** Everything held for LFS has landed: 43 objects, 34.24 MiB.
  - Act II finals in `assets/audio/music/act2/`, 23.65 MiB: the 12 zones and the 4 bosses' stems.
    - The music.json zone rows now play `act2/`, and the sketches stay as fallbacks.
    - There are new boss stem rows.
  - The Kite foley in `assets/audio/sfx/act3/`, 0.94 MiB, with `sfx_act3.json`.
  - Act III cues in `assets/audio/music/act3/`, 9.65 MiB, with their music.json rows.
  - Every file is deterministic. Act III files are byte-identical to the composers' renders.
  - `.import` loop flags are synced from the sidecars with `render_all._sync_import`.
  - Every file has a PROVENANCE row.
  - test_audio_loudness keeps the LFS paths out of the 72 MiB plain-git budget, which stands at 71.52 MiB.

## In progress
- **M3-AUD-860:** a composer in a worktree is writing `cloudloom` (Act II, Ch12, env-art's cloudloom_hall) and
  `undertow_layers` (Act III, Ch20). It commits sources only and leaves its renders in
  `$SCRATCH/M3-AUD-860/renders/`.

## Exact next step
1. When M3-AUD-860 reports:
   - Merge its branch, unioning the ACT2_FINALS and ACT3_FINALS rows.
   - Render each cue once, alone: `HYMN_AUDIO_JOBS=2 python3 tools/audio/render_all.py --act2 --only act2/cloudloom`, then the `--act3` render for undertow_layers.
   - `cmp` each file against the composer's render.
   - Run `godot --headless --path . --import`, then `render_all._sync_import` for the loops, then import again.
   - Add music.json rows (from the task file) and PROVENANCE rows, in a separate commit. Check that `git lfs ls-files` lists the new oggs.
   - Push, and post MERGE-READY.
2. Backlog after that:
   - The Act III plan's remaining cues whose scenes or zones exist.
   - Act III creature voices as the creatures track designs them.
   - The Kite zone row (`ch18/kite` → ambience `kite_deck`) once that scene exists.

## Known issues
- **Memory:** two renders at once is the safe limit; three restarted the container at about 23:40. The Lead now wants one render or composer at a time.
- **Boss and zone rows wait on their scenes or fights.** The intended encounter and phase rows are in each music.json `_note`:
  - Act II bosses, and the revenant pair: `hesper_fallen` and `ilsabet_fallen` → stems_off.
  - Zone rows for ch10–ch19.
- **Still blocked:**
  - Malcor Venn's and the Abiding guard's music.
  - The Act II scene cues and Vowbound stings, until Story's beat sheets exist.
  - The ShrineTravelMenu and ReefballOutfitterMenu hooks stay `pending` until claude/ui merges.

## Files touched
- **Sources:**
  - assets_src/sfx/vowbound_sfx.py and assets_src/sfx/act3/kite_foley.py
  - assets_src/music/act3/*.py, by the composers
- **Audio (LFS):** assets/audio/music/act2/**, assets/audio/music/act3/** and assets/audio/sfx/act3/**
- **Data:** game/data/audio/{music, creature_voices, sfx_creatures, sfx_choreo, choreo_sfx, sfx_act3}.json
- **Tools:** tools/audio/{render_all, targets}.py
- **Tests:**
  - tools/tests/test_act2_finals.py, test_audio_loudness.py and test_vowbound_sfx.py
  - tests/unit/test_choreo_audio.gd
- **Docs:**
  - assets/PROVENANCE.md and docs/kb/audio/act2_finals.md
  - task files M3-AUD-852, 853, 856, 857, 858 and 859
  - docs/kb/handoffs/live/audio.md
