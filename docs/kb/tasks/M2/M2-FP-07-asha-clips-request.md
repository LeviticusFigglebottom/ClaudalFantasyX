---
id: M2-FP-07
title: Animation clips the first-playable thread needs from Asha's rig
role: character
status: todo
owner_session: ""
depends_on: [M1-CHR-03]
milestone: M2
request-from: lead
---
## Goal
The first playable's cutscenes and field ask Asha's model for body clips that don't exist yet; today the sequencer stands her on marks (`CutsceneStage.clip_marks`) in her rest pose. List of what the thread calls, in priority order. Clip names are the `@anim` ids the scripts already use, so naming the AnimationPlayer clips the same makes them play with no code change (CutsceneSequencer plays a same-named clip when the actor has an AnimationPlayer).

## Acceptance criteria (clips on asha.glb's AnimationPlayer, loopable where marked)
- [ ] `idle` (loop): standing breath and weight shift. Field NPC and between-line default.
- [ ] `walk` (loop), `run` (loop): `@mark ... walk|run` moves her; the sequencer will play these during a move.
- [ ] `talk` (loop): a light upper-body gesture layer while she has a line (the sequencer will play it on her lines).
- [ ] Cutscene A (ch02_girl_on_the_beach): `kneel_over_rhen`, `laugh`, `rise_to_stand`, `offer_hand`, `take_hand` (Rhen's clip, listed for the shared rig), and `look_at` as an additive head turn (optional; the sequencer turns the body today).
- [ ] Cutscene B (ch03_the_first_verse): `walk_to_chamber`, `emerge_doorway`, `face_west`.
- [ ] Face: the `@face` cue uses emotions.json ids (soft_smile, neutral, tender, laugh, sad, worried, surprised, exhausted, smile, determined, grief, afraid). Shape keys or a pose library named after those ids would let the sequencer blend them over the cue's seconds; tell us the names you choose.

## Notes
- Do not wait on M2-FP; clips can land one at a time. Coordinate with CHR-07 (face rework).
- The sequencer side (M2-FP-08) drives whatever exists: AnimationPlayer clips by name, and face shape keys if present.

## Review log
