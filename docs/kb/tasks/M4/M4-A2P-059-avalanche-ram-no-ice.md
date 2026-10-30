---
id: M4-A2P-059
title: "The Avalanche Ram without ice: swap the ice plates and icicles for wet, matted, seep-lit wool (ADR 0015)"
role: character
status: doing
owner_session: "creatures-b (ADR 0205, the Lead 2026-10-30 02:26)"
depends_on: [M3-CRE-624]
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
The built Avalanche Ram (M3-CRE-624, avalanche_ram.md) has fleece matted into plates of ice, icicles on its locks, and an ice beard. ADR 0015 bans ice, frost and frozen water in any temple **or set piece** from Ch12 to Ch15, and the Lead ruled (2026-10-30) that the Ram's fight counts. creatures-b swaps the ice for **wet, matted, seep-lit wool**. This is a materials and small-geometry change, not a rebuild.

## Acceptance criteria
- [ ] No ice, icicle or frost reads anywhere on the Ram: the `salt_glass` ice slots become wet matted wool (`sand_cloth` darkened wet, clearcoat), and the icicle strands become dripping wool lock tips.
- [ ] The seep's cold light still shows through the partings (`spawn_wound`, `glimmer_held`).
- [ ] The camelid head (M3-CRE-635) and the herd-cord are unchanged. Budget and clips are unchanged.
- [ ] avalanche_ram.md is updated (the palette and "As built"); the `creature_avalanche_ram` shot is self-rendered and viewed; tests are green.
- [ ] ADR 0041 §3's final bar.

## Notes
- Filed by the act2-plan track (2026-10-30) on the Lead's answer to the LEAD-ASK in act2_ch12.md §10.1.
- Owner: creatures-b (act2_tracks.md).
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log
