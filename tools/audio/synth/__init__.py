"""Self-authored synthesis library for the project's music and SFX.

Everything here is pure numpy DSP written in-repo: no samples, soundfonts,
downloads or generative models (SPEC §2, §4.3, §9).

Modules
    dsp          filters, oscillators, block-vectorized combs/allpasses, panning
    piano        additive/modal piano with inharmonic partials, hammer noise, dampers
    metallophone gamelan-like inharmonic bars in beating pairs
    flute        breathy flute: harmonic core + noise-excited bore resonator
    pad          soft string pad (detuned polyBLEP saw ensemble + body filter)
    reverb       early reflections + allpass diffusion + 8-line FDN
    loudness     approximate ITU-R BS.1770-4 LUFS, momentary max, true peak
    mixer        buses, sends, look-ahead limiter, LUFS normalization, Vorbis export
    score        note names, tempo map, event lists (score-as-code)
"""
from .dsp import SR  # noqa: F401
