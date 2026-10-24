---
id: M3-CMB-02
title: "Ch1 playtest: enemies act more often than they should, and than the timeline shows"
role: combat
status: review
reviewer: lead
owner_session: "combat worktree agent-ae69bc8623b2c0c6f (session_019iimsngAgPLEram1wcbLpE)"
depends_on: []
milestone: M3
request-from: lead
---
## Goal
From the human's playtest on the integration branch, in Act I Ch1's Underway and Oruvel, solo Rhen: "the enemies seemed to attack much more frequently than they should, both in general and according to the action reels; they seemed to act twice on some turns". Find the root cause, telling apart (a) tuning, (b) an engine bug, (c) a presentation bug and (d) encounter flow, then fix it and pin it with a test.

## Acceptance criteria
- [x] Reproduced headlessly on the live path (FieldBattle, BattleController and BattleChoreo, ticked frame by frame) for every Ch1 fight and the tideline, logging each action's actor, engine tick and the order before and after.
- [x] Root cause found and fixed. It was (a) tuning plus a timeline prediction error; not (b) or (c). (d) is fixed by M2-FP-28, which is already cherry-picked onto the integration branch (07781cba).
- [x] Regression tests: one engine action is one playback by its actor, in order; the timeline matches the engine's order and ticks; battle_speed changes no actor, order or tick.
- [x] `sim.py --check` passes, and balance_report.md has a tuning-log entry.

## Notes
- **Evidence:** the diagnostic run of `ch01_underway_shoals` at seed 7, before the fix. Rhen is at agility 22 with Attack at 174 ticks. The Wickfry is at agility 30, with the rank-2 Shoal Nip at 90 ticks.
  ```
  ACT now=119 rhen attack       order_before=rhen@119 wickfry#1@134 wickfry#2@183 wickfry#1@269 rhen@293 ...
  ACT now=134 wickfry#1 shoal_nip  (the reel said wickfry#1 next @269)
  ACT now=183 wickfry#2 shoal_nip
  ACT now=224 wickfry#1 shoal_nip  <- actually back at 224 (134 + 90), ahead of what the reel showed
  ACT now=273 wickfry#2 shoal_nip
  ACT now=293 rhen attack       (4 foe actions between two Rhen turns)
  counts { resolved: 13, plays: 13 }  (one choreography playback per engine action, at speed 1.0 and 2.0 alike)
  ```
- **(a) Tuning:** a shoal took 1.9 turns per Rhen action, and two shoals took about 3.9. The Wickfry's agility went 30 → 26 and Shoal Nip's rank 2 → 3, so a shoal now acts every 150 ticks, about 1.16 times per Attack, and Quick Hit (116) outpaces it.
- **The reel:** `CtbTimeline.predict()` assumed every foe uses `DEFAULT_RANK`, so a rank-2 foe jumped the queue it had shown, and a rank-4 pusher (the Tower Limpet) was drawn too early. ADR 0038 now predicts foes at their AI's rank (`EnemyAI.predicted_skill`), including that skill's delay push on a lone foe or on all foes.
- **(b) Engine:** clean. Delays were applied once, ticks never reset, and battle_speed is presentation-only (the same ticks at 0.75 and 2.0).
- **(c) Presentation:** clean. `choreo.played` equals the resolved actions one for one, and the HUD's slots equal the engine's preview.
- **(d) Encounter flow:** M2-FP-28's fixes (the per-location meter, the re-anchor, the 12 m grace) reached the integration branch at 07781cba, after this worktree's base, so nothing was redone here.

## Review log
