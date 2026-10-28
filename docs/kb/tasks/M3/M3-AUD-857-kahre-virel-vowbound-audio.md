---
id: M3-AUD-857
title: "Kahre and Virel, the second and third Vowbound: their voices, and their layers on the summon's call, rise and dismissal"
role: audio
status: review
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: combat
depends_on: [M3-AUD-846]
milestone: M3
request-from: lead
---
## Goal
The backlog (TRACK-RULES § SELF-DIRECTED BACKLOG: "creature voice sets for creatures' newest designs"). The creatures
track has built Kahre (M3-CRE-640, docs/kb/art/creatures/vowbound/kahre.md) and Virel
(docs/kb/art/creatures/vowbound/virel.md) on claude/creatures. Both are in vowbound.json, and until now both had only
the shared Vowbound rows and their music stings. Give each the treatment Ilun had in M3-AUD-846.

## Acceptance criteria
- [x] assets_src/sfx/vowbound_sfx.py adds both. Ilun's eleven files are byte-identical: the same seeds and code.
      - **Kahre** (lightning, weight and work):
        - a ground hornbill's low boom for his voice;
        - the mane's running sparks as a dry, high crackle;
        - his strike: the hammer coming down, a thump, and the anvil's ring, with a roll of thunder off it;
        - his knuckle-walk as heavy thumps on the water;
        - the keepsake, the hammer on the anvil, as an iron ring on A4. On the call and rise it is struck twice, like a smith's tap before the blow.
        - Files: creatures/kahre_* (idle 1, attack 2, hurt 2, death 1, step 2) and choreo/kahre_rise, kahre_call and kahre_sink.
      - **Virel** (fire carried on wind):
        - taut sailcloth luffing and snapping;
        - the seams' fire as a soft wavering breath with small crackles;
        - Kite Flare as a fast rising flare;
        - the keepsake, the brass tuning key, as a small brass ping (the act2 brass partials, ×1.6).
        - She flies, so her movement is the cloth filling (drift 2), and she is in choreo_sfx.json `no_steps`.
        - Files: creatures/virel_* and choreo/virel_rise, virel_call and virel_sink.
- [x] Data wiring:
      - creature_voices.json has `kahre` and `virel` (family vowbound, all five events).
      - sfx_creatures.json has `cre_kahre_*` and `cre_virel_*`.
      - sfx_choreo.json has `kahre_*` and `virel_*`.
      - choreo_sfx.json `vowbound.layers` has `kahre` and `virel` (call, rise, sink, fall).
- [x] Loudness:
      - Rules in targets.py: choreo/kahre_* and virel_* at −22 momentary, under the shared rows like Ilun's. Movement words `step` and `drift` at −21.
      - Every file measures within its rule (render_all `--only vowbound_sfx`).
      - All 33 files are byte-identical across `--determinism`.
- [x] Size: the 22 new files are 534 KB. Shipped audio is now 71.52 MiB of the 72 MiB budget, which leaves about 0.48 MiB for non-LFS audio.
- [x] Tests:
      - tools/tests/test_vowbound_sfx.py: every vowbound.json id has a full voice and all four layers, rendered, imported, with PROVENANCE and the −22 rule; fliers take no steps.
      - tests/unit/test_choreo_audio.gd: the no-layers case uses a made-up id, since Kahre has layers now. A new test checks that Kahre and Virel answer the call with their own layer.
      - Godot `--filter=audio`: 171 run, 0 failed.

## Review log
