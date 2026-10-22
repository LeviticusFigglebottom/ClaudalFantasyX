# Audio pipeline: score-as-code to .ogg

Owner: Audio Director. Status: M1 (M1-AUD-01 proof of concept, then the M1-AUD-02 upgrade and three prototype cues).

Every sound is synthesized by code in this repo. We use no samples, soundfonts,
downloads, or AI generation (SPEC §2, §4.3, §9). The only dependencies are numpy and an
ffmpeg build with libvorbis (plus ffprobe for the loop-tag check).

```
assets_src/music/<cue>.py   assets_src/sfx/<set>.py     score / patch (what to play)
            │                          │
            └──────► tools/audio/synth/ ◄──────────────   instruments, performance, reverb, mixer, meter
                              │
                      assets/audio/{music,sfx}/*.ogg       rendered output (committed)
                      assets/audio/music/*.loop.json       loop sidecars for looping cues
```

**Regenerate everything:** `python3 tools/audio/render_all.py` (about 6–8 minutes on 4
cores; `--only <text>` renders a subset). The script decodes each output again and
prints its size, integrated LUFS, momentary max, and true peak. For looping cues it also
checks the decoded length against the sidecar, the `LOOPSTART`/`LOOPLENGTH` Vorbis
comments, and the wrap seam, and it copies the loop settings into the Godot `.import`
file (run `godot --headless --path . --import` afterwards). `--determinism` renders a
second copy and compares SHA-256 hashes. Outputs are bit-identical between runs on the
same numpy and ffmpeg/libvorbis versions.

**Measure quality:** `python3 tools/audio/measure_quality.py [--voicing]` prints every
number in the "Objective metrics" section below.
**Regression tests:** `python3 -m unittest discover -s tools/audio/tests` (about 10 s).
CI does not run these yet: the tools/tests discovery root is outside the audio paths.
**Godot side:** `tests/unit/test_audio_loops.gd` checks that each looping cue imports as
`AudioStreamOggVorbis` and that the loop settings match its sidecar.

## Library map (`tools/audio/synth/`)

Frozen modules are kept byte-stable so `hush_theme_sketch.ogg` (M1 v1) still renders
identically for A/B listening. Do not change them; add new modules instead.

| Module | What it is |
|---|---|
| `dsp.py` | RBJ biquads applied in the frequency domain (no scipy), FFT convolution, a polyBLEP saw, smooth random LFOs, block-vectorized feedback comb and allpass, constant-power pan |
| `piano.py` | **Frozen.** M1 additive piano |
| `grand.py` | **M1-AUD-02 piano.** Nonlinear felt hammer (F = K x^p) on the string impedance, with the agraffe reflection, integrated at 4x. 1, 2 or 3 unison strings struck in phase and detuned by fractions of a cent, giving Weinreich two-stage decay. Stiff-string partials with B from a register table. Loss σ = σ₁ + b₃(ω² − ω₁²). Tension pitch glide. Commuted excitation (the modal string IR convolved with the force pulse). Dampers driven by a continuous half-pedal-aware engagement curve, with no dampers above E6 and damper-felt noise. `PianoBody`: stereo modal soundboard IR (Poisson modes, Q falling with frequency, radiation tilt), sympathetic resonance IRs (pedal down: all strings; pedal up: the undamped top), pedal mechanism noise |
| `performance.py` | Phrase-arch rubato and dynamics (Todd/KTH-style), per-role voicing and melody lead (Palmer), metric and contour accents, humanized legato pedal curves with half-changes and drift |
| `metallophone.py` | Gamelan-like bar: 4 inharmonic modes, a beating pair (`ombak_hz`), resonator bloom, mallet click, hand damping |
| `gongs.py` | Large hanging gong and kettle gongs: near-harmonic boss modes with slowly beating pairs, bloom, a slight downward glide |
| `drums.py` | Frame drums from circular-membrane (Bessel) modes with air loading. Strokes (dum, tek, slap, ghost) choose which modes are excited (rim strokes add dense high-order modes). Tension glide, jingles, big drum. Renders are cached per (stroke, velocity, variant) |
| `electric.py` | Modal plucked string (pick-position comb, palm mute, pitch-sharp attack), fingered bass, strummed power chords. `Amp`: mid-hump pre-EQ, two asymmetric soft-clip stages at 4x oversampling (FFT, overlap-save), and a synthesized 4x12-style cabinet IR |
| `lead.py` | Monophonic virtual-analog lead: additive saw/square pair, a resonant 4-pole low-pass applied per harmonic from its analytic response, portamento, scoops, delayed vibrato |
| `flute.py` | **Frozen.** M1 flute |
| `winds.py` | Breath flute: pressure-dependent brightness, jet noise pulsed in sync with the oscillation, bore-tuned breath, breath-before-tone attacks, meri-style scoops, swells |
| `voice.py` | Formant voices: an additive glottal source through 5 cascaded formant resonators per harmonic, nasal pole and zero for /m n/, phoneme glides. `hum_ensemble`: a congregation with pitch scatter and staggered breathing; its loop mode wraps each voice at a random phase |
| `water.py` | Drips: a splash transient plus Minnaert bubbles (f ≈ 3.26/r, van den Doel damping and rising chirp) |
| `pad.py` | String pad: detuned polyBLEP saw ensemble plus the `string_body` bus filter |
| `reverb.py` | `FDNReverb` (**frozen**, 8 lines). `ModFDNReverb`: 16 lines of 25–100 ms with modulated delays read by cubic Lagrange interpolation, per-line 3-tap loss filters from RT60 at DC and at 8 kHz, LFOs that can snap to whole cycles per loop (`loop_period`), and `t_offset` to phase-align an intro |
| `looping.py` | `LoopMixer`: circular placement, steady-state bus processing via a wrap-around pre-roll, the intro rendered together with an un-wrapped loop start (`splice_residual_db`), `master_loop` (common gain plus wrap-aware limiting, with a limiter report), `write_loop_sidecar` |
| `analysis.py` | Objective metrics: partial finder and B fit, heterodyne partial envelopes and decay rates, spectral centroid, crest factor, echo density (Abel & Huang), mixing time, tail spectral peakiness against Rayleigh statistics, tail periodicity, kurtosis, band RT60, loop-seam report |
| `loudness.py` | BS.1770-4-style integrated LUFS, momentary max, true peak, and a `self_test()` |
| `mixer.py` | `Mixer` (stereo buses, gain, pre-fader processing, reverb send), look-ahead `limit()`, `normalize_integrated()` / `normalize_momentary()`, `write_ogg(tags=...)` / `read_audio()` |
| `parallel.py` | Deterministic process-parallel note rendering (`HYMN_AUDIO_JOBS=1` forces serial). It pays off for heavy notes (the piano) but not for thousands of short ones |
| `score.py` | Note names, `TempoMap`, `Score.add()` / `Score.line()` |

## How to add a music cue

1. Copy the closest existing cue: `hush_theme_v2.py` for through-composed pieces, or
   `battle_standard.py` / `temple_trial.py` for loops. Keep the conventions: a
   module-level `SEED`, all randomness through `synth.dsp.rng(seed)`, and
   `render(out_path, verbose=True, stats=None) -> dict`.
2. Normalize to −16 LUFS with a −2 dBFS ceiling (`normalize_integrated` or `master_loop`).
3. **Loops:** build on `LoopMixer(intro_s, loop_s)`. Place loop events in loop time
   (they wrap). If there is an intro, make it a copy of the loop's own last bars so the
   splice carries the same tails. Write tags `LOOPSTART`/`LOOPLENGTH` (in samples) and
   the sidecar. Never make a bus processor depend on the signal's overall level (an amp
   that normalizes its own input would sound different in the intro and the loop).
   Never use `hash()` for seeds, because it is salted per process.
4. Register the cue in `JOBS` in `render_all.py` (kind `music` or `music_loop`), add the
   asset paths to `LOOPING_CUES` in `test_audio_loops.gd` for loops, and append
   PROVENANCE rows (one per output file, sidecars included).
5. Run `render_all.py --determinism`, then `godot --headless --path . --import`, then
   `tools/ci_local.sh`.
6. Original-melody check (SPEC §2): the cue's docstring states what the material is and
   that it is not derived from an existing tune.

## Objective metrics (M1-AUD-02)

None of the agents can listen, so we compare against physical expectations and against
the M1 version. Reproduce everything with `measure_quality.py --voicing`.

### Piano: old additive `piano` vs new `grand` (through its soundboard), velocity 0.55

Reference: B within 2x of the register table (concert-grand measurements scatter about
that much). Fundamental *early* decay (0.1–1.0 s) ranges, which are approximate,
recalled from the piano-acoustics literature, and kept wide on purpose: A1 3–10, C3
4–12, C4 6–16, C5 8–25, C6 12–40, C7 20–70 dB/s.

| Note | B / ref (old → new) | Early decay dB/s (old → new) | In range (old → new) | Two-stage (old → new) | Audible length s (old → new) | Centroid at 30 ms, Hz (old → new) |
|---|---|---|---|---|---|---|
| A1 (33) | 0.53 → 0.97 | 15.4 → 5.9 | no → yes | yes → weak (late 4.1) | 10.1 → 10.4 | 762 → 628 |
| C3 (48) | 1.15 → 0.97 | 15.1 → 8.6 | no → yes | yes → yes | 5.5 → 10.1 | 1090 → 687 |
| C4 (60) | 0.93 → 0.98 | 10.6 → 11.6 | yes → yes | no → yes (late 4.7) | 3.0 → 10.0 | 1300 → 843 |
| C5 (72) | 0.76 → 0.98 | 13.3 → 15.7 | yes → yes | no → yes | 1.5 → 6.2 | 1790 → 1039 |
| C6 (84) | 0.49 → 0.98 | 43.5 → 22.4 | no → yes | no → yes | 0.74 → 3.5 | 2750 → 1087 |
| C7 (96) | 0.30 → 0.98 | 91.8 → 32.4 | no → yes | – | 0.43 → 1.7 | 4240 → 1406 |

- In the new model, decay rate rises with partial frequency in every register (slope
  +2.8 to +10 dB/s per kHz). The old model was non-monotonic at C4 and C6 (slopes of
  −0.7 and −1.0).
- From pp to ff at C4 (velocity 0.2 → 0.8), the level rises 18.9 dB and the attack
  centroid rises 2.2x (old: 20.5 dB and 1.6x). Hammer contact shortens from 3.0 ms to
  2.1 ms, so timbre now changes with the hammer, not through a tone control.
- The old upper register died 2–4x too fast (C6 0.7 s, C7 0.4 s). That is a large part
  of the "music box" impression.
- The new attack is **warmer** than the old one (C4 mf at 843 Hz vs 1300 Hz). That is
  deliberate but not verified by ear. If the human hears it as muffled, raise the
  `soundboard_ir_modal` high-shelf (currently +7 dB at 1.1 kHz).

### Reverb: 8-line FDN vs modulated 16-line FDN (RT60 2.6 s), with ideal diffuse noise as the target

| Metric | Old FDN | New ModFDN | Ideal decaying Gaussian noise |
|---|---|---|---|
| Tail spectral p99/median (Rayleigh predicts 8.2 dB) | **15.9 dB** | 8.9 dB | 8.5 dB |
| Fraction of bins > 10x local mean | 1.2 % | 0.022 % | 0.022 % |
| Tail periodicity (max normalized autocorrelation, 4–250 ms) | **0.35** | 0.067 | 0.017 |
| Mixing time (echo density ≥ 0.95) | 165 ms | 90 ms | 95 ms |
| Tail kurtosis (Gaussian = 3) | 2.95 | 3.02 | 3.03 |
| L/R correlation of the tail | −0.18 | 0.00 | 0.00 |
| Modal density (Σ delays) / modal overlap at RT60 | 0.43 /Hz / 0.36 | 0.87 /Hz / 0.74 | – |
| RT60 at 500 Hz / 4 kHz | 2.60 / 2.07 s | 2.62 / 1.97 s | – |

The old tail had about 50x too many stationary spectral peaks for a diffuse field, and a
strong repeating echo. That is the metallic ring. Two fixes did the work: delay
modulation, and taking the early-reflection taps out of the late network's input (a
fixed tap pattern feeding the FDN printed itself into the tail's autocorrelation).
Modulation is about 12 samples at about 0.7 Hz by default, which is a few cents of
pitch wobble in the tail. The Hush theme uses 8 samples at 0.5 Hz.

### Performance (Hush v1 vs v2)

| Metric | v1 sketch | v2 |
|---|---|---|
| Melody minus accompaniment loudness (split buses) | **−1.0 LU** (melody buried) | +8.3 LU |
| Loudness range (EBU 3342-style) | 5.5 LU | 8.6 LU |
| Local tempo | tempo map only | 49–77 BPM (phrase arches plus the written ritardando) |
| Pedal | one mechanical change per downbeat | 25 humanized lifts, 2 half-changes, slow final release |
| Sympathetic layer vs board | none | −22.6 dB |
| L/R correlation | 0.81 | 0.36 (wider: a spaced-pair image) |

v2 voicing (+8.3 LU) is at the high end of what I'd aim for (5–7). If the melody sounds
detached from the accompaniment, lower `Voicing.scale["mel"]` toward 1.06.

### Shipped cues (decoded files)

| File | Length | Integrated | True peak | LRA | Limiter | Size |
|---|---|---|---|---|---|---|
| `hush_theme_v2.ogg` | 69.4 s | −16.1 LUFS | −1.6 dBTP | 8.6 LU | not reported | 0.76 MiB |
| `battle_standard.ogg` (3.0 s intro + 72.0 s loop) | 75.0 s | −16.1 LUFS | −1.9 dBTP | 5.4 LU | not reported | 1.09 MiB (q 3.5) |
| `temple_trial.ogg` (80.0 s loop) | 80.0 s | −16.0 LUFS | −3.2 dBTP | 5.3 LU | 0 % of samples touched | 0.80 MiB (q 3.0) |

Note: `master_loop` can report the limiter's work (`render(stats=...)["limiter"]`), but
only the temple number was captured. For Hush and battle, the ceiling is −2 dBFS and the
decoded true peaks stay at or below −1.6 dBTP. Crest factors are 18.1 dB (Hush) and
17.0 dB (battle), so neither is being squashed.

Loop checks:
- **Decoded length:** matches the sidecar exactly. Tags: battle LOOPSTART 132300 /
  LOOPLENGTH 3175200; temple 0 / 3528000.
- **Wrap seam:** spectral flux across the seam is 0.85x (battle) and 0.49x (temple) the
  loop's median, so there's no spectral discontinuity. The battle seam's sample jump is
  4.9x the median step, because the seam lands on the bar-1 downbeat attack. Continuous
  cuts at other downbeats (bars 9, 17, 33, 41) measure 1.0–4.4x, so it reads as an
  attack, not a click.
- **Battle intro→loop splice** (first play only): the residual is −102.5 dB, because the
  intro is the loop's own last two bars.

## Known quality limits (honest, ranked)

1. **Nobody has listened.** Every number above is a proxy. Physical plausibility is
   necessary, not sufficient: a piano can pass all these checks and still sound
   synthetic (for example, the attack's micro-structure, or how the soundboard colours
   individual notes).
2. **Synthetic voice (temple Cantor).** Formant singing is the element most likely to be
   uncanny. It is mixed −8 LU under the hum and far back, and it can be removed with
   `CANTOR = False`. The congregation hum is much safer, because a closed-mouth /m/ has
   few cues to get wrong.
3. **Distorted guitar and lead synth.** The amp and cabinet are plausible on paper (cab
   roll-off, aliasing products > 10 kHz at −64 dB, crest 12 dB), but the string feeding
   them is modal, not a real pick on steel. The palm-mute chug will likely read as "synth
   guitar", in the 90s-console-rock sense. The lead is honest virtual analog.
4. **Piano.** Still missing: longitudinal/phantom partials, duplex scaling, hammer felt
   hysteresis, real per-note soundboard admittance, and the key/action noise beyond a
   knock. Register evenness varies by about ±3 dB note to note.
5. **Pad.** Unchanged 80s/90s saw-ensemble strings. Kept quiet (−19 dB bus) in Hush v2.
6. **Render time.** About 6–8 minutes for everything on 4 shared cores. The battle cue
   spends most of its time in event synthesis (3,000+ notes, serial) and the oversampled
   amp.
7. **Meter.** Approximately BS.1770. It agrees with ffmpeg `ebur128` within about 0.1 LU.
8. **Not yet built:** shakuhachi-specific techniques (breath ornaments), a choir with
   Lamptongue lyrics (the hymn), adaptive stems, field-to-battle stingers.
