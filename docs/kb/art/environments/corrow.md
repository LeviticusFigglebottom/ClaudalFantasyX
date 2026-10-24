# Corrow Bastion and the Seawall: Design Notes

Owner: Environment Artist (M3-ENV-04). Lighting: Rendering (the Undertow itself is Rendering's: M2-RND-01,
`UndertowStorm`). Gameplay placement: m2-slice (swap-in note in the task file and
`docs/kb/handoffs/live/env-art.md`).
Story: [act outline Ch8 "The Seawall"](../../story/beats/act_outline.md) (the evacuation set-piece, Liss's
hoist, Pell on the wall, Kerrid at the stair foot, the wall falls), Ch9 (the night variant, the stair foot at
slack water), [bible §5.4 Corrow](../../story/bible.md) (the Watchers, the Fisher Stair, the stair-watch and
its stair-law, the Coilspire beacon), bible's 1001 AL row (Imra, Dace and Kerrid on this stair),
[ADR 0017](../../decisions/0017-act-one-restaging.md) (Corrow has no weapon and nobody pretends otherwise),
[ADR 0020](../../decisions/0020-kerrid-restaging.md) and [ADR 0022](../../decisions/0022-dace-imra-strangers-sweep-f.md)
(c) and (g) (no rope-burn glow at the stair foot). Grade: [color script `ch08`](../color_script.md) and its
`storm_grey` water look. Colours: [palette.json](../palette.json).
Zone: `game/levels/ch08/corrow/`. Kit: `assets_src/environments/kits/corrow/`. Preview:
`game/levels/_tests/corrow_kit/`.

**The feeling in one line:** a warm, carved, nine-hundred-year wall holding the last of the afternoon sun
against a slate storm: the most beautiful thing in Corrow, about to fail.

**Influences** (references.md, in words): Khmer laterite galleries, where porous rust-red blocks are laid
dry in long courses and then carved in place, so the joints run straight through the carved faces; old
harbour moles and sea dykes, a battered sea face with a tumble of rip-rap at its foot and a broad walk on
top; fishing quarters huddled under a sea defence, their roofs below the wall-head. **Our originals and
transformations:** Khmer face towers → **the Watchers**: not towers and not facing four ways, but a single
row of colossal heads that *are* the wall's parapet (each head is a merlon, the gaps between them are the
embrasures), with closed eyes and open, humming mouths, and a crown of breaking-wave scallops (an original
motif, ours alone); below them two staggered rows of the same faces in relief on the sea face, all looking
out to sea. The **Fisher Stair**: a single broad stair built up the wall's inner face, its treads dished by
nine hundred years of feet, with an iron-stanchioned hand-line on its open edge (the line Kerrid held).
**Liss's hoist**: a salvaged spar bolted into the back of a Watcher's head, plain rope and iron.

**Act I rule (references.md "No grimdark desaturation in Act I").** Ch8 is Act I's edge: "warm laterite,
cold sky: the fight at the edge of the color arc" (color script). So the warmth lives in the *stone*: the
laterite is never brown-grey mud; it stays rust and ochre in light and teal-shadowed in shade (rule 5),
with salt and spray darkening it low. The sky and sea carry the cold. Saturation is ×0.95, not lower.

---

## 0. Layout, Orientation, and Lighting

**Geography (world north = −Z, +X east).** Corrow sits at the head of a shallow bay on the Low Reaches'
outer coast; the open sea is to the **south**. The **seawall** arcs across the bay's mouth for about 1.1 km,
convex to the sea: its walk's centre line is an arc of **R = 240 m** about a centre inland (north). The
**low town** (the fishers' quarter) lies behind it on reclaimed ground at **+1.0 m**, below storm-surge
level, which is why the stair exists. The Bastion (the Stillguard garrison, a later task) stands at the
wall's west root on higher ground. The **Coilspire** headland closes the bay to the east: "the headland where
storms always break". Its spire stands about 480 m east-south-east of the stair head, and its beacon is the
one warm point on the skyline.

```
                   N (-Z)       hinterland (rising to +20 m)
                    |
     Bastion   low town (+1.0)   houses   houses
     (west)    lanes ↑ ↑ stair foot
   ============\=====[ FISHER STAIR ]======================\\  seawall (R 240 m, convex to sea)
     Watchers' heads (parapet, sea side) ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲  \\
     sea face reliefs, rip-rap apron ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈ \\___ Coilspire headland
                    |          open sea (storm_grey)                (beacon lit), ESE
                    S (+Z)   the storm front comes in from the SOUTH-EAST
                             the sun (250°) lights the sea face from the WEST-SOUTH-WEST
```

- **The wall's section** (origin on the walk's centre line at walk level; +Z is the sea side):
  the **walk** at **+12.0 m** (6.0 m wide, z −3.0 … +3.0), paved in big laterite slabs, dished and
  puddled; the **parapet course** on the sea edge (z +3.0 … +4.2, 0.9 m tall) and on it the **Watchers'
  heads** (2.4 m tall, every 3.0 m: 0.9 m gaps are the embrasures); a **kerb** 0.5 m tall on the inner
  edge; the **sea face** battered 12° from the parapet down to the rip-rap at **−1.0 m** (so the foot is
  about 2.8 m further out to sea); the **inner face** battered 6° down to the low town at +1.0 m.
- **The Fisher Stair** climbs the inner face from the low town to the walk: **3.2 m wide** ("wide enough to
  matter, not wide enough"), 11 m of rise in two flights with a half-way landing, 0.2 m risers and 0.34 m
  treads, dished in the middle by feet. Its open edge carries the **hand-line**: a tarred rope through iron
  eyes on stanchions every 2 m. The stair-watch's law is cut into nothing; it is spoken (no inscriptions).
- **Liss's hoist** is bolted into the back of the Watcher's head nearest the stair head: a 5.5 m spar raking
  out over the inner face, a block at its tip, the fall of rope to a sling-board in the lane below.
- **The party arrives on the walk** from the west and holds the wall-head over the stair, looking east along
  the curve with the sun behind them: the heads are front-lit warm against the storm.
- **The storm (the Undertow) comes from the south-east**, over the sea; the sun at 250° still slants in
  under its western edge. By 16:40 the front has covered the sun.

**Tide datum:** `tide_line_y = 0.0` at mean sea level (Haluna). Storm surge: the sea stands at **+0.6 m**
under the front (phase `front`) and **+1.8 m** at the height of the storm (phase `surge`), which floods the
low town lanes about 0.8 m deep at the stair foot: Kerrid's "waist-deep in the storm-dark and the spray".
The rip-rap's top is at +1.0 m; the low town at +1.0 m; the walk at +12.0 m.

**GI recommendation:** an open exterior. **SDFGI on GPU tiers, sky ambient + SSAO on Low and lavapipe**
(the Haluna README's finding). The beacon is one shadowless OmniLight3D at the spire top; in `surge` it is
the frame's warm accent.

| Sub-frame | Use | Time | Sun elev / az | Key | Fill | Rim | Fog | LUT |
|---|---|---|---|---|---|---|---|---|
| `ch08` (color script) | Arrival, the evacuation's start, the hoist | 16:00 | 30° / 250° | `#FFE4CE` (~4,900 K), energy 2.0 | `#5E6E80` at 0.5 (sky ambient tinted to it) | `#CFE8FF` 1.2 (characters) | albedo `#5E6670`, volumetric density 0.03 (spray haze) | `lut_ch08_storm`: laterite kept warm (hue 10–40° spared the cut), sky and sea pushed toward slate teal, saturation ×0.95, S-curve 0.65, teal toe |
| `ch08_surge` | The stair foot, the boss, the wall falls | ~16:40 | 22° / 255°, **behind the front** | `#FFE4CE` at 0.35 (the sun as a smear) | `#5E6E80` at 0.6 | `#CFE8FF` 1.2 | `#5E6670`, volumetric 0.06 | `lut_ch08_storm` |

Lightning frames (2.0× exposure for 2 frames) are Rendering's `UndertowStorm` events and are not in the kit.

**Exposure, key product and water** (ADR 0014): exposure 0.80, k = 0.80 × 2.0 = 1.6. Water: **`storm_grey`**
(σ 4.5 / 1.13 / 0.95 m⁻¹ = base × 2.25; `col_scatter_shallow` `#1F7F86`, `col_deep` `#0E4A55`, `col_sss`
`#1F7F86`), validated on screen at `#126462` · `#115F5D` · `#0F3C3B` · `#143332`: dark churned teal under a
slate sky. Waves: a storm swell from the south-east (wavelengths 96 / 54 / 29 / 14 / 6.5 m, amplitudes to
0.55 m) with foam on, breaking on the rip-rap.

**Value structure.** The upper half of a frame is the slate sky (dark-mid); the **laterite in sun is the
brightest large value** (the inversion that makes the frame: light stone against dark sky). The darks are
the embrasure gaps, the mouths of the Watchers, the wet stone low on the sea face, and the sea. The beacon
is the hottest point but tiny. Nothing in the zone is whiter than the foam.

---

## 1. Mood by Moment

1. **Arrival on the walk (16:00, `ch08`).** The wall runs away east in its curve, head after head, each
   one sunlit on its west cheek. Beyond the heads, over the sea, the storm is a slate wall; to the left the
   Coilspire stands on its headland with its beacon lit. The walk is wet with spray; people are already
   moving down below.
2. **The evacuation (`ch08` → `ch08_surge`).** Looking down from the wall-head: the stair packed with
   climbers, the lanes of the low town filling with water, Liss's spar out over the face with a child in
   the sling. Pell on the parapet between two heads, calling into the wind.
3. **The stair foot (`ch08_surge`).** From the lane, waist-deep: the stair rises steeply into spray and dark;
   the top is lost. One figure stays at the bottom step (Kerrid). **No glow of any kind** at his hands or
   on the stair: the only light is the beacon, far off.
4. **The wall falls.** A destroyed state: a breach where three segments have gone, the heads tumbled into
   the low town, the stair's upper flight hanging. **Follow-up task (M3-ENV-04B)**; the kit is built so a
   breach can replace segments one for one.
5. **Ch9 night (the variant, a later pass).** The same stair foot at slack water, under stars, with the
   motes going out to sea: the `ch09` frame on these pieces.

---

## 2. Kit Pieces (origin on the ground or at walk level as stated, +Y up; the wall is built along +X with
the sea on +Z and bent onto the R = 240 m arc)

| Kit | Pieces | Key dimensions and parameters |
|---|---|---|
| **Seawall** | `seawall_curve` | One **12 m** run of the wall (arc length on the walk's centre line), bent about R = 240 m (centre at local z = −240), so segments laid edge to edge at 2.865° steps close exactly. Origin at walk level on the centre line. Walk, parapet course, kerb, battered sea face (12°) and inner face (6°), the footing at −1.0 m (sea) and +1.0 m (town). Faces are displaced grids carrying **0.5 m courses with staggered head joints** (geometry grooves, 1.5 cm) and a little per-block proud/sunken offset, so coursing reads at 100 m where the texture cannot. Per-segment seed varies blocks. |
| **The Watchers** | `watcher_head`, `watcher_relief` | Head: a parapet merlon carved as a colossal face, **2.4 m tall, 2.1 m wide, 1.2 m deep**, built of four courses of blocks (the joints cut through the face), standing on the parapet course. Face to the sea: high brow, **closed lids** (convex, a down-curving crease), straight nose, cheeks, **open, rounded mouth** as if humming, chin; a crown band of breaking-wave scallops. Back: plain blocks. Relief: the same face carved **3.0 m tall** in a 3.4 × 3.6 m panel set flush into the sea face (tilted to its 12° batter), in two staggered rows (+4.5 m and +8.5 m centres). Salted and wet low, worn smooth on the brows and noses (A channel). |
| **The Fisher Stair** | `fisher_stair` | A 24 m piece set against the inner face (two segments long), bent onto the same arc, origin at the low-town ground at the stair foot. 3.2 m wide: flight 1 (27 risers, 0.2 / 0.34 m), a 3.2 m landing at +6.4 m, flight 2 (23 risers) to the walk at +12.0 m (local x from 0 to 22.6 m). Solid masonry body below the treads; tread tops **dished** up to 4 cm in the middle; nosings worn round; a hand-line on the open edge: iron stanchions (1.0 m) every 2 m, eyes, a tarred rope line in shallow sags. |
| **Liss's hoist** | `liss_hoist` | Bolted to a `watcher_head`'s back (origin at the head's base centre, same yaw). A **5.5 m** salvaged spar (0.16 m), its heel in an iron shoe on the walk, raking 35° out over the inner face; two iron strap-plates with four bolt heads into the stone; a guy rope back to a ring in the walk; a double block at the tip; the fall of rope to a sling-board 6 m below. All rope and iron, nothing bound (no emissive). |
| **The foot** | `wall_apron` | A 12 m strip of rip-rap on the sea foot (bent on the arc): tumbled laterite blocks and dark boulders 0.6–1.6 m from −1.5 to +1.0 m, wet, barnacled low. |
| **Low town** | `lowtown_ground`, `lowtown_house_a`, `lowtown_house_b` | Ground: a 24 × 24 m cell at +1.0 m (edges exactly there so cells tile): packed-earth lanes, worn cobble patches, a stone gutter, puddles in the hollows (VC.B). Houses: fishers' houses of laterite rubble (2.6 m walls), dark door and windows, a timber lintel, net hooks, a **red clay tile hip roof** (the Haluna roof generator, read-only): a 5 × 6 m and a 4 × 7 m. Roofs stay below the walk's level so the wall dominates. |
| **The skyline** | `coilspire_headland` | A far piece (seen at 300–800 m): a rocky headland 260 × 180 m rising to +34 m, and the **Coilspire** on it: a hollow tapering stone spire 46 m tall, its old **copper flues coiled** round it in three bands (bronze patina), and the **beacon cage** at the top with a fire (emissive `ember_orange`). The temple's interior is a later task (`ch08/coilspire`). |
| **Far ground** | `corrow_far` | A 1.4 km apron: the hinterland north of the wall rising to +20 m; the seabed south of the wall falling to −9 m (the sea shows dark over it); a hole for the preview's low-town cells. |

**Budgets (triangles, LOD0 / LOD1):** seawall 12,000 / 900; watcher head 7,000 / 400; relief 7,000 / 300;
stair 12,000 / 900; hoist 3,000 / 300; apron 6,000 / 500; ground cell 4,800 / 320; houses 16,000 / 1,400;
headland 9,000 / 1,500; far apron 3,600 / 900. LOD1 begins at 70 m and every piece is a chain (`<piece>`,
`<piece>-lod1`), so exactly one LOD draws at every distance (vegetation.md "One LOD at every distance").

## 3. Materials (palette.json names)

| Slot | Shader | Look |
|---|---|---|
| `cw_laterite` | weathering (triplanar, new `laterite` texture) | the wall: `laterite` `#A8573A` blocks, porous (vesicular pits and limonite nodules), varied block to block from rust to ochre (UV2.y), salt crust in the spray band, wet and algae low, worn smooth on edges (A) |
| `cw_laterite_carved` | weathering (laterite texture, finer tile) | the Watchers: the same stone, a shade paler where the carving has weathered smooth, rougher in the eyes' creases and the mouths |
| `cw_paving` | weathering (laterite texture, larger tile) | the walk's slabs: the stone worn smoother and darker with feet, puddles from VC.B (`wet_roughness` 0.08, so the walk mirrors the storm sky) |
| `cw_rubble` | weathering (Haluna `coral_stone` greyed) + laterite tint | rip-rap: dark weathered boulders among laterite blocks, barnacles and algae low |
| `cw_earth`, `cw_cobble` | weathering (Brine Shoals `mud` and `shingle`, read-only) | the low town's packed earth (warm grey-brown) and cobbles, puddled |
| `cw_house_stone` | weathering (laterite, coarse) | rubble house walls, lime-washed patches gone grey (`mortar_white` at low cover) |
| `cw_timber`, `cw_rope` | weathering (Haluna `timber`, `woven_panel`) | lintels, the hoist's spar (sun-silvered `timber_weathered`), tarred hemp |
| `cw_roof_tile` | weathering (Haluna `roof_tile`) | `roof_clay` tiles, salt-dulled |
| `cw_iron` | standard | the hand-line stanchions, the hoist's straps and bolts, shoes: wet rust-dark iron |
| `cw_interior_dark` | standard | doors and windows: deep shade (`#2A2622`, above the albedo floor) |
| `cw_copper` | weathering (detail map) / standard | the Coilspire flues: `bronze_patina` green-cyan with dark copper |
| `cw_headland` | weathering (Haluna `coral_stone`, darkened) | the far headland's rock: dark, wet, `volcanic_stone` toward `cold_blue_stone` |
| `cw_beacon` | standard, emissive | the beacon fire, `ember_orange` at emission 6 (tiny at 480 m, the warm accent) |

Weathering channels follow haluna.md §4 (**R moss, G salt, B wet, A erosion**). The sea face carries a salt
band from +1 to +8 m and wet below +2 m (VC.B, plus the live tide line); the walk is wet in its puddles; no
moss on the sea face (spray), a little on the inner face's lower courses (R).

---

## 4. Composed Shots (vFOV = 2·atan(12 / mm); heights above the local ground)

All at `ch08` unless noted. **◆** marks the preview shots built in `corrow_kit/`.

| # | Lens (vFOV) | Height | Framing | What the shot is about |
|---|---|---|---|---|
| C01 ◆ | 28 mm (46.4°) | 1.7 m on the walk, west of the stair head, looking east-south-east along the curve | The Watchers' heads recede in a row on the right third, sunlit on their west cheeks, against the slate storm over the sea; the wet walk leads in; the Coilspire with its beacon on the left of the skyline. Sky ≈ 45%. | Arrival: the wall as the town's whole defence, beautiful and doomed. |
| C02 ◆ | 24 mm (53.1°) | 1.6 m in the lane at the stair foot, looking up | The Fisher Stair rising from the lower left to the wall-head; Liss's spar against the sky at the top right; a house corner frames the left. | "Wide enough to matter, not wide enough." |
| C03 ◆ | 50 mm (27.0°) | 2.0 m above the sea, 40 m out, looking north-north-west | The sea face: two rows of relief faces and the parapet heads, the low sun raking across them from the west so every lid and lip throws a shadow; spray at the foot on the rip-rap. | The Watchers humming out to sea. |
| C04 ◆ | 35 mm (37.8°) | 1.6 m on the walk beside the hoist's head | The back of a Watcher's head with the spar bolted into it, the rope falling over the edge to the lane; the walk curving away behind. | Plain rope and iron, bolted into something sacred. |
| C05 ◆ | 35 mm (37.8°) | 1.1 m above the flood, `ch08_surge` | The stair foot from the flooded lane: dark water to the bottom step, the stair rising into haze, the beacon a far warm point. No glow on the stair. | Where the captain died in 1001 (the player does not know yet). |
| C06 ◆ | 18 mm (67.4°) | 30 m above the low town, looking south over the wall | The layout as a diagram: the lanes, the stair, the walk, the heads, the sea face and the storm sea. | The player sees the space (pillar 4). |
| C07 ◆ | 35 mm (37.8°) | 2.0 m, kit row | Review only: the kit pieces in a row on the far apron. | The kit, side by side. |
| C08 | 85 mm (16.1°) | 12.5 m, from the walk | One Watcher's face in profile against the storm, its humming mouth. (Cinematics.) | The wall's voice. |
| C09 | 65 mm (20.9°) | 13 m | Rhen at the wall's edge, the storm wall filling the frame. (Cinematics, with `UndertowStorm`.) | The figure in the storm. |

**Registered baselines (the repo's binary budget: at most two):** chosen after the captures (§6).

## 5. Review Checklist

- [ ] Grayscale check: the sunlit laterite is the brightest large value against the slate sky; darks in the
      embrasures, the mouths, the wet low stone and the sea.
- [ ] Shadows teal, not grey (rule 5), even on the laterite.
- [ ] The laterite stays warm (hue 10–40°) in every `ch08` frame; the sky and sea stay cold.
- [ ] Every Watcher's eyes are closed and its mouth open; no face copies a real temple's.
- [ ] No glow at the stair foot (ADR 0022 (g)); the hoist carries nothing bound.
- [ ] Red ≤ 8% (the roofs only), gold 0%.

## 6. The Preview (M3-ENV-04)

Filled in after the captures (lavapipe, 960 × 540).

## Revisions
- 2026-10-24 (env-art, M3-ENV-04): first version, written against the act outline Ch8 and Ch9, bible §5.4
  and its 1001 AL row, ADRs 0017, 0020 and 0022, and the colour script `ch08` row before any geometry.
