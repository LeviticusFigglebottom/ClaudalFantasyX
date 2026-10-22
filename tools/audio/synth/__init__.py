"""Self-authored synthesis library for the project's music and SFX.

Everything here is pure numpy DSP written in-repo: no samples, soundfonts,
downloads or generative models (SPEC §2, §4.3, §9).

Modules
    dsp          filters, oscillators, block-vectorized combs/allpasses, panning
    piano        M1 additive piano (frozen: the M1 sketch still renders byte-identically)
    grand        M1-AUD-02 piano: nonlinear hammer, 1-3 unison strings, two-stage decay,
                 dampers + half pedal, modal soundboard, sympathetic resonance, pedal noise
    performance  phrase rubato and dynamics, voicing and melody lead, humanized pedal curves
    metallophone gamelan-like inharmonic bars in beating pairs
    gongs        large hanging gong and kettle gongs (beating pairs, bloom, glide)
    drums        frame drums (circular-membrane modes, strokes, glide), jingles, big drum
    electric     plucked bass and guitar strings, power chords, oversampled amp + cabinet
    lead         monophonic virtual-analog lead (spectral resonant filter, portamento)
    flute        M1 breathy flute (frozen)
    winds        breath flute: pressure-dependent spectrum, pulsed jet noise, scoops
    voice        formant voices: hummed congregation and a sung (Lamptongue) cantor line
    water        drips and bubbles (Minnaert resonance with the rising chirp)
    pad          soft string pad (detuned polyBLEP saw ensemble + body filter)
    reverb       FDNReverb (M1, frozen) and ModFDNReverb (16 lines, modulated, loop-periodic)
    looping      seamless loop rendering (circular mix, steady state, intro splice), sidecars
    analysis     objective metrics: inharmonicity, partial decay, centroid, echo density,
                 tail peakiness/periodicity, RT60 bands, loop seams
    loudness     approximate ITU-R BS.1770-4 LUFS, momentary max, true peak
    mixer        buses, sends, look-ahead limiter, LUFS normalization, Vorbis export (+tags)
    parallel     deterministic process-parallel note rendering
    score        note names, tempo map, event lists (score-as-code)
"""
from .dsp import SR  # noqa: F401
