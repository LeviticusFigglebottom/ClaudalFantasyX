"""`hush_second_verse`: the Hush, verse 2, sung to the mountain (M3-AUD-821; act1_ch05.md B10, §6), 46.6 s.

Original composition for this project (SPEC §2): the melody is our own Hush theme's second phrase (hush_theme_v2.py
MEL_B, its eight bars note for note), not adapted from any existing tune.

The brief (act1_ch05.md §6): "Diegetic Hush, verse 2: the Hush theme's second phrase, sung (or carried by the
vocalise-like solo instrument until SPEC §16 Q4/Q5 settle a voice) over a drone. Thunder on *mir* is part of the cue
(timed to the plume flash)." Asha faces the crown in Ashcrown's anvil court and sings toward the plume
(ch05_kahre.dlg, `@music hush_second_verse fade=0.5`, then ch05_kahre_014-017, every verse ending on *mir*).

Through-composed (not looped):
* 0-4 s: the drone breathes in, the same A drone as the first verse (hush_first_verse.py `drone`: A2, E3, a little
  A3) and held to the end.
* The verse, four lines, one per sung line of the .dlg, with a breath after each. The voice is the first verse's
  vocalise-like instrument (a breath flute shaped by an open "ah", hush_first_verse.py `vocalise_bus`), slow
  vibrato, legato; MEL_B sits a third higher than MEL_A, so it is sung brighter and a little harder:
  "Ish karra, ish karra," = A G F | G D (ch05_kahre_014); "vey hal ennu," = E F G | A, held (015);
  "re ish, re ish..." = F E D | D C B (016); "...mir." = C E G | B, and the G# held (017). The verse ends on the
  phrase's own half cadence, the leading tone held over the A drone: an open question put to the mountain.
* **Thunder on *mir*:** the plume flashes as the held G# starts (MIR_S), and the thunder comes a beat later
  (THUNDER_DELAY_S, the light before the sound): a crack high in the plume, then a long roll down the mountain over
  about 7 s, with the voice still holding under it. The voice lets go into the roll.
* After: the drone under Rhen's and Toma's lines; the vocalise answers once, far back and soft, G# rising to A
  (the question settling: nothing comes up out of the ground, it is only Daro's hammer), and the drone fades.

**Marker (for Cinematics):** at render time `mir` starts at MIR_S = 31.54 s from the file start and the thunder's
crack lands at THUNDER_S = 32.59 s (render(stats=...) reports both). Time the plume flash to MIR_S. The .dlg's own
`@sfx plume_thunder` after ch05_kahre_017 would now double the thunder: it can go (Story's file; noted in the report).

Render:  python3 assets_src/music/hush_second_verse.py   (or tools/audio/render_all.py --only hush_second_verse)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import SR, bq_highpass, bq_lowpass, bq_peak, db_to_lin, filt, rng, smooth_noise  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("hush_first_verse", os.path.join(os.path.dirname(__file__),
                                                                                 "hush_first_verse.py"))
HF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(HF)

OUT = os.path.join(ROOT, "assets", "audio", "music", "hush_second_verse.ogg")
SEED = 20261823
TARGET_LUFS = -16.0
BPM = 56.0                      # the singer's tempo, as in the first verse
BEAT = 60.0 / BPM
DRONE_IN = HF.DRONE_IN          # 4 s (the drone function fades in over this)
FLUTE_PRE = HF.FLUTE_PRE        # the breath flute speaks 50-80 ms late
BREATH_S = 0.75                 # the singer's breath after each line
THUNDER_DELAY_S = 1.05          # the plume's flash, then a beat later the sound
MIR_HOLD_BEATS = 4.0            # *mir*: the held G#
TAIL_S = 14.0                   # after the thunder: Rhen's and Toma's lines, and the drone fading

## MEL_B (hush_theme_v2.py, bars 11-18), (pitch, beats) per line; each line is two 3/4 bars. The last note is *mir*.
VERSE = [
    [("A5", 2), ("G5", .5), ("F5", .5), ("G5", 2), ("D5", 1)],
    [("E5", 1.5), ("F5", .5), ("G5", 1), ("A5", 3)],
    [("F5", 1), ("E5", 1), ("D5", 1), ("D5", 1.5), ("C5", .5), ("B4", 1)],
    [("C5", 1), ("E5", 1), ("G5", 1), ("B4", 2), ("G#4", MIR_HOLD_BEATS)],
]
ANSWER = [("G#4", 1.5), ("A4", 4.5)]


def verse_notes() -> tuple[list[tuple[float, float, float]], float]:
    """[(t, dur, midi)] of the verse from the file start, and MIR_S (the held G#'s onset)."""
    out = []
    t = DRONE_IN
    mir = 0.0
    for li, line in enumerate(VERSE):
        for k, (p, beats) in enumerate(line):
            last = k == len(line) - 1
            d = beats * BEAT * (1.12 if last else 1.0)      # each line leans into its last note
            out.append((t, d, n(p)))
            if li == len(VERSE) - 1 and last:
                mir = t
            t += d
        t += BREATH_S
    return out, mir


def thunder(g, sec: float = 8.0) -> np.ndarray:
    """The plume's thunder near the crown: a crack (broadband, a few tens of ms) high in the plume, then the roll
    down the mountain: rumble bursts at random, ever lower and darker as they come from further down, over a long
    low swell. Stereo (the roll wanders across)."""
    N = int(sec * SR)
    t = np.arange(N) / SR
    out = np.zeros((N, 2))
    k = int(0.05 * SR)
    crack = g.standard_normal(k) * np.exp(-np.arange(k) / (0.012 * SR))
    crack = filt(crack, [bq_highpass(180, 0.7), bq_lowpass(5000, 0.7)])
    out[:k, 0] += 1.4 * crack
    out[:k, 1] += 1.1 * crack
    for _ in range(16):
        at = float(g.uniform(0.04, 5.5)) ** 1.15
        if at > sec - 1.5:
            continue
        dur = float(g.uniform(0.4, 1.4))
        m = int(dur * SR)
        s = int(at * SR)
        cut = 900.0 * np.exp(-at / 1.8) + 140.0
        burst = filt(g.standard_normal(m), [bq_lowpass(cut, 0.7), bq_highpass(28, 0.7)])
        env = np.clip(np.arange(m) / (0.05 * SR), 0, 1) * np.exp(-np.arange(m) / (0.3 * dur * SR))
        amp = float(g.uniform(0.35, 1.0)) * np.exp(-at / 2.6)
        pan = float(g.uniform(-0.7, 0.7))
        e = min(N, s + m)
        seg = burst[: e - s] * env[: e - s] * amp
        out[s:e, 0] += seg * np.cos((pan + 1) * np.pi / 4)
        out[s:e, 1] += seg * np.sin((pan + 1) * np.pi / 4)
    swell = filt(g.standard_normal(N), [bq_lowpass(110, 0.7), bq_highpass(22, 0.7)])
    swell *= np.clip(t / 0.25, 0, 1) * np.exp(-t / 2.4) * (0.7 + 0.3 * smooth_noise(N, 2.0, g))
    out[:, 0] += 0.9 * swell
    out[:, 1] += 0.9 * swell
    fade = int(1.0 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return out


# Bus gains from measured bus loudness (_bus_stats): the vocalise at L over the verse; the drone L-9 as in the first
# verse; the thunder level with the voice over its first 3 s (the mountain answering: felt, not feared).
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    verse, mir = verse_notes()
    thunder_s = mir + THUNDER_DELAY_S
    answer_t = thunder_s + 6.5
    length = thunder_s + TAIL_S
    mx = Mixer(length + 6.0)
    mx.bus("vocalise", 0.0, send=0.40, process=HF.vocalise_bus)
    mx.bus("drone", -4.6, send=0.25, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1500, 0.6)]))
    mx.bus("thunder", 4.2, send=0.22, process=lambda x: filt(x, [bq_highpass(25, 0.7), bq_peak(80, 2.0, 0.8)]))
    mx.add("drone", HF.drone(length - 1.0, rng(SEED + 1)), 0.0)
    for i, (t0, d, m) in enumerate(verse):
        is_mir = i == len(verse) - 1
        x = breath_flute(m, d + 0.06, 0.56 if not is_mir else 0.5, seed=SEED + 31 * i, breath=0.18,
                         scoop_cents=40.0, vib_cents=16.0, vib_rate=5.0, swell=0.22 if d > 1.5 else 0.0, attack=0.14,
                         release=0.9 if is_mir else 0.4, beta=0.5)
        mx.add("vocalise", x, t0 - FLUTE_PRE, pan=-0.05)
    t = answer_t
    for i, (p, beats) in enumerate(ANSWER):
        d = beats * BEAT
        x = breath_flute(n(p), d, 0.3, seed=SEED + 900 + i, breath=0.25, scoop_cents=30.0, vib_cents=14.0,
                         vib_rate=4.8, swell=0.3 if d > 2 else 0.0, attack=0.35, release=1.4)
        mx.add("vocalise", x * 0.45, t - FLUTE_PRE, pan=0.3)
        t += d
    mx.add("thunder", thunder(rng(SEED + 7)), thunder_s)
    hall = ModFDNReverb(rt60=3.4, rt60_high=1.3, predelay=0.035, size=1.2, mod_depth=8.0, mod_rate=0.45,
                        early_level=0.25, lowcut=90.0, seed=SEED % 9973)
    master = mx.render(reverb=hall, reverb_return_db=-2.0)[: int(length * SR)]
    k = int(3.0 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, master, quality=4.0)
    m = measure(master)
    if stats is not None:
        stats["mir_s"] = mir
        stats["thunder_s"] = thunder_s
        stats["bus_lufs"] = _bus_stats(mx, mir, thunder_s)
    if verbose:
        print(f"hush_second_verse: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  mir at {mir:.2f}s  thunder at {thunder_s:.2f}s")
    return m


def _bus_stats(mx: Mixer, mir: float, thunder_s: float) -> dict:
    """Each bus's loudness after its fader: the vocalise and the drone over the verse, the thunder over its 3 s."""
    out = {}
    for b in mx.buses.values():
        x = db_to_lin(b.gain_db) * (b.process(b.buf) if b.process else b.buf)
        a, e = (DRONE_IN, mir + 2.0) if b.name != "thunder" else (thunder_s, thunder_s + 3.0)
        out[b.name] = integrated_lufs(x[int(a * SR): int(e * SR)])
    return out


if __name__ == "__main__":
    st: dict = {}
    render(stats=st)
    print("  buses", {k: round(v, 1) for k, v in st["bus_lufs"].items()})
