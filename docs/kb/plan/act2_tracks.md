# Act II track split and ownership globs (PROPOSED)

- **Status: approved by the Lead (2026-10-30); paste-ready.** §3 and §4 are written to be applied to `docs/kb/ownership.md` and `docs/kb/handoffs/live/SESSION-BRIEFS.md` in one commit at the gate (ADR 0203). This file changes neither of them.
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
| **combat** (new seat; Act I had it inside act1-chapters and battle-presentation) | new | The engine features in act2_plan §4.6 (drain, rooted, glide, ambush, repair, part-break targeting, element cycling), the Act II loadouts, the boss suites, and the review of every Act II skill and encounter row. **Folded into chapters (Lead, 2026-10-30)**; split it out only if the queue grows past ~6 open engine tasks. | `claude/act2-chapters` (folded) | day 1 |
| **cinematics** (was slice-polish) | **renamed** | Act II's cutscene staging, framing and timing: the farewell-tide, the Lamp Archive, the wedding trap and escape, Kerrid's reveal, the Choir's memory sequence, the Vowbound bind cinematics, the act break. slice-polish's beat audit with self-rendered stills carries over. | `claude/m2-slice` (keeps its branch) or a new `claude/act2-cinematics` | after the first beat sheet (week 1) |
| **ui-menus** | continues | The document reader (the Archive), codex and bestiary pages, portraits for the new NPCs, the Act II shops and the heresy rules in the menus, the formation menu at seven, the set-piece HUD bits, loading (every Act II scene change ≤ 1 s hidden). | `claude/ui` | week 1 |
| **audio** | continues | The Act II gaps in act2_finals.md (scene cues, stings, the two people-boss stem sets, cloudloom, sanctum), the creature voices for every Act II foe (M4-AUD-1001), ambiences for the new zones, foley for the barge and the bells, and a Hollowmere zone row for its Ch15 visit (re-using act3's `hollowmere` cue). | `claude/audio` | week 1 (sources exist; the gaps wait on beat sheets) |
| **integration-qa** | continues | `placeholder_audit.py --act 2`, the Act II inventory, the trial merges, the Act II playthrough (New Game → Ch16 end), encounter-entry smoke tests, the Act II completion gate's evidence (`act2_complete.md`, the same rule as ADR 0203). | `claude/hero-integration` | day 1 |
| **progression** (new seat) | new | The Act II Lattice section, Act II shop tiers and prices, drops, the Act II tier gear and abilities. **Folded (Lead, 2026-10-30):** chapters for the numbers, ui-menus for the menus. | — | week 2 |

**Not proposed:** a separate rendering track. The PC is offline (TRACK-RULES 2026-10-29), and Act I's rule holds (env-art-b owns the zone and kit looks; battle-presentation owns battle VFX). Real-GPU items queue for the PC.

**Total:** 12 tracks at peak (chapters, story, env-art, env-art-b, characters, creatures, creatures-b, battle-presentation, cinematics, ui-menus, audio, integration-qa), against Act I's 11. Start eight on day 1: chapters, story, env-art, env-art-b, characters, creatures-b, ui-menus and integration-qa. Add creatures, battle-presentation, cinematics and audio as their inputs land.

## 3. Ownership rows, paste-ready (the gate commit)

**Lead decisions applied** (2026-10-30, answers to this file's asks):
- a new **story** track;
- slice-polish becomes **cinematics** and keeps its branch;
- combat is folded into **chapters**;
- progression is split between chapters (numbers) and ui-menus (menus);
- eight tracks start on day 1;
- these rows land **at the gate**, not before.

`<GATE>` is the date the Lead tags `act1-complete`. Sessions name the track and its branch, as in the existing rows.

### 3a. Rows to append to `docs/kb/ownership.md` (in this order, at the end of the table)

```markdown
| Act II chapters (chapters; continues act1-chapters, ADR 0203; combat seat folded in, Lead 2026-10-30) | `game/levels/ch1[0-6]/**` except each zone's `*_dressing.json`, `*_collision.json`, `*_environment.tres`, `lut_*.png` and `*_water_material.tres` (env-art's and env-art-b's rows below); `game/levels/ch17/hollowmere/**` for its Ch15 flow block only (zone key, triggers, cast; the dressing is env-art-b's); `game/data/flow/chapters/ch1[0-6].json`, `game/data/flow/ch1[0-6]_*.json`; `tools/act2/**` (the Act II greybox and flow generators, moved from `tools/act1/` on day 1: M4-A2P-018) except `tools/act2/ch1[0-6]_*_dressing.py`; `tests/integration/test_ch1[0-6]_*.gd`, `tests/integration/act2_*.gd`; the Act II rows of `game/data/battle/encounters.json`, `enemies.json`, `skills.json` and `vowbound.json` (append-only), `tools/balance/targets.json`'s Act II suites and loadouts; the Act II engine features as new files under `game/battle/` named for the feature (edits to `battle_engine.gd`, `enemy_ai.gd`, `combatant.gd` by a per-task row, as M3-CMB-01 did); `docs/kb/design/battle_ctb.md`'s Act II sections; the Act II rows of `game/data/items/shops.json`, item and drop tables and `game/data/progression/**`'s Act II Lattice section (numbers; menus are ui-menus') | <GATE> | chapters (claude/act1-chapters) |
| Act II story (story; new track, Lead 2026-10-30) | `docs/kb/story/beats/act2_*.md`, `game/data/dialogue/ch1[0-6]/**`, the text rows of `game/data/loc/ch1[0-6].csv` (append-only; chapters appends location and skill names), the Act II rows of `game/data/lore/codex.json` and `game/data/loc/codex.csv` (text; ui-menus owns the screens) | <GATE> | story (claude/act2-story) |
| Act II zones, Ch10–Ch12 (env-art) | `tools/act2/ch1[0-2]_*_dressing.py`; `game/levels/ch1[0-2]/**/*_dressing.json`, `*_collision.json`, `*_environment.tres`, `lut_*.png`, `*_water_material.tres`; `assets_src/environments/kits/haluna/{ossa_fen,reedhollow,fen_zone_lut,lowlight,lowlight_zone_lut,keth,keth_zone_lut}.py` and their outputs under `assets/environments/kits/haluna/`; `assets_src/environments/vegetation/mangrove*/**`, `assets/environments/vegetation/mangrove*/**`; `game/levels/_tests/{ossa_fen,lowlight,keth}_kit/**` | <GATE> | env-art (claude/env-art) |
| Act II zones, Ch13–Ch16 and Hollowmere (env-art-b; also rendering's zone looks, TRACK-RULES) | `tools/act2/ch1[3-6]_*_dressing.py`; `game/levels/ch1[3-6]/**/*_dressing.json`, `*_collision.json`, `*_environment.tres`, `lut_*.png`, `*_water_material.tres`; `game/levels/ch17/hollowmere/*_dressing.json` and its grade; `assets_src/environments/kits/haluna/{ansedra,bridal_barge,hollowmere,hollowmere_grades,hollowmere_preview,drowned_choir}.py` and their outputs; `game/levels/_tests/{ansedra,bridal_barge,hollowmere,drowned_choir}_kit/**`; the still-mirror and ripple parts of `game/shaders/water/**` (a sub-row, as M3-RND-26's; coordinate with the water stream); `game/vfx/act2/**` (the zone VFX: the farewell-tide lift, the shoal, breath fog, the storm at the Choir) | <GATE> | env-art-b (claude/env-art-b) |
| Act II people (characters) | `assets_src/characters/{tobin,merel,aldous_varrow,malcor_venn,abiding_guard,kirru,owa,ullari}*/**`, the same names under `assets/characters/**` and `game/characters/**`; the Act II sets of the crowd generator (`assets_src/crowd/{ansedra,hollowmere,quellan}*`, the Act II rows of `game/data/world/npc/crowd.json`); Kerrid's rope-burn emission mask and his Ch15 face rows (inside the existing Kerrid paths, by this row) | <GATE> | characters (claude/characters) |
| Act II regular foes and wildlife (creatures) | `assets_src/creatures/{tannin_archer,root_crab,fen_leech,gallery_ray,rime_urchin,conduit_crawler,ridge_lynx,cord_moth,scree_crawler,glass_skate,rim_crawler}/**` and the same ids under `assets/creatures/**` and `game/creatures/**`; `assets_src/wildlife/{fen_firefly,fen_kingfisher,woolback,rim_ray}/**` and the same under `assets/wildlife/**`; `docs/kb/plan/act2/creatures/**` | <GATE> | creatures (claude/creatures) |
| Act II bosses and Vowbound (creatures-b) | `assets_src/creatures/{mangrove_drowner,lamp_engine,avalanche_ram,wakefin,flat_engine,nhoa,hesk,ethren,kesh}/**` and the same ids under `assets/creatures/**` and `game/creatures/**`; `docs/kb/art/creatures/vowbound/kesh.md`; `docs/kb/plan/act2/bosses/**`; the battle_sandbox stand-in scenes for Malcor Venn and the Abiding guard (ADR 0204 §5) | <GATE> | creatures-b (claude/creatures-b) |
| Act II battle VFX (battle-presentation) | the Act II entries of `game/data/vfx/battle/effects.json` (generated by `tools/vfx/gen_act2_ability_vfx.py`, new), `game/vfx/battle/act2/**`, the Act II rows of `game/data/battle/choreo.json` | <GATE> | battle-presentation (claude/battle-presentation) |
| Act II cutscenes (cinematics; was slice-polish, renamed by the Lead 2026-10-30) | `game/data/cutscene/ch1[0-6]/**` (new), `game/cutscene/act2/**` (new), the Act II cutscene camera data; field camera rails stay chapters' | <GATE> | cinematics (claude/m2-slice) |
| Act II menus (ui-menus; progression menus folded in) | `game/ui/codex/document_reader*` (new), the Act II rows of `game/data/ui/**`, `assets/ui/portraits/{tobin,merel,aldous_varrow,malcor_venn,owa,kirru_child,ullari_woman,abiding_guard,kesh}*` (via `tools/portraits/**`), the heresy rules in the menus, `docs/kb/plan/act2/ui/**` | <GATE> | ui-menus (claude/ui) |
| Act II audit and gate (integration-qa) | `tools/placeholder_audit.py`'s `--act 2` scope, `docs/kb/qa/act2_*.md`, `tests/integration/test_act2_playthrough*.gd` | <GATE> | integration-qa (claude/hero-integration) |
```

**Audio needs no new row.** Its existing rows (`assets/audio/**`, `assets_src/music/**`, `assets_src/sfx/**`, `game/data/audio/**`, `docs/kb/audio/**`) cover Act II, and the music stays in `assets/audio/music/act2/` (ADR 0039; TRACK-RULES' LFS note while uploads are blocked). Add `docs/kb/plan/act2/audio/**` to its row if the Lead wants the lane doc claimed.

### 3b. Rows to narrow (edit in place, same commit)

1. **act1-chapters' row** (it appears **twice** in ownership.md today, at about lines 58 and 67, with slightly different test lists; keep one, the one with `test_zone_cast.gd`). Replace its first glob clause:
   - **from:** `` `game/levels/ch04/**` through `game/levels/ch09/**` and every later Act I chapter (`game/levels/ch1[0-9]/**`; Ch7's story scenes only, Reefball gameplay stays Combat's) ``
   - **to:** `` `game/levels/ch04/**` through `game/levels/ch09/**` (Ch7's story scenes only, Reefball gameplay stays Combat's; Ch10–Ch16 moved to the Act II chapters row, <GATE>) ``
   - and **from:** `` `docs/kb/story/beats/act1_ch04.md` onward `` **to:** `` `docs/kb/story/beats/act1_ch0[4-9].md` ``;
   - and **from:** `` `game/data/dialogue/ch04/**` onward `` **to:** `` `game/data/dialogue/ch0[4-9]/**` ``;
   - and **from:** `` `game/data/flow/chapters/ch04.json` onward `` **to:** `` `game/data/flow/chapters/ch0[4-9].json` ``;
   - and **from:** `` `game/data/loc/ch04.csv` onward `` **to:** `` `game/data/loc/ch0[4-9].csv` ``.
2. **m2-slice / slice-polish rows:** rename the session cell to `cinematics (claude/m2-slice)`; the paths stay.
3. **Narrative's row** (`docs/kb/story/**`, `game/data/dialogue/**`, narrative-stream-1): leave it. The story row above is more specific, and the narrative-stream sessions are long gone.
4. **Act III stays unassigned** (`game/levels/ch1[7-9]/**`, `ch2[01]/**`): paused until Act II's gate (ADR 0203).

## 4. SESSION-BRIEFS rows, paste-ready (the gate commit)

### 4a. The COMMON PREAMBLE's first rule, replaced

Replace the bullet `- ADR 0041: only Act I (the title through Ch9) as played, at final quality. Act II and later are PAUSED.` with:

```
- ADR 0203: Act II (Ch10–Ch16) is live at final quality (ADR 0041 §3's bar: no greybox, no stand-ins, no placeholder art or sound). Act III stays PAUSED. Act I regressions and the human's playtest notes are FAST-TRACK, ahead of Act II work. ADR 0204 holds the Act II design answers; read it first.
- Your Act II reading: docs/kb/plan/act2_plan.md (the index), the beat-sheet drafts docs/kb/story/beats/act2_ch1[0-6].md, your lane doc under docs/kb/plan/act2/<lane>/, and your rows in docs/kb/plan/act2_consistency.md (fix them first).
```

### 4b. The track table: replace the "Track briefs (Act I focus, ADR 0041)" table with this one

```markdown
## Track briefs (Act II, ADR 0203)

| Track | Branch | Live log | Brief (after the preamble) |
|---|---|---|---|
| chapters | `act1-chapters` | `act1-chapters.md` | You own Ch10–Ch16's encounters, flow, triggers, field cameras, set-piece data, the Act II engine features and sim bands (the combat seat), and the Act II numbers (Lattice section, shop stock, drops; the progression seat). Day 1: move the generators to `tools/act2/` (M4-A2P-018), put `model` keys on the ten regular enemy rows, add the four creature bosses' enemy rows and encounters with M3-BPR-419's staged ids, and fix your rows in act2_consistency.md (the flag names follow the beat sheets' §3). Then the chapters in order (M4-A2P-010…016), each on its zone's final dressing, never on greybox. Engine features M4-A2P-020…025 and M4-CMB-1001 go before their chapter's boss suite. |
| story | `act2-story` | `act2-story.md` | You own Act II's words: take the seven beat-sheet drafts (docs/kb/story/beats/act2_ch1[0-6].md, `draft: pre-gate`) through review (cinematics reviews; the Lead also reviews Ch14–Ch16), then write the `.dlg` scripts (M4-A2P-001…008), barks, the Archive's record texts and codex text. Order: Ch10, Ch14, Ch15, then Ch11–13, Ch16. Keep ADR 0016/0020/0022/0204's watches. Every coined name goes through tools/banned_terms.txt. |
| env-art | `env-art` | `env-art.md` | Act I FAST-TRACKs and your GPU QA rows first. Then Ch10–Ch12 at final quality from the built kits (M4-A2P-040…042; M3-ENV-716…718, 733…736): Ossa Fen and Reedhollow with a new mangrove vegetation system, the Sunken Vey and Lowlight, Keth Pass, Quellan and Cloudloom; ten composed shots per zone; footstep surfaces `root`, `snow`, `slate` (ADR 0204 §11). |
| env-art-b | `env-art-b` | `env-art-b.md` | Act I FAST-TRACKs first. Then Ch13–Ch16 and Hollowmere at final quality (M4-A2P-043…048, M4-A2P-017's swap maps): Ansedra (the hero zone) and its still mirror and ripples, the Sanctum, the Archive, the Lacquer Court and the lagoon, the bridal barge at night, Hollowmere (shared with Act III), the Pale Rim and the Drowned Choir (a hero zone), the storm at the Choir, and the Act II glimmer events (M4-A2P-049). Your lane doc is docs/kb/plan/act2/zones/. |
| characters | `characters` | `characters.md` | Act I FAST-TRACKs first. Then Act II's people (M4-A2P-050…055): Tobin and Merel, Aldous Varrow, Malcor Venn (battle actor), the Abiding guard (living; battle actors), Owa and the Kirru, the Ullari, the Ansedran, Hollowmere and Quellan crowd sets; Kerrid's rope-burn mask and Ch15 facial pass (M3-CHR-505 first); Sefir and young Sefir for close framing. |
| creatures | `creatures` | `creatures.md` | Your rows in act2_consistency.md first (no frost on the lynx, scree crawler or rime urchin: ADR 0204 §2). Then the Act II regulars to the final bar (models exist: M3-CRE-627/628/645; their VFX with M4-A2P-058) and the Act II wildlife (M4-A2P-056; none in Ansedra). Lane doc: docs/kb/plan/act2/creatures/. |
| creatures-b | `creatures-b` | `creatures-b.md` | Your rows in act2_consistency.md first (the Abiding guard are living; the Wakefin's dive is evasion up, not untargetable; the phase maps). Then the Ram's wet wool (M4-A2P-059), the bosses' VFX (M4-A2P-058), Kesh's sheet and model (M4-A2P-057), and the people bosses' stand-in scenes (ADR 0204 §5). Lane doc: docs/kb/plan/act2/bosses/. |
| battle-presentation | `battle-presentation` | `battle-presentation.md` | Act II battle VFX and intros (M4-A2P-060), the four Vowbound summons and Swells (M4-A2P-061), the Wakefin in the dark (M4-A2P-062), Kesh's element telegraphs; your M3-BPR-408/418/419 go live as chapters adds the boss rows. |
| cinematics | `m2-slice` | `slice-polish.md` (renamed cinematics in its header) | Act II's cutscene staging, framing and timing from the beat sheets (M4-A2P-070…075): the farewell-tide, the four bindings (Kesh's as a memory sequence), the wedding trap and the escape across the water, Kerrid's reveal, the Choir and the act break. Beat audit with self-rendered stills. You review the story track's sheets (SPEC §12.3). |
| ui-menus | `ui` | `ui-menus.md` | Your rows in act2_consistency.md first ("Outside the Level"; codex flags that actually fire; `ch15_kerrid_told`). Then the document reader (M4-A2P-080), portraits (081), the heresy and the seven-hero menus (082), the bestiary and set-piece HUD (083), Act II loading under 1 s hidden (084), and the progression menus for the Act II Lattice and shops. Lane doc: docs/kb/plan/act2/ui/. |
| audio | `audio` | `audio.md` | Your rows in act2_consistency.md first (no `ysolde_confession`: ADR 0204 §12 reprises `ysolde_theme`; `kesh_bound`'s order; `kerrid_at_sea` covers ~7–8 min). Then act2_finals.md's gaps as the sheets land (M4-A2P-090…093), `battle_heretic` from Ch14, the zone rows in music.json for the twelve existing finals first (M4-A2P-091). LFS: TRACK-RULES' note while uploads are blocked. Lane doc: docs/kb/plan/act2/audio/. |
| integration-qa | `hero-integration` | `hero-integration.md` | `placeholder_audit.py --act 2` (M4-A2P-100) and `docs/kb/qa/act2_final_inventory.md` from it, trial merges, the Act II playthrough (M4-A2P-101) and the Act II gate file (M4-A2P-102); keep the Act I protection (no Act II change breaks an Act I test or shot). |

**To save usage, start small** (Lead 2026-10-30: eight on day 1): chapters, story, env-art, env-art-b, characters, creatures-b, ui-menus, integration-qa. Start creatures, battle-presentation, cinematics and audio when their inputs land (the boss rows, the first reviewed sheet).
```

## 5. Small structural proposals for the Lead
1. **Move the Act II generators out of `tools/act1/`:** `ch10_greybox.py` … `ch15_16_greybox.py` live in `tools/act1/` today. Proposal: `git mv` them to `tools/act2/` on day 1 (chapters, one commit), so Act I's tools stay Act I's.
2. **`ch17/hollowmere`** is built in Act II (Ch15's first visit) but its zone key is Act III's. Proposal: env-art-b owns the dressing from the start; chapters owns the Ch15 flow block; Act III's flow joins later (M4-C14-02's note).
3. **An Act II gate file** `docs/kb/qa/act2_complete.md`, the same five conditions as ADR 0203's, so Act III starts the same way.
