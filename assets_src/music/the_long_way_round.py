"""`the_long_way_round`: Ch4 C4-04/C4-05, "The Long Way Round" (M3-AUD-820; act1_ch04.md §6), ~80 s, through-composed.

Original composition for this project (SPEC §2): the tune, its harmony parts and the form below were written for
this cue, to Narrative's lyric (game/data/dialogue/ch04/ch04_shell_is_set.dlg, the #sung lines ch04_shell_012-015 and
021). It is a plain folk tune in the style of a slow seafarers' farewell; it quotes and derives from no existing song,
shanty or hymn, and shares no phrase with the game's own tunes (the Hush falls E-D-C-A in A minor; Haluna's cell
circles F#-E-D-E; Dace's current-song strikes repeated soundings in D dorian).

The brief: the Low Reaches farewell for a voyage, the song you sing so a sailor comes back the long way, safe. The
whole village sings it, unaccompanied, for Asha at her wake, and everyone singing knows she isn't coming back. Plain
and singable, **in a major mode that makes it worse**. Until SPEC §16 Q4/Q5 settle voices, a small ensemble of solo
instruments carries it, as hush_first_verse's vocalise does: breath flutes shaped by sung vowels. No chords, no
drone, no percussion: only lines, the way a village sings.

F major, 4/4 at 88 BPM, each sung line four bars (with a breath and a pickup), every stressed syllable on beat 1 or 3:

    Bring her | ROUND by the LONG way, by the | REEF and the WEED and the | LIGHT ...      (012: an open cadence)
    Bring her | ROUND by the LONG way, and the | TIDE will BRING her | HOME by NIGHT ...   (013: home, to F)
              | DON'T go the SHORT way | O-ver, where the | DEEP is COLD and | WIDE ...    (014: the high line)
    come      | ROUND the LONG way, | LOVE, ... come | ROUND the LONG way, on the | TIDE    (015: the top, F)

The first two lines share their first bar (a folk tune's repeat). Line 014 climbs to the tune's top (G5 on "short")
and hangs on the second degree over C ("wide"); line 015 reaches **G5 on "love"**, the song's one long high note,
over B-flat (the warm sixth, the major-mode ache), then walks down to F on "tide". The parts are written in D in the
data below, and `KEY` moves them up a minor third, into the flutes' best range.

Voices (all synthesized breath flutes; no samples, no synthetic singer):
* **the lead** ("ah", alto formants, as hush_first_verse.vocalise_bus): one voice alone for 012 (Osu starts it), the
  whole song;
* **the village**: from 013 a second voice on the tune, a few cents and a few ms apart (many people on one line);
* **the women's harmony** ("oh"): from 013, a third or sixth under the tune in long notes;
* **the men** ("oo", low): from 014, the roots in half notes.

Form (bars; bar 0 is the pickup bar):
0-4 012, the lead alone | 5-8 013, the village joins | 9-12 014, the men join | 13-16 015, the full song, the swell
on "love" | 17-20 014 again, softly (under Rhen's lines to Toma; no caption) | 21-24 021 (= 015's words), Asha's
face, the song full but soft | 25-26 the tag: "come round the long way, on the tide" once more, slower, the lead and
the men only, the last note held | a breath of hall.

**markers** (seconds from the cue's first sample, where each sung line's first syllable starts; Cinematics paces
`@wait music=<marker>` on these; `markers()` computes them and render() prints them):
    ch04_shell_012   2.20    ch04_shell_013  13.25    ch04_shell_014  25.08    ch04_shell_015  35.79
    verse_repeat    47.28    ch04_shell_021  57.99    tag             69.16    end             78.18
("verse_repeat" is the uncaptioned 014 repeat under Rhen's lines; "tag" is the uncaptioned last half-line; "end" is
where the last held note is released; the file runs on 2 s more into the hall.)

Render:  python3 assets_src/music/the_long_way_round.py   (or tools/audio/render_all.py --only the_long_way_round)
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

import numpy as np  # noqa: E402

from synth.dsp import bq_highpass, bq_lowpass, bq_peak, filt, rng  # noqa: E402
from synth.mixer import Mixer  # noqa: E402
from synth.reverb import ModFDNReverb  # noqa: E402
from synth.score import n  # noqa: E402
from synth.winds import breath_flute  # noqa: E402


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HFV = _mod("hush_first_verse")
HUSH = _mod("hush_theme_v2")

OUT = os.path.join(ROOT, "assets", "audio", "music", "the_long_way_round.ogg")
SEED = 20261420
BPM = 88.0
BEAT = 60.0 / BPM
T0 = 2.2                # the first sung syllable ("Bring", beat 3 of bar 0), after the script's 2 s fade-in
FLUTE_PRE = 0.065
KEY = 3                 # the parts are written in D below and sung a minor third up, in F major
# Bars stretch a little where a line ends (the singers lean on the held note and breathe) and broaden in the tag.
STRETCH = {4: 1.07, 8: 1.07, 12: 1.06, 16: 1.08, 20: 1.06, 24: 1.10, 25: 1.22, 26: 1.45}

# The tune, per line: one list per bar of (pitch | None, beats, syllable). Bar 0's pickup and every line's pickup
# sit at the end of the bar before it.
PICK_BRING = [("A3", 0.5, "Bring"), ("D4", 0.5, "her")]
PICK_COME = [("A4", 0.5, "come")]
BAR_ROUND = [("F#4", 1.5, "round"), ("E4", .25, "by"), ("D4", .25, "the"), ("A4", 1, "long"), ("B4", .5, "way,"),
             ("A4", .25, "by"), ("B4", .25, "the")]
L012 = [BAR_ROUND,
        [("D5", 1, "reef"), ("C#5", .5, "and"), ("B4", .5, "the"), ("A4", 1, "weed"), ("F#4", .5, "and"),
         ("G4", .5, "the")],
        [("A4", 4, "light.")],
        [("A4", 2, "-"), (None, 1, "")] + PICK_BRING]
L013 = [[*BAR_ROUND[:5], ("A4", .25, "and"), ("B4", .25, "the")],
        [("D5", 1, "tide"), ("C#5", 1, "will"), ("B4", 1, "bring"), ("A4", 1, "her")],
        [("F#4", 1.5, "home"), ("E4", .5, "by"), ("D4", 2, "night.")],
        [("D4", 2, "-"), (None, 2, "")]]
L014 = [[("D5", 1, "Don't"), ("C#5", .5, "go"), ("B4", .5, "the"), ("E5", 1.5, "short"), ("D5", .5, "way")],
        [("B4", 1.5, "o-"), ("A4", 1.5, "ver,"), ("F#4", .5, "where"), ("G4", .5, "the")],
        [("B4", 1, "deep"), ("A4", 1, "is"), ("G4", 1, "cold"), ("F#4", 1, "and")],
        [("E4", 3, "wide."), (None, .5, "")] + PICK_COME]
L015 = [[("D5", 1.5, "round"), ("C#5", .5, "the"), ("B4", 1, "long"), ("A4", 1, "way,")],
        [("E5", 3, "love,"), (None, .5, "")] + PICK_COME,
        [("F#4", 1.5, "round"), ("E4", .5, "the"), ("A4", 1, "long"), ("G4", .5, "way,"), ("F#4", .25, "on"),
         ("E4", .25, "the")],
        [("D4", 4, "tide.")]]
# The tag ends 021 differently: its last bar leaves room for the pickup, and the tag holds "tide".
L021 = L015[:3] + [[("D4", 3.5, "tide."), ("A4", .5, "come")]]
TAG = [L015[2], [("D4", 6, "tide.")]]

# The women's harmony ("oh"): long notes a third or sixth under the tune; the men ("oo"): roots in half notes.
ALTO_013 = [[("D4", 2), ("F#4", 2)], [("B4", 1), ("A4", 1), ("G4", 1), ("E4", 1)],
            [("D4", 1.5), ("C#4", .5), ("D4", 2)],
            [("D4", 2), (None, 2)]]
ALTO_014 = [[("F#4", 2), ("G4", 2)], [("D4", 2), ("F#4", 2)], [("G4", 2), ("D4", 2)], [("C#4", 3), (None, 1)]]
ALTO_015 = [[("F#4", 2), ("D4", 2)], [("B4", 3), (None, 1)], [("D4", 2), ("C#4", 2)], [("A3", 4)]]
BASS_014 = [[("B3", 2), ("E3", 2)], [("G3", 2), ("D3", 2)], [("E3", 2), ("D3", 2)], [("A3", 3), (None, 1)]]
BASS_015 = [[("D3", 2), ("B3", 2)], [("G3", 3), (None, 1)], [("D3", 2), ("A3", 2)], [("D3", 4)]]
BASS_TAG = [[("D3", 2), ("A3", 2)], [("D3", 6)]]
LYRIC = {
    "ch04_shell_012": "Bring her round by the long way, by the reef and the weed and the light.",
    "ch04_shell_013": "Bring her round by the long way, and the tide will bring her home by night.",
    "ch04_shell_014": "Don't go the short way over, where the deep is cold and wide.",
    "ch04_shell_015": "Come round the long way, love, come round the long way, on the tide.",
}


def bar_start(bar: int) -> float:
    """Start (s) of bar `bar` (bar 0 is the pickup bar: it starts three beats before T0's 'Bring')."""
    t = T0 - 3.0 * BEAT
    for b in range(bar):
        t += 4 * BEAT * STRETCH.get(b, 1.0)
    return t


def t_of(bar: int, beat: float) -> float:
    return bar_start(bar) + beat * BEAT * STRETCH.get(bar, 1.0)


def markers() -> dict[str, float]:
    """Where each sung line's first syllable starts (s)."""
    return {"ch04_shell_012": t_of(0, 3.0), "ch04_shell_013": t_of(4, 3.0), "ch04_shell_014": t_of(9, 0.0),
            "ch04_shell_015": t_of(12, 3.5), "verse_repeat": t_of(17, 0.0), "ch04_shell_021": t_of(20, 3.5),
            "tag": t_of(24, 3.5), "end": t_of(27, 2.0)}


def check_lyric() -> None:
    """Every #sung line gets one note per syllable (hyphenated syllables count once each)."""
    def count(text: str) -> int:        # every word is one syllable but "over"
        return len(text.split()) + text.count("over")
    tune = {"ch04_shell_012": PICK_BRING + [x for b in L012[:3] for x in b],
            "ch04_shell_013": PICK_BRING + [x for b in L013[:3] for x in b],
            "ch04_shell_014": [x for b in L014[:3] for x in b] + L014[3][:1],
            "ch04_shell_015": PICK_COME + [x for b in L015[:2] for x in b] + [x for b in L015[2:] for x in b]}
    for key, notes in tune.items():
        sung = [s for p, _, s in notes if p is not None and s not in ("-",)]
        assert len(sung) == count(LYRIC[key]), (key, sung)


def _notes(bars: list, start_bar: int, offset_beats: float = 0.0) -> list[tuple[float, float, float, str]]:
    """[(t, dur, midi, syllable)] for a part written as bars, starting at `start_bar` (+ offset beats)."""
    out = []
    bar, beat = start_bar, offset_beats
    for b in bars:
        for item in b:
            p, beats = item[0], item[1]
            if p is not None:
                t0 = t_of(bar, beat)
                end_bar, end_beat = bar, beat + beats
                while end_beat > 4.0 + 1e-9:
                    end_beat -= 4.0
                    end_bar += 1
                out.append((t0, t_of(end_bar, end_beat) - t0, n(p) + KEY, item[2] if len(item) > 2 else ""))
            beat += beats
            while beat >= 4.0 - 1e-9:
                beat -= 4.0
                bar += 1
    return out


def _merge_held(notes: list) -> list:
    """A '-' syllable continues the note before it (a held note across a barline)."""
    out = []
    for t, d, m, s in notes:
        if s == "-" and out and abs(out[-1][2] - m) < 1e-6:
            pt, pd, pm, ps = out[-1]
            out[-1] = (pt, t + d - pt, pm, ps)
        else:
            out.append((t, d, m, s))
    return out


def tune() -> list[tuple[float, float, float, str]]:
    """The whole sung line, in order: 012 (from bar 0's pickup), 013, 014, 015, 014 again, 021, the tag."""
    parts = [(0, 3.0, [PICK_BRING] + L012), (5, 0.0, L013), (9, 0.0, L014), (13, 0.0, L015), (17, 0.0, L014),
             (21, 0.0, L021), (25, 0.0, TAG)]
    out = []
    for bar, beat, bars in parts:
        out += _notes(bars, bar, beat)
    # 015's pickup is in L014's last bar, so the 014 repeat's pickup leads into 021.
    return _merge_held(out)


def dyn(t: float) -> float:
    """The song's dynamics by section (0..1): one voice, the village, full, the swell, soft, full-soft, the tag."""
    m = markers()
    if t < m["ch04_shell_013"] - 0.4:
        return 0.42
    if t < m["ch04_shell_014"]:
        return 0.50
    if t < m["ch04_shell_015"] - 0.4:
        return 0.56
    if t < m["verse_repeat"] - 0.5:
        return 0.62
    if t < m["ch04_shell_021"] - 0.4:
        return 0.40
    if t < m["tag"] - 0.3:
        return 0.50
    return 0.38


def oh_bus(x: np.ndarray) -> np.ndarray:
    """An 'oh' (F1 500, F2 860 Hz): the women's harmony."""
    return filt(x, [bq_highpass(160, 0.7), bq_peak(500, 6.0, 3.0), bq_peak(860, 5.0, 3.5), bq_peak(2600, 2.0, 4.0),
                    bq_peak(3300, -5.0, 1.0), bq_lowpass(4200, 0.7)])


def oo_bus(x: np.ndarray) -> np.ndarray:
    """An 'oo' (F1 330, F2 700 Hz), dark: the men's roots."""
    return filt(x, [bq_highpass(90, 0.7), bq_peak(330, 6.0, 3.0), bq_peak(700, 4.0, 3.0), bq_peak(2400, -3.0, 1.5),
                    bq_lowpass(2600, 0.7)])


def _sing(mx: Mixer, bus: str, notes: list, seed: int, vel: float, pan: float, cents: float = 0.0,
          late: float = 0.0, vib: float = 13.0) -> None:
    g = rng(seed)
    prev_end = -10.0
    for i, (t0, d, m, syl) in enumerate(notes):
        first = t0 - prev_end > 0.2                # a breath before it: a fresh onset
        long = d > 1.4 * BEAT
        v = vel * dyn(t0) / 0.5 * g.uniform(0.95, 1.04) * (1.06 if long else 1.0)
        if syl.startswith("love"):
            v *= 1.12
        x = breath_flute(m + cents / 100.0, d + 0.05, float(np.clip(v, 0.05, 0.95)), seed=seed + 31 * i,
                         breath=0.2, scoop_cents=38.0 if first else 14.0, vib_cents=vib if long else 0.4 * vib,
                         vib_rate=float(g.uniform(4.7, 5.3)), swell=0.25 if long else 0.0,
                         attack=0.13 if first else 0.06, release=0.45 if long else 0.25, beta=0.5)
        mx.add(bus, x, t0 - FLUTE_PRE + late + float(g.normal(0, 0.006)), pan=pan)
        prev_end = t0 + d


# Bus gains from measured bus loudness (render(stats=...)): the lead at L, the village's second voice L-4 (over the
# bars it sings), the women's harmony L-6, the men's roots L-7. Each instrument's level is its section's dynamic, so
# the song's shape (one voice, then a hundred, then soft under the dialogue) is in the playing, not the faders.
def render(out_path: str = OUT, verbose: bool = True, stats: dict | None = None) -> dict:
    check_lyric()
    mel = tune()
    m = markers()
    village = [x for x in mel if x[0] >= m["ch04_shell_013"] - 0.01 and x[0] < m["tag"] - 0.01]
    alto = (_notes(ALTO_013, 5) + _notes(ALTO_014, 9) + _notes(ALTO_015, 13) + _notes(ALTO_014, 17)
            + _notes(ALTO_015, 21))
    bass = (_notes(BASS_014, 9) + _notes(BASS_015, 13) + _notes(BASS_014, 17) + _notes(BASS_015, 21)
            + _notes(BASS_TAG, 25))
    length = m["end"] + 7.0
    mx = Mixer(length)
    mx.bus("lead", 0.0, send=0.36, process=HFV.vocalise_bus)
    mx.bus("village", -4.1, send=0.45, process=HFV.vocalise_bus)
    mx.bus("alto", -4.6, send=0.45, process=oh_bus)
    mx.bus("men", -5.1, send=0.42, process=oo_bus)
    _sing(mx, "lead", mel, SEED + 1, 0.5, -0.05)
    _sing(mx, "village", village, SEED + 2, 0.46, 0.3, cents=6.0, late=0.028, vib=15.0)
    _sing(mx, "alto", [(t, d, mm, "") for t, d, mm, _ in alto], SEED + 3, 0.42, -0.35, vib=10.0)
    _sing(mx, "men", [(t, d, mm, "") for t, d, mm, _ in bass], SEED + 4, 0.46, 0.15, vib=8.0)
    hall = ModFDNReverb(rt60=2.4, rt60_high=1.0, predelay=0.03, size=1.0, mod_depth=8.0, mod_rate=0.45,
                        early_level=0.3, lowcut=110.0, seed=SEED % 9973)     # the causeway head at night: open air
    st: dict = {}
    HUSH._bus_stats(mx, st)
    if stats is not None:
        stats.update(st)
        stats["markers"] = m
    res = HFV._finish(mx, hall, out_path, 3.5)
    if verbose:
        print("  buses", {k: round(v, 1) for k, v in st.items()})
        print("  markers", {k: round(v, 2) for k, v in m.items()})
        print(f"the_long_way_round: {res['seconds']:.1f}s  {res['integrated_lufs']:.2f} LUFS"
              f"  TP {res['true_peak_dbtp']:.2f} dBTP")
    return res


if __name__ == "__main__":
    render()
