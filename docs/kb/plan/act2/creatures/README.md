---
draft: pre-gate
---
# Act II creatures: plan sheets (regular foes and wildlife)

ADR 0203's preparation, docs only (creatures, 2026-10-30). One sheet per Act II regular foe and wildlife creature:
silhouette, materials, rig, clips, the battle-distance read, reuse of existing generators, and its state against the
final bar. The bosses (Mangrove Drowner, Lamp Engine, Avalanche Ram, Wakefin, flat-engine) are creatures-b's and
battle-presentation's (act2_plan.md §2) and are not here. Measured with the Act I audit's tools on the integration
branch: tools/creatures/clip_audit.gd (slip, pops, dips) and clip_sheet.tscn (poses viewed).

## Regular foes (all 11 exist on the integration branch, built with their full clip sets)

| Id | Ch | Kind | Meets the bar | What is left at the gate |
|---|---|---|---|---|
| [tannin_archer](tannin_archer.md) | 10 | fen beast | yes | `model` key, `tannin_jet` effect |
| [root_crab](root_crab.md) | 10 | variant (reef crab) | yes | `model` key, value check in the fen |
| [fen_leech](fen_leech.md) | 10 | variant (sail leech) | **no (read)** | hang lower (edge-on read, as the sail leech was) |
| [gallery_ray](gallery_ray.md) | 11 | reef beast | **no (read)** | pale on pale and flat: pattern or margin glow, lower hover |
| [rime_urchin](rime_urchin.md) | 11 | reef beast | yes, but its KO | a readable KO |
| [conduit_crawler](conduit_crawler.md) | 11 | construct | close | **no enemy row** (a boss add, M4-A2P-022); jointed legs |
| [ridge_lynx](ridge_lynx.md) | 12 | beast | **no** | paws slide 18–29 cm: `grounding.pinned`, a stepping pounce, leg shaping |
| [cord_moth](cord_moth.md) | 12 | beast | yes (read: medium) | battle scale like the ashwing's |
| [scree_crawler](scree_crawler.md) | 12 | variant (slag tortoise) | yes | `model` key; 17.5k tris vs budget |
| [glass_skate](glass_skate.md) | 16 | reef beast | yes | the risen read on white water |
| [rim_crawler](rim_crawler.md) | 16 | variant (tide crawler) | model yes, **read no** | chalk on white: value check |

**Common to all ten with enemy rows:** the rows have no `model` key (they fight as capsules: act2_plan.md §5), and
their skills have no effects yet (test_battle_act1_ability_vfx lists them).

## Wildlife (M4-A2P-056; none exists yet)

| Id | Ch | From | Sheet |
|---|---|---|---|
| fen kingfisher | 10 | the gull generator, small, a dive state | [fen_kingfisher](fen_kingfisher.md) |
| fen fireflies | 10 | the insect swarm, a blinking `firefly` type | [fen_firefly](fen_firefly.md) |
| woolback | 12 | the avalanche ram's build at 0.3 scale, no seep | [woolback](woolback.md) |
| rim rays | 16 | the shoal generator with a disc body | [rim_ray](rim_ray.md) |

**No wildlife on purpose:**
- **Ansedra (Ch13–14):** bible §5.8 and ansedra.md: "no seabirds, no dogs, and no children's games in the squares".
  The city's silence is the point (beautiful and airless), so the plan's "still-city birds (Ch13)" is not built;
  M4-A2P-056's goal line should drop it (LEAD-ASK in the creatures live log).
- **Lowlight, the Lamp Archive, Sunken Vey's dry halls:** interiors.
- **The open sea at night (Ch15):** only the Wakefin and the sea-glow (act_outline).
