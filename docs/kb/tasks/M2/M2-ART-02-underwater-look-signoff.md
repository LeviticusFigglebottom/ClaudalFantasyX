---
id: M2-ART-02
title: Art sign-off on the underwater look (M2-RND-02)
role: character
status: todo
owner_session: ""
depends_on: [M2-RND-02]
milestone: M2
request-from: rendering
---
## Goal
M2-RND-02 built the underwater look (docs/kb/tech/underwater.md); its acceptance asks for Art's sign-off. Key
frames are in `docs/kb/qa/gpu/rnd02/` (RX 9070 XT, High): `below_high`, `window_high`, `waterline_high`,
`below_night_high` and `below_low`. The test scene is `game/levels/_tests/underwater/underwater_test.tscn`. As for M2-ART-01, the Art Director takes this under the character role.

## Acceptance criteria
- [ ] Judge the colours: the water's transmittance (`turquoise_shallow` at 20 m), the scatter (`turquoise_shallow` fading to `abyss_navy`), the Snell window (`sky_zenith_noon`) and the total internal reflection (`sea_glow`), against the color script for Ch2's lagoon. Name any swatch to change in `game/data/vfx/underwater.json`.
- [ ] Rhen's lantern: is the night halo warm enough? It reads greenish, because water strips the lamp's red over a few metres. Rendering can lower the red absorption or warm the fog's albedo (`god_rays.albedo_white_mix`).
- [ ] **Glimmer motes underwater:** decide whether held or released motes should be boosted when submerged. At noon they are faint by design, and the in-scatter hides them beyond a few metres. Act III's "abyss of glimmer" probably wants them boosted. Rendering implements the call.
- [ ] Sign off, or list the changes, in this task's Review log.

## Review log
