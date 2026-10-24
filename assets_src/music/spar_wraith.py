"""`spar_wraith`: the Spar-Wraith boss (M3-AUD-08; act_outline Ch4): a 2.8 s intro and a 72.8 s loop.

Original composition for this project (SPEC §2, §9). The lopsided ostinato, the flute's theme and the sound of the
rigging were written for this fight and are not derived from any existing tune. The brief (act_outline Ch4,
ADR 0017): mid-strait the ferry comes on a trader lost in the Rising that took Oruvel, drifting with its sails set
and nobody at the helm. Rhen and Asha board it for its name-board, and a spawn tangled in its rigging comes down
at them on the dead ship's deck. Eerie before it is loud: rope, wind and dead wood.

F# Locrian (F# G A B C D E: the home chord has a diminished fifth, so it never sits still), 7/8 grouped 2+2+3 at
an eighth of 300 (a bar is 1.4 s), 52 bars. The odd bar is the ship's roll with nobody steering: it always comes
round a beat short.

Ensemble (all synthesized; no samples):
* the rigging: wind through the shrouds (a noise band that drifts in pitch, with a thin whistle on top), and
  rope creaking under load (a stick-slip pulse train through a few wood and fibre resonances, its rate gliding as
  the strain changes), on the bar's long group;
* dead wood: frame drums in 2+2+3, the big drum on each bar, and a larger, slacker drum as the hull knocking;
* the bass: a fingered bass on the root and then its fifth, which on F# is the tritone C;
* the theme: a low, breathy breath flute (F#4-D5 in A, up to C6 in B), and an open high plucked line (the
  shrouds) when the theme returns;
* the dead sails: a low string chord through the becalmed section only, kept quiet.

Form: 1-8 the rigging (wind, creaks, the bass; drums from 5) | 9-16 A | 17-24 A' with the shrouds | 25-32 B,
higher, drums doubled | 33-44 becalmed: the drums stop, the sails, the wind and the hull knocking, building from 41 |
45-52 A'' with the shrouds, a fill in bar 52 into the wrap.

Loop: the intro is a copy of bars 51-52 (so the splice into bar 1 carries the same tails); LOOPSTART = its length,
LOOPLENGTH = 52 bars.

Render:  python3 assets_src/music/spar_wraith.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, rng  # noqa: E402
from synth.electric import bass_note, string_pluck  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "spar_wraith.ogg")
SEED = 20261025
TARGET_LUFS = -16.0
BPM = 300.0                # eighths
E8 = 60.0 / BPM
BAR = 7 * E8
BARS = 52
LOOP_S = BARS * BAR
INTRO_BARS = 2
INTRO_S = INTRO_BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065

CHORDS = (["F#"] * 6 + ["G", "G"]
          + ["F#", "F#", "D", "Em", "F#", "F#", "C", "C"]
          + ["F#", "F#", "D", "Em", "F#", "G", "C", "F#"]
          + ["G", "G", "Em", "Em", "C", "C", "F#", "F#"]
          + ["F#"] * 4 + ["G", "G", "F#", "F#", "C", "C", "G", "G"]
          + ["F#", "F#", "D", "Em", "F#", "G", "C", "C"])
SECTION = ["I"] * 8 + ["A"] * 8 + ["A1"] * 8 + ["B"] * 8 + ["X"] * 12 + ["A2"] * 8
ROOTS = {"F#": "F#1", "G": "G1", "D": "D2", "Em": "E2", "C": "C2", "Bm": "B1"}
FIFTH = {"F#": 6, "G": 7, "D": 7, "Em": 7, "C": 7, "Bm": 7}     # on F# the "fifth" is the tritone
SAILS = {"F#": ["F#2", "C3", "A3"], "G": ["G2", "D3", "B3"], "C": ["C3", "G3", "E4"]}
SHROUDS = {"F#": ("A5", "C6"), "G": ("B5", "D6"), "D": ("A5", "F#5"), "Em": ("G5", "B5"), "C": ("E6", "G5")}
GROUPS = (0, 2, 4)                         # 2+2+3

## the theme, (pitch, eighths) per bar
THEME_A = [[("F#4", 2), ("G4", 2), ("A4", 3)], [("C5", 4), ("B4", 1), ("A4", 2)],
           [("A4", 2), ("F#4", 2), ("D4", 3)], [("E4", 2), ("G4", 2), ("B4", 3)],
           [("A4", 2), ("G4", 2), ("F#4", 3)], [("C5", 2), ("B4", 2), ("C5", 3)],
           [("E5", 4), ("D5", 1), ("C5", 2)], [("G4", 6), (None, 1)]]
THEME_A1 = THEME_A[:5] + [[("D5", 2), ("B4", 2), ("G4", 3)], [("E5", 4), ("D5", 1), ("C5", 2)],
                          [("F#4", 6), (None, 1)]]
THEME_A2 = THEME_A1[:7] + [[("C5", 2), ("B4", 2), ("G4", 2), (None, 1)]]
THEME_B = [[("D5", 2), ("G5", 2), ("F#5", 3)], [("B5", 4), ("A5", 1), ("G5", 2)],
           [("E5", 2), ("G5", 2), ("B5", 3)], [("A5", 4), ("G5", 1), ("E5", 2)],
           [("G5", 2), ("E5", 2), ("C6", 3)], [("B5", 2), ("A5", 2), ("G5", 3)],
           [("F#5", 3), ("E5", 1), ("C5", 3)], [("F#5", 6), (None, 1)]]


def t_of(bar: int, eighth: float = 0.0) -> float:
    return (bar - 1) * BAR + eighth * E8


class Placer:
    """Adds each loop event, and a copy of every event that sounds in the loop's last INTRO_BARS bars (including the
    tails of earlier ones) to the intro, at the same place relative to the loop end."""

    def __init__(self, mx: LoopMixer):
        self.mx = mx
        self.win = LOOP_S - INTRO_S

    def __call__(self, bus: str, x: np.ndarray, t: float, pan: float = 0.0) -> None:
        self.mx.add(bus, x, t, pan=pan)
        tm = t % LOOP_S
        # (an event humanized up to 50 ms before bar 1 is already in the mixer's cold copy of the loop start)
        if tm + x.shape[0] / SR > self.win and not -0.05 <= t < 0.0:
            self.mx.add(bus, x, tm - self.win, pan=pan, part="intro")


def rope_creak(dur: float, rate0: float, rate1: float, seed: int, sr: int = SR) -> np.ndarray:
    """Rope working under load: stick-slip pulses whose rate glides rate0 -> rate1 (Hz), each one ringing a few
    fibre and wood resonances, swelling in and out. Mono."""
    g = rng(seed)
    N = int(dur * sr)
    imp = np.zeros(N)
    t = 0.0
    while t < dur:
        u = t / dur
        rate = rate0 * (rate1 / rate0) ** u
        k = int(t * sr)
        if k < N:
            imp[k] += g.uniform(0.5, 1.0) * np.sin(np.pi * u) ** 0.7
        t += (1.0 / rate) * g.uniform(0.75, 1.3)
    tt = np.arange(int(0.04 * sr)) / sr
    ir = np.zeros(len(tt))
    for f, d, a in ((g.uniform(520, 640), 0.012, 1.0), (g.uniform(1050, 1250), 0.008, 0.7),
                    (g.uniform(2100, 2500), 0.004, 0.45), (g.uniform(260, 320), 0.02, 0.5)):
        ir += a * np.sin(2 * np.pi * f * tt) * np.exp(-tt / d)
    x = fft_convolve(imp, ir)[:N]
    return x / (np.abs(x).max() + 1e-9)


def rigging_wind(dur: float, seed: int, sr: int = SR) -> np.ndarray:
    """Wind in the shrouds: a noise band drifting 300-900 Hz with a thin whistle drifting near 1.1-1.6 kHz, under
    a Hann window (overlapping copies at half its length sum to a steady wind). Mono."""
    g = rng(seed)
    N = int(dur * sr)
    noise = g.standard_normal(N)
    out = np.zeros(N)
    hop = int(0.25 * sr)
    c_band = 300.0 * 3.0 ** g.uniform(0, 1)
    c_wh = 1100.0 * 1.45 ** g.uniform(0, 1)
    for i in range(0, N, hop):
        c_band = float(np.clip(c_band * 2 ** g.normal(0, 0.12), 300.0, 900.0))
        c_wh = float(np.clip(c_wh * 2 ** g.normal(0, 0.05), 1100.0, 1600.0))
        a = max(0, i - hop)
        seg = noise[a: min(N, i + 2 * hop)]
        y = filt(seg, [bq_bandpass(c_band, 1.2, sr)], sr=sr) * 0.5 + filt(seg, [bq_bandpass(c_wh, 30.0, sr)], sr=sr)
        out[a: a + len(y)] += y[: N - a] * np.hanning(len(y))[: N - a]
    gust = 0.6 + 0.4 * np.sin(2 * np.pi * np.arange(N) / N * 3 + g.uniform(0, 6.28)) ** 2
    return out * gust * np.hanning(N) / (np.abs(out).max() + 1e-9)


def add_theme(place: Placer, bars: list, start_bar: int, seed: int, vel: float, pan: float = -0.12) -> None:
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, e in bar:
            d = e * E8
            if p is None:
                pos += d
                first = True
                continue
            x = breath_flute(n(p), d * 0.94 + 0.02, vel * g.uniform(0.94, 1.04), seed=seed + int(round(pos * 1000)),
                             breath=0.7, scoop_cents=55.0 if first or e >= 3 else 15.0,
                             vib_cents=14.0 if e >= 3 else 0.0, vib_rate=4.4, swell=0.3 if e >= 4 else 0.0,
                             attack=0.05, release=0.25, beta=0.5)
            place("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.004)), pan=pan)
            pos += d
            first = False


def build(mx: LoopMixer) -> None:
    place = Placer(mx)
    g = rng(SEED)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        calm = sec == "X" and bar < 41
        drums_on = (sec != "I" or bar >= 5) and (sec != "X" or bar >= 41)
        r = n(ROOTS[ch])
        # the bass: root, root, fifth (the tritone on F#)
        if not calm or bar % 2 == 1:
            for e, m, ln, v in ((0, r, 1.8, 0.85), (2, r, 1.6, 0.62), (4, r + FIFTH[ch], 2.7, 0.72)):
                if calm and e:
                    continue
                place("bass", bass_note(m, (BAR * 2 if calm else ln * E8), v * g.uniform(0.93, 1.05),
                                        seed=SEED + 100 * bar + e, mute=0.0 if calm else 0.3), t_of(bar, e) + 0.003)
        # dead wood
        if drums_on:
            lvl = 0.8 if sec in ("I", "X") else 1.0
            for e, (stroke, v) in enumerate((("dum", 0.9), ("ghost", 0.3), ("tek", 0.6), ("ghost", 0.3),
                                              ("slap", 0.8), ("ghost", 0.3), ("tek", 0.5))):
                place("drums", frame_drum(stroke, lvl * v * g.uniform(0.9, 1.06), variant=bar * 7 + e, seed=SEED + 3),
                      t_of(bar, e) + float(g.normal(0, 0.003)), pan=-0.12 if stroke in ("tek", "ghost") else 0.0)
            place("big", big_drum(0.8 * lvl, variant=bar, seed=SEED + 4), t_of(bar))
            if sec in ("B", "A2"):
                place("big", big_drum(0.55, variant=bar + 2, seed=SEED + 4), t_of(bar, 4))
        if sec in ("I", "X"):          # the hull knocking: a larger, slacker drum, late in the bar
            for e in ((4,) if bar % 2 else (4, 5.5)):
                place("hull", frame_drum("dum", 0.75 * g.uniform(0.85, 1.05), size=1.6, variant=bar + int(e),
                                         seed=SEED + 9), t_of(bar, e) + float(g.normal(0, 0.01)), pan=0.3)
        if bar == 52:
            for k, e in enumerate((4, 4.5, 5, 5.5, 6, 6.5)):
                place("drums", frame_drum("slap" if k % 2 else "dum", 0.5 + 0.08 * k, variant=k, seed=SEED + 6),
                      t_of(bar, e), pan=0.05)
        # rope creaking on the long group (every other bar, every bar in the sections without the theme)
        if sec in ("I", "X") or bar % 2 == 0:
            r0, r1 = (18.0, 42.0) if bar % 3 else (40.0, 16.0)
            place("rope", rope_creak(3 * E8 + 0.25, r0, r1, SEED + 500 + bar), t_of(bar, 4) - 0.05,
                  pan=-0.5 if bar % 2 else 0.45)
        # the shrouds (A', A'')
        if sec in ("A1", "A2"):
            for k, e in enumerate((0, 4)):
                x = string_pluck(n(SHROUDS[ch][k]), 4 * E8, 0.45 * g.uniform(0.94, 1.04),
                                 seed=SEED + 30000 + 10 * bar + k, pick_pos=0.08, t60=3.0, mute=0.0, max_f=7000.0,
                                 release=0.15)
                place("shroud", x, t_of(bar, e) + 0.008, pan=0.45)
    # the dead sails (becalmed)
    for bar in range(33, 45, 2):
        ch = CHORDS[bar - 1]
        x = pad_chord([n(p) for p in SAILS[ch]], 2 * BAR + 0.3, 0.6, seed=SEED + 2000 + bar, voices=4,
                      spread_cents=14.0, attack=0.8, release=0.9, width=0.8)
        place("sails", x, t_of(bar) - 0.1)
    # the wind: 8-bar Hann windows every 4 bars (they sum to a steady wind), wrapping round the loop
    for k, bar in enumerate(range(1, BARS + 1, 4)):
        place("wind", rigging_wind(8 * BAR, SEED + 700 + k), t_of(bar), pan=0.0)
    add_theme(place, THEME_A, 9, SEED + 100, 0.8)
    add_theme(place, THEME_A1, 17, SEED + 200, 0.82)
    add_theme(place, THEME_B, 25, SEED + 300, 0.88)
    add_theme(place, THEME_A2, 45, SEED + 400, 0.86)


## Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
## flute (0 LU): drums -5, the big drum -7, the bass -6, the hull -10, the rope -11, the wind -13 (it never stops:
## eerie, not a wash), the shrouds -9, the sails -13 (the old saw pad; it only plays when becalmed).
GAINS = {"flute": 0.0, "drums": -1.0, "big": -4.8, "bass": -1.8, "hull": -7.5, "rope": -12.0, "wind": -15.7,
         "shroud": 10.2, "sails": -0.1}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=INTRO_S, loop_s=LOOP_S, intro_tail_s=6.0, preroll_s=10.0)
    mx.bus("flute", GAINS["flute"], send=0.3, process=lambda x: filt(x, [bq_highpass(200, 0.7),
                                                                         bq_peak(1900, 2.0, 1.0)]))
    mx.bus("drums", GAINS["drums"], send=0.14, process=lambda x: filt(x, [bq_highpass(32, 0.7),
                                                                          bq_lowpass(6000, 0.7)]))
    mx.bus("big", GAINS["big"], send=0.15, process=lambda x: filt(x, [bq_highpass(30, 0.7)]))
    mx.bus("bass", GAINS["bass"], send=0.04, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_peak(90, 2.0, 0.9),
                                                                        bq_lowpass(2500, 0.7)]))
    mx.bus("hull", GAINS["hull"], send=0.35, process=lambda x: filt(x, [bq_lowpass(1200, 0.7)]))
    mx.bus("rope", GAINS["rope"], send=0.3, process=lambda x: filt(x, [bq_highpass(200, 0.7)]))
    mx.bus("wind", GAINS["wind"], send=0.3, process=lambda x: filt(x, [bq_highpass(150, 0.7)]))
    mx.bus("shroud", GAINS["shroud"], send=0.4, process=lambda x: filt(x, [bq_highpass(300, 0.7)]))
    mx.bus("sails", GAINS["sails"], send=0.45, process=lambda x: string_body(x, cutoff=1400.0))
    build(mx)
    hold = ModFDNReverb(rt60=1.9, rt60_high=0.8, predelay=0.02, size=0.9, mod_depth=9.0, mod_rate=0.5,
                        early_level=0.35, lowcut=100.0, seed=SEED % 9973)
    intro, loop = mx.render(reverb=hold, reverb_return_db=-3.0)
    rep: dict = {}
    intro, loop = master_loop(intro, loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    y = np.concatenate([intro, loop])
    S, L = len(intro), len(loop)
    write_ogg(out_path, y, quality=3.0, tags={"LOOPSTART": str(S), "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, S, L, BPM, 7,
                       extra={"intro_bars": INTRO_BARS, "loop_bars": BARS, "meter": "7/8 (2+2+3)"})
    m = measure(y)
    if stats is not None:
        stats["splice_residual_db"] = mx.splice_residual_db
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"spar_wraith: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  loop {S}+{L}  splice {mx.splice_residual_db:.1f} dB  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
