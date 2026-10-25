# Handoff — cinematics/architect — 2026-10-25 (m2-slice) #1, account handover

Session: m2-slice, session_01DQ9tdk8Uatb8Jr6raAkXiC. Branch `claude/m2-slice`, head 97620754, pushed. There are no worktrees and nothing un-pushed. Full state: `docs/kb/handoffs/live/m2-slice.md`, section "STATE AT HANDOVER (2026-10-25)". This file summarises the session.

## Done this session
- **The integration branch merged twice:** 29b1dbfa (1cc9fc66) and big7 d6a0886d (00bf4b01).
  - Merge decisions for big7: keyed loc union; voices for 17 Act I speakers; big7's PartyJoins and Drownbell targets; Haluna's resident prewarm entries back.
  - `tools/dev/merge_union.py` now does a keyed three-way union for loc CSVs (94402863).
- **The human's playtest, round 1 (M2-FP-28):**
  - random encounters: the meter persists per location, re-anchors on placement, and has a 12 m grace;
  - prologue → Haluna by default, with Act I a data switch;
  - the prologue's dusk frame carries colour.
- **Round 2:**
  - the prologue's figures, lantern and grade stand-in (583759c0);
  - eased cutscene motion (M2-FP-29, 716c2db4);
  - the hero hooks doc for hero-integration (d06ba098);
  - Haluna's Asha faces her root's forward (M2-FP-101, 74ed95b4).
- **M3-C04-04:** the `end_card.next_location` switch, empty by default.
- **M3-ARC-02:** the F8 debug chapter select.
- **M3-CMB-01:** Ch8's set-piece battle pieces (subagent; ADR 0100), merged at 74ef8626.
- **M3-C08-02:** Ch8 "The Seawall" (subagent), merged at 97620754. Its own handoff is `2026-10-24-cinematics-m2-slice-1.md`.
- **Creature battle models** for 15 Act I enemies, plus Ch8's four (544958b1, 74ef8626).
- **Requests filed:**
  - M3-CHR-01: Act I body clips; `test_hero_clips` allows the requested list;
  - M2-UI-100: voice-over subtitles;
  - M3-UI-100: the set-piece battle HUD.
- **M2-ENV-05:** the router swap regression traced to the resident flags (reverted, then restored with big7's rewritten test).

## In progress
Nothing.

## Exact next step
See the live log's "Exact next steps, in priority order":
1. regenerate `dialogue.csv` on merge;
2. hero-integration's sequencer patch, `walk_mps` 1.0 and the run-start speed;
3. wildlife and FieldNpc hooks;
4. the prologue lantern's `@light` cue;
5. Ch7's real Reefball match.

## Known issues
- `test_shrine_audio` is racy when run alone (the audio track's test).
- `test_scene_router_swap` is sensitive to the resident prewarm flags, and can fail once on a cold cache.
- Ch8's limits are in its own handoff.

## Gates
- **Last full run:** 2069 run, 0 failed; tools OK; sim in band; coverage battle 99.96% and progression 96.89% (on f3ef6f8c).
- **After that, scoped runs:** ch0* 59, zone_story 15, debug_overlay 14, fp_thread 2, haluna 47, cutscene 44, prologue 6, ch08 8, set_piece 28. All 0 failed.
- **Skipped:** Blender (no source touched) and the full shot manifest (no shot covers the changes).

## Files touched (main ones)
- **Encounters and zones:** `game/world/zone/field_encounters.gd`, `greybox_zone.gd`.
- **Cutscenes:** `game/cutscene/cutscene_motion.gd` (new), `cutscene_sequencer.gd`.
- **Flow:** `game/flow/end_card.gd`, `game/levels/prologue/prologue_scene.gd`, `prologue.tscn`.
- **Debug:** `game/core/debug/debug_overlay.gd`, `debug_readouts.gd`.
- **Haluna:** `game/levels/ch02/haluna/haluna.tscn`.
- **Data:** `game/data/flow/first_playable.json`, `game/data/debug/chapter_select.json`, `game/data/world/greybox_defaults.json`, `game/data/cutscene/sequencer.json`, `game/data/battle/enemies.json`, `game/data/audio/voices.json`, `assets_src/characters/requested_clips.json`.
- **Tools:** `tools/chapter_flow_check.py`, `tools/dev/merge_union.py`, `tools/tests/test_merge_union.py`, `tools/tests/test_hero_clips.py`.
- **Docs:** `docs/kb/tech/chapter_flow.md`, `cutscenes.md`, `field_hero_hooks.md` (new).
- **Merged from subagents:** the CMB-01 and Ch8 files, listed in their own handoffs.
