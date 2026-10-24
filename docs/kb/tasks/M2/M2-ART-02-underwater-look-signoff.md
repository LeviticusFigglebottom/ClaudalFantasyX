---
id: M2-ART-02
title: Art sign-off on the underwater look (M2-RND-02)
role: character
status: done
owner_session: "env-art"
depends_on: [M2-RND-02]
milestone: M2
request-from: rendering
---
## Goal
M2-RND-02 built the underwater look (docs/kb/tech/underwater.md); its acceptance asks for Art's sign-off. Key
frames are in `docs/kb/qa/gpu/rnd02/` (RX 9070 XT, High): `below_high`, `window_high`, `waterline_high`,
`below_night_high` and `below_low`. The test scene is `game/levels/_tests/underwater/underwater_test.tscn`. As for M2-ART-01, the Art Director takes this under the character role.

## Acceptance criteria
- [x] Judge the colours: the water's transmittance (`turquoise_shallow` at 20 m), the scatter (`turquoise_shallow` fading to `abyss_navy`), the Snell window (`sky_zenith_noon`) and the total internal reflection (`sea_glow`), against the color script for Ch2's lagoon. Name any swatch to change in `game/data/vfx/underwater.json`.
- [x] Rhen's lantern: is the night halo warm enough? It reads greenish, because water strips the lamp's red over a few metres. Rendering can lower the red absorption or warm the fog's albedo (`god_rays.albedo_white_mix`).
- [x] **Glimmer motes underwater:** decide whether held or released motes should be boosted when submerged. At noon they are faint by design, and the in-scatter hides them beyond a few metres. Act III's "abyss of glimmer" probably wants them boosted. Rendering implements the call.
- [x] Sign off, or list the changes, in this task's Review log.

## Review log
- 2026-10-24 Art Director (env-art): **approve with fixes** (filed as M2-RND-09). I looked at all five GPU key frames in `docs/kb/qa/gpu/rnd02/` and the three `underwater_*` lavapipe baselines. The numbers are Oklab channel medians of sampled regions (960×540), compared with palette `onscreen_hex`. Ch2 is lit at the lagoon's water look, `lagoon_clear` (scatter `lagoon_teal`, deep `deep_teal_shadow`, Act I hue 198–213°).
  - **Transmittance and scatter (`turquoise_shallow`): change.** The mid-water away from the sun is right. Upper-left `#156D75` (h 204°) is ΔE 0.020 from `deep_teal_shadow` +1 `#106776`, which is exactly the lagoon's > 15 m band (`#186D7B`). But the lower water `#0C615F` (h 192°), the floor `#11786D` (h 183°) and the sun-side water `#288C81` (h 184°) drift green. `turquoise_shallow` keeps more green than blue (lin G 0.63 > B 0.58), so long paths go green, and Act I's water is teal-to-blue. **Change:** `scatter` and `transmit` to **`lagoon_teal`**, with `transmit_distance_m` **40**. That keeps σ_G about the same (0.023 → 0.025), lets blue outlast green (σ_B 0.024), and cuts red absorption (σ_R 0.150 → 0.107).
  - **Deep (`abyss_navy`): change the default to `deep_teal_shadow`, and keep `abyss_navy` for `night_sea` zones** (ch20, ch21, night dives), via a per-zone override. One deep colour cannot serve both an Act I lagoon and the Act III abyss.
  - **Snell window (`sky_zenith_noon`): approve.** The window measures `#2B7DAB` (h 238°), ΔE 0.048 from `sky_zenith_noon` 0 `#3B8AC0`. The edge is soft, and the sun disc and halo are clean.
  - **TIR (`sea_glow`): change the swatch, keep the value.** The TIR measures `#196775`, ΔE 0.012 from `sea_glow` 0, the right value for a reflection of the water column. But `sea_glow` is emission only, the anchored dead, and its absence is the last shot's payoff. So it must not be a day surface colour. `tir` → `deep_teal_shadow`, scaled to the same on-screen value. At night, `sea_glow` belongs in the column (rule 3), and it is missing: open night water reads `#002233` (h 235°, outside rule 3(c)'s teal band). Filed as RND-09 item 3.
  - **Lantern halo: not warm enough; it reads green.** Night: `#005D33` (h 155°, C 0.10) beside the lamp, `#035536` (h 160°) above it, `#0F4739` (h 172°) further out. Day: `#26907C` (h 177°). Oil light (`oil_lamp` on-screen 0 `#CFA67C`, h 67°) is the hero's light and the game's last light (rule 4, N-02). A green lamp loses Ch1's only warm/cool contrast against the held cyan motes. Physics yields to that. **Call:** `god_rays.albedo_white_mix` 0.5 → **1.0** for the lantern, plus the lower red absorption above. My arithmetic: oil × albedo × exp(−σd) at 5 m goes from (0.25, 0.32, 0.11), green, to (0.59, 0.39, 0.14), warm. **Target:** h 45–95° with C ≥ 0.04 within 0.5 m of the lamp, cooling to teal by 2–3 m, never in h 120–175°.
  - **Glimmer motes underwater: boost, for underwater cameras only.** I found 2–3 px dots at 5–15 m, lost in the haze. **Call:** compensate the path's transmittance on the mote emission: **1.0 for released (lift)** motes, because rising light must read through water (the Ch20 releases, the Letting, the Ending's motes rising out of the sea), and **0.6 for held** motes, which are meant to fade as they sink. Clamp at the swatch's +1, and keep the frame-fraction limits. The in-scatter haze still hides distant motes, so depth reads. Ch2's nine motes are seen from above the water and are unaffected. The abyss of glimmer gets no separate boost beyond ch20/21's own energies.
  - **Waterline: recapture.** `waterline_high`'s upper half is TIR (`#156074`, ΔE 0.034 from `sea_glow`), not air. The lavapipe `underwater_waterline` shows sky, sea and water. The GPU meniscus is a broken, aliased white streak.
  - **Low (`below_low`): approve as the fallback.** The water is a consistent h 210–212°, nearer the lagoon than High.
  - SPEC §8.2 item 2's caustics on characters are still open (tech/underwater.md). Not part of this colour sign-off.
