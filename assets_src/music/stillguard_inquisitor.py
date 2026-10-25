"""`stillguard_inquisitor`: the Ch6 boss, a Stillguard Inquisitor and a raid-hound (M3-AUD-20; act_outline Ch6
"Salt Edict"): a 2-bar intro and a 32-bar loop.

Original composition for this project (SPEC §2, §9). The march, the piano's edict theme, the flute's lament and the
shield calls were written for this fight and are not derived from any existing tune. Original-material check: the
edict theme is built from two rising-fifth summonses (A-E, then D-A a fourth higher) that step back down to a
half cadence; the lament is a falling line of long notes with one raised (Lydian) B over F; neither was taken from,
or written to resemble, any existing melody, march or hymn, and no existing cue's rhythm or progression is copied.
(The Order's hum is this project's own convention, bible §4; Sefir's motif, sefir_theme.py, is not used here: it is
his, and he arrives after this fight.)

The brief (act_outline Ch6): the party stumbles on an Order raid burning a Saltwright salvage camp in the Brine
Shoals and shelters Liss. The boss is a Stillguard Inquisitor with a raid-hound: the first fight against the Order's
own people, and Toma, a former Stillguard, refuses to strike to kill. It must not sound like a monster fight. It is
the Order's music: disciplined, lawful and cold, with something sorrowful under it, because these are people.

A minor, kept to the white notes (the Order's C major seen from below) except for the G# of the E major dominant
at the cadences: the law always resolves. In the hound's passage the Bb chord (the flattened second) bites once.
4/4 at 104 BPM (a bar is 2.31 s), 32 bars: a march. The Order keeps exact time, so the drill drums are barely
humanized (1 ms), unlike every other battle cue.

Ensemble (all synthesized; no samples):
* the drill: frame drums in a strict march pattern on the sixteenths (the dum on 1 and 3, the tek on 2 and 4) and
  the big drum on 1 and 3;
* the shields: a red-lacquered shell shield struck with a spear shaft (a hand-damped kettle gong on E3 under a
  small, hard frame-drum slap), on beat 4 of each bar, and the drill call ("Hold. On my shield.") of three strokes
  on 2-3-4 at each cadence;
* the edict: a low piano in octaves, marching eighths on the chord's root and fifth, and the theme on piano in
  octaves above it, marcato; in A'' the theme drops an octave, heavier;
* the Order: men humming the chord roots through the whole loop (only Cantors sing), and women humming above them
  in the people's sections; a large gong at the sections;
* the people: a breath flute, the lament (B) and a counterline of long notes over the edict (A'');
* the hound: in its passage the drill breaks into running sixteenths, the bass snaps through the flattened second
  in eighths and the shields strike on 2 and 4.

Form: 1-4 the line forms (drill, shields, the march, the hum) | 5-12 A, the edict, to the half cadence | 13-20 B,
the people: the drums thin to the dum, the flute's lament in C major over F C G Am, the women's hum | 21-24 the
hound: running drill, Am Bb Am E | 25-32 A'', the edict an octave down and the lament's counterline over it, the
shield fill in bar 32; its G# leads into bar 1.

Loop: the intro is a copy of bars 31-32 (so the splice into bar 1 carries the same tails); LOOPSTART = its length,
LOOPLENGTH = 32 bars. Every event sits a sixteenth late (DOWNBEAT_OFFSET_S, in the sidecar), so the wrap seam falls
a sixteenth before bar 1's downbeat, not on its heaviest attack.

Render:  python3 assets_src/music/stillguard_inquisitor.py   (or tools/audio/render_all.py --only stillguard)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.electric import bass_note  # noqa: E402
from synth.gongs import kettle_gong, large_gong  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.piano import piano_note  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "stillguard_inquisitor.ogg")
SEED = 20261124
TARGET_LUFS = -16.0
BPM = 104.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
E8 = BEAT / 2
S16 = BEAT / 4
BARS = 32
LOOP_S = BARS * BAR
INTRO_BARS = 2
INTRO_S = INTRO_BARS * BAR
## breath_flute's tone starts after its breath (0.05-0.08 s): notes are placed this much early.
FLUTE_PRE = 0.065
## every event sits a sixteenth late, so the file's wrap falls a sixteenth before bar 1's downbeat
DOWNBEAT_OFFSET_S = S16

CHORDS = (["Am", "Am", "F", "E"]
          + ["Am", "Am", "Dm", "Am", "F", "G", "E", "E"]
          + ["F", "C", "G", "Am", "F", "C", "Dm", "E"]
          + ["Am", "Bb", "Am", "E"]
          + ["Am", "Am", "Dm", "Am", "F", "G", "E", "E"])
SECTION = ["I"] * 4 + ["A"] * 8 + ["B"] * 8 + ["X"] * 4 + ["A2"] * 8
CADENCE = (4, 12, 20, 28)
## the march's octaves (root, fifth) and the hum's roots
ROOT2 = {"Am": "A2", "F": "F2", "E": "E2", "Dm": "D2", "G": "G2", "C": "C2", "Bb": "Bb1"}
FIFTH = {"Am": 7, "F": 7, "E": 7, "Dm": 7, "G": 7, "C": 7, "Bb": 7}
HUM_ROOT = {"Am": "A2", "F": "F2", "E": "E2", "Dm": "D3", "G": "G2", "C": "C3", "Bb": "Bb2"}
WOMEN = {"Am": "E4", "F": "F4", "E": "E4", "Dm": "F4", "G": "G4", "C": "E4", "Bb": "F4"}
MARCH = [0, 0, 1, 0, 2, 0, 1, 0]                 # root, fifth, octave per eighth
## the drill, per sixteenth: (stroke, velocity)
DRILL = {0: ("dum", 0.85), 2: ("tek", 0.38), 3: ("ghost", 0.3), 4: ("tek", 0.75), 7: ("ghost", 0.3),
         8: ("dum", 0.7), 10: ("tek", 0.38), 11: ("tek", 0.4), 12: ("tek", 0.75), 14: ("ghost", 0.3),
         15: ("ghost", 0.34)}

## the edict, (pitch, eighths) per bar: two rising-fifth summonses, then the steps down to the half cadence
EDICT = [[("A4", 3), ("A4", 1), ("E5", 4)], [("D5", 2), ("C5", 2), ("B4", 2), ("C5", 2)],
         [("D5", 3), ("D5", 1), ("A5", 4)], [("G5", 2), ("F5", 2), ("E5", 4)],
         [("F5", 3), ("E5", 1), ("D5", 2), ("C5", 2)], [("D5", 3), ("C5", 1), ("B4", 2), ("G4", 2)],
         [("C5", 2), ("B4", 2), ("A4", 2), ("G#4", 2)], [("B4", 6), (None, 2)]]
## the lament (B), in C major over F C G Am F C Dm E
LAMENT = [[("A5", 4), ("G5", 2), ("F5", 2)], [("E5", 4), ("D5", 2), ("E5", 2)], [("D5", 6), ("B4", 2)],
          [("C5", 8)], [("A5", 4), ("C6", 2), ("B5", 2)], [("G5", 6), ("E5", 2)],
          [("F5", 4), ("E5", 2), ("D5", 2)], [("E5", 6), (None, 2)]]
## the counterline over the edict (A'')
COUNTER = [[(None, 2), ("E5", 2), ("A5", 4)], [("G5", 4), ("E5", 4)], [("F5", 6), ("A5", 2)],
           [("G5", 2), ("F5", 2), ("E5", 4)], [("A5", 4), ("C6", 4)], [("B5", 4), ("G5", 4)],
           [("G#5", 4), ("B5", 2), ("A5", 2)], [("G#5", 6), (None, 2)]]


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT + DOWNBEAT_OFFSET_S


class Placer:
    """Adds each loop event, and a copy of every event that sounds in the loop's last INTRO_BARS bars (including the
    tails of earlier ones) to the intro, at the same place relative to the loop end."""

    def __init__(self, mx: LoopMixer):
        self.mx = mx
        self.win = LOOP_S - INTRO_S

    def __call__(self, bus: str, x: np.ndarray, t: float, pan: float = 0.0) -> None:
        # (bar 32's last sixteenth lands on the loop end itself: wrap it first, so the splice's cold copy has it)
        tm = t % LOOP_S
        self.mx.add(bus, x, tm, pan=pan)
        if tm + x.shape[0] / SR > self.win:
            self.mx.add(bus, x, tm - self.win, pan=pan, part="intro")


def shield(vel: float, variant: int) -> np.ndarray:
    """A lacquered shell shield struck with a spear shaft: a hand-damped kettle gong under a small, hard slap."""
    plate = kettle_gong(n("E3"), vel, seed=SEED + 700 + variant % 3, t60=1.2, damp_at=0.09)
    slap = frame_drum("slap", min(1.0, vel * 1.1), size=0.6, variant=variant % 4, seed=SEED + 9)
    out = np.zeros(max(len(plate), len(slap)))
    out[: len(plate)] += plate
    out[: len(slap)] += 0.7 * slap
    return out


def add_line(place: Placer, bus: str, bars: list, start_bar: int, seed: int, vel: float, octave: int = 0,
             pan: float = 0.0) -> None:
    """A melody: on the flute (bus 'flute') or on the piano in octaves (bus 'piano')."""
    g = rng(seed)
    first = True
    for i, bar in enumerate(bars):
        pos = t_of(start_bar + i)
        for p, e in bar:
            d = e * E8
            if p is None:
                pos += d
                first = True
                continue
            m = n(p) + 12 * octave
            if bus == "flute":
                x = breath_flute(m, d * 0.95 + 0.03, vel * g.uniform(0.95, 1.03),
                                 seed=seed + int(round(pos * 1000)), breath=0.42,
                                 scoop_cents=30.0 if first or e >= 4 else 8.0, vib_cents=13.0 if e >= 4 else 0.0,
                                 vib_rate=4.8, swell=0.25 if e >= 6 else 0.0, attack=0.07, release=0.3, beta=0.55)
                place("flute", x, pos - FLUTE_PRE + float(g.normal(0, 0.004)), pan=pan)
            else:
                v = vel * (1.0 if e >= 3 else 0.88) * g.uniform(0.97, 1.02)
                for k, mm in enumerate((m, m - 12)):
                    x = piano_note(mm, v * (1.0 if k == 0 else 0.85), d * 0.8,
                                   seed=seed + 7 * k + int(round(pos * 1000)))
                    place("piano", x, pos + 0.004 * k, pan=pan + (0.08 if k == 0 else -0.08))
            pos += d
            first = False


def build(mx: LoopMixer) -> None:
    place = Placer(mx)
    g = rng(SEED)
    for bar, (ch, sec) in enumerate(zip(CHORDS, SECTION), start=1):
        root = n(ROOT2[ch])
        tones = (root, root + FIFTH[ch], root + 12)
        hound = sec == "X"
        people = sec == "B"
        # the march: low piano octaves in eighths (quarters, softer, for the people)
        for e, k in enumerate(MARCH):
            if people and e % 2:
                continue
            acc = e in (0, 4)
            v = (0.62 if acc else 0.48) * (0.75 if people else 1.0) * g.uniform(0.96, 1.03)
            hold = (2 * E8 if people else E8) * 0.7
            for j, mm in enumerate((tones[k], tones[k] + 12)):
                place("march", piano_note(mm, v * (1.0 if j == 0 else 0.8), hold,
                                          seed=SEED + 1000 + 16 * bar + 2 * e + j),
                      t_of(bar, e / 2) + 0.002 * j, pan=-0.2)
        # the bass: half notes on the root; the hound snaps through the flattened second in eighths
        if hound:
            for e, off in enumerate((0, 0, 12, 0, 1, 0, 7, 0)):
                v = (0.8 if e % 2 == 0 else 0.62) * g.uniform(0.95, 1.03)
                place("bass", bass_note(root - 12 + off, E8 * 0.9, v, seed=SEED + 2000 + 10 * bar + e, mute=0.3),
                      t_of(bar, e / 2))
        else:
            for h in (0, 2):
                place("bass", bass_note(root - 12 + (0 if h == 0 or people else 7), 2 * BEAT * 0.95,
                                        0.8 * g.uniform(0.95, 1.03), seed=SEED + 2000 + 10 * bar + h, mute=0.2),
                      t_of(bar, h))
        # the drill
        if people:
            for b4, v in ((0, 0.7), (2, 0.55)):
                place("drums", frame_drum("dum", v, variant=bar * 2 + b4, seed=SEED + 3), t_of(bar, b4))
            for s in (6, 14):
                place("drums", frame_drum("ghost", 0.22, variant=bar + s, seed=SEED + 3), t_of(bar, s / 4), pan=0.15)
            place("big", big_drum(0.55, variant=bar, seed=SEED + 4), t_of(bar))
        else:
            lvl = 0.85 if sec == "I" else 1.0
            for s in range(16):
                if hound:
                    stroke, v = DRILL.get(s, ("tek", 0.3))
                    if s % 4 == 0:
                        v = max(v, 0.7)
                else:
                    if s not in DRILL:
                        continue
                    stroke, v = DRILL[s]
                place("drums", frame_drum(stroke, lvl * v, variant=(bar * 16 + s) % 6, seed=SEED + 3),
                      t_of(bar, s / 4) + float(g.normal(0, 0.001)), pan=0.12 if stroke in ("tek", "ghost") else 0.0)
            for b4 in ((0, 1, 2, 3) if hound else (0, 2)):
                place("big", big_drum((0.8 if b4 == 0 else 0.62) * lvl, variant=bar + b4, seed=SEED + 4), t_of(bar, b4))
        # the shields
        if bar == BARS:
            for k, b4 in enumerate((1, 1.5, 2, 2.5, 3, 3.25, 3.5)):
                place("shield", shield(0.6 + 0.05 * k, k), t_of(bar, b4), pan=0.15 if k % 2 else -0.15)
        elif bar in CADENCE:
            for k, b4 in enumerate((1, 2, 3)):
                place("shield", shield(0.75 + 0.05 * k, bar + k), t_of(bar, b4), pan=(-0.2, 0.0, 0.2)[k])
        elif hound:
            for k, b4 in enumerate((1, 3)):
                place("shield", shield(0.75, bar + k), t_of(bar, b4), pan=-0.15 if k else 0.15)
        elif not people:
            place("shield", shield(0.62, bar), t_of(bar, 3), pan=0.1)
    # the Order: the men's hum on the roots, the whole loop; the women above in the people's sections
    men = hum_ensemble([(n(HUM_ROOT[c]), BAR) for c in CHORDS], voices=14, seed=SEED + 50, register="low",
                       loop=True)
    # (one exact cycle with its tails already wrapped onto its start: the loop gets all of it at 0, and the intro
    # only the cycle's last INTRO_S, so the hum is not doubled after the splice)
    mx.add("hum", men, 0.0)
    mx.add("hum", men[len(men) - mx.S:], 0.0, part="intro")
    for start in (13, 25):
        line = [(n(WOMEN[c]), BAR) for c in CHORDS[start - 1: start + 7]]
        place("women", hum_ensemble(line, voices=8, seed=SEED + 60 + start, register="high"), t_of(start))
    for bar, v in ((1, 0.5), (13, 0.45), (21, 0.65), (25, 0.55)):
        place("gong", large_gong(n("A1"), v, seed=SEED + 80 + bar, t60=6.0), t_of(bar))
    add_line(place, "piano", EDICT, 5, SEED + 100, 0.78, pan=0.05)
    add_line(place, "flute", LAMENT, 13, SEED + 200, 0.75, pan=-0.1)
    add_line(place, "piano", EDICT, 25, SEED + 300, 0.82, octave=-1, pan=0.05)
    add_line(place, "flute", COUNTER, 25, SEED + 400, 0.7, pan=-0.2)


## Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]) for these levels relative to the
## leads (the piano's edict and the flute, 0 LU each, measured over the loop where each plays): drums -5, the big
## drum -8, the march -8, the bass -7, the shields -9, the men's hum -9, the women's hum -11, the gong -14. The drill
## and the shields keep the line; the hum is under everything, the way the Order is.
GAINS = {"piano": 5.4, "flute": -0.4, "march": -1.2, "bass": -2.8, "drums": -2.2, "big": -7.1, "shield": -9.6,
         "hum": -0.6, "women": -9.0, "gong": -15.1}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=INTRO_S, loop_s=LOOP_S, intro_tail_s=6.0, preroll_s=8.0)
    mx.bus("piano", GAINS["piano"], send=0.25, process=lambda x: filt(x, [bq_highpass(90, 0.7),
                                                                          bq_peak(2500, 1.5, 1.0)]))
    mx.bus("flute", GAINS["flute"], send=0.32, process=lambda x: filt(x, [bq_highpass(220, 0.7)]))
    mx.bus("march", GAINS["march"], send=0.15, process=lambda x: filt(x, [bq_highpass(45, 0.7),
                                                                          bq_lowpass(4000, 0.7)]))
    mx.bus("bass", GAINS["bass"], send=0.0, process=lambda x: filt(x, [bq_highpass(32, 0.7), bq_lowpass(2500, 0.7)]))
    mx.bus("drums", GAINS["drums"], send=0.14, process=lambda x: filt(x, [bq_highpass(40, 0.7),
                                                                          bq_peak(3500, 1.5, 0.8)]))
    mx.bus("big", GAINS["big"], send=0.18, process=lambda x: filt(x, [bq_highpass(30, 0.7)]))
    mx.bus("shield", GAINS["shield"], send=0.3, process=lambda x: filt(x, [bq_highpass(80, 0.7)]))
    mx.bus("hum", GAINS["hum"], send=0.35, process=lambda x: filt(x, [bq_highpass(60, 0.7)]))
    mx.bus("women", GAINS["women"], send=0.4, process=lambda x: filt(x, [bq_highpass(150, 0.7)]))
    mx.bus("gong", GAINS["gong"], send=0.45)
    build(mx)
    hall = ModFDNReverb(rt60=1.9, rt60_high=0.9, predelay=0.022, size=0.95, mod_depth=8.0, mod_rate=0.6,
                        early_level=0.3, seed=SEED % 9973)
    intro, loop = mx.render(reverb=hall, reverb_return_db=-3.5)
    rep: dict = {}
    intro, loop = master_loop(intro, loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    y = np.concatenate([intro, loop])
    S, L = len(intro), len(loop)
    write_ogg(out_path, y, quality=3.5, tags={"LOOPSTART": str(S), "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, S, L, BPM, 4,
                       extra={"intro_bars": INTRO_BARS, "loop_bars": BARS, "downbeat_offset_s": DOWNBEAT_OFFSET_S})
    m = measure(y)
    if stats is not None:
        stats["splice_residual_db"] = mx.splice_residual_db
        stats["bus_lufs"] = dict(mx.bus_lufs)
        stats["limiter"] = rep
    if verbose:
        print(f"stillguard_inquisitor: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS"
              f"  TP {m['true_peak_dbtp']:.2f} dBTP  loop {S}+{L}  splice {mx.splice_residual_db:.1f} dB"
              f"  limiter {rep}")
        print("  buses", {k: round(v, 1) for k, v in mx.bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
