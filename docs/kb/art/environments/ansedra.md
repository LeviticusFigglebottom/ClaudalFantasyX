# Ansedra, the Holy City (Ch13–Ch14): Design Notes

Owner: Environment Artist (M3-ENV-721; the sheet first, then the kit). Lighting review: Rendering.
- **Story:** [act_outline Ch13–14](../../story/beats/act_outline.md), bible §5.8, [ADR 0016](../../decisions/0016-act-two-restaging.md).
- **Grade targets:** [color script](../color_script.md) `ch13` (the still city) and `ch14` (the wedding at dusk).
- **Zones:**
  - `ch13/ansedra`, the city and its lagoon;
  - `ch13/sanctum`, the Sanctum of the Level;
  - `ch13/lamp_archive`;
  - `ch13/ansedra_lacquer_court`.
- **Kit:** in the Haluna kit as `ansedra.py`.
- **Arena:** `ansedra_lagoon_escape` (Warden Malcor Venn, Ch14).

**The feeling in one line:** beautiful and airless. Gold bowl-domes doubled in a mirror lagoon under a white-grey sky.
Then, at dusk, the first ripple in four hundred years.

**What the place is** (bible §5.8):
- **The city:** the Order's seat, built on a lagoon kept perfectly flat. No wind ripples it and no wake is permitted;
  barges are poled, never rowed. There are no seabirds, no dogs, and no children's games in the squares.
- **The skyline: bowl-domes.** Each is an inverted gilded bowl on a tiered red-lacquer base, crowned with a thin
  spire. The domes stand on islands of white stone, and each doubles in the mirror below.
- **The Lacquer Court:** the ceremonial heart. Red lacquer halls on a white court, with water-steps down to the
  lagoon and the court's water-gate.
- **The Sanctum of the Level:** a basin held so still it is a perfect mirror, lit from beneath by a steady light
  (`glimmer_bound`: the thing the Order forbids).
- **The Lamp Archive:** the Order's library of Lit Age records, kept in plain sight. Shelves of lamp-ledgers in
  lacquered cases under a white vault, and the Cantor roll on its lectern.

**Influences** (transformed; SPEC §2): Thai and Burmese lacquer and gold leaf and Javanese tiered roofs (bible §5.8),
combined into an original plan: the bowl-dome on a tiered base, and the mirror lagoon as the city's ground. No
religious figures, no script on the domes; the Order's sign is the Level line.

**Gold rule** (colour script `ch13`): gold may break its 5 % frame limit only here (up to 12 %), and it must feel
cold: wealth, not warmth.

## 0. Lighting

- **`ch13`:** 16:30 overcast, sun 25° / 230°, key `#FFF9F2` 1.6, fill `#8A96A4`, exposure 0.75, saturation ×0.8,
  `lut_ch13_still`. The lagoon is a perfect mirror (roughness 0).
- **`ch14`:** dusk 18:30, sun 1° / 270°, key `#FFAA5F` 1.4, rim `#B3261E`, fill `#4A5A78`, exposure 0.90, S-curve
  0.7, `lut_ch14_wedding`: red lacquer pushed toward blood, shadows navy. The escape barge's wake breaks the
  domes' reflections apart.

## 1. Kit pieces (metres; LOD0 / LOD1 triangle budgets)

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `bowl_dome` | A bowl-dome on its island: a white stone plinth at the water, three tiered red-lacquer drums with gilt bands (each drum ringed with black lacquer pilasters, dark windows under gilt heads between them, a black eave on its brackets), the inverted gilded bowl ribbed in gilt, and a thin spire with rings; the plinth steps down into the water; scaled per placement | 14 × 30 | 6k / 400 |
| `ansedra_far_domes` | The skyline ring: low-poly domes and their islands round the lagoon at 300–700 m | r 700 | 4k / 800 |
| `pursuit_barge` | The Conclave's pursuit barge: long, black lacquer with gilt, a raised poop for the Warden, and at its stern the **bound flat-engine** (a bronze disc on a gimbal, its bound core in `glimmer_bound`) that pulls the water level and still | 14 × 5 | 10k / 700 |
| `lacquer_hall` | One hall of the Lacquer Court: a white plinth, red-lacquer columns with gilt capitals, a lacquered back wall, and a three-tier hip roof of red tile with gilt eaves whose tips sweep up; open on +Z | 15 × 10 × 10 | 8k / 500 |
| `lacquer_court_ground` | The court: white slabs with the Level line inlaid in gilt, eight water-steps down into the lagoon on +Z, and the water-gate over them (two red posts, a lintel, the lacquered drop-gate held up) | 40 × 33 | 12k / 800 |
| `sanctum_basin` | The Sanctum's basin: 14 m square, 1 m deep, salt-glass tiles over the bound light, a white rim with a gilt Level line and two kneeling steps outside it; the scene fills it with still water to −0.1 | 19 × 19 | 8k / 500 |
| `archive_stacks` | One bay of the Lamp Archive: two black-lacquer ledger cases across a 2.4 m aisle, red shelves of ledgers (cream and red spines), a rolling ladder, and the lectern with the Cantor roll at the aisle's end | 7 × 4 × 3.3 | 9k / 500 |

**Composition notes** for the zones (act1-chapters places them):
- **The Lacquer Court:** halls on three sides of `lacquer_court_ground`, the open side toward the steps and the gate;
  domes behind. Keep halls' fronts 6 m back from the steps so the gate scene has the court floor.
- **The Sanctum:** the basin centred under a white vault (use `lowlight_nave_bay` scaled, or plain walls); no other
  light source than the floor. The basin's mirror is the scene's water at −0.1, roughness 0.
- **The Archive:** bays in a row along X (7 m pitch), the lectern of the last bay facing the entrance.

## 2. The Warden's arena (`ansedra_lagoon_escape`)

- **The floor:** the party stands on Merel's bridal barge (`bridal_barge`, open_sea_ch15.md), the deck at y 0, out
  on the lagoon (water at −0.6).
- **The pursuit barge** lies alongside on the enemy side, its waterline centre at (−2, −7.6) and its bow toward −X.
  The `BossAnchor` is on its deck at the near rail (−4.5, −0.2, −7.0). In phase 2 the Warden boards.
- **Behind the enemy line:** the bowl-domes on their islands, the city's windows lit (it has come out to watch the
  water move), and the thin red band under the overcast.
- **The water:** still, then rippling round the barges (the escape's wake, `ch14`).
- **Hints:** `the_engine` (the flat-engine at the pursuit barge's stern) and `the_city_watching` (the domes over
  the water).
- **Light:** `ch14` dusk. No lamp on the bridal barge (ch15's rule starts here); the city's windows are the warm
  lights, far off.

## Revisions

- 2026-10-27 (env-art, M3-ENV-721): first issue, with the Ch14 boss arena.
- 2026-10-27 (env-art, M3-ENV-721): the zone pieces (`lacquer_hall`, `lacquer_court_ground`, `sanctum_basin`,
  `archive_stacks`) and composition notes.
