"""`undertow_rising`: Ch1 C1-12/C1-13 and Ch8 B07-B09, the Undertow standing up (M3-AUD-819): two synchronized
stems, a ~17 s intro and a 70 s loop.

Original composition for this project (SPEC §2, §9). The brass line, the clusters and both pulses below were written
for this cue and are not derived from any existing melody. The intro quotes our own Oruvel town tune (oruvel.py
TUNE_A, played by oruvel.py's own squeezebox model; nothing re-typed).

The briefs. Ch1 (act1_ch01.md §6): "Cutscene score, two stems. Stem 1: the town bed's melody stopping mid-phrase,
then low brass and a held cluster as the wall rises. Stem 2 (the run): a pulse added, never a heroic one." Ch8
(act1_ch08.md §6): "Low brass and a slow pulse that is wrong against the wind's sound. The bells along the coast
(diegetic SFX) fall on its downbeats." One cue serves both: it loops after its intro, so it can sit under the run.

The storm's own mode: G octatonic (half-whole: G Ab Bb B C# D E F), the mode undertows_reach.py gave the Undertow
and nothing else in the score uses. It repeats at every minor third, so no chord in it is home; the line climbs by
minor thirds (G, then Bb, then the tritone C#) and the wall never arrives anywhere. 4/4 at 48 BPM (a bar is 5 s).

**Stem 1** (`undertow_rising_p1.ogg`; plays from the start):
* the intro: Oruvel's tune on the squeezebox with its left hand, two bars and a half, stopping mid-phrase (the
  bellows stop on the C), then a breath of nothing, then the wall: the loop's own last two bars (the rise);
* low brass: a section of trombones and a tuba (synthesized here: lip-buzz harmonics that brighten as the breath
  pressure rises, a scoop into each attack, a broad formant near 600 Hz) in octaves, slow;
* a held cluster in the low strings (G Ab Bb, then wider), swelling and receding in four-bar breaths;
* the slow pulse, wrong against the wind: a big drum on every downbeat (where the Ch8 coast bells fall) and a
  second, softer stroke late, on the "and" of two (3 + 5 eighths: a limp, not a march); a large gong at bars 1, 9.

**Stem 2** (`undertow_rising_p2.ogg`; the run, Ch1 C1-13): the pulse added. A muted low string ostinato in
sixteenths that leans on the minor second (G G G Ab), frame-drum teks on the eighths and ghosts between, a sub-bass
heartbeat on each half bar. No snare, no fanfare, no major chord, no rising sequence: it hurries, it never charges.

Form (bars): 1-4 the line from G (cluster G Ab Bb) | 5-8 the line a minor third up, from Bb | 9-12 the tritone, C#,
the cluster widest | 13-14 the rise: the brass on a held G and the full cluster swelling into bar 1 (these two bars
are also the intro's end, so the first-play splice carries the same tails).

Mastering (as undertows_reach): both stems share one gain (the full stack at -16 LUFS over intro + loop) and one
limiter gain curve computed on the full stack, so stem 1 + stem 2 is exactly the limited mix; stem 2 lifts the stack
about 2 LU. The loop starts a thirty-second before bar 1's downbeat (the sidecars' `downbeat_offset_s`), so the
wrap seam falls inside the run's last sixteenth, not on an attack; LOOPSTART is the intro's length. The sidecars
count quarter notes (bpm 48).

Render:  python3 assets_src/music/undertow_rising.py   (or tools/audio/render_all.py --only undertow_rising)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.drums import big_drum, frame_drum  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, midi_to_hz, rng  # noqa: E402
from synth.dsp import smooth_noise  # noqa: E402
from synth.electric import bass_note  # noqa: E402
from synth.gongs import large_gong  # noqa: E402
from synth.looping import LoopMixer, write_loop_sidecar  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import limit_gain, measure, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402

_spec = importlib.util.spec_from_file_location("oruvel", os.path.join(HERE, "oruvel.py"))
ORU = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ORU)

OUT_DIR = os.path.join(ROOT, "assets", "audio", "music")
OUT = os.path.join(OUT_DIR, "undertow_rising_p1.ogg")
STEM_NAMES = ("undertow_rising_p1.ogg", "undertow_rising_p2.ogg")
SEED = 20261821
TARGET_LUFS = -16.0
BPM = 48.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 14
LOOP_S = BARS * BAR
RISE_BARS = 2                         # the loop's last bars, which the intro ends with
LEAD_IN_S = BEAT / 8                  # the files' loop starts a thirty-second before bar 1's downbeat
## Stem 2's trim at mastering (dB): the run lifts the stack about 2 LU over stem 1 alone (render prints both).
STEM2_GAIN_DB = 3.0

## The intro: Oruvel's tune (oruvel.TUNE_A) from its first bar, stopped on the C of its third bar.
TOWN_T0 = 0.35                        # the squeezebox's first note (s)
TOWN_STOP = (3, 4)                    # bar 3 of the tune, at eighth 4 (the C5's attack): the bellows stop
TOWN_CHORDS = ["G", "G", "C"]         # oruvel's left hand under those bars (its CHORDS for bars 5-7)
GAP_S = 1.5                           # nothing, then the wall
ORU_BAR = ORU.BAR


def _town_t(bar: int, eighth: float) -> float:
    """Seconds from the file start to swung eighth `eighth` of tune bar `bar` (oruvel.t_of, re-based)."""
    return TOWN_T0 + ORU.t_of(bar, eighth) - ORU.t_of(1, 0)


TOWN_END = _town_t(*TOWN_STOP) + 0.16
INTRO_S = TOWN_END + GAP_S + RISE_BARS * BAR

## Stem 1: the brass line (pitch | None, beats), four bars a row; the tuba doubles it an octave down.
BRASS = [
    [("G2", 3), ("Ab2", 1)], [("Bb2", 2), ("Ab2", 2)], [("G2", 4)], [(None, 2), ("F2", 1), ("Ab2", 1)],
    [("Bb2", 3), ("B2", 1)], [("C#3", 2), ("B2", 2)], [("Bb2", 4)], [(None, 2), ("Ab2", 1), ("B2", 1)],
    [("C#3", 4)], [("D3", 2), ("C#3", 2)], [("B2", 2), ("Bb2", 2)], [("Ab2", 3), (None, 1)],
    [("G2", 8)], [],
]
## the held clusters: (start bar, bars, pitches, attack s)
CLUSTERS = [(1, 4, ["G2", "Ab2", "Bb2"], 3.0), (5, 4, ["G2", "Bb2", "B2", "C#3"], 3.0),
            (9, 4, ["G2", "Ab2", "C#3", "D3", "E3"], 3.0), (13, 2, ["G1", "G2", "Ab2", "Bb2", "B2", "C#3"], 8.0)]
## Stem 2: the run's ostinato by half bar (sixteenths): the minor second leaned on, the root moving with the line
RUN_ROOT = {1: "G1", 5: "Bb1", 9: "C#2", 13: "G1"}


def t_of(bar: int, beat: float = 0.0) -> float:
    """Seconds from the loop start to `beat` (0-based) of `bar` (1-based)."""
    return (bar - 1) * BAR + beat * BEAT


def low_brass(m: float, dur: float, vel: float, seed: int, attack: float = 0.12, swell: float = 0.0,
              release: float = 0.3, sr: int = SR) -> np.ndarray:
    """One low brass note (trombone or tuba): a lip-buzz harmonic series whose upper harmonics grow faster than the
    fundamental as the breath pressure rises (so a soft note is dark and round, a loud one brassy, not just louder),
    a broad formant near 600 Hz and a softer one near 1.4 kHz (the bore and bell), a scoop of a few cents into the
    attack (the lips finding the slot), a slow drift, and a little buzz noise on the pressure. Mono."""
    g = rng(seed)
    f0 = midi_to_hz(m)
    N = int((dur + 4 * release + 0.05) * sr)
    t = np.arange(N) / sr
    P = np.clip(t / attack, 0, 1) ** 1.6
    if swell:
        x = np.clip(t / max(dur, 1e-3), 0, 1)
        P *= (1 - swell) + swell * x ** 1.6                         # a crescendo through the note
    P *= np.where(t > dur, np.exp(-(t - dur) / release), 1.0)
    P *= 1 + 0.03 * smooth_noise(N, 2.0, g, sr)
    P *= vel
    cents = -28.0 * np.exp(-t / 0.05) + 3.0 * smooth_noise(N, 0.4, g, sr)
    f = f0 * 2 ** (cents / 1200.0)
    ph = 2 * np.pi * np.cumsum(f) / sr
    K = int(max(1, min(40, 4500.0 / f0)))
    y = np.zeros(N)
    for k in range(1, K + 1):
        fk = k * f0
        a = k ** -0.85 * (1.0 + 1.4 * np.exp(-((fk - 600.0) / 380.0) ** 2)
                          + 0.5 * np.exp(-((fk - 1400.0) / 500.0) ** 2))
        a /= 1.0 + (fk / 2600.0) ** 4
        y += a * P ** (1.0 + 0.32 * (k - 1)) * np.sin(k * ph + g.uniform(0, 0.3))
    buzz = filt(g.standard_normal(N), [bq_bandpass(900.0, 0.8)]) * P ** 2 * 0.02
    out = y + buzz
    k2 = int(0.01 * sr)
    out[-k2:] *= np.linspace(1, 0, k2)
    return 0.15 * out


def _brass_events(bars: list, start_bar: int) -> list[tuple[float, float, float]]:
    """[(t, dur, midi)] of a line written as bars of (pitch | None, beats)."""
    out = []
    for i, bar in enumerate(bars):
        pos = 0.0
        for p, beats in bar:
            if p is not None:
                out.append((t_of(start_bar + i, pos), beats * BEAT, float(n(p))))
            pos += beats
    return out


def events_p1() -> list[tuple[str, np.ndarray, float, float]]:
    """Stem 1's loop events: (bus, signal, loop time, pan)."""
    ev = []
    for i, (t0, d, m) in enumerate(_brass_events(BRASS, 1)):
        long = d >= 6 * BEAT
        for j, (dm, pan, v, det) in enumerate(((0, -0.25, 0.85, 0.0), (0, 0.15, 0.8, 0.05), (-12, 0.0, 0.9, -0.03))):
            x = low_brass(m + dm + det, d * 0.97, v, SEED + 100 * i + j, attack=1.6 if long else 0.35,
                          swell=0.7 if long else 0.25, release=0.5 if long else 0.35)
            ev.append(("brass" if dm == 0 else "tuba", x, t0 + 0.012 * j, pan))
    for k, (bar, bars, pitches, att) in enumerate(CLUSTERS):
        x = pad_chord([n(p) for p in pitches], bars * BAR - 0.4, 0.8, seed=SEED + 2000 + k, voices=5,
                      spread_cents=10.0, attack=att, release=1.6, width=0.8)
        ev.append(("cluster", x, t_of(bar), 0.0))
    for bar in range(1, BARS + 1):
        ev.append(("pulse", big_drum(0.9, variant=bar, seed=SEED + 4), t_of(bar), 0.0))
        ev.append(("pulse", big_drum(0.5, variant=bar + 40, seed=SEED + 4), t_of(bar, 1.5), 0.08))
    for bar in (1, 9):
        ev.append(("gong", large_gong(n("G1"), 0.55, seed=SEED + 80 + bar, t60=9.0), t_of(bar), -0.1))
    return ev


def events_p2() -> list[tuple[str, np.ndarray, float, float]]:
    """Stem 2's loop events: the run."""
    g = rng(SEED + 1)
    ev = []
    root = n("G1")
    for bar in range(1, BARS + 1):
        if bar in RUN_ROOT:
            root = n(RUN_ROOT[bar])
        for s in range(16):
            off = 1 if s % 4 == 3 else 0                              # G G G Ab: the minor second leaned on
            v = (0.62 if s % 4 == 0 else 0.42) * g.uniform(0.92, 1.05)
            x = bass_note(root + 12 + off, BEAT / 4 * 0.85, v, seed=SEED + 5000 + 16 * bar + s, mute=0.65)
            ev.append(("run", x, t_of(bar, s / 4) + 0.002, 0.2 if s % 2 else -0.15))
            if s % 2 == 0:
                st, dv = ("tek", 0.34) if s % 4 == 2 else ("tek", 0.26)
            else:
                st, dv = "ghost", 0.12
            ev.append(("ticks", frame_drum(st, dv * g.uniform(0.88, 1.08), variant=bar * 16 + s, seed=SEED + 6),
                       t_of(bar, s / 4), 0.3 if st == "tek" else -0.3))
        for h in (0, 2):                                              # the heartbeat under it
            tt = np.arange(int(1.2 * SR)) / SR
            sub = np.sin(2 * np.pi * (36.0 + 10.0 * np.exp(-tt / 0.2)) * tt) * np.exp(-tt / 0.35)
            sub *= np.minimum(1.0, tt / 0.008)
            ev.append(("sub", sub * (1.0 if h == 0 else 0.7), t_of(bar, h), 0.0))
    return ev


def town_intro(mx: LoopMixer) -> None:
    """Stem 1's intro: Oruvel's tune on its squeezebox (oruvel.free_reed) with its left hand, stopped mid-phrase."""
    g = rng(SEED + 9)
    stop_t = _town_t(*TOWN_STOP)
    for i, bar_notes in enumerate(ORU.TUNE_A[: TOWN_STOP[0]]):
        bar = i + 1
        pos = 0
        for p, d in bar_notes:
            t0 = _town_t(bar, pos)
            if p is not None and t0 <= stop_t + 1e-6:
                t1 = _town_t(bar, pos + d) if pos + d < 8 else _town_t(bar + 1, 0)
                cut = t0 >= stop_t - 1e-6                               # the C: the bellows stop as it sounds
                dur = 0.16 if cut else t1 - t0
                x = ORU.free_reed(n(p), dur * 0.92, 0.75 * g.uniform(0.95, 1.03), int(g.integers(1 << 30)),
                                  detune_cents=10.0, bright=1.1, release=0.035 if cut else 0.06)
                mx.add("town", x, t0 + float(g.normal(0, 0.004)), pan=0.05, part="intro")
            pos += d
    for i, chord in enumerate(TOWN_CHORDS):                           # the left hand: bass on 1 and 3, stabs on 2, 4
        bar = i + 1
        rt, fifth, triad = ORU.LH[chord]
        for b in range(4):
            t0 = _town_t(bar, 2 * b)
            if t0 > stop_t + 0.01:
                break
            if b % 2 == 0:
                x = ORU.free_reed(n(rt if b == 0 else fifth), ORU.BEAT * 0.8, 0.62, SEED + 300 + 10 * bar + b,
                                  detune_cents=6.0, bright=0.8, release=0.05)
                mx.add("town_lh", x, t0, pan=-0.1, part="intro")
            else:
                for k, p in enumerate(triad.split()):
                    x = ORU.free_reed(n(p), ORU.BEAT * 0.42, 0.45, SEED + 400 + 100 * bar + 10 * b + k,
                                      detune_cents=7.0, bright=0.9, release=0.04, attack=0.02)
                    mx.add("town_lh", x, t0, pan=-0.1 + 0.1 * k, part="intro")


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]) for the planned levels below.
GAINS = {"town": -6.6, "town_lh": -6.5, "brass": 0.0, "tuba": 0.5, "cluster": 8.7, "pulse": -0.8, "gong": -6.5,
         "run": 6.9, "ticks": 16.1, "sub": -7.5}
## The plan (LU relative to the stem-1 lead, the trombones, by each bus's integrated loudness; the town's buses over
## the intro only, measured against the brass over the loop).
PLAN = {"town": -2.0, "town_lh": -9.0, "brass": 0.0, "tuba": -4.0, "cluster": -6.0, "pulse": -6.0, "gong": -12.0,
        "run": -5.0, "ticks": -11.0, "sub": -10.0}


def _bus_setup(mx: LoopMixer, stem: int) -> None:
    G = GAINS
    if stem == 1:
        mx.bus("town", G["town"], send=0.22,
               process=lambda x: filt(x, [bq_highpass(120, 0.7), bq_peak(3200, -1.5, 1.0)]))
        mx.bus("town_lh", G["town_lh"], send=0.15, process=lambda x: filt(x, [bq_highpass(60, 0.7),
                                                                             bq_lowpass(5000, 0.7)]))
        mx.bus("brass", G["brass"], send=0.35, process=lambda x: filt(x, [bq_highpass(60, 0.7), bq_lowpass(5000, 0.7)]))
        mx.bus("tuba", G["tuba"], send=0.3, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(2500, 0.7)]))
        mx.bus("cluster", G["cluster"], send=0.4, process=lambda x: string_body(x, cutoff=1100.0))
        mx.bus("pulse", G["pulse"], send=0.25, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(1800, 0.7)]))
        mx.bus("gong", G["gong"], send=0.4)
    else:
        mx.bus("run", G["run"], send=0.12, process=lambda x: filt(x, [bq_highpass(45, 0.7), bq_lowpass(2200, 0.7)]))
        mx.bus("ticks", G["ticks"], send=0.15, process=lambda x: filt(x, [bq_lowpass(5000, 0.7)]))
        mx.bus("sub", G["sub"], send=0.0, process=lambda x: filt(x, [bq_lowpass(120, 0.7)]))


def _place(mx: LoopMixer, events: list) -> None:
    """Each loop event in the loop; those of the last RISE_BARS bars again at the intro's end (the same signal)."""
    rise_t = LOOP_S - RISE_BARS * BAR
    for bus, x, t, pan in events:
        mx.add(bus, x, t, pan=pan)
        if t >= rise_t - 1e-6:
            mx.add(bus, x, INTRO_S - (LOOP_S - t), pan=pan, part="intro")


# Levels (LU relative to the trombones, the stem-1 lead; PLAN above): GAINS were set from a render's measured bus
# loudness to land these, and confirmed by a second render.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    intros, loops, bus_lufs, splice = [], [], {}, []
    for stem in (1, 2):
        mx = LoopMixer(intro_s=INTRO_S, loop_s=LOOP_S, preroll_s=9.0)
        _bus_setup(mx, stem)
        if stem == 1:
            town_intro(mx)
            _place(mx, events_p1())
        else:
            _place(mx, events_p2())
        hall = ModFDNReverb(rt60=3.0, rt60_high=1.0, predelay=0.03, size=1.2, mod_depth=8.0, mod_rate=0.4,
                            early_level=0.28, lowcut=90.0, seed=SEED % 9973)
        intro, loop = mx.render(reverb=hall, reverb_return_db=-3.0)
        intros.append(intro)
        loops.append(loop)
        bus_lufs.update(mx.bus_lufs)
        splice.append(mx.splice_residual_db)
        if stem == 1:
            for name in ("town", "town_lh"):
                b = mx.buses[name]
                xi = b.process(b.intro[: mx.S]) * db_to_lin(b.gain_db)
                bus_lufs[name] = integrated_lufs(xi)
    loops[1] = loops[1] * db_to_lin(STEM2_GAIN_DB)
    intros[1] = intros[1] * db_to_lin(STEM2_GAIN_DB)
    # The loop is periodic: the files' loop starts a thirty-second before bar 1's downbeat (the intro loses its last
    # thirty-second, which is the loop's last too), so the wrap seam falls inside a sixteenth, not on its attack.
    lead = int(round(LEAD_IN_S * SR))
    intros = [x[: len(x) - lead] for x in intros]
    loops = [np.roll(x, lead, axis=0) for x in loops]
    S, L = len(intros[0]), len(loops[0])
    fi, fl = intros[0] + intros[1], loops[0] + loops[1]
    gain = db_to_lin(TARGET_LUFS - integrated_lufs(np.concatenate([fi, fl])))
    ctx = int(0.05 * SR)
    # one limiter gain curve for both stems, from the full stack (the loop wrap-aware), iterated to the target
    for _ in range(5):
        a, b = fi * gain, fl * gain
        lg_l = limit_gain(np.concatenate([b[-ctx:], b, b[:ctx]]), -2.0)[ctx: ctx + L]
        lg_i = limit_gain(np.concatenate([a, b[:ctx]]), -2.0)[:S]
        cur = integrated_lufs(np.concatenate([a * lg_i[:, None], b * lg_l[:, None]]))
        if abs(cur - TARGET_LUFS) < 0.1:
            break
        gain *= db_to_lin(TARGET_LUFS - cur)
    stems = [np.concatenate([i * gain * lg_i[:, None], lp * gain * lg_l[:, None]]) for i, lp in zip(intros, loops)]
    paths = [out_path, os.path.join(os.path.dirname(out_path), STEM_NAMES[1])]
    extra = {"stems_of": "undertow_rising", "loop_bars": BARS, "intro_s": S / SR, "downbeat_offset_s": lead / SR}
    for x, p in zip(stems, paths):
        write_ogg(p, x, quality=3.0, tags={"LOOPSTART": str(S), "LOOPLENGTH": str(L)})
        write_loop_sidecar(os.path.splitext(p)[0] + ".loop.json", SR, S, L, BPM, 4, extra=extra)
    m = measure(stems[0] + stems[1])
    m1 = measure(stems[0])
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
        stats["stem1_lufs"] = m1["integrated_lufs"]
        stats["splice_residual_db"] = splice
    if verbose:
        lim = np.concatenate([lg_i, lg_l])
        print(f"undertow_rising: {m['seconds']:.2f}s (intro {S / SR:.2f}s + loop {L / SR:.2f}s)  full "
              f"{m['integrated_lufs']:.2f} LUFS TP {m['true_peak_dbtp']:.2f} dBTP; stem 1 alone "
              f"{m1['integrated_lufs']:.2f} LUFS; limited {(lim < 0.999).mean() * 100:.2f} %, max {-20 * np.log10(max(lim.min(), 1e-9)):.2f} dB;"
              f" splice residual {[round(s, 1) for s in splice]} dB")
        lead_l = bus_lufs["brass"]
        print("  buses (LU vs the brass)", {k: round(v - lead_l, 1) for k, v in bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
