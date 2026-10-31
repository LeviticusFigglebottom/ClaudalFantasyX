---
id: M5-A3P-1950
title: "Act III score, part 1: the Unbinding themes (the Letting sung, its release, the release sting, the swell)"
role: audio
status: review
owner_session: "claude/audio (session_01UPFyE9L9BA3QodpCNJEfAs)"
depends_on: []
reviewer: story
milestone: M5
---
## Goal
ADR 0207 opens Act III per track. The Lead's 10-30 21:56 item gave audio the Act III score: the Unbinding themes, the finale, the ending, and the Hush in Lamptongue (docs/kb/audio/lamptongue.md). This first part is the Unbinding themes, which the finale and ending build on.

## Acceptance criteria
- [x] **Storage:** ADR 0208 puts Act III's new audio in plain git under `assets/audio/act3/`, with the budget at 150 MiB. targets.py has the act3 rules.
- [x] **The sung Letting is derived, never retyped.** motifs.py `letting_verse()` is the first verse (hush_first_verse VERSE) turned upward line by line, with its close climbing to `LETTING_TASH`. Tested in test_motifs.
- [x] **Lamptongue is sung from one place.** `assets_src/music/act3/lamptongue.py` holds lamptongue.md's eight verses and its syllable rules, and has two singers:
  - Asha's vowel-shaped breath-flute vocalise, until SPEC §16 Q4 settles her voice;
  - choir phonemes for the procedural formant voices.

  Tested in test_lamptongue_sung.
- [x] **`the_letting`** (H07, a 53 s loop): Asha's vocalise sings the Eighth Verse twice. The first pass is cool and held; on the second, the choir hums her words an octave down and glass rises. A minor leans to C major on each *tash*. No percussion: the voice is the music.
- [x] **`the_letting_release`** (H08, 22 s, the cue's `release`): the held E6 while the strings thin to the E alone.
- [x] **`release_sting`** (Ch20's six releases and Kesh's, 10.5 s, -18 momentary): the Letting's cell rising on metallophone and glass, strings opening A minor to C. No voice and no cadence.
- [x] **`unbinding_swell`** (H09, 109 s), in five parts:
  - the Letting's close;
  - the swell;
  - the full choir and orchestra singing the Hush's first phrase in Lamptongue, twice (the only time in the game);
  - the second statement resolving upward, B D E | A, to A major on *tash*;
  - the chord held and thinning upward.

  Its loudness peaks at the resolution (-9 short-term), with the body around -18.
- [x] music.json rows. `the_letting` names its release. `battle.encounters` maps `ch21_sefir_letting` (H07's fight, pending combat) to `the_letting`, so the battle keeps her song.
- [x] Loudness, determinism (render_all `--determinism`), the loop seam, the mono fold, PROVENANCE.

## Next (part 2 onward)
- **The finale:** heart_approach, heart_rest, kesh_first_voice, sefir_warden, sefir_heart.
- **The ending:** goodbye_imra, ending_lift_bed, goodbye_dace, goodbye_kerrid, ending_dock, credits_suite, post_credits_lamp.
- **Ch17–Ch20:** the scene cues and the six memories.

## Review log
