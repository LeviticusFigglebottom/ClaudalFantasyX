---
id: M3-UI-04
title: Act I area maps and objective lines (Ch1, Ch4, Ch5, Ch7, Ch9 greybox zones)
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M3
request-from: lead
---
## Goal
Lead queue item 6. The map and the objective line know only the slice (Haluna and the Shell Shrine). Give every Act I greybox zone that m2-slice has built a map and objective rows, so the player always knows the next step there too.

## Acceptance criteria
- [x] **Shapes from the layout.** A new shape kind, `greybox_layout` (`ZoneMapShapes`): each block's footprint is turned by its yaw as GreyboxZone builds it. Its height and size pick the layer: floor, pad, building or structure. Posts, overhead blocks and non-solid decor are left off. `shape_hints` in `zone_maps.json` names blocks by layer where height alone reads them wrong (the sea, channels, the galleries' stands, lamp strips). The thresholds are in `zone_map_menu.json` `greybox`. The new `seas` layer draws under everything.
- [x] **Nine zones in `zone_maps.json`,** with bounds, shape hints and POIs (counts in brackets):
  - `ch01/oruvel_underway` (11)
  - `ch01/oruvel` (11)
  - `ch04/haluna_wake` (8)
  - `ch04/brightwater_ferry` (9)
  - `ch05/pemakar` (7)
  - `ch05/ashcrown` (10)
  - `ch07/tamsule` (6)
  - `ch07/tamsule_bell_galleries` (4)
  - `ch09/corrow_night` (6)
- [x] **POI sources.** A greybox scene is only its root, so these sources name layout points: `spawn:`, `trigger:`, `actor:` and `mark:`. `tools/tests/test_zone_map_pois.py` checks them, and checks that every shape hint names a block the layout still has.
- [x] **The route** runs the whole of Act I, from the Underway to Corrow (12 stops). The strip shows two stops either side of the current one (`zone_map_menu.json` route `before`/`after`), so it stays readable and the road far ahead stays unnamed. The strip's rect was widened to fit five names.
- [x] **39 objective rows** in `objectives.json`, each on the chapter's own flags (all declared), with loc keys appended to `strings.csv`: Ch1 14, Ch4 8, Ch5 7, Ch7 6 and Ch9 4. Each chapter's rows are listed in the note for m2-slice below.
- [x] **Tests:**
  - `test_objective_tracker.gd`: Ch1 walked flag by flag, either lashing first, Ch4–Ch9 spot checks, and errands that come and go.
  - `test_zone_map.gd`: every greybox zone builds (shapes, POIs in bounds, known glyphs, on the route), the block rules, yaw, Oruvel's sea, the route window, and the Underway view's marker.
- [x] **Shot:** `field_menu_map_underway`, the Underway after the glassfry shoal. `field_menu_map_haluna` and `field_menu_map_shrine` were re-approved for the wider five-stop route strip.

## Note for m2-slice (M2-FP-25 keeps these current)
New rows in `game/data/flow/objectives.json`. When a beat, flag, trigger or spawn moves, update the row or the POI; the POI test fails when a source drifts.
- **Ch1 Underway:**
  - main rows: `u_crown_tether`, `u_bell_tether`, `u_galleries`, `u_gauge_room`, `u_gauge_wheel`, `u_current_shaft`
  - side: `u_side_hinge`
- **Ch1 Oruvel:**
  - main rows: `o_kell`, `o_dive_mooring`, `o_low_run`, `o_lashing_west`, `o_lashing_east` (one line for both lashings, in either order), `o_net_pen`, `o_hold_net_pen`
- **Ch4 Haluna wake:**
  - main rows: `w_neme_table`, `w_wall`, `w_sleep`
  - side: `w_side_ink`
- **Ch4 ferry:**
  - main rows: `f_bow`, `f_galley`, `f_hold`, `f_mainmast`
- **Ch5 Pemakar:**
  - main rows: `p_crown_bell`, `p_harbour_road`
  - side: `p_side_smith`
- **Ch5 Ashcrown:**
  - main rows: `a_crown`, `a_trial`, `a_anvil_court`
  - side: `a_side_quench`
- **Ch7 Tamsule:**
  - main rows: `t_market_boats`, `t_gantry`, `t_harbour`
- **Ch7 Bell galleries:**
  - main rows: `g_rim`, `g_to_port`
  - side: `g_side_moorings`
- **Ch9 Corrow:**
  - main rows: `c_landing`, `c_road`
  - side: `c_side_toma`, `c_side_liss`

## Gaps (for m2-slice or the Lead)
- **No flag between two beats:**
  - The Underway's drop to the galleries sets no flag. `u_bell_tether` points at the bell-room tether until the glassfry fight is won, a walk of about 13 m after the drop.
  - The Ashcrown trial has no per-tier flags. `a_trial` points at the crown tier's rod for the whole trial; a flag per tier landed would let the line follow the strike down.
- **Not mapped:**
  - Ch6 and Ch8 have no zones on this branch, so they have no route stops and no rows. Ch6 is in progress (M3-C06-02, m2-slice); its zones need a row each, with route stops between Ashcrown and Tamsule, once it lands.
  - `ch03/saltgrass_causeway` is a route stop with no map of its own (route id `causeway`), as before.
- **Waits on Ch8:** `c_side_liss` needs `ch08_hoist_cut_down` (the trigger it mirrors needs it too), so it never shows until Ch8 sets that flag.
- **Secret left unmarked:** the old tin (Underway) is a lantern secret, so it has no POI. The alcove's floor still shows on the map as a nook.
- **`OBJ_NONE` names Haluna** ("Haluna's lanes are yours to walk"). It shows in any mapped zone where no row applies, for example for a moment between chained beats, or after Hullgnaw in Oruvel. It needs a place-neutral line or a per-zone one. That is a UI follow-up, left alone here to keep existing shots stable.
- **Lines to check with Narrative:**
  - `w_wall`, "Go up to the wake-shell wall with Asha.", is written from the layout's state notes (Asha's shell is set in the wall).
  - `p_crown_bell` names Lanternfall, which Ysolde says on the ferry.

## Review log
