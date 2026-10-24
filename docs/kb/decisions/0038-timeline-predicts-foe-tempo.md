# 0038 — The timeline predicts a foe's turns at its AI's rank

- **Status:** accepted
- **Date:** 2026-10-24
- **Roles affected:** combat, ui (TurnTimeline shows the same order), design (enemy skill ranks now read on the timeline), qa
- **Author role:** combat (M3-CMB-02)

## Context
In the human's Ch1 playtest, the enemies "seemed to attack much more frequently than they should, both in general and according to the action reels; they seemed to act twice on some turns". SPEC §6.1 and pillar 4 say the player always knows who acts next. `CtbTimeline.predict()` assumed every future action is `DEFAULT_RANK` (formulas.md § Time, "Timeline preview"). That holds for the party, because the player hasn't chosen yet. It doesn't hold for a foe whose AI only has quicker or slower skills. The Wickfry's rank-2 Shoal Nip at agility 30 came back every 90 ticks while the timeline drew it every 135, so it jumped ahead of Rhen on the reel. The Tower Limpet's rank-4 clamp, which also pushes Rhen back, was drawn too early, and so was Rhen. The engine itself was right: one action per turn, one playback per action, and battle_speed leaves the ticks alone (`tests/integration/test_battle_timeline_honesty.gd`).

## Options
1. Keep the assumption and make every enemy skill rank 3. That's honest by data, but it throws away rank as a design knob for foes (Hullgnaw's quick Thrash, the limpet's slow clamp).
2. Predict each foe's turn at the rank its AI will use, read from its rules without drawing from the RNG. Party turns stay at `DEFAULT_RANK`.
3. Show a range on the reel (earliest and latest). That's harder to read, and it's a UI redesign.

## Decision
Option 2. `CtbTimeline.tempo` is a Callable that BattleEngine sets to `tempo_rank`, which calls `EnemyAI.predicted_skill` for a foe or an automatic (Berserk/Confused) turn:
- The first AI rule whose conditions hold decides, with `turn_mod` counted that many own turns on. Other conditions are read as they stand now.
- Of that rule's weighted options, the one with the lowest rank (the soonest the foe can act; the first on a tie).
- No rule holding means a standard action (the engine's idle turn).
- The predicted skill's delay push lands on every foe of the actor for an all-foes skill, and on the only foe left for a single-foe one. With more than one foe the target is the AI's draw, so none is pushed.
- The swap, Vowbound-call and dismissal previews copy the same `tempo`. A charged skill's `intent` turn keeps its own rule (battle_ctb.md § Timeline honesty).

No formula changes. `formulas.gd` is untouched, and formulas.md § Time gains a "Foe tempo" paragraph after "Timeline preview".

## Consequences
- The reel now matches play for every Ch1 fight and the tideline from the opening until the first KO or phase change. A test pins this, including the old prediction's failure on the limpet.
- A foe with rank-2 skills (the Gull Harrier's Dive Rake) now takes the slots it really takes, so 16 chips cover fewer of a slow foe's turns. `test_ui_timeline::test_skipped_turns_are_flagged` reads 32 entries.
- Still not predicted: HP-threshold rules crossing mid-preview, phase changes, gathers, and which of several foes a single-target push hits.
- Tuning a foe's tempo is now visible to the player, so Design should read rank × base delay against the party's (balance_report.md 2026-10-24 tempo entry).
