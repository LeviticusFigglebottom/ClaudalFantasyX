---
id: M3-BPR-417
title: "Ilun's model: the summon choreography is ready for a creature actor (no more capsule once it lands)"
role: combat
status: review
owner_session: claude/battle-presentation
reviewer: lead
depends_on: [M2-BPR-04, M2-BPR-08]
milestone: M3
request-from: lead
---
## Goal
The Lead (20:54): Ilun the Vowbound is still a teal capsule. Creatures is building the model, so prepare the
summon choreography for it.

## Done (2026-10-27)
- A creature model reached the stage only through enemies.json `model` (CreatureModels, the creatures track's).
  Ilun is a Vowbound, not an enemy, so a creatures.json row for it was ignored and the capsule stayed.
- `BattleStage.vowbound_model`: a creatures.json row keyed by a Vowbound's id (`ilun`, `kahre`, `virel`) with a
  `scene` replaces the capsule, with that row's `stand_in` keys. Foes and heroes are untouched.
- Test `test_battle_vowbound_model` borrows an existing creature scene for Ilun's row. It checks the stand-in is the
  creature actor, the C10 first call plays on it, it rises onto its mark, and it has a head for the call frame and
  the floats. Both tests fail without the change.

## For creatures (what Ilun's row needs; no code change on this side)
- `creatures.json` row **`ilun`**: `scene` (its battle scene with a CreatureActor root and `creature_id = ilun`), and
  `stand_in` (`yaw_deg` toward the foes, `hover` if it floats).
- Clips (by kind, the `defaults` map): `attack` for Attack and Brine Lash (its finisher), `cast` for Tidal Ward
  (support). Add a `contact` time for each strike clip so the reaction lands on the blow. Also `idle`, `hit`, `ko`.
- The rise is the stage's own motion (choreo.json `vowbound.entry`, `summon_cinematic.entry`), so no rise clip is
  needed. An optional `ready` clip plays as it lands.
- `choreo_sfx.json` already lists `ilun` in `no_steps` (it doesn't walk).

## After the model lands
- [ ] Re-render battle_vowbound_call, battle_vowbound_out, battle_choreo_vowbound_rise and battle_choreo_summon.
  View them and re-approve.

## Review log
