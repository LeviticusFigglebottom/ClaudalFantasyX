# Handoff — cinematics — 2026-10-24 #4

Session: m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`. Task: M2-FP-18, Cutscene A/B facial animation.

## Done
- Asha (and any actor with a face table) now blinks on a seeded timer and on every expression change.
- Her mouth follows each line's text through her viseme shapes (`FaceVisemes`), instead of one shape opening and closing.
- Rigs exist from the scene's start. All tables are in sequencer.json. I checked it on lavapipe on Asha's stage.

## In progress
- Nothing. M2-FP-18 is in review (reviewer: character, for the weights and the blink timing).

## Exact next step
- M2-FP-17 (the Drownbell with the real Vowbound call) once M2-CMB-05 lands on the integration branch. Merge the integration branch first.

## Known issues
- No gaze yet. Rhen and Toma have no faces (capsules).

## Files touched
- game/cutscene/face_visemes.gd (new), cutscene_face.gd, cutscene_sequencer.gd; game/data/cutscene/sequencer.json
- tests/unit/test_cutscene_face_anim.gd (new)
- docs/kb/tech/cutscenes.md, docs/kb/tasks/M2/M2-FP-18-cutscene-face-animation.md
