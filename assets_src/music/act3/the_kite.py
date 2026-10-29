"""`the_kite`: Ch18, the Kite, the Saltwright airship as the hub (M3-AUD-853; act3_plan.md §2, act_outline Ch18,
SPEC §6.6): a 142.2 s seamless loop.

Original composition for this project (SPEC §2, §9). Its two tunes are the game's own and are loaded, never
retyped: the star-path (haluna_dawn.py `RH_CELL`, the homecoming lullaby Asha hums on Ch2's beach, F#-E-D-E |
F#-A, as name_board_home.py imports it) over the harmony that first carried it (haluna_dawn.py `LH`, bars 5-12), and
Liss's theme (liss_theme.py `T_A`, `T_A2`, `T_B` and its chords and voicings, bars 3-18) on her own wright-built
cittern (`cittern_body`), with the tide-wheel's seven paddles (`WHEEL`, `paddle`) as the engines' vanes. What this
cue adds was written for it: the rigging's thrum (an eighth-note figure grouped 3+3+2 on the chord's upper tones), the
sails filling, the low sea-glow section (the star-path's first four notes two octaves down on haluna_dawn's low
metallophone, under glass), the outro's turn home and every voicing outside the two borrowed harmonies. The style
evoked is an open, airborne folk-orchestral one; it quotes no tune and no real instrument's repertoire.

The brief: the hub, the maiden flight, **the world opens**. Dace's unfinished hull, finished by other hands and flown
on sails modelled on Virel (art/environments/kite.md): small, hand-made, patched, and it holds everyone. The only
open, airborne cue in the game: wind, sail, rigging and a lifted major; the star-path at last flying home; Liss's
theme in a B section, because she flies it. Beauty in decline still holds (the sea below glows with the dead), so it
is lifted but not triumphant: no brass, no fanfare, the drum soft, and the star-path still ends on its open E over A,
the beach's unresolved ninth, not the name-board's D.

D major (the C section turns to B minor below), 4/4 at 108 BPM (a bar is 2.222 s), 64 bars. The star-path is stated
in half time (each of its beats is two of this cue's), so it sings at its own beach tempo (54 against 50) while the
rigging runs under it at the Kite's; Liss's theme keeps its own beats, at almost its own tempo (108 against 110).

Ensemble (all synthesized; no samples): the sky flute (synth.winds.breath_flute, open and airy) for the star-path;
Liss's cittern; the rigging's thrum (a taut plucked line, right of centre) and the stays whistling
(act2_voices.cord_song on D6 A5 E6); the wind (act2_voices.wind); the sails filling (a swell of low air and a cloth
snap); a string pad and a plucked low string; a soft frame drum's lift (beat 1 and the and of 2) and a far big drum;
the vanes (Liss's seven paddles, soft, in B); glass and the low metallophone in C.

Form (bars):
*  1-4   the deck: wind, the stays, the thrum and the pad (D D G A);
*  5-20  A, the star-path (haluna_dawn bars 5-12's harmony, two bars a chord), the sails filling every four bars;
* 21-36  B, Liss's theme (her bars 3-18: A, A', B) on her cittern over her own chords, the vanes knocking seven
         against eight; the thrum thins to quarters;
* 37-44  C, the sea below: Bm Bm G G Em Em A A; no drum; glass, the low star-path cell on the metallophone;
* 45-60  A', the star-path again: glass doubles its long notes an octave up in the first half, and in the second
         the cittern joins it an octave down (she flies it home); it ends on E over A, held open;
* 61-64  the deck again (G G A A), and the A leads back to bar 1's D.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/act3/the_kite.py   (or tools/audio/render_all.py --act3 --only act3/the_kite)
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
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HD = _mod("haluna_dawn", os.path.join(MUSIC, "haluna_dawn.py"))     # the star-path: RH_CELL, and LH under it
LS = _mod("liss_theme", os.path.join(MUSIC, "liss_theme.py"))       # Liss's theme, her cittern, her wheel
V = LS.AV                                                           # act2_voices: wind, cord_song, glass, finish

OUT = os.path.join(ROOT, "assets", "audio", "music", "act3", "the_kite.ogg")
SEED = 20261853
TARGET_LUFS = -16.0
BPM = 108.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
E8 = BEAT / 2
BARS = 64
LOOP_S = BARS * BAR
LEAD_IN_S = BEAT / 4            # the file starts a sixteenth before bar 1's downbeat
HALF_TIME = 2.0                 # the star-path's beats, in this cue's beats
QUALITY = 3.0

SECTION = ["I"] * 4 + ["A"] * 16 + ["B"] * 16 + ["C"] * 8 + ["A2"] * 16 + ["O"] * 4
## this cue's own voicings, as liss_theme's VOICING: (bass on 1, fifth on 3, the upper tones)
OWN = {"D": ("D2", "A2", "F#4 A4 E5"), "G": ("G1", "D2", "B3 D4 A4"), "A": ("A1", "E2", "C#4 E4 B4"),
       "Asus": ("A1", "E2", "D4 E4 B4"), "Bm": ("B1", "F#2", "D4 F#4 C#5"), "Em": ("E2", "B2", "G3 B3 F#4")}
INTRO = ["D", "D", "G", "A"]
SEA = ["Bm", "Bm", "G", "G", "Em", "Em", "A", "A"]
OUTRO = ["G", "G", "Asus", "A"]
LISS_BARS = LS.CHORDS[2:18]     # her bars 3-18, under T_A, T_A2 and T_B
STAR_LH = HD.LH[4:12]           # haluna_dawn's bars 5-12: the harmony under RH_CELL (one of its bars = two here)
STAYS = ["D6", "A5", "E6"]
SEA_CELL = 4                    # C: the star-path's first four notes (F# E D E), two octaves down
## where the thrum accents its eighths (3+3+2) and which upper tone it plays (0 low .. 2 high, 3 the fifth up)
THRUM = [(0, 1.0), (1, 0.7), (2, 0.8), (0, 0.95), (1, 0.7), (2, 0.8), (3, 0.9), (1, 0.7)]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def chord(bar: int) -> tuple[int, int, list[int]]:
    """(bass, fifth, upper tones) in MIDI for a bar."""
    sec, i = SECTION[bar - 1], bar - 1
    if sec in ("A", "A2"):
        ps = [n(p) for p in STAR_LH[(i - (4 if sec == "A" else 44)) // 2].split()]
        return ps[0], ps[1], [p + 12 for p in ps[1:]]
    if sec == "B":
        b1, b3, up = LS.VOICING[LISS_BARS[i - 20]]
        return n(b1), n(b3), [n(b3) + 12] + [n(p) for p in up.split()]
    name = {"I": INTRO, "C": SEA, "O": OUTRO}[sec][(i - {"I": 0, "C": 36, "O": 60}[sec])]
    b1, b3, up = OWN[name]
    return n(b1), n(b3), [n(p) for p in up.split()]


def sail_fill(g) -> np.ndarray:
    """The sails filling: a swell of low air and, at its crest, the cloth's snap. Mono."""
    N = int(2.6 * SR)
    t = np.arange(N) / SR
    env = np.clip(t / 0.55, 0, 1) ** 2 * np.exp(-np.maximum(t - 0.55, 0) / 0.7)
    y = filt(g.standard_normal(N), [bq_lowpass(520, 0.7), bq_highpass(60, 0.7)]) * env
    k = int(0.05 * SR)
    s = int(0.5 * SR)
    snap = filt(g.standard_normal(k), [bq_bandpass(1400, 1.2)]) * np.exp(-np.arange(k) / (0.008 * SR))
    y[s:s + k] += 0.5 * snap
    return y


def star_path(start_bar: int, notes: list | None = None) -> list[tuple[int, float, float]]:
    """The star-path (RH_CELL) in half time from a bar: [(midi, start s, dur s)]."""
    out, pos = [], t_of(start_bar)
    for p, beats in (notes if notes is not None else HD.RH_CELL):
        d = beats * HALF_TIME * BEAT
        if p is not None:
            out.append((n(p), pos, d))
        pos += d
    return out


def add_sky(mx: LoopMixer, line: list, seed: int, vel: float) -> None:
    g = rng(seed)
    for j, (m, t0, d) in enumerate(line):
        long_ = d >= 4 * BEAT
        x = breath_flute(m, d * 0.97 + 0.04, vel * float(g.uniform(0.95, 1.04)) * (1.06 if long_ else 1.0),
                         seed=seed + j, breath=0.42, scoop_cents=30.0, vib_cents=11.0, vib_rate=4.8,
                         swell=0.25 if long_ else 0.08, attack=0.14, release=0.7, beta=0.5)
        mx.add("sky", x, t0 - V.FLUTE_PRE + float(g.normal(0, 0.006)), pan=-0.08)


def add_cittern(mx: LoopMixer, body: np.ndarray, bars: list, start_bar: int, seed: int, vel: float) -> None:
    """Liss's tune on her cittern (liss_theme.add_line's voice, at this cue's bars)."""
    g = rng(seed)
    for i, bar in enumerate(bars):
        pos = 0.0
        for p, beats in bar:
            if p is not None:
                d = beats * BEAT
                v = vel * g.uniform(0.92, 1.05) * (1.08 if pos in (0.0, 2.0) else 1.0)
                x = string_pluck(n(p), d * 0.92, v, seed=seed + 100 * i + int(pos * 4), pick_pos=0.08, t60=1.7,
                                 B=4e-5, max_f=9000.0, release=0.09)
                mx.add("cittern", fft_convolve(x, body)[: len(x) + 3000],
                       t_of(start_bar + i, pos) + float(g.normal(0, 0.005)), pan=0.15)
            pos += beats


def add_cittern_line(mx: LoopMixer, body: np.ndarray, line: list, seed: int, vel: float) -> None:
    """The cittern on the star-path an octave down (A', second half): long notes re-struck on the beat."""
    g = rng(seed)
    for j, (m, t0, d) in enumerate(line):
        hits = max(1, int(round(d / (2 * BEAT))))
        for h in range(hits):
            x = string_pluck(m - 12, min(d - 2 * BEAT * h, 2 * BEAT) * 0.95, vel * (1.0 if h == 0 else 0.7)
                             * g.uniform(0.93, 1.05), seed=seed + 10 * j + h, pick_pos=0.08, t60=1.9, B=4e-5,
                             max_f=9000.0, release=0.1)
            mx.add("cittern", fft_convolve(x, body)[: len(x) + 3000], t0 + 2 * BEAT * h + float(g.normal(0, 0.005)),
                   pan=0.15)


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = LS.cittern_body(SEED + 5)
    mx.add("wind", V.wind(LOOP_S, SEED + 3, lo_hz=320.0, hi_hz=2300.0, gusts=(8, 17, 5), hi_level=0.32), 0.0)
    mx.add("stays", V.cord_song(LOOP_S, [n(p) for p in STAYS], SEED + 4, q=50.0), 0.0)
    for bar in range(1, BARS + 1):
        sec = SECTION[bar - 1]
        bass, fifth, up = chord(bar)
        x = pad_chord(up, BAR * 0.96, 0.42 if sec != "C" else 0.5, seed=SEED + 200 + bar, voices=4, attack=0.9,
                      release=1.4, width=0.9)
        mx.add("pad", x, t_of(bar) - 0.2)
        for beat, p, v in ((0, bass, 0.6), (2, fifth, 0.45)):
            if sec == "C" and beat == 2:
                continue
            x = string_pluck(p, 1.9 * BEAT, v * g.uniform(0.94, 1.04), seed=SEED + 400 + 4 * bar + beat,
                             pick_pos=0.16, t60=2.4, B=8e-5, max_f=3000.0, release=0.14)
            mx.add("low", x, t_of(bar, beat) + float(g.normal(0, 0.004)), pan=-0.1)
        # the rigging's thrum: eighths 3+3+2 (quarters only under Liss's tune, none over the sea)
        tones = up[:3] + [fifth + 24]
        for e, (k, acc) in enumerate(THRUM):
            if sec == "C" or (sec == "B" and e % 2):
                continue
            v = 0.34 * acc * g.uniform(0.9, 1.06) * (0.8 if sec in ("I", "O") else 1.0)
            x = string_pluck(tones[k] + 12, 0.45 * BEAT, v, seed=SEED + 1000 + 8 * bar + e, pick_pos=0.1, t60=0.9,
                             B=6e-5, max_f=8000.0, release=0.06)
            mx.add("thrum", x, t_of(bar, e / 2) + float(g.normal(0, 0.004)), pan=0.4 - 0.08 * k)
        # the lift: a soft frame drum on 1 and the and of 2; a far big drum every eight bars
        if sec in ("A", "B", "A2"):
            for beat, stroke, v in ((0, "dum", 0.2), (1.5, "tek", 0.1), (3, "ghost", 0.07)):
                x = frame_drum(stroke, v * float(g.uniform(0.9, 1.08)), variant=bar, size=1.1, seed=SEED + 1)
                mx.add("step", x, t_of(bar, beat) + float(g.normal(0, 0.006)), pan=0.08)
        if bar % 8 == 5 and sec != "C":
            mx.add("drum", big_drum(0.3, variant=bar, seed=SEED + 2), t_of(bar))
        if bar % 4 == 1 and sec != "C":
            mx.add("sail", sail_fill(rng(SEED + 3000 + bar)), t_of(bar) - 0.45, pan=-0.3 if bar % 8 == 1 else 0.3)
    # A: the star-path
    add_sky(mx, star_path(5), SEED + 600, 0.55)
    # B: Liss's theme, her A, A' and B, on her cittern; the vanes knocking her wheel's seven against eight
    add_cittern(mx, body, LS.T_A, 21, SEED + 700, 0.62)
    add_cittern(mx, body, LS.T_A2, 25, SEED + 800, 0.62)
    add_cittern(mx, body, LS.T_B, 29, SEED + 900, 0.66)
    for e in range(16 * 8):
        k = e % len(LS.WHEEL)
        v = (0.5 if k == 0 else 0.34) * g.uniform(0.88, 1.06)
        mx.add("vanes", LS.paddle(n(LS.WHEEL[k]) + 12, v, SEED + 2000 + 13 * k + (e % 3)),
               t_of(21) + e * E8 + LS.WHEEL_LAG_S, pan=-0.45 + 0.08 * k)
    # C: the sea below glows: the star-path's first cell, two octaves down, under glass
    for j, (m, t0, d) in enumerate(star_path(37, HD.RH_CELL[:SEA_CELL])):
        x = metallophone_note(m - 24, 0.42, seed=SEED + 300 + j, decay=7.0, hardness=0.2, ombak_hz=3.2)
        mx.add("metal", x, t0, pan=0.2)
    for j, (bar, p) in enumerate(((37, "F#5"), (39, "D5"), (41, "B4"), (43, "C#5"))):
        mx.add("glass", V.glass(n(p), 2 * BAR - 0.6, 0.5, SEED + 320 + j), t_of(bar) - V.GLASS_PRE, pan=-0.3)
    # A': the star-path again; glass on its long notes an octave up, then Liss's cittern an octave down
    line = star_path(45)
    add_sky(mx, line, SEED + 640, 0.58)
    for j, (m, t0, d) in enumerate(line):
        if t0 < t_of(53) and d >= 4 * BEAT:
            mx.add("glass", V.glass(m + 12, d - 0.3, 0.32, SEED + 340 + j), t0 - V.GLASS_PRE, pan=0.35)
    add_cittern_line(mx, body, [x for x in line if x[1] >= t_of(53) - 1e-6], SEED + 950, 0.34)


## Bus gains from measured bus loudness (render(stats=...)["bus_lufs"], LU against the sky flute over the loop): the
## cittern -3.7 (it leads B alone, and its plucks peak high), the pad -9, the low string -10, the thrum -11, the wind
## -12, the stays -18, the frame drum and the sails -14, the big drum -16, the vanes -15, glass and the low
## metallophone -10 where they play. Measured section loudness (LUFS): deck -21.4, A -14.7, B -17.5, the sea -19.3,
## A' -14.2, the deck again -20.9.
GAINS = {"sky": 0.0, "cittern": 3.0, "pad": 3.3, "low": -0.7, "thrum": 9.3, "wind": 7.5, "stays": -6.3, "step": 3.0,
         "drum": -5.9, "sail": -12.6, "vanes": -11.9, "glass": -10.8, "metal": -2.6}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    G = GAINS
    mx.bus("sky", G["sky"], send=0.42, process=lambda x: filt(x, [bq_highpass(240, 0.7), bq_peak(2600, 1.5, 1.0),
                                                                  bq_lowpass(8000, 0.7)]))
    mx.bus("cittern", G["cittern"], send=0.25, process=lambda x: filt(x, [bq_highpass(180, 0.7),
                                                                          bq_peak(3200, 1.0, 1.0)]))
    mx.bus("pad", G["pad"], send=0.5, process=lambda x: string_body(x, cutoff=1900.0))
    mx.bus("low", G["low"], send=0.15, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1600, 0.7)]))
    mx.bus("thrum", G["thrum"], send=0.3, process=lambda x: filt(x, [bq_highpass(300, 0.7), bq_lowpass(7000, 0.7)]))
    mx.bus("wind", G["wind"], send=0.12)
    mx.bus("stays", G["stays"], send=0.3)
    mx.bus("step", G["step"], send=0.35, process=lambda x: filt(x, [bq_lowpass(2400, 0.7)]))
    mx.bus("drum", G["drum"], send=0.6, process=lambda x: filt(x, [bq_lowpass(1100, 0.7)]))
    mx.bus("sail", G["sail"], send=0.2)
    mx.bus("vanes", G["vanes"], send=0.2, process=lambda x: filt(x, [bq_highpass(200, 0.7), bq_lowpass(6000, 0.7)]))
    mx.bus("glass", G["glass"], send=0.6)
    mx.bus("metal", G["metal"], send=0.5)
    build(mx)
    sky = ModFDNReverb(rt60=2.8, rt60_high=1.2, predelay=0.05, size=1.4, mod_depth=8.0, mod_rate=0.35,
                       early_level=0.1, lowcut=120.0, seed=SEED % 9973)
    return V.finish(mx, "the_kite", out_path, BPM, 4, BARS, LEAD_IN_S, TARGET_LUFS, sky, -3.0, verbose, stats,
                    quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
