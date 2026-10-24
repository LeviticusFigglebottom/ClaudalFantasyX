# Brine Shoals: Design Notes

Owner: Environment Artist (M3-ENV-02). Lighting: Rendering. Gameplay placement: m2-slice (swap-in notes in
`docs/kb/handoffs/live/env-art.md`).
Story: [act outline Ch6 "Salt Edict"](../../story/beats/act_outline.md), [ADR 0017 (a)](../../decisions/0017-act-one-restaging.md)
(Sefir's first appearance), [bible §7 The Saltwrights](../../story/bible.md) (salvage, brine-branding, burned
camps), bible §5 (Ansedra: barges are poled, never rowed, and no wake is permitted). Grade: [color script
`ch06`](../color_script.md) and its `silted_flats` water look. Colours: [palette.json](../palette.json).
Zone: `game/levels/ch06/brine_shoals/`. Kit: `assets_src/environments/kits/brine_shoals/`. Preview:
`game/levels/_tests/brine_shoals_kit/`.

**The feeling in one line:** the Order's violence in daylight on a beautiful, ruined shore: brown-grey flats
that mirror the sky, black wrecks, orange fire, and one white barge that the smoke cannot touch.

**Influences** (references.md, in words): tidal mud-flats and creeks at low water, where the wet mud holds
the sky like a dull mirror and every footprint fills; ship-breaking beaches where hulls are taken apart by
hand on the sand; a nomad salvage camp of lashed spars and sail-cloth. **Our originals:** Saltwright camp
furniture built from salvage (oars as tent poles, hull plating as tables, glass net-floats as lamp lenses), the
brine vats in which the wrights cure brine-glass, the Order's branding brazier, and Sefir's poled white
barge, which is Ansedra's stillness eight chapters early.

**Act I rule (references.md "No grimdark desaturation in Act I").** Ch6 is the least saturated Act I frame
(×0.90), and it is still Act I: the sorrow comes from beauty with an ending, *not from mud*. So the mud is
never flat brown. It is warm grey-brown in sun, teal in shade (rule 5), and where it is wet it carries the
sky's blue and the fire's orange in soft reflections. The flats should look *gorgeous and doomed*
(pillar 2): a glittering shore with a camp burning on it.

---

## 0. Layout, Orientation, and Lighting

**Geography (world north = −Z, +X east).** The Brine Shoals are a belt of mud-flats and sand-bars on the
south coast, about 3 km of route, crossed at low water. A **shoal channel** (a tidal creek, 9–13 m wide at
low water and 1.3–1.7 m deep in its bed) winds north from the open sea into the flats. It is the only water
deep enough for a hull at low tide, which is why the Saltwrights camp beside it and why the barge can come up
it at all. The route of wrecks runs east to west along the flats: ships that grounded on the bars over the
centuries, now black ribs and hull sections the wrights take apart.

```
            N (-Z)
            |
   wreck    |  channel (winds N)        mast stub
   ribs  ·  |  ~~~~                         |
  plank walk ======== camp hard ====≈≈      |      route of wrecks
  (route, from E) ← ← ← ← [tents/rack]≈  hull section   ← party arrives from the east
            |       tideline ≈≈≈≈≈≈        bow
            |  ~~~~ (to the sea, S)
            S (+Z)                       wind from SW -> smoke leans NE across the channel
```

- **The camp** stands on a **hard**: a low shingle-and-shell bank 0.5 m above the flats on the channel's
  **west** bank, 20 × 14 m. It is the only dry ground for a long way, so the wrights' tents, racks, crates,
  salvage piles and brine vats crowd onto it. A plank walk leads to it across the mud from the east.
- **The party arrives from the east** along the plank walk, walking **west, into the 240° sun**: the smoke is
  backlit and glows amber, and the burning tents throw long shadows toward the lens.
- **The wind is from the south-west** (onshore sea breeze, 5 m/s). The smoke leans **north-east, across the
  channel**, so the barge coming up the channel from the south passes *through* it (ADR 0017 (a)).
- **The tideline** (high-water strand line) runs along the hard's south and west edges: a band of wrack weed,
  shell grit, sticks and salt crust at +0.9 m above the datum. Liss buries her lamp in it (side scene).

**Tide datum:** `tide_line_y = 0.0` at mean sea level, as in Haluna. The raid happens at **low water, still
falling: water at −0.35 m**. The flats lie at 0.0 to +0.3 m (damp by capillary rise, wet where VC.B is
painted), the hard's top at +0.5 m, the strand line at +0.9 m. The channel bed is at −1.3 to −1.7 m, so the
barge (draft 0.5 m) has a metre under its keel. Pools in the flats' dips hold water at the same −0.35 m.

**GI recommendation:** an open exterior, single lighting state: **SDFGI on GPU tiers, sky ambient + SSAO on
Low and on lavapipe** (the Haluna README's finding: SDFGI on lavapipe loses the sky fill, which breaks rule
5). The fire is lit by a handful of shadowless OmniLights in `ember_orange`; they are fill, not key.

| Sub-frame | Use | Time | Sun elev / az | Key | Fill | Rim / fire | Fog | LUT |
|---|---|---|---|---|---|---|---|---|
| `ch06` (color script) | The raid, the boss, Sefir's barge | 15:30 | 35° / 240° | `#FFD5B3` (4,300 K), energy 2.4 | sky ambient `#A8B8B0` at 0.55 | `#E0702E` rim 0.7 (characters); fire omnis `#E0702E` 1.5–3, range 6–9 m, no shadows | albedo `#B8A890`, volumetric density 0.02 (smoke haze) | `lut_ch06_smoke`: amber haze in the highlights, mud greens desaturated, saturation ×0.90, S-curve 0.5, fire kept hot |
| `ch06_after` | Side scene: Liss at the tideline after the barge has gone | ~16:40 | 24° / 255° | `#FFC79A` (3,800 K), energy 2.2 | `#A8B8B0` at 0.5 | fire omnis off; embers only (emission) | volumetric 0.012 (smoke thinning) | `lut_ch06_smoke` |

**Exposure, key product and water** (ADR 0014): exposure 0.70, k = 0.70 × 2.4 = 1.7 (a sun-facing surface
reads near the palette's `onscreen_hex` +1 column). Water: `silted_flats` (σ 7.0 / 2.1 / 1.91 m⁻¹, own
ratio; `col_scatter_shallow` `#6E7A62`, `col_deep` `#4A5A50`, `col_sss` `#7A8A6A`, caustics off), validated on
screen at `#47534C` · `#47524C` · `#454335` · `#474840`: grey-green mud water, chroma ≤ 0.023, so the burning
camp's orange carries the frame. The channel is sheltered, so its waves are the lagoon set at reduced
amplitude; where the barge passes there is **no wake** (Cinematics: the barge moves without a wake mesh or
foam trail).

**Value structure.** About 55% of a frame is upper-mid values (hazy sky, sunlit wet mud catching the sky);
the darks are concentrated in the **wrecks** (tarred black timber) and the **char**. The fire and the barge
are the two focal values: the fire is the brightest warm accent, the barge the brightest neutral. Nothing
else in the zone is cleaner than `order_marble`: the wrights' canvas is sun-bleached `sand_cloth` and faded
teal at best, and it is smoke-stained near the fire.

---

## 1. Mood by Moment

1. **Arrival (the raid in progress).** Smoke first, seen over the flats from the east: three columns leaning
   north-east. Then the camp: half its tents already charred frames, one still standing and catching, a
   salvage pile smouldering with embers, the Order's branding brazier glowing beside the brine vats. The
   Stillguard's red lacquer (characters) is the only saturated red; the zone itself adds none.
2. **The fight** (the Stillguard Inquisitor and a raid-hound) on the hard: clear footing on the shingle, the
   tents and vats as a ring of cover. Fire is behind the enemy, so silhouettes read against the smoke
   (pillar 4: the player always reads the combatants).
3. **Sefir's barge.** Seen first from the hard, looking south down the channel: a white shape poled through
   the drifting smoke on water that does not move. It is the only clean white in the frame and the only
   thing the smoke does not stain. Then it lies alongside the hard while he speaks.
4. **After.** The fire has finished; the camp is char, ash and embers, the smoke thinning. Liss walks to the
   tideline and buries a burned lamp. The sun is lower and warmer; the wet mud is a sheet of amber light.

---

## 2. Kit Pieces (origin at the ground, +Y up; module grid 24 m for ground cells)

| Kit | Pieces | Key dimensions and parameters |
|---|---|---|
| **Mud-flat ground** | `mudflat_patch_a`, `mudflat_patch_b` (24 × 24 m cells), `mudflat_far` (1.2 km apron with a hole for the cells) | Seeded low relief (±0.12 m), rivulets 0.3–0.8 m wide cut to −0.45 m (they hold water at −0.35), wind-and-tide ripple field (texture). Cell edges are exactly y = 0 so cells and channel cells tile. VC.B paints wetness into the low ground and the rivulets' margins. The apron slopes to −2 m toward the south so the sea shows at the horizon. |
| **Shoal channel** | `channel_straight_a`, `channel_straight_b` (24 × 24 m cells) | The channel enters and leaves each cell on its centre line and meanders ±2.5 m inside it (variant b mirrored). Cross-section: levee lip +0.12 m at 8 m from the centre, a glistening mud bank down to the waterline (−0.35 m) at 6 m, then a steeper slumped bank to the bed (−1.6 m) at 3.5 m. Slump terraces and drainage runnels on the banks. |
| **The hard** | `camp_hard` | A shingle-and-shell bank 20 × 14 m, top +0.5 m, edges tapering into the mud over 2 m. Material: shell grit. |
| **Tideline** | `tideline_wrack` (8 m strip), `lamp_burial` | A 0.6–1.2 m wide band of wrack: weed clumps, sticks, shells, a few rope ends, at +0.9 m. `lamp_burial`: a scooped hole 0.4 m across with its spoil mound, and a small **burned Saltwright lamp** (brass and iron, glass cracked, sooted) half set in it. |
| **Plank walk** | `plank_walk` (4 m) | Salvage planks laid two wide over the mud on cross-sleepers, 0.9 m wide, a few boards missing or cracked: the route's line (pillar 3, and the readable path). |
| **Wrecks** | `wreck_hull_section`, `wreck_bow`, `wreck_mast_fallen`, `wreck_mast_standing`, `wreck_ribs_large` | Hull section: a 10 m section of a carvel-built trader, 4.2 m beam, listing 18° to starboard, its broken end showing frames, planks sprung and missing, mud-filled. Bow: a 6 m bow half sunk, stem post rising 4.2 m. Fallen mast: 11 m with a yard and torn rope. Standing mast stub: 7.5 m leaning 14°, a vertical for silhouettes. Ribs: a big hull's frames (6.5 m), the Haluna `wreck_rib` generator scaled. All **tarred black timber** with an algae and barnacle band at the low-water line and salt crust above. |
| **Saltwright camp, intact** | `camp_tent`, `salvage_rack`, `crate_stack`, `salvage_pile`, `brine_vat` | Tent: 3 × 4 m ridge tent of sail-cloth over oars (ridge 2.1 m), guy lines to driftwood stakes, a faded-teal patch. Rack: a 3 m lashed spar frame hung with rope coils, brass fittings, net-floats and Lit Age ceramic plates. Crates: 3–4 rope-bound crates of mixed size. Salvage pile: hull plating, brass, a Lit Age conduit shard, coiled rope. Brine vat: a 1.4 m coopered vat with iron hoops and a white salt rime, plus a shallow evaporation pan. |
| **Saltwright camp, burned** | `camp_tent_burned`, `salvage_rack_burned`, `crate_stack_burned`, `salvage_pile_burned`, `brine_vat_burned` | The same layouts after the fire: frames **charred** (deep char near the fire's seat, smoke-stained above), the ridge **collapsed**, canvas burned to tatters with char edges, crates broken open and lids fallen, the rack down on one side, staves of the vat sprung and its salt spilled grey with ash. **Embers** (emissive `ember_orange`) glow in the salvage pile and the tent's ash bed. |
| **The raid** | `branding_brazier` | The Order's brine-branding gear: an iron tripod brazier with live coals (emissive), three branding irons resting in it, their grips bound in `lacquer_red_deep` cord (the Order's colour, small). It is the only Order object the zone dresses. |
| **Liss's crate** | `liss_crate` | A small iron-cornered crate (0.6 × 0.4 × 0.4 m). Its plank seams leak **bound** light (`glimmer_bound`, emission 1.2, steady, no motes: it is held light). ≤ 0.5% of any frame. |
| **Smoke** | `smoke_plume` | A tapered, leaning column 14 m tall (1.2 m → 6 m across) as two crossed soft shells, drawn by `env_smoke_plume.gdshader` (in-repo, simple): scrolling noise breakup, soft edges, height fade, lit warm from below by the fire. **Request to Rendering:** a proper volumetric smoke column for the shipped zone (filed as a task). |
| **The barge** | `white_barge` | Sefir's progress barge: 12 m, 3.4 m beam, flat-bottomed and square-ended, draft 0.5 m, **white lacquer** (`order_marble`) with a thin `lacquer_red` sheer line and a low four-post canopy with a small gilded bowl-dome finial (gold ≤ 1% of a frame). Two pole-men stand at the stern; a 5 m pole lies in its crutch. It is poled, never rowed (bible §5). |

**Budgets (triangles, LOD0 / LOD1):** ground cells 4,700 / 300, apron 3,500 / 900, wrecks 5,000–12,000 /
600–1,200, camp pieces 2,500–9,000 / 300–900, small props ≤ 2,500 / 300, the barge 12,000 / 1,200. LOD1
begins at 70 m (the Haluna kit's table) and every piece is a chain (`<piece>`, `<piece>-lod1`), so exactly one
LOD draws at every distance (vegetation.md "One LOD at every distance", `LodChain`).

## 3. Materials (palette.json names)

| Slot | Shader | Look |
|---|---|---|
| `bs_mud` | weathering (triplanar, new `mud` texture) | warm grey-brown mud (`sand_wet` × `timber_weathered`, about `#6E6253` dry, never below the albedo floor wet), ripple and crack relief, algae film low, **salt crust** on the higher, drier mud, wetness from VC.B and the live wet line (`wet_roughness` 0.08 so the wet mud mirrors the sky) |
| `bs_shell_grit` | weathering (triplanar, Haluna `sand` + coral stone) | the hard's shingle: pale grey shell grit (`coral_stone_weathered`), drier, salt in the hollows |
| `bs_timber_tar` | weathering (Haluna `timber`) | the wrecks: tarred, near-black brown timber (`#3A3029` at the plank face, never below `#1D1916`), algae and barnacle band at the low-water line, salt crust above |
| `bs_timber` | weathering (Haluna `timber`) | the camp's salvaged spars: sun-silvered `timber_weathered` |
| `bs_char` | weathering (new `char` texture) | deep char: alligatored charcoal, `#262019` with a faint warm sheen, cracks lighter grey-brown |
| `bs_scorch` | weathering (Haluna `timber`) | smoke-stained and scorched timber: `timber_weathered` darkened 55% and browned |
| `bs_canvas`, `bs_canvas_teal`, `bs_canvas_scorched` | weathering (Haluna `woven_panel`, painted) | sun-bleached sail-cloth (`sand_cloth`), the Saltwright patch (`faded_teal_cloth`), and the canvas browned by smoke |
| `bs_rope` | weathering | tarred hemp (`timber_weathered` × 0.6) |
| `bs_iron`, `bs_iron_hot` | standard | rust-dark iron (`#4A3A30`, metallic 0.5); the irons' tips glowing `ember_orange` (emission 2.0) |
| `bs_brass`, `bs_lit_ceramic`, `bs_glass` | standard / weathering | salvage: `brass`, Lit Age ceramic (`lit_ceramic`, greyed, Haluna `coral_concrete`), net-float glass (`salt_glass`) |
| `bs_salt` | weathering | the vats' brine rime (`#E8E4D8`, rough) |
| `bs_ash` | weathering (mud texture, painted) | pale grey ash (`#8E8A84`) in the burned beds |
| `bs_ember` | standard, emissive | `ember_orange` at emission 2.5 (the brightest warm value; it is small) |
| `bs_glimmer_leak` | standard, emissive | `glimmer_bound` at emission 1.2, steady |
| `bs_weed` | weathering | wrack weed: olive-brown `#4A4A2E`, wet sheen |
| `bs_barge_white`, `bs_lacquer_red`, `bs_gold` | standard | `order_marble` white lacquer (roughness 0.3, clearcoat), `lacquer_red` sheer line, `gold_leaf` finial |
| `bs_smoke` | `env_smoke_plume` | smoke: lit `#B8A890` (the fog albedo) to `#5A524A` in the core, warmed by `ember_orange` at the base |

Weathering channels follow haluna.md §4 (**R moss, G salt, B wet, A erosion**). Burned pieces assign
`bs_char` and `bs_scorch` per triangle from a seeded char field (deepest at the fire's seat, low on the
piece), so the char reads as burned from below, not painted on.

---

## 4. Composed Shots (vFOV = 2·atan(12 / mm); heights above the local ground)

All at `ch06` unless noted. **◆** marks the preview shots built in `brine_shoals_kit/`.

| # | Lens (vFOV) | Height | Framing | What the shot is about |
|---|---|---|---|---|
| B01 ◆ | 24 mm (53.1°) | 1.7 m, on the plank walk 45 m east of the camp, looking west-south-west | The plank walk leads from the bottom left to the camp on its hard at the right third; three smoke columns lean north-east (to frame right) against the hazed sun-side sky; wreck ribs in the left foreground; the channel a dull silver line beyond the camp. Sky ≈ 45%. | Arrival: the Order's violence in daylight. |
| B02 ◆ | 35 mm (37.8°) | 1.6 m | The route of wrecks: the hull section large at the right third, the standing mast stub a vertical at the left third, the plank walk receding between them; wet mud mirrors the sky. | The pilgrimage through a graveyard of ships (pillars 2, 3). |
| B03 ◆ | 28 mm (46.4°) | 1.4 m, on the hard | Inside the camp: a burned tent's charred frame in the foreground, the salvage pile glowing with embers, the brine vats and the branding brazier beyond, one tent still standing and catching. | The camp as a home being destroyed. |
| B04 | 50 mm (27.0°) | 1.5 m | Toma frozen in the left third, the branding brazier's glow in the soft foreground at right, the captured wrights beyond. (Cinematics.) | He freezes. |
| B05 ◆ | 85 mm (16.1°) | 1.2 m, at the hard's channel edge looking south | The channel recedes in the centre, smoke drifting across it from right to left in two soft bands; the white barge emerges between them, its reflection a still white shape in grey-green water. | Sefir's arrival: the only clean white, on water the smoke cannot stir. |
| B06 | 35 mm (37.8°) | 2.5 m | The barge alongside the hard, Sefir under the canopy, the party on the shingle; the burned camp behind the party. (Cinematics.) | Mercy that costs him nothing. |
| B07 ◆ | 65 mm (20.9°) | 0.8 m | Liss's crate beside the burned rack, its seams leaking steady teal light; char and ash around; shallow DOF. | The thing he looks at a moment too long. |
| B08 ◆ | 50 mm (27.0°) | 1.0 m, `ch06_after` | The tideline: the lamp burial in the strand line, the wet flats beyond as a sheet of amber light, thin smoke. | "He put the fire out once it had finished." |
| B09 | 85 mm (16.1°) | 1.0 m | The standing mast stub against the hazed sun, smoke behind it. | Decline. |
| B10 ◆ | 18 mm (67.4°) | 14 m, south-east of the camp, pitched down | The whole layout as a diagram: the channel winding north, the camp on its hard, the plank walk, the wrecks. | The player sees the space (pillar 4). |
| B11 ◆ | 35 mm (37.8°) | 2.0 m, kit row | Review only: each camp piece intact beside its burned variant, on the hard. | The intact and burned kit, side by side. |

**Registered baselines (the repo's binary budget: at most two):** B01 and B05.

## 5. Review Checklist

- [ ] Every shot passes the grayscale value check: darks concentrated in the wrecks and the char, the fire
      and the barge the focal values.
- [ ] Shadows are teal, not grey, even on the mud (rule 5). The mud is never flat brown (Act I rule).
- [ ] Red ≤ 8% (the zone adds only the brazier cord and the barge's sheer line), gold ≤ 5% (the barge finial).
- [ ] The barge is the only clean white; nothing else exceeds `order_marble`.
- [ ] Liss's crate light is steady `glimmer_bound`, no motes, ≤ 0.5% of the frame.
- [ ] No wake behind the barge.

## Revisions
- 2026-10-24 (env-art, M3-ENV-02): first version, written against the act outline Ch6, ADR 0017 (a), bible §5
  and §7 and the colour script `ch06` row before any geometry.
