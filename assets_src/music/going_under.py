"""`going_under`: Ch1 C1-15 "Cutscene: Going under" (M3-AUD-819; act1_ch01.md §6), ~30 s, through-composed.

Original material (SPEC §2): the tune is Dace's current-song as written once in motifs.py (CURRENT_SONG, all three
phrases), our own working chart in D dorian, composed for this project and not derived from any existing melody.
This file performs it and never re-types its notes. It is not the Hush (hush_first_verse.py opens on a falling
E-D-C-A in A minor); the two must stay two songs when act3 E2 sets them side by side.

The brief: "Cutscene score. Underwater roar falling away to near silence; then the current-song sung WHOLE by a
distant male voice (until SPEC §16 Q4/Q5 settle a voice, a vocalise-like solo instrument carries it, as
`hush_first_verse` does), very far down, and nothing else. Ends in silence." In C1-06 Rhen only hummed phrase 1
(`rhen_current_hum`); here, for the first time, the player hears the whole chart, from below him. The song leads
nowhere and nothing comes toward him (ADR 0017, ADR 0022): so it never swells, never rises to meet him, and stops.

Layers (all synthesized; no samples):
* **the roar** (U10): the storm heard from under the surface, a low churning noise band with turbulent swells and
  a sub-bass pressure, loud at the cut and falling away (its band sinking as it fades) to near silence by the time
  the camera looks down (U11);
* **the song** (U11): the vocalise-like instrument of hush_first_verse (the breath flute shaped by an open "ah",
  `vocalise_bus`), at the motif's written pitch (D4-C5, a man's singing range), a little slower than Rhen's hum (66
  BPM: sung, not hummed), legato, slow vibrato, a breath after each phrase. "Very far down": it is heard almost
  only through the water and its own long dark reverb, the top of it gone (low-passed near 1.3 kHz), the dry sound
  far under the wet.
Nothing else: no drone, no pad, no motes. After the last D the reverb dies to digital silence.

Form: 0-7 s the roar falls away | ~6.2 s the song begins: phrase 1 (sound, sound, the set rising), phrase 2 (over the
shoal and along), phrase 3 (sound again, and home to D), the last D held | the tail into silence. render() prints
the last note's onset: the beats doc asks for the cut to black on it (see listening_notes.md "going_under").

Render:  python3 assets_src/music/going_under.py   (or tools/audio/render_all.py --only going_under)
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from motifs import phrases_in_seconds  # noqa: E402
from synth.dsp import SR, bq_bandpass, bq_highpass, bq_lowpass, filt, rng, smooth_noise  # noqa: E402
from synth.loudness import integrated_lufs  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

_spec = importlib.util.spec_from_file_location("hush_first_verse", os.path.join(HERE, "hush_first_verse.py"))
HFV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(HFV)

OUT = os.path.join(ROOT, "assets", "audio", "music", "going_under.ogg")
SEED = 20261820
TARGET_LUFS = -16.0
SONG_BPM = 66.0
SONG_T0 = 6.2              # the song starts as the camera looks down (U11: the fade in 1.5 s + the wait 4.0 s)
BREATH_S = 0.85            # the singer's breath after each phrase
ROAR_S = 9.0               # the roar's length (it is near silence from ~7 s)
FLUTE_PRE = 0.065          # breath_flute speaks this late


def song_notes() -> list[tuple[float, float, float]]:
    """[(t, dur, midi)] of the whole current-song from SONG_T0 (motifs.phrases_in_seconds at SONG_BPM)."""
    out, t = [], SONG_T0
    for pi, phrase in enumerate(phrases_in_seconds(SONG_BPM)):
        for k, (m, d) in enumerate(phrase):
            last = k == len(phrase) - 1
            dur = d * (1.12 if last else 1.0) * (1.1 if (last and pi == 2) else 1.0)   # each phrase leans into its end
            out.append((t, dur, m))
            t += dur
        t += BREATH_S
    return out


def roar(g, sr: int = SR) -> np.ndarray:
    """The storm from under the surface: churning low noise and a sub pressure, falling away and sinking."""
    N = int(ROAR_S * sr)
    t = np.arange(N) / sr
    fall = np.where(t < 1.2, 1.0, np.exp(-(t - 1.2) / 1.35))          # holds at the cut, then falls away
    fall *= np.clip((ROAR_S - t) / 1.5, 0, 1) ** 2
    out = np.zeros((N, 2))
    hop = int(0.25 * sr)
    for ch in range(2):
        noise = g.standard_normal(N)
        churn = 0.55 + 0.45 * np.clip(smooth_noise(N, 1.3, g, sr), -1, 1)   # turbulent swells
        y = np.zeros(N)
        for i in range(0, N, hop):                                       # the band sinks as it fades
            c = 520.0 * (0.35 + 0.65 * fall[min(N - 1, i)]) + 60.0
            a = max(0, i - hop)
            seg = noise[a: min(N, i + 2 * hop)]
            z = filt(seg, [bq_lowpass(c, 0.7, sr), bq_highpass(35.0, 0.7, sr)], sr=sr)
            y[a: a + len(z)] += z * np.hanning(len(z)) * 0.5
        hiss = filt(noise[::-1].copy(), [bq_bandpass(1400.0, 0.6, sr)], sr=sr) * 0.06 * fall ** 2   # bubbles, churned
        out[:, ch] = (y / (np.std(y) + 1e-9) * churn + hiss) * fall
    sub = np.sin(2 * np.pi * (31.0 + 6.0 * smooth_noise(N, 0.4, g, sr)) * t)
    out += (0.8 * sub * fall ** 1.5)[:, None]
    return out * 0.05


def far_down(x: np.ndarray) -> np.ndarray:
    """The vocalise's 'ah', then the water: the top gone, a little of the low end too (it is far below)."""
    return filt(HFV.vocalise_bus(x), [bq_highpass(220.0, 0.7), bq_lowpass(1300.0, 0.7)])


## Bus gains (dB), set from measured bus loudness (render(stats=...)["bus_lufs"]): the song at L, the roar L+7 over
## its own seconds (in the decoded file the cut is about 4 LU over the song, and it falls away from there).
GAINS = {"song": 0.0, "roar": 4.0}


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    notes = song_notes()
    end = notes[-1][0] + notes[-1][1]
    mx = Mixer(end + 9.0)
    mx.bus("song", GAINS["song"], send=0.85, process=far_down)
    mx.bus("roar", GAINS["roar"], send=0.15, process=lambda x: filt(x, [bq_lowpass(900.0, 0.6)]))
    mx.add("roar", roar(rng(SEED + 1)), 0.0)
    for i, (t0, d, m) in enumerate(notes):
        x = breath_flute(m, d + 0.06, 0.46 * float(g.uniform(0.96, 1.03)), seed=SEED + 31 * i, breath=0.22,
                         scoop_cents=30.0, vib_cents=14.0, vib_rate=4.7, swell=0.15 if d > 1.2 else 0.0,
                         attack=0.16, release=0.45, beta=0.5)
        mx.add("song", x * 0.35, t0 - FLUTE_PRE, pan=0.0)                # the dry sound, far under the wet
    deep = ModFDNReverb(rt60=5.5, rt60_high=0.9, predelay=0.06, size=1.5, mod_depth=11.0, mod_rate=0.3,
                        early_level=0.12, lowcut=110.0, seed=SEED % 9973)
    bus_lufs = {name: integrated_lufs((b.process(b.buf) if b.process else b.buf) * 10 ** (b.gain_db / 20))
                for name, b in mx.buses.items()}
    master = mx.render(reverb=deep, reverb_return_db=0.0)
    env = np.abs(master).max(axis=1)
    last = int(np.nonzero(env > 10 ** (-70 / 20))[0][-1]) + int(0.2 * SR)
    master = master[: min(last, len(master))]
    k = int(2.0 * SR)
    master[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
    master = normalize_integrated(master, TARGET_LUFS, ceiling_db=-2.0)
    write_ogg(out_path, master, quality=3.0)
    m = measure(master)
    if stats is not None:
        stats["bus_lufs"] = bus_lufs
        stats["last_note_s"] = notes[-1][0]
        stats["song_end_s"] = end
    if verbose:
        print(f"going_under: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP"
              f"  song {SONG_T0:.1f}-{end:.2f}s, last note at {notes[-1][0]:.2f}s")
        print("  buses (LU vs the song)", {k: round(v - bus_lufs["song"], 1) for k, v in bus_lufs.items()})
    return m


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT)
