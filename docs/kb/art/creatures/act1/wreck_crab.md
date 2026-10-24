# Wreck crab (`wreck_crab`), Ch6 the Brine Shoals

**Idea.** A variant of the [reef crab](../reef_crab.md) that lives in the wrecks. m2-slice's act1_ch06 §9 asks for it
to live in **broken Lit Age lamp housings** the way a hermit crab lives in a shell. Where the reef crab wears the
houses the sea took, this one wears a Saltwright lamp: an octagonal brass housing lying on its side on the crab's
back, scorched black and green with patina, its salt-glass panes crazed and two of them gone. The crab's soft
abdomen fills the open collar at the front. It is a defender: it hunkers under the brass. It puts the bound dead into
the shoals' ecology before the crate, and it echoes the scorched lamp housing Liss sits beside in the same chapter.

**Silhouette and palette.** The reef crab's body, legs and claws (0.62 m body, 1.4 m across), with a low crust in
place of the coral dome and the lamp on top, so it stands about 0.85 m: at battle distance, a crab carrying a lantern.
The crust is salt-white (`mortar_white` held under the ceiling, over `coral_stone_weathered`) with `salt_glass`
crystals, and three planks of wreck timber (`timber_weathered`) are lodged in it instead of house coral. The legs and
claws are the reef crab's chitin, bleached toward `timber_weathered`; the crusher's fixed finger is a salt slab. The
housing is `brass` with `bronze_patina` and `lacquer_black` scorch; its panes are `salt_glass` dulled with
`storm_slate`. The weak point is the crab's own: a `spawn_wound` crack in the crust on the crusher's side.

**The lamp's light (art sign-off, M3-CRE-05).** Inside the housing a little light is still bound: `glimmer_bound`
(`#4FB3B0`), faint, seen through the crazed panes and strongest through the two broken ones on top. This is the
**world's bound lamp light, not the crab's own**: the housing is a Lit Age machine, which color_script rule 2 assigns
to bound glimmer, and the crab merely lives in it. It is the one sanctioned use of `glimmer_bound` on a creature
(README rule 3 otherwise forbids it). Per rule 2 it is **steady** (no pulse in the `glass` and `lamp_light` slots),
sheds no motes, and moves only as part of the housing. It stays spatially apart from the `spawn_wound` crack (front
crust vs the lamp on the back) and much dimmer, so the two never read as one light.

**Clips.** The reef crab's (imported from its build module, which is not edited): `idle` (eye-stalks and a one-leg
shuffle), `attack` (a crusher strike, contact 0.5 s), `cast` (rear and spit, release 0.7 s), `hit`, `ko`. The housing
rides on the body bone. Budget ≤ 8k (as the reef crab); built at 7.8k.

**Build.** `assets_src/creatures/wreck_crab/build_wreck_crab.py` imports `build_reef_crab` for the rig, eyes, legs,
claws and clips, and adds the crust, the timbers and the lamp. Its Blender job lists the reef crab's folder in its
`sources`, so a change to the reef crab rebuilds it.
