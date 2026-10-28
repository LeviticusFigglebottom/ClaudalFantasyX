---
id: M3-AUD-856
title: "Act III, Ch19: compose iskarra_ruins (the drowned capital's zone loop) and iskarra_spire (the Lamp Spire climb)"
role: audio
status: blocked
owner_session: "audio worktree agent"
reviewer: design
depends_on: [M3-AUD-836]
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
The two Ch19 "Iskarra" loops from act3_plan.md §2. `iskarra_ruins` is the prologue's place seen in full: the
iskarra_vigil's world (the Hush's MEL_A two octaves down, the drone on A, glass motes that rise) as a seamless loop,
an elegy in dusk gold. `iskarra_spire` is the Lamp Spire, climbed to shut down the founders' anchor-engine: a
bound-light machine of steady glass, the Lamp Engine's tick, and the Order's hum as the engine's drone. The motifs
are imported, never retyped (hush_theme_v2.MEL_A through iskarra_vigil.py; motifs.ORDER_HUM). Both cues render
through `tools/audio/render_all.py --act3` into `assets/audio/music/act3/`, which stays uncommitted until Git LFS is
live (ADR 0039).

## Acceptance criteria
- [x] `assets_src/music/act3/iskarra_ruins.py`: A aeolian over a fixed A drone, 3/4 at 50 BPM, 38 bars, a
      136.80 s seamless loop (LOOPSTART 0, LOOPLENGTH 6032880; `downbeat_offset_s` 0.300).
      - Form: the sea (1-4); MEL_A two octaves down over the drone alone (5-12); B, the dusk gold, with a pad and
        the viola's climbing line (13-20); MEL_A in the deep again, harmonized, with the viola above it (21-28);
        the thinning, where the glass answers with MEL_A's first cell and the motes rise thickest (29-34); the sea
        again, with the last rising figure left open on B (35-38).
      - The motes' figures and the halo are loaded from iskarra_vigil.py. No voices or words, and no wind or laps
        (the `iskarra_dusk` bed carries those).
      - Measured: 1,152,244 bytes, −16.04 LUFS integrated, true peak −1.80 dBTP, seam jump ×0.60, flux ×0.72,
        Vorbis loop tags match the sidecar, `--determinism` identical.
- [x] `assets_src/music/act3/iskarra_spire.py`: E minor, 4/4 at 104 BPM (2 × ORDER_HUM_BPM, so one hum beat is one
      bar), 56 bars, a 129.23 s seamless loop (LOOPSTART 0, LOOPLENGTH 5699077; `downbeat_offset_s` 0.144).
      - The engine's organ-like hum holds a pedal of E2-B2 and sounds ORDER_HUM an octave down: on G in A
        (5-22), and a fourth up in A' (27-44), where low strings double it.
      - The ticks are the Lamp Engine's (lamp_engine.tick, loaded from it), and the stroke is Lowlight's
        engine_thud. The ticks go from quarters to eighths to added off-sixteenths.
      - A hand-damped metallophone climb figure plays in A, and an octave up in A'.
      - The glass is steady bound tones, tuned just to E so that nothing beats: E5 always, B5 from bar 13, and a
        lamp line climbing B5, C6, D6, E6, with G6 at the top (45-52).
      - The turn (53-56) falls back to bar 1's state. No drums and no bass line: this is a climb, not a fight.
      - Measured: 1,764,254 bytes, −16.06 LUFS integrated, true peak −1.88 dBTP, seam jump ×0.58, flux ×0.35,
        Vorbis loop tags match the sidecar, `--determinism` identical.
- [x] Both rows are appended to `ACT3_FINALS` in tools/audio/render_all.py. `python3 -m unittest
      tools/tests/test_act2_finals.py` passes. Nothing under `assets/audio/music/act3/` is committed.
- [ ] Design's review (listening):
      - whether the ruins' viola sits warm enough against the deep line;
      - whether the spire's tension curve (the off-sixteenths from bar 35, the stroke on every beat at the top)
        reads as a climb and not as combat.
- [ ] When LFS is live, the Lead adds the music.json rows below and the PROVENANCE.md rows, and commits the
      renders.

## Intended music.json rows (not yet added: the files are not committed)
```json
    "iskarra_ruins": {
      "file": "res://assets/audio/music/act3/iskarra_ruins.ogg",
      "resume": true,
      "_note": "Ch19, the Iskarra Ruins in full, the prologue's place understood (M3-AUD-856): a 136.8 s loop; MEL_A two octaves down over the drone on A, rising glass motes, dusk-gold strings; plays over the iskarra_dusk bed"
    },
    "iskarra_spire": {
      "file": "res://assets/audio/music/act3/iskarra_spire.ogg",
      "resume": true,
      "_note": "Ch19, the Lamp Spire climb to the founders' anchor-engine (M3-AUD-856): a 129.2 s loop; the Lamp Engine's tick, steady just-tuned glass, ORDER_HUM as the engine's drone"
    }
```

## Review log
