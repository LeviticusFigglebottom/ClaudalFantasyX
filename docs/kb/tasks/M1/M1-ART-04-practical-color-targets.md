---
id: M1-ART-04
title: Make the art numbers renderable: on-screen targets, absorption, exposure units
role: character
status: review
owner_session: art-stream-3
depends_on: [M1-RND-01, M1-ART-03]
milestone: M1
request-from: "rendering"
reviewer: rendering
---
## Goal
Rendering's reviews found four art-direction numbers that fail in practice.

## Acceptance criteria
- [x] Hexes split into input albedo/emission values vs. on-screen (post-tonemap) targets
- [x] Water absorption numbers replaced with values validated in the water test scene
- [x] Exposure: an ADR on physical light units vs. Godot's default exposure, with the color script converted accordingly
- [x] Sea-glow brightness rule made reachable against moonlit stone values
- [x] Define the ch03_steps grade (needed by ch03_the_first_verse.dlg node `steps`)

## Notes
Sources: M1-ART-01 review log (rendering-stream-2), docs/kb/tech/water.md, the M1-NAR-04 report (ch03_steps grade).

Done (art-stream-3, 2026-10-23):
- **Swatch card** `game/levels/_tests/swatches/swatch_card.tscn` (new shot `swatch_card`, baseline approved).
  - `swatch_measure.tscn` reads the card back to JSON.
  - palette.json 0.2.0: every non-UI swatch keeps its input `hex`/`linear` and gains `input_kind` and `onscreen_hex` at k = 0.5 / 1 / 2 (AgX, white 12, exposure 1). The 34-step tonemap ladder is in `onscreen_reference`.
  - With `--exposure=0.9 --saturation=1.12` the tool reproduces Rendering's review numbers to within 2/255.
  - README gains "Two kinds of colour value" and "How to pick a value".
- **Water looks**: nine looks on the shared base σ (2.0, 0.5, 0.42) × `absorption_scale`.
  - Each was validated by `water_look_probe.tscn` (the water test scene, unmodified, plus the look and the frame's light), with per-depth-band on-screen values, in color_script.md "Water looks".
  - Act I clear water is ×1.5 (ΔE_ok ≤ 0.068 to the palette ramp).
  - Every frame's Water row and haluna.md now name a look.
- **ADR 0014**: stay on default light units. Exposure is `tonemap_exposure` = 0.65 × 2^((15 − EV100)/10), with EV kept as intent only. No Lead action.
- **Sea-glow**: rule 3 is now a night value order with three ratio checks: glow on/off ≥ 1.5×, moonlit stone ≤ 2.5× the sea (moon ≤ 2.5 × sea-glow energy), and teal hue. All were measured in `water_night`. Night frames use sea-glow ≥ 0.08. Ch9's moon goes 0.6 → 0.35.
- **ch03_steps**: full frame in color_script.md (Ch3 sub-frame) and haluna.md. It is in the `cues.json` grades, and the `steps` node uses it (recompiled).

Open, for other roles:
- `docs/kb/tech/dialogue_format.md`'s `grades` row needs `ch03_steps` (tech doc).
- SSS crest patches seen from high cameras (color_script.md, "Two findings for Rendering").
- `CameraAttributesPractical.exposure_multiplier` had no effect with physical units off.
- `game/levels/_tests/swatches/` should get an ownership line (Lead).

## Review log
