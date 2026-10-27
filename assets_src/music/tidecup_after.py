"""`tidecup_after`: Ch7, after the Bell (M3-AUD-822; act1_ch07.md B07, and its reprise in B10): about 57 s,
through-composed.

Original composition for this project (SPEC §2, §9). The string line and its harmony below were written for this
scene and are not derived from any existing tune. Original-material check: the line (A G A | C B | A F | E, then
C D E | D B | E D C B | C, then F E D | C A | B D G | E) shares no phrase with the Tidecup's song (tidecup_match.py
SONG_A), the galleries' song (tamsule_bell_galleries.py) or the Hush (hush_theme_v2.py MEL_A), and follows no melody
we know. The style evoked is a slow string elegy; nothing is quoted.

The brief: "Warm strings over the crowd, unresolved, ending on a held note." The match is over. Win or lose (the cue,
like the scene, never knows which), Oruvel's side withdraws: "Win or lose, she'd have yelled at us the same." Tavi
leaves through a crowd that parts for him, and Rhen stays in the pool a moment, the band on his arm. In B10 it comes
back as the trader pulls away from Tamsule. So the cue is warm, and it does not close: it opens on F major (the
subdominant), never sits on A minor's root, and its last chord, F major seventh, lets go and leaves the violins
alone on E, the seventh of that chord and the fifth of the home key, held until it fades.

A minor (Aeolian; the harmony is F C/E Dm7 Am/C | F G Em7 Am | Dm F/A G Fmaj7), 4/4 at 58 BPM (a bar is 4.14 s) with
a small ritardando into the last bar, 12 bars and the held note.

Ensemble (all synthesized; no samples):
* the line (synth.pad's detuned saw section through string_body, one note at a time, legato): cellos in bars 1-4,
  violas an octave up in 5-8, violins two octaves up in 9-12, and the violins' held E;
* the inner strings, three voices, above the cellos and under the violins;
* the low strings: basses and cellos on the root and fifth;
* the Bell (synth.bells.tower_bell, the Tamsule Bell's prime A2, padded: dark 0.35), once at the start, far;
* the crowd in the Bell, after the match: a floor of murmur and far voices (assets_src/sfx/reefball_sfx.py's own
  talkers and babble, so it is the same crowd), warm and thinning, gone by bar 7.

Form: 1-4 the cellos, the crowd still talking | 5-8 the violas; the crowd thins away | 9-12 the violins, the widest
point, falling back | 13 F major seventh lets go and the E is held alone.

Render:  python3 assets_src/music/tidecup_after.py   (or tools/audio/render_all.py --only tidecup_after)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, os.path.join(ROOT, "assets_src", "sfx"))

import numpy as np  # noqa: E402

from synth.bells import tower_bell  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _mod(name: str, folder: str = HERE):
    spec = importlib.util.spec_from_file_location(name, os.path.join(folder, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HUSH = _mod("hush_theme_v2")            # its per-bus loudness meter (_bus_stats)
CROWD = _mod("reefball_sfx", os.path.join(ROOT, "assets_src", "sfx"))

OUT = os.path.join(ROOT, "assets", "audio", "music", "tidecup_after.ogg")
SEED = 20261824
TARGET_LUFS = -16.0
BPM = 58.0
BEAT = 60.0 / BPM
BARS = 12
RIT_FROM = 11                 # the ritardando: bars 11-12 broaden, to RIT_MAX x the beat by the held note
RIT_MAX = 1.12
HOLD_S = 6.5                  # the violins' last E, alone, after the chord lets go
LENGTH = 57.5
CROWD_END = 26.0              # the crowd has thinned away by here (bar 7)

## (low strings, inner strings) per bar
CHORDS = [
    ("F2 C3", "C4 F4 A4"), ("E2 G2", "C4 E4 G4"), ("D2 A2", "C4 F4 A4"), ("C2 G2", "C4 E4 A4"),
    ("F2 C3", "F3 A3 A4"), ("G2 D3", "G3 B3 G4"), ("E2 B2", "G3 B3 D4"), ("A2 E3", "A3 E4"),
    ("D2 A2", "F3 A3 D4"), ("A2 F3", "A3 C4 F4"), ("G2 D3", "B3 D4 G4"), ("F2 C3", "A3 C4 F4"),
]
## the line: one list per bar of (pitch, beats); bars 5-8 sound an octave up, bars 9-12 two octaves up (OCTAVE)
LINE = [
    [("A3", 2), ("G3", 1), ("A3", 1)], [("C4", 3), ("B3", 1)], [("A3", 2), ("F3", 2)], [("E3", 4)],
    [("C3", 2), ("D3", 1), ("E3", 1)], [("D3", 3), ("B2", 1)], [("E3", 1.5), ("D3", .5), ("C3", 1), ("B2", 1)],
    [("C3", 4)],
    [("F3", 2), ("E3", 1), ("D3", 1)], [("C3", 2), ("A2", 2)], [("B2", 2), ("D3", 1), ("G3", 1)], [("E3", 4)],
]
OCTAVE = [0] * 4 + [12] * 4 + [24] * 4
## the dynamic arc, per bar (the line's velocity; the chords follow it)
ARC = [0.50, 0.54, 0.56, 0.50, 0.56, 0.62, 0.66, 0.60, 0.70, 0.74, 0.66, 0.58]


def beat_len(bar: int) -> float:
    if bar < RIT_FROM:
        return BEAT
    k = (bar - RIT_FROM + 1) / (BARS - RIT_FROM + 1)
    return BEAT * (1.0 + (RIT_MAX - 1.0) * k)


def t_of(bar: int, beat: float = 0.0) -> float:
    """Seconds from the start to `beat` (0-based) of 1-based `bar` (bar 13 is the held note)."""
    t = 0.6
    for b in range(1, bar):
        t += 4 * beat_len(b)
    return t + beat * beat_len(bar)


def add_line(mx: Mixer) -> None:
    g = rng(SEED + 1)
    notes = []
    for i, bar in enumerate(LINE, start=1):
        pos = 0.0
        for p, beats in bar:
            notes.append((t_of(i, pos), beats * beat_len(i), n(p) + OCTAVE[i - 1], ARC[i - 1]))
            pos += beats
    last = notes[-1]
    notes[-1] = (last[0], t_of(BARS + 1) - last[0] + HOLD_S, last[2], last[3])
    for k, (t0, d, m, v) in enumerate(notes):
        legato = 0.18 if k < len(notes) - 1 else 0.0
        x = pad_chord([m], d + legato, vel=v * g.uniform(0.95, 1.04), seed=SEED + 100 + k, voices=4,
                      spread_cents=6.0, attack=0.35 if k else 0.8, release=1.2 if k < len(notes) - 1 else 2.2,
                      width=0.45)
        if k == len(notes) - 1:               # the held E fades over its last seconds
            tt = np.arange(len(x)) / SR
            x *= np.clip(1.0 - (tt - (d - 3.5)) / 3.5, 0, 1)[:, None] ** 1.5
        mx.add("line", x, t0 - 0.12)


def add_chords(mx: Mixer) -> None:
    g = rng(SEED + 2)
    for i, (low, mid) in enumerate(CHORDS, start=1):
        d = 4 * beat_len(i)
        v = ARC[i - 1]
        last = i == BARS
        hold = d + (0.9 * BEAT if last else 0.25)
        x = pad_chord([n(p) for p in mid.split()], hold, vel=v * g.uniform(0.95, 1.04), seed=SEED + 200 + i,
                      voices=4, spread_cents=8.0, attack=0.6, release=1.6 if last else 1.0, width=0.8)
        mx.add("inner", x, t_of(i) - 0.15)
        y = pad_chord([n(p) for p in low.split()], hold, vel=v * g.uniform(0.95, 1.04), seed=SEED + 300 + i,
                      voices=3, spread_cents=6.0, attack=0.5, release=1.8 if last else 1.0, width=0.5)
        mx.add("low", y, t_of(i) - 0.1)


def add_crowd(mx: Mixer) -> None:
    """The bowl after the match: a murmur floor and far talkers, warm, thinning to nothing by CROWD_END."""
    g = rng(SEED + 3)
    L = int(CROWD_END * SR)
    t = np.arange(L) / SR
    thin = np.clip(1.0 - t / CROWD_END, 0, 1) ** 1.5
    mx.add("crowd", 0.25 * CROWD.babble(g, L) * thin[:, None], 0.0)      # the floor about -12 dB under the talkers
    for _ in range(22):
        pan = float(g.uniform(-1, 1))
        lvl = float(g.uniform(0.4, 1.0))
        high = bool(g.random() < 0.5)
        tt = float(g.uniform(0, 2.0))
        while tt < CROWD_END - 1.5:
            p = CROWD.phrase(g, high, False)
            mx.add("crowd", p, tt, pan=pan, gain=lvl * (1.0 - tt / CROWD_END) ** 1.5)
            tt += len(p) / SR + float(g.uniform(0.4, 2.0))


# Bus gains from measured bus loudness (HUSH._bus_stats, gated integrated per bus), for these levels relative to the
# line (0 LU): inner strings -5, low strings -6, the crowd -12 (over the bars it sounds in), the Bell -10.
GAINS = {"line": 0.0, "inner": -4.5, "low": -3.5, "crowd": -28.3, "bell": -14.7}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = Mixer(LENGTH + 0.5)
    mx.bus("line", GAINS["line"], send=0.35, process=lambda x: string_body(x, cutoff=2600.0))
    mx.bus("inner", GAINS["inner"], send=0.45, process=lambda x: string_body(x, cutoff=1900.0))
    mx.bus("low", GAINS["low"], send=0.3, process=lambda x: string_body(x, cutoff=1300.0))
    mx.bus("crowd", GAINS["crowd"], send=0.5, process=lambda x: filt(x, [bq_highpass(160, 0.7),
                                                                          bq_lowpass(1600, 0.7)]))
    mx.bus("bell", GAINS["bell"], send=0.6)
    add_line(mx)
    add_chords(mx)
    add_crowd(mx)
    mx.add("bell", tower_bell(n("A2"), 0.5, seed=SEED + 4, t60=9.0, dark=0.35), 0.3, pan=-0.2)
    hall = ModFDNReverb(rt60=2.8, rt60_high=1.2, predelay=0.03, size=1.2, mod_depth=8.0, mod_rate=0.5,
                        early_level=0.25, lowcut=90.0, seed=SEED % 9973)
    st: dict = {}
    HUSH._bus_stats(mx, st)
    y = mx.render(reverb=hall, reverb_return_db=-2.0)[: int(LENGTH * SR)]
    k = int(1.5 * SR)
    y[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, y, quality=3.0)
    m = measure(y)
    if stats is not None:
        stats.update(st)
    if verbose:
        lead = st.get("bus_line_lufs", 0.0)
        print(f"tidecup_after: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f"  (held E from {t_of(BARS + 1):.1f} s)")
        print("  buses (LU vs the line)", {k[4:-5]: round(v - lead, 1) for k, v in st.items()})
    return m


if __name__ == "__main__":
    render()
