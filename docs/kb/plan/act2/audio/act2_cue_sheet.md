# Act II cue sheet: music, stings, ambience and SFX families (Ch10–Ch16)

- **draft: pre-gate.** Prepared under ADR 0203's "preparation now" (docs only). Nothing here starts until the Lead
  tags `act1-complete`. Until then the Act II audio tasks (M4-A2P-090 … 093, M4-AUD-1001) stay `blocked`. No
  synth source is written for this sheet.
- **Author:** audio (claude/audio), 2026-10-30. **Companions:** [act2_plan.md](../../act2_plan.md) (the work list),
  [act2_finals.md](../../../audio/act2_finals.md) (the existing finals and their sizes), the motif library
  `assets_src/music/motifs.py`.
- **Decided by ADR 0204 (2026-10-30):** `battle_heretic` from Ch14, the Order's one sung lullaby and Liss's sung
  current-song, the `root`, `snow` and `slate` footstep surfaces, and the two Act I reprises (§5). This sheet also
  follows ADR 0204's boss phases (the Ram's `torn_fleece`, the Wakefin's `close_circle`) and its Wakefin (one whole
  animal; `sound_dive` is evasion up with a clear telegraph).
- **Timings are provisional:** no Act II beat sheet or `.dlg` exists yet (act2_plan §5.1). Every scene cue's length
  here is the outline's estimate, and is re-cut to the scene once Story's sheet lands.

## 0. Ground rules for every Act II cue
1. **Original and self-synthesized** (SPEC §2, ADR 0042 §2): every note is written for this project. Evoke a style;
   never imitate a melody. There are no samples, no recordings, no generated audio, and no names or echoes from the
   inspiring series (`tools/banned_terms.txt`). The motifs below are this project's own (`motifs.py`, the Hush's
   `hush_theme_v2.py`), imported by name and never re-typed.
2. **The palette** (tools/audio/synth/; names as the sources use them):
   - grand piano (`grand`) and the older piano model (`piano`); the breath flute (`flute`);
   - plucked strings (`electric.string_pluck` through a body: zither, harp, oud-like; `strings_for`);
   - the metallophone (`metallophone`); tower bells (`bells.tower_bell`); kettle and large gongs (`gongs`);
   - frame drum, big drum and jingles (`drums`); reed and pipe winds (`winds`); pads (`pad.pad_chord`); the lead
     voice (`lead`);
   - sung and hummed voices (`voice.sing`, `voice.hum_ensemble`, `act2_voices.py`); water (`water`).
   - **Who sings:** the Order hums; only Cantors sing (bible §4). The Kirru sing wordlessly.
   - **New voices Act II needs inside that palette:** a bowed string (a friction-excited `string_pluck` body, for
     Kerrid's telling and the Choir), and a frame-drum roll for the people-boss stems.
3. **Levels and files.**
   - Zone loops and scene cues: −16 LUFS integrated. Boss stems: the stack at −16. Stings: −18 momentary max. Beds:
     −26, about 10 LU under their zone's music (act1_loop_check's rule).
   - Seamless loops start a sixteenth before the downbeat (`downbeat_offset_s`), and every music file writes its
     `.loop.json` with bpm, so MusicDeck's on-the-beat changes work (M3-AUD-864). An unmetered piece's cue row says
     `"beat": "free"`.
   - **Storage (ADR 0175):** new Act II audio ships as plain git under `assets/audio/act2/{music,ambience,sfx}/`.
     The 16 finals already in `assets/audio/music/act2/**` stay in LFS. Anything over 5 MB waits for the PC.
4. **Determinism:** every render is byte-identical twice (`render_all.py --determinism`). Every file gets a
   PROVENANCE row, and an `.import` with `beat_count=0`.

## 1. Transition rules (the whole act)
These are the M3-AUD-864 runtime rules, applied to Act II's data. Nothing new is needed in the engine.

| Change | Fade | On the beat? | Notes |
|---|---|---|---|
| zone → zone | `crossfade_sec` 1.5 s | yes: the next beat of the zone loop, ≤ 0.6 s wait | A zone row with `resume: true` picks up on its own beat. Every Act II zone loop is `resume`. |
| zone → battle (regular) | `battle_in_sec` 0.3 s | yes | The encounter's stinger covers the entry. Ambush and preemptive keep Act I's stings. |
| battle → zone | `battle_out_sec` 1.2 s | yes | The zone loop resumes where it left off, on its own beat. |
| zone → boss | the boss intro sting, then the stems at 0.3 s | yes | Phase rows bring stems in over 3–4 s (`battle.phases`), never as cuts. |
| boss phase change | stem fade 3–4 s | stems are one synchronized stream, so always in time | Each boss has `phases` rows (M4-A2P-092). |
| cutscene `@music` | `fade=` (sequencer default 1.0 s; never under `min_fade_sec` 0.2 s) | yes, through the deck | A cutscene cue that should carry into the zone (Act I's dawn → village) ends on the zone's key. |
| cutscene → silence | `@music silence fade=` ≥ 0.2 s | yes | Kept for the act's held breaths: the trap, the reveal, the storm's waking. |
| Vowbound summon | the `*_summon` sting on the Music bus over the battle cue, ducked by the summon | n/a | `battle_sfx.json` `vowbound_stings`. |

**Key relations, so the crossfades sit well:** each chapter's zone, boss and scene cues share a tonic or a fifth
relation (the tables below give each key). A scene cue that hands back to its zone ends on the zone's tonic or
dominant.

## 2. Battle tiers

| Tier | Cue | Exists? | Mood | Instrumentation | Key / tempo | Loop | Transitions |
|---|---|---|---|---|---|---|---|
| Regular, Ch10–Ch13 | `battle_standard_v2` (Act I's) | yes | Continuity: the same road, further along | as Act I | as Act I | as Act I | battle_in 0.3 / out 1.2 on the beat |
| Regular, Ch14–Ch16 (heretics) | `battle_heretic` | **gap (ADR 0204 §9)** | The same fight theme with the Order now hunting them: harder, its warmth gone. **Proposal:** a variant of `battle_standard_v2`, not a new theme, with ORDER_HUM's first cell in the low winds under the riff. | battle_standard_v2's ensemble, minus its bright lead; low reed winds, frame drums, kettle gong | battle_standard_v2's key and tempo (so the two can swap mid-act) | ~75 s | as above. `music.json` `battle.default` stays; the Ch14+ encounters' rows name `battle_heretic`. |
| Creature boss | per boss (§3): `mangrove_drowner`, `lamp_engine`, `avalanche_ram`, `wakefin` | yes (2 stems each) | each its own | each its own | each its own | 74–84 s | boss intro sting → stem 1; the phase row brings stem 2 in over 3–4 s |
| People boss | `malcor_venn`, `abiding_guard` | **gap** (M4-A2P-092) | §3 Ch14, Ch16 | §3 | §3 | ~80 s, 2 stems | as above; `abiding_guard`'s stem 2 is the storm waking early |
| Set-piece hold | Ch14's step-hold (Merel's knife), `court_steps` | yes (2 stems, 60 s; ch14_hold_the_steps) | The court steps held while the barge is cut loose: the ceremony's music torn open | **Proposal:** `peace_wedding`'s break material as stem 1 of a two-stem `court_steps` cue; stem 2 enters at the last turn | C minor, 112 BPM (the wedding's tune in diminution) | ~60 s | the trap cutscene → the set piece on the beat; out to `lagoon_escape`, which carries the boss |
| Scripted escape | Ch16's storm waking | reuses `abiding_guard` stem 2 → `act2_break` | — | — | — | — | as Ch8's Reach: Kerrid `locked_active`, no new cue |

## 3. Chapter by chapter
"Exists" means rendered and wired in `music.json` as a cue (act2_finals.md); zone rows for Ch10+ are still missing
everywhere (M4-A2P-091). Durations of gaps are the outline's.

### Ch10 "Fen of the Kirru" (overcast dusk, tannin water)

| Cue | Kind | Exists? | Mood | Instrumentation | Key / tempo | Length | Transitions |
|---|---|---|---|---|---|---|---|
| `ossa_fen` | zone loop | yes | Humid, patient, a little wary; dusk under roots | low reed pipe and the breath flute in answer, plucked zither, soft frame drum, water | G Dorian, 4/4 at 62 BPM | 154.8 s | resume; to `reedhollow` 1.5 s on the beat (G to A: the Kirru's world is a step apart) |
| `reedhollow` | zone loop | yes | A people's home, warm and strange; the clutch line in it | wordless Kirru voices, reed winds, metallophone, hand drums | the Kirru mode on A (A B C# D# F#, no fifth), 5/4 (3+2) at 78 BPM | 153.8 s | resume; the farewell-tide cue takes the bed |
| `farewell_tide` (+ `farewell_tide_release`) | scene cue (C3), in two parts (M4-CIN-1301: a held gathering loop, the tail on the release gate) | yes | The act's first showpiece: grief turned upward. The clutch sings, turns its back, and the motes lift into the stars. It must feel the opposite of the Ch9 Ebbing (that drifts seaward; this rises). | the clutch's voices (from reedhollow's line) carrying **the Letting's first cell** (LETTING, from the Hush's MEL_A, inverted upward); the breath flute rising; high metallophone; no drums | the Kirru mode on A, rubato over a slow 5/4 pulse at 60 BPM (`"beat": "free"` if the rite's timing leads) | ~90 s, through-composed; ends on a rise, held open, and the backs turned | `@music farewell_tide fade=3.0` from reedhollow; it ends in silence, and reedhollow resumes after the scene's release (2 s) |
| `mangrove_drowner` | boss, 2 stems | yes | Something old and rooted pulling down | stem 1 rooted: low drums, bowed drones, reed growl; stem 2 uprooted: the full ensemble, a few rising chimes as the motes escape | G minor, 12/8 at 62 dotted quarters a minute (the fen's bar exactly) | 77.4 s | phase `uprooted` brings stem 2 in over 3 s; out on the beat to `ossa_fen` |
| Drowner intro | sting | yes (title key) | the roots tighten | gong, low reed swell | G minor | ≤ 8 s | `battle_stings.json` `boss_intro` by_arg (the Act I pattern) |
| C1 Pell at the fen's edge | cutscene | reuse | Quiet, final | `ossa_fen`, ducked under the lines | — | — | the zone bed stays (no `@music`) |
| C2 arrival at Reedhollow | cutscene | reuse | Welcome with a door left shut (Pell outside) | `reedhollow` from its top | — | — | `@music reedhollow fade=2.0` |
| C4 the Drowner's fall (the root-lift) | cutscene | reuse | A small release | the boss's stem 2 decaying, then 4 s of silence, then `ossa_fen` | — | — | `@music silence fade=1.5`, then the zone |
| C5 the Kirru child | side scene | reuse | Gentle question, no answer | `reedhollow` thinned: the Kirru voices only (a stem, or a quieter variant row) | — | — | resume |

### Ch11 "Lowlight" (overcast midday, bound teal)

| Cue | Kind | Exists? | Mood | Instrumentation | Key / tempo | Length | Transitions |
|---|---|---|---|---|---|---|---|
| `sunken_vey` | zone loop | yes | Drowned galleries, light still in the conduits | low glass, bell, piano, a slow song line | E-flat Dorian, 3/4 at 46 BPM | 156.5 s | resume; to `lowlight` 1.5 s on the beat (Eb Dorian → C minor share Eb, Ab, Bb) |
| `lowlight` | zone loop | yes | The temple half under water; the Kirru call bound into the Order's mode | glass, temple voices, the Kirru call on a reed | C minor (Aeolian, B natural on G) | 149.0 s | resume |
| `lamp_engine` | boss, 2 stems | yes | Machine-holy, repaired as fast as you break it | stem 1: ticking metallophone, pulse, temple brass; stem 2 (`opened`): the core bared, a warm rise at the release | C minor, 4/4 at 116 BPM | 74.5 s | phase `opened` over 3 s. The release's small upward lift is the stem's last bar and a `glimmer_lift` SFX. |
| Engine intro | sting | yes (title key) | lamps lighting in sequence | metallophone run, kettle gong | C minor | ≤ 8 s | boss_intro by_arg |
| `nhoa_bound` | sting | **gap** | Ressa bound: Pell's silence made audible | high glass and a single wordless Kirru voice, ice-bright, no drums | A (the Kirru mode), free | ≤ 8 s | `@music nhoa_bound` in the bind cinematic (C3), as `virel_bound` |
| `nhoa_summon` | sting | **gap** | The only Vowbound whose motes go **up** | rising glass chimes on the Letting's cell | A, free | ≤ 6 s | `vowbound_stings.nhoa` |
| C1 the housing-mark; "Dace's son" | cutscene | reuse + silence | Anger in a quiet room | `sunken_vey`, then `@music silence fade=0.5` on Liss's line | — | — | silence holds; the zone returns on release |
| C3 the descent and binding of Nhoa | cutscene | reuse + sting | Long, silent, filial | `lowlight` thinned to glass only, then `nhoa_bound` | — | — | `@music lowlight fade=2.0` from the hall; the sting at the bind |
| C4 the lamp repaired (the truce) | side scene | reuse | Working hands, a truce | `sunken_vey` from its song section (A') | — | — | resume |

### Ch12 "The Cold Road" (cold 09:00, woven reds)

| Cue | Kind | Exists? | Mood | Instrumentation | Key / tempo | Length | Transitions |
|---|---|---|---|---|---|---|---|
| `keth_pass` | zone loop | yes | Thin air, a long climb, cords singing in the wind | low pipe, plucked string, wind-like pad, frame drum on the switchbacks | E minor (Aeolian), 6/8 at 46 dotted quarters a minute | 125.2 s | resume; to `quellan` 1.5 s on the beat |
| `quellan` | zone loop | yes | A highland town's warmth against the cold; red banners | fiddle-like bowed string, plucked strings, frame drums, a town hum | F major / D minor, 4/4 at 92 BPM | 125.2 s | resume |
| `cloudloom` | zone loop | **gap** | The open-roofed weaving-hall: thousands of keth, noon light writing on white stone; reverent and busy at once | a **loom figure** (an ostinato of plucked strings and soft wooden clicks in 3+3+2), high metallophone shimmer, a held women's hum; no Order hum (this is the Ullari's place) | A minor, 4/4 at 72 BPM (3+3+2 eighths). A minor ties it to keth_pass's E and to Hesk's binding. | ~120 s loop | resume; the bind cinematic takes the bed |
| `avalanche_ram` | boss, 2 stems | yes | The mountain itself charging | stem 1: low drums, horn-like reed, snow-noise swells; stem 2 (under 50% HP): the bellow's rage | E minor, 6/8 at 92 dotted quarters a minute (twice the pass) | 83.5 s | the `torn_fleece` phase row (ADR 0204 §6) brings stem 2 in over 3 s. If combat cuts the phase, the row moves to the 50% HP rule. |
| Ram intro | sting | yes (title key) | the shelf groans, the first snow slides | big drum, low brass-reed, a hiss of snow | E minor | ≤ 8 s | boss_intro by_arg |
| `hesk_bound` / `hesk_summon` | stings | **gap** | Holy, woven: light through cords | the loom figure condensed, bells, a sung (Cantor) note | A major (lifted from cloudloom's A minor) / free | ≤ 8 s / ≤ 6 s | as Ch11 |
| C1 the pass-cords; Kerrid's breath | cutscene | reuse + hold | Unease noticed and not said | `keth_pass` with its drum stem out; KERRID_STAIR's two notes, once, far below, on Toma's look | — | — | the zone stays; a one-shot motif SFX (Music bus) |
| C3 Hesk's binding; Ysolde's lie | cutscene | reuse + sting | Beauty with a lie inside it | `cloudloom` at full, then `hesk_bound` | — | — | `@music cloudloom fade=2.0` |
| C4 night at Quellan: the confession | cutscene | **reprise (ADR 0204 §12)** | Forty-seven voices, seven houses: a confession by a fire | Act I's `ysolde_theme` as it is (the zither in fourths and fifths, cold and exact), no new render | C major, 4/4 at 63 BPM (the final's) | the scene's length; the deck fades it out | `@music ysolde_theme fade=3.0`; `@music silence fade=2.0` at the scene's end |
| C5 the Ullari woman's knot | side scene | reuse | Small, kind | `quellan` thinned | — | — | resume |

### Ch13 "Gold and Lacquer" (overcast 16:30, cold gold; no fights)

| Cue | Kind | Exists? | Mood | Instrumentation | Key / tempo | Length | Transitions |
|---|---|---|---|---|---|---|---|
| `ansedra` | zone loop | yes | The holy city of perfect stillness: beautiful, airless, a little wrong | barge song on a lacquered zither, gold bowls (metallophone), the men's hum on C and G under everything | C major (with A minor and B-flat lacquer chords), 4/4 at 63 BPM | 152 s | resume; to `lamp_archive` and the sanctum on the beat |
| `sanctum_of_the_level` | zone loop | **gap** | The still basin lit from beneath by a light that never moves: awe that becomes unease | one sustained pad chord that **never changes** under a slow bell every 4 bars, a glass harmonic halo; the Order hum far off, once a minute. The sameness is the point, so this is the one Act II loop where monotony is by design (the listening report must list it as such). | C major (Ansedra's), 4/4 at 40 BPM (a bell every 4 bars) | ~120 s loop | resume; Kerrid never enters, so no Kerrid motif here |
| `lamp_archive` | zone loop | yes | Paper and dust; truth assembling itself | grand piano, the Hush's broken-off fragment, "kept / spent" sighs, Sefir's motif in canon | D minor, 3/4 at 59 BPM | 137.3 s | resume; the Archive's reading scenes keep the loop (no `@music`) |
| `ethren_bound` / `ethren_summon` | stings | **gap** | Glimmer, still water: a held breath | glass harmonics, a sustained bowed string, no attack | C major / free | ≤ 8 s / ≤ 6 s | as Ch11 |
| C1 arrival in the still city | cutscene | reuse | Arrival; the stillness noticed | `ansedra` from its top | — | — | `@music ansedra fade=3.0` |
| C2 Sefir's hospitality | cutscene | reuse | Warm on the surface | `ansedra` thinned (hum and bowls) | — | — | resume |
| C3 the Sanctum; Liss before the light | cutscene | reuse | The light that never moves | `sanctum_of_the_level` | — | — | `@music sanctum_of_the_level fade=2.0` |
| C4 Ethren's binding | cutscene | reuse + sting | Ysolde before Corran | the sanctum loop, then `ethren_bound` | — | — | as Ch11 |
| C5 the wedding announced | cutscene | reuse | A celebration that frightens | `peace_wedding`'s opening bars as a preview (cue row `peace_wedding_preview`, the same file from 0 s, faded after ~30 s) | — | — | `@music peace_wedding_preview fade=2.0` |
| C6 the Archive's three days | cutscenes ×2–3 | reuse | The truth on paper | `lamp_archive` | — | — | resume |
| C7 the pact of silence | cutscene | reuse + silence | Sefir knows | `lamp_archive`, cut to silence (fade 0.5) on Sefir's look | — | — | silence; the zone resumes on release |
| C8 Corran's house | side scene | reuse | Quiet memory | `ysolde_theme` (Act I), a lower register | — | — | `@music ysolde_theme fade=3.0` |

### Ch14 "The Peace Wedding" (dusk 2,800 K, contrast 0.70: the game's peak)

| Cue | Kind | Exists? | Mood | Instrumentation | Key / tempo | Length | Transitions |
|---|---|---|---|---|---|---|---|
| `peace_wedding` | scene loop (C1) | yes (the ceremony loop) | The ceremony: tender, public, already watched | zither, slow flute descant, the couple's tune (E minor), the Stillguard's damped gong stepping 2 against 3 | G major, 3/4 at 88 BPM (its dark episode in E-flat and C minor) | 130.9 s loop | `@music peace_wedding fade=3.0` |
| `peace_wedding_break` | scene cue (C2, the trap) | **gap** | The break: the ceremony torn. The gong's 2-against-3 wins; the couple's tune breaks off mid-phrase. | the wedding's ensemble cut to the gong and low drums; ORDER_HUM entering **loud and close** (the Conclave springing it) | the wedding's 3/4 at 88 BPM, broken into C minor, then free | ~25 s, ends in a held low C | `@music peace_wedding_break fade=0.2` (the only near-cut in the act, by design; still ≥ min_fade_sec) |
| C3 Tobin's death | cutscene | silence | Nothing plays | — | — | — | `@music silence fade=0.5`; foley only |
| `court_steps` | set-piece battle | yes (2 stems) | §2 | §2 | C minor, 112 BPM | ~60 s, 2 stems | §2 |
| `lagoon_escape` | scene cue (C4–C6) | **gap** | The first ripple in four hundred years: terror and wonder. The bells ring, the city comes to its windows, and Merel stays behind. | the pole's stroke as a pulse (low drum and water), tower bells entering one by one, the couple's tune reborn in the flute, a bowed string for Merel at the gate | E minor → C minor at Merel, 4/4 at 72 BPM (the strokes) | ~2 min, through-composed (sections cut to C4, C5 and C6) | from the step-hold on the beat; into `malcor_venn` at C7 |
| `malcor_venn` | people boss, 2 stems | **gap** (M4-A2P-092) | A Warden, a living-seeming man, the Order's still power | stem 1 (the flat-engine): a **flattening drone** (a pad whose motion is filtered out; the timeline's slow pulse as a low gong every 4 beats, the same pulse the timeline shows), muted strings; stem 2 (he boards): frame-drum roll, low brass-reed, ORDER_HUM's cell in the bass | C minor, 4/4 at 96 BPM | ~80 s | intro sting → stem 1; the part-break (Liss) brings stem 2 in over 3 s |
| Malcor Venn intro | sting | yes (`ch14_malcor_venn`) | the pursuit barge closes | gong, the flat drone swelling | C minor | ≤ 8 s | boss_intro by_arg |
| C8 the Warden left standing | cutscene | reuse | Ripples, then quiet | `lagoon_escape`'s coda (the last bars as a cue row `lagoon_escape_coda`, a start offset) | — | — | out to silence; Ch15 opens on `unlamped` |

### Ch15 "Unlamped" (moonlight 9,000 K, sea-glow)

| Cue | Kind | Exists? | Mood | Instrumentation | Key / tempo | Length | Transitions |
|---|---|---|---|---|---|---|---|
| `unlamped` | zone loop (the barge) | yes | Drifting south in the dark with the dead aboard | pad turning through F-flat and B-flat, rising glow tones, very low drums | E-flat minor, 4/4 at 51 BPM | 155.3 s | resume |
| `wakefin` | boss, 2 stems | yes | Fought in the dark: telegraphs are **sounds** (pillar 4), so the music leaves room for them | stem 1: sub pulse and sea-glow shimmer; stem 2: the full chase. The mix leaves 1–4 kHz clear for the telegraph SFX (§4). One whole animal, no deck adds (ADR 0204 §3). | E-flat minor, 4/4 at 102 BPM | 75.3 s | intro sting → stem 1; the `close_circle` phase row (ADR 0204 §6) brings stem 2 in over 3 s |
| Wakefin intro | sting | yes (title key) | something circling under the barge | low swell, glass glint, a single drum | E-flat minor | ≤ 8 s | boss_intro by_arg |
| `kerrid_at_sea` | scene cue (C3, the reveal) | **gap** | The act's emotional peak: a bed for a voice. Grief, guilt and a long-held stillness, never sentimental. | a sustained **bowed string** and a low pad, KERRID_STAIR's two notes (D, A) far below as his tread, now slowed until they stop; the held motes as faint sideways glass. No melody over his words. | D minor, free (`"beat": "free"`), the tread at 40 BPM where it appears | ~2.5 min (cut to the scene), a bed like `iskarra_vigil` | `@music kerrid_at_sea fade=4.0` from `unlamped`; it ends in silence |
| `hollowmere_answers` | scene cue (C4) | **gap** | Dawn in fog: Liss sings a current-song, and Hollowmere answers from the flotilla | Liss's voice on CURRENT_SONG, sung (ADR 0204 §10: a current-song is a work-song, not a rite; Narrative confirms in review); the answer as many far voices and a horn, the flotilla's bells | CURRENT_SONG's key, at CURRENT_SONG_BPM 76 | ~60 s, ends into `hollowmere` | `@music hollowmere_answers fade=2.0`, carrying into the zone loop |
| `hollowmere` | zone loop (first visit) | yes (Act III's cue) | The Saltwright flotilla: work, scrap, family | Act III's cue, as is | D Dorian | 135 s | **the zone row only** (M4-A2P-091); resume |
| C5 Liss and her father | cutscene | reuse | Reunion, hard words | `hollowmere` thinned | — | — | resume |
| C6 Toma's confession | cutscene | silence → reuse | Faith breaking | silence under the confession (fade 1.0), then the pyre-raft cue | — | — | silence |
| C7 the pyre-raft | cutscene | **reprise (ADR 0204 §12)** | A funeral on the water | Act I's `hush_first_verse` (the Hush's first statement), no new render | as the cue (free) | the scene's length | `@music hush_first_verse fade=3.0` |
| C8 supper: two memories of Dace | side scene | reuse | Warm and sore | `hollowmere`, and `dace_ledger`'s zither (Act III's) as a 30 s insert if Narrative wants Dace heard | — | — | resume |

### Ch16 "The Edge of the World" (white noon, the game's lowest contrast; the Choir at moonrise)

| Cue | Kind | Exists? | Mood | Instrumentation | Key / tempo | Length | Transitions |
|---|---|---|---|---|---|---|---|
| `pale_rim` | zone loop | yes | White shallows under a white sky; no thirds; days passing | fifths and octaves only (the white), soft bells, wind pad | E, no third, 4/4 at 51 BPM | 155.3 s | resume; C2's wade montage keeps the loop (no `@music`) |
| `drowned_choir` | zone loop | yes | The ring of colossal mouths at moonrise | the stones' open-vowel chords, the Cantor's E-D-C cell | A minor (the Hush's key), F and E majors, 3/4 at 47 BPM | 153.2 s | resume |
| `kesh_bound` | sting | **gap** | All six elements in turn; the singer becomes the storm's heart | six short colours chained (fire crackle-bell, ice glass, lightning static-chime, water, holy bell, glimmer), resolving onto the Hush's A minor | A minor, free | ≤ 8 s | as the others. `kesh_summon` is Act III's (H03). |
| C4 Kesh's memory (the binding) | cutscene | **gap** | A memory sequence a thousand years back: what the Hush really does | **Proposal:** `drowned_choir` heard **through water** (MusicDeck under the muffle, mix.json `muffle`) plus MEL_A sung by one far voice | A minor | ~90 s (the cue row `kesh_memory`) | `@music kesh_memory fade=2.0`; the muffle is a mix reason for the scene |
| `sefir_go_home` | scene cue (C5) | **gap** | The temptation: the Long Stillness offered as a gift. Sefir's motif at its warmest, and frightening because it is kind. | grand piano and a warm pad, ORDER_HUM **sung** for the first and only time as a lullaby by many (ADR 0204 §10: a deliberate break from "the Order hums"; Narrative confirms in review), no percussion | C major (Ansedra's), 3/4 at 52 BPM | ~2 min | `@music sefir_go_home fade=3.0`; it breaks to silence (0.5 s) on Asha's refusal (C6) |
| `abiding_guard` | people boss, 2 stems | **gap** (M4-A2P-092) | Sefir's elite: disciplined, faithful, terrible | stem 1: low frame-drum roll, the guard's own hum (a Stillguard choir, ORDER_HUM in canon), gongs; stem 2: **the storm waking early**: the Undertow's octatonic storm band (Act I's `undertows_reach` mode) breaking in | A minor, 4/4 at 96 BPM (a bar is exactly the Reach's 12/8 bar, 2.5 s, so `undertows_reach`'s surge fits bar for bar) | 80 s, 2 stems | intro sting → stem 1; the storm's row → stem 2 over 4 s; into the scripted escape |
| Abiding guard intro | sting | yes (`ch16_abiding_guard`) | the guard closing ranks | big drum, hum cut off | A minor | ≤ 8 s | boss_intro by_arg |
| C8 the storm wakes; swept away | cutscene | reuse | Catastrophe | `abiding_guard` stem 2 at full, then the sea's roar (SFX) | — | — | `@music silence fade=0.5` at the sweep |
| `act2_break` | scene cue (C9) | **gap** | The act break: Rhen's voice-over after the sweep; spent, honest, still going | a bed for a voice: the Hush's MEL_A on the breath flute, slow and alone, over a low drone; the Letting's cell once, unresolved, at the end | A minor, free | ~90 s | `@music act2_break fade=4.0`; it ends in silence for the act card |

## 4. New SFX families Act II needs (Act I has none of these)
Each family is a source module and a data file in the Act I pattern: a `sfx_<domain>.json`, a source under
`assets_src/sfx/`, rows named by what plays them, and new rows for the Act I audit's sections (M4-A2P-093, M4-AUD-1001).

| Family | What plays it | Content | Notes |
|---|---|---|---|
| **Fen ambience and wildlife** | Ossa Fen and Reedhollow beds, LifeAudio | insects at dusk, root creak, tannin drips, fen birds, fireflies (silent: wildlife, not glimmer), reed wind, the clutch's wordless hum as a bed | 2 beds + life rows |
| **Kirru voices** | CreatureAudio-like hook on the Kirru actors, cutscenes | wordless calls, the clutch's sung line (non-verbal), a child's question tone | a people, never monster sounds (act2_roster) |
| **Mangrove and water-root foley** | footsteps (the root-walks), cutscene foley | wet wood on roots, splash-through on tannin water | **new footstep surfaces (ADR 0204 §11):** `root` (wet hollow wood, Ch10), `snow` and `slate` (Ch12); env-art marks them in the kits |
| **Drain and rooted statuses** | battle_sfx `vfx` rows for the new effects | drain: a pull from target to caster (inverse heal); rooted: roots gripping, a creak lock; a no-swap refusal tick in the menu | M4-CMB-1001 |
| **Repair (conduit crawlers)** | battle_sfx skill rows | ratchet, a spark-weld, a part's light coming back | the Lamp Engine's adds |
| **Part break** (the flat-engine, the Engine's lamps) | CreatureAudio `break_parts` | a part breaking off: brass crack, glass shatter, the bound light escaping upward | one family, variants per part material |
| **Snow and avalanche** | Keth Pass beds, the Ram's field hazard | high wind with gusts, cord whistle, snow hiss, slide rumble, field-hazard ticks per round | the hazard tick must read on the timeline's beat (pillar 4) |
| **Keth cords and the loom** | Keth Pass and Cloudloom beds, cutscene foley | thousands of cords in wind (a granular whistle), loom clacks, shuttle swish | Cloudloom's bed sits under its music's loom figure: tune it 10 LU under, no clash |
| **Buff strip** (`unravel`) | battle_sfx | a weave pulled apart: threads snapping, a ward's ring dying | — |
| **Still water and ripples** | Ansedra beds, the lagoon escape | near-silence with very low air; the **first ripple** (a pole stroke on perfectly still water, the ring spreading); lapping that grows as the city wakes | the chapter's hero sound; paired with the ripple propagation shader |
| **City bells and windows** | the lagoon escape | the bells of Ansedra ringing across water one by one, shutters opening along the canals, distant voices | layered with `lagoon_escape`; the bells are SFX so they sit in space |
| **The flat-engine and timeline slow** | Malcor Venn's stem 1, the field rule | a low gong pulse on the timeline's slow tick, a pressure hum that flattens other sounds (a mix reason that low-passes Combat) | the pulse must be **visible on the timeline and heard on the beat** |
| **People-boss voices** (Malcor Venn, the Abiding guard) | CreatureAudio-style sets for human bosses | armour, haft, breath, effort; a yield rather than a death where the story spares them | Act I's Stillguard Inquisitor is the precedent |
| **Darkness telegraphs** (the Wakefin) | battle_sfx telegraph rows | a sound per telegraph type (the circle, `sound_dive`, the tail): distinct pitch families in 1–4 kHz. `sound_dive` is evasion up, so its sound says "it's gone deep", never "it's gone" (ADR 0204 §3). | every telegraph needs one; the audit must check it. **Done:** `skill_{fin_cut,sound_dive,wakefin_rise,wake_wash,bill_strike}`, `phase_close_circle` (act2_skill_sfx.py) |
| **Sea-glow and held motes** | Ch15 cutscenes, the shoal | sideways glass glints for held motes (not rising, not falling), the shoal's slow hum below the barge | consistent with the visual rule: held motes go sideways |
| **Hollowmere work foley** | Hollowmere beds (shared with Act III) | windmills, tide-wheels, hull creak, rope and capstan, a work crowd | build once at final quality (Act III reuses it) |
| **Pyre-raft** | cutscene foley | fire on water, a raft pushed off, embers hissing on the sea | — |
| **Element cycling** (Kesh) | battle telegraphs and the bind | a short colour per element, the same six as `kesh_bound`, one per shift on the timeline | pillar 4: each shift telegraphed |
| **Memory sequence filter** | Ch16 C4 | a mix reason (the muffle) for "a thousand years ago": low-passed, widened, with a slow pitch drift | data only (mix.json reason) |
| **The storm's waking and the sweep** | Ch16 C8 | the sea standing up: roar, rigging and stone, the party swept off | reuses the Undertow's family (Act I), larger |
| **Heresy UI** | ui_sfx hooks | a refusal at an Order shop or shrine (a closed shutter), a desecrated-shrine tone, the status-menu title change sting | UI only; quiet |
| **The document reader** | ui_sfx hook on the reader | paper slides, a page laid beside another, the matching-hand highlight tone | the Archive's set piece (ui-menus) |
| **Act II creature voices** | creature_voices.json (M4-AUD-1001) | the 11 regulars and the 4 creature bosses (most exist: act2_creature_sfx.py); `conduit_crawler` and the variants are new | the Act I audit's Enemies section, scoped `--act 2` |

## 5. Decided (ADR 0204, 2026-10-30)
1. **`battle_heretic`:** a variant regular-battle cue from Ch14 on (§9).
2. **Singing:** the Order sings ORDER_HUM once, as `sefir_go_home`'s lullaby, and Liss sings the current-song in
   `hollowmere_answers` (§10). Narrative confirms both in review.
3. **Footstep surfaces** `root`, `snow` and `slate` are approved (§11). env-art marks them.
4. **Reprises:** the pyre-raft plays `hush_first_verse` and Ysolde's confession plays `ysolde_theme` (§12). Neither
   needs a new render.

## 6. Mapping to tasks
- M4-A2P-090 (scene cues): `farewell_tide`, `peace_wedding_break`, `lagoon_escape` (+ coda row), `kerrid_at_sea`,
  `hollowmere_answers`, `sefir_go_home`, `kesh_memory` (row only), `act2_break`. The two reprises (§5.4) need only
  their `@music` lines.
- M4-A2P-091 (zone loops, stings, zone rows): `cloudloom`, `sanctum_of_the_level`, the Vowbound `*_bound` and
  `*_summon` stings (Nhoa, Hesk, Ethren; Kesh's bound only), `music.json` zone rows for all 15 Act II zones, `beat`
  grids, and the `peace_wedding_preview` row.
- M4-A2P-092 (people bosses): `malcor_venn`, `abiding_guard`, `court_steps`; every Act II boss's encounter and phase
  rows (the Ram's `torn_fleece` and the Wakefin's `close_circle` included); the six boss-intro stings.
- M4-A2P-093 (ambience and foley): §4's families, the new footstep surfaces and the beds.
- M4-AUD-1001: the creature voices.
- A new item for the Act II gate: extend `tools/audio/act1_audio_audit.py` with an `--act 2` scope (the zone, battle,
  cutscene-action and battle-event sections), so the Act II audio inventory exists on day one.
