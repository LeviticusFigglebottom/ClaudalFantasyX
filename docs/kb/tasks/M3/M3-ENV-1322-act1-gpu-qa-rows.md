---
id: M3-ENV-1322
title: The PC's Act I GPU QA rows for env-art-b (docs/kb/qa/act1_gpu_qa.md on gpu/act1-qa-2)
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: []
milestone: M3
reviewer: pc-gpu
---
## Notes (2026-10-28, env-art-b)
Pass A ran on integration 048b0a7f, before this branch's Ch5–Ch9 work merged. Each row was re-rendered on this
branch's head; the per-row status is in `docs/kb/handoffs/live/env-art-b.md`. New fixes in this task:
- **Coilspire interior (rows 6, 27):** the zone's own `coilspire_inner_material.tres` keeps the kit's verdigris off the
  mortar joints (that was the green grid), applied by slot through ZoneKitDressing's new `material_paths`, plus a ring
  of low wall-wash lamps on each tier.
- **Ch9 rocks (row 28):** `strand_rocks` boulders are mostly laterite, more angular and less wet (`b_strand.py`).
- **Lanternfall (row 16):** a warm key over the party's slots (`b_lanternfall.py`).
Tests: `--filter=` ch08 23/0, ch09 12/0, zone_kit 12/0, battle_arena 18/0; tools test_corrow_kit, test_arenas,
test_b_arenas OK. The PC re-checks these on the GPU.

## Review log
