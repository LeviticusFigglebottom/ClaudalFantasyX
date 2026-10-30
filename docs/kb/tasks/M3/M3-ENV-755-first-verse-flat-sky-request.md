---
id: M3-ENV-755
title: "The First Verse's sky renders as one flat tan (its fog paints the whole sky) (request to slice-polish)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
env-art's Prologue–Ch4 audit (2026-10-29, `lead/gate-big18`, player-eye stills): every view of the First Verse that shows
sky (the spawn's four vistas, the causeway, the Drownbell, Toma's seaward mark) has a uniform tan sky with no gradient,
cloud or sun. `game/levels/ch03/first_verse/first_verse.tscn`'s Environment has depth fog (`fog_mode = 1`, begin 30 m,
end 220 m, `fog_light_color` the horizon colour) with the default `fog_sky_affect` of 1.0, so the fog covers the
ProceduralSkyMaterial's dusk gradient entirely. The scene is slice-polish's (`game/levels/ch03/**`).

## Ask
- [ ] Set the Environment's `fog_sky_affect` to about **0.25**, so the dusk gradient (`sky_top_color` to
      `sky_horizon_color`) shows over a hazed horizon. Better, if the shot allows: the project's dusk cumulus sky
      (`env_sky_cumulus.gdshader`, as the Prologue's `iskarra` dusk Environment uses) for clouds.
- [ ] Re-render `slice_verse_steps` and the C08 stills; the shrine and the bell are unchanged.

## Review log
