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

## M2: the slice's three final cues (M2-AUD-03; SPEC §10 M2, §16 Q3)

The slice needs three *final* cues. I built three families, so you can judge each by the scene it scores. Please
listen in this order (about 15 minutes). **Your verdict on each decides "final"**; one sentence per cue is enough
("flute too breathy", "bell too loud", "the night one is lovely").

### (a) Haluna by day and by night

| # | File | Length | Plays |
|---|---|---|---|
| 1 | `music/haluna_village.ogg` | 75 s loop | B02, B03, B05: Haluna by day |
| 2 | `music/haluna_night.ogg` | 83 s loop | B11: the dock at night (after the Drownbell) |

- The brief: *a festival for a departure.* Warm, gamelan-like percussion, a flute tune that never quite resolves.
  The tune never lands on the home note D: it hangs on E, then on B (a deceptive close), and only the harmony
  comes home at the loop's wrap. **Does it feel bittersweet, or just unfinished?**
- The plucked "lute" under the tune is a modelled string through a small wooden body. Lute, harp, or toy?
- The two metallophones interlock (each plays every other note). Do you hear one figure, or a clatter?
- The night version is the same tune, slower, flute and drone only, the second half an octave lower. Is it
  intimate, or empty?
- Loop seams: 75 s and 83.5 s. Any bump?

### (b) Battle v2 and the Drownbell

| # | File | Length | Plays |
|---|---|---|---|
| 3 | `music/battle_standard.ogg` | 75 s | **The M1 version, for comparison** (30 s is enough) |
| 4 | `music/battle_standard_v2.ogg` | 3 s intro + 72 s loop | Every ordinary battle |
| 5 | `music/drownbell_p1.ogg` | 72.7 s loop | The Drownbell, phase 1 |
| 6 | `music/drownbell_p1.ogg` **and** `music/drownbell_p2.ogg` **together** | 72.7 s loop | Phase 2, the Flood: the game fades stem 2 in over 4 s on top of stem 1 |

- **v2 is the same composition as v1 with a different band.** The listening notes for M1 named the modelled
  guitar and the synth lead as the weakest parts, and offered "metallophone and drums only" as a direction. v2 takes
  it: no guitar (its chords became struck metallophone stabs and muted plucks), no synth lead (the theme is a
  hard-blown flute, doubled by a metallophone). **Which do you prefer, v1 or v2, and why?** If v2's flute sounds
  too gentle for a battle, say so: that tells me whether to bring a (better) lead synth back.
- The Drownbell: a tower bell tolls on every downbeat (a minor-third "tierce", the partial that makes bells sound
  sad). Under it the interlocking metallophones, a 3+3+2 bass and drums, and a breath-flute theme. Phase 2 adds
  low strings, rising water (a band of noise that climbs over 8 bars, with bubbles) and a sub-bass surge into each
  section. To hear phase 2, play both stem files at once (in Audacity: import both, play). **Does phase 2 feel like
  the water rising, a real escalation?** Is the bell too loud, or not menacing enough?
- The low strings are the old saw-ensemble pad, kept low. If they sound like a 90s keyboard, tell me.

### (c) The Hush family (the cutscenes and the end)

| # | File | Length | Plays |
|---|---|---|---|
| 7 | `music/haluna_dawn.ogg` | ~2.6 min | Cutscene A (B01): the girl on the beach |
| 8 | `music/hush_first_verse.ogg` | 80 s | Cutscene B (B09): Asha sings the first verse |
| 9 | `music/hush_coda.ogg` | 39 s | The slice end card (B12) |
| 10 | `sfx/ilun_summon.ogg` | 6 s | The sting when Asha calls Ilun (B10) |

- **haluna_dawn:** solo piano and a low metallophone. The brief: *it doesn't know yet whether it's sad.* It moves
  between D major and B minor under the same melody, and it previews Haluna's tune before the village plays it.
  Does the ambiguity come across?
- **hush_first_verse:** the Hush theme's first phrase as Asha's song. Until a voice is settled (Q4/Q5), a
  "vocalise-like instrument" carries it: the breath flute shaped by an open "ah" vowel's resonances. The piano
  enters on the last word, *mir* (at about 0:28). **Does the line read as singing, or as a flute with a cold?**
  This is the single most important judgement for the slice. If you'd rather hear the synthetic singing voice
  (the temple cue's Cantor, the same voice model), say so and I'll render that version for comparison.
- **hush_coda:** the same phrase on the piano alone, slower. Too sentimental, or right for the end card?
- **ilun_summon:** the Hush's first six notes, two octaves up on glass, over gathering water. Beautiful, or shrill?

**Correction (2026-10-24, later the same day):** in the first render of `hush_first_verse.ogg` the piano was mixed
about 31 LU too quietly (the grand-piano model's raw level is far below the breath flute's, and I balanced it by
guess instead of by measurement), so the piano "entering on *mir*" was almost inaudible. `haluna_dawn.ogg` had the
opposite fault: its low metallophone sat about 6 LU over the piano instead of 10 under. Both are re-rendered with
measured bus levels. If you listened to the earlier files, please listen to these two again.

## M2/M3: the causeway, the dive, Sefir, the Ebbing (M2-AUD-11, M3-AUD-01, -03, -05)

| # | File | Length | Plays |
|---|---|---|---|
| 1 | `music/saltgrass_causeway.ogg` | 80 s loop | B06, the slice's route |
| 2 | `music/lamp_diver.ogg` | 90 s loop | Ch1, Rhen's dive in the drowned tower |
| 3 | `music/sefir_theme.ogg` | 71 s loop | Ch6, Sefir's barge; his motif |
| 4 | `music/the_ebbing.ogg` | 114 s | Ch9, Asha's first great Ebbing |

- **saltgrass_causeway:** wind, a walking pulse of plucked open fifths (no thirds, so neither warm nor sad), and a
  sparse high plucked melody. Brief: *three voices walking; the path leads somewhere that doesn't come back.* Does
  the wind read as wind (not hiss)? Does it make you want to keep walking?
- **lamp_diver:** everything heard through water (a hard low-pass on all but the glints), a sub-bass pressure, a
  warm swelling "lantern" chord, a muffled heartbeat, bubble trains, and once a loop, far below, a single hummed
  voice with one long note and a fall of a third (the opening gesture of our own Hush: Rhen's father's
  current-song). **Did you notice the voice? You shouldn't be sure.** Is it too murky to bear for a whole dungeon?
- **sefir_theme:** the only cue in C major (the Order's pure key), and nothing with an attack (his barge "leaves no
  wake"): a congregation humming, a glass harmonica. His motif rises calmly to D, then slips to C# and holds it over
  F major: one wrong note in a beautiful line. **Is it beautiful first and unsettling second, in that order?** That
  is the whole character.
- **the_ebbing:** the Hush theme danced. The Cantor's line (the same vocalise instrument as the first verse), the
  piano, a slow 3/4 dance of interlocking metallophones and a soft drum, and glass "motes" whose every figure falls,
  because the motes go *down and seaward* (Pell: "Beautiful. And pointing the wrong way."). Is it the most beautiful
  thing in Act I? If not, what is missing?

## M3: Act I area and match themes (M3-AUD-02, M3-AUD-04)

Three new loops for chapters that aren't built yet, so you can only hear them on their own for now. Each one has
a different key and band from the slice cues, so a chapter change should sound like a change of place. About 4
minutes in all. The scenes are in act_outline.md (Ch5, Ch7, Ch8).

| # | File | Length | Plays |
|---|---|---|---|
| 1 | `music/terraces_of_ash.ogg` | 80 s loop | Ch5: Pemakar and the Lanternfall festival among the graves |
| 2 | `music/tidecup_match.ogg` | 68.6 s loop | Ch7: the story Reefball match inside the Tamsule Bell |
| 3 | `music/corrow_seawall.ogg` | 75.8 s loop | Ch8: walking Corrow Bastion and the seawall before the storm |

### (1) Terraces of Ash: a festival held in a cemetery

- **The band:** a plucked zither carries the tune, with low zither strings under it. High, soft bars fall in short
  runs: the leaf-boat lanterns tipping over the terrace lips. Quiet tuned bubbles stand for the channels, and
  copper gongs keep a slow eight-bar cycle (the stair-mountain). Through the second half, women hum the tune an
  octave down: the mourners. There is no flute and there are no interlocking bars, so it shouldn't sound like
  Haluna.
- **The key:** F, on a five-note scale with a flat second and a flat sixth (F Gb Bb C Db), in a slow 3/4. **Is it
  lovely and grave at the same time, or only gloomy?** If it's gloomy, the fix is to make the lanterns brighter
  and more frequent, not to change the key.
- **The zither** is a modelled string in a modelled box. Zither, harp, or "a guitar in a cave"? If it's the cave,
  the box resonances are what to change.
- **The lanterns:** small fires on water, or wind chimes? Too many, or too few?
- **The hum:** does it make the second half feel like mourners joining in, or does it muddy the zither?

### (2) The Tidecup: a sports theme that is also a lament

- **The brief:** each captain names one person the sea has taken, and Oruvel's side plays "for the ones who didn't
  come up". It should never sound triumphant. The piece sets two things against each other. Underneath is the
  game's drive: 112 BPM, frame drums and a big drum, a running plucked ostinato and a walking bass. Over it is a
  slow A-minor song on the flute, in long notes. While the drums are going, the song never lands on its home note.
- **The Bell:** the arena is the Tamsule Bell, so a low padded bronze bell sounds at each section, and a soft
  "salt-glass" bar doubles the song's long notes in the third section. In the second section the crowd **hums**
  the song's outline under the drums. Nobody in the crowd sings, because only Cantors sing.
- **The ending:** the last four bars drop to the big drum's heartbeat, the Bell, the glass and the flute's last
  falling notes. That is "the naming". Then the loop picks the game back up.
- **The key question:** does it make you want to watch a match **and** feel sad, or does one side win? If it
  sounds like a battle theme, the drums are too forward. If it sounds like a funeral, the song is.
- The crowd hum: a crowd in an arena, or a church choir? Is the bell too loud?
- Mastering: the big drum's hits take up to about 3 dB of fast limiting on under 1 % of samples. If the downbeats
  sound flattened, tell me and I'll lower the drums instead.

### (3) The Seawall: nine hundred years of the same defence

- **The idea:** a ground bass. One four-bar bass line (B D | A F# | G E G | F#) comes round six times without
  changing, while everything above it varies. Each time round it ends on the dominant and climbs back to B, so
  the loop has no last bar, only "the next time round". That is the image of the same defence kept for nine
  hundred years. Above the bass, a low, dark flute (a fisher's whistle, not a festival flute) plays four phrases.
  Muted plucks in eighths are the rope and block. The frame drum keeps a footstep on every beat (the stair). A
  kettle gong (the beacon) marks each round.
- **The Watchers:** the wall's carved faces hum, so in the fourth round the men hum a slow descending chorale over
  the ground alone, and the women join a third above in the fifth.
- **The key question:** does it feel steady and dutiful, not afraid yet and not hopeful either? Or does the
  repetition get dull by the third time round? If it's dull, I'd vary the plucks before touching the bass, because
  the unchanging bass is the point.
- Does the flute's low register sound like a breathy whistle (good), or a flute played badly (bad)?
- The step drum has the same fast limiting on its hits as the Tidecup's drums (up to about 4 dB on 0.5 % of
  samples). Do the footsteps sound natural, or clipped?

**For all three:** can you hear the loop wrap? The seams are at 80 s, 68.6 s and 75.8 s.

## M3: Act I bosses (sea) (M3-AUD-08)

Two boss loops for fights that aren't built yet, so for now you can only hear them on their own. Neither uses the
Drownbell's tower bell or the gamelan bars of the ordinary battle theme, and each has its own key and meter. That
way a boss should sound like a different kind of trouble, not the battle theme played louder. It takes about
2.5 minutes in all. The scenes are in act_outline.md (Ch1, Ch4).

| # | File | Length | Plays |
|---|---|---|---|
| 1 | `music/hullgnaw.ogg` | 2.7 s intro + 64.0 s loop | Ch1: Hullgnaw, on a breaking raft while Oruvel is torn apart |
| 2 | `music/spar_wraith.ogg` | 2.8 s intro + 72.8 s loop | Ch4: the Spar-Wraith, on the deck of the drowned trader |

### (1) Hullgnaw: the turn-order tutorial

- **The brief:** an eel grown through a sunken ship's ribs. It's the first boss and teaches the timeline, so it
  has to be easy to follow before it's heavy. It is in G minor and 6/8: two big beats a bar, like a raft heaving on
  a swell. Only one tune plays at a time.
- **The band:** a fingered bass is the eel. It sits on each chord root and then crawls chromatically into the next
  one, so the low line is always coiling. Muted plucks through a small wooden body run in eighths (Oruvel is a town
  of rope). Frame drums and a big drum keep the beat. A low gong groans at each section: the hull. The tune is a
  hard-blown flute, and an open plucked counterline joins it when the tune comes back.
- **The break (bars 33-40):** the drums drop out to the big drum and hard slaps (timbers cracking) over the eel,
  then build back.
- **The key question:** is it easy to follow while you learn the timeline, or busy? If it's busy, the plucks
  should come down first. **Is it menacing enough for a first boss,** or does it sound like a jig? If it's a jig,
  I'd make the eel's crawl slower and lower before touching the meter.
- Mastering: one stack of drum, bass and flute in bar 27 takes about 4.6 dB of fast limiting, and other hits take
  2-3 dB, on under 1 % of samples. If the downbeats sound flattened, tell me and I'll lower the drums.

### (2) The Spar-Wraith: rope, wind and dead wood

- **The brief:** a trader lost in the same storm as Oruvel, drifting with its sails set and nobody at the helm. A
  spawn is tangled in its rigging. It should be eerie before it's loud. It is in F# Locrian, where the home chord
  has a flat fifth, so it never settles. The meter is 7/8 counted 2+2+3: the ship's roll with nobody steering
  always comes round a beat short.
- **The rigging:** wind in the shrouds (a drifting noise band with a thin whistle on top) never stops. Rope creaks
  under load on the long beat of the bar: a modelled stick-slip, a rapid run of tiny catches whose rate rises or
  falls. A larger, slack drum is the hull knocking.
- **The band:** a low, breathy flute (a whistle in the rigging) carries the tune. High open plucks (the shrouds)
  answer it when it returns. The bass falls to the tritone C on the home chord. In the becalmed section (bars
  33-44) the drums stop, and a low string chord (the dead sails) holds under the wind and the knocking.
- **The key question:** is it eerie and still a fight, or just strange? **Do the rope creaks sound like rope and
  wood,** or like a door hinge or a frog? If they're the hinge, I'd lower their rate. Is the wind too steady (a hiss)
  or about right?
- The dead sails are the old saw-ensemble pad, kept low. If they sound like a keyboard, tell me.

**For both:** can you hear the loop wrap? The seams are at 64 s and 72.8 s after each intro.
