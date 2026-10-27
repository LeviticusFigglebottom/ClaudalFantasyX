---
id: M3-BPR-410
title: "A sound row for a new 'charge' choreography style (the Avalanche Ram's run)"
role: audio
status: todo
owner_session: ""
depends_on: [M3-BPR-408]
milestone: M3
request-from: combat
---
## Goal
Battle-presentation wants the Avalanche Ram (Ch12 boss) to charge: a long, low run with a heavy lean and a big lunge,
not the regular melee. Every choreo.json style needs a row in your `game/data/audio/choreo_sfx.json`
(test_battle_audio_live), so please add a `charge` row: heavy hoofbeats over the approach, a big whoosh, the weapon
contact. Then battle-presentation adds the style and turns it on.

The style, ready to add to choreo.json `styles`:
`"charge": {"travel": "target", "stop_short_m": 1.0, "approach_sec": 0.55, "strike_sec": 0.3, "contact_at": 0.5,
"recover_sec": 0.2, "return_sec": 0.6, "clip": "attack", "lunge_m": 0.6, "lift_m": 0.0, "crouch_m": 0.12,
"lean_deg": 22.0, "react_scale": 1.5}`

It also needs `camera.by_style.charge` and `style_by_actor.avalanche_ram.physical = "charge"`.

## Acceptance criteria
- [ ] choreo_sfx.json `charge` row (audio).
- [ ] The style and its rows in choreo.json, and test_battle_act2_bosses asserting the Ram charges (battle-presentation).

## Review log
