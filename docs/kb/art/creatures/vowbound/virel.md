# Virel, the Kite-Serpent (`virel`), Asha's Fire Vowbound

**Who:** the third Vowbound (docs/kb/story/vowbound.md §3): the glimmer of **Wenna Corr**, the 53rd Cantor, who sang
about 95 years ago. She was a Corrow-born girl of hidden Saltwright blood who passed as Order-faithful all her life
and scratched tiny line-marks into the stones of every temple she visited, a trail for her people that nobody found.
She has been bound in Coilspire on the Corrow headland since. **Kind:** a Vowbound, so bound light, not a creature
and not Undertow-spawn. **Role:** an ally. Asha binds her in Ch8 (B06, `ch08_virel_bound`) and calls her from the
Undertow's Reach on (B16 phase 2). vowbound.json `virel`: `attack`, `kite_flare` (fast fire that pushes its target
down the timeline) and the Swell technique `flare_line` (fire to every foe, a delay, `clears_field: storm_dark`).
She takes the middle party slot alone while the party has stepped off.
**Where you see her:** the binding's held frame (act1_ch08.md F07), the first call's full summon cinematic at the
wall-head (B16, with Liss's reaction shot on the tuning key), and every later call.

**The idea:** a long ribbon-serpent sewn from sailcloth panels, with bound light running along every seam: a Saltwright
signal kite flown alight as a flare and held still. She is built **as a kite**: taut panels on a light timber frame
(a spine spar and a batten across every panel), a bridle of three lines meeting under her throat, two ribbon
streamers at her tail. From the bridle knot hangs **a brass tuning key**, the keepsake: the knot is where a flyer ties
the string, so the one human object about her hangs exactly where a hand would hold her. Her shape is what Dace
modelled the Kite's sails on (Act III), so the panels, battens and scalloped hems are the same language the Kite's
sails will speak.

Original design (README rule 1). It starts from a sewn cloth kite of many cells, a ribbon serpent's coil, and one
human object, a sailmaker's or wright's brass tuning key. No scales, no fangs, no horns, no claws: nothing about her
is a beast. Her crest is the kite's bowed spar, swept back past the head; her eye is a ring of seam-light on the cloth.

## Silhouette and size

| | |
|---|---|
| Length | **6.25 m** of ribbon: a 0.75 m head and a 5.5 m body, plus 0.55 m streamers |
| Width | the head 0.56 m, the neck 0.58 m, the loop 0.48 m, tapering to 0.16 m at the tail |
| The coil | the body coils **once** round an upright oval (1.2 m across by 1.36 m tall, its centre 1.7 m over the water) in a plane turned 22° off the battle axis; the neck enters the loop at its top, the tail leaves it at its top and goes back, the tail's pass 0.55 m deeper than the neck's so they clear |
| Head | a long lozenge of cloth, widest at the cheek, pointed at the nose (2.64 m up, 1.5 m ahead of her mark), with a seam-ringed eye on each face and the bowed crest-spar swept back over it |
| Panels | 14 body panels 0.4 m long between cross-seams, each hem drawn in 6% mid-panel (kite cells, a scalloped edge) and the cloth bellied 5% of the width behind the frame |
| Streamers | two ribbons 0.55 m long, 7 cm wide, hanging down and back from the tail end |
| The key | a 0.26 m brass tuning key (a 9 cm ring bow, a collar, a shaft and a square socket) on a 10 cm cord from the bridle knot, 0.38 m under the throat |

As built: x −0.92 to +0.61, y 0.76 (the loop's lowest hem) to 2.94 (the crest-spar), z −0.58 to +1.51 at rest.

**Why coiled, and why in that plane.** A Vowbound stands on the middle party slot (battle_sandbox.json
`vowbound_slot` 1), which sits 1.1 m from the right edge of the default battle camera's HUD safe frame (choreo.json
`camera.safe_frame`: 4% left, 15% right, 10% top, 26% bottom). Ilun's tail crossed it. A 6 m serpent laid out would
cross it by metres, so Virel is coiled into a figure 2.1 m along the battle axis and 2.2 m tall with her head toward the foes (where the frame
has room) and her tail kept short of her mark. The coil's plane is turned 22° from the battle axis so its sails face
a direction between the two cameras that see her: the default camera (about 76° to her side, 16° above) and the
`summon` shot (behind her along the axis and to the side, low). Both see the sails at about 37° off square, never on
edge. The summon shot holds 0.6 m to 3.3 m in height around her mark; she spans 0.76 m to 2.94 m.

**The framing check** (every baked frame of every clip, projected through both cameras from the build's vertices:
the margin to each edge of the safe frame as a fraction of the screen; negative is outside). Default camera, at
rest: left 0.61, right 0.05, top 0.09, bottom 0.24; summon shot, at rest: left 0.32, right 0.21, top 0.15, bottom 0.04. The tightest frames per clip: right 0.028 (idle, the streamers),
0.019 (attack), 0.020 (hit), 0.011 (victory's gust); top 0.016 (attack's rear), 0.033 (victory). **Every clip is
inside the default camera's safe frame**, except Flare Line's release (`special`, 2.07 s), which touches the right
edge (−0.002, under 3 px at 1280) as the line swings back into the coil. Summon shot: every clip the summon plays
(`ready`, `rise`, `idle`) is inside it (bottom 0.03–0.04, the loop's lowest hem); the KO (−0.008 at the bottom) and
Flare Line's line (−0.057) leave it at the bottom, and neither is played on that shot.

**The stand-in's anchors.** Unlike Ilun, Virel has no `stand_ins` row in battle_sandbox.json (UI's), so her stand-in
spec has no `height`: FighterStandIn takes 1.0 m (the damage numbers' and markers' head point is 1.0 m) and BattleVfx
takes 1.7 m for its anchors (effects.json `anchor_heights`: chest 1.02 m, head 1.7 m, feet 0.09 m). Both land on the
lower half of her loop, so the effects hit her body, but the head point sits under her head. **Request to UI:** add
`stand_ins.virel` with `height` 2.6 (chest 1.56 m, the loop's middle; head 2.6 m, her head) and a placeholder in her
colours, as Ilun has. She is **built hovering** like Ilun: the origin is the water under her mark and creatures.json
gives her no `hover`; `yaw_deg` −90 turns her +Z face toward the foes.

## Colour (palette.json swatches; README rule 7)

| Part | Albedo | Light |
|---|---|---|
| Sailcloth | `sand_cloth` `#C9B48E`; every third panel a `faded_teal_cloth` `#5E9A96` patch (the Saltwright mend, as on their camp tents); paler toward `gauze_white` `#EBE7DF` mid-panel, where the light shows through the cloth, and a little darker toward `timber_weathered` at the hems | a low inner light, `glimmer_bound` at 1.2 on a mask of 0.05 mid-panel rising to 0.35 at the seams: the cloth lit through from its burning seams |
| The head's mask band | `faded_teal_cloth` with `deep_teal_shadow` (0.25) | as the sailcloth |
| **The seams** (both hems, every cross-seam, the eye rings) | `gauze_white` | **`glimmer_bound` `#4FB3B0`, energy 1.2, steady**: emission mask 1 |
| Frame (spine spar, battens, crest-spar) | `timber_weathered` `#7E6A55` | none |
| Bridle and the key's cord | `sand_cloth` | none |
| **The key** | `brass` `#B08D57`, metallic 0.9 | **none**: it is brass, not light, and only catches the light around it |

**Fire on a Vowbound: the palette rule, and the choice.** palette.json gives `glimmer_bound` to "the Vowbound
(temple and summoned forms) until their release" ("emissive inserts and Vowbound forms only; steady: no flicker, no
drift, no shed motes"), and `ember_orange` is "flame and horizon only; never a surface albedo" and the "Fire VFX base".
color_script.md rule 2 says the Vowbound are bound light, and act1_ch08.md says it of Virel by name: at rest "the seams
read as steady `glimmer_bound`, never flickering. The fire *element* belongs to Virel's battle VFX" (F07), and "Virel
is bound (`glimmer_bound`, steady) with fire-element VFX on her attacks. The Flare Line ... is fire light, not
glimmer" (§5, Light). **So her seam fire is `glimmer_bound` at 1.2 on her form, in every clip, and no warm colour is
on her model at all**: the fire you see when she strikes is battle-vfx's (`ember_orange` and its flame swatches on
`kite_flare` and `flare_line`), never her own emissive. That keeps bound and fire from ever being confused (act1_ch08.md
§9, Rendering item 2): her own light is teal and still, and the fire comes off her only when she acts. The warmth in
her read comes from the sand-coloured cloth and the brass, not from light.

**The bound light (color_script.md rule 2).** Every emissive slot is `glimmer_bound` at 1.2 with
`emission_pulse_hz` 0. The seams are **geometry** (flattened bands round the cloth's edges, skinned with the cloth
under them), not particles: no flicker, no drift, no shed motes, no trails. Her light moves only because her body
moves. No `glimmer_held`, no `glimmer_lift` (she is bound until her Act III release, Ch20; not built here), and **no
`spawn_wound` anywhere: she has no weak point.** ADR 0151's one answer to where to strike is for foes.

## The kite

- **Panels and seams.** The ribbon is one closed cloth slab (two faces 1 cm apart and a rim) cut into panels by
  cross-seams every 0.4 m. Each hem is a flattened band of seam-light (2.8 cm wide), and each cross-seam a band of
  3.2 cm. The hems draw in 6% between seams, so the outline is a run of kite cells, and the cloth bellies 5% of its
  width behind the frame.
- **The frame** is lashed on the cloth's outer face, the side both battle cameras see: a spine spar (2.4 cm) down the
  middle from the snout to the tail end, a batten (1.8 cm) across the middle of every panel standing 5 cm past both
  hems, a batten across the cheek, and the bowed crest-spar (three rods) from the snout up over the crown and swept
  back past the head.
- **The bridle**: three lines from the head's lower hem (the throat, the cheek and the back of the head) meet in a knot
  0.38 m under the throat, and the key hangs from the knot on a short cord. The key counter-turns 0.9 of the head's
  turn, 0.12 s behind it, so it hangs and swings as she moves.
- **The streamers**: two ribbons from the tail end, splayed a little, lit faintly along their middles.

## Clips (contact seconds go in creatures.json `contact`)

All in place: the stage moves her (the entry's rise from 2.6 m under the water, the dismissal's sink, the fall's tip
back and draw under; choreo.json `vowbound`), and the clips play on top. Every frame of every clip stays above the
water (GroundedClipsTest), so she needs no allow-list entry.

| Clip | Length | What it shows |
|---|---|---|
| `idle` | 4.0 s, loop | a slow undulation runs down her from the nose to the tail (each spine bone bending 0.9° and luffing 4° about its own length, a little behind the one before), so the panels luff in turn; she bobs 4 cm; the streamers flutter twice a cycle |
| `ready` | 1.4 s | she gathers: the coil draws in, the head rears and she lifts 10 cm (0.5 s), then snaps taut (0.95 s) and settles. The stage plays it on the entry and the dismissal until `rise` and `dismiss` are wired (below). |
| `attack` | 1.2 s, contact **0.5 s** | the whipping strike: the neck draws back and the head rears (0.3 s), then the whip runs up the neck and the head lashes forward and down (the contact), the body thrown 16 cm after it, the tail whipped the other way |
| `cast` | 1.6 s, contact **0.6 s** | Kite Flare: a gust through the whole kite (the panels turn and flare), the head rears, then **three quick jabs** of the head at 0.6, 0.88 and 1.15 s (the fast multi-hit fire; the first is the contact) |
| `hit` | 0.5 s, peak **0.1 s** | struck: the body jolts back, the head snaps up and back, the panels twist, the streamers whipped; most displaced at 0.10 s (numpy and GLB) |
| `defend` | 1.2 s | the coil draws in tight round her middle and the head tucks down before the loop, held 0.3–0.85 s, then opens |
| `ko` | 1.8 s | the kite loses its wind: a flinch, then the string goes slack, the head droops 0.5 m, the panels luff loose, and she settles 0.2 m and holds (from 1.45 s); the key still hangs. The stage tips her back a further 38° and draws her under (`vowbound.fall`, 1.5 s). |
| `victory` | 2.2 s | she climbs 18 cm as a kite climbs in a gust, head high, one long wave down her length, and settles |
| `rise` | 2.6 s | the unfurling: from furled (the coil wound tight, the head tucked 0.8 m below its rest), the coil opens and the head lifts by 1.5 s, one wave runs down her, rest at 2.6 s. In place, built for the stage's rise (C10's 2.6 s) |
| `dismiss` | 1.0 s | the furling: the head lifts once (0.35 s), then the coil winds tight and the head bows and tucks; it ends furled (the stage sinks her) |
| `special` | 2.4 s, contact **1.4 s** | **Flare Line**: the coil winds in (a held breath, to 1.05 s), then the whole kite-string is pulled taut in **one straight line** rising 17° toward the foes, from her tail low behind her mark (1.05 m up) to her head 4.8 m ahead over the field (2.65 m up), 5.4 m end to end: the contact, the whole length burning at once. It holds, trembling, to 1.85 s and is let go back into the coil. The pull and the release turn each bone's direction (not its Euler angles), so the line unrolls and rolls up cleanly. |

The kit adds `hit_b` (the hit mirrored and 1.35× heavier; mirroring only rolls the panels the other way, so it needs
no authored copy) and `idle_b` (the cast at 0.3×, 1.4× speed: the fidget). creatures.json maps `kite_flare` → `cast`
and `flare_line` → `special`; `attack` is the physical default.

**Lowest vertex per clip** (skinned from the GLB, GroundedClipsTest's measure): idle 0.72 m, ready 0.76, attack 0.73,
cast 0.76, hit 0.76, hit_b 0.76, defend 0.76, ko 0.56, victory 0.76, rise 0.76, dismiss 0.76, special 0.35 (the line's
tail end as the release swings), idle_b 0.76. Highest: Flare Line's release, 3.48 m.

**What the stage plays today.** choreo.json `vowbound` names `ready` for the entry and the dismissal and `ko` for the
fall; `rise` and `dismiss` wait on battle-presentation, the same request as Ilun's (M3-CRE-639). Also for
battle-presentation: choreo.json `summon_cinematic.first_call_flags` lists only Ilun, so Virel's first call (B16's
full cinematic) needs a `virel` flag there (`ch08_virel_first_call_seen`, declared in flags.tres).

## Rig (16 bones)

`root` (the water point), `body` (the loop's lowest station, 1.06 m up), `fore_0..4` (from the body up the loop's
front and over its top to the back of the head), `head` (the back of the head to the nose), `aft_0..5` (from the body
round the loop's back and out to the tail end), `streamer`, `key` (at the bridle knot, a child of the head). Every
spine bone is 0.5 m of arc. The cloth, seams and spars are weighted **by arc length**, not by distance, because the
coil passes close to itself: each span's bone, blended 50/50 with its neighbour across 0.3 of a span at each joint.

## Budget

≤ 16k triangles (a Vowbound; the creature range is 5k–16k), GLB ≤ 2 MB. Five slots: `sail`, `seam`, `spar`, `cord`,
`key`.

**As built (M3-CRE-641):** **12,158 triangles** (seams 4,620, sail 3,888, spars 2,538, eyes 448, key 352, cord 168,
streamers 144), 6,279 vertices, 16 bones, 13 clips, GLB 1.05 MB.

## Review

The shot `creature_virel` (tests/screenshots/shots.json) shows her idle on the creature stage from `flank_high` (yaw
68°, pitch 24°), with the heroes' scale bars: close to the default battle camera's angle on her and square to her
sails (the stage's `three_quarter`, yaw 35°, would see the coil nearly on edge). Her bestiary portrait
(tools/portraits/portraits.json `virel`, as the Lead asked for Ilun) turns her 72° for the same reason (creatures.json
`portrait`). **Neither is rendered yet: both need the PC.** On the first render, check: the seams' brightness against
the cloth (1.2 is the colour script's value; a set-piece allows 35% glimmer by area, and her seams are a few
percent), whether the cloth reads as lit through from the seams or just pale, the frame's read on the cloth, the key on
the summon frame, and whether the teal seams read as fire held still (the point) or simply as teal.

## As built: the held form (M3-CRE-647, 2026-10-28)

The foe form for the Ch20 release fight (act3_roster.md, "The Vowbound as foes").

- **`release`** (3.4 s, its KO as a foe; the only clip added, every other clip samples identically): the kite's last flight: the coil draws in once, then unrolls (0.55–1.45 s, bone directions slerped as Flare Line does) into one line climbing 38° away from the party, the panels luffing and the streamers flying; then the line lifts 1.5 m up and 0.6 m back. Let go, not cut.
  Lowest vertex over every frame +0.66 m. GLB 1.05 → 1.13 MB.
- Scene `game/creatures/virel/virel_held_battle.tscn` (the same GLB; `CreatureActor.material_dir` puts on `assets/creatures/virel/materials_held/`, written by write_materials.py from the `held` block in materials.json: 2 emissive slots glimmer_bound to glimmer_held `#7FC6D9` at the same energy, steady; the rest as they are). creatures.json row `virel_held`: no `vowbound` key, `ko` = `release`, `phases.release` = {clip `release`, `hold` true}, `stand_in.yaw_deg` 90 (facing the party), portrait framing kept. Review shot `creature_virel_held` (not rendered yet). No enemies.json row (Combat's, with the chapter designer). The turn to `glimmer_lift` and the rising motes are presentation (battle VFX), not the model.

## Final pass (M3-CRB-008, 2026-10-28)

ADR 0041 (Act I at final quality). The critique of the M3-CRE-641 render: primitive. The body was a closed ring of
identical box panels (a tyre, not a serpent in flight), the seams glowed like neon tubing, the head was a flat fish
cut-out with a stick-on eye and the key a tiny ring on a stick. build_virel.py's spine, layout and mesh are rewritten
on the same kit; every bone, clip and material slot name, the contact times (creatures.json: attack 0.5 s, cast
0.6 s, special 1.4 s), the held form (`release`, `materials_held/`, virel_held_battle.tscn) are kept. Where this
section differs, the sections above are history (the coil, its framing numbers, the seam and key descriptions, the
budget line).

- **An open S in flight, never a loop.** The head leads, raised, 2.4 m toward the foes (nose 3.1 m ahead of her
  mark, 2.4 m up); the neck dives to a trough 1.2 m up just ahead of her mark, the body climbs to a second crest
  (2.1 m) and the tail streams back and down past her mark and away from the cameras, trailing its kite-tail. The
  S lies in the same plane, turned 22° off the battle axis, and swings a little in depth along its length (the
  neck toward the cameras, the tail away). The ribbon is 4.85 m behind a 0.70 m head (was 5.5 m: the S has to fit
  the default camera's safe frame, whose right edge allows little behind her mark), 0.34 m wide at the neck, 0.38 m
  mid-body, 0.12 m at the tail's end. The 11 spine bones are an eleventh of it each (0.44 m).
- **Panels of real sailcloth.** 15 panels of 0.3–0.44 m (shorter toward the tail), each cross-seam cut on the bias
  at its own angle (up to about 40°), so the panels are trapezoids and rhombs, not boxes; each panel is its own
  bolt (sand, bark-tanned `sand_cloth`/`tortoiseshell`, `sand_dry`, `sand_wet`, a thatch-yellow), with its own cut:
  a scalloped or bowed upper hem, often a burnt bite out of it, and the belly hem drawn out to a pointed flap at
  its trailing corner (the serrated kite-cell edge of her underside). The cloth bellies behind the frame, troughs
  along each batten and carries tension wrinkles; it is sun-faded along the upper hem, grimed toward the belly and
  tide-line stained. Four Saltwright mends (faded teal, sea blue, new white) are their own sewn-on rectangles with
  a darker stitched border. A folded hem tape binds both hems.
- **The frame:** a bamboo spine spar (nodes every 0.27 m) on the outer face, a bowed batten mid-panel following the
  bias between the seams and standing 1.8 cm past both hems, a cord lashing at each crossing, a brass grommet in the
  upper hem tape at each batten's end. Cane is `thatch` to `timber_weathered`, darker at the nodes, scorched where it
  crosses a seam.
- **Fire along every seam, held still.** Each cross-seam is a raised felled seam (4.8 cm lips to lips) with a thin
  burning core (`glimmer_bound`, mask 0.32–1.0, its width and heat wandering along the seam in beads of ember), an
  ember-lit ring of char (mask 0.06–0.22) and black lips; the cloth either side is scorched `tortoiseshell` to
  `lacquer_black` for about 9.5 cm (a ragged edge), lit faintly through at the seam (0.12). The hem tapes' stitching
  smoulders in patches (up to 0.4). Clusters of small flame tongues (thin double-faced blades, 4–12 cm, broad at the
  root and brightest there, curling and leaning back toward the tail as a flare's flames stream downwind) lick off
  the upper hem where each seam meets it, with a few on the belly hem and between seams. They move only as her body
  moves: no flicker, no drift, no motes.
- **The colour rule, and the choice (documented as the brief asked).** The critique asked for fire swatches on the
  burning seams if palette.json allows. It does not: `ember_orange` is "flame and horizon only; never a surface
  albedo" and the Fire VFX base, `glimmer_bound` is the light of "Vowbound forms" (steady), act1_ch08.md F07 and §5
  say her seams read as steady `glimmer_bound` with the fire element in her battle VFX only, and write_materials.py's
  held swap requires every emissive slot to be `glimmer_bound` (a warm emissive slot would break `materials_held/`).
  So every light on her is `glimmer_bound` at 1.2, steady: the seam cores, the flame tongues, the eyes and the glow
  in the mouth (her soul-light). The **fire reads through the burn**, not the hue: the scorched and charred cloth
  round every seam, the ember ring, the bitten hems and the frozen flame tongues; the warmth comes from the tanned
  cloth, the scorch and the brass.
- **The head, a kite-dragon's.** Two double-layered cheek panels meet on a cane skull ridge (a wedge, 0.2 m across
  at the cheek, not a cut-out), with a raised brow; the lower jaw is its own V of cloth on a keel cane, hung open, the
  palate and the jaw's floor dark and glowing toward the throat (0.2–0.65), a burning seam along each lip, at the
  neck and down the cheek seam. A **lantern-eye** on each cheek: a ribbed paper bulb 12 cm across lit from inside,
  darker ribs, a dark pupil at its crown looking a little forward, in a lashed cane ring, under a cane brow. A
  painted face (a teal ring round the eye, a dark stroke swept back over the cheek, a pale muzzle, a tanned crown).
  A cane **nose scroll** curls up at the snout. A **cheek frill** each side: a fan of five cane ribs with cloth
  cells (sand and faded teal, burnt edges, lit at the rim) swept back over the neck join. Cord **whiskers** from the
  snout stream back and hang, each ending in a tassel. The bowed **crest-spar** (two rods) sweeps back past the
  head with a slim faded-teal pennant hung from it.
- **The keepsake.** The brass tuning key is 0.37 m from the bow's crown to the socket: a cast ring bow (11.6 cm
  across, facing the cameras) with a bead at its crown where the cord's loop passes, a collar, a turned shaft with
  two scored bands (`bronze_patina` in them), and a flat-shaded square socket with a dark hollow end; worn bright
  (`sand_dry`) on the bow's outer rim and the collar, tarnished in the hollows. It hangs on a 7 cm cord from the
  bridle knot, 0.26 m under the jaw (three lines: two from the jaw's keel, one from the throat). materials.json
  `key`: metallic 0.75, roughness 0.24, specular 0.7, rim sheen 0.5 (the glint). Still no light of its own.
- **The tail:** two ribbon streamers (0.86 m faded teal and 0.7 m sand, swallowtail ends, scorched tips) and between
  them a kite-tail: a 0.95 m cord with three cloth bows (sea blue, faded teal, sand) and a 12 cm tassel. **The
  kite-tail now hangs** (new `hang_tail`, like the key's `hang_key`): the streamer bone undoes 0.6 of the tail end's
  world turn, 0.1 s behind, on top of its keyed flutter, so it hangs on its string instead of swinging out with
  every turn of the tail (not in `release`, where it flies).
- **Rig (18 bones):** the 16 kept, plus two unweighted VFX anchors: **`vfx_core`** on `body` (the body bone's
  station, the S's trough, mid-body: 0.71, 1.25, 1.01) and **`vfx_keepsake`** on `key` (the key's bow, 1.03, 1.86,
  2.50).
- **Clips.** `idle` is a travelling wave: each spine bone bends in the S's plane (1.9°) and sways out of it (1.4°) a
  beat behind the one before (0.62 rad a bone, about one wavelength along her), growing toward the tail, while the
  panels luff twice a cycle (4.5°); she bobs 4 cm and the streamers flutter. Flare Line's wind-in is the S drawn
  together (the head rears back over her, the tail curls under: head to tail 2.3 m at 1.0 s), then the line (4.75 m
  head to tail at the contact; tests/unit/test_creature_virel_vowbound.gd `LINE_M` 5.0 → 4.5 for the shorter body),
  its tail anchored 1.05 m up, 0.2 m behind her mark. The furl (`rise`'s start, `dismiss`'s end) dives the head
  0.68 m below its rest and curls the tail up; `defend` likewise. The attack's tail and the victory's gust are
  calmer (the tail's swing kept inside the safe frame). Contact times unchanged.
- **Framing** (every baked frame, projected through both cameras from the numpy poser). Default camera at rest:
  left 0.46, right 0.075, top 0.081, bottom 0.211. Tightest: right 0.005 (hit), 0.015 (Flare Line), 0.026
  (attack), 0.027 (victory); top 0.003 (Flare Line's line), 0.03 (victory). **Every clip she plays as an ally is
  inside the default camera's safe frame**, Flare Line included now. Summon shot: top 0.21–0.23 on `ready`, `rise`
  and `idle`; her body (lowest hem 0.92 m) is above the bottom line, and the kite-tail's strands and tassel (to
  0.38 m) hang under it, as pipeline.md expects for strands.
- **The stand-in's anchors (was the request to UI above).** creatures.json `virel` and `virel_held` now carry their
  own `stand_in` `height` 2.6 and `radius` 0.8 (the M3-CRE-640 mechanism Kahre and Nhoa use), so chest (1.56 m) lands
  on the S's middle and head (2.6 m) at her head's height.

**As built:** 17,750 triangles (≤ 18k): sail 4,860, spars 1,850, seams 1,736, flames 1,272, tapes 1,080, head canes
940, head cloth 904, tail 772, frills 688, key 662, whiskers 536, eyes 496, lashings 450, head seams 420, grommets
420, cord 264, nose 140, vane 132, mends 128. 11,133 vertices, 18 bones, 14 clips (with hit_b and idle_b), GLB 1.55 MB.
Rest bounds: x −1.10 to 1.33, y 0.38 (the tassel; the body 0.92) to 2.96, z −0.45 to 3.11. Lowest vertex per clip:
idle 0.14 m, ready 0.18, attack 0.38, cast 0.38, hit 0.38, hit_b 0.36, defend 0.37, ko 0.38, victory 0.48, rise
0.38, dismiss 0.38, special 0.07, release 0.10, idle_b 0.38. Highest: Flare Line 3.44 m, release 5.74 m.

**Not done:** no portrait (test_creature_portraits fails on the missing Vowbound portrait PNGs, before and after this
pass); creatures.json `portrait` (yaw 72°) is unchanged and should be re-checked against the S when it is rendered.
The held review shot (`creature_virel_held`, the stage's front-on view of a foe facing the party) sees the S nearly
on edge, as it saw the coil.
