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
*Masked (M3-AUD-835):* a seam report over all 78 loops found this bed alone near click level (the decoded wrap was 9.7
times an ordinary sample step). The loop now starts at its quietest moment (0.12 times). Listen for the wrap anyway.

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

## M3: Act II sketches I (M3-AUD-804)

Six **sketches**, one per Act II place in Ch10-12. They're for judging direction: is each place's colour right,
and do the six feel like one act? They aren't finished cues. None of the scenes exists yet, so for now you can only
hear them on their own. The scenes are in act_outline.md (Ch10, Ch11, Ch12), and the places in bible §5.5-5.7 and
§8. Each is a seamless loop of about a minute (about 6 minutes in all). Act II's colour is overcast, storm,
moonlight and cold blue stone, so all six sit darker and slower than Act I, except Quellan, which is the warm room
after the cold road.

The new instruments are in `assets_src/music/act2_voices.py`: a fen reed pipe; the Kirru's whistle, root-harp,
water-gourd and tongue-clicks; a glass harmonica (Sefir's recipe); the Lamp Engine's stroke and its hum; a highland
ten-string lute; woolback bells; and seamless textures (insects, wind, the pass-cords, the deep's cold).

| # | File | Length | Key, metre | Plays |
|---|---|---|---|---|
| 1 | `music/ossa_fen.ogg` | 61.9 s loop | G Dorian, 4/4 at 62 | Ch10: Ossa Fen, the mangrove channels |
| 2 | `music/reedhollow.ogg` | 61.5 s loop | the Kirru mode on A (A B C# D# F#), 5/4 (3+2) at 78 | Ch10: Reedhollow, the Kirru village |
| 3 | `music/sunken_vey.ogg` | 62.6 s loop | E-flat Dorian, 3/4 at 46 | Ch11: Sunken Vey, the drowned galleries |
| 4 | `music/lowlight.ogg` | 62.1 s loop | C minor, 4/4 at 58 | Ch11: the Lowlight temple and the Lamp Engine |
| 5 | `music/keth_pass.ogg` | 62.6 s loop | E minor, 6/8 at 46 | Ch12: Keth Pass, the mountain route |
| 6 | `music/quellan.ogg` | 62.6 s loop | F major, 4/4 at 92 | Ch12: Quellan, the highland town |

### (1) Ossa Fen: humid and still

- **The band:** a nasal double-reed pipe (new) plays a low, swaying tune over a still drone on G and D and a very
  dark string pad. A muted low string on 1 and the "and" of 3 is a pole finding the mud. Insects are made from
  texture, not samples: clustered high chirps, a faint bed, and now and then a far frog's purr. Drips fall from the
  roots. In bars 13-16 the pipe stops and a low, soft flute answers.
- **The key:** G Dorian. Its E natural is the fen's colour, heard in the C major chords. **Does it feel humid and
  still, or only slow?** **Is the reed pipe a reed** (nasal, a little buzzy, a touch flat at the ends of long
  notes), or does it sound like a cheap synth oboe? That's the biggest risk in this sketch.
- **The insects:** do they read as insects in the heat, or as hiss or tinnitus? If they're tiring over a long
  explore, they come down or thin out.

### (2) Reedhollow: a people with their own music

- **The idea:** the Kirru aren't human, and the Order calls them soulless. Their music shouldn't sound like the
  coast's. So no metallophones and no D pentatonic (Haluna's), and a mode of their own: **A B C# D# F#. It has no
  fifth**, so it never sits down on a home chord. It floats, rises, and ends its phrases in silence instead of
  cadences.
- **The band, all new:** two **whistlers** (a low, near-pure whistle that glides between notes and slides *up* into
  its long ones, with a tongue-click at each phrase start), the first left and the answer right. The **root-harp**
  is gut strings on a mangrove-root frame over the water: on some notes the player presses the string up into
  pitch after the pluck, so the harp rises too. **Water-gourds** play on the two group starts of the 3+2 bar, and
  **tongue-clicks** on the offbeats are the Kirru talking. In bars 11-14 the clutch hums a wordless line that rises
  one step a bar and never comes down: the farewell-tide's *shape* (not the song itself; that scene isn't scored
  yet). Bar 16 is only clicks and the harp's root: the backs turned.
- **Key questions:** **does it sound like a people with their own music, and not "exotic"?** Is the fifthless mode
  beautiful, or does it just sound unresolved? Do the whistles read as voices (good) or as a theremin (bad)? Is the
  5/4 unhurried, or does it limp?
- The farewell-tide is meant to carry the Eighth Verse without knowing it (bible §7). This sketch doesn't decide
  that melody. If you like the rising line, it's a candidate seed.

### (3) Sunken Vey: under the water, among the dead

- **The band:** a glass harmonica sings a slow song in 3/4 at 46 (the slowest 3/4 in the game). From bar 9 a
  second glass doubles its long notes an octave below. Everything else is heard as if through water, low-passed
  hard: a drone on Eb and Bb, a very dark pad, a drowned bell at bars 1 and 9, and a low root pluck every other
  bar. The conduits' bound light is a faint pair of high tones that swell once every two beats. Bubbles rise in
  short strings.
- **The key:** E-flat Dorian. The C natural (the top of the song over A-flat major) is the light still in the
  conduits. **Does it sound submerged, glassy and dead-but-gorgeous, or just muffled?** Is the conduits' pulse
  audible enough to read as *light*, or is it lost?
- **Glass here and in Sefir's motif:** the glass harmonica is the game's voice for glimmer, and Sefir's theme uses it
  too. Does it point at the Order too early? If so, I'll swap it for bowed glass bars.

### (4) Lowlight: a dead machine still keeping time

- **The engine:** a muffled piston stroke through water on every beat, with a valve clank. Beat 4 limps late,
  beat 2 stutters every fourth bar, and in the last bar the engine **stalls for two beats** before it catches again
  on the loop's downbeat. Under it is the conduits' choked hum on C, which flickers and sometimes nearly fails, and
  a very low heave of the deep's cold. Glints of drowned glimmer drift down in register like silt.
- **The motifs (the game's own, developed):** the low flute plays **the Kirru call from Reedhollow**, moved to C
  and sinking at the end: Nhoa is Ressa, the only Kirru Cantor, held at the foot of the well-shaft. The glass plays
  **the Hush's outline** (the long held note, the fall of a third, the turn a sixth below) in C minor: the
  Cantor's song she was given. In bars 12-15 they sound together and don't quite agree (the call's E against the
  Hush's E-flat). **Is that clash the point (Kirru against Order, in one drowned woman), or does it just sound
  wrong?** If it's wrong, I'd keep the two apart.
- **Is the pulse dead (mechanical, wrong, tired) or just a drum?** Does the stall read as the machine failing, or
  as a glitch in the file? Pell kneels before his sister in this temple. Does the cue leave room for that?

### (5) Keth Pass: cold, wind-borne, wide

- **The band:** two breathy pipes, hard left and right, play the tune **in hocket**. Each plays every other note,
  so the tune exists only between them. The wind never stops. The pass-cords whistle in it: very narrow bands of
  wind-noise on E, G, B and E, each swelling on its own gust. An open-fifth string pad sits wide, a big drum sounds
  far below every four bars, and a soft frame-drum step falls on the second dotted quarter. In bars 13-16 one pipe
  plays alone, lower and slower (C D G Em). In A' (bars 17-20) the hocket goes up an octave.
- **The key:** E minor, 6/8 at 46 dotted quarters, the slowest 6/8 in the game. **Does it feel high, cold and
  huge?** Does the hocket sound like two players, or like a broken-up line? **Do the cords sound like cords
  singing,** or like a whistle-tone fault? Is the wind tiring?
- **Toma notices Kerrid's breath doesn't fog.** That beat isn't scored here; the verse (bars 13-16) is the place
  a later cutscene cue could branch from.

### (6) Quellan: warm against the cold

- **The band:** a warm breath flute in its middle plays a tune in F major (the only cue in F major). A second flute
  a third below joins in A'. The **ten-string** (new) is a small, deep-backed lute of paired wire courses, strummed
  long-short-short on every beat. Under it are a fingered bass on 1 and 3, a big drum on 1, and a frame-drum slap
  on the "and" of 2. Outside, the woolbacks' wooden-clappered bells clonk in small, uneven clusters. A C7
  turnaround in the last half-bar leads home.
- **Key questions:** **is it warm (a hearth after the pass), or just cheerful?** The Ullari are stoic about death,
  but at home they're a town. Does the strum read as a highland lute, or as a ukulele? (If it's a ukulele, the
  body gets deeper and the courses lower.) Do the herd bells sound like animals passing in the street, or like a
  clock?
- Quellan sits next to Keth Pass (E minor, 6/8, cold). Does going from one to the other feel like coming inside?

**For all six:** can you hear any loop wrap? Every file starts a sixteenth before its first downbeat, so the wrap
falls between notes. And as a set: **do the six sound like one act** (darker, colder, slower than Act I) **and like
six different places?**
## M3: Act II sketches II, Ansedra to the Drowned Choir (M3-AUD-805)

Six **sketches**: loops to judge the direction by, not finished cues. None of their scenes exists yet, so for now
you can only hear them on their own. The scenes are in act_outline.md (Ch13 to Ch16). About 6 minutes in all.

| # | File | Length | Plays |
|---|---|---|---|
| 1 | `music/ansedra.ogg` | 61.0 s loop | Ch13: Ansedra, the holy city, gold and lacquer |
| 2 | `music/lamp_archive.ogg` | 61.0 s loop | Ch13: the Lamp Archive, the three days of reading before the wedding |
| 3 | `music/peace_wedding.ogg` | 61.4 s loop | Ch14: the wedding in the Lacquer Court at dusk, before the trap is sprung |
| 4 | `music/unlamped.ogg` | 61.2 s loop | Ch15: the open sea at night, aboard the bridal barge with no lamp |
| 5 | `music/pale_rim.ogg` | 61.2 s loop | Ch16: the Pale Rim, days of wading through white shallows |
| 6 | `music/drowned_choir.ogg` | 61.3 s loop | Ch16: the Drowned Choir, the stone figures in the water |

### (1) Ansedra: gold, and nothing alive under it

- **The idea:** the bowls (gilded bars that beat slowly, like a gamelan) ring the same four notes on every bar, and
  never change the pattern, only the chord. Those four notes are Sefir's motif reordered, so the city rings with its
  Warden before you hear him. A breathy flute plays a court tune over a warm pad, with the Order humming an open
  fifth on C under everything. In bars 11-14 Sefir's own motif comes in on his glass harmonica (the same instrument as
  `sefir_theme`), with the congregation humming it an octave down. Its wrong note, C#, is held until the chord under
  it turns to D-flat major seventh: for a bar the wrong note becomes the floor, all gold, with nowhere to go.
- **The key:** C major (the Order's key), 4/4 at 63 BPM. **Is it opulent and a little hollow, or just pleasant?** If
  it's too pleasant, I'd thin the pad's thirds before touching the tune.
- Does the D-flat bar sound like gilding, or like a mistake?

### (2) The Lamp Archive: the truth on paper

- **The idea:** a grand piano alone in a big, dry room, with a dark pad far under it and three page-turns a loop.
  The left hand is the ledger: a low fifth on each downbeat, and the same soft D ticking on beats 2 and 3 for the
  whole loop (the same hand signing for four hundred years). The right hand reads the Hush's first phrase in D minor
  and stops where the theme would climb. In bars 7-11 the phrase is read twice at once, an octave apart and a bar out
  of step, and the two copies disagree. That is Liss laying the pages side by side. At the end comes Sefir's motif,
  and in D minor its C# is the leading tone, so for the first time it resolves, up to D.
- **The key:** D minor, 3/4 at 59 BPM. **Quiet, dusty and uneasy, or only sparse?** Is the D tick a pen and a
  column of names, or a clock? If it's a clock, it gets less regular.
- **Do the page-turns read as paper,** or as noise bursts? They're mixed far back on purpose.
- Can you hear Sefir's motif resolving at the end, and does it feel like a discovery?

### (3) The peace wedding: a dance that is a trap

- **The idea:** a real court dance in 3/4. A plucked zither plays bass on 1 and chords on 2 and 3, a flute plays
  the tune, gilded bars double its downbeats, and a soft frame drum plays. The first sixteen bars are honestly
  lovely. Then in bars 17-24 the harmony slides to E-flat major and C minor, and a damped low gong starts stepping
  every *two* beats, against the dance's three: something keeping a different time in the same room. The Order
  hums Sefir's motif in G, and its last note (G#) is held over C until it becomes the A-flat of C minor. When the tune
  returns, its third bar has caught the minor, and it ends on the dominant, never on G.
- **The key:** G major, 3/4 at 88 BPM. **Do you want the peace too, in bars 1-16?** If the A section isn't
  beautiful, the trap doesn't work.
- **Does the two-against-three gong read as wrong footsteps,** or as a mistake in the drum part? If it's the
  latter, it gets lower and further away.

### (4) Unlamped: the sea at night, no lamp

- **The idea:** no pulse at all; nobody is rowing. A sea of filtered noise swells once a bar. A low bowed E-flat
  drone sits under a pad that rocks between E-flat minor and C-flat, like a barge with nobody steering. A low,
  breathy flute keeps a vigil rather than singing. The sea-glow is soft glass bars, always rising (the held dead
  come up off the water toward Kerrid), sparse at first and gathering in bars 8-11. The flute's last note is A-flat,
  left unresolved.
- **The key:** E-flat minor, the darkest in the score, notated 4/4 at 51 BPM in 13 bars (an odd number, so the
  loop never settles into pairs). **Is it dark and grieving, or only dark?**
- Is the sea a sea, or a hiss?
- Do the rising motes read as light coming up off the water?

### (5) The Pale Rim: almost silent

- **The idea:** mostly air. A halo of high, pure tones beats slowly, like glare off white water. Far down there is
  an open fifth on E, and there are no thirds at all for most of the loop: no colour, the white. The only motion is
  the party wading: five walkers, a soft splash at each step, a little irregular, the last one a step behind
  (Kerrid walks last). A flute, very far off, plays three short calls in thirteen bars. In the third call it
  touches A# and G#, the loop's only third.
- **The key:** E (no third), 4/4 at 51 BPM. **Vast and bleached, or empty?** It's played at the same loudness as
  every other cue, so "almost silent" here means sparse, not quiet. If it's too present, it could be the one cue
  that sits a few dB under the others (that would need an ADR on mix.md §2).
- **Does the wading sound like water around legs,** or like footsteps on gravel?
- Is the halo restful, or a whine? If it's a whine, the top two partials go.

### (6) The Drowned Choir: the Hush, sung by the stones

- **The idea:** everything is heard through water. Men hum the roots and women hum the Hush's first phrase, slowed
  right down. In bars 13-16 the mouths open: six voices sing open vowels (oo to oh to ah) on F major and then E
  major, and one distant alto sings the Hush's first three notes. The water's filter opens slowly toward those bars
  and closes again after them. A deep gong sounds at bars 1 and 9, and a few bubbles rise.
- **The key:** A minor (the Hush's key), 3/4 at 47 BPM. **Awe and grief, or just murk?**
- **The sung voices are synthesized,** and a synthetic voice is the thing most likely to sound uncanny. Are the open
  vowels in bars 13-16 a choir of stones, or a robot? If they're a robot, they get further back, or go to hum.
- Is the Hush recognizable at this tempo, under the water?

**For all six:** can you hear the loop wrap? Each file starts a sixteenth before its first downbeat, so the wrap
falls between notes. And **do they sound like the same game as Act I** (the same flute, bars, hum and pad), while
each sounds like its own place?

## M3: village and wildlife life (M3-AUD-814)
Heard in Haluna once claude/creatures merges (or on creatures' `_tests/npc` and `_tests/wildlife` stages). Listen for:
- **Murmur turns:** two villagers chatting should read as people talking out of earshot, never as words, and never as
  a loop: a turn starts with its speaker's turn and two voices alternate. Is −26 LUFS (momentary max) too present
  next to the dialogue blips?
- **Work:** the net-mender's twine and knot, the sweeper's broom on the chapel stones, the stall's bowls and jars,
  the bowl's pestle. Every 2.5–5.5 s: does it feel like steady work or like a metronome?
- **Gulls near:** brighter than the bed's far gulls; do the two layers sit together? Takeoff claps should be soft.
- **Crabs and fish:** very quiet ticks and plips, heard only up close. Too faint to notice is better than too loud.

## M3: battle impact weight (M3-AUD-816)
Heard once claude/battle-presentation merges, in any fight. Listen for:
- **Tiers:** a medium blow should thicken the hit, not double it; a heavy one should land as the hit-stop releases.
  Is the crushing tier's debris too much on every crit?
- **The hit-stop duck:** −6 dB of music for about 0.15 s. Is it felt as a held breath or as a dropout?
- **The KO slow-mo:** the air drawn down and the one heartbeat under the last foe's fall, with the music ducked
  −9 dB. The victory sting should follow cleanly.

## M3: the slice's cutscenes (M3-AUD-817)
Play the prologue and Cutscene A in Haluna. Listen for:
- **The prologue's room tone (iskarra_dusk):** the city should feel enormous and empty: water on stone, the towers'
  faint singing in the gusts, a far drip. Is the singing too tonal (it is two quiet tones a fifth apart)?
- **The lantern catching** under the line, "the only flame in the frame": a breath of flare, then a small steady
  flutter. Does it crowd the voice?
- **The glimmer lift** after the line: tiny chimes drifting upward, never a tune.
- **Steps in cutscenes:** Rhen crossing the plaza. Wet stone in the prologue is `stone`; Haluna's beach is sand,
  its shallows water.
- **Cloth on `look_at`:** very quiet (−27). Too much over 63 uses?

## M3: Act I cutscene cues (M3-AUD-818)
Sixty-eight `@sfx` cues, heard in their cutscenes (the F8 chapter select reaches them). The ones to hear first:
- **Ch1 undertow_wall_roar:** the sea coming in, under "Go! Don't look back, go!". Big enough?
- **Ch7 crowd_up:** ten thousand people saying "Up." low and together. Does it read as one word from a crowd, or as
  a wash? The second use is louder, and should sound ragged.
- **The hums and songs:** Neme's hum at the wake, Asha's lullaby on the wall, Pell's storm call, and the figure's
  song in the current. These are synth voices, so their timbre is the risk.
- **Ch8's set piece** (the Reach, the breach, the stone falling): the loudest cues in Act I (−15 to −17). Are they
  too much against the music cues there?
- **Ch9 staff_bell_shells and harbour_lap:** the Ebbing's quiet; nothing should crowd the dance.

## M3: Ch4 and Ch7 scene cues (M3-AUD-820)
Six cues the Act I scripts already call with `@music <id>` (the F8 chapter select reaches them once claude/act1-chapters
merges). About 6 minutes in all.

| # | File | Length | Plays |
|---|---|---|---|
| 1 | `music/the_long_way_round.ogg` | 80.2 s | Ch4 C4-04/05: the village's farewell song at Asha's wake (**final**) |
| 2 | `music/hearer_hum.ogg` | 61.0 s loop | Ch4 C4-06: the dock in the dark |
| 3 | `music/ysolde_theme.ogg` | 61.0 s loop | Ch4 C4-07 The Ink, C4-09 the gangplank (sketch) |
| 4 | `music/name_board_home.ogg` | 58.2 s | Ch4 C4-14: the name-board |
| 5 | `music/tavi_kell.ogg` | 32.7 s | Ch7 B03: after "She couldn't swim, Tavi." |
| 6 | `music/oruvel_theme.ogg` | 59.5 s | Ch7 B09: the Empty Moorings |

### (1) The Long Way Round: a major-key farewell
- **The tune** is original, F major, 4/4 at 88, one note per syllable of Narrative's four #sung lines; every stressed
  syllable falls on beat 1 or 3. One voice starts it (012); the village joins on 013 (a second voice on the tune and a
  women's harmony a third under); the men's roots join on 014; 015 peaks on "love" (G5 over B-flat). Then 014 again,
  softly, under Rhen's lines to Toma; 021 (015's words) over Asha's face; and a slower tag on "on the tide".
- **The voices are breath flutes shaped by vowels** ("ah" lead, "oh" harmony, "oo" men), as the Hush's first verse
  does, until voices are settled. **Does it sound like a village singing, or like a flute band?** Can you hear the
  words' rhythm in it? Is it singable after one hearing? **Does the major key make it worse?**
- **Markers** (s, for `@wait music=`): 012 2.20, 013 13.25, 014 25.08, 015 35.79, the 014 repeat 47.28, 021 57.99,
  the tag 69.16, the last note released 78.18. The script fades the cue in over 2 s, so the first syllable comes
  after the fade.

### (2) hearer_hum: someone humming in the next room
- Water under the dock, slaps on the pilings, the far wake (voices, two drum strokes twice a loop), and under it three
  low voices humming one D, heard **through a wall** (nothing above about 450 Hz). It is mastered to -16 like every
  music cue, so "near silence" is its character, not its level. **Is the hum there without being noticed at first?**
  Is it too present (the hum is about 6 LU under the water)? Does it read as a voice through a wall, or as a drone?

### (3) Ysolde's theme: cold and exact
- A plucked board zither (stiff steel strings, a small lacquered box) over a steady reed drone on C and G; the line
  moves in fourths and fifths, quarters and paired eighths, each phrase ending on a long note; it turns Lydian (F#)
  in its second half. Timing scatter is 2 ms, no vibrato, the drone doesn't breathe; one gilded bowl at bars 1 and 9.
  **Cold and correct, or just thin?** Does the zither read as a zither, or a harp or a guitar? Does it sound like
  Ansedra (the bowls, C major) and not like the Low Reaches?

### (4) name_board_home: the lullaby, true for once
- The beach's star-path phrase (haluna_dawn's right hand) once, slower (46 BPM against 50), with its own harmony and
  the low metallophone doubling the long notes. On the beach it stopped on an unresolved ninth; here the last E
  resolves to D over D major. **Does the resolution land, or sound too neat?** Do you recognise the beach?

### (5) tavi_kell: two notes of Oruvel
- Solo piano, very sparse: a low E, an E minor third, then Oruvel's first two notes (D, B) over an open G, and no G
  after them; a single D later over A minor; a C major chord with the B and D inside it, left ringing. **Is the quote
  recognisable after Ch1 (the squeezebox's opening fall)?** Is it too sparse to hold four minutes of scene? (It ends
  after 33 s; the scene goes on in the market's noise.)

### (6) oruvel_theme: the town on one flute
- Oruvel's A section and the tag's head, on one breath flute, straight and slow (63 BPM), moved up a tone to sit on
  the Tamsule Bell's A, over the Bell's hum as bound glimmer: its partials as steady sines, no breathing, no beating.
  **Does the hum sound bound (still, wrong) next to the galleries' breathing drone?** Is the tune still Oruvel without
  its swing and squeezebox?
## M3: Ch7 and Ch8's scripted music cues (M3-AUD-822)
Six cues that Act I's scripts already call with `@music` (or, for Virel's sting, from battle). The F8 chapter select
reaches the scenes.
- **`tidecup_after`** (Ch7 B07 and the B10 reprise, 57 s): warm strings in A minor. The cellos, then the violas, then
  the violins carry one slow line. It opens on F major, never rests on A, and ends with the violins alone on a held
  E, with a far crowd thinning out under the first half. **Warm, or saccharine?** The strings are the saw-ensemble
  pad, so the risk is a synth-string sound. If it reads that way, drop the inner voices before you touch the line.
- **`tidecup_crowd`** (Ch7 B04, a 62 s loop): the bowl before the match. About sixty talkers (the Reefball crowd's
  voices), a faint ring of the Bell's partials in the roof, the column's weep and an idle frame drum high up. It sits
  at the music level (−16), under `bell_hum`. **Does Liss's line come through it?** If it's too dense under dialogue,
  thin the near talkers.
- **`virel_bound`** (Ch8 B06, a 7.9 s sting): the Hush's first phrase (MEL_A, two bars) on the new spire reed, in
  F-sharp minor over a still F#/C# flue drone. This is the first time a wind plays the theme. **Is the reed a reed?**
  It's additive, so if it buzzes like a synth, lower `spire_reed`'s buzz term or move the 1.5 kHz formant.
- **`virel_summon`** (Ch8 B16, a 5.8 s sting): four sail snaps, the seams catching fire, then the same phrase quicker
  on the reed, and the fire flaring once. **Do the snaps read as cloth, or as gunshots?**
- **`corrow_aftermath`** (Ch8 B18, a 62.4 s loop): rain and one plucked string counting B in groups of 3, 4, 5, 6 and
  3, with each group's last note a step lower, plus one far thunder roll. **Is it counting, or a ticking clock?**
  If it's too regular, the plucks have only 12 ms of jitter; widen it.
- **`seawall_hold`** (Ch8 B10–B14, three 72 s stems): (1) big drums and taiko-like mid drums, the held low strings
  and a cello line that strains a little higher each time round; (2) adds the hoist: the rope creaking on 1 and 3,
  the block knocking on 2 and 4, the pawl, plucks and bass; (3) adds the storm's G as a sub drone under the B minor.
  The steps are about +1.7 and +1.5 LU. **Effort, not triumph?** Listen on speakers that reach 50 Hz: stem 3 is
  mostly below 150 Hz. The limiter takes up to about 4–5 dB off the biggest drum hits.

## M3: Act I scripted cues (M3-AUD-819)
Five cues the Act I scripts already call (`@music`); heard in their cutscenes (the F8 chapter select reaches them).
- **rhen_current_hum** (Ch1 C1-06, the shaft, 15 s): Rhen hums phrase 1 of Dace's current-song (motifs.py) twice,
  the second time fainter as the music crossfades to `oruvel_raft`. Listen for: the two "soundings" (the repeated D)
  heard as two hums, not one note; whether the synth voice reads as a young man humming under his breath or as an
  instrument; the bubbles between the passes (too cute?). It must be recognisable again in `going_under`.
- **going_under** (Ch1 C1-15, 30 s): the roar falls away by ~4.5 s, the song starts at 6.2 s, its last note at
  22.9 s, silence by ~29 s. The vocalise is far down (dark, wet, the top gone). **Timing:** the script
  (ch01_going_under.dlg) holds U11 for `@wait 6.0` and then fades the music, which cuts the song after phrase 1. To
  "cut to black on the song's last note" (beats doc), U11 needs about `@wait 17.4` (Story's call). Is the roar big
  enough after `undertow_wall_roar`?
- **undertow_rising** (Ch1 C1-12/13, Ch8 B07-B09; two stems, a 17.6 s intro and a 70 s loop): the intro is Oruvel's
  squeezebox tune stopping on a C, a breath, then the brass and the cluster rising. Listen for: does the low brass
  model read as brass (trombones and tuba) or as an organ; is stem 2 (the run's sixteenths) a hurry and never a
  charge; the limping second drum stroke. **Ch8 hears the same intro**, so Oruvel's tune plays at Coilspire too (as
  Rhen's memory of the first storm). If Story wants Ch8 without it, that needs a second cue id or a start offset.
  Stem 2 is not switched on by anything yet (music.json `_note`).
- **corrow_night** (Ch9 B01/B03/B08, a 61 s loop): the day tune on the flute, slower, with nothing under it but the
  surf; the Order's hum in broken fragments, far off. Is the hum audible enough to be recognised as the shrine's
  tune, and still "people doing other things"?
- **dawn_road** (Ch9 B09, a 62 s loop): the causeway's pulse, slower and duller, and the causeway's melody on a low
  flute, then a call in open fifths. Does it read as the causeway "come back older", or just as a different cue?
## M3: Act I's Ch5 and Ch6 scripted cues (M3-AUD-821)

Seven cues that Act I's scripts already call with `@music` (and the Kahre sting). Each is heard in its scene on
claude/act1-chapters (the F8 chapter select reaches Ch5 and Ch6), or on its own.

| # | File | Length | Plays |
|---|---|---|---|
| 1 | `music/lanternfall.ogg` | 60.0 s intro + 32.0 s loop | Ch5 B04-B06: Lanternfall, the boats, the weir, the inn gate |
| 2 | `music/hush_second_verse.ogg` | 46.6 s, once | Ch5 B10: the second verse in Ashcrown's anvil court |
| 3 | `music/kerrid_stair.ogg` | 20.0 s, once | Ch5 B05's close: Kerrid falls in at the back of the line |
| 4 | `sfx/kahre_summon.ogg` | 6.0 s sting | Any battle: Asha calls Kahre |
| 5 | `music/liss_theme.ogg` | 61.1 s loop | Ch6 B06-B07: after the barge, Liss and the lantern |
| 6 | `music/raid.ogg` | 92.3 s loop | Ch6 B03: the raid on the salvage camp |
| 7 | `music/shoals_dusk.ogg` | 63.6 s loop | Ch6 B08: the camp on the wreck-ridge at night |

### (1) Lanternfall: the town's own music, thinning

- **The idea:** diegetic. Six flutes play one procession tune in Pemakar's five-note scale on F, each a little out of
  tune with the others (28 cents flat to 33 sharp), a little early or late, two an octave up. Kettle gongs on the
  downbeats, a large gong every four bars, a big drum on 1 and a frame drum on 3. From bar 9 one flute stops each
  bar; the second statement starts with three and the last flute stops mid-tune. Then only the big drum is left, and
  that is the loop (32 s), so the weir scene can run as long as it likes.
- **Is the out-of-tune heterophony a town playing together, or just sour?** If sour, I'd halve the detune spread
  before touching the tune.
- Does the thinning land near the weir? The festival is gone by about 52 s; the boats scene may run longer than
  that on a slow read.
- The inn gate (B06) calls `@music lanternfall` again and so restarts the whole festival, not a distant one. A
  distant mix would be a volume or filter on that call, or a variant cue (a question for Story and Tech).

### (2) The second verse: the Hush to the mountain

- **The idea:** the first verse's voice (a breath flute shaped by an open "ah") over the same A drone, singing the
  Hush theme's second phrase (MEL_B) note for note, one line per sung line, ending on the phrase's own G#, held. The
  plume flashes as *mir* starts (31.54 s) and the thunder comes a beat later (32.59 s), rolling down the mountain for
  about 7 s with the voice still holding under it. Then the voice answers once, far back, G# rising to A.
- **The thunder:** does it feel like the mountain answering (a hammer), or like a storm? Is it too loud under Rhen's
  line? It is level with the voice over its first 3 s.
- **Does the held G# over the A drone sound like a question, or like a wrong note?**
- ch05_kahre.dlg still fires `@sfx plume_thunder` after line 017; with the cue's own thunder that doubles it.

### (3) Kerrid's stair: the tread

- **The idea:** his motif (motifs.py KERRID_STAIR): a low bowed string, D falling to A, one note a stride, over a
  big frame drum on every beat at 48 BPM, the first of each pair heavier. A second string an octave down joins from
  the second statement. No chord is stated, so `goodbye_kerrid` can harmonize the same two notes and slow them.
- **The bowed string is a new synth voice** (a sawtooth with bow noise through a cello body). Does it sound bowed, or
  like an organ? If it's an organ, I'd add more bow noise at the start of each stroke.
- Heavy and patient, or dirge-like?

### (4) Kahre's sting

- **The idea:** a hammer on an anvil, then a white crack of lightning a fifth of a second later, then the Hush's
  second phrase (A G F | G D) on low brass two octaves down, the last D held under the anvil's ring.
- **The brass is a new synth voice** (additive, it brightens as it gets louder). Brass, or a reed organ?
- Does the crack read as lightning (white) or as a gunshot?

### (5) Liss: bright and guarded

- **The idea:** a small, bright wright-built cittern plays the tune in D major over a tide-wheel of seven wooden
  paddles knocking on a seven-eighth cycle, so the wheel's accent walks across the bar and lands a little late. The
  tune never closes on D: E, A, a C major bar, a step aside to B.
- **Is the wheel "a little off the beat", or just wrong?** If it's wrong, I'd remove its lag (32 ms) first and keep
  the seven-cycle.
- Bright and guarded, or just cheerful?

### (6) The raid

- **The idea:** almost no score. Fire (a roar and crackle), a big low frame drum on 1 and 3 at the Order's tempo
  (52 BPM), and men humming the Order's tune (motifs.py ORDER_HUM) in G. The loop leaves its first 23 s to the
  scene's own `stillguard_hum` SFX (the near men), then the cue's men hum it further off, then fire alone, then
  fewer men further still.
- **With the SFX:** does the first hum (the SFX) sit over the fire and drum, and does the cue's own hum sound like
  more men across the camp, not a second recording of the same ones?
- **Calm and frightening, or merely sleepy?** If sleepy, I'd raise the drum before the hum.

### (7) The shoals at night

- **The idea:** the Brine Shoals' field bed thinned to one low reed playing its tune (brine_shoals.py TUNE_A, an
  octave down) with long rests, and the tide coming in over the flats, swelling and drawing back seven times a loop.
  B09 (the burned lamp) cuts it to silence and the `tide_ambience` SFX.
- **The reed** is act2_voices.py's fen pipe with its nasal edge softened. Lonely, or thin?
- Is the tide too loud for a night bed? It carries the bed where the reed rests (about 8 LU under the reed).

## M3: the Act II creatures (M3-AUD-831)

`sfx/creatures/` for the Ch10–12 bosses, the Wakefin and the four Ch10–11 regulars (act2_creature_sfx.py). Each needs
idle, attack, hurt, death and movement. The two that most decide a creature's character:
- **The Avalanche Ram's bellow** (`avalanche_ram_*`): a long throat's formants under a deep nasal voice. Does it
  sound like a huge pack animal and not a monster? Is it too close to any real animal's call?
- **The Mangrove Drowner's moan under its creaking roots** (`mangrove_drowner_*`): does the moan stay under the wood,
  or does it turn the boss into a ghost?

Also listen for:
- The Lamp Engine and the conduit crawler are Lit Age constructs. Their hum is steady (bound light does not pulse)
  until the KO winds it down. Is a steady hum too static over a long boss fight?
- The Wakefin's voice is water only. Does the blade's hiss read as a cut?
- The tannin archer's spit is a sharp jet and its droplets. Is it too close to a gunshot's crack?

## M3: the UI track's new screens (M3-AUD-832)

`sfx/ui_whoosh_in`, `ui_whoosh_out`, `ui_title_reveal`, `ui_save_slot`, `ui_load_slot`, `ui_shrine_travel`,
`ui_reefball_choices`, `ui_reefball_glint` (screen_sfx.py), in the menus' palette.
- **The whooshes** play on every menu page open and close, about 12 dB under the page's own sound. Are they felt
  more than heard? If you notice them, they are too loud. Turn Reduced motion on: they should stop, because nothing
  moves.
- **The title's reveal** sits under the swell: a low glass bloom, then three rising bars as the choices rise. Does
  it make the title feel alive without crowding the swell?
- **Saving and loading:** a stylus mark and a settled bar; the tide drawing back and two falling bars. Can you tell
  them apart without looking?
- **Shrine travel:** a slow glass arpeggio over a rising wash, under the router's fade. Is it long enough to cover
  the fade, and short enough not to linger into the new place?

## M3: the Iskarra prologue soundscape (M3-AUD-847)

`ambience/iskarra_dusk.ogg` now carries the vigil. Now and then, far across the plaza, someone murmurs a few words to
themselves, never close enough to follow (about three times in each 44 s loop, about 15 dB under the wind). Rhen's
lamp crackles at the lamp itself (`cs_lamp_crackle`, heard only near it). Listen at the prologue's own level:
- Do the murmurs make the plaza feel kept by people apart, or do they read as a crowd?
- Does the wick's crackle sit under the dialogue without ticking like a clock?

## The three beds the notes had missed (M3-AUD-855, the listening-note sweep)

A sweep of every music.json cue and every bed in assets/audio/ambience/ against these notes found three beds with
no note. Every cue now has one. Listen at the level they play: −26 LUFS, under the zone's music.
- **`ambience/haluna_day.ogg`** (48 s; Haluna, B02 to B05): village life far off. Palm rustle in the trade wind,
  gull-like calls, distant mallet work on a hull, rope creak, a few people murmuring with no words. Does it read
  as a lived-in village heard from the beach? Now that the villagers have their own positional murmurs and work
  sounds (M3-AUD-814), does the bed's far murmur double them when you stand among them?
- **`ambience/underwater_deep.ogg`** (46 s; Ch1's dive): open deep water. A pressure hum, distant creaks of
  something old and large settling, slow bubble trains from far below, a faint ticking of particles. Is it heavy
  without being muddy on small speakers?
- **`ambience/drowned_tower.ogg`** (42 s; Ch1 inside the drowned tower): the stone shaft resonating in the current,
  surges through the openings, stones ticking down, air leaking in short trains, and the tower now and then
  groaning. Does the groan come too often for a 42 s loop?
