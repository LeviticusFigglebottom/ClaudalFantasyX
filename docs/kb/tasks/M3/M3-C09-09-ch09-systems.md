---
id: M3-C09-09
title: "Ch9 systems: grade ids, the act_card event, the @vfx follow/anchors cue, the held-input event"
role: architect
status: review
owner_session: "integration-qa (claude/hero-integration; architect seat)"
depends_on: [M3-C09-02]
milestone: M3
request-from: cinematics
---
## Goal
act1_ch09.md §9 (Systems):
1. **New speakers:** done in M3-C09-02. Ch8 has no speaker rows yet, so Ch9 added `marra`, `hobb`, `fenn` and `stillguard` (speakers.json; names in `game/data/loc/ch09.csv`). Ch8 reuses them.
2. **New grade ids:** `ch09`, `ch09_dawn`, and `prologue` for the vigil (the Prologue's own `.dlg` notes that no grade cue exists for it yet). Add them to `cues.json` `sets.grades` once the color-script frames exist (M3-C09-10). Then Cinematics adds `grade=` to the Ch9 shots.
3. **New events:**
   - `act_card` (an int act number);
   - the Ebbing's held input, as an event or a new cue, shared with act3_ending E4.
     - **Done as events in M3-C09-02:** `hold_input <prompt>` and `hold_input_end` in `events.json`, read by `CutsceneHoldGate` (`game/cutscene/cutscene_hold_gate.gd`; cutscenes.md "Held input").
     - Review them. If a cue suits the format better, supersede them; Ch9's scripts move with it.
4. **The `@vfx` extension** (Rendering item 9, M3-C09-03): a `follow=<actor|prop>` kwarg for an attractor host and a way to name anchor actors, or a sequencer event that Cinematics drives.

## Acceptance criteria
- [x] The grade ids, the `act_card` event, and the `@vfx` follow/anchor vocabulary in `cues.json` and `events.json`, with `dlgc` tests.
- [x] A ruling on `hold_input` and `hold_input_end` (keep them, or replace them with a cue).

## Notes

- **integration-qa (architect seat), 2026-10-29:**
  - `cues.json` `sets.grades` gains `ch09`, `ch09_dawn` and `prologue`. M3-C09-10's colour-script frames exist
    (env-art-b; the dawn variant loads `corrow_ch09_dawn_environment.tres`). Grade ids are header and `@camera grade=`
    vocabulary for dlgc; each zone's environment carries the actual look. Cinematics can add `grade=` to Ch9's shots now.
  - `events.json` gains `act_card <int act>`, the event ActCard already listens for (`ActCard.EVENT`, M3-C09-05).
    `ch09_the_road_out.dlg` still reaches its card through `<<jump ch09_act_card>>` and a narration line. Moving
    it to `<<event act_card 2>>` is Cinematics' edit (act1-chapters), not mine.
  - The `@vfx` follow/anchors vocabulary went in with M3-ARC-1326 (5f59e2878; CutsceneVfxHosts).
  - **Ruling: keep `hold_input` / `hold_input_end` as events.** The held input is a span with a prompt argument
    and a host-side gate (CutsceneHoldGate), not a one-shot staging verb. Events already carry it, dlgc checks the
    arguments, and Ch9's scripts use them. A cue would add a second spelling and buy nothing. act3_ending E4 reuses
    the same pair.
  - Tests: tools.tests.test_dlgc 129/0 (new `test_ch09_grades_and_the_act_card_event`); dlgc --check 0/0.
  - Reviewer: cinematics.

## Review log
