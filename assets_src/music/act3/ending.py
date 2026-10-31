"""The Ending's quiet cues (M5-A3P-1952; act3_ending.md E1–E7, R2–R4; ADR 0208): `goodbye_imra`, `ending_lift_bed`,
`goodbye_kerrid`, `ending_dock` and `post_credits_lamp`. One render() writes all five.

Original composition for this project (SPEC §2). Every tune in them is the game's own and is loaded, never retyped:
* the Hush's first phrase as the first verse is sung (hush_first_verse.py `VERSE`, its harmony `LH`): the Velamir
  lullaby (decisions_log N-11);
* Kerrid's stair (motifs.py `KERRID_STAIR`, on his own bowed low string, kerrid_stair.py `bowed`, `cello_body`);
* the star-path cell (haluna_dawn.py `RH_CELL`), the homecoming tune of Ch2's beach.
The settings, voicings and endings were written for these cues.

**goodbye_imra** (E1, about 16 s). "The score drops out completely, and Imra's unaccompanied hum is the cue. A single
piano note enters only after she is gone." Her hum is the scene's own sound (`velamir_lullaby_hum`, act3 sfx); this
cue is the one note: the lullaby's home, A, played once, softly, pedal down, and left to ring out.

**ending_lift_bed** (R2, R3, a loop of 40 s; R4 thins it to nothing with the scene's own fade). "The drone and a faint
high shimmer, no melody." A drone on A (A2 E3 A3, low strings, barely moving), and high glints of glass on the notes
of A major (A6 C#7 E7) placed sparsely, like the last motes still rising off the sea. Quiet: a rest, not a cue.

**goodbye_kerrid** (E3, about 115 s, the last farewell). "A solo low string with a gamelan pulse, the walking rhythm
of the pilgrimage, slowing to a stop. As the last farewell, its stop is the end of the walking." His stair (D3 then
A2, a stride each) on his bowed low string; under each stride a gamelan pulse (a metallophone an octave up, a soft
kettle gong on the first of each pair). It starts at the stair's own 48 BPM and every stride is a little longer than
the last, until the last A is held and nothing follows it. The kerrid_last_night cue never slowed (motifs.py's rule);
this is where the stride is spent.

**ending_dock** (E6, about 80 s). "Solo piano: the Hush theme's first phrase, which resolves at last. The instrument
carries it, never a voice." The first verse's tune on the piano over its own harmony. Its fourth line, which always
stopped on E (*mir*), goes on up to A, over E7 to A major, as `unbinding_swell` resolved it. Then the first line
once more, an octave lower, slower, ending on A, and the chord left ringing over the dark sea.

**post_credits_lamp** (E7, about 18 s). "A single low metallophone phrase from `haluna_dawn` and one struck match." The
match is the scene's own sound (`match_struck`); the cue is the star-path's first phrase (F# E D E | F# A B A), two
octaves down on a low metallophone, unhurried, in the blue hour before dawn.

Render:  python3 assets_src/music/act3/ending.py   (all five; or tools/audio/render_all.py --only act3/ending)
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
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from levels import bus_levels  # noqa: E402
from motifs import KERRID_STAIR, KERRID_STAIR_BPM, KERRID_STAIR_STRIDE  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.gongs import kettle_gong  # noqa: E402
from synth.grand import MAX_LEN, PedalCurve, PianoBody, grand_note  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.metallophone import metallophone_note  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.parallel import render_jobs  # noqa: E402
from synth.performance import plan_pedal  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from the_letting import glass  # noqa: E402
from unbinding_swell import RESOLVED, RESOLVED_CHORDS  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FV = _load("hush_first_verse")
KS = _load("kerrid_stair")
DAWN = _load("haluna_dawn")
OUT_DIR = os.path.join(ROOT, "assets", "audio", "act3", "music")
SEED = 20261036
QUIET_LUFS = -20.0          # the rests, the bed and the post-credits phrase (targets.py)
TARGET_LUFS = -16.0
ONE_NOTE_LUFS = -24.0       # goodbye_imra: one soft note after silence, never limited (targets.py)


def _piano(notes: list[dict], pedal, seed: int) -> list[np.ndarray]:
    jobs = []
    for k, nt in enumerate(notes):
        m = (pedal.times >= nt["t0"] - 0.01) & (pedal.times <= nt["t0"] + MAX_LEN + 0.01)
        jobs.append((grand_note, dict(m=nt["m"], vel=nt["vel"], key_up=nt["key_up"], seed=seed + 7919 * k,
                                      t_abs=nt["t0"], pedal=PedalCurve(pedal.times[m].copy(), pedal.depth[m].copy()))))
    return render_jobs(jobs)


def _finish(mx, hall, out_path: str, target: float, fade_s: float, ceiling: float = -2.0) -> dict:
    y = mx.render(reverb=hall, reverb_return_db=-2.0)
    fade = int(fade_s * SR)
    y[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    y = normalize_integrated(y, target, ceiling_db=ceiling)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, y, quality=3.0)
    return measure(y)


def _hall(seed: int, rt60: float = 3.4) -> ModFDNReverb:
    return ModFDNReverb(rt60=rt60, rt60_high=1.4, predelay=0.03, size=1.2, mod_depth=8.0, mod_rate=0.4,
                        early_level=0.22, lowcut=80.0, width=0.75, seed=seed % 9973)


def goodbye_imra(out_path: str, verbose: bool) -> dict:
    length = 16.0
    note = [dict(m=n("A3"), vel=0.30, t0=0.4, key_up=12.0)]
    pedal = plan_pedal([], start=0.0, end_release=13.0, release_len=3.0, g=rng(SEED))
    mx = Mixer(length)
    mx.bus("piano", 25.2, send=0.3, process=PianoBody(pedal))
    for nt, x in zip(note, _piano(note, pedal, SEED + 1)):
        mx.add("piano", x, nt["t0"])
    m = _finish(mx, _hall(SEED + 1), out_path, ONE_NOTE_LUFS, 2.0, ceiling=-3.0)
    if verbose:
        print(f"goodbye_imra: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


LIFT_LOOP_S = 40.0
# From measured bus loudness: the drone at L, the shimmer L-8 (faint).
LIFT_GAINS = {"drone": 0.0, "shimmer": -23.8}


def ending_lift_bed(out_path: str, verbose: bool, stats: dict | None) -> dict:
    g = rng(SEED + 10)
    mx = LoopMixer(intro_s=0.0, loop_s=LIFT_LOOP_S, preroll_s=8.0)
    mx.bus("drone", LIFT_GAINS["drone"], send=0.35, process=lambda x: string_body(x, cutoff=900.0))
    mx.bus("shimmer", LIFT_GAINS["shimmer"], send=0.8, process=lambda x: filt(x, [bq_highpass(600, 0.7)]))
    mx.add("drone", pad_chord([n("A2"), n("E3"), n("A3")], LIFT_LOOP_S + 8.0, vel=0.4, seed=SEED + 11, attack=4.0,
                              release=4.0, voices=4, spread_cents=5.0), -4.0)
    t = 1.5
    k = 0
    while t < LIFT_LOOP_S - 1.0:
        p = ["A6", "C#7", "E7", "A6", "E7"][k % 5]
        mx.add("shimmer", glass(float(n(p)), 2.5, 0.35 + 0.1 * float(g.random()), SEED + 20 + k), t,
               pan=float(g.uniform(-0.5, 0.5)))
        t += 3.0 + 2.5 * float(g.random())
        k += 1
    _, loop = mx.render(reverb=_hall(SEED + 12, rt60=4.5), reverb_return_db=-1.5)
    _, loop = master_loop(np.zeros((0, 2)), loop, QUIET_LUFS, ceiling_db=-6.0, report={})
    L = len(loop)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, None, None)
    m = measure(loop)
    if stats is not None:
        stats["lift_bus_lufs"] = dict(mx.bus_lufs)
    if verbose:
        print(f"ending_lift_bed: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


KERRID_STRIDES = 18
KERRID_SLOWING = 1.09        # each stride this much longer than the last
# From measured bus loudness: the stair at L, the metallophone pulse L-6, the gong L-8.
KERRID_GAINS = {"stair": 0.0, "pulse": 5.0, "gong": -2.8}


def kerrid_strides() -> list[tuple[float, float, float]]:
    """[(t, stride seconds, midi)]: the stair from its own tempo, each stride a little longer, to a stop."""
    beat = 60.0 / KERRID_STAIR_BPM
    out = []
    t = 1.0
    for k in range(KERRID_STRIDES):
        m, _beats = KERRID_STAIR[k % len(KERRID_STAIR)]
        stride = KERRID_STAIR_STRIDE * beat * KERRID_SLOWING ** k
        out.append((t, stride, float(m)))
        t += stride
    return out


def goodbye_kerrid(out_path: str, verbose: bool, stats: dict | None) -> dict:
    g = rng(SEED + 30)
    strides = kerrid_strides()
    last_t, last_d, last_m = strides[-1]
    length = last_t + last_d + 8.0
    mx = Mixer(length)
    mx.bus("stair", KERRID_GAINS["stair"], send=0.3, process=KS.cello_body)
    mx.bus("pulse", KERRID_GAINS["pulse"], send=0.4, process=lambda x: filt(x, [bq_highpass(150, 0.7)]))
    mx.bus("gong", KERRID_GAINS["gong"], send=0.35, process=lambda x: filt(x, [bq_highpass(60, 0.7),
                                                                           bq_lowpass(4000, 0.7)]))
    for k, (t, stride, m) in enumerate(strides):
        last = k == len(strides) - 1
        d = stride - 0.1 if not last else stride + 2.0
        lvl = 1.0 - 0.25 * k / len(strides)
        mx.add("stair", KS.bowed(m, d, 0.5 * lvl * float(g.uniform(0.97, 1.02)), SEED + 100 + k, attack=0.4,
                                 release=1.2 if not last else 3.0), t - KS.BOW_PRE)
        mx.add("pulse", metallophone_note(m + 12, vel=0.45 * lvl, seed=SEED + 200 + k), t, pan=0.2)
        if k % 2 == 0:
            mx.add("gong", kettle_gong(m + 12, vel=0.4 * lvl, seed=SEED + 300 + k, t60=2.4), t, pan=-0.2)
    m = _finish(mx, _hall(SEED + 31, rt60=3.0), out_path, TARGET_LUFS, 4.0)
    if stats is not None:
        stats["kerrid_bus_lufs"] = bus_levels(mx)
    if verbose:
        print(f"goodbye_kerrid: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f"  last stride {last_d:.1f}s")
    return m


DOCK_BPM = 50.0
A_MAJOR_SPREAD = ["A1", "A2", "E3", "C#4", "E4", "A4"]


def ending_dock(out_path: str, verbose: bool) -> dict:
    g = rng(SEED + 40)
    beat = 60.0 / DOCK_BPM
    bar = 3 * beat
    lines = FV.VERSE[:3] + [RESOLVED]
    chords = FV.LH[:6] + RESOLVED_CHORDS
    notes: list[dict] = []
    t = 1.0
    for line in lines:
        for p, beats in line:
            notes.append(dict(m=n(p), vel=0.36 * float(g.uniform(0.95, 1.04)), t0=t + float(g.normal(0, 0.006)),
                              key_up=beats * beat + 0.03, role="mel"))
            t += beats * beat
    for b, ch in enumerate(chords):
        bass, fifth, c1, c2 = ch.split()
        for i, p in enumerate([bass, fifth, c1, c2, c1, fifth]):
            v = (0.30 if i == 0 else 0.18) * float(g.uniform(0.94, 1.05))
            notes.append(dict(m=n(p), vel=v, t0=1.0 + b * bar + i * bar / 6 + float(g.normal(0, 0.006)),
                              key_up=bar * (1.0 if i == 0 else 0.3), role="acc"))
    resolve_t = 1.0 + 8 * bar - 3 * beat
    for j, p in enumerate(A_MAJOR_SPREAD):
        notes.append(dict(m=n(p), vel=0.28 - 0.02 * j, t0=resolve_t + 0.09 * j, key_up=3 * bar, role="acc"))
    # the first line once more, an octave lower and slower, ending on A; the chord left ringing
    t = resolve_t + 3 * bar
    for p, beats in FV.VERSE[0]:
        notes.append(dict(m=n(p) - 12, vel=0.30, t0=t, key_up=beats * beat * 1.25 + 0.03, role="mel"))
        t += beats * beat * 1.25
    end_t = t
    for j, p in enumerate(["A1", "E2", "A2", "C#3", "E3"]):
        notes.append(dict(m=n(p), vel=0.24 - 0.02 * j, t0=end_t + 0.12 * j, key_up=8.0, role="acc"))
    changes = [1.0 + b * bar for b in range(1, len(chords))] + [resolve_t, resolve_t + 3 * bar, end_t]
    pedal = plan_pedal(changes, start=1.0, end_release=end_t + 9.0, release_len=3.0, g=g)
    length = end_t + 14.0
    mx = Mixer(length)
    mx.bus("piano", 25.2, send=0.28, process=PianoBody(pedal))
    for nt, x in zip(notes, _piano(notes, pedal, SEED + 41)):
        mx.add("piano", x, nt["t0"], pan=float(np.clip((nt["m"] - 64) / 60.0, -0.3, 0.3)))
    m = _finish(mx, _hall(SEED + 42, rt60=3.0), out_path, TARGET_LUFS, 3.0)
    if verbose:
        print(f"ending_dock: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


def post_credits_lamp(out_path: str, verbose: bool) -> dict:
    g = rng(SEED + 50)
    beat = 60.0 / 54.0
    phrase = DAWN.RH_CELL[:8]                      # F# E D E | F# A B A
    length = sum(b for _, b in phrase) * beat + 9.0
    mx = Mixer(length)
    mx.bus("metal", 0.0, send=0.4, process=lambda x: filt(x, [bq_highpass(90, 0.7), bq_lowpass(5000, 0.7)]))
    t = 1.0
    for i, (p, beats) in enumerate(phrase):
        mx.add("metal", metallophone_note(float(n(p)) - 24, vel=0.5 * float(g.uniform(0.95, 1.04)), seed=SEED + 60 + i),
               t + float(g.normal(0, 0.01)))
        t += beats * beat
    m = _finish(mx, _hall(SEED + 51, rt60=2.8), out_path, QUIET_LUFS, 3.0, ceiling=-4.0)
    if verbose:
        print(f"post_credits_lamp: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}")
    return m


def render(out_path: str = os.path.join(OUT_DIR, "goodbye_imra.ogg"), verbose: bool = True,
           stats: dict | None = None) -> dict:
    d = os.path.dirname(out_path)
    m = goodbye_imra(os.path.join(d, "goodbye_imra.ogg"), verbose)
    ending_lift_bed(os.path.join(d, "ending_lift_bed.ogg"), verbose, stats)
    goodbye_kerrid(os.path.join(d, "goodbye_kerrid.ogg"), verbose, stats)
    ending_dock(os.path.join(d, "ending_dock.ogg"), verbose)
    post_credits_lamp(os.path.join(d, "post_credits_lamp.ogg"), verbose)
    return m


if __name__ == "__main__":
    render()
