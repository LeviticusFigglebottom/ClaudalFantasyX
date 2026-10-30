---
id: M4-A2P-009
title: "Act II NPC and crowd barks, boss bestiary pages, and world codex entries"
role: narrative
status: review
owner_session: "act2 story track (claude/act2-plan, ADR 0205)"
depends_on: [M4-A2P-001, M4-A2P-008]
reviewer: ui
milestone: M4
request-from: lead
---
## Goal
The Lead's 2026-10-30 request: ambient barks for the named and crowd NPCs of Ch10–Ch16, plus the Act II lore not yet written, which is bestiary blurbs for the bosses and the boss add on Combat's ids, and world codex entries. The places already existed (M3-UI-207), and the people were done in M4-A2P-008.

## Acceptance criteria
- [x] One `.dlg` per NPC under `game/data/dialogue/ch1N/`, with `#line:` ids, each line behind its story flag (heresy-state variants from `ch14_declared_heretics`).
- [x] `ENEMY_<ID>` and `LORE_<ID>` rows in each chapter's loc csv for `mangrove_drowner` (ch10), `conduit_crawler` and `lamp_engine` (ch11), `avalanche_ram` (ch12), `malcor_venn` (ch14), `wakefin` (ch15) and `abiding_guard` (ch16), ready for Combat's `enemies.json` rows (`name_key`/`lore_key`).
- [x] World codex entries `farewell_tide`, `name_shells`, `outside_the_level` and `the_hush`, each behind its flag, with their read flags declared.
- [x] dlgc --check, validate_data (banned terms) and Godot `--filter=dialogue|codex|bestiary` are clean.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- **Barks (28 files):**
  - Ch10: Pell at the fen edge and at the gate (the two the lane doc names), Owa, the shell-carver, the fisher, the child after the tide.
  - Ch11: the Lowlight keeper, Pell at the conduits, Kerrid in the galleries.
  - Ch12: the keth-reader (`npc_reader`), a herder's boy, the well at night (`ch12_hesk_bound`), the Cloudloom keeper, a traveller on the pass.
  - Ch13: the pole-barge man, the archivist, a child at the ledge, the seamstress, the kneeling woman.
  - Ch14: a wedding guest, a Lamplighter, a Stillguard.
  - Ch15: a current-singer, the raft cook, the lookout, a child after the pyre-raft.
  - Ch16: a cairn-wader, a wader turning back.
- Dialogue loc keys are `DLG_*` in `dialogue.csv`, because dlgc writes every compiled line there. The lore rows go in the chapter csv files.
- `test_codex.gd` pinned the World total at 12, and I raised it to 16 (two lines). Raise it again whenever World gains entries.
- Keth got no entry of its own: the Ullari and Keth Pass pages already explain it.
- Location strings follow the existing barks (`ch13/lamp_archive`, `ch16/pale_rim`). The field placement (interactables, NPC actors) belongs to the chapters and towns tracks.

## Review log
