"""`hush_first_verse` (Cutscene B, B09) and `hush_coda` (the slice end card, B12) (M2-AUD-03).

Original composition for this project (SPEC §2): the melody is our own Hush theme's first phrase (hush_theme_v2.py,
MEL_A: a long held note, a stepwise fall of a third, a turn), not adapted from any existing tune.

The brief (vertical_slice.md §6): "The first diegetic statement of the Hush theme. A sung line (until SPEC §16
Q4/Q5 settle a voice, a vocalise-like solo instrument carries it) over a held drone, with the piano entering on
*mir*. The B12 coda is piano alone."

**hush_first_verse** (~80 s, not looped; the cutscene stops it with `@music silence` at the bell):
* 0-4 s: an A drone (A2, E3, a little A3) breathes in. It holds to the end.
* The verse, four lines, one per sung line of the .dlg (ch03_verse_042-045), with a breath after each:
  "Vey ennu, vey ennu," = E D C | A G A; "hal oan, ish karra." = G C D | E G E; "Ennu re, ennu re..." =
  F E D | C B A; "...mir." = B D | E, held. The line is a breath flute shaped by an open "ah" vowel's formants
  (a vocalise-like instrument: no synthetic singer, per Q5's default), slow vibrato, legato.
* On *mir* (the held E) the grand piano enters: an A minor chord spread up from the bass. It then plays the
  phrase's harmony softly (hush_theme_v2's left hand, bars 3-10) with the melody's first notes as a memory in its
  top voice, and the vocalise echoes "...mir" once more, far back, over the last chord.

**hush_coda** (~40 s, piano alone, B12): the same phrase on the piano, slower and quieter than the theme, ending on
an open A minor (add 9) chord left ringing.

Render:  python3 assets_src/music/hush_first_verse.py   (both files; or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, filt, midi_to_hz, rng  # noqa: E402
from synth.grand import MAX_LEN, PedalCurve, PianoBody, grand_note  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.performance import plan_pedal  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "hush_first_verse.ogg")
OUT_CODA = os.path.join(ROOT, "assets", "audio", "music", "hush_coda.ogg")
SEED = 20261108
TARGET_LUFS = -16.0
BPM = 56.0
BEAT = 60.0 / BPM
DRONE_IN = 4.0
FLUTE_PRE = 0.065
BREATH_S = 0.7          # the singer's breath after each line

# (pitch, beats) per line; each line is two 3/4 bars.
VERSE = [
    [("E5", 2), ("D5", .5), ("C5", .5), ("A4", 2), ("G4", .5), ("A4", .5)],
    [("G4", 1), ("C5", 1), ("D5", 1), ("E5", 1), ("G5", 1.5), ("E5", .5)],
    [("F5", 1.5), ("E5", .5), ("D5", 1), ("C5", 2), ("B4", .5), ("A4", .5)],
    [("B4", 1), ("D5", 1), ("E5", 4)],
]
# hush_theme_v2's left hand for bars 3-10 (bass, fifth, colour tones), as broken chords.
LH = ["A2 E3 B3 C4", "F2 C3 A3 E4", "G2 E3 C4 D4", "E2 B2 G3 D4", "D2 A2 F3 E4", "C3 E3 A3 B3", "E2 B2 A3 D4",
      "E2 B2 G#3 D4"]
MEMORY = [("E5", 2), ("D5", .5), ("C5", .5), ("A4", 3)]
CODA_MEL = [("E5", 2), ("D5", .5), ("C5", .5), ("A4", 2), ("G4", .5), ("A4", .5), ("G4", 1), ("C5", 1), ("D5", 1),
            ("E5", 2), ("G5", 1), ("F5", 1.5), ("E5", .5), ("D5", 1), ("C5", 2), ("B4", .5), ("A4", .5),
            ("B4", 1), ("D5", 1), ("E5", 1), ("E5", 3)]


def vocalise_bus(x: np.ndarray) -> np.ndarray:
    """An open 'ah' (alto formants F1 730, F2 1090, F3 2440 Hz) on the breath flute: a voice-like instrument."""
    return filt(x, [bq_highpass(160, 0.7), bq_peak(730, 7.0, 3.0), bq_peak(1090, 5.0, 3.5), bq_peak(2440, 4.0, 4.0),
                    bq_peak(3300, -4.0, 1.0), bq_lowpass(5200, 0.7)])


def verse_notes() -> tuple[list[tuple[float, float, float]], float]:
    """[(t, dur, midi)] of the verse from the drone's start, and the time of *mir* (the held E's onset)."""
    out = []
    t = DRONE_IN
    mir = 0.0
    for li, line in enumerate(VERSE):
        for k, (p, beats) in enumerate(line):
            last = k == len(line) - 1
            d = beats * BEAT * (1.12 if last else 1.0)      # each line leans into its last note
            out.append((t, d, n(p)))
            if li == 3 and last:
                mir = t
            t += d
        t += BREATH_S
    return out, mir


def drone(length: float, g, sr: int = SR) -> np.ndarray:
    N = int(length * sr)
    t = np.arange(N) / sr
    out = np.zeros((N, 2))
    breath = 0.5 - 0.5 * np.cos(2 * np.pi * t / 17.0)
    for root, lvl in ((n("A2"), 1.0), (n("E3"), 0.45), (n("A3"), 0.18)):
        f0 = midi_to_hz(root)
        for k, a in ((1, 1.0), (2, 0.42), (3, 0.2), (4, 0.1), (5, 0.05)):
            for side, det in ((0, 0.0), (1, 0.08 + 0.02 * k)):
                s = lvl * a * (1 + 0.3 * (k - 1) / 4 * (breath - 0.5) * 2) * np.sin(
                    2 * np.pi * (f0 * k + det) * t + g.uniform(0, 6.28))
                out[:, side] += s
                out[:, 1 - side] += 0.6 * s
    env = np.clip(t / DRONE_IN, 0, 1) ** 2 * np.clip((length - t) / 6.0, 0, 1) ** 2
    return out * env[:, None] * 0.05


def _piano_jobs(notes: list[dict], pedal: PedalCurve, seed: int) -> list:
    jobs = []
    for k, nt in enumerate(notes):
        m = (pedal.times >= nt["t0"] - 0.01) & (pedal.times <= nt["t0"] + MAX_LEN + 0.01)
        jobs.append((grand_note, dict(m=nt["m"], vel=nt["vel"], key_up=nt["key_up"], seed=seed + 7919 * k,
                                      t_abs=nt["t0"], pedal=PedalCurve(pedal.times[m].copy(), pedal.depth[m].copy()))))
    return jobs


def _broken_chords(bars: list[str], t0: float, bar_s: float, vel: float, g) -> list[dict]:
    out = []
    for b, chord in enumerate(bars):
        bass, fifth, c1, c2 = chord.split()
        for i, p in enumerate([bass, fifth, c1, c2, c1, fifth]):
            v = (0.34 if i == 0 else 0.22 if i in (1, 5) else 0.25) * vel * g.uniform(0.94, 1.05)
            t = t0 + b * bar_s + i * bar_s / 6 + float(g.normal(0, 0.006))
            out.append(dict(m=n(p), vel=v, t0=t, key_up=bar_s * (1.0 if i == 0 else 0.3), role="bass" if i == 0 else "acc"))
    return out


def _finish(mx: Mixer, hall: ModFDNReverb, out_path: str, quality: float) -> dict:
    master = mx.render(reverb=hall, reverb_return_db=-2.0)
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(2.0 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, master, quality=quality)
    return measure(master)


# Bus gains from measured bus loudness (hush_theme_v2._bus_stats): the vocalise at L, the piano L-3 once it enters,
# the drone L-9. The grand piano model's raw level is about 31 dB under the breath flute's (the first render of this
# cue missed that, and the piano on *mir* was buried).
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    verse, mir = verse_notes()
    bar_s = 3 * BEAT * 1.04
    piano_t0 = mir
    acc_t0 = mir + 2 * bar_s
    acc = _broken_chords(LH, acc_t0, bar_s, 0.8, g)
    chord = [dict(m=n(p), vel=0.30 - 0.03 * j, t0=piano_t0 + 0.09 * j, key_up=2 * bar_s, role="bass" if j < 2 else "acc")
             for j, p in enumerate(["A1", "A2", "E3", "B3", "C4"])]
    memory, t = [], acc_t0
    for p, beats in MEMORY:
        memory.append(dict(m=n(p), vel=0.34, t0=t + float(g.normal(0, 0.005)), key_up=beats * bar_s / 3 + 0.03,
                           role="mel"))
        t += beats * bar_s / 3
    end_t = acc_t0 + len(LH) * bar_s
    final = [dict(m=n(p), vel=0.26 - 0.025 * j, t0=end_t + 0.1 * j, key_up=4 * bar_s, role="bass" if j < 2 else "acc")
             for j, p in enumerate(["A1", "A2", "E3", "B3", "C4", "E4"])]
    notes = chord + acc + memory + final
    changes = [piano_t0 + 2 * bar_s] + [acc_t0 + b * bar_s for b in range(1, len(LH))] + [end_t]
    pedal = plan_pedal(changes, start=piano_t0, end_release=end_t + 3 * bar_s, release_len=3.0, g=g)
    length = end_t + 4 * bar_s + 8.0
    mx = Mixer(length)
    mx.bus("piano", 25.2, send=0.24, process=PianoBody(pedal))
    mx.bus("vocalise", 0.0, send=0.38, process=vocalise_bus)
    mx.bus("drone", -6.4, send=0.25, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1500, 0.6)]))
    mx.add("drone", drone(length - 2.0, rng(SEED + 1)), 0.0)
    for i, (t0, d, m) in enumerate(verse):
        x = breath_flute(m, d + 0.06, 0.5, seed=SEED + 31 * i, breath=0.18, scoop_cents=40.0, vib_cents=16.0,
                         vib_rate=5.0, swell=0.22 if d > 1.5 else 0.0, attack=0.14, release=0.4, beta=0.5)
        mx.add("vocalise", x, t0 - FLUTE_PRE, pan=-0.05)
    echo = breath_flute(n("E5"), 3 * bar_s, 0.32, seed=SEED + 999, breath=0.25, scoop_cents=30.0, vib_cents=14.0,
                        vib_rate=4.8, swell=0.3, attack=0.4, release=1.2)
    mx.add("vocalise", echo * 0.5, end_t + 0.6, pan=0.3)
    for nt, x in zip(notes, render_jobs(_piano_jobs(notes, pedal, SEED + 5))):
        mx.add("piano", x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    hall = ModFDNReverb(rt60=3.2, rt60_high=1.3, predelay=0.03, size=1.15, mod_depth=8.0, mod_rate=0.45,
                        early_level=0.25, lowcut=90.0, seed=SEED % 9973)
    m = _finish(mx, hall, out_path, 4.0)
    if stats is not None:
        stats["mir_s"] = mir
    if verbose:
        print(f"hush_first_verse: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  mir at {mir:.1f}s")
    return m


def render_coda(out_path: str = OUT_CODA, verbose: bool = True) -> dict:
    g = rng(SEED + 50)
    beat = 60.0 / 48.0
    bar_s = 3 * beat
    t0 = 0.6
    acc = _broken_chords(LH, t0, bar_s, 0.62, g)
    mel, t = [], t0
    for i, (p, beats) in enumerate(CODA_MEL):
        stretch = 1.1 if beats >= 2 else 1.0
        d = beats * beat * stretch
        mel.append(dict(m=n(p), vel=0.36 * g.uniform(0.95, 1.04), t0=t + float(g.normal(0, 0.006)), key_up=d + 0.035,
                        role="mel"))
        t += d
    end_t = max(t0 + len(LH) * bar_s, t)
    final = [dict(m=n(p), vel=0.24 - 0.02 * j, t0=end_t + 0.11 * j, key_up=5 * bar_s, role="bass" if j < 2 else "acc")
             for j, p in enumerate(["A1", "A2", "E3", "B3", "C4", "E4"])]
    notes = acc + mel + final
    pedal = plan_pedal([t0 + b * bar_s for b in range(1, len(LH))] + [end_t], start=t0, end_release=end_t + 4 * bar_s,
                       release_len=3.5, g=g)
    mx = Mixer(end_t + 5 * bar_s + 8.0)
    mx.bus("piano", 0.0, send=0.24, process=PianoBody(pedal))
    for nt, x in zip(notes, render_jobs(_piano_jobs(notes, pedal, SEED + 55))):
        mx.add("piano", x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    hall = ModFDNReverb(rt60=2.8, rt60_high=1.2, predelay=0.026, size=1.05, mod_depth=8.0, mod_rate=0.5,
                        seed=(SEED + 50) % 9973)
    m = _finish(mx, hall, out_path, 4.0)
    if verbose:
        print(f"hush_coda: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


if __name__ == "__main__":
    render()
    render_coda()
