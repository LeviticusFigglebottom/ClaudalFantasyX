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

## Victory and escape (M2-BPR-05, part 2)

**`BattleOutro`** (`game/battle/scene/battle_outro.gd`), a child of the sequencer, listens to
`engine.battle_finished`. It waits for the last action's choreography (`after_sequence`), then:
- **Victory:** every standing party fighter plays `victory` (the clip contract), or a stand-in hops `hops` times
  `hop_m` high over `sec`, each one `stagger_sec` after the last, after `delay_sec`. It stands back on its mark
  at the end. A looping `victory` clip carries on under the result panel.
- **Escape:** the party walks `back_m` back off the field over `sec` and stays there under the result panel.
- **Defeat:** nothing more; the KO collapses already told it.

`BattleController` holds the result panel `BattleStage.outro_hold(result_delay)`: the base delay, or the last
blow's rest plus the outro plus `outro.settle_sec`. That is an in-place change to the two `result_delay_sec`
waits; the controller is still 995 lines. Instant pacing and "skip animations" skip the outro.

**Return to the field.** The result panel's Return goes back through SceneRouter's opaque fade, as before.
The field's own arrival is the field camera's business (field_camera.md), so nothing new plays here.

**Data:** `choreo.json` `outro` (validated with the rest of the file).

## Camera director (M2-BPR-03)

**`BattleCameraDirector`** (`game/battle/scene/battle_camera_director.gd`) frames each action on `%BattleCamera`.
- **Listens only.** `BattleChoreo.attached` builds it under the sequencer (`c.camera = BattleCameraDirector.attached(
  controller, c)`); the controller is untouched. It follows the sequencer's `posed(t)` (emitted after every pose
  of a sequence) and `sequence_finished`, and writes only the camera's `transform` and `fov`. BattleStage.shake()
  still tweens `h_offset`, which composes on top.
- **The default** is the camera's authored transform and fov, stored on the camera (meta
  `battle_camera_default`) at the first attach, so a retry mid-shot still returns to the authored frame.

**Shots** (`choreo.json → camera.shots`):

| Shot | Anchor | Used for |
|---|---|---|
| `default` | the authored camera | the readable wide; every sequence starts and ends on it |
| `actor` | the actor's mark | a party melee, item, read or guard: behind the actor's shoulder, 3/4 toward the foes |
| `target` | the targets' middle | a party action's contact (melee, cast, read, finisher, chant): the target(s) with the actor at its strike point |
| `cast` | the actor's mark | cast, chant, support: lower and wider |
| `finisher` | the actor's strike point | finisher: closer, a wider lens |
| `push` | the default | every enemy action: a gentle push and turn toward the target, nothing more |

- **One axis, never crossed.** Placed shots are built off the battle axis taken from the authored default
  (party → foes is the default's screen-left): `back_m` behind the anchor along it, `side_m` toward the default
  camera's side (always ≥ 0, checked), `up_m` up, looking at `look_at` of the way from the actor's mark to the
  targets, raised `look_up_m`. So the party stays screen-right and the foes screen-left in every frame, the
  camera never rolls (look-at with world up), and there is no orbit or sweep around the party: a shot is a
  short eased dolly between fixed framings.
- **Per style** (`camera.by_style`): a lead shot (approach and strike) and a contact shot (`""` holds the lead).
  Enemy actions use `camera.enemy`. Clarity first: an enemy turn is the player's to read, not a showcase.
- **Safe frame.** When a sequence starts, each shot is checked at the design aspect (the project viewport, so
  tests, captures and play agree): every target's feet and head must sit inside `safe_frame` (screen fractions
  kept clear for the timeline on the right and the party panel at the bottom), and the actor's head at its strike
  point must be on screen. A shot that fails becomes the default for that sequence (`shot_ids` says which shots
  framed it).

**Timing, and the clock.** The camera is a pure function of the plan and its plan time
(`BattleCameraDirector.frame_at(t)`, `BattleChoreo.time()`): eased weights blend default → lead over
`blend_in_sec`, → contact over `to_contact_sec` ending on the contact, and → default over `blend_out_sec`, ending
**exactly on the sequence end** (held at least `hold_contact_sec` after the contact). Position, look-at point and
fov blend; the basis is rebuilt with world up. So:
- `seek(t)` gives the same frame every time (freeze-frame captures), and the battle speed only changes the pace.
- The default is back when the sequence ends; `BattleController.after_action` waits the sequence plus
  `settle_sec` before the next command menu opens, so input never starts on a moving or framed camera (pillar 4).
- With pacing 0 (tests, captures) or skip animations no sequence plays and the camera never leaves the default.

**Accessibility** (`game/data/ui/accessibility.json`, rows appended at the end):
- `battle_speed` (0.75, 1.0, 1.5, 2.0; default 1.0): BattleChoreo `speed`, inside `choreo.json speeds`.
- `battle_animations` (`full`, `skip`; default `full`): `skip` lands every action at once (BattleChoreo `skip`).
- **Reduced motion keeps the camera on the default** (no travel and no cuts) — chosen over cutting to a still
  framing, because a cut is itself a jolt and the default already shows everyone. The shake is already off under
  reduced motion (BattleFloats checks `animations_enabled()`). The director draws nothing, so it adds no flash.
- There is no accessibility settings screen yet (only the graphics menu), so no screenshot lists these rows.

**Known limits.** Damage numbers spawn at the target's screen position on contact while the camera may still be
blending; they rise in screen space, so they drift a little from the target during the out blend. The safe frame
is checked on the key shots; blends between two passing shots stay between them and are sampled by the tests.

**Data:** `choreo.json → camera`, checked by `tools/validate_choreo.py` (`camera_errors`): the five named shots
exist, anchors are known, placed shots carry back/side/up and stay on the viewer's side, fovs in range, every
choreography style has a lead/contact pair naming real shots, times ≥ 0, safe-frame margins in [0, 0.5).
Tests: `tests/unit/test_battle_camera_director.gd`.

## Arenas (M2-BPR-07)

Each story encounter fights in its own place. **`BattleArena`** (`game/battle/scene/battle_arena.gd`) reads
`game/data/battle/arenas.json` (`by_encounter` → `scenes`) and moves the children of the arena's scene into the
battle scene, each replacing the node of the same name (`WorldEnvironment`, `Sun`, `Arena`) or added beside them
(the causeway's cool `Fill`). `BattleChoreo.attached` applies it before BattleVfx attaches, so the Drownbell's
flood rig finds the arena's `Sun` (scaled to 0.6x in the Flood) and `Arena/Sea` (the flat sea it replaces). A
retry of the same encounter keeps the arena (the `hymn_arena` meta on the battle scene).

| Arena | Encounter | Grade (color_script.md) | Greybox |
|---|---|---|---|
| `tideline_noon` | `ch02_tideline` | ch02_noon: sun 74°, 3.2, exposure 0.65, saturation 1.12; the lagoon sky | dry sand behind the party, a wet band and rocks before the lagoon |
| `causeway_dusk` | `drownbell` | Ch3: sun 6° over the western sea, key `#FFAE67` 2.6, fill `#6E8FC0` 0.4, sky `#46609A` / `#F0A35C`, fog `#D9A27A`, exposure 0.80 | a stone road along the battle axis, water both sides, leaning posts and salt-grass tufts; the flood takes the road |

- **Unchanged:** the sandbox's own encounters and every capture fixture (`fixture_reef`) have no row, so no
  battle baseline moved except `drownbell_flood` (now on the causeway at sunset, as battle_vfx.md's "the arena is
  the noon sandbox" asked).
- **Shots:** `battle_arena_tideline`, `battle_arena_causeway` (`game/battle/arenas/shots/`).
- **Final kits:** env-art, M2-ENV-11 (the contract is in that task). The tideline's sand albedo is darker than the
  sandbox's: under the ch02_noon key (k 2.1) the sandbox's pale sand blew out.
- **Checked by** `tools/validate_choreo.py` `arena_errors` (from validate_data).
