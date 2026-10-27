# Ethren, the Level Saint (`ethren`), Asha's Vowbound: design sheet (proposed, M3-CRE-644)

**Who:** the sixth Vowbound (docs/kb/story/vowbound.md §6): the glimmer of **Corran Ysel**, the 60th Cantor. He sang
24 years ago, a 31-year-old Ansedran Tender and Ysolde's husband: patient, funny and a terrible cook. He was displaced
when Imra sang, then placed in the Sanctum of the Level as the Order's showpiece Saint. He is bound in Ansedra (Ch13).
**Kind:** a Vowbound: bound light. **Role:** an ally, Glimmer. His battle identity is stillness: Slow and Stop on foes,
and mass wards on the party. His Swell is *Still Water*. **Status:** a sheet ahead of the build; he is not yet in
vowbound.json.

**The idea:** the Order's ideal made literal: an armoured, winged figure of **gold lacquer** with a **veiled face** and
a **bowl-halo** behind the head, lit from inside by a steady bound light that never drifts. He is beautiful and
impersonal. **A plain copper wedding ring** sits on one gauntleted finger, the keepsake: the only human thing about
him, and the only part of him that does not shine.

**People or creature?** He is a winged *figure*, not a person: Corran never appears in it except as the face under the
veil, in the final fight (Act III, Ch20, cinematics). So the form is this track's, built with the creature pipeline. If
the characters track's base body (MPFB2 topology, ADR 0021) would serve its proportions better, a shared build is a
fair request. The veil-fall face is theirs (Corran's face, a person).

## Silhouette and size

| | |
|---|---|
| Height | **3.0 m** to the top of the halo (head at 2.3 m): a standing figure, hovering 0.2 m off the water, the robe's hem 0.1 m above it |
| Wings | four, folded close behind him like a closed screen: long, flat lacquered panels (not feathers), 2.0 m tall. They open only in `ready`, `cast`, `special` and `victory`, to 3.6 m across. Folded at rest, so the HUD's right edge stays clear |
| Armour | a long, smooth, closed armoured robe like a lacquer shrine-figure, no visible body. It has gauntlets, and the hands are the only joints that read as human |
| Veil | a fine, still veil over the whole face, falling to the chest: it never moves, even when he does (the stillness) |
| The halo | a shallow bowl-shaped disc behind the head, 0.9 m across, its inner face lit |
| The ring | a plain copper band on the left ring finger, matte: albedo `laterite` toward `tortoiseshell` (the palette has no copper; the closest unlit warm metal), roughness high, no emission, no metallic shine |

## Colour, and the gold budget

palette.json limits `gold_leaf` and `gold_leaf_hi` to **≤5% of the frame area in any shot**. A gold figure filling the
summon shot would break that. So he is built as the Order builds its shrines:
- the bulk is `lacquer_black` `#1D1916` and `lacquer_red_deep` `#7A1712`, a deep lacquer whose glossy highlights
  carry the light;
- `gold_leaf` only on the **edges**: panel rims, the halo's lip, the gauntlet ridges and the veil's border. That is
  enough to read "gold lacquer" at battle distance and stays inside 5% (to be measured on his first render, as the
  palette tool does).

If the Lead wants him truly gold all over, that needs a palette exception (Ansedra's interiors already have a
lacquer_red exception at ≤15%); this sheet does not assume one.

| Part | Albedo | Light |
|---|---|---|
| Armour and robe | `lacquer_black`, `lacquer_red_deep` panels | none on the surface |
| Edges, halo lip | `gold_leaf` (metallic 1.0) | none |
| Halo inner face, armour seams | — | **`glimmer_bound` 1.2, steady**: the bound light is *inside* the lacquer shell and shows at the seams and the halo, never as a surface glow |
| The veil | `gauze_white`, thin | faint `glimmer_bound` (0.2) from behind (the face under it is never seen here) |
| The ring | `laterite`/`tortoiseshell`, rough | **none** |

This colour plan also serves the story: the light under his gold is the same bound glimmer the Order burns Saltwright
camps for (vowbound.md §6, Ch13). His seams glow exactly like the Lit Age machines, the flat-engine and the Lamp
Engine, which is the Act II truth hanging in plain sight.

## Clips

| Clip | Length | What it shows |
|---|---|---|
| `idle` | 4.0 s, loop | **almost nothing moves**: a very slow rise and fall of 1 cm. The veil is still. His stillness *is* the idle, the most still thing on the field |
| `ready` | 1.4 s | the wings open a little; the halo stays as it is (bound light is steady, so it never brightens) |
| `attack` | 1.2 s, contact ~0.55 s | one gauntleted hand raised, palm out, then a downward press: no weapon |
| `cast` | 1.6 s, contact ~0.8 s | Slow and Stop: both hands spread level, palms down, as if smoothing water flat |
| `ward` (or `cast`) | 1.6 s | the wings open forward around the party's side, a lacquer screen |
| `hit` | 0.5 s, peak ~0.1 s | a small, stiff recoil; the veil doesn't move |
| `defend` | 1.2 s | the wings close in front of him |
| `ko` | 1.8 s | he kneels, his wings folding down; the halo tips |
| `victory` | 2.2 s | wings fully open, the hands lowered, utterly still at the end |
| `rise` | 2.6 s | from kneeling, wings closed, he stands |
| `dismiss` | 1.0 s | he kneels again |
| `special` | 2.4 s, contact ~1.45 s | Still Water: wings flung fully open, both hands pressed down; at the contact everything on the field stops (VFX and the battle's own stop) |

## Rig and budget

About 30 bones: `root`, a three-bone `spine`, `neck` and `head` (the veil rigid on the head), two bones per arm plus
hand, and two finger groups on the ring hand so the ring can be framed. Four wings of two bones each, and the halo
on the head. Up to 16k triangles. Seven slots: `lacquer`, `lacquer_red`, `gold`, `seam`, `halo`, `veil`, `ring`.

## Open questions
- His vowbound.json row (Combat).
- The gold budget: edges only (the default above) or a Sanctum-wide palette exception (a Lead ADR).
- Corran's face under the veil, for Ch20's veil-fall: the characters track's, with the veil a separate rigid piece
  that cinematics can drop.
