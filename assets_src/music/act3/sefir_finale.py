"""`sefir_warden` and `sefir_heart`: Ch21 H04–H06, Sefir's first two phases (M5-A3P-1951; act3_ending.md H04–H06;
ADR 0208). Both loop.

Original composition for this project (SPEC §2). Their tunes are the game's own, loaded and never retyped:
* Sefir's motif (sefir_theme.py `MOTIF`: G4 C5 D5 E5 D5, slipping a half step to C#5, held): the leading tone that
  never leads;
* the Order's congregational tune (motifs.py `ORDER_HUM`), hummed.
The ostinati, the percussion and the harmony were written for these cues.

**sefir_warden** (H04, phase 1, a loop of 16 bars of 4/4 at 52 BPM, about 74 s). The brief: "a hummed congregation
over strings, beautiful and airless (the Order hums)." He buffs, delays and "settles" the timeline, warmly and
reasonably, and never moves his feet. So:
* C major, the Order's pure key, the only key his music is ever in;
* the congregation hums ORDER_HUM three times a loop, close and many, at ORDER_HUM_BPM;
* the strings play close, dark chords (C | F | Am | G), and twice a loop his motif in the violins, ending on the held
  C# over F;
* soft low bells strike C on the downbeats, and C# under the held C# (sefir_theme's 5/4 bells, here in his calm
  four);
* *airless*: a small, dead room (rt60 0.8 s), no breath noise in the voices, the top rolled off above 4 kHz. It is
  beautiful and nothing in it moves the air.

**sefir_heart** (H05–H06, phase 2, a loop of 32 bars of 7/8 (2+2+3) at 132 BPM in eighths, about 51 s). The brief:
"the storm's own note under rock-fusion percussion." Sefir has reached past Dace into Imra's light and drawn the
heart into himself. The storm's own note is the heart's A (heart.py's drone: A1, the A everything sank toward). So:
* the storm's note: a huge low throat-note on A (formant voices, many, on "o" opening to "a"), swelling and
  falling a quarter tone every four bars, over a sub A;
* rock-fusion percussion in 2+2+3: a big drum on each group's first beat, a slap backbeat on the 3 and the 5, ghost
  strokes between, a tom run into every eighth bar;
* low strings in eighths on A with the Phrygian B-flat (A A Bb A C A G A), driving;
* his motif returns in the high strings, and now its C# doesn't hang: it is the major third of the storm's A. The
  leading tone that never led has found the one chord it belongs to, and it is the Undertow's. He has become the
  storm.

Render:  python3 assets_src/music/act3/sefir_finale.py   (both; or tools/audio/render_all.py --only sefir_finale)
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
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from motifs import ORDER_HUM, ORDER_HUM_BPM  # noqa: E402
from synth.bells import tower_bell  # noqa: E402
from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble, sing  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SEFIR = _load("sefir_theme")
OUT_DIR = os.path.join(ROOT, "assets", "audio", "act3", "music")
OUT = os.path.join(OUT_DIR, "sefir_warden.ogg")
OUT_HEART = os.path.join(OUT_DIR, "sefir_heart.ogg")
SEED = 20261035
TARGET_LUFS = -16.0

# --- the Warden: 4/4 at the Order's own tempo
W_BPM = ORDER_HUM_BPM
W_BEAT = 60.0 / W_BPM
W_BAR = 4 * W_BEAT
W_BARS = 16
W_LOOP = W_BARS * W_BAR
W_CHORDS = ["C3 G3 E4", "C3 G3 E4", "F2 C3 A3", "F2 C3 A3", "A2 E3 C4", "F2 C3 A3", "G2 D3 B3", "C3 G3 E4",
            "C3 G3 E4", "C3 G3 E4", "F2 C3 A3", "F2 C3 A3", "A2 E3 C4", "D3 A3 F4", "F2 C3 A3", "F2 C3 A3"]
W_MOTIF_BARS = (1, 9)        # his motif (16 beats) from these bars; its C# lands on the F bars
W_HUM_BEATS = (0.0, 21.0, 42.0)
# From measured bus loudness: the congregation at L, the strings L-3, the motif L-4, the bells L-9.
W_GAINS = {"hum": 0.0, "strings": 6.6, "motif": 4.9, "bells": -4.5}

# --- the heart: 7/8 (2+2+3) in eighths
H_EIGHTH = 60.0 / 132.0 / 2.0
H_BAR = 7 * H_EIGHTH
H_BARS = 32
H_LOOP = H_BARS * H_BAR
H_RIFF = ["A1", "A1", "A#1", "A1", "C2", "A1", "G1"]          # one note an eighth: A A Bb A C A G
H_MOTIF_BARS = (8, 24)
# From measured bus loudness: the big drum at L, the kit L-1, the storm's note L-2, the riff L-4, the motif L-5,
# the sub L-8.
H_GAINS = {"kick": 0.0, "kit": 1.2, "storm": -15.9, "riff": 10.1, "motif": 3.8, "sub": -16.2}


def motif_in(beat_s: float, t0: float, shift: int = 0) -> list[tuple[float, float, float]]:
    out = []
    t = t0
    for p, beats in SEFIR.MOTIF:
        out.append((t, beats * beat_s, float(n(p)) + shift))
        t += beats * beat_s
    return out


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    mx = LoopMixer(intro_s=0.0, loop_s=W_LOOP, preroll_s=8.0)
    G = W_GAINS
    dark = lambda x: filt(x, [bq_highpass(60, 0.7), bq_lowpass(4000, 0.7)])  # noqa: E731
    mx.bus("hum", G["hum"], send=0.25, process=dark)
    mx.bus("strings", G["strings"], send=0.25, process=lambda x: string_body(x, cutoff=1800.0))
    mx.bus("motif", G["motif"], send=0.3, process=lambda x: string_body(x, cutoff=3500.0))
    mx.bus("bells", G["bells"], send=0.3, process=lambda x: filt(x, [bq_highpass(60, 0.7), bq_lowpass(3000, 0.7)]))
    hum_beat = 60.0 / ORDER_HUM_BPM
    for k, at in enumerate(W_HUM_BEATS):
        line = [(float(m), b * hum_beat) for m, b in ORDER_HUM]
        x = hum_ensemble(line, voices=14, seed=SEED + 10 * k, register="low")
        mx.add("hum", x, at * W_BEAT)
    for b, ch in enumerate(W_CHORDS):
        tb = b * W_BAR
        mx.add("strings", pad_chord([n(x) for x in ch.split()], W_BAR * 1.01, vel=0.45, seed=SEED + 100 + b,
                                    attack=1.0, release=1.2), tb - 0.1)
        held_c_sharp = any(b0 + 2 <= b <= b0 + 3 for b0 in W_MOTIF_BARS)
        bell = "C#2" if held_c_sharp else "C2"
        mx.add("bells", tower_bell(float(n(bell)), vel=0.35, seed=SEED + 200 + b, t60=4.0, dark=0.6), tb)
    for b0 in W_MOTIF_BARS:
        for i, (t, d, m) in enumerate(motif_in(W_BEAT, b0 * W_BAR)):
            mx.add("motif", pad_chord([m, m + 12], d * 1.02, vel=0.42, seed=SEED + 300 + 10 * b0 + i, attack=0.5,
                                      release=1.0, voices=4), t)
    room = ModFDNReverb(rt60=0.8, rt60_high=0.4, predelay=0.01, size=0.6, mod_depth=3.0, mod_rate=0.3,
                        early_level=0.4, lowcut=120.0, highcut=4000.0, width=0.6, seed=SEED % 9973)
    _, loop = mx.render(reverb=room, reverb_return_db=-6.0)
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report={})
    _write(out_path, loop, W_BPM, 4)
    m = measure(loop)
    if stats is not None:
        stats["warden_bus_lufs"] = dict(mx.bus_lufs)
    if verbose:
        print(f"sefir_warden: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    render_heart(os.path.join(os.path.dirname(out_path), os.path.basename(OUT_HEART)), verbose=verbose, stats=stats)
    return m


def storm_note(length: float, seed: int) -> np.ndarray:
    """The storm's own note: many huge low throats on A, "o" opening to "a", the pitch swelling a quarter tone up
    and back over each four bars."""
    g = rng(seed)
    swell = 4 * H_BAR
    steps = int(np.ceil(length / swell))
    out = np.zeros((int((length + 2.0) * SR), 2))
    for v in range(8):
        pitches = []
        for k in range(steps):
            base = float(n("A1" if v % 2 == 0 else "A2")) + float(g.normal(0, 0.06))
            pitches += [(base, swell * 0.5), (base + 0.5, swell * 0.5)]
        ph = []
        for k in range(steps):
            ph += [("o", swell * 0.5), ("a", swell * 0.5)]
        y = sing(ph, pitches, vel=0.75, seed=seed + v, scale=0.92, tilt=1.4, breath=0.0, vib_cents=6.0, vib_rate=3.0,
                 jitter_cents=8.0, release=0.5)
        k = min(len(y), len(out))
        pan = (v / 7.0 - 0.5) * 0.8
        out[:k, 0] += y[:k] * (1 - pan)
        out[:k, 1] += y[:k] * (1 + pan)
    return out


def render_heart(out_path: str = OUT_HEART, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED + 1)
    mx = LoopMixer(intro_s=0.0, loop_s=H_LOOP, preroll_s=4.0)
    G = H_GAINS
    mx.bus("kick", G["kick"], send=0.12, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(3000, 0.7)]))
    mx.bus("kit", G["kit"], send=0.15, process=lambda x: filt(x, [bq_highpass(80, 0.7)]))
    mx.bus("storm", G["storm"], send=0.3, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(2500, 0.7)]))
    mx.bus("riff", G["riff"], send=0.15, process=lambda x: string_body(x, cutoff=1400.0))
    mx.bus("motif", G["motif"], send=0.3, process=lambda x: string_body(x, cutoff=4000.0))
    mx.bus("sub", G["sub"], send=0.0, process=lambda x: filt(x, [bq_lowpass(120, 0.7)]))
    mx.add("storm", storm_note(H_LOOP + 2.0, SEED + 50), -1.0)
    N = int((H_LOOP + 2.0) * SR)
    t = np.arange(N) / SR
    sub = 0.3 * np.sin(2 * np.pi * midi_to_hz(n("A0") + 12) * t)
    mx.add("sub", np.stack([sub, sub], axis=1), -1.0)
    groups = (0, 2, 4)                                   # 2+2+3: each group's first eighth
    for b in range(H_BARS):
        tb = b * H_BAR
        fill = b % 8 == 7
        for e in range(7):
            te = tb + e * H_EIGHTH
            if e in groups:
                mx.add("kick", big_drum(0.75 if e == 0 else 0.6, variant=(b + e) % 3, seed=SEED + 100 * b + e), te)
            if e in (2, 4) and not fill:
                mx.add("kit", frame_drum("slap", 0.85, variant=(b + e) % 8, seed=SEED + 2000 + 10 * b + e), te,
                       pan=0.1)
            elif not fill:
                mx.add("kit", frame_drum("ghost", 0.3, variant=(b + e) % 8, seed=SEED + 4000 + 10 * b + e), te,
                       pan=-0.25)
            if fill:                                       # a tom run into every eighth bar, high to low
                mx.add("kit", frame_drum("dum", 0.55 + 0.05 * e, variant=e % 8, size=1.3 - 0.06 * e,
                                         seed=SEED + 6000 + 10 * b + e), te, pan=0.4 - 0.12 * e)
            mx.add("riff", pad_chord([n(H_RIFF[e])], H_EIGHTH * 0.8, vel=0.6, seed=SEED + 8000 + 10 * b + e,
                                     attack=0.01, release=0.08, voices=2), te)
    for b0 in H_MOTIF_BARS:
        quarter = 2 * H_EIGHTH
        for i, (t0, d, m) in enumerate(motif_in(quarter, b0 * H_BAR, shift=12)):
            mx.add("motif", pad_chord([m], d, vel=0.5, seed=SEED + 9000 + 10 * b0 + i, attack=0.08, release=0.6,
                                      voices=4), t0)
        # the C# is the storm's A major third now: an A major chord sounds under it as it lands
        last_t = motif_in(quarter, b0 * H_BAR)[-1][0]
        mx.add("motif", pad_chord([n("A3"), n("E4"), n("A4")], 6 * quarter, vel=0.42, seed=SEED + 9500 + b0,
                                  attack=0.2, release=0.8), last_t)
    hall = ModFDNReverb(rt60=1.8, rt60_high=0.9, predelay=0.02, size=1.0, mod_depth=6.0, mod_rate=0.5,
                        early_level=0.3, lowcut=150.0, width=0.7, seed=SEED % 9973 + 1)
    _, loop = mx.render(reverb=hall, reverb_return_db=-4.0)
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report={})
    _write(out_path, loop, 132.0, 7)
    m = measure(loop)
    if stats is not None:
        stats["heart_bus_lufs"] = dict(mx.bus_lufs)
    if verbose:
        print(f"sefir_heart: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


def _write(out_path: str, loop: np.ndarray, bpm: float, bpb: int) -> None:
    L = len(loop)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, bpm, bpb)


if __name__ == "__main__":
    render()
