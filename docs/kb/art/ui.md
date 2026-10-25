# UI Art Rules

Owner: Art Director (M1-ART-01). Build: UI/UX (M1-UI-01). SPEC §7.6, §6.1, §6.11, pillar 4.
Every color here is a swatch in [`palette.json`](palette.json) (the `ui_*` family unless noted). All UI is Godot Control nodes plus shaders. **No raster mock-ups ship**, and icons are agent-authored SVG.

**Thesis:** deep water seen from above, with lamplight on its surface. The panels are translucent deep blue with thin gold and white lines, the motion is calm, and nothing is decorative unless it also carries information.

---

## 1. Colors

| Use | Swatch | Hex | Alpha |
|---|---|---|---|
| Panel fill, top of the vertical gradient | `ui_panel_deep` | `#0A2342` | 0.80 |
| Panel fill, bottom of the gradient | `ui_panel_low` | `#06162B` | 0.86 |
| Selected row and raised sub-panel | `ui_panel_raised` | `#133A66` | 0.85 |
| Outer frame line, separators of rank | `ui_line_gold` | `#D9B45A` | 0.85 (frame), 1.0 (focus) |
| Inner rule, primary text | `ui_line_white` | `#F2F5FA` | 0.18 (inner rule), 1.0 (text) |
| Secondary text, disabled | `ui_text_dim` | `#A9B8CC` | 1.0 (secondary), 0.5 (disabled) |
| Cursor glow, focus, current actor, ally target ring | `ui_focus` | `#6FE0D8` | 0.9 |
| HP / MP / Swell fills | `ui_hp` / `ui_mp` / `ui_swell` | `#7FD38A` / `#6FA8F0` / `#F2B84B` | 1.0 |
| Low HP (< 25%), enemy target ring, damage to allies | `ui_danger` | `#E85A44` | 1.0 |
| Healing numbers | `ui_heal` | `#9FF0B8` | 1.0 |
| Text shadow | `night_sky` | `#050A14` | 0.6, offset (0, 2) px, blur 4 px |

**Panel recipe:** a vertical gradient from `ui_panel_deep` to `ui_panel_low`, a 1 px inner rule of `ui_line_white` at 0.18 inset by 3 px, and a 1 px outer frame of `ui_line_gold` at 0.85. Optionally, add a background blur of the screen behind (a 6 px radius, through a `BackBufferCopy` shader), which is disabled on the Low preset. A soft gradient highlight sits along the top edge: the top 24 px lighten to `ui_panel_raised` at 0.25 to suggest light on the water's surface.

**Gold discipline:** gold is for **lines, icons, and the focused item only**. It is never a fill larger than 4 px across. It may not exceed **2% of the screen area** in any menu state.

---

## 2. Line Weights (at 1080p)

Scale every weight by `round(viewport_height / 1080)`, with a minimum of 1 px, so lines stay crisp at 1440p (×1, then ×2 at 2160p). **Never draw fractional lines.**

| Line | Weight | Color |
|---|---|---|
| Panel outer frame | 1 px | `ui_line_gold` at 0.85 |
| Panel inner rule | 1 px | `ui_line_white` at 0.18 |
| Row separators | 1 px | `ui_line_white` at 0.10 |
| Focused element frame | 2 px | `ui_line_gold` at 1.0, plus a 6 px outer glow in `ui_focus` at 0.35 |
| Timeline current-actor frame | 2 px | `ui_focus` |
| Gauge borders | 1 px | `ui_line_white` at 0.35 |
| Icon strokes (on a 48 px icon grid) | 2 px, round caps, miter joins | Per context |

---

## 3. Corner Treatment: the "Tide-notch"

An original corner system, built to avoid both the rounded-rectangle windows of the inspiring game and generic flat cards:

- **Panels are rectangles with 0 px radius on two corners and a 45° chamfer of 10 px on the other two: the top-left and bottom-right corners only.** This is the costume asymmetry principle applied to UI. Small panels (< 160 px tall) use a 6 px chamfer.
- The gold frame line follows the chamfer. At the midpoint of each chamfer sits a **lamp-node**: a 3 px gold dot with a 4 px glow at 0.3, the one ornament allowed per corner.
- Tabs (the speaker name, menu category) sit on the top-left chamfer and share its angle.
- **No drop shadows** behind panels. Depth comes from translucency and blur only.

**Cursor:** not a pointer glyph. The focused row gets a `ui_panel_raised` fill, a 2 px gold frame, and a **lamp mote**: a soft 10 px dot of `ui_focus` with a gold core, set 14 px left of the row text. It "breathes" (alpha 0.75 to 1.0 over 2.4 s, sine).

---

## 4. Typography

### 4.1 Recommended families (both SIL Open Font License 1.1; UI fetches them and logs PROVENANCE rows. Art has not downloaded anything.)
1. **Cormorant Garamond** (serif, by Christian Thalmann): for titles, chapter cards, speaker names, Vowbound and boss names, and location banners.
   *Why:* a high-contrast Garamond-derived display serif with long, elegant ascenders and calligraphic italics. It reads as liturgical and old without being gothic, which suits a faith-and-song story. It has a deep weight range (Light to Bold), true italics, small caps, and Latin Extended, Cyrillic, and Vietnamese coverage, which helps localization. **Its limit:** a small x-height makes it weak below about 24 px, so it's used only for display.
2. **Source Sans 3** (sans, by Paul D. Hunt for Adobe): for dialogue body text, menus, numbers, the battle HUD, tooltips, and settings.
   *Why:* a humanist sans built for screen UI. It has open apertures that read at TV distance, **tabular figures** (essential for HP and damage columns that must not jitter), a full weight range with italics, and wide script coverage (Latin Extended, Greek, Cyrillic, Vietnamese). It's calm and neutral beside Cormorant's flourish.
   *Fallback pairing if review rejects these:* EB Garamond plus Inter (also both OFL).

### 4.2 Sizes at 1080p (scaled with the text-size setting: 100 / 115 / 130%)
| Role | Family and weight | Size / line height | Tracking |
|---|---|---|---|
| Title, chapter card | Cormorant Garamond Light | 72 / 80 px | +2% |
| Location banner, boss name | Cormorant Garamond Medium, small caps | 40 / 48 px | +8% |
| Speaker name tab | Cormorant Garamond SemiBold, small caps | 28 / 32 px | +6% |
| Dialogue body | Source Sans 3 Regular | 30 / 41 px | 0 |
| Menu items, commands | Source Sans 3 Medium | 26 / 36 px | +1% |
| HUD numbers (HP, MP) | Source Sans 3 SemiBold, **tabular** | 24 px | 0 |
| Rank and cost labels | Source Sans 3 Bold, tabular | 20 px | +4% |
| Damage numbers | Source Sans 3 Bold, tabular, with a 2 px outline of `night_sky` | 44 px (crit 56 px) | 0 |
| Help line | Source Sans 3 Regular, italic for flavor text | 24 / 32 px | 0 |
| **Minimum anywhere** | | **22 px** | |

---

## 5. Motion Timings

The motion is calm. Nothing bounces, and nothing overshoots (except damage numbers, below).

| Event | Duration | Easing | Properties |
|---|---|---|---|
| Panel open | 180 ms | ease-out cubic | alpha 0→1, scale 0.98→1.00, translate 8 px up |
| Panel close | 120 ms | ease-in cubic | the reverse |
| Cursor move between rows | 90 ms | ease-out quad | fill and frame slide, lamp mote follows with a 30 ms lag |
| Sub-menu push | 200 ms | ease-in-out cubic | the new panel slides 24 px from the right, and the old one dims to 0.5 |
| **Timeline reorder (on a real turn)** | 240 ms | ease-in-out quart | chips slide to their new slots, staggered 15 ms |
| **Timeline preview (hovering an action)** | 120 ms in, 90 ms out | ease-out | a ghost chip appears at its preview slot, and affected chips shift with a 50% ghost trail |
| Turn start | 300 ms | ease-out | the current-actor chip pulses once (scale 1.0→1.06→1.0), and the party bar row highlights |
| Damage number | rise 36 px over 700 ms, then fade over 250 ms | ease-out cubic, with a 6% scale pop at 0–80 ms | |
| Dialogue box open | 220 ms | ease-out cubic | alpha plus a 12 px rise |
| Typewriter reveal | default 45 characters per second (setting 25–90 or instant) | linear | punctuation holds: `,` 80 ms, `.?!` 220 ms, `…` 400 ms |
| Lamp mote breathing | 2.4 s period | sine | alpha 0.75–1.0 |
| Screen transition (field to battle) | 600 ms | custom (the Rendering shader) | out of scope here; owned by Rendering and Architect |

**Reduced-motion setting:** translations are halved, breathing and pulses are removed, and timeline reorder becomes a 120 ms cross-fade.

---

## 6. Battle HUD Layout (SPEC §7.6), 1920 × 1080 Reference

The safe margin is **48 px** on all sides. Coordinates are top-left x, y and width × height, in px.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ [Target info 48,48 480×96]   [Help line 560,48 800×48]                    │
│                                                        [Timeline         │
│                                                         1704,96          │
│                (battlefield: ground rings on targets)    168×680]        │
│                                                                          │
│ [Command menu                                [Party bars                 │
│  48,760 480×272]                              1272,800 600×232]          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 6.1 Turn-order timeline (right side; pillar 4: always visible)
- **Panel:** at (1704, 96), 168 × 680, with a tide-notch.
- **Slot 0 (acting now):** a chip of 168 × 72 with a 64 × 64 portrait, the name in Source Sans 3 Medium at 22 px, and a 2 px `ui_focus` frame.
- **Slots 1–15:** chips of 168 × 36 at a 40 px pitch, starting at y = 180, so the last chip ends at y = 776. Each has a 32 × 32 portrait and the name at 22 px. **That makes 16 turns visible**, as SPEC §6.1 requires.
- **Ally or enemy coding, without relying on hue (a colorblind requirement):** an ally chip has a square left edge and a fill of `ui_panel_raised`. An enemy chip has a **chevron-cut left edge** (pointing left, 8 px) and a fill of `#2A1420` at 0.85, with its name in `ui_danger`. A Vowbound chip has a double gold frame.
- **Preview:** while an action is highlighted, a **ghost chip** of the actor (alpha 0.5, with a dashed 1 px gold frame) appears at its predicted slot. Chips that move get a small arrow glyph (▲ or ▼, 10 px, `ui_text_dim`). Delay-attack previews on enemies show the enemy's ghost moving down in `ui_focus`.
- **Rank cost:** shown in the command menu's right column as `R1`–`R5` (Bold at 20 px). Rank 3 and up is in `ui_swell` color.

### 6.2 Party bars (bottom right)
- **Panel:** at (1272, 800), 600 × 232. There are 3 rows of 72 px with an 8 px pitch gap.
- **Each row:** name (Medium at 24 px, 180 px wide), HP number and bar (220 px; the bar is 6 px tall), MP number and bar (120 px; bar 4 px), and the Swell gauge (64 px wide, 4 px tall, `ui_swell`; when full it glows with a 1.6 s sine pulse). Status icons sit in a 24 px strip above the bars, up to 6 icons.
- Low HP turns the HP number and bar to `ui_danger`, and adds a bar pattern of 2 px diagonal hatching (again, not hue alone).
- Reserve members are listed in the swap menu only, not here (the HUD shows 3 active fighters).
- **Full Swell gauge frame (M1-UI-05; recorded here by M1-NIT-01).** Besides the 1.6 s sine pulse, a full gauge is framed, so "full" is a shape cue and not hue alone: a 2 px `outline` (night) gap, then a 2 px `text` (white) line outside the bar. Both edges of the gap clear 3:1 against any fill. With reduced motion the pulse holds at full glow and the frame stays. The gauge sits under the name, not in its own column (tech/ui.md deviation 8 has the sizes and the reason for 2 px).

### 6.3 Command menu (bottom left)
- **Panel:** at (48, 760), 480 × 272. A header tab with the actor's name (Cormorant at 28 px) sits on the top-left chamfer. Up to 6 rows at 40 px pitch. The right column shows the rank cost and MP cost (tabular).
- Sub-menus (skills, items) push to the right over the battlefield, at a maximum width of 560 px.
- The swap command is always the last row, labeled with a two-arrow icon and the text "Swap".

### 6.4 Target highlights (ground-ring shader)
- The ring sits on the ground under the target, at a radius of 1.4 × the target's collision radius and a line width of 0.06 m (world space). It gets a soft inner gradient 0.25 m wide, rotates at 12°/s, and has 6 small notch-gaps, so it is never a plain circle.
- Color: `ui_focus` for ally targets and `ui_danger` for enemy targets. A multi-target selection pulses the rings in sequence (80 ms stagger).
- The target's name and HP band (if Read) appear in the target info panel at the top left (48, 48), 480 × 96.

### 6.5 Help line
At (560, 48), 800 × 48, a single line: the action's description and its effect on turn order ("Delays target 2 turns").

---

## 7. Dialogue Box and Field UI
- **Dialogue box:** at (320, 812), 1280 × 220 (bottom center), with a tide-notch. The speaker-name tab sits on the top-left chamfer. There are 3 lines of body text at most, and the advance indicator is a lamp mote at the bottom right. In cinematics with letterboxing on, the box sits *over* the lower bar.
- **Location banner:** centered at the top. Cormorant at 40 px, between two 1 px gold rules 320 px long, fading in over 600 ms, holding 2.5 s, then fading out over 800 ms.

## 8. Iconography
- An original SVG set on a 48 px grid with a 2 px stroke, plus fills only for status icons (a flat tint at 0.35 behind the stroke).
- Motifs come from our world: shells, knots, lamps, waves, and cords. Element icons are original glyphs (Water a wave with three ticks, Fire a stepped ember, Lightning a kite line, Ice a knot, Holy a ring, Glimmer a rising mote).
- No icon may copy the shapes of the inspiring game's icons. When in doubt, the reviewer decides, and the icon is redesigned.

## 9. Accessibility (summary; UI owns the details)
- Every state carries a shape or pattern cue as well as hue (chips, low HP, targets).
- There is a colorblind palette swap option: `ui_danger` becomes `#F08A24` (orange), and the enemy chip fill becomes `#2A2414`. Text contrast is at least 4.5:1 against the panel's worst case (white on `ui_panel_deep` at 0.80 over a `sun_noon` background measures about 8:1).
- Text size runs 100 to 130%, there is a reduced-motion option, and the typewriter can be set to instant.

## 10. Swell Input, Read Panel, Opening Banner and Bestiary (M2-ART-01)

Accepted from tech/ui.md deviations 8–12 after Art review on 2026-10-24 (the measurements are in M2-ART-01's Review log). Changes Art asked for are in M2-UI-08. Layout numbers are in `game/data/ui/battle_hud.json` (`swell_ring`, `read_panel`, `enemy_page`, `opening_banner`) and `game/data/ui/bestiary_menu.json`. The 1080p reference applies, as in §6.

### 10.1 Swell gauge (deviation 8)
- The gauge is **64 × 4 px under the hero's name**, bottom-aligned with the HP and MP bars. Only heroes with a Swell draw one. This replaces the separate column §6.2 assumed.
- **Full** adds a 2 px `outline` (night) gap, then a 2 px `ui_line_white` line, outside the bar, plus the 1.6 s pulse. It is 2 px and not 1 px because 720p draws the 1080p layout at 2/3 scale. Measured on `battle_swell_ring`: white `#F2F5FA`, gap `#050A14`, fill `#F5C771`–`#F6CC7F` (`ui_swell` with its glow). Full is a shape cue and not hue alone.

### 10.2 Swell input panel (deviation 9)
- The input panel takes **the command menu's place** (48, 700, 480 × 332), and the menu hides while it is open. It never covers the fighters or the timeline (pillar 4). It is a tide-notch panel. The technique name is the header (Cormorant small caps), and the hint is a help line at the foot.
- **The ring** has a lamp at the centre, a `ui_line_gold` rim on the lamp's edge, and a closing `ui_focus` ring. The pips are hollow diamonds while they wait. The next beat's pip is outlined in `ui_focus`, and the later ones in `ui_text_dim`. A perfect beat is a filled `ui_swell` diamond with a gold halo, a good one a filled `ui_focus` diamond, and a miss a `ui_danger` cross. A graded beat therefore differs in shape and fill as well as hue.
- **The lamp at rest must still read as lamplight**: a dim warm ember, never a grey or olive disc and never a grey halo (M2-UI-08). The flare toward the peak is the timing cue and carries the brightness. The rest state carries only the hue.
- **Timing-assist tag:** `DimLabel` at the panel's top left under the header, 150 px wide and wrapping to at most two lines ("Assist: misses count as Good"). It stays clear of the ring's outer radius. While an assist is on, it is the only text besides the title and the hint.

### 10.3 Read panel and bestiary page (deviation 10)
- **Read panel:** at (560, 128), 800 wide, between the help line and the command menu. It never overlaps the timeline. It uses the standard panel recipe, translucent over the battlefield. Body text measures 10:1 to 12:1 against its fill and the lore 6.7:1, with a fighter behind it. Its parts are a header (the name in Cormorant small caps, the level in `ui_text_dim` on the right), a numbers line, the stat grid (labels `ui_text_dim`, values `ui_line_white` tabular), a 1 px separator, the affinity facts (label dim, value white; "None" dim), the lore in italic, and the close hint in dim on the right.
- **Bestiary page** (out of battle): a full-screen panel over a `night_sky` scrim, with the list on the left and the same `EnemyPageView` on the right, so the page in battle and the page in the book are one design. An unread foe says "Not Read" in words. That is the shape cue, so the state is never shown by colour alone.
- **Defeat counts (`×N`) are `ui_line_white` when the foe has been Read and `ui_text_dim` when it hasn't, never `ui_focus`** (M2-UI-08). `ui_focus` means "this is where you are or who acts" (cursor, focus, current actor, ally target). The one standing exception is the "No time" cost word (M1). A teal count in the list would compete with the cursor row.

### 10.4 Opening banner (deviation 11)
- This is §7's location banner, shortened for battle: 0.3 s in, 1.8 s hold, 0.5 s out. It sits at (560, 156), 800 × 120, under the help line, and never covers the timeline.
- **Band:** `ui_panel_low` at 0.72, fading to nothing over the outer 22% at each side. It is a band, not a panel: no frame, no chamfer. Measured over the noon sky, the band reads `#324253`. The title (`#F2F5FA`) is 9.4:1 against it and the caption 9.0:1.
- **Rules:** two 1 px `ui_line_gold` rules, 320 px, above and below the title. The rule ends carry the timeline's side shapes: **squares for First Strike** and **outward chevrons in `ui_danger` for Caught Unaware**. So the opening is read by shape as well as by the danger hue. The caption ("Every foe acts before your party.") sits under the lower rule, and it is what makes the order legible.
- It never takes input and never holds the battle.

### 10.5 Swell root row and fill-mode rows (deviation 12)
- A Swell hero's root menu always shows the **Swell** row. Below full, it names the fill mode in force on the right, in `ui_text_dim`. At full, it names the input in `ui_swell`.
- **The Swell page** lists the techniques (disabled at 0.5 until full), then one row per unlocked fill mode. The mode in force says **"In use"** in `ui_swell` (7.2:1 on the panel). The others say **"No time"** in `ui_focus` (5.6:1 on the raised row), the same word and colour as the Swap row, because choosing a mode costs no turn. The help line names the mode and repeats "Choosing it costs no time", and the timeline shows no ghost.
- IP note: fill modes are presented as plain rows on our own Swell page, with original names and no per-mode use counters or separate mode screen. Keep it that way.
