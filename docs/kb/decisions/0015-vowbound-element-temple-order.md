# 0015 — Vowbound elements and temple settings, second IP pass: no frozen temple before Ansedra

- **Status:** accepted
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

- **Lowlight (Ice):** its drowned inner sanctum lies at the foot of a Lit Age well-shaft, where cold water from the open deep wells up through the floor, and drowned glimmer sifts down through it like snow. **Nothing in it is frozen.** The cold is the deep's. Nhoa's motes sift like snow in deep water, and her Swell *Farewell-Tide* is that snow falling upward. Her copy ability is kept.
- **Cloudloom (Holy, unchanged element):** an open-roofed weaving-hall cut into the summit rock, hung with keth that stir in the wind. The noon shadows of the cords fall on white stone. **There is no glacier and nothing frozen.** The Cold Road stays cold, because Kerrid's unfogged breath depends on it.
- **The Sanctum of the Level (Glimmer):** its basin is a perfect mirror that hasn't stirred in four hundred years, lit from beneath by bound glimmer, the light the Order forbids. Ethren is gold lacquer lit from inside, and his ring is the only part of him that doesn't shine. Its kit is unchanged apart from the damage element: Slow, Stop, wards, and the Swell *Still Water*.
- **The rule from here on:** no Ice Vowbound at Ch12 or Ch13, and no ice, frost, glacier or frozen water in any temple or set-piece from Ch12 to Ch15.

**The echo check (element × temple setting × plot beat).** In the inspiring game, an ice temple on a frozen lake is where the party is branded traitors. The wedding betrayal in the church's city follows.
- *Ice* is now at a drowned gallery temple with no frozen water. Its beats are Lit Age records, Rhen's confession, and Pell's silence before his sister. A whole mountain chapter and the city stand between it and the wedding.
- *The temple before the city* is a stone hall open to the sky, Holy, where a believer's arithmetic is read.
- *The city's temple* is a glimmer mirror, and the clue it plants points to the Cistern (Ch15), not to ice.

No pairing of element, setting and beat from that stretch survives. The new element order is Water, Lightning, Fire, Ice, Holy, Glimmer, then all six. It matches neither the first draft nor the inspiring game beyond the shared opening on Water (the slice), which is generic.

## Consequences
- **Narrative (done in M1-NAR-08):** vowbound.md, bible §5.6–5.8, act_outline Ch11–Ch13, act3_ending H09 (the mirror basin goes dark and ripples), decisions_log N-15, and the glossary rows.
- **Combat:** element tables. Nhoa is Ice plus copy. Ethren is Glimmer plus Slow, Stop and wards. Hesk is unchanged. No combat data names these yet.
- **Art and Environment:** the Vowbound sheets (`docs/kb/art/vowbound/`, when written). Lowlight's well-shaft sanctum and its sifting motes (`glimmer_held`, falling). Cloudloom as a stone hall, not ice (color script `ch12` interior note updated). The Sanctum's basin is a lit mirror (`glimmer_bound` from beneath, which `ch13` already lists). Asha's S4 band (root and mote) still fits.
- **Watch:** any later ice or snow imagery in Act II must stay out of the Ch12–Ch15 run. The Cold Road's snow and wind on the pass are weather, not a temple. They are allowed but should not be featured in the Cloudloom interior.
- Supersedes the element columns of decisions_log N-09 for Nhoa and Ethren, and its Sanctum and Cloudloom setting text. N-09's Act I order stands.
