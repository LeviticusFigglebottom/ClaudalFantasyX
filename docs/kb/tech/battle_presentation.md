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
| `finisher` | no | `finisher`, `chant`, `dive`, `verse`, `brace`, `glyph` strike (Swell techniques, Vowbound finishers; M2-BPR-04) | each style's own shape (see Specials) |
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
