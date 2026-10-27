# Act II's final cues: the list, the sizes, and how they land (M3-AUD-839)

Git LFS is approved for `assets/audio/music/act2/**` (ADR 0039) but is **not live in the cloud yet**: the network
blocks `lfs.github.com`. Until the Lead announces it:
- every final renders from `assets_src/music/act2/<cue>.py` into `assets/audio/music/act2/`, and **only** with
  `python3 tools/audio/render_all.py --act2` (render_all.py `ACT2_FINALS`). The default run, the 72 MiB budget and
  the tests don't expect these files.
- no `.ogg` or `.loop.json` under `assets/audio/music/act2/` is committed (tools/tests/test_act2_finals.py fails if
  one is tracked before `.gitattributes` routes the path to LFS), and nobody edits `.gitattributes` but the Lead.
- music.json rows, PROVENANCE rows and the `.import` files land **with** the files, in the LFS commit. Until then
  this file holds each cue's measured size and loudness.

The sketches (M3-AUD-804/805: about 60 s loops, `assets/audio/music/<cue>.ogg`, committed) stay as they are and keep
playing until the finals replace them. A final keeps its sketch's mode, palette and themes (the human hasn't heard
the sketches yet: if a verdict changes a direction, the final follows it), and grows it into a full piece. Each
final is a 2–3 minute seamless loop with developed sections, Vorbis q3 stereo, −16 LUFS integrated (mix.md §2).

## The list

Sizes are estimates (about 0.95 MB a minute at q3) until a final is rendered; the **Measured** column replaces them.

| Ch | Cue (final) | From | Kind | Est. | Measured |
|---|---|---|---|---|---|
| 10 | `ossa_fen` | sketch | loop ~150 s | 2.4 MB | |
| 10 | `reedhollow` | sketch | loop ~150 s (its clutch line carries the Letting's first cell: act3_plan.md §4 Q2) | 2.4 MB | |
| 10 | `farewell_tide` | reedhollow's material | cue ~90 s, the dusk rite; the motes lift; it ends on a rise and the backs turned | 1.4 MB | |
| 10 | `mangrove_drowner` | new | boss, 2 stems × ~120 s (phase 2 `uprooted`) | 3.8 MB | |
| 11 | `sunken_vey` | sketch | loop ~150 s | 2.4 MB | |
| 11 | `lowlight` | sketch | loop ~150 s | 2.4 MB | |
| 11 | `nhoa_bound` / `nhoa_summon` | new (as virel's) | stings ≤ 8 s / ≤ 6 s (sfx folder) | 0.3 MB | |
| 11 | `lamp_engine` | new | boss, 2 stems (phase 2 `opened`; the core's release is a small upward lift) | 3.8 MB | |
| 12 | `keth_pass` | sketch | loop ~150 s | 2.4 MB | |
| 12 | `quellan` | sketch | loop ~150 s | 2.4 MB | |
| 12 | `cloudloom` | new | loop ~120 s, the open-roofed weaving-hall | 1.9 MB | |
| 12 | `hesk_bound` / `hesk_summon` | new | stings | 0.3 MB | |
| 12 | `avalanche_ram` | new | boss, 2 stems (no phases: the second stem is the bellow's rage under 50% HP) | 3.8 MB | |
| 13 | `ansedra` | sketch | loop ~150 s | 2.4 MB | |
| 13 | `sanctum_of_the_level` | new | loop ~120 s, the still mirror | 1.9 MB | |
| 13 | `lamp_archive` | sketch | loop ~150 s | 2.4 MB | |
| 13 | `ethren_bound` / `ethren_summon` | new | stings | 0.3 MB | |
| 14 | `peace_wedding` | sketch | cue ~3 min (the ceremony; it breaks at the trap) | 2.9 MB | |
| 14 | `lagoon_escape` | new | cue ~2 min, the first ripples; the bells; Merel left behind | 1.9 MB | |
| 14 | `malcor_venn` | new | boss, 2 stems (phase 1 the still water slows; phase 2 he boards) | 3.8 MB | |
| 15 | `unlamped` | sketch | loop ~150 s | 2.4 MB | |
| 15 | `wakefin` | new | boss, 2 stems, in the dark | 3.8 MB | |
| 15 | `kerrid_at_sea` | new | cue ~2.5 min under his telling (a bed for a voice, as `iskarra_vigil`; KERRID_STAIR far below) | 2.4 MB | |
| 15 | `hollowmere_answers` | new | cue ~60 s: Liss's current-song into the fog, Hollowmere answering (CURRENT_SONG) | 1.0 MB | |
| 16 | `pale_rim` | sketch | loop ~150 s | 2.4 MB | |
| 16 | `drowned_choir` | sketch | loop ~150 s | 2.4 MB | |
| 16 | `kesh_bound` | new | sting (`kesh_summon` belongs to Act III's H03) | 0.2 MB | |
| 16 | `sefir_go_home` | new | cue ~2 min, the temptation (Sefir's motif at its warmest; ORDER_HUM) | 1.9 MB | |
| 16 | `abiding_guard` | new | boss, 2 stems; the storm waking early is stem 2 | 3.8 MB | |
| 16 | `act2_break` | new | ~90 s bed for the Rhen voice-over | 1.4 MB | |

**Total estimate: about 72 MB** for Act II's finals (14 zones about 31 MB, 6 bosses about 23 MB, scenes and stings
about 18 MB). It all goes to LFS. No single file goes over 5 MB (a boss's stems are separate files), so nothing here
needs ADR 0039's over-5-MB rule.

## Order of work
1. **The 12 zone finals from the sketches** (M3-AUD-840..843, three each). Their sources and measured sizes land now,
   and their audio lands with LFS.
2. **The six bosses**: the four whose models exist (drowner, engine, ram, wakefin) first.
3. The new zones and the scene cues, as Act II's beat sheets are written (none exist yet: act_outline.md is the
   only source, so their timings wait on Story's sheets).
