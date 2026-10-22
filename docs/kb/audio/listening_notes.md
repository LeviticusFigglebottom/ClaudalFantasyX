# Listening check for SPEC §16 Q3 (M1-AUD-02)

For: the human. From: Audio Director (an agent that **cannot hear**). Date: 2026-10-22.

Everything below was synthesized from code in this repo, with no samples and no AI audio.
I measured it every way I could (see [pipeline.md](pipeline.md)), but nobody has
listened to it yet. Your ears are the test. It takes about 10 minutes, so please use
headphones or decent speakers, not a laptop speaker.

## What to play, in this order

| # | File | Length | What it is |
|---|---|---|---|
| 1 | `assets/audio/music/hush_theme_sketch.ogg` | 69 s | **The old version** (M1 v1). Play 30 s of it so you have a "before". |
| 2 | `assets/audio/music/hush_theme_v2.ogg` | 69 s | The main theme, same composition, new piano, reverb, and a "human" performance. |
| 3 | `assets/audio/music/battle_standard.ogg` | 75 s | Standard battle. A 3 s intro, then a 72 s loop. |
| 4 | `assets/audio/music/temple_trial.ogg` | 80 s | Temple-trial ambience, which loops end to start. |

To hear the **loop seams**, play the file on repeat in a player that loops gaplessly
(the in-game loop starts at 3.0 s for the battle cue and at 0 s for the temple). Or use:
`ffplay -loop 0 assets/audio/music/temple_trial.ogg` (that loops the whole battle file,
intro included, so it is only a rough check of the battle seam).

## What to listen for

**Hush v2, compared with v1**
- Does the piano sound like a *piano*, or like an electric piano or synth? Listen to
  the attack of each note and the high notes (the climax around 0:40).
- I made the tone warmer than v1 on purpose (v1 was glassy and its high notes died
  too fast). Is it now *muffled*?
- Does the melody sing over the accompaniment and breathe (it pushes and relaxes,
  with a soft pedal haze), or does it sound drunk or uneven?
- Any metallic ringing in the reverb tail at the very end? (The old reverb rang. The
  numbers say the new one is close to an ideal room.)

**Battle**
- Does it drive? Is the **interlocking metallophone figure** (left and right
  alternating, very fast) audible as one melody?
- **The distorted guitar** (hard left and right) is my weakest instrument. Does it read
  as "guitar", or as a fizzy synth buzz?
- The lead synth is deliberately a 90s-style fusion lead. Is that style acceptable, or
  does it sound cheap?
- The drums are frame drums (no rock kit). Is that enough punch for a battle?
- At the loop point (bar 1 restarts at 0:03 after each pass), do you hear a bump,
  click, or gap?

**Temple trial**
- Does it feel like a sacred, wet, stone place: still, and a little ominous?
- The **congregation hum** (the Order hums; only Cantors sing): does it read as people
  humming, or as an organ or buzzing?
- At about 0:46 a distant **Cantor** sings three words in Lamptongue ("vey… ennu… mir",
  water… hush… stay). This synthetic singing voice is the element most likely to
  sound uncanny. Is it beautiful, acceptable, or creepy? I can remove it in one line.
- The water drips should sound like water, not like blips.
- Can you hear where the 80 s loop wraps?

## My honest self-assessment

"% of commercial" means: if a shipped JRPG soundtrack cue in the same style is 100 %,
where does this land? These are guesses from measurements, not from listening.

| Cue | Guess | Strongest element | Weakest element |
|---|---|---|---|
| Hush v2 | **40–50 %** (v1 was 30–40 %) | The performance (phrasing, voicing, pedal) and the reverb | The piano timbre itself is physically plausible on paper but unverified by ear, and the soft synth-string pad underneath is still 90s-grade |
| Battle | **25–35 %** | The gamelan/rock structure (gong cycles, interlocking metallophones, the 3+3+3+3+4 riff) and a seamless loop | The distorted rhythm guitar (a modelled string into a modelled amp), and the lack of a punchy drum kit |
| Temple trial | **45–55 %** | Ambient textures hide synthesis well: the drone, hum, drips, and a long modulated reverb | The synthetic Cantor voice (uncanny-valley risk), then the hum's timbre |

Realistic ceiling: with more iteration I think pure code synthesis can reach about
60–70 % for ambient and piano-led cues and about 40–50 % for rock/fusion battle music.
Electric guitar, choir with lyrics, and orchestral strings are where self-synthesis
falls furthest behind recordings.

## The decision I need from you (SPEC §16 Q3)

After listening, please choose one, per cue type if you like:

1. **Keep iterating** (the default). Tell me which element bothered you most, in your
   own words ("piano sounds like a toy", "guitar is fizz", "voice is creepy"). One
   sentence per cue is enough, and it's the most useful thing you can give me.
2. **Supply or commission music.** You (or a composer you hire) provide recordings,
   and we keep synthesis for SFX, ambience, and prototypes. This needs an ADR and
   PROVENANCE rules for third-party audio.
3. **Accept a simpler style.** For example, lean into the "synthesized" sound on purpose
   (piano, metallophones, ambient textures, a chiptune-adjacent battle palette) and drop
   the realistic rock guitar and the sung voice entirely. This is the cheapest path to a
   consistent soundtrack.

A mixed answer is fine, for example "iterate on piano and ambience; for battle, drop the
guitar and go metallophone-and-drums only."

If you answer nothing, the SPEC default applies: **keep iterating and show samples
again at the end of M2.**
