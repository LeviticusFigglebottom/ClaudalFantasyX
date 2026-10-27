# 2026-10-25 audio handoff (session on claude/audio, ended at the account handover)

The full state, the next steps and the gotchas are in `docs/kb/handoffs/live/audio.md`, "STATE AT HANDOVER
(2026-10-25)". That is the entry point; this file is the session summary.

## Done
- **The Lead's queues, all merged on claude/audio:**
  - Act I music: Ch1, Ch4–Ch9, the temples, the bosses and the Stillguard (M3-AUD-08..12, -19, -20).
  - The M3 SFX sets: battle choreography (M3-AUD-13), creature voices (-14), menu UI (-15, M2-AUD-14, M2-AUD-17),
    the Act I zone beds (-16), Reefball (-17, -22) and the battle stings (-18).
  - Syllable blips (-21), the mix pass and report (-23), and the voices for the new speakers (-24).
- **The pending hooks switched live on the real classes after big7:** M2-AUD-17, M3-AUD-800, M3-AUD-801. Two real
  battle bugs were fixed: creature hurt and death now play on the contact beat, and a retry leaves one listener.
- **Hero footsteps and foley on the foot contacts** (M3-AUD-802): four surfaces, walk and run, stop and turn scuffs,
  cloth and gear. It reads hero-integration's `foot_contact(foot, run)` (M3-AUD-810, confirmed).
- **KO-once verified** against M2-BPR-11 (M3-AUD-803).
- **The Act II sketches I:** six cues (M3-AUD-804).
- **ADR 0170:** the audio budget is 56 MiB.
- **The last full gate:** MERGE-READY @ 2a699ddb (2006/0). The items merged later had scoped checks.

## In progress
- **M3-AUD-805, the Act II sketches II.** The sources are committed as WIP; the wiring patch and the steps are in
  `docs/kb/audio/wip/`.

## Exact next step
Finish M3-AUD-805 with `docs/kb/audio/wip/README.md`. Then merge the integration branch and run the full Godot suite
and the loudness test, and post MERGE-READY in the live log.

## Known issues
- The human hasn't heard anything yet (listening_notes.md).
- The menus' tests leak GDScript resources at exit (M2-AUD-16; not audio's).
- `test_scene_router_swap` is sensitive to CPU load.
- The audio storage plan for the full game is still open (Git LFS, ADR 0005 and ADR 0170).

## Files touched (main ones)
- game/audio/* (the runtime and the listeners).
- game/data/audio/*.json.
- assets_src/music/*.py and assets_src/sfx/*.py, with assets/audio/** (their outputs) and assets/PROVENANCE.md.
- tools/audio/* (render_all, data_check, targets, mix_report).
- tools/tests/test_audio_*.py.
- tests/unit/test_*audio*.gd and tests/integration/test_battle_audio_live.gd.
- docs/kb/audio/*, docs/kb/tech/audio_runtime.md, docs/kb/decisions/0170-audio-budget-56-mib.md.
- docs/kb/tasks/M2/M2-AUD-*, docs/kb/tasks/M3/M3-AUD-*.
