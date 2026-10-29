# Handoff — environment (env-art) — 2026-10-29 #1

Branch `claude/env-art`; integration `claude/new-session-mj8c3c` (merged in at session start, 58011116); Lead
`session_01Bg3iP7cPGyjbX4CyniBahc`. Details and every MERGE-READY line: `docs/kb/handoffs/live/env-art.md` ("Now").

## Done
- **M3-ENV-750 / inventory:** the Haluna trees ship only as `banyan_hero` / `windbreak_tree` (slice-polish's rename carried
  as identical lines); the four tree rows are gone; the three left are re-routed (characters, env-art-b).
- **Walk-through (Prologue–Ch4, all nine walks, every frame viewed):** Oruvel's commons rafts tuck their hulls
  (`raft_deck_tucked`, `raft_deck_small_tucked`); Haluna's inn gets `inn_hearth`.
- **GPU QA rows 4, 19, 23–25:** re-checked on this tree; all fixed since 4c85ffb7b (row 24's shots retired).
- **M3-ENV-104** (Oruvel: ridge gulls, the cabin under the roof child, Kell's beacon, the low hull's load, the storm sky),
  **M3-ENV-103** (`travel_bundle`, Asha's bag), **M3-ENV-1228** (the Ch4 derelict's moon fill), **M3-CRE-663**
  (`kirru_roost` host determinism), all to review.
- To review after checking on this tree: M2-HER-1127, M3-ENV-105, M2-ENV-12, M3-C01-04, M3-C04-03, M3-ENV-746, M3-HER-1140.
- Routed: M3-HER-1156 to slice-polish (its ch03 camera volumes).

## In progress
- Nothing. No background jobs; no un-pushed state.

## Exact next step
1. The Lead's gate re-approves the drifted shots listed in the live log (`ch01_oruvel_dressed`, `oruvel_o17_pen_split`,
   `iskarra_p01_plaza_dusk`, `slice_prologue_vigil_line`, `ch04_ferry_deck`, `ch04_ferry_derelict`, the Haluna inn
   frames) and gives first baselines to the pending ones (`zone_oruvel_*`, `ch01_kell_stall`, `ch01_scale_hull`,
   `ch01_net_pen`, `ch01_bell_room`, `brightwater_landing_f01/f06`).
2. slice-polish swaps `travel_bundle` in at `NPCs/Neme/Bag` (M3-ENV-103's note); act1-chapters re-aims D06 (M3-ENV-1228).
3. When the PC returns: the live log's `### PC-QUEUE`.

## Known issues
- The Ch4 wake's lagoon glows bright turquoise close to the dock at night (the shader's sea-glow, as the approved H10);
  PC-QUEUE.
- 2ff511ab carries M3-ENV-103's bundle under M3-ENV-104's message (not rewritten; noted in the live log).

## Files touched
- `assets_src/environments/kits/haluna/{trees,props,ossa_fen}.py`; `assets_src/environments/kits/oruvel/{ov_hulls,
  ov_zone_dressing,ov_preview_layout}.py`; `tools/act1/ch04_ferry_dressing.py`; `tools/tests/test_haluna_kit.py`.
- Assets: `kits/haluna/{inn_hearth,travel_bundle}.glb` (+import), `kirru_roost.glb`, the trees' glbs removed;
  `kits/oruvel/raft_deck{,_small}_tucked.glb` (+import); both kits' manifests; `zones/ch01/oruvel_dressing.json` and
  the storm environment; `game/levels/_tests/oruvel_kit/{oruvel_layout.json,oruvel_storm_environment.tres}`;
  `game/levels/ch04/brightwater_ferry/brightwater_ferry_dressing.json`; PROVENANCE rows.
- Haluna zone: `haluna_layout.json`, and slice-polish's identical tree lines in `haluna.tscn`, `test_haluna_zone.gd`,
  `test_post_import.gd`, `scene_loads.json`.
- Task files and `docs/kb/handoffs/live/env-art.md`.
