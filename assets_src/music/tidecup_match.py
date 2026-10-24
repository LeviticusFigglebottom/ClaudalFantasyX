"""`tidecup_match`: the Tidecup's story Reefball match (M3-AUD-02; act_outline Ch7, N-12): a 68.6 s seamless loop.

Original composition for this project (SPEC §2, §9). The melody, bass line, ostinato and drum patterns below were
written for this match and are not derived from any existing tune or chant. The brief: the match opens with each
captain naming one person the sea has taken, and Oruvel's side plays "for the ones who didn't come up". It is a
sports theme that is also a lament, and never triumphant. So the piece is built from two things that pull against
each other: a game's drive underneath (a steady 112 BPM pulse, the frame drums and big drum, a busy plucked ostinato
and a walking bass), and over it a slow minor song in long notes that never lands on its home note while the
drums are going. The arena is the Tamsule Bell, so a low bronze bell (prime A2) marks each section, and a soft
"salt-glass" bar (a metallophone with a light mallet and a slow shimmer) doubles the song's long notes.

A minor (Aeolian, with E major as the lament's half-close in B), 4/4 at 112 BPM (a bar is 2.143 s), 32 bars.

Ensemble (all synthesized; no samples):
* breath flute: the song, mid register, with a little more breath than Haluna's and slower vibrato;
* salt-glass bars: an octave over the song's held notes in A', and alone in the tail;
* plucked strings (synth.electric.string_pluck through a small body) in running eighths: the game's motion;
* fingered bass on the roots, quarter notes with a pickup;
* frame drums (dum, tek, slap, ghost) and the big drum; in B the big drum takes every beat (the crowd's feet), with
  jingles on the off-beats. No handclap pattern borrowed from any stadium chant;
* the Bell (synth.bells.tower_bell, padded: dark=0.35) at bars 1, 13 and 29, softly at 21;
* the crowd, humming (the Order hums; only Cantors sing, bible §4): a low congregation hum on the song's skeleton
  through B, mixed back.

Form (bars): 1-4 the teams take the water (drums, bass, ostinato, the Bell) | 5-12 A (the song) | 13-20 B (higher;
the crowd hums, the big drum on every beat) | 21-28 A' (the song with the glass) | 29-32 the naming: the drums
drop to the big drum's heartbeat on 1 and 3, the Bell, the glass and the flute's last cell; the harmony (F Dm E E)
leans back into bar 1's A minor.

Render:  python3 assets_src/music/tidecup_match.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.bells import tower_bell  # noqa: E402
from synth.drums import big_drum, frame_drum, jingle  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, fft_convolve, filt, rng  # noqa: E402
from synth.electric import bass_note, string_pluck  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "tidecup_match.ogg")
SEED = 20261201
TARGET_LUFS = -16.0
BPM = 112.0
BEAT = 60.0 / BPM
E8 = BEAT / 2
BAR = 4 * BEAT
BARS = 32
LOOP_S = BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065

CHORDS = (["Am", "Am", "F", "G"]
          + ["Am", "F", "C", "G", "Am", "F", "Dm", "Em"]
          + ["F", "G", "Am", "Am", "F", "G", "E", "E"]
          + ["Am", "F", "C", "G", "Am", "F", "Dm", "Em"]
          + ["F", "Dm", "E", "E"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 8 + ["A2"] * 8 + ["T"] * 4
ROOTS = {"Am": "A1", "F": "F1", "C": "C2", "G": "G1", "Dm": "D2", "Em": "E1", "E": "E1"}
## chord tones for the plucked ostinato (root, third, fifth, octave), mid register
TONES = {"Am": ["A3", "C4", "E4", "A4"], "F": ["F3", "A3", "C4", "F4"], "C": ["C4", "E4", "G4", "C5"],
         "G": ["G3", "B3", "D4", "G4"], "Dm": ["D4", "F4", "A4", "D5"], "Em": ["E3", "G3", "B3", "E4"],
         "E": ["E3", "G#3", "B3", "E4"]}
OSTINATO = [0, 2, 1, 2, 3, 2, 1, 2]           # indices into TONES per eighth

## the song: one list per bar of (pitch, beats); None is a rest
SONG_A = [
    [("A4", 2), ("C5", 1), ("B4", 1)],
    [("A4", 3), ("G4", .5), ("F4", .5)],
    [("E4", 1.5), ("G4", .5), ("C5", 2)],
    [("B4", 3), (None, 1)],
    [("C5", 1.5), ("D5", .5), ("E5", 2)],
    [("F5", 1), ("E5", 1), ("C5", 1), ("A4", 1)],
    [("D5", 1.5), ("C5", .5), ("A4", 1), ("F4", 1)],
    [("E4", 3), (None, 1)],
]
SONG_B = [
    [("A5", 2), ("G5", 1), ("F5", 1)],
    [("E5", 2), ("D5", 1), ("B4", 1)],
    [("C5", 1), ("E5", 1), ("A5", 2)],
    [("G5", 1), ("E5", 1), ("D5", 1), ("C5", 1)],
    [("C5", 2), ("F5", 2)],
    [("E5", 1.5), ("D5", .5), ("B4", 2)],
    [("B4", 1), ("C5", 1), ("B4", 1), ("G#4", 1)],
    [("B4", 3), (None, 1)],
]
TAIL = [
    [("A4", 2), ("G4", 2)],
    [("F4", 3), ("E4", 1)],
    [("E4", 4)],
    [(None, 4)],
]
## the crowd's hum: the song's skeleton through B, one pitch per bar (men's register)
HUM_B = ["A3", "B3", "C4", "C4", "A3", "B3", "B3", "G#3"]


def t_of(bar: int, beat: float = 0.0) -> float:
    """Start time (s) of `beat` (0-based) in 1-based `bar`."""
    return (bar - 1) * BAR + beat * BEAT


def small_body(seed: int, sr: int = SR) -> np.ndarray:
    """A small wooden body (a few damped modes and a bright click) as an impulse response."""
    g = rng(seed)
    t = np.arange(int(0.22 * sr)) / sr
    ir = np.zeros(len(t))
    ir[0] = 1.0
    for f, q, a in ((120.0, 11, 0.8), (240.0, 13, 0.7), (430.0, 10, 0.45), (640.0, 9, 0.3), (1300.0, 6, 0.2),
                    (2700.0, 4, 0.1)):
        d = q / (np.pi * f)
        ir += a * np.sin(2 * np.pi * f * t + g.uniform(0, 0.4)) * np.exp(-t / d) * 0.08
    return ir / np.abs(ir).max()


def add_song(mx: LoopMixer, bars: list, start_bar: int, seed: int, vel: float, pan: float = -0.05,
             glass: bool = False) -> None:
    """The flute line; with glass=True the salt-glass bar doubles its notes of 2 beats or more an octave up."""
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, beats in bar:
            d = beats * BEAT
            if p is None:
                pos += d
                first = True
                continue
            v = vel * g.uniform(0.93, 1.04) * (1.05 if beats >= 2 else 1.0)
            x = breath_flute(n(p), d * 0.95 + 0.03, v, seed=seed + int(round(pos * 1000)), breath=0.42,
                             scoop_cents=45.0 if first else 15.0, vib_cents=11.0 if beats >= 2 else 4.0,
                             vib_rate=4.4, swell=0.22 if beats >= 3 else 0.0, attack=0.06 if first else 0.035,
                             release=0.28, beta=0.55)
            mx.add("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.004)), pan=pan)
            if glass and beats >= 2:
                y = metallophone_note(n(p) + 12, 0.30, seed=seed + 31 * int(round(pos * 100)), decay=3.2,
                                      hardness=0.18, ombak_hz=2.2)
                mx.add("glass", y, pos + 0.01, pan=0.45)
            pos += d
            first = False


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    body = small_body(SEED + 5)
    for bar, (chord, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        tones = TONES[chord]
        # plucked ostinato in eighths (thinner in the tail: only the first half of each bar)
        for e, k in enumerate(OSTINATO):
            if sec == "T" and e >= 4:
                break
            v = (0.46 if e in (0, 4) else 0.34) * g.uniform(0.9, 1.05) * (0.8 if sec == "T" else 1.0)
            x = string_pluck(n(tones[k]), E8 * 1.6, v, seed=SEED + 20000 + 10 * bar + e, pick_pos=0.16, t60=1.6,
                             mute=0.25, max_f=5000.0, release=0.06)
            mx.add("pluck", fft_convolve(x, body)[: len(x) + 3000], t_of(bar, e / 2) + float(g.normal(0, 0.004)),
                   pan=0.22 if e % 2 else 0.12)
        # bass: quarter notes on the root (octave on beat 3), a pickup on the and of 4; whole notes in the tail
        root = n(ROOTS[chord])
        if sec == "T":
            bass = [(0.0, root, 0.55, 3.6 * BEAT)]
        elif sec == "I" and bar <= 2:
            bass = [(0.0, root, 0.5, 1.8 * BEAT), (2.0, root, 0.36, 1.8 * BEAT)]
        else:
            bass = [(0.0, root, 0.55, 0.9 * BEAT), (1.0, root, 0.36, 0.9 * BEAT), (2.0, root + 12, 0.42, 0.9 * BEAT),
                    (3.0, root, 0.36, 0.45 * BEAT), (3.5, root + 7, 0.32, 0.45 * BEAT)]
        for b, m, v, d in bass:
            x = bass_note(m, d, v * g.uniform(0.94, 1.04), seed=SEED + 30000 + int(round(100 * (bar + b / 4))),
                          mute=0.25)
            mx.add("bass", x, t_of(bar, b) + 0.004, pan=0.0)
        # drums
        if sec == "T":
            hits = [(0.0, "big", 0.62), (2.0, "big", 0.45), (3.5, "ghost", 0.14)]
        else:
            hits = [(0.0, "dum", 0.55), (0.5, "ghost", 0.16), (1.0, "slap", 0.34), (1.5, "ghost", 0.18),
                    (2.0, "dum", 0.42), (2.5, "tek", 0.26), (3.0, "slap", 0.38), (3.5, "tek", 0.22),
                    (0.0, "big", 0.55), (1.5, "big", 0.30)]
            if sec == "B":
                hits += [(1.0, "big", 0.42), (2.0, "big", 0.50), (3.0, "big", 0.42)]
            if sec == "I" and bar <= 2:
                hits = [(0.0, "big", 0.58), (2.0, "big", 0.40), (1.0, "tek", 0.22), (3.0, "tek", 0.24),
                        (3.5, "ghost", 0.15)]
            if bar == 28:      # a short roll into the naming
                hits += [(3.25, "tek", 0.22), (3.5, "slap", 0.30), (3.75, "tek", 0.26)]
        for b, stroke, v in hits:
            if stroke == "big":
                x = big_drum(v * g.uniform(0.92, 1.05), variant=int(bar * 4 + b), seed=SEED + 1)
                mx.add("drums", x, t_of(bar, b), pan=0.0)
            else:
                x = frame_drum(stroke, v * g.uniform(0.9, 1.08), variant=int(bar * 8 + 2 * b), seed=SEED + 2)
                mx.add("drums", x, t_of(bar, b) + float(g.normal(0, 0.004)), pan=-0.15 if stroke == "tek" else 0.08)
        if sec == "B":
            for e in range(8):
                if e % 2:
                    x = jingle(0.26 if e in (3, 7) else 0.18, variant=bar + e, open_=(e == 7), seed=SEED + 3)
                    mx.add("drums", x, t_of(bar, e / 2) + float(g.normal(0, 0.003)), pan=0.4)
    # the Bell
    for bar, v in ((1, 0.7), (13, 0.8), (21, 0.5), (29, 0.75)):
        x = tower_bell(n("A2"), v, seed=SEED + 400 + bar, t60=8.5, dark=0.35)
        mx.add("bell", x, t_of(bar), pan=-0.08)
    # the song
    add_song(mx, SONG_A, 5, SEED + 600, 0.50)
    add_song(mx, SONG_B, 13, SEED + 700, 0.56)
    add_song(mx, SONG_A, 21, SEED + 800, 0.52, glass=True)
    add_song(mx, TAIL, 29, SEED + 900, 0.42, pan=0.05)
    # the glass alone in the tail: the song's first two notes, high and far
    for i, (p, b) in enumerate((("E6", 0.0), ("C6", 2.0), ("A5", 0.0), ("B5", 2.0))):
        x = metallophone_note(n(p), 0.26, seed=SEED + 1300 + i, decay=3.4, hardness=0.15, ombak_hz=2.0)
        mx.add("glass", x, t_of(29 + 2 * (i // 2), b), pan=0.5 - 0.3 * (i % 2))
    # the crowd hums through B (and lets go over the first bar of A')
    line = [(n(p), BAR) for p in HUM_B] + [(n("A3"), BAR)]
    crowd = hum_ensemble(line, voices=12, seed=SEED + 11, register="low", spread=0.95)
    env = np.ones(len(crowd))
    k = int(2.5 * SR)
    env[:k] = np.linspace(0, 1, k) ** 2
    tail_from = int(8 * BAR * SR)
    env[tail_from:] = np.exp(-np.arange(len(env) - tail_from) / SR / 0.9)
    mx.add("hum", crowd * env[:, None], t_of(13) - 0.15)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
# flute (0 LU): plucked ostinato -9, bass -8, drums -5 (the game's drive), Bell -6, glass -12, crowd hum -10 (measured
# over the whole loop; it sounds only in B).
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=9.0)
    mx.bus("flute", 0.0, send=0.30, process=lambda x: filt(x, [bq_highpass(180, 0.7), bq_peak(2400, 1.5, 1.0)]))
    mx.bus("glass", -1.5, send=0.55)
    mx.bus("pluck", -13.9, send=0.20, process=lambda x: filt(x, [bq_highpass(110, 0.7), bq_lowpass(5200, 0.7)]))
    mx.bus("bass", -2.7, send=0.04, process=lambda x: filt(x, [bq_lowpass(1000, 0.7)]))
    mx.bus("drums", -3.2, send=0.15)
    mx.bus("bell", -9.6, send=0.40)
    mx.bus("hum", -11.3, send=0.70)
    build(mx)
    hall = ModFDNReverb(rt60=2.6, rt60_high=1.1, predelay=0.03, size=1.1, mod_depth=9.0, mod_rate=0.5,
                        early_level=0.30, lowcut=110.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=hall, reverb_return_db=-3.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=3.5, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4, extra={"loop_bars": BARS})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"tidecup_match: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
