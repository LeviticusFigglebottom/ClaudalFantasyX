# UI and Battle HUD: How It Is Built

Owner: UI/UX + Combat (M1-UI-01, M1-CMB-01, M1-UI-02). Art rules: [`docs/kb/art/ui.md`](../art/ui.md). Battle rules: [`docs/kb/design/battle_ctb.md`](../design/battle_ctb.md).

## Files

| Path | What it is |
|---|---|
| `game/data/ui/theme.json` | The theme recipe: palette roles (swatch + alpha), line weights, chamfers, fonts, and the type variations. |
| `game/ui/theme/hymn_theme_builder.gd` | Builds the `Theme` from `theme.json` and `docs/kb/art/palette.json`. |
| `game/ui/theme/hymn_theme.tres` | **Generated.** Never hand-edit it. `tests/unit/test_ui_theme.gd` fails if it drifts from the builder. |
| `game/ui/theme/tide_notch_style_box.gd` | `TideNotchStyleBox`: the panel recipe (gradient, sheen, inner rule, gold frame, chamfers, lamp-nodes). |
| `game/ui/shaders/lamp_mote.gdshader`, `scrim.gdshader` | The breathing focus dot and the result-screen vignette. |
| `game/data/ui/battle_hud.json` | Every HUD rect, pitch, timing and pacing value, at the 1920 × 1080 reference. |
| `game/ui/battle/` | HUD components (below) and `battle_hud.tscn`. |
| `game/data/ui/battle_sandbox.json` | Sandbox roster, encounter, seed, greybox stand-in shapes and colors, ring metrics, the stone look and the camera shake. |
| `game/data/ui/accessibility.json` | The accessibility settings (ids, types, options, loc keys), the colorblind palette overrides and the reduced-motion numbers. |
| `game/ui/settings/ui_settings.gd` | `UiSettings`: the settings layer the future settings menu calls (§ Accessibility below). |
| `game/data/ui/battle_fixtures.json` | Frozen battle tables and per-state setups for the HUD captures (§ Capture fixtures below). |
| `game/battle/scene/` | `battle_sandbox.tscn`, `BattleController`, `BattleStage`, `BattleMenus`, `BattleFixture`, `FighterStandIn`, `ground_ring.gdshader`, and `shots/` (capture entry scenes). |
| `assets/fonts/` | Source Sans 3 and EB Garamond, each with its `OFL.txt`. |

## Theme

Regenerate after editing `theme.json` (or a UI swatch in `palette.json`):

```bash
godot --headless --path . --script res://game/ui/theme/build_theme.gd
```

- **Palette roles live in the theme**, as colors of the theme type `Hymn`. Code reads `get_theme_color(&"focus", &"Hymn")` and never hard-codes a color. Constants in that type (`line_px`, `focus_px`, `chamfer_px`, and so on) do the same for metrics. Petrify uses `stone` (`coral_stone_weathered`) and `stone_crack` (`volcanic_stone`).
- **Panels** are `TideNotchStyleBox`, a scripted `StyleBox`. It draws the vertical gradient with vertex colors, the 24 px top sheen, the 1 px inner rule inset 3 px, the 1 px gold frame, and 45° chamfers on the top-left and bottom-right corners only (6 px on `PanelSmall`), each with a lamp-node. Lines are drawn unantialiased at half-pixel offsets, so they stay crisp. Buttons, the cursor and the focus frame use `StyleBoxFlat` with `corner_detail = 1`, which turns a radius into the same 45° cut.
- **Type variations:** `TitleLabel`, `BannerLabel` and `HeaderLabel` (serif; small caps through `smcp`), `BodyLabel`, `MenuLabel`, `HudName`, `HudNumber` and `RankLabel` (tabular figures, `tnum` + `lnum`), `SmallLabel`, `HelpLabel`, `FlavorLabel`, `DimLabel`, `DamageNumber` / `DamageNumberCrit` (outlined), `FloatText` (28 px outlined words over the field) and `BadgeNumber` (22 px outlined counts, such as Doom), `CommandButton`, and `PanelSmall`.
- The theme is **not yet the project default**: each UI scene sets `theme` on its root (`battle_hud.tscn`). The Lead can register it with `gui/theme/custom="res://game/ui/theme/hymn_theme.tres"` in `project.godot`.

### Fonts (SIL OFL 1.1, both unmodified, rows in `assets/PROVENANCE.md`)

| Role | Family | Files | Source |
|---|---|---|---|
| Display serif (titles, headers, names) | **EB Garamond** 0.016 (Georg Duffner) | `EBGaramond12-Regular.otf`, `-Italic.otf` | Ubuntu `fonts-ebgaramond` 0.016+git20230418-2 |
| UI sans (menus, HUD, help, numbers) | **Source Sans 3** 3.052 (Adobe) | Regular, Medium, Semibold, Bold, It | Ubuntu `fonts-adobe-sourcesans3` 3.052+dfsg-2 |

Cormorant Garamond, art's first choice, is not packaged on the reachable archive (GitHub and Google Fonts are blocked here), so we use art's documented fallback serif. EB Garamond has a larger x-height than Cormorant, so it holds up at the 28 px header size. Its Bold in this release is incomplete (43 KB), so "SemiBold" headers use `FontVariation.variation_embolden`. The total is 2.3 MB. System font fallback is off in the `.import` files, so captures don't depend on host fonts.

## HUD components (`game/ui/battle/`)

Every component is a view: it reads `BattleCombatant` / `TurnEntry` data and never writes it.

| Class | Responsibility |
|---|---|
| `TurnTimeline` + `TimelineChip` | 16 slots (`CtbTimeline.PREVIEW_LENGTH`). `show_turns(current, base, preview, targets, color, mode, full_preview)`. The pure `build_slots()` keys each turn as `<id>#<turn index>` (stable across previews and real turns, via `note_turn_taken`), marks the ghost (the actor's next turn), and sets `moved` (▲/▼) **only for the actor and its targets**. Everyone else just slides; arrows on all 15 chips buried the two that matter. With `full_preview` the preview is a whole order from slot 0 (`BattleEngine.preview_swap`): the entrant can take slot 0, and turns that were not in the base order get no arrow. Allies have a square edge and square portrait; enemies have a chevron edge, a diamond portrait and a `ui_danger` name. Skipped (Stop/Sleep) turns are hatched and dimmed, and targeted turns carry a ring mark. A Doomed turn shows the hourglass glyph and its count (`TurnEntry.doom`); the count runs 3, 2, 1 down the fighter's chips and then the fighter has no more. **The chip acting now** has a 3 px focus frame, a 6 px `focus_glow` halo outside it, and a caption under the name: "Acting now", or "Berserk: acts alone" / "Confused: acts alone". One tween per chip is killed and restarted on every new layout. |
| `PartyPanel` + `PartyRow` + `HudGauge` | Active fighters only, each with a 40 px tinted portrait square. HP/MP numbers are tabular. Low HP (< 25%) turns `ui_danger` **and** hatched. A status strip holds up to 6 `StatusGlyph`s; Doom adds its count beside the hourglass, and Regen on a Zombie draws inverted. **Petrify** turns the portrait to stone (`stone` fill, `stone_crack` strata lines and frame), dims the name and HP, and leaves the HP number as it was (stone keeps HP). **The current actor's row** gets a raised fill, a 4 px focus bar on the left edge and a ▶ mark; the ▶ is hollow when Berserk/Confuse plays the turn. An ally target gets a full focus frame. |
| `CommandMenu` + `MenuPage` | A stack of pages. Root: Attack, Skills, Escape, Swap (always last). The right column shows MP (dim) and rank (`R3` and up in `ui_swell`). Sub-menus size to their rows, sit bottom-aligned at x = 552 and slide 24 px in; the page below dims its text but keeps its cursor, so the path stays readable. Input comes from `handle_input(event)` (`ui_up/down/accept/cancel`, so keyboard and controller come free) and from mouse hover and click. It emits `highlighted`, `chosen` and `cancelled`, and decides nothing. |
| `TargetCursor` | Chevrons over targets (danger for foes, focus for allies), the target info panel (name, statuses, and HP for allies; foes show "HP unknown until Read" until M1-CMB-03), and **the acting fighter's marker**: a 34 px focus diamond with a 2 px gold frame, lifted 30 px over the head on an 18 px stem, with the breathing mote as a halo *behind* it (it used to be an 18 px diamond under the mote). On an automatic turn it is hollow with a dashed stem. **Provoke:** a fish-hook glyph on a dark plate hangs over the provoker for the whole Provoked turn, and a chevron the cursor is locked to gets a solid bar over it. **Reflect:** when the chosen target would bounce the spell, a dashed gold arc with an arrowhead and the Reflect glyph (on a dark plate) runs from it to the real recipient, which gets an outlined chevron. |
| `StatusGlyph` | Original vector icons on a 48-unit grid with a 2-unit stroke, **one distinct silhouette per status (all 21)**, so none depends on hue. Polarity is coded twice: buffs are `ui_focus` on a round backing, ailments `ui_danger` on a diamond backing (tint 0.35). The M1-CMB-02 shapes: Petrify a rock with two strata lines, Berserk a zigzag of teeth, Confuse an inward spiral, Doom an hourglass with caps, Zombie a diagonal cross (Regen's plus turned over) with a centre dot, Reflect a mirror line with a bouncing chevron, Provoke a fish hook. Regen under Zombie draws `inverted`: a bar with a downward chevron, as an ailment. All four Breaks share a crack stroke. `has_shape()` lists them; a test asserts every status in `statuses.json` has one. |
| `DamageNumber`, `BattleResultPanel`, `LampMote`, `BattleHud` | The pop-and-rise numbers, plus `KIND_INFO` float text ("Reflected", "Heal turns to harm", "Regen turns to harm", "Doom") in the 28 px outlined `FloatText` style; the victory, defeat and escape screen (scrim, title, per-fighter XP and movement rows, choices); the cursor dot; and the scene root, which owns the help line (it wraps to a second line only when one line cannot hold the text) and applies `UiSettings`. `help_history` keeps the last 16 help lines for tests. |

## Battle sandbox (`game/battle/scene/`)

`BattleController` (the root of `battle_sandbox.tscn`) is the only glue. It calls `setup`, `begin`, `preview`, `perform`, `swap`, `escape`, `run_enemy_turn` and `xp_awards`, plus `engine.timeline.predict()` for the "failed escape" preview, and it listens to `action_resolved`. It never writes combatant state.

- **States:** `command → skills → target`, `command → swap_in → swap_out`, `busy` (enemy turns, automatic turns and post-action holds), and `result`.
- **Swap preview:** hovering a reserve member in `swap_in` shows the order after that member replaces the acting fighter, and `swap_out` shows it for the highlighted leaver, both from `BattleEngine.preview_swap(out, in)` as a full order (`full_preview`). A test checks the preview against the order after the real swap.
- **Refusals in words:** a refused action returns to the menu and the help line gives `BattleMenus.fail_text(reason)`: one `HUD_FAIL_*` sentence per engine reason (`FAIL_REASONS`; a test reads the reasons out of `battle_engine.gd`, so a new one fails the suite until it has its line), and `HUD_FAIL_GENERIC` for anything unknown. Raw ids never reach the screen.
- **Provoke:** `_candidates_for()` and `_default_targets()` use `engine.forced_target()`, so a Provoked fighter's single-foe cursor starts on, and cannot leave, the provoker. The help line leads with "provoked: must strike {name}".
- **Automatic turns (Berserk/Confuse):** on either side, `_next_turn()` announces the turn ("{name} is berserk and fights on their own") and waits `pacing.auto_announce_sec` (longer than an enemy's think time), then `run_enemy_turn()` plays it and the help line reports it from `ActionResult.auto_reason` ("Berserk: Rhen lashes out with Attack at Reef Crab."). A party member's automatic turn is held for `auto_hold_sec`. The timeline caption, the hollow ▶ and the hollow actor marker say the player is not choosing.
- **Reflect, Zombie, end of turn:** the preview marks the timeline where a bounced spell lands and the help line says so. On resolution, a hit with `reflected_from` floats "Reflected" over the reflector; a heal that harmed (Zombie) pops as damage with "Heal turns to harm"; and the HP the engine changes after the action (Poison, Regen, Regen under Zombie) pops on the actor at the end of the turn, with "Regen turns to harm" or "Doom" when that is the cause. Heals aimed at a Zombie warn in the help line first.
- **Petrify:** stone fighters stay on the stage in the stone material (`battle_sandbox.json → stone`), do not sink or flinch, and are not on the timeline.
- **Camera shake:** a critical hit shakes the camera (`BattleStage.shake()`, deterministic, `battle_sandbox.json → shake`), never under reduced motion or in captures.
- **Intent API** (menus, tests and capture scripts all use it): `act(skill, target_ids)`, `swap_members(out, in)`, `try_escape()`.
- **Pacing:** `pacing_scale` (1 = readable, 0 = instant). Waits run through `tick(delta)` from `_process`, and a drain loop means instant mode never recurses. The values are in `battle_hud.json → pacing`.
- **Lattice:** `start_sandbox()` loads `Game.state.lattice` (or a fresh `LatticeProgress` on the standard board) and sets `engine.party_modifier = progress.apply_to`. On victory, `xp_awards()` feeds `award_battle()`, and the result is written back to `Game.state.lattice` (`persist_progress`). A fighter with no start on the board (Ysolde) shows "no Lattice path yet". Participants who fell show "Fell before the end: no XP".
- **Engine hook (the only engine change):** `BattleEngine.party_modifier: Callable`. When set, it runs once on every party combatant (active and reserve) right after `_make_party_member` builds it. It is unset by default; tests are in `tests/unit/test_battle_engine.gd`.
- **Stage:** `BattleStage` seats `FighterStandIn`s on `PartySlots/SlotN` and `EnemySlots/SlotN`, swaps them on `swap_members`, sinks and fades KO'd fighters, and projects heads to screen space for the HUD. `ground_ring.gdshader` draws the ring at radius 1.4 × the stand-in radius, 0.06 m wide, with a 0.25 m inner gradient and 6 notches, rotating 12°/s from script time.
- **Staged build (M1-UI-03, SPEC §4.2 swap budget):** entered through `SceneRouter`, the sandbox does not build in one frame. `start_sandbox(-1, true)` → `start_battle_staged()` runs one group per frame behind the router's fade: (0) Lattice progress; (1) engine, fixture opening state, 3D stand-ins, and 8 hidden timeline chips; (2) timeline identities, party panel, and the other 8 chips; (3) `engine.begin()` and the first order, filled from the pooled chips; (4) the first turn (command menu). Entering the tree, which propagates the theme through each chip's labels, was most of the old 25–30 ms block, so `TurnTimeline.prebuild(n)` adds chips hidden ahead of time and `show_turns()` takes them from the pool. `building` is true until the first turn is open; input is ignored meanwhile (state `idle`). Tests, captures and Retry keep the one-call `start_battle()`, so baselines cannot change. Tests drive the staged path synchronously by setting `frame_wait`.
- **Reaching it:** in a debug build, press **F9** on the boot screen. It is temporary until the M1-ARC-02 debug overlay.
- **Capture states:** `scripted_state` = `player_preview` (Rhen, Skills → Undertow Cut on the Gull Harrier), `swap_menu` (Rhen, Swap → reserve list, Toma hovered), `victory` (the "elegant answer" policy to a win), `defeat` (attack the first foe until the party falls), or `statuses` (Ysolde, Provoked by the reflecting Lantern Eel, aims Ember: it bounces onto Rhen, who is Doomed, a Zombie and under Regen; Asha is stone). Each runs on a **fixture** (below), forces instant pacing, no damage numbers or shake, no persistence, and the default accessibility settings. `run_script(state)` is public so tests drive the same path. The wrapper scenes in `shots/` set it, and `tests/screenshots/shots.json` lists `battle_hud_preview`, `battle_swap_menu`, `battle_victory` and `battle_statuses`.

## Capture fixtures (`BattleFixture`, `game/data/ui/battle_fixtures.json`)

The captures used to play the live sandbox, so any change to `enemies.json` moved a baseline (M1-CMB-05's softening did). Now every capture state starts from a fixture:

- `tables` is a **frozen copy** of the sandbox rows (characters, the three enemies, their skills, all 21 statuses, and a `fixture_reef` encounter) taken on 2026-10-23. Balance work never edits it.
- Each entry in `fixtures` names `active`, `reserve`, `encounter` and `seed`, may deep-merge `overrides` into rows by id (the victory fixture gives the enemies 1 HP, the defeat fixture gives the party 1 HP and the enemies sure hits, the statuses fixture makes Ysolde quick), and may set an `opening` state per combatant: `hp`, `statuses` (`[{id, duration}]`) and `provoked_by`.
- `BattleController.start_fixture(fx)` builds the engine on `fx.db`, and `fx.prepare(engine)` applies the opening state between `setup()` and `begin()`. That is the one place outside the engine that writes combatant state, and only for captures and tests. The Lattice progress is fresh and never saved.
- Tests reuse fixtures with their own `opening` (Doom, Berserk, Confuse, Zombie, Provoke) so they do not depend on balance either. To change what a shot shows, edit its fixture and re-approve the baseline after looking at it.
- Formula changes (`game/battle/formulas.gd`) can still move the HUD shots, because the timeline is real engine output. That is intended: a formula change should be seen.

## Accessibility (`UiSettings`, SPEC §6.11, art/ui.md §4.2, §5 and §9)

`UiSettings` is the data-driven layer the settings menu (later) calls. The settings, their options and their loc keys live in `game/data/ui/accessibility.json`; values persist in `user://settings.cfg` under `[accessibility]`, next to `GraphicsSettings`' section.

| Setting | Options | Effect |
|---|---|---|
| `reduced_motion` | `false`, `true` | Timeline chips snap to their slot with a 120 ms cross-fade (no slide, no stagger, no turn-start pulse); the command cursor jumps and sub-menus fade in place; the lamp motes stop breathing and the markers stop bobbing; translations (result panel rise, damage number rise) are halved; the camera never shakes. |
| `text_scale` | `1.0`, `1.15`, `1.3` | Every font size in the theme (variations and the default) is multiplied and rounded. Layout rects stay put, so long labels ellipsize. |
| `palette` | `standard`, `colorblind` | Overrides theme roles: `danger` → `#F08A24`, `enemy_chip` → `#2A2414` (art/ui.md §9). Shapes already carry every distinction (chip edges, portraits, glyph silhouettes and backings, hatching). |

API (what a menu or a view calls):

```gdscript
var s := UiSettings.shared()            # the game's instance; loads user://settings.cfg once
s.settings()                            # [&"reduced_motion", &"text_scale", &"palette"] in menu order
s.setting_row(&"text_scale")            # {id, type, default, options, option_keys, label_key, help_key}
s.options(&"palette")                   # allowed values in display order
s.get_value(&"text_scale"); s.set_value(&"text_scale", 1.3)   # set_value validates; false if refused
s.reset(); s.is_default(); s.save_to(); s.load_from()
s.changed                               # signal(key) on a real change
# what views ask instead of reading raw values:
s.animations_enabled(); s.motion_scale(); s.crossfade_sec(); s.color_overrides()
s.theme_for(base_theme)                 # base itself at the defaults, else a cached rebuilt Theme
```

`BattleHud.apply_settings(s)` (called with `shared()` in `_ready`) re-themes the HUD and pushes reduced motion into the timeline, command menu, target cursor and result panel; it follows `changed` live. Captures and tests pass their own `UiSettings.new()` (always defaults). A new setting is a new row in the JSON plus a question method here; views never read raw values.

## Deliberate deviations from `art/ui.md` (reviewer: please confirm or push back)

1. **Timeline width is 208 px of chips (a 224 px panel at x = 1648)**, not 168. At 168 px, "Gull Harrier" at the 22 px minimum did not fit beside a portrait.
2. **Rank labels are 22 px, not 20.** The doc's own minimum is 22 px.
3. **Preview arrows mark the actor and the targets only** (see `TurnTimeline` above).
4. **The text shadow is an outline, not a blur.** Godot can't blur font shadows, so the 4 px "blur" is `shadow_outline_size`.
5. **Not built yet:** the background blur behind panels (optional in the doc), the Swell gauge (the engine has no Swell until M1-CMB-04), and the "panel open" animation on HUD panels (the result panel has it). The colorblind palette, reduced motion and the text-size setting are built (M1-UI-02, § Accessibility).
6. **Reduced motion keeps a short cross-fade on chips** that change slot (120 ms from alpha 0.25), as art/ui.md §5 asks, instead of no animation at all.
7. **The help line may take two lines.** With Provoke and Reflect notes the line no longer fits 800 px; it wraps (up to two lines) only when it must, and the notes come first.

## Known gaps

- **Enemy statuses show only in the target info panel** (and as the Provoke hook and the Reflect arc when they matter). There is no status strip over enemies on the stage yet.
- **Status icons are 22 px at 1080p** (about 15 px at 720p). The shapes stay distinct, but a larger strip would help once the party rows have room.
- **Text scale does not reflow rects.** At 130% long names and help text ellipsize earlier; a settings preview should show that.
- The help line generates its text from data (kind, reach, statuses, delay, and next-turn distance). Skills have no authored description keys yet.
- `tools/ci_local.sh` and `capture.sh` write fixed `/tmp/hymn_*.log` paths, so parallel worktrees running at the same time clobber each other's logs.
