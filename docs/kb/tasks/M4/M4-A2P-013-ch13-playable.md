---
id: M4-A2P-013
title: "Ch13 playable at final quality: Ansedra, the Sanctum, Ethren, the Lamp Archive"
role: cinematics
status: doing
owner_session: act1-chapters
depends_on: [M4-C13-01, M4-C13-02, M4-A2P-004, M4-A2P-024, M4-A2P-043, M4-A2P-080]
reviewer: ui
milestone: M4
request-from: lead
---
## Goal
Wire Ch13 on env-art-b's dressing: the scripts; Kerrid out of the Sanctum; Ethren bound; the Archive's three days with the document reader (M4-A2P-080); Ansedra's shops, inn and shrine (M3-UI-209), marked as Order places for the heresy rules (M4-A2P-031); the town's NPCs; cameras.

## Acceptance criteria
- [ ] Thread test through Ch13; audit zero for Ch13; greybox retired.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch13 (no boss).
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **act1-chapters (ADR 0205), 2026-10-30, cameras landed on the greybox:**
  - Shots A02–A06, S02, R02, R03 (docs/kb/plan/act2/chapters/ch13.md §4); every frame rendered and viewed.
  - Marks `house_sefir`, `pact_sefir`, `basin_ysolde`.
  - Kerrid's stage actor at the moorings, shown on `ch13_guest_of_sefir` (ADR 0022 (c)).
  - Pan-follow volumes on the moorings, the centre, each causeway, the Archive isle, the Sanctum's gate and basin, and
    the Archive's two bays. `test_qa_field_camera` is green.
  - A02 and A05 wait on the mirror's reflection (rendering) before a final look.
  - Still to come: the triggers and beats, which wait on story's scenes (M4-C13-01).

## Review log
