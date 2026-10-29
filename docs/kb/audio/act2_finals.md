# Act II's final cues: the list, the sizes, and how they land (M3-AUD-839)

**Git LFS is live (ADR 0039, 2026-10-28).** `assets/audio/music/act2/**` is stored in LFS by `.gitattributes`
(the `.import` and `.loop.json` sidecars stay plain text), and validate_data and test_audio_loudness keep it out of the
plain-git 5 MB limit and 72 MiB budget. The 16 finals below with a measured size are **committed** (render with
`python3 tools/audio/render_all.py --act2`, then `godot --headless --path . --import`): 23.65 MiB of LFS objects.
music.json's 12 zone rows now play `act2/<cue>.ogg`, and the four bosses have stem rows (`start_stems [0]`; their
encounters and phases wait for the fights). Run `git lfs pull` in a fresh clone (tools/ci_local.sh does it).

The sketches (M3-AUD-804/805: about 60 s loops, `assets/audio/music/<cue>.ogg`, committed) stay as they are and keep
playing until the finals replace them. A final keeps its sketch's mode, palette and themes (the human hasn't heard
the sketches yet: if a verdict changes a direction, the final follows it), and grows it into a full piece. Each
final is a 2–3 minute seamless loop with developed sections, Vorbis q3 stereo, −16 LUFS integrated (mix.md §2).

## The list

Sizes are estimates (about 0.95 MB a minute at q3) until a final is rendered; the **Measured** column replaces them.

| Ch | Cue (final) | From | Kind | Est. | Measured |
|---|---|---|---|---|---|
| 10 | `ossa_fen` | sketch | loop ~150 s | 2.4 MB | 2.11 MB (q2), 154.8 s, −16.07 LUFS |
| 10 | `reedhollow` | sketch | loop ~150 s (its clutch line carries the Letting's first cell: act3_plan.md §4 Q2) | 2.4 MB | 1.58 MB, 153.9 s, −15.97 LUFS |
| 10 | `farewell_tide` | reedhollow's material | cue ~90 s, the dusk rite; the motes lift; it ends on a rise and the backs turned | 1.4 MB | |
| 10 | `mangrove_drowner` | new | boss, 2 stems × ~120 s (phase 2 `uprooted`) | 3.8 MB | 0.81 + 0.99 MB, 77.4 s, stack −16.07 LUFS |
| 11 | `sunken_vey` | sketch | loop ~150 s | 2.4 MB | 0.98 MB, 156.5 s, −15.99 LUFS |
| 11 | `lowlight` | sketch | loop ~150 s | 2.4 MB | 1.39 MB, 149.0 s, −15.99 LUFS |
| 11 | `nhoa_bound` / `nhoa_summon` | new (as virel's) | stings ≤ 8 s / ≤ 6 s (sfx folder) | 0.3 MB | |
| 11 | `lamp_engine` | new | boss, 2 stems (phase 2 `opened`; the core's release is a small upward lift) | 3.8 MB | 0.90 + 0.85 MB, 74.5 s, stack −16.05 LUFS |
| 12 | `keth_pass` | sketch | loop ~150 s | 2.4 MB | 1.60 MB, 125.2 s, −16.05 LUFS |
| 12 | `quellan` | sketch | loop ~150 s | 2.4 MB | 1.34 MB, 125.2 s, −16.02 LUFS |
| 12 | `cloudloom` | new | loop ~120 s, the open-roofed weaving-hall | 1.9 MB | |
| 12 | `hesk_bound` / `hesk_summon` | new | stings | 0.3 MB | |
| 12 | `avalanche_ram` | new | boss, 2 stems (no phases: the second stem is the bellow's rage under 50% HP) | 3.8 MB | 2 × 1.06 MB, 83.5 s, stack −16.05 LUFS |
| 13 | `ansedra` | sketch | loop ~150 s | 2.4 MB | 1.65 MB, 152.4 s, −16.01 LUFS |
| 13 | `sanctum_of_the_level` | new | loop ~120 s, the still mirror | 1.9 MB | |
| 13 | `lamp_archive` | sketch | loop ~150 s | 2.4 MB | 1.25 MB, 137.3 s, −16.07 LUFS |
| 13 | `ethren_bound` / `ethren_summon` | new | stings | 0.3 MB | |
| 14 | `peace_wedding` | sketch | cue ~3 min (the ceremony; it breaks at the trap) | 2.9 MB | 1.42 MB, 130.9 s loop, −16.03 LUFS (the ceremony's loop; the break at the trap is a later cue) |
| 14 | `lagoon_escape` | new | cue ~2 min, the first ripples; the bells; Merel left behind | 1.9 MB | |
| 14 | `malcor_venn` | new | boss, 2 stems (phase 1 the still water slows; phase 2 he boards) | 3.8 MB | |
| 15 | `unlamped` | sketch | loop ~150 s | 2.4 MB | 1.74 MB, 155.3 s, −16.04 LUFS |
| 15 | `wakefin` | new | boss, 2 stems, in the dark | 3.8 MB | 0.81 + 0.74 MB, 75.3 s, stack −16.09 LUFS |
| 15 | `kerrid_at_sea` | new | cue ~2.5 min under his telling (a bed for a voice, as `iskarra_vigil`; KERRID_STAIR far below) | 2.4 MB | |
| 15 | `hollowmere_answers` | new | cue ~60 s: Liss's current-song into the fog, Hollowmere answering (CURRENT_SONG) | 1.0 MB | |
| 16 | `pale_rim` | sketch | loop ~150 s | 2.4 MB | 1.68 MB, 155.3 s, −16.03 LUFS |
| 16 | `drowned_choir` | sketch | loop ~150 s | 2.4 MB | 0.83 MB, 153.2 s, −16.00 LUFS |
| 16 | `kesh_bound` | new | sting (`kesh_summon` belongs to Act III's H03) | 0.2 MB | |
| 16 | `sefir_go_home` | new | cue ~2 min, the temptation (Sefir's motif at its warmest; ORDER_HUM) | 1.9 MB | |
| 16 | `abiding_guard` | new | boss, 2 stems; the storm waking early is stem 2 | 3.8 MB | |
| 16 | `act2_break` | new | ~90 s bed for the Rhen voice-over | 1.4 MB | |

**Total estimate: about 72 MB** for Act II's finals (14 zones about 31 MB, 6 bosses about 23 MB, scenes and stings
about 18 MB). It all goes to LFS. No single file goes over 5 MB (a boss's stems are separate files), so nothing here
needs ADR 0039's over-5-MB rule.

## Order of work
1. **The 12 zone finals from the sketches** (M3-AUD-840..843): **sources done**. Measured 17.4 MB in all (against 28.8
   estimated). Their audio lands with LFS.
2. **The six bosses**: the four whose models exist (drowner, engine, ram, wakefin): **sources done** (M3-AUD-844/845;
   two stems each, 74–84 s loops, 7.2 MB in all). Malcor Venn and the Abiding guard wait for their fights.
3. The new zones and the scene cues, as Act II's beat sheets are written (none exist yet: act_outline.md is the
   only source, so their timings wait on Story's sheets).
