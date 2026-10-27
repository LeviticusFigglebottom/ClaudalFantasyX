"""`kerrid_stair`: Kerrid's walking motif, its first statement (M3-AUD-821; act1_ch05.md B05 close, §6), ~19 s.

Original composition for this project (SPEC §2, §9). The motif is motifs.py KERRID_STAIR (written for this project:
a bowed two-note figure, D3 falling a fourth to A2, one note a stride); it quotes and derives from no existing melody.
The brief: "Motif, first statement (<= 20 s). A slow walking rhythm: low frame drum and a bowed two-note figure,
heavy, patient. This is the motif that slows to a stop as goodbye_kerrid later. Here it starts, steady, as he falls
in." Kerrid has just joined the line, last, as on a stair; he says nothing.

Played when the party starts back up the terraces (ch05_lanternfall_weir.dlg, `@music kerrid_stair fade=2.0`), over
lanternfall's last drum. Through-composed, not looped: it plays once and rings out under Rhen's line.

Layers (all synthesized; no samples):
* the tread: a large, low frame drum on every beat, the first of each pair heavier (a step, then the weight coming
  onto it), at KERRID_STAIR_BPM (48) exactly: the drum is not humanized beyond 4 ms, because he isn't;
* the figure: a low bowed string (a sawtooth Helmholtz motion with bow noise and a slow-speaking, heavy attack
  through a cello-like body) plays D3 then A2, each two beats, a second string an octave below joining from the
  second statement, so the figure grows heavier without getting louder in the treble;
* nothing else: no harmony is stated, so E3's goodbye_kerrid can put any chord under the same two notes.

Form (a beat is 1.25 s, a stride two beats): two steps of the drum alone (he falls in) | the figure three times over
the drum, D A D A D A, the last A held | the drum walks on to its fourteenth step and stops; the strings ring out.

Render:  python3 assets_src/music/kerrid_stair.py   (or tools/audio/render_all.py --only kerrid_stair)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

from motifs import KERRID_STAIR, KERRID_STAIR_BPM, KERRID_STAIR_STRIDE  # noqa: E402
from synth.drums import frame_drum  # noqa: E402
from synth.dsp import (SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, midi_to_hz,  # noqa: E402
                       polyblep_saw, rng, smooth_noise)
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "kerrid_stair.ogg")
SEED = 20261821
TARGET_LUFS = -16.0
BPM = KERRID_STAIR_BPM
BEAT = 60.0 / BPM
BAR = 4 * BEAT
LEAD_IN = 0.15          # the first step lands this long after the file starts
STEPS = 14             # the drum's steps (beats); it stops after the last
FIGURE_FROM = 2        # the figure enters on the third step
## a bowed note speaks slowly: placed this much early so its weight arrives on the step
BOW_PRE = 0.12


def bowed(m: float, dur: float, vel: float, seed: int, attack: float = 0.28, release: float = 0.9) -> np.ndarray:
    """A low bowed string: a band-limited sawtooth (the Helmholtz motion) whose bow pressure swells in, with bow
    noise riding the stick-slip, a slow, narrow vibrato that starts late, and a heavy 'dig' at the start of the
    stroke. Mono, dry (the body is the bus filter)."""
    g = rng(seed)
    f0 = midi_to_hz(m)
    N = int((dur + 4 * release + 0.05) * SR)
    t = np.arange(N) / SR
    P = np.clip(t / attack, 0, 1) ** 1.6 * np.where(t > dur, np.exp(-(t - dur) / (release / 2.5)), 1.0)
    P *= 1.0 + 0.06 * smooth_noise(N, 2.2, g)
    dig = 1.0 + 0.5 * np.exp(-t / 0.08) * np.clip(t / 0.02, 0, 1)
    vib = 7.0 * np.clip((t - 0.9) / 1.2, 0, 1) * np.sin(2 * np.pi * 4.6 * t + g.uniform(0, 6.28))
    cents = vib + 3.0 * smooth_noise(N, 0.8, g) - 10.0 * np.exp(-t / 0.07)
    freq = f0 * 2 ** (cents / 1200.0)
    saw = polyblep_saw(freq, SR, float(g.random()))
    tone = filt(saw, [bq_lowpass(900.0 + 1800.0 * vel, 0.7)]) * (P * dig) ** 1.15
    noise = filt(g.standard_normal(N), [bq_bandpass(2.5 * f0 + 700.0, 0.9)]) * P * (0.10 + 0.35 * np.exp(-t / 0.1))
    out = tone + noise * 0.25
    k = int(0.01 * SR)
    out[-k:] *= np.linspace(1, 0, k)
    return 0.3 * vel * out


def cello_body(x: np.ndarray) -> np.ndarray:
    """A large bowed instrument's body: the air and wood resonances (about 100, 210, 580 Hz), a bridge hill near
    2.3 kHz, and the top rolled off."""
    return filt(x, [bq_highpass(45, 0.7), bq_peak(105, 4.0, 2.0), bq_peak(210, 3.5, 1.6), bq_peak(580, 3.0, 1.4),
                    bq_peak(2300, 2.0, 1.2), bq_lowpass(4200, 0.7)])


def t_of(beat: float) -> float:
    return LEAD_IN + beat * BEAT


# Bus gains from measured bus loudness (render(stats=...)["bus_lufs"]): the bowed figure at L, the tread L-3 (it is
# the walking rhythm, so it sits close under the strings), the low octave L-7.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    length = t_of(STEPS) + 2.3
    mx = Mixer(length + 4.0)
    mx.bus("bow", 0.0, send=0.30, process=cello_body)
    mx.bus("bow_low", -3.5, send=0.25, process=cello_body)
    mx.bus("drum", 7.2, send=0.22, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(2200, 0.7)]))
    # the tread: a step on every beat, the first of each pair heavier; the last one a little softer (he stops)
    for i in range(STEPS):
        heavy = i % 2 == 0
        v = (0.62 if heavy else 0.40) * (0.85 if i == STEPS - 1 else 1.0) * g.uniform(0.96, 1.03)
        mx.add("drum", frame_drum("dum", v, variant=i, size=1.7, seed=SEED + 1), t_of(i) + float(g.normal(0, 0.004)),
               pan=-0.06)
    # the figure: D then A, a stride each, from the third step; three times, the last A held
    (m_hi, _), (m_lo, _) = KERRID_STAIR
    stride = KERRID_STAIR_STRIDE * BEAT
    strokes = [(m_hi, 1.0), (m_lo, 1.0)] * 2 + [(m_hi, 1.0), (m_lo, 1.6)]
    for i, (m, hold) in enumerate(strokes):
        at = t_of(FIGURE_FROM + i * KERRID_STAIR_STRIDE)
        d = stride * hold - 0.08
        v = (0.78 if m == m_hi else 0.72) * g.uniform(0.97, 1.02) * (0.94 if i == len(strokes) - 1 else 1.0)
        mx.add("bow", bowed(m, d, v, SEED + 100 + i), at - BOW_PRE, pan=0.08)
        if i >= 2:      # the second string an octave down, from the second statement
            mx.add("bow_low", bowed(m - 12, d, v * 0.9, SEED + 200 + i, attack=0.35), at - BOW_PRE + 0.02, pan=-0.1)
    hall = ModFDNReverb(rt60=2.8, rt60_high=1.1, predelay=0.03, size=1.1, mod_depth=8.0, mod_rate=0.45,
                        early_level=0.22, lowcut=70.0, seed=SEED % 9973)
    y = mx.render(reverb=hall, reverb_return_db=-3.0)[: int(length * SR)]
    k = int(2.0 * SR)
    y[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, y, quality=3.0)
    m = measure(y)
    if stats is not None:
        stats["bus_lufs"] = {name: _bus_lufs(mx, name) for name in ("bow", "bow_low", "drum")}
    if verbose:
        print(f"kerrid_stair: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


def _bus_lufs(mx: Mixer, name: str) -> float:
    """One bus's integrated loudness after its fader and processing (for setting the gains above)."""
    b = mx.buses[name]
    x = b.process(b.buf) if b.process else b.buf
    return integrated_lufs(db_to_lin(b.gain_db) * x)


if __name__ == "__main__":
    st: dict = {}
    render(stats=st)
    print("  buses", {k: round(v, 1) for k, v in st["bus_lufs"].items()})
