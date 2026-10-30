---
id: M4-AUD-1010
title: "Request: battle voices and summon layers for Nhoa, Hesk, Ethren and Kesh (drop their sfx_pending)"
role: audio
status: review
owner_session: "claude/audio (session_01UPFyE9L9BA3QodpCNJEfAs)"
depends_on: [M4-A2P-024, M4-A2P-025]
reviewer: combat
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
- [x] Voices and layers for the four; `sfx_pending` gone; test_vowbound_sfx green with them in.

- 2026-10-30 (claude/audio): done in `assets_src/sfx/vowbound_sfx.py` (appended; Act I's three render byte-identical): each of Nhoa, Hesk, Ethren and Kesh has a full battle voice (creature_voices.json, `cre_<id>_*` rows in sfx_creatures.json) and rise / call / sink layers (choreo_sfx.json, `fall` plays `sink` as Act I's), at the Act I Vowbound targets. All four are in `no_steps` and test_vowbound_sfx's FLIERS (Nhoa and Ethren hover, Hesk flies, Kesh is a column of water). `sfx_pending` is dropped from the four vowbound.json rows. Also: Nhoa's `nhoa_echo` and Hesk's `cord_lift` skills have their own sounds, and Kesh has a call sting (`kesh_summon`, battle_sfx.json vowbound_stings).

## Review log
