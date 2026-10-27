---
id: M2-CHR-513
title: "Hero battle clip fixes from hero-integration (M2-HER-1105): livelier victory, lying-down ko, revive, Rhen's hooks in hand"
role: character
status: review
owner_session: "characters (new account, branch claude/characters)"
reviewer: combat
depends_on: [M2-CHR-07]
milestone: M2
request-from: hero-integration
priority: top
---
## Goal
The hero-integration track saw M2-CHR-07's clips on the real models (M2-HER-1105) and asked for four fixes:
1. `victory` barely moves: the head moves under 1 mm per frame. Make a readable loop in each hero's idiom.
2. `ko` is a kneel or slump, but the contract says a fall that lies down. Make a fall to lying, holding the last frame, unless battle-presentation rewords the contract.
3. A ~0.8 s `revive`, from the ko's last frame to idle's first frame (rise_to_stand is 2 s).
4. Rhen attacks and does his finisher empty-handed while his hooks stay on his belt. He needs a hook bone, or a hand-held hook instance, so attack and finisher strike with a hook. This needs Rhen's build, so it waits for M1-CHR-15, which is rebuilding Rhen.

## Acceptance criteria
- [x] victory, ko and revive for Asha, Rhen and Toma, with tests (loop, hold-last, joins).
- [x] Rhen's hooks in hand for attack and finisher, after M1-CHR-15.
- [x] Rig ratchets don't rise (Toma's Body count is already at its limit of 200).
- [ ] Shots viewed; the hero-integration and battle-presentation tracks notified.

## Notes
- **2026-10-27, done (characters, on top of M1-CHR-15; the saved wip patch finished).**
  - **victory:** a loop in each idiom, every term whole cycles per loop, feet planted: Asha raises the lantern-staff
    and sways, the chest and head answering; Rhen bounces four times a loop and punches the gauntlet up, grinning
    round; Toma, the spear planted, rolls his shoulders in turn and his head tilts with them. The chest and head turn
    5 deg or more over the loop (test_hero_battle_clips).
  - **ko:** a buckle, down onto both knees, then a pitch forward to lie face down (the last keys hold). The legs are
    re-solved in world space between keys, so a knee or foot on the floor slides along it. Asha's toes are half
    tucked (30 deg: deeper pushes them through the sandal straps); Rhen and Toma kneel and lie on bent toes, their
    ankles at rest (the trouser hems).
  - **revive** (new, 12 keys = 0.8 s, after every other clip so the existing sub-resources keep their ids): from
    ko's held last frame, up onto the knees, a crouch, then idle's first frame. BattleClips plays it when present.
  - **Rhen's run arm:** a sprinter's forward swing (the upper arm comes 0.7 as far forward, the elbow folds 45 deg
    more, opening 10 deg), so the hand rises to the chest instead of reaching.
  - **Rhen's hooks in hand:** each reef-hook is now its own part on `DEF-hook.L/.R` (children of the hips, sheathed
    at the back as before), and a non-deforming marker `hook_grip.L/.R` on each hand holds the hook's frame as held:
    the grip across the fist, the blade forward out of the thumb side with its curl down. hero_clips keys both hooks'
    position and rotation in every Rhen clip (a sheathed hook is two keys): attack draws the right hook as the hand
    drops to its grip (u 0.10-0.25) and sheathes it as the arm comes back (0.80-1.0); finisher draws both (0.10-0.25,
    0.85-1.0). On the way the hook swings 0.12 m out from the hips' axis, which keeps it out of the forearm on every
    frame (every-frame probe: props 0 mm). Test: TestRhenHooks.
  - **Ratchets:** none raised. Toma's victory left arm opens 3 deg more (his tunic side, 32.5 -> under 32).
  - **Verify:** rhen rebuilt (hook bones); the villager jobs import hero_clips, which now reads
    game/data/characters/helper_bones.json, so `copy_into_sandbox` gains `game/data/characters` and the villager jobs
    list the file as a source.
  - **Shots:** new asha/rhen/toma `_battle_ko` and `_battle_victory`, plus `rhen_battle_finisher`; requested from the
    PC with rhen_battle_attack (the hook in hand). The ko camera is the attack's; it may need lowering once seen.
  - **For battle-presentation and hero-integration:** `revive` exists for Asha, Rhen and Toma; `ko` now lies down and
    holds; Rhen's attack and finisher carry his hooks in the clip itself (nothing to attach at runtime).

## Review log
