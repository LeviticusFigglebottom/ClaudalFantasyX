---
id: M3-AUD-817
title: "FAST-TRACK: the slice's cutscene sound pass: actors' steps, cue foley, the prologue's room tone"
role: audio
status: review
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M3-AUD-802]
milestone: M3
request-from: lead
---
## Goal
The human's playtest ("parts look primitive"): between the lines, the slice's cutscenes ran on silence. The actors
walked without steps (145 `@mark ... walk|run` across the cutscenes), a book shut, a lantern caught and a glimmer
rose without a sound, and the prologue had no room tone at all.

## Acceptance criteria
- [x] Steps: the director gives every CutsceneStage.cast() actor its own FootstepAudio (AudioDirector.attach_cast),
      so cutscene walks and runs step on the zone's ground: from the hero body's foot contacts once
      hero-integration merges, by distance until then.
- [x] Cue foley: CutsceneAudio hears each sequencer's `cue_played`. cutscene_foley.json maps `@anim` clips (globs
      allowed), `@light` names (on and off; off only when lit) and `@vfx` effects to 34 synthesized foley files
      (assets_src/sfx/cutscene_foley.py), positional at the actor, the light or the place. It is silent through a
      skip, and a Memories replay still sounds.
- [x] The prologue's room tone: `iskarra_dusk`, a 44 s seamless loop at −26 LUFS (water on stone, wind singing
      faintly through the ceramic towers, far drips, the far sea; no life). ambience.json's zone row for
      prologue.tscn.
- [x] tests/unit/test_cutscene_audio.gd (6); data_check validates cutscene_foley.json. `--filter=audio` 146/0,
      `prologue` 5/0, `cutscene` 43/0.

## Notes
- 2026-10-27 audio: Act I's cutscenes name 68 `@sfx` files that don't exist (`assets/audio/sfx/<id>.ogg`; the
  sequencer warns "no sound" and plays nothing). That is the next item, per chapter (M3-AUD-818).
- HeroMotion sync: the cast's steps come from HeroFieldActor.foot_contact, the same signal the field uses, so they
  land on the clip's footfalls with no audio change once hero-integration merges.

## Review log
