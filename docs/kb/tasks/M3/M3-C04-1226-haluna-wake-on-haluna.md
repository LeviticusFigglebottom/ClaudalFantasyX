---
id: M3-C04-1226
title: "Ch4's wake night on the real Haluna: its dressing at night, its walk collision, env-art's wake sets by flag (ADR 0041)"
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-C04-02, M3-ENV-709]
reviewer: qa
milestone: M3
request-from: lead
---
## Goal
ADR 0041: `ch04/haluna_wake` was a 41-block greybox stand-in for Haluna's night (ADR 0035: HalunaStory is not
data-driven). env-art had already built the wake night into Haluna itself (M3-ENV-709: the lamps to the wall, the
feast, the ink kit, the shells as `StorySet_*`, "Ch4's zone shows it by flag"), so the zone now stands on the real
Haluna.

## Done (act1-chapters, 2026-10-28)
- `tools/act1/ch04_haluna_wake.py` writes the layout: GreyboxZone's `dressing` row instances
  `ch02/haluna/haluna_dressing.tscn` (adopted by `HalunaZoneDresser`), `dressing_mood: night`, no blocks, and every story
  point placed by hand on Haluna's places (Neme's house on the tidewall lane, the lane's child, the shut inn, Reed at the
  chapel court, the dock, the feast and the wake-shell wall at the causeway head, the causeway's first slabs at dawn),
  their heights read from Haluna's collision by `tools/act1/ch04_haluna_wake_floors.tscn` (props ignored under shots).
- `Ch04Zone`: Haluna's runtime walk collision when the dressing is Haluna's (its tuning read from ch02/haluna's own
  Collision node through SceneState, so the two never drift), the dressing's mood, and `show_sets` / `hide_sets` rows
  for the dresser's story sets; `story_set_shown()`.
- States: the lamps, feast and Imra's faded shell from the start; Asha's shell from `ch04_shell_set`; the village home
  and the stranger at the wall from `ch04_dock_comforted`; Imra's shell re-inked from `ch04_saw_ysolde_ink`. The lit
  windows going dark (greybox blocks) are gone: Haluna's night lamps stay lit (a nuance for env-art if wanted).
- The zone map (UI's `zone_maps.json`, as for the earlier relayouts) reads Haluna's layout with Ch2's bounds and the
  new POIs; `test_zone_map` counts eight greybox-layout zones now.
- Tests: `test_ch04_zones` (the wake is Haluna at night, on its collision, no greybox; the sets by flag),
  `test_ch04_thread` (the sets instead of the blocks). `--filter=ch04` 12/0, `zone_map` 20/0.
- Shots `ch04_haluna_wake_feast` and `ch04_haluna_wake_lane` (rig `ch04_haluna_wake_shots.tscn`); every story camera
  (H02-H16, C01, C02) re-aimed and viewed.

## Review log
