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
- **Boss effects are separate work:** the Drownbell's are M2-RND-04, on the hook points in battle_ctb.md.
