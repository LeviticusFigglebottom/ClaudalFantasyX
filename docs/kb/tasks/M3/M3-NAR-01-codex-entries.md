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

## Review log
