---
id: M3-C01-02
title: Ch1 "Lamp-Diver" playable (dialogue, flow, greybox levels, encounters, cutscenes)
role: cinematics
status: review
owner_session: "m2-slice subagent D (Ch1 build)"
depends_on: [M3-C01-01, M3-ARC-01]
reviewer: narrative
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). Build Ch1 from its beat sheet (`docs/kb/story/beats/act1_ch01.md`):
- the `.dlg` scripts under `game/data/dialogue/ch01/`;
- the chapter's flow in the M3-ARC-01 chapter data;
- greybox levels under `game/levels/ch01/` (or the night variant named in the sheet), built for env-art's kit to swap in later;
- the encounters, with combat data and `sim.py` bands;
- the cutscenes.

Use env-art, audio and creature swap-in notes as they land.

## Acceptance criteria
- [x] The chapter plays headless from its entry to its exit in an integration test, like `test_fp_thread`.
- [x] Every line goes through a loc key or a `#line:` tag; flags are declared in `flags.tres`; `validate_data` and `dlgc --check` are clean.
- [ ] Each boss and encounter has a `sim.py --check` band, and the combat reviewer has seen it. (Bands in and passing; the combat review is pending.)
- [x] Each greybox level has a `place_at` root and its spawns, and an entry in `locations.json`.
- [x] PLAYTEST notes for the chapter.

## Notes
2026-10-24, m2-slice subagent D. **Review:** narrative (the staging and the lines), and combat for the bands and ADR 0034.

**Done:**
- **Dialogue.** 24 scripts in `game/data/dialogue/ch01/`: C1-01 to C1-15, the six town barks (169 words, within the sheet's 170 rule), Kell's stall with its side scene, the run's branches, and three tutorial prompts. They come to about 783 words, against the sheet's estimate of about 780.
  - New speakers: kell, scaleman, cook, sabe and skipper_sadi; netmender and child are reused.
  - The speaker and UI strings are in a new per-domain loc table, `game/data/loc/ch01.csv`, added to project.godot's translations.
  - `ch01_haggled` and `ch01_kell_first` are appended to events.json.
- **Zones.** `ch01/oruvel_underway` and `ch01/oruvel` are GreyboxZone subclasses under `game/levels/ch01/` (`Ch01Zone`, `Ch01UnderwayZone`, `Ch01OruvelZone`), with layouts, shots, marks, actors and triggers, and rows in locations.json.
  - Bell-rooms are rest points: a full heal, no save.
  - The lantern shutter is a held F or left face button. Its data is `game/data/flow/ch01_field.json`. Opening it widens the light, reveals the old tin behind the coral curtain, and has an encounter-rate multiplier.
  - The storm variant comes up from `ch01_gulls_cried`.
  - The generic GreyboxZone is unchanged.
- **Story.** `game/data/flow/chapters/ch01.json` is listed in chapters.json. The prologue now hands off to `ch01/oruvel_underway` `Drop`. C1-15 empties the party and goes to `ch02/haluna` `Beach`, so Cutscene A and the party join play exactly as before. Nothing in Ch2 changed.
- **Flags.** The ten from the sheet's §3, plus implementation and tutorial seen-flags.
- **Battles.**
  - Enemies: wickfry (displayed as "Glassfry Shoal", per the sheet's wick note), tower_limpet, oil_slug, scuttler, and hullgnaw in two phases (the Ribs: a Coil charge telegraphs the Gnaw; the Breaking Raft at 50%: softer and faster).
  - Seven encounters, all solo Rhen.
  - Hullgnaw lends Kick Off through a new encounter field `party_skills` (ADR 0034, `BossMechanics.lend_skills`, checked by the validator).
  - The battle prompts use the existing encounter and phase `prompt_key`s.
  - Sim bands are in targets.json and all in band at 1000 seeds. Hullgnaw: naive 0.6, smart 86.4, role_answer report only. Scuttlers: naive 75.4. The tutorial fights' naive is 100. Every existing suite is unchanged.
- **Tests.** `tests/integration/test_ch01_thread.gd` drives the prologue to Haluna, with every fight played in the real field battle, plus the Kell-first branch. `tests/unit/test_ch01_zones.gd` and `tests/unit/test_ch01_battles.gd` cover the zone roots and the battles; `tools/tests/test_ch01_validate.py` covers the validator.
- **Shared code touched (small):**
  - ZoneStory doesn't fade back in after a scene that the run hands off from (tested in test_zone_story).
  - chapter_flow_check and validate_data follow a subclassed zone root to GreyboxZone, and accept a battle step's own `party`.
  - test_fp_prologue and test_fp_thread now assert the new prologue target.

**Gaps (placeholders):**
- **`Game.set_chapter(1)` at C1-01** waits for the shared `{"chapter": 1}` step (M2-FP-25), which the local checker rejects today. Until it lands Ch1 writes no chapter autosave.
- **Random encounters:** the Underway layout's `encounters` table (`ch01_underway_shoals`, `ch01_underway_limpet`) is for the shared field encounters (M2-FP-25). Until then only the scripted fights play. The optional shaft limpet stands in for the shaft's roll and carries the escape prompt.
- **Battle prompts show on every attempt,** not by seen-flag. They are encounter and phase prompt_keys.
- **"The ribs blunt heavy strikes"** has no engine expression: phase 1 is high defense across the board.
- **The underwater look** in the field is a stand-in (dark light and fog), with no UnderwaterRig (M3-C01-04).
- **CH01_TITLE_CARD** is a dlg caption line, since there is no title-card UI.
- **The old tin's accessory** has no slot (M3-C01-03).
- **Live battles don't apply equipment yet,** so Rhen has 20 HP less than the sim's loadout gives him.
- **No music or SFX exist** for Ch1's cues (Audio).

**Requests filed:** M3-C01-03 (combat: Kick Off persistence, the bands, the shutter numbers, the economy, the tin, the pre-boss rest, no save) and M3-C01-04 (environment: kits and the UnderwaterRig).

## Review log
