---
id: M3-NAR-01
title: Review and extend the lore codex entries, and place the two field records
role: narrative
status: todo
owner_session: ""
depends_on: [M3-UI-03]
milestone: M3
request-from: ui
---
## Goal
M3-UI-03 built the lore codex (SPEC §6.11) with a small starter set written by UI: ten entries in `game/data/lore/codex.json`, text in `game/data/loc/codex.csv`. Narrative owns the voice and the canon. Please review them, fix anything that is off, and extend the set as the chapters land.

## The starter set (titles; unlock in brackets)
- **World:** Glimmer (always), The Undertow (`ch02_met_asha`), The Vowbound (`ch03_ilun_bound`).
- **Places:** Haluna (`ch02_met_asha`), The Saltgrass Causeway (`ch03_causeway_arrived`), The Shell Shrine (`ch03_shrine_door_open`).
- **People:** Asha Velamir (`ch02_met_asha`), Toma Okeru (`ch02_met_asha`).
- **Records** (found in the field): The Tide-Readers' Notice (`causeway_notice`), Words at the Basin Steps (`basin_steps`).

## Acceptance criteria
- [ ] Every entry reads as sincere and in-world (pillar 1), 2 to 4 sentences, with nothing from Acts II and III (no hearts, no Abiding, no Cage, no displaced hearts; the Vowbound entry keeps to what the Order teaches: "the Saints who stayed").
- [ ] Watch: the Asha entry hints that she is a hearer without naming it, and the People entries say nothing Rhen does not yet know at their unlock flag. Move an unlock to a later flag where a line gives something away too early.
- [ ] Extend as chapters land (Ch1 Oruvel, the lamp-divers, Saltwrights, the Order, Cantors, Ch4 onward). Each entry needs `codex_<id>_read` declared in `game/data/flags.tres`, and a record also `codex_<id>_found`. `python3 tools/validate_data.py` (check_codex) checks categories, flags, keys and ids.
- [ ] **Place the two records** (environment and m2-slice own the level scenes; this needs a request to them, or their own task). Each is an ordinary `Interactable` (activation INTERACT, a `prompt_key` such as "Examine"; not "Read", which is a battle command), with `payload = {"record": "<id>"}`. `CodexNotice` (attached by FieldHud in every field scene) marks it found and shows "Record added to the Codex: <title>". No `sets_flag` is needed: the hook sets `codex_<id>_found` itself.
  - `causeway_notice`: `game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn`, on the first old timber marker post past the causeway head (the C02 stretch), where the party sets out. It should be readable before the first banter post (C04).
  - `basin_steps`: `game/levels/ch03/shell_shrine/shell_shrine.tscn`, on the first step at the shrine's entrance (S01), before the shell-basins, so it is read on the way in and frames the puzzle ("Turn the shells gently").

## Notes
- The menu, unlock rules and the record hook are in docs/kb/tech/ui.md "Lore codex (M3-UI-03)".
- Records are shown in the italic flavour face; other entries in the body face.

- **2026-10-27, ui-menus (the Lead's queue item 8, Act I UI):** the Act I set landed for your review: 22 entries in Ch1 to Ch9 story order. **World:** Lamp-Divers (`ch01_started`), The Order of the Still Water (`ch02_met_asha`), The Pilgrim's Wake (`ch04_shell_set`), The Saltwrights (`ch06_arrived`). **Places:** The Underway (`ch01_saw_bell_room`), Oruvel (`ch01_underway_done`), The Kind Weather (`ch04_ysolde_joined`), Pemakar (`ch05_arrived`), Ashcrown (`ch05_trial_begun`), The Brine Shoals (`ch06_arrived`), Tamsule (`ch07_arrived`), The Bell Galleries (`ch07_saw_galleries`), Corrow (`ch09_started`). **People:** Mother Kell (`ch01_has_kell_wick`), Neme (`ch04_started`), Ysolde Ysel (`ch04_ysolde_joined`), Old Kerrid (`ch05_met_kerrid`), Garo Tenmak (`ch05_told_the_smith`), Liss Varrow (`ch06_liss_joined`), Sefir Aurane (`ch06_met_sefir`), Tavi Orse (`ch07_met_tavi`), Pell (`ch09_pell_named`). The text is drawn from the bible, the beat sheets and the character files, and keeps to what Rhen knows at each unlock: nothing about Kerrid's death, Sefir's Conclave, Ysolde's husband, Ressa, the Bell's light or Oruvel's fall. Please check the voice, and especially Neme's unlock (her Ch2 meeting has no plain flag, so it waits for `ch04_started`) and Ashcrown's (`ch05_trial_begun` is set at the crown, not at the stair foot).
- **2026-10-27, ui-menus, Ch8 (after M3-C08-02 landed):** Corrow now unlocks on `ch08_arrived_corrow` (it was `ch09_started`), plus Coilspire (`ch08_entered_coilspire`) and Ivo Brannick (`ch08_met_ivo`, written in the past tense so it holds after W27; nothing of the 1003 burning). 24 Act I entries in all.

## Review log
