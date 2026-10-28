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
- **A KO plays once (M2-BPR-11, the human's playtest).** Only the action that fells a target lists it in `kos`;
  refresh_ko re-applies every fighter's stone and KO state after every action, so both must be idempotent:
  `CreatureActor.set_ko` and `set_frozen` ignore a repeat (a repeated `set_frozen(false)` used to call `play()`
  and restart the finished KO clip on every later move). A fallen **foe** fades to `foe_ko_alpha` (0) and is
  hidden (no shadow); a fallen **party member** keeps `ko_alpha` (0.35) so it can be revived. A revive shows it
  again. Tests: `tests/unit/test_battle_ko_once.gd` (creature model and primitive stand-in, three later actions).
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
| `finisher` | no | `finisher`, `chant`, `dive`, `verse`, `brace`, `glyph` strike (Swell techniques, Vowbound finishers; M2-BPR-04) | each style's own shape (see Specials) |
| `hit` | no | a damaging hit's target, on contact | recoil and tip back |
| `dodge` | no | a missed target, on contact | sidestep |
| `ko` | no (holds the last frame) | a felled target, `ko.delay_sec` after contact; plays once (M2-BPR-11) | drop and tip over, then the stand-in's sink and fade |
| `victory` | yes | the party at the battle's end (M2-BPR-05), each fighter `stagger_sec` after the last | a small hop |

- **Timing on the clip.** A strike clip should reach its contact frame at `contact_at` of its length at 1x
  speed; the sequencer plays it at the battle speed (`speed_scale`). A model clip replaces the procedural strike
  (no lunge or lean on top) but the travel still happens: the root moves, the clip animates in place.
- **Root motion.** Clips are **in place** (no root translation). Travel belongs to the sequencer.
- **KO pose.** Any pose that reads as down: a fall, or a kneel or slump (the heroes' M2-CHR-07 clips kneel). A
  model with a `ko` clip is not sunk by the stand-in (its clip puts it on the ground; M2-HER-1103). A fallen party
  member holds that last frame, faint, until a revive (its optional `revive` clip, then idle; else idle); a fallen
  foe fades out.
- **Blends.** BattleClips plays by name and leaves the blend to the model's AnimationPlayer: a hero scene sets short
  per-pair blend times into its strikes (0.12–0.2 s, hero-integration M2-HER-1103) so the wind-up before an early
  contact frame isn't swallowed by the 0.3 s default.
- **Agreed with:** the characters track (`claude/characters`, heroes, M2-CHR-06 / M2-UI-07) and the creatures
  track (`claude/creatures`, CreatureActor `clip_by_kind`, M2-CRE-03); see their live logs. A creature's
  `clip_by_kind` names its own clips per skill kind; until those rows map onto the contract names, the creature
  plays its clip through BattleActorMotion and the sequencer only moves its root.
- **Part cues** (M3-C05-07, `BattlePartCues`). Model parts that battle events show and hide without a phase change,
  from `battle_sandbox.json → part_cues` per creatures.json row: the Cinder Matron's `Crust` shows when `recrust`
  lands on her or a hit on her `reacted` (her quench in the Pour), and hides when a hit adds `armor_break`. Applied on
  the action's contact beat (`BattleChoreo.contact`), hides before shows within one hit (the engine's order).
  `BattleStage`'s `choreo` setter attaches it, so a retry's new sequencer gets a fresh one. Listens only.

**Placeholder clips (M2-BPR-10).** Until the heroes' battle clips land (M2-CHR-07), `BattlePlaceholderClips`
(`game/battle/scene/battle_placeholder_clips.gd`) gives a model with a `Skeleton3D` and an `AnimationPlayer` a
generated pose clip for every contract name it lacks. `BattleClips.player_of` calls it the first time it finds the
player. The poses are data, in `choreo.json` `placeholder_clips`: per clip a `length_sec`, `loop`, and keys of
role → `[x, y, z]` degrees at times. A pose is a turn in the model's axes on top of what the bone inherits, the same
convention as the characters' `hero_clips.py`. Roles map to bone names with alternatives: the MPFB2 rig as the
characters track exports it (`DEF-spine.003`, `DEF-upper_arm.R`, ...), then MPFB2's default names. The clips are
added to the player's own copy of its default library, and **only for missing names**, so a real clip always wins and
M2-CHR-07 replaces them with no code change. A skeleton that resolves fewer than `min_roles` roles (a creature) and a
creature actor get nothing; a primitive stand-in has no player and keeps the procedural motion. A placeholder counts
as a clip everywhere (`has_clip`), so the strike's lunge and lean are skipped and the travel still moves the root.
The hero's `ko` clip now plays on the collapse beat and holds its last frame (`BattleClips.play_ko`). On a revive the
hero idles again (`ko_changed`). `tools/validate_choreo.py` checks the rows: every contract clip present, positive
lengths, key times within the clip, poses naming known roles.

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

Each story encounter fights in its own place. Its `encounters.json` row names an **`arena`**
(`tideline_dawn`, `causeway_disc_sunset`), and `game/data/battle/arenas.json` maps the id to a scene.
**`BattleArena`** (`game/battle/scene/battle_arena.gd`) applies it from `BattleChoreo.attached`, before BattleVfx
attaches, so the Drownbell's flood rig finds the arena's `Sun` (scaled to 0.6x in the Flood) and `Arena/Sea`.

**The scene contract** (agreed with env-art, whose `docs/kb/tech/battle_arenas.md` on `claude/env-art` is the
full version): a root Node3D whose children are
- `WorldEnvironment` and `Sun` (a DirectionalLight3D): they replace the battle scene's;
- everything else (dressing, extra lights, `Sea`, an optional `CameraHints` of Marker3Ds): moved under a new
  `Arena` node in place of the sandbox's. A child named `Sea` is the flat sea the flood rig hides.

The fighters keep standing on the battle scene's slot markers (party at +x, foes at -x around the origin; the
camera looks from +z). The floor under every slot is flat and clear at y = 0, nothing stands between the camera and
the fighters. A retry of the same encounter keeps the arena (the `hymn_arena` meta on the battle scene).

| Arena | Encounter | Grade (color_script.md) | Greybox (`game/battle/arenas/`) |
|---|---|---|---|
| `tideline_dawn` | `ch02_tideline` | Ch2 dawn: 06:20, sun 6° over the eastern sea, key `#FFB87B` 2.4, fill `#7FA6CC` 0.5, sky `#4E7FB8` / `#F6C9A0`, fog `#E9C9A8`, exposure 0.75 | dry sand behind the party, a wet band and rocks before the lagoon |
| `causeway_disc_sunset` | `drownbell` | Ch3: sun 6° over the western sea, key `#FFAE67` 2.6, fill `#6E8FC0` 0.4, sky `#46609A` / `#F0A35C`, fog `#D9A27A`, exposure 0.80 | a stone road along the battle axis, water both sides, leaning posts and salt-grass tufts; the flood takes the road |
| `oruvel_raft_morning` | `ch01_scuttlers`, `ch01_hullgnaw` | Ch1 10:30: sun 58°, key `#FFEFE1` 3.0, fill `#8FC3E0` 0.6, sky `#2E7FD6` / `#A9DCF2`, fog `#BFDDE8`, exposure 0.65, sat ×1.12; `lagoon_clear` sea | the net-pen hull: a lashed plank deck, the Reefball net behind the foes, the plank bridge to the keel-hull (Kell's beacon lit) behind the party, raft huts, the storm wall low on the horizon under a blue sky |
| `underway_tower` | `ch01_wickfry`, `ch01_oil_slug`, `ch01_shaft_limpet`, `ch01_underway_shoals`, `ch01_underway_limpet` | Ch1 Underway note: only Rhen's `oil_lamp` (`#FFB16E` omni by the party) and held cyan (`#7FC6D9`) points; a `deep_teal_shadow` colour background, exponential fog 0.055, a dim cyan Sun from above; no Sea | a gallery floor, a ring of pillars and lintels behind the fighters, fallen blocks and coral, the dark shaft beyond the foes |
| `causeway_route_afternoon` | `ch03_causeway_shore`, `ch03_causeway_harrier` | haluna.md `ch03_causeway` 14:30: sun 52°, key `#FFEAD8` 3.0, sky fill `#A9DCF2` 0.6, `lut_ch02_noon` (+200 K): exposure 0.65, sat ×1.12, a far haze only | low tide: a slab landing on the stone path over tidal flats, coral boulders, tidepools and salt-grass, the lagoon at the horizon |
| `derelict_deck_night` | `ch04_sail_leeches`, `ch04_bottle_hermit`, `ch04_spar_wraith`, `ch04_derelict_*` | Ch4: key `#FFB16E` lamp 1.2 (the Sun), fill `#2A4A6E` 0.2, rim `#9DB4D9` 0.5, sky `#0B1630` / `#1E2E4E`, fog `#22354F`, exposure 1.10, sat ×0.95; `night_sea` with sea-glow 0.12 | a planked deck, mainmast and foremast behind the fighters (yards and set sails above the frame), the far bulwark only (no near rail), two hung deck lamps, the ferry's lamps far off |
| `ash_terrace_lanternfall` | `ch05_stair_*`, `ch05_cinder_matron` | Ch5: key `#FFA757` lamp 1.6 (the Sun), fill `#3A4A6A` 0.25, rim `#E0702E` 0.9, sky `#101A33` / `#3A2A3A`, fog `#5A3A2E`, exposure 1.05, sat ×1.15; no Sea | a volcanic-stone terrace, four tiers stepping up behind the foes with graves and small warm lanterns on their lips, a leaf-boat channel down the steps, the mountain's cone and plume beyond |
| `brine_shoals_afternoon` | `ch06_ridge_skippers`, `ch06_ridge_crab`, `ch06_ridge_gulls`, `ch06_flats_crabs` | Ch6 15:30 haze: sun 35°, key `#FFD5B3` 2.4, fill `#A8B8B0` 0.55, rim `#E0702E` 0.35 (the far smoke), sky `#7FA3C0` / `#D8C8A8`, fog `#B8A890` (thick), exposure 0.70, sat ×0.9; `silted_flats` sea (deep `#4A5A50`) | a grey-brown mud bank with puddles, a tide channel behind the foes, wreck-ridges of black Lit Age hull plating (one with a Saltwright chalk camp-sign) and wooden hulks' ribs, gulls high over the ridges |
| `salvage_camp_burning` | `ch06_inquisitor` | the same Ch6 grade, rim 0.7, plus four steady orange fire points (`#FF8A3A`, no flicker); `silted_flats` sea at the waterline | the camp's mud bank; behind the foes the hulk the party hid in, charred and burning low along its gunwale, lashed hulls with a tide-wheel behind the party's side, lamp racks alight, three dark smoke columns of stacked billows far behind; sober: no embers, nothing falling |
| `wall_head_storm` (greybox, M3-BPR-406) | `ch08_stair_hold_1..3`, `undertows_reach` | Ch8 "The Seawall": key `#FFE4CE` 2.0 (sun 30 deg az 250), fill `#5E6E80` 0.5, rim `#CFE8FF` 1.2, sky `#3E4A57` / `#8A8070`, fog `#5E6670`, exposure 0.80, sat ×0.95; two steady watch lamps | the warm laterite wall-walk; the crenellated parapet behind everyone with the storm sea below and dark storm columns on the horizon; the Fisher Stair going down landward at the party's side, `EntryMarker_ward` at its head; Liss's hoist (rope and iron); no glow at the stair foot (Kerrid). Final kit requested: M3-BPR-407 |

- **Act I (M3-BPR-01):** the Underway's scripted fights (`ch01_wickfry`, `ch01_oil_slug`) are underwater in the
  drowned tower (act1_ch01.md C1-04, C1-06), so they take `underway_tower`, not the raft. Two grades are the
  chapter's frame, not the fight's hour: the derelict is boarded at 07:40 (act1_ch04.md C4-12) and the stair and
  anvil court are fought on day 2 at 11:30–13:40 (act1_ch05.md B07–B09); a morning-ferry and an Ashcrown-day
  sub-frame are open with Art and env-art (M3-ENV-06).

- **Env-art's kits** land at `assets/environments/arenas/<id>/<id>.tscn`; they repoint `arenas.json` then (M2-ENV-11
  / their own task). The greybox stays as the fallback until they do.
- **Unchanged:** the sandbox's own encounters and every capture fixture (`fixture_reef`) have no arena, so no
  battle baseline moved except `drownbell_flood` (now on the causeway at sunset, as battle_vfx.md's "the arena is
  the noon sandbox" asked).
- **Shots:** `battle_arena_tideline`, `battle_arena_causeway`, `battle_arena_raft`, `battle_arena_underway`,
  `battle_arena_route`, `battle_arena_derelict`, `battle_arena_terrace`, `battle_arena_shoals`, `battle_arena_camp`
  (`game/levels/_tests/battle_arenas/`; shot fixtures live under `_tests` so release builds and the game/battle
  coverage gate exclude them).
- **Ch6 (M3-BPR-03):** every light in the two Ch6 arenas sets `light_volumetric_fog_energy = 0.0` (Lead rule: the
  default 1.0 bands dense fog volumes). Env-art's Brine Shoals zone (M3-ENV-02) is the kit for the final versions.
- **Staging** (`arenas.json` `staging`, M3-BPR-01): `travel_scale` scales every run, step, walk-in and exit, `tempo`
  the battle speed. The underway tower: shorter runs (0.6) and slower (0.8); the derelict deck: shorter runs (0.85).
- **Checked by** `tools/validate_choreo.py` `arena_errors` (from validate_data): every scene exists, every
  encounter's `arena` is a known id, staging rows name known arenas with positive scales.

### Lead-in bark

An encounter with a row in `battle_transition.json` `barks.rows` shows one line ("Speaker: line",
`BARK_LINE_FMT`, the UI theme) over the rising water, holds the stinger `hold_extra_sec` longer so it can be read,
and announces it on `EventBus.dialogue_event("battle_bark", [encounter, line_key, speaker_key])` for audio (a voice
line or a stinger cue from claude/audio). `BattleRequest.submit` passes the encounter to `BattleStinger.play`.
The table ships empty: the tideline's line is Narrative's (request M2-NAR-01).

Every stinger also announces `EventBus.dialogue_event("battle_stinger", [encounter])` as the tide line starts (the
audio track's rising-water sting, M3-AUD-18).

## Specials (M2-BPR-04)

The Swell finishers, the Drownbell's set piece and the Vowbound. Everything stays a listen-only view of the
engine, moves fighters' **roots only** (a hero actor's clip or a creature actor's phase pose composes under it),
and lands at once at pacing 0 or with "skip animations".

### Generic shape fields (choreo.json styles, all optional)

| Field | What it does | Used by |
|---|---|---|
| `arc_m` | The approach rises in an arc to `arc_m` at its end (a leap; needs `approach_sec` > 0); the strike falls from that height onto the contact, faster and faster (the plunge). Root travel, so it plays under a clip too. Reduced motion scales it by `travel_scale`. | `dive` |
| `windup_m`, `windup_at` | Before the contact the actor is pushed back `windup_m` (and crouched by `crouch_m`), deepest at `windup_at` of the way to the contact, and leans back; the lunge starts only once the windup has held. | `brace`, `toll` |
| `trace_m`, `trace_strokes` | The actor sways `trace_m` side to side, `trace_strokes` strokes (a whole number), ending on the contact. | `glyph` |
| `stagger_sec` | Reactions start in hit order, `stagger_sec` apart, from the contact (their clips too). A felled target collapses after its own reaction starts. | `verse`, `glyph` |
| `wave_m_s` | Each target reacts when a wave from the actor's mark reaches it (flat distance / `wave_m_s`). | `toll` |
| `react_scale` | Multiplies the damage recoil and tilt. | `toll` |
| `shot` | A camera framing name for BattleCameraDirector (`"finisher"`, `"toll"`). The plan carries it as `plan.shot`; the sequencer itself never moves the camera. | every special |

The damage numbers and float words still land on the contact for every target (pillar 4: the result is known at
once; the motion is the read).

### Swell finishers

| Technique | Hero | Style | The read |
|---|---|---|---|
| Lamp Dive | Rhen | `dive` | A leap toward the target, rising 1.5 m, then a plunge; contact on the landing, a deep crouch and lean. |
| Shallows Verse | Asha | `verse` | A long held chant (rise and lean back); each healed ally lifts in turn, 0.2 s apart. |
| Return Tide | Toma | `brace` | Planted: he gives ground to the tide (back and down), then one counter thrust on the contact. |
| Written Light | Ysolde | `glyph` | A glyph written in the air, five strokes side to side, finished on the contact; the light reaches each foe in turn. |

All four play the contract's `finisher` clip on a model (no hero-specific clip is needed: the shapes above are
the stand-in fallback). Their rows say `"shot": "finisher"`.

### The Drownbell

- **The toll** is an ordinary action with the `toll` style: the bell rears back (`windup_m`) and lurches down on
  the toll; every party member recoils hard (`react_scale` 1.9) as the shockwave reaches it. `wave_m_s` (7.7) is
  BattleBossVfx's ring speed, boss_vfx.json `toll` (`ring_radius_m` − 0.2) / `ring_s`; a Python test fails if the
  two drift apart.
- **BattleBossVfx hook (PC GPU's file, a minimal change):** `BattleBossVfx.attach` connects its action handler
  to `BattleChoreo.contact` when the stage has a sequencer, else to `engine.action_resolved`, the same `if` as
  `BattleVfx.attach`. So the toll's ring and flash, the rim-hit cracks and the polyp mend start on the contact
  beat, and the ring passes the party as they recoil. At pacing 0 the contact is emitted with the action, as
  before.
- **BattleBossChoreo** (`game/battle/scene/battle_boss_choreo.gd`), built by `BattleChoreo.attached` when an
  enemy has a row in choreo.json `bosses` (the controller is untouched). It listens to the engine's boss signals
  and only lays **accents** (below):
  - the gather (`charge_started` for `charge_skill`): the bell sways on the gathering action's contact, then
    again at the start of each turn of the charge (not on the turn the toll fires);
  - the rim break (`charge_broken`): the bell staggers back on the breaking blow's contact;
  - the flood (`phase_changed` to `flood.phase`): once the action playing has finished, the party braces in slot
    order (`stagger_sec` apart), a short crouch leaning into the water.
  - `moments` records them (tests). A creature actor plays the bell's own phase clips; the accents only move its
    root.
- **Accents** (`BattleChoreo.accent(cid, spec, delay)`): a short overlay on a fighter's root, out and back over
  `sec`: `lift_m`/`crouch_m`, `recoil_m` and `tilt_deg` back (away from the other side; negative leans in),
  `sway_deg` side to side `sways` times, an optional contract `clip`. It composes with the fighter's own action,
  reaction or entrance. A fallen fighter takes none.

### The Vowbound (Ilun; ADR 0026/0027)

The engine's call and departure have already happened when BattleVowboundHud re-seats the stage. BattleStage
`sync_party` now hands each stand-in it takes off to `BattleChoreo.leave(cid, node)` (instead of freeing it) and
each one it places to `BattleChoreo.enter(cid)`. **BattleVowboundChoreo** (`battle_vowbound_choreo.gd`, built by
`BattleChoreo.attached`) answers what each plays, from choreo.json `vowbound`:

| Moment | What plays |
|---|---|
| The call | The caller (the row's `caller`) makes its call: an accent with the `cast` clip, a rise and lean back. Then the party walks back off the field in slot order (`step_off`: from 0.5 s, 0.12 s apart, 2.8 m back) and is freed. A fallen member goes at once. |
| Ilun's entry | After the party (`entry.delay_sec` 0.95, unseen until then), he rises 2.6 m out of the water at the Vowbound slot over 1.3 s, tipped forward and straightening. A swap's walk-in is 0.34 s. |
| The dismissal | He sinks back over 0.9 s (a battle won while he is out too), after the action playing is done with him. The party walks back in (choreo `enter`) once half of his exit has played, 0.12 s apart. |
| The fall | Struck down, he takes the blow (the reaction plays on his node), and at the blow's KO beat he tips back 38° and is drawn under over 1.5 s: not the collapse. The party returns as above. |

A swap's leaver still goes at once. `hold_after` now also waits for any entrance, exit or accent in progress
(`busy_sec`), so the turn after a call starts once Ilun is up.

### Freeze-frame captures

| Shot | Capture state | Frame |
|---|---|---|
| `battle_choreo_lamp_dive` | `choreo_lamp_dive` (CHOREO_FREEZES; a Swell technique is unleashed with a fixed perfect/good/perfect result) | Lamp Dive mid-plunge, 0.085 s before the contact. |
| `battle_choreo_toll` | `choreo_toll` | The toll 0.75 s after its contact, the age of BattleBossVfx's ring when the shot is taken (settle 45 frames at 60 fps), so the recoils and the ring agree. Party Toma, Asha, Ysolde (nobody quick enough to break the rim). |
| `battle_choreo_vowbound_rise` | `choreo_vowbound_rise` | Ilun half way up out of the water after Asha's call; the party has stepped off. |

Fixtures in `battle_fixtures.json`; the tables now carry a frozen Drownbell (its Toll phase only) and its three
skills, with encounter `fixture_drownbell`. Baselines are approved by the track lead after the camera merge.

### Tests

`tests/unit/test_battle_specials_choreo.gd`: each technique's own row and shape (the leap's top and the plunge,
the Verse's staggered lifts, the glyph's strokes and staggered foes, the brace then the counter), the toll on its
contact with the wave reaching each member in turn and BattleBossVfx's ring on the contact, BattleBossChoreo's
moments with no combat state changed, the call (step-off, the caller's beat, Ilun's rise, the hand-off), the
dismissal (the sink, the party walking back in slot order), the fall (the blow, then drawn under), instant at
pacing 0, and the three capture states. `tools/tests/test_choreo_validate.py` covers the new fields and blocks
(`tools/validate_choreo.py`).

## Ilun's first call: C10 (M2-BPR-08)

The slice's one Vowbound and its first call must be unmissable (vertical_slice.md B10, C10). **`BattleSummonCinematic`**
(`game/battle/scene/battle_summon_cinematic.gd`), attached by `BattleChoreo.attached`, gives the Vowbound's entrance
when `BattleVowboundChoreo.enter_spec` asks:
- **When:** the first call of each Vowbound in a live story battle (its `first_call_flags` seen-flag,
  `ch03_ilun_first_call_seen`, is unset; the cinematic sets it) under the accessibility setting **Vowbound calls**
  (`summon_cinematic`, the UI track's row, M2-UI-23) on Short, the default. Full plays it on every call; Off skips
  the rise (`off_entry`: the Vowbound is simply there). A capture fixture, instant pacing and "skip animations" play
  the short entry (`vowbound.entry`). The decision reads
  `UiSettings.summon_cinematic_cut` (accessibility.json `summon_cinematics`, M2-BPR-1000).
- **What:** the water stills (`entry.delay_sec` 1.4 s after the party steps off), Ilun rises slowly (2.6 s), and a
  steady bound light (`glimmer_bound`, color script C10: no flicker, no drift, no trails) fades in at his slot and
  stays while he is out. The camera eases to the low `summon` frame (camera.shots), holds, and is back on the
  default by the end (`hold_sec` after he stands). Reduced motion keeps the camera on the default. Nothing flashes.
- **Skip:** confirm or cancel ends it; Ilun stands on his mark. The controller's hand-off waits for it
  (`BattleChoreo.busy_sec` includes it).
- **The help line** says "Asha calls Ilun." while any call plays (pillar 4), not the last menu preview.
- **Shot:** `battle_choreo_summon` (the capture forces the full version). Checked by `validate_choreo.summon_errors`
  (the flag declared, the numbers, the `summon` shot).
- **Not here:** a line for Ilun or Asha (Narrative has none for C10 yet) and his face (save it for the model).

## Mouse targeting (M2-BPR-09, superseded)

The UI track's input-parity audit (M2-UI-26, ADR 0036) built mouse targeting and Swell play in battle
(`BattlePointer`, wired through the controller). This track's own picker was removed so the battle has one mouse
path; `docs/kb/tech/ui.md` and the UI track's parity tests are the reference.

For the input-parity audit (ADR 0036). The command menus already take hover and click (MenuPage's row signals);
**`BattleMousePick`** (`game/battle/scene/battle_mouse_pick.gd`, built by `BattleStage._ready`, no controller line)
adds the pick:
- In `STATE_TARGET` and `STATE_SWAP_OUT` only. Hovering a candidate's fighter (its projected body: feet to head,
  its stand-in radius wide, plus a margin; the nearest when two overlap) moves the cursor onto it; a left click aims
  and confirms. Group targets: hovering any one of them keeps the whole group; a click confirms it.
- It sends the keyboard's own actions through `BattleController.handle_input` (`ui_right` steps the cursor,
  `ui_accept` confirms), so the mouse can't pick anything the keyboard couldn't.
- Right click is Cancel: `UiInput` turns it into `ui_cancel` for every screen once it is in the tree; until then this
  helper does it.
- Non-candidates, empty space and every other state: the mouse does nothing here.
- Tests: `tests/unit/test_battle_mouse_pick.gd`. When UiInput merges, the UI track's `InputDriver` parity walk can
  drive the battle with real mouse events through the viewport.

## Boss intros (M3-BPR-02)

A boss fight opens with a short, quiet intro: the camera finds the boss, its name and an epithet show, and the first
turn follows. **`BattleBossIntro`** (`game/battle/scene/battle_boss_intro.gd`) is built by `BattleChoreo.attached`
(one line; the controller is untouched) and listens to the engine's first `turn_started`.

**When.** An encounter with a row in `choreo.json → boss_intro.rows`: Hullgnaw (`ch01_hullgnaw`), the Bottle Hermit
(`ch04_bottle_hermit`), the Spar-Wraith (`ch04_spar_wraith`), the Cinder Matron (`ch05_cinder_matron`), Inquisitor
Hadric Moll (`ch06_inquisitor`, M3-BPR-03) and the Drownbell (`drownbell`). Once per battle.
- **Sequenced, never on top of anything.** At the first turn it waits while the router's fade covers the screen
  (`SceneRouter.is_busy`) and while the opening banner is pending or showing, at most `reveal_wait_max_sec`. The boss
  encounters open `normal`, so in practice no banner shows; the order is still fixed.
- **Fight again** rebuilds the engine on the same controller; the intro plays again only when the row says
  `on_retry` (every row says false). The controller's meta `hymn_boss_intro_played` remembers the encounter.
- **Instant** at pacing 0 and with "skip animations"; `force_play` overrides that (its capture).

**What** (all times data; the battle speed scales them):

| Beat | When | What happens |
|---|---|---|
| in | 0 → `camera_in_sec` | The camera eases from the default to the row's `shot` (`boss`, or `boss_tall` for the Matron and the Drownbell), placed on the boss's slot like any placed shot: a low 3/4 view from the party's side, on the viewer's side of the axis. |
| card | from `card_at_sec`, in over `card_in_sec` | The title card fades in (and rises `rise_px`). |
| hold | `hold_sec` (per row) | The boss holds the frame; the card is fully shown. The card fades out over `card_out_sec`, ending as the camera turns home. |
| home | the last `camera_out_sec` | The camera eases back to the default and stands exactly on it at the end. |

- **The shot is checked**: the boss's feet and head must sit in the camera's `safe_frame` (as every director shot);
  a shot that fails keeps the default for the intro and only the card plays. A test checks every row passes.
- **Fit to the model (M3-BPR-404; the human's playtest: Hullgnaw framed too close).** The shot keeps its angle and
  fov, but its distance fits a sphere around the boss's visible meshes (their AABB in camera-parent space) in the
  narrower field of view at `boss_intro.fit.margin` (1.05), clamped to `min_m`..`max_m`, aimed `look_drop` (0.3)
  of the radius below the centre. The boss's top and bottom must pass the safe frame **and its feet must clear the
  title card's top edge** by `card_clear_px` (a small boss framed close, the Inquisitor's capsule, and the Matron's
  base sank behind the card). To get there it first aims lower (`drop_step` up to `drop_max`, which lifts the boss
  in the frame), then widens (× `widen_step` up to `widen_max`); the closest pose that holds wins. If none clears
  the card, the closest that passes the safe frame; if none passes, the default camera. A row's `fit_margin`
  overrides the margin; `fit: false` keeps the shot's own offsets.
- **The title card** is its own `CanvasLayer` (`card.layer` 2, above the HUD, below the router's fade) in the HUD's
  current theme: the name in `TitleLabel` over a thin `focus_gold` rule and the epithet in `FlavorLabel`, on a dark
  band that fades at both ends (art/ui.md §9 contrast). It sits centre-low (`card.rect` 560, 616, 800 × 140 at the
  1920 × 1080 reference), under the framed boss's feet and clear of the timeline, the party panel, the help line,
  the target info and the opening banner (tested). Text: `BOSS_TITLE_*` and `BOSS_EPITHET_*` (strings.csv), drawn
  from the story beats and the bestiary lore: *Storm-born, caged in a drowned ship's ribs*; *It keeps house in the
  old lamp glass*; *It hauls a dead ship's lines*; *Woken by the anvil's ring*; *It still rings for the drowned*.
  The Inquisitor is a living officer of the Order, not a monster (act1_ch06.md B03, §5): his card is his name and
  rank, *Inquisitor Hadric Moll*, over *A tired officer who still believes the Edict* (Narrative may refine). His
  encounter's opening prompt (`TUT_CH06_HOUND`) is hidden while the intro plays and shows after it; Toma's
  first-turn bark (`turn_prompt_key`) still shows on his first turn (tested). Shot: `battle_boss_intro_inquisitor`.
- **Original staging.** A slow ease to a still frame and a fading card: no screen break, no spin, no flash, no
  name plate sweeping in, no letterbox bars.

**The first turn waits.** While the intro waits or plays, `BattleHud.holds_battle()` is true through a new generic
hook, `BattleHud.holds` (name → Callable; the intro registers `boss_intro`, a retried battle's replaces it, a freed
owner holds nothing), so `BattleController.tick` holds its first wait: an enemy's think time never runs under it.
A party first turn's command menu, help line and actor marker are hidden by modulate (the controller's own
visibility is untouched) and come back when it ends; the timeline and party panel stay. While it holds, the intro
takes every input (`_input`): **confirm or cancel skips it** (the card goes, the camera is home at once), the rest is
dropped.

**Accessibility.** Reduced motion keeps the camera on the default (as the director and the summon do) and the card
only fades, no rise. Nothing flashes.

**Data:** `choreo.json → boss_intro` and two shots in `camera.shots`, checked by `validate_choreo.boss_intro_errors`
(from `validate_data`): real encounters listing the row's enemy, known shots, `hold_sec` > 0 with room for the card's
fades, loc keys that exist, a boolean `on_retry`, the card's numbers.

**Tests and shot.** `tests/unit/test_battle_boss_intro.gd` (rows and keys, every boss framed, the card's place, the
first turn waits and nobody acts, the fade and banner waits and the cap, confirm skips, instant pacing and skip
animations, reduced motion, the camera home, retry, no row no intro); `tools/tests/test_choreo_validate.py`.
Shot `battle_boss_intro_hullgnaw` (`game/battle/scene/shots/boss_intro_shot.gd`, a live-data fixture like the arena
shots: Rhen alone against Hullgnaw, the intro forced and frozen half way through its hold).

**Open.** No sound cue yet (Audio may hang a sting on the intro's start); the stand-ins stand still under it, and a
creature actor could play a `ready` or roar clip at the hold when the creatures track has one.

- **Audio hook (boss intros):** as an intro starts it announces `EventBus.dialogue_event("boss_intro",
  [encounter_id, title_key])`, the same channel as the stinger's `battle_bark`, so audio can play a sting.

## Impact: battle feel (M3-BPR-401)
The human's note: battles looked primitive. `BattleImpact` (`game/battle/scene/battle_impact.gd`, a child of
BattleChoreo, listen-only) adds weight on the contact beat. Every number is in `choreo.json` `impact`.
- **Strength.** A hit's weight, 0..1: its damage over the target's max HP, 1 at `full_frac` (0.35); a crit adds
  `crit_bonus`. A miss or a heal is 0. BattleChoreoPlan stores each damage reaction's `weight` and the plan's peak
  `impact`.
- **Hit-stop.** From `heavy_strength`, the contact holds the choreography clock and the actor's and targets' clips
  for `hit_stop_frames` [2, 4] (lerped by strength) at `stop_fps` 60, divided by the battle speed. A seek (a
  freeze-frame) carries none.
- **Shake.** From `shake_min_strength`, `BattleStage.shake(speed, scale)` at `shake_scale` [0.6, 1.6] of its base
  amplitude. The old crit-only shake now runs only for instant pacing (BattleFloats with no sequence).
- **Flash.** A warm OmniLight3D pulse at the hardest-hit target (`flash`: colour, energy [lo, hi] capped at
  `energy_cap`, range, height, `sec` back to dark, eased out). Never a screen flash; fog energy 0 (the fog rule). On
  a held clock it follows the choreography time, so freeze-frames are deterministic.
- **Recoil.** Each damage reaction's recoil and tilt scale by `recoil_scale` [0.75, 1.45]; a model that plays its own
  hit clip still gets `reaction.damage.clip_recoil_k` (0.5) of the root push under it.
- **KO slow-mo.** The blow that fells the last foe slows the clock to `ko_slowmo.factor` (0.35) for `sec` from
  `lead_sec` before the collapse.
- **Hand-off.** `BattleChoreo.remaining_sec` adds `BattleImpact.extra_sec` (the coming hit-stop and the rest of the
  slow-mo), so the controller waits for the stretched sequence.
- **Reduced motion.** No shake (`reduced_motion.shake_scale` 0), the flash at `flash_scale` 0.5, a gentler slow-mo
  (`slowmo_factor` 0.6). Hit-stop stays: it is a pause, not motion.
- **Screen shake setting.** Every battle shake (BattleStage.shake, so BattleFloats' too) scales by the
  accessibility row `screen_shake` (Full 1, Half 0.5, Off 0) and is 0 under Reduced motion
  (`BattleStage.shake_setting`).
- **Damage numbers** already pop (6% in 80 ms) and ease out on the rise (DamageNumber, the UI track's, to
  docs/kb/art/ui.md §5); they land on the contact beat. Element particles on contact are the PC track's BattleVfx.
- **Audio hooks (listen-only).** `BattleImpact.landed(target_id, strength, stop_sec)` fires on each contact with
  weight (the hardest-hit target, 0..1, the hit-stop in real seconds). `slowmo_planned(from_sec, sec, factor)`
  fires when a sequence will fell the last foe. Audio layers an impact by weight and a KO swell on them
  (request M3-BPR-405).
- **Tests:** `tests/unit/test_battle_impact.gd`; data checks `tools/validate_choreo.py` `impact_errors`.

## Spacing: no overlaps (M3-BPR-402)
A melee run used to stop a fixed `stop_short_m` short of the target's centre, so a big creature (the Drownbell,
radius 0.85) or the lunge put the actor inside it. `BattleChoreoPlan.melee_gap` now also stops it so that, at the end
of its lunge, the actor keeps its radius + each body's radius + `spacing.clearance_m` from every living fighter in
its path (a body off the path changes nothing). A radius is the model's real footprint (`BattleChoreoPlan.footprint`:
the mean of its visible meshes' half-width and half-depth about the stand-in's origin, times `footprint_k`; the eel
about 0.5 m, the gull harrier about 1.0 m), else the primitive's `stand_ins` radius. The test samples a
hero on a creature and a creature on a hero across the whole sequence and asserts no two footprints overlap. With
the real hero rigs (claude/hero-integration) the footprint comes from their meshes too. **Open:** the enemy line-up
slots were sized for the primitives, so some real models overlap each other on their marks (the reef crab and the
gull harrier); a run never brings an actor closer to such a body than it started. Spreading the slots by footprint
is M3-BPR-403.
- **Detour.** A body *beside* the path (the gull harrier's wings next to the reef crab) used to stop the run short:
  Rhen struck the air 2.9 m from the crab. `BattleChoreoPlan.melee_approach` now tries the straight line first.
  If something other than the targets stops it short, it turns by `spacing.detour_step_deg` each way, up to
  `detour_max_deg`, and takes the smallest turn whose run ends within `detour_reach_m` of where an unobstructed run
  would. So the actor comes at the target a little from one side and still meets it. Test:
  `test_a_body_beside_the_path_turns_the_run_instead_of_stopping_it`.

### The opening line-up (M3-BPR-403)
The slot markers were laid out for primitive stand-ins, and real models overlapped on their marks (in sandbox_reef
the reef crab and the gull harrier stood 1.92 m apart against 2.45 m of footprints and clearance). At spawn,
`BattleLineup` (`game/battle/scene/battle_lineup.gd`) pushes each side's fighters apart on the ground in fixed pair
order, `spacing.lineup_iters` passes, until every pair keeps both footprints + `clearance_m`. It pushes only
sideways on screen (along the battle camera's horizontal), because a first try along the pair's own axis moved the
reef crab toward the camera and behind the command menu. Each fighter moves at
most `lineup_max_shift_m` (0.6) off its mark, which keeps the camera's safe frames valid. It runs only at spawn,
before BattleChoreo caches each fighter's home; fighters who join mid-battle keep their marks.
Test: `tests/unit/test_battle_lineup.gd` (every encounter's opening line-up; it fails with the spread off).

## Set pieces on stage (M3-BPR-406, ADR 0100)
Ch8's evacuation battles (docs/kb/design/set_piece_battles.md) add things the stage had never seen.
- **Entries** (the Climb, the Surge, the Kirru) have no fighter. Their turns plan and play with no actor body
  (tested: all four Ch8 encounters play to their result panel through the controller at full pacing,
  `tests/unit/test_battle_set_piece_stage.gd`). UI draws their timeline glyphs (set_piece_battles.md §8 request 1).
- **Withdrawals** (`BattleCombatant.withdrawn`: Pell's Storm-Call, the foes left when an objective ends) used to
  leave the foe standing. BattleStage.refresh_ko knew only HP 0 and yielded. The foe now backs away from the party by
  choreo.json `withdraw.back_m` over `sec` and is hidden, with no KO collapse; it is not a death. Reduced motion or
  instant pacing hide it at once.
- **Counters** (`counter_by` on an appended hit). The planner used to skip any hit on the actor, so the riposte
  showed nothing. Now:
  - the countering hero plays its attack clip `counter.delay_sec` after the blow's strike;
  - the attacker's reaction (clip only, so it keeps its run) lands on that clip's contact frame;
  - an attacker felled by the riposte collapses once it is home.
- **Intercepts** (`ActionResult.intercepted_by`). The engine already aims the ward skill at the guard, so the foe
  runs at Toma and strikes him. Showing the intercept in words is UI's (§8 request 3).
- **The Reach** has a boss intro row (W18: `boss_skyward`, low and looking up; shot battle_boss_intro_reach).
- **The Breach closes in.** While a foe gathers a skill named in `camera.pressure` (`breach` over 4 turns,
  `hand_closes` over 2), the camera's resting frame narrows by up to `max_fov_deg`, a step each turn as the charge
  counts down (BattleCameraDirector.rest_fov). It reads as a closing clock (Pillar 4). Reduced motion keeps the
  plain default.
- **Still to do** (task M3-BPR-406): the intercept step-in, which needs EntryMarker_ward on the Ch8 arena
  (request M3-BPR-407 to env-art); a look for untargetable or damage-immune phases; freeze-frame shots.

## Barks (M3-C08-100)
A few skills and calls say one short line over the speaker's head. `BattleBarks` (`game/battle/scene/battle_barks.gd`,
listen-only, a node under the battle HUD that the controller attaches; see ui.md "Battle barks") reads the rows:
- skills.json `bark_key`: the skill's user says it as the skill resolves.
- vowbound.json `call_bark_key`: the caller says it as the Vowbound is called.

The line pops as a float (BattleHud.pop_info) at the speaker's head, and `barked(speaker, key)` fires for audio's
voice blips. Ch8's (act1_ch08.md B05): Toma's "Hold." on Hold the Stair, Liss's "Pull!" on Haul, Asha's "Virel." on
the call. Flare Line and Virel say nothing. Keep them rare: a bark marks a moment, not every swing. (big13: the
battle-presentation and ui-menus tracks both built this; the merge kept ui-menus' data-on-the-rows version and
battle-presentation's `barked` signal, and dropped choreo.json `barks` and its BARK_CH08_* keys.)

## Act II boss intros by enemy id (M3-BPR-408)
`boss_intro.by_enemy` gives a boss its intro wherever it first appears, for bosses whose encounters are not written
yet (the Lamp Engine `boss_tall`, the Avalanche Ram `boss`). An encounter's own `rows` entry wins
(`BattleBossIntro.row_for`).

## Filling the staging audit (M3-BPR-416)
- **Foes stage their blows by their reach.** In `style_by_skill`, a ranged or whole-party blow (Brine Spit, Shroud
  Sweep, Undertow Pull) plays `cast`, so the foe stays in place instead of running at one hero. The heaviest blows
  (Gnaw, Ladle Swing, Pounce) play `finisher`. A creature plays its own clip by kind either way; the style sets the
  travel, timing and shot.
- **`reaction.push`.** A landed hit with no HP change and `delay_ticks > 0` staggers its target back (recoil and a
  small tilt, the hit clip at `clip_recoil_k`). Damage still wins. The ward now visibly takes Rope Dive.
- **Summoned foes walk in.** `BattleStage.add_enemy` plays the `enter` walk for every foe that joins mid-battle.
- **`tools/battle_vfx_coverage.py`** lists, for each skill or item with no effect, its stage answer (`staged`). The
  particle itself is rendering's (request M3-BPR-411).

## Phase looks and set-piece freeze-frames (M3-BPR-406)
- **BattlePhaseLooks** (a node under the sequencer): on each phase change and turn, a living foe that is untargetable
  fades every surface (GeometryInstance3D.transparency, model or primitive) to `phase_looks.untargetable.alpha`, and
  comes back when the phase ends. The Reach's Breach reads as out of reach.
- **`reaction.immune`**: a blow (physical or magical, with power) on a damage-immune foe stops dead: a sideways
  shudder, no recoil, no tilt, and still under reduced motion.
- **Freeze-frames** (`shots/set_piece_beat_shot.gd`, the real Ch8 wave): `battle_ch08_intercept` (the crawler's grip
  lands on Toma, who covers the stair), `battle_ch08_counter` (Rhen's riposte lands), and `battle_ch08_withdraw` (a
  crawler half-way back). The stage keeps a withdrawal's tween on the stand-in (`WITHDRAW_TWEEN_META`) so a capture
  can hold it.

## Act II, next bosses (M3-BPR-418)
- `boss_intro.by_enemy` also has the Mangrove Drowner (`boss_tall`) and the Wakefin (`boss`).
- `bosses.mangrove_drowner.phases.uprooted`: the Drowner tears free of its tree and stands on its roots (a lift and a
  rock while its own clip plays; the party braces in turn). Same machinery as the Lamp Engine's `opened`.
- The Act II boss arenas are env-art's final kits (`ossa_fen_roots`, `lowlight_engine_hall`, `keth_seep_terrace`,
  `bridal_barge_night`). Encounters name them in `arena` (request M3-BPR-419).
