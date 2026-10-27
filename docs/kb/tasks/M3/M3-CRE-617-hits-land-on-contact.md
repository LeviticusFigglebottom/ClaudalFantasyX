---
id: M3-CRE-617
title: "Battle polish: creature hits land on the contact frame (hit snap) and the bosses' hits carry weight"
role: character
status: review
owner_session: "creatures (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY, branch claude/creatures)"
reviewer: combat
depends_on: [M3-CRE-612]
milestone: M3
request-from: lead
---
## Goal
The Lead's queue item 4: the weight of the hit, idle and KO clips on all 27 Act I creatures, in sync with
battle-presentation's M3-BPR-401 hit-stop and recoil.

## Findings (measured from the 27 GLBs)
- Every `hit` peaks 0.13–0.20 s in (the squall wing 0.30 s, half way at 0.07 s); a 2–4 frame hit-stop on the contact
  frame therefore held the creature's pre-hit pose (the hit started at 0 with a 0.12 s cross-fade).
- Four bosses barely moved when hit (summed bone deviation): the Drownbell 0.03 rad, the Cinder Matron 0.08, the
  tower limpet 0.12, the Undertow's Reach 0.13 (a reef crab: 1.9).
- Battle-presentation's side (logged for them, not changed here): BattleImpact holds every involved AnimationPlayer
  at contact, but the reaction beat that follows calls BattleClips.play, which sets the target's `speed_scale` back
  to the choreography speed, so the struck creature's clip is not held at all while the attacker and the procedural
  recoil are.

## Acceptance criteria
- [x] CreatureActor: a hit (and its variants) cuts in at `hit_snap.preroll_sec` (0.1 s) with no blend; strikes and
      other clips unchanged; the held frame is a struck pose (test_creature_actor)
- [x] The four bosses' hits rebuilt with a real recoil, peaking near 0.1 s (Blender verify identical); hit frames
      viewed before and after
- [x] validate_creatures knows `hit_snap`; docs/kb/art/creatures/pipeline.md
- [ ] battle-presentation keeps the target's clip held through the hit-stop (their BattleClips/BattleImpact)

## Review log
