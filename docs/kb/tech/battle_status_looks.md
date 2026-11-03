# Battle status looks and storm fights (FAST-TRACK 11-03)

Owner: battle-presentation. Tasks: M3-BPR-450 (status looks), M3-BPR-451 (storm fights). Requests out: M3-UI-212
(ui-menus: the icons in the status help), M3-ENV-1340 (env-art-b and act1-chapters: the storm fight list and grades).

## Status looks

The human's playtest: status effects must be **obvious on the character**. `BattleStatusLooks`
(`game/vfx/battle/battle_status_looks.gd`, attached by `BattleVfx.attach`) shows every status a fighter holds, on
that fighter, for as long as it lasts. It listens only: after the choreography's contact beat (or `action_resolved`
with no choreography), `turn_ended`, `turn_lost`, `turn_started` and `combatants_joined` it re-reads each
combatant's `statuses` and adds or removes looks. A fallen, withdrawn or yielded fighter shows none. The battle's end
takes them all off.

Each look (`game/data/vfx/battle/status_looks.json` `looks.<id>`) is made of:

| part | what it is | data |
|---|---|---|
| overlay | `status_overlay.gdshader` as every body surface's `material_overlay` (not the target ring). One at a time: the highest `priority` | `pattern` (rim, pulse, bands_up, bands_down, flicker, hatch, frost, cracks), `strength`, `speed` |
| aura | a looping GPUParticles3D on the fighter, at an anchor height (effects.json `anchor_heights`) | `motion` (rise, rise_fast, drift_up, fall, sag, shards, shards_wide, burst, hang, orbit), `at`, amount, size, speed |
| prop | a mesh round the body | `kind`: sphere (Shell), rings (Protect), panes (Reflect), ring at the mouth (Silence), ground_mark (Provoke) |
| icon | `assets/vfx/battle/status_icons/<id>.svg` in a row beside the head (right of the actor marker, or left of it for a fighter on the screen's right half, so it never leaves the frame); over the feet, centred, for a body taller than `icons.feet_over_height_m` | `icon_swatch`; Doom adds its count (`count`) |

Petrify's body look is the stage's existing stone material (`BattleStage.refresh_ko`); its look adds grit and the icon.

**Colour-blind safety.** No two statuses share a body signature (overlay pattern, aura motion and height, prop kind);
`test_each_look_differs_by_shape_or_motion` holds it. The icons carry the side in their badge (beneficial: a circle;
harmful: a rounded square) and the status in a glyph of its own; a "break" adds a down-arrow tab to the glyph of the
stat it breaks, so Protect and Armor Break share a shield, Shell and Mental Break the rings.

| status | on the body | icon |
|---|---|---|
| poison | green pulse; yellow-green bubbles rise off the chest | drop |
| sleep | indigo edge glow; big pale motes drift up from the head | crescent |
| silence | a still grey band at the mouth | slashed speech bubble |
| darkness | a black veil sinks down the body; dark motes fall round the head | slashed eye |
| petrify | stone; grit trickles | cairn |
| slow | slow blue bands sink; heavy motes sag at the feet | hourglass |
| haste | gold bands race up; quick gold streaks rise | double chevron |
| stop | still deep-blue glaze, no motion (stone is grey); sparkles hang frozen | two bars |
| berserk | fast red pulse; embers burst off the shoulders | jagged burst |
| confuse | gold flicker in patches; gold motes circle the head | spiral |
| doom | a red tide climbs from the feet in slow bands; the count by the icon | bell |
| zombie | patina hatching; dark drops fall | cracked heart |
| shell | a clear blue bubble round the body | three rings |
| protect | three gold rings at knee, waist and chest | shield |
| reflect | three salt-glass panes circle the body | mirror and rebound |
| regen | slow turquoise breath; small motes rise from the feet | plus |
| armor_break | brass cracks over the body; brass shards fall off the chest | shield + down tab |
| mental_break | cyan cracks; cyan shards fall off the head | rings + down tab |
| power_break | clay-red cracks; clay shards fall from the arms | blade + down tab |
| magic_break | blue cracks; blue shards fall from over the head | star + down tab |
| provoke | a red crosshair mark turns on the ground | crosshair |

Reduced motion: fewer aura particles and slower patterns and props (`reduced_motion`).

**Icons** are generated: `python3 tools/vfx/status_icons.py` (`--check` in the tools suite). Re-run it after adding
a status or changing an `icon_swatch`.

**Contact sheet:** `godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver
vulkan res://tools/vfx/status_look_sheet.tscn -- --out=<abs dir> [--enc=ch01_scuttlers] [--only=a,b]` writes one
still per status on the first hero and the first foe at once, and `stack.png` with three each.

## Storm fights

The human's playtest: the seagull/storm scene's fights used the normal sunny backdrop and never showed the Undertow.
`BattleStorm` (`game/vfx/battle/battle_storm.gd`, attached by `BattleVfx.attach`) turns a listed fight's arena into
its storm variant at spawn. The arena scenes are untouched: the Environment, Sky and sky material are duplicated.

`game/data/vfx/battle/storm_fights.json`:
- `fights`: encounter -> look, matching act1-chapters' storm table (encounters.json `storm: true`, arenas.json
  `storm`). The storm fights are Ch1 C1-13/C1-14 (`ch01_scuttlers`, `ch01_hullgnaw`), Ch8 B10-B16 (the three stair
  holds, `undertows_reach`) and Ch16 B09 (`ch16_storm_wakes`). Ch8's headland fights and the flue moths come before
  the storm, so they are not storm fights.
- `looks`: `preset` (an `undertow.json` preset), `yaw_offset_deg`, `environment_res` and/or `sky_params`, `sun`,
  `rain`, `wind`.

**One Undertow per fight** (the Lead, 11-03, big47):
- A storm arena with its own `Undertow` (arenas.json `storm.arenas`: the seawall arenas; env-art's
  `oruvel_raft_storm` once built) owns the static set: the sky, the wet surfaces and the vortex.
  - BattleStorm then adds only the dynamic layer: wind and spray, plus rain only when the arena's storm brings
    none (row 72: doubled rain hid the party).
- On an arena without one (`storm.pending`'s interims), BattleStorm draws the full look: the sky, the sun and its
  own Undertow.
- `test_no_storm_fight_draws_two_undertows` holds this.

The fallback Undertow: its own rain curtains are off (the battle has its rain), its lightning never flashes the
screen (`exposure_flash` off: the battle flash safety contract), and it never takes the sun back (`zone_shadow` off).
`StormFarPlane` raises the battle camera's far plane past it. It keeps its preset's distance: its bound is about
16 km, and a battle nearer than that stands inside it.

**Framing:** choreo.json `camera.rest_by_encounter` tilts a storm fight's rest frame up (`tilt_up_deg`), so the
sky behind the foes is in the frame (Ch1: 8 deg).
- Ch8's stair holds have no tilt: the wall's merlons fill the sky there. M3-ENV-1340 asks env-art-b for a
  sightline.

PC-QUEUE: the Undertow's cost in a battle on the GPU (it stands in the field zones at the same moments already).
