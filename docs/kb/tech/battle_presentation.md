# Battle presentation (M2-BPR)

## Encounter transition

M2-BPR-05 part 1: the beat between a field battle being asked for and the battle's first turn, and the
opening banner's timing. The victory pose and the return to the field are part 2.

### The stinger: a tide line

When `BattleRequest.submit` opens a battle (every field fight goes through it: `HalunaStory`, the
First Verse's `<<event start_battle>>`), it first awaits `BattleStinger.play()` (`game/flow/battle_stinger.gd`),
then calls `FlowRouting.change_scene` as before. The stinger is a `CanvasLayer` added to the field scene:

1. **Rise** (`rise_sec` 0.5, eased out by `rise_ease`): a band of dark water rises from the bottom edge to
   `crest` (62 %) of the screen. Its surface is a slow two-sine swell with a thin foam crest. The field under
   it ripples sideways a little, as if seen through water, and sinks into a gradient from `deep_teal_shadow`
   at the surface to `abyss_navy` at the bottom. The field above it dims (`dim`) and loses its colour
   (`desaturate`). The player stops where they stand (`FieldController.accepts_input` off, velocity zeroed).
2. **Hold** (`hold_sec` 0.25): the drowned, greyed field holds for a breath.
3. The router's opaque fade then runs exactly as before (`SceneRouter.FADE_SEC`, black, layer 128, above the
   stinger's layer 120). The stinger is a child of the field scene, so it goes when the router unloads the
   field under the opaque fade. If it had to sit on the root, it goes on `scene_swapping`.

The stinger lasts 0.75 s in all. The idea is a tide coming in over the world rather than the world breaking
apart: the sea takes the field, quietly, and the fight happens under it (pillar 2, beauty in decline). It is
not a shatter, a swirl, a spin, a zoom or a flash, and it has no camera move.

- **Shader:** `game/shaders/vfx/battle_tideline.gdshader` (canvas_item, reads `hint_screen_texture`). At
  `progress` 0 it outputs the screen unchanged. `phase` is driven by the stinger's clock, not `TIME`, so a
  frame can be reproduced.
- **Data:** `game/data/flow/battle_transition.json`. Every time, fraction and colour is here, and the colours
  are palette swatches named in `swatches` (tested against `docs/kb/art/palette.json`). `enabled: false`
  turns the stinger off.
- **Prewarm:** the shader is in `prewarm_materials.json` for the zones that open battles (Haluna, the First
  Verse), so its pipeline compiles under the zone-entry fade, not on the frame the stinger first draws.

### Accessibility and safety

- **Reduced motion** (`UiSettings.reduced_motion()`) uses no shader at all: a plain `ColorRect` cross-fades to
  `abyss_navy` at alpha 0.6 over 0.35 s, holds 0.15 s, then the router fades. Nothing sweeps or ripples.
- **No flash.** The stinger only darkens the field. Its one bright element, the foam crest, is a hairline at
  `foam_alpha` 0.28, under battle_vfx's `safety.flash_max_alpha` (0.3, tested). The stinger plays once per
  battle, far more than 0.5 s from any battle flash.

### ADR 0029 budgets are unchanged

The stinger runs **before** `SceneRouter.change_scene()` is called. The router's entry window (change_scene
until the fade lifts), its hidden frames and its staged battle build are untouched, so `entry_ms`,
`max_frame_ms` and the visible window measure exactly what they measured before. The stinger's own frames
are ordinary visible field frames: one full-screen canvas pass with one screen copy. The stinger is skipped
when the router is already busy, because the screen is covered or about to be.

### Opening banner timing

`OpeningBanner`'s times are data in `battle_hud.json` `opening_banner`: `fade_in_sec` 0.3, `hold_sec` 1.8,
`fade_out_sec` 0.5 (ui.md rule 11), plus `reveal_wait_max_sec` 3.0 (new).

The staged build (`start_battle_staged`) opens the first turn while the router's fade is still up, and the
banner used to start its fade-in then, partly unseen. Now `show_opening` checks `is_screen_covered()`
(`SceneRouter.is_busy()`, which stays true until the fade has fully lifted). While the screen is covered, the
banner is **pending**: it stays invisible with no timer, and `BattleHud.holds_battle()` is true, so the
controller holds its paced waits. An ambush's first foe does not act unseen. Once the fade has lifted, or
after `reveal_wait_max_sec` at most, the banner plays its fade-in, hold and fade-out, and the first turn goes
on. Instant pacing (captures, tests) never waits.

### Tests and shots

- `tests/unit/test_battle_stinger.gd` covers:
  - the data loads and names real swatches;
  - the length fits the 0.6–0.9 s brief and the rise eases to full;
  - the foam stays under the flash cap and the layer sits under the router's fade;
  - the tide line finishes once, and reduced motion is a plain cross-fade with no shader;
  - `BattleRequest.submit` plays the stinger before the router's change, and a recorded change (tests)
    skips it;
  - the banner's timings are data, and it waits for the fade (holding the battle), gives up at its cap, and
    never waits when uncovered or instant.
- **Screenshots:** no shot in `tests/screenshots/shots.json` captures the field-to-battle transition, so no
  baseline moves. `battle_opening_banner` renders at instant pacing (shown, no wait) and is unaffected.
- **Hooks for tests:** `BattleRequest.play_stinger` and `OpeningBanner.screen_covered`, both Callables.
