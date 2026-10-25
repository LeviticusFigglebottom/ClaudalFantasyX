# Art Direction (docs/kb/art)

Owner: Art Director (M1-ART-01, v0). This is the written art direction that the Rendering, Environment, Character, and UI agents build against. **It is words, numbers, and palettes only. There are no images in this folder, ever** (SPEC §2).

## Files
| File | What it is | Primary readers |
|---|---|---|
| [references.md](references.md) | The inspiring qualities in words: palette, values, silhouettes, costume asymmetry, architecture, sky, water by depth, light from the dead. Cultural influences and how to transform them. The "must NOT do" list. **The only file here that may name the inspiring game.** | Everyone |
| [color_script.md](color_script.md) | One key frame per chapter (Prologue through post-credits, 25 frames): sun, key, fill, and rim (hex, linear, K), sky, fog, water look, glimmer, sea-glow, exposure, contrast, saturation, LUT intent, emotional note. **The narrative light rules**, and the validated **water looks**. | Rendering, Environment, Cinematics |
| [palette.json](palette.json) | The machine-readable master palette (0.2.1): 77 named swatches. Each has an **input** value (`hex`, `linear`, luminance, temperature, family, `input_kind`) and, except UI, its measured **on-screen** value (`onscreen_hex` at −1 / 0 / +1). Also role, usage limit, global rules, the measured tonemap ladder, and per-act palettes. | Rendering (LUT and validator tools), UI, Character, Environment |
| [characters/asha.md](characters/asha.md) | The M1 hero design sheet, and the home of the **shared** conventions: face-shape API, emotion mapping, mask packing, budgets, procedural build. | Character, Rendering, Cinematics |
| [characters/rhen.md](characters/rhen.md) | Rhen's design sheet (deltas from Asha). | Character |
| [characters/toma.md](characters/toma.md) | Toma's design sheet (deltas from Asha). | Character |
| [environments/haluna.md](environments/haluna.md) | The vertical-slice mood brief: Haluna, the Saltgrass Causeway, and the Shell Shrine. Kits, materials, the weathering stack, vegetation, and **30 composed shots** (M1-ENV-01 uses the five marked ◆). | Environment, Rendering |
| [ui.md](ui.md) | UI art rules: colors, line weights, tide-notch corners, fonts, motion timings, and the battle HUD layout in px. | UI |

Planned (not in v0): `vowbound/` sheets (SPEC §7.5), the other four party sheets, and mood briefs per zone as each enters production.

## Cross-role conventions set here (Rendering and Character, read these first)
1. **Color pipeline:** hex is sRGB-encoded, and `linear` is the sRGB EOTF of it. Lights use the stated blackbody K. The tonemapper is AgX (white 12, contrast 1.25), followed by a per-frame LUT. Exposure is `tonemap_exposure` in Godot's default light units ([ADR 0014](../decisions/0014-light-units-exposure.md)). **Palette and color-script hexes are inputs. What the screen must show is `onscreen_hex`** (see "Two kinds of colour value" below). No neutral-grey shadows and no (0, 0, 0) black point.
2. **The glimmer meaning rule:** rising + warm `glimmer_lift` = released, sideways/down + cool `glimmer_held` = held, and still `glimmer_bound` = bound: machines **and the Vowbound**. Ilun in his chamber and every summon are lit as bound light (steady, never drifting, moving only with their own form) until their Act III release ([decisions_log N-05](../story/decisions_log.md); color script rule 2). Oil flame (`oil_lamp`) is none of these: it is honest light, and Rhen's lantern burns oil ([N-02](../story/decisions_log.md)). **The night sea-glow** (`sea_glow`, energy 0.04–0.15, and ≥ 0.08 once the sun is below −6°) is in every night frame until `ending_dock`, where it is exactly 0. At night it is the brightest *water* value, not the brightest value in the frame (color script rule 3).
3. **Texture packing:** `*_clothmask` is R embroidery, G gold thread, B lacquer, A sheen. `*_orm` is AO, roughness, metallic. Stone vertex colors are R moss, G salt, B wet, A erosion, plus a global `tide_line_y` and water-height uniform.
4. **Face API:** 32 shared shape names plus 10 visemes, with the 15 dialogue emotion tags mapped per character.
5. **Frame-area limits:** gold ≤ 5%, lacquer red ≤ 8%, and glimmer ≤ 3% by day, ≤ 12% by night, ≤ 35% at set-pieces. Albedo stays within `#1D1916` to `#EBE7DF` (excluding foam and emissives).
6. **Camera:** lens in full-frame mm, and Godot's vertical FOV = 2·atan(12/mm). World north = −Z.

These conventions affect more than one role. The Lead may want to fold items 2–3 into an ADR.

## Two kinds of colour value (M1-ART-04)
Rendering's M1-ART-01 review showed that a palette hex rendered through AgX doesn't come back as itself: `#3FD0C9` came back `#62B7B3`. So every swatch now carries two values. Don't mix them up.

| | **Input value** | **On-screen value** |
|---|---|---|
| Fields | `hex` (sRGB) and `linear` | `onscreen_hex` `{"-1", "0", "+1"}` |
| What it is | What you **type in**: albedo, light color, sky color, emission color, water shader color (`input_kind` says which) | What that input **shows** after exposure and the AgX tonemap, before the LUT, at key product k = 0.5 / 1 / 2 |
| Where it comes from | Art direction (chosen) | **Measured** on the swatch card (`game/levels/_tests/swatches/swatch_card.tscn`, shot `swatch_card`). Never hand-typed. |
| Used for | Building materials, lights, skies | Reviewing screenshots and captures |

- **k, the key product,** is `tonemap_exposure × incident light`. That's key energy × N·L, plus fill, for albedo; emission energy for emissives; `sky_energy_multiplier` for sky colors. Light-color swatches are shown as a white card lit by that light. Each frame's exposure and key are in the color script: Act I noon is 0.65 × 3.2 ≈ 2 (+1), a moonlit surface is about 0.3, an oil-lamp pool about 1.3. Exposure and light are interchangeable: exposure 2 on a value is pixel-identical to level 2 at exposure 1 (measured).
- **UI swatches** (`input_kind: ui_final`) are drawn after the tonemap, so their hex is already the on-screen value. They have no `onscreen_hex`.
- **The water ramp** (`turquoise_shallow` … `deep_teal_shadow`) holds **inputs**. That answers Rendering's question. Its on-screen targets are its `onscreen_hex`, and the LUT does **not** add cyan saturation to make the screen match the input hex. A frame's saturation is its color-script "Saturation", nothing more.
- **The tonemap, measured** (AgX, white 12, contrast 1.25, exposure 1; the full 34-step ladder is in `palette.json` `onscreen_reference.tonemap_ladder`):

| Linear in | 0.004 | 0.011 | 0.031 | 0.088 | 0.18 | 0.25 | 0.5 | 0.71 | 1.0 | 2.0 | 4.4 | 9.5 | ≥ 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| On screen | `#060606` | `#131313` | `#2B2B2B` | `#515151` | `#757575` | `#888888` | `#ADADAD` | `#BDBDBD` | `#CBCBCB` | `#E1E1E1` | `#F2F2F2` | `#FCFCFC` | `#FFFFFF` |

  Below mid grey AgX is close to plain sRGB encoding, and 0.18 lands at 46% either way. Above it AgX compresses: linear 1.0 reads 80%, not white, and white needs 12. Saturated colors lose chroma as they brighten (`#3FD0C9` → `#6FB8B5` at k 1 → `#9CD4D2` at k 2). Darks hold their hue (`#0E4A55` → `#014652`).
- **Re-measure** whenever a swatch's hex changes. Run `godot-render --path . --audio-driver Dummy --fixed-fps 60 res://game/levels/_tests/swatches/swatch_measure.tscn -- --out=/abs/path.json`, copy the three hexes into `onscreen_hex`, and re-approve the `swatch_card` baseline in the same commit. Passing `--exposure=0.9 --saturation=1.12` reproduces Rendering's review numbers to within 2/255.

## How to pick a value (environment and character artists)
1. **Pick the swatch by role.** Use the `family`, `role` and `usage_limit` in `palette.json`, and type its **`hex`** into the material, light or shader field. Never type an `onscreen_hex` into anything: that double-counts the tonemap and comes out too dark and too grey.
2. **Find your frame's k** from the color script or the zone brief: exposure × key energy. That tells you which `onscreen_hex` column to expect on a surface facing the key (−1 / 0 / +1 = k 0.5 / 1 / 2). The shadow side sits at the fill's k, usually −1 or lower. Use the tonemap ladder above to interpolate between columns.
3. **Check a capture, not the material preview.** Sample a front-lit patch and compare it with that column. A close match (ΔE_ok ≲ 0.05, or "same hue, same value step" by eye in the grayscale value check) is right.
4. **If it reads wrong, fix the cause:**
   - *Wrong hue:* wrong swatch, or a light color off its stated K.
   - *Too bright or too dull overall:* the frame's k is wrong. Light energy and exposure are coupled, so change them in the frame (color script), not in the albedo.
   - *Too bright or too dull on one material:* that's a material choice. Pick a neighbouring swatch, or propose a new one.
   - Never push an albedo past `gauze_white` `#EBE7DF` or below `lacquer_black` `#1D1916` to fix exposure.
5. **Characters.** Skin, hair and cloth are checked at the key's k for the lit side and the rim's k for the edge. A rim pushing past +1 is a highlight and should roll off to cream, which AgX does. Faces keep the fill within 1.5–2 stops of the key where the shot sheet says so (k ratio ≤ 3–4).
6. **Emissives** (glimmer, flames, sea-glow) read at k = exposure × emission energy. Mote energies of 0.6–6 run past +1 into white-hot cores that bloom; the hue lives in the halo. Sea-glow at 0.04–0.15 sits far below −1 by design, which is why color script rule 3 judges it by ratios, not by brightest value.
7. **Water.** Don't author absorption numbers. Pick a **water look** from the color script ("Water looks"), set its `absorption_scale`, and compare the depth bands with that look's validated on-screen values. To change a look, rerun `water_look_probe.tscn` and record the new numbers in the same commit.
8. **New swatch?** Add `hex`, `linear` (EOTF, 4 places), luminance and `input_kind`, re-measure, and grep the art docs for any old hex.

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
- **Rendering:** a nacre thin-film option for the Shell Shrine. The cost of keeping sea-glow at ≥ 0.04 on the Low preset. New from M1-ART-04: (a) from high cameras at noon, the SSS crest term (`col_sss`) paints the 62 m swell as large pale-turquoise patches over deep water; consider fading it with view elevation. (b) `docs/kb/tech/dialogue_format.md` lists the `grades` set and needs `ch03_steps` added (it is in `cues.json` now; that tech doc isn't Art's to edit). (c) Mood-frame `.tres` files should set `tonemap_exposure` from the color script's Exposure column (ADR 0014).
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
- `palette.json` is the source of truth for colors. When a swatch changes, update the hex and recompute `linear` with the sRGB EOTF (`c/12.92` if `c ≤ 0.04045`, else `((c+0.055)/1.055)^2.4`, for c in 0–1), **re-measure its `onscreen_hex`** (above) and re-approve `swatch_card`, then grep the art docs for the old hex. Bump `version`: minor for a schema or field change (0.2.0 added `input_kind`, `onscreen_hex` and `onscreen_reference`), patch for value changes.
- Every color script change gets a line in that file's review log, along with the screenshot baseline it affects.
