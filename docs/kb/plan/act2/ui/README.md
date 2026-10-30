---
draft: pre-gate
---
# Act II UI spec (ui-menus, docs only, ADR 0203)

- **Status:** `draft: pre-gate`. Nothing here is built until the Lead tags `act1-complete` (ADR 0203). This is the
  ui-menus track's preparation: no code, scenes, data or loc rows yet.
- **Sources:** [act2_plan.md](../../act2_plan.md) (§2 chapters, §4 systems, §4.5 menus), [act2_inventory.md](../../act2_inventory.md) §1e
  and §2g (what already exists), the story beats, and the Act I UI as it ships.
- **Rule:** Act I's final-quality bar from day one (ADR 0203). Every screen gets its parity test (keyboard, pad, mouse),
  the aspect and pseudo-locale audits, and self-rendered shots, as in Act I.

| File | What it specifies |
|---|---|
| [screens.md](screens.md) | New screens and changes to existing ones: the document reader, seven heroes, the Vowbound list, Pell's Listen, shops |
| [hud.md](hud.md) | Battle and field HUD: rooted, drain, repair, the flat-engine part and tide pulse, darkness telegraphs, element cycling |
| [tutorials.md](tutorials.md) | New first-time tips and battle prompts, with when each appears |
| [codex_bestiary.md](codex_bestiary.md) | Codex entries (world, places, people, records, Vowbound) and bestiary rows, with their unlock beats |
| [portraits.md](portraits.md) | Dialogue and menu portraits for every new speaking person |
| [heresy.md](heresy.md) | The heresy state from Ch14: shrines that go dark and refuse, shops that refuse, the party's title |
| [kerrid.md](kerrid.md) | What Kerrid's reveal (Ch15) changes in the party UI: text and portraits, never his kit |

**What already exists (keep, extend):** Act II area maps for 15 zones (`zone_maps.json`, `maps_act2.csv`, M3-UI-206); the
Kite world map (M3-UI-205); 16 codex entries (the Kirru, the Ullari and 14 places, M3-UI-207); shop and inn rows for
Quellan, Ansedra and Hollowmere (`shops.json`, `towns_act2.csv`); the act card's Act III title (M3-UI-210); bestiary
portraits for every Act II creature; names and lore for the 10 regular foes.

**Loc-key totals (new rows):** about 225, listed per file (screens ~37, HUD ~72 with ~40 objective lines, tutorials 20, codex and bestiary ~70, portraits ~12, heresy 10, Kerrid 2–3), plus Narrative's ~60 record sentences. They go in new per-domain CSVs (`ui_act2.csv`, `codex_act2.csv`,
`tut_act2.csv`) per CLAUDE.md §5, never appended to `strings.csv`.
