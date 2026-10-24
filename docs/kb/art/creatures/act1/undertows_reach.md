# The Undertow's Reach (`undertows_reach`), Ch8 boss (with the PC GPU session)

**Idea.** A colossal limb of the storm reaching over Corrow's seawall (act_outline Ch8: multi-phase, scripted escape;
the wall falls anyway). The storm itself is Rendering's (the Undertow shaders). The creatures track builds the
**near part**: where the limb comes over the wall-head, a lashing mass of black water, wreckage and spawn bodies
fused together, with held-glimmer wounds the size of doors. Its far body is the storm VFX.

**Silhouette.** It fills the top of the battle frame: a curved column 8–10 m high coming down out of the storm, its
end splitting into grasping fingers of water and wreck. Phases: its fingers (targets) break away one at a time.

**Palette.** `lacquer_black`, `storm_slate` water, `abyss_navy`; wounds `spawn_wound`; motes `glimmer_held`.

**Coordination.** A joint task with the PC GPU session (the storm limb's shader, rain and lightning). Art makes the
mesh, rig and the finger `break_parts`; Rendering makes it water. Budget ≤ 24k (one per scene).

## Built (M3-CRE-06, 2026-10-24): first pass, per m2-slice act1_ch08 §5 and §9

- **Form.** A forearm of black water about 16 m long and 3 m thick, coming down over the top out of the storm behind
  the parapet and flaring where it breaks into a **six-fingered** grip of spawn-crust on the wall-head (six, so it never
  reads as a man's hand). Four broken spars are driven through it, and two drowned spawn shells are half sunk in it. Two
  door-sized `spawn_wound` wounds face the party. 10.9k triangles (budget 24k), 25 bones.
- **States** (creatures.json `phases`; the ids `dark` and `breach` are placeholders until m2-slice names the phases in
  enemies.json): the Grip is `idle`; the Dark is `phase_dark` → `idle_dark` (the hand lifts off the stone and hangs
  over the wall-head, closing slowly); the Breach is `phase_breach` → `idle_breach` (it lets go and draws back over the
  sea, the hand raised and open, gathering).
- **Clips.** `attack` (Crust Slam: lift and slam, contact 1.2 s), `cast` (Undertow Pull / Close the Hand: the fingers
  rake back and close, 1.3 s), `hit` (a shudder up the limb), `ko` (drawn back up into the storm; never used by the
  design, kept for safety).
- **For the PC GPU session:** the materials (`water`, `crust`, `wreck`) are creature-shader stand-ins. The forearm's
  vertex data carries the wound mask in the emission channel and a streak pattern in the albedo. Swap the `water`
  slot for the Undertow look whenever it suits; the mesh and rig won't change shape under you.
- **Known:** `attack` and `cast` start from the Grip pose, so in the Breach phase a skill clip would pop. The Breach
  only charges (`breach`), so map that to no clip, or ask for a breach-pose charge clip.
