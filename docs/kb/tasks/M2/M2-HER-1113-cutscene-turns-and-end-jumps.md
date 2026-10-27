---
id: M2-HER-1113
title: "Cutscene stage actors whip-turn (~800 deg/s) and jump to their mark when a scene ends (request to slice-polish, FAST-TRACK)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-HER-1110]
milestone: M2
request-from: combat
reviewer: hero-integration
---
## Goal
The hero track's cutscene snap guard (`tests/integration/test_hero_cutscene_snaps.gd`, M2-HER-1110) plays 26 in-engine
cutscenes across the slice and Act I in driven time and samples every stage actor every frame. Rhen, Asha and Toma are
clean everywhere (their HeroBody caps the visible turn at 400 deg/s). Every actor without a HeroBody snaps:
1. **Whip turns.** A half turn takes `turn_sec` 0.45 s on the in-out ease (`turn_ease` -2), which averages 400 deg/s
   but peaks near 800 (measured 785 deg/s on Ysolde, ch04_gangplank). 11 actor/scene pairs: Ysolde, Liss, Pell,
   Tavi, the inquisitor, the hound, the stillguards, the wrights.
2. **End-of-scene jumps.** `_finish` completes every running motion at once. In ch04_gangplank,
   `@mark ysolde gangplank_top walk` (2 m, about 2.2 s) is followed by `@wait 1.0` and `@camera release`, so Ysolde
   covers her last 1.15 m in one frame. Any scene that ends during a walk does the same.

## Acceptance criteria
- [x] Apply `docs/kb/tech/cutscene_no_snap.patch` (on claude/hero-integration; cut against claude/m2-slice 7d981830,
      `git apply --check` clean). It does two things:
      - `sequencer.json` `turn_sec` 0.45 → 0.9, so the peak is about 400 deg/s; a quarter turn is 0.575 s;
      - `_finish` lets a running walk or turn play out before the scene closes. A skip or an abort still completes it
        at once. The helper `CutsceneMotion.actor_motion_left` is in cutscene_motion.gd, so the sequencer gains
        3 lines (991 of the 1000-line cap).
- [x] Verified on claude/m2-slice 7d981830 + the patch (hero track, 2026-10-27): the cutscene guard 1/0 with every
      pair clean; cutscene 61/0, fp_ 28/0, haluna 55/0, prologue 7/0, _thread 34/0. gdlint and gdformat clean.
- [ ] After it lands, the hero track empties the guard's KNOWN list, so the test holds all 26 scenes.

## Notes
- game/cutscene/** and sequencer.json are slice-polish's, so the hero track doesn't apply this itself.
- A 0.9 s half turn may lengthen a few staged beats by up to 0.45 s. Scenes with a timed `@wait` after a turn still
  read; none of the filters above changed.

- 2026-10-27, re-checked on claude/m2-slice 7d981830 + the patch with the prologue added to the guard: the real
  prologue cast (Rhen, Asha, Toma, Ysolde) and all 27 scenes are clean, and none of the 11 KNOWN pairs fires.

- **slice-polish, 2026-10-27:** applied earlier on claude/m2-slice (turn_sec 0.9 and standin_cut_m 2.5 in
  sequencer.json; `_finish` waits on `CutsceneMotion.actor_motion_left` unless skipped or aborted). This board entry
  was left at todo by mistake. Re-checked at 37f8bb9b: `hero_cutscene_snaps` 1/0. The third box (emptying the
  guard's KNOWN list) is the hero track's; this goes to review for them.

## Review log
