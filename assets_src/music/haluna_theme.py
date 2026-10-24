"""Haluna's musical material (M2-AUD-03), shared by `haluna_village.py` (the day loop) and `haluna_night.py`.

Original composition for this project (SPEC §2). The brief (vertical_slice.md §6): "warm, gamelan-like
percussion, a flute melody that never quite resolves. The festival is for a departure."

* D major pentatonic (D E F# A B) for the metallophones; the flute adds G and, once in the B phrase, the leading
  tone C#, which is the only note that leans toward home.
* 6/8. The melody's phrases never land on D: the A phrase hangs on E (the 2nd, over A) and then on B (the 6th,
  over G, a deceptive close); the B phrase rises to E6 and settles back on E5 over an A sus chord. Only the
  harmony comes home, at the loop's wrap, under a melody that has already stopped.
* The tune is written for this game: it is not adapted from any folk tune or existing melody. Its intervals
  (a falling 3-2-1-2 cell answered by a leap to the 5th) were checked against the Hush theme so the two stay
  distinct: the Hush falls by step from a long held note; Haluna's tune circles.

Units: eighth notes (six to a bar). Notes are (name | None for a rest, eighths).
"""
from __future__ import annotations

# The A phrase, 8 bars: the first half hangs on E5 (bar 4), the second on B4 (bar 8).
PHRASE_A = [
    [("F#5", 2), ("E5", 1), ("D5", 2), ("E5", 1)],
    [("F#5", 3), ("A5", 3)],
    [("B5", 2), ("A5", 1), ("F#5", 2), ("E5", 1)],
    [("E5", 5), (None, 1)],
    [("D5", 2), ("E5", 1), ("F#5", 2), ("A5", 1)],
    [("B5", 3), ("D6", 2), ("B5", 1)],
    [("A5", 2), ("F#5", 1), ("E5", 2), ("D5", 1)],
    [("B4", 5), (None, 1)],
]
# A' ends on F#5 over B minor instead of B4 over G.
PHRASE_A2_LAST = [("D5", 1), ("E5", 1), ("F#5", 3), (None, 1)]
# The B phrase, 8 bars, higher: the C#6 in bar 1 is the only leading tone in the tune.
PHRASE_B = [
    [("D6", 3), ("C#6", 2), ("B5", 1)],
    [("A5", 3), ("F#5", 3)],
    [("G5", 2), ("A5", 1), ("B5", 2), ("A5", 1)],
    [("F#5", 5), (None, 1)],
    [("E5", 2), ("F#5", 1), ("A5", 2), ("B5", 1)],
    [("D6", 3), ("E6", 3)],
    [("D6", 2), ("B5", 1), ("A5", 2), ("F#5", 1)],
    [("E5", 5), (None, 1)],
]

# Chords per phrase bar (roots; the qualities are implied by the pentatonic voicings below).
CHORDS_A = ["D", "D", "G", "A", "Bm", "G", "Em", "G"]
CHORDS_A2 = ["D", "D", "G", "A", "Bm", "G", "Em", "Bm"]
CHORDS_B = ["Bm", "G", "Em", "A", "G", "D", "Em", "Asus"]

# Metallophone colours per chord (pentatonic only; the interlock cycles through them).
CHORD_TONES = {
    "D": ["D5", "F#5", "A5", "E5"],
    "G": ["D5", "G5", "B5", "E5"],
    "A": ["E5", "A5", "B5", "E5"],
    "Asus": ["E5", "A5", "D5", "B4"],
    "Bm": ["D5", "F#5", "B5", "A5"],
    "Em": ["E5", "G5", "B5", "D5"],
}
# Plucked accompaniment (low to high) and the bass root per chord.
LUTE = {
    "D": ["D3", "A3", "D4", "F#4"],
    "G": ["G2", "D3", "B3", "D4"],
    "A": ["A2", "E3", "A3", "C#4"],
    "Asus": ["A2", "E3", "A3", "D4"],
    "Bm": ["B2", "F#3", "B3", "D4"],
    "Em": ["E3", "B3", "E4", "G4"],
}
BASS = {"D": "D2", "G": "G1", "A": "A1", "Asus": "A1", "Bm": "B1", "Em": "E2"}
# The interlock order over a chord's four colours, one per eighth (two players alternate them).
INTERLOCK = [0, 1, 2, 1, 3, 1]


def notes_in_order(phrases: list[list[list[tuple[str | None, int]]]]) -> list[tuple[str | None, int]]:
    """Flattens bars of phrases into one note list (eighths)."""
    out: list[tuple[str | None, int]] = []
    for phrase in phrases:
        for bar in phrase:
            out.extend(bar)
    return out


def phrase_a2() -> list[list[tuple[str | None, int]]]:
    return PHRASE_A[:7] + [PHRASE_A2_LAST]
