---
id: M3-AUD-838
title: "The `charge` choreography style's sound row (battle-presentation's M3-BPR-410: the Avalanche Ram's run)"
role: audio
status: review
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: combat
depends_on: [M3-AUD-831]
milestone: M3
request-from: combat
---
## Goal
Battle-presentation's M3-BPR-410 (on claude/battle-presentation) needs a `charge` row in choreo_sfx.json before it
can add the style: heavy hoofbeats over the approach, a big whoosh, and the weapon contact.

## Acceptance criteria
- [x] assets_src/sfx/charge_sfx.py, built from the Ram's own woolback voice (act2_creature_sfx.py):
      `choreo/step_hoof_1..3` (one broad padded hoof on snow, -21 LUFS like every battle footfall) and
      `choreo/whoosh_charge_1..2` (the mass going past, rising into the lunge, ice rattling in the coat; -20 LUFS, its
      crest at 0.42 s in `peaks`).
- [x] choreo_sfx.json `styles.charge`: approach and return are four `choreo_hoof` each, the strike is
      `whoosh_charge`, and the contact is `@weapon`. The row is marked `pending`, so the checker and
      test_battle_audio_live accept it before choreo.json has the style.
- [ ] When battle-presentation adds `charge` to choreo.json: drop `pending` (audio), or battle-presentation drops it in
      the same commit.

## Review log
