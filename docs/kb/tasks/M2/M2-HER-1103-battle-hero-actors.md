---
id: M2-HER-1103
title: "Battle hero actors: the real heroes play the clip contract in battle (integration of UI-07, CHR-07, BPR-10)"
role: combat
status: doing
owner_session: "hero-integration (claude/hero-integration)"
reviewer: combat
depends_on: [M2-UI-07]
milestone: M2
request-from: lead
---
## Goal
In battle the heroes are still capsules on the integration branch. The pieces are on three branches: the stand-in hook
data (claude/ui, M2-UI-07), the 12 contract clips (claude/characters, M2-CHR-07) and the choreography plus placeholder
clips (claude/battle-presentation, M2-BPR-10). Make them meet, check every contract clip on the real model, and fix
what does not read naturally (clip crossfades, KO hold, idle micro-motion, ready and victory).

## Acceptance criteria
- [ ] A trial merge of the three branches shows Rhen, Asha and Toma in battle playing idle, ready, attack (contact on
      the marker), hit, KO, victory, cast and finisher; any gap is fixed in this track's files or requested from the
      owner track.
- [ ] Clip changes crossfade (no pops), and a one-shot returns to idle smoothly.
- [ ] Shots battle_hero_* (viewed), and tests for the hero actor path.

## Notes
- Also depends on M2-CHR-07 (claude/characters) and M2-BPR-10 (claude/battle-presentation), not on this branch yet.
battle-presentation owns the choreography; this track only adds the hero-actor side and reports.

### 2026-10-24: trial merge and hero actor (worktree subagent)
- **Trial merge** (local branch `hro03-trial`, never pushed): this branch + origin/claude/ui (427c65fc) +
  origin/claude/characters (34cea6d6) + origin/claude/battle-presentation (329ce604). Conflicts: field_encounters.gd
  (FP-28 per-location meters vs MNU-08 GROUP/refresh_rate: both kept, they are additive), shots/baselines/flags
  (merge_union), project.godot translations (union: + ch06), balance_report.md (both sections kept); a clean
  auto-merge duplicated `BOOT_FIRST_RUN_NOTE` in strings.csv (one dropped). Filters on the trial: battle 594/4 failed,
  choreo 40/4, fighter 4/0, clips 7/0. The 4 failures are test expectations of battle-presentation that assume a
  primitive Rhen (hop, procedural brace and glyph trace, "a primitive can't say" on Rhen) now that UI-07 gives him a
  model; a test-only patch (in the handoff to the Lead) makes them 40/0.
- **Viewed** (trial, `game/levels/_tests/hero_motion/battle_heroes_*.tscn`, shots `battle_heroes_*`): real models,
  facing the foes, feet on the ground, scale right against the crab and eel; attack contact and cast read; finisher
  reads as a heavier attack (no leap: the clip replaces the dive's shape); hit recoil is small; victory is nearly
  idle (head moves < 1 mm/frame: a characters gap); KO is a kneel/slump (head at 1.15 m), not a fall, and
  FighterStandIn.set_ko sinks it 0.25 m through the floor (lowest bone -0.246 m): patch proposed (no sink when the
  model has a KO clip). Rhen strikes empty-handed (his hooks stay on the belt).
- **Transitions** measured on the real Toma (60 Hz): BattleClips.play crossfades with the player's 0.3 s default and
  the queued idle too; no pop anywhere (largest head step 0.024 m/frame, inside the finisher itself). Gaps: the 0.3 s
  blend swallows the attack's anticipation (contact at 0.33 s), and a revive (ko -> idle) springs up in 0.3 s
  (0.036 m/frame).
- **HeroBattleActor** (`game/hero_motion/hero_battle_actor.gd`, `game/data/hero_motion/battle_hero.json`, wrappers
  `game/hero_motion/battle/<hero>_battle_actor.tscn`, 5 tests): sets per-pair AnimationPlayer blend times (strikes
  in fast, hit 0.06 s, ko -> idle 0.9 s: the revive now 0.012 m/frame), a per-hero idle phase, and HeroIdleMicro. It
  works through the existing BattleClips path (no play_clip, so BattleClips still queues idle). It takes effect when
  UI points battle_sandbox.json `stand_ins.<hero>.scene` at the wrappers (one-line-per-hero request in the handoff).
- Still open: the shots `battle_heroes_*` and their test stage live on the trial branch until the three branches are
  merged; then add them here and approve baselines. Requests: characters (victory, KO fall, weapon in hand), UI +
  Combat (the scene paths; FighterStandIn.set_ko's sink), battle-presentation (four tests, victory clip stagger).

### 2026-10-25: new account
- Merged the integration branch. battle-presentation's branch already carries the choreo test hunks and the KO no-sink
  (as does claude/ui), and it now plays an optional `revive` clip (characters' M2-CHR-513) on a revive. battle_hero.json
  gets ko -> revive 0.15 s (the clip starts on the ko's last frame), revive -> idle / ready 0.3 s.
- Pop guard on the real models: tests/unit/test_hero_battle_pops.gd (M2-HER-1110) samples every bone through all 26
  battle clip changes for each hero: no pops, no cuts.
- Left: the stand_ins repoint (request M2-HER-1108, ui-menus, after big9); the battle_heroes_* shots
  (hero_battle_shots.patch, after ui, characters and battle-presentation are on the integration branch); re-check KO,
  victory and revive when M2-CHR-513 lands (the pop test picks the new clips up by itself).

### 2026-10-27: Ysolde, placeholders
- `game/hero_motion/battle/ysolde_battle_actor.tscn`: the fourth wrapper. Her contract clips are all placeholders
  (request M2-HER-1115 to characters for the real ones). Ysolde also gets a field body (hero_motion.json; walk
  1.02 m/s and run 2.11 m/s measured by HeroClipGait), so her stage actors in cutscenes stop whip-turning.
- **Fixed:** placeholder clips were installed after HeroBattleActor set its blends, so they were untuned. Ysolde's
  ko -> idle was 0 s, not 0.9: a revive in one frame. The wrapper now installs them itself before tuning (on a
  stopped player: installing under a playing one crashes, see M2-HER-1114), and `retune()` (per frame) covers any
  clips added later.
- The pop guard on Ysolde: 25 of 26 changes inside the limit. ready -> finisher is the placeholder's arm flip
  (KNOWN, M2-HER-1114).

## Review log
