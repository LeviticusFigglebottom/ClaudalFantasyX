"""`lanternfall`: Pemakar's festival music, played by the town (M3-AUD-821; act1_ch05.md B04-B06, §6).

Original composition for this project (SPEC §2, §9). The procession tune, its harmony of gongs and the drum's
pattern were written for this cue and are not derived from any existing tune. Like terraces_of_ash (the area's own
loop) it uses Pemakar's five-note scale on F (F Gb Bb C Db), but the tune is a different one: a town's tune, sung
on flutes by everyone who owns one.

The brief (act1_ch05.md §6): "Diegetic festival music played by the town on the terraces: gongs, a slow processional
drum, many flutes slightly out of tune with each other. It thins as the procession descends, and at the weir only
one drum is left." The crown bell rings once (B04 P08, `@sfx crown_bell`, at the cue's start), the mountain lights
up, and the town walks down the terraces beside its boats; at the bottom is the sea-cut weir (B05).

**Form: a through-composed intro that thins, then a loop of the one drum that is left** (my call). The intro is the
festival and its thinning (60 s, about the boats scene's length); LOOPSTART is where only the drum is left, and the
loop (32 s) is that drum, so the weir scene can run as long as the player reads and the drum never runs out. The
intro's last bars are already drum alone, played exactly as the loop plays them, so the first pass into the loop
carries the same tails. `kerrid_stair` takes over from it at the weir's close (its own frame drum, 48 BPM).

Ensemble (all synthesized; no samples):
* the flutes: six players (breath flutes) on the same tune in heterophony, each tuned a little differently from the
  others (from 28 cents flat to 33 sharp, fixed per player: home-made flutes and cold fingers), each a few
  hundredths of a second early or late, two of them an octave up, some adding a grace note from below or leaving
  out a re-articulation; they drop out one or two at a time as the procession goes down;
* the gongs: kettle gongs on the downbeats (F and C), a large gong every four bars while the town is together;
* the processional drum: a big drum on beat 1 and a frame drum on beat 3 with two soft ghosts, until only the big
  drum is left, on 1 (and softer on 3).

Form (4/4 at 60 BPM, a bar is 4 s; every event a sixteenth late, DOWNBEAT_OFFSET_S, so the loop seam falls before a
downbeat, not on it): 1-2 the gongs answer the bell, the drum enters | 3-10 A: the tune; six flutes to bar 8, then
one player stops each bar | 11-13 A again from the top, three flutes, then two, then one, who stops mid-tune; the
kettle gongs every other bar after bar 8, the last large gong at bar 11, the frame drum gone after bar 11 | 14-15 the
big drum alone | loop (bars 16-23, = LOOPSTART): the big drum alone, played for as long as the scene lasts.

Render:  python3 assets_src/music/lanternfall.py   (or tools/audio/render_all.py --only lanternfall)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, rng  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "lanternfall.ogg")
SEED = 20261824
TARGET_LUFS = -16.0
BPM = 60.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
S16 = BEAT / 4
INTRO_BARS = 15
LOOP_BARS = 8
INTRO_S = INTRO_BARS * BAR
LOOP_S = LOOP_BARS * BAR
## every event sits a sixteenth late, so the file's loop seam falls a sixteenth before a downbeat
DOWNBEAT_OFFSET_S = S16
## breath_flute's tone starts after its breath (0.05-0.08 s): its notes are placed this much early
FLUTE_PRE = 0.065
DRUM_ALONE_FROM = 14            # the first bar with only the big drum
FRAME_UNTIL = 11                # the frame drum's last bar

SCALE = ["F4", "Gb4", "Bb4", "C5", "Db5", "F5", "Gb5"]
## the procession tune, (pitch, beats) per bar
TUNE = [
    [("F5", 2), ("Gb5", 1), ("F5", 1)],
    [("Db5", 1.5), ("C5", .5), ("Bb4", 2)],
    [("C5", 1), ("Db5", 1), ("F5", 2)],
    [("Gb5", 3), ("F5", 1)],
    [("Db5", 2), ("C5", 1), ("Db5", 1)],
    [("Bb4", 1.5), ("Gb4", .5), ("F4", 2)],
    [("Gb4", 1), ("Bb4", 1), ("C5", 1), ("Db5", 1)],
    [("C5", 4)],
]
## the players: (cents off true, octave, timing bias s, grace notes, last bar they play)
PLAYERS = [
    (-28.0, 0, 0.035, True, 9),
    (-12.0, 0, -0.020, False, 11),
    (0.0, 0, 0.000, True, 13),
    (9.0, 1, 0.025, False, 8),
    (21.0, 0, -0.035, True, 12),
    (33.0, 1, 0.045, False, 10),
]
TUNE_STARTS = (3, 11)           # A, and A again (thinning)


def t_of(bar: int, beat: float = 0.0) -> float:
    """File time (seconds) of a bar and beat; bars past the intro are loop bars."""
    return (bar - 1) * BAR + beat * BEAT + DOWNBEAT_OFFSET_S


def scale_below(m: float) -> float:
    k = m - 1
    pcs = {n(p) % 12 for p in SCALE}
    while k % 12 not in pcs:
        k -= 1
    return k


def add_flutes(mx: LoopMixer) -> None:
    """Each player's line through both statements of the tune, until their last bar."""
    for pi, (cents, octv, bias, grace, last_bar) in enumerate(PLAYERS):
        pg = rng(SEED + 1000 + 37 * pi)
        for start in TUNE_STARTS:
            for bi, bar in enumerate(TUNE):
                b = start + bi
                if b > last_bar:
                    break
                pos = 0.0
                for k, (p, beats) in enumerate(bar):
                    m = n(p) + 12 * octv + cents / 100.0
                    d = beats * BEAT
                    t0 = t_of(b, pos) + bias + float(pg.normal(0, 0.018))
                    v = 0.5 * (1.06 if k == 0 else 1.0) * pg.uniform(0.92, 1.05)
                    if grace and k == 0 and beats >= 1.5 and pg.random() < 0.6:
                        gm = scale_below(n(p)) + 12 * octv + cents / 100.0
                        x = breath_flute(gm, 0.09, v * 0.7, seed=SEED + 5000 + 97 * pi + 7 * b + k, breath=0.4,
                                         scoop_cents=10.0, vib_cents=0.0, attack=0.02, release=0.05)
                        mx.add("flutes", x, t0 - 0.11 - FLUTE_PRE, pan=-0.6 + 0.24 * pi, part="intro")
                    x = breath_flute(m, d * 0.94 + 0.03, v, seed=SEED + 3000 + 101 * pi + 11 * b + k, breath=0.38,
                                     scoop_cents=35.0, vib_cents=12.0 + 3 * pi % 7, vib_rate=4.4 + 0.25 * pi,
                                     swell=0.18 if beats >= 2 else 0.0, attack=0.06, release=0.25, beta=0.55)
                    mx.add("flutes", x, t0 - FLUTE_PRE, pan=-0.6 + 0.24 * pi, part="intro")
                    pos += beats


## the drum alone, per loop bar: (velocity on 1, velocity on 3)
ALONE_VEL = [(0.56, 0.30), (0.52, 0.28), (0.55, 0.31), (0.50, 0.27), (0.54, 0.29), (0.51, 0.30), (0.55, 0.28),
             (0.49, 0.27)]


def drum_alone(mx: LoopMixer, k: int, t0: float, part: str) -> None:
    """One bar of the drum alone (loop bar k + 1): the big drum on 1 and, softer, on 3. The intro's drum-alone bars
    play the loop bar they stand for, with the same takes and velocities, so the pass into the loop carries
    identical tails."""
    mx.add("drum", big_drum(ALONE_VEL[k][0], variant=k, seed=SEED + 4), t0, part=part)
    mx.add("drum", big_drum(ALONE_VEL[k][1], variant=(k + 2) % 4, seed=SEED + 4), t0 + 2 * BEAT, part=part)


def procession_bar(mx: LoopMixer, bar: int, g) -> None:
    """The procession (intro bars 3-13): the big drum on 1, the frame drum on 3 with two soft ghosts; after
    FRAME_UNTIL the frame drum has gone and the big drum takes beat 3 too."""
    mx.add("drum", big_drum(0.62 * g.uniform(0.95, 1.04), variant=bar, seed=SEED + 4),
           t_of(bar) + float(g.normal(0, 0.008)), part="intro")
    if bar <= FRAME_UNTIL:
        for beat, stroke, v in ((2, "dum", 0.42), (2.5, "ghost", 0.12), (3.5, "ghost", 0.10)):
            x = frame_drum(stroke, v * g.uniform(0.9, 1.08), variant=4 * bar + int(2 * beat), size=1.3, seed=SEED + 1)
            mx.add("frame", x, t_of(bar, beat) + float(g.normal(0, 0.008)), pan=-0.15, part="intro")
    else:
        mx.add("drum", big_drum(0.36 * g.uniform(0.95, 1.04), variant=bar + 1, seed=SEED + 4),
               t_of(bar, 2) + float(g.normal(0, 0.008)), part="intro")


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    # the drum: from bar 2's beat 3 through the intro; then alone; the loop is the drum alone
    mx.add("drum", big_drum(0.4, variant=0, seed=SEED + 4), t_of(2, 2), part="intro")
    for bar in range(3, DRUM_ALONE_FROM):
        procession_bar(mx, bar, g)
    for bar in range(DRUM_ALONE_FROM, INTRO_BARS + 1):
        drum_alone(mx, (bar - INTRO_BARS - 1) % LOOP_BARS, t_of(bar), "intro")      # the loop bar it stands for
    for k in range(LOOP_BARS):
        drum_alone(mx, k, k * BAR + DOWNBEAT_OFFSET_S, "loop")
    # the gongs: answering the bell, then on the downbeats while the town is together
    mx.add("gong", large_gong(n("F1"), 0.40, seed=SEED + 500, t60=9.0), t_of(1, 1.5), pan=-0.1, part="intro")
    mx.add("gong", kettle_gong(n("C4"), 0.30, seed=SEED + 401, t60=2.6), t_of(2), pan=0.3, part="intro")
    for bar in range(3, 12):
        if bar > 8 and bar % 2 == 0:
            continue
        p = "F3" if bar % 2 else "C4"
        v = (0.30 if bar <= 8 else 0.24) * g.uniform(0.92, 1.05)
        mx.add("gong", kettle_gong(n(p), v, seed=SEED + 400 + bar, t60=2.4), t_of(bar), pan=0.3 if bar % 2 else -0.25,
               part="intro")
    for bar, v in ((3, 0.34), (7, 0.30), (11, 0.24)):
        mx.add("gong", large_gong(n("F1"), v, seed=SEED + 500 + bar, t60=9.0), t_of(bar), pan=-0.1, part="intro")
    add_flutes(mx)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"], over bars 3-10 where all play) for
# these levels relative to the flutes (0 LU): the big drum -8, the frame drum -11, the gongs -10. The loop alone is
# about 13 LU under the festival (-27.5 against -14.5 LUFS): one drum, far quieter than the town.
GAINS = {"flutes": 0.0, "drum": 0.0, "frame": 2.9, "gong": -1.7}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=INTRO_S, loop_s=LOOP_S, intro_tail_s=12.0, preroll_s=LOOP_S)
    mx.bus("flutes", GAINS["flutes"], send=0.38, process=lambda x: filt(x, [bq_highpass(250, 0.7),
                                                                           bq_peak(3000, -1.5, 1.0)]))
    mx.bus("drum", GAINS["drum"], send=0.30, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(2500, 0.7)]))
    mx.bus("frame", GAINS["frame"], send=0.28, process=lambda x: filt(x, [bq_lowpass(3500, 0.7)]))
    mx.bus("gong", GAINS["gong"], send=0.45)
    build(mx)
    night = ModFDNReverb(rt60=3.4, rt60_high=1.4, predelay=0.04, size=1.2, mod_depth=10.0, mod_rate=0.45,
                         early_level=0.22, lowcut=100.0, seed=SEED % 9973)
    intro, loop = mx.render(reverb=night, reverb_return_db=-2.0)
    rep: dict = {}
    intro, loop = master_loop(intro, loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    y = np.concatenate([intro, loop])
    S, L = len(intro), len(loop)
    write_ogg(out_path, y, quality=3.0, tags={"LOOPSTART": str(S), "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, S, L, BPM, 4,
                       extra={"intro_bars": INTRO_BARS, "loop_bars": LOOP_BARS, "downbeat_offset_s": DOWNBEAT_OFFSET_S})
    m = measure(y)
    if stats is not None:
        stats["splice_residual_db"] = mx.splice_residual_db
        stats["bus_lufs"] = _bus_stats(mx)
        stats["limiter"] = rep
    if verbose:
        print(f"lanternfall: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  loop {S}+{L}  splice {mx.splice_residual_db:.1f} dB  limiter {rep}")
    return m


def _bus_stats(mx: LoopMixer) -> dict:
    """Each bus's loudness (after its fader) over bars 3-10 of the intro, where everyone plays."""
    out = {}
    a, e = int(t_of(3) * SR), int(t_of(11) * SR)
    for b in mx.buses.values():
        x = db_to_lin(b.gain_db) * (b.process(b.intro) if b.process else b.intro)
        out[b.name] = integrated_lufs(x[a:e])
    return out


if __name__ == "__main__":
    st: dict = {}
    render(stats=st)
    print("  buses", {k: round(v, 1) for k, v in st["bus_lufs"].items()})
