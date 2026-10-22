"""'Hush' main theme, v2 (M1-AUD-02): the M1 sketch re-performed on the new instruments.

Original composition for this project (SPEC §2, §9); the motif is the one
written for the M1 sketch: a long held note, a stepwise fall of a third
(E-D-C), then the line settling a sixth below with a turn. It is not
adapted from any existing melody. A minor (Aeolian, major V at half
cadences), 3/4, about 72 BPM.

What changed from `hush_theme_sketch.py` (which is kept for A/B listening):

* Piano: `synth.grand` (hammer model, 1-3 unison strings, two-stage decay,
  dampers, modal soundboard, sympathetic resonance, pedal noise) instead of
  the additive `synth.piano`.
* Performance: phrase-arch rubato and dynamics, melody voicing and melody
  lead, per-role micro-timing, and a humanized legato pedal curve (with two
  half-changes over the held tonic of the intro) instead of mechanical
  per-bar pedalling.
* Composition, small changes only: in the reprise (bars 19-22) the left hand
  opens out to a wider figure (bass, fifth, tenth), so the return feels like
  growth rather than repetition; the last chord is spread from the bass up.
* Flute counterline: `synth.winds.breath_flute`. Reverb: `ModFDNReverb`.

Render:  python3 assets_src/music/hush_theme_v2.py   (or tools/audio/render_all.py)
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, rng  # noqa: E402
from synth.grand import MAX_LEN, PedalCurve, PianoBody, grand_note  # noqa: E402
from synth.loudness import _block_powers, _to_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.performance import ExpressiveTempo, Phrase, Voicing, onset_offset, plan_pedal, shape_velocity  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import Score  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

OUT = os.path.join(ROOT, "assets", "audio", "music", "hush_theme_v2.ogg")
SEED = 20261023
TARGET_LUFS = -16.0
BARS = 26
BPB = 3

# --------------------------------------------------------------------------- #
# Harmony (unchanged from the sketch): LH broken-chord tones and pad voicings
# --------------------------------------------------------------------------- #
LH = {
    1: "A2 E3 B3 C4", 2: "A2 E3 B3 C4",
    3: "A2 E3 B3 C4", 4: "F2 C3 A3 E4", 5: "G2 E3 C4 D4", 6: "E2 B2 G3 D4",
    7: "D2 A2 F3 E4", 8: "C3 E3 A3 B3", 9: "E2 B2 A3 D4", 10: "E2 B2 G#3 D4",
    11: "F2 C3 A3 E4", 12: "G2 D3 A3 B3", 13: "E2 B2 G3 D4", 14: "A2 E3 B3 C4",
    15: "D2 A2 F3 C4", 16: "G2 D3 F3 C4", 17: "C3 G3 B3 E4", 18: "G#2 E3 B3 D4",
    19: "A2 E3 B3 C4", 20: "F2 C3 A3 E4", 21: "D2 A2 F3 E4", 22: "E2 B2 A3 D4",
    23: "F2 C3 A3 B3", 24: "A2 E3 B3 C4",
}
# Reprise: wider figure (bass, fifth, tenth, upper colour) for bars 19-22.
LH_WIDE = {19: "A2 E3 C4 B3", 20: "F2 C3 A3 G4", 21: "D2 A2 F3 E4", 22: "E2 B2 G#3 D4"}

PAD = {
    1: "A3 E4 B4", 3: "A3 C4 E4 B4", 4: "F3 A3 C4 E4", 5: "G3 C4 E4 D5", 6: "E3 G3 B3 D4",
    7: "D3 F3 A3 E4", 8: "C4 E4 A4", 9: "E3 A3 B3 D4", 10: "E3 G#3 B3 D4",
    11: "F3 A3 C4 E4", 12: "G3 B3 D4 A4", 13: "E3 G3 B3 D4", 14: "A3 C4 E4 B4", 15: "D3 F3 A3 C4",
    16: "G3 C4 D4 F4", 17: "C4 E4 G4 B4", 18: "G#3 B3 D4 E4",
    19: "A3 C4 E4 B4", 20: "F3 A3 C4 E4", 21: "D3 F3 A3 E4", 22: "E3 A3 B3 D4", 23: "F3 A3 B3 E4",
    24: "A3 C4 E4 B4",
}

MEL_A = [  # bars 3-10
    ("E5", 2, .52), ("D5", .5, .44), ("C5", .5, .42),
    ("A4", 2, .46), ("G4", .5, .38), ("A4", .5, .40),
    ("G4", 1, .42), ("C5", 1, .46), ("D5", 1, .50),
    ("E5", 2, .55), ("G5", 1, .52),
    ("F5", 1.5, .56), ("E5", .5, .48), ("D5", 1, .46),
    ("C5", 2, .46), ("B4", .5, .40), ("A4", .5, .38),
    ("B4", 1, .42), ("D5", 1, .46), ("E5", 1, .50),
    ("E5", 3, .44),
]
MEL_B = [  # bars 11-18
    ("A5", 2, .62), ("G5", .5, .52), ("F5", .5, .50),
    ("G5", 2, .58), ("D5", 1, .48),
    ("E5", 1.5, .55), ("F5", .5, .56), ("G5", 1, .62),
    ("A5", 3, .72),
    ("F5", 1, .58), ("E5", 1, .53), ("D5", 1, .50),
    ("D5", 1.5, .52), ("C5", .5, .46), ("B4", 1, .44),
    ("C5", 1, .46), ("E5", 1, .52), ("G5", 1, .56),
    ("B4", 2, .48), ("G#4", 1, .42),
]
MEL_C = [  # bars 19-24
    ("E5", 2, .46), ("D5", .5, .40), ("C5", .5, .38),
    ("A4", 2, .40), ("B4", .5, .37), ("C5", .5, .39),
    ("D5", 1, .42), ("F5", 1, .46), ("E5", 1, .42),
    ("E5", 2, .42), ("D5", .5, .36), ("B4", .5, .34),
    ("C5", 3, .36),
    ("A4", 3.6, .32),
]
INNER = {11: "C4 E4", 12: "B3 D4", 13: "B3 E4", 14: "C4 E4", 15: "A3 D4", 16: "F4", 17: "E4 G4", 18: "D4 E4"}
FLUTE = [
    ("C6", 3, .40), ("C6", 2, .42), ("B5", 1, .40), ("A5", 3, .42), ("B5", 2, .40), ("G#5", 1, .36),
    ("A5", 2.6, .34),
]
METAL = [
    (1, 1, "E5", .42, 5.0), (1, 2.5, "A5", .32, 4.5), (2, 1, "B5", .36, 4.5), (2, 3, "E5", .28, 4.0),
    (3, 1, "A5", .26, 4.5), (7, 1, "A5", .24, 4.0),
    (11, 1, "C6", .32, 4.0), (13, 1, "B5", .32, 4.0), (14, 1, "E6", .36, 4.5), (15, 1, "A5", .30, 4.0),
    (17, 1, "G5", .30, 4.0), (18, 2, "B5", .26, 3.5),
    (19, 1, "A5", .26, 4.5), (23, 1, "E6", .24, 4.5),
    (24, 1, "A5", .34, 6.0), (24, 1, "E5", .26, 6.0), (25, 2, "B5", .22, 5.0),
]

# Phrases (beats, 0-based). Climax of the piece is bar 14 (beat 39).
PHRASES = [
    Phrase(0, 6, peak=0.5, tempo_depth=0.02, dyn_depth=0.06, final_rit=0.04),
    Phrase(6, 18, peak=0.62, tempo_depth=0.035, dyn_depth=0.10, final_rit=0.05),
    Phrase(18, 30, peak=0.40, tempo_depth=0.035, dyn_depth=0.10, final_rit=0.12),
    Phrase(30, 42, peak=0.85, tempo_depth=0.045, dyn_depth=0.14, final_rit=0.06),
    Phrase(42, 54, peak=0.25, tempo_depth=0.04, dyn_depth=0.12, final_rit=0.14),
    Phrase(54, 66, peak=0.50, tempo_depth=0.03, dyn_depth=0.10, final_rit=0.08),
    Phrase(66, 78, peak=0.20, tempo_depth=0.02, dyn_depth=0.08, final_rit=0.0),
]


def build_score() -> Score:
    sc = Score(beats_per_bar=BPB)
    for bar in range(1, 25):
        b, f, c1, c2 = (LH_WIDE.get(bar) or LH[bar]).split()
        pat = [b, f, c1, c2, c1, f]
        if bar == 22:
            pat = [b, f, c1, c2, "G#3", f]
        intro = bar <= 2
        for i, p in enumerate(pat):
            vel = (0.40 if i == 0 else 0.27 if i in (1, 5) else 0.31) * (0.8 if intro else 1.0)
            if 11 <= bar <= 18:
                vel *= 1.12
            if bar >= 22:
                vel *= 0.85
            role = "bass" if i == 0 else "acc"
            sc.add("piano", bar, 1 + 0.5 * i, p, 3.0 if i == 0 else 0.5, vel, role=role)
    # final chord, spread upward from the bass
    for j, p in enumerate(["A1", "A2", "E3", "C4"]):
        sc.add("piano", 25, 1 + 0.09 * j, p, 3, 0.30 - 0.03 * j, role="bass" if j < 2 else "acc")
    for mel, bar in ((MEL_A, 3), (MEL_B, 11), (MEL_C, 19)):
        sc.line("piano", bar, mel, role="mel")
    for bar, notes in INNER.items():
        for p in notes.split():
            sc.add("piano", bar, 1, p, 2.5, 0.26, role="inner")
    sc.line("flute", 19, FLUTE)
    for bar, beat, p, v, d in METAL:
        sc.add("metal", bar, beat, p, 0.0, v, decay=d)
    keys = sorted(PAD)
    for i, bar in enumerate(keys):
        nxt = keys[i + 1] if i + 1 < len(keys) else 26
        vel = 0.55 if bar < 11 else 0.75 if bar < 19 else 0.5
        sc.add("pad", bar, 1, PAD[bar].split(), (nxt - bar) * 3 + 0.4, vel)
    return sc


def tempo() -> ExpressiveTempo:
    pts = [(0, 70), (2 * BPB, 72), (13 * BPB, 74), (15 * BPB, 72), (21 * BPB, 70), (23 * BPB, 58),
           (24 * BPB, 50), (26 * BPB, 50)]
    return ExpressiveTempo(pts, total_beats=BARS * BPB, phrases=PHRASES)


def _pedal_slice(pedal: PedalCurve, t0: float) -> PedalCurve:
    m = (pedal.times >= t0 - 0.01) & (pedal.times <= t0 + MAX_LEN + 0.01)
    return PedalCurve(pedal.times[m].copy(), pedal.depth[m].copy())


def perform(sc: Score, tm: ExpressiveTempo):
    """Turn score events into timed, voiced piano jobs plus a pedal curve."""
    g = rng(SEED)
    voicing = Voicing()
    piano = [e for e in sc.events if e.inst == "piano"]
    piano.sort(key=lambda e: (e.beat, e.opts.get("role") != "mel", e.pitch))
    # accompaniment velocity per beat (for the melody lead)
    acc_v = {}
    for e in piano:
        if e.opts.get("role") != "mel":
            acc_v.setdefault(round(e.beat, 3), []).append(e.vel)
    notes = []
    for e in piano:
        role = e.opts.get("role", "acc")
        v = shape_velocity(e.vel, role, e.beat, BPB, e.pitch, PHRASES, voicing, g)
        av = float(np.mean(acc_v.get(round(e.beat, 3), [0.3]))) * voicing.scale["acc"]
        t0 = tm.t(e.beat) + onset_offset(role, v, av, voicing, g)
        dur = tm.t(e.beat + e.beats) - tm.t(e.beat)
        if role == "mel":
            key_up = dur + 0.035            # finger legato overlap
        elif role == "bass":
            key_up = dur * 0.97
        else:
            key_up = dur * 0.9
        notes.append(dict(m=e.pitch, vel=v, t0=max(0.0, t0), key_up=key_up, role=role))
    # pedal changes: just after each bar's bass note; bars 2 and 3 keep the same
    # tonic, so they get half-changes (clear the blur, keep the bloom)
    bass_t = sorted(nt["t0"] for nt in notes if nt["role"] == "bass" and nt["t0"] < tm.t(24 * BPB) + 0.1)
    changes = bass_t[1:]
    pedal = plan_pedal(changes, start=notes[0]["t0"], end_release=tm.t(26 * BPB) + 1.2, release_len=2.6, g=g,
                       half={0, 1})
    return notes, pedal


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    sc = build_score()
    tm = tempo()
    notes, pedal = perform(sc, tm)
    end_t = tm.t(BARS * BPB) + 6.0
    mx = Mixer(end_t)
    body_mel = PianoBody(pedal)
    body_acc = PianoBody(pedal)
    mx.bus("piano_mel", 0.0, send=0.20, process=body_mel)
    mx.bus("piano_acc", 0.0, send=0.20, process=body_acc)
    mx.bus("metal", -15.0, send=0.40)
    mx.bus("pad", -19.0, send=0.55, process=string_body)
    mx.bus("flute", -20.0, send=0.42)

    jobs = []
    for k, nt in enumerate(notes):
        jobs.append((grand_note, dict(m=nt["m"], vel=nt["vel"], key_up=nt["key_up"], seed=SEED + 7919 * k,
                                      t_abs=nt["t0"], pedal=_pedal_slice(pedal, nt["t0"]))))
    rendered = render_jobs(jobs)
    for nt, x in zip(notes, rendered):
        pan = float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3))
        mx.add("piano_mel" if nt["role"] == "mel" else "piano_acc", x, nt["t0"], pan=pan)

    g = rng(SEED + 1)
    for k, ev in enumerate(sorted((e for e in sc.events if e.inst != "piano"), key=lambda e: (e.beat, e.inst))):
        t0 = tm.t(ev.beat)
        dur = tm.t(ev.beat + ev.beats) - t0
        seed = SEED + 104729 * (k + 1)
        if ev.inst == "metal":
            x = metallophone_note(ev.pitch, ev.vel, seed=seed, decay=ev.opts.get("decay", 4.5), hardness=0.42,
                                  ombak_hz=5.2)
            mx.add("metal", x, max(0.0, t0 + g.normal(0, 0.006)), pan=0.25)
        elif ev.inst == "flute":
            x = breath_flute(ev.pitch, dur * 0.97, ev.vel, seed=seed, breath=0.30, scoop_cents=30.0,
                             vib_cents=12.0, swell=0.15 if ev.beats >= 3 else 0.0)
            mx.add("flute", x, max(0.0, t0 - 0.05 + g.normal(0, 0.01)), pan=-0.22)
        elif ev.inst == "pad":
            x = pad_chord(ev.pitch, dur, ev.vel, seed=seed, attack=1.6 if ev.beat > 0 else 3.0, release=2.2)
            mx.add("pad", x, max(0.0, t0))

    hall = ModFDNReverb(rt60=2.6, rt60_high=1.1, predelay=0.024, size=1.0, mod_depth=8.0, mod_rate=0.5,
                        seed=SEED % 9973)
    if stats is not None:
        _bus_stats(mx, stats)
        stats["sym_ratio_db"] = body_acc.last_sym_ratio_db
        stats["pedal"] = pedal
        stats["notes"] = notes
        stats["tempo_bpm_range"] = tm.local_bpm_range()
    master = mx.render(reverb=hall, reverb_return_db=-2.0)
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(1.5 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, master, quality=4.0)
    m = measure(master)
    if verbose:
        print(f"hush_theme_v2: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  "
              f"peak {m['sample_peak_dbfs']:.2f} dBFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


def _bus_stats(mx: Mixer, stats: dict) -> None:
    """Integrated (gated) loudness of each processed bus, for the voicing check."""
    for name, b in mx.buses.items():
        x = (b.process(b.buf) if b.process else b.buf) * 10 ** (b.gain_db / 20)
        p = _block_powers(x, SR, 0.4, 0.1)
        lk = _to_lufs(p)
        p = p[lk > -70]
        if len(p):
            rel = _to_lufs(p.mean()) - 10
            stats[f"bus_{name}_lufs"] = float(_to_lufs(p[_to_lufs(p) > rel].mean()))


if __name__ == "__main__":
    render()
