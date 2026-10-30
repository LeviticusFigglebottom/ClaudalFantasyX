---
id: M4-CRB-001
title: "Avalanche Ram wool swap: no ice on the Ch12 boss (ADR 0015), matted snow-caked wool and stone instead"
role: character
status: done
owner_session: "creatures-b"
depends_on: []
reviewer: rendering
milestone: M4
request-from: ""
---
## Goal
ADR 0015 forbids ice, frost, glacier or frozen water in any temple or set piece from Ch12 to Ch15. The Avalanche Ram
(Ch12 boss, `keth_seep_terrace`) is built with ice: fleece "matted into plates of ice", an ice beard at the jaw and
belly, icicles on the lock chains, and `salt_glass` ice on the locks. Swap all of it for **matted, snow-caked wool and
stone** (snow on the pass is weather, so caked snow is allowed; nothing is frozen). The design is in
[avalanche_ram.md](../../plan/act2/bosses/avalanche_ram.md), "The wool swap" (draft: pre-gate, M3-CRB-015).

## Acceptance criteria
- [ ] No icicle, ice plate, ice beard or translucent ice material is left on the model; the `fleece_ice` slot becomes
      `fleece_snow` (`foam_white` snow cake, opaque, rough 0.95, no clearcoat or transmission) with `cold_blue_stone`
      grit.
- [ ] Felted plates of matted wool with lodged grit and slate chips; felted lock tips weighted with rounded snow
      clumps (never spikes); a snow-caked wool beard.
- [ ] `hit` sheds snow and grit (VFX request), not ice shards; the art sheet's ice text is corrected.
- [ ] The head, neck, herd-cord, seep partings, triangle budget (≤ 16k) and clip names are unchanged; GroundedClipsTest
      passes with no allow-list entry; `creature_avalanche_ram` re-rendered and viewed at battle distance.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by creatures-b (M3-CRB-015, 2026-10-30) with the Act II boss sheets.
- Blocked until the Lead tags `act1-complete` (ADR 0203: it starts at the Act I gate); then `todo`.
- Related: `ridge_lynx` ("ear tufts frosted") and `scree_crawler` ("frost-split scree") are a Lead question in the
  sheets' README, not part of this task.

## Review log
- 2026-10-30, creatures-b: closed as a duplicate of the Lead's M4-A2P-059 (filed the same day by the act2-plan track),
  which carries the work. Its "wet, matted, seep-lit wool" reading replaces this task's "snow-caked" one where they
  differ; the snow-and-grit reading stays for the Ch12 regulars (M4-CRE-701).
