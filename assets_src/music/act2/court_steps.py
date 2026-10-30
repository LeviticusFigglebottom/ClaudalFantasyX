"""`court_steps`: Ch14's step-hold, the court steps held while Merel cuts the barge loose (M4-A2P-092; the cue sheet
§2 "Set-piece hold", docs/kb/plan/act2/chapters/ch14.md §3 `ch14_hold_the_steps`): two synchronized stems, a 60 s loop.

Original composition for this project (SPEC §2, §9). It is made of the wedding's own material, torn open as the trap
(peace_wedding_break.py) left it: the couple's tune (act2/peace_wedding.py's COUPLE) in diminution, the Stillguard's
damped kettle gong on D2 stepping every two beats, and the Order's tune ORDER_HUM (motifs.py), hummed. Our own lines
are imported, never retyped. Nothing is taken from any existing music.

The brief: the ceremony's music torn open while the party hold the steps for N turns, Kerrid locked in the line, a
ward entry ("Merel's knife") on the timeline. C minor at 112 BPM, the wedding's tune in diminution.
* **Stem 1, the hold:** the gong's step on 1 and 3 (it won at the trap, and it keeps stepping), a frame drum in
  3+3+2 eighths under it (the dance's three, still pushing against the gong's two), muted plucked strings on the
  roots, a low string pad, and the Stillguard's hum, ORDER_HUM's first six notes, low and close. Over it the party's
  answer: the couple's tune in C minor, in eighths (diminution), on the breath flute, three times a loop.
* **Stem 2, the last turn** (its row brings it in when Merel's knife is nearly through): the big drum on 1 and 3, a
  sixteenth roll building through each phrase, the couple's tune doubled an octave up on struck bars every phrase,
  and a sixteenth plucked ostinato. It hands on the beat to `lagoon_escape` (the cue ends each phrase on G, the
  dominant, and lagoon_escape's E minor turns to C minor at Merel).

C minor, 4/4 at 112 BPM (a bar is 2.14 s), 28 bars (seven 4-bar phrases: A A B A A B A). The stems share one limiter
gain curve from the full stack. Vorbis q3; the stack is -16 LUFS. Plain git (ADR 0175).

Render:  python3 tools/audio/render_all.py --only court_steps
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)

import numpy as np  # noqa: E402

from motifs import ORDER_HUM  # noqa: E402
from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PW = _mod("peace_wedding_final", os.path.join(HERE, "peace_wedding.py"))   # COUPLE, in E minor

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "court_steps_p1.ogg")
OUT2 = os.path.join(ROOT, "assets", "audio", "act2", "music", "court_steps_p2.ogg")
SEED = 20262040
TARGET_LUFS = -16.0
BPM = 112.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
PHRASE_A = ["Cm", "Bb", "Ab", "G"]
PHRASE_B = ["Fm", "Ab", "G", "G"]
CHORDS = PHRASE_A * 2 + PHRASE_B + PHRASE_A * 2 + PHRASE_B + PHRASE_A
BARS = len(CHORDS)
LOOP_S = BARS * BAR
LEAD_IN_S = BEAT / 4
ROOTS = {"Cm": "C2", "Bb": "Bb1", "Ab": "Ab1", "G": "G1", "Fm": "F2"}
TONES = {"Cm": ["C3", "Eb3", "G3"], "Bb": ["Bb2", "D3", "F3"], "Ab": ["Ab2", "C3", "Eb3"], "G": ["G2", "B2", "D3"],
         "Fm": ["F2", "Ab2", "C3"]}
TO_C_MINOR = -4                   # the couple's tune, E minor -> C minor
TUNE_BARS = (5, 13, 21)           # the flute's statements (stem 1); stem 2's bars double every phrase
HUM_BARS = (1, 15)
GAINS = {"gong": -7.0, "drum": -6.0, "pluck": -8.0, "pad": -6.0, "hum": -2.0, "flute": -1.0,
         "big": -6.0, "roll": -8.0, "bars": -6.0, "ostinato": -10.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def tune() -> list[tuple[int, float]]:
    """COUPLE's first four bars in C minor, each note half as long: [(midi, beats)]."""
    return [(n(p) + TO_C_MINOR, d / 2) for bar in PW.COUPLE[:4] for p, d in bar]


def build_p1(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    for bar, ch in enumerate(CHORDS, start=1):
        for beat in (0, 2):                                                  # the gong's step: it keeps stepping
            mx.add("gong", kettle_gong(n("D2"), 0.45 * float(g.uniform(0.92, 1.04)), seed=SEED + 10 + (bar + beat) % 4,
                                       t60=1.3, damp_at=0.5), t_of(bar, beat) + float(g.normal(0, 0.003)), pan=-0.3)
        for e, stroke, v in ((0, "dum", 0.55), (3, "tek", 0.35), (6, "tek", 0.4)):   # 3+3+2 against the gong's two
            mx.add("drum", frame_drum(stroke, v * float(g.uniform(0.92, 1.04)), variant=(bar + e) % 3, seed=SEED + 20),
                   t_of(bar, e / 2) + float(g.normal(0, 0.003)), pan=0.15)
        root = n(ROOTS[ch])
        for e in range(8):                                                   # muted roots and fifths, eighths
            m = root + 12 + (7 if e % 4 == 2 else 0)
            mx.add("pluck", string_pluck(m, BEAT * 0.4, 0.5, seed=SEED + 100 + 8 * bar + e, pick_pos=0.13, t60=0.7,
                                         mute=0.8, max_f=3500.0, release=0.03), t_of(bar, e / 2), pan=-0.15)
        mx.add("pad", pad_chord([n(p) for p in TONES[ch]], BAR * 0.96, 0.45, seed=SEED + 200 + bar, attack=0.25,
                                release=0.4), t_of(bar), pan=0.0)
    line = [(float(m) - 12, 2 * BEAT) for m, _ in ORDER_HUM[:6]]             # the Stillguard's hum, low and close
    for k, bar in enumerate(HUM_BARS):
        mx.add("hum", hum_ensemble(line, voices=14, seed=SEED + 300 + k, register="low", spread=0.7), t_of(bar))
    for k, bar in enumerate(TUNE_BARS):                                      # the party's answer: the couple's tune
        at = 0.0
        for i, (m, d) in enumerate(tune()):
            x = breath_flute(m, d * BEAT * 0.92, 0.55 + 0.1 * (i == 0), seed=SEED + 400 + 40 * k + i, scoop_cents=25.0,
                             attack=0.04, release=0.15)
            mx.add("flute", x, t_of(bar, at) - 0.03, pan=0.2)
            at += d


def build_p2(mx: LoopMixer) -> None:
    g = rng(SEED + 2)
    for bar, ch in enumerate(CHORDS, start=1):
        for beat in (0, 2):
            mx.add("big", big_drum(0.7 * float(g.uniform(0.92, 1.04)), variant=(bar + beat) % 4, seed=SEED + 40),
                   t_of(bar, beat))
        ph = (bar - 1) % 4                                                   # the roll builds through each phrase
        for s in range(16):
            if ph < 2 and s % 2 == 1 or (ph == 3 and s == 15):
                continue                                                     # a breath before each phrase
            v = 0.18 + 0.4 * (ph * 16 + s) / 63
            mx.add("roll", frame_drum("tek", v, variant=s % 4, seed=SEED + 41),
                   t_of(bar, s / 4) + float(g.normal(0, 0.003)), pan=float(g.uniform(-0.3, 0.3)))
        tones = [n(p) + 12 for p in TONES[ch]]
        for s in range(16):                                                  # the sixteenth ostinato
            m = tones[(0, 1, 2, 1)[s % 4]]
            mx.add("ostinato", string_pluck(m, BEAT * 0.22, 0.4, seed=SEED + 500 + 16 * bar + s, pick_pos=0.1, t60=0.5,
                                            mute=0.6, max_f=5000.0, release=0.02), t_of(bar, s / 4), pan=0.35)
        if ph == 0:                                                          # the tune, an octave up, every phrase
            at = 0.0
            for i, (m, d) in enumerate(tune()):
                mx.add("bars", metallophone_note(m + 12, 0.5, seed=SEED + 600 + 8 * bar + i, decay=1.2, hardness=0.7,
                                                 damp_at=max(0.15, d * BEAT * 0.9)), t_of(bar, at), pan=-0.3)
                at += d


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 1:
        mx.bus("gong", G["gong"], send=0.3, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
        mx.bus("drum", G["drum"], send=0.2)
        mx.bus("pluck", G["pluck"], send=0.2, process=lambda x: filt(x, [bq_highpass(80, 0.7), bq_lowpass(3500, 0.7)]))
        mx.bus("pad", G["pad"], send=0.4, process=lambda x: string_body(x, cutoff=1400.0))
        mx.bus("hum", G["hum"], send=0.4, process=lambda x: filt(x, [bq_lowpass(1800, 0.7)]))
        mx.bus("flute", G["flute"], send=0.3,
               process=lambda x: filt(x, [bq_highpass(220, 0.7), bq_peak(1500, 1.0, 1.0), bq_lowpass(7000, 0.7)]))
    else:
        mx.bus("big", G["big"], send=0.2, process=lambda x: filt(x, [bq_lowpass(2000, 0.7)]))
        mx.bus("roll", G["roll"], send=0.15)
        mx.bus("bars", G["bars"], send=0.35, process=lambda x: filt(x, [bq_lowpass(6000, 0.7)]))
        mx.bus("ostinato", G["ostinato"], send=0.2, process=lambda x: filt(x, [bq_highpass(150, 0.7),
                                                                                 bq_lowpass(5000, 0.7)]))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    loops = []
    for stem, build in ((1, build_p1), (2, build_p2)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
        _bus_setup(mx, stem)
        build(mx)
        court = ModFDNReverb(rt60=2.4, rt60_high=1.0, predelay=0.03, size=1.2, mod_depth=8.0, mod_rate=0.4,
                             early_level=0.3, lowcut=100.0, seed=SEED % 9973)
        _, loop = mx.render(reverb=court, reverb_return_db=-3.0)
        loops.append(loop)
        del mx
    lead_in = int(round(LEAD_IN_S * SR))
    loops = [np.roll(x, lead_in, axis=0) for x in loops]
    full = loops[0] + loops[1]
    gain = db_to_lin(TARGET_LUFS - integrated_lufs(full))
    ctx = int(0.05 * SR)
    L = len(full)
    for _ in range(4):                    # one limiter gain curve for both stems, from the full stack (wrap-aware)
        f = full * gain
        env = np.maximum.reduce([np.abs(f)] + [np.abs(x * gain) for x in loops])
        lg = limit_gain(np.concatenate([env[-ctx:], env, env[:ctx]]), -3.0)[ctx: ctx + L]   # drums overshoot decoded
        cur = integrated_lufs(f * lg[:, None])
        if abs(cur - TARGET_LUFS) < 0.1:
            break
        gain *= db_to_lin(TARGET_LUFS - cur)
    stems = [s * gain * lg[:, None] for s in loops]
    paths = [out_path, os.path.join(os.path.dirname(out_path), os.path.basename(OUT2))]
    extra = {"stems_of": "court_steps", "loop_bars": BARS, "downbeat_offset_s": lead_in / SR}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    for x, p in zip(stems, paths):
        write_ogg(p, x, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
        write_loop_sidecar(os.path.splitext(p)[0] + ".loop.json", SR, 0, L, BPM, 4, extra=extra)
    m = measure(stems[0] + stems[1])
    if stats is not None:
        stats["stem1_lufs"] = measure(stems[0])["integrated_lufs"]
        stats["stem2_lufs"] = measure(stems[1])["integrated_lufs"]
    if verbose:
        print(f"court_steps: stack {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}  "
              f"stem1 {measure(stems[0])['integrated_lufs']:.2f}  stem2 {measure(stems[1])['integrated_lufs']:.2f}")
    return m


if __name__ == "__main__":
    render()
