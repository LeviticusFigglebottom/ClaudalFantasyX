"""`malcor_venn`: Warden Malcor Venn on the Conclave's pursuit barge (M4-A2P-092; act2_plan.md §2 Ch14; the cue sheet
§3): two synchronized stems, an 80 s loop.

Original composition for this project (SPEC §2, §9). The ostinato, the stabs and the form were written for this fight.
The only borrowed line is our own: ORDER_HUM (motifs.py), its first notes hummed in the bass. Nothing is taken from
any existing music.

The brief (act2_plan Ch14): phase 1, the barge's bound flat-engine pulls the water flat and slows the timeline; Liss
breaks it (a part). Phase 2, he boards, fighting as a living-seeming man; nothing about what he is is revealed. A
Warden, the Order's still power, after the wedding's betrayal: C minor, the key `lagoon_escape` ends in.
* **Stem 1, the flat-engine** (from the start): a drone whose motion is taken out (a low C minor chord, its breath
  slowed until it hardly moves); a low kettle gong on every fourth beat, the engine's slow pulse, which is also the
  pulse the timeline shows (pillar 4: the player hears and sees it coming); muted plucks in steady eighths, flat, no
  accents; a soft frame drum on 1 and 3.
* **Stem 2, he boards** (the part broken: its phase row brings it in over 3 s): a frame-drum roll building every two
  bars, the big drum on 1, the Order's hum in the bass (ORDER_HUM's first six notes, two beats each), and hard
  metallophone stabs on the minor chords' roots.

C minor, 4/4 at 96 BPM (a bar is 2.5 s), 32 bars. Loop: LOOPSTART = 0, LOOPLENGTH = the whole file; the stems share
one limiter gain curve from the full stack, as every Act II boss's. Vorbis q3; the stack is -16 LUFS. Plain git (ADR
0175).

Render:  python3 tools/audio/render_all.py --only malcor_venn
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
from synth.dsp import SR, bq_highpass, bq_lowpass, db_to_lin, filt, rng  # noqa: E402
from synth.electric import string_pluck  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402


def _mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _mod("act2_voices", os.path.join(MUSIC, "act2_voices.py"))   # periodic_drone()

OUT = os.path.join(ROOT, "assets", "audio", "act2", "music", "malcor_venn_p1.ogg")
OUT2 = os.path.join(ROOT, "assets", "audio", "act2", "music", "malcor_venn_p2.ogg")
SEED = 20262020
TARGET_LUFS = -16.0
BPM = 96.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 32
LOOP_S = BARS * BAR
LEAD_IN_S = BEAT / 4
STEM2_GAIN_DB = 0.0
CHORDS = ["Cm", "Cm", "Ab", "Ab", "Fm", "Fm", "G", "G"] * 4
ROOTS = {"Cm": "C2", "Ab": "Ab1", "Fm": "F2", "G": "G1"}
TONES = {"Cm": ["C3", "Eb3", "G3"], "Ab": ["Ab2", "C3", "Eb3"], "Fm": ["F2", "Ab2", "C3"], "G": ["G2", "B2", "D3"]}
HUM_BARS = (1, 9, 17, 25)
GAINS = {"drone": -6.0, "pulse": -4.0, "pluck": -6.0, "soft": -10.0, "roll": -6.0, "big": -3.0, "hum": -4.0,
         "stab": -8.0}


def t_of(bar: int, beat: float = 0.0) -> float:
    return (bar - 1) * BAR + beat * BEAT


def build_p1(mx: LoopMixer) -> None:
    g = rng(SEED + 1)
    mx.add("drone", V.periodic_drone(LOOP_S, [(n("C2"), 1.0), (n("G2"), 0.5), (n("Eb3"), 0.25)], SEED + 2, partials=5,
                                     breath_s=LOOP_S), 0.0)                         # one breath a loop: almost still
    for k in range(BARS):                                                          # the engine's pulse, every 4 beats
        mx.add("pulse", kettle_gong(n("C2"), 0.6, seed=SEED + 10 + k % 4, t60=1.8, damp_at=1.2), t_of(k + 1), pan=-0.1)
    for bar, ch in enumerate(CHORDS, start=1):
        tones = [n(p) for p in TONES[ch]]
        for e in range(8):                                                        # flat eighths, no accents
            x = string_pluck(tones[e % 3], BEAT * 0.45, 0.45, seed=SEED + 100 + 8 * bar + e, pick_pos=0.12, t60=0.9,
                             mute=0.75, max_f=4000.0, release=0.03)
            mx.add("pluck", x, t_of(bar, e / 2) + float(g.normal(0, 0.003)), pan=-0.3 + 0.3 * (e % 3))
        for beat in (0, 2):
            mx.add("soft", frame_drum("dum", 0.35, variant=bar % 3, seed=SEED + 30), t_of(bar, beat), pan=0.1)


def build_p2(mx: LoopMixer) -> None:
    g = rng(SEED + 3)
    for bar, ch in enumerate(CHORDS, start=1):
        mx.add("big", big_drum(0.7 * float(g.uniform(0.92, 1.04)), variant=bar % 4, seed=SEED + 40), t_of(bar))
        for s in range(16):                                                       # the roll, building every two bars
            if s % 2 == 1 and bar % 2 == 1:
                continue
            v = 0.2 + 0.4 * ((bar - 1) % 2 * 16 + s) / 31
            mx.add("roll", frame_drum("tek", v, variant=s % 4, seed=SEED + 41), t_of(bar, s / 4) + float(g.normal(0, 0.003)),
                   pan=float(g.uniform(-0.3, 0.3)))
        if ch in ("Cm", "Fm") and bar % 2 == 1:                                   # hard stabs on the minor roots
            m = n(ROOTS[ch]) + 24
            for k, off in enumerate((0, 7)):
                mx.add("stab", metallophone_note(m + off, 0.6, seed=SEED + 200 + bar * 2 + k, decay=1.6, hardness=0.8,
                                                 damp_at=0.4), t_of(bar), pan=-0.3 + 0.6 * k)
    line = [(float(m) - 12, 2 * BEAT) for m, _ in ORDER_HUM[:6]]                  # the Order's hum in the bass
    for k, bar in enumerate(HUM_BARS):
        mx.add("hum", hum_ensemble(line, voices=12, seed=SEED + 300 + k, register="low", spread=0.6), t_of(bar))


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 1:
        mx.bus("drone", G["drone"], send=0.35, process=lambda x: filt(x, [bq_lowpass(900, 0.7)]))
        mx.bus("pulse", G["pulse"], send=0.3, process=lambda x: filt(x, [bq_lowpass(1500, 0.7)]))
        mx.bus("pluck", G["pluck"], send=0.2, process=lambda x: filt(x, [bq_highpass(100, 0.7), bq_lowpass(4000, 0.7)]))
        mx.bus("soft", G["soft"], send=0.2)
    else:
        mx.bus("roll", G["roll"], send=0.15)
        mx.bus("big", G["big"], send=0.2, process=lambda x: filt(x, [bq_lowpass(2000, 0.7)]))
        mx.bus("hum", G["hum"], send=0.4, process=lambda x: filt(x, [bq_lowpass(1600, 0.7)]))
        mx.bus("stab", G["stab"], send=0.3, process=lambda x: filt(x, [bq_lowpass(6000, 0.7)]))


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    loops = []
    for stem, build in ((1, build_p1), (2, build_p2)):
        mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
        _bus_setup(mx, stem)
        build(mx)
        barge = ModFDNReverb(rt60=2.6, rt60_high=0.9, predelay=0.03, size=1.3, mod_depth=8.0, mod_rate=0.35,
                             early_level=0.2, lowcut=100.0, seed=SEED % 9973)
        _, loop = mx.render(reverb=barge, reverb_return_db=-3.0)
        loops.append(loop)
        del mx
    loops[1] = loops[1] * db_to_lin(STEM2_GAIN_DB)
    lead_in = int(round(LEAD_IN_S * SR))
    loops = [np.roll(x, lead_in, axis=0) for x in loops]
    full = loops[0] + loops[1]
    gain = db_to_lin(TARGET_LUFS - integrated_lufs(full))
    ctx = int(0.05 * SR)
    L = len(full)
    for _ in range(4):                    # one limiter gain curve for both stems, from the full stack (wrap-aware)
        f = full * gain
        lg = limit_gain(np.concatenate([f[-ctx:], f, f[:ctx]]), -2.0)[ctx: ctx + L]
        cur = integrated_lufs(f * lg[:, None])
        if abs(cur - TARGET_LUFS) < 0.1:
            break
        gain *= db_to_lin(TARGET_LUFS - cur)
    stems = [s * gain * lg[:, None] for s in loops]
    paths = [out_path, os.path.join(os.path.dirname(out_path), os.path.basename(OUT2))]
    extra = {"stems_of": "malcor_venn", "loop_bars": BARS, "downbeat_offset_s": lead_in / SR}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    for x, p in zip(stems, paths):
        write_ogg(p, x, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
        write_loop_sidecar(os.path.splitext(p)[0] + ".loop.json", SR, 0, L, BPM, 4, extra=extra)
    m = measure(stems[0] + stems[1])
    if stats is not None:
        stats["stem1_lufs"] = measure(stems[0])["integrated_lufs"]
    if verbose:
        print(f"malcor_venn: stack {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


if __name__ == "__main__":
    render()
