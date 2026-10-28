# Iskarra, the Drowned Capital (the Prologue, Ch19): Design Notes

Owner: Environment Artist (M3-ENV-710 kit, M3-ENV-724 the fast-track pass, M3-ENV-726 the Lamp Spire). Lighting
review: Rendering.
- **Story:** [act_outline](../../story/beats/act_outline.md) (the Prologue; Ch19) and bible §5.10. The Prologue's
  staging is slice-polish's (`game/levels/prologue/`).
- **Grade:** [color script](../color_script.md) `prologue` and `ch19`.
- **Kit:** in the Haluna kit, as `iskarra.py` and `iskarra_spire.py`.
- **Drop-in city:** `assets/environments/zones/iskarra/iskarra_city.tscn` (`iskarra_city.py`).
- **Arena:** `iskarra_spire_crown` (Warden Hesper Oan and Ilsabet Rue, Ch19).

**The feeling in one line:** gold dusk light over drowned white towers. A capital that was beautiful on purpose,
standing in a sea that will not give it back.

## 1. The city (bible §5.10)
- **The towers.** White Lit Age ceramic towers, drowned to their sixth storey. Each is clad in glazed tile laid in
  running bond and fluted. Galleries every 9 m are real ledges on a cast coping, with a parapet rail on posts and a
  band of reef-blue glaze under each. Two storeys of arched windows sit between galleries: dark openings in cast
  frames, with sills.
  - **The crowns:** domed (white, or glazed blue on the stepped towers), stepped, or broken to a jagged shell.
  - **The waterline band:** salt and weed.
- **The drowned midground.** Buildings' top storeys stand out of the sea: tiled walls, arched windows, the glazed
  band under a cornice, roofs fallen in. There are domed blocks, a sunk arcade, and the far city to the horizon
  (180–520 m).
- **The plaza.** A broken plaza on a podium above the water, with flags of Iskarra's pale limestone and channels
  inlaid in blue glaze.
  - **Inlays and debris:** a Lit Age sunburst inlaid at its middle; fallen glazed tiles from the towers' bands.
  - **The edges:** steps down to the water; the back corner fallen into the sea.
  - **The cast:** every cast mark of the Prologue stands on a slab (test_iskarra).
- **Colour.** White and gold at dusk (warm whites and gilt domes since M3-ENV-752: the cool white read grey on
  screen), with one saturated note: the reef-blue glaze (`#1569A0`, lifted to `#1F7FC2`), cool against the
  gold. No lamps are lit; the Prologue's only flame is Rhen's.
- **Influences** (transformed; SPEC §2), combined into an original plan of fluted ceramic towers with galleried
  storeys:
  - Mediterranean and North African glazed tilework;
  - Byzantine galleried towers;
  - drowned-city photographs, for the waterline.

## 2. Kit pieces
See `iskarra.py`'s docstring for every piece and its origin, and its `TRI_BUDGET`. The towers are 36k / 2.4k: their
windows are geometry.

## 3. The Lamp Spire (Ch19, `ch19/iskarra_spire`)
- **The spire's crown** (`spire_crown_floor`, 112 m over the sea):
  - a round floor (r 12) of flags with flush glazed rings and rays;
  - a balustrade round the edge;
  - an arcade of twelve clad columns carrying round arches and a ring entablature under a glazed band, open to
    the dusk;
  - two bays fallen, their stones on the floor's edge.
- **The founders' anchor-engine** (`anchor_engine`, 7.4 m): a salt-glass column round a bound core (`glimmer_bound`
  teal), caged in three bronze rings tilted about different axes, on a stepped ceramic base, with bronze conduits
  running into the floor. Shutting it down opens the way into the storm's eye.
- **The arena** `iskarra_spire_crown`:
  - The party stands on the crown floor; the engine stands behind the enemy line at (−7.2, −4.6).
  - **Light:** the afterglow low in the west (`#FF9F46` 0.7), the fill `#5A7FA8`, and the engine's teal as the
    one practical light.
  - **Below:** the drowned city (`iskarra_far_towers`) 112 m down.
  - **LUT:** `lut_ch19_spire`.
  - **Hints:** `the_engine`, `the_city_below`.
- **Still to build:** the spire's climb (its interior stair drums and the exterior for the field). They follow when
  Ch19's beat sheet stages the climb.

## Revisions
- 2026-10-27 (env-art): first issue, after the M3-ENV-724 fast-track pass, with the Lamp Spire's crown (M3-ENV-726).
