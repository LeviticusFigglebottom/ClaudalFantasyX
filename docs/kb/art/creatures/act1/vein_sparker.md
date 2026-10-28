# Vein sparker (`vein_sparker`), Ch5 the copper veins (optional)

**Idea.** A lean terrace lizard that lives in the exposed copper veins above Pemakar and soaks up their charge
(m2-slice act1_ch05 §9). It stores the charge in a ridge of copper spines and in its tail, which it holds up behind it
in a tight coil that brightens as it charges, then spits it out as lightning. Water grounds it. A beast; the one
exaggeration is the coiled tail.

**Silhouette and palette.** 0.75 m nose to rump, 0.6 m to the top of the coil; a low sprawl with elbows out, a wedge
head, the coil rising over the rump (no other Act I creature holds its tail up). Scales `bronze_patina` speckled with
`hair_copper`, dark `foliage_shadow` cross-bands, a `sand_dry` belly; the ridge spines bare copper. The stored charge
glows `starlight` #DCE6FF and pulses at 3 Hz, **in points only** (see below). It is not glimmer, so it uses none of
the glimmer lights.

**The charge and the palette (M3-CRE-650).** palette.json limits `starlight` to "point sources only; <=0.5% of frame".
Before this change the coil's whole last third glowed starlight over its surface (energy 2.5 in the `scale` slot,
besides the spine tips at 4.0). That was a lit surface, not a point, and it covered 1.4% of a frame filled by the
creature in the review three-quarter (a numpy estimate from the GLB). That broke both clauses. **Decision: keep the
swatch and confine it to small point sparks.** The charge now glows only at the ridge spines' 11 tips (2.2 cm) and at
four 1.6 cm sparks on the coil's flanks, alternating between the near side (-x) and the far side (+x) so that both
cameras see some. The coil's outer face is hidden where each turn winds inside the last. All of this is the `copper`
slot at its old values (4.0, 3 Hz, depth 0.6). The coil's last third is bare `hair_copper`, where the stored charge
shows through the scales. Starlight now covers 0.30% of a filled review frame (0.29% from the portrait angle), and
far less at battle scale. The spark read is unchanged: white-blue points along the spine and on the coil, pulsing at
3 Hz.

**Weak point (M3-CRE-650, ADR 0151).** It is a beast, so its weak point is one small closed mark: an old break in the
tail's root, healed over, where the tail lifts off the rump to climb into the coil. It is the one place the stored
charge leaks to ground. The seam of light is 6.8 cm long and 2.2 cm wide, in a raised `lacquer_black` ridge, on top
of the root and clear of the spines, a little to its near side (its right, -x, the battle camera's side once the stage
turns it to the party). It faces up and forward, so both the battle camera and the review three-quarter (+x front)
see it. It is never an open seam and never sheds motes. The `scale` slot carries it (#3FE0C8, 1.4, pulse 0.35 Hz at
depth 0.35, the reef crab's values), since the charge no longer uses that slot's emission. Clips, bones and rests are
unchanged.

**Clips.** `idle`: head flicks, the coil twitches. `attack`: a darting bite. `cast`: it rears, the coil tightens and
the jaw gapes to spit (the bolt itself is VFX). `hit`: a sideways flinch. `ko`: the legs splay, the coil unwinds.
Budget ≤ 5k (4.2k).
