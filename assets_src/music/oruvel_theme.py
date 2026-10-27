"""`oruvel_theme`: Ch7 B09, "The Empty Moorings" (M3-AUD-820; act1_ch07.md §6), ~60 s, through-composed reprise.

Original composition for this project (SPEC §2). It is a reprise of our own material: Ch1's Oruvel town theme
(oruvel.py `TUNE_A` and the tag's head, `TAG`), imported from oruvel.py and never retyped, played by one flute over
the hum of the Tamsule Bell (tamsule_bell_galleries.py: the same bell, prime `BELL_PRIME` A2, and the same partial
ratios, `DRONE`). Nothing here is derived from any existing tune.

The brief: "Ch1's Oruvel town theme, stripped to one flute, over bell_hum (the Tamsule Bell's hum)." Under the Bell's
skirt, six empty iron rings where Oruvel's boats tied up; Tavi names the boats, Rhen names the people, Asha says each
name back; Rhen says "Pio" for the ring Tavi can't name. No song (Cantors sing only the Hush).

So the harbour dance is gone: no squeezebox, no left hand, no drum, no swing. One breath flute plays the tune's eight
bars straight and slowly, then the tag's head once more, and stops on its third. The tune is moved up a tone, from G
to A, so that it sits on the Bell (its prime is A): the town's tune, in the Bell's key, among the moorings. **The bell
hum** is the sound of bound glimmer as the Ch7 sheet defines it, "a steady tone with no breath and no beating": the
Bell's partials (hum, prime, quint, nominal, and its major third, the deciem, louder than its minor tierce, so A
mixolydian sits on it), each a single sine at a constant level, faded in and out and never moving. It is the
galleries' drone with the life taken out of it.

A mixolydian, 4/4 at 63 BPM (a bar is 3.81 s), straight eighths, a little time at each phrase end:
0-5 s the hum alone | bars 1-8 TUNE_A (Oruvel's A section), the flute | a half-bar's breath | bars 9-12 the tag's
head (Oruvel bars 29-32), ending on C# (the tune's third) | the hum alone, fading.

Render:  python3 assets_src/music/oruvel_theme.py   (or tools/audio/render_all.py --only oruvel_theme)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng  # noqa: E402
from synth.mixer import Mixer  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ORUVEL = _mod("oruvel")
BELL = _mod("tamsule_bell_galleries")
HFV = _mod("hush_first_verse")
HUSH = _mod("hush_theme_v2")

OUT = os.path.join(ROOT, "assets", "audio", "music", "oruvel_theme.ogg")
SEED = 20261723
BPM = 63.0
BEAT = 60.0 / BPM
EIGHTH = BEAT / 2
BAR = 4 * BEAT
T0 = 5.0                 # the hum alone before the flute
FLUTE_PRE = 0.065
UP = 2                   # Oruvel's G, up a tone to the Bell's A
BREATH_BARS = 0.5        # between the tune and the tag
# The steady hum's levels by partial name (tamsule_bell_galleries.DRONE gives the ratios): the deciem (major third)
# over the tierce (minor third), so the hum carries A mixolydian; no doublets, no LFO, no breathing.
HUM_LEVEL = {"hum": 1.0, "prime": 0.55, "tierce": 0.08, "quint": 0.22, "nominal": 0.30, "deciem": 0.30}
# A little time at each phrase's end (bar index in the flute's 12 bars, 1-based).
STRETCH = {4: 1.08, 8: 1.12, 12: 1.2}


def bar_start(bar: int) -> float:
    t = T0
    for b in range(1, bar):
        t += BAR * STRETCH.get(b, 1.0) + (BREATH_BARS * BAR if b == 8 else 0.0)
    return t


def flute_line() -> list[tuple[float, float, float]]:
    """[(t, dur, midi)]: TUNE_A then the tag's head, straight eighths."""
    out = []
    for i, bar in enumerate(ORUVEL.TUNE_A + ORUVEL.TAG, start=1):
        pos = 0
        k = STRETCH.get(i, 1.0)
        for p, e in bar:
            if p is not None:
                out.append((bar_start(i) + pos * EIGHTH * k, e * EIGHTH * k, n(p) + UP))
            pos += e
    return out


def bell_hum(length: float, seed: int) -> np.ndarray:
    """The Tamsule Bell's hum as bound glimmer: its partials, steady sines, faded in over 4 s and out over 6 s."""
    g = rng(seed)
    N = int(length * SR)
    t = np.arange(N) / SR
    f1 = midi_to_hz(n(BELL.BELL_PRIME))
    out = np.zeros((N, 2))
    for name, r, _, _ in BELL.DRONE:
        for ch in range(2):
            out[:, ch] += HUM_LEVEL[name] * np.sin(2 * np.pi * f1 * r * t + g.uniform(0, 2 * np.pi))
    env = np.clip(t / 4.0, 0, 1) ** 2 * np.clip((length - t) / 6.0, 0, 1) ** 2
    return out * env[:, None] / np.abs(out).max()


def flute_bus(x: np.ndarray) -> np.ndarray:
    return filt(x, [bq_highpass(180, 0.7), bq_peak(1600, 1.0, 1.0), bq_lowpass(6500, 0.7)])


# Bus gains from measured bus loudness (render(stats=...)): the flute at L, the hum L-8 (the galleries' drone level).
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    line = flute_line()
    end = line[-1][0] + line[-1][1]
    length = end + 9.0
    mx = Mixer(length + 4.0)
    mx.bus("flute", 0.0, send=0.38, process=flute_bus)
    mx.bus("hum", -23.8, send=0.30, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    mx.add("hum", bell_hum(length, SEED + 3), 0.0)
    prev_end = -10.0
    for i, (t0, d, m) in enumerate(line):
        first = t0 - prev_end > 0.15
        long = d >= 2 * EIGHTH - 1e-6
        x = breath_flute(m, d * 0.97 + 0.03, 0.48 * g.uniform(0.95, 1.04) * (1.04 if long else 1.0),
                         seed=SEED + 41 * i, breath=0.45, scoop_cents=35.0 if first else 10.0,
                         vib_cents=9.0 if d > 1.5 * BEAT else 3.0, vib_rate=4.5, swell=0.25 if d > 1.5 * BEAT else 0.0,
                         attack=0.09 if first else 0.05, release=0.5, beta=0.52)
        mx.add("flute", x, t0 - FLUTE_PRE + float(g.normal(0, 0.006)), pan=-0.1)
        prev_end = t0 + d
    hall = ModFDNReverb(rt60=4.0, rt60_high=1.5, predelay=0.045, size=1.3, mod_depth=9.0, mod_rate=0.4,
                        early_level=0.3, lowcut=90.0, seed=SEED % 9973)       # under the Bell's bronze skirt
    st: dict = {}
    HUSH._bus_stats(mx, st)
    if stats is not None:
        stats.update(st)
    m = HFV._finish(mx, hall, out_path, 3.5)
    if verbose:
        print("  buses", {k: round(v, 1) for k, v in st.items()})
        print(f"oruvel_theme: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


if __name__ == "__main__":
    render()
