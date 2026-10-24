# Wallcrab (`wallcrab`), Ch8 the headland path

**Idea.** A palette variant of the reef crab (m2-slice act1_ch08 §9; Toma's answer). It is a crab of Corrow's grey
laterite seawall rather than the coral reef: the same build, rig and clips.

**Palette.** Shell `cold_blue_stone` and `overcast_slate`, with mortar-white barnacle crust; the shell tiling is
laterite under the grey. Legs and claws are laterite darkened toward `volcanic_stone`; the underside is
`volcanic_stone`. The weak point is unchanged (`spawn_wound`).

**Build.** `assets_src/creatures/wallcrab/build_wallcrab.py` imports `build_reef_crab` and overrides its palette. A fix
to the reef crab reaches the wallcrab, and the job lists the reef crab's folder as a source.
