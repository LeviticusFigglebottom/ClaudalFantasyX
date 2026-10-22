# Audio pipeline: score-as-code to .ogg

Owner: Audio Director. Status: M1 proof of concept.

Every sound is synthesized by code in this repo. We use no samples, soundfonts,
downloads, or AI generation (SPEC §2, §4.3, §9). The only dependencies are numpy and an
ffmpeg build with libvorbis.

```
assets_src/music/<cue>.py   assets_src/sfx/<set>.py     score / patch (what to play)
            │                          │
            └──────► tools/audio/synth/ ◄──────────────   instruments, reverb, mixer, meter
                              │
                      assets/audio/{music,sfx}/*.ogg       rendered output (committed)
```

**Regenerate everything:** `python3 tools/audio/render_all.py`. This takes about 50 s
for the theme plus under 1 s for the SFX. The script decodes each output again and
prints its size, integrated LUFS, momentary max, and true peak.
`--determinism` renders a second copy and compares the SHA-256 hashes (about 2.5 min in
total). Outputs are bit-identical between runs on the same numpy and ffmpeg/libvorbis
versions. A different libvorbis version may change the bytes but not the sound.

## Library map (`tools/audio/synth/`)

| Module | What it is |
|---|---|
| `dsp.py` | RBJ biquads applied in the frequency domain (no scipy), FFT convolution, a polyBLEP saw, smooth random LFOs, block-vectorized feedback comb and allpass, constant-power pan |
| `piano.py` | Additive/modal piano: stiff-string inharmonic partials, strike-position comb, velocity brightness, two detuned strings per note (beating), two-stage decay, frequency-dependent dampers, hammer click and thump, synthetic soundboard IR |
| `metallophone.py` | Gamelan-like bar: 4 inharmonic modes (1, 2.76, 5.40, 8.93), a beating pair (`ombak_hz`), a resonator bloom, a mallet click, optional hand damping |
| `flute.py` | Breathy flute: harmonic core with delayed vibrato and an attack scoop, plus white noise through a tuned feedback comb (a simplified bore waveguide), air noise, and attack chiff |
| `pad.py` | String pad: detuned polyBLEP saw ensemble with per-voice drift and vibrato, plus the `string_body` bus filter |
| `reverb.py` | `FDNReverb`: early-reflection taps, 4 allpass diffusers, and an 8-line Hadamard FDN with RT60-derived gains and in-loop damping |
| `loudness.py` | BS.1770-4-style integrated LUFS, momentary max, true peak, and a `self_test()` |
| `mixer.py` | `Mixer` (stereo buses, gain, pre-fader processing, reverb send), look-ahead `limit()`, `normalize_integrated()` / `normalize_momentary()`, and `write_ogg()` / `read_audio()` through ffmpeg |
| `score.py` | Note names (`n("F#3")`), a `TempoMap` with ritardandi, `Score.add()` / `Score.line()` with 1-based bars and beats |

## How to add a music cue

1. Copy `assets_src/music/hush_theme_sketch.py` to `assets_src/music/<cue>.py`. Keep
   these conventions:
   - A module-level `SEED`. Every random draw goes through `synth.dsp.rng(seed)`.
     Never use `np.random.*` globals or the time.
   - Use `render(out_path, verbose=True) -> dict` as the entry point, and write with
     `write_ogg()`.
   - Normalize with `normalize_integrated(master, -16.0, ceiling_db=-2.0)` (see
     [mix.md](mix.md)).
2. Write the score as data, with harmony per bar, melody lines as `(pitch, beats, vel)`
   tuples, and accents as tuples. Then map events onto instruments in `render()`.
3. Register the cue in `JOBS` in `tools/audio/render_all.py`.
4. Run `python3 tools/audio/render_all.py --determinism`. Check that it reaches −16 ± 0.5
   LUFS, true peak ≤ −1 dBTP, the size budget holds, and both renders are identical.
5. Add a row to `assets/PROVENANCE.md` with the same columns as
   [provenance_rows.md](provenance_rows.md).
6. Original-melody check (SPEC §2): note in the cue's docstring what the motif is and
   that it is not derived from an existing tune. Do not write any existing game melody,
   even as a test.

To balance levels, measure each bus in 3 s windows. Wrap `Mixer.render` so it runs
`synth.loudness._block_powers(bus, sr, 3.0, 3.0)` on each processed bus before summing.
Aim for the relative levels in mix.md §3.

## How to add an instrument

1. Create `tools/audio/synth/<instrument>.py` with a function like
   `<inst>_note(m, ..., vel, seed, sr) -> np.ndarray`. It returns mono `(N,)` or stereo
   `(N, 2)`, with the attack at index 0. Its length should cover the natural tail and
   end with a short fade, so it never cuts off above about −70 dB.
2. **Vectorize.** Per-sample Python loops are too slow. Express recursion as a
   block-processed structure whose block is no longer than its shortest delay (see
   `feedback_comb`, `allpass_block`, `FDNReverb`). Otherwise use the frequency-domain
   `filt()`.
3. Put shared per-bus processing (body IRs, EQ) in a bus `process=` callable, not in
   each note.
4. Document the model in the module docstring and add it to the table above.

## Known quality limits (honest)

These are ranked by how much they hurt:

1. **Piano realism.** This is an additive approximation, not a physical model. It is
   missing sympathetic and duplex resonance, longitudinal "phantom" partials, the
   hammer–string nonlinearity (timbre changes with velocity only through a low-pass),
   real soundboard modes (we use a 90 ms noise IR), and release noise. The upper
   register tends toward "glassy/music box". Expect a good mid-90s synth piano, not a
   sampled grand.
2. **Performance.** Timing jitter is ±6 ms and velocity varies by ±5 %, plus a tempo
   map. There is no phrase-level rubato, voicing, or pedal nuance (pedal changes
   mechanically on each downbeat). A human pianist shapes much more than this. The
   biggest cheap win is hand-authored per-note timing offsets for the melody.
3. **Flute.** The bore is a linear comb driven by noise, with no jet nonlinearity, so it
   cannot overblow or have real attack transients. It reads as a "synth flute/ocarina",
   so it stays low in the mix.
4. **Pad.** This is a filtered saw ensemble: 80s/90s synth strings, not an orchestral
   section (no bow noise, no per-player articulation).
5. **Reverb.** The 8-line FDN has no modulation. Sharp transients can reveal slight
   metallic periodicity. A 16-line FDN with delay modulation is the M2 upgrade.
6. **Limiter.** It is block-free and zero-phase but simple (6 ms box smoothing). It is
   fine for a few dB on transients, but not for heavy limiting on dense battle mixes.
7. **Meter.** It is "approximately" BS.1770: true peak uses FFT interpolation, and it
   does not handle surround channel weights. It agrees with ffmpeg `ebur128` within
   0.1 LU on our files.
8. **Render speed.** About 50 s for 70 s of music on 4 cores, which is fine for now.
   Dense battle cues may need note caching or multiprocessing.
9. **Not yet built:** shakuhachi-like winds, frame drums, choir (formant/vocoder synth
   for the hymn), the rock/fusion layer, loop-point rendering, and adaptive stems.
