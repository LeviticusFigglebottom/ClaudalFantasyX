"""`drownbell`: the Drownbell boss (M2-AUD-03; vertical_slice.md B10): two synchronized stems, a 72.7 s loop.

Original composition for this project (SPEC §2, §9); the theme below was written for this fight and is not
adapted from any existing melody. The brief (vertical_slice.md §6): "Stem 1 (phase 1) is built around a pitched
bell toll on the downbeat. Stem 2 (phase 2) adds low strings and a rising-water swell." The boss is a drowned
bell; its toll is the fight's clock.

C Phrygian (C Db Eb F G Ab Bb), 4/4 at 132 BPM (a bar is 1.818 s), 40 bars.

**Stem 1** (`drownbell_p1.ogg`, plays from the start):
* the toll: a tower bell (synth.bells, prime C3, the hum C2) on every downbeat, heavier on each 4-bar group; in the
  breakdown it tolls every other bar and is left to ring;
* a kotekan in C Phrygian (two metallophones interlocking on sixteenths) and a low metallophone on the roots;
* a fingered bass in 3+3+2 (tresillo) sixteenths; frame drums and a big drum in the same grouping;
* the theme: a hard-blown breath flute doubled an octave up by a hard metallophone (A: bars 9-16, B: 17-24, A:
  33-40); a low congregation hum on C and Db (the dead) in the intro and the breakdown.

**Stem 2** (`drownbell_p2.ogg`, the Flood; the game fades it in over the stem 1 already playing):
* low strings: a sustained root-fifth-octave section on every chord, swelling inside each two bars;
* the rising water: a band of noise that rises in pitch and level over each 8 bars, a thickening field of bubbles,
  and a sub-bass surge into every section's first bar;
* a second big drum doubling the first in sixteenth-note pickups, and a high bar countermelody over the B and the
  last A.

Form: 1-8 the toll (ostinato, drums, bass; the hum from bar 5) | 9-16 A | 17-24 B | 25-32 breakdown (the toll every
other bar, ostinato, hum; builds from 29) | 33-40 A, with a drum fill in bar 40 into the wrap.

Mastering: both stems share one gain (the full stack at -16 LUFS) and one limiter gain curve computed on the full
stack (synth.mixer.limit_gain), so stem 1 + stem 2 is exactly the limited mix and neither stem alone is louder
than its share. Loop: LOOPSTART = 0 on both; equal lengths.

Render:  python3 assets_src/music/drownbell.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.bells import tower_bell  # noqa: E402
from synth.drums import big_drum, frame_drum, jingle  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, midi_to_hz, rng  # noqa: E402
from synth.electric import bass_note  # noqa: E402
from synth.gongs import large_gong  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.water import bubble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "music")
OUT = os.path.join(OUT_DIR, "drownbell_p1.ogg")
OUT2 = os.path.join(OUT_DIR, "drownbell_p2.ogg")
SEED = 20261107
TARGET_LUFS = -16.0
BPM = 132.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
S16 = BEAT / 4
BARS = 40
LOOP_S = BARS * BAR
FLUTE_PRE = 0.065
## Stem 2's trim at mastering: the Flood lifts the stack about 2 LU over stem 1 alone (measured: render prints both).
STEM2_GAIN_DB = 1.7

SCALE = [n(x) % 12 for x in "C4 Db4 Eb4 F4 G4 Ab4 Bb4".split()]
CHORDS = (["C", "C", "Db", "C", "C", "C", "Db", "C"]
          + ["C", "Db", "C", "C", "Ab", "Eb", "Db", "C"]
          + ["Ab", "Bb", "Ab", "F", "Db", "Ab", "Db", "C"]
          + ["C", "C", "Db", "Db", "C", "C", "Bb", "Db"]
          + ["C", "Db", "C", "C", "Ab", "Eb", "Db", "C"])
SECTION = ["I"] * 8 + ["A"] * 8 + ["B"] * 8 + ["D"] * 8 + ["A2"] * 8
ROOT_MIDI = {"C": "C2", "Db": "Db2", "Eb": "Eb2", "F": "F2", "Ab": "Ab1", "Bb": "Bb1"}

THEME_A = [
    [("C5", 1.5), ("Db5", .5), ("Eb5", 1), ("G5", 1)],
    [("F5", 2), ("Eb5", 1), ("Db5", 1)],
    [("C5", 1), ("Bb4", .5), ("C5", .5), ("Db5", 2)],
    [("C5", 3), (None, 1)],
    [("G5", 1.5), ("Ab5", .5), ("G5", 1), ("F5", 1)],
    [("Eb5", 2), ("F5", 1), ("G5", 1)],
    [("Ab5", 1.5), ("G5", .5), ("F5", 1), ("Db5", 1)],
    [("C5", 3), (None, 1)],
]
THEME_B = [
    [("C6", 2), ("Bb5", 1), ("Ab5", 1)],
    [("G5", 1.5), ("Ab5", .5), ("Bb5", 2)],
    [("Ab5", 1), ("G5", 1), ("F5", 1), ("Eb5", 1)],
    [("F5", 3), (None, 1)],
    [("Db6", 2), ("C6", 1), ("Bb5", 1)],
    [("Ab5", 1.5), ("Bb5", .5), ("C6", 2)],
    [("Db6", 1), ("C6", 1), ("Bb5", 1), ("G5", 1)],
    [("C6", 3), (None, 1)],
]
COUNTER = [("G6", 8), ("Ab6", 4), ("G6", 4), ("F6", 8), ("Eb6", 4), ("Db6", 4)]   # beats; the high bar line
KOTEKAN = [0, 2, 4, 2, 0, 2, 5, 4, 0, 2, 4, 2, 7, 5, 4, 2]
TRESILLO = (1, 4, 7, 9, 12, 15)


def t_of(bar: int, s16: float = 1.0) -> float:
    return (bar - 1) * BAR + (s16 - 1) * S16


def scale_note(root: str, degree: int, octave_midi: float) -> float:
    """The `degree`-th scale tone above chord root `root` (in C Phrygian), placed from octave_midi up."""
    r = n(root + "4") % 12
    i0 = SCALE.index(int(r)) if int(r) in SCALE else 0
    i = i0 + degree
    o, k = divmod(i, 7)
    pc = SCALE[k]
    base = octave_midi - (octave_midi % 12)
    m = base + pc + 12 * o
    while m < octave_midi:
        m += 12
    return m


def add_line(mx: LoopMixer, bus: str, bars: list, start_bar: int, seed: int, vel: float, pan: float,
             metal_bus: str | None = None) -> None:
    g = rng(seed)
    t = t_of(start_bar)
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, beats in bar:
            d = beats * BEAT
            if p is not None:
                x = breath_flute(n(p), d * 0.93 + 0.02, vel * g.uniform(0.94, 1.04), seed=seed + 5 * int(pos * 100),
                                 breath=0.5, scoop_cents=35.0 if beats >= 1 else 10.0,
                                 vib_cents=10.0 if beats >= 2 else 0.0, vib_rate=5.4, swell=0.2 if beats >= 3 else 0.0,
                                 attack=0.03, release=0.14, beta=0.6)
                mx.add(bus, x, pos - FLUTE_PRE + float(g.normal(0, 0.003)), pan=pan)
                if metal_bus:
                    y = metallophone_note(n(p) + 12, 0.42, seed=seed + 7 * int(pos * 100), decay=2.4, hardness=0.7,
                                          ombak_hz=6.2, damp_at=min(d, 0.5))
                    mx.add(metal_bus, y, pos, pan=0.15)
            pos += d
    del t


def build_p1(mx: LoopMixer) -> None:
    g = rng(SEED)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT_MIDI[ch])
        group_start = (bar - 1) % 4 == 0
        toll = sec != "D" or bar % 2 == 1
        if toll:
            v = 0.95 if group_start else 0.7
            mx.add("bell", tower_bell(n("C3"), v, seed=SEED + 10 * bar, t60=7.0 if sec == "D" else 4.5,
                                      dark=0.25 if not group_start else 0.1), t_of(bar), pan=0.0)
        # kotekan
        if sec != "D" or bar >= 27:
            lvl = 0.85 if sec in ("A", "B", "A2") else 0.7
            for s in range(1, 17):
                m = scale_note(ch, KOTEKAN[s - 1], n("C5"))
                v = lvl * (0.48 if s % 4 == 1 else 0.38) * g.uniform(0.92, 1.06)
                x = metallophone_note(m, v, seed=SEED + 1000 * bar + s, decay=2.2, hardness=0.6, ombak_hz=6.0,
                                      damp_at=S16 * 1.6)
                mx.add("metal", x, t_of(bar, s) + float(g.normal(0, 0.003)), pan=-0.45 if s % 2 else 0.45)
        # low metallophone on the root
        x = metallophone_note(root + 24, 0.5, seed=SEED + 50000 + bar, decay=3.5, hardness=0.4, ombak_hz=4.0)
        mx.add("lowmetal", x, t_of(bar), pan=0.0)
        # bass in 3+3+2
        if sec != "D" or bar >= 29:
            for s in TRESILLO:
                off = 12 if s in (7, 15) else 0
                x = bass_note(root + off, S16 * 2.6, (0.85 if s in (1, 9) else 0.65) * g.uniform(0.92, 1.05),
                              seed=SEED + 60000 + 100 * bar + s, mute=0.3)
                mx.add("bass", x, t_of(bar, s) + 0.003, pan=0.0)
        elif bar % 2 == 1:
            mx.add("bass", bass_note(root, 2 * BAR - 0.1, 0.8, seed=SEED + 61000 + bar, mute=0.0), t_of(bar))
        # drums
        if sec in ("I", "A", "B", "A2") or bar >= 29:
            for s in TRESILLO:
                mx.add("drums", frame_drum("dum", (0.9 if s in (1, 9) else 0.7) * g.uniform(0.92, 1.05),
                                           variant=bar * 16 + s, seed=SEED + 3), t_of(bar, s) + float(g.normal(0, 0.003)))
            for s in (5, 13):
                mx.add("drums", frame_drum("slap", 0.8 * g.uniform(0.92, 1.05), variant=bar * 16 + s, seed=SEED + 3),
                       t_of(bar, s), pan=0.05)
            for s in range(1, 17):
                if s not in TRESILLO and s not in (5, 13):
                    mx.add("drums", frame_drum("tek" if s % 2 == 0 else "ghost", 0.42 * g.uniform(0.85, 1.1),
                                               variant=bar * 16 + s, seed=SEED + 3), t_of(bar, s), pan=-0.15)
            for s in (1, 7):
                mx.add("drums", big_drum(0.85 if s == 1 else 0.6, variant=bar + s, seed=SEED + 4), t_of(bar, s))
            if sec in ("B", "A2"):
                for s in range(1, 17, 2):
                    mx.add("jingle", jingle(0.45 if s % 4 == 1 else 0.3, variant=bar + s, seed=SEED + 5),
                           t_of(bar, s), pan=0.3)
        else:
            mx.add("drums", big_drum(0.7, variant=bar, seed=SEED + 4), t_of(bar))
        if bar == 40:
            for s in range(9, 17):
                mx.add("drums", frame_drum("slap" if s % 2 else "dum", 0.5 + 0.06 * (s - 9), variant=s, seed=SEED + 6),
                       t_of(bar, s), pan=0.05)
    # the dead hum on C and Db
    for start, line in ((5, [("C3", 4 * BAR - 0.4)]), (25, [("C3", 2 * BAR), ("Db3", 2 * BAR), ("C3", 4 * BAR - 0.4)])):
        x = hum_ensemble([(n(p), d) for p, d in line], voices=12, seed=SEED + 70 + start, register="low", spread=0.8)
        env = np.ones(len(x))
        k = int(1.5 * SR)
        env[:k] = np.linspace(0, 1, k) ** 2
        env[-k:] *= np.linspace(1, 0, k) ** 2
        mx.add("hum", x * env[:, None], t_of(start))
    mx.add("gong", large_gong(n("C2"), 0.6, seed=SEED + 80, t60=8.0), t_of(25), pan=0.0)
    add_line(mx, "lead", THEME_A, 9, SEED + 100, 0.85, -0.12, metal_bus="metal_lead")
    add_line(mx, "lead", THEME_B, 17, SEED + 200, 0.9, -0.12, metal_bus="metal_lead")
    add_line(mx, "lead", THEME_A, 33, SEED + 300, 0.9, -0.12, metal_bus="metal_lead")


def rising_water(sec_len: float, g, sr: int = SR) -> np.ndarray:
    """Eight bars of rising water: a noise band climbing 180 -> 1400 Hz and swelling, with thickening bubbles."""
    N = int(sec_len * sr)
    t = np.arange(N) / sr
    x = t / sec_len
    out = np.zeros(N)
    noise = g.standard_normal(N)
    hop = int(0.25 * sr)
    for i in range(0, N, hop):          # a slowly sweeping band-pass, in quarter-second blocks with overlap
        c = 180.0 * (1400.0 / 180.0) ** (i / N)
        seg = noise[max(0, i - hop): min(N, i + 2 * hop)]
        y = filt(seg, [bq_bandpass(c, 0.9, sr)], sr=sr)
        a = max(0, i - hop)
        w = np.hanning(len(y))
        out[a: a + len(y)] += y * w * 0.5
    out *= (0.2 + 0.8 * x ** 1.6)
    tt = 0.0
    while tt < sec_len:
        r = float(np.exp(g.uniform(np.log(2.0), np.log(9.0))))
        b = bubble(r, g.uniform(0.2, 1.0), rise=0.12)
        s = int(tt * sr)
        e = min(N, s + len(b))
        out[s:e] += 0.6 * b[: e - s] * (0.2 + 0.8 * (tt / sec_len))
        tt += g.exponential(1.0 / (8.0 + 70.0 * (tt / sec_len) ** 2))
    k = int(0.3 * sr)
    out[-k:] *= np.linspace(1, 0, k)
    return out


def build_p2(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    for bar in range(1, BARS + 1, 2):
        ch = CHORDS[bar - 1]
        root = n(ROOT_MIDI[ch]) + 12
        x = pad_chord([root, root + 7, root + 12], 2 * BAR - 0.05, 0.85, seed=SEED + 2000 + bar, voices=5,
                      spread_cents=11.0, attack=0.35, release=0.6, width=0.7)
        swell = 0.75 + 0.25 * np.sin(np.pi * np.clip(np.arange(len(x)) / (2 * BAR * SR), 0, 1)) ** 2
        mx.add("strings", x * swell[:, None], t_of(bar) - 0.03)
    for start in (1, 9, 17, 25, 33):
        mx.add("water", rising_water(8 * BAR, rng(SEED + 3000 + start)), t_of(start), pan=0.0)
        sub_t = np.arange(int(1.6 * SR)) / SR
        sub = np.sin(2 * np.pi * (36.0 + 14.0 * np.exp(-sub_t / 0.4)) * sub_t) * np.exp(-sub_t / 0.7)
        sub *= np.minimum(1.0, sub_t / 0.01)
        mx.add("sub", sub, t_of(start), pan=0.0)
    for bar, sec in enumerate(SECTION, start=1):
        if sec == "D" and bar < 29:
            continue
        for s in (11, 15, 16):
            mx.add("drums2", big_drum(0.55 + 0.1 * (s == 16), variant=bar * 3 + s, seed=SEED + 7), t_of(bar, s), pan=0.2)
    for start in (17, 33):
        pos = t_of(start)
        for i, (p, beats) in enumerate(COUNTER):
            x = metallophone_note(n(p), 0.32, seed=SEED + 4000 + start + i, decay=5.0, hardness=0.5, ombak_hz=5.0)
            mx.add("glass", x, pos, pan=0.5)
            pos += beats * BEAT


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    # Bus gains from measured bus loudness (render(stats=...)): with the lead at L, the bell L-2, drums L-4,
    # kotekan and its lead doubling L-8, low metallophone L-10, bass L-6, hum L-9, jingles L-12, gong L-12; in stem 2
    # strings L-4, water L-8, sub L-10, the second drum L-7, the glass line L-8 (stem 2 sits 2 dB over its first
    # balance so the Flood is a clear escalation: about +2 LU over stem 1 alone).
    if stem == 1:
        mx.bus("bell", -3.2, send=0.35, process=lambda x: filt(x, [bq_highpass(45, 0.7)]))
        mx.bus("metal", -2.7, send=0.25)
        mx.bus("metal_lead", -1.8, send=0.3)
        mx.bus("lowmetal", -1.7, send=0.3)
        mx.bus("bass", -4.8, send=0.0, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_peak(90, 2.0, 0.9),
                                                                    bq_lowpass(3500, 0.7)]))
        mx.bus("drums", -6.7, send=0.12, process=lambda x: filt(x, [bq_highpass(32, 0.7), bq_peak(4000, 1.5, 0.8)]))
        mx.bus("jingle", 6.3, send=0.1)
        mx.bus("hum", -0.4, send=0.6)
        mx.bus("gong", -14.1, send=0.4)
        mx.bus("lead", -1.0, send=0.22, process=lambda x: filt(x, [bq_highpass(220, 0.7), bq_peak(2200, 2.5, 1.0)]))
    else:
        mx.bus("strings", 5.3, send=0.3, process=lambda x: string_body(x, cutoff=1500.0))
        mx.bus("water", -14.0, send=0.25, process=lambda x: filt(x, [bq_highpass(120, 0.7)]))
        mx.bus("sub", -14.3, send=0.0, process=lambda x: filt(x, [bq_lowpass(120, 0.7)]))
        mx.bus("drums2", -5.4, send=0.12)
        mx.bus("glass", 3.1, send=0.45)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    loops = []
    bus_lufs = {}
    for stem, build in ((1, build_p1), (2, build_p2)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
        _bus_setup(mx, stem)
        build(mx)
        hall = ModFDNReverb(rt60=2.4, rt60_high=1.0, predelay=0.022, size=1.0, mod_depth=8.0, mod_rate=0.5,
                            early_level=0.3, lowcut=110.0, seed=SEED % 9973)
        _, loop = mx.render(reverb=hall, reverb_return_db=-3.0)
        loops.append(loop)
        bus_lufs.update({f"p{stem}.{k}": v for k, v in mx.bus_lufs.items()})
    loops[1] = loops[1] * db_to_lin(STEM2_GAIN_DB)
    full = loops[0] + loops[1]
    gain = db_to_lin(TARGET_LUFS - integrated_lufs(full))
    ctx = int(0.05 * SR)
    L = len(full)
    # one limiter gain curve for both stems, from the full stack (wrap-aware), iterated to the target
    for _ in range(4):
        f = full * gain
        lg = limit_gain(np.concatenate([f[-ctx:], f, f[:ctx]]), -2.0)[ctx: ctx + L]
        cur = integrated_lufs(f * lg[:, None])
        if abs(cur - TARGET_LUFS) < 0.1:
            break
        gain *= db_to_lin(TARGET_LUFS - cur)
    stems = [s * gain * lg[:, None] for s in loops]
    paths = [out_path, os.path.join(os.path.dirname(out_path), os.path.basename(OUT2))]
    for x, p in zip(stems, paths):
        write_ogg(p, x, quality=3.5, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
        write_loop_sidecar(os.path.splitext(p)[0] + ".loop.json", SR, 0, L, BPM, 4, extra={"stems_of": "drownbell"})
    m = measure(stems[0] + stems[1])
    m1 = measure(stems[0])
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
        stats["stem1_lufs"] = m1["integrated_lufs"]
        stats["limited_fraction"] = float((lg < 0.999).mean())
    if verbose:
        print(f"drownbell: {m['seconds']:.2f}s  full {m['integrated_lufs']:.2f} LUFS TP {m['true_peak_dbtp']:.2f} dBTP; "
              f"stem 1 alone {m1['integrated_lufs']:.2f} LUFS; limited {(lg < 0.999).mean() * 100:.2f} %, "
              f"max {-20 * np.log10(max(lg.min(), 1e-9)):.2f} dB")
        print("  buses", {k: round(v, 1) for k, v in bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
