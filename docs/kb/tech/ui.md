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
| `game/ui/bestiary/` | `BestiaryMenu` (+ `bestiary_menu.tscn`), `BestiaryMenuModel`, and the `bestiary_menu` capture driver (`BestiaryShot`, `shots/`). Layout: `game/data/ui/bestiary_menu.json` (M2-UI-02). |
| `game/ui/field_menu/` | `FieldMenu` (+ `field_menu.tscn`), `FieldMenuModel`, and the `field_menu` / `field_menu_swell_modes` capture driver (`FieldMenuShot`, `shots/`). Layout: `game/data/ui/field_menu.json` (M2-UI-04). |

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
| `CommandMenu` + `MenuPage` | A stack of pages. Root: Attack, Swell (for a hero with a Swell: the input's name when the gauge is full, else the mode in force; M1-CMB-04, M2-UI-01), Skills, Items, Escape, Swap (always last). The right column shows MP (dim) and rank (`R3` and up in `ui_swell`). Sub-menus size to their rows, sit bottom-aligned at x = 552 and slide 24 px in; the page below dims its text but keeps its cursor, so the path stays readable. Input comes from `handle_input(event)` (`ui_up/down/accept/cancel`, so keyboard and controller come free) and from mouse hover and click. It emits `highlighted`, `chosen` and `cancelled`, and decides nothing. |
| `TargetCursor` | Chevrons over targets (danger for foes, focus for allies), the target info panel (name, statuses, and HP for allies; foes show "HP unknown until Read" until M1-CMB-03), and **the acting fighter's marker**: a 34 px focus diamond with a 2 px gold frame, lifted 30 px over the head on an 18 px stem, with the breathing mote as a halo *behind* it (it used to be an 18 px diamond under the mote). On an automatic turn it is hollow with a dashed stem. **Provoke:** a fish-hook glyph on a dark plate hangs over the provoker for the whole Provoked turn, and a chevron the cursor is locked to gets a solid bar over it. **Reflect:** when the chosen target would bounce the spell, a dashed gold arc with an arrowhead and the Reflect glyph (on a dark plate) runs from it to the real recipient, which gets an outlined chevron. |
| `StatusGlyph` | Original vector icons on a 48-unit grid with a 2-unit stroke, **one distinct silhouette per status (all 21)**, so none depends on hue. Polarity is coded twice: buffs are `ui_focus` on a round backing, ailments `ui_danger` on a diamond backing (tint 0.35). The M1-CMB-02 shapes: Petrify a rock with two strata lines, Berserk a zigzag of teeth, Confuse an inward spiral, Doom an hourglass with caps, Zombie a diagonal cross (Regen's plus turned over) with a centre dot, Reflect a mirror line with a bouncing chevron, Provoke a fish hook. Regen under Zombie draws `inverted`: a bar with a downward chevron, as an ailment. All four Breaks share a crack stroke. `has_shape()` lists them; a test asserts every status in `statuses.json` has one. |
| `EnemyPage` + `EnemyPageView` (M2-UI-02) | One foe's page: the words (`EnemyPage`, Node-free: from a `BattleRead.reveal`, from an enemies.json row, or name and count only) and their layout (`EnemyPageView`: name and level, HP and MP, the eight stats in a 4-column grid, the affinity rows, delay, statuses, the lore in italics, the defeat count). Shared by the Read panel and the bestiary, so both read the same. Metrics: `battle_hud.json → enemy_page`. |
| `ReadPanel`, `OpeningBanner` (M2-UI-02) | The Read result panel and the preemptive / ambush banner (§ Read, the bestiary and openings below). Both are built on first use (`BattleHud.read_panel()`, `opening_banner()`), so the staged build (M1-UI-03) never pays for them. |
| `DamageNumber`, `BattleResultPanel`, `LampMote`, `BattleHud` | The pop-and-rise numbers, plus `KIND_INFO` float text ("Reflected", "Heal turns to harm", "Regen turns to harm", "Doom") in the 28 px outlined `FloatText` style; the victory, defeat and escape screen (scrim, title, per-fighter XP and movement rows, choices); the cursor dot; and the scene root, which owns the help line (it wraps to a second line only when one line cannot hold the text) and applies `UiSettings`. `help_history` keeps the last 16 help lines for tests. |

## Battle sandbox (`game/battle/scene/`)

`BattleController` (the root of `battle_sandbox.tscn`) is the only glue. It calls `setup`, `begin`, `preview`, `perform`, `swap`, `escape`, `run_enemy_turn` and `xp_awards`, plus `engine.timeline.predict()` for the "failed escape" preview, and it listens to `action_resolved`. It never writes combatant state.

- **States:** `command → skills → target`, `command → items → target`, `command → swap_in → swap_out`, `busy` (enemy turns, automatic turns and post-action holds), and `result`.
- **Swap preview:** hovering a reserve member in `swap_in` shows the order after that member replaces the acting fighter, and `swap_out` shows it for the highlighted leaver, both from `BattleEngine.preview_swap(out, in)` as a full order (`full_preview`). A test checks the preview against the order after the real swap.
- **Refusals in words:** a refused action returns to the menu and the help line gives `BattleMenus.fail_text(reason)`: one `HUD_FAIL_*` sentence per engine reason (`FAIL_REASONS`; a test reads the reasons out of `battle_engine.gd`, so a new one fails the suite until it has its line), and `HUD_FAIL_GENERIC` for anything unknown. Raw ids never reach the screen.
- **Provoke:** `BattleMenus.skill_candidates()` and `default_targets()` use `engine.forced_target()`, so a Provoked fighter's single-foe cursor starts on, and cannot leave, the provoker. The help line leads with "provoked: must strike {name}".
- **Automatic turns (Berserk/Confuse):** on either side, `_next_turn()` announces the turn ("{name} is berserk and fights on their own") and waits `pacing.auto_announce_sec` (longer than an enemy's think time), then `run_enemy_turn()` plays it and the help line reports it from `ActionResult.auto_reason` ("Berserk: Rhen lashes out with Attack at Reef Crab."). A party member's automatic turn is held for `auto_hold_sec`. The timeline caption, the hollow ▶ and the hollow actor marker say the player is not choosing.
- **Reflect, Zombie, end of turn:** the preview marks the timeline where a bounced spell lands and the help line says so. On resolution, a hit with `reflected_from` floats "Reflected" over the reflector; a heal that harmed (Zombie) pops as damage with "Heal turns to harm"; and the HP the engine changes after the action (Poison, Regen, Regen under Zombie) pops on the actor at the end of the turn, with "Regen turns to harm" or "Doom" when that is the cause. Heals aimed at a Zombie warn in the help line first.
- **Petrify:** stone fighters stay on the stage in the stone material (`battle_sandbox.json → stone`), do not sink or flinch, and are not on the timeline.
- **Camera shake:** a critical hit shakes the camera (`BattleStage.shake()`, deterministic, `battle_sandbox.json → shake`), never under reduced motion or in captures.
- **Items (M1-UI-04):** the root shows **Items** between Skills and Escape only while `BattleController.items` (a `BattleItemSource`) is set. `start_sandbox()` wraps `Game.state.inventory` (a copy unless `persist_progress`). Capture fixtures set no bag, so their baselines keep the four-row root. `BattleMenus.item_rows` lists the bag's battle items with `xN` and their rank, greyed out while `item_candidates` is empty. The cursor moves over exactly the targets `BattleEngine.item_can_target` admits, on the active party or the foes; items ignore the Provoke lock. A revive starts on the first fallen ally. Hover and target both preview `engine.preview_item`. `BattleMenus.item_notes` leads the help line with what the use really does: a felled Zombie (`HUD_HELP_ITEM_FELLS_FMT`), a heal turned to harm, or, when `engine.item_defeats_party` is true (a Zombie reviving itself as the last one standing), `HUD_HELP_ITEM_DEFEAT_FMT` alone in the `danger` role (`BattleHud.set_help(text, role)`). It is a warning, not a block: the use stays legal. Rules: design/economy.md § Targeting in battle.
- **Intent API** (menus, tests and capture scripts all use it): `act(skill, target_ids)`, `use_item_on(item, target_ids)`, `swap_members(out, in)`, `try_escape()`. The capture scripts live in `BattleCaptureScript.play()` and use only this API plus `default_targets()` and `aim_at()`.
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
| `timing_assist` | `off`, `wide`, `auto` | Timed Swell inputs (M2-UI-01). `wide` scales the perfect and good windows by 1.5 (kept inside the beat); `auto` makes a miss count as Good. Applied to the input row (`timing_input(row)`), never in the engine; the ring panel shows a short tag while it is on. Numbers: formulas.md § Swell, Timing assist. |

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
s.timing_input(row); s.timing_assist_tag_key()   # M2-UI-01: an input row as the assist plays it
s.theme_for(base_theme)                 # base itself at the defaults, else a cached rebuilt Theme
```

`BattleHud.apply_settings(s)` (called with `shared()` in `_ready`) re-themes the HUD and pushes reduced motion into the timeline, command menu, target cursor and result panel; it follows `changed` live. Captures and tests pass their own `UiSettings.new()` (always defaults). A new setting is a new row in the JSON plus a question method here; views never read raw values.

## Deliberate deviations from `art/ui.md` (reviewer: please confirm or push back)

1. **Timeline width is 208 px of chips (a 224 px panel at x = 1648)**, not 168. At 168 px, "Gull Harrier" at the 22 px minimum did not fit beside a portrait.
2. **Rank labels are 22 px, not 20.** The doc's own minimum is 22 px.
3. **Preview arrows mark the actor and the targets only** (see `TurnTimeline` above).
4. **The text shadow is an outline, not a blur.** Godot can't blur font shadows, so the 4 px "blur" is `shadow_outline_size`.
5. **Not built yet:** the background blur behind panels (optional in the doc) and the "panel open" animation on HUD panels (the result panel has it). The colorblind palette, reduced motion and the text-size setting are built (M1-UI-02, § Accessibility).
6. **Reduced motion keeps a short cross-fade on chips** that change slot (120 ms from alpha 0.25), as art/ui.md §5 asks, instead of no animation at all.
7. **The help line may take two lines.** With Provoke and Reflect notes the line no longer fits 800 px; it wraps (up to two lines) only when it must, and the notes come first.
8. **The Swell gauge sits under the name, not in its own column** (M1-CMB-04). The row has no room for a fourth 64 px column (name 134 + HP 220 + MP 120 + gaps fill the 594 px row), so the gauge is 64 x 4 px at the name's left edge, bottom-aligned with the HP and MP bars. Only heroes with a Swell draw one. When full, it is framed (a shape cue, not hue alone) and its fill pulses on the 1.6 s sine; with reduced motion it holds the full glow. **M1-UI-05:** the frame was `focus_gold` at 1 px, which sat on the `ui_swell` fill at about 1.1:1 and could not be seen in `battle_swell_ring`. It is now a 2 px `outline` (night) gap and then a 2 px `text` (white) line outside the bar, drawn as filled whole-pixel bands under the bar. 2 px, because the 1280x720 captures (and a 720p window) draw the 1080p layout at 2/3 scale, where a 1 px band is 0.67 px and vanishes; that is also part of why the old frame could not be seen (`swell_full_gap_px`, `swell_full_frame_px` in battle_hud.json). Both edges of the gap clear 3:1 (WCAG non-text contrast) whatever the fill's hue; `tests/unit/test_hud_gauge.gd` checks it on the real theme colours. The frame is now also in art/ui.md §6.2 (M1-NIT-01).
9. **Every hero's Swell input is a panel where the command menu was** (Rhen's since M1-CMB-04, the others since M2-UI-03) (`battle_hud.json` `swell_ring`, 480 x 332 at (48, 700)), so it never covers the fighters, and the menu is hidden while it is open. It has no doc spec yet; see § Swell below.

10. **The Read panel and the bestiary page have no doc spec** (M2-UI-02). Both use the result panel's tide-notch and the existing type roles (header serif for the name, `DimLabel` for labels, `HudNumber` for numbers, `FlavorLabel` for lore). The Read panel sits at (560, 128), 800 wide, between the help line and the command menu, so the timeline stays uncovered (pillar 4; a test checks the rects).
11. **The opening banner is art/ui.md §7's location banner, shortened for battle** (0.3 s in, 1.8 s hold, 0.5 s out instead of 0.6 / 2.5 / 0.8) and given a dark band that fades at both ends, because the words sit over a bright sky (§9's contrast floor). The rule ends carry the timeline's side shapes: squares for a preemptive strike, outward chevrons for an ambush.
12. **The Swell root row is on the menu for a Swell hero at any gauge** (M2-UI-01), not only when full, so the fill mode can be chosen before the gauge fills. It names the mode in force (dim) until the gauge is full, then the input (swell color), as before.

## Read, the bestiary and openings (M2-UI-02)

- **Read panel.** `BattleBestiary` (the M1-CMB-03 glue) opens `hud.read_panel()` on every Read of a foe, with `EnemyPage.from_reveal(last_reveal, db.statuses)`: name, level, HP and MP as they stand, the eight stats, the four affinity lists (SPEC element order, "None" when empty), delay immunity, current statuses and the lore. The weakness float stays; the panel joins it.
  - **It costs no battle time.** The Read paid its rank. While the panel is open `BattleHud.holds_battle()` is true and `BattleController.tick()` holds every wait (a one-condition hook on an existing line), so the next turn starts only after it closes. In live pacing the controller is `busy` then and ignores input.
  - **Input.** Confirm or cancel closes it, so does a click anywhere (the full-screen root takes the mouse). It swallows the other `ui_*` actions while open and lets other keys (the debug F-keys) pass. It handles its own `_unhandled_input`: the HUD sits under the controller, so it sees an event first.
  - Instant pacing (tests, captures) drains the waits inside `act()`, so there the next turn is already open under the panel. The `battle_read_panel` capture shows that state.
  - Reduced motion halves the 8 px open rise, as the result panel does. A Confused reader's Read on an ally opens nothing (there is no enemies.json page).
- **Opening banner.** At the first turn of a preemptive or ambush opening (`BattleOpening.CAPTION_KEYS`, `engine.opening`), `BattleBestiary` shows `hud.opening_banner()` instead of the old caption float: the title ("First Strike" / "Caught Unaware"), the caption, and what it means for the order ("Your party acts before any foe." / "Every foe acts before your party."). It never takes input and does not hold the battle. Instant pacing shows it held, with no timer. Rules: battle_ctb.md and formulas.md § Openings.
  - Fixtures can now set `"battle_opening"` (`BattleFixture.battle_opening`, applied in `prepare()` before `begin()`), so a capture shows an opening without a roll.
- **Bestiary menu** (out of battle). `BestiaryMenu.open_in(host)` (its own CanvasLayer; it pauses the tree while open, like `SaveMenu`) over `BestiaryMenuModel.from_game()` (`Game.state.bestiary` and enemies.json).
  - The left list holds every logged foe that enemies.json still lists, in enemies.json order, with its defeat count (`×N`). An unread one also says "Not Read" in the middle column (words, not only the dim count).
  - The right side shows the entry under the cursor. A Read foe gets the full page from its row (`EnemyPage.from_row`: stats, weaknesses, lore, "Defeated: N"). A foe defeated but never Read shows its name, its count and how to learn more.
  - Ids the table no longer lists are skipped on screen and never removed from the save (`skipped_ids()`).
  - Up and down choose, hover shows, cancel closes.
  - **Reached from the field menu** (M2-UI-04, § Field menu below): Bestiary calls `BestiaryMenu.open_in(field_menu)`.
- **Captures:** `battle_read_panel` (fixture `read_panel`: Ysolde, quick and taught `read`, Reads the reflecting Lantern Eel; the fixture adds the enemies' `lore_key`s and a `read` row to the frozen tables), `battle_opening_banner` (fixture `opening_banner`: an ambush), `bestiary_menu` (`BestiaryShot`: a fixed log over the frozen enemies, the Lantern Eel's page on show).

## Swell fill modes (M2-UI-01)

- The **Swell** page lists the techniques (greyed out until the gauge is full), then one row per unlocked mode (`BattleMenus.swell_mode_rows`, in swell.json order). Each row shows the mode's `name_key`, and "In use" or "No time" on the right. Highlighting a mode row puts its `desc_key` on the help line with "Choosing it costs no time", and the timeline shows the order unchanged (no ghost). Choosing one calls `BattleSwell.set_mode` (the engine's rule), redraws the page and the root row in place, and leaves the turn with the same fighter. `SwellModeRows` is the glue; the controller reaches it through one-condition hooks on two existing lines.
- Since the merge with M2-ARC-01 a mode chosen in battle is carried out of it with the gauge (`BattleSwellCarry`). The out-of-battle API exists (`BattleSwellCarry.mode_rows` / `set_mode`, battle_ctb.md), and the field menu's Swell page is its chooser (M2-UI-04, § Field menu below).
- **Timing assist:** see § Accessibility. The controller builds the ring from `hud.settings.timing_input(row)`, and the ring panel shows the tag ("Assist: wider window" / "Assist: misses count as Good") at its top left. `SwellInput.assist_floor` (every kind grades through `SwellInput._record`) is the one engine-side addition.
- **Capture:** `battle_swell_modes` (fixture `swell_modes`: Rhen at 40, the Swell page with Wake highlighted).

## Field menu (M2-UI-04)

- **Opening it.** In the field, `ui_cancel` (Escape, B / Circle) opens `FieldMenu.open_in(player)`. That's a three-line `elif` in `FieldController._unhandled_input`, under the same `accepts_input` guard as interact, so a cutscene or a conversation (the sequencer turns `accepts_input` off) never opens it. Like `SaveMenu`, it brings its own CanvasLayer (layer 60, under the bestiary's 64) and pauses the tree while open, so the player can't get a second Escape.
- **Three levels.** All three are `MenuPage`s, with words from `FieldMenuModel` and loc keys `FIELD_MENU_*`:
  - **Root** (left): Bestiary, Swell, Return to the path.
  - **Heroes** (right): each Swell hero, with the mode in use on the right.
  - **Modes** (right, headed "Rhen's fill mode"): `BattleSwellCarry.mode_rows(cid)`. Each row shows its `name_key`, and the current one also says "In use" (`HUD_SWELL_MODE_IN_USE`, the battle page's word).

  A line under the right page says what the highlighted row does: the root row's purpose, a hero's mode and its `desc_key`, or a mode's `desc_key` ("… is in use: …" for the current one). On the root the line sits at the top of the right column. Choosing a mode calls `BattleSwellCarry.set_mode` and redraws in place. The line then confirms the change until the cursor moves: "Rhen's gauge now fills by Wake. It keeps what it holds." The gauge keeps its points (battle_ctb.md "Carried Swell").
- **Input.** Up and down move. Confirm chooses. Cancel goes back a level, and closes the menu from the root. Hovering moves the cursor, and a click chooses (a click on the root page from a deeper level goes back to the root). While the bestiary is open it takes every input, and the field menu hides until the bestiary closes. The field menu keeps holding the pause, so the field stays still in between.
- **Heroes.** `PartyGoods.joined_members(Game.state)`, minus anyone with no Swell. The first playable never writes `Game.state.party_ids` (its party comes from first_playable.json `field_battle`), so when no one has joined, that party stands in. Remove the fallback once the flow fills `party_ids`. With no Swell hero, the Swell row is off and the line says why.
- **Layout.** `field_menu.json`. Every rect is a multiple of 3 at the 1080p reference, so the 1280 x 720 captures (2/3 scale) draw each frame edge on a whole pixel. Before that, the page borders broke up at fractional pixels. The right page is only as tall as its rows (`MenuPage.height_for`). `MenuPage.set_header` is new: the right page is set up titled once and renamed per level.
- **Captures:** `field_menu` (the root, cursor on Swell) and `field_menu_swell_modes` (Rhen's modes with Tether unlocked and Wake in use, cursor on Tether). Both come from `FieldMenuShot` on a scratch `GameStateData`. The modes come from swell.json, as they do in play.
- **The target info panel knows a Read foe.** `BattleController._show_pick` now takes `revealed` from `BattleBestiary.knows(c)`, which is `book.is_read(BattleEngine.enemy_id(c))` for a foe. A foe the party has Read, in this battle or before it (a live battle's book is `Game.state.bestiary`), shows its HP gauge instead of "HP unknown until Read". The controller line count is unchanged (994). Capture fixtures log into a scratch book, so no battle baseline moves.

## The Vowbound (M2-UI-05, ADR 0030)

`BattleVowboundHud` (`game/battle/scene/battle_vowbound_hud.gd`) is the glue, built like `BattleBossHud`. The controller reaches it through one-line hooks: the attach in `_build_engine`, `vow.perform` in `act()`, `vow.highlight` in the highlight guard, `vow.choose` as the root `match`'s default, and `vow.show_note` in `_open_command`. `_after_action` is now the public `after_action`, so the glue can end a call or a dismissal the way an action ends. Engine rules: battle_ctb.md § Vowbound.
- **Binding.** `attach()` builds `engine.vowbound` before `begin()`.
  - A live battle binds every vowbound.json row whose `bound_flag` is set (`Game.get_flag`; Ilun's is `ch03_ilun_bound`; `validate_data.py` checks that the flag is declared).
  - A fixture binds its `vowbound` list from the frozen `tables.vowbound`. Fixture `overrides` merge into those rows too.
  - Any other battle loads the rows with nothing bound.
- **The caller's Call row** (`BattleMenus.call_rows`) comes after Skills: "Call Ilun", with the call's rank (`R3`) on the right.
  - Refused, it is greyed and the reason replaces the rank: "Silenced" or "Fallen". Disabled rows cannot be highlighted, so the reason has to sit on the row.
  - **With nothing bound yet there is no row** (Lead decision on M2-UI-05, ADR 0030 amendment): a greyed "Call · None bound" before Chapter 3 would be a dead row hinting at a beat to come. The `not_bound` refusal keeps its words for the engine's reason only.
  - Highlighting it shows the whole order after the call (`BattleVowbound.preview_call`, a full preview as for Swap): Ilun takes slot 0 and the party is gone.
  - The help line says what the call costs: "Ilun answers and takes this turn, and the party stands down. When it returns, Asha waits a rank 3 delay; the others keep their place." The return cannot be drawn before the call, because it depends on when Ilun leaves.
- **The Vowbound's own page** (`vowbound_root_rows`, titled with its name) has these rows:
  - **Attack.**
  - **Floodnet.** Greyed until the gauge is full, with the right column saying how full ("38%"); full, it shows its rank.
  - **Skills:** Brine Lash and Tidal Ward.
  - **Dismiss** ("Ends turn").
  - **Escape and Swap**, greyed (the engine refuses them with `vowbound_out`). Items is left off ("a Vowbound uses no items"), so the page never needs more than six rows.
- **The root page grows upward.** Its rect (`commands.rect`, 272 px) holds five rows, and a sixth used to spill below the frame. That could already happen to live Rhen with a bag (Attack, Swell, Skills, Items, Escape, Swap), and now to Asha with a bag and her Call row. `CommandMenu.open_root` now sizes the page to `MenuPage.height_for(rows)` when that is taller, from the same foot. Five-row pages, and so every baseline, are unchanged. Asha reaches seven rows with a bag and Ilun bound (Attack, Swell, Skills, Call Ilun, Items, Escape, Swap); M2-UI-03 raised `max_rows` to 7, so the whole root stands above the same foot (top at y 684, well clear of the help line) instead of scrolling Swap out of sight.

  Floodnet goes through the normal target pick, and `act()` hands it to `BattleVowbound.unleash` (`vow.perform`). Highlighting Dismiss shows the whole order with the party back (`preview_dismiss`), the caller after its call delay, and the help line says when the caller acts again.
- **The field.**
  - `called` and `departed` re-seat the stage. `BattleStage.sync_party` now takes off any party stand-in not on the field, and seats a called Vowbound on `battle_sandbox.json` `vowbound_slot` (the middle slot). Ilun's greybox stand-in is a tall deep-teal capsule with a lagoon glow.
  - They also rebuild the party panel: the Vowbound alone, with HP, MP and a Swell gauge (`PartyRow.show_swell`; it has no fill mode), and a dim note at the panel's foot, "Standing down: Rhen, Asha" (`PartyPanel.set_note`, `party.note_height`).
  - A departure leads the next command menu's help line: "Ilun has fallen and cannot answer again this battle. The party returns." or "Ilun has left the field. The party returns." A boss prompt waiting for the same menu wins.
- **Refusals in words.** `BattleMenus.FAIL_REASONS` gains the six Vowbound reasons, each with its own `HUD_FAIL_*` line.
- **No flash or new motion.** The call has no cinematic yet (SPEC §6.3; a cinematics task), so nothing here flashes. The panel and timeline use their existing reduced-motion paths.
- **Captures:**
  - `battle_vowbound_call` (fixture `vowbound_call`): Asha's turn, the Call row highlighted.
  - `battle_vowbound_out` (fixture `vowbound_out`): Ilun out after one exchange, Dismiss highlighted. The fixture makes Ilun quicker, so he lives to a second turn with some gauge.
- **Tests:** `tests/unit/test_battle_vowbound_hud.gd` (scene) and `test_battle_vowbound_preview.gd` (each preview against the engine's real order after the action); `tools/tests/test_vowbound_flag_validate.py`.

## Swell input panels for the chant, brace and glyph (M2-UI-03)

`SwellRingView` (`hud.swell_ring`) is now the panel for every kind. It holds the title, one pip per grade, the last grade in words at the top right, the hint and the assist tag. The last-grade word (`callout_text()`) is drawn in the grade's role: swell for the best grade, focus for one that earns power, danger for a miss. The view draws Rhen's lamp itself and hands each other kind to a drawer in `game/ui/battle/`: `SwellChantDraw`, `SwellBraceDraw` and `SwellGlyphDraw`. Each draws its input's state and decides nothing. Metrics are in `battle_hud.json → swell_ring`.
- **Grades read by shape, not hue.** The best grade (perfect, swift) is a filled diamond with a gold halo. Braced, traced and good are filled diamonds. A miss is a cross. The step that finishes a kind (the brace's counter, the glyph's swift) waits as a hollow circle, not a diamond.
- **Asha, the chant.** The phrase's notes scroll from the right onto a gold line. Each is an arrow pointing at its direction, spaced by its time, so the rhythm reads before it sounds. A band shows the good window and, brighter, the perfect one, so the timing assist's wider window is visible. The waiting note is a focus outline in a gold diamond frame. A perfect note is filled swell with a halo, and "Perfect" shows at the top right: Shallows Verse's power hangs on it.
- **Toma, the brace.** A track runs from the opening to the end of the counter's window. The blows hang over it as wedges at their times, the counter is a gold diamond in its window band, and a white playhead moves along it. A shield under the track is filled while Confirm is held and hollow when it is not, and the status line says "Holding" or "Not holding".
  - **Lead-in (M2-NIT-03).** A release during the lead-in only lets go (`SwellBrace.release`, formulas.md § Swell), so the tap that chose Return Tide cannot spoil it. `SwellInputKeys.carry_held` starts the hold when that Confirm is still held as the brace opens.
- **Ysolde, the glyph.** The whole glyph is drawn as strokes from a gold start node. Traced strokes are solid swell; a missed one is a dashed danger line with a cross; the one asked for now is dashed focus with an arrowhead; later ones are dim. A bar under the glyph runs down with the window's time left. A gold notch marks where Swift closes, and the bar is swell-colored past it while a Swift trace is still possible.
- **Hints.** `SwellRingView.hint_key(kind, locked)` picks `HUD_SWELL_{RING,CHANT,BRACE,GLYPH}_HINT[_LOCKED]`; "locked" drops Cancel once a step is graded. The help line still leads with the row's `help_key`.
- **Grade words.** `BattleMenus.grade_text` reads `SwellRingView.grade_key`, so Braced, Traced and Swift are named in the result line.
- **The gate is gone.** `DRAWN_KINDS` lists all four kinds, so Asha, Toma and Ysolde have gauges and Swell rows. A capture fixture gives a hero a Swell row only when the hero's technique is in the frozen tables. Shallows Verse, Return Tide and Written Light are now there, so Asha's root in `battle_vowbound_call` and Ysolde's in `battle_statuses` gained the row.
- **Unlocks are seen.** `BattleSwell.mode_unlocked` floats "{mode} unlocked" over the field in the swell color (`SwellModeRows.announce`, at `swell_ring.unlock_at`). Like every float, it follows `show_damage_numbers`.
- **Captures:**
  - `battle_swell_chant`: the first note perfect, the second closing on the line.
  - `battle_swell_brace`: Confirm held, the first blow braced, the second coming.
  - `battle_swell_glyph`: two strokes traced, with Swift still in reach.
- **Tests:** `tests/unit/test_swell_input_panels.gd`.

## Swell (M1-CMB-04)

- **Gauge:** `PartyRow.swell_gauge()`, a `HudGauge` with the `swell` role (see deviation 8). `HudGauge.glow` (0..1) brightens the fill and adds the full frame (`HudGauge.full_frame_rects()`: night gap, white line).
- **Command:** a **Swell** row under Attack, only while `BattleSwell.is_ready(actor)`. Its right column names the input ("Lamp Ring") in `ui_swell`. It opens the Swell page (technique rows with their rank). The help line on the page leads with the input's instruction.
- **Input:** `SwellRingView` (`hud.swell_ring`) draws a `SwellTimingRing`:
  - a lamp at the centre that flares toward each beat's peak and flickers slightly (no flicker with reduced motion),
  - a gold rim at the lamp's edge, and a `focus` ring that closes from the outer edge onto the rim at the peak,
  - one pip per beat: a hollow diamond while waiting; filled `ui_swell` with a gold halo for perfect; filled `focus` for good; a `danger` cross for a miss.
  The hint reads "Confirm: strike as the ring meets the lamp · Cancel: back" and drops the Cancel part once a beat is graded. `ui_accept` presses and `ui_cancel` backs out to the target pick.
- **Input fairness (M1-UI-05):** `SwellRingClock` (game/battle/scene) is the only thing that reads the wall clock. A rendered frame (`_process` → `tick(delta, true)`) moves the ring by at most `max_step_sec` (swell.json, 0.05 s, validated ≤ `perfect_sec`), so a long frame (a 121-150 ms prewarm frame, a GC pause) pauses the ring instead of skipping a peak or grading a miss the player never saw. A press first catches the ring up from the last frame to the moment it is handled (clamped the same way), so it is graded against now, not the previous frame, and the next frame subtracts what was caught up. `tick(delta)` without `frame` stays exact simulated time for tests and capture scripts. Godot 4 input events carry no timestamp, so "handled" (the start of the frame that flushes the event) is as close as we get.
  - **One clock (M1-NIT-01, review-sweep-J S1):** a frame's `delta` is game time, which `Engine.time_scale` scales, so the press catch-up multiplies its wall-clock interval by `Engine.time_scale` before clamping. Under a slow-mo, or a frozen capture (`time_scale` 0), frames and presses then agree. Pacing never scales the ring.
  - **Below 20 fps** (a frame longer than `max_step_sec`) the ring runs slower than real time, by design: the ring draws its own `elapsed`, so what the player sees and what is graded still match.
- **Help text:** `SWELL_INPUT_TIMING_RING_HELP` takes `{beats}` from the input row, so a tuning of `beats` never leaves the text wrong.
- **Capture:** `battle_swell_ring` (fixture `swell_ring`) freezes the ring 0.2 s before the second peak, with the first beat perfect (`BattleController.swell_input_live = false`).

## Known gaps

- **Enemy statuses show only in the target info panel** (and as the Provoke hook and the Reflect arc when they matter). There is no status strip over enemies on the stage yet.
- **Status icons are 22 px at 1080p** (about 15 px at 720p). The shapes stay distinct, but a larger strip would help once the party rows have room.
- **Text scale does not reflow rects.** At 130% long names and help text ellipsize earlier; a settings preview should show that.
- The help line generates its text from data (kind, reach, statuses, delay, and next-turn distance). Skills have no authored description keys yet.
- `tools/ci_local.sh` and `capture.sh` write fixed `/tmp/hymn_*.log` paths, so parallel worktrees running at the same time clobber each other's logs.
