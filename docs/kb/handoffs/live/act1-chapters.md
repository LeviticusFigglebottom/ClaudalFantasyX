# Live log: act1-chapters environment

Branch `claude/act1-chapters`, cut by the Lead from `claude/m2-slice` @ 6c50823f (2026-10-25). Integration branch:
`claude/undertow-lead-handoff-ze8rrn`. Binding rules: CLAUDE.md and `docs/kb/handoffs/live/TRACK-RULES.md` (on the
integration branch).

## Scope
Act I from **Ch4 onward**: Ch4–Ch9 (greybox, built by m2-slice) and the chapters after them; the greybox-to-final swaps
with env-art's Act I kits; Ch7's real Reefball match; real casts; encounters per chapter; the cutscene quality bar;
greyboxing Ch10 onward to the end of Act I. **slice-polish** (`claude/m2-slice`) keeps the M2 slice, Ch1–Ch3, the
cutscene sequencer (`game/cutscene/**`), `game/flow/**` and the playtest fixes.

- **Id block:** tasks 1200–1299 (e.g. `M3-C04-1200`), ADRs 0200–0209, handoffs `<date>-cinematics-act1-chapters-<n>.md`.
- **Paths claimed** (docs/kb/ownership.md, last row): `game/levels/ch04/**`–`ch09/**` and later chapters,
  `game/data/dialogue/ch04/**` onward, `game/data/flow/chapters/ch04.json` onward, `game/data/flow/ch0[4-9]_*.json`,
  `game/data/loc/ch04.csv` onward, `docs/kb/story/beats/act1_ch04.md` onward, the Ch4+ thread tests.
  **For slice-polish:** Ch1 (`game/levels/ch01/**`, `game/data/dialogue/ch01/**`, `ch01.json`) stays yours with
  Ch2–Ch3. Ch5 and Ch7's zones subclass your `Ch01Zone`; I won't edit it (I'll ask via a task if I need a hook).
- **The Act I switches** in `first_playable.json` stay EMPTY until the human signs off M2 (the Lead flips them). F8
  chapter select reaches Ch4–Ch9 meanwhile.

## NEW ACCOUNT (from 2026-10-25)
- **MERGE-READY @ (see the commit after d7b55c10)**: the integration branch (big8, c6a960ab) merged in (d7b55c10).
  Conflicts: encounters.json (theirs' arenas + Ch8's rows), voices.json (theirs + Ivo; the 17 Act I speakers' `pending`
  flags cleared now they're in speakers.json), translations (union, +ch08), validate_data (both sides' checks),
  test_hero_clips (the all-dialogue check with M3-CHR-01's pending list), the two different combat-14 handoffs (both
  kept; m2-slice's renamed `-cmb01`), balance_report (theirs). Ownership claim for Ch4+.
  - **Checks run:** `--import`; Godot `--filter=ch0` 59 run, 0 failed; validate_data 0/0; dlgc --check 0/0;
    taskboard --check; gdlint, gdformat clean; `tools.tests.test_hero_clips` 9 OK.
  - **Checks skipped:** the full suite and sim (the merge touched no battle code on this side; the Lead gates the
    integration merge); coverage (no game/battle or progression change of mine); Blender (no source); shots (no
    scene of mine changed).

## Exact next step
Queue item 2, greybox → final, starting with the kits already on the integration branch: Ch6 `brine_shoals`
(M3-ENV-02), then Ch8 `corrow` (M3-ENV-04/04B), Ch5 `pemakar` (M3-ENV-03), Ch7 `tamsule_bell` (M3-ENV-01). The
ferry (Ch4), oruvel, ashcrown and coilspire kits are only on `claude/env-art` until the Lead merges it.
