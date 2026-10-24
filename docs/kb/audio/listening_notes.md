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

---

# M2 listening notes (SPEC §16 Q3; the slice's cues and sounds)

Same rules as above: everything is synthesized from code in this repo, nobody has heard it, and your ears decide
what is "final". Each entry says what to play, what it should feel like, and the questions I most need answered.
In the game they play by themselves (the `Audio` autoload, docs/kb/tech/audio_runtime.md); the files are in
`assets/audio/`.

## M2: Shell Shrine (B07, the temple trial)

| File | Length | What it is |
|---|---|---|
| `music/shell_shrine_interior.ogg` | 72 s loop | The trial's interior cue |
| `sfx/shrine/shrine_stone_turn_1.ogg` (and _2, _3) | ~1.7 s | A basin turning on its stone seat |
| `sfx/shrine/shrine_pour.ogg`, `shrine_drain.ogg`, `shrine_spill.ogg` | ~1.8 s | The water reaching the pool, the sluice, a grate |
| `sfx/shrine/shrine_side_drain.ogg`, `shrine_door.ogg`, `shrine_charm.ogg`, `shrine_pool_fill.ogg` | 1–4 s | The side pool emptying, the door's valve, the charm, the pool filling (a loop) |

**Listen for (the cue):**
- The brief is "a tended, loved place": warm, still, a little sacred. Does it feel *kinder* than the M1 temple cue
  (`temple_trial.ogg`, which is meant to be ominous)? It should.
- The drips are tuned to the drone's scale and each one rings its shell basin at the same pitch. Do the drips sound
  like water, or like a glockenspiel? If the "ring" is too musical, I can drop it 6 dB in one number.
- The far congregation hum (the Order hums): people, or an organ?
- Can you hear the loop wrap (every 72 s)?

**Listen for (the puzzle):** does the stone grind sound like heavy stone turning (not a creaking door)? Do the
pour, the drain and the spill sound *different* enough that you'd know where the water went with your eyes shut?
That is the point of them (pillar 4).
