---
id: M3-BPR-406
title: "Ch8 set pieces on stage: entries, intercepts, counters, withdrawals, the Reach's phases (ADR 0100)"
role: combat
status: doing
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
- [ ] Intercept step-in (needs a stair position on the arena: env-art/act1-chapters' Ch8 arena, not built yet).
- [ ] The Reach's intro row, the breach_gather push-in, and the phase looks: these need PC renders to tune.

## Acceptance criteria
- [x] Every Ch8 encounter plays to its end at full pacing with no script error (a test drives each by policy).
- [ ] Freeze-frame shots: an intercept at contact, a counter at contact, a withdrawal mid-way, the Reach's intro.
- [ ] Reduced motion: no camera push-in; withdrawals fade in place.

## Review log
