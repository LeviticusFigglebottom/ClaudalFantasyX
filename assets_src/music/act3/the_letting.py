"""`the_letting` and `the_letting_release`: Ch21 H07–H08, the Eighth Verse sung (M5-A3P-1950; act3_ending.md H07, H08;
docs/kb/audio/lamptongue.md verse 8; ADR 0208).

Original composition for this project (SPEC §2). The tune is the game's own and is loaded, never retyped:
motifs.py `letting_verse()`, the first verse turned upward line by line, with its close climbing to the held E6 on
*tash*. The text is lamptongue.md's verse 8, from act3/lamptongue.py: *Ish oan, ish oan, / vey hal, ennu tash, /
oan re, oan re... / ...tash.* The harmony, the counter-lines and the arrangement were written for this cue.

The brief (act3_ending.md H07): "Asha steps off the battle timeline and sings the Eighth Verse... her voice is the
music, and the score follows her. Over the countdown the palette rotates from cool held to warm released... The verse
ends on *tash* (let go)." H08: "`the_letting` thinning to a single held note."

**the_letting** (a loop, 16 bars of 3/4 at 54 BPM, about 53 s; it plays under Sefir's third phase for as long as the
countdown runs):
* Asha's voice leads throughout: the vocalise (lamptongue.vocalise, the breath flute through each syllable's vowel)
  sings the whole verse twice, a breath before each line.
* The score follows her. Pass 1 (bars 1–8) is cool and held: an A drone and strings close under her, in the Hush's
  minor. Pass 2 (bars 9–16) warms: the strings open upward, a hummed choir (the formant voices) doubles her an
  octave below on the same Lamptongue, and a glass line rises against each held note like the motes.
* The harmony leans out of A minor toward C major on every *tash*: Am | Em7 | Fmaj7 | Am/C | Dm7 | G | G/B | Cmaj7.
  Each pass ends on a C major seventh under the held E6, open and bright; the loop's return to the A drone is the
  verse beginning again.
* There is no percussion. The countdown is the fight's, and the voice is the music.

**the_letting_release** (about 22 s, the cue's `release`: silencing `the_letting` plays it): H08, Sefir lets go. The
voice holds the last *tash* on E6. Under it the strings thin one voice at a time, top to bottom, until only the E is
left, held in the violins and the voice together, and then that goes too.

Render:  python3 assets_src/music/act3/the_letting.py   (both files; or tools/audio/render_all.py --only the_letting)
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(MUSIC, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))
sys.path.insert(0, MUSIC)
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import lamptongue as LT  # noqa: E402
from motifs import letting_verse  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, midi_to_hz, rng  # noqa: E402
from synth.looping import LoopMixer, master_loop, write_loop_sidecar  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import sing  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "audio", "act3", "music")
OUT = os.path.join(OUT_DIR, "the_letting.ogg")
OUT_RELEASE = os.path.join(OUT_DIR, "the_letting_release.ogg")
SEED = 20261030
TARGET_LUFS = -16.0
BPM = 54.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
BARS = 16
LOOP_S = BARS * BAR
BREATH_S = 0.28             # the singer's breath, taken from the end of each line's last note
VOICE_PRE = 0.065           # the breath flute's breath leads its tone
# One chord a bar per pass (A minor leaning to C major on every tash), as voicings for the strings.
CHORDS = ["A3 C4 E4 B4", "E3 G3 D4 B4", "F3 A3 E4 C5", "C3 E3 A3 G4", "D3 F3 C4 A4", "G3 B3 D4 A4", "B2 G3 D4 B4",
          "C3 G3 E4 B4"]
# Pass 2's strings open upward: the same chords with a high voice added.
OPEN = ["E5", "B4", "C5", "E5", "F5", "B5", "D5", "G5"]
ROOTS = ["A1", "E2", "F1", "C2", "D2", "G1", "B1", "C2"]
# Bus gains from measured bus loudness (render(stats=...)): the voice at L, the strings L-8, the choir L-4 (in pass 2),
# the glass L-11, the drone and the opened strings L-12, the root L-14.
GAINS = {"voice": 0.0, "strings": 5.0, "open": 3.0, "drone": -12.0, "root": 5.0, "choir": -12.5, "glass": -16.3}


def verse_events(t0: float) -> list[tuple[float, float, float, str, str]]:
    """[(t, dur, midi, vowel, coda)] of one sung verse from t0: each line two bars, a breath before the next."""
    out = []
    t = t0
    for line, text in zip(letting_verse(), LT.VERSES[8]):
        syl = LT.fit(line, LT.line_syllables(text))
        for k, ((p, beats), (v, coda)) in enumerate(zip(line, syl)):
            d = beats * BEAT
            if k == len(line) - 1:
                d -= BREATH_S
            out.append((t, d, float(n(p)), v, coda))
            t += beats * BEAT
    return out


def glass(m: float, dur: float, vel: float, seed: int) -> np.ndarray:
    """A rubbed glass rim: near-pure partials, slow bloom, a little beating (the motes rising)."""
    g = rng(seed)
    N = int((dur + 1.5) * SR)
    t = np.arange(N) / SR
    f0 = midi_to_hz(m)
    x = np.zeros(N)
    for k, a in ((1, 1.0), (2.01, 0.25), (3.02, 0.08)):
        x += a * np.sin(2 * np.pi * f0 * k * t + g.uniform(0, 6.28)) * (1 + 0.04 * np.sin(2 * np.pi * 0.9 * k * t))
    env = np.clip(t / 0.5, 0, 1) ** 2 * np.exp(-np.clip(t - dur, 0, None) / 0.5)
    return vel * 0.3 * x * env


def _voice_bus(x: np.ndarray) -> np.ndarray:
    return filt(x, [bq_highpass(170, 0.7)])


def _strings(x: np.ndarray) -> np.ndarray:
    return string_body(x, cutoff=2400.0)


def build(mx, g, passes: int = 2) -> None:
    """Both passes of the verse and the score under them."""
    for p in range(passes):
        t0 = p * 8 * BAR
        warm = p == 1
        for i, (t, d, m, v, coda) in enumerate(verse_events(t0)):
            x = LT.vocalise(m, d + 0.06, 0.52 if not warm else 0.56, v, seed=SEED + 97 * p + i, coda=coda,
                            breath=0.16, scoop_cents=30.0, vib_cents=15.0, vib_rate=5.0,
                            swell=0.25 if d > 1.5 else 0.0, attack=0.12, release=0.45, beta=0.5)
            mx.add("voice", x, t - VOICE_PRE, pan=-0.04)
            if warm:
                # the choir hums her line an octave below, in her own words
                ph = LT.choir_phonemes([(v, coda)], [d])
                for c in range(3):
                    y = sing(ph, [(m - 12 + float(g.normal(0, 0.05)), d)], vel=0.5, seed=SEED + 500 + 13 * i + c,
                             scale=1.0 + 0.05 * c, tilt=2.0, breath=0.05, vib_cents=12.0, vib_rate=4.6 + 0.3 * c,
                             release=0.4)
                    mx.add("choir", y, t + 0.03 * c, pan=(-0.35, 0.0, 0.35)[c])
                if d > 1.5:
                    # a glass note rises a third above each held note, the motes going up
                    for k, step in enumerate((3, 7)):
                        mx.add("glass", glass(m + step + 12, d * 0.6, 0.6, SEED + 900 + 7 * i + k),
                               t + 0.35 + 0.4 * k, pan=0.4 - 0.25 * k)
        for b in range(8):
            tb = t0 + b * BAR
            notes = [n(x) for x in CHORDS[b].split()]
            mx.add("strings", pad_chord(notes, BAR * 1.02, vel=0.42 if not warm else 0.5, seed=SEED + 40 * p + b,
                                        attack=0.9, release=1.6), tb - 0.15)
            if warm:
                mx.add("open", pad_chord([n(OPEN[b])], BAR * 1.02, vel=0.4, seed=SEED + 300 + b, attack=1.1,
                                         release=1.6), tb - 0.1)
            mx.add("root", pad_chord([n(ROOTS[b])], BAR * 1.02, vel=0.45, seed=SEED + 600 + 40 * p + b, attack=0.8,
                                     release=1.4, voices=2), tb - 0.1)


def drone(length: float, seed: int) -> np.ndarray:
    """The A drone under the whole verse (A2, E3), breathing slowly."""
    g = rng(seed)
    N = int(length * SR)
    t = np.arange(N) / SR
    y = np.zeros((N, 2))
    for m, a in ((45, 1.0), (52, 0.6), (57, 0.25)):
        for c in range(2):
            ph = g.uniform(0, 6.28)
            y[:, c] += a * np.sin(2 * np.pi * midi_to_hz(m + g.normal(0, 0.04)) * t + ph)
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * t / (LOOP_S / 3.0))
    return 0.12 * y * lfo[:, None]


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    mx = LoopMixer(intro_s=0.0, loop_s=LOOP_S, preroll_s=8.0)
    G = GAINS
    mx.bus("voice", G["voice"], send=0.36, process=_voice_bus)
    mx.bus("strings", G["strings"], send=0.5, process=_strings)
    mx.bus("open", G["open"], send=0.55, process=_strings)
    mx.bus("root", G["root"], send=0.3, process=lambda x: string_body(x, cutoff=700.0))
    mx.bus("drone", G["drone"], send=0.2, process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1200, 0.6)]))
    mx.bus("choir", G["choir"], send=0.6, process=lambda x: filt(x, [bq_highpass(110, 0.7), bq_lowpass(3800, 0.7)]))
    mx.bus("glass", G["glass"], send=0.7)
    build(mx, g)
    mx.add("drone", drone(LOOP_S + 2.0, SEED + 1), -1.0)
    hall = ModFDNReverb(rt60=3.6, rt60_high=1.5, predelay=0.035, size=1.25, mod_depth=9.0, mod_rate=0.4,
                        early_level=0.22, lowcut=90.0, width=0.75, seed=SEED % 9973, loop_period=LOOP_S)
    _, loop = mx.render(reverb=hall, reverb_return_db=-2.0)
    rep: dict = {}
    _, loop = master_loop(np.zeros((0, 2)), loop, TARGET_LUFS, ceiling_db=-2.0, report=rep)
    L = len(loop)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, loop, quality=3.0, tags={"LOOPSTART": "0", "LOOPLENGTH": str(L)})
    write_loop_sidecar(os.path.splitext(out_path)[0] + ".loop.json", SR, 0, L, BPM, 3)
    m = measure(loop)
    if stats is not None:
        stats["bus_lufs"] = dict(mx.bus_lufs)
    if verbose:
        print(f"the_letting: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f} dBTP")
    render_release(os.path.join(os.path.dirname(out_path), os.path.basename(OUT_RELEASE)), verbose=verbose)
    return m


def render_release(out_path: str = OUT_RELEASE, verbose: bool = True) -> dict:
    """H08: the last *tash* held on E6 while the strings thin to the E alone, then nothing."""
    hold = 14.0
    length = hold + 8.0
    mx = Mixer(length)
    mx.bus("voice", GAINS["voice"], send=0.42, process=_voice_bus)
    mx.bus("strings", GAINS["strings"] + 1.0, send=0.55, process=_strings)
    mx.bus("drone", GAINS["drone"] - 2.0, send=0.25,
           process=lambda x: filt(x, [bq_highpass(35, 0.7), bq_lowpass(1000, 0.6)]))
    x = LT.vocalise(float(n("E6")), hold, 0.5, "a", seed=SEED + 4000, breath=0.2, scoop_cents=10.0, vib_cents=12.0,
                    vib_rate=4.8, swell=0.15, attack=0.3, release=2.5, beta=0.5)
    mx.add("voice", x, 0.0, pan=-0.04)
    # Cmaj7 under the E: B, G, C, then the low C leave in turn, top to bottom, and the violins' E stays with her
    leave = [("B4", 2.5), ("G4", 5.0), ("C4", 7.5), ("C3", 9.5)]
    for k, (p, at) in enumerate(leave):
        mx.add("strings", pad_chord([n(p)], at, vel=0.42, seed=SEED + 4100 + k, attack=0.3, release=2.2), 0.0)
    mx.add("strings", pad_chord([n("E5"), n("E6")], hold, vel=0.38, seed=SEED + 4200, attack=0.3, release=3.0), 0.0)
    mx.add("drone", drone(9.0, SEED + 4300), 0.0)
    hall = ModFDNReverb(rt60=4.0, rt60_high=1.6, predelay=0.035, size=1.3, mod_depth=9.0, mod_rate=0.4,
                        early_level=0.22, lowcut=90.0, width=0.75, seed=SEED % 9973 + 1)
    y = mx.render(reverb=hall, reverb_return_db=-2.0)
    fade = int(1.5 * SR)
    y[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-2.0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, y, quality=3.0)
    m = measure(y)
    if verbose:
        print(f"the_letting_release: {m['seconds']:.2f}s  {m['integrated_lufs']:.2f} LUFS"
              f"  TP {m['true_peak_dbtp']:.2f} dBTP")
    return m


if __name__ == "__main__":
    render()
