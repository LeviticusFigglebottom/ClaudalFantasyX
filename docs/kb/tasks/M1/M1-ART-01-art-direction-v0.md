---
id: M1-ART-01
title: Art direction v0: verbal references, color script, Asha design sheet
role: character
status: done
owner_session: art-stream-1
depends_on: [M1-NAR-01]
milestone: M1
request-from: ""
reviewer: rendering
---
## Goal
SPEC §7.1–7.3 foundations, in words and shader mood frames only (no reference images).

## Acceptance criteria
- [x] docs/kb/art/references.md: palettes, silhouettes, composition (words only)
- [x] docs/kb/art/color_script.md: one key frame per chapter
- [x] docs/kb/art/characters/asha.md design sheet

## Notes
- 2026-10-22 art-stream-1: delivered all of docs/kb/art/ (index in docs/kb/art/README.md). Beyond the criteria: palette.json (77 swatches plus per-act palettes), Rhen and Toma sheets, the Haluna, causeway, and shrine mood brief with 30 shots (◆ marks the five for M1-ENV-01), and ui.md (fonts: Cormorant Garamond plus Source Sans 3, both OFL).
- Reviewer focus (Rendering, SPEC §12.3): are the color script energies, EVs, and absorption coefficients plausible in Forward+ with AgX? Is the cloth, skin, and hair mask packing (asha.md §4.2) workable for M1-RND-04? Is the stone vertex-color convention (haluna.md §4) workable? Can sea-glow be kept at ≥ 0.04 on Low?
- Cross-role conventions that may need an ADR are listed in docs/kb/art/README.md. Glossary candidates are listed there too, for the Lead to merge.
- Size: about 17.8k words including tables, which is over the 8–12k guide. The overage is mostly per-frame data tables and shot lists.

## Review log
- 2026-10-22 rendering (rendering-stream-2, M1-RND-01 water): **approve with fixes**. The numbers are actionable: sun elevation/azimuth, key hex and energy, fill, the depth ramp, the sea-glow band and the compass convention all dropped straight into a scene and a rig. Four places failed in practice; each measured value comes from the `water_*` baselines.
  1. **Absorption triples don't reach the ramp.** With ch02 (R 0.45, G 0.065, B 0.045 m⁻¹), noon-lit water 0.3–1 m deep over sand rendered **#BFD8CD** (ramp #3FD0C9), 1–2 m rendered **#92C9D5** (ramp #1FA3A6), and the reef rendered **#61A3C5** (ramp #1569A0). That's near-white: AgX bleaches anything above ~1.0 linear, and sand under a 3.2-energy sun is ~2.7. The look needed **R 2.0, G 0.5, B 0.42** (with a Snell-corrected path) plus a two-tone scatter colour. After that, 0.5–1 m reads **#7BBEC1** and 1–2 m **#70B9BE**. The reef past the lip reads **#5689A4**: lighter than target, because Fresnel sky reflection at grazing angles is physical. Please restate the per-frame "water absorption" as look values (or as a multiplier on a shared base), not as physical water.
  2. **Hex targets are pre-tonemap.** The palette hexes rendered as unshaded swatches through the Act I grade (AgX, exposure 0.9, saturation ×1.12) come out as #3FD0C9 → **#62B7B3**, #1FA3A6 → **#329C9F**, #1569A0 → **#006C9F**, #0E4A55 → **#004552**, #EFDDB4 → **#C3B8A3**, and sky #2E7FD6 → **#2D85C3**. Say whether the ramp is an on-screen target (then the LUT must add saturation in cyans) or an input value. I compared against the AgX-mapped values.
  3. **EV100 isn't actionable** while physical light units are off (project default; CameraAttributesPhysical exposure needs them). I used `tonemap_exposure` 0.65 by day and 1.1 at night. Give exposure as a tonemap multiplier per frame, or decide on physical units (an ADR).
  4. **Night: "the glow is the brightest value" isn't reachable with these energies.** Sea-glow 0.12 × #1C6B78 is ~0.02–0.04 linear even with the full water column, while moon key 0.25 on white coral is ~0.12–0.17. In `water_night` the oil-lamp flame and its glints are the brightest values, then moonlit stone, then the shallow glowing water. It reads correctly as a faint teal sea under a navy sky, but the rule should say "brightest *water* value", or the moon fill on stone should be ≤ ~0.08.
  - Minor: ch02's "deep color" #1FA3A6 is lagoon teal, while references §1.7 puts > 15 m at #0E4A55 and 4–15 m at #1569A0. The shader now takes both (`col_scatter_shallow`, `col_deep`). There's also no swatch for a white coral lagoon floor; I used mortar #E6E1D6 under water. Wet sand #B59D74 reads correctly in the capillary band.
- 2026-10-23 lead: closing on Rendering's approve-with-fixes; the four practical fixes are tracked in M1-ART-04.
