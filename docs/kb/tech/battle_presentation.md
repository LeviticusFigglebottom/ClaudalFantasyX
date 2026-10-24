# Battle presentation (M2-BPR)

How a battle *moves*: the choreography of each action, the clips fighters play, the camera, the specials, and
the way into and out of a battle. Everything here is a **listen-only view** of the headless engine
(CLAUDE.md §3). It never writes combat state, and with the controller's pacing at 0 (tests, captures) it lands
every action at once, exactly as the battle did before it existed.

## Choreography (M2-BPR-01)

**`BattleChoreo`** (`game/battle/scene/battle_choreo.gd`) is a node under the stage.
- `BattleController._build_engine` attaches it with one line, `BattleChoreo.attached(self, engine)`, where
  BattleFloats used to connect to `action_resolved`. A retry replaces it.
- It connects to `engine.action_resolved`. The engine has already resolved the action, so the choreography is
  pure presentation of a known result.

**One action is five beats**, from `plan_for(result)` (pure data; the tests call it):

| Beat | When | What happens |
|---|---|---|
| approach | 0 → `approach_sec` | The actor travels to its strike point: `travel: target` runs to `stop_short_m` in front of the target(s) (their middle for a group), `step` steps `step_m` toward them, `none` stays on the mark. It plays `ready`. |
| strike | → `+ strike_sec` | The style's clip (`attack`, `cast`, ...), or on a stand-in the procedural strike: a lunge (`lunge_m`), a rise (`lift_m`) or a crouch (`crouch_m`) and a lean (`lean_deg`), peaking on contact. |
| contact | `approach_sec + contact_at × strike_sec` | **The blow lands**: the damage numbers and float words (BattleFloats.show_hits), the hit VFX (BattleVfx listens to `contact`), the crit shake, and each target's reaction (below). |
| recover | → `+ recover_sec` | The actor holds its strike point. |
| return | → `+ return_sec` | The actor goes back to its mark. |

- **KO.** A target the action felled collapses `ko.delay_sec` after contact. BattleStage.refresh_ko holds its KO
  look (`holds_ko`) until then. A model with a `ko` clip plays it through the stand-in's own KO path; a stand-in
  drops `drop_m` and tips `tilt_deg` away from the actor over `collapse_sec`, then sinks and fades as before. It
  lies tipped until a revive (`on_ko_state`) stands it back on its mark.
- **Reactions** (`reaction`): damage recoils `recoil_m` away from the actor and tips `tilt_deg` back, out and back
  over `sec`; a heal lifts `lift_m`; a miss sidesteps `dodge_m`. The actor never reacts to its own action.
- **Styles.** An item plays `item_style`; a skill plays `style_by_skill`, else `style_by_target` (self-targeted
  skills guard), else `style_by_kind`; the fallback is `melee`.
- **Swap and call.** A fighter the stage seats mid-battle (a swap, a Vowbound's call) walks onto its mark from
  `enter.back_m` behind it over `enter.sec` (`BattleChoreo.enter`, from BattleStage.sync_party).

**The turn hand-off.** `BattleController.after_action` waits `BattleStage.hold_after(base)`: the base hold, or,
while a sequence plays, its remaining time plus `settle_sec`, whichever is longer. That is the only change to the
controller's flow (in place, no new line). The engine never waits on the choreography beyond that hold. The
end-of-turn floats (Poison, Regen, Doom) wait for the sequence too (`after_sequence`).

**Instant.** `animating()` is false when the controller's `pacing_scale` is 0 or "skip animations" is on: the
floats and VFX land with the action and nothing moves. Freeze-frame captures set `force_play`, hold the clock
(`live = false`) and `seek(t)` to the frame they want.

**Moving a fighter.** The sequencer moves a FighterStandIn's root transform (travel, lean, collapse), about its
feet. It never touches the stand-in's inner mesh or actor, so the stand-in's own flinch, KO sink and fade,
Petrify, and a creature actor's phase poses compose with it. Each fighter's home is the transform the stage
placed it at; every sequence ends with everyone on their home (or their KO pose).

**Speed and motion.**
- `speed` (UiSettings `battle_speed` when that setting exists) scales every beat; it is clamped to `speeds`.
- Reduced motion scales travel (`travel_scale`) and leans (`lean_scale`), and drops the reaction tilt
  (`tilt_scale`). The beats keep their timing: the contact is still the information.

**Data:** `game/data/battle/choreo.json`, checked by `tools/validate_choreo.py` (called from
`validate_data.py`): positive strike times, contacts inside the strike, travel distances, styles that exist,
every skill kind covered, contract clips only.

## Clip contract (M2-BPR-02)

A fighter's model plays a named clip when it has one; a primitive stand-in falls back to procedural motion.
`BattleClips` (`game/battle/scene/battle_clips.gd`) looks for the first AnimationPlayer under the stand-in (a
hero actor scene, M2-UI-07, or a creature actor, M2-CRE-03). A creature actor plays through its own
`play_clip`, so it idles again after; a hero actor's one-shot queues `idle`.

| Clip | Loop | Played on | Stand-in fallback |
|---|---|---|---|
| `idle` | yes | always, between clips | none (still) |
| `ready` | no | the actor's approach beat; a fighter walking in; a heal's target | none |
| `attack` | no | `melee` strike | lunge toward the target and lean in |
| `cast` | no | `cast`, `support` strike | rise and lean back |
| `item` | no | `item` strike | a short lunge |
| `read` | no | `read` strike | a slight lean |
| `defend` | no | `guard` strike (self-targeted skills) | crouch and lean |
| `finisher` | no | `finisher`, `chant` strike (Swell techniques, Vowbound finishers) | a big lunge and rise |
| `hit` | no | a damaging hit's target, on contact | recoil and tip back |
| `dodge` | no | a missed target, on contact | sidestep |
| `ko` | no (holds the last frame) | a felled target, `ko.delay_sec` after contact | drop and tip over, then the stand-in's sink and fade |
| `victory` | yes | the party at the battle's end (M2-BPR-05) | a small hop |

- **Timing on the clip.** A strike clip should reach its contact frame at `contact_at` of its length at 1x
  speed; the sequencer plays it at the battle speed (`speed_scale`). A model clip replaces the procedural strike
  (no lunge or lean on top) but the travel still happens: the root moves, the clip animates in place.
- **Root motion.** Clips are **in place** (no root translation). Travel belongs to the sequencer.
- **Agreed with:** the characters track (`claude/characters`, heroes, M2-CHR-06 / M2-UI-07) and the creatures
  track (`claude/creatures`, CreatureActor `clip_by_kind`, M2-CRE-03); see their live logs. A creature's
  `clip_by_kind` names its own clips per skill kind; until those rows map onto the contract names, the creature
  plays its clip through BattleActorMotion and the sequencer only moves its root.

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
