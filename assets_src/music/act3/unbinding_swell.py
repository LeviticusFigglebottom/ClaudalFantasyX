"""`unbinding_swell`: Ch21 H09, the Great Unbinding (M5-A3P-1950; act3_ending.md H09; ADR 0208). About 105 s, not
looped.

Original composition for this project (SPEC §2). Its tunes are the game's own, loaded and never retyped:
* the Letting's close (motifs.py `letting_verse()` line 4, *...tash* climbing to the held E6);
* the Hush's first phrase as the first verse is sung (hush_first_verse.py `VERSE`), in Lamptongue (verse 1,
  act3/lamptongue.py), over its own harmony (hush_first_verse.py `LH`, hush_theme_v2's left hand).
The orchestration, the swell and the resolution were written for this cue.

The brief (act3_ending.md H09): "The last *tash*. Every mote in Maresh lifts at once... *Music:* `the_letting`'s last
phrase, then `unbinding_swell`: full choir and orchestra for the only time in the game, and the Hush theme finally
resolves upward." The Hush has always ended hanging on its E (*mir*, stay), the dominant, never coming home. Here,
once, it comes home upward, to A, and in A **major**: the only major tonic the theme is ever given.
* 0–9 s: Asha sings the Letting's close, *...tash* (B5 D6 | E6, held), alone over the C major seventh the_letting
  ends on.
* 9–15 s: the swell. Her E6 passes into the sopranos. The strings climb in octaves under it and a timpani roll
  rises: everything lifts at once.
* 15–38 s: the choir, full, sings the Hush's first phrase in its own words (*Vey ennu, vey ennu...*), three lines,
  on the Hush's own minor harmony. The strings double the sopranos an octave up, the low strings and the timpani take
  each bar's root, and the bells strike the downbeats of each line.
* 38–75 s: the phrase again, everything playing. The fourth line, which has always gone B D | E and stopped, goes
  B D E | A instead. The choir sings *tash* (let go) where the first verse sang *mir* (stay), on an E7 that resolves
  to A major.
* 75–105 s: A major, held. Choir on an open "a", strings in five octaves, the bells ringing it, the glass rising
  over it, then everything thinning upward into the hall until only the high A and E remain.

A minor to A major, 3/4. The sung close at the_letting's 54 BPM; from the swell on, 48 BPM (a bar 3.75 s): broader.

Render:  python3 assets_src/music/act3/unbinding_swell.py   (or tools/audio/render_all.py --only unbinding_swell)
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

import lamptongue as LT  # noqa: E402
from levels import bus_levels  # noqa: E402
from motifs import letting_verse  # noqa: E402
from synth.bells import tower_bell  # noqa: E402
from synth.drums import big_drum  # noqa: E402
from synth.dsp import SR, bq_highpass, bq_lowpass, filt, rng  # noqa: E402
from synth.mixer import Mixer, measure, normalize_integrated, write_ogg  # noqa: E402
from synth.pad import pad_chord, string_body  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.voice import sing  # noqa: E402
from the_letting import BPM as LETTING_BPM, VOICE_PRE, glass  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MUSIC, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FV = _load("hush_first_verse")
OUT = os.path.join(ROOT, "assets", "audio", "act3", "music", "unbinding_swell.ogg")
SEED = 20261032
TARGET_LUFS = -16.0
L_BEAT = 60.0 / LETTING_BPM
BPM = 48.0
BEAT = 60.0 / BPM
BAR = 3 * BEAT
SWELL_AT = 9.0
VERSE_AT = 15.0
SECOND_AT = VERSE_AT + 8 * BAR - 1.5     # the second statement follows the first's three lines and a held bar
HOLD_S = 30.0
# The fourth line resolved upward: the first verse's close (B D | E, on *mir*) goes on up to A, on *tash*.
RESOLVED = [("B4", 1.0), ("D5", 1.0), ("E5", 1.0), ("A5", 3.0)]
RESOLVED_CHORDS = ["E2 B2 A3 D4", "E2 B2 G#3 D4"]     # Esus4 to E7, as the Hush's bars 9-10
A_MAJOR = "A1 A2 E3 A3 C#4 E4 A4 C#5 E5 A5"
# From measured bus loudness (levels.bus_levels): the choir at L, the strings L-3, the voice (her close, alone) L-4,
# the low strings L-6, the timpani L-9, the bells L-10, the glass L-14.
GAINS = {"voice": 10.5, "choir": 0.0, "strings": 21.8, "low": 26.3, "timp": 10.4, "bells": 9.2, "glass": -1.5}


def _voices(lh: str) -> list[float]:
    """A Hush chord (bass, fifth, colour tones) as bass, tenor and alto pitches for the choir."""
    p = [n(x) for x in lh.split()]
    return [float(p[0]), float(p[1] + 12), float(p[3])]


def choir_line(mx, g, notes: list[tuple[float, float, float]], syl: list[tuple[str, str]], vel: float, seed: int,
               singers: int, register: float) -> None:
    """The sopranos: each note one syllable, `singers` voices a little apart."""
    for i, ((t, d, m), s) in enumerate(zip(notes, syl)):
        ph = LT.choir_phonemes([s], [d])
        for c in range(singers):
            y = sing(ph, [(m + float(g.normal(0, 0.04)), d)], vel=vel, seed=seed + 31 * i + c, scale=register,
                     tilt=1.8, breath=0.05, vib_cents=14.0, vib_rate=4.8 + 0.25 * c, release=0.45)
            mx.add("choir", y, t + 0.02 * c + float(g.normal(0, 0.006)), pan=float(np.linspace(-0.45, 0.45, singers)[c]))


def choir_chord(mx, g, t: float, d: float, pitches: list[float], vowel: str, vel: float, seed: int) -> None:
    """Altos, tenors and basses holding a chord on a vowel, three singers a part."""
    for pi, m in enumerate(pitches):
        reg = (1.0, 1.0, 1.12)[min(pi, 2)]
        for c in range(3):
            y = sing([(vowel, d)], [(m + float(g.normal(0, 0.05)), d)], vel=vel, seed=seed + 10 * pi + c, scale=reg,
                     tilt=2.0, breath=0.05, vib_cents=12.0, vib_rate=4.5 + 0.3 * c, release=0.6)
            mx.add("choir", y, t + 0.03 * c, pan=float((-0.5, 0.0, 0.5)[c]) * 0.8)


def statement(mx, g, t0: float, full: bool, seed: int) -> float:
    """The Hush's first phrase sung in Lamptongue from t0; the second, `full`, resolves upward. Returns its end."""
    lines = FV.VERSE[:3] + [RESOLVED if full else FV.VERSE[3]]
    texts = LT.VERSES[1][:3] + (["...tash."] if full else [LT.VERSES[1][3]])
    chords = FV.LH[:6] + (RESOLVED_CHORDS if full else FV.LH[6:8])
    t = t0
    notes, syls = [], []
    for line, text in zip(lines, texts):
        syl = LT.fit(line, LT.line_syllables(text))
        for (p, beats), s in zip(line, syl):
            notes.append((t, beats * BEAT * 0.97, float(n(p))))
            syls.append(s)
            t += beats * BEAT
    choir_line(mx, g, notes, syls, 0.62 if full else 0.55, seed, 5 if full else 4, 1.18)
    for b, lh in enumerate(chords):
        tb = t0 + b * BAR
        vowel = "a" if full else "o"
        choir_chord(mx, g, tb, BAR * 1.01, _voices(lh), vowel, 0.5 if full else 0.45, seed + 400 + 37 * b)
        p = [n(x) for x in lh.split()]
        mx.add("strings", pad_chord([q + 12 for q in p[1:]] + ([p[3] + 24] if full else []), BAR * 1.02,
                                    vel=0.5 if full else 0.42, seed=seed + 700 + b, attack=0.5, release=1.4), tb - 0.1)
        mx.add("low", pad_chord([p[0], p[0] - 12] if full else [p[0]], BAR * 1.02, vel=0.5, seed=seed + 800 + b,
                                attack=0.4, release=1.2, voices=2), tb - 0.05)
        if full or b % 2 == 0:
            mx.add("timp", big_drum(0.55 if full else 0.4, variant=b % 3, seed=seed + 900 + b), tb)
        if b % 2 == 0:
            mx.add("bells", tower_bell(float(p[0] + 24), vel=0.45 if full else 0.35, seed=seed + 950 + b, t60=6.0), tb,
                   pan=0.3 - 0.15 * (b // 2))
    # the sopranos doubled in the violins an octave up, in the full statement
    if full:
        for t, d, m in notes:
            mx.add("strings", pad_chord([m + 12], d, vel=0.38, seed=seed + 1000 + int(t * 10), attack=0.15,
                                        release=0.6, voices=3), t - 0.05)
    return t


def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    g = rng(SEED)
    end_at = SECOND_AT + 8 * BAR
    length = end_at + HOLD_S + 6.0
    mx = Mixer(length)
    G = GAINS
    mx.bus("voice", G["voice"], send=0.38, process=lambda x: filt(x, [bq_highpass(170, 0.7)]))
    mx.bus("choir", G["choir"], send=0.55, process=lambda x: filt(x, [bq_highpass(80, 0.7), bq_lowpass(6000, 0.7)]))
    mx.bus("strings", G["strings"], send=0.5, process=lambda x: string_body(x, cutoff=3200.0))
    mx.bus("low", G["low"], send=0.32, process=lambda x: string_body(x, cutoff=700.0))
    mx.bus("timp", G["timp"], send=0.35, process=lambda x: filt(x, [bq_highpass(30, 0.7), bq_lowpass(2500, 0.7)]))
    mx.bus("bells", G["bells"], send=0.6, process=lambda x: filt(x, [bq_highpass(120, 0.7)]))
    mx.bus("glass", G["glass"], send=0.75)

    # 0-9 s: her close, *...tash*, alone over the_letting's last chord
    close = letting_verse()[3]
    t = 0.4
    for i, (p, beats) in enumerate(close):
        d = beats * L_BEAT if i < len(close) - 1 else SWELL_AT - t + 2.5
        x = LT.vocalise(float(n(p)), d, 0.54, "a", seed=SEED + i, breath=0.16, scoop_cents=25.0, vib_cents=14.0,
                        vib_rate=5.0, swell=0.3 if i == len(close) - 1 else 0.0, attack=0.12, release=1.5, beta=0.5)
        mx.add("voice", x, max(0.0, t - VOICE_PRE), pan=-0.04)
        t += beats * L_BEAT
    mx.add("strings", pad_chord([n(x) for x in "C3 G3 E4 B4".split()], SWELL_AT + 1.0, vel=0.38, seed=SEED + 50,
                                attack=1.5, release=2.0), 0.0)
    # 9-15 s: the swell. Her E6 passes into the sopranos; the strings climb in octaves; the timpani roll rises.
    choir_chord(mx, g, SWELL_AT - 0.5, VERSE_AT - SWELL_AT + 1.0, [float(n("E5")), float(n("A4")), float(n("C4"))],
                "a", 0.5, SEED + 60)
    for k, p in enumerate(["E3", "E4", "E5", "E6"]):
        at = SWELL_AT + 1.2 * k
        mx.add("strings", pad_chord([n(p)], VERSE_AT - at + 0.5, vel=0.36 + 0.04 * k, seed=SEED + 70 + k, attack=1.0,
                                    release=1.2, voices=3), at)
    mx.add("low", pad_chord([n("E2")], VERSE_AT - SWELL_AT + 0.5, vel=0.45, seed=SEED + 80, attack=2.0, release=1.0),
           SWELL_AT)
    roll_t = SWELL_AT + 1.0
    k = 0
    while roll_t < VERSE_AT - 0.1:
        u = (roll_t - SWELL_AT) / (VERSE_AT - SWELL_AT)
        mx.add("timp", big_drum(0.12 + 0.45 * u ** 1.5, variant=k % 3, seed=SEED + 100 + k), roll_t)
        roll_t += 0.11 - 0.03 * u
        k += 1
    # 15-38 s: the first statement, the Hush's own minor; 38-75 s: the second, everything, resolving upward
    statement(mx, g, VERSE_AT, False, SEED + 1000)
    end = statement(mx, g, SECOND_AT, True, SEED + 3000)
    # 75-105 s: A major, held, thinning upward
    pitches = [n(x) for x in A_MAJOR.split()]
    hold_at = end - 3 * BEAT
    choir_chord(mx, g, hold_at, HOLD_S * 0.6, [float(n("A3")), float(n("E4")), float(n("C#5"))], "a", 0.48,
                SEED + 5000)
    for k, m in enumerate(pitches):
        dur = HOLD_S * (1.0 - 0.07 * (len(pitches) - 1 - k))     # the low voices leave first; the top A stays longest
        mx.add("low" if m < 50 else "strings", pad_chord([m], dur, vel=0.45, seed=SEED + 5100 + k, attack=1.0,
                                                         release=3.0, voices=3), hold_at)
    for k, p in enumerate(["A3", "E4", "A4", "C#5"]):
        mx.add("bells", tower_bell(float(n(p)), vel=0.5 - 0.06 * k, seed=SEED + 5200 + k, t60=9.0), hold_at + 0.15 * k,
               pan=-0.3 + 0.2 * k)
    for k, p in enumerate(["A5", "C#6", "E6", "A6"]):
        mx.add("glass", glass(float(n(p)), 8.0, 0.5, SEED + 5300 + k), hold_at + 3.0 + 3.5 * k, pan=0.35 - 0.2 * k)
    mx.add("timp", big_drum(0.6, variant=0, seed=SEED + 5400), hold_at)

    hall = ModFDNReverb(rt60=4.6, rt60_high=1.9, predelay=0.04, size=1.4, mod_depth=9.0, mod_rate=0.35,
                        early_level=0.2, lowcut=70.0, width=0.75, seed=SEED % 9973)
    y = mx.render(reverb=hall, reverb_return_db=-1.5)
    fade = int(3.0 * SR)
    y[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    y = normalize_integrated(y, TARGET_LUFS, ceiling_db=-1.5)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_ogg(out_path, y, quality=3.0)
    m = measure(y)
    if stats is not None:
        stats["bus_lufs"] = bus_levels(mx)
        stats["second_at"] = SECOND_AT
        stats["resolve_at"] = end - 3 * BEAT
    if verbose:
        print(f"unbinding_swell: {m['seconds']:.1f}s  {m['integrated_lufs']:.2f} LUFS  TP {m['true_peak_dbtp']:.2f}"
              f" dBTP  second statement {SECOND_AT:.1f}s, A major at {end - 3 * BEAT:.1f}s")
    return m


if __name__ == "__main__":
    render()
