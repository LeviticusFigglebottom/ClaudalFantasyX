# Conduit crawler (`conduit_crawler`), Ch11

**Where:** Lowlight temple, along its conduits. **Kind:** construct. **Role:** it **repairs** the Lamp Engine's
parts; it ignores the party until the engine is struck.

**The idea:** a Lit Age conduit-cleaning machine still on its rounds: a salt-glass shell on six brass feet, a brush
and a wiper on its fore-arms, a dim bound light inside to see by. It isn't hostile. It tends. The one
exaggeration: **it has kept working for four hundred years**.

**Silhouette:** a beetle-like dome 0.7 m long on six thin legs, the shell clear, the light inside visible; two short
fore-arms with brush heads.

**Palette:** shell `salt_glass`; frame `brass` going to `bronze_patina`; feet and joints `lacquer_black`; its light
`glimmer_bound` (steady, small: a construct, README rule 3); weak point (the shell's seam) `spawn_wound`.

**Clips:** `idle` (it scrubs at the floor, feet ticking); `attack` (a brush jab: contact 0.45 s of 1.0 s); `cast`
(the repair: it scuttles to the engine and its arms work); `hit` (it rocks on its legs; peak near 0.1 s); `ko` (its
light dims and its legs fold under it). Budget ≤ 5k triangles. Rig: body, six legs of 2, two arms of 2.

## Act III use (M5-A3P-1807, 2026-10-30)
The Act III bestiary (act3_roster.md, Ch19) reuses this model on the Lamp Spire, where it tends the spire's conduits:
the same mesh, rig, clips, portrait and creatures.json row. A foe's creatures.json row is found by its model scene
(`CreatureModels.creature_for_scene`), so an Act III enemies.json row with `model` set to
`res://game/creatures/conduit_crawler/conduit_crawler_battle.tscn` picks up this row (contacts, clip_by_skill) with
nothing new. That row is Combat's (M5-A3P-1849).

Brought to the Act I bar for the reuse:
- **Planted feet** (common/grounding.py `pinned`, in every clip, the KO included): the feet hold their spots while
  the body rocks, jabs, leans and sinks over them.
- **The brush and the wiper no longer drag:** the attack's wiper arm lifts clear (−22° to −14°), the body settles
  before the brush sets down (0.86 s), and in the KO the arms fold up in the first 0.45 s, before the body sinks.
  The clip audit is clean (the worst slip is 1.9 cm, under its 2 cm flag).
