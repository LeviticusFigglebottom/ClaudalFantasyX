"""`lamp_archive`: Ch13, the Lamp Archive, the Order's library of Lit Age records (M3-AUD-805; act_outline Ch13,
ADR 0016): a 61 s seamless loop. An Act II sketch, for the human to judge the direction.

Original composition for this project (SPEC §2, §9). Original-material check: everything here is our own. The
piano's fragment is the Hush's first phrase (hush_theme_v2.py MEL_A, bars 1-4) moved to D minor and broken off where
the theme would climb; the closing phrase is High Warden Sefir's motif (sefir_theme.py MOTIF, G C D E D C#),
compressed into 3/4. The ledger figure (a low fifth, then a soft D ticking on beats 2 and 3), the "kept / spent"
sighs (F-E, E-D) and the canon of bars 7-11 were written for this cue. The style evoked is a spare, slow piano piece in
an empty room; no phrase is quoted from any existing music.

The brief: Liss and Ysolde have the run of the Archive for three days. The founders' lamp-ledgers, the Cantor roll
with its one extra column (*kept* or *spent*), the same few hands signing across four hundred years. Nobody says
"revenant"; Liss just lays the pages side by side. And Sefir let her read it. Quiet, dusty, uneasy: the truth on
paper, in plain sight.

So the cue is the game's own two themes laid side by side, like the pages. The Hush (the song the founders wrote) is
read in fragments that stop mid-line. In bars 7-11 it is read twice at once, an octave apart and a bar out of step,
and the two copies do not agree (the echo's C and G over the A chord). Then Sefir's motif, whose C# has never led
anywhere (in C major it is the one wrong note), is played in D minor, where C# is the leading tone: for the first
time it resolves, up to D. The truth is that the wrong note belongs to this key.

D minor, 3/4 at 59 BPM (a bar is 3.05 s), 20 bars. The quietest texture in the score so far: a grand piano, a dark
string pad an octave under it, and paper.

Ensemble (all synthesized; no samples):
* grand piano (synth.grand, a light constant pedal): the fragments in the right hand; in the left a low open fifth
  on each downbeat and a soft D ticking on beats 2 and 3 for the whole loop (the ledger's column, the same hand);
* a string pad, very low and dark (sul tasto, filtered at 1.2 kHz): dust in the air;
* paper: three page-turns a loop (filtered noise with a dry crackle), far back.

Form (bars): 1-2 the ledger alone | 3-6 the Hush, broken off (Dm Bb F A5) | 7-11 the Hush an octave up and its echo a
bar behind (Dm Bb Gm A5 Dm) | 12-14 kept / spent (Bb(#11) Dm(add9) Bb(#11)) | 15-16 the ledger and the dust | 17-20
Sefir's motif over C, Bb-A, A7, resolving to Dm, which is bar 1.

Loop: LOOPSTART = 0 and LOOPLENGTH = the whole file. The file starts a sixteenth before bar 1's downbeat (the
sidecar's `downbeat_offset_s`), so the wrap seam falls before the resolution's downbeat, not on it.

Render:  python3 assets_src/music/lamp_archive.py   (or tools/audio/render_all.py --only lamp_archive)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.grand import PedalCurve, PianoBody, grand_note  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "lamp_archive.ogg")
SEED = 20261323
TARGET_LUFS = -16.0
BPM = 59.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
BARS = 20
LOOP_S = BARS * BAR
## the file starts this many beats before bar 1's downbeat (see render())
LEAD_IN_BEATS = 0.25
PEDAL_DEPTH = 0.35      # a light, constant pedal: the soundboard bus stays time-invariant
QUALITY = 3.0  # mix.md §5's sparse-cue quality

CHORDS = ["Dm", "Dm", "Dm", "Bb", "F", "A5", "Dm", "Bb", "Gm", "A5", "Dm", "Bb#11", "Dm9", "Bb#11", "A5", "A5",
          "C", "Bb", "A7", "Dm"]
## the left hand's downbeat fifth, and the pad (an octave under the melody, dark)
LH = {"Dm": "D2 A2", "Bb": "Bb1 F2", "F": "F2 C3", "A5": "A1 E2", "Gm": "G1 D2", "Bb#11": "Bb1 F2", "Dm9": "D2 A2",
      "C": "C2 G2", "A7": "A1 E2 G2"}
PAD = {"Dm": "D3 A3 F4", "Bb": "Bb2 F3 D4", "F": "F3 C4 A4", "A5": "A2 E3 A3", "Gm": "G2 D3 Bb3",
       "Bb#11": "Bb2 F3 D4 E4", "Dm9": "D3 A3 E4 F4", "C": "C3 G3 E4", "A7": "A2 E3 G3 C#4"}
TICK = "D5"
## the Hush's first phrase in D minor (hush_theme_v2 MEL_A bars 1-4, down a fifth), broken off after its fourth bar
FRAG = [("A4", 2), ("G4", .5), ("F4", .5), ("D4", 2), ("C4", .5), ("D4", .5), ("C4", 1), ("F4", 1), ("G4", 1),
        ("A4", 2)]
## kept / spent (bars 12-14)
SIGHS = [(12, [("E5", 2), ("D5", 1)]), (13, [("F5", 2), ("E5", 1)]), (14, [("E5", 2)])]
## Sefir's motif (sefir_theme MOTIF) in 3/4, its C# resolving at last
MOTIF = [("G4", 1), ("C5", 1), ("D5", .5), ("E5", .5), ("D5", 2), ("C#5", 1), ("C#5", 0), ("D5", 3)]
PAGES = (2.3, 9.6, 15.2)        # bar positions of the page-turns

# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"], the whole loop) for these levels
# relative to the piano's right hand (0 LU): the ledger (left hand) -5, the pad -11, paper -19. (The grand piano
# model's raw output is about 30 dB under the pad's, hence the piano's large gains.)
GAINS = {"piano_rh": 25.5, "piano_lh": 19.1, "pad": 0.0, "paper": -28.7}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def _phrase(notes: list, bar: int, octave: int, vel: float, g: np.random.Generator) -> list[dict]:
    out, pos = [], 0.0
    for i, (p, beats) in enumerate(notes):
        if beats == 0:                  # a tie: the previous note is held (MOTIF's C# across the barline)
            out[-1]["key_up"] += BEAT * 3
            pos += 3
            continue
        # a reader's phrasing: each fragment leans on its first note and fades toward the break
        v = vel * (1.06 - 0.025 * i) * g.uniform(0.95, 1.04)
        out.append(dict(m=n(p) + octave, vel=v, t0=t_of(bar, pos) + float(g.normal(0.01, 0.006)),
                        key_up=beats * BEAT * 0.98))
        pos += beats
    return out


def _piano_jobs(notes: list[dict], seed: int) -> list:
    pedal = PedalCurve(np.array([0.0, 1.0e6]), np.array([PEDAL_DEPTH, PEDAL_DEPTH]))
    return [(grand_note, dict(m=nt["m"], vel=nt["vel"], key_up=nt["key_up"], seed=seed + 7919 * k, t_abs=nt["t0"],
                              pedal=pedal)) for k, nt in enumerate(notes)]


def page_turn(seed: int) -> np.ndarray:
    """A page lifted and laid down: a soft swish of air (band-limited noise that rises and falls) with a dry crackle
    of paper fibres over it, and a faint touch as it lands. Mono, about 0.9 s."""
    g = rng(seed)
    N = int(0.9 * SR)
    t = np.arange(N) / SR
    env = np.sin(np.pi * np.clip(t / 0.75, 0, 1)) ** 2
    swish = filt(g.standard_normal(N), [bq_bandpass(float(g.uniform(1800, 2600)), 0.6), bq_highpass(600, 0.7)])
    swish = swish / (np.std(swish) + 1e-9) * env * 0.25
    crackle = np.zeros(N)
    for _ in range(int(g.integers(28, 40))):
        k = int(g.uniform(0.05, 0.7) * SR)
        crackle[k] += g.uniform(-1, 1) * env[k]
    crackle = filt(crackle, [bq_bandpass(4200.0, 1.2)])
    crackle = crackle / (np.abs(crackle).max() + 1e-9) * 0.35
    k = int(0.74 * SR)
    land = np.zeros(N)
    m = int(0.06 * SR)
    land[k: k + m] = filt(g.standard_normal(m), [bq_lowpass(700, 0.7)]) * np.exp(-np.arange(m) / (0.012 * SR)) * 0.4
    y = swish + crackle + land
    return y / (np.abs(y).max() + 1e-9)


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    rh: list[dict] = []
    lh: list[dict] = []
    for bar, ch in enumerate(CHORDS, start=1):
        # the ledger: a low open fifth on the downbeat, the tick on beats 2 and 3 (bar 18 changes chord on beat 3)
        fifth = LH[ch].split()
        for p in fifth:
            lh.append(dict(m=n(p), vel=0.34 * g.uniform(0.95, 1.03), t0=t_of(bar) + float(g.normal(0, 0.004)),
                           key_up=(2 if bar == 18 else 3) * BEAT * 0.97))
        if bar == 18:
            for p in ("A1", "E2"):
                lh.append(dict(m=n(p), vel=0.3, t0=t_of(bar, 2) + 0.005, key_up=BEAT * 0.97))
        for beat in (1, 2):
            lh.append(dict(m=n(TICK), vel=(0.17 if beat == 1 else 0.14) * g.uniform(0.92, 1.05),
                           t0=t_of(bar, beat) + float(g.normal(0.012, 0.008)), key_up=BEAT * 0.5))
        x = pad_chord([n(p) for p in PAD[ch].split()], BAR * 0.98, 0.45, seed=SEED + 100 + bar, attack=1.4,
                      release=2.0, voices=3, spread_cents=7.0)
        mx.add("pad", x, t_of(bar) - 0.4)
    # the Hush, read and broken off; then read again an octave up, with its echo a bar behind
    rh += _phrase(FRAG, 3, 0, 0.42, g)
    rh += _phrase(FRAG, 7, 12, 0.38, g)
    lh += _phrase(FRAG, 8, 0, 0.30, g)
    for bar, notes in SIGHS:
        rh += _phrase(notes, bar, 0, 0.36, g)
    rh += _phrase(MOTIF, 17, 0, 0.42, g)
    for bus, notes, seed in (("piano_rh", rh, SEED + 20), ("piano_lh", lh, SEED + 30)):
        for nt, x in zip(notes, render_jobs(_piano_jobs(notes, seed))):
            mx.add(bus, x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    for i, b in enumerate(PAGES):
        mx.add("paper", page_turn(SEED + 900 + i), t_of(int(b), (b % 1) * 3), pan=0.55 - 0.5 * i)


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
    _, loop = mx.render(reverb=room, reverb_return_db=-3.0)
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loop = np.roll(loop, lead_in, axis=0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=QUALITY, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 3,
                       extra={"loop_bars": BARS, "downbeat_offset_s": lead_in / SR})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"lamp_archive: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
