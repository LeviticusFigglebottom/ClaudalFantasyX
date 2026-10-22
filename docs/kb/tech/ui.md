# UI and Battle HUD: How It Is Built

Owner: UI/UX + Combat (M1-UI-01, M1-CMB-01). Art rules: [`docs/kb/art/ui.md`](../art/ui.md). Battle rules: [`docs/kb/design/battle_ctb.md`](../design/battle_ctb.md).

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
| `game/data/ui/battle_sandbox.json` | Sandbox roster, encounter, seed, greybox stand-in shapes and colors, and ring metrics. |
| `game/battle/scene/` | `battle_sandbox.tscn`, `BattleController`, `BattleStage`, `BattleMenus`, `FighterStandIn`, `ground_ring.gdshader`, and `shots/` (capture entry scenes). |
| `assets/fonts/` | Source Sans 3 and EB Garamond, each with its `OFL.txt`. |

## Theme

Regenerate after editing `theme.json` (or a UI swatch in `palette.json`):

```bash
godot --headless --path . --script res://game/ui/theme/build_theme.gd
```

- **Palette roles live in the theme**, as colors of the theme type `Hymn`. Code reads `get_theme_color(&"focus", &"Hymn")` and never hard-codes a color. Constants in that type (`line_px`, `focus_px`, `chamfer_px`, and so on) do the same for metrics.
- **Panels** are `TideNotchStyleBox`, a scripted `StyleBox`. It draws the vertical gradient with vertex colors, the 24 px top sheen, the 1 px inner rule inset 3 px, the 1 px gold frame, and 45° chamfers on the top-left and bottom-right corners only (6 px on `PanelSmall`), each with a lamp-node. Lines are drawn unantialiased at half-pixel offsets, so they stay crisp. Buttons, the cursor and the focus frame use `StyleBoxFlat` with `corner_detail = 1`, which turns a radius into the same 45° cut.
- **Type variations:** `TitleLabel`, `BannerLabel` and `HeaderLabel` (serif; small caps through `smcp`), `BodyLabel`, `MenuLabel`, `HudName`, `HudNumber` and `RankLabel` (tabular figures, `tnum` + `lnum`), `SmallLabel`, `HelpLabel`, `FlavorLabel`, `DimLabel`, `DamageNumber` / `DamageNumberCrit` (outlined), `CommandButton`, and `PanelSmall`.
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
| `TurnTimeline` + `TimelineChip` | 16 slots (`CtbTimeline.PREVIEW_LENGTH`). `show_turns(current, base, preview, targets, color, mode)`. The pure `build_slots()` keys each turn as `<id>#<turn index>` (stable across previews and real turns, via `note_turn_taken`), marks the ghost (the actor's next turn), and sets `moved` (▲/▼) **only for the actor and its targets**. Everyone else just slides; arrows on all 15 chips buried the two that matter. Allies have a square edge and square portrait; enemies have a chevron edge, a diamond portrait and a `ui_danger` name. Skipped (Stop/Sleep) turns are hatched and dimmed, and targeted turns carry a ring mark. One tween per chip is killed and restarted on every new layout. |
| `PartyPanel` + `PartyRow` + `HudGauge` | Active fighters only. HP/MP numbers are tabular. Low HP (< 25%) turns `ui_danger` **and** hatched. A status strip holds up to 6 `StatusGlyph`s. The current actor's row gets a raised fill and a focus edge, and an ally target gets a full focus frame. |
| `CommandMenu` + `MenuPage` | A stack of pages. Root: Attack, Skills, Escape, Swap (always last). The right column shows MP (dim) and rank (`R3` and up in `ui_swell`). Sub-menus size to their rows, sit bottom-aligned at x = 552 and slide 24 px in; the page below dims its text but keeps its cursor, so the path stays readable. Input comes from `handle_input(event)` (`ui_up/down/accept/cancel`, so keyboard and controller come free) and from mouse hover and click. It emits `highlighted`, `chosen` and `cancelled`, and decides nothing. |
| `TargetCursor` | Chevrons over targets (danger for foes, focus for allies), the target info panel (name, statuses, and HP for allies; foes show "HP unknown until Read" until M1-CMB-03), and the acting fighter's focus diamond with a breathing mote. |
| `StatusGlyph` | Original vector icons on a 48-unit grid: a tint disc at 0.35 with a 2-unit stroke. Buffs use `ui_focus` and ailments `ui_danger`. All four Breaks share a crack stroke. Unimplemented statuses fall back to a diamond. |
| `DamageNumber`, `BattleResultPanel`, `LampMote`, `BattleHud` | The pop-and-rise numbers; the victory, defeat and escape screen (scrim, title, per-fighter XP and movement rows, choices); the cursor dot; and the scene root, which also owns the help line. |

## Battle sandbox (`game/battle/scene/`)

`BattleController` (the root of `battle_sandbox.tscn`) is the only glue. It calls `setup`, `begin`, `preview`, `perform`, `swap`, `escape`, `run_enemy_turn` and `xp_awards`, plus `engine.timeline.predict()` for the "failed escape" preview, and it listens to `action_resolved`. It never writes combatant state.

- **States:** `command → skills → target`, `command → swap_in → swap_out`, `busy` (enemy turns and post-action holds), and `result`.
- **Intent API** (menus, tests and capture scripts all use it): `act(skill, target_ids)`, `swap_members(out, in)`, `try_escape()`.
- **Pacing:** `pacing_scale` (1 = readable, 0 = instant). Waits run through `tick(delta)` from `_process`, and a drain loop means instant mode never recurses. The values are in `battle_hud.json → pacing`.
- **Lattice:** `start_sandbox()` loads `Game.state.lattice` (or a fresh `LatticeProgress` on the standard board) and sets `engine.party_modifier = progress.apply_to`. On victory, `xp_awards()` feeds `award_battle()`, and the result is written back to `Game.state.lattice` (`persist_progress`). A fighter with no start on the board (Ysolde) shows "no Lattice path yet". Participants who fell show "Fell before the end: no XP".
- **Engine hook (the only engine change):** `BattleEngine.party_modifier: Callable`. When set, it runs once on every party combatant (active and reserve) right after `_make_party_member` builds it. It is unset by default; tests are in `tests/unit/test_battle_engine.gd`.
- **Stage:** `BattleStage` seats `FighterStandIn`s on `PartySlots/SlotN` and `EnemySlots/SlotN`, swaps them on `swap_members`, sinks and fades KO'd fighters, and projects heads to screen space for the HUD. `ground_ring.gdshader` draws the ring at radius 1.4 × the stand-in radius, 0.06 m wide, with a 0.25 m inner gradient and 6 notches, rotating 12°/s from script time.
- **Reaching it:** in a debug build, press **F9** on the boot screen. It is temporary until the M1-ARC-02 debug overlay.
- **Capture states:** `scripted_state` = `player_preview` (Rhen, Skills → Undertow Cut on the Gull Harrier), `swap_menu` (Rhen, Swap → reserve list), or `victory` (the "elegant answer" policy to a win). Each forces instant pacing, no damage numbers and no persistence. The wrapper scenes in `shots/` set it, and `tests/screenshots/shots.json` lists `battle_hud_preview`, `battle_swap_menu` and `battle_victory`.

## Deliberate deviations from `art/ui.md` (reviewer: please confirm or push back)

1. **Timeline width is 208 px of chips (a 224 px panel at x = 1648)**, not 168. At 168 px, "Gull Harrier" at the 22 px minimum did not fit beside a portrait.
2. **Rank labels are 22 px, not 20.** The doc's own minimum is 22 px.
3. **Preview arrows mark the actor and the targets only** (see `TurnTimeline` above).
4. **The text shadow is an outline, not a blur.** Godot can't blur font shadows, so the 4 px "blur" is `shadow_outline_size`.
5. **Not built yet:** the background blur behind panels (optional in the doc), the colorblind palette swap, reduced motion, the text-size setting, the Swell gauge (the engine has no Swell until M1-CMB-04), and the "panel open" animation on HUD panels (the result panel has it).

## Known gaps

- **No timeline preview for Swap.** The engine has no `preview_swap(out, in)`, so the help line explains the effect ("takes Rhen's place in the order") but the chips don't move. This is a candidate Combat API.
- The help line generates its text from data (kind, reach, statuses, delay, and next-turn distance). Skills have no authored description keys yet.
- `tools/ci_local.sh` and `capture.sh` write fixed `/tmp/hymn_*.log` paths, so parallel worktrees running at the same time clobber each other's logs.
