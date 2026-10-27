"""Shared motifs: the one place a recurring tune is written down, so every cue that states it states the same notes.

CURRENT_SONG (M3-AUD-818; act1_ch01.md C1-06 / C1-15, act1_ch08.md B17, act3_ending E2): Dace's current-song, the
Saltwright sung chart he taught Rhen for reading water. A working tune, not a lullaby, and never the Hush: it moves
in D dorian with repeated "soundings" (a note struck twice, as a leadsman calls a depth), climbs a fourth to the
current's set and walks back down; the Hush (hush_first_verse.py VERSE) opens with a falling E-D-C-A in A minor
instead. Written for this project (SPEC §2); it quotes and derives from no existing melody.
Every statement uses these notes: `rhen_current_hum` hums phrase 1 (Ch1, C1-06), `going_under` and `current_song`
sing the whole tune (Ch1 C1-15, Ch8 B17), and E2's `goodbye_dace` returns to it.

Each phrase is [(midi, beats)] at CURRENT_SONG_BPM; a phrase ends on a held note so a singer can breathe after it.
"""
from __future__ import annotations

CURRENT_SONG_BPM = 76.0
CURRENT_SONG = [
    [(62, 0.5), (62, 0.5), (69, 1.5), (67, 0.5), (65, 0.5), (67, 0.5), (69, 2.0)],  # sound, sound, the set rising
    [(72, 1.0), (69, 0.5), (67, 0.5), (65, 1.0), (64, 0.5), (65, 0.5), (67, 2.0)],  # over the shoal and along
    [(69, 0.5), (69, 0.5), (65, 1.0), (64, 1.0), (60, 1.0), (62, 3.0)],              # sound again, and home to D
]


def phrases_in_seconds(bpm: float = CURRENT_SONG_BPM) -> list[list[tuple[float, float]]]:
    """CURRENT_SONG as [(midi, seconds)] per phrase."""
    beat = 60.0 / bpm
    return [[(float(m), b * beat) for m, b in phrase] for phrase in CURRENT_SONG]
