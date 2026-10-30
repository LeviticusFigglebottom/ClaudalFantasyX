---
draft: pre-gate
author: env-art-b (claude/env-art-b), 2026-10-30
adr: 0203 (preparation, docs only; no builds until the Lead tags act1-complete)
---
# Act II zone kit specs (env-art-b's chapters, Ch13–Ch16)

One file per zone, plus the arenas and an inventory of the Ch10–Ch12 kits. They turn the art sheets
(`docs/kb/art/environments/{ansedra,open_sea_ch15,hollowmere,pale_rim}.md`) and the colour script (`ch13`–`ch16`)
into the work list for dressing each greybox zone at ADR 0041's bar. They are drafts: the beat sheets (M4-C13-01 …
M4-C16-01) don't exist yet, so marks, triggers and cutscene staging may still move.

| Zone | Spec | Kit | State today |
|---|---|---|---|
| `ch13/ansedra` (and its Ch14 night lagoon) | [ch13_ansedra.md](ch13_ansedra.md) | `ansedra.py` | kit built (8 pieces), zone greybox |
| `ch13/sanctum` | [ch13_sanctum.md](ch13_sanctum.md) | `ansedra.py`, `lowlight.py` | kit built, zone greybox |
| `ch13/lamp_archive` | [ch13_lamp_archive.md](ch13_lamp_archive.md) | `ansedra.py` | kit built, zone greybox |
| `ch13/ansedra_lacquer_court` (Ch14) | [ch14_lacquer_court.md](ch14_lacquer_court.md) | `ansedra.py`, `bridal_barge.py` | kit built, zone greybox |
| `ch15/open_sea` | [ch15_open_sea.md](ch15_open_sea.md) | `bridal_barge.py` | kit built (1 piece), zone greybox |
| `ch17/hollowmere` (Ch15's first visit) | [ch15_hollowmere.md](ch15_hollowmere.md) | `hollowmere.py` | kit built (6 pieces) and the Ch17 grade, zone greybox |
| `ch16/pale_rim` | [ch16_pale_rim.md](ch16_pale_rim.md) | `drowned_choir.py`, `keth.py` | kit built (3 pieces), zone greybox |
| `ch16/drowned_choir` | [ch16_drowned_choir.md](ch16_drowned_choir.md) | `drowned_choir.py` | kit built, zone greybox |
| The arenas | [arenas_ch13_16.md](arenas_ch13_16.md) | as above | 3 built (`drowned_choir_ring` has no baseline); 1 new |
| Ch10–Ch12 (env-art's) | [inventory_ch10_12.md](inventory_ch10_12.md) | `ossa_fen.py`, `reedhollow.py`, `lowlight.py`, `keth.py` | inventory against the bar |

## How every zone here is built (Act I's method, ADR 0200 and env-art-b's Ch5–Ch9)
1. **The zone moves into its kit's frame** once (`--relayout`), as Ashcrown did, wherever the greybox and the kit
   disagree in size. A one-off relayout moves the story's marks with it. Several greyboxes here are smaller than
   their kit pieces (noted per zone).
2. **A generator writes the dressing.** `tools/act2/ch1x_<zone>_dressing.py` writes `*_dressing.json` (ZoneKitDressing),
   `*_collision.json` (KitCollision) and the zone's grade, LUT copy and water material. Nothing is hand-placed.
3. **No flat colour reaches the screen.** The Haluna kit's StandardMaterial slots this act uses (`kit_gold_leaf`,
   `kit_lacquer_red`, `kit_lacquer_black`, `kit_window_lit`, `kit_bound_core`) take zone looks through
   `kit_material_paths` (`tools/act1/ch05_09_zone_looks.py`: `lacquer()`, `GOLD`, `VERDIGRIS`, …). Arenas take them
   through `KitSlotSwaps`.
4. **Light has a visible source.** Every fire light, wash or window glow sits on a kit piece that explains it
   (Act I's audit: Coilspire's sourceless washes).
5. **Walk it before calling it done.** Eye-height stills from every spawn, trigger and mark, looking in four
   directions, every story variant, and every arena from each camera hint, all viewed (env-art-b's 10-29 audit
   method).

## Act II's palette (SPEC §7.2, the colour script): what the materials answer to
- Overcast, storm, moonlit, cold blue stone. Key light from ~6,200 K (Ch13) to moonlight (Ch15/16 at night).
- Saturation ×0.7–0.9, except Ch14's dusk (contrast 0.70, the game's peak).
- **Gold** may reach 12 % of the frame only in Ansedra (`ch13`), and must read cold and metallic: wealth, not warmth.
- **Glimmer:** `glimmer_bound` (`#4FB3B0`) for anything the Order binds (the Sanctum floor, the flat-engine, the
  Saltwright lamps); `glimmer_held` (`#7FC6D9`) for the dead (the Ch15 shoal, Kerrid's hands, Kesh).
- No warm source on the open sea at night (Ch15).
- **Guardrails** (act2_plan §2a): no ice, frost or frozen basin from Ch12 to Ch15; no underground route at Ansedra;
  no script on the domes; the Order's sign is the Level line.
