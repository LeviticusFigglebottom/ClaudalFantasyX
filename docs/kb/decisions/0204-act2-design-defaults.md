# 0204 — Act II design defaults (the Lead's answers to the pre-gate drafts)

- **Status:** accepted
- **Date:** 2026-10-30
- **Roles affected:** story, design, combat, creatures, creatures-b, audio, env-art, ui
- **Author role:** lead

## Context
The Act II prep drafts (ADR 0203) raised LEAD-ASKs in the act2-plan, creatures, creatures-b and audio live logs. They're answered here in one place so the Act II tracks start from the same answers. Everything else in the drafts keeps its written default.

## Decisions
**Canon and IP**
1. **Ansedra has no seabirds** (bible §5.8). Drop "still-city birds (Ch13)" from M4-A2P-056. Ansedra has no wildlife, by design.
2. **No ice from Ch12 to Ch15** (ADR 0015) also covers the Ch12 regulars, for consistency:
   - `ridge_lynx` and `scree_crawler` swap frost for snow and grit (creatures task);
   - the Avalanche Ram gets wet, matted wool (M4-A2P-059).
3. **The Wakefin** stays one whole animal, with no deck adds and no separate fin target, fought from an unlamped drifting barge. That avoids echoing the inspiring game's fin-from-a-deck fight. `sound_dive` gives **evasion up with a clear telegraph**, not untargetable (pillar 4, tactical clarity).
4. **Proposed names:** all approved: Commander Brannoc Hale, Warden Dask, the dock-master Aldous Varrow, and the Kirru eldest **Owa** (named). The heresy's words are "Outside the Level". All are banned-terms clean.

**Bosses**

5. **People bosses** (Malcor Venn, the Abiding guard) follow Moll's precedent: a battle_sandbox stand-in scene plus characters' clips.
6. **Extra phases** (the Ram's `torn_fleece`, the Wakefin's `close_circle`) are kept, because each gives a mid-fight read. Combat may cut either one with sim data.
7. **Kesh:** battle scale 4.2 m (Kahre's summon frame), colossal only in the bind. The element order follows the order the party met the Vowbound.
8. **The smaller boss defaults stay as drafted:**
   - the Lamp Engine crawler start;
   - the Drowner's snag-root;
   - Malcor Venn's engine break as a lent set-piece skill;
   - Nhoa copying ordinary skills only;
   - Hesk's Mending as its own skill;
   - Ethren's Still Water as Stop on every foe.

**Audio**

9. **`battle_heretic`:** a variant regular-battle cue from Ch14 on.
10. **Singing:** the Order **sings** ORDER_HUM once, as `sefir_go_home`'s lullaby, as a deliberate break from "the Order hums; only Cantors sing". Liss sings the current-song in `hollowmere_answers`. Narrative confirms both in review.
11. **New footstep surfaces:** `root`, `snow` and `slate`. env-art marks them.
12. **Reprises:** the pyre-raft (Ch15 C7) and Ysolde's confession (Ch12 C4) reprise `hush_first_verse` and `ysolde_theme`.

**Story**

13. **Tobin's light** is caught in a Saltwright lamp at the pyre-raft, which plants Liss's Act III. Something is still lost: the raft burns and the lamp is cracked (pillar 6).
14. **Sefir's one word to Kerrid, "Captain."**, stays.
15. **The ledger phrase "the heart sung in" (Ch13)** stays, but fragmentary: a torn line, not a statement. The Choir truth lands in its own chapter.
16. **Kesh in Ch21:** act3_ending H03 ("raises Kesh from the stones") conflicts with Ch16 binding her to Asha. It goes on the Act III backlog to reconcile. Act II's binding stands.

## Consequences
- The Act II tracks start from one set of answers.
- Anything not listed keeps the default written in its draft.
