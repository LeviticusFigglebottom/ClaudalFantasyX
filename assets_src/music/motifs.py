"""Shared motifs: the one place a recurring tune is written down, so every cue that states it states the same notes.

CURRENT_SONG (M3-AUD-818; act1_ch01.md C1-06 / C1-15, act1_ch08.md B17, act3_ending E2): Dace's current-song, the
Saltwright sung chart he taught Rhen for reading water. A working tune, not a lullaby, and never the Hush: it moves
in D dorian with repeated "soundings" (a note struck twice, as a leadsman calls a depth), climbs a fourth to the
current's set and walks back down; the Hush (hush_first_verse.py VERSE) opens with a falling E-D-C-A in A minor
instead. Written for this project (SPEC §2); it quotes and derives from no existing melody.
Every statement uses these notes: `rhen_current_hum` hums phrase 1 (Ch1, C1-06), `going_under` and `current_song`
sing the whole tune (Ch1 C1-15, Ch8 B17), and E2's `goodbye_dace` returns to it.

Each phrase is [(midi, beats)] at CURRENT_SONG_BPM; a phrase ends on a held note so a singer can breathe after it.

ORDER_HUM (bible §4: the Order hums; only Cantors sing): the congregation's tune, first heard far off in the Shell
Shrine (shell_shrine_interior.py CHANT, G3 A3 B3 A3 G3 E3 G3 D3 E3 G3, slow). The Stillguard hum it in Ch6's raid
(`raid`, `stillguard_hum`) and Corrow hums it, broken, in Ch9 (`corrow_night`), so the player knows it. Here at
ORDER_HUM_BPM, in beats; the shrine's own slow layer stretches the same notes over seconds.

KERRID_STAIR (M3-AUD-821; act1_ch05.md B05 close, ADR 0020): Kerrid's walking motif, the stair-watch's tread. A
bowed two-note figure, D3 falling a fourth to A2, each note one stride of two beats over a low frame drum on every
beat (the first of each pair heavier), at KERRID_STAIR_BPM: heavy, patient, the pace of a man who has climbed one
stair for a very long time. Written for this project (SPEC §2); it quotes and derives from no existing melody (two
notes a fourth apart, chosen for their weight, not taken from any tune). `kerrid_stair` (Ch5) states it steady as he
falls in at the back of the line; E3's `goodbye_kerrid` must play these same two notes and slow the tempo from
KERRID_STAIR_BPM to a stop (KERRID_STAIR_STRIDE beats a note, so each slowing stride is one note).
"""
from __future__ import annotations

CURRENT_SONG_BPM = 76.0
CURRENT_SONG = [
    [(62, 0.5), (62, 0.5), (69, 1.5), (67, 0.5), (65, 0.5), (67, 0.5), (69, 2.0)],  # sound, sound, the set rising
    [(72, 1.0), (69, 0.5), (67, 0.5), (65, 1.0), (64, 0.5), (65, 0.5), (67, 2.0)],  # over the shoal and along
    [(69, 0.5), (69, 0.5), (65, 1.0), (64, 1.0), (60, 1.0), (62, 3.0)],              # sound again, and home to D
]


ORDER_HUM_BPM = 52.0
ORDER_HUM = [(55, 2.0), (57, 1.5), (59, 2.0), (57, 1.0), (55, 2.0), (52, 2.0), (55, 1.5), (50, 1.5), (52, 1.5),
             (55, 3.0)]


def phrases_in_seconds(bpm: float = CURRENT_SONG_BPM) -> list[list[tuple[float, float]]]:
    """CURRENT_SONG as [(midi, seconds)] per phrase."""
    beat = 60.0 / bpm
    return [[(float(m), b * beat) for m, b in phrase] for phrase in CURRENT_SONG]


def order_hum_in_seconds(bpm: float = ORDER_HUM_BPM) -> list[tuple[float, float]]:
    """ORDER_HUM as [(midi, seconds)]."""
    beat = 60.0 / bpm
    return [(float(m), b * beat) for m, b in ORDER_HUM]


KERRID_STAIR_BPM = 48.0
KERRID_STAIR_STRIDE = 2.0      # beats a note: one stride
KERRID_STAIR = [(50, KERRID_STAIR_STRIDE), (45, KERRID_STAIR_STRIDE)]   # D3, then A2: the tread


def kerrid_stair_in_seconds(bpm: float = KERRID_STAIR_BPM) -> list[tuple[float, float]]:
    """KERRID_STAIR as [(midi, seconds)] (one statement of the two notes)."""
    beat = 60.0 / bpm
    return [(float(m), b * beat) for m, b in KERRID_STAIR]
