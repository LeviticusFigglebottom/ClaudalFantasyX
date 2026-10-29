"""`kite_maiden_flight`: Ch18, the Kite's first lift-off (M3-AUD-853; act3_plan.md §2, act_outline Ch18), 46.9 s,
through-composed.

Original composition for this project (SPEC §2, §9). Its tunes are the game's own and are loaded, never retyped:
Dace's current-song (motifs.py `CURRENT_SONG`, its first phrase, "sound, sound, the set rising"), whistled, because
this is his hull leaving his flotilla; and the_kite's A section (the_kite.py, which loads the star-path from
haluna_dawn.py `RH_CELL` and its harmony from haluna_dawn.py `LH`), its first half, with the_kite's own voices and
voicings (its thrum, sails, pad and low string). What this cue adds was written for it: the whistle's climb out of
the current-song (A, then C, C#, E: the dorian's C lifted to the major's C#, the moment the hull leaves the water),
the engines waking (a hum gliding up an octave and the vanes knocking faster until they reach the_kite's eighths),
and the harmony of the first twelve seconds (Dm, G/D, C, A).

The brief: the first lift-off, rising out of Hollowmere's world (D dorian, a Saltwright whistle) into the_kite's A
section, ending where the_kite's loop can take over. So it starts in the dry-dock's key and pace (the current-song's
76 BPM, mallets on a hull, an open fifth), lifts by one semitone of harmony, and arrives at the_kite's tempo (108 BPM),
its deck and its star-path; it stops on the_kite's A chord with the star-path's A held, so the hub loop's bar 1 (D)
follows as a resolution.

D dorian, then D major; 76 BPM (a beat is 0.789 s), then 4/4 at 108 BPM (a bar is 2.222 s). In seconds: 0-6 the
dry-dock: the open fifth, a few mallet knocks, the whistle's current-song phrase over Dm and G/D | 6-13 the lift: the
whistle climbs (C over C, C# and E over A), the engines' hum rises an octave, the vanes quicken, the first sail fills
and the far drum marks the hull leaving the water | 13-17 the deck at 108: the thrum and the wind (the_kite's bars
1-2, on D) | 17-35 the_kite's A, first half: the star-path (F# E D E | F# A B A) in half time over D, Bm, G, A |
35-40 the A chord, the star-path's A held | the ring-out.

Ensemble (all synthesized; no samples): the Saltwright whistle (synth.winds.breath_flute, high, little breath, a
narrow vibrato); the_kite's sky flute, thrum, pad, low string, frame drum, big drum, sails, wind and stays; the
engines (a hum of a few harmonics gliding D1 to D2, with a faint bound-light shimmer) and their vanes (liss_theme's
paddles, as in the_kite's B); mallets on the hull (frame-drum rim strokes).

Render:  python3 assets_src/music/act3/kite_maiden_flight.py
         (or tools/audio/render_all.py --act3 --only act3/kite_maiden_flight)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, rng, smooth_noise  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


K = _mod("the_kite", os.path.join(HERE, "the_kite.py"))            # the hub loop: its A section, voices, voicings
MOTIFS = _mod("motifs", os.path.join(MUSIC, "motifs.py"))          # Dace's current-song
HD, LS, V = K.HD, K.LS, K.V

OUT = os.path.join(ROOT, "assets", "audio", "music", "act3", "kite_maiden_flight.ogg")
SEED = 20261854
TARGET_LUFS = -16.0
QUALITY = 3.0
DOCK_BEAT = 60.0 / MOTIFS.CURRENT_SONG_BPM      # the dry-dock's pace: the current-song's own tempo
BEAT, BAR, E8 = K.BEAT, K.BAR, K.E8              # the Kite's
T_SONG = 1.2                                     # the whistle's current-song phrase
T_DECK = 13.0                                    # the_kite's tempo starts: two bars of its deck on D
T_STAR = T_DECK + 2 * BAR                        # the_kite's A, first half (eight bars)
STAR_BEATS = 16.0                                # the star-path's first half, in its own beats
T_CLOSE = T_STAR + 8 * BAR                       # two bars of A, the star-path's A held
T_END = T_CLOSE + 2 * BAR
## the whistle's climb out of the current-song, in dock beats after it: (pitch, beats)
CLIMB = [("C6", 3.0), ("C#6", 1.5), ("E6", 4.0)]
## the dock's harmony: (start in dock beats from T_SONG, pad pitches, bass)
DOCK = [(-1.0, "D3 A3 F4 E4", "D2"), (3.0, "D3 B3 G4", "D2"), (6.0, "C3 G3 E4", "C2"), (9.0, "A2 E3 C#4 A4", "A1")]
## mallets on the hull (dock beats from T_SONG)
MALLETS = [-0.5, 0.5, 2.0, 3.5, 4.0, 5.5]


def song_line() -> list[tuple[int, float, float]]:
    """The whistle: the current-song's first phrase an octave up, then the climb: [(midi, start s, dur s)]."""
    out, t = [], T_SONG
    for m, beats in MOTIFS.CURRENT_SONG[0]:
        out.append((m + 12, t, beats * DOCK_BEAT))
        t += beats * DOCK_BEAT
    for p, beats in CLIMB:
        d = beats * DOCK_BEAT if p != CLIMB[-1][0] else T_DECK + BAR - t
        out.append((n(p), t, d))
        t += beats * DOCK_BEAT
    return out


def engine_hum(dur: float, seed: int) -> np.ndarray:
    """The two lift engines waking: a few harmonics gliding from D1 up to D2 over seven seconds, then steady, with a
    faint high shimmer of the bound core. Mono."""
    g = rng(seed)
    N = int(dur * SR)
    t = np.arange(N) / SR
    rise = 1 - np.exp(-t / 2.4)
    f = 36.71 * 2 ** rise * (1 + 0.003 * smooth_noise(N, 0.8, g))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = sum(a * np.sin(k * ph + g.uniform(0, 6.28)) for k, a in ((1, 1.0), (2, 0.6), (3, 0.35), (4, 0.2), (6, 0.08)))
    y += 0.04 * np.sin(16 * ph) * (0.5 + 0.5 * smooth_noise(N, 1.5, g))
    env = np.clip(t / 3.0, 0, 1) ** 2 * np.clip((dur - t) / 4.0, 0, 1)
    return y * env * 0.2


def air(dur: float, seed: int) -> np.ndarray:
    """The wind rising as the hull lifts, then the open air: stereo."""
    g = rng(seed)
    N = int(dur * SR)
    t = np.arange(N) / SR
    out = np.zeros((N, 2))
    level = 0.25 + 0.75 * np.clip((t - 5.0) / 9.0, 0, 1) ** 1.5
    for ch in range(2):
        lo = filt(g.standard_normal(N), [bq_highpass(150, 0.6), bq_lowpass(1300, 0.6)])
        hi = filt(g.standard_normal(N), [bq_highpass(1800, 0.7), bq_lowpass(3200, 0.7)])
        gust = 0.75 + 0.25 * smooth_noise(N, 0.25, g)
        out[:, ch] = (lo + 0.3 * hi) * level * gust
    k = int(3.0 * SR)
    out[-k:] *= np.linspace(1, 0, k)[:, None]
    return out * 0.05


def vane_times() -> list[float]:
    """The vanes: slow knocks quickening from 0.55 s apart to the_kite's eighths at T_DECK, then on its grid until
    the star-path starts."""
    ts, t, gap = [], 6.8, 0.55
    while t < T_DECK - 1e-6:
        ts.append(t)
        t += gap
        gap = max(E8, gap * 0.93)
    t = T_DECK
    while t < T_STAR + BAR - 1e-6:
        ts.append(t)
        t += E8
    return ts


def tones(spec: str) -> tuple[int, int, list[int]]:
    """the_kite's chord(): a haluna_dawn LH string, or one of the_kite's OWN voicings."""
    if spec in K.OWN:
        b1, b3, up = K.OWN[spec]
        return n(b1), n(b3), [n(p) for p in up.split()]
    ps = [n(p) for p in spec.split()]
    return ps[0], ps[1], [p + 12 for p in ps[1:]]


def kite_bars() -> list[tuple[float, str, str]]:
    """(start s, chord, section) for every bar at the Kite's tempo."""
    out = [(T_DECK + i * BAR, "D", "deck") for i in range(2)]
    out += [(T_STAR + i * BAR, K.STAR_LH[i // 2], "star") for i in range(8)]
    out += [(T_CLOSE, "Asus", "close"), (T_CLOSE + BAR, "A", "close")]
    return out


def build(mx: Mixer) -> None:
    g = rng(SEED)
    # the dry-dock
    for j, (b, pad, bass) in enumerate(DOCK):
        t0 = T_SONG + b * DOCK_BEAT
        t1 = T_SONG + DOCK[j + 1][0] * DOCK_BEAT if j + 1 < len(DOCK) else T_DECK
        mx.add("pad", pad_chord([n(p) for p in pad.split()], t1 - t0, 0.4, seed=SEED + 200 + j, voices=4,
                                attack=1.4 if j == 0 else 0.8, release=1.4, width=0.8), t0 - 0.2)
        x = string_pluck(n(bass), 3.0, 0.55, seed=SEED + 400 + j, pick_pos=0.16, t60=2.6, B=8e-5, max_f=3000.0,
                         release=0.2)
        mx.add("low", x, t0, pan=-0.1)
    for j, b in enumerate(MALLETS):
        x = frame_drum("tek", 0.14 * float(g.uniform(0.85, 1.1)), variant=j, size=1.6, seed=SEED + 1)
        mx.add("mallet", x, T_SONG + b * DOCK_BEAT + float(g.normal(0, 0.01)), pan=0.5 if j % 2 else -0.4)
    for j, (m, t0, d) in enumerate(song_line()):
        x = breath_flute(m, d * 0.95 + 0.03, 0.5 * float(g.uniform(0.95, 1.04)), seed=SEED + 600 + j, breath=0.18,
                         scoop_cents=25.0 if j else 40.0, vib_cents=6.0, vib_rate=5.4, swell=0.2 if d > 1.5 else 0.0,
                         attack=0.035, release=0.25 if j < 7 else 0.9, beta=0.45)
        mx.add("whistle", x, t0 - V.FLUTE_PRE, pan=0.18)
    # the lift: the engines, the vanes, the wind, the first sail and the far drum
    mx.add("engine", engine_hum(T_END + 2.0 - 5.5, SEED + 7), 5.5, pan=0.0)
    for j, t in enumerate(vane_times()):
        k = j % len(LS.WHEEL)
        fade = float(np.clip((T_STAR + BAR - t) / (2 * BAR), 0, 1)) ** 0.7
        v = (0.5 if k == 0 else 0.34) * fade * float(g.uniform(0.88, 1.06))
        mx.add("vanes", LS.paddle(n(LS.WHEEL[k]) + 12, v, SEED + 2000 + 13 * k + (j % 3)), t + LS.WHEEL_LAG_S,
               pan=-0.45 + 0.08 * k)
    mx.add("wind", air(T_END + 4.0, SEED + 3), 0.0)
    span = T_END + 4.0 - T_DECK
    ts = np.arange(int(round(span * SR)))[:, None] / SR
    stays = V.cord_song(span, [n(p) for p in K.STAYS], SEED + 4, q=50.0)
    mx.add("stays", stays * np.clip(ts / 3.0, 0, 1) * np.clip((span - ts) / 4.0, 0, 1), T_DECK - 1.0)
    mx.add("sail", K.sail_fill(rng(SEED + 3001)), 10.4 - 0.45, pan=-0.3)
    mx.add("drum", big_drum(0.34, variant=1, seed=SEED + 2), T_SONG + 9.0 * DOCK_BEAT)
    # the Kite's tempo: its deck, its A (first half), and the A chord
    for i, (t0, ch, sec) in enumerate(kite_bars()):
        bass, fifth, up = tones(ch)
        mx.add("pad", pad_chord(up, BAR * (0.96 if i < 11 else 1.6), 0.42, seed=SEED + 260 + i, voices=4, attack=0.9,
                                release=1.6 if i < 11 else 2.6, width=0.9), t0 - 0.2)
        for beat, p, v in ((0, bass, 0.6), (2, fifth, 0.45)):
            x = string_pluck(p, 1.9 * BEAT if i < 11 else 3.0, v * g.uniform(0.94, 1.04), seed=SEED + 440 + 4 * i
                             + beat, pick_pos=0.16, t60=2.4, B=8e-5, max_f=3000.0, release=0.14 if i < 11 else 0.6)
            mx.add("low", x, t0 + beat * BEAT + float(g.normal(0, 0.004)), pan=-0.1)
        thr = up[:3] + [fifth + 24]
        for e, (k, acc) in enumerate(K.THRUM):
            if i == 11 and e >= 4:
                break
            v = 0.34 * acc * g.uniform(0.9, 1.06) * (0.8 if sec == "deck" else 1.0)
            x = string_pluck(thr[k] + 12, 0.45 * BEAT, v, seed=SEED + 1000 + 8 * i + e, pick_pos=0.1, t60=0.9,
                             B=6e-5, max_f=8000.0, release=0.06)
            mx.add("thrum", x, t0 + e * E8 + float(g.normal(0, 0.004)), pan=0.4 - 0.08 * k)
        if sec == "star" or (sec == "close" and i == 10):
            for beat, stroke, v in ((0, "dum", 0.2), (1.5, "tek", 0.1), (3, "ghost", 0.07)):
                x = frame_drum(stroke, v * float(g.uniform(0.9, 1.08)), variant=i, size=1.1, seed=SEED + 1)
                mx.add("step", x, t0 + beat * BEAT + float(g.normal(0, 0.006)), pan=0.08)
        if sec == "star" and i % 4 == 2:
            mx.add("sail", K.sail_fill(rng(SEED + 3100 + i)), t0 - 0.45, pan=0.3 if i % 8 == 2 else -0.3)
            mx.add("drum", big_drum(0.3, variant=i, seed=SEED + 2), t0)
    # the star-path's first half, as the_kite's A states it; its last A held over the A chord
    cell, beats = [], 0.0
    for p, b in HD.RH_CELL:
        if beats >= STAR_BEATS:
            break
        cell.append((p, b))
        beats += b
    line = [(m, t - K.t_of(5) + T_STAR, d) for m, t, d in K.star_path(5, cell)]
    m, t0, _ = line[-1]
    line[-1] = (m, t0, T_END - t0)
    sky = rng(SEED + 640)
    for j, (m, t0, d) in enumerate(line):
        long_ = d >= 4 * BEAT
        x = breath_flute(m, d * 0.97 + 0.04, 0.55 * float(sky.uniform(0.95, 1.04)) * (1.06 if long_ else 1.0),
                         seed=SEED + 640 + j, breath=0.42, scoop_cents=30.0, vib_cents=11.0, vib_rate=4.8,
                         swell=0.25 if long_ else 0.08, attack=0.14, release=0.7 if j < len(line) - 1 else 1.8,
                         beta=0.5)
        mx.add("sky", x, t0 - V.FLUTE_PRE + float(sky.normal(0, 0.006)), pan=-0.08)


## Bus gains: the_kite's (its voices keep their balance), plus the whistle level with the sky flute, the engines -14,
## the mallets -16, the vanes -15 and the rising wind -12 (bus loudness measured over each bus's own span,
## render(stats=...)).
GAINS = dict(K.GAINS, whistle=0.8, engine=-18.4, mallet=15.6, wind=K.GAINS["wind"] - 3.3,
             vanes=K.GAINS["vanes"] + 1.3)


def _bus_stats(mx: Mixer) -> dict:
    out = {}
    for b in mx.buses.values():
        x = db_to_lin(b.gain_db) * (b.process(b.buf) if b.process else b.buf)
        out[b.name] = integrated_lufs(x) if np.any(x) else float("-inf")
    return out


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = Mixer(T_END + 8.0)
    G = GAINS
    mx.bus("whistle", G["whistle"], send=0.35, process=lambda x: filt(x, [bq_highpass(400, 0.7),
                                                                          bq_peak(3000, 2.0, 1.0)]))
    mx.bus("sky", G["sky"], send=0.42, process=lambda x: filt(x, [bq_highpass(240, 0.7), bq_peak(2600, 1.5, 1.0),
                                                                  bq_lowpass(8000, 0.7)]))
    mx.bus("pad", G["pad"], send=0.5, process=lambda x: string_body(x, cutoff=1900.0))
    mx.bus("low", G["low"], send=0.15, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1600, 0.7)]))
    mx.bus("thrum", G["thrum"], send=0.3, process=lambda x: filt(x, [bq_highpass(300, 0.7), bq_lowpass(7000, 0.7)]))
    mx.bus("wind", G["wind"], send=0.12)
    mx.bus("stays", G["stays"], send=0.3)
    mx.bus("step", G["step"], send=0.35, process=lambda x: filt(x, [bq_lowpass(2400, 0.7)]))
    mx.bus("drum", G["drum"], send=0.6, process=lambda x: filt(x, [bq_lowpass(1100, 0.7)]))
    mx.bus("sail", G["sail"], send=0.2)
    mx.bus("vanes", G["vanes"], send=0.2, process=lambda x: filt(x, [bq_highpass(200, 0.7), bq_lowpass(6000, 0.7)]))
    mx.bus("engine", G["engine"], send=0.25, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))
    mx.bus("mallet", G["mallet"], send=0.45, process=lambda x: filt(x, [bq_lowpass(3000, 0.7)]))
    build(mx)
    st = _bus_stats(mx)
    hall = ModFDNReverb(rt60=2.8, rt60_high=1.2, predelay=0.05, size=1.4, mod_depth=8.0, mod_rate=0.35,
                        early_level=0.1, lowcut=120.0, seed=SEED % 9973)
    master = mx.render(reverb=hall, reverb_return_db=-3.0)
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(2.0 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, master, quality=QUALITY)
    m = measure(master)
    if stats is not None:
        stats["bus_lufs"] = st
    if verbose:
        print(f"kite_maiden_flight: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS"
              f"  TP {m['true_peak_dbtp']:.2f} dBTP")
        print("  buses", {k: round(v, 1) for k, v in st.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
