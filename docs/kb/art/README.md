# Art Direction (docs/kb/art)

Owner: Art Director (M1-ART-01, v0). This is the written art direction that the Rendering, Environment, Character, and UI agents build against. **It is words, numbers, and palettes only. There are no images in this folder, ever** (SPEC §2).

## Files
| File | What it is | Primary readers |
|---|---|---|
| [references.md](references.md) | The inspiring qualities in words: palette, values, silhouettes, costume asymmetry, architecture, sky, water by depth, light from the dead. Cultural influences and how to transform them. The "must NOT do" list. **The only file here that may name the inspiring game.** | Everyone |
| [color_script.md](color_script.md) | One key frame per chapter (Prologue through post-credits, 25 frames): sun, key, fill, and rim (hex, linear, K), sky, fog, water absorption, glimmer, sea-glow, EV, contrast, saturation, LUT intent, emotional note. **The narrative light rules.** | Rendering, Environment, Cinematics |
| [palette.json](palette.json) | The machine-readable master palette: 77 named swatches (hex, linear, luminance, temperature, family, role, usage limit), global rules, and per-act palettes. | Rendering (LUT and validator tools), UI, Character, Environment |
| [characters/asha.md](characters/asha.md) | The M1 hero design sheet, and the home of the **shared** conventions: face-shape API, emotion mapping, mask packing, budgets, procedural build. | Character, Rendering, Cinematics |
| [characters/rhen.md](characters/rhen.md) | Rhen's design sheet (deltas from Asha). | Character |
| [characters/toma.md](characters/toma.md) | Toma's design sheet (deltas from Asha). | Character |
| [environments/haluna.md](environments/haluna.md) | The vertical-slice mood brief: Haluna, the Saltgrass Causeway, and the Shell Shrine. Kits, materials, the weathering stack, vegetation, and **30 composed shots** (M1-ENV-01 uses the five marked ◆). | Environment, Rendering |
| [ui.md](ui.md) | UI art rules: colors, line weights, tide-notch corners, fonts, motion timings, and the battle HUD layout in px. | UI |

Planned (not in v0): `vowbound/` sheets (SPEC §7.5), the other four party sheets, and mood briefs per zone as each enters production.

## Cross-role conventions set here (Rendering and Character, read these first)
1. **Color pipeline:** hex is sRGB-encoded, and `linear` is the sRGB EOTF of it. Lights use the stated blackbody K. The tonemapper is AgX, followed by a per-frame LUT. No neutral-grey shadows and no (0, 0, 0) black point.
2. **The glimmer meaning rule:** rising + warm `glimmer_lift` = released, sideways/down + cool `glimmer_held` = held, and still `glimmer_bound` = machines. **The night sea-glow** (`sea_glow`, energy 0.04–0.15) is in every night frame until `ending_dock`, where it is exactly 0.
3. **Texture packing:** `*_clothmask` is R embroidery, G gold thread, B lacquer, A sheen. `*_orm` is AO, roughness, metallic. Stone vertex colors are R moss, G salt, B wet, A erosion, plus a global `tide_line_y` and water-height uniform.
4. **Face API:** 32 shared shape names plus 10 visemes, with the 15 dialogue emotion tags mapped per character.
5. **Frame-area limits:** gold ≤ 5%, lacquer red ≤ 8%, and glimmer ≤ 3% by day, ≤ 12% by night, ≤ 35% at set-pieces. Albedo stays within `#1D1916` to `#EBE7DF` (excluding foam and emissives).
6. **Camera:** lens in full-frame mm, and Godot's vertical FOV = 2·atan(12/mm). World north = −Z.

These conventions affect more than one role. The Lead may want to fold items 2–3 into an ADR.

## Terms coined in this folder (glossary candidates; the Lead merges them)
| Term | Meaning |
|---|---|
| **sea-glow** | The faint ambient emission of the night sea, made by a thousand years of anchored dead. It's absent only in the final shot. |
| **held light / released light** | Art shorthand for anchored motes (cyan, sinking) versus lifting motes (gold, rising). |
| **wake-shell wall** | The shell-set wall at the Haluna end of the causeway where Cantors' wake-shells are placed (location proposal). |
| **fan-shell roof** | The Shell Shrine's tiered stone roof of scallop-like fans. |
| **lamp-node / lamp mote (UI)** | The gold corner dot of the UI frames, and the breathing focus dot that replaces a cursor glyph. |
| **tide-notch** | The UI corner system: 45° chamfers on the top-left and bottom-right corners only. |
| **verse_count / sleeve states S0–S8** | The verse-sleeve embroidery states (technical term, not player-facing). |

## Open questions raised (by owner)
- **Narrative:** Asha's first reach-band after the Ch4 ferry. Whether Rhen's lantern flame is oil or bound glimmer. Placing the wake-shell wall at the causeway head. The ceremonial gold lash stroke.
- **Cinematics:** S8, the verse-sleeve unraveling into rising motes during the Letting. The "protective smile" layer (`smile` + `brow_inner_up` 0.25), which could become a new emotion tag `brave_smile` in `tech/dialogue_format.md`.
- **Rendering:** a nacre thin-film option for the Shell Shrine. The cost of keeping sea-glow at ≥ 0.04 on the Low preset.
- **Lead:** an ADR for the mask and vertex-color packing conventions.

## Maintenance
- `palette.json` is the source of truth for colors. When a swatch changes, update the hex and recompute `linear` with the sRGB EOTF (`c/12.92` if `c ≤ 0.04045`, else `((c+0.055)/1.055)^2.4`, for c in 0–1), then grep the art docs for the old hex.
- Every color script change gets a line in that file's review log, along with the screenshot baseline it affects.
