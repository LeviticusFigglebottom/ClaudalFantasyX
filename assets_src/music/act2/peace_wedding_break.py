"""`peace_wedding_break`: Ch14 C2, the trap sprung in the Lacquer Court (M4-A2P-090; the cue sheet,
docs/kb/plan/act2/audio/act2_cue_sheet.md): about 25 s, the ceremony torn open.

Original composition for this project (SPEC §2, §9). Everything in it is the wedding's own: the couple's tune (from
act2/peace_wedding.py's COUPLE), the sketch's breath flute and gilded bars (its add_tune), the court's pad and frame
drum, the Stillguard's damped kettle gong on D2, and the Order's congregational tune ORDER_HUM (motifs.py), hummed.
Only the Cantors sing; ADR 0204 §10's one exception is Sefir's lullaby, not this. Nothing is taken from any
existing music.

The brief (act2_plan Ch14; the cue sheet): the ceremony at dusk on still water, then the Conclave springs the trap.
So the couple's tune starts as the vows did (E minor, tender) and breaks off on its third bar, mid-phrase, on the
damped gong. The gong's step every two beats, which in the ceremony stepped against the dance's three, is now all
there is: it wins. The Order's hum comes in loud and close, not far off across the court, over C minor. The cue ends on
a held low C with the gong stopped: the party are heretics now, and the scene's next lines are said over that drone.

G major's court, 3/4 at 88 BPM (the wedding's tempo; a bar is 2.05 s): bars 1-2 the couple's tune over E minor |
bar 3, beat 2: the break | bars 3-9 the gong every two beats, frame-drum dums, C minor, ORDER_HUM hummed by many men
| then the drone on C alone, about 6 s, settling low and held on (HOLD_S) until the scene cuts it. Not a loop. Vorbis q3, -16 LUFS integrated.

Render:  python3 tools/audio/render_all.py --only peace_wedding_break
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)

import numpy as np  # noqa: E402

from motifs import ORDER_HUM  # noqa: E402
from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PW = _mod("peace_wedding_final", os.path.join(HERE, "peace_wedding.py"))   # the final: COUPLE, the gong's pitch
S = PW.S                                                                      # the sketch: add_tune, its tempo

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "peace_wedding_break.ogg")
SEED = 20261920
TARGET_LUFS = -16.0
BEAT = S.BEAT
BAR = S.BAR
LEAD_S = 0.4                      # the file starts this long before bar 1's downbeat
BREAK = (3, 1.0)                  # bar 3, beat 2 (0-based beat 1): where the tune is cut off
GONG_FROM, GONG_TO = 3, 10        # the gong's step, every two beats, from the break to bar 10
DRONE_S = 6.5
# The low C held on under the declarations until Asha's "No." cuts it dead (`@music silence fade=0.0`): the scene runs
# about 12 s past the drone's 6.5 s (act1_playthrough.py --act 2), and the direction notes' holds and pauses add more,
# so it holds HOLD_S longer, settled HOLD_DB down (under the loudness gate, so the cue's -16 LUFS doesn't move).
HOLD_S = 18.0
HOLD_DB = -12.0
GAINS = {"flute": 0.0, "bars": -2.0, "pad": -2.0, "drum": -6.0, "gong": -4.0, "hum": 3.0, "drone": -6.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return LEAD_S + (bar - 1) * BAR + beat * BEAT


class _Shift:
    """add_tune writes at the sketch's own bar times; this shifts it onto this cue's (its lead-in)."""

    def __init__(self, mx: Mixer, until: float):
        self.mx, self.until = mx, until

    def add(self, bus: str, x, start: float, **kw) -> None:
        start += LEAD_S
        if start < self.until:                    # the break: nothing the tune would play after it sounds
            keep = int(max(0.0, self.until - start) * SR)
            x = x[:keep].copy()
            k = min(len(x), int(0.04 * SR))
            if k:
                x[-k:] *= np.linspace(1, 0, k)[:, None] if x.ndim == 2 else np.linspace(1, 0, k)
            self.mx.add(bus, x, start, **kw)


def build(mx: Mixer) -> None:
    g = rng(SEED)
    cut = t_of(*BREAK)
    # bars 1-2 (and the start of 3): the couple's tune as the vows had it, over E minor, then cut off
    S.add_tune(_Shift(mx, cut), PW.COUPLE[:3], 1, SEED + 10, 0.47, gilded=True)
    for bar in (1, 2):
        mx.add("pad", pad_chord([n(p) - 12 for p in PW.PAD["Em"].split()], BAR * 0.98, 0.42, seed=SEED + 20 + bar,
                                attack=0.8, release=1.2), t_of(bar) - 0.2)
        mx.add("drum", frame_drum("dum", 0.45, variant=bar, seed=SEED + 30), t_of(bar), pan=-0.1)
        mx.add("drum", frame_drum("tek", 0.25, variant=bar, seed=SEED + 31), t_of(bar, 2), pan=0.2)
    pad3 = pad_chord([n(p) - 12 for p in PW.PAD["Em"].split()], BAR * 0.8, 0.42, seed=SEED + 23, attack=0.8,
                     release=0.25)
    mx.add("pad", pad3[: int((cut - t_of(3) + 0.2) * SR)], t_of(3) - 0.2)
    # the break: the gong struck hard, a big drum under it, and C minor
    mx.add("gong", kettle_gong(n("D2"), 0.7, seed=SEED + 40, t60=2.2), cut)
    mx.add("drum", big_drum(0.8, variant=0, seed=SEED + 41), cut)
    cm = pad_chord([n("C3"), n("Eb3"), n("G3"), n("C4")], (GONG_TO - BREAK[0]) * BAR, 0.5, seed=SEED + 42, attack=0.5,
                   release=2.0)
    mx.add("pad", cm, cut + 0.05)
    # the gong's step, every two beats, now with nothing to step against; a frame-drum dum under each
    k = 1
    while cut + 2 * k * BEAT < t_of(GONG_TO):
        t = cut + 2 * k * BEAT
        mx.add("gong", kettle_gong(n("D2"), 0.45 * float(g.uniform(0.9, 1.05)), seed=SEED + 50 + k, t60=1.4,
                                   damp_at=0.55), t + float(g.normal(0, 0.003)), pan=-0.3)
        mx.add("drum", frame_drum("dum", 0.5 * float(g.uniform(0.9, 1.05)), variant=k % 3, seed=SEED + 32), t, pan=0.1)
        k += 1
    # the Order's hum, close and loud: ORDER_HUM's opening notes at the court's pulse (a note a beat or two)
    line = [(float(m), b * BEAT) for m, b in ORDER_HUM[:6]]
    mx.add("hum", hum_ensemble(line, voices=18, seed=SEED + 60, register="low", spread=0.7), cut + BEAT)
    # the end: a held low C, alone, fading; the scene's lines go over it
    t_drone = t_of(GONG_TO)
    drone = pad_chord([n("C2"), n("G2"), n("C3")], DRONE_S + HOLD_S, 0.5, seed=SEED + 70, attack=1.5, release=1.5)
    t = np.arange(len(drone)) / SR
    held = 10 ** (HOLD_DB / 20)                  # past the drone's own length it settles to the held level
    env = np.where(t < DRONE_S - 2.5, 1.0, held + (1.0 - held) * np.exp(-np.maximum(t - (DRONE_S - 2.5), 0.0) / 1.2))
    drone *= env[:, None]
    k = int(2.5 * SR)
    drone[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    mx.add("drone", drone, t_drone - 1.0)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = Mixer(t_of(GONG_TO) + DRONE_S + HOLD_S + 6.0)
    flute_eq = lambda x: filt(x, [bq_highpass(200, 0.7), bq_peak(1500, 1.0, 1.0), bq_lowpass(7000, 0.7)])  # noqa
    mx.bus("flute", GAINS["flute"], send=0.32, process=flute_eq)
    mx.bus("bars", GAINS["bars"], send=0.5, process=lambda x: filt(x, [bq_lowpass(6500, 0.7)]))
    mx.bus("pad", GAINS["pad"], send=0.45, process=lambda x: string_body(x, cutoff=1600.0))
    mx.bus("drum", GAINS["drum"], send=0.2)
    mx.bus("gong", GAINS["gong"], send=0.35, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
    mx.bus("hum", GAINS["hum"], send=0.4, process=lambda x: filt(x, [bq_lowpass(2400, 0.7)]))
    mx.bus("drone", GAINS["drone"], send=0.5, process=lambda x: string_body(x, cutoff=900.0))
    build(mx)
    court = ModFDNReverb(rt60=2.8, rt60_high=1.2, predelay=0.03, size=1.2, mod_depth=8.0, mod_rate=0.4,
                         early_level=0.3, lowcut=100.0, seed=SEED % 9973)
    bus_lufs = {name: integrated_lufs((b.process(b.buf) if b.process else b.buf) * 10 ** (b.gain_db / 20))
                for name, b in mx.buses.items()}
    master = mx.render(reverb=court, reverb_return_db=-2.0)
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(1.5 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, master, quality=3.0)
    m = measure(master)
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
    if verbose:
        print(f"peace_wedding_break: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
