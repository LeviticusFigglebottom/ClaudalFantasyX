# Act III music and sound: the motif map and the cue list (M3-AUD-836)

Planning only: nothing here is rendered yet. Sources: [act_outline.md](../story/beats/act_outline.md) Ch17–Ch21,
[act3_ending.md](../story/beats/act3_ending.md) (its cue ids are adopted as written), [bible.md](../story/bible.md)
§4, §6, §8 and §10, and the motifs already in code. Every melody is original (SPEC §2). Where a cue states a motif,
it imports the notes from the one place they are written down, never retypes them
([motifs.py](../../../assets_src/music/motifs.py)'s rule).

## 1. The motif map

Each recurring tune, where its notes live, where Acts I–II state it, and what Act III does with it. The map's shape
follows the story's turn: **in Acts I–II the tunes fall, hold or circle; in Act III they rise.** That is the light
grammar ("up = released", act3_ending §0 rule 4) heard as melody.

| Motif | Notes live in | Acts I–II | Act III |
|---|---|---|---|
| **The Hush**, verse 1 = **the Velamir lullaby** (N-11): E D C, then A, a stepwise fall from a long note | `hush_theme_v2.py` `MEL_A` | `hush_first_verse` (B09), `iskarra_vigil` (two octaves down, "somebody is still below"), `drowned_choir` (hummed by the stones) | `heart_approach` plays it **backwards**, very slow (H01). `goodbye_imra` is Imra's unaccompanied hum of it (E1). It is the four bars inside `goodbye_dace` (E2). `ending_dock` plays it on piano and it **resolves at last** (E6). `credits_suite` ends on it. |
| **The Hush**, verses 2–7 | `MEL_B` (verse 2); verses 3–7 are each Act II temple's own phrase (to be fixed when the Act II finals land) | `hush_second_verse` (Ch5); the Act II temples | `kesh_first_voice` states all seven verse phrases in turn, one per element phase (H03). |
| **The Eighth Verse, the Letting** (new): the first verse's phrase **turned upward**, ending on *tash* | `motifs.py` `letting()` (M3-AUD-851): MEL_A's first cell inverted around E5, E F G \| B C B, closing up on E6, held | Unheard. But the bible says the Kirru farewell-tide "carries it unknowingly" (§6), so **Reedhollow's rising clutch line must carry the Letting's first cell** (see §4 Q2). | `the_letting` (H07–H09, diegetic, Asha's voice leading); `unbinding_swell` opens with it in full choir. |
| **Sefir's motif**: G C D E D C#, rising to a leading tone that never leads | `sefir_theme.py` (move it to `motifs.py` on its first reuse; bytes verified with `--determinism`) | `sefir_theme` (Ch6), the Order scenes | `sefir_warden` uses variant (c): the six notes as a 5/4 ostinato in low bells, with a hummed congregation over strings (H04). `sefir_heart` distorts it under the storm's note (H06). In **H08 the C# finally resolves up to D**: his relief, inside `the_letting`'s thinning, the only time the motif arrives. |
| **The Order's hum** | `motifs.py` `ORDER_HUM` | the Shell Shrine, the raid, `corrow_night` | the congregation in `sefir_warden` hums it; `iskarra_spire`'s founders' engine drones under it. |
| **Dace's current-song**, D dorian, with "soundings" | `motifs.py` `CURRENT_SONG` | `rhen_current_hum` (Ch1), `going_under`, `current_song` (Ch8) | `hollowmere` (his flotilla; fragments in the wrights' work), `dace_ledger` (Ch17, reading his logs), `goodbye_dace` on plucked strings (E2; motifs.py already names it). |
| **Kerrid's stair**: D3 to A2, one stride each | `motifs.py` `KERRID_STAIR` | `kerrid_stair` (Ch5) | `kerrid_last_night` (Ch19), steady and at rest. `goodbye_kerrid` (E3) slows from 48 BPM to a stop, one note a stride (motifs.py's rule). **Its stop is the end of the walking.** |
| **The star-path**, the homecoming lullaby (not the Velamir one): F# E D E \| F# A | `haluna_dawn.py` `RH_CELL` | Ch2's beach, `name_board_home` (Ch4, resolved) | `the_kite` (Ch18, the world opening: the Kite can go home now); `post_credits_lamp` uses haluna_dawn's metallophone phrase, as the sheet asks. |
| **The farewell-tide** (Kirru): a wordless rising line that never comes down | `reedhollow.py` (the clutch's line A B C# D# F#) | `reedhollow` (Ch10), Pell | `pell_name_shell` (Ch18: Pell teaches Asha the farewell-tide). `haluna_lifting` (Ch18, optional: Toma leads Haluna in lifting its own dead the Kirru way, the first time human voices sing it). |
| **Liss's theme** | `liss_theme.py` | Ch7 onward | `the_kite`'s B section (she flies it). E4 is silence: the theme is not heard when she brings the Kite down. |
| **Ysolde's theme**, cold and exact | `ysolde_theme.py` | Ch4, Ch7 | `dace_ledger`'s second half, where Ysolde begins reconstructing the Eighth Verse (Ch17). R2 has no melody (sheet). |
| **The Vowbound summons** | `ilun_summon.py`, `kahre_summon.py`, `virel_summon.py` and the Act II summons | each summon | Ch20's six releases: each summon's phrase turned upward and left open, then `release_sting`. |

**New in Act III:** `LETTING` and, possibly, a figure for the Cage's four founders (their own Lamptongue chord; the
founders sang before the Order taught humming). Nothing else: Act III should sound like the whole game coming home,
not like new material.

## 2. The cue list

Kinds: **loop** (a seamless zone or dungeon bed), **stems** (a boss with phase stems: music.json `stems`,
`start_stems` and a phase's `stems_on`), **cue** (through-composed for a scene), **sting**. Sizes assume Vorbis q3
stereo (about 0.95 MB a minute) as Acts I–II do.

| Ch | Cue id | Kind | Scene | Motifs | Sketch | Est. |
|---|---|---|---|---|---|---|
| 17 | `hollowmere` | loop 60 s | the flotilla, Dace's dry-dock | current-song | Saltwright work music: mallets on hulls, rope, a wright's whistle carrying current-song fragments; D dorian | 1.0 MB |
| 17 | `dace_ledger` | cue 90 s | Rhen reads the logs (on screen, never Dace's voice: N-26) | current-song, then Ysolde's | under reading: low strings and the current-song in pieces; ends on the blank page in silence ("After the storm") | 1.4 MB |
| 18 | `the_kite` | loop 75 s | the hub, the maiden flight; the world opens | star-path, Liss | the only open, airborne cue in the game: wind, sail, a lifted major; the star-path at last flying home | 1.2 MB |
| 18 | `kite_maiden_flight` | cue 45 s | the first lift-off | the_kite's A section | rises out of `hollowmere` into `the_kite` | 0.7 MB |
| 18 | `pell_name_shell` | cue 60 s | Pell's new name-shell; the farewell-tide taught | farewell-tide | Kirru whistles and the root-harp (act2_voices) | 1.0 MB |
| 18 | `haluna_lifting` | cue 75 s (optional scene) | Haluna lifts its dead the Kirru way | farewell-tide, star-path | the farewell-tide sung by human voices for the first time, then the backs turned: the cue stops on a rise | 1.2 MB |
| 18 | `<town>_after` × up to 6 | variants | revisited towns, changed | each town's own | reuse each Act I cue's stems with one changed layer (a lighter mix, a missing voice), not new files where avoidable | 0–3 MB |
| 19 | `iskarra_ruins` | loop 60 s | the ruins in full (the prologue's place) | the Hush (as `iskarra_vigil`) | prologue_ambience's `iskarra_dusk` bed plus `iskarra_vigil`'s deep MEL_A, looped | 1.0 MB |
| 19 | `iskarra_spire` | loop 70 s | the Lamp Spire dungeon | Order's hum, founders' engine | a bound-light machine: steady glass, a lamp-engine's tick (the Lamp Engine's family), a hum that never pulses | 1.1 MB |
| 19 | `hesper_and_ilsabet` | stems 2 × 90 s | the revenant pair boss | two lines that never meet | two stems, one per revenant; the second stem drops out when one falls | 3.0 MB |
| 19 | `kerrid_last_night` | cue 70 s | his last quiet night with Rhen | Kerrid's stair | at rest: the stride under a low string, unhurried; nothing ends yet | 1.1 MB |
| 20 | `undertow_layers` | loop 60 s | the drowned-memory dungeon's connective water | the Hush, low | the dark between the layers; each layer room plays its remembered place's **own Act I cue** through `bus_muffle` (Oruvel's market, a Corrow kitchen, a Tidecup crowd): no new files | 1.0 MB |
| 20 | `release_<vowbound>` × 6 | stings 15–20 s | Ilun, Kahre, Virel, Hesk, Nhoa, Ethren released | each summon, turned upward | each summon's phrase rising and left open | 6 × 0.3 MB |
| 20 | `release_sting` | sting 25 s | the shared release sting (H03's is "last and longest") | the Letting's first cell | glass and choir lifting | 0.4 MB |
| 20 | `the_cage` | stems 4 × 120 s | the four founders as one boss | founders' chord, the Hush | four stems, one per founder; each falls silent as its founder falls ("they thank the party") | 7.5 MB |
| 21 | `heart_approach` | loop 60 s | H01–H02 | MEL_A backwards | a low drone and the reversed phrase, very slow; thins to `silence` on Sefir's first word | 1.0 MB |
| 21 | `kesh_first_voice` | stems 7 × ~50 s, or one 6 min cue | H03, the Kesh fight | the seven verses | one verse phrase per element phase; build it as a long cue with phase markers if seven stems are too large | 5.5 MB |
| 21 | `heart_rest` | loop 40 s | R1, the save point | the drone only | `heart_approach`'s drone, no melody | 0.6 MB |
| 21 | `sefir_warden` | stems 2 × 120 s | H04 | Sefir variant (c), Order's hum | beautiful and airless: no attacks, strings and a hummed congregation | 3.8 MB |
| 21 | `sefir_heart` | stems 3 × 120 s | H05–H06 | Sefir distorted, the storm's note | rock-fusion percussion under the storm (the battle_standard family's kit) | 5.7 MB |
| 21 | `the_letting` | cue ~5 min, phase-marked | H07–H09, diegetic | **LETTING** | Asha's voice leads and the score follows her; the countdown is the cue's length; it thins to one held note (H08) and its last phrase hands to `unbinding_swell` | 4.8 MB |
| 21 | `unbinding_swell` | cue 120 s | H09 | LETTING, the Hush resolving upward | full choir and orchestra, the only time in the game | 1.9 MB |
| End | `goodbye_imra` | cue 150 s | E1 | MEL_A hummed | the score drops out; Imra's hum alone, once; one piano note after she is gone | 0.6 MB |
| End | `ending_lift_bed` | loop 45 s | R2, R3 (R4: thins to nothing) | none | the drone and a faint high shimmer | 0.7 MB |
| End | `goodbye_dace` | cue 180 s | E2 | current-song, four bars of MEL_A | plucked strings; the lullaby inside it for four bars | 2.8 MB |
| End | `goodbye_kerrid` | cue 120 s | E3 | Kerrid's stair, slowing | solo low string and a gamelan pulse; slows from 48 BPM to a stop | 1.9 MB |
| End | `ending_dock` | cue 90 s | E6 | MEL_A on piano, resolved | solo piano; never a voice | 1.4 MB |
| End | `credits_suite` | cue 7 min | CR | every theme, ending on MEL_A | see §3 (the 5 MB rule) | 6.5 MB |
| End | `post_credits_lamp` | cue 60 s | E7 | haluna_dawn's metallophone phrase | one low metallophone phrase and one struck match (sfx) | 0.5 MB |

**Silence is a cue too** (`@music silence`): H02's thinning, E4 (wind, rope and the hull meeting water only, as
foley: a Kite-landing sound set), and E5, the quietest scene in the game. E5 needs an explicit **room tone of
nothing**: the ambience and the zone bed must both be off, which today's `@music silence` does not promise.

**SFX for Act III**, beyond the creature voices for Act III's bestiary: the Kite's foley (sails, rigging, the hull,
the engines and their stopping at H09), E4's landing set, the Unbinding's six cutaways (a tide-wheel stopping, the
Tamsule Bell's light leaving it as a bell's hum that lifts away, the Sanctum basin rippling, Lowlight's conduits
emptying upward), Kesh's and Sefir's battle voices, and the Letting's countdown entry on the timeline (a UI sound
that must not compete with Asha's voice).

**Total estimate: about 76 MB** for Act III music (a range of 60–85 MB, depending on stems against long cues and
how many `_after` variants reuse files). Act III alone is larger than the whole 72 MiB budget, so it cannot ship
committed. It needs either Git LFS (the human's decision) or ADR 0172's build-time render.

## 3. Constraints the plan has to meet

- **No file over 5 MB** (CLAUDE.md §8, until LFS). `credits_suite` (7 min, about 6.5 MB at q3) must be split into
  movements played in sequence, or rendered at q2. The same applies to `kesh_first_voice` and `the_letting` if they
  are built as one long file: split them at their phase markers.
- **Voices (SPEC §16 Q4/Q5).** `the_letting` (Asha), `goodbye_imra` (Imra's hum) and `kesh_first_voice` all need a
  voice decision. Until it comes, they use the vocalise-like solo instrument from `hush_first_verse` (a breath
  flute shaped by vowel formants), as every sung line has so far. N-14 binds: after E5, Asha never sings or hums
  again, and `ending_dock` is piano only.
- **One goodbye per scene** (act3_ending §0 rule 1). Every goodbye cue has its own motif: E1 the lullaby, E2 the
  current-song, E3 the stair. No goodbye cue quotes another goodbye's motif, except that the lullaby sits inside
  `goodbye_dace`, as the sheet asks.
- **Rule 7 (released at H09).** No cue after H09 releases anything, so no new upward resolution after
  `unbinding_swell`. The one exception is `ending_dock`'s resolution, which belongs to Asha, not to a release.
- **Stems through the cutscene sequencer.** The ending runs on the sequencer, which today plays one file per
  `@music` (M3-AUD-833). The boss stems and the phase-marked cues need M3-AUD-834 (`@music` through the MusicDeck,
  and `@stem`) before Act III's scripts are written.

## 4. Open questions

1. **For the human (SPEC §16 Q4/Q5):** a voice for the Letting, Imra's hum and Kesh. This is the biggest open
   decision in Act III audio.
2. **For Story and the Lead:** the bible says the farewell-tide carries the Letting unknowingly. Audio proposes
   writing `LETTING` first, then revising Reedhollow's clutch line (an Act II sketch, not yet final) so that it
   carries the Letting's first cell. The player will then have heard the Eighth Verse in Ch10 without knowing it.
3. **For the Lead (ADR 0172 / LFS):** Act III's 60–85 MB decides the storage question if Act II's does not.
4. **For Cinematics:** E5 needs a "nothing" room tone. Should `@music silence` also silence the zone bed and
   ambience in E-mode scenes, or should E5 get its own cue?
