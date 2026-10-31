---
id: M3-C08-1400
title: "Coilspire: the binding holds the player for ~42 min (Virel's @mark walks 2.5 km off-stage), and no objective covers crown → binding (request from cloud QA, the Act I playthrough)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: qa
reviewer: qa
priority: high
---
## Goal
The cloud QA Act I playthrough (headless, `tools/gpu_bench/playthrough_probe.tscn`) on big33 (5695a69ce) and big34
(9317c6b6c) stops for good inside the Ch8 binding (`ch08_binding.dlg`, beat `binding` in `ch08.json`).

- **The hang.** `ch08_binding.dlg:26` is `@mark virel virel_gone`. Every `@mark` is a walk (docs/kb/tech/cutscenes.md),
  and `virel_gone` is the off-stage park at (2000, 0, 2000), about 2,500 m from Virel's coil. At `walk_mps` 1.0 that's a
  2,500 s walk. The scene's end plays every running walk out (`CutsceneSequencer._finish`, M2-HER-1113), so after
  Asha's "I think she was a kind person…" the letterbox lifts and the field still takes no input for about 42 minutes.
  The sequencer was seen awaiting `wait` with `wait_left` at 2483 s and counting down in real time (a headless debug
  script, 2026-10-31). Holding ui_cancel (the cutscene skip) gets out; tapping ui_accept does not.
- **The objective gap.** q_crown runs until `ch08_flame_at_crown` and q_beacon needs `ch08_virel_bound`. No row covers
  the step between them, the walk up into the crown chamber to the `crown` trigger, so the HUD reads "No errand calls
  just now" there.

## Acceptance criteria
- [ ] Virel leaves without a 2.5 km walk: hide Virel (the `ch08_virel_bound` state already hides it), or move it under
      the fade by a means that doesn't walk. Then the binding ends within seconds of Asha's last line.
- [ ] Optionally, a check in the dialogue validator or a unit test that no `@mark` walk runs longer than a set number
      of seconds (no other `.dlg` has a mark over 200 m away; only this one was found).
- [ ] An objective row from `ch08_flame_at_crown` to `ch08_virel_bound` pointing at the `crown` POI.
- [ ] Cloud QA's playthrough from F8 Ch6 reaches the end card with no PLAY_SKIP_SCENE in the binding.

## Notes
Owner: act1-chapters (Ch8 dialogue and flow). The sequencer behaviour is slice-polish's (`game/cutscene/**`). An
alternative fix there is to snap rather than walk any move longer than N seconds once the scene ends.
See `docs/kb/handoffs/live/cloud-qa.md` on `qa/cloud-pass6`.

## Review log
