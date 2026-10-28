"""`keth_pass`: Ch12, Keth Pass, the mountain route into the Ullar Heights (M3-AUD-841 final of the M3-AUD-804
sketch; act_outline Ch12, bible §5.7): a 125.2 s seamless loop.

Original composition for this project (SPEC §2, §9). Original-material check: the tune and the verse are the
sketch's (assets_src/music/keth_pass.py, loaded here, never retyped): one cell of our own (a fall from the fifth to
the third, B-A-G, then the long tonic) and its climb back (G-A-B to D), split between two pipes in hocket, and the low
pipe's verse. What this final adds grows out of that cell and was written for it: in the development the cell is
carried up a fourth onto A minor (E-D-C to A, and the climb C-D-E to G) by one high pipe, and the pass answers it a
bar later from the far side of the valley (a soft echo, left then right); the verse's return gets a held counter-pipe
above it (E | F# | D | E). The style evoked is a highland one (a hocketed panpipe over an open-fifth drone), quoting
no tune and no real instrument's repertoire. Nothing is borrowed from another cue.

The brief: the pass-cords strung across every pass, where the Ullari tie a knot for their dead and walk on without
looking back; thin air and enormous skies; in the cold, Toma notices that Kerrid's breath doesn't fog. Cold,
wind-borne and wide: the pipes breathy and high, the space huge, the wind never stopping, the cords whistling in it.
The echo section is the pass's size: one voice, and the mountains giving it back.

E minor (Aeolian: E F# G A B C D; the tune keeps to the pentatonic inside it), as the sketch. 6/8 at 46 dotted
quarters a minute (a bar is 2.609 s), 48 bars.

Ensemble (the sketch's palette, all synthesized; no samples): two pipes (synth.winds.breath_flute, very breathy) hard
left and right in hocket; one pipe alone, lower and slower (the verse, and the high line of the development); the
pipes' echo (the same pipe, far, darker, mostly reverb); the wind (act2_voices.wind) and the pass-cords
(act2_voices.cord_song on E G B E); an open-fifth string pad; a big drum far below and a frame drum's soft step.

Form (bars):
*  1-4   the pass (wind, cords, pad, the far drum): Em Em C Em;
*  5-12  A, the hocket (the sketch's TUNE): Em Em G D C D Em Em;
* 13-16  B, one pipe alone (VERSE): C D G Em;
* 17-24  A', the hocket, its first four bars an octave higher;
* 25-32  C, the echo: Am Am C C G G D D; the cell carried onto A minor by one high pipe, the valley answering each
         bar a bar later (bars 26-32); no frame drum, the big drum every second bar;
* 33-36  B', the verse with a held counter-pipe above it;
* 37-44  A'', the hocket at full height: both octaves together for four bars, then the tune's close;
* 45-48  the pass again, and the long tonic leads back to bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/act2/keth_pass.py   (or tools/audio/render_all.py --act2 --only act2/keth_pass)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _mod("keth_pass_sketch", os.path.join(MUSIC, "keth_pass.py"))   # the sketch: its themes, voices and timing
V = S.V

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "keth_pass.ogg")
SEED = 20261842
TARGET_LUFS = -16.0
BPM, DQ, EIGHTH, BAR = S.BPM, S.DQ, S.EIGHTH, S.BAR
BARS = 48
LOOP_S = BARS * BAR
LEAD_IN_EIGHTHS = S.LEAD_IN_EIGHTHS
QUALITY = 3.0

_A = ["Em", "Em", "G", "D", "C", "D", "Em", "Em"]
CHORDS = (["Em", "Em", "C", "Em"] + _A + ["C", "D", "G", "Em"] + _A
          + ["Am", "Am", "C", "C", "G", "G", "D", "D"]
          + ["C", "D", "G", "Em"] + _A + ["Em", "Em", "C", "Em"])
SECTION = (["I"] * 4 + ["A"] * 8 + ["B"] * 4 + ["A2"] * 8 + ["C"] * 8 + ["B2"] * 4 + ["A3"] * 8 + ["I2"] * 4)
PAD = dict(S.PAD, Am="A1 E2 A2 C3")

## C: the cell carried onto A minor (one list per bar of (pitch, eighths)); the valley echoes bars 25-31
HIGH_LINE = [
    [("E5", 3), ("D5", 1), ("C5", 2)],
    [("A4", 6)],
    [("C5", 2), ("D5", 1), ("E5", 3)],
    [("G5", 6)],
    [("G5", 3), ("E5", 1), ("D5", 2)],
    [("B4", 4), ("D5", 2)],
    [("A4", 3), ("B4", 1), ("A4", 2)],
    [("A4", 3), ("F#4", 3)],
]
ECHO_BARS = 7
## B': the held counter-pipe above the verse
COUNTER = [[("E5", 6)], [("F#5", 6)], [("D5", 6)], [("E5", 5), (None, 1)]]

LEAD = "pipes"
LEVELS = dict(S.LEVELS, echo=-9.0)
GAINS = dict(S.GAINS, echo=-4.7)


def t_of(bar: int, eighth: float = 0.0) -> float:
    return (bar - 1) * BAR + eighth * EIGHTH


def add_line(mx: LoopMixer, bus: str, bars: list, start_bar: int, seed: int, vel: float, pan: float = 0.0) -> None:
    """One pipe alone, lower and slower: the sketch's verse voice, placed at any bar."""
    g = rng(seed)
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for j, (p, e) in enumerate(bar):
            d = e * EIGHTH
            if p is None:
                pos += d
                continue
            x = breath_flute(n(p), d * 0.96 + 0.03, vel * float(g.uniform(0.94, 1.04)),
                             seed=seed + int(round(pos * 1000)), breath=0.7, scoop_cents=40.0 if j == 0 else 15.0,
                             vib_cents=8.0, vib_rate=4.4, swell=0.3, attack=0.1, release=0.6, beta=0.55)
            mx.add(bus, x, pos - V.FLUTE_PRE + float(g.normal(0, 0.005)), pan=pan)
            pos += d


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("wind", V.wind(LOOP_S, SEED + 3, lo_hz=300.0, hi_hz=2400.0, gusts=(6, 15, 4), hi_level=0.3), 0.0)
    mx.add("cords", V.cord_song(LOOP_S, [n("E5"), n("G5"), n("B5"), n("E6")], SEED + 4, q=45.0), 0.0)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.95, 0.45, seed=SEED + 200 + bar, voices=4,
                      attack=1.2, release=1.6, width=0.95)
        mx.add("pad", x, t_of(bar) - 0.3)
        if sec in ("A", "A2", "A3"):
            x = frame_drum("dum", 0.16 * float(g.uniform(0.9, 1.08)), variant=bar, size=1.2, seed=SEED + 1)
            mx.add("step", x, t_of(bar, 3) + float(g.normal(0, 0.01)), pan=0.1)
    for bar in range(1, BARS + 1):
        sec = SECTION[bar - 1]
        if sec == "C" and bar % 2 == 1:
            mx.add("drum", big_drum(0.24, variant=bar, seed=SEED + 2), t_of(bar), pan=0.0)
        elif sec != "C" and bar % 4 == 1:
            mx.add("drum", big_drum(0.4 if bar in (1, 13, 25, 37) else 0.3, variant=bar, seed=SEED + 2), t_of(bar),
                   pan=0.0)
    # A, B, A': the sketch's order
    S.add_hocket(mx, S.TUNE, 5, SEED + 600, 0.55)
    add_line(mx, "verse", S.VERSE, 13, SEED + 700, 0.5)
    S.add_hocket(mx, S.TUNE[:4], 17, SEED + 640, 0.5, octave=1)
    S.add_hocket(mx, S.TUNE[4:], 21, SEED + 660, 0.55)
    # C: one high pipe, and the valley answering a bar later, left then right
    add_line(mx, "verse", HIGH_LINE, 25, SEED + 710, 0.5, pan=0.05)
    for i in range(ECHO_BARS):
        add_line(mx, "echo", [HIGH_LINE[i]], 26 + i, SEED + 720 + i, 0.3, pan=-0.75 if i % 2 == 0 else 0.75)
    # B': the verse and its counter-pipe
    add_line(mx, "verse", S.VERSE, 33, SEED + 730, 0.5)
    add_line(mx, "pipes", COUNTER, 33, SEED + 740, 0.28, pan=-0.45)
    # A'': both octaves, then the close
    S.add_hocket(mx, S.TUNE[:4], 37, SEED + 680, 0.5)
    S.add_hocket(mx, S.TUNE[:4], 37, SEED + 690, 0.38, octave=1)
    S.add_hocket(mx, S.TUNE[4:], 41, SEED + 695, 0.55)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    G = GAINS
    pipe_eq = [bq_highpass(220, 0.7), bq_peak(2500, 1.5, 1.0), bq_lowpass(7000, 0.7)]
    mx.bus("pipes", G["pipes"], send=0.45, process=lambda x: filt(x, pipe_eq))
    mx.bus("verse", G["verse"], send=0.45, process=lambda x: filt(x, [bq_highpass(160, 0.7), bq_lowpass(6000, 0.7)]))
    mx.bus("echo", G["echo"], send=0.9, process=lambda x: filt(x, [bq_highpass(300, 0.7), bq_lowpass(2600, 0.7)]))
    mx.bus("wind", G["wind"], send=0.15)
    mx.bus("cords", G["cords"], send=0.35)
    mx.bus("pad", G["pad"], send=0.5, process=lambda x: string_body(x, cutoff=1400.0))
    mx.bus("drum", G["drum"], send=0.6, process=lambda x: filt(x, [bq_lowpass(1200, 0.7)]))
    mx.bus("step", G["step"], send=0.4, process=lambda x: filt(x, [bq_lowpass(2000, 0.7)]))
    build(mx)
    sky = ModFDNReverb(rt60=3.4, rt60_high=1.4, predelay=0.06, size=1.5, mod_depth=8.0, mod_rate=0.3,
                       early_level=0.12, lowcut=120.0, seed=SEED % 9973)
    return V.finish(mx, "keth_pass", out_path, BPM, 2, BARS, LEAD_IN_EIGHTHS * EIGHTH, TARGET_LUFS, sky, -2.5,
                    verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
