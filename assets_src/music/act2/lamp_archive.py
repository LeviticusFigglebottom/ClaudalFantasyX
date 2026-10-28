"""`lamp_archive` (final): Ch13, the Lamp Archive, the Order's library of Lit Age records (M3-AUD-842; act_outline
Ch13, ADR 0016, act2_finals.md): a 137 s seamless loop, grown from the M3-AUD-805 sketch
(assets_src/music/lamp_archive.py).

Original composition for this project (SPEC §2, §9). Original-material check: everything here is our own. The
Hush's broken-off fragment (hush_theme_v2.py MEL_A, bars 1-4, in D minor), the "kept / spent" sighs, Sefir's motif in
3/4 (sefir_theme.py MOTIF, G C D E D C#, its C# resolving to D), the ledger figure, the voicings and the page-turn
are the sketch's, imported from it, not retyped. Written new for this final: the roll (bars 17-24), a chain of the
sighs falling a step a bar (A-G, G-F, F-E, E; D-B-flat-D, C-A, B-flat-G, A) over a bass that walks down from D to A;
its first half signed again by the left hand, lower and softer (bars 25-28); the sighs' answer that climbs a step
further (G-F over G minor) in bars 36-39; and the canon's second reading, with the voices' order swapped. The style
evoked is a spare, slow piano piece in an empty room; no phrase is quoted from any existing music.

The brief (the sketch's, unchanged): Liss and Ysolde have the run of the Archive for three days. The founders'
lamp-ledgers, the Cantor roll with its one extra column (*kept* or *spent*), the same few hands signing across four
hundred years. Nobody says "revenant"; Liss just lays the pages side by side. And Sefir let her read it. Quiet,
dusty, uneasy: the truth on paper, in plain sight.

So the final reads longer and finds the same thing. The ledger (a low open fifth, the soft D ticking on beats 2 and
3) runs under all forty-five bars. The new roll is the sighs turned into a list: a name, a step down, a name, as if
reading a column of entries down a page; and then the same entries again in a lower hand (the same few hands, a
century later). The second canon puts the low reading first and the high copy a bar behind it, so they disagree in
new places. The A chord stays bare (no third) all through, as in the sketch, so Sefir's C# at the close is still the
first C# the loop has heard, and it still resolves, once, up to D.

D minor, 3/4 at 59 BPM (a bar is 3.05 s), 45 bars. Ensemble (the sketch's; all synthesized, no samples): grand piano
with a light constant pedal, a dark string pad an octave under it, and paper.

Form (bars): 1-2 the ledger alone | 3-6 A, the Hush, broken off (Dm Bb F A5) | 7-11 A2, the Hush an octave up and its
echo a bar behind (Dm Bb Gm A5 Dm) | 12-14 kept / spent (Bb(#11) Dm(add9) Bb(#11)) | 15-16 the ledger and the dust |
17-24 C, the roll (Dm C Bb A5 Gm F Em7b5 A5) | 25-28 C', its first half in the left hand (Dm C Bb A5) | 29-30 the
ledger and the dust | 31-35 A2', the low reading first and the high copy a bar behind (Dm Bb Gm A5 Dm) | 36-39 the
sighs climbing (Bb(#11) Dm(add9) Gm A5) | 40-41 the ledger | 42-45 Sefir's motif over C, Bb-A, A7, resolving to Dm,
which is bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls before the resolution's downbeat, not on it.

Render:  python3 assets_src/music/act2/lamp_archive.py   (or tools/audio/render_all.py --act2 --only act2/lamp_archive)
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

from synth.dsp import bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.grand import PedalCurve, PianoBody  # noqa: E402
from synth.looping import LoopMixer  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _mod("lamp_archive_sketch", os.path.join(MUSIC, "lamp_archive.py"))   # the sketch: its material, never edited
V = _mod("act2_voices", os.path.join(MUSIC, "act2_voices.py"))            # V.finish: the sketches' render path

OUT = os.path.join(ROOT, "assets", "audio", "music", "act2", "lamp_archive.ogg")
SEED = 20261343
TARGET_LUFS = S.TARGET_LUFS
BPM = S.BPM
BEAT = S.BEAT
BAR = S.BAR
BARS = 45
LOOP_S = BARS * BAR
LEAD_IN_BEATS = S.LEAD_IN_BEATS
PEDAL_DEPTH = S.PEDAL_DEPTH
QUALITY = S.QUALITY

ROLL_CHORDS = ["Dm", "C", "Bb", "A5", "Gm", "F", "Em7b5", "A5"]
CHORDS = (S.CHORDS[:16] + ROLL_CHORDS + ROLL_CHORDS[:4] + ["Dm", "Dm"] + S.CHORDS[6:11]
          + ["Bb#11", "Dm9", "Gm", "A5", "A5", "A5"] + S.CHORDS[16:])
LH = {**S.LH, "Em7b5": "E2 Bb2"}
PAD = {**S.PAD, "Em7b5": "E3 G3 Bb3"}
## the roll: the sighs as a falling list, one entry a bar (bars 17-24), as one phrase of (pitch, beats)
ROLL = [("A5", 2), ("G5", 1), ("G5", 2), ("F5", 1), ("F5", 2), ("E5", 1), ("E5", 3),
        ("D5", 1), ("Bb4", 1), ("D5", 1), ("C5", 2), ("A4", 1), ("Bb4", 2), ("G4", 1), ("A4", 3)]
ROLL_BAR = 17
ROLL_LH_BAR = 25                # its first half (seven notes, four bars) again in the left hand, an octave down
## the sighs climbing (bars 36-39): the sketch's first two, then one step further, then the fall
SIGHS_UP = [(36, S.SIGHS[0][1]), (37, S.SIGHS[1][1]), (38, [("G5", 2), ("F5", 1)]), (39, [("E5", 3)])]
CANON2_BAR = 31                 # the low reading at 31, the high copy at 32
MOTIF_BAR = 42                  # the sketch's bar 17: the motif, its second bar changing chord on beat 3
## page-turns: bar positions (the sketch's three, then three more through the new bars)
PAGES = S.PAGES + (21.4, 29.5, 40.2)

# The sketch's bus gains (set from its measured bus loudness).
GAINS = dict(S.GAINS)


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def phrase(notes: list, bar: int, octave: int, vel: float, g) -> list[dict]:
    """The sketch's phrasing (S._phrase) placed on this final's bars (its t_of is the same bar grid)."""
    return S._phrase(notes, bar, octave, vel, g)


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    rh: list[dict] = []
    lh: list[dict] = []
    split = MOTIF_BAR + 1           # the motif's second bar: Bb, then A on beat 3
    for bar, ch in enumerate(CHORDS, start=1):
        # the ledger: a low open fifth on the downbeat, the tick on beats 2 and 3
        for p in LH[ch].split():
            lh.append(dict(m=n(p), vel=0.34 * g.uniform(0.95, 1.03), t0=t_of(bar) + float(g.normal(0, 0.004)),
                           key_up=(2 if bar == split else 3) * BEAT * 0.97))
        if bar == split:
            for p in ("A1", "E2"):
                lh.append(dict(m=n(p), vel=0.3, t0=t_of(bar, 2) + 0.005, key_up=BEAT * 0.97))
        for beat in (1, 2):
            lh.append(dict(m=n(S.TICK), vel=(0.17 if beat == 1 else 0.14) * g.uniform(0.92, 1.05),
                           t0=t_of(bar, beat) + float(g.normal(0.012, 0.008)), key_up=BEAT * 0.5))
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.98, 0.45, seed=SEED + 100 + bar, attack=1.4,
                      release=2.0, voices=3, spread_cents=7.0)
        mx.add("pad", x, t_of(bar) - 0.4)
    # A and A2: the sketch's readings of the Hush, on the sketch's bars
    rh += phrase(S.FRAG, 3, 0, 0.42, g)
    rh += phrase(S.FRAG, 7, 12, 0.38, g)
    lh += phrase(S.FRAG, 8, 0, 0.30, g)
    for bar, notes in S.SIGHS:
        rh += phrase(notes, bar, 0, 0.36, g)
    # C: the roll, read in two halves (each leans on its first entry); C': its first half in the left hand
    rh += phrase(ROLL[:7], ROLL_BAR, 0, 0.38, g)
    rh += phrase(ROLL[7:], ROLL_BAR + 4, 0, 0.35, g)
    lh += phrase(ROLL[:7], ROLL_LH_BAR, -12, 0.31, g)
    # A2': the low reading first, the high copy a bar behind
    lh += phrase(S.FRAG, CANON2_BAR, 0, 0.33, g)
    rh += phrase(S.FRAG, CANON2_BAR + 1, 12, 0.34, g)
    for bar, notes in SIGHS_UP:
        rh += phrase(notes, bar, 0, 0.36, g)
    rh += phrase(S.MOTIF, MOTIF_BAR, 0, 0.42, g)
    for bus, notes, seed in (("piano_rh", rh, SEED + 20), ("piano_lh", lh, SEED + 30)):
        for nt, x in zip(notes, render_jobs(S._piano_jobs(notes, seed))):
            mx.add(bus, x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    for i, b in enumerate(PAGES):
        mx.add("paper", S.page_turn(SEED + 900 + i), t_of(int(b), (b % 1) * 3), pan=0.55 - 0.22 * i)


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    G = GAINS
    for bus in ("piano_rh", "piano_lh"):
        mx.bus(bus, G[bus], send=0.3, process=PianoBody(PedalCurve(np.array([0.0, 1.0e6]),
                                                                   np.array([PEDAL_DEPTH, PEDAL_DEPTH]))))
    mx.bus("pad", G["pad"], send=0.45, process=lambda x: string_body(x, cutoff=1200.0))
    mx.bus("paper", G["paper"], send=0.5, process=lambda x: filt(x, [bq_highpass(300, 0.7), bq_lowpass(7000, 0.7)]))
    build(mx)
    room = ModFDNReverb(rt60=2.6, rt60_high=0.9, predelay=0.03, size=1.1, mod_depth=6.0, mod_rate=0.4,
                        early_level=0.35, lowcut=110.0, seed=SEED % 9973)
    return V.finish(mx, "lamp_archive (final)", out_path, BPM, 3, BARS, LEAD_IN_BEATS * BEAT, TARGET_LUFS, room, -3.0,
                    verbose, stats, quality=QUALITY)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
