# Handoff 2026-10-25: hero-integration (character / cinematics), session 1

**Session:** session_013oczHh2qUMy5kVz7nXsZef · **Branch:** claude/hero-integration · **Stopped for:** the account
handover (the Lead's order, 2026-10-25).

## What was done
- Built the hero motion layer (ADR 0190) in `game/hero_motion/`, with data in `game/data/hero_motion/`:
  - HeroLocomotion: pure maths, a rate-capped eased yaw and a gait blend by speed.
  - HeroFieldActor: the real model on the field player and on the cutscene stage actors.
  - HeroFieldParty: the followers.
  - HeroGaitClips: starts, stops, turns in place and an idle variant.
  - HeroMotion and HeroIdleMicro: the cutscene API and the micro-motion.
  - HeroFootContacts: footfalls for audio.
  - HeroBattleActor: battle cross-fades.
  - HeroClipGait: measures a clip's ground speed.
- Re-tuned the field speeds to the clips (ADR 0191).
- Wrote a sequencer patch for m2-slice, and proposed patches for UI and battle-presentation.
- Characters took the clip requests (M2-HER-1105 → M2-CHR-12 landed; M2-CHR-513 pending).
- Tasks: M2-HER-1101, 1102, 1104 and 1107 are in review; 1103, 1105 and 1106 are doing.

## In progress
Nothing is half-built. Everything waiting is listed in the live log's "STATE AT HANDOVER".

## Exact next step
See `docs/kb/handoffs/live/hero-integration.md`, "STATE AT HANDOVER (2026-10-25)", "EXACT next steps". First:
the Lead gates and merges claude/hero-integration, then re-approves the three field_hero_* shots after
claude/characters merges.

## Known issues
- Rhen's forward arm reaches out at shoulder height in the run (characters).
- After a teleport next to a wall, a follower can briefly stand inside it.
- `test_shrine_audio` fails in a filtered run only (pre-existing).
- The battle_heroes_* shots wait on three other branches (`docs/kb/tech/hero_battle_shots.patch`).

## Files touched
- **Code:** `game/hero_motion/**`, `game/data/hero_motion/**`, `game/levels/_tests/hero_motion/**` and
  `tests/unit/test_hero_*.gd`.
- **Other tracks' files:** one line in `game/world/field_controller.gd`, the speed rows of
  `game/data/world/field_movement.json`, and the shot rows and baselines in `tests/screenshots/`.
- **Docs:**
  - ADRs 0190 and 0191;
  - tasks M2-HER-1101..1107;
  - `docs/kb/tech/hero_motion.md`, `hero_motion_sequencer.patch`, `hero_battle_proposed.patch` and
    `hero_battle_shots.patch`;
  - the ownership row;
  - the live log.
