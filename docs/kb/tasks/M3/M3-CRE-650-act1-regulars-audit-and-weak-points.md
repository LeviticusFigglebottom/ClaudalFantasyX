---
id: M3-CRE-650
title: "Act I regulars: audit to final quality; weak-point marks for flue_moth, raid_hound and vein_sparker"
role: character
status: review
owner_session: "creatures (worktree agent)"
reviewer: art
depends_on: []
milestone: M3
request-from: lead
---
## Goal
ADR 0041 (Act I at final quality first; the Lead's refocus, 2026-10-28): every **regular** enemy a player fights in
Act I gets its real mesh, rig, full animation set (idle, hit, act, death), weak-point readout and spawn/death VFX hooks,
self-rendered and viewed at battle distance and in the bestiary portrait. The bosses and the Vowbound are creatures-b's.

The 20 regulars (encounters.json, Ch1–Ch8 plus the slice): ashwing, flue_moth, gull_harrier, lantern_eel, oil_slug,
raid_hound, reef_crab, sail_leech, scuttler, shoal_skipper, slag_tortoise, squall_wing, stormgull, tide_crawler,
tower_limpet, vein_sparker, wall_polyp, wallcrab, wickfry (glassfry's model), wreck_crab.

**Audit (2026-10-28, creatures):** all 20 have a real mesh and rig and the full set (idle, ready, attack, cast, hit, hit_b, ko). 17 carry a spawn_wound weak point. **flue_moth** (ember glow only), **raid_hound** (no emissive) and **vein_sparker** (starlight glow, a palette point-source swatch at 2.5–4.0 over its scales) have none: each needs one small closed spawn_wound mark (ADR 0151), and vein_sparker's starlight is to be checked against palette.json's ≤0.5% usage limit.

## Notes
**Weak points added (2026-10-28, creatures worktree agent).** Each is one small closed `spawn_wound` mark (ADR 0151:
all three are beasts, so no seam is open and none sheds motes). Each is a glowing lens of seam in a raised dark lip,
projected onto the part's surface and bent to its curve, at the reef crab's values (#3FE0C8, 1.4, 0.35 Hz, depth
0.35):
- **raid_hound:** an old gaff scar healed shut, slanting across the breast below the throat toward its right (-x),
  11 x 2.4 cm, in the `coat` slot (it had no emission). Its sheet's "no weak-point glow" is superseded.
- **flue_moth:** a seam seared shut across its brow above the eyes, toward -x, 7.6 x 2.6 cm, in a new `wound` slot
  (the fur's emission is the embers), with a PROVENANCE row for `materials/wound.tres`. A first try on the thorax
  collar was buried by the shaggy fur.
- **vein_sparker:** an old break healed over on top of the tail's root, where the tail climbs into the coil, toward
  -x, 6.8 x 2.2 cm, in the `scale` slot.

**Camera side.** The brief said "+x", but every creature source and sheet (reef crab, gallery ray, ridge lynx, lantern
eel, gull harrier, squall wing, wreck crab) puts the battle camera on the model's -x. The stand-in yaw is 90 and the
BattleCamera is at (0.6, 2.8, 8.4), which gives a view from model space of about (-0.88, 0.33, 0.35). The review
three-quarter (creature_stage.json, yaw 35) and the portrait (yaw 30) look from the +x front quarter. So each mark
faces forward and up, a little toward -x, where both views see it.

**Starlight (vein_sparker).** The coil's whole last third glowed `starlight` as a surface, covering 1.4% of a filled
review frame. That broke palette.json's "point sources only; <=0.5%". The charge is now points only: the 11 spine
tips and four 1.6 cm sparks on the coil's flanks, alternating -x and +x (`copper` slot, values unchanged). That is
0.30% of a filled review frame. The coil's last third is bare `hair_copper`. The decision is recorded in the sheet.

**Unchanged:** clips, bones, rests and contact times. All three GLBs' animation channels and node rests are
bit-identical to before, so grounding is untouched and no allow-list was added. Budgets: hound 3760 / 7k, moth 3240 /
5k, sparker 4240 / 5k. Each build script now has `build_mesh()` (rig and mesh without Blender), which the preview
sheets use.

**Previews (numpy/PIL from the GLBs, z-buffered; not engine renders):** before/after sheets
`<scratch>/M3-CRE-650/{raid_hound,flue_moth,vein_sparker}_final.png`, with battle-scale zooms in `*_final_zoom.png`.
They cover the three-quarter (35/14), the battle direction at about 110 px/m (supersampled), the front and the camera
side. The coordinator self-renders `creature_flue_moth`, `creature_raid_hound`, `creature_vein_sparker` and their
portraits. The old baselines and portraits are stale for these three.

## Review log
