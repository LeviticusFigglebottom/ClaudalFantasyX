---
id: M3-BPR-401
title: "Battle feel: hit-stop, shake by damage, impact flash, recoil by damage, KO slow-mo"
role: combat
status: review
owner_session: battle-presentation (session_014EcW9e5tEmjDi5S2HmCECd)
depends_on: [M2-BPR-01]
milestone: M3
request-from: lead
reviewer: lead
---
## Goal
The human's note: battles look primitive. Add weight on the contact beat, all data-driven, Reduced motion honoured.

## Acceptance criteria
- [x] Hit-stop 2–4 frames on heavy contact (clock and clips hold); the hand-off waits for it.
- [x] Camera shake scaled by damage (strength = damage / max HP); none under Reduced motion.
- [x] Impact flash at the struck target (capped light, no screen flash, fog-safe); dimmer under Reduced motion.
- [x] Recoil scaled by damage; models with their own hit clip get a smaller root push.
- [x] KO slow-mo on the last foe; the hand-off waits for it.
- [x] Damage-number pop and easing: already to the art spec (UI's DamageNumber), landing on contact.
- [x] A Screen shake setting (Full / Half / Off, accessibility.json `screen_shake`); Reduced motion drops every
      battle shake, BattleFloats' too (BattleStage.shake_setting).
- [x] Tests (test_battle_impact), validator (impact_errors), doc ("Impact").

## Notes
Element particles on contact are the PC track's BattleVfx (unchanged).

## Review log
