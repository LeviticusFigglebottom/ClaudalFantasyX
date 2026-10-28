# Oil slug (`oil_slug`), Ch1 Oruvel Underway

## The idea

A sea slug (a nudibranch's shape) that feeds on lamp oil leaking from the drowned tower's lamps and cisterns. What it
eats it keeps: its frills glow the warm **oil-lamp** colour, the only warm light in the underway apart from Rhen's
lantern. Where it has fed, the diver's lamp gutters (it blinds). A reef beast and a beautiful one: the cruelty is
that it looks like home.

The one exaggeration: it **glows with eaten lamplight**.

## Silhouette and palette

- A long low slug 1.1 m long and 0.4 m high, its back a double row of flame-shaped frills (cerata), two curled
  horns (rhinophores) at the head. At battle distance: a low warm glow with a soft bristling outline.
- Body `sand_wet` to `tortoiseshell` along the foot; frills translucent with `oil_lamp` emissive tips (the oil
  glow is the creature's, not glimmer; never a glimmer swatch); horns `ember_orange`; weak point a `spawn_wound` gill
  rosette on its back near the tail.

## Clips

- `idle`: the frills ripple front to back, the horns sway, a slow glide in place.
- `attack`: it rears its front up and lunges, horns forward.
- `cast` (blind): the frills flare open and pulse brighter, the body arching.
- `hit`: the frills fold flat, it flinches back.
- `ko`: the frills dim one by one from the tail forward, the body flattens.

Rig: a spine chain of 6, two horns; frills ride the spine. Budget ≤ 6k triangles.

## Final quality (M3-CRE-654, ADR 0041)

The first build's horns read as sausages floating off a tube body. What changed, within the 6k budget (4,192 to
5,782 triangles; the bones, the clip names and the contact times are unchanged):

- **Body:** one loft on a flat sole. Each section is widest low, so the back arches over the middle and rounds down
  to the floor at a low head and a tapering tail. The skin is a net of grooves between raised tubercles, with a dark
  band along each flank over a pale foot and dark freckles.
- **Oil sheen:** an oil film's swirling `sea_glow` and `dusk_gold` bands in the colour. The body material is slick:
  `roughness_wet` 0.07, clearcoat 1.0.
- **Mantle:** a smooth raised shield over the shoulders, hugging the back, with a shadowed rim and a breathing pore on
  its right side.
- **Foot fringe:** a thin, ruffled skirt round the sole, pale with a `tortoiseshell` edge.
- **Tentacles:**
  - two tall upper ones on the horn bones, rooted in the head, ringed, with dark eyes on their tips;
  - two short, flat oral ones under the head, reaching forward and out.
- **Cerata:** 28 flattened flames in four rows behind the mantle. Each is dark and wet at the root and `ember_orange`
  up its length, and its tip glows `oil_lamp`. They lean out and curl back. The frill's rim sheen is 0.3 and its
  glow 2.2, so the root colour shows.
- **Weak point:** a small closed gill rosette of six folded plumes on the back near the tail, glowing `spawn_wound`
  at their tips (ADR 0151's beast form).
- **Grounding:** a root lift of a few millimetres takes up what the chain's ripple presses under the floor.
