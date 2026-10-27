"""`raid`: the Order's raid on the Saltwright salvage camp (M3-AUD-821; act1_ch06.md B03, §6), a 92.3 s loop.

Original for this project (SPEC §2, §9). The only melody is the Order's congregational hum, motifs.py ORDER_HUM (this
project's own tune, first heard in the Shell Shrine; its notes are imported, never re-typed here); the drum pattern
and the fire were written for this cue. Nothing is derived from any existing tune.

The brief (act1_ch06.md §6): "Cutscene score. Almost no score: fire crackle, a low frame drum, and the diegetic
Stillguard hum (the Order's congregational tune, hummed calmly by a dozen men's voices) as the melody. The hum must
be the Order's existing hummed tune from the temple ambience, so the player knows it." Stillguard in red-lacquered
shell armour walk through the burning camp with torches, unhurried, humming while they work; it is the most
frightening sound in Act I because it is calm.

**Working with `stillguard_hum`.** ch06_raid.dlg plays `@music raid fade=1.0` and, at once, `@sfx stillguard_hum`
(assets_src/sfx/act1_cutscene_sfx.py: a dozen men hum ORDER_HUM once, ~22 s, close by). This cue is in the same key
(G: ORDER_HUM's own pitches) and at the same tempo (ORDER_HUM_BPM, 52), and it leaves the hum's first statement to
that SFX: the loop opens with 20 beats of fire and drum only (R, 23.1 s, the length of the hummed tune and a breath),
so on the first pass the SFX's men are the melody, near. Then the cue's own men take the tune up (H, 20 beats),
further off across the camp; then the fire alone again (R'), and the tune once more from fewer men, further still
(H'), as the patrol moves on through the camp. The hum, then only the fire: the way men at work hum a verse and
stop.

Layers (all synthesized; no samples):
* the fire: a burning camp's roar (low band noise that breathes) and its crackle (short pops), seamless over the
  loop; a timber giving way in R and in R';
* the drum: a large, low frame drum on beats 1 and 3, the second softer, unhurried and exact (the Order keeps
  time), from the first beat;
* the hum (H and H' only): men's voices on ORDER_HUM, eight at its pitch and four an octave below (as
  stillguard_hum voices it), set back in the camp; in H' six and three, softer and darker (further off).

Form (4/4, 20 bars of 4 beats; every event a sixteenth late, DOWNBEAT_OFFSET_S, so the loop seam falls before a
drum stroke, not on it): bars 1-5 R, fire and drum (the SFX's hum on the first pass) | bars 6-10 H, the hummed
tune (18 beats) and a breath | bars 11-15 R', fire and drum | bars 16-20 H', the tune further off. Loop:
LOOPSTART = 0, LOOPLENGTH = the whole file.

Render:  python3 assets_src/music/raid.py   (or tools/audio/render_all.py --only music/raid)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

from motifs import ORDER_HUM, ORDER_HUM_BPM, order_hum_in_seconds  # noqa: E402
from synth.drums import frame_drum  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, db_to_lin, filt, rng, smooth_noise  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import measure, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.voice import hum_ensemble  # noqa: E402

_spec = importlib.util.spec_from_file_location("act2_voices", os.path.join(os.path.dirname(__file__),
                                                                           "act2_voices.py"))
AV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AV)

OUT = os.path.join(ROOT, "assets", "audio", "music", "raid.ogg")
SEED = 20261825
TARGET_LUFS = -16.0
BPM = ORDER_HUM_BPM
BEAT = 60.0 / BPM
HUM_BEATS = sum(b for _, b in ORDER_HUM)          # 18
SECTION_BEATS = 20                                 # the tune and a breath
SECTIONS = 4                                       # R H R' H'
BARS = SECTIONS * SECTION_BEATS // 4
LOOP_S = SECTIONS * SECTION_BEATS * BEAT
S16 = BEAT / 4
## every event sits a sixteenth late, so the file's wrap falls a sixteenth before a drum stroke
DOWNBEAT_OFFSET_S = S16
H_START_BEAT = SECTION_BEATS
H2_START_BEAT = 3 * SECTION_BEATS
## the fire's pops peak about 1 dB over their samples between them (true peak): the mix is limited this far down
CEILING_DB = -2.5


def t_of(beat: float) -> float:
    return beat * BEAT + DOWNBEAT_OFFSET_S


def fire(g, loop_s: float) -> np.ndarray:
    """The camp burning: a roar that breathes and a crackle of pops, exactly one loop long and seamless (rendered
    longer and folded, act2_voices.fold). Stereo."""
    N = int(round(loop_s * SR))
    k = int(2.0 * SR)
    M = N + k
    out = np.zeros((M, 2))
    # one fire, a little wide: the roar and hiss are shared by both sides (mostly mono, so it costs the encoder
    # little), with a quieter independent layer on each side for width
    roar = filt(g.standard_normal(M), [bq_highpass(70, 0.7), bq_lowpass(700, 0.7)])
    roar *= 0.55 + 0.45 * (0.5 + 0.5 * smooth_noise(M, 0.9, g))
    hiss = filt(g.standard_normal(M), [bq_bandpass(2400, 0.8)]) * (0.25 + 0.15 * smooth_noise(M, 2.0, g))
    for side in (0, 1):
        width = filt(g.standard_normal(M), [bq_highpass(70, 0.7), bq_lowpass(500, 0.7)]) * 0.3
        out[:, side] += roar + 0.25 * hiss + width
    pops = np.zeros((M, 2))
    for _ in range(int(loop_s * 14)):
        at = int(g.uniform(0, M - 400))
        n_ = int(g.uniform(0.0015, 0.006) * SR)
        burst = g.standard_normal(n_) * np.exp(-np.arange(n_) / (n_ / 3.0)) * float(g.uniform(0.2, 1.0)) ** 1.5
        pan = float(g.uniform(-0.8, 0.8))
        pops[at: at + n_, 0] += burst * np.cos((pan + 1) * np.pi / 4)
        pops[at: at + n_, 1] += burst * np.sin((pan + 1) * np.pi / 4)
    pops = filt(pops, [bq_highpass(1200, 0.7), bq_lowpass(5500, 0.7)])
    return AV.fold(out * 0.25 + pops * 0.9, N, k)


def timber(g) -> np.ndarray:
    """A burning timber giving way: a dull crack and a short fall of embers. Mono."""
    N = int(1.5 * SR)
    t = np.arange(N) / SR
    k = int(0.03 * SR)
    crack = np.zeros(N)
    crack[:k] = filt(g.standard_normal(k), [bq_bandpass(900, 0.8)]) * np.exp(-np.arange(k) / (0.006 * SR))
    thud = np.sin(2 * np.pi * 85 * t) * np.exp(-t / 0.09) * 0.6
    embers = filt(g.standard_normal(N), [bq_highpass(1500, 0.7)]) * np.exp(-t / 0.4) * 0.15 * (t > 0.05)
    return crack + thud + embers


def build(mx: LoopMixer) -> None:
    g = rng(SEED)
    mx.add("fire", fire(rng(SEED + 1), LOOP_S), 0.0)
    mx.add("fire", timber(rng(SEED + 2)) * 0.7, t_of(11.3), pan=-0.4)
    mx.add("fire", timber(rng(SEED + 5)) * 0.5, t_of(2 * SECTION_BEATS + 6.6), pan=0.45)
    # the drum: 1 and 3 of every bar, the second softer, exact
    for beat in range(0, SECTIONS * SECTION_BEATS, 2):
        first = beat % 4 == 0
        v = 0.55 if first else 0.36
        x = frame_drum("dum", v, variant=(beat // 2) % 8, size=1.8, seed=SEED + 3)
        mx.add("drum", x, t_of(beat) + float(g.normal(0, 0.002)), pan=-0.05)
    # the men across the camp: ORDER_HUM, eight at pitch and four an octave below
    line = order_hum_in_seconds(BPM)
    hi = hum_ensemble(line, voices=8, seed=SEED + 10, register="low", spread=0.7)
    lo = hum_ensemble([(m - 12.0, d) for m, d in line], voices=4, seed=SEED + 11, register="low", spread=0.6)
    mx.add("hum", hi, t_of(H_START_BEAT) - 0.08)
    mx.add("hum", lo * 0.8, t_of(H_START_BEAT) - 0.08)
    hi2 = hum_ensemble(line, voices=6, seed=SEED + 20, register="low", spread=0.8)
    lo2 = hum_ensemble([(m - 12.0, d) for m, d in line], voices=3, seed=SEED + 21, register="low", spread=0.7)
    far = filt(hi2 + 0.8 * lo2, [bq_lowpass(1500, 0.7)]) * 0.6
    mx.add("hum", far, t_of(H2_START_BEAT) - 0.08)


# Bus gains were set from measured bus loudness (render(stats=...)["bus_lufs"]): the hum at L (over H, where it
# sings); the drum L-4 and the fire L-6, each over the whole loop. In R the cue is fire and drum only, about 6 LU
# under H (about -19 LUFS), so stillguard_hum's men (an SFX at -21 LUFS momentary) carry the first statement over it.
GAINS = {"hum": 0.0, "drum": 1.0, "fire": -4.8}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=10.0)
    mx.bus("hum", GAINS["hum"], send=0.45, process=lambda x: filt(x, [bq_highpass(70, 0.7), bq_lowpass(2600, 0.7)]))
    mx.bus("drum", GAINS["drum"], send=0.25, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(1800, 0.7)]))
    mx.bus("fire", GAINS["fire"], send=0.12)
    build(mx)
    shoals = ModFDNReverb(rt60=1.9, rt60_high=0.7, predelay=0.025, size=1.0, mod_depth=7.0, mod_rate=0.4,
                          early_level=0.18, lowcut=110.0, seed=SEED % 9973)
    _, loop = mx.render(reverb=shoals, reverb_return_db=-4.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=CEILING_DB, report=rep)
    L = len(loop)
    write_ogg(out_path, loop, quality=2.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})  # q2: noise-heavy (ADR 0171)
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 4,
                       extra={"loop_bars": BARS, "downbeat_offset_s": DOWNBEAT_OFFSET_S,
                              "hum_from_s": t_of(H_START_BEAT)})
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = _bus_stats(mx)
        stats["limiter"] = rep
    if verbose:
        print(f"raid: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  limiter {rep}")
    return m


def _bus_stats(mx: LoopMixer) -> dict:
    """The hum over H; the drum and the fire over the loop."""
    out = {}
    h0, h1 = int(t_of(H_START_BEAT) * SR), int(t_of(2 * SECTION_BEATS) * SR)
    for b in mx.buses.values():
        x = db_to_lin(b.gain_db) * (b.process(b.loop) if b.process else b.loop)
        out[b.name] = integrated_lufs(x[h0:h1] if b.name == "hum" else x)
    return out


if __name__ == "__main__":
    st: dict = {}
    render(stats=st)
    print("  buses", {k: round(v, 1) for k, v in st["bus_lufs"].items()})
