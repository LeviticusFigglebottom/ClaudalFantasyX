---
id: M3-C09-04
title: "Corrow at night, the dawn road and the vigil's plaza: kits for Ch9's greybox"
role: environment
status: review
owner_session: "env-art-b (claude/env-art-b; Ch5–Ch9 dressing is env-art-b's, Lead 2026-10-28)"
depends_on: [M3-C09-02]
milestone: M3
reviewer: art
request-from: cinematics
---
## Goal
Ch9 plays on one greybox zone, `ch09/corrow_night` (M3-C09-02; `game/levels/ch09/corrow_night/`). It stands in for the sheet's `ch08/corrow` night variant, because Ch8 isn't built. Build the real places from act1_ch09.md §9 (Environment Art):
1. **The `ch08/corrow` night variant** (the chapter's zone):
   - the breach in the wall: a black gap, with rubble tipped seaward and two fallen Watchers face-up in the shallows;
   - the low town flooded to the eaves at slack water, with debris;
   - the harbour strand with rows of shrouded dead under sailcloth (shapes only, **faces covered**: a set of shroud props with a variation parameter, and oil lamps at intervals);
   - the Stillguard row, with round shields at the feet;
   - the Ebbing raft (lacquered timber, poled, a low deck with no rail);
   - the cut hoist rope coiled on the wall-head;
   - the landward foot of the Fisher Stair rising out of still water, for N13.
2. **The dawn road:** the coast road out of Corrow's landward gate, a milestone, wet laterite and scrub, with the broken wall behind and the sea to the south.

## Acceptance criteria
- [ ] **Where Ch9 lives.** Decide with Ch8's builder whether Ch9 moves into `ch08/corrow` as its night variant or keeps its own zone dressed with the Corrow kit.
  - Either way, keep the spawns (`Strand`, `RoadGate`), the trigger ids and payloads, the marks the scripts use, and the shots N01–N19, N05A/N05B, D01–D03, D02B and P02–P04.
  - Moving zones means repointing `ch09.json` and `locations.json`. That is Cinematics' change; ask in a task.
- [ ] **The swim.** The harbour is a walkable floor 1.1 m down, and the raft's crossing is a cut (`clip_marks`). The real harbour needs real water and the raft's poled crossing.
- [ ] **B01's systems (sheet B01).** A save shrine on the wall-head and a chandler restocking on the strand: Act I's last shop. Neither is in the greybox. The chapter-start autosave is the only save today, so quitting at dawn replays the night.
- [ ] **The Iskarra vigil (B10).** The greybox stages it on a stand-in plaza far east in the same zone (x 300), so the cut from D03 to P02 is a camera cut in one scene. Either dress that stand-in with the Prologue's plaza pieces or propose another way to keep the cut hard. A scene change fades through the router.

## Notes
- 2026-10-27 (env-art): the kit pieces are M3-ENV-708 (`cw_night.py`): shrouds, strand lamps, round shields, the
  Ebbing raft, flood debris, the milestone. Placement and the zone decision stay with act1-chapters.
- The layout's `doc` describes each block. `tests/integration/test_ch09_thread.gd` names the spawns, marks, shots and triggers it depends on.
- In the greybox, +Z is south, out to sea; the placeholder held motes drift that way. On the real Corrow the sea is south-west (act1_ch09.md §9 Rendering 2).

- **env-art, 2026-10-27 (B01 and B10):**
  - **B01's save shrine:** M3-ENV-101's `save_shrine` / `save_shrine_core` (swap note in env-art's live log).
  - **B10, the Iskarra vigil:** dress the stand-in plaza with `assets/environments/zones/iskarra/iskarra_city.tscn`
    (M3-ENV-710). It instances as one node, so the x 300 stand-in can take it as is.

- **env-art-b, 2026-10-29 (dressed; Ch9 keeps its own zone, dressed from Ch8's Corrow dressing):**
  - The breach and its rubble (dry broken laterite at night, M3-ENV-1322), six fallen Watchers, the low town flooded
    (`LowTownLake` water) with the kit's `flood_debris` adrift among the roofs (12, seeded), the strand's shrouds in
    weathered sailcloth (M3-ENV-1326) with 35 strand lamps, the Stillguard row's round shields, the Ebbing raft, the cut
    hoist rope, the broken Fisher Stair's foot; the dawn road with its milestone; the Iskarra vigil plaza dressed from
    the Iskarra kit; the harbour, Iskarra's sea and the lake as water; the moon over the sea (M3-ENV-1309).
  - The strand's landing, Pell's rocks and the mole gangway (`b_strand.py`), the Ebbing's motes (M3-C09-03).
  - **B01's save shrine:** the Level-stone shrine stands on the wall-head on the `Shrine` block (in Haluna's shrine
    stone, M3-ENV-1326); making it a SaveShrine interactable and the chandler are act1-chapters' (systems, not dressing).

## Review log
