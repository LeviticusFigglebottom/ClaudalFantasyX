---
id: M3-C08-1202
title: Ch8 greybox to final, ch08/corrow on the seawall kit's heights (walk at 12 m, the Fisher Stair, the Bastion, the mole)
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-ENV-04, M3-ENV-04B, M3-C08-02, M3-C06-1200]
milestone: M3
request-from: ""
---
## Goal
Swap Ch8's flat greybox Corrow for env-art's seawall kit (M3-ENV-04, the breach M3-ENV-04B). Unlike Ch6, the kit's
heights matter to play: the walk is 12 m above the low town and the Fisher Stair climbs the wall's inner face, so the
zone moves into the kit's frame and its collision is generated from the kit (ADR 0200 "Consequences").

## Acceptance criteria
- [x] `tools/act1/corrow_frame.py`: the kit's frame and the greybox → kit map; `ch08_corrow_relayout.py` migrated
      the layout once (spawns, marks, actors, shots, triggers, story blocks).
- [x] `tools/act1/ch08_corrow_dressing.py`: the kit dressing (wall, Watchers, reliefs, stair, hoist, town, far ground,
      headland; the stair breach on the `Breach` block) and the collision (`corrow_collision.json`: wall, kerb and
      parapet per segment, town floor, Bastion platform, the stair's flights and the mole as `Ch04Zone` ramps).
- [x] The fall hides the breach segment, its parapet and kerb, the Watchers there and the stair's upper flights.
- [x] Light rows: the day is the kit's front, the storm the surge, the aftermath the fallen grade (`environment_res`).
- [x] `test_ch08_thread` passes; `test_ch08_corrow_walkable` walks the mole, the walk, the stair both ways and the
      town lane, and stands every mark on a floor.
- [x] The views viewed on lavapipe (arrival, walk, stair, low town, Bastion); the cutscene shots re-aimed where the
      map misplaced them (W10, W14, W21–W23); baselines `ch08_corrow_arrival`, `ch08_corrow_stair` (viewed).
- [x] The Bastion dressed from the kit: seawall segments turned outward as its revetments, ground cells on top.

## Notes
- Greybox kept visible until env-art builds them (M3-ENV-1203): the mole's pier and ramp, the Bastion's platform and
  rim, the kites, the net racks, Marra's step, the hoist's pins, rope and basket, the trader, the flood and the lake,
  the shrine, the chandler, the wall-gate.
- The houses come from the kit's own town generator, minus those within 8 m of a story mark or trigger, on the
  Bastion or by the stair.

- Reviewer: environment (placement), then narrative (the breach now takes the stair's middle, as the kit has it).
- Not yet: Ch9's `ch09/corrow_night` is still the flat greybox (next), and the shrine is a greybox marker.

## Review log
- **2026-10-27, environment (env-art, session_01YbaV2c8yquRHqj6afQYg89): placement approved. Narrative is next, so
  the status stays `review`.**
  - **Checks run:** `--filter=ch08` 19/0, `--filter=zone_kit` 6/0, and `tools.tests.test_act1_kit_collision` OK.
  - **Viewed:** `ch08_corrow_arrival` and `ch08_corrow_stair`. The wall, the Watchers, the reliefs, the town's
    houses and the stair stand on the kit's own heights and frame correctly; the breach takes the stair's middle.
  - **What still reads as greybox in the arrival:**
    - the mole pier (the flat grey slab under Rhen);
    - the actor stand-in capsule on the stair view, which is the cast's.
  - **Kit pieces now built for the greybox blocks** (M3-ENV-707 / M3-ENV-1203, `assets/environments/kits/corrow/`),
    ready to swap in with `ch08_corrow_dressing.py`:
    - `mole_pier`, `mole_sea_stair`, `bastion_platform`;
    - `stillguard_barracks`, `wall_gate`, `kite_line`, `kite_line_high`, `marra_step`;
    - `hoist_pins`, `hoist_rope`, `hoist_basket`, `trader_boat`.
    `Flood` and `Lake` are Rendering's water.
