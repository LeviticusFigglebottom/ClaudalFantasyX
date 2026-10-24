---
id: M2-RND-04
title: Drownbell boss: the flood rig and phase-change VFX
role: rendering
status: done
reviewer: environment
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
depends_on: [M2-RND-03]
milestone: M2
request-from: "lead"
---
## Goal
The First Playable session builds the Drownbell two-phase boss (logic); it needs its spectacle.

## Acceptance criteria
- [x] The bell's toll shockwave, the rising flood using the global hymn_water_level (one publisher per M1-RND-15), and the phase 2 transformation
- [x] Coordinate with the First Playable session (session_01ELR13ohWMPrprcpcgLa7UR, branch claude/first-playable): read its boss data and docs before starting; expose hooks it can call
- [x] Performance within the battle budget; reduced-motion variant

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Design, cost and gotchas: docs/kb/tech/battle_vfx.md, "The Drownbell". Key frames: docs/kb/qa/gpu/rnd04/.
- **Merge order.** Built on gpu/m2-rnd-03-battle-vfx (the dependency); merge that first.
- **The moments.** `BattleBossVfx`, attached through BattleVfx (no new controller line), plays every hook point in
  battle_ctb.md "VFX hook points":
  - the toll telegraph (a glow that builds per turn, gathering motes);
  - the toll shockwave and a capped flash;
  - rim sparks and the break;
  - the Flood (the flood rig: -0.7 to +0.6 m over 8 s, the battle scene's one hymn_water_level publisher, with the
    key light and sea-glow following the color script);
  - polyp lights under the water, and mend streams;
  - Ilun's Floodnet (bound light), with the water falling back;
  - the bell's held, seaward release.
- **Coordination.** These are the First Playable's hooks from battle_ctb.md and its data (enemies.json,
  skills.json, ADR 0026), read before starting. Nothing was added to the battle core.
- **Budget.** At High 1440p the worst frame is 2.0 ms, and the flood water is most of it. Ultra is 3.4 ms.
  Reduced motion is covered and tested, at the same cost.
- **Tests.** `tests/unit/test_battle_boss_vfx.gd` (6); all 375 battle tests pass.
- **Screenshots.** No baseline drifts: no shot uses the Drownbell. There's one pending shot,
  `docs/kb/qa/gpu/2026-10-24-rnd-04-pending-shots.json` (`drownbell_flood`).
- **Finding.** No shipped scene drives the weather clock (`hymn_wind_time`); only test rigs do. The flood rig
  runs it in the boss battle. Zones need an owner: the Lead routes it.
- **Also fixed (RND-03).** A retry left the old BattleVfx (and its flash layer) behind; the new view now replaces
  it.

## Review log
- 2026-10-24 review-sweep-Q (environment): **approve.** `BattleBossVfx` listens only to generic engine signals: `charge_started`, `charge_broken`, `phase_changed`, `combatants_joined`, `field_cleared` and `action_resolved`. So Floodnet's light keys on `field_cleared`, not on the `call_ilun` stand-in, and it will survive M2-FP-17's real call unchanged. Nothing was added to the battle core. The flood rig is the one `hymn_water_level` publisher across a retry (tested). The toll flash is capped through BattleVfx, and the rim glow pulses at 0.6 Hz, far below any flash threshold. Reduced motion is covered. The worst frame is 2.0 ms at High. The `drownbell_flood` shot and its baseline are in. `--filter=boss_vfx`: 6/0. The weather-clock finding is filed as M2-ARC-02.
