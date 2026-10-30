---
id: M4-A2P-1952
title: "Audio accessibility pass: sliders reach every sound, mono, captions, distinct battle tells"
role: audio
status: review
owner_session: "claude/audio (session_01UPFyE9L9BA3QodpCNJEfAs)"
depends_on: []
reviewer: lead
milestone: M4
---
## Goal
The Lead's 10-30 21:25 item. Check four things:
- the volume sliders (music, effects, voice) apply to every sound, voice-like barks included;
- the mix survives being folded to mono;
- important non-dialogue cues get captions, if the game has a captions setting;
- Act I's enemy wind-up tells are distinct.

## Acceptance criteria
- [x] **Sliders reach every sound.** Every bus sends to a slider bus:
  - UI, World and Combat go under SFX (the effects slider);
  - Ambience goes under the effects slider too;
  - Music and Voice have their own sliders.

  A player that never names a bus (another track's scene or code) would sit on Master, under no slider but the master's. `AudioDirector.route_stray` now moves it to mix.json `stray_bus` (SFX). Today nothing hits this: the dialogue blip is routed to Voice and the cutscene sound fallback to SFX.
- [x] **Voice-like barks follow the voice slider.** The townsfolk's chatter (`villager_murmur_*`) was on World, under the effects slider only. It now plays on a new `Walla` bus that sends through World, which gives three things:
  - the voice slider (and the effects slider) reaches it;
  - it still ducks under a spoken line;
  - it keeps the zone's reverb.

  The voice slider's help text says so. Battle barks are dialogue lines (the Voice blip). The creatures' voices are effects.
- [x] **Mono.** A new `mono_audio` setting on the Audio page (accessibility.json, appended) folds Master to (L + R) / 2: an `AudioEffectStereoEnhance` with `pan_pullout` 0, ahead of the limiter. It applies live and lets go when turned off.
  - `tools/audio/mono_check.py` holds every rendered file (1,289; 186 of them stereo) to the fold. It fails a file whose whole loses more than 4.5 LU, or whose sounding moment loses more than 8 dB (a part going missing).
  - One failed: `sefir_theme` lost 8.5 dB at 39.4 s, where its hall reverb's late field went out of phase under the bar-9 hum. It was re-rendered with the hall at width 0.7 and now thins by 6.4 dB for that moment.
  - The largest whole-file loss is 2.1 LU (kesh_memory). Fifteen more cues thin by 4–7.4 dB for a moment and keep every part.
- [x] **Captions.** The game has no captions setting. Dialogue, narration and voice-over are already subtitled (DialogueBox and SubtitleStyle). Captions for non-dialogue cues are a UI feature, requested in M4-A2P-1953 with the list of cues that carry meaning.
- [x] **Act I tells are distinct.** `tools/audio/tell_check.py` checks the seven Act I wind-ups (skills.json `charge`):
  - each against its enemy's attack;
  - each against every other tell of its chapter (tells that can meet in one fight).

  All are distinct; the closest is Hullgnaw's coil against its bite, which is 4.8 times as long and 1.28 times brighter. The Cinder Matron's recrust (Ch5) and the Grip (Ch8) are alike but never share a fight, so that pair is reported, not failed.

## Tests
- Godot: `test_audio_accessibility.gd`:
  - a stray player is moved under the effects slider;
  - Walla follows the voice slider and ducks;
  - mono folds live and lets go.
- Godot: `test_ui_settings.gd`'s pinned settings list gains `mono_audio`, the one id appended.
- Tools: `test_mono_check.py`, the judge (anti-phase fails; a wide part and a quiet tail pass).
- Tools: `test_tell_check.py`, the Act I tells as rendered.

## Review log
