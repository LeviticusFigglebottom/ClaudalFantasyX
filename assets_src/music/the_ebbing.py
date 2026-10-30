"""`the_ebbing`: Ch9 "The Ebbing" (M3-AUD-05; act_outline.md Ch9), about 2 minutes, through-composed.

Original composition for this project (SPEC §2): built from our own Hush theme (hush_theme_v2.py: its harmony and
its three phrases MEL_A, MEL_B, MEL_C), not from any existing melody. Corrow's shore at night after the wall fell;
hundreds drowned. Asha performs her first great Ebbing, dancing on a raft as the motes follow her lantern-staff out
to sea, drifting *down and seaward*. The most beautiful sequence in Act I; Pell, watching: "Beautiful. And
pointing the wrong way."

So the cue is the Hush danced: the Cantor's line (the vocalise-like instrument of hush_first_verse: a breath flute
shaped by an open "ah") over the grand piano, with a slow 3/4 dance under it (two metallophones interlocking on
the eighths, a soft frame drum), and glass motes that only ever *fall*: every arpeggio in the glass runs downward.
The beauty is real; the wrongness is in the direction.

3/4 at 64 BPM (a bar is 2.81 s), 40 bars, laid to the scene as played (the Lead's 10-30 19:25 item: the cue must
peak on the hero frame and resolve on the letting-down). ch09_the_ebbing starts it on the gathering (the first held
input) and reaches the long line, N11, the hero frame, about 12 s in; at its floor the scene silences it on the
letting-down about 44 s in, and every pause of the held input only adds time. So:
1-4 the drone and the first falling motes (the gathering) | 5-12 MEL_A with the dance full and the glass doubling the
line an octave up (the long line: the river of motes) | 13-20 MEL_B, the dance (the stair, the letting-down) | 21-28
MEL_A again, the Cantor over the dance | 29-34 MEL_C, slower, the dance thinning | 35-40 the piano's last A minor chord
and the motes falling away, ending on E (unresolved), for a player who lingers.
Wherever the scene silences it, `the_ebbing_release` takes over (music.json `release`; AudioDirector): the last
chord, the motes falling away twice and the Cantor's E held, about 9 s, unresolved, under the next scene's cue.

Render:  python3 assets_src/music/the_ebbing.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.grand import PianoBody  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.performance import plan_pedal  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HUSH = _mod("hush_theme_v2")
HFV = _mod("hush_first_verse")

OUT = os.path.join(ROOT, "assets", "audio", "music", "the_ebbing.ogg")
SEED = 20261114
BPM = 64.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
T0 = 0.5
FLUTE_PRE = 0.065
PENTA = ["A4", "C5", "D5", "E5", "G5"]
FALL = ["E6", "C6", "A5", "E5"]          # the motes' figure: always downward


def t_of(bar: int, beat: float = 0.0) -> float:
    return T0 + (bar - 1) * BAR + beat * BEAT


# M3-C09-06: where each movement starts (s from the first sample), for the cutscene's `@wait music=<marker>`. The held
# input pauses the dance, not the music (decided: the cue runs on through a pause, and the dance re-syncs on the next
# of these). music.json's `markers` row carries the same numbers (tools/tests/test_music_markers.py).
MOVEMENTS = {"dance_full": 5, "dance": 13, "cantor": 21, "thinning": 29, "last_chord": 35}
OUT_RELEASE = os.path.join(ROOT, "assets", "audio", "music", "the_ebbing_release.ogg")


def markers() -> dict[str, float]:
    """Each movement's first downbeat (s)."""
    return {name: t_of(bar) for name, bar in MOVEMENTS.items()}


def lh_for(bar: int) -> str:
    """The piano's chord in bar `bar`: Hush bars 1-2 for the intro, then the theme's bars in order."""
    hush_bar = {**{b: 1 for b in range(1, 5)}, **{b: b - 2 for b in range(5, 13)}, **{b: b - 2 for b in range(13, 21)},
                **{b: b - 18 for b in range(21, 29)}, **{b: b - 10 for b in range(29, 35)}}.get(bar, 24)
    return HUSH.LH[hush_bar]


def melody(mel: list, start_bar: int, slow: float = 1.0) -> list[tuple[float, float, float, float]]:
    out, pos = [], 0.0
    for p, beats, v in mel:
        out.append((t_of(start_bar, pos * slow), beats * BEAT * slow, n(p), v))
        pos += beats
    return out


# Bus gains from measured bus loudness (render(stats=...)): the Cantor's line at L, the piano L-3, the dance L-8,
# the glass motes L-10, the drone L-10, the drum L-12. (The grand piano model's raw level is about 35 dB under the
# breath flute's, hence its large gain.)
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    bars = [lh_for(b) for b in range(1, 41)]
    acc = HFV._broken_chords(bars[:34], T0, BAR, 0.8, g)
    final = [dict(m=n(p), vel=0.24 - 0.02 * j, t0=t_of(35) + 0.1 * j, key_up=5 * BAR, role="bass" if j < 2 else "acc")
             for j, p in enumerate(["A1", "A2", "E3", "B3", "C4", "E4"])]
    notes = acc + final
    pedal = plan_pedal([t_of(b) for b in range(2, 36)], start=T0, end_release=t_of(39), release_len=4.0, g=g)
    mx = Mixer(t_of(41) + 8.0)
    mx.bus("piano", 27.7, send=0.25, process=PianoBody(pedal))
    mx.bus("cantor", 0.0, send=0.4, process=HFV.vocalise_bus)
    mx.bus("dance", 8.3, send=0.35)
    mx.bus("drum", -1.8, send=0.2)
    mx.bus("motes", 4.7, send=0.6, process=lambda x: filt(x, [bq_highpass(400, 0.7)]))
    mx.bus("drone", -5.4, send=0.25, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1500, 0.6)]))
    mx.add("drone", HFV.drone(t_of(41), rng(SEED + 1)), 0.0)
    for nt, x in zip(notes, render_jobs(HFV._piano_jobs(notes, pedal, SEED + 5))):
        mx.add("piano", x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    lines = (melody(HUSH.MEL_A, 5) + melody(HUSH.MEL_B, 13) + melody(HUSH.MEL_A, 21) + melody(HUSH.MEL_C, 29, 1.04))
    for i, (t0, d, m, v) in enumerate(lines):
        x = breath_flute(m, d + 0.05, 0.42 + 0.3 * v, seed=SEED + 31 * i, breath=0.18, scoop_cents=35.0,
                         vib_cents=16.0, vib_rate=5.0, swell=0.2 if d > 1.5 * BEAT else 0.0, attack=0.12, release=0.4,
                         beta=0.5)
        mx.add("cantor", x, t0 - FLUTE_PRE, pan=-0.05)
    for i, (t0, d, m, _) in enumerate(melody(HUSH.MEL_A, 5)):           # the glass doubles the line, an octave up
        y = metallophone_note(m + 12, 0.22, seed=SEED + 2000 + i, decay=3.0, hardness=0.3, ombak_hz=5.0)
        mx.add("motes", y, t0, pan=0.3)
    for bar in range(5, 35):                                             # the dance, full at once on the long line
        full = 5 <= bar <= 12
        thin = bar >= 29
        for e in range(6):
            if thin and e % 2:
                continue
            p = PENTA[(bar * 2 + [0, 2, 1, 3, 2, 4][e]) % len(PENTA)]
            v = (0.26 if e in (0, 3) else 0.2) * (1.1 if full else 1.0) * g.uniform(0.9, 1.05)
            x = metallophone_note(n(p), v, seed=SEED + 100 * bar + e, decay=2.0, hardness=0.3, ombak_hz=5.5,
                                  damp_at=BEAT * 0.9)
            mx.add("dance", x, t_of(bar, e * 0.5) + float(g.normal(0, 0.005)), pan=-0.4 if e % 2 == 0 else 0.4)
        for beat, (stroke, v) in enumerate((("dum", 0.4), ("ghost", 0.14), ("tek", 0.22))):
            if thin and stroke != "dum":
                continue
            mx.add("drum", frame_drum(stroke, v, variant=bar * 3 + beat, seed=SEED + 2), t_of(bar, beat), pan=0.1)
    for k, bar in enumerate([1, 3, 6, 10, 14, 18, 22, 26, 30, 33, 35, 36, 37, 38, 39]):   # the motes fall
        for j, p in enumerate(FALL):
            x = metallophone_note(n(p) + (12 if k % 3 == 0 else 0), 0.16 + 0.04 * (bar >= 35), seed=SEED + 5000 + 10 * k + j,
                                  decay=4.5, hardness=0.25, ombak_hz=4.0)
            mx.add("motes", x, t_of(bar, 1.0) + 0.22 * j, pan=0.55 - 0.3 * j)
    hall = ModFDNReverb(rt60=3.6, rt60_high=1.4, predelay=0.03, size=1.2, mod_depth=9.0, mod_rate=0.45,
                        early_level=0.2, lowcut=90.0, seed=SEED % 9973)
    st: dict = {}
    HUSH._bus_stats(mx, st)
    if stats is not None:
        stats.update(st)
    m = HFV._finish(mx, hall, out_path, 4.0)
    render_release(os.path.join(os.path.dirname(out_path), os.path.basename(OUT_RELEASE)), verbose)
    if verbose:
        print("  buses", {k: round(v, 1) for k, v in st.items()})
        print(f"the_ebbing: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


def render_release(out_path: str = OUT_RELEASE, verbose: bool = True) -> dict:
    """The Ebbing let go wherever the scene silences it: the last A minor chord, the motes falling away twice, the
    Cantor's E held and fading over the drone; unresolved (it ends on E)."""
    g = rng(SEED + 9000)
    t0 = 0.3
    final = [dict(m=n(p), vel=0.24 - 0.02 * j, t0=t0 + 0.1 * j, key_up=4.5, role="bass" if j < 2 else "acc")
             for j, p in enumerate(["A1", "A2", "E3", "B3", "C4", "E4"])]
    pedal = plan_pedal([t0], start=0.0, end_release=6.0, release_len=3.0, g=g)
    mx = Mixer(12.0)
    mx.bus("piano", 27.7, send=0.25, process=PianoBody(pedal))
    mx.bus("cantor", 0.0, send=0.4, process=HFV.vocalise_bus)
    mx.bus("motes", 4.7, send=0.6, process=lambda x: filt(x, [bq_highpass(400, 0.7)]))
    mx.bus("drone", -5.4, send=0.25, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1500, 0.6)]))
    drone = HFV.drone(8.0, rng(SEED + 9001))
    k = int(3.0 * SR)
    drone[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    mx.add("drone", drone, 0.0)
    for nt, x in zip(final, render_jobs(HFV._piano_jobs(final, pedal, SEED + 9005))):
        mx.add("piano", x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    x = breath_flute(n("E5"), 4.5, 0.5, seed=SEED + 9010, breath=0.18, scoop_cents=20.0, vib_cents=14.0, vib_rate=5.0,
                     swell=0.0, attack=0.3, release=1.6, beta=0.5)
    mx.add("cantor", x, t0 - FLUTE_PRE, pan=-0.05)
    for k2, at in enumerate((0.9, 2.6)):                                   # the motes falling away
        for j, p in enumerate(FALL):
            y = metallophone_note(n(p) + 12 * (k2 == 0), 0.2 - 0.04 * k2, seed=SEED + 9100 + 10 * k2 + j, decay=4.5,
                                  hardness=0.25, ombak_hz=4.0)
            mx.add("motes", y, at + 0.22 * j, pan=0.55 - 0.3 * j)
    hall = ModFDNReverb(rt60=3.6, rt60_high=1.4, predelay=0.03, size=1.2, mod_depth=9.0, mod_rate=0.45,
                        early_level=0.2, lowcut=90.0, seed=SEED % 9973)
    m = HFV._finish(mx, hall, out_path, 4.0)
    if verbose:
        print(f"the_ebbing_release: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


if __name__ == "__main__":
    render()
