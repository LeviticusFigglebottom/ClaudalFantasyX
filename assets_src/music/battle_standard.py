"""Standard battle theme (M1-AUD-02 prototype): loopable, 160 BPM, 4/4.

Original composition for this project (SPEC §2, §9). It is not derived from
any existing battle theme. The colour is E Phrygian with a pelog-like
five-note subset (E F G B C) for the metallophones; the rock/fusion edge
comes from a double-tracked distorted guitar, a fingered bass and a
virtual-analog lead.

Idea: a gamelan colotomic frame (a large gong marks every section start,
a damped kettle gong marks beats 2 and 4) under a rock rhythm section
whose riff is grouped 3+3+3+3+4 sixteenths. Two metallophone parts
interlock (kotekan-style): each plays every other sixteenth and only the
sum is the melody, panned apart so the interlock is audible.

Form (bars, 1.5 s each; the loop is bars 1-48 = 72.0 s):
    1-8   A  riff + ostinato (bars 7-8 step up F, G)
    9-16  B  lead theme
    17-24 C  answer phrase, higher
    25-32 D  breakdown: half-time frame drums, ostinato alone, bass pedal; builds from 29
    33-40 E  theme again as a twin lead in diatonic thirds, metallophone doubling an octave up
    41-46 F  climb C-D-E-F-G-A, guitars on every beat
    47-48 G  turnaround: gong + full stop, frame-drum fill
Intro (3.0 s, played once) = bars 47-48, so the splice into bar 1 carries
the same tails the loop start does.

Render:  python3 assets_src/music/battle_standard.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, freq_response, rng  # noqa: E402
from synth.drums import big_drum, frame_drum, jingle  # noqa: E402
from synth.electric import Amp, bass_note, power_chord  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.lead import lead_phrase  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "battle_standard.ogg")
SEED = 20261024
TARGET_LUFS = -16.0
BPM = 160.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
S16 = BEAT / 4
LOOP_BARS = 48
INTRO_BARS = (47, 48)

# chord root per bar (power-chord root name, in the guitar's low octave)
CHORDS = {}
for _b in range(1, 7):
    CHORDS[_b] = "E"
CHORDS.update({7: "F", 8: "G"})
for _b, _c in zip(range(9, 17), "E C F E E C D F".split()):
    CHORDS[_b] = _c
for _b, _c in zip(range(17, 25), "A G F E C D E E".split()):
    CHORDS[_b] = _c
for _b in range(25, 31):
    CHORDS[_b] = "E"
CHORDS.update({31: "F", 32: "G"})
for _b in range(33, 41):
    CHORDS[_b] = CHORDS[_b - 24]
for _b, _c in zip(range(41, 47), "C D E F G A".split()):
    CHORDS[_b] = _c
CHORDS.update({47: "E", 48: "E"})
GTR_ROOT = {"E": "E2", "F": "F2", "G": "G2", "A": "A2", "C": "C3", "D": "D3", "B": "B2"}
BASS_ROOT = {"E": "E1", "F": "F1", "G": "G1", "A": "A1", "C": "C2", "D": "D2", "B": "B1"}

SECTION = {}
for _b in range(1, 49):
    SECTION[_b] = ("A" if _b <= 8 else "B" if _b <= 16 else "C" if _b <= 24 else "D" if _b <= 32
                   else "E" if _b <= 40 else "F" if _b <= 46 else "G")

# --------------------------------------------------------------------------- #
# Melody (lead synth). (pitch | None, beats)
# --------------------------------------------------------------------------- #
THEME = [
    [("E5", .75), ("F5", .25), ("G5", 1.0), ("F5", .5), ("E5", .5), ("B4", 1.0)],
    [("C5", 1.5), ("B4", .5), ("G4", 1.0), ("B4", 1.0)],
    [("C5", .75), ("B4", .25), ("C5", .5), ("F5", 1.5), ("E5", .5), ("C5", .5)],
    [("B4", 3.0), (None, .75), ("D5", .25)],
    [("E5", .75), ("F5", .25), ("G5", 1.0), ("B5", 1.0), ("G5", .5), ("F5", .5)],
    [("G5", 1.5), ("F5", .5), ("E5", 1.0), ("C5", 1.0)],
    [("F5", 1.0), ("E5", .5), ("D5", .5), ("C5", 1.0), ("D5", 1.0)],
    [("E5", 2.5), (None, 1.5)],
]
ANSWER = [
    [("C6", 2.0), ("B5", 1.0), ("A5", 1.0)],
    [("B5", 1.5), ("A5", .5), ("G5", 2.0)],
    [("A5", 1.0), ("G5", .5), ("F5", .5), ("A5", 1.0), ("C6", 1.0)],
    [("B5", 3.0), (None, 1.0)],
    [("E6", 1.5), ("D6", .5), ("C6", 1.0), ("G5", 1.0)],
    [("F6", 1.5), ("E6", .5), ("D6", 1.0), ("A5", 1.0)],
    [("E6", 1.0), ("F6", .5), ("G6", .5), ("F6", 1.0), ("E6", 1.0)],
    [("E6", 3.0), (None, 1.0)],
]
CLIMB = [[("G5", 4.0)], [("A5", 4.0)], [("B5", 4.0)], [("C6", 4.0)], [("D6", 4.0)], [("E6", 2.0), (None, 2.0)]]

PHRYGIAN = [n(x) % 12 for x in "E4 F4 G4 A4 B4 C5 D5".split()]


def diatonic_below(m: float, steps: int = 2) -> float:
    """The scale tone `steps` degrees below m in E Phrygian (2 = a diatonic third)."""
    k = 0
    p = int(m)
    while k < steps:
        p -= 1
        if p % 12 in PHRYGIAN:
            k += 1
    return float(p)


# --------------------------------------------------------------------------- #
# Ostinato: composite two-bar kotekan in pelog-like degrees (indices into PELOG)
# --------------------------------------------------------------------------- #
PELOG = [n(x) for x in "E5 F5 G5 B5 C6".split()]
KOTEKAN = [0, 1, 2, 1, 0, 3, 2, 1, 0, 1, 2, 3, 4, 3, 2, 1,
           2, 1, 0, 1, 2, 3, 4, 3, 2, 1, 0, -1, 0, 1, 2, 3]
SHIFT = {"E": 0, "F": 1, "G": 2, "B": 3, "C": 4, "A": 4, "D": 1}


def pelog_note(idx: int) -> float:
    o, i = divmod(idx, 5)
    return PELOG[i] + 12 * o


# bass riff: 16th position (1-based) -> (semitone offset, velocity, length in 16ths)
RIFF = {1: (0, 1.0, 2), 3: (12, .62, 1), 4: (0, .9, 2), 6: (12, .6, 1), 7: (0, .9, 2), 9: (10, .6, 1),
        10: (0, .9, 2), 12: (7, .66, 1), 13: (0, .95, 2), 15: (3, .62, 1), 16: (1, .6, 1)}
RIFF_ALT_END = {15: (7, .62, 1), 16: (12, .6, 1)}


def t_of(bar: int, s16: float = 1.0) -> float:
    """Seconds from the loop start (bar 1-based, sixteenth 1-based)."""
    return (bar - 1) * BAR + (s16 - 1) * S16


class Ev:
    __slots__ = ("bus", "kind", "t", "args", "pan", "bar")

    def __init__(self, bus, kind, t, args, pan=0.0, bar=0):
        self.bus, self.kind, self.t, self.args, self.pan, self.bar = bus, kind, t, args, pan, bar


def build_events() -> tuple[list[Ev], list[list[tuple]]]:
    """All loop events, with per-event humanization drawn once (so the intro copy matches)."""
    g = rng(SEED)
    ev: list[Ev] = []

    def add(bus, kind, bar, s16, args, pan=0.0, jit=0.003):
        ev.append(Ev(bus, kind, t_of(bar, s16) + g.normal(0, jit), args, pan, bar))

    for bar in range(1, LOOP_BARS + 1):
        sec = SECTION[bar]
        ch = CHORDS[bar]
        gr = n(GTR_ROOT[ch])
        br = n(BASS_ROOT[ch])
        v = lambda x: float(np.clip(x * (1 + g.normal(0, 0.04)), 0.05, 1.0))  # noqa: E731

        # ---- colotomic gongs
        if bar in (1, 9, 17, 25, 33, 41, 47):
            add("gong", "gong", bar, 1, dict(vel=0.85 if bar != 47 else 1.0), jit=0.0)
        if sec in "ABCEF" or (sec == "D" and bar >= 29):
            for s in (5, 13):
                add("kettle", "kettle", bar, s, dict(m=n("B5"), vel=v(0.4)), pan=0.35)

        # ---- drums
        if sec in "ABCE":
            if bar % 2 == 1:
                add("drums", "big", bar, 1, dict(vel=v(0.8)))
            for s, vv in ((1, 1.0), (4, .7), (7, .9), (10, .7), (13, .85)):
                add("drums", "dum", bar, s, dict(vel=v(0.9 * vv)))
            for s in (5, 13):
                add("drums", "slap", bar, s, dict(vel=v(0.85)), pan=0.05)
            for s in range(1, 17):
                if s not in (1, 4, 5, 7, 10, 13):
                    add("drums", "tek" if s % 2 == 0 else "ghost", bar, s, dict(vel=v(0.55 if s % 4 == 3 else 0.4)),
                        pan=-0.15)
            for s in range(1, 17, 2):
                add("jingle", "jingle", bar, s, dict(vel=v(0.6 if s % 4 == 3 else 0.42), open_=(s == 15 and bar % 2 == 0)),
                    pan=0.3)
        elif sec == "D":
            add("drums", "big", bar, 1, dict(vel=v(0.7)))
            add("drums", "dum", bar, 1, dict(vel=v(0.85)))
            add("drums", "dum", bar, 7, dict(vel=v(0.6)))
            add("drums", "slap", bar, 9, dict(vel=v(0.8)))
            for s in (3, 11, 15):
                add("drums", "tek", bar, s, dict(vel=v(0.4)), pan=-0.15)
            for s in (1, 5, 9, 13):
                add("jingle", "jingle", bar, s, dict(vel=v(0.4 + 0.04 * (bar - 25)), open_=False), pan=0.3)
            if bar == 32:
                for s in range(9, 17):
                    add("drums", "slap" if s % 2 else "tek", bar, s, dict(vel=v(0.45 + 0.06 * (s - 9))), pan=0.05)
        elif sec == "F":
            for s in (1, 5, 9, 13):
                add("drums", "dum", bar, s, dict(vel=v(0.95)))
            if bar % 2 == 1:
                add("drums", "big", bar, 1, dict(vel=v(0.85)))
            for s in (5, 13):
                add("drums", "slap", bar, s, dict(vel=v(0.9)), pan=0.05)
            for s in range(1, 17):
                add("jingle", "jingle", bar, s, dict(vel=v(0.5 if s % 2 else 0.35), open_=False), pan=0.3)
        elif sec == "G":
            if bar == 47:
                add("drums", "big", bar, 1, dict(vel=1.0))
                add("drums", "dum", bar, 1, dict(vel=1.0))
                add("drums", "slap", bar, 1, dict(vel=0.9))
                add("jingle", "jingle", bar, 1, dict(vel=0.7, open_=True), pan=0.3)
                for s in (13, 15):
                    add("drums", "tek", bar, s, dict(vel=v(0.45)), pan=-0.15)
            else:
                for s in (1, 4, 7):
                    add("drums", "dum", bar, s, dict(vel=v(0.8)))
                for s in range(9, 17):
                    add("drums", "slap" if s % 2 else "dum", bar, s, dict(vel=v(0.5 + 0.06 * (s - 9))), pan=0.05)
                add("drums", "big", bar, 13, dict(vel=0.9))

        # ---- bass
        if sec in "ABCEF":
            riff = dict(RIFF)
            if ch != "E":
                riff.update(RIFF_ALT_END)
            if sec == "F":
                riff = {s: (0, .95 if s in (1, 5, 9, 13) else .7, 2) for s in (1, 3, 5, 7, 9, 11, 13, 15)}
            for s, (off, vv, ln) in riff.items():
                add("bass", "bass", bar, s, dict(m=br + off, dur=ln * S16 * 0.92, vel=v(0.75 * vv), mute=0.25),
                    jit=0.004)
        elif sec == "D":
            if bar in (25, 27, 29):
                add("bass", "bass", bar, 1, dict(m=br, dur=2 * BAR - 0.05, vel=0.8, mute=0.0), jit=0.0)
            elif bar >= 31:
                for s in range(1, 17, 2):
                    add("bass", "bass", bar, s, dict(m=br, dur=S16 * 1.8, vel=v(0.6 + 0.02 * s), mute=0.3))
        elif sec == "G":
            if bar == 47:
                add("bass", "bass", bar, 1, dict(m=br, dur=BAR * 0.9, vel=1.0, mute=0.0), jit=0.0)
            else:
                for s in (9, 11, 13, 14, 15, 16):
                    add("bass", "bass", bar, s, dict(m=br + (12 if s in (14, 16) else 0), dur=S16 * 0.9,
                                                     vel=v(0.7), mute=0.3))

        # ---- guitars (two takes, hard left / right)
        for take, pan in ((0, -1.0), (1, 1.0)):
            def gadd(s16, args, jit=0.006):
                add("gtr", "chord", bar, s16, dict(args, take=take), pan=pan, jit=jit)
            if sec in "ABE":
                lvl = 1.0 if sec == "A" else 0.8
                for s in (1, 4, 7, 10, 13):
                    gadd(s, dict(root=gr, dur=S16 * 1.9, vel=v(0.8 * lvl), mute=0.45))
                for s in (2, 5, 8, 11, 14, 16):
                    gadd(s, dict(root=gr, dur=S16 * 0.9, vel=v(0.55 * lvl), mute=0.9, octave=False))
            elif sec == "C":
                gadd(1, dict(root=gr, dur=2 * BEAT * 0.95, vel=v(0.85), mute=0.0))
                gadd(9, dict(root=gr, dur=2 * BEAT * 0.95, vel=v(0.8), mute=0.0))
                for s in (6, 7, 14, 15):
                    gadd(s, dict(root=gr, dur=S16 * 0.9, vel=v(0.5), mute=0.9, octave=False))
            elif sec == "D" and bar >= 29:
                for s in range(1, 17, 2):
                    gadd(s, dict(root=gr, dur=S16 * 1.6, vel=v(0.35 + 0.05 * (bar - 29) + 0.01 * s), mute=0.9,
                                 octave=False))
            elif sec == "F":
                for s in (1, 5, 9, 13):
                    gadd(s, dict(root=gr, dur=BEAT * 0.9, vel=v(0.9), mute=0.15))
                for s in (3, 7, 11, 15):
                    gadd(s, dict(root=gr, dur=S16 * 0.9, vel=v(0.5), mute=0.9, octave=False))
            elif sec == "G" and bar == 47:
                gadd(1, dict(root=gr, dur=BAR * 1.0, vel=1.0, mute=0.0), jit=0.002)
            elif sec == "G":
                for s in (13, 14, 15, 16):
                    gadd(s, dict(root=gr, dur=S16 * 0.9, vel=v(0.6), mute=0.9, octave=False))

        # ---- metallophone ostinato (two interlocking parts)
        if sec in "ABCDEF":
            half = (bar - 1) % 2
            sh = SHIFT[ch]
            lvl = 1.0 if sec == "D" else 0.75 if sec in "BCE" else 0.85
            for s in range(1, 17):
                idx = KOTEKAN[half * 16 + s - 1] + sh
                part = "polos" if s % 2 else "sangsih"
                add("metal", "metal", bar, s, dict(m=pelog_note(idx), vel=v(lvl * (0.5 if s % 4 == 1 else 0.4)),
                                                   damp=S16 * 1.6, part=part),
                    pan=-0.45 if part == "polos" else 0.45)
        elif bar == 47:
            for p in ("E5", "E6", "B5"):
                add("metal", "metal", bar, 1, dict(m=n(p), vel=0.6, damp=None, part="hit"), pan=0.0, jit=0.002)

    # ---- lead lines: list of phrases, each [(t_start, dur, midi, vel)]
    phrases = []

    def line(bars, start_bar, octave=0, vel=0.85):
        out = []
        for i, notes in enumerate(bars):
            b = start_bar + i
            pos = 0.0
            for p, beats in notes:
                if p is not None:
                    out.append((t_of(b) + pos * BEAT + g.normal(0, 0.004), beats * BEAT * 0.97, n(p) + 12 * octave,
                                float(np.clip(vel * (1 + g.normal(0, 0.03)), 0.3, 1.0))))
                pos += beats
        return out

    phrases.append(("lead", line(THEME, 9)))
    phrases.append(("lead", line(ANSWER, 17)))
    twin = line(THEME, 33, vel=0.85)
    phrases.append(("lead", twin))
    phrases.append(("lead2", [(t, d, diatonic_below(m), v * 0.9) for t, d, m, v in twin]))
    phrases.append(("lead", line(CLIMB, 41, vel=0.9)))
    # metallophone doubling of the E-section theme, an octave up (8th-quantized feel)
    for t, d, m, vv in twin:
        ev.append(Ev("metal_lead", "metal", t, dict(m=m + 12, vel=0.42, damp=min(d, 0.6), part="lead"), 0.1, 0))
    return ev, phrases


def event_job(e: Ev) -> tuple:
    """(library callable, kwargs) for one event: picklable, so notes render in parallel."""
    a = e.args
    seed = SEED + int(round(e.t * 1000)) * 13 + hash_kind(e.kind) + (a.get("take", 0) * 7)
    if e.kind in ("dum", "tek", "ghost", "slap"):
        return frame_drum, dict(stroke=e.kind, vel=a["vel"], variant=seed, seed=SEED)
    if e.kind == "big":
        return big_drum, dict(vel=a["vel"], variant=seed, seed=SEED)
    if e.kind == "jingle":
        return jingle, dict(vel=a["vel"], variant=seed, open_=a["open_"], seed=SEED)
    if e.kind == "gong":
        return large_gong, dict(m=n("E1") + 12, vel=a["vel"], seed=SEED + 5, t60=7.0)
    if e.kind == "kettle":
        return kettle_gong, dict(m=a["m"], vel=a["vel"], seed=seed, t60=1.2, damp_at=0.16)
    if e.kind == "bass":
        return bass_note, dict(m=a["m"], dur=a["dur"], vel=a["vel"], seed=seed, mute=a["mute"])
    if e.kind == "chord":
        return power_chord, dict(root=a["root"], dur=a["dur"], vel=a["vel"], seed=seed, mute=a["mute"],
                                 octave=a.get("octave", True))
    if e.kind == "metal":
        return metallophone_note, dict(m=a["m"], vel=a["vel"], seed=seed, decay=2.6 if a["damp"] else 5.0,
                                       hardness=0.62, ombak_hz=6.0, damp_at=a["damp"])
    raise ValueError(e.kind)


KIND_IDS = {"dum": 1, "tek": 2, "ghost": 3, "slap": 4, "big": 5, "jingle": 6, "gong": 7, "kettle": 8, "bass": 9,
            "chord": 10, "metal": 11}


def hash_kind(k: str) -> int:
    return KIND_IDS[k] * 1000003


def bass_bus(x: np.ndarray) -> np.ndarray:
    y = filt(x, [bq_highpass(35, 0.7), bq_peak(90, 2.5, 0.9), bq_peak(800, 2.0, 1.0), bq_lowpass(4500, 0.7)])
    return np.tanh(2.2 * y) / 2.2


def lead_bus(x: np.ndarray) -> np.ndarray:
    """Light drive, presence, and a ping-pong 3/16 delay. The delay network
    (5 taps, feedback 0.32, each repeat darker) is applied as one frequency
    response per channel, so it costs a single FFT."""
    y = np.tanh(1.6 * x) / 1.6
    y = filt(y, [bq_highpass(180, 0.7), bq_peak(2600, 2.0, 1.0), bq_lowpass(9000, 0.7)])
    d = int(round(3 * S16 * SR))
    taps, fb = 5, 0.32
    nfft = 1 << int(np.ceil(np.log2(len(y) + taps * d + SR)))
    Y = np.fft.rfft(y, nfft, axis=0)
    z = np.exp(-2j * np.pi * np.arange(nfft // 2 + 1) / nfft)
    lp = freq_response([bq_lowpass(4500, 0.7)], nfft)
    out = np.empty_like(y)
    for ch in range(2):
        H = np.ones(nfft // 2 + 1, dtype=np.complex128)
        for i in range(1, taps + 1):
            side = 0.9 if i % 2 == ch else 0.3
            H += side * fb ** i * lp ** i * z ** (i * d)
        out[:, ch] = np.fft.irfft(Y[:, ch] * H, nfft)[: len(y)]
    return out


def drum_bus(x: np.ndarray) -> np.ndarray:
    return filt(x, [bq_highpass(32, 0.7), bq_peak(4000, 1.5, 0.8)])


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    events, phrases = build_events()
    mx = LoopMixer(intro_s=2 * BAR, loop_s=LOOP_BARS * BAR, intro_tail_s=6.0)
    mx.bus("drums", -4.0, send=0.12, process=drum_bus)
    mx.bus("jingle", 1.0, send=0.10)
    mx.bus("gong", -11.0, send=0.30)
    mx.bus("kettle", -12.0, send=0.20)
    mx.bus("bass", -2.0, send=0.0, process=bass_bus)
    mx.bus("gtr", -0.5, send=0.10, process=Amp(drive_db=30.0))
    mx.bus("metal", -3.0, send=0.28)
    mx.bus("metal_lead", -7.0, send=0.30)
    mx.bus("lead", -3.0, send=0.22, process=lead_bus)
    mx.bus("lead2", -7.0, send=0.22, process=lead_bus)

    rendered = render_jobs([event_job(e) for e in events], workers=1)  # many small notes: IPC costs more
    intro_offset = -(INTRO_BARS[0] - 1) * BAR
    for e, x in zip(events, rendered):
        mx.add(e.bus, x, e.t, pan=e.pan)
        if e.bar in INTRO_BARS:
            mx.add(e.bus, x, e.t + intro_offset, pan=e.pan, part="intro")
    for k, (bus, notes) in enumerate(phrases):
        t0 = min(t for t, _, _, _ in notes) - 0.05
        rel = [(t - t0, d, m, v) for t, d, m, v in notes]
        x = lead_phrase(rel, seed=SEED + 977 * k, cutoff=1700.0 if bus == "lead" else 1400.0)
        mx.add(bus, x, t0, pan=-0.12 if bus == "lead" else 0.25)

    room = ModFDNReverb(rt60=1.7, rt60_high=0.7, predelay=0.018, size=0.85, mod_depth=8.0, mod_rate=0.6,
                        early_level=0.35, seed=SEED % 9973)
    intro, loop = mx.render(reverb=room, reverb_return_db=-3.0)
    rep: dict = {}
    intro, loop = master_loop(intro, loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    y = np.concatenate([intro, loop])
    S, L = len(intro), len(loop)
    write_ogg(out_path, y, quality=3.5, tags={"LOOPSTART": str(S), "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, S, L, BPM, 4,
                       extra={"intro_bars": 2, "loop_bars": LOOP_BARS})
    m = measure(y)
    if stats is not None:
        stats["splice_residual_db"] = mx.splice_residual_db
        stats["S"], stats["L"] = S, L
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"battle_standard: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  "
              f"peak {m['sample_peak_dbfs']:.2f} dBFS  TP {m['true_peak_dbtp']:.2f} dBTP  loop {S}+{L}")
    return m


if __name__ == "__main__":
    render()
