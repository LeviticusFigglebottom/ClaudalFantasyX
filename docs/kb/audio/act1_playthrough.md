# Act I as-played music pass (2026-10-30, on 0347aa74)

The Lead's 10-30 item: run each chapter's cutscene → field → battle → victory changes and log silence gaps, double
starts, abrupt cuts and loudness jumps over 3 LU, then fix them. Act I's flow lives in each chapter's story code, so
the pass checks each layer where it lives:

| Layer | How it was run | Result |
|---|---|---|
| Field after a cutscene, field after a battle | AudioDirector itself, headless (`tests/unit/test_zone_return.gd`) | **Fixed: a silence gap.** See below. |
| Inside each cutscene | each Act I script's timeline (`@music`, `@wait`, every line at a reading pace) against the cues' real lengths (`tools/audio/act1_playthrough.py`) | 3 items, all statements that end before a quiet walk-away (below); no cuts and no double starts |
| Cuts | every music fade the game asks for, at least mix.json `min_fade_sec` (`test_music_transitions.gd`) | 0 in Act I |
| Double starts | MusicDeck leaves a cue that is already current alone; a stem change (`stem=1`) is meant | 0 |
| Loudness at each hand-over | `tools/audio/act1_mix_pass.py` (docs/kb/audio/act1_mix_pass.md) | 81 hand-overs, 0 over 3 LU |
| Battle in, battle out, victory | `battle_in_sec` 0.3 on the beat, `battle_out_sec` 1.2 as the outcome sting plays (battle_audio.gd), then the zone | covered by the rows above |

## The fault found and fixed: the field fell silent
A scene that ended on `@music silence` or on a one-shot cue left the field silent until the next scene swap. Act I has
24 such scenes (13 end in silence, 11 on a one-shot). So did a battle that ends in the zone it began in,
because battle_out stops the music and nothing started it again. Act I's cue sheet rule is "the zone returns on
release", but nothing in the engine did that.

**Fix (game/audio):** `AudioDirector._step_zone_return` and `MusicDeck.is_silent()`. When no cutscene plays, no
battle is in the tree, no cue is loading and the music has been silent for `mix.json` `music.zone_return_sec`
(3.0 s, longer than the cutscene release), the zone's own cue comes back from where it left off. A swap or a battle
that follows at once starts its own cue first, so nothing is ever doubled. A zone with no music (the first verse,
scored by its own cutscene) stays silent. `tests/unit/test_zone_return.gd` covers six cases.

## Inside the scenes: statements that end before the scene does
These are one-shot cues that finish a few seconds before a quiet walk-away. The estimate counts both arms of every
`<<if>>`, so the real gaps are shorter. They stay as they are: a theme that ends and then a goodbye is the scene's
pacing, and the zone comes back 3 s after each scene now.
- ch07_empty_moorings: `oruvel_theme` ends up to about 18 s before the scene does (both of Asha's leaf-boat branches counted).
- ch07_tavi: `tavi_kell` ends about 5 s before.
- ch08_binding: `virel_bound` (a sting) ends about 4 s before.

## Act II, from the same tool (`--act 2`)
- **Fixed:** `kerrid_at_sea` ran out about 88 s before ch15_the_shoal silences it, because Story's scene is longer
  than the cue sheet's estimate. It is retimed to 270 s: the same bed, with the tread stopping at about 125 s inside
  the confession.
- **For Story:** eight `@music ... fade=0.0` lines (ch14_the_vows, ch15_current_song, ch16_swept_away, ch16_the_choir).
  The deck plays them as 0.2 s fades. That is right for the trap and the storm; the others may want 0.5.
- `peace_wedding_break` (about 27 s) ends roughly 12 s before ch14_the_vows' `@music silence`, which is the held low C
  dying away under the declaration, as written. `kesh_bound` ends about 4 s before `kesh_memory`.
