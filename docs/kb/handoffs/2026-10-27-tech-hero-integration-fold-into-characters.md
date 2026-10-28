# Handoff — hero-integration → characters: the hero motion layer — 2026-10-27

The hero-integration track was set up to bring the real heroes to life in the field, cutscenes and battle, then to fold
its work into the characters track. This is the map for whoever owns it next. Everything is on
`claude/hero-integration` (merged up to big11). ADRs: 0190 (the motion layer), 0191 (field speeds follow the clips),
0192 (no snapping is a test), 0193 (steep stairs).

## 1. What lives where (all owned by this layer: `game/hero_motion/**`, `game/data/hero_motion/**`)
| File | What it does | Tuning |
|---|---|---|
| `hero_field_actor.gd` (HeroFieldActor) | A hero's visible body in the field and on cutscene stages: the model on a FieldController or stage actor, an AnimationTree gait blend (idle / walk / run, starts, stops and turns in place from characters' locomotion clips), eased turns (400°/s cap), `play_clip` for cutscenes, carried props (Rhen's lantern light), foot contacts (`foot_contact(foot, run)` for audio) | `hero_motion.json` field.heroes, locomotion.json (characters') |
| `hero_field_party.gd` (HeroFieldParty) | Followers on the leader's trail: spacing, catch-up, floor within a step of his height and eased, no walls (slide, clear catch-up side), face the speaker when he talks, steep stairs | `hero_motion.json` field.followers |
| `hero_locomotion.gd`, `hero_gait_clips.gd`, `hero_clip_gait.gd` | The speed and yaw maths, the start, stop and turn clip picker, and the clip speed measure (HeroClipGait) | `hero_motion.json` turn, gait, gait_measure |
| `hero_idle_micro.gd` (HeroIdleMicro) | Breathing, weight shift, the head leading turns: a SkeletonModifier3D on every body | `idle_micro.json` |
| `hero_foot_ik.gd` (HeroFootIK) | Feet on slopes and steps: two-bone IK, hips drop, a 1 cm continuous dead zone, eased, `enabled` switch | `foot_ik.json` |
| `hero_stairs.gd`, `hero_stair_flight.gd` | Steep flights walked on a marked profile (Ashcrown's 48° and 60°); `height_at` and `speed_cap_at` for anyone | `stairs.json` |
| `hero_motion.gd` (HeroMotion) | The static entry for cutscenes and other hosts: `play`, `set_locomotion_speed`, `add_micro_motion`, `add_foot_ik`, `skeleton_of`, `player_of` | n/a |
| `hero_battle_actor.gd` + `battle/<hero>_battle_actor.tscn` | A hero's battle actor: per-pair cross-fades, the idle phase, micro-motion; it installs and repairs placeholder clips for a model missing part of the contract; `model_path` for a model not yet on the branch (the stand-in capsule meanwhile) | `battle_hero.json` |
| `hero_motion_guard.gd` (HeroMotionGuard) | The no-snapping measures: transform snaps, clip-change pops, floor gaps | `motion_guard.json` |

The one hook outside: `game/world/field_controller.gd` `_ready` calls `HeroFieldActor.attach(self)` (slice-polish owns
that file). `attach` adds the body, the stage bodies, HeroStairs and HeroFieldParty.

## 2. Adding a hero (what characters does when a new party member's model lands)
1. **Field:** add a `hero_motion.json` field.heroes row: `scene` (the lod1 glb), `walk_clip_mps` and `run_clip_mps`.
   Measure the speeds with HeroClipGait.clip_speed (test_hero_field_actor checks them within 10%). If the model has
   locomotion.json clips (walk_start and the rest), its row there wins.
2. **Battle:** add a wrapper `game/hero_motion/battle/<id>_battle_actor.tscn`:
   - HeroBattleActor with `hero_id`, plus either the battle scene as a child (as Rhen's) or `model_path`;
   - an `idle_phase_sec` entry in `battle_hero.json`;
   - ui-menus' `battle_sandbox.json` stand_in row pointing at it;
   - the wrapper added to the WRAPPERS lists in test_hero_battle_actor and test_hero_battle_pops.
3. **Clips:** a missing contract clip gets a placeholder (battle-presentation's BattlePlaceholderClips); the wrapper
   repairs it and caps fades into fast ones. The real clips replace it with no code change.
4. Run `--filter=hero_`: the guards cover the new hero at once.

Status today:
- Rhen, Asha, Toma: everything.
- Ysolde: field and battle; her battle clips are placeholders (request M2-HER-1115).
- Liss: field and battle rows ready, and they come alive when claude/characters' `assets/characters/liss` merges;
  her battle_sandbox row is M3-HER-1120.
- **Kerrid:** nothing yet, because there's no model anywhere. Do steps 1–4 when M3-CHR builds him.
- Sefir is not a party member, and her clips (walk_glide) don't fit the gait: she stays a plain stage actor.

## 3. The guards (keep them green; they are the human's #1 complaint made into tests)
- `tests/unit/test_hero_battle_pops.gd`: every battle clip change on every hero, on every bone. KNOWN list: empty.
- `tests/unit/test_hero_field_snaps.gd`: every chapter zone (from locations.json), the party through run, reverse,
  strafe, stop and walk.
- `tests/integration/test_hero_cutscene_snaps.gd`: every in-engine cutscene (the prologue, HalunaStory, the chapter
  files' play steps; 79 now), with camera cuts allowed.
  - KNOWN: the 31 pairs that `docs/kb/tech/cutscene_walks_combined.patch` fixes. Empty the list when slice-polish
    applies it.
  - OFF-FLOOR lines are report-only. Make them fail once act1-chapters' via= paths land (M3-CIN-1220).
- `tests/unit/test_villager_snaps.gd`: Haluna's villagers (creatures' layer).
- Also: test_hero_stairs, test_hero_foot_ik, test_hero_followers, test_hero_field_actor, test_hero_battle_actor.
- Sources of truth for what they cover: `tests/hero_guard_sources.gd` (reads the game's data), plus the
  WRAPPERS lists.

## 4. Open requests (task files; their owners act)
| Task | Owner | What |
|---|---|---|
| M2-HER-1112 | slice-polish | Put the VillagerLayer in Haluna (the villagers are still frozen in the game until then) |
| M2-HER-1113 / M3-CIN-1221 | slice-polish | Apply `cutscene_walks_combined.patch` (via= paths + no-snap fixes) |
| M2-HER-1114 | battle-presentation | `stop()` before BattlePlaceholderClips' library swap (a crash for any other caller); a felled hero fades out (the KO shot) |
| M2-HER-1115 | characters | Ysolde's battle clips |
| M2-CHR-513 | characters | Livelier victory, a lying-down KO, revive, Rhen's hooks in hand |
| M3-HER-1117 | creatures | Villagers' foot IK (one line in FieldNpc) |
| M3-HER-1118 | creatures | Villagers on steep stairs (`height_at`, `speed_cap_at`) |
| M3-HER-1119 | slice-polish | Cutscene walks on steep stairs |
| M3-HER-1120 | ui-menus | Liss's battle_sandbox row |
| M2-HER-1111 | QA & Tools | run_tests.gd counts a parse error as "0 failed" |

## 5. Gotchas
- **Placeholders under a playing player crash Godot 4.6.3** (the library swap). HeroBattleActor stops the player
  and installs them itself before starting idle; anyone else calling BattleClips.player_of on a playing model needs
  M2-HER-1114's fix.
- **Physics in tests:** a StaticBody moved after entering the tree, or freed, changes the physics space only on a
  physics step. Place bodies before add_child; use a fresh site per test (test_hero_foot_ik). The runner makes a
  new TestCase instance per test method.
- **The test runner hides parse errors** ("N run, 0 failed" with a file's tests missing): when a new class_name is
  added, run `godot --import` first.
- Never edit another track's file without the owner or the Lead's word. The two exceptions so far:
  - the FieldController hook line;
  - Ysolde's battle_sandbox row (the Lead's FAST-TRACK).
- send_message from track sessions is refused. The live log is the channel.

## 6. Exact next steps for the new owner
1. When the combined cutscene patch lands, empty the cutscene guard's KNOWN list and re-run it.
2. When act1-chapters has its via= paths in: make OFF-FLOOR fail.
3. When characters' Liss merges, check her in battle and the field (render request). Add Kerrid when he's built.
4. When M2-CHR-513 lands: view KO, victory and revive (the battle_heroes_* shots).
5. Respond to the PC's foot IK perf numbers (live log PERF-REQUEST).
