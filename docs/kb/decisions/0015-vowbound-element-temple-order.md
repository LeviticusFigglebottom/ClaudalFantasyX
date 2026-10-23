# 0015 — Vowbound elements and temple settings, second IP pass: no frozen temple before Ansedra

- **Status:** accepted (amended by [0016](0016-act-two-restaging.md): the Lowlight wording, the order statement and the Ch15 clue below were corrected on 2026-10-23 at the Lead's request in review-sweep-D)
- **Date:** 2026-10-23
- **Roles affected:** Narrative, Combat (element and status tables), Character Art and Environment (Vowbound sheets, the Lowlight, Cloudloom and Sanctum zones), Rendering and Art (color script `ch12` interior note), Audio (Vowbound motifs), Cinematics (the H09 cutaway)
- **Author role:** Narrative (M1-NAR-08)

## Context
SPEC §2 bans recreating the inspiring game's expression, and a sequence of beats counts as expression. M1-NAR-05 (decisions_log N-09) moved the Vowbound elements off the inspiring game's temple order. But it gave **Ice** to the Order's own Saint, Ethren, in a basin "held so still it freezes" at the Order's seat (Ch13). That temple came straight before the peace-wedding trap (Ch14) and the heretic turn (Ch15). Cinematics (review-sweep-C, M1-NAR-05 Review log) pointed out that this recreates the inspiring game's frozen-lake ice temple, where the party becomes traitors, followed by the wedding in the church's city, more closely than the old order did. The temple just before it, Cloudloom (Ch12), was also a glacier cave hung with frozen cords. So even without the element, an ice temple sat right before the holy city and the wedding.

The constraints:
- Chapter numbers and zone paths (`ch10`–`ch13`) are referenced by the color script, palette.json and the water-look validation data (`game/levels/_tests/swatches/water_looks.json`). Those belong to Art and Rendering.
- Each temple's Cantor is tied to its place: Ressa (a Kirru) at Lowlight next to the Kirru fen, Ama (an Ullari) at Cloudloom, and Corran (an Ansedran Tender) at the Sanctum.
- The six SPEC §6.8 elements are each held by one pre-Choir Vowbound. Kesh holds all six.
- N-09's Act I order (Water, Lightning, Fire) stays as it is, along with its reasons.

## Options
1. **Ice back to Cloudloom and Holy to the Sanctum** (Cinematics' alternative). Ice would then be the temple straight before the holy city, wedding and heretic turn, with a glacier cave as the setting. That is the same echo, one chapter earlier. Rejected.
2. **Re-sequence Act II** (the Cold Road as Ch10, Ice at Cloudloom, then the Fen and Lowlight). This puts the most distance between Ice and Ansedra. But it renumbers three chapters across Art and Rendering's frame data and validated water looks. It also still leaves an ice temple as "the fourth temple, then an interlude, then the holy city". Rejected for its cost to other roles, with no clear gain over option 3.
3. **Re-theme in place (chosen).** Keep every chapter, zone and Cantor where it is. Ice goes to the Ch11 temple, which sits in the deep cold and has nothing frozen in it. Cloudloom loses its ice. The Sanctum loses both its ice and the Ice element.
4. **Give Ice to an Act I temple** (Ashcrown or Coilspire). Rejected: it breaks N-09's reasons for each place (ash-plume lightning, the storm-beacon fire) and pushes the order back toward the inspiring game's Act I.

## Decision
| Ch | Vowbound | Temple | N-09 | **Now** |
|---|---|---|---|---|
| 3 | Ilun | Shell Shrine | Water | Water |
| 5 | Kahre | Ashcrown | Lightning | Lightning |
| 8 | Virel | Coilspire | Fire | Fire |
| 11 | Nhoa | Lowlight, Sunken Vey | Glimmer | **Ice** |
| 12 | Hesk | Cloudloom, Ullar Heights | Holy | Holy |
| 13 | Ethren | Sanctum of the Level, Ansedra | Ice | **Glimmer** |
| 16 | Kesh | the Drowned Choir | all six | all six |

- **Lowlight (Ice):** its drowned inner sanctum lies at the foot of a Lit Age well-shaft, where cold water from the open deep wells up through the floor, and drowned glimmer sifts down through it like silt. **Nothing in it is frozen.** The cold is the deep's. Nhoa's motes sift like silt in deep water, and her Swell *Farewell-Tide* is that settling silt turning and rising. *(Corrected per 0016: the first wording said "snow", which leaned toward a frozen image.)* Her copy ability is kept.
- **Cloudloom (Holy, unchanged element):** an open-roofed weaving-hall cut into the summit rock, hung with keth that stir in the wind. The noon shadows of the cords fall on white stone. **There is no glacier and nothing frozen.** The Cold Road stays cold, because Kerrid's unfogged breath depends on it.
- **The Sanctum of the Level (Glimmer):** its basin is a perfect mirror that hasn't stirred in four hundred years, lit from beneath by bound glimmer, the light the Order forbids. Ethren is gold lacquer lit from inside, and his ring is the only part of him that doesn't shine. Its kit is unchanged apart from the damage element: Slow, Stop, wards, and the Swell *Still Water*.
- **The rule from here on:** no Ice Vowbound at Ch12 or Ch13, and no ice, frost, glacier or frozen water in any temple or set-piece from Ch12 to Ch15.

**The echo check (element × temple setting × plot beat).** In the inspiring game, an ice temple on a frozen lake is where the party is branded traitors. The wedding betrayal in the church's city follows.
- *Ice* is now at a drowned gallery temple with no frozen water. Its beats are Rhen's confession and Pell's silence before his sister. *(Corrected per 0016: the founders' records, the truth of the pilgrimage, moved out of Lowlight to the Ch13 Lamp Archive, so no truth of the ritual lands in the cold sanctum.)* A whole mountain chapter and the city stand between it and the wedding.
- *The temple before the city* is a stone hall open to the sky, Holy, where a believer's arithmetic is read.
- *The city's temple* is a glimmer mirror, and the clue it plants points to the Lamp Archive's ledgers and the Cistern they describe (Ch13, per 0016), not to ice.

No pairing of element, setting and beat from that stretch survives. The new element order is Water, Lightning, Fire, Ice, Holy, Glimmer, then all six.

*Corrected per 0016 (this paragraph first said the order matched the inspiring game only in its opening on Water, which overstated it).* The order still has real overlap. The inspiring game's elemental temples run Fire, Lightning, Ice, then a non-elemental summon at the holy city. Ours runs Water, then **the same Fire and Lightning pair, swapped**, then **Ice in fourth place, as there**, then Holy, then the game's special element (Glimmer) at the holy city. What keeps this within SPEC §2 is that no setting or beat travels with the elements: Ice is a drowned, unfrozen sanctum with no truth beat, Lightning and Fire sit at a caldera and a storm-beacon, and the holy city's temple is a lit mirror. Narrative accepts the residual positional overlap. If a later change moves an element, it must not increase it.

## Consequences
- **Narrative (done in M1-NAR-08):** vowbound.md, bible §5.6–5.8, act_outline Ch11–Ch13, act3_ending H09 (the mirror basin goes dark and ripples), decisions_log N-15, and the glossary rows.
- **Combat:** element tables. Nhoa is Ice plus copy. Ethren is Glimmer plus Slow, Stop and wards. Hesk is unchanged. No combat data names these yet.
- **Art and Environment:** the Vowbound sheets (`docs/kb/art/vowbound/`, when written). Lowlight's well-shaft sanctum and its sifting motes (`glimmer_held`, falling). Cloudloom as a stone hall, not ice (color script `ch12` interior note updated). The Sanctum's basin is a lit mirror (`glimmer_bound` from beneath, which `ch13` already lists). Asha's S4 band (root and mote) still fits.
- **Watch:** any later ice or snow imagery in Act II must stay out of the Ch12–Ch15 run. The Cold Road's snow and wind on the pass are weather, not a temple. They are allowed but should not be featured in the Cloudloom interior.
- Supersedes the element columns of decisions_log N-09 for Nhoa and Ethren, and its Sanctum and Cloudloom setting text. N-09's Act I order stands.
