---
id: M2-HER-1114
title: "Placeholder clips: a crash when installed under a playing player, and a finisher arm flip (request to battle-presentation)"
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: [M2-BPR-10]
milestone: M2
request-from: combat
---
## Goal
The hero track's battle pop guard (tests/unit/test_hero_battle_pops.gd, M2-HER-1110) samples every bone through every
clip change the battle makes. On Ysolde, the first hero with no contract clips of her own, so BattlePlaceholderClips
builds them all, the change ready -> finisher moves her left hand **1.3 m in one frame** at 0.133 s. The placeholder
finisher's `DEF-upper_arm.L` rotation keys 0 and 1 (t = 0 and 0.15 s) are almost antipodal (dot -0.01), a ~180° swing.
Played alone it is just fast (0.23 m/frame), but in a cross-fade the near-antipodal path flips mid-blend.

**A crash, found first.** `BattlePlaceholderClips._install` swaps the player's library (`remove_animation_library` then
`add_animation_library`). When the player is **playing** at that moment, Godot 4.6.3 segfaults, either right away or
at teardown. Minimal repro: instance `game/hero_motion/battle/ysolde_battle_actor.tscn` (it starts idle in `_ready`),
add it to the tree, call `BattleClips.player_of(it)`, quit: signal 11. It doesn't crash with the player stopped first,
or on characters' bare `ysolde_battle.tscn` (not playing yet). No hero hit it before, because Rhen, Asha and Toma have
every contract clip, so nothing is ever installed on them. Any hero with missing clips whose player is already
playing when the battle first looks it up will.

## Acceptance criteria
- [x] (56921688) `_install`: `if playing: player.stop()` before the swap. The re-play and seek after it already exist. Verified
      locally: the repro is clean, and hero_ 91/0 twice. (The hero track's wrapper now stops the player and installs the
      placeholders itself before idle starts, so the wrappers are safe either way. The fix protects every other
      caller.)
- [x] (56921688; `placeholder_clips.max_key_deg` 60, test_battle_placeholder_clips fails without it) In `game/battle/scene/battle_placeholder_clips.gd`, no rotation track has consecutive keys more than ~90° apart.
      For example, insert slerped midpoint keys when `abs(q0.dot(q1)) < cos(45°)` (half-angle), and keep each key on
      the same hemisphere as the one before it (`q1.dot(q0) >= 0`).
- [ ] (hero-integration's step) The hero track's pop test then passes for `ysolde ready -> finisher`. The hero track removes that KNOWN entry
      once the fix reaches its branch.

**Seen in the PC render of battle_heroes_ko (2026-10-27):** a felled *hero* (Toma) dissolves away in a dust puff. M2-BPR-11's felled-foe
fade-and-hide seems to apply to party members too. A KO'd hero should stay down on the ground (its KO clip holds the
last frame) so it can be revived. Please limit the fade to foes, or confirm the party fade is intended.

## Notes
- Measured 2026-10-27 on claude/hero-integration after big9: the other 25 placeholder changes on Ysolde are inside the
  limit; idle -> victory is close (0.087 m/frame against 0.090 allowed).
- Placeholder clips only cover a hero until characters ships the real ones (Ysolde's: request M2-HER-1115).

- 2026-10-27 (requester): the arm flip is handled in the hero track's own files, so Ysolde's battle is clean today.
  HeroBattleActor gives the placeholders it receives short-path rotation keys, and caps fades into fast placeholders
  at 0.06 s. Her guard is clean and its KNOWN list is empty. The generator fix (and the `stop()` before the library
  swap) would still help any other caller. Nothing here blocks the hero track.

## Review log
