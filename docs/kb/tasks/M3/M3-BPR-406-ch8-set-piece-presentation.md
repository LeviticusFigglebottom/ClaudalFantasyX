---
id: M3-BPR-406
title: "Ch8 set pieces on stage: entries, intercepts, counters, withdrawals, the Reach's phases (ADR 0100)"
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: [M3-CMB-01]
milestone: M3
request-from: combat
---
## Goal
ADR 0100 and docs/kb/design/set_piece_battles.md add scripted entries, ward cover, counters, withdrawals and
untargetable or damage-immune phases to the engine (m2-slice M3-CMB-01, in big10). §8 of that page leaves the
stage side open. Choreography and the camera must make each of these readable (Pillar 4), and sincere: Ch8 is the
evacuation, and nobody's death is a joke.

## Design (to build once big10 is on the integration branch)
- **Entries have no fighter.** A ward, tide or guest turn plays no actor run. BattleChoreo plans it as a `beat`
  style: the camera holds the default (or an arena `entry_shot` marker: the stair, the tide line), with a short
  help-line name (UI draws the timeline glyph). It must never crash on `stand_in(id) == null`.
- **Intercept (`ActionResult.intercepted_by`).**
  - The coverer steps from its mark to a point between the foe and the stair (`spacing` keeps it clear) before
    the contact, and takes the blow there: its reaction and the impact flash.
  - It steps back on the return.
  - The camera frames the foe and the coverer, never an empty target.
- **Counter (`counter_by` on a hit).** The answer is a second, short sequence chained right after the blow's
  recover: the hero's lunge (`counter` style: no run, a step and a strike) and the attacker's hit reaction. One
  hit-stop at most per chain.
- **Withdrawal (`withdrawn`).**
  - Not a KO collapse. The foe turns and recedes: a `withdraw` beat back along its facing over `sec`, fading,
    then hidden.
  - The objective's end withdraws everyone left in one staggered beat before the outro.
- **Untargetable or damage-immune phases.** A per-phase stand-in tint or alpha (data: enemies.json phase
  `presentation`, or choreo.json `phase_looks`), so the player sees why their aim is refused. Damage immunity
  shows a "no effect" reaction (a hard stop, no recoil) instead of the damage reaction.
- **The Reach.**
  - A boss intro row (BattleBossIntro; the fit from M3-BPR-404).
  - The `breach_gather` telegraph gets a slow push-in over its 4 turns (the camera director's per-turn
    `pressure` offset).
  - `breach` itself plays the toll-wave language of the Drownbell (BattleBossVfx), which pushes the stair entry.
- **Audio hooks:** reuse BattleImpact.landed; new `intercepted` and `withdrew` events for audio (request later).

## Progress (2026-10-27)
- [x] Every Ch8 encounter plays to its result panel at full pacing through the controller and the choreography
      (test_battle_set_piece_stage).
- [x] Withdrawals: the foe backs away and is hidden (it used to stay standing); reduced motion hides it in place.
- [x] Counters: the hero's riposte clip, then the attacker's clip-only reaction; a riposte KO falls once home.
- [x] Arena: greybox `wall_head_storm` (Ch8 grade), with `EntryMarker_ward` at the stair head. The final kit is
      requested from env-art (M3-BPR-407).
- [x] Intercept: no step-in needed. The stair head is behind the party line, so the guard on his mark already
      stands between the foe and the stair, and the foe's grip lands on him there. Revisit if the final kit puts the
      stair elsewhere.
- [x] The Breach push-in (camera.pressure) and the Reach's intro row.
- [x] Staging: arenas.json `wall_head_storm` travel_scale 0.85 (the narrow wall-walk: shorter runs, as on the
      derelict's deck). The timeline names the entries (the Fisher Stair, the Surge, the Kirru).
- [x] **The per-wave beats** (asked of act1-chapters on 10-27, never answered; decided 2026-10-29 under ADR 0042).
      Wave 3's Kirru cuts to the hoist arena's `CameraHints/along_the_walk` (the movers in front, the party behind
      them) the first time Pell sounds Storm-Call. His later calls, and Storm-Call itself (the withdrawal), stay on
      the home frame, where the player sees which spawn leaves. This uses choreo.json `camera.moments.entry`
      `skills` / `once` in BattleEntryCamera, tested by test_the_kirrus_first_call_cuts_along_the_walk. Five hints
      were rendered and viewed with `boss_camera_sheet --entry`. `the_storm_wall` showed only Toma's back against
      the storm, and `party_side` hid the foes. The Breach's gather turns stay on the home frame, with the push-in
      only.
- [x] The phase looks: BattlePhaseLooks fades an untargetable foe to `phase_looks.untargetable.alpha` (the
      Reach's Breach) and back. A blow on a damage-immune foe plays the `immune` reaction (a hard stop, a stiff
      sideways shudder, no recoil). Test test_battle_phase_looks.
- [x] Freeze-frames for an intercept, a counter and a withdrawal (set_piece_beat_shot.gd on the real wave; test
      test_battle_set_piece_shots). The renders are requested.

## Acceptance criteria
- [x] Every Ch8 encounter plays to its end at full pacing with no script error (a test drives each by policy).
- [x] Freeze-frame shots: battle_ch08_intercept, battle_ch08_counter, battle_ch08_withdraw, battle_boss_intro_reach
      (render requested; first baselines once viewed).
- [x] Reduced motion: no camera push-in (test_battle_set_piece_stage, test_battle_reduced_motion_audit);
      withdrawals hide in place (test_a_withdrawn_foe_leaves_the_stage_without_a_collapse); the immune shudder is still.

## Review log
