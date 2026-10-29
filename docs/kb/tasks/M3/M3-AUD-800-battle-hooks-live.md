---
id: M3-AUD-800
title: Switch the battle hooks live: ChoreoAudio on the real BattleChoreo, CreatureAudio on CreatureActor, the stings
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agent)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
big7 brought claude/battle-presentation's BattleChoreo and claude/creatures' CreatureActor onto the integration branch. choreo_sfx.json's hook is still pending, and M3-AUD-13/14/18 were only tested against stand-ins.

## Acceptance criteria
- [x] Pending flags off; validate_data checks the real names; tests drive a real battle with the real choreography and creature models and hear each layer once (no doubled contacts, a retry leaves one listener).

## Notes
- 2026-10-24 audio (worktree agent, claude/audio; not pushed). Listen-only throughout: no battle-presentation or
  creatures file touched, no class_name stubs, nothing under game/battle/. No request task was needed: every read is
  public on the real classes.
- **ChoreoAudio against the real BattleChoreo** (game/battle/scene/battle_choreo.gd): signals `beat(kind, actor_id)`
  and `contact(result)` match; `current()` holds style, approach_end, contact, recover_end, return_end and kos;
  `style_id_for(result)`, `animating()`, `after_sequence(cb)` and the `speed` property are there; `entering(cid)` is
  `{t, spec, fwd, clip}` and `leaving(cid)` `{cid, node, t, spec, fwd, clip}`, with t counting up from -delay_sec and
  `spec.sec` the length, so the `{t, spec}` reading holds. The engine comes from BattleController.engine (the
  choreography has only a private `_engine`). All 13 choreo.json styles have a choreo_sfx.json row and back.
  - `pending` removed from the hook; validate_data now checks the real signals (0 errors).
  - **Flood stagger:** no longer duplicated. ChoreoAudio.flood_for(enemy) reads the phase and stagger from the
    choreography's `data` (choreo.json `bosses.<enemy base id>.flood`), the table BattleBossChoreo braces from;
    choreo_sfx.json `flood` keeps only the sfx. data_check.choreo_errors accepts the timing from either table and
    fails when neither has it (a new ChoreoSfxTest case). A fallen member's brace is silent too (BattleChoreo.accent
    gives it no motion).
  - **Retry:** BattleChoreo.attached removes the old node and adds a new one; ChoreoAudio.attach_to now frees any
    listener whose choreography has left the tree (`drop_stale`) before building the new one, so there is one
    ChoreoAudio right away, not only after the director's next sweep.
- **CreatureAudio against the real CreatureActor** (game/creatures/creature_actor.gd): the actors are under
  FighterStandIn < BattleStage < BattleController, so the controller scope finds them; `creature_id` is an exported
  StringName base id; the clips are idle / hit / ko / attack / cast (+ phase clips), and `clips` (attack, cast ->
  move) matches creatures.json `clip_by_kind`. `models` counts each sandbox creature once; the move plays once per
  action, from the strike clip, never with the attack as well.
  - **Fixed: hurt and death were early.** They were timed on the engine's action_resolved, but with the choreography
    animating the blow, and BattleVfx's hit and KO sounds, land on BattleChoreo's contact beat, often half a second
    or more later (later still with a creature's contact_time). CreatureAudio now hears the choreography's contact
    signal (the node choreo_sfx.json's hook names, found under its scope) for hurts and deaths, `delays_ms` after
    it; with no choreography it keeps action_resolved. The attack voice stays at the action's start (a cry as it sets
    off), so `delays_ms.attack` stays 0.
- **Stings:** only `battle_bark` is emitted on this branch (BattleStinger._show_bark, `[encounter, line_key,
  speaker_key]`), as StingAudio expects. `battle_stinger` (`[encounter]`) and `boss_intro` (`[engine.encounter_id,
  title_key]`, from BattleBossIntro._begin) are on origin/claude/battle-presentation (bcc8e94c and M3-BPR-02, 5ee5eb04)
  and not merged here yet; their shapes match battle_stings.json (by_arg `drownbell` is the encounter id). Once they
  merge, nothing in audio changes; the boss-intro test can then drive BattleBossIntro instead of emitting its shape.
- **Tests:** `tests/integration/test_battle_audio_live.gd` (9): the real sandbox battle (BattleController,
  BattleChoreo, the CreatureActor foes) with a test director attaching what its hooks attach. Hooks find the real
  classes and models; one whoosh then one accent per melee blow and BattleAudio's hit once (no doubled contact); the
  whoosh crest and the accent on the contact beat at 1x and 2x; one KO collapse and one death; one hurt, 70 ms after
  the hit; a creature's attack once and its move once, from its clip; a retry leaves one ChoreoAudio and one
  BattleAudio, and the old one hears nothing; the boss card's sting (`sting_boss_bell`) ducks and lets go after
  duck_sec; the real BattleStinger's bark plays `sting_bark` once. Sounds are recorded through a test bank
  (`_HeardBank`: SfxBank's rules and history, no playback) and the battle gets no music cue, so no playback outlives
  the run; the game's Audio autoload is kept off EventBus during the run. test_choreo_audio.gd's Flood test now reads
  choreo.json's stagger.
- **Gates:** validate_data 0 errors; taskboard --check; test_audio_data.py 44 OK; gdlint and gdformat clean; Godot
  import (run again after adding the test, for its .uid), then `--filter=audio` 97/0 (twice), `--filter=creature` 21/0, `--filter=battle` 541/0. The audio,
  creature and battle_audio_live runs print "2 resources still in use at exit": `field_submenu.gd` and
  `battle_pause_menu.gd`, GDScripts the battle scene keeps (test_battle_choreo on its own prints the same). The
  battle run prints 12, all GDScripts (those two, battle core scripts, test_battle_boss / turn_events / vowbound).
  `--verbose` (audio, battle, battle_audio_live runs) shows no audio stream among them. Skipped: screenshots,
  Blender, coverage (nothing under game/battle/ or game/progression/ touched), the full suite.
- Docs: audio_runtime.md "Choreography layers", "Battle stings" and "Creature voices and movement" updated.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
