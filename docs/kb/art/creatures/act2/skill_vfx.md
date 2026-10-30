# Act II regulars: their skills' battle effects (the creature side of M4-A2P-058)

The creatures track's spec for the eight Act II regulars' skills that have no effect yet. M4-A2P-060 (combat; reviewer
rendering) writes the entries into `game/data/vfx/battle/effects.json` with `tools/vfx/gen_act2_ability_vfx.py`. That
file and its data belong to rendering's battle-VFX stream, so this track does not edit them. Each line below is
written in the Act I generator's own vocabulary (`tools/vfx/gen_act1_ability_vfx.py`: `fx(at, motif(...), note)`,
the motifs `slash`, `heavy`, `burst`, `spray`, `shards`, `sink`, `ring`, `rise`, `column`, `charge`), so it can be
pasted almost as is. Colours are palette.json swatch names only.

Rules kept (color_script.md, the Act I generator's header):
- **No glimmer on a beast.** None of these creatures is Vowbound or a mote-bearer. Their only cyan is the
  `spawn_wound` weak point on the models, never in a skill's effect.
- **No impact core of their own.** The element hit (water for the jet, ice for the spines) already plays one.
- **The fen and the pass stay in their light.** The Ch10 effects are tannin browns and dull water. The Ch11 effects
  are cold salt-glass. The Ch12 effects are slate, snow and keth-cord red. The Ch16 effects are white sand and pale
  water.

| Skill (enemy) | Entry | Why |
|---|---|---|
| `tannin_jet` (tannin_archer, Ch10) | `fx("chest", spray("timber_weathered", "sand_wet", 46), "The archer's jet: tannin-dark water thrown hard.")` | A jet of the fen's own water. It reads as brown, not the reef's turquoise, and its element hit (water) supplies the splash core. |
| `root_drag` (root_crab, Ch10) | `fx("feet", heavy("timber_weathered", "foliage_shadow", "sand_wet", "timber_weathered", 30), "Roots drag the target down.")` | Low and heavy at the feet: mud and root fibre kicked up as the target is pulled two ranks back. |
| `leech_bite` (fen_leech, Ch10) | `fx("chest", sink("laterite", "lacquer_red_deep", 26, 0.25), "The leech's bite: a dark welling that sinks.")` | A bite that takes. A slow dark sink (not a spray) foreshadows the drain the roster wants (M4-CMB-1001), and its poison chance plays the status effect on top. |
| `glide_lash` (gallery_ray, Ch11) | `fx("chest", slash("salt_glass", "cumulus_shadow", 30, side=-1.0), "The ray's tail lashes past.")` | A pale, quick lateral streak, the tail whipping by as the ray banks. It sweeps from the right (side -1), the way the attack clip banks. |
| `rime_spine` (rime_urchin, Ch11) | `fx("chest", shards("salt_glass", "foam_white", 22), "Rime spines break off in the target.")` | Few, larger cold pieces falling: frozen spine tips. Its ice element hit and the slow status play on top. |
| `unravel` (cord_moth, Ch12) | `fx("chest", rise("lacquer_red", "sand_cloth", 30, 1.0, 0.4) + sink("sea_blue_cloth", "sand_cloth", 18, 0.3), "Woven buffs pulled apart like knotted cord.")` | The moth strips woven buffs: faded cord-red threads lift off and blue ones settle, the knot dyes of its wings (lacquer_red, sea_blue_cloth). It is not light, so no glimmer. |
| `scree_slide` (scree_crawler, Ch12) | `fx("feet", heavy("overcast_slate", "storm_slate", "gauze_white", "overcast_slate", 36), "A slide of split scree and snow.")` | Slate chunks and a low snow-dust cloud at the feet, the crawler's shell shedding scree. |
| `skate_sting` (glass_skate, Ch16) | `fx("chest", burst("sand_dry", "mortar_white", 30, rise=-3.0) + spray("turquoise_shallow", "foam_white", 24), "The skate erupts from the sand and stings.")` | A puff of white sand thrown up and a thin splash of the shallows. It reads against the Rim's white water by its spray, not by colour alone. |

`pounce` (ridge_lynx, Ch12) already has its Act I entry (the raid hound's), which fits the lynx as it is.
`ash_rake`, `shell_ram` and `pinch` (cord_moth, scree_crawler, root_crab) are Act I entries shared by family and
also fit.

Viewed: these are specs, not effects yet. M4-A2P-060 renders them in tools/vfx's sheet (act1_vfx_sheet.tscn or its
Act II twin) and in the encounters (`ch10_fen_archers`, `ch10_fen_roots`, `ch10_fen_leeches`, `ch11_vey_rays`,
`ch11_vey_urchins`, `ch12_pass_moths`, Ch12's scree crawlers and lynxes, Ch16's skates).
