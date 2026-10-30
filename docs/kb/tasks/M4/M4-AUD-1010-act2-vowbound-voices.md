---
id: M4-AUD-1010
title: "Request: battle voices and summon layers for Nhoa, Hesk, Ethren and Kesh (drop their sfx_pending)"
role: audio
status: todo
owner_session: ""
depends_on: [M4-A2P-024, M4-A2P-025]
milestone: M4
request-from: combat
---
## Goal
vowbound.json now has rows for `nhoa`, `hesk`, `ethren` (M4-A2P-024) and `kesh` (M4-A2P-025). Each carries
`"sfx_pending": "M4-AUD-1010"`, so tools/tests/test_vowbound_sfx.py checks them only once their voice exists.
- Give each a full battle voice in creature_voices.json and its summon layers in choreo_sfx.json, as Ilun, Kahre and
  Virel have (assets_src/sfx/vowbound_sfx.py, with PROVENANCE rows).
- Then drop `sfx_pending` from each row. The test checks it: a row with a voice must not keep the key.
- Hesk and Ethren are winged: `FLIERS` and `no_steps` if they fly.

## Acceptance criteria
- [ ] Voices and layers for the four; `sfx_pending` gone; test_vowbound_sfx green with them in.

## Review log
