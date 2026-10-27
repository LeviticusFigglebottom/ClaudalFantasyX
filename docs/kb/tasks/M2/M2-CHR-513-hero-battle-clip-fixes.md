---
id: M2-CHR-513
title: "Hero battle clip fixes from hero-integration (M2-HER-1105): livelier victory, lying-down ko, revive, Rhen's hooks in hand"
role: character
status: doing
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
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
- [ ] victory, ko and revive for Asha, Rhen and Toma, with tests (loop, hold-last, joins).
- [ ] Rhen's hooks in hand for attack and finisher, after M1-CHR-15.
- [ ] Rig ratchets don't rise (Toma's Body count is already at its limit of 200).
- [ ] Shots viewed; the hero-integration and battle-presentation tracks notified.

## Notes

## Review log
