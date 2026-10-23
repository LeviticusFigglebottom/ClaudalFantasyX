---
id: M1-ART-04
title: Make the art numbers renderable: on-screen targets, absorption, exposure units
role: character
status: done
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
- 2026-10-23 rendering (review-sweep-C): **approve with fixes**. **The onscreen_hex values reproduce exactly.** I ran `swatch_measure.tscn` in a clean copy (llvmpipe, 45 s) and compared all 195 values (65 swatches × k 0.5/1/2) against palette.json: max difference 0/255. The 34-step ladder also matches. The exposure conversion is sound as a *fitted practical mapping*: 0.65·2^((15−EV)/10) gives EV 15 → 0.65, 7.5 → 1.093 (rounds to 1.1), 6 → 1.21 (1.2), and 11 → 0.857 (0.85), all as stated, and it passes through both validated settings. **The sea-glow rule is reachable for moonlit frames.** I fitted the water_night numbers: sea = 0.068·moon + 0.130·glow and stone = 0.295·moon, in linear luminance from the measured hexes. At the authoring limit moon = 2.5 × glow, that gives stone/sea ≈ 2.46 (≤ 2.5) and glow on/off ≈ 1.76 (≥ 1.5), so (b) implies (a). Ch9 (0.35 against 0.15) passes.
  - should-fix: color_script.md:41 (rule 3b) only constrains the **moon**. Night frames keyed by a practical source break the stated "every night frame" value order. Ch4 (lamp key 1.2, sea-glow 0.12), Ch5 (lamp 1.6, 0.08) and Ending, the lifting (glimmer key 0.8, 0.08) all light stone about 5–15× brighter than the glowing sea. Either state that practical-lit pools are exempt, like the character rims are, or give (b) a per-key-type rule. Otherwise reviewers of Ch4/Ch5 shots will fail them against rule 3.
  - should-fix: color_script.md:74 versus the frame at 583+. The strip summary gives "Ending, lifting" a sea-glow of 0.15 → 0, but the frame row says 0.08. act3_ending.md §0 rule 4 also says 0.15 → 0.0 across E1–E5. This number is the game's final payoff, so pick one.
  - nit: ADR 0014 calls the formula a "conversion". It is a two-point fit that compresses 7.5 EV of intent into 0.75 stop. Say so, and note that frames between the two validated points (dusk 0.85, Ch20 1.10) are unvalidated until their mood frames exist.
  - nit: rule 3's "ratios hold at any exposure" is only approximately true after AgX (it is near-linear below mid grey, where night values sit). Also, the 2.5× guarantee assumes a coral-stone albedo: a `gauze_white` sand or wall at the same moon exceeds it. Name the albedo assumption.
  - nit: all measurements are lavapipe. Re-run `swatch_measure` on the GPU runner (M1-QA-01) before treating onscreen_hex as final.
- 2026-10-23 lead: closing on review-sweep-C approve-with-fixes; follow-ups are in M1-NAR-08 (art-doc section).
