---
id: M3-AUD-849
title: "Act II creatures, part 2: the ridge lynx, cord moth, glass skate, flat-engine and the four variants"
role: audio
status: blocked
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: design
depends_on: [M3-AUD-831]
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
The Lead (10-27, 21:42), item 4: creature and boss sets for anything the creatures track adds. The creatures branch
added eight creatures with no voice row since M3-AUD-831.

## Acceptance criteria
- [x] act2_creature_sfx.py: four new creatures, appended to the table so the first eight keep their seeds; all 68 of
      the earlier files are byte-identical.
      - **ridge_lynx** (Ch12): a lynx's growl, hiss and yowl; the pounce's leap over the front row (contact
        0.7 s); snowshoe paws in powder snow.
      - **cord_moth** (Ch12): the Act I moth family, pale and a little brighter.
      - **glass_skate** (Ch16): buried in white sand under shallow water; it erupts and slaps (contact 0.5 s).
      - **flat_engine** (Ch14, the boss part on Malcor Venn's barge): a bound iron drum whose paddles press the lagoon
        flat, with a steady hum (never a pulse). Its death is the first ripple.
      - 33 files, at −18, −20 and −21 LUFS; `--determinism` reports all 101 files identical.
- [x] Variants reuse their parent's set at another pitch (as wreck_crab does, since the models reuse the parent's
      rig): root_crab is reef_crab ×0.85, fen_leech sail_leech ×0.9, scree_crawler slag_tortoise ×1.08, and
      rim_crawler tide_crawler ×1.06.
- [x] Every creature on claude/creatures now has a voice row. **The redesigned Mangrove Drowner** (M3-CRE-622: a
      walking stump of root bundles, its phases and contacts unchanged) keeps its set: roots, water and the
      spawn's moan still describe it.
- [x] Shipped audio is 71.0 of 72 MiB (ADR 0171). The loudness, data and act2-creature tests and
      `--filter=creature_audio` pass; validate_data is 0/0.

## Review log
