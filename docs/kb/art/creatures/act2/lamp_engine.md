# The Lamp Engine (`lamp_engine`), Ch11 boss

**Where:** Lowlight, the half-drowned temple: the engine hall below the sanctum (act_outline Ch11: "a still-running
Lit Age machine full of bound dead, two phases; releasing its core makes a small upward lift").

## The idea

A Lit Age construct, the second after the Cinder Matron: a machine for keeping light. A tall brass frame
holds a lattice of salt-glass lamps around one core, and each lamp holds a bound dead light, steady and
unpulsing (`glimmer_bound`, color_script rule 2). Water has risen to its knees and it is still running, still
trimming, still turning its lamps toward a congregation that drowned. It isn't cruel. It keeps.

The one exaggeration: **a temple lamp-stand that walks**. Every part is a real lamp-stand's (gimbals, chimneys,
trimming arms, a bell-shaped hood); it is simply the size of a chapel and has four jointed feet.

## Silhouette

- A 3.4 m bell-hooded tower of lamps on four short jointed legs: twelve lamps on three gimballed rings, the
  rings turning against each other; two long trimming arms with scissor heads.
- **Phase 2:** the rings fold back like petals and the core shows: a single large salt-glass globe, cracked, with
  the brightest bound light in it.
- Reads as vertical and ringed, nothing like the Matron's squat body.

## Palette

Frame `brass` going to `bronze_patina` at the waterline, `lacquer_black` joints; chimneys `salt_glass`;
lamp lights and the core `glimmer_bound` (emissive, steady); its weak points (the gimbal hubs) `spawn_wound`.
Drips of `sea_glow` where water runs down the glass.

## Battle read and clips

- **At battle distance:** a tall ringed tower of steady lights on legs, its arms raised.
- `idle`: the rings turn slowly against each other; the trimming arms tick; water drips.
- `attack` (the trim): an arm's scissor head snips at the target; contact at 0.6 s of 1.3 s.
- `cast` (the gathering): every lamp swings to face the target and brightens in sequence; a held breath.
- `hit`: the rings jolt and a lamp swings loose on its gimbal; peak near 0.1 s.
- `ko`: the core goes dark and a small lift of motes rises out of it (VFX, `glimmer_lift`: the dead it held
  released), then the frame settles on its knees.
- **Phase `opened`** (50% HP): `phase_change` (2.0 s), the rings fold back and the core shows; `idle_opened`.

Budget ≤ 20k triangles. Rig: body, three ring bones, twelve lamp gimbals, two arms of 3, four legs of 2, the core.

**Break parts (proposal):** the lamp rings (one per ring). Each broken ring frees its lamps (they go dark) and
slows the cast. The conduit crawlers (roster) repair them.
