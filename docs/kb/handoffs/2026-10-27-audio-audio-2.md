# Handoff: audio, 2026-10-27 (session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)

## Done (all pushed; full gate clean at 248dfa76: Godot 2676/0, tools 1145 OK)
- Merged the integration branch twice (the second time big9, with hero-integration).
- M3-AUD-805, Act II sketches II: finished.
- The playtest's "parts look primitive" (FAST-TRACK):
  - M3-AUD-812: footsteps hear every slice surface (dock wood, shallows, stone), listen-only. Verified on the real
    HeroFieldActor, plus a stall fix for clips with no footfall markers.
  - M3-AUD-814 and 826: villager life and wildlife (LifeAudio); FieldNpc and WildlifeLayer are `pending` until
    claude/creatures merges.
  - M3-AUD-816: battle impact tiers on BattleImpact, `pending` until claude/battle-presentation merges.
  - M3-AUD-817: the cutscene pass (the cast's footsteps, cue foley, the prologue's room tone).
  - M3-AUD-818: Act I's 68 cutscene `@sfx` files.
- Wiring: M3-AUD-813 (menu hooks), 823 (eight music aliases), 824 (Reefball on the real ReefballMatch, with a
  ring bell), 825 (the Ashcrown trial), 827 (the pending zone beds and voices are live), 828 (Act I zone and boss
  music rows).
- M3-AUD-819 to 822: four composer agents wrote the 24 remaining Act I cues. Every Act I `@music` id now resolves.
- ADR 0171: budget 72 MiB (68.8 used). Shared motifs live in assets_src/music/motifs.py (CURRENT_SONG, ORDER_HUM,
  KERRID_STAIR).

## In progress
Nothing un-pushed. The composer worktrees (.claude/worktrees/agent-*) are merged and can be removed.

## Exact next step
1. When claude/creatures and claude/battle-presentation merge into the integration branch, merge it here, then drop
   the `pending` flags in game/data/audio/life.json and impact_audio.json, and run validate_data and
   `--filter=audio`.
2. Watch M3-AUD-829 and 830 (act1-chapters' script timings) and M3-AUD-815 (creatures' public reads).
3. Act II finals wait on the Lead's storage decision (ADR 0171). Until then: listening-note follow-ups, and Act III
   planning.

## Known issues
- The human's listening verdict is pending (docs/kb/audio/listening_notes.md). Nothing new has been heard; the
  synth voices (hums, the current-song, Pell) are the biggest risk.
- `undertow_rising`'s second stem has no trigger (M3-AUD-829).

## Files touched (main)
game/audio/{footstep,life,impact,cutscene,ashcrown,reefball}_audio.gd, audio_director.gd, audio_data.gd;
game/data/audio/*.json; assets_src/sfx/{life,impact,cutscene_foley,prologue_ambience,act1_cutscene,ashcrown,reefball}_sfx.py;
assets_src/music/ (motifs.py and the 24 Act I cues); tools/audio/{data_check,render_all,targets}.py;
tools/tests/test_cutscene_sfx_files.py; tests/unit and tests/integration audio tests; docs/kb/tasks/M3/M3-AUD-812..830.
