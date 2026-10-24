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

## M3: Act I bosses (land) (M3-AUD-09)

Two boss cues for fights that aren't built yet, so the stems can only be heard on their own for now. Each is a set
of synchronized stems like the Drownbell's: the game starts stem 1 and fades the others in at the fight's phase
changes. To hear a phase, play its stems together (in Audacity: import them all, play). The scenes are in
act_outline.md (Ch5 and Ch8). About 5 minutes in all, if you play each stack once.

| # | Files | Length | Plays |
|---|---|---|---|
| 1 | `music/cinder_matron_p1.ogg` | 67.2 s loop | Ch5, the Cinder Matron, phase 1: the crust |
| 2 | `cinder_matron_p1` **and** `_p2` together | 67.2 s loop | Phase 2: Kerrid breaks its armour and the fire shows |
| 3 | `music/undertows_reach_p1.ogg` | 70 s loop | Ch8, the Undertow's Reach, phase 1: the limb rises |
| 4 | `undertows_reach_p1` **and** `_p2` together | 70 s loop | Phase 2: the Reach strikes the wall |
| 5 | all three `undertows_reach_p*` together | 70 s loop | The scripted escape: the wall falls anyway |

### (1) The Cinder Matron: a temple guardian with fire under its crust

- **The idea:** a magma-crusted construct on a stair-mountain with copper veins. It moves in an uneven 7/8 (two
  short steps and a long one, 2+2+3): a limping, mechanical gait. The key is D with a flat second and a major third,
  which reads as heat, not water. The theme is on a **copper chime**: tuned kettle gongs struck as a melody,
  doubled an octave up by a hard bar. A hard, hand-damped high bar hits each step like an anvil. A low men's hum
  (the temple) holds D and A in the intro and the breakdown.
- **Phase 2 (the Fire):** when the crust breaks, a hard-blown flute enters high with a long counter-line over the
  chime. Underneath, a low rumbling noise swells in each bar (the core), with magma crackle, jingles on every
  eighth, and more drums on the long step. The stack is about 2 LU louder than phase 1.
- **The key question:** does phase 1 sound like stone and copper, and phase 2 like the same thing on fire? If phase 2
  just sounds "busier", the flute line is what to change.
- Does the 7/8 feel heavy and purposeful, or does it trip? Is the chime clear as a tune, or does it read as
  percussion? The crackle: fire, or vinyl noise?

### (2) The Undertow's Reach: the sea's size against a stair that was not wide enough

- **The idea:** Corrow has no weapon against the storm, so this is not a hero's fight. A new mode belongs to the
  storm alone (G octatonic: it repeats at every minor third, so none of its chords is home). It is in a surging
  12/8, grouped as two long swells and three short breakers. **Phase 1:** the drowned in the wave, a low men's
  chorale (hummed) carrying the theme in long notes, each note struck on a low bar; the storm as a noise band that
  swells through each bar; the bass and drums on the swell. Corrow's beacon gong from the seawall cue sounds every
  four bars, on its own F#, the one note outside the storm's mode.
- **Phase 2 (the Reach strikes):** two hard flutes play the theme a minor third apart, with muted plucks running in
  eighths (the seawall cue's rope and block, now at speed).
- **The escape (stem 3):** the drive. A big drum on every dotted quarter, the bass doubled in running eighths, a
  slap roll and a riser into every four bars. Above it, high women's voices hum a slow line that never resolves:
  the current-song Rhen hears inside the storm's wall. Each stem adds about 1.5–2 LU.
- **The key question:** does it feel enormous and hopeless rather than heroic? Does the escape feel like running,
  not like winning? If the escape sounds triumphant, the riser is the first thing to cut.
- Is the beacon's F# a stubborn note against the storm (good), or just out of tune (bad)? Does the current-song
  read as voices inside the storm, or as a synth pad?

**For both:** can you hear the loop wrap? Both start a sixteenth before the downbeat, so the seam falls in a quiet
spot. The seams are at 67.2 s and 70 s.

## M3: Oruvel, the living funeral, the causeway beds (M3-AUD-10, M2-AUD-13)

Two music loops and two ambience beds. None of their scenes exist yet, so for now you can only hear them on their
own. The beds play at the ambience level (−26 LUFS), so turn up to hear them, or play them under
`saltgrass_causeway.ogg`. The scenes are in act_outline.md (Ch1, Ch4) and vertical_slice.md (B06).

| # | File | Length | Plays |
|---|---|---|---|
| 1 | `music/oruvel.ogg` | 73.8 s loop | Ch1: the Oruvel raft-town before the storm |
| 2 | `music/pilgrims_wake.ogg` | 83.5 s loop | Ch4: Haluna holds Asha's living funeral, a feast at night |
| 3 | `ambience/causeway_wind.ogg` | 52 s loop | B06: wind over the saltgrass on the causeway |
| 4 | `ambience/tidepools.ogg` | 46 s loop | B06: close to the tidepools at low tide |

### (1) Oruvel: a town at home, just before it dies

- **The band:** a squeezebox carries the tune. It is a new instrument, built for this cue: two reeds tuned a few
  cents apart, so it beats like an old, salt-worn box, and bellows pressure that brightens the tone as it swells.
  Its left hand plays an oom-pah (bass reed on 1 and 3, a short chord on 2 and 4). A small wire-strung cittern
  (a "salvage" instrument) chops the off-beats and plays the tune alone at the end. The rope and trade sounds are
  a wooden pulley block knocking on 2 and 4, a frame drum, three people clapping in the second verse, a rope
  creaking on a cleat, and a ship's bell rung twice where the loop starts.
- **The key:** G with a flat seventh (F natural), swung, at 104 BPM. It's a harbour dance. It isn't Haluna's 6/8
  festival, and it has no flute and no bars. Unlike Haluna's tune, this one lands on its home note: a town that
  is sure of itself. Only the middle eight bars turn to E minor, slower and lower. **Is it lively enough for Rhen
  haggling and joking, and does the E minor passage make you feel, for a moment, what is coming?**
- **The squeezebox** is the one thing most likely to sound synthetic. Does it sound like a squeezebox, a harmonium,
  or a cheap organ? If it sounds like an organ, the fix is more bellows movement and air.
- Is the swing right, or does the tune limp? Can you hear the loop wrap at 73.8 s?

### (2) The Pilgrim's Wake: a feast that is a funeral

- **The idea:** the feast and the funeral play at the same time at two speeds. The funeral moves in half notes: a
  hymn in C minor over a descending ground bass. The piano plays the hymn first, then the village hums it (nobody
  sings words, because only Cantors sing), and a low, dark bell tolls once each time round. The feast moves in
  sixteenths: frame drums and a bright plucked harp in a 3+3+2 dance, with jingles and claps in the second round.
  It's one harmony at two tempos.
- **The end of each round:** the hymn stops on an unresolved note. In the third round the dance thins and stops,
  the last two bars are bare (the feast forgetting itself for a moment), and the wrap brings the dance back as the
  hymn resolves. **Does it feel like a celebration and a funeral at once? Or does one win?** If it sounds like
  only a funeral, the harp and drums go up. If it sounds like only a party, the piano and hum go up.
- **For the scene:** Rhen understands here that the Cantor doesn't come back, and he leaves the feast angry. The
  cue doesn't play his anger. Should it? A short stinger for his exit would be a separate cue.
- The hum: a village humming, or a choir? Is the funeral bell too loud?

### (3) and (4) The causeway beds

- **causeway_wind:** a low wind that breathes in gusts, the saltgrass's dry hiss, the fast flutter of blades
  beating together (it speeds up in the gusts), a few long swishes of grass swept flat, and a faint hollow whistle
  over the coral boulders at the strongest gusts. **Does it read as wind on grass, or as hiss?** It should be
  brighter and drier than Haluna's `wind` bed.
- **tidepools:** water trickling between pools, small pops and clicks in the rock, drips off the coral, a gurgle
  now and then, and the surf line far out across the flat. Is it close and small enough? Do the pops sound like
  creatures in the rock, or like clicks in the file?
- **For both:** can you hear them wrap (52 s and 46 s)? Is anything distracting enough to notice on its tenth time
  round?

## M3: Tamsule and the Iskarra vigil (M3-AUD-12)

A town loop and the Act I break. Neither scene exists yet, so for now you can only hear them on their own. The
scenes are in act_outline.md (Ch7, and the end of Ch9).

| # | File | Length | Plays |
|---|---|---|---|
| 1 | `music/tamsule.ogg` | 70.0 s loop | Ch7: Tamsule port, the Reefball town of the Tamsule Bell |
| 2 | `music/iskarra_vigil.ogg` | 93 s, plays once | The end of Ch9: Rhen's voice-over at the Iskarra vigil (the act break) |

### (1) Tamsule: a busy port lit by machines nobody questions

- **The band:** a hammered dulcimer carries the tune. It is new for this cue: three wire strings per note struck
  together by a light hammer, ringing through a broad, thin soundboard, with long notes rolled (struck again every
  quaver, softer). Under it a low lute runs every quaver, a bass plays each beat group, and frame drums play the
  groups, with jingles in the second verse. The glimmer-tech lamps hum: a soft pair of high tones that pulse
  slowly and never quite settle. Glass bars double the tune's long notes in the second verse. Rigging tinks against
  a mast now and then. The **Tamsule Bell**, the same bell as in the Tidecup match, rings where the loop starts and
  softly at the middle section.
- **The metre:** 7/8 (2+2+3), A dorian, a quaver every quarter second. That makes it a hurrying market step, not
  Haluna's 6/8 roll or Oruvel's swung 4/4. **Is it busy and bright enough for a port? Does the 7/8 feel natural,
  or like a stumble?**
- **The middle eight bars** are Oruvel's side waiting a week for news: the Tidecup's song, re-barred into 7/8 and
  played slowly on rolled notes, with the drums down to a heartbeat. **Does it sound like waiting? Does it give
  away the Tidecup's tune too early, or does it tie the town to the arena?**
- **The dulcimer** is the part most likely to sound synthetic. Does it sound like a hammered string, a harpsichord, or
  a plucked guitar? If it sounds plucked, the hammer should be softer and the board's ring longer. Is the lamps' hum
  audible? It should be felt more than heard. Can you hear the loop wrap at 70 s?

### (2) The Iskarra vigil: a bed for a voice

- **The idea:** this cue plays under Rhen's voice-over, so it leaves the voice's range (about 300 Hz to 3 kHz) empty.
  Everything sits below or above it. Below is the sea: a breathing drone on A, a slow swell of deep water, and the
  Hush theme's first phrase played two octaves down on dark low strings, the theme heard from under the water
  ("Somebody's still below"). Three deep piano octaves, muffled as if through the sea, mark the start, the end of the
  phrase, and the close. Above are glass motes that **rise** (at the Ebbing they only fell), a faint high halo, and
  once the Hush's first notes in the glass, the theme above answering the theme below. The voice's band measures
  about 24 LU under the whole cue.
- **With a voice:** read any line over it (the prologue's "Everyone I'm going to tell you about is still here
  tonight" will do). **Does every word come through without the bed ducking? Does the bed still sound like music,
  or only like rumble and tinkle?** If it's only rumble, the low strings go up. If the voice is crowded, the motes
  go down.
- **On its own:** is the hollow in the middle strange to listen to? It is meant to be filled. Is the deep Hush
  phrase recognisable that low? Does the last rising figure, left open on B, feel like an act ending, or an
  interruption?

## M3: Act I routes (M3-AUD-11)

Two field loops for the routes between Act I's towns. Neither scene exists yet, so for now you can only hear them
on their own. Both are at the music level (−16 LUFS). The scenes are in act_outline.md (Ch4, Ch6). Play
`saltgrass_causeway.ogg` before them: all three are walking music, and each should sound like a different journey.

| # | File | Length | Plays |
|---|---|---|---|
| 1 | `music/brightwater_ferry.ogg` | 76.2 s loop | Ch4: the dawn ferry across Brightwater strait, with the drifting trader |
| 2 | `music/brine_shoals.ogg` | 72.7 s loop | Ch6: the Brine Shoals, wrecks and mud-flats, smoke from the raid ahead |

### (1) The Brightwater ferry: open water at dawn, and a drowned hull in the middle of it

- **The idea:** the first time the pilgrimage leaves the coast. It's in E-flat with a raised fourth (A natural),
  which is the dawn colour: bright and a little unearthly. It's in a slow 9/8, one bar to each roll of the hull. A
  high flute carries the tune over a low string pad and a plucked rigging figure that rolls in threes. The sea is a
  band of noise that swells once a bar.
- **Ysolde:** in the middle section a hand-damped metallophone plays two even notes a bar against the 9/8's three.
  It's the only part with no human timing: it sits exactly on the grid. **Does it read as someone cold and correct
  stepping on board, or just as a rhythm mistake?** If it sounds wrong rather than cold, it can fall in line with
  the threes.
- **The derelict (about 48–62 s):** the harmony darkens to C-flat and A-flat minor (the minor key's chords), the
  flute stops, the rigging thins to one pluck per beat, and a ship's bell heard over water rings twice off the beat,
  as if the roll were ringing it. Then one long flute note. **Does the passage make you think of a ship with nobody
  at the helm?** It shouldn't sound like danger yet: the boss cue (`spar_wraith`) is the danger.
- It should be distinct from the causeway (A minor, bare fifths, a 4/4 walk). Is it? Can you hear the wrap at
  76.2 s?

### (2) The Brine Shoals: walking toward a fire

- **The idea:** low tide over a graveyard of hulls. It's in C-sharp minor, in 5/4 grouped 3+2: a long step and then
  the pull of the foot out of the mud. A big frame drum makes the steps, with softer strokes after each for the mud
  letting go, over a muted bass and a low, groaning string pad. A salvage lute carries the tune and picks its long
  notes in tremolo, like a Saltwright playing on a cold beach.
- **The smoke (about 45–64 s):** a D major chord over a C-sharp bass (one sour, borrowed colour), a large gong, the
  lute at its highest, and sparse crackle like embers. **Does the crackle read as fire, or as clicks in the file?**
  If it's clicks, it either goes or gets darker.
- **Is it heavy without being a battle?** This is the route before the raid and the Inquisitor fight, so it should
  feel wary. The fight has its own cue.
- Does the 5/4 feel like trudging, or does it limp? Can you hear the wrap at 72.7 s?

## M3: Act I zone beds (M3-AUD-16)

`ambience/tamsule_port.ogg`, `tamsule_bell.ogg`, `brine_shoals.ogg`, `pemakar_terraces.ogg`, `ashcrown.ogg`,
`corrow_seawall.ogg`: 40–46 s loops at −26 LUFS, meant to sit under the area music. Listen at a low volume, the way
they play. Does each read as its place (a harbour; the inside of a great bell's arena; mud and smoke; running
terrace water at a festival; a mountain under falling ash; a hard sea wall)? **Please check the wrap of
`tamsule_bell.ogg`** (every 40 s): the Vorbis encoder leaves a tiny step at the file's ends that this quiet, humming
bed shows more than the others; if you hear a tick, I'll mask it.

## M3: the battle's motion (M3-AUD-13)

Files in `assets/audio/sfx/choreo/` (from `assets_src/sfx/choreo_sfx.py`). In the game they sit **under** the hits
you already know (`assets/audio/sfx/battle/hit_*`): play a hit right after its accent to hear the pair.

- **Whooshes** (`whoosh_melee_*`, `heavy_*`, `cast_*`, `throw_*`, `guard_*`): each crests about 0.1–0.3 s in, on the
  blow. Do they read as air moving, or as hiss? Is the heavy one heavy without being a roar?
- **Weapons** (`accent_*`): Rhen's twin hooks with the lantern's glass ticking (`hooks`), Asha's wooden staff with the
  shell-bell (`staff`), Toma's spear and his old turtle-shell shield (`spear`, `shield`), Ysolde's book struck flat and
  her focus releasing a cast (`book`, `focus`), Kerrid's anchor-cleaver breaking armour (`cleaver`), claws, teeth,
  and the Drownbell's hood. **Can you tell the four heroes apart with your eyes closed?** Are any of them too quiet
  or too clicky to matter under a hit?
- **Footfalls** (`step_sand_1..4`): damp battle sand. Do four in a row sound like one person, not a machine gun?
- **The KO** (`ko_collapse_*`): the knees, then the body into shallow water. Too much splash for a sad moment?
- **Swell accents** (`swell_rhen`, `asha`, `toma`, `ysolde`): short and bright, over each finisher's own sound. Do
  they feel earned, or like a slot machine?
- **The Drownbell:** `toll_wave` is the ring passing the party (play it right after `battle/drownbell_toll.ogg`);
  `flood_surge` the surge attacks; `flood_brace_*` the water at the party's legs as they brace.
- **Ilun:** `vowbound_beckon` (Asha's call: a breath rising a fifth), `vowbound_rise` and `vowbound_rise_long` (the
  first call's slow rise), `vowbound_sink` (dismissed), `vowbound_fall` (struck down, drawn under). Does the fall
  sound sadder than the sink?

## M3: battle stings (M3-AUD-18)

`sfx/battle/sting_tideline.ogg` (the tide line rising before a battle), `sting_bark.ogg` (a breath under the lead-in
line), `sting_boss.ogg` (a boss's title card) and `sting_boss_bell.ogg` (the Drownbell's). Does the boss sting read as
"this one matters" without crowding the battle music's first bar (the music dips 5 dB under it for 3.5 s)? Is the
Drownbell's drawn-in swell too long before the toll (1.1 s)?

## M3: creature voices and movement (M3-AUD-14)

194 short sounds in `assets/audio/sfx/creatures/`, from `assets_src/sfx/creature_sfx.py`: each creature's idle, attack,
hurt and death, and how it moves. Nothing here is a recording or an imitation of one. Each creature is a small
physical model: shell modes for carapace taps and claw snaps, stick-slip for creaks and scrapes, Minnaert bubbles for
froth and gurgles, a formant voice (an additive throat under vowel-like resonances, with roughness and a growl's
subharmonic) for anything that calls, and filtered noise bursts for wings. Voices are at −18 LUFS momentary, idles
−20 and movement −21. In battle the hurt and death play 3 dB under the hit and KO sounds, just behind them. Listen
in this order, a creature at a time (`ffplay -autoexit <file>`):

| # | Files | What it should be |
|---|---|---|
| 1 | `reef_crab_*` | A 1.4 m crab in a coral shell: mandible chatter and froth, a scrape then a hard claw snap, a shell knock and a panicked chatter when hurt, legs rattling to a stop when it dies, and a stony skitter |
| 2 | `lantern_eel_*` | A low throat purr with bubbles from the gills, and a pure, slowly beating glass hum for its lure. A water rush and a jaw snap. Its death is a long moan sinking under a bubble trail, the lure bending down as it goes out |
| 3 | `gull_harrier_*` | A storm-fattened sea-bird: a rasping two-note call, a dive (the wings folding) into a screech and the talons raking, heavy wingbeats |
| 4 | `spawn_polyp_*` | Soft wet mouths: suction pops opening, gurgles, a low wet moan under it, a squelching lunge |
| 5 | `drownbell_*` | The bell's body, not its toll: the six legs ticking wet under the rim, the rotten rope creaking, a faint dark hum of the bronze. Rearing for `hood_slam`, the bronze grinds on its lip. Hurt is a damped bronze clank. In its death the bell's ring bends down as it drowns |
| 6 | the Act I foes | `hullgnaw` (the eel through ship's ribs: timber creaks and crunches), `glassfry` (a cloud of tiny glass ticks that tightens to strike), `tower_limpet`, `oil_slug` (slower, viscous), `bottle_hermit` (taps ring on its lamp glass), `sail_leech` (wet flaps), `spar_wraith` (wind through the shrouds as its moan, rope whips, timber collapse), `ashwing` and `flue_moth` (papery flutter, dust), `slag_tortoise` (a hiss and a horny beak), `cinder_matron` (stone grinding, magma bubbling, the crust coming down), `vein_sparker` (arcs and a hiss), `shoal_skipper` (mud slaps and a wet gulp), `raid_hound` (a growl, a bark, a yelp, a whine, paws on deck boards and the harness), `tide_crawler` and `scuttler` (wet spawn crawlers), `squall_wing` (a gull heard through rain), `undertows_reach` (a mass of water and a groan below hearing's floor) |

**What to listen for:**
- **Does anything sound like a recording of a real animal?** It shouldn't, but the hound's bark and the harrier's
  call are closest. If one sounds like an actual dog or gull, say so and it gets pushed further from the animal.
- **The voices are the part most likely to sound synthetic:** a buzzy or "talking robot" throat means fewer
  harmonics and more breath. The eel's purr and the polyp's moan are meant to be felt more than heard.
- **Movement repeats on every action.** Do the skitters, wingbeats and squelches get tiring after ten turns? If one
  does, it gets quieter, or a third variant.
- **Bright clicks:** the crab, scuttler and bottle hermit skitters and the glassfry are click-heavy by design. Do
  they read as legs and glass, or as digital clicks?
- **Variants:** the wreck crab, wallcrab, wall polyp and stormgull play their parent's set at another pitch. Is
  that distinct enough, or does each want its own?

## M2: the menus' pages (M2-AUD-14)

Seven UI sounds in `assets/audio/sfx/`, from `assets_src/sfx/menu_page_sfx.py`, in the palette of the M3 menu set
(bars on D-A-E, dry paper, soft air, a small room): `ui_item_use`, `ui_item_sort`, `ui_formation_pick`,
`ui_formation_swap`, `ui_customize_open`, `ui_craft` and `ui_map_pan`. All at −20 LUFS momentary; the pan plays 6 dB
under that in game. Listen with `ffplay -autoexit <file>`, then next to `ui_cursor`, `ui_confirm` and `ui_equip`.

**What to listen for:**
- **Do they belong with the menu set?** `ui_craft` should read as a smaller cousin of `ui_lattice_node`, and
  `ui_formation_swap` as a relative of `ui_equip`, not as a new instrument.
- **Repetition:** a player uses five tonics in a row and re-sorts the bag twice. Do `ui_item_use`'s bubbles or
  `ui_item_sort`'s flicks get tiring? If so, they get quieter, or a second variant.
- **`ui_map_pan`** plays at most every 110 ms while the map moves. Does it read as paper sliding, or as noise
  hiss? Does the train sound like a slide or like a ticking clock?
- **`ui_customize_open`'s low hum:** is it too heavy for opening a list?

## M3: Act I temples (M3-AUD-19)

Three loops for the temples and the Bell's galleries. None of their scenes is built on this branch yet, so for now
you can only hear them on their own. The scenes are in act_outline.md (Ch5, Ch7 and Ch8). About 4 minutes in all.

| # | File | Length | Plays |
|---|---|---|---|
| 1 | `music/ashcrown.ogg` | 80.0 s loop | Ch5: the Ashcrown temple, the Cinder Matron's home, under the falling ash |
| 2 | `music/coilspire.ogg` | 73.0 s loop | Ch8: the Coilspire temple at Corrow, the beacon's trial, before the storm |
| 3 | `music/tamsule_bell_galleries.ogg` | 80.0 s loop | Ch7: the galleries inside the Tamsule Bell, around the arena (not the match) |

### (1) Ashcrown: the heat under the stone

- **The band:** a breathy flute in its warm middle plays a call (Bb, C, Db, held) and its falling answer. Under it
  is a dark, low string pad that swells and sinks with each chord: the embers. Soft copper bowls, long and slowly
  beating, fall in short figures where the flute rests: the copper veins carrying the strike down. Kettle gongs sound
  on 1 and 3, a large gong every four bars, and a big drum's slow heartbeat. In the second half the men hum Bb under
  it, and in bars 13-16 a low rumble of the plume swells twice.
- **The key:** B-flat minor, 4/4 at 60 BPM, the slowest metred loop in Act I. Every note of the Terraces' five-note
  scale is in this key, so the temple should sound like the same mountain, higher up and closer to the fire. **Does
  it feel warm-dark and ritual, or only slow?** If it drags, I'd add bowls before I'd raise the tempo.
- **The plume rumble** is meant to be felt more than heard. On speakers without bass you may not hear it at all.
  If it does come through, does it read as the mountain, or as wind noise?
- Is the drum heartbeat too regular? It should be a procession, not a clock.

### (2) Coilspire: everything climbs, nothing arrives

- **The idea:** one two-bar flute cell (up a fourth, then back down by step) comes back a step higher each time,
  the way the beacon's fire climbs the spire. Under it, damped copper bars run eighths in a 3+3+2 pattern, each group
  starting a step higher (the flues opening and shutting). A bass and drums keep the same 3+3+2. In the middle
  section men and women hum the rising bass in long notes, and the music brightens for one bar into B major. In bars
  21-24 the flute climbs to its top note (the fire at the top). Then it falls away, and C-sharp major leads back to
  the start.
- **The key:** F-sharp minor, 4/4 at 92 BPM. That is the dominant of the seawall's B minor, so it should sound like
  Corrow's question left open. **Is it tense without being a battle?** If it sounds like a fight, the drums are too
  forward. If it sounds calm, the flues are too soft.
- **The surf** washes against the spire's foot every two bars, low and wide, left then right. Is it salt and stone,
  or a hiss?
- The flute is high and hard-blown here (up to E6). Is it a wind in the flues (good), or shrill (bad)?
- Mastering: the big drum's hits take up to about 2 dB of fast limiting on 0.3 % of samples. Do the downbeats sound
  flattened?

### (3) The Bell's galleries: inside an instrument

- **The idea:** the drone is the Tamsule Bell's own partials, held: its hum, prime, minor-third tierce, fifth and
  octave. A struck bell also has a major third an octave higher up (the deciem). In the middle eight bars the minor
  third sinks and the major third rises, so the music turns from A minor to A major and back. The Bell itself, the
  same padded bell as in the Tidecup and the town, strikes at bars 1, 13 and 21.
- **The band:** a slow flute song in 3/4 at 54 BPM, with no drums at all. Each long note comes back a beat later
  from the other side, darker and quieter: the sound running round the gallery's curved wall. Soft glass bars double
  the song's long notes an octave up in the second half, and a low plucked string marks each root.
- **The key question:** does it feel resonant and hollow, like being inside a bell, or just empty? Does the echo
  read as the room, or as a mistake?
- **Tuning:** the drone's thirds are a bell's (a just minor third, about 15 cents sharp of the piano's C), so the
  flute's C and C# rub very slightly against it. This is deliberate. If it sounds out of tune rather than like
  bronze, I'll tune the drone to the flute.
- Does the major middle section sound like a memory (Toma played here as a boy) or like a different piece?

**For all three:** can you hear the loop wrap? The seams are at 80.0 s, 73.0 s and 80.0 s. Each file starts a
sixteenth before its first downbeat, so the wrap falls between notes.

## M3: the Ch6 boss, the Stillguard Inquisitor and the raid-hound (M3-AUD-20)

`music/stillguard_inquisitor.ogg`: a 4.6 s intro and a 73.8 s loop (78.5 s in all), from
`assets_src/music/stillguard_inquisitor.py`. The fight isn't built yet, so for now it can only be heard on its own.
The scene is act_outline.md Ch6: an Order raid burning a Saltwright salvage camp in the Brine Shoals. It is the
first fight against the Order's own people, and Toma refuses to strike to kill. So it must not sound like a monster
fight. It should sound lawful and cold, with sorrow under it.

- **The brief in sound:** a march in A minor, 4/4 at 104 BPM. It keeps to the white notes (the Order's C major seen
  from below) except for the G# of the cadences. The drill drums are barely humanized (1 ms), unlike every other
  battle cue: the Order keeps exact time.
- **The band:** frame drums in a strict march pattern, with the big drum on 1 and 3. Shields (a hand-damped kettle
  gong under a hard slap) strike on beat 4, and three times ("Hold. On my shield.") at each cadence. A low piano
  marches in octaves on eighths. The edict theme is on piano in octaves, marcato. A men's hum holds the chord roots
  under the whole loop, because the Order hums and only Cantors sing.
- **The people (bars 13-20):** the drums thin to the dum. A breath flute plays the lament in C major over
  F C G Am, and women hum above the men. In A'' (bars 25-32) the edict drops an octave and the flute's counterline
  sits over it: law and sorrow at once.
- **The hound (bars 21-24):** the drill breaks into running sixteenths, the bass snaps through the flattened second
  (Bb) in eighths, and the shields strike on 2 and 4.
- **The key questions:** does it read as **people** (the Order's discipline) and not a beast? Does the sorrow
  come through, or is it only stern? **Does the strict drill sound disciplined, or mechanical?** If it's
  mechanical, I'd add a little timing spread before changing the pattern. **Is the piano edict cold, or thin
  against the drums?** If it's thin, I'd double it on the flute an octave up in A rather than raise the piano.
- **Do the shields sound like a struck shield,** or like a pot or a gong? If they're a gong, the plate gets shorter.
- **Can you hear the loop wrap?** The seam is 73.8 s after the intro, a sixteenth before bar 1's downbeat.
