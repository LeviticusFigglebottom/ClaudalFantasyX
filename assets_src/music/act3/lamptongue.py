"""Lamptongue, sung: the Hush's verses as the score carries them (docs/kb/audio/lamptongue.md; ADR 0208).

The verse texts are lamptongue.md §2's, exactly, and every Act III cue that sings takes them from here. The sheet's
pronunciation rules decide the syllables:
  * every vowel is sounded, so *oan* is o-an and *aun* is a-un;
  * *ennu* is two syllables with a long n (en-nu);
  * *vey*'s y is a glide, not a syllable;
  * a doubled consonant splits between syllables (kar-ra, ar-re).
Each syllable has a vowel and, where it closes on m or n, that nasal coda.

Two ways to sing a line:
  * `vocalise`: Asha's voice until SPEC §16 Q4 settles one (lamptongue.md: "the breath flute shaped by vowels, as
    `hush_first_verse` is"). The breath flute of hush_first_verse, each note through its syllable's vowel formants
    (alto, F1-F3), so the line says its vowels and no synthetic singer stands in for her.
  * `choir_phonemes`: phonemes for `synth.voice.sing` (the procedural formant voices Act II's choirs use), for the
    congregation and the Unbinding's choir: the vowel, then its nasal coda.
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import bq_highpass, bq_lowpass, bq_peak, filt  # noqa: E402
from synth.voice import VOWELS  # noqa: E402
from synth.winds import breath_flute  # noqa: E402

# lamptongue.md §2, line by line (the sheet's spelling and punctuation).
VERSES = {
    1: ["Vey ennu, vey ennu,", "hal oan, ish karra.", "Ennu re, ennu re...", "...mir."],
    2: ["Ish karra, ish karra,", "vey hal ennu,", "re ish, re ish...", "...mir."],
    3: ["Seli arre, seli arre,", "vey karra oan,", "arre re, arre re...", "...mir."],
    4: ["Aun vey, aun vey,", "ish aun ennu,", "vey re, vey re...", "...mir."],
    5: ["Thel ish, thel ish,", "sen karra, sen oan,", "thel re, thel re...", "...mir."],
    6: ["Sev vey, sev vey,", "ish sev ennu,", "ennu sev, ennu sev...", "...mir."],
    7: ["Una kor, una kor,", "vey ish hal oan,", "kor re, kor re...", "...mir."],
    8: ["Ish oan, ish oan,", "vey hal, ennu tash,", "oan re, oan re...", "...tash."],
}
# An alto's formants: the adult table (voice.py) raised by this (a shorter tract).
ALTO = 1.16
_VOWEL = "aeiou"


def words(line: str) -> list[str]:
    return re.findall(r"[a-z]+", line.lower())


def syllables(word: str) -> list[tuple[str, str]]:
    """A word as [(vowel, nasal coda or '')], by lamptongue.md's rules."""
    w = word.lower().replace("y", "")              # vey: the y glides
    out: list[tuple[str, str]] = []
    i = 0
    while i < len(w):
        if w[i] in _VOWEL:
            coda = ""
            j = i + 1
            # the consonants after the vowel, up to the next vowel
            k = j
            while k < len(w) and w[k] not in _VOWEL:
                k += 1
            cons = w[j:k]
            if k == len(w):                          # word-final: all of it closes this syllable
                coda = cons
            elif len(cons) >= 2:                      # split: the first closes this one (en-nu, kar-ra)
                coda = cons[0]
            out.append((w[i], coda[:1] if coda[:1] in "mn" else ""))
            i = j
        else:
            i += 1
    return out


def line_syllables(line: str) -> list[tuple[str, str]]:
    return [s for word in words(line) for s in syllables(word)]


def verse_syllables(verse: int) -> list[list[tuple[str, str]]]:
    return [line_syllables(line) for line in VERSES[verse]]


def fit(notes: list[tuple[str, float]], syl: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """One syllable a note. A line with fewer syllables than notes holds its last syllable over the rest (a melisma:
    *tash* across the last two notes); one with more folds the extra syllables into the last note."""
    if not syl:
        return [("a", "")] * len(notes)
    if len(syl) >= len(notes):
        return syl[: len(notes)]
    return syl + [syl[-1]] * (len(notes) - len(syl))


def vowel_filter(x: np.ndarray, vowel: str) -> np.ndarray:
    """The breath flute through an alto's vowel: its first three formants as peaks (hush_first_verse's 'ah' chain,
    generalised)."""
    (f1, f2, f3, *_), _bw = VOWELS[vowel]
    return filt(x, [bq_highpass(160, 0.7), bq_peak(f1 * ALTO, 7.0, 3.0), bq_peak(f2 * ALTO, 5.0, 3.5),
                    bq_peak(f3 * ALTO, 4.0, 4.0), bq_peak(3300, -4.0, 1.0), bq_lowpass(5200, 0.7)])


def vocalise(m: float, dur: float, vel: float, vowel: str, seed: int, coda: str = "", **kw) -> np.ndarray:
    """One sung note of Asha's line: the breath flute on `vowel`, a nasal coda darkening its tail."""
    x = breath_flute(m, dur, vel, seed=seed, **kw)
    y = vowel_filter(x, vowel)
    if coda in ("m", "n"):
        # the mouth closes for the last fifth of the note: the upper spectrum damps toward the nasal's dark
        n = len(y)
        k = int(min(n, dur * 0.8 * 44100))
        dark = filt(x, [bq_highpass(160, 0.7), bq_peak(260 * ALTO, 6.0, 2.0), bq_lowpass(1400, 0.7)])
        w = np.zeros(n)
        w[k:] = np.linspace(0.0, 1.0, n - k) if n > k else 0.0
        y = y * (1 - w) + dark * w * 0.8
    return y


def choir_phonemes(syl: list[tuple[str, str]], durs: list[float]) -> list[tuple[str, float]]:
    """[(phoneme, seconds)] for synth.voice.sing: each syllable's vowel, and its nasal coda in the note's last 20 %."""
    out: list[tuple[str, float]] = []
    for (v, coda), d in zip(syl, durs):
        if coda in ("m", "n"):
            out += [(v, d * 0.8), (coda, d * 0.2)]
        else:
            out.append((v, d))
    return out
