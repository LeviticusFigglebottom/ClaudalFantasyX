---
id: M3-AUD-831
title: "Act II creature voices: the Ch10-12 bosses, the Wakefin and the Ch10-11 regulars"
role: audio
status: blocked
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: design
depends_on: [M3-AUD-14]
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
The Lead's queue item 1 (2026-10-27): idle, attack, hit and KO sounds for the creatures the creatures track built
for Act II (claude/creatures: M3-CRE-621 mangrove_drowner, 623 lamp_engine, 624 avalanche_ram, 626 wakefin, 627
tannin_archer, gallery_ray, rime_urchin, conduit_crawler), wired through the creature data the way the Act I set is.

## Acceptance criteria
- [x] `assets_src/sfx/act2_creature_sfx.py`: eight families on creature_sfx.py's building blocks, its own seed (the
      Act I set renders byte for byte as before). Each sound follows the sheet's body and its clips' timing:
      the Drowner's drag at 0.7 s, the Lamp Engine's snip at 0.6 s, the Ram's charge at 0.75 s, the Wakefin's breach
      and sweep at 0.8 s, the archer's spit at 0.55 s, the ray's wing at 0.6 s, the urchin's stab at 0.5 s, and the
      crawler's jab at 0.45 s. The two Lit Age constructs hum steadily (rule 3: bound light does not pulse) until
      the KO winds the hum down.
- [x] 68 files in assets/audio/sfx/creatures/. Bosses: idle 1, attack 2, hurt 3, death 1, movement 2. Regulars:
      idle 1, attack 2, hurt 2, death 1, movement 2. 1.5 MB; shipped audio is 70.1 of 72 MiB (ADR 0171).
- [x] Rows in sfx_creatures.json (`cre_<id>_<event>`) and creature_voices.json under each creature's
      creatures.json key. Every creature on claude/creatures now has a voice row. CreatureAudio hears the
      CreatureActor's `creature_id`, so the voices play as soon as the models merge, and the validator's rule
      (every enemies.json enemy has a voice) covers the encounters when design adds them.
- [x] The movement words (heave, clank, trudge, cut, scull, glide, rattle, tick) have their -21 LUFS rule in targets.py.
      The render job is in render_all.py, and `--determinism` reports all 68 files identical.
- [x] PROVENANCE rows (their own commit); tools/tests/test_act2_creature_sfx.py; the loudness gate and
      test_creature_audio.gd pass.
- [ ] Listening pass (human, or the Lead's verdict): the Ram's bellow and the Drowner's moan are the two most
      character-defining; adjust their formants or level on a note.

## Notes
- The phase changes (the Drowner uprooting, the Lamp Engine opening) have no event of their own: creature_voices
  only knows idle, attack, hurt, death and move. When design times those phases, a `phase` event (and a cue) is the
  next step; a phase-change sting in battle_stings.py would serve as well.

## Review log
