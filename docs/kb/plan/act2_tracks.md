# Act II track split and ownership globs (PROPOSED)

- **Status: proposed.** The Lead applies it to `docs/kb/ownership.md` and `docs/kb/handoffs/live/SESSION-BRIEFS.md` at the gate (ADR 0203). This file changes neither of them.
- **Author:** the act2-plan track, 2026-10-30. **Companion:** [act2_plan.md](act2_plan.md) (the work list) and the `M4-A2P-*` tasks.

## 1. Principles

1. **Keep Act I's tracks and their pipelines; split by chapter, not by discipline,** where one discipline is the bottleneck (ADR 0041 §5). Act I's tracks know their generators, import kinds and gotchas, and those carry straight over.
2. **Act I stays protected** (ADR 0203). Every Act II track keeps the duty to take Act I FAST-TRACK rows first. No Act II change may break an Act I test or shot without the owner's fix in the same batch.
3. **One owner per path.** Act II paths are new (`ch1[0-6]`, `act2`, the new creature ids), so the globs below don't overlap Act I's. Where an Act I row already claims a broad glob that would swallow an Act II path (act1-chapters' `game/levels/ch1[0-9]/**`), the Lead narrows or re-assigns it explicitly (§3).
4. **Start small** (SESSION-BRIEFS' rule): the tracks on the critical path first (§4), the rest as their inputs land.

## 2. The tracks

| Track | From Act I | Act II scope | Branch (proposed) | Start |
|---|---|---|---|---|
| **chapters** (was act1-chapters) | continues | Ch10–Ch16 encounters, NPC and trigger placement, field cameras, chapter flow (`chapters/ch1[0-6].json`), the set-piece encounters' data, the Act II regular and boss encounter tables and sim bands, headless thread tests. Owns the greybox it built (M4-C1x-02) and retires it zone by zone as env-art's dressing lands. | `claude/act2-chapters` | day 1 |
| **story** (new; the narrative seat) | new (Act I's beat sheets were written by m2-slice/act1-chapters with a narrative hat; the Act II sheets are blocked tasks with role narrative) | The seven beat sheets (M4-C10-01 … M4-C16-01), the `.dlg` scripts for Ch10–Ch16, barks, codex text, the heresy NPC lines, loc. ~10–14k words for Act II (SPEC §3.6: 40–60k across the game). | `claude/act2-story` | day 1 (critical path) |
| **env-art** | continues | **Ch10–Ch12** kits and dressing: Ossa Fen and Reedhollow (`ossa_fen.py`, plus a new mangrove vegetation system), Sunken Vey and Lowlight (`lowlight.py`), Keth Pass, Quellan and Cloudloom (`keth.py`); their arenas, grades, LUTs and water materials. | `claude/env-art` | day 1 |
| **env-art-b** | continues | **Ch13–Ch16** kits and dressing: Ansedra, the Sanctum, the Lamp Archive, the Lacquer Court and the lagoon (`ansedra.py`), the bridal barge (`bridal_barge.py`), Hollowmere's first visit (`hollowmere.py`, shared with Act III), the Pale Rim and the Drowned Choir (`drowned_choir.py`); arenas; plus the rendering zone looks (the still mirror and the ripple propagation, the darkness-lit barge). | `claude/env-art-b` | day 1 |
| **characters** | continues | New people: Tobin, Merel Dask, Liss's father, Malcor Venn (a battle actor too), Sefir in person (the review exists), the Abiding guard (battle actors), the Kirru (base, eldest, child, clutch), the Ullari woman and Quellan townsfolk modules, the Hollowmere and Ansedran costume sets for the crowd generator. Kerrid's rope-burn emission mask and his Ch15 long-speech facial pass. | `claude/characters` | day 1 |
| **creatures** | continues | Act II **regular** foes: `tannin_archer`, `root_crab`, `fen_leech`, `gallery_ray`, `rime_urchin`, `conduit_crawler`, `ridge_lynx`, `cord_moth`, `scree_crawler`, `glass_skate`, `rim_crawler` (models, rigs, clips, review shots); the wildlife for the new zones (fen birds and fireflies, highland goats, white-shallows rays). | `claude/creatures` | after the bosses' sheets (week 1) |
| **creatures-b** | continues | Act II **bosses and Vowbound**: Mangrove Drowner, Lamp Engine, Avalanche Ram, Wakefin, the flat-engine part; Nhoa, Hesk, Ethren, **Kesh** (the sheet first: `vowbound/kesh.md` is the gap). | `claude/creatures-b` | day 1 (critical path) |
| **battle-presentation** | continues | Act II battle VFX in `effects.json` (each new skill), the four Vowbound summons (full and short) and Swell finishers, the boss intros, the darkness-lit Wakefin fight, Kesh's element telegraphs, the set-piece HUD bits (with ui-menus). | `claude/battle-presentation` | after the first boss model (week 1–2) |
| **combat** (new seat; Act I had it inside act1-chapters and battle-presentation) | new | The engine features in act2_plan §4.6 (drain, rooted, glide, ambush, repair, part-break targeting, element cycling), the Act II loadouts, the boss suites, and the review of every Act II skill and encounter row. **Proposal: fold into chapters** unless the queue grows past ~6 open engine tasks; then split it out. | `claude/act2-chapters` (folded) | day 1 |
| **cinematics** (was slice-polish) | **renamed** | Act II's cutscene staging, framing and timing: the farewell-tide, the Lamp Archive, the wedding trap and escape, Kerrid's reveal, the Choir's memory sequence, the Vowbound bind cinematics, the act break. slice-polish's beat audit with self-rendered stills carries over. | `claude/m2-slice` (keeps its branch) or a new `claude/act2-cinematics` | after the first beat sheet (week 1) |
| **ui-menus** | continues | The document reader (the Archive), codex and bestiary pages, portraits for the new NPCs, the Act II shops and the heresy rules in the menus, the formation menu at seven, the set-piece HUD bits, loading (every Act II scene change ≤ 1 s hidden). | `claude/ui` | week 1 |
| **audio** | continues | The Act II gaps in act2_finals.md (scene cues, stings, the two people-boss stem sets, cloudloom, sanctum), the creature voices for every Act II foe (M4-AUD-1001), ambiences for the new zones, foley for the barge and the bells, and a Hollowmere zone row for its Ch15 visit (re-using act3's `hollowmere` cue). | `claude/audio` | week 1 (sources exist; the gaps wait on beat sheets) |
| **integration-qa** | continues | `placeholder_audit.py --act 2`, the Act II inventory, the trial merges, the Act II playthrough (New Game → Ch16 end), encounter-entry smoke tests, the Act II completion gate's evidence (`act2_complete.md`, the same rule as ADR 0203). | `claude/hero-integration` | day 1 |
| **progression** (new seat) | new | The Act II Lattice section, Act II shop tiers and prices, drops, the Act II tier gear and abilities. **Proposal: a small track or folded into ui-menus** (which held the progression-adjacent UI in Act I). Default: folded into chapters' combat seat for numbers and ui-menus for menus, until the Lattice section is designed. | — | week 2 |

**Not proposed:** a separate rendering track. The PC is offline (TRACK-RULES 2026-10-29), and Act I's rule holds (env-art-b owns the zone and kit looks; battle-presentation owns battle VFX). Real-GPU items queue for the PC.

**Total:** 12 tracks at peak (chapters, story, env-art, env-art-b, characters, creatures, creatures-b, battle-presentation, cinematics, ui-menus, audio, integration-qa), against Act I's 11. Start eight on day 1: chapters, story, env-art, env-art-b, characters, creatures-b, ui-menus and integration-qa. Add creatures, battle-presentation, cinematics and audio as their inputs land.

## 3. Proposed ownership globs (Act II)

Rows to **add** to `docs/kb/ownership.md` at the gate. Since 2026-10-30 (proposed); sessions as the Lead assigns.

| Role (track) | Path glob |
|---|---|
| Cinematics (chapters) | `game/levels/ch1[0-6]/**` (not `*_dressing.json`, `*_collision.json`, `*_environment.tres`, `lut_*.png`, `*_water_material.tres`: those are env-art's and env-art-b's rows below), `game/levels/ch17/hollowmere/**` for its Ch15 visit only (the zone key, flow and triggers; the dressing is env-art-b's), `game/data/flow/chapters/ch1[0-6].json`, `game/data/flow/ch1[0-6]_*.json`, `tools/act1/ch1[0-6]_*.py` greybox and flow generators (rename to `tools/act2/` at the gate: §5), `tests/integration/test_ch1[0-6]_*.gd`, `tests/integration/act2_*.gd`, the Act II rows appended to `game/data/battle/encounters.json`, `enemies.json` and `skills.json` (append-only; combat reviews) and `tools/balance/targets.json`'s Act II suites |
| Narrative (story) | `docs/kb/story/beats/act2_*.md`, `game/data/dialogue/ch1[0-6]/**`, `game/data/loc/ch1[0-6].csv` text rows (chapters appends location and skill names; both append-only) |
| Environment (env-art) | the Ch10–Ch12 kit dressing: `tools/act2/ch1[0-2]_*_dressing.py` (new), `game/levels/ch1[0-2]/**/*_dressing.json`, `*_collision.json`, `*_environment.tres`, `lut_*.png`, `*_water_material.tres`; `assets_src/environments/kits/haluna/{ossa_fen,lowlight,keth}*.py` and their outputs; `assets_src/environments/vegetation/mangrove*/**`, `assets/environments/vegetation/mangrove*/**`; `game/levels/_tests/{ossa_fen,lowlight,keth}_kit/**` |
| Environment (env-art-b) | the Ch13–Ch16 kit dressing: `tools/act2/ch1[3-6]_*_dressing.py`, `game/levels/ch1[3-6]/**/*_dressing.json` etc. (as above), `game/levels/ch17/hollowmere/*_dressing.json` and its grade; `assets_src/environments/kits/haluna/{ansedra,bridal_barge,hollowmere,drowned_choir}*.py` and outputs; `game/levels/_tests/{ansedra,bridal_barge,hollowmere,drowned_choir}_kit/**`; the still-mirror and ripple parts of `game/shaders/water/**` (a sub-row like M3-RND-26's), coordinated with the water stream |
| Character (characters) | `assets_src/characters/{tobin,merel,liss_father,malcor_venn,sefir,abiding_guard,kirru*,ullari*}/**`, `assets/characters/{…same…}/**`, `game/characters/{…same…}/**`, `assets_src/crowd/{ansedra,hollowmere,quellan}*` (append to the crowd generator), `game/data/world/npc/crowd.json`'s Act II rows |
| Character (creatures) | `assets_src/creatures/{tannin_archer,root_crab,fen_leech,gallery_ray,rime_urchin,conduit_crawler,ridge_lynx,cord_moth,scree_crawler,glass_skate,rim_crawler}/**` and the same ids under `assets/creatures/**` and `game/creatures/**`; `assets_src/wildlife/{act2 ids}/**` |
| Character (creatures-b) | `assets_src/creatures/{mangrove_drowner,lamp_engine,avalanche_ram,wakefin,flat_engine,nhoa,hesk,ethren,kesh}/**` and the same ids under `assets/creatures/**` and `game/creatures/**`; `docs/kb/art/creatures/vowbound/kesh.md` |
| Combat (battle-presentation) | the Act II entries of `game/data/vfx/battle/effects.json` (generated by a new `tools/vfx/gen_act2_ability_vfx.py`), `game/vfx/battle/act2/**` |
| Combat (chapters' combat seat) | the Act II engine features: new files under `game/battle/` named for the feature (e.g. `battle_drain.gd`); edits to `battle_engine.gd`, `enemy_ai.gd`, `combatant.gd` by an explicit row per task, as M3-CMB-01 did; `docs/kb/design/battle_ctb.md`'s Act II sections; `game/data/battle/vowbound.json`'s Act II rows |
| UI (ui-menus) | `game/ui/codex/document_reader*`, the Act II rows of `game/data/ui/**`, `assets/ui/portraits/{act2 ids}*` (via `tools/portraits/**`) |
| Audio | unchanged (`assets/audio/**`, `assets_src/music/**`, `assets_src/sfx/**`, `game/data/audio/**`); the Act II music stays in `assets/audio/music/act2/` (ADR 0039; the LFS block in TRACK-RULES 2026-10-30 applies) |
| QA (integration-qa) | `tools/placeholder_audit.py` (its `--act 2` scope), `docs/kb/qa/act2_*.md`, `tests/integration/test_act2_playthrough*.gd` |
| Cinematics (cinematics) | `game/data/cutscene/ch1[0-6]/**` (new), the Act II cutscene `.tscn` files under `game/cutscene/act2/**` (new); field camera rails stay chapters' |

**Rows to narrow** at the gate:
- **act1-chapters' `game/levels/ch1[0-9]/**`** ("every later Act I chapter") → `game/levels/ch0[4-9]/**`. Its Act II half moves to the chapters row above, and its Act III half (ch17+) stays unassigned until Act III's gate.
- **env-art-b's `tools/act1/ch0[5-9]_*.py`** stays as it is (Act I).
- **creatures' broad `assets_src/creatures/**`** row (M2-CRE) and **creatures-b's** per-id row: the per-id rows above make the split explicit, as creatures-b's Act I row did.

## 4. Proposed SESSION-BRIEFS rows (Act II)

The COMMON PREAMBLE changes one rule: "ADR 0041: only Act I…" becomes **"ADR 0203: Act II (Ch10–Ch16) at final quality; Act I regressions are FAST-TRACK first; Act III stays paused."**

| Track | Branch | Live log | Brief (after the preamble) |
|---|---|---|---|
| chapters | `act2-chapters` | `act2-chapters.md` | You own Ch10–Ch16's encounters, flow, triggers, field cameras and set-piece data, plus the Act II engine features and sim bands (the combat seat). Start with Ch10: Pell in the formation (M3-C09-07 if open), the Drowner's encounter, drain and rooted. Retire the greybox zone by zone as the env-art dressing lands; never call a chapter playable on greybox. Work `M4-A2P-*` tasks with role cinematics or combat. |
| story | `act2-story` | `act2-story.md` | You own Act II's beat sheets (M4-C10-01 … M4-C16-01, in that order) and their `.dlg` scripts, barks and codex text. Each sheet lists its requests to other roles; file them as tasks. Keep Kerrid's watch rules (ADR 0020, 0022) and ADR 0015 (nothing frozen). |
| env-art | `env-art` | `env-art.md` | Act I FAST-TRACKs first. Then Ch10–Ch12 at final quality: the Ossa Fen and Reedhollow kit with a new mangrove vegetation system, Lowlight and the Sunken Vey, Keth Pass, Quellan and Cloudloom, their arenas, grades and LUTs. |
| env-art-b | `env-art-b` | `env-art-b.md` | Act I FAST-TRACKs first. Then Ch13–Ch16 at final quality: Ansedra (the hero zone), the Sanctum's still mirror, the Lamp Archive, the Lacquer Court and the lagoon's ripples, the bridal barge at night, Hollowmere (shared with Act III), the Pale Rim and the Drowned Choir. |
| characters | `characters` | `characters.md` | Act I FAST-TRACKs first. Then Act II's people: Tobin, Merel, Liss's father, Malcor Venn (battle actor), Sefir, the Abiding guard, the Kirru, the Ullari and the Act II crowd sets. Kerrid's rope-burn emission mask and his Ch15 facial pass. |
| creatures | `creatures` | `creatures.md` | Act II's eleven regular foes (act2_roster.md), in chapter order, and the new zones' wildlife. |
| creatures-b | `creatures-b` | `creatures-b.md` | Act II's four bosses and the flat-engine part, then the four Vowbound (Kesh's sheet first). Bosses before Vowbound; chapter order inside each. |
| battle-presentation | `battle-presentation` | `battle-presentation.md` | Act II's battle VFX, the four summons and Swells, the boss intros, the darkness fight and Kesh's element telegraphs. |
| cinematics | `m2-slice` | `cinematics.md` | Act II's cutscene staging, framing and timing, from the beat sheets: the farewell-tide, the Archive, the wedding trap and escape, Kerrid's reveal, the Choir's memory, the bind cinematics, the act break. Beat audit with stills. |
| ui-menus | `ui` | `ui-menus.md` | The document reader, codex and bestiary for Act II, the new portraits, the shops and the heresy rules in the menus, the formation at seven, loading under 1 s hidden. |
| audio | `audio` | `audio.md` | act2_finals.md's gaps as the beat sheets land, the Act II creature voices, ambiences and foley. |
| integration-qa | `hero-integration` | `hero-integration.md` | `placeholder_audit.py --act 2`, the Act II inventory and its rows as tasks, trial merges, the Act II playthrough, and the Act II gate evidence. |

## 5. Small structural proposals for the Lead
1. **Move the Act II generators out of `tools/act1/`:** `ch10_greybox.py` … `ch15_16_greybox.py` live in `tools/act1/` today. Proposal: `git mv` them to `tools/act2/` on day 1 (chapters, one commit), so Act I's tools stay Act I's.
2. **`ch17/hollowmere`** is built in Act II (Ch15's first visit) but its zone key is Act III's. Proposal: env-art-b owns the dressing from the start; chapters owns the Ch15 flow block; Act III's flow joins later (M4-C14-02's note).
3. **An Act II gate file** `docs/kb/qa/act2_complete.md`, the same five conditions as ADR 0203's, so Act III starts the same way.
