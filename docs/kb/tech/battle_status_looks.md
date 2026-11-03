# Battle status looks and storm fights (FAST-TRACK 11-03)

Owner: battle-presentation. Tasks: M3-BPR-450 (status looks), M3-BPR-451 (storm fights). Requests out: M3-UI-212
(ui-menus: the icons in the status help), M3-ENV-1341 (env-art-b and act1-chapters: the storm fight list and grades).

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
| overlay | `status_overlay.gdshader` as every body surface's `material_overlay` (not the target ring). One at a time: the highest `priority` | `pattern` (rim, pulse, bands_up, bands_down, flicker, hatch, frost), `strength`, `speed` |
| aura | a looping GPUParticles3D on the fighter, at an anchor height (effects.json `anchor_heights`) | `motion` (rise, rise_fast, drift_up, fall, sag, shards, shards_wide, burst, hang, orbit), `at`, amount, size, speed |
| prop | a mesh round the body | `kind`: sphere (Shell), rings (Protect), panes (Reflect), ring at the mouth (Silence), ground_mark (Provoke) |
| icon | `assets/vfx/battle/status_icons/<id>.svg` over the head, in a row with the others; over the feet of a body taller than `icons.feet_over_height_m` | `icon_swatch`; Doom adds its count (`count`) |

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
| darkness | a dark veil sinks down the body; dark motes fall round the head | slashed eye |
| petrify | stone; grit trickles | cairn |
| slow | slow blue bands sink; heavy motes sag at the feet | hourglass |
| haste | gold bands race up; quick gold streaks rise | double chevron |
| stop | still pale glaze, no motion; sparkles hang frozen | two bars |
| berserk | fast red pulse; embers burst off the shoulders | jagged burst |
| confuse | gold flicker in patches; gold motes circle the head | spiral |
| doom | a dark tide climbs from the feet; the count by the icon | bell |
| zombie | patina hatching; dark drops fall | cracked heart |
| shell | a clear blue bubble round the body | three rings |
| protect | three gold rings at knee, waist and chest | shield |
| reflect | three salt-glass panes circle the body | mirror and rebound |
| regen | slow turquoise breath; small motes rise from the feet | plus |
| armor_break | brass shards fall off the chest | shield + down tab |
| mental_break | cyan shards fall off the head | rings + down tab |
| power_break | clay shards fall from the arms | blade + down tab |
| magic_break | blue shards fall from over the head | star + down tab |
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
- `fights`: encounter -> look. Ch1 after the Rising (`ch01_scuttlers`, `ch01_hullgnaw`); Ch8's headland path
  (`ch08_headland_gulls`, `ch08_headland_crabs`), the tier landing (`ch08_flue_moths`), the three stair holds and the
  Reach. `ch06_ridge_gulls` is a calm afternoon and is left out.
- `looks`: `preset` (an `undertow.json` preset for the Undertow), `yaw_offset_deg` (where it stands relative to the
  rest frame's look), `environment_res` (a whole storm Environment, e.g. Oruvel's after the Rising) and/or
  `sky_params` (the arena sky shader's uniforms: overcast, no sun disc), `sun` (energy scale, colour), `rain`, `wind`.

The Undertow in battle: its own rain curtains are off (the battle has its rain), its lightning never flashes the
screen (`exposure_flash` off: the battle flash safety contract), and it never takes the sun back (`zone_shadow` off).
`StormFarPlane` raises the battle camera's far plane past it.

PC-QUEUE: the Undertow's cost in a battle on the GPU (it stands in the field zones at the same moments already).
