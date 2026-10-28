---
id: M3-AUD-846
title: "Ilun the Vowbound's audio: his voice, and his layers on the summon's call, rise and dismissal"
role: audio
status: review
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: combat
depends_on: [M3-AUD-13, M3-AUD-14]
milestone: M3
request-from: lead
---
## Goal
The Lead (10-27, 21:42): creatures is modelling Ilun (M3-CRE-638) and battle-presentation has the summon choreography
ready for him (M3-BPR-417). Write his rise, act, special, dismiss and sting sounds, and wire them to that
choreography.

## Acceptance criteria
- [x] assets_src/sfx/vowbound_sfx.py: Ilun is a vast spectral manta (vowbound.md §1). His sound is slow wing-water,
      the net's light as a glassy shimmer, and his child's glass net-float chiming on E5 (the Hush's key).
      - creatures/ilun_*: idle 1, attack 2 (a heavy sweep of water, never a blow), hurt 2, death 1, glide 2.
      - choreo/ilun_rise, ilun_call, ilun_sink: layers at -22 LUFS, under the shared rows.
      - 11 files, deterministic.
- [x] **The rise, the dismissal and the call:** choreo_sfx.json gains a `vowbound.layers.ilun` table and
      ChoreoAudio plays a Vowbound's layer beside the shared row (`_layer`). The call gets `ilun_call` over
      vowbound_beckon; the rise gets `ilun_rise` over vowbound_rise or rise_long; the sink and the fall get
      `ilun_sink`. data_check validates the table.
- [x] **The act:** creature_voices.json has an `ilun` row. CreatureAudio hears his actions, hits and fall by his
      combatant id now, and his model's clips once M3-CRE-638 lands (the model's CreatureActor `creature_id = ilun`).
- [x] **The special:** Floodnet already has its own sound (battle_sfx's `flood` -> `floodnet`, and choreo's chant
      style), and his attack voice plays on it. The summon sting `ilun_summon` already exists (M2-AUD-03,
      battle_sfx `vowbound_stings`).
- [x] test_choreo_audio: the call, the rise, the long rise, the fall and the sink each play Ilun's layer, and a
      Vowbound with no layers plays only the shared rows. The `choreo_audio`, `creature_audio`, `battle_audio`,
      `vowbound` and `summon` filters pass, and the loudness and data tests pass.
- [ ] When the model lands: check his clips map (attack / cast -> the move row), and re-hear the rise against
      battle-presentation's re-rendered summon shots.

## Review log
