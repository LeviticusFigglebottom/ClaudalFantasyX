# Ilun, the Net-Warden (`ilun`), Asha's Vowbound

**Who:** the first Vowbound (docs/kb/story/vowbound.md §1): the glimmer of **Teyo Marrin**, the 50th Cantor, a
sixteen-year-old Haluna fisher boy who went so the Order would not take his sister Pila. Bound in the Shell Shrine
since. **Kind:** a Vowbound, so bound light, not a creature of the reef and not Undertow-spawn. **Role:** an ally.
Asha calls him (vowbound.json `ilun`: `attack`, `brine_lash`, `tidal_ward`; Swell technique `floodnet`), and he stands
alone on the middle party slot while the party has stepped off (battle_presentation.md "The Vowbound (Ilun)").
**Where you see him:** the slice's one Vowbound call (B10, C10): the shots `battle_vowbound_out`,
`battle_choreo_summon` and `battle_choreo_vowbound_rise`, and his chamber (S08).

**The idea:** a vast spectral manta ray carrying a heron's crest. His wing membranes are crossed by a knotted
fishing net drawn in light, and a child's glass net-float hangs on a cord from the end of his tail: the keepsake, the
one thing about him that is not light. He is huge and gentle. He reads as **protective**: a wide roof of wings
spread over the place where the party stood, slow, never a predator.

Original design (README rule 1). It starts from two real animals, the manta and the grey heron, and one human object,
the hand-knotted glass fishing float of a Low Reaches boat. No horns, no teeth, no armour, no spikes: nothing about
him threatens.

## Silhouette and size

| | |
|---|---|
| Wingspan | **5.1 m** (half span 2.55 m), the wings swept back to pointed tips (z −0.15) with a falcate (concave) trailing edge (M3-CRB-008; was 4.6 m) |
| Disc length | 1.98 m from the blunt head (z +1.85) to the rear of the body (z −0.13): the disc sits **forward of the origin** (its centre at z +0.87) so the tail and the float stay inside the battle HUD's safe frame (M3-CRB-008) |
| The mantle | the wings rise from the body (+0.1 m at mid-span) and arch down to the tips (0.95 m above the water): a canopy, as a heron **mantles**, spreading its wings over the water like a roof. It reads protective, and it turns the near wing's back (and its net) toward the default battle camera, which otherwise sees a flat manta edge-on |
| Tail | a whip about 1.6 m long, back and then down in one arc to z −0.95 and 0.67 m above the water, so the float hangs plumb under it instead of reaching toward the summon camera, with a small dorsal fin at its root |
| Hover | the disc's mid-plane at **1.35 m** above the water (the origin, y 0) |
| Crest | three long heron plumes (1.3–1.5 m) from the crown, lanceolate vanes on a bright shaft, swept back and up over the back, with two short ones, to 2.16 m |
| The float | a 22 cm glass sphere in a cord net, on a 17 cm cord from the tail tip, its bottom 0.27 m above the water |
| Head | a broad, flat-fronted, rounded head with a wide mouth slit under its front edge, two **rolled** cephalic lobes from its corners, curling forward and down into scrolls (not horns), two soft glowing eyes in dark sockets under a brow ridge, and five gill slits a side on the belly |

As built (M3-CRB-008): x ±2.55, y 0.26–2.16, z −1.07 to +2.10 at rest.

**Why 4.6 m.** The camera `summon` shot (choreo.json camera.shots) sits 4.2 m back and 2.6 m to the side of his
mark, 0.35 m up, looking at a point 1.6 m above it with a 46° vertical FOV: about 4.9 m away, so it holds ±2.1 m
vertically around 1.6 m (−0.5 to 3.7 m) and ±3.7 m across at 16:9. "Back" is along the battle axis, so for a
party-side fighter the camera is behind him and low: it looks up at his belly and the mantle from behind, with the
foes beyond. His wings run across the battle axis, so seen from 32° off it his span projects to about 3.9 m, inside
the HUD's safe frame (checked on the silhouette sheet, M3-CRE-638). At the battle camera (README rule 6: about 110
px a metre at 720p) he is the largest thing on the field, which is what a Vowbound should be. He stands alone on the
Vowbound slot (battle_sandbox.json `vowbound_slot` 1, the party's back slot; the others are empty while he is out),
and the wings reach across the empty slots, never toward the foes.

**The stand-in's anchors.** battle_sandbox.json (UI's) gives `ilun` a 2.3 m height and no hover; the VFX anchors are
fractions of that height from the water (effects.json `anchor_heights`): chest 0.6 → 1.38 m (his disc), head 1.0 →
2.3 m (just over the crest), feet 0.05 → 0.12 m (the water under him). So the model is **built hovering**: the origin
is the water point under him and the rest pose already floats at 1.35 m. creatures.json gives him no `hover` (the
stand-in would add it under every anchor), and `yaw_deg` −90 turns his +Z face toward the foes, as the heroes'
actors are turned.

## Colour (palette.json swatches; README rule 7)

| Part | Albedo | Light |
|---|---|---|
| Back | `deep_teal_shadow` `#0E4A55` at the core, mottled toward `lagoon_teal` `#1FA3A6`, with two soft pale "shoulder" chevrons of `salt_glass` `#BFE6E0` | a faint inner light: `glimmer_bound` at 1.2 on a low mask (0.10), so the body reads as light held in deep water |
| Wings (membrane) | `lagoon_teal` over `deep_teal_shadow`, paling toward `salt_glass` at the thin margins, where the light shows through | the same faint inner light (0.08), and a strong back-lit rim sheen: the thin membrane reads as translucent |
| Belly | `salt_glass` with `lagoon_teal` (0.35), darker toward the margins (a manta's pale underside) | as the back |
| The net | `salt_glass` threads with knots | **`glimmer_bound` `#4FB3B0`, energy 1.2, steady** (color_script C10 and rule 2): emission mask 1.0 |
| Crest | `salt_glass` plumes from a `deep_teal_shadow` root | `glimmer_bound` along the shafts (0.35), stronger at the tips (0.6) |
| Eyes | `deep_teal_shadow` | `glimmer_bound`, a soft glow (0.55): kind, not staring |
| The float | `salt_glass`, glossy and wet | **none**: it is glass, not light, and only catches the light around it (rim sheen) |
| The float's net | `sand_cloth` `#C9B48E` cord | none |

Albedo stays between `lacquer_black` and `gauze_white`. No `spawn_wound` anywhere: **he has no weak point**. ADR 0151's
one answer to where to strike is for foes, and he is an ally. No `glimmer_held` or `glimmer_lift`: he is bound until
his Act III release (Ch20), and only then does his light turn to rising gold (color_script rule 1; not built here).

**The bound light (color_script.md rule 2, C10).** Every emissive slot is `glimmer_bound` at 1.2 with
`emission_pulse_hz` 0: no breath, no flicker, no drift, no shed motes, no trails. His light moves only because his
body moves. The summon's OmniLight3D (choreo.json `summon_cinematic`, BattleSummonCinematic) is the same swatch and
energy, and is battle-presentation's.

**Translucency.** The creature shader is opaque (it has no alpha; its surfaces cast shadows and sort like solids). He
reads as spectral through value and light, not alpha: a deep core, pale thin margins, a strong rim sheen on the wings
and crest (the shader's back-lit edge), a faint inner glow, and the bright net. A real alpha body would need a
`creature_spectral` shader and a per-slot shader choice in `common/write_materials.py`, which reruns every creature's
Blender job; that is a follow-up for after his first PC render, if the render says he needs it (task M3-CRE-638).

## The net on the membranes

A knotted fishing net, built as geometry by the build script (no image, no texture): a diamond-mesh lattice of
knots 0.21 m apart (the mesh side) laid over each wing's planform from 0.6 m out from the midline to 95% of the half
span, inset 4 cm from the leading and trailing edges. Each knot is jittered up to 1.8 cm (a seeded `default_rng`), so
it reads hand-knotted, not ruled. Every strand between two knots is a flat ribbon 2.4 cm wide lying 8 mm off the
membrane (on the back and, for the low summon camera, on the belly), skinned with the same weights as the membrane
under it, so the net flexes with the wing. Each knot is a small flattened bead. The net is its own slot (`net`), all
emissive: 135 strands and 63 knots over both wings, on each face. Per-vertex emission could not draw lines this thin
on a membrane this size (the membrane's vertices are about 5 cm apart), which is why the net is geometry.

It echoes the float's real cord net: the boy's float is wrapped in the net he knotted, and his wings carry its
memory drawn in light.

## The heron's crest

A grey heron's nuchal plumes, made into light: two long plumes (1.2–1.3 m) and one a little shorter from the crown
of the head, rising and sweeping back over his back, flattened like feathers, plus two short tufts. They lift when
he gathers (`ready`, `cast`, `special`, `victory`), lie back when he flinches, and flatten in the KO and the dismissal.
Rig: `crest_0` (root half) and `crest_1` (tip half).

## The glass net-float (the keepsake)

A child's glass float, the size of a fist (19 cm), pale `salt_glass`, glossy, wrapped in a `sand_cloth` cord net (six
meridians and two rings), tied by a short cord and a collar to the tail tip. It hangs: the `float` bone counter-turns
the tail's and body's pitch and roll with a short lag, so it swings back as he moves and settles under the tail. It is
the only part of him that is an object, so it never glows. In the finale it is the last thing to fade (not built here).

## Clips (contact seconds go in creatures.json `contact`)

All in place: the stage moves him (the entry's rise from 2.6 m under the water, the dismissal's sink, the fall's tip
back and draw under; choreo.json `vowbound`), and the clips play on top. Every frame of every clip stays above the
water (y ≥ 0; GroundedClipsTest), so no allow-list is needed.

| Clip | Length | What it shows |
|---|---|---|
| `idle` | 4.0 s, loop | a slow wing undulation (a wave from the body out to the tips, 8°–13°), the disc bobbing 4 cm, the tail swaying, the crest stirring; he hovers in place |
| `ready` | 1.4 s | he gathers: wings rise high (by 0.5 s), the crest lifts, the body rises 8 cm, then one slow down-stroke and back to rest. The stage plays it on the entry (the 1.3 s rise, and C10's 2.6 s) and on the dismissal's 0.9 s sink. |
| `attack` | 1.2 s, contact **0.55 s** | the brine lash: he banks, lifts the near wing high, then sweeps it forward and down across the target, the body dipping into the blow (also the plain `attack`) |
| `cast` | 1.6 s, contact **0.8 s** | the tidal ward: the wings spread and curl forward around his front, a shield, the crest raised, held, then released |
| `hit` | 0.5 s, peak **0.12 s** | he is pushed back and pitched nose up, the wings flinching up, the crest snapped back |
| `defend` | 1.2 s | the wings fold forward over his front and hold, the body lowered a little, then open |
| `ko` | 1.8 s | the fall: a flinch, then he tips back (nose up 24°), the wings fold up and back, the crest flattens, he settles 0.12 m and holds (from 1.45 s); the tail curls up so it stays out of the water, and the float still hangs. The stage tips him back a further 38° and draws him under (`vowbound.fall`, 1.5 s, so the clip outlasts it). |
| `victory` | 2.2 s | he rises 0.25 m with the wings spread high and the crest up, one slow full stroke, and settles |
| `rise` | 2.6 s | the unfurling: from wings folded up over his back like a closed shell and the crest flat, the wings open high, one stroke, to rest. In place: built for the stage's rise (C10's 2.6 s) |
| `dismiss` | 1.0 s | the folding: wings close up over his back, the crest lowers, the nose dips; it ends folded (the stage sinks him) |
| `special` | 2.4 s, contact **1.45 s** | Floodnet: wings flung wide and high, the body lifting 0.3 m (by 0.9 s), a held breath, then the great sweep down (the contact, as battle_vfx.md's net of `glimmer_bound` threads lands on the water) and back to rest |

`hit_b` is authored (the hit rolled to the other side, 1.35× heavier): the kit's mirrored copy would flip the wings'
flinch from up to down. The kit adds `idle_b` (the cast at 0.3×, 1.4× speed: the fidget). creatures.json maps
`brine_lash` → `attack`, `tidal_ward` → `cast` and `floodnet` → `special` (a creature's own action clip wins over the
style's, so `special` plays today); `attack` is the physical default.

**Lowest vertex per clip** (skinned from the GLB, GroundedClipsTest's measure): idle 0.34 m, ready 0.44, attack 0.07
(the lashing wingtip at the contact), cast 0.44, hit 0.36, hit_b 0.34, defend 0.35, ko 0.22, victory 0.44, rise 0.27,
dismiss 0.35, special 0.17, idle_b 0.44. Highest: dismiss's folded wingtips, 3.42 m.

**What the stage plays today.** choreo.json `vowbound` names `ready` for the entry and the dismissal and `ko` for the
fall, so `rise` and `dismiss` wait on battle-presentation (the request is in the task, M3-CRE-638). `ready` works for
both today: it is a gathering of the wings that reads as an unfurl on the way up and a last stroke on the way down,
and `ko` is authored to sit under the stage's tip back.

## Rig (16 bones)

`root` (the water point), `body` (the disc's centre, 1.35 m), `wing_l0..2` and `wing_r0..2` (hinged along the body's
length at 0.5, 1.15 and 1.75 m out), `tail_0..4`, `crest_0`, `crest_1`, `float` (at the tail tip).

## Budget

≤ 16k triangles (the showpiece of the slice; the creature range is 5k–16k), GLB ≤ 2 MB. Seven slots: `body`,
`membrane`, `net`, `crest`, `eye`, `glass`, `cord`.

**As built (M3-CRE-638):** 13,655 triangles (membrane 4,880, net 2,792, body 1,920, crest 1,320, cord 1,191, tail
544, lobes 448, glass 320, eyes 240), 8,697 vertices, 16 bones, 13 clips, GLB 1.29 MB.

## As built: the held form (M3-CRE-647, 2026-10-28)

The foe form for the Ch20 release fight (act3_roster.md, "The Vowbound as foes").

- **`release`** (3.3 s, its KO as a foe; the only clip added, every other clip samples identically): the first release, gentle: the wings rise and open wide, the crest up, he lifts a little (to 1.85 s); then one slow stroke carries him 1.5 m up and 0.45 m back, level and unhurried, the float hanging. He ends open and calm, not fallen.
  Lowest vertex over every frame +0.31 m. GLB 1.29 → 1.37 MB.
- Scene `game/creatures/ilun/ilun_held_battle.tscn` (the same GLB; `CreatureActor.material_dir` puts on `assets/creatures/ilun/materials_held/`, written by write_materials.py from the `held` block in materials.json: 5 emissive slots glimmer_bound to glimmer_held `#7FC6D9` at the same energy, steady; the rest as they are). creatures.json row `ilun_held`: no `vowbound` key, `ko` = `release`, `phases.release` = {clip `release`, `hold` true}, `stand_in.yaw_deg` 90 (facing the party). Review shot `creature_ilun_held` (not rendered yet). No enemies.json row (Combat's, with the chapter designer). The turn to `glimmer_lift` and the rising motes are presentation (battle VFX), not the model.

## Final pass (M3-CRB-008, 2026-10-28)

ADR 0041 (Act I at final quality). The critique of the M3-CRE-638 render: he read as a flat, thin paper cut-out with a
crude grid of white tick marks, small and weightless. What changed (build_ilun.py rewritten on the same kit; every
clip name kept; the held form, `materials_held/` and `release` unchanged in kind):

- **Body with weight and anatomy.** A domed disc (0.27 m above and 0.15 m below the mid-plane at the core, rounded at
  the head's front), a spine ridge, two shoulder humps and a brow ridge, fine skin relief that fades out over the
  membrane, and a broad flat-fronted head. The wing root is thicker (0.08 / 0.05 m) and the membrane thins to a 4 mm
  trailing edge frozen in a soft ripple (3.5 waves along the span, up to 7 cm). The span stations bunch over the body.
- **Head detail.** Cephalic lobes built as lofted, rolled sheets (a stem from the head's corner into a forward scroll
  curling down and back, 1.45 turns of π); a mouth slit under the front edge and five gill slits a side on the belly,
  dark (`deep_teal_shadow` toward `lacquer_black`) with a little of his light inside them (mask 0.3); eyes in dark
  sockets.
- **The net of light**, rebuilt: continuous cords laid in the wing's own span-and-chord coordinates (two families of
  diagonals, 4 diamonds across the chord and 7 along the span, about 0.25 m), so every cord follows the wing's
  curvature and narrows with its chord toward the tip; the lattice is warped smoothly (hand-knotted) so crossings stay
  crossings; a heavier head-rope round the net's three inner edges; a flat bead at every crossing on the back. Cords
  are 4.2 cm wide, 7 mm off the membrane, sampled every 5.5 cm on the back and 10 cm on the belly (beads on the back
  only). Emission masks: cords 0.72, head-rope 0.85, knots 1.0 (brightest at the knots); all `glimmer_bound` at 1.2,
  steady. 20 cords, 3 ropes and 46 knots a wing.
- **Colour (layered, spectral).** Back: a `deep_teal_shadow` core and spine, `sea_glow` across the mid-wing,
  `lagoon_teal` toward the tips, `reef_blue` and darker mottling for depth, pale `salt_glass` shoulder chevrons, a
  darker band just inside a thin pale rim (margins measured in metres now, so the outer wing is not washed pale), and
  the trailing edge palest (`salt_glass` with `foam_white`). Belly: `foam_white`/`salt_glass` with `sea_glow` spots,
  dark margins; the flanks keep the back's tones (by normal), so a thick body seen from the side has no belly band.
  The inner light is a low mask (0.05) pooling in the wings and rising to about 0.37 along the thin margins.
  materials.json: rim sheen body 0.6 → 0.45, membrane 0.85 → 0.55 (at the battle camera's grazing angle the near wing
  went flat white).
- **Crest:** three long lanceolate plumes (1.3–1.5 m) and two short ones as thin vanes on a raised shaft, fringed
  (alternate barbs parted), `deep_teal_shadow` root to `salt_glass` with a `foam_white` shaft; the shaft and tips
  glow (0.2–0.45).
- **Tail:** a long whip in one arc, darker above and pale beneath, with pale rings toward the tip and a light that rises
  toward it, and a small dorsal fin at its root.
- **The keepsake:** the float is 22 cm, its glass deeper `lagoon_teal` toward the bottom (thick old glass), a
  `gauze_white` glint high on the camera side, a glass seal on top under a `sand_wet` knot, six meridians and two rings
  of `sand_cloth` cord. No emission (it is the one thing about him that is not light).
- **Scale and framing.** At the default battle camera he is the largest thing on the field (about 340 × 240 px at
  720p) and his rest pose stays left of the turn-order column and above the party panel (the safe frame,
  choreo.json camera.safe_frame); a wing in a hit or the KO's tip-back crosses it for a few frames. The VFX anchors
  still land on him: chest (1.38 m at the origin) on the disc's rear half, head (2.3 m) just over the crest.
- **Rig (20 bones):** a fourth wing segment each side (`wing_l3`, `wing_r3`, the tips; the clips key it at 1.15× the
  third's flap) and two unweighted VFX anchors: **`vfx_core`** (on `body`, the disc's centre, 5 cm over the mid-plane)
  and **`vfx_keepsake`** (on `float`, the float's centre).
- **Idle:** a travelling wave: each wing segment flaps (5°, 8°, 10°, 12°) 0.85 rad behind the one inside it, and twists
  (1.5°–6.5°) a quarter beat behind its flap, so the wave runs out to the tip and the soft trailing edge ripples after
  the leading edge. Other clips keep their keys, with small changes for the new size: attack's wind-up banks 11° and
  lifts 0.17 m (the far wingtip stayed above the water), the contact lifts 0.08 m; `rise` lifts the tail more
  (the float stays clear of the water while he starts nose-up); `FOLDED` tip 22°; `ko` curls the tail up 24°.
  Contacts unchanged (attack 0.55 s, cast 0.8 s, special 1.45 s).

**As built:** 15,561 triangles (≤ 18k): membrane 5,060, net 3,172, body 2,392, crest 1,440, cord 1,105, lobes 864,
tail 672, glass 496, eyes 240, gill slits and mouth 120; 9,934 vertices, 20 bones, 14 clips (with hit_b and idle_b),
GLB 1.61 MB. Lowest vertex per clip (numpy poser): idle 0.18 m, ready 0.26, attack 0.24, cast 0.24, hit 0.11, hit_b
0.06, defend 0.15, ko 0.12, victory 0.26, rise 0.25, dismiss 0.16, special 0.26, release 0.19, idle_b 0.25. The
"Silhouette and size" table above is updated; the M3-CRE-638 budget and lowest-vertex lines are history.

**Not done (follow-ups):** a real alpha (`creature_spectral`) shader is still a kit change (common/write_materials.py,
another track's); he reads spectral through value, the bright net and the glowing margins. No portrait yet
(assets/ui/portraits/creatures/ilun.png, the portrait manifest's; test_creature_portraits fails on it and the other
missing Vowbound portraits, before and after this pass).

## Polish 2 (2026-10-28)

The near wing read pale and washed at the battle camera's grazing angle (battle_vowbound_out,
battle_choreo_vowbound_rise). A diagnostic render showed the pale sheet was mostly the net: toward the tip the net's
chord closes up, its 4.2 cm cords crowded into a solid pale band, and the membrane between them was pale too. Now:
- **The membrane deepens toward the trailing edge** on both wings, back and belly (`reef_blue` into
  `deep_teal_shadow` on the back, `sea_glow` with `reef_blue` underneath, up to 70%), and the pale trailing margin is
  pulled in to a thin rim (8 cm); its inner light dips a little there.
- **The cords thin with the net's chord** (full width where the chord is 0.8 m or more, down to 35% where it closes up
  toward the tip), so the dark membrane shows between them out to the tip. Their colour and light (`glimmer_bound`
  masks 0.72 / 0.85 / 1.0) are unchanged, so the net stays the brightest thing on him; he still reads spectral and
  luminous. The far wing gets the same treatment (in the rise its net reads as clear dark diamonds).
Triangles (15,561), bones, clips, contacts and anchors unchanged; materials.json unchanged.
