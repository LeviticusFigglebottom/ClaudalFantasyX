# Battle VFX library (M2-RND-03)

The battle's effects: a hit per element, the slice's signature skills, heals, statuses, the KO, and the opening
flash. They're data-driven, listen-only, and safe for photosensitive players.

## How it's wired

- **`BattleVfx`** (`game/vfx/battle/battle_vfx.gd`) is a view.
  - `BattleController._build_engine` attaches it with one line, `BattleVfx.attached(self, engine)`, next to
    `BattleBossHud.attached`.
  - It connects to `engine.action_resolved` and **never writes combat state**. The battle engine stays headless
    (CLAUDE.md §3).
- **What an action plays.** `effects_for(result)` returns `[{effect, target}]` with no nodes, and the tests call
  it. For each hit of an action:
  1. The skill's own effect, if `map.skills` names it, or the item's, if `map.items` does. It plays once per
     target.
  2. A hit that landed then plays by what it did:
     - damage plays `map.elements[<the skill's element>]` (an item, or an unknown element, plays `none`);
     - an HP restore (`amount < 0`) plays `events.heal`;
     - any added status plays `events.status`;
     - a hit that leaves the target at 0 HP plays `events.ko`.
  3. A miss plays only the skill's own effect. A failed action plays nothing.
- **The opening.** A battle that starts in an ambush or a preemptive plays `events.ambush` / `events.preemptive`
  (`engine.opening`).
- **Data:** `game/data/vfx/battle/effects.json`.
  - `effects`: each effect is `particles` (one emitter, or one per entry of `layers`) or `flash`.
  - `map`, `anchor_heights` (feet, chest, head: fractions of the stand-in's height), `safety` and
    `reduced_motion`.
  - Colours are palette swatches, named in each layer's `swatches` and tested against `palette.json`.
- **Rendering:**
  - Built-in `GPUParticles3D`: no custom shader.
  - One shared billboard draw material (`materials/battle_spark_draw.tres`: alpha blend, unshaded, a procedural
    soft dot, sRGB vertex colour).
  - A `ParticleProcessMaterial` per effect layer, copied from `battle_spark_process.tres`.
  - Emitters are pooled per effect layer (six each).
  - **Prebuilt at attach (M2-RND-07).** `prebuild()` builds one emitter per layer of every particle effect,
    without emitting, in the frame the battle scene enters (under the router's opaque fade). The first emitter of a
    ParticleProcessMaterial feature set (turbulence on) costs about 32 ms of main-thread work in the battle's tree.
    Built mid-fight, the Drownbell's `polyp_rise` made the Flood a 35–44 ms frame (79 ms on a fresh install).
    - A staged prewarm didn't help: holding its materials didn't carry the cost over, so it's the emitter's, in
      this tree.
    - The prebuild adds about 0.3 s to the battle's hidden entry: worst frame 0.35–0.6 s, entry 0.9–1.4 s, inside
      ADR 0029.
  - The pair is registered for prewarm on `battle_sandbox.tscn` and `field_battle.tscn`.

## The first set

| Effect | Trigger | Look |
|---|---|---|
| `hit_none`, `hit_fire`, `hit_ice`, `hit_lightning`, `hit_water`, `hit_holy` | damage, by the skill's element | an impact core and sparks: foam white, ember to dusk gold (rising), salt glass (falling), starlight (fast, brief), turquoise spray (falling), sun gold (rising) |
| `lamp_dive` | Rhen's Swell | an oil-lamp column and a splash from the target's feet. Oil light, never glimmer (decisions_log N-02) |
| `shallows_verse` | Asha's Swell heal | shallow-water light lapping up around each ally |
| `read` | Read | a still ring of gold points |
| `heal`, `status_apply` | HP restored; a status added | rising heal sparks; sinking indigo motes at the head |
| `ko_release` | a KO | the fighter dissolves into **released glimmer**: `glimmer_lift` motes rising in slow spirals (color_script.md rule 1) |
| `flash_preemptive`, `flash_ambush` | the opening | a sun-gold or a deep lacquer-red tint |

Key frames (RX 9070 XT, High) are in `docs/kb/qa/gpu/rnd03/`: `elements`, `lamp_dive`, `shallows_verse`, `ko`
and `ambush_flash`.

## Safety and readability (pillar 4)

- **Photosensitivity.** Every flash's opacity is capped at `safety.flash_max_alpha` (0.3). Two flashes are at
  least `flash_min_interval_s` (0.5 s) apart, at most two a second, under WCAG 2.3.1's three. A refused flash
  counts in `flashes_suppressed`.
- **The timeline is never covered.** Flashes draw on a CanvasLayer at `safety.flash_layer` 0, below the HUD's
  layer 1, so they tint the 3D view only (`ambush_flash.png`). The particles are in the 3D world, under the HUD.
- **Reduced motion** (`UiSettings.reduced_motion()`, followed live):
  - particles × 0.4 in number and × 0.5 in speed;
  - no turbulence;
  - flashes at a third of their opacity, with at least a 0.3 s ramp.

## Cost (RX 9070 XT, battle sandbox, 2560×1440, GPU median over 300 frames)

`tools/gpu_bench/battle_vfx_probe.tscn --bench` compares an idle pass with a pass that replays effects every
30 frames.

| Load | High | Low |
|---|---:|---:|
| Idle | 0.860 ms | 0.557 ms |
| The worst 3v3 burst (a fire hit, a status and a KO on all three foes, and Shallows Verse on the party) | 0.897 ms (+0.04) | 0.590 ms (+0.03) |
| The same, reduced motion | 0.894 ms | 0.582 ms |
| Any one effect on all three foes (`--effect=<id>`, all 12 measured) | +0.03 to +0.04 ms | – |

Even on a min-spec card (×4–5) that's a fraction of a millisecond: well within the budget.

## Adding an effect

1. Add it to `effects` (palette hex values, with their swatch names), and map it in `map.skills`, `map.items`,
   `map.elements` or `map.events`.
2. `tests/unit/test_battle_vfx.gd` checks the swatches, that every map target exists, that every skill element is
   mapped, and the trigger rules.
3. Look at it with `tools/gpu_bench/battle_vfx_probe.tscn` (add a group to its `GROUPS`), and measure it with
   `--bench --effect=<id>`.

## Known limits (next passes)

- **Pale effects on bright scenes.** On the noon beach the pale ones (ice, the KO's lift) read softly. An art
  pass with flipbook sprites, or a stronger core, would help.
- **Effects play when the engine resolves the action,** not on an animation's contact frame. Body clips don't
  exist yet (M2-FP-07). When they do, `play()` can be deferred to the clip's hit marker.
- **Boss effects:** the Drownbell's are below (M2-RND-04).

## The Drownbell (M2-RND-04)

`BattleBossVfx` (`game/vfx/battle/battle_boss_vfx.gd`) plays a boss's set piece. Its data is
`game/data/vfx/battle/boss_vfx.json` (one row per boss), and its particle effects are entries in `effects.json`.
`BattleVfx.attach` builds it when an enemy has a boss row, so the controller still has one VFX line. It listens to
the engine's boss signals (battle_ctb.md "VFX hook points") and never writes combat state.

| Moment | Signal | What plays |
|---|---|---|
| The toll gathers | `charge_started` (the bell, `toll`), then each `turn_started` while it charges | A `spawn_wound` rim glow (an OmniLight3D) builds a step per turn and is full on the turn the toll fires, with a slow pulse. `toll_gather`: held motes drawn down the hood. |
| The toll | `action_resolved`, `toll` | A shockwave ring over the water from the bell's foot to past the party (`battle_shockwave.gdshader`, 1.4 s), plus `flash_toll` (a capped flash). The floats' flinch and shake do the knock-back. |
| Rim hits, the break | `weak_point_hits` on a hit; `charge_broken` | `rim_crack` sparks per hit; `rim_break`, a cyan burst, and the glow drops. |
| The Flood | `phase_changed`, `flood` | **The flood rig:** the water rises from -0.7 to +0.6 m over 8 s, eased (haluna.md section 2.2). The sun's key falls to 0.6x (2.0 to 1.2 in the color script) and sea-glow goes from 0.04 to 0.06. |
| Polyps | `combatants_joined` | `polyp_rise` at each polyp, and a `spawn_wound` light at it that glows under the water until it falls. |
| A polyp mends the bell | `action_resolved`, `polyp_mend` | `polyp_mend`: held motes streaming from the polyp to the bell (aimed at play time, sinking). |
| Call Ilun | `field_cleared`, `flood` | **Floodnet:** a steady net of `glimmer_bound` threads on the water, with a teal fill (bound light: it fades in, holds and fades out, with no drift or trails), then the water falls back over 6 s. The polyps' lights go with the field. |
| The bell dies | its KO through `BattleVfx.effects_for` | `effects.json` `map.ko_overrides`: `bell_release`, motes sliding seaward and down. Never the rising release. |

**The flood rig.**
- **Publisher.** It's a `WaterSurface` that publishes `hymn_water_level`, the battle scene's one publisher
  (M1-RND-15). Leaving the tree resets the global.
- **Look and waves.** The color script's `lagoon_low_sun` look and the lagoon's four longest waves at 0.6x, both
  in data.
- **The sandbox sea.** The sandbox's flat `Arena/Sea` gives way to it at the start, so the fight opens at low
  tide with real water around the dais.
- **Retry.** A retry replaces the whole VFX view, so the old water stops publishing.

**The weather clock.** Since M2-ARC-02 the rig never writes `hymn_wind_time`: `WeatherClock`, SceneRouter's
child, is its one writer in play and runs it through every battle (architecture.md, "The weather clock"), and
the flood water reads it from the global. The battle scene gets the zone_weather.json default wind on its swap.
When the wind is still calm (a scene with no zone wind, like the drownbell_flood test rig), the rig sets the
breeze in `flood.weather` and puts the wind back when it leaves.

**Reduced motion** (UiSettings):
- The shockwave runs 1.8x slower at half its alpha.
- The glow doesn't pulse.
- The Floodnet fades over at least 1 s.
- Particles thin as in RND-03.
- The flood still rises over 8 s, because the rise is the phase's information.

**Cost** (RX 9070 XT, 2560x1440, GPU median over 300 frames; `tools/gpu_bench/drownbell_probe.tscn --bench`). The
sandbox's own `sandbox_reef` battle frame, with the flat sea, is 0.88 ms at High and 0.58 ms at Low.

| Preset | Opening (low tide) | Flood up (water over the dais, 2 polyp lights) | Flood plus the toll ring, the Floodnet and motes |
|---|---:|---:|---:|
| Low | 0.77 ms | 1.20 ms | 1.25 ms |
| Medium | 1.01 ms | 1.62 ms | 1.70 ms |
| High | 1.14 ms | 1.92 ms | **2.00 ms** |
| Ultra | 1.49 ms | 3.30 ms | 3.37 ms |

- **Where the cost goes.** Nearly all of it is the flood water covering the screen; the ring, the net and the
  lights add under 0.1 ms. At High the worst battle frame is 2.0 ms, well inside the 16.7 ms frame. On an RTX
  3060 (about 3x slower) it's about 6 ms.
- **Reduced motion** costs the same (High: 2.00 ms).

**Key frames** are in `docs/kb/qa/gpu/rnd04/` (High, from `drownbell_probe.tscn`):
- `opening`, `telegraph`, `toll`, `toll_reduced_motion`, `rim_break`;
- `flood_full`, `mend`, `floodnet`, `bell_release`.

A screenshot fixture, `game/levels/_tests/drownbell/drownbell_flood.tscn`, holds the flood at full height
(`BattleBossVfx.settle()`); it's deterministic on the GPU. Its pending lavapipe shot is
`docs/kb/qa/gpu/2026-10-24-rnd-04-pending-shots.json`.

**Not done (next passes):**
- **The arena is the noon sandbox.** The fight's 18:15 sunset grade (color script `ch03_boss`) belongs to the
  arena scene, and the rig only scales whatever sun it finds.
- **The bell doesn't sink.** The water covers its lower quarter, but the stand-in doesn't sink.
- **No crack decals** on the rim: hits spray sparks only.
- **C10's full Ilun cinematic** waits on the Vowbound system (ADR 0026).
- **Prewarm.** The ocean prewarm entries now list the battle scenes, and the two new shaders are registered.
  Measure battle transitions again once M1-RND-22 merges.

## Act I abilities (M3-BPR-420, ADR 0041)
- Every Act I ability has its own effect: 77 skills and 8 battle items, written by `tools/vfx/gen_act1_ability_vfx.py`
  (each `note` says what it shows). It plays once per target on top of the element hit, the heal and the status.
- The exceptions: the ward-aimed Ch8 skills (no fighter to play on) and the Drownbell's toll (its boss view).
- Sounds are borrowed rows in `battle_sfx.json` until audio's own (request M3-BPR-421).
- `prebuild()` builds a skill's own effect only if someone in the battle can use it (headless: 178 emitters took
  66 ms; the sandbox fight builds 72).
- Viewing: `tools/vfx/act1_vfx_sheet.tscn` (six per sheet on the battle stage, labelled).
