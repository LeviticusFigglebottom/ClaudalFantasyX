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
2. **The glimmer meaning rule:** rising + warm `glimmer_lift` = released, sideways/down + cool `glimmer_held` = held, and still `glimmer_bound` = bound: machines **and the Vowbound**. Ilun in his chamber and every summon are lit as bound light (steady, never drifting, moving only with their own form) until their Act III release ([decisions_log N-05](../story/decisions_log.md); color script rule 2). Oil flame (`oil_lamp`) is none of these: it is honest light, and Rhen's lantern burns oil ([N-02](../story/decisions_log.md)). **The night sea-glow** (`sea_glow`, energy 0.04–0.15) is in every night frame until `ending_dock`, where it is exactly 0.
3. **Texture packing:** `*_clothmask` is R embroidery, G gold thread, B lacquer, A sheen. `*_orm` is AO, roughness, metallic. Stone vertex colors are R moss, G salt, B wet, A erosion, plus a global `tide_line_y` and water-height uniform.
4. **Face API:** 32 shared shape names plus 10 visemes, with the 15 dialogue emotion tags mapped per character.
5. **Frame-area limits:** gold ≤ 5%, lacquer red ≤ 8%, and glimmer ≤ 3% by day, ≤ 12% by night, ≤ 35% at set-pieces. Albedo stays within `#1D1916` to `#EBE7DF` (excluding foam and emissives).
6. **Camera:** lens in full-frame mm, and Godot's vertical FOV = 2·atan(12/mm). World north = −Z.

These conventions affect more than one role. The Lead may want to fold items 2–3 into an ADR.

## Terms coined in this folder (glossary candidates; the Lead merges them)
| Term | Meaning |
|---|---|
| **sea-glow** | The faint ambient emission of the night sea, made by a thousand years of anchored dead. It's absent only in the final shot. |
| **held light / released light / bound light** | Art shorthand for anchored motes (cyan, sinking) versus lifting motes (gold, rising) versus still teal light locked into a housing or a Vowbound's form. |
| **wake-shell wall** | The shell-set wall at the Haluna end of the causeway where Cantors' wake-shells are placed: the Shell Shrine's outer wall (placement confirmed, [N-03](../story/decisions_log.md)). |
| **fan-shell roof** | The Shell Shrine's tiered stone roof of scallop-like fans. |
| **lamp-node / lamp mote (UI)** | The gold corner dot of the UI frames, and the breathing focus dot that replaces a cursor glyph. |
| **tide-notch** | The UI corner system: 45° chamfers on the top-left and bottom-right corners only. |
| **verse_count / sleeve states S0–S8** | The verse-sleeve embroidery states (technical term, not player-facing). |

## Open questions raised (by owner)
- **Narrative:** all four answered on 2026-10-22 in [decisions_log.md](../story/decisions_log.md):
  - ~~Asha's first reach-band after the Ch4 ferry.~~ **Resolved ([N-01](../story/decisions_log.md)):** one band, left forearm, earned on the Ch4 crossing (Toma inks it) and shown from Ch5; a second band only in the ending dock shot. The generator's band count is 0 → 1 (Ch5) → 2 (`ending_dock`).
  - ~~Whether Rhen's lantern flame is oil or bound glimmer.~~ **Resolved ([N-02](../story/decisions_log.md)):** oil (`oil_lamp`), never `glimmer_bound`, and it does not go dark at the Unbinding.
  - ~~Placing the wake-shell wall at the causeway head.~~ **Resolved ([N-03](../story/decisions_log.md)):** confirmed; it is the Shell Shrine's outer wall (haluna.md §1.2, H08).
  - ~~The ceremonial gold lash stroke.~~ **Resolved ([N-04](../story/decisions_log.md)):** approved as the **gilt line**, an Order-rite mark worn at Ch9, Ch13, Ch14, and Ch16 only. It is never worn in the vertical slice or in Act III; Asha wipes it off at the Choir.
  - New from Narrative, also adopted: the Vowbound are bound light ([N-05](../story/decisions_log.md)), and the Drownbell comes after the verse at ~18:15 ([N-07](../story/decisions_log.md); haluna.md §0).
- **Cinematics:** S8, the verse-sleeve unraveling into rising motes during the Letting. The "protective smile" layer (`smile` + `brow_inner_up` 0.25), which could become a new emotion tag `brave_smile` in `tech/dialogue_format.md`.
- **Rendering:** a nacre thin-film option for the Shell Shrine. The cost of keeping sea-glow at ≥ 0.04 on the Low preset.
- **Lead:** an ADR for the mask and vertex-color packing conventions. Narrative suggests folding N-05 (Vowbound = bound light) into the same glimmer-meaning ADR as convention 2.

## Palette check: vertical-slice `@vfx` cues (M1-ART-03, 2026-10-22)
Each cue in `ch02_girl_on_the_beach.dlg` and `ch03_the_first_verse.dlg` was checked against `palette.json` usage limits and the frame-area rules. The per-shot values are in color_script.md (`ch02` held motes, `ch03` glimmer by shot).

| Cue | Shot | Verdict |
|---|---|---|
| `glimmer_held at=rhen_shallows count=9 drift=down_seaward` | H06 | OK: held motes, energy 0.6, ≤ 1% (day limit 3%). |
| `glimmer_bound at=ilun_chamber form=ilun` | S08 | **Conflict, fixed:** `glimmer_bound` was limited to "emissive inserts only", so a Vowbound form was out of bounds. palette.json 0.1.1 adds Vowbound forms. S08 is a set-piece (target ≤ 15%). |
| `glimmer_lift at=asha motion=spiral_up rate=slow` | S09 | OK for the swatch. **Frame area:** at 85 mm a day frame (3%) is too tight, so S09 is a set-piece (target ≤ 10%, limit 35%). |
| `glimmer_held at=drownbell drift=down_seaward` | C08 | **Ambiguity, fixed:** `glimmer_held` listed "spawn wounds" while `spawn_wound` is "creature weak points only". Now the wound surfaces are `spawn_wound` and the motes they shed are `glimmer_held`. C08 ≤ 3% (the sun is up). |

Other conflicts found:
1. **`glimmer_held` listed "bound lamps"**, against color script rule 2 and N-02. Removed in palette.json 0.1.1. Bound lamps are `glimmer_bound`, and oil lamps are `oil_lamp`.
2. **Sea-glow 0.03** in `ch02`/`ch03` was under the `sea_glow` floor (0.04–0.15), and the shader gate clamps visible values to that range, so 0.03 could never render. Both are now 0.04.
3. **Requests to Rendering** (tech docs are not ours to edit): (a) the H06 field is fixed-count, so nine motes must survive the Low preset's `amount_scale` 0.35; (b) bound (`MACHINE`) motes need zero velocity *relative to their carrier*, so Ilun's light can move with his body in C10 without drifting; (c) `docs/kb/tech/glimmer.md` gives "Ch2 2.5" as an example `hymn_glimmer.a`. Ch2 is now 0.6, and 2.5 is Ch3.
4. No gold conflict: the slice has no `gold_leaf` on Asha (the gilt line is never worn in the slice, N-04) and none in the Shell Shrine (haluna.md §3.3). Sunset key light is not counted in the gold budget.

## Maintenance
- `palette.json` is the source of truth for colors. When a swatch changes, update the hex and recompute `linear` with the sRGB EOTF (`c/12.92` if `c ≤ 0.04045`, else `((c+0.055)/1.055)^2.4`, for c in 0–1), then grep the art docs for the old hex.
- Every color script change gets a line in that file's review log, along with the screenshot baseline it affects.
