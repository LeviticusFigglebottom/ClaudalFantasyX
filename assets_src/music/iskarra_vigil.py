"""`iskarra_vigil`: the Act I break (M3-AUD-12; act_outline.md, the end of Ch9): about 90 s, through-composed.

Original composition for this project (SPEC §2): built from our own Hush theme (hush_theme_v2.py, MEL_A, its first
phrase), not from any existing melody. After the Ebbing and Kerrid's "Somebody's still below", the story cuts back to
the prologue's frame: the Iskarra Ruins at dusk, the party keeping their apart vigil on the broken plaza, the sea
glowing faintly with drowned motes, Rhen's wick the only flame. Rhen speaks one or two lines in voice-over.

This is a **bed for a voice**, so the cue leaves the voice's band (about 300 Hz to 3 kHz) to the voice. Everything
it plays lives below or above it, and a wide cut centred on 1 kHz on the master takes out what leaks:
* **below** (under 300 Hz): the sea, a low drone on A (A1, E2, A2) that breathes, a slow swell of deep water, and the
  Hush theme's first phrase (MEL_A) **two octaves down**, on low strings played sul tasto and filtered dark: the theme
  sounding from under the water, because somebody is still below. Three deep piano octaves, filtered as if heard
  through the sea, mark the start, the phrase's end and the close;
* **above** (over 3 kHz): glass motes that **rise** (the prologue's glimmer rises around Rhen; at the Ebbing the motes
  only ever fell), a faint high halo of glass tones that beat slowly, and once, at the phrase's end, the Hush's
  first cell in the glass, the theme above answering the theme below.

So the voice sits in a hollow between the deep and the high, and the music never competes with a word.

Timeline (s): 0-10 the drone breathes in, the first piano octave (A) | 10-16 the first motes rise | 16-55 MEL_A in
the deep (slow; the motes every few seconds; the halo) | 55-64 the piano's low E, the glass answers with the Hush's
first cell | 64-80 the drone alone with the motes, thinning | 80 the last piano octave, A with its fifth, and one
last rising figure left open on B; the drone fades by 93.

Render:  python3 assets_src/music/iskarra_vigil.py   (or tools/audio/render_all.py --only iskarra_vigil)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng, smooth_noise  # noqa: E402
from synth.grand import PianoBody  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.performance import plan_pedal  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HUSH = _mod("hush_theme_v2")
HFV = _mod("hush_first_verse")

OUT = os.path.join(ROOT, "assets", "audio", "music", "iskarra_vigil.ogg")
SEED = 20261224
TARGET_LUFS = -16.0
LENGTH_S = 93.0
FADE_S = 9.0              # the drone's fade at the end
BEAT = 1.6                # one beat of MEL_A in the deep (s): very slow
LINE_T0 = 16.0
DEEP_SHIFT = -24          # MEL_A two octaves down
VOICE_BAND = (300.0, 3000.0)
BAND_CUT = (1000.0, -9.0, 0.45)    # master: centre Hz, gain dB, Q (about 360 Hz to 2.8 kHz at half the cut)
LOW_LP = 300.0            # every low layer stays under this
HIGH_HP = 2600.0          # every high layer stays over this
RISE = ["E7", "G7", "A7", "C8"]                  # the motes' figure: always upward
RISE_LAST = ["E7", "A7", "B7"]                   # the last one, left open
CELL = ["E8", "D8", "C8", "A7"]                  # the Hush's first cell (MEL_A: E D C | A), in the glass
MOTES_AT = [10.5, 15.0, 22.0, 29.5, 36.0, 43.5, 50.0, 70.0, 75.5]
HALO = [("E7", 1.0), ("A7", 0.7), ("B7", 0.45)]


def low_band(x: np.ndarray) -> np.ndarray:
    return filt(x, [bq_highpass(35, 0.7), bq_lowpass(LOW_LP, 0.6), bq_lowpass(LOW_LP * 1.25, 0.7)])


def high_band(x: np.ndarray) -> np.ndarray:
    return filt(x, [bq_highpass(HIGH_HP, 0.6), bq_highpass(HIGH_HP * 0.9, 0.7), bq_lowpass(11000, 0.7)])


def sea_drone(length: float, g, sr: int = SR) -> np.ndarray:
    """A on the sea: A1, E2 and A2 (each a detuned pair with a few harmonics) breathing on a 13 s cycle. Stereo."""
    N = int(length * sr)
    t = np.arange(N) / sr
    out = np.zeros((N, 2))
    breath = 0.5 - 0.5 * np.cos(2 * np.pi * t / 13.0)
    for root, lvl in ((n("A1"), 1.0), (n("E2"), 0.55), (n("A2"), 0.35)):
        f0 = midi_to_hz(root)
        for k, a in ((1, 1.0), (2, 0.5), (3, 0.22), (4, 0.1)):
            for side, det in ((0, 0.0), (1, 0.07 + 0.03 * k)):
                s = lvl * a * (0.75 + 0.25 * breath) * np.sin(2 * np.pi * (f0 * k + det) * t + g.uniform(0, 6.28))
                out[:, side] += s
                out[:, 1 - side] += 0.55 * s
    env = np.clip(t / 8.0, 0, 1) ** 2 * np.clip((length - t) / FADE_S, 0, 1) ** 2
    return out * env[:, None] * 0.05


def deep_water(length: float, g, sr: int = SR) -> np.ndarray:
    """A slow swell of deep water: noise under 180 Hz, rising and falling like a long wave on drowned stone."""
    N = int(length * sr)
    t = np.arange(N) / sr
    x = np.stack([filt(g.standard_normal(N), [bq_lowpass(180, 0.7), bq_lowpass(220, 0.7), bq_highpass(30, 0.7)])
                  for _ in range(2)], axis=1)
    swell = (0.35 + 0.65 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 9.5)) ** 2) * (1 + 0.2 * smooth_noise(N, 0.2, g, sr))
    env = np.clip(t / 10.0, 0, 1) ** 2 * np.clip((length - t) / FADE_S, 0, 1) ** 2
    return x * (swell * env)[:, None] * 0.02


def halo(t0: float, t1: float, g, sr: int = SR) -> np.ndarray:
    """A faint high halo of glass tones (each a slowly beating pair) that swells in and out. Stereo, t1 - t0 long."""
    N = int((t1 - t0) * sr)
    t = np.arange(N) / sr
    out = np.zeros((N, 2))
    for k, (p, lvl) in enumerate(HALO):
        f0 = midi_to_hz(n(p))
        sw = 0.5 - 0.5 * np.cos(2 * np.pi * t / (11.0 + 3.0 * k) + g.uniform(0, 6.28))
        s = lvl * sw * (np.sin(2 * np.pi * f0 * t + g.uniform(0, 6.28))
                        + 0.8 * np.sin(2 * np.pi * (f0 + 0.4 + 0.25 * k) * t + g.uniform(0, 6.28)))
        out[:, k % 2] += s
        out[:, 1 - k % 2] += 0.5 * s
    env = np.clip(t / 6.0, 0, 1) ** 2 * np.clip((t[-1] - t) / 6.0, 0, 1) ** 2
    return out * env[:, None] * 0.02


def deep_line() -> list[tuple[float, float, int, float]]:
    """MEL_A two octaves down, from LINE_T0: [(t, dur, midi, vel)]; each line's last note leans a little long."""
    out, pos = [], LINE_T0
    for i, (p, beats, v) in enumerate(HUSH.MEL_A):
        d = beats * BEAT * (1.1 if beats >= 2 else 1.0)
        out.append((pos, d, n(p) + DEEP_SHIFT, v))
        pos += d
    return out


# Bus gains from measured bus loudness (hush_theme_v2._bus_stats, gated integrated per bus): the deep line (MEL_A) at
# L; the sea drone L-2 (the bed itself); the deep water L-9; the piano octaves L-3 where they sound (its raw level is
# about 31 dB under the breath flute's, and under the low-pass it loses most of its partials, hence the large gain);
# the rising motes L-2 and the halo L-8 (the only layers over the voice's band, so they carry the bed's air).
# Measured on the decoded file: the 300 Hz-3 kHz band is about 24 LU under the whole cue (render(stats=...)
# also reports its share of the spectrum's energy).
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    line = deep_line()
    line_end = line[-1][0] + line[-1][1]
    # three deep piano octaves: A at the start, E at the phrase's end, A with its fifth at the close
    close_t = 80.0
    piano = ([dict(m=n(p), vel=0.42 - 0.04 * j, t0=1.0 + 0.05 * j, key_up=9.0, role="bass")
              for j, p in enumerate(["A0", "A1"])]
             + [dict(m=n(p), vel=0.36 - 0.04 * j, t0=line_end - 1.0 + 0.05 * j, key_up=8.0, role="bass")
                for j, p in enumerate(["E1", "E2"])]
             + [dict(m=n(p), vel=0.4 - 0.04 * j, t0=close_t + 0.07 * j, key_up=10.0, role="bass")
                for j, p in enumerate(["A0", "A1", "E2"])])
    pedal = plan_pedal([line_end - 1.0, close_t], start=1.0, end_release=close_t + 8.0, release_len=4.0, g=g)
    body = PianoBody(pedal)
    mx = Mixer(LENGTH_S)
    mx.bus("deep", 0.0, send=0.3, process=low_band)
    mx.bus("drone", -8.0, send=0.2, process=low_band)
    mx.bus("water", 19.2, send=0.15, process=low_band)
    mx.bus("piano", 15.8, send=0.25, process=lambda x: low_band(body(x)))
    mx.bus("motes", -1.9, send=0.55, process=high_band)
    mx.bus("halo", -3.7, send=0.4, process=high_band)
    mx.add("drone", sea_drone(LENGTH_S - 0.5, rng(SEED + 1)), 0.0)
    mx.add("water", deep_water(LENGTH_S - 0.5, rng(SEED + 2)), 0.0)
    mx.add("halo", halo(14.0, 84.0, rng(SEED + 3)), 14.0)
    for i, (t0, d, m, v) in enumerate(line):            # the deep line: low strings, legato, sul tasto
        x = pad_chord([m], d + 0.25, vel=0.5 + 0.6 * v, seed=SEED + 100 + i, voices=4, spread_cents=7.0,
                      attack=min(0.6, 0.4 * d), release=1.4, width=0.5)
        mx.add("deep", x, t0 - 0.1)
    for nt, x in zip(piano, render_jobs(HFV._piano_jobs(piano, pedal, SEED + 5))):
        mx.add("piano", x, nt["t0"], pan=-0.1)
    for k, t in enumerate(MOTES_AT):                     # the motes rise
        fig = RISE if k % 3 != 2 else RISE[:3]
        for j, p in enumerate(fig):
            x = metallophone_note(n(p), 0.2 + 0.03 * j, seed=SEED + 500 + 10 * k + j, decay=4.0, hardness=0.2,
                                  ombak_hz=3.5)
            mx.add("motes", x, t + 0.28 * j + float(g.normal(0, 0.01)), pan=-0.5 + 0.33 * j)
    for j, p in enumerate(CELL):                         # the theme above answers the theme below
        x = metallophone_note(n(p), 0.24, seed=SEED + 700 + j, decay=4.5, hardness=0.18, ombak_hz=3.0)
        mx.add("motes", x, line_end + 1.5 + (0.0, 1.2, 1.6, 2.0)[j] * 1.4, pan=0.35)
    for j, p in enumerate(RISE_LAST):                    # the last figure, left open on B
        x = metallophone_note(n(p), 0.22, seed=SEED + 800 + j, decay=5.0, hardness=0.18, ombak_hz=3.0)
        mx.add("motes", x, close_t + 2.5 + 0.45 * j, pan=-0.3 + 0.3 * j)
    hall = ModFDNReverb(rt60=3.8, rt60_high=1.6, predelay=0.035, size=1.25, mod_depth=9.0, mod_rate=0.4,
                        early_level=0.18, lowcut=40.0, seed=SEED % 9973)
    st: dict = {}
    HUSH._bus_stats(mx, st)
    master = mx.render(reverb=hall, reverb_return_db=-2.0)
    f, gdb, q = BAND_CUT
    master = filt(master, [bq_peak(f, gdb, q)])
    k = int(2.0 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, master, quality=3.0)
    m = measure(master)
    spec = np.abs(np.fft.rfft(master.mean(axis=1))) ** 2
    fr = np.fft.rfftfreq(len(master), 1.0 / SR)
    band = (fr >= VOICE_BAND[0]) & (fr <= VOICE_BAND[1])
    st["voice_band_energy_pct"] = float(100 * spec[band].sum() / spec.sum())
    st["voice_band_pct_of_above_300"] = float(100 * spec[band].sum() / spec[fr >= VOICE_BAND[0]].sum())
    if stats is not None:
        stats.update(st)
    if verbose:
        print("  buses", {k_: round(v, 1) for k_, v in st.items()})
        print(f"iskarra_vigil: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
