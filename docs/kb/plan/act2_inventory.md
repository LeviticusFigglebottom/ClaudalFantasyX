# Act II inventory, in detail (2026-10-30)

The full branch-by-branch inventory behind [act2_plan.md](act2_plan.md) §3. Read-only research over every `origin/claude/*` branch; integration @ 89021833 at the time of the sweep. The plan's §3 summarises it; this file is the evidence.


Read-only research, 2026-10-30. Integration branch `origin/claude/new-session-mj8c3c` @ 89021833.  

## 0. Branch facts

- **18 remote branches.** None has Act II content that integration lacks, apart from the three unmerged fixes in the table below.
- **ADR 0041-blocked task files.** All 80 are byte-identical on the 12 current branches: act1-chapters, audio, battle-presentation, characters, creatures, creatures-b, env-art, env-art-b, hero-integration, m2-slice, ui and new-session-mj8c3c. `git diff` between those branches over the 80 paths is empty.
- **Branches with nothing to add:**
  - `first-playable`, `gate-runner-a` and `gate-runner-b` have unrelated histories (no merge base, last commits 10-23/10-24). They hold no Act II files.
  - `menus`, `undertow-lead-handoff-423ixt` and `undertow-lead-handoff-ze8rrn` are 0 commits ahead of integration. They hold only older copies (for example the sketch oggs on ze8rrn).
- **Unmerged Act II-relevant commits** (not on integration):

| Commit | What | On branches |
|---|---|---|
| `e1db6170` | M3-CRE-663: `kirru_roost` rebuilds byte for byte on every numpy SIMD path (`assets_src/environments/kits/haluna/ossa_fen.py`) | characters, creatures-b, env-art, m2-slice |
| `2224e784`, `c3f61ea6` (+2) | Primitive pass: the tide crawler rebuilt (crab carapace, jointed legs), and the paused **rim_crawler** rebuilt from it (`assets/creatures/rim_crawler/*`, creatures.json, portrait) | characters, creatures, creatures-b, m2-slice |
| `6b399185` | Act I audit: `grounding.pinned` (planted feet). It changes `rim_crawler.glb` and `root_crab.glb` | creatures |

- **Gate-run PNGs.** `docs/kb/qa/gate-runs/big14/out/*.png` holds the first PC renders (lead/gate-big14 @ 8707ff90, 2026-10-28) of the Act II shots that have no baseline. Examples: `creature_nhoa/hesk/ethren(_held)`, `kitrow_*`, `hollowmere_m01/m02`, `kite_k01_moored`, `kite_map`, `field_menu_kite`, `field_menu_map_{ansedra,keth_pass,lowlight}`, `battle_arena_drowned_choir_ring`. These PNGs exist only on act1-chapters, creatures and battle-presentation (with `.import` files there). Integration pruned `out/`.
- **Old Kerrid models.** `assets/characters/kerrid/*`, `avalanche_ram.glb` and `scree_crawler.glb` differ on act1-chapters and battle-presentation. Those copies are **older**: integration has 4 newer commits.
- **No branch** has `docs/kb/plan/`, an Act II beat sheet (`docs/kb/story/beats/act2_*`) or any `.dlg` for Ch10–16.
- **The placeholder audit is Act I only.** `tools/placeholder_audit.py` has `LAST_CHAPTER = 9`, and no branch has the `--act 2` option that ADR 0203 asks for.
  - **Runtime half:** Godot loads every Act I zone and arena, and flags visible capsule stand-ins, flat-coloured primitive or CSG meshes (greybox), and visible nodes named placeholder/temp/greybox/proxy.
  - **Static half:**
    - every foe, spawn, summon and Vowbound has a real actor scene;
    - every encounter has an arena (one with no arena fights on the sandbox, and an arena under `game/battle/arenas/` counts as greybox);
    - hero and bestiary portraits exist;
    - every `@sfx/@music/@ambience` cue resolves to a file;
    - no file is named like a placeholder.
  - Owners come from the ADR 0041 split. Severity is high, medium or low.
- **Governing ADRs:**
  - ADR 0041 paused this work.
  - ADR 0203 (accepted 10-30) lifts the pause for Act II once the Act I gate passes. Then the ADR-0041 tasks move from blocked to todo, and `docs/kb/plan/act2_plan.md` becomes the work list. Act III stays paused.
  - CONSOLIDATED.md line 6: this session writes `act2_plan.md`, `act2_tracks.md` and M4 tasks blocked-by ADR 0203.

---

## 1. Tasks with `blocked-by: ADR 0041` (80; identical on all 12 current branches)

Branches column: "all 12" means act1-chapters, audio, battle-presentation, characters, creatures, creatures-b, env-art, env-art-b, hero-integration, m2-slice, ui and new-session-mj8c3c. All 80 are `status: blocked`.

### 1a. Audio (19)
| id | title (short) | role | Done per notes | Open |
|---|---|---|---|---|
| M3-AUD-804 | Act II music sketches I (ossa_fen, reedhollow, sunken_vey, lowlight, keth_pass, quellan) | audio | Six ~62 s loops plus `act2_voices.py` kit. Plain git: `assets/audio/music/<cue>.ogg`. Cue rows, PROVENANCE | Superseded by the finals (music.json points at act2/) |
| M3-AUD-805 | Act II music sketches II (ansedra, lamp_archive, peace_wedding, unlamped, pale_rim, drowned_choir) | audio | Six ~61 s loops, −16 LUFS, deterministic | Superseded by the finals |
| M3-AUD-831 | Act II creature voices: Ch10-12 bosses, Wakefin, Ch10-11 regulars | audio | `assets_src/sfx/act2_creature_sfx.py`. 68 files in assets/audio/sfx/creatures. Rows in sfx_creatures.json and creature_voices.json | Listening pass. No `phase` event (Drowner uproot, Engine open) |
| M3-AUD-836 | Act III planning: motif map and cue list | audio | docs/kb/audio/act3_plan.md §1–4 | Story review |
| M3-AUD-837 | Prototype ADR 0172 build-time audio render | audio | tools/audio/build_render.py, measurements, ADR 0172 | PC cross-machine check |
| M3-AUD-839 | Act II final cues: list, sizes, LFS render path | audio | docs/kb/audio/act2_finals.md (30 cues). `render_all.py --act2`. 12 zone and 4 boss sources | Malcor Venn, the Abiding guard and the scene cues |
| M3-AUD-840 | Zone finals Ch10-11: ossa_fen, reedhollow, sunken_vey | audio | `assets_src/music/act2/{ossa_fen,reedhollow,sunken_vey}.py`, ~154 s loops | When written: "Lead adds music.json/PROVENANCE with LFS". **Now done on integration**: act2/*.ogg are LFS pointers and the music.json cues exist |
| M3-AUD-841 | Finals: lowlight, keth_pass, quellan | audio | Sources plus measurements | Design review, human listening |
| M3-AUD-842 | Finals Ch13-14: ansedra, lamp_archive, peace_wedding | audio | Sources plus measurements | Same as 840 (now in LFS on integration) |
| M3-AUD-843 | Finals Ch15-16: unlamped, pale_rim, drowned_choir | audio | Sources plus measurements | Same as 840 |
| M3-AUD-844 | Boss music: mangrove_drowner, lamp_engine (2 stems each) | audio | Sources. The intended `uprooted`/`opened` phase rows are written in the task | battle.encounters and phases rows wait on the encounters. The stems are now in LFS with cue rows on integration |
| M3-AUD-845 | Boss music: avalanche_ram, wakefin | audio | Sources plus measurements. Intended phases `ram_rage`, `wakefin_breaching` | Same as 844 |
| M3-AUD-849 | Act II creatures part 2: ridge lynx, cord moth, glass skate, flat-engine, 4 variants | audio | 33 more files (101 in total). Variants pitch-shift their parents | none listed |
| M3-AUD-851 | Write the Letting motif in motifs.py | audio | `letting()` plus test_motifs.py | Story review |
| M3-AUD-852 | Act III Ch17: hollowmere, dace_ledger | audio | Sources. **The renders are on integration** (`assets/audio/music/act3/hollowmere.ogg`, `dace_ledger.ogg`, LFS) | Design listening. music.json rows |
| M3-AUD-853 | Act III: the_kite, kite_maiden_flight | audio | Sources. Renders on integration (act3/, LFS) | Design review. music.json rows once ch18/kite exists |
| M3-AUD-856 | Act III Ch19: iskarra_ruins, iskarra_spire | audio | Sources. Renders on integration (act3/) | Design review. music.json rows |
| M3-AUD-858 | Act III: hesper_and_ilsabet (2 stems), kerrid_last_night | audio | Sources. Renders on integration (act3/) | Design review. Encounter phase ids. music.json rows |
| M3-AUD-859 | **Kite foley** (deck beds, engine stop, landing…) | audio | `assets_src/sfx/act3/kite_foley.py`. 16 files in LFS at `assets/audio/sfx/act3/`, with `.import`, PROVENANCE and `game/data/audio/sfx_act3.json` | Zone row `ch18/kite`. Ending cutscenes use `kite_deck_dark` |

### 1b. Battle presentation (3)
| id | title (short) | role | Done | Open |
|---|---|---|---|---|
| M3-BPR-408 | Act II bosses' camera: intros by enemy id; Lamp Engine opening; Ram charge | combat | choreo.json `boss_intro.by_enemy` (lamp_engine, avalanche_ram), `bosses.lamp_engine.phases.opened`, Ram `charge_side` camera plus pressure. tests/unit/test_battle_act2_bosses.gd | Shots wait on encounters. The Ram's `charge` run style waits on M3-BPR-410 / M3-AUD-838 (in review) |
| M3-BPR-418 | Next bosses: Mangrove Drowner, Wakefin | combat | Intros (BOSS_TITLE/EPITHET loc keys), `uprooted` moment, the Wakefin's blade-under telegraph plus camera pressure. The greybox arenas were withdrawn in favour of env-art's | Shots |
| M3-BPR-419 | Request: Act II boss encounters use the staged ids (milestone M4) | combat | Table of enemy, phase and arena ids: drowner/`uprooted`/`ossa_fen_roots`; lamp_engine/`opened`/`lowlight_engine_hall`; avalanche_ram/`keth_seep_terrace`; wakefin/`bridal_barge_night` | No boss encounters exist yet |

### 1c. Creatures (17)
| id | title (short) | role | Done | Open |
|---|---|---|---|---|
| M3-CRE-620 | Act II bestiary: roster, sheets, builds | character | docs/kb/art/creatures/act2_roster.md. Sheets in act2/ (4 bosses, 7 regulars, variants.md, flat_engine) | First PC renders |
| M3-CRE-621 | Build the Mangrove Drowner (Ch10 boss) | character | GLB 16.4k tris, 48 bones, phase `uprooted`, battle scene, creatures.json, shots plus baselines, tests. Polished by M3-CRE-622 (done) | Enemy row. VFX: snagged motes, telegraph. Break part not wired |
| M3-CRE-623 | Build the Lamp Engine (Ch11 boss) | character | 18.5k tris, phase `opened`, 12 clips, scene, row, shots | Enemy row. Break parts (rings) need geometry and a skill. VFX: lamps brightening, KO motes |
| M3-CRE-624 | Build the Avalanche Ram (Ch12 boss) | character | 15.2k tris (14.9k after M3-CRE-635), 38 bones, clips, scene, row | Enemy row. VFX: breath, snow, ice |
| M3-CRE-626 | Build the Wakefin (Ch15 boss) | character | 11.1k tris, clips, scene, row, shots `creature_wakefin` and `_body` | Enemy row. VFX: wake, sea-glow. The arena needs a water plane at y 0 |
| M3-CRE-627 | Four regulars Ch10-11: tannin archer, gallery ray, rime urchin, conduit crawler | character | Four GLBs, scenes, rows, tests, shots | Enemy `model` links. VFX: jet, frost, crawler dimming |
| M3-CRE-628 | Ridge lynx, cord moth, glass skate plus 4 variants (root_crab, fen_leech, scree_crawler, rim_crawler) | character | Seven GLBs, scenes, rows, tests, shots | Enemy `model` links. VFX |
| M3-CRE-635 | Act II bosses after the first PC render (Ram's head, Wakefin shot) | character | Ram head made camelid; Wakefin `creature_wakefin_body` shot plus stronger wounds | Baselines approved from the post-fix render |
| M3-CRE-637 | Build the flat-engine (Ch14 boss part on Malcor Venn's barge) | character | 7.6k tris, `Engine`/`EngineBroken` meshes, clips, scene, row, portrait row | Break part needs Liss's charge skill. No enemy row |
| M3-CRE-642 | **Nhoa** Vowbound model (Ice, Ch11) | character | GLB 14.8k tris, 1,623 mote beads as geometry, 13 clips, `vowbound_pending`, tests, summon-path test | vowbound.json row (combat). Summon VFX (Farewell-Tide column). First-call flag. PC render or baseline |
| M3-CRE-643 | **Hesk** Vowbound model (Holy, Ch12) | character | GLB 13.6k tris, knotted-cord primaries, 13 clips, tests | Same as Nhoa: vowbound.json row, Pass-Cord VFX, baseline |
| M3-CRE-644 | **Ethren** Vowbound model (Glimmer, Ch13) | character | GLB 14.4k tris, veil mesh, 13 clips, tests | vowbound.json row, Still Water VFX, baseline |
| M3-CRE-645 | Polish the plain reads: gallery ray, glass skate, ridge lynx muzzle | character | Re-modelled within budget, grounding kept | PC render of 3 shots |
| M3-CRE-646 | Act III bestiary roster (Vowbound held forms first) | character | act3_roster.md | Lead confirmation, sheets, builds |
| M3-CRE-647 | Six Vowbound as foes for Ch20 (held materials, `release` clip, held scenes) | character | `materials_held/`, `<id>_held` rows and scenes, `hold` phase key | Ch20 enemy rows, VFX, PC render |
| M3-CRE-648 | Act III sheets: Cage, Lamp Spire 3, Undertow 2 | character | Six sheets in docs/kb/art/creatures/act3/ | Lead review |
| M3-CRE-649 | Act III sheets: revisits plus **Kesh** | character | **Nothing written.** Research only | Four sheets, including vowbound/kesh.md |

### 1d. Environment (19)
| id | title (short) | role | Done | Open |
|---|---|---|---|---|
| M3-ENV-716 | Lowlight and Sunken Vey (Ch11): sheet, kit, Lamp Engine arena | environment | lowlight.md; `lowlight.py` (engine_hall, conduit_run, lamp_niche_tier, conduit_housing, nave bays, well_shaft, vey arcade/bridge, lowlight_sanctum, strangler_fig); `lut_ch11_vey`; arena `lowlight_engine_hall` (baseline) | PC render approval |
| M3-ENV-717 | Keth Pass (Ch12): sheet, kit, Ram arena | environment | keth_pass.md; `keth.py`; arena `keth_seep_terrace`; switchback, scree, trough; Quellan and Cloudloom pieces (cloudloom_hall, keth_curtain, quellan_house, woven_awning). Reworked after an **unapproved** PC render | PC render approval |
| M3-ENV-718 | Ossa Fen and Reedhollow (Ch10): sheet, kit, Drowner arena | environment | ossa_fen.md; `ossa_fen.py` (fen_bank_ground, mangrove_tree/dead, reed_bed, fen_far_mangroves, kirru_roost, name_shell_cord); `lut_ch10_fen`; arena `ossa_fen_roots` | PC render approval. kirru_roost determinism fix unmerged (M3-CRE-663) |
| M3-ENV-720 | Open sea at night (Ch15): bridal barge plus Wakefin arena | environment | open_sea_ch15.md; `bridal_barge.py`; `lut_ch15_unlamped`; arena `bridal_barge_night` | PC approval |
| M3-ENV-721 | Ansedra (Ch13–14): sheet, kit, Warden's escape arena | environment | ansedra.md; `ansedra.py` (bowl_dome, far domes, pursuit_barge, lacquer_hall, lacquer_court_ground, sanctum_basin, archive_stacks); `lut_ch14_wedding`; arena `ansedra_lagoon_escape` | PC approval |
| M3-ENV-722 | Pale Rim and Drowned Choir (Ch16): Choir arena | environment | pale_rim.md; `drowned_choir.py` (choir_singer, choir_amphitheatre, pale_rim_flats); `lut_ch16_choir`; arena `drowned_choir_ring` (**no baseline**) | PC approval |
| M3-ENV-723 | Hollowmere (Ch17): sheet, kit, grade | environment | hollowmere.md; `hollowmere.py` (hm_* pieces, dace_hull_frame); `zones/ch17` grade `lut_act3_dusk` | Placement (no shot yet) |
| M3-ENV-725 | The Kite (Ch18 hub) | environment | kite.md; `kite.py` (kite_hull, kite_rig, kite_engine) | Story review |
| M3-ENV-726 | Iskarra Lamp Spire (Ch19) | environment | iskarra.md, spire kit, `lut_ch19_spire`, arena `iskarra_spire_crown` | PC approval |
| M3-ENV-727 | Undertow layers (Ch20) | environment | Kit, `lut_ch20_abyss`, arena `undertow_cage` | PC approval |
| M3-ENV-728 | Undertow heart (Ch21) | environment | Kit, arenas `undertow_heart`, `undertow_heart_letting` | PC approval |
| M3-ENV-729 | Ending grades | environment | ending.md, 3 LUTs, ending_grades.json | Mood frames |
| M3-ENV-730 | Oruvel rebuilt (E7) | environment | `ov_rebuilt.py`, layout state `rebuilt` | Mood frame |
| M3-ENV-731 | Hollowmere and Kite preview scene plus shots | environment | `game/levels/_tests/hollowmere_kit/hollowmere_preview.tscn`; shots hollowmere_m01, m02, kite_k01 (no baseline) | Render review |
| M3-ENV-732 | Act II zone pieces in review rows (7 kitrow shots) | environment | `game/levels/_tests/late_kit_rows/late_kit_rows.tscn` | Render review |
| M3-ENV-733 | Ch10 walks: root_walk_6m, reed_causeway_6m, reed_platform_6m, clutch_stone; swap map | environment | `reedhollow.py`; ossa_fen.md §4 swap map; shot kitrow_fen_reedhollow_walks | Swap (act1-chapters) |
| M3-ENV-734 | Ch12: quellan_inn, quellan_well, hesk_dais; swap map | environment | keth.py; keth_pass.md §6 | Swap |
| M3-ENV-735 | Ch11: vey_gallery_walk_6m, lowlight_lamp_bench; swap map | environment | lowlight.md §5 | Swap |
| M3-ENV-736 | Request: swap Ch10–12 greyboxes onto env-art's kits (milestone M4) | cinematics | (request) | Every item open |

### 1e. UI / menus (6)
| id | title (short) | role | Done | Open |
|---|---|---|---|---|
| M3-UI-205 | The Kite's world map | ui | kite.json, KiteMapModel/Menu/Chart, kite.csv, kite_map.json, field-menu row behind `kite_flying`, tests; Act II destinations | Baselines (kite_map, field_menu_kite); Act III secrets |
| M3-UI-206 | Act II area maps (15 zones) | ui | zone_maps.json entries, maps_act2.csv, route to Ch16, tests, 3 shots | Baselines; objectives.json rows wait on the beat sheets |
| M3-UI-207 | Act II codex (14 places plus Kirru, Ullari) | ui | codex.json/csv, read flags | Narrative review; story entries; field_menu_codex count |
| M3-UI-208 | Request: Act II enemies.json rows for the bestiary | combat | (request) | Boss rows; `model` links on the regulars' rows |
| M3-UI-209 | Request: Act II shops, inns, shrines triggers (milestone M4) | cinematics | Data rows exist: shops.json (quellan_trader, ansedra_purveyor, hollowmere_chandler), inns, towns_act2.csv | Triggers, Shrine spawns, locations.json shrines |
| M3-UI-210 | Act card names Act III (for Ch16) | ui | act_card.json `acts."3"`, test | Ch16 `.dlg` call |

### 1f. M4 tasks (16)
| id | title (short) | role | Done | Open |
|---|---|---|---|---|
| M4-AUD-1001 | Request: voices for tannin archer, root crab, fen leech | audio | (request). **In effect satisfied:** creature_voices.json on integration has non-silent rows for all three (M3-AUD-831/849) | Close or verify |
| M4-C10-01 | Ch10 beat sheet | narrative | **Not started** (owner empty) | `docs/kb/story/beats/act2_ch10.md` |
| M4-C10-02 | Ch10 greybox (ossa_fen, reedhollow) | cinematics | `tools/act1/ch10_greybox.py`, Ch10Zone, layouts, ch10.json, flags, loc, tests | Story, Drowner encounter, kit swap |
| M4-C10-03 | Ch10 field fights (archer, root crab, fen leech) with sim bands | cinematics | enemies, skills and encounters rows; table in ch10_greybox.py; 3 balance suites (ch08_seawall loadout) | The Drowner; an Act II loadout; drain (M4-CMB-1001) |
| M4-C11-01 | Ch11 beat sheet | narrative | Not started | act2_ch11.md |
| M4-C11-02 | Ch11 greybox (sunken_vey, lowlight) | cinematics | ch11_greybox.py, zone, flags, tests | Story, Lamp Engine |
| M4-C11-03 | Ch11/12/16 field fights with sim bands | cinematics | 7 enemies, 5 skills, 7 encounters, 7 suites | Bosses; Act II loadout |
| M4-C12-01 | Ch12 beat sheet | narrative | Not started | act2_ch12.md |
| M4-C12-02 | Ch12 greybox (keth_pass, quellan, cloudloom) | cinematics | ch12_greybox.py, zone, flags, tests | Story, Ram |
| M4-C13-01 | Ch13 beat sheet | narrative | Not started | act2_ch13.md |
| M4-C13-02 | Ch13 greybox (ansedra, sanctum, lamp_archive) | cinematics | ch13_greybox.py, zone, flags, tests | Story |
| M4-C14-01 | Ch14 beat sheet | narrative | Not started | act2_ch14.md |
| M4-C14-02 | Ch14–16 greybox (lacquer court, open sea, Hollowmere first visit, pale rim, drowned choir) | cinematics | ch14_greybox.py, ch15_16_greybox.py, Ch15/16/17 zones, 5 flags, tests | Story; Venn, Wakefin, Abiding guard |
| M4-C15-01 | Ch15 beat sheet | narrative | Not started | act2_ch15.md |
| M4-C16-01 | Ch16 beat sheet | narrative | Not started | act2_ch16.md |
| M4-CMB-1001 | Request: drain field on enemy skills (fen leech) | combat | (request) | Engine field, tests |

(Totals: 19 + 3 + 17 + 19 + 6 + 16 = 80.)

### 1g. Related Act II tasks NOT blocked by ADR 0041 (integration status)
| id | status | relevance |
|---|---|---|
| M3-CRE-622 drowner-polish | done | The Drowner's current mesh |
| M3-BPR-410 charge-style-sound-request | todo | The Avalanche Ram's charge run sound |
| M3-AUD-838 charge-style-sound | review | Its answer |
| M3-C09-07 pell-battle-kit | todo | Pell fights from Ch10 |
| M3-BPR-1340 pell-battle-framing-request | todo | Pell in battle |
| M3-CIN-1240 pell-face-poses-request | todo | Pell cutscenes |
| M3-NAR-1000 pell-arc-echo-and-sheet-questions | todo | Pell and Kerrid sheet questions |
| M3-CRE-663 kirru-roost-host-determinism | todo | Fix `e1db6170` unmerged (characters, creatures-b, env-art, m2-slice) |
| M3-ENV-719 rhen-lantern-housing-mark | todo | Ch11 housing-mark reveal prop on Rhen's lantern |
| M3-HER-1230 drowned-choir-body-pop | todo | Rhen's field body pops in ch16/drowned_choir |
| M3-CRE-634 portrait-test-enemies-only | review | Bestiary portrait test scope (Act II creatures) |
| M3-CHR-505 kerrid-hero | review | Kerrid's model (needed for the Ch15 reveal) |

---

## 2. Assets, scenes, data, music and tests by category

"Int?" = on integration. "Final bar" = ADR 0041 §3: no greybox, capsule or box stand-in; no placeholder texture, portrait or sound; every enemy has mesh, rig, animation, VFX and sounds; areas dressed, lit and walkable.

### 2a. Zones (playable levels)
| Item | Paths | Branches | Int? | State | Final bar |
|---|---|---|---|---|---|
| Ossa Fen, Reedhollow (Ch10) | `game/levels/ch10/{ossa_fen,reedhollow}/*.tscn,*_layout.json`, `game/levels/ch10/ch10_zone.gd`, gen `tools/act1/ch10_greybox.py` | all 12 | yes | Greybox: 81 and 84 blocks, 0 kit refs. Ossa Fen has 5 random encounters; 1 shot each | **no**: greybox blocks, no kit swap, no story, no NPCs |
| Sunken Vey, Lowlight (Ch11) | `game/levels/ch11/{sunken_vey,lowlight}/…`, `ch11_greybox.py` | all 12 | yes | Greybox: 65 and 36 blocks | **no** |
| Keth Pass, Quellan, Cloudloom (Ch12) | `game/levels/ch12/{keth_pass,quellan,cloudloom}/…`, `ch12_greybox.py` | all 12 | yes | Greybox: 55, 27 and 55 blocks | **no** |
| Ansedra, Sanctum, Lamp Archive, Lacquer Court (Ch13–14) | `game/levels/ch13/{ansedra,sanctum,lamp_archive,ansedra_lacquer_court}/…`, `ch13_greybox.py`, `ch14_greybox.py` | all 12 | yes | Greybox: 86, 22, 20 and 39 blocks | **no** |
| Open sea (Ch15) | `game/levels/ch15/open_sea/…`, `ch15_16_greybox.py` | all 12 | yes | Greybox: 9 blocks | **no** |
| Hollowmere first visit (Ch15/17) | `game/levels/ch17/hollowmere/…`, `ch17_zone.gd` | all 12 | yes | Greybox: 73 blocks | **no** |
| Pale Rim, Drowned Choir (Ch16) | `game/levels/ch16/{pale_rim,drowned_choir}/…` | all 12 | yes | Greybox: 15 and 25 blocks. Pale Rim has 5 encounters | **no** (and M3-HER-1230 body pop) |
| Chapter flow | `game/data/flow/chapters/ch10.json`…`ch16.json`; `game/data/world/locations.json` (15 Act II locations); flags `ch10_started`…`ch16_reached_choir` (15) in flags.tres; loc `game/data/loc/ch10.csv`…`ch16.csv` | all 12 | yes | Arrival, there-and-back and hand-offs only. Ch9 does not yet hand off to Ch10 | **no**: no story beats |

### 2b. Environment kits, arenas, grades (env-art)
| Item | Paths | Branches | Int? | State | Final bar |
|---|---|---|---|---|---|
| Ossa Fen / Reedhollow kit | `assets_src/environments/kits/haluna/{ossa_fen,reedhollow,fen_zone_lut}.py`; GLBs `assets/environments/kits/haluna/{fen_bank_ground,mangrove_tree,mangrove_dead,reed_bed,fen_far_mangroves,kirru_roost,name_shell_cord,root_walk_6m,reed_causeway_6m,reed_platform_6m,clutch_stone}.glb`; `kit_fen_*.tres`; `lut_ch10_fen.png`; tests `tools/tests/test_ossa_fen.py`, `test_reedhollow.py` | all 12 (kirru_roost fix only on characters, creatures-b, env-art, m2-slice) | yes | Built. Kitrow shots unrendered on integration | partial: real kit, not placed in the zone, PC render not approved |
| Lowlight / Vey kit | `lowlight.py`, `lowlight_zone_lut.py`; `{engine_hall,conduit_run,lamp_niche_tier,conduit_housing,lowlight_nave_bay(_broken),well_shaft,vey_arcade_bay,vey_gallery_bridge,vey_gallery_walk_6m,lowlight_sanctum,lowlight_lamp_bench,strangler_fig}.glb`; `kit_lowlight_*`; `lut_ch11_vey`; `test_lowlight.py`, `test_lowlight_housing.py` | all 12 | yes | Built | partial (same reasons) |
| Keth / Quellan / Cloudloom kit | `keth.py`, `keth_zone_lut.py`; `{keth_terrace_ground,lit_terrace_wall,seep_pool,pass_cord,keth_far_ridges,keth_road_switchback,keth_scree_slope,woolback_trough,cloudloom_hall,keth_curtain,quellan_house,woven_awning,quellan_inn,quellan_well,hesk_dais,cairn}.glb`; `kit_keth_*`; `lut_ch12_heights`; `test_keth.py` | all 12 | yes | Built. Reworked after a failed PC render | partial |
| Ansedra / Lacquer Court kit | `ansedra.py`; `{bowl_dome,ansedra_far_domes(_lit),pursuit_barge,lacquer_hall,lacquer_court_ground,sanctum_basin,archive_stacks}.glb`; `kit_lacquer_black/red`, `kit_window_lit`; `lut_ch14_wedding`; `test_ansedra.py` | all 12 | yes | Built. The −4° red hue turn is left to Rendering | partial |
| Bridal barge (Ch15) | `bridal_barge.py`; `bridal_barge.glb`; `lut_ch15_unlamped`; `test_bridal_barge.py` | all 12 | yes | Built | partial |
| Pale Rim / Choir kit | `drowned_choir.py`; `{choir_singer,choir_amphitheatre,pale_rim_flats}.glb`; `kit_rim_sand`; `lut_ch16_choir`; `test_drowned_choir.py` | all 12 | yes | Built | partial |
| Hollowmere kit (Ch17) | `hollowmere.py`, `hollowmere_grades.py`, `hollowmere_preview.py`; `hm_*` GLBs, `dace_hull_frame`; `assets/environments/zones/ch17/` (lut_act3_dusk) | all 12 | yes | Built; preview scene `game/levels/_tests/hollowmere_kit/hollowmere_preview.tscn` | partial |
| Kite kit (Ch18) | `kite.py`; `{kite_hull,kite_rig,kite_engine}.glb`; `test_kite.py` | all 12 | yes | Built; shot kite_k01_moored (no baseline) | partial (Act III) |
| Battle arenas | `assets/environments/arenas/{ossa_fen_roots,lowlight_engine_hall,keth_seep_terrace,bridal_barge_night,ansedra_lagoon_escape,drowned_choir_ring}/`; rows in `game/data/battle/arenas.json`; previews `game/levels/_tests/battle_arenas/preview_*.tscn` | all 12 | yes | Built. Baselines (llvmpipe) for 5 of 6; **drowned_choir_ring has no baseline**. No encounter uses them yet (Act II encounters have no `arena`) | partial: previews use stand-in enemies; PC approval pending |
| Kit review rows | `game/levels/_tests/late_kit_rows/late_kit_rows.tscn`; shots `kitrow_*` ×10 | all 12 | yes | No baselines. Big14 PC PNGs exist only on act1-chapters, creatures, battle-presentation | partial |

### 2c. Creatures (bosses, regulars, variants, boss part)
Each has `assets_src/creatures/<id>/build_<id>.py` + `materials.json`, `assets/creatures/<id>/<id>.glb` + `materials/`, `game/creatures/<id>/<id>_battle.tscn`, a creatures.json row, a stage `game/levels/_tests/creatures/shots/creature_<id>.tscn`, a portrait `assets/ui/portraits/creatures/<id>.png`, voice and SFX rows, and tests in `tests/unit/test_creature_actor.gd`. All 12 branches have them; all are on integration.

| Item | Enemy row (enemies.json) | Encounter | Baseline | Final bar |
|---|---|---|---|---|
| mangrove_drowner (Ch10 boss) | **none** | none | yes (+`_risen`) | partial: mesh, rig, anim, sound and staging done; no enemy or encounter; VFX not built; break part unwired |
| lamp_engine (Ch11 boss) | none | none | yes (+`_opened`) | partial (same) |
| avalanche_ram (Ch12 boss) | none | none | yes | partial (same); charge sound in review |
| wakefin (Ch15 boss) | none | none | yes (+`_body`) | partial (same) |
| flat_engine (Ch14 boss part) | none | none | yes | partial; break part needs Liss's skill; no Malcor Venn |
| tannin_archer, root_crab, fen_leech (Ch10) | yes (act: 2), **no `model` key** | ch10_fen_archers, _roots, _leeches (no arena) | yes | partial: models exist but enemy rows don't link them, so battles use capsules on the sandbox arena; no VFX (jet etc.); root_crab grounding fix unmerged (creatures) |
| gallery_ray, rime_urchin (Ch11) | yes, no `model` | ch11_vey_rays, ch11_vey_urchins | yes | partial (same) |
| conduit_crawler (Ch11) | **none** | none | yes | partial |
| ridge_lynx, cord_moth, scree_crawler (Ch12) | yes, no `model` | ch12_pass_lynxes, _moths, _scree | yes | partial |
| glass_skate, rim_crawler (Ch16) | yes, no `model` | ch16_rim_skates, ch16_rim_crawlers | yes | partial; the rim_crawler rebuild is unmerged (characters, creatures, creatures-b, m2-slice) |
| Malcor Venn (Ch14 boss) | none | none | – | **no**: no character model, sheet, music or encounter. Only the flat_engine, the pursuit_barge and the arena `ansedra_lagoon_escape` exist |
| Sefir's Abiding guard (Ch16 boss) | none | none | – | **no**: only the arena `drowned_choir_ring`; nothing in creatures or characters |

### 2d. Vowbound
| Item | Paths | Int? | State | Final bar |
|---|---|---|---|---|
| Nhoa (Ice, Ch11) | `assets_src/creatures/nhoa/`, `assets/creatures/nhoa/` (+`materials_held`), `game/creatures/nhoa/nhoa_battle.tscn`, `nhoa_held_battle.tscn`, sheet `docs/kb/art/creatures/vowbound/nhoa.md`, tests `tests/unit/test_creature_nhoa_vowbound.gd`, `tests/integration/test_nhoa_summon_path.gd`, portrait `nhoa.png`, `nhoa_held.png` | yes | Model done. `vowbound_pending` (no `game/data/battle/vowbound.json` row: it holds only ilun, kahre, virel). No skills, VFX, voice or first-call flag. Shot has no baseline (PC PNG only on act1-chapters, creatures, battle-presentation) | partial |
| Hesk (Holy, Ch12) | same pattern, `hesk` | yes | Same | partial |
| Ethren (Glimmer, Ch13) | same pattern, `ethren` | yes | Same | partial |
| Kesh (Ch16) | — | no | Nothing: M3-CRE-649 wrote no sheet. Only story (vowbound.md §7) and the greybox mark `kesh` | **no** |

### 2e. Music and audio
| Item | Paths | Int? | State | Final bar |
|---|---|---|---|---|
| 12 zone finals | `assets_src/music/act2/{ossa_fen,reedhollow,sunken_vey,lowlight,keth_pass,quellan,ansedra,lamp_archive,peace_wedding,unlamped,pale_rim,drowned_choir}.py` → `assets/audio/music/act2/*.ogg` (LFS pointers) + `.loop.json`; cue rows in `game/data/audio/music.json` `cues` | yes (all 12 branches) | Rendered and committed (LFS). **No `zones` rows for ch10+** in music.json. Human listening pending | partial (assets final; not wired to zones) |
| 4 boss finals (2 stems each) | `assets_src/music/act2/{mangrove_drowner,lamp_engine,avalanche_ram,wakefin}.py` → `act2/*_p1/_p2.ogg` | yes | Cue rows exist. **No `battle.encounters` or `battle.phases` rows** (`uprooted`, `opened`, `ram_rage`, `wakefin_breaching` are only written in the task files) | partial |
| Missing Act II cues | Malcor Venn boss, the Abiding guard boss, scene cues (act2_finals.md) | – | Not written | **no** |
| Sketches (superseded) | `assets_src/music/*.py` and `assets/audio/music/{ossa_fen,…}.ogg` (plain git) | yes | Kept as source material | n/a |
| Shared Act II voices | `assets_src/music/act2_voices.py`; `motifs.py` `letting()` | yes | – | – |
| Act II creature SFX | `assets_src/sfx/act2_creature_sfx.py` → 101 files `assets/audio/sfx/creatures/cre_<id>_*`; `sfx_creatures.json`, `creature_voices.json`; `tools/tests/test_act2_creature_sfx.py` | yes | Done for all 15 Act II creatures. No phase-change event or sting | partial (listening pass) |
| Kite foley (M3-AUD-859) | `assets_src/sfx/act3/kite_foley.py` → `assets/audio/sfx/act3/` (16 files, LFS); `game/data/audio/sfx_act3.json` | yes | Done. Zone row `ch18/kite` pending (no zone) | partial (Act III) |
| Act III music (relevant: hollowmere, kerrid_last_night, the_kite) | `assets_src/music/act3/*.py` → `assets/audio/music/act3/*.ogg` (LFS) | yes | No music.json rows | partial |
| Render tests | `tools/tests/test_act2_finals.py`, `tools/audio/render_all.py` (`ACT2_FINALS`, `ACT3_FINALS`, `ACT3_SFX`) | yes | – | – |

### 2f. Battle presentation, balance, combat data
| Item | Paths | Int? | State | Final bar |
|---|---|---|---|---|
| Boss staging | `game/data/battle/choreo.json` (`boss_intro.by_enemy` drowner, lamp_engine, avalanche_ram, wakefin; `bosses.*.phases`; `camera.pressure.by_enemy`); loc BOSS_TITLE/EPITHET in strings.csv; `tests/unit/test_battle_act2_bosses.gd`; `tools/validate_choreo.py` | yes | Keyed by enemy id, waiting on enemy rows. No boss-intro shots | partial |
| Act II skills | skills.json: tannin_jet, root_drag, leech_bite, glide_lash, rime_spine, unravel, scree_slide, skate_sting | yes | Flagged for combat review. No drain field (M4-CMB-1001) | partial |
| Balance (ch10/11/12/16) | `tools/balance/targets.json`: 10 suites (ch10_fen_archers, _leeches, _roots; ch11_vey_rays, _urchins; ch12_pass_lynxes, _moths, _scree; ch16_rim_crawlers, _skates) on the **ch08_seawall** loadout, 1000 seeds, `--check` clean | yes | No boss suites; no Act II loadout or shops tuning | partial |
| Random-encounter tables | In the zone layouts (`encounters` blocks) from `tools/act1/ch1x_greybox.py` | yes | – | – |

### 2g. Act II menus and UI
| Item | Paths | Int? | State | Final bar |
|---|---|---|---|---|
| Kite world map | `game/data/world/kite.json`, `game/data/ui/kite_map.json`, `game/data/loc/kite.csv`, `game/ui/kite/{kite_chart,kite_map_menu,kite_map_model,kite_map_shot}.gd`, tests `test_kite_map.gd`, `test_input_parity_kite_map.gd`, `test_field_menu_kite.gd`, `tools/tests/test_kite_validate.py` | yes | Built; shots kite_map, field_menu_kite have no baseline | partial |
| Area maps | `game/data/ui/zone_maps.json` (15 Act II zones), `game/data/loc/maps_act2.csv`, shots field_menu_map_{keth_pass,lowlight,ansedra} | yes | Follows the greybox layouts; no baselines; no objectives | partial (tied to greybox) |
| Codex | `game/data/lore/codex.json`, `game/data/loc/codex.csv` (14 places, Kirru, Ullari), `codex_*_read` flags | yes | Narrative review pending; no story entries | partial |
| Act card III | `game/data/ui/act_card.json` `acts."3"`, `tests/unit/test_act_card.gd` | yes | Done | yes (needs a Ch16 `.dlg` call) |
| Shops and inns | `game/data/items/shops.json` (quellan_trader, ansedra_purveyor, hollowmere_chandler), inn rows, `game/data/loc/towns_act2.csv` | yes | Data only; no triggers or shrines in zones | partial |
| Bestiary | Lists enemies.json rows; portraits exist for all Act II creatures | yes | 10 regular rows listed without `model`; no bosses | partial |

### 2h. Characters relevant to Act II
| Item | Paths | Int? | State | Final bar |
|---|---|---|---|---|
| Kerrid (party; Ch15 reveal) | `assets_src/characters/kerrid/*`, `assets/characters/kerrid/*`, `game/characters/heroes/kerrid_battle.tscn`, `game/hero_motion/battle/kerrid_battle_actor.tscn`, portraits `kerrid_*.png` | yes (older copies on act1-chapters and battle-presentation) | M3-CHR-505 in review. **No reveal content**: no motes-leaving-hands VFX, no beat sheet, no `.dlg` | partial (model); **no** (reveal) |
| Pell (party from Ch10) | `assets/characters/pell/`, `game/characters/heroes/pell_battle.tscn`, `pell_name_shell.gd` | yes | Battle kit todo (M3-C09-07) | partial |
| Sefir | `assets/characters/sefir/` | yes | Act I model reused | – |
| Tobin, Merel Dask, Malcor Venn, Corran, Cantor, Liss's father, Kirru and Ullari folk, Ressa | — | no | Nothing on any branch | **no** |

### 2i. Set pieces
| Item | What exists | Final bar |
|---|---|---|
| Peace wedding (Ch14) | Music `peace_wedding` (final, LFS); greybox `ch13/ansedra_lacquer_court` (marks `vows`, `tobin_falls`, `kerrid_steps`, `barge_deck`, `merel_gate`); kit `lacquer_hall`, `lacquer_court_ground`, `bridal_barge`, `pursuit_barge`; arena `ansedra_lagoon_escape`; grade `lut_ch14_wedding` | **no**: no beat sheet, cast models, cutscene or escape staging |
| Kerrid reveal (Ch15) | Greybox marks `tobin_bier`, `kerrid_sits`, `bow`, the Shoal in `ch15/open_sea`; music `unlamped` | **no** |
| Farewell-tide (Ch10) | Music `reedhollow` (clutch line, swappable for the Letting); kit `kirru_roost`, `name_shell_cord`, `clutch_stone` | **no** |
| Drowned Choir / act break (Ch16) | Greybox (`kesh`, `sefir`, `kerrid_line`); `drowned_choir` music; arena; act card III | **no** |

### 2j. Tests (all on integration and all 12 branches)
- **Greybox flow:**
  - `tests/integration/act2_greybox_case.gd`;
  - `test_ch10_thread.gd`, `test_ch10_walkable.gd`, `test_ch11_thread.gd`, `test_ch11_walkable.gd`, `test_ch12_thread.gd`, `test_ch12_walkable.gd`, `test_ch13_thread.gd`, `test_ch13_walkable.gd`;
  - `test_ch14_16_thread.gd`, `test_ch14_16_walkable.gd`.
- **Vowbound:**
  - `tests/integration/test_{nhoa,hesk,ethren}_summon_path.gd`;
  - `tests/unit/test_creature_{nhoa,hesk,ethren}_vowbound.gd`;
  - `tests/unit/test_creature_vowbound_held.gd`.
- **Creatures and battle:** `tests/unit/test_creature_actor.gd` (Act II cases), `tests/unit/test_battle_act2_bosses.gd`.
- **UI:** `tests/unit/test_kite_map.gd`, `test_input_parity_kite_map.gd`, `test_field_menu_kite.gd`, `test_act_card.gd`, `test_zone_map`, `test_codex.gd`.
- **Tools:** `tools/tests/test_{ossa_fen,reedhollow,lowlight,lowlight_housing,keth,ansedra,bridal_barge,drowned_choir,hollowmere,kite,kite_validate,act2_finals,act2_creature_sfx}.py`.
- **Screenshot ids** (tests/screenshots/shots.json).
  - With baselines:
    - all 15 Act II creatures, plus the variants `_risen`, `_opened` and `_body`;
    - 5 arenas: ossa_fen_roots, lowlight_engine_hall, keth_seep_terrace, bridal_barge_night, ansedra_lagoon_escape.
  - **Without baselines:**
    - `battle_arena_drowned_choir_ring`, `iskarra_spire_crown`, `undertow_cage`, `undertow_heart(_letting)`;
    - `hollowmere_m01_dace_hull`, `hollowmere_m02_raft_city_dusk`, `kite_k01_moored`;
    - `kitrow_{ansedra_court_hall,ansedra_basin_stacks,keth_cloudloom_house,keth_road_details,lowlight_nave_bays,lowlight_vey_details,fen_roost_cord,fen_reedhollow_walks,quellan_inn_well_dais,vey_gallery_walk_bench}`;
    - `creature_{nhoa,hesk,ethren}` and `creature_{ilun,kahre,virel,hesk,nhoa,ethren}_held`;
    - `kite_map`, `field_menu_kite`, `field_menu_map_{keth_pass,lowlight,ansedra}`.
  - No Act II boss-intro shots exist.

---

## 3. Story and dialogue docs for Act II

| Doc | Path | State |
|---|---|---|
| Act outline, Act II (Ch10–16) | `docs/kb/story/beats/act_outline.md` (§"ACT II: THE TRUTH", line 111–168) | The only chapter-level story source |
| Beat sheets Ch10–16 | `docs/kb/story/beats/act2_ch10.md` … `act2_ch16.md` | **Do not exist on any branch** (M4-C10-01 … M4-C16-01 unstarted) |
| `.dlg` scripts Ch10–16 | `game/data/dialogue/ch10…ch16/` | **None on any branch** (dialogue dirs stop at ch09) |
| Act I hand-off to Act II | `docs/kb/story/beats/act1_ch09.md` §10 (B11 act card "Act II: The Truth"; flags `ch09_pell_joined`, `ch09_kerrid_on_road`, `ch09_asha_said_they_hung_back`, `ch09_ebbing_danced`, `ch09_act_one_complete`) | Done |
| Act I flags read by Act II | Flag tables in `act1_ch04.md` (`ch04_saw_ysolde_ink` → Ch13), `act1_ch05.md` (`ch05_heard_straw_cape_tale` → Ch15), `act1_ch06.md` (`ch06_met_sefir`, `ch06_rhen_greeted_sefir`, `ch06_liss_read_lantern`, `ch06_saw_lamp_buried`, `ch06_dug_without_asking`, `ch06_inquisitor_yielded`), `act1_ch08.md` (`ch08_liss_found_marks`, `ch08_fishwife_called`, `ch08_rhen_froze`), `act1_ch09.md` | Payoffs to place |
| Restaging ADRs | `docs/kb/decisions/0016-act-two-restaging.md`, `0020-kerrid-restaging.md`, `0022-dace-imra-strangers-sweep-f.md`; `0017-act-one-restaging.md` | Canon |
| Vowbound | `docs/kb/story/vowbound.md` §4 Hesk, §5 Nhoa, §6 Ethren, §7 Kesh | Canon |
| Characters | `docs/kb/story/characters/{kerrid,pell,sefir_aurane,liss_varrow,toma_okeru,ysolde,asha_velamir,rhen_sallow}.md` | Act II arcs inside |
| Bible, voice, glossary | `docs/kb/story/bible.md`, `voice_guide.md`, `glossary_additions.md`, `decisions_log.md`, `docs/kb/glossary.md` | – |
| Colour script | `docs/kb/art/color_script.md` §Act II (lines 404–538: ch10…ch16) | Done |
| Environment sheets | `docs/kb/art/environments/{ossa_fen,lowlight,keth_pass,ansedra,open_sea_ch15,pale_rim,hollowmere,kite}.md` (swap maps: ossa_fen §4, lowlight §5, keth_pass §6) | Done |
| Creature sheets | `docs/kb/art/creatures/act2_roster.md`, `act2/{README,mangrove_drowner,lamp_engine,avalanche_ram,wakefin,flat_engine,tannin_archer,gallery_ray,rime_urchin,conduit_crawler,ridge_lynx,cord_moth,glass_skate,variants}.md`, `vowbound/{nhoa,hesk,ethren}.md` (no kesh.md) | Done except Kesh |
| Audio plans | `docs/kb/audio/act2_finals.md`, `act3_plan.md`, `listening_notes.md` | Done (Measured column Lead-owned) |
| Act III ending | `docs/kb/story/beats/act3_ending.md` | Exists (paused) |
| Pause/lift | `docs/kb/decisions/0041-act1-final-quality-first.md`, `0203-act2-starts-when-act1-is-complete.md` | 0203 accepted 10-30 |

---

## 4. Task ids (to avoid collisions)

### 4a. Every task in `docs/kb/tasks/M4/`, across all branches
The same 16 files are on the 12 current branches. The other 6 branches have no M4 folder. Every frontmatter `id` matches its filename.

| id | file |
|---|---|
| M4-AUD-1001 | M4-AUD-1001-act2-fen-voices.md |
| M4-C10-01 | M4-C10-01-ch10-beat-sheet.md |
| M4-C10-02 | M4-C10-02-ch10-greybox.md |
| M4-C10-03 | M4-C10-03-ch10-field-fights.md |
| M4-C11-01 | M4-C11-01-ch11-beat-sheet.md |
| M4-C11-02 | M4-C11-02-ch11-greybox.md |
| M4-C11-03 | M4-C11-03-act2-regulars.md |
| M4-C12-01 | M4-C12-01-ch12-beat-sheet.md |
| M4-C12-02 | M4-C12-02-ch12-greybox.md |
| M4-C13-01 | M4-C13-01-ch13-beat-sheet.md |
| M4-C13-02 | M4-C13-02-ch13-greybox.md |
| M4-C14-01 | M4-C14-01-ch14-beat-sheet.md |
| M4-C14-02 | M4-C14-02-ch14-16-greybox.md |
| M4-C15-01 | M4-C15-01-ch15-beat-sheet.md |
| M4-C16-01 | M4-C16-01-ch16-beat-sheet.md |
| M4-CMB-1001 | M4-CMB-1001-drain.md |

Unused ids referenced in text: M4-C15-02 and M4-C16-02 are named as "the greybox" in M4-C15-01 and M4-C16-01, but no such files exist. The Ch15–16 greybox is M4-C14-02.

Milestone-M4 tasks filed under `docs/kb/tasks/M3/`: M3-BPR-419, M3-ENV-736, M3-UI-209.

### 4b. Highest id per prefix, across all 18 branches (union of filenames)
The numbers are spread over per-track **id blocks** (CONSOLIDATED-history-2026-10-28 §4):

| Track | Block |
|---|---|
| m2-slice | 100–199 |
| ui | 200–299 |
| menus | 300–399 |
| battle-presentation | 400–499 |
| characters | 500–599 |
| creatures | 600–699 |
| env-art | 700–799 |
| audio | 800–899 |
| PC | 900–999 |
| Lead | 1000–1099 |
| hero-integration | 1100–1199 |
| act1-chapters | 1200–1299 |

ADRs follow the same order in blocks of ten, from 0100. act1-chapters takes ADR 0200–0209.

Observed 1300s ids: env-art-b (ENV 1303–1327), BPR-1305/1325/1340, ARC-1324/1326, RND-1315. creatures-b uses its own `M3-CRB-001..013`.

| Prefix | # ids | Highest | Other number ranges in use |
|---|---|---|---|
| M3-ARC | 7 | M3-ARC-1326 | 3–4, 1216, 1324 |
| M3-AUD | 85 | **M3-AUD-864** (audio only) | 01–1xx, 800s |
| M3-BPR | 31 | M3-BPR-1340 | 01–, 400–427, 1305, 1325 |
| M3-C01 | 6 | M3-C01-101 | |
| M3-C04 | 8 | M3-C04-1226 | |
| M3-C05 | 9 | M3-C05-1215 | |
| M3-C06 | 8 | M3-C06-1200 | |
| M3-C07 | 9 | M3-C07-1211 | |
| M3-C08 | 7 | M3-C08-1210 | 100–102 |
| M3-C09 | 12 | M3-C09-1209 | 01–10, 201 |
| M3-CHR | 45 | M3-CHR-1218 | 500–592, 1000–1001 |
| M3-CIN | 9 | M3-CIN-1240 | 1231–1234 |
| M3-CMB | 2 | M3-CMB-02 | |
| M3-CRB | 13 | M3-CRB-013 (creatures-b only) | |
| M3-CRE | 64 | **M3-CRE-700** (act1-chapters, characters, creatures-b, m2-slice; renamed from a 627 collision) | 600–664 (highest in block: 664) |
| M3-ENV | 104 | **M3-ENV-1327** (env-art-b only) | 700–746, 1000s, 1200s, 1300s; plus 04B/07B/08B/09B |
| M3-HER | 47 | M3-HER-1230 | 1100s, 1219–1227 |
| M3-MNU | 3 | M3-MNU-04 | |
| M3-NAR | 2 | M3-NAR-1000 | 01 |
| M3-PRG | 1 | M3-PRG-1207 | |
| M3-RBL | 3 | M3-RBL-1208 | 01, 201 |
| M3-RND | 11 | M3-RND-1315 | 01–28 |
| M3-UI | 16 | M3-UI-1212 | 200–211 |
| M4-AUD | 1 | M4-AUD-1001 | |
| M4-C10 | 3 | M4-C10-03 | |
| M4-C11 | 3 | M4-C11-03 | |
| M4-C12 | 2 | M4-C12-02 | |
| M4-C13 | 2 | M4-C13-02 | |
| M4-C14 | 2 | M4-C14-02 | |
| M4-C15 | 1 | M4-C15-01 | |
| M4-C16 | 1 | M4-C16-01 | |
| M4-CMB | 1 | M4-CMB-1001 | |
| M2-* (for reference) | | ARC-12, AUD-17, BPR-1000, CHR-544, CMB-08, CRE-10, ENV-1000, FP-1001, HER-1128, MNU-306, NAR-01, NIT-06, QA-100, RND-910, UI-1000 | |
| M1-* | | ARC-17, ART-06, AUD-02, CHR-15, CMB-08, ENV-11, LEAD-01, NAR-12, NIT-02, PRG-03, QA-10, RND-29, UI-11 | |
| M0-LEAD | | M0-LEAD-01 | |

**Free for new M4 work:**
- Every M4 role prefix other than AUD, CMB and C10–C16 is unused: ENV, CRE, CRB, BPR, UI, CHR, NAR, CIN, RND, HER, PRG, QA, ARC.
- In M4-AUD and M4-CMB, only 1001 is taken.
- M4-C10 through M4-C16 run to at most -03.
