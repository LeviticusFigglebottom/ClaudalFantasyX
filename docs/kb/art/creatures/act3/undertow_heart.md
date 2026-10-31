# The Undertow-heart (`sefir_heart`), Ch21 final boss, phase 2 (the heart's body)

**Task:** M5-A3P-1855 (creatures-b, ADR 0207; the Lead assigned "the finale's Undertow heart", 2026-10-31).
**Where:** Ch21, the heart arena (`undertow_heart`, env-art's M3-ENV-728). **Beat:** act3_ending.md H05–H08: "Sefir
reaches past Dace into Imra's light and begins drawing the heart into himself ... the held motes reverse direction
around Sefir, inward and down, the wrong way, faster." Phase 2, the Undertow-heart: "he draws on the party's
Vowbound-adjacent glimmer."

**What this sheet covers:** the heart's body only, the held light Sefir has drawn around himself. **Sefir's figure
is the characters track's** (his hero-path actor). This body gives his figure a place (`Sefir`, a node at its centre)
and plays around him. **Imra's column, the floor and the eyewall are env-art's** (undertow_layers.md §3). Act3_roster
first gave the Undertow-heart to rendering. The Lead's assignment moves its battle body here. A rendering pass on the
storm's light, if wanted, works on top of this body.

## The idea

The Undertow is the sea's held dead, a thousand years of light kept from rising. Sefir takes it into himself, and
for one phase he wears it: **three broad bands of held light wound round him in a slow helix**, always sinking. The
stripes slide down and inward and never stop. Around the bands, three shards of the column's salt-glass sleeves,
torn away when he reached in, orbit him like the plates of a lamp-housing coming apart. A ring of light lies on the
water at his feet.

The one exaggeration: **a storm worn as a garment.** Read from the camera, it is a man standing still at the centre
of a turning wall of cold light.

## Silhouette and size

- **Height:** 4.0 m (the bands run from the water to 3.6 m, and the sleeves orbit to 3.4 m). Sefir (1.8 m) stands at
  the centre, visible through the gaps between the bands. **The bands never cover his face:** each band climbs a
  third of a turn per metre, and the gaps between bands stay 0.6 m or wider at head height (0.7 m as built).
- **Radius:** the bands at 1.1–1.5 m (widest at the waist), the sleeves at 1.7 m.
- **The bands:** three ribbons, 0.26 m wide and 0.03 m thick, spaced 120° apart.
- **The sleeves:** three curved salt-glass shards, each 0.9 m high and 55° of arc, at heights 0.5, 1.5 and 2.5 m.
- **The tendrils:** two tapering tubes of held light (left and right). At rest they lie coiled against the bands; in
  `attack` they reach toward the party and draw back. They are the "draws on the party's glimmer".
- **The foot ring:** 1.3 m on the water.

## Palette

| Part | Albedo | Light |
|---|---|---|
| The bands, the tendrils, the foot ring | `glimmer_held` `#7FC6D9` over `abyss_navy` cores | `glimmer_held`, steady (the motion is the bands', never a pulse) |
| The sleeves | `salt_glass`, broken edges | none (unlit glass, catching the bands' light) |

**No `glimmer_bound`:** the heart Sefir takes is the held dead, not a machine's light. **No `glimmer_lift`, ever, on
this body.** The lift belongs to H07–H08 (the Letting's motes, Kesh's and Sefir's lift: VFX and characters). When
he lets go (`let_go`), the bands unwind outward and **sink** as the KO fade takes them. Held light never rises
(color_script rule 1), so the lift is the effect layer's alone, never a mixed mote.

## The fight (Combat's mechanics; proposal)

Phase 2 of Sefir's fight is **one combatant**, Sefir. This body is his phase-2 model, under him in the same row: a
`sefir_heart` creatures row whose scene instances his figure at `Sefir`.
- `attack` **the draw:** a tendril reaches into the party and pulls back (MP drain or a glimmer-drain status;
  Combat's).
- `cast` **the tightening:** the bands sink and turn faster and the sleeves close in, a held breath (a big party-wide
  skill's telegraph).
- `phase_change` **into the Letting** (H07): the bands slow and loosen. Asha's countdown begins.
- The KO is `let_go` (H08): the bands unwind outward and sink, and the sleeves drift out and down, under the KO fade.
  Sefir's own lift is his figure's.

## Clips

| Clip | Length | Contact | What it shows |
|---|---|---|---|
| `idle` (loop) | 8.0 s | | The bands turn a third of a turn (one band's spacing), so their stripes sink; the sleeves orbit the other way, slower; the tendrils sway |
| `ready` (loop) | 4.0 s | | As idle, twice as fast |
| `attack` | 1.6 s | 0.9 s | The right tendril reaches forward and down into the party and draws back; the bands lurch with it |
| `cast` | 2.4 s | 1.4 s | The bands sink 0.2 m and turn a third of a turn, fast; the sleeves close in 0.25 m; a hold; they ease back |
| `hit` | 0.6 s | 0.1 s peak | The bands jolt back and the sleeves scatter a little |
| `phase_change` | 3.0 s | 1.5 s | The bands slow and loosen outward; the sleeves drift wide; it ends at rest |
| `let_go` (KO) | 4.0 s | | The bands unwind, tilting outward, and sink 0.6 m; the sleeves drift out and down; the foot ring stays (the KO fade takes it all) |

## Rig

`root`; `spin` (the bands' turn, about y); `band_0..2` (each band's own sway, sink and unwinding); `sleeves` (their counter-
orbit); `sleeve_0..2`; `tendril_l_0..2` and `tendril_r_0..2`; `ring` (the foot ring). The VFX anchor `vfx_core` sits
at Sefir's chest (1.3 m). There is no `vfx_wound`: the weak point, if any, is Sefir's (characters and Combat).

**Budget:** ≤ 12k triangles (his figure's budget is characters').

## Open questions (Combat, characters, the chapter designer)

1. Is phase 2 a model swap on Sefir's row (this body plus his figure), or a second row? This build proposes the swap:
   one `sefir_heart` row whose scene holds his figure.
2. Does his figure play its own phase-2 clips inside the body (characters' `sefir` clips), or hold a pose?
3. The Letting (phase 3): does the body stay, slowed, behind the countdown? `phase_change` leaves it slowed and
   loosened, ready for that.
