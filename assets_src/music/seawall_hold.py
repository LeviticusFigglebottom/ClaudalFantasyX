"""`seawall_hold`: Ch8, holding the Fisher Stair while the low town climbs (M3-AUD-822; act1_ch08.md B10-B14, the three
waves before the Undertow's Reach): three synchronized stems, a 72 s loop.

Original composition for this project (SPEC §2, §9). The ground, the cellos' straining line, the drum pattern and the
hauling rhythm below were written for this fight and are not derived from any existing melody. Original-material
check: the line is three phrases of long notes over a four-chord ground (Bm G A F#), each phrase climbing higher
than the last (F#3, then B3, then F#4) and falling back; it shares no phrase with Corrow's ground and tune
(corrow_seawall.py) or with the Reach's theme (undertows_reach.py), and none with any melody we know. The style
evoked is a heavy processional on large drums; nothing is quoted.

The brief: "One battle cue in three stems that stack across the waves: (1) taiko-like drums and a held-low string;
(2) adds a driving rope-and-pulley rhythm (percussion that sounds like hauling); (3) adds the storm's own note as a
sub-bass drone. It should feel like effort, not triumph." Wave 1 holds the stair; in wave 2 Liss's hoist lifts
baskets of children up the wall's face and the party protects the rope; in wave 3 the last of the low town comes up
with the storm at the wall. So nothing in the cue arrives: the ground ends every eight bars on F# major, the
dominant, and climbs back to B minor; the line strains up a little further each time and falls back; the drums are
heavy and on the beat, a weight being carried, never a march.

B minor (Corrow's key; the F# chord takes A#), 4/4 at 80 BPM (a bar is 3.0 s), 24 bars: three statements of an
eight-bar ground, Bm (2) G (2) A (2) F# (2), the third with E minor in place of A.

**Stem 1** (`seawall_hold_p1.ogg`, wave 1, plays from the start):
* the drums: a big drum (synth.drums.big_drum) on 1 and 3, heavier on 1, and a pair at the end of each two bars;
  frame drums struck as a taiko-like mid drum (don, don-ko, don, don) with rim strokes between; a roll into every
  eighth bar;
* the held-low string: basses and cellos (synth.pad through string_body, dark) holding root, fifth and octave
  for two bars a chord;
* the cellos' line over it, in long notes, one phrase per statement;
* Corrow's beacon, the kettle gong on F# (corrow_seawall's and undertows_reach's), at each statement.

**Stem 2** (`seawall_hold_p2.ogg`, wave 2, the hoist):
* the haul: on beats 1 and 3 the rope takes the strain (a creak: friction through rope-fibre resonances, rising
  with the pull, and the pawl clicking over the ratchet), and on 2 and 4 the block catches (a hard wooden knock);
  under each pull a foot set against the stone (a muted low drum);
* muted plucks in eighths on the chord tones and a fingered bass on the root in pairs: the drive.

**Stem 3** (`seawall_hold_p3.ogg`, wave 3, the storm at the wall):
* the storm's own note: G (the Reach's mode is G octatonic, undertows_reach.py), as a sub-bass drone on G1 with its
  octave and twelfth, swelling every four bars, every partial snapped to a whole number of cycles per loop so the
  drone is exactly periodic; under the B minor it makes every chord lean (G under B minor, under A, under F#);
* a low storm rumble that rises and falls with it.

Mastering (as the Drownbell and the Reach): the three stems share one gain (the full stack at -16 LUFS) and one
limiter gain curve computed on the full stack (synth.mixer.limit_gain), so the stems sum exactly to the limited mix.
Stems 2 and 3 are trimmed so each step up is about 1.5-2 LU, and stem 1 alone is the quietest. Loop: LOOPSTART = 0 on
all three; equal lengths. The files start a sixteenth before bar 1's downbeat (the sidecars' `downbeat_offset_s`), so
the wrap seam falls in a quiet sixteenth.

Render:  python3 assets_src/music/seawall_hold.py   (or tools/audio/render_all.py --only seawall_hold)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, os.path.join(ROOT, "assets_src", "sfx"))

import numpy as np  # noqa: E402

from field_ambience import circ_noise, modal, plfo, stick_slip  # noqa: E402
from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, midi_to_hz, rng  # noqa: E402
from synth.electric import bass_note, string_pluck  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "music")
OUT = os.path.join(OUT_DIR, "seawall_hold_p1.ogg")
STEM_NAMES = ("seawall_hold_p1.ogg", "seawall_hold_p2.ogg", "seawall_hold_p3.ogg")
SEED = 20261827
TARGET_LUFS = -16.0
BPM = 80.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 24
LOOP_S = BARS * BAR
## the files start a sixteenth before bar 1's downbeat; see render()
LEAD_IN_BEATS = 0.25
## Trims at mastering (dB) on stems 2 and 3, so each layer lifts the stack about 1.5-2 LU (render prints the steps).
STEM2_GAIN_DB = 0.5
STEM3_GAIN_DB = 2.5
## Vorbis quality per stem: the hoist's creaks, clicks and knocks are noise-like, so stem 2 is a little lower
## (ADR 0171: a 60 s loop <= 0.9 MiB per file)
STEM_QUALITY = (3.0, 2.5, 3.0)
STORM_NOTE = "G1"             # the storm's own note (the Reach's G)

CHORDS = ["Bm", "Bm", "G", "G", "A", "A", "F#", "F#"] * 2 + ["Bm", "Bm", "G", "G", "Em", "Em", "F#", "F#"]
ROOTS = {"Bm": "B1", "G": "G1", "A": "A1", "F#": "F#1", "Em": "E2"}
## chord tones for the plucks (root, third, fifth, octave)
TONES = {"Bm": ["B3", "D4", "F#4", "B4"], "G": ["G3", "B3", "D4", "G4"], "A": ["A3", "C#4", "E4", "A4"],
         "F#": ["F#3", "A#3", "C#4", "F#4"], "Em": ["E3", "G3", "B3", "E4"]}
PLUCK = [0, 2, 1, 2, 3, 2, 1, 2]
## the cellos' line: one phrase per statement, (pitch, bars); each climbs higher and falls back
LINE = [
    [("F#3", 2), ("G3", 1.5), ("F#3", .5), ("E3", 2), ("C#3", 2)],
    [("B3", 2), ("B3", 1), ("D4", 1), ("C#4", 2), ("A#3", 2)],
    [("D4", 2), ("D4", 1), ("E4", 1), ("G4", 1), ("E4", 1), ("F#4", 2)],
]
## stem 1's mid drum per bar: (beat, stroke, velocity); "don, don-ko, don, don" with rim strokes between
MID = [(0.0, "dum", 0.85), (1.0, "dum", 0.62), (1.75, "dum", 0.42), (2.0, "dum", 0.75), (3.0, "dum", 0.6),
       (0.5, "tek", 0.3), (2.5, "tek", 0.32), (3.5, "tek", 0.28)]


def t_of(bar: int, beat: float = 0.0) -> float:
    """Seconds from the loop start to `beat` (0-based) of 1-based `bar`."""
    return (bar - 1) * BAR + beat * BEAT


def build_p1(mx: LoopMixer) -> None:
    g = rng(SEED)
    for bar, ch in enumerate(CHORDS, start=1):
        # the big drum: 1 and 3; a pair at the end of each two bars
        hits = [(0.0, 0.95), (2.0, 0.72)] + ([(3.0, 0.62), (3.5, 0.7)] if bar % 2 == 0 else [])
        for b, v in hits:
            mx.add("taiko", big_drum(v * g.uniform(0.94, 1.04), variant=bar * 8 + int(2 * b), seed=SEED + 4),
                   t_of(bar, b), pan=0.0)
        roll = bar % 8 == 0
        for b, stroke, v in MID:
            if roll and b >= 2.0:
                continue
            mx.add("drums", frame_drum(stroke, v * g.uniform(0.9, 1.06), variant=bar * 16 + int(4 * b), size=1.4,
                                       seed=SEED + 3), t_of(bar, b) + float(g.normal(0, 0.003)),
                   pan=0.12 if stroke == "dum" else -0.25)
        if roll:                                     # a roll into the next statement, ending a sixteenth early
            for k in range(7):
                b = 2.0 + 0.25 * k
                mx.add("drums", frame_drum("dum", 0.4 + 0.07 * k, variant=200 + k, size=1.4, seed=SEED + 5),
                       t_of(bar, b), pan=0.12 - 0.04 * k)
    # the held-low string: root, fifth and octave, two bars a chord
    for bar in range(1, BARS + 1, 2):
        root = n(ROOTS[CHORDS[bar - 1]])
        x = pad_chord([root, root + 7, root + 12], 2 * BAR - 0.05, 0.9, seed=SEED + 100 + bar, voices=5,
                      spread_cents=10.0, attack=0.5, release=0.6, width=0.6)
        mx.add("low", x, t_of(bar) - 0.05)
    # the cellos' line
    for s, phrase in enumerate(LINE):
        pos = t_of(1 + 8 * s)
        for i, (p, bars) in enumerate(phrase):
            d = bars * BAR
            x = pad_chord([n(p)], d + 0.15, 0.75 + 0.08 * s, seed=SEED + 300 + 20 * s + i, voices=4,
                          spread_cents=7.0, attack=0.45, release=0.8, width=0.4)
            mx.add("line", x, pos - 0.1)
            pos += d
    for s in range(3):                               # Corrow's beacon at each statement
        mx.add("beacon", kettle_gong(n("F#4"), 0.4, seed=SEED + 400 + s, t60=3.0), t_of(1 + 8 * s), pan=0.35)


def creak(g, seconds: float) -> np.ndarray:
    """The rope taking the strain: friction releasing through rope-fibre and block resonances, rising with the pull."""
    return stick_slip(g, seconds, 14.0, 60.0, [(230.0, 1.0), (520.0, 0.6), (1100.0, 0.35), (2300.0, 0.15)], q=7.0)


def pawl(g, seconds: float) -> np.ndarray:
    """The pawl clicking over the ratchet as the rope runs: small hard ticks, quickening and then slowing."""
    N = int(seconds * SR)
    out = np.zeros(N)
    tt = 0.03
    while tt < seconds - 0.03:
        k = modal([float(g.uniform(2600, 3400)), float(g.uniform(5200, 6400))], [0.006, 0.003], [1.0, 0.4], 0.03, g,
                  click=0.3)
        s = int(tt * SR)
        out[s: s + len(k)] += k[: N - s] * float(g.uniform(0.5, 1.0))
        x = tt / seconds
        tt += 1.0 / (9.0 + 9.0 * np.sin(np.pi * x))
    return out


def block(g, v: float) -> np.ndarray:
    """The block catching: a hard knock of wood on wood (the sheave in its cheeks), with a little rattle."""
    f = float(g.uniform(180.0, 210.0))
    x = modal([f, f * 2.6, f * 4.9, f * 7.3], [0.07, 0.035, 0.018, 0.01], [1.0, 0.55, 0.3, 0.15], 0.35, g, click=0.6)
    return v * x


def build_p2(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    for bar, ch in enumerate(CHORDS, start=1):
        tones = TONES[ch]
        root = n(ROOTS[ch])
        for b in (0.0, 2.0):                                     # the pulls on 1 and 3
            mx.add("rope", creak(rng(SEED + 1000 + 4 * bar + int(b)), 1.25 * BEAT), t_of(bar, b) + 0.02,
                   pan=-0.3 if b == 0 else -0.15)
            mx.add("pawl", pawl(rng(SEED + 2000 + 4 * bar + int(b)), 1.1 * BEAT), t_of(bar, b) + 0.06, pan=-0.45)
            mx.add("stamp", frame_drum("dum", 0.7 * g.uniform(0.92, 1.05), variant=bar * 4 + int(b), size=1.8,
                                       seed=SEED + 7), t_of(bar, b) + 0.01, pan=0.0)
        for b in (1.0, 3.0):                                     # the block catches on 2 and 4
            mx.add("block", block(rng(SEED + 3000 + 4 * bar + int(b)), 0.9 if b == 1.0 else 0.75),
                   t_of(bar, b) + float(g.normal(0, 0.004)), pan=0.4)
        for e in range(8):                                       # muted plucks in eighths
            v = (0.55 if e % 2 == 0 else 0.4) * g.uniform(0.9, 1.06)
            x = string_pluck(n(tones[PLUCK[e]]), BEAT * 0.45, v, seed=SEED + 4000 + 10 * bar + e, pick_pos=0.15,
                             t60=1.2, mute=0.5, max_f=4200.0, release=0.03)
            mx.add("pluck", x, t_of(bar, e / 2) + float(g.normal(0, 0.003)), pan=0.3 if e % 2 else 0.18)
        for b, o, v in ((0.0, 0, 0.85), (0.5, 0, 0.55), (2.0, 0, 0.75), (2.5, 12, 0.55)):   # the bass in pairs
            x = bass_note(root + o, 0.45 * BEAT, v * g.uniform(0.93, 1.05), seed=SEED + 5000 + 10 * bar + int(2 * b),
                          mute=0.4)
            mx.add("bass", x, t_of(bar, b) + 0.003)


def storm_drone(L: int, g) -> np.ndarray:
    """The storm's own note: G1 with its octave and twelfth, each partial snapped to whole cycles per loop and doubled
    by a slowly beating partner, swelling every four bars. (L,) mono, exactly periodic."""
    t = np.arange(L) / SR
    f1 = midi_to_hz(n(STORM_NOTE))
    out = np.zeros(L)
    for r, a in ((1.0, 1.0), (2.0, 0.45), (3.0, 0.22), (4.0, 0.08)):
        for dc, aa in ((0.0, 1.0), (0.12, 0.6)):
            f = max(1, round((f1 * r + dc) * L / SR)) * SR / L
            out += a * aa * np.sin(2 * np.pi * f * t + g.uniform(0, 6.28))
    swell = 0.7 + 0.3 * np.cos(2 * np.pi * t / (4 * BAR) + np.pi)     # 6 whole cycles per loop; loudest on bar 3, 7..
    return out * swell


def build_p3(mx: LoopMixer) -> None:
    L = mx.L
    g = rng(SEED + 2)
    mx.add("drone", storm_drone(L, g), 0.0, pan=0.0)
    t = np.arange(L) / SR
    swell = 0.6 + 0.4 * np.cos(2 * np.pi * t / (4 * BAR) + np.pi)
    rumble = circ_noise(L, g, [bq_lowpass(140.0, 0.7), bq_highpass(30.0, 0.7), bq_peak(60.0, 4.0, 0.8)])
    mx.add("rumble", rumble * swell * (0.85 + 0.15 * plfo(L, 0.3, g)), 0.0, pan=0.0)


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]) for the planned levels below.
GAINS = {
    "taiko": 0.0, "drums": -0.2, "low": 6.7, "line": 3.7, "beacon": -9.2,
    "rope": -2.3, "pawl": -14.4, "block": -8.5, "stamp": -4.5, "pluck": 7.8, "bass": -0.3,
    "drone": -16.1, "rumble": -22.3,
}
## The plan (LU relative to the stem-1 lead, the big drum, by each bus's integrated loudness over the loop).
PLAN = {
    "taiko": 0.0, "drums": -3.0, "low": -4.0, "line": -4.0, "beacon": -14.0,
    "rope": -6.0, "pawl": -12.0, "block": -5.0, "stamp": -8.0, "pluck": -8.0, "bass": -5.0,
    "drone": -3.0, "rumble": -9.0,
}


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 1:
        mx.bus("taiko", G["taiko"], send=0.18, process=lambda x: filt(x, [bq_highpass(30, 0.7)]))
        mx.bus("drums", G["drums"], send=0.15, process=lambda x: filt(x, [bq_highpass(45, 0.7),
                                                                           bq_peak(2800, 1.0, 0.8)]))
        mx.bus("low", G["low"], send=0.25, process=lambda x: string_body(x, cutoff=900.0))
        mx.bus("line", G["line"], send=0.35, process=lambda x: string_body(x, cutoff=1600.0))
        mx.bus("beacon", G["beacon"], send=0.45)
    elif stem == 2:
        mx.bus("rope", G["rope"], send=0.2, process=lambda x: filt(x, [bq_highpass(150, 0.7)]))
        mx.bus("pawl", G["pawl"], send=0.15, process=lambda x: filt(x, [bq_highpass(1500, 0.7)]))
        mx.bus("block", G["block"], send=0.2, process=lambda x: filt(x, [bq_highpass(120, 0.7)]))
        mx.bus("stamp", G["stamp"], send=0.1, process=lambda x: filt(x, [bq_highpass(40, 0.7), bq_lowpass(900, 0.7)]))
        mx.bus("pluck", G["pluck"], send=0.15, process=lambda x: filt(x, [bq_highpass(140, 0.7),
                                                                           bq_lowpass(4200, 0.7)]))
        mx.bus("bass", G["bass"], send=0.0, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_peak(90, 2.0, 0.9),
                                                                        bq_lowpass(2500, 0.7)]))
    else:
        mx.bus("drone", G["drone"], send=0.05, process=lambda x: filt(x, [bq_lowpass(400, 0.7)]))
        mx.bus("rumble", G["rumble"], send=0.15)


# Levels (LU relative to the big drum, the stem-1 lead; PLAN above): the mid drums -3, the held-low string -4, the
# cellos' line -4, the beacon -14; in stem 2 the rope's creak -6, the pawl -12, the block -5, the stamp -8, plucks
# -8, bass -5; in stem 3 the storm's drone -3 (it is mostly below 100 Hz, where the meter weighs little) and the
# rumble -9. GAINS were set from a render's measured bus loudness to land these, and confirmed by a second render.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    loops = []
    bus_lufs = {}
    for stem, build in ((1, build_p1), (2, build_p2), (3, build_p3)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
        _bus_setup(mx, stem)
        build(mx)
        wall = ModFDNReverb(rt60=2.2, rt60_high=0.9, predelay=0.025, size=1.1, mod_depth=8.0, mod_rate=0.5,
                            early_level=0.3, lowcut=110.0, seed=SEED % 9973)
        _, loop = mx.render(reverb=wall, reverb_return_db=-3.0)
        loops.append(loop)
        bus_lufs.update(mx.bus_lufs)
    loops[1] = loops[1] * db_to_lin(STEM2_GAIN_DB)
    loops[2] = loops[2] * db_to_lin(STEM3_GAIN_DB)
    # The loop is periodic, so the files may start anywhere: a sixteenth before bar 1's downbeat, so the wrap seam
    # falls in a quiet sixteenth instead of on the heaviest attack (big drum, mid drum, beacon and bass at once).
    lead_in = int(round(LEAD_IN_BEATS * BEAT * SR))
    loops = [np.roll(x, lead_in, axis=0) for x in loops]
    full = loops[0] + loops[1] + loops[2]
    gain = db_to_lin(TARGET_LUFS - integrated_lufs(full))
    ctx = int(0.05 * SR)
    L = len(full)
    # one limiter gain curve for all stems, from the full stack (wrap-aware), iterated to the target
    for _ in range(4):
        f = full * gain
        lg = limit_gain(np.concatenate([f[-ctx:], f, f[:ctx]]), -2.0)[ctx: ctx + L]
        cur = integrated_lufs(f * lg[:, None])
        if abs(cur - TARGET_LUFS) < 0.1:
            break
        gain *= db_to_lin(TARGET_LUFS - cur)
    stems = [s * gain * lg[:, None] for s in loops]
    paths = [out_path] + [os.path.join(os.path.dirname(out_path), s) for s in STEM_NAMES[1:]]
    extra = {"stems_of": "seawall_hold", "loop_bars": BARS, "downbeat_offset_s": lead_in / SR}
    for x, p, q in zip(stems, paths, STEM_QUALITY):
        write_ogg(p, x, quality=q, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
        write_loop_sidecar(os.path.splitext(p)[0] + ".loop.json", SR, 0, L, BPM, 4, extra=extra)
    m = measure(stems[0] + stems[1] + stems[2])
    steps = [integrated_lufs(stems[0]), integrated_lufs(stems[0] + stems[1])]
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
        stats["stem1_lufs"], stats["stems12_lufs"] = steps
        stats["limited_fraction"] = float((lg < 0.999).mean())
    if verbose:
        print(f"seawall_hold: {m['seconds']:.2f}s  full {m['integrated_lufs']:.2f} LUFS TP "
              f"{m['true_peak_dbtp']:.2f} dBTP; stem 1 alone {steps[0]:.2f}, stems 1+2 {steps[1]:.2f} LUFS; "
              f"limited {(lg < 0.999).mean() * 100:.2f} %, max {-20 * np.log10(max(lg.min(), 1e-9)):.2f} dB")
        lead = bus_lufs["taiko"]
        print("  buses (LU vs the big drum)", {k: round(v - lead, 1) for k, v in bus_lufs.items()})
        print("  gains for the plan", {k: round(GAINS[k] + PLAN[k] - (v - lead), 1) for k, v in bus_lufs.items()})
    return m


if __name__ == "__main__":
    render()
